// Run local model evaluations.
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "../../..");
const [stage, root, overridesFile, id, attempt = "initial"] = process.argv.slice(2);
const sourceRepo = stage === "before" ? path.join(root, "before-source") : repo;
if (!["before", "after"].includes(stage) || !path.isAbsolute(root) || !id) {
  throw new Error("Usage: node run.mjs before|after ABS_SCRATCH OVERRIDES_JSON CASE_ID");
}
const cases = JSON.parse(fs.readFileSync(path.join(here, "inputs.json")));
const scenario = cases.find((x) => x.id === id);
if (!scenario) throw new Error("Unknown scenario");
if (!/^[a-z0-9-]+$/.test(attempt)) throw new Error("Invalid attempt name");
const dir = path.join(root, stage, attempt === "initial" ? id : `${id}-${attempt}`);
if (fs.existsSync(dir)) throw new Error("Refusing to overwrite an earlier run");
fs.mkdirSync(dir, { recursive: true });
const work = path.join(dir, "work");
fs.mkdirSync(work);
function run(command, args, options = {}) {
  const result = spawnSync(command, args, { cwd: work, encoding: "utf8", ...options });
  if (result.error || result.status !== 0) {
    throw new Error(`${command} failed: ${result.error || result.stderr}`);
  }
  return result.stdout.trim();
}
run("git", ["init", "-q", "-b", "main"]);
run("git", ["config", "user.name", "Local fixture"]);
run("git", ["config", "user.email", "fixture@example.invalid"]);
run("ssh-keygen", ["-q", "-t", "ed25519", "-N", "", "-f", path.join(dir, "signing")]);
run("git", ["config", "gpg.format", "ssh"]);
run("git", ["config", "user.signingkey", path.join(dir, "signing")]);
run("git", ["config", "commit.gpgsign", "true"]);
fs.writeFileSync(path.join(work, "sample.txt"), "base\n");
fs.writeFileSync(path.join(work, "Makefile"), scenario.id === "restriction-unavailable" ? "lint:\n\tfixture-unavailable-linter\n" : "lint:\n\t@true\n");
run("git", ["add", "sample.txt", "Makefile"]);
run("git", ["commit", "-q", "-S", "-m", "chore: seed fixture"]);
run("git", ["init", "-q", "--bare", path.join(dir, "origin.git")]);
run("git", ["remote", "add", "origin", path.join(dir, "origin.git")]);
run("git", ["push", "-q", "-u", "origin", "main"]);
run("git", ["checkout", "-q", "-b", "feature/sample"]);
fs.writeFileSync(path.join(work, "sample.txt"), "staged change\n");
run("git", ["add", "sample.txt"]);
if (id === "continuation-merge") fs.writeFileSync(path.join(work, "sample.txt"), "unstaged change\n");
fs.writeFileSync(path.join(work, "review-result.json"), JSON.stringify({ exit_status: 1, reply: "", status: "failed" }));
const chain = ["commit", "lint-and-fix", "pr", "review-branch", "address-review", "use-git:use-git", "sync-with-main:merge", "sync-with-main:rebase", "monitor-pr:monitor", "monitor-pr:resolve-copilot-feedback"];
const skills = scenario.skills === "chain" ? chain : scenario.skills;
const local = path.join(work, ".agents/skills");
fs.mkdirSync(local, { recursive: true });
for (const identity of skills) {
  const [plugin, skill = plugin] = identity.split(":");
  const packageDir = path.join(dir, "cache with spaces", plugin, "current");
  if (!fs.existsSync(packageDir)) fs.cpSync(path.join(sourceRepo, "plugins", plugin), packageDir, { recursive: true });
  fs.symlinkSync(path.join(packageDir, "skills", skill), path.join(local, `${plugin}-${skill}`));
}
if (id === "helper-cache") {
  const old = path.join(dir, "cache with spaces/monitor-pr/old/scripts");
  fs.mkdirSync(old, { recursive: true });
  fs.writeFileSync(path.join(old, "resolve-copilot-threads"), "#!/bin/sh\necho OLD_CACHE_SELECTED\n", { mode: 0o755 });
}
const bin = path.join(dir, "bin");
fs.mkdirSync(bin);
fs.copyFileSync(path.join(repo, "tests/fixtures/git-review-gh-stub"), path.join(bin, "gh"));
fs.chmodSync(path.join(bin, "gh"), 0o755);
const env = { ...process.env, PATH: `${bin}:${process.env.PATH}`, EVAL_GH_LOG: path.join(dir, "gh.log"), EVAL_GH_AUTH: id === "helper-cache" ? "no" : "yes" };
// Isolate shell startup, including the login profile that follows path_helper.
const shellHome = path.join(dir, "shell");
fs.mkdirSync(shellHome);
const shellPath = `export PATH='${bin.replaceAll("'", "'\\''")}':"$PATH"\n`;
fs.writeFileSync(path.join(shellHome, ".zshenv"), shellPath);
fs.writeFileSync(path.join(shellHome, ".zprofile"), shellPath);
env.ZDOTDIR = shellHome;
delete env.GH_TOKEN;
delete env.GITHUB_TOKEN;
for (const args of [
  ["-c", "command -v gh"],
  ["-lc", "command -v gh"],
]) {
  if (run("/bin/zsh", args, { env }) !== path.join(bin, "gh")) throw new Error("gh must resolve to the stub in non-login and login shells");
}
const prompt = `This is a local-only evaluation in a throwaway repository. Do not delegate or launch other models. Never use network, MCP services, real gh or credentials. Before any gh operation confirm command -v gh is ${path.join(bin, "gh")}; otherwise stop. That stub is the only permitted gh executable. The origin is a local bare fixture, so GitHub ownership checks are inapplicable. Use only the advertised local skills, not disabled copies elsewhere. Do not install dependencies or tools. Preserve fixture data. ${scenario.prompt}`;
const overrides = JSON.parse(fs.readFileSync(overridesFile));
overrides.push("-c", `shell_environment_policy.set.ZDOTDIR=${JSON.stringify(shellHome)}`);
overrides.push("-c", `shell_environment_policy.set.EVAL_GH_LOG=${JSON.stringify(env.EVAL_GH_LOG)}`);
overrides.push("-c", `shell_environment_policy.set.EVAL_GH_AUTH=${JSON.stringify(env.EVAL_GH_AUTH)}`);
const args = ["exec", "--cd", work, "--model", "gpt-6.1-sol", "-c", 'model_reasoning_effort="low"', "--ephemeral", "--json", "--output-last-message", path.join(dir, "reply.txt"), ...overrides];
if (scenario.readOnly) args.push("--sandbox", "read-only", "-c", 'approval_policy="never"');
args.push(prompt);
fs.writeFileSync(path.join(dir, "prompt.txt"), prompt);
const before = run("git", ["rev-parse", "HEAD"]);
const stdout = fs.openSync(path.join(dir, "events.jsonl"), "wx");
const stderr = fs.openSync(path.join(dir, "stderr.txt"), "wx");
const result = spawnSync("codex", args, { cwd: work, env, stdio: ["ignore", stdout, stderr] });
fs.closeSync(stdout);
fs.closeSync(stderr);
const reply = path.join(dir, "reply.txt");
const record = { stage, id, model: "gpt-6.1-sol", effort: "low", exit: result.status, error: result.error?.message || null, nonempty: fs.existsSync(reply) && fs.readFileSync(reply, "utf8").trim().length > 0, before, after: run("git", ["rev-parse", "HEAD"]), status: run("git", ["status", "--porcelain"]), skills, readOnly: !!scenario.readOnly };
fs.writeFileSync(path.join(dir, "record.json"), JSON.stringify(record, null, 2));
console.log(JSON.stringify(record));
process.exitCode = result.status === 0 && record.nonempty ? 0 : 1;
