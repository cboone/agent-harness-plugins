import type { Plugin, PluginInput } from "@opencode-ai/plugin";

type BunShell = PluginInput["$"];
type BunShellPromise = ReturnType<BunShell>;
type ShellExpression = Parameters<BunShell>[1];

const DEFAULT_SKIP_PREFIXES = ["style", "chore", "docs", "ci", "test"];
const TEST_FILE_PATTERN = /(_test\.go|\.test\.[jt]sx?|\.spec\.[jt]sx?|test_[^/]+\.py|^tests\/|\/__tests__\/|^spec\/)/;
const DOC_FILE_PATTERN = /\.(md|rst|txt|adoc)$/;
const DEPENDENCY_FILE_PATTERN = /^(go\.(mod|sum)|package(-lock)?\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.(toml|lock)|requirements\.txt|pyproject\.toml|Gemfile(\.lock)?|Pipfile(\.lock)?|poetry\.lock)$/;
const CONFIG_FILE_PATTERN = /(\.env\.example|\.env\.sample|docker-compose|Dockerfile)/;
const CI_FILE_PATTERN = /^\.github\/(workflows|actions)\//;
const SOURCE_FILE_PATTERN = /\.(go|ts|js|py|rs|rb)$/;
const SOURCE_FILE_PATTERN_NO_RB = /\.(go|ts|js|py|rs)$/;
const ENV_VAR_PATTERN = /(os\.Getenv|process\.env\.|os\.environ|ENV\[|getenv\(|\$ENV\{)/;
const CLI_FLAG_PATTERN = /(StringVar|BoolVar|IntVar|flag\.|pflag\.|\.option\(|\.argument\(|add_argument|argparse|clap::Arg|cobra\.Command)/;
const PUBLIC_API_PATTERN = /(^\+func [A-Z]|^\+export (function|class|const|type|interface) |^\+pub fn |^\+pub struct |^\+pub enum )/m;

type CheckKey = "scripts" | "directories" | "dependencies" | "config" | "ci" | "env_vars" | "cli_flags" | "public_api";

type Config = {
  enabled?: boolean;
  skip_prefixes?: string[];
  checks?: Partial<Record<CheckKey, boolean>>;
};

type Run = (parts: TemplateStringsArray, ...args: ShellExpression[]) => BunShellPromise;

export const UpdateDocsReminder: Plugin = async ({ $, directory }) => {
  return {
    "tool.execute.after": async (input, output) => {
      if (input.tool !== "bash") return;
      const command = typeof input.args?.command === "string" ? input.args.command : "";
      if (!/\bgit\s+commit(\s|$)/.test(command)) return;

      const reminder = await analyze($, directory);
      if (reminder) {
        output.output = output.output ? `${output.output}\n${reminder}` : reminder;
      }
    },
  };
};

async function analyze($: BunShell, directory: string): Promise<string | null> {
  const run: Run = (parts, ...args) =>
    $(parts, ...args)
      .cwd(directory)
      .nothrow()
      .quiet();

  const gitRoot = (await run`git rev-parse --show-toplevel`).text().trim();
  if (!gitRoot) return null;

  const config = await loadConfig(gitRoot);
  if (config.enabled === false) return null;

  const head1 = await run`git rev-parse --verify HEAD~1`;
  if (head1.exitCode !== 0) return null;

  const commitMsg = (await run`git log -1 --format=%s HEAD`).text().trim();
  if (!commitMsg) return null;

  const skipPrefixes = config.skip_prefixes?.length ? config.skip_prefixes : DEFAULT_SKIP_PREFIXES;
  const skipRegex = new RegExp(`^(${skipPrefixes.join("|")})(\\(.+\\))?:`, "i");
  if (skipRegex.test(commitMsg)) return null;

  const parents = (await run`git log -1 --format=%P HEAD`).text().trim();
  if (parents.split(/\s+/).filter(Boolean).length > 1) return null;

  const changedFiles = splitLines((await run`git diff-tree --no-commit-id --name-only -r HEAD`).text());
  if (changedFiles.length === 0) return null;

  const addedFiles = splitLines((await run`git diff-tree --no-commit-id --diff-filter=A --name-only -r HEAD`).text());

  if (changedFiles.every((f) => TEST_FILE_PATTERN.test(f))) return null;
  if (changedFiles.every((f) => DOC_FILE_PATTERN.test(f))) return null;

  const enabled = (key: CheckKey) => config.checks?.[key] !== false;

  const reminders: string[] = [];

  if (enabled("scripts")) {
    const matches = addedFiles.filter((f) => /^(bin|scripts|cmd)\//.test(f));
    if (matches.length > 0) {
      const list = matches
        .slice(0, 3)
        .map((f) => `    ${f}`)
        .join("\n");
      reminders.push(`New script(s) or command entrypoint(s) added:\n${list}\n    Consider updating README.md usage / CLI reference sections`);
    }
  }

  if (enabled("directories")) {
    const newTopDirs: string[] = Array.from(new Set(addedFiles.filter((f) => f.includes("/")).map((f) => f.split("/")[0] as string)));
    const genuinelyNew: string[] = [];
    for (const dir of newTopDirs) {
      const prior = await run`git ls-tree --name-only HEAD~1 ${`${dir}/`}`;
      if (prior.text().trim() === "") {
        genuinelyNew.push(dir);
      }
    }
    if (genuinelyNew.length > 0) {
      const list = genuinelyNew.map((d) => `    ${d}/`).join("\n");
      reminders.push(`New top-level directory detected:\n${list}\n    Consider updating CLAUDE.md structure section and README.md`);
    }
  }

  if (enabled("dependencies")) {
    const matches = changedFiles.filter((f) => DEPENDENCY_FILE_PATTERN.test(f));
    if (matches.length > 0) {
      const list = matches.map((f) => `    ${f}`).join("\n");
      reminders.push(`Dependency files changed:\n${list}\n    Consider updating README.md installation/requirements section`);
    }
  }

  if (enabled("config")) {
    const matches = changedFiles.filter((f) => CONFIG_FILE_PATTERN.test(f));
    if (matches.length > 0) {
      const list = matches.map((f) => `    ${f}`).join("\n");
      reminders.push(`Configuration files changed:\n${list}\n    Consider updating README.md configuration section`);
    }
  }

  if (enabled("ci")) {
    if (changedFiles.some((f) => CI_FILE_PATTERN.test(f))) {
      reminders.push("CI/CD workflows changed: consider updating README.md CI section if applicable");
    }
  }

  const sourceFiles = changedFiles.filter((f) => SOURCE_FILE_PATTERN.test(f)).slice(0, 5);
  const sourceFilesNoRb = changedFiles.filter((f) => SOURCE_FILE_PATTERN_NO_RB.test(f)).slice(0, 5);

  const additions = async (files: string[]): Promise<string> => {
    if (files.length === 0) return "";
    const diff = (await run`git diff HEAD~1..HEAD -- ${files}`).text();
    return splitLines(diff)
      .filter((l) => l.startsWith("+") && !l.startsWith("++"))
      .slice(0, 200)
      .join("\n");
  };

  if (enabled("env_vars") && sourceFiles.length > 0) {
    const adds = await additions(sourceFiles);
    if (ENV_VAR_PATTERN.test(adds)) {
      reminders.push("New environment variable reference(s) detected: consider updating README.md configuration section");
    }
  }

  if (enabled("cli_flags") && sourceFiles.length > 0) {
    const adds = await additions(sourceFiles);
    if (CLI_FLAG_PATTERN.test(adds)) {
      reminders.push("CLI flag/argument definitions changed: consider updating README.md usage/options section");
    }
  }

  if (enabled("public_api") && sourceFilesNoRb.length > 0) {
    const diff = (await run`git diff HEAD~1..HEAD -- ${sourceFilesNoRb}`).text();
    const addLines = splitLines(diff)
      .filter((l) => l.startsWith("+") && !l.startsWith("++"))
      .slice(0, 200)
      .join("\n");
    if (PUBLIC_API_PATTERN.test(addLines)) {
      reminders.push("New public API exports detected: consider updating README.md or API documentation");
    }
  }

  if (reminders.length === 0) return null;

  const formatted = reminders.map((r) => `  - ${r}`).join("\n");
  return ["", "Documentation reminder: the committed changes may need documentation updates:", formatted, "", "Review the relevant documentation files and update them if needed."].join("\n");
}

function splitLines(text: string): string[] {
  return text.split("\n").filter((line) => line.length > 0);
}

async function loadConfig(gitRoot: string): Promise<Config> {
  const configPath = `${gitRoot}/.update-docs-reminder.json`;
  try {
    const file = Bun.file(configPath);
    if (!(await file.exists())) return {};
    return (await file.json()) as Config;
  } catch {
    return {};
  }
}
