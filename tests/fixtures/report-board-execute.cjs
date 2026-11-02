const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync(process.argv[2], "utf8");
const payload = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
class Element {
  constructor() {
    this.children = [];
    this.classList = { add() {}, toggle() {} };
  }
  append(...items) {
    this.children.push(...items);
  }
  replaceChildren(...items) {
    this.children = items;
  }
  setAttribute() {}
  get textContent() {
    return this.children.map((x) => (x instanceof Element ? x.textContent : x)).join("");
  }
  set textContent(value) {
    this.children = [value];
  }
}
const root = new Element();
const context = {
  Node: Element,
  document: {
    getElementById: (id) => (id === "board" ? root : { textContent: JSON.stringify(payload) }),
    createElement: () => new Element(),
  },
  window: { setInterval() {} },
  URL,
};
const script = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
if (!script.includes("    function tokens(parts) {")) throw Error("model capture marker missing");
vm.runInNewContext(script.replace("    function tokens(parts) {", "    globalThis.models = lanes;\n    function tokens(parts) {"), context);
console.log(JSON.stringify({ freedAfter: context.models[0].freedAfter, thenOneMore: root.textContent.includes("then one more"), states: payload.issues.map((i) => [i.number, context.models[0].state(i.number)]) }));
