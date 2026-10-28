// Preserve relevant transcripts without host-specific paths or credential data.
import fs from "node:fs";
import path from "node:path";
const [root, destination] = process.argv.slice(2);
if (!root || !destination) throw new Error("Usage: node collect.mjs SCRATCH OUTPUT");
const redact = (s) => s.replaceAll(`/private${root}`, "<scratch>").replaceAll(root, "<scratch>").replaceAll(process.env.HOME, "<home>");
const output = [];
for (const stage of ["before", "after"]) {
  for (const directory of fs.readdirSync(path.join(root, stage)).sort()) {
    const dir = path.join(root, stage, directory);
    const record = JSON.parse(fs.readFileSync(path.join(dir, "record.json")));
    const events = fs.readFileSync(path.join(dir, "events.jsonl"), "utf8").trim().split("\n").map(JSON.parse);
    output.push({
      directory,
      record,
      reply: redact(fs.readFileSync(path.join(dir, "reply.txt"), "utf8")),
      commands: events.filter((x) => x.type === "item.completed" && x.item?.type === "command_execution").map((x) => ({ command: redact(x.item.command), exit: x.item.exit_code })),
      usage: events.find((x) => x.type === "turn.completed")?.usage,
    });
  }
}
if (output.length !== 31) throw new Error(`Expected 31 case/probe records plus the original host probe, got ${output.length}`);
fs.writeFileSync(destination, `${JSON.stringify(output, null, 2)}\n`);
