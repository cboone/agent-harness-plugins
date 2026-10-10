import type { Plugin, PluginInput } from "@opencode-ai/plugin";
import type { TextPart } from "@opencode-ai/sdk";

// Body length budget: a banner shows about two lines, an expanded alert about four.
const BODY_LIMIT = 140;
const FIRE_TIMEOUT = 86400;

const PANE_TITLE_DEFAULTS = new Set(["", "zsh", "bash", "fish", "sh", "tmux", "ssh", "nvim", "vim", "-zsh", "-bash", "Claude Code", "Codex", "OpenCode"]);

const ICON_PATH = `${import.meta.dir}/../assets/opencode.png`;
const FOCUS_SCRIPT = `${import.meta.dir}/../scripts/focus-pane`;

type BunShell = PluginInput["$"];
type Client = PluginInput["client"];

interface TmuxState {
  session: string;
  window: string;
  pane: string;
}

const seenPermissions = new Set<string>();
const seenErrors = new Set<string>();

const TOOL_DISPLAY_NAMES: Record<string, string> = {
  bash: "Bash",
  edit: "Edit",
  glob: "Glob",
  grep: "Grep",
  notebookedit: "NotebookEdit",
  read: "Read",
  shell: "Shell",
  task: "Task",
  webfetch: "WebFetch",
  write: "Write",
};

// Titles name the action; the icon names the harness.
export const Notify: Plugin = async ({ $, client, directory }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        const sessionID = event.properties.sessionID;
        const subtitle = await computeSubtitle($, directory);
        const reply = await lastAssistantText(client, sessionID);
        const tmux = await computeTmuxState($);

        fireAlerterDetached($, {
          title: "Done",
          subtitle,
          message: summarizeReply(reply ?? "", BODY_LIMIT) || "Task completed",
          sound: "Glass",
          group: "opencode-stop",
          icon: ICON_PATH,
          tmux,
        });
        return;
      }

      if (event.type === "session.error") {
        const props = event.properties as { sessionID?: string; error?: unknown };
        const sessionID = typeof props.sessionID === "string" ? props.sessionID : "";
        const error = props.error as { name?: string; data?: Record<string, unknown> } | undefined;
        const errorName = typeof error?.name === "string" ? error.name : "";
        const errorData = error?.data && typeof error.data === "object" ? error.data : {};
        const errorMessage = typeof errorData.message === "string" ? errorData.message : "";

        // Dedup on (session, name, message) so retry storms with the same root
        // cause do not replay the alert sound, while distinct errors still fire.
        const dedupKey = `${sessionID}:${errorName}:${errorMessage}`;
        if (seenErrors.has(dedupKey)) return;
        seenErrors.add(dedupKey);

        const subtitle = await computeSubtitle($, directory);
        const tmux = await computeTmuxState($);
        const body = errorMessage || errorName || "Session error";

        fireAlerterDetached($, {
          title: "Error",
          subtitle,
          message: truncate(body.replace(/\n/g, " "), BODY_LIMIT),
          sound: "Funk",
          group: "opencode-error",
          icon: ICON_PATH,
          tmux,
        });
        return;
      }

      if (event.type === "permission.updated") {
        const id = event.properties.id;
        if (seenPermissions.has(id)) return;
        seenPermissions.add(id);

        const subtitle = await computeSubtitle($, directory);
        const root = await repoRoot($, directory);
        const tmux = await computeTmuxState($);
        const tool = extractToolFromPermission(event, root, directory);

        fireAlerterDetached($, {
          title: tool.name ? `Approve ${tool.name}?` : "Needs approval",
          subtitle,
          message: tool.preview || "Needs permission",
          sound: "Funk",
          group: "opencode-permission",
          icon: ICON_PATH,
          tmux,
        });
        return;
      }
    },
  };
};

interface AlerterArgs {
  title: string;
  subtitle: string;
  message: string;
  sound: string;
  group: string;
  icon: string;
  tmux: TmuxState | null;
}

function fireAlerterDetached($: BunShell, args: AlerterArgs): void {
  const termProgram = process.env.TERM_PROGRAM ?? "";
  const session = args.tmux?.session ?? "";
  const window = args.tmux?.window ?? "";
  const pane = args.tmux?.pane ?? "";

  void (async () => {
    try {
      const result = await $`alerter \
        --title ${args.title} \
        --subtitle ${args.subtitle} \
        --message ${args.message} \
        --sound ${args.sound} \
        --group ${args.group} \
        --app-icon ${args.icon} \
        --timeout ${String(FIRE_TIMEOUT)}`
        .nothrow()
        .quiet();
      const stdout = result.text();
      if (stdout.includes("@CONTENTCLICKED")) {
        await $`${FOCUS_SCRIPT} ${termProgram} ${session} ${window} ${pane}`.nothrow().quiet();
      }
    } catch {
      // Notification failures are silent: alerter not installed, sandbox, etc.
    }
  })();
}

async function repoRoot($: BunShell, directory: string): Promise<string> {
  const result = await $`git -C ${directory} rev-parse --show-toplevel`.nothrow().quiet();
  const root = result.exitCode === 0 ? result.text().trim() : "";
  return root || directory;
}

// Names the repository rather than the worktree folder: worktrees share the
// primary checkout's git directory, so its parent names the repository.
async function repoName($: BunShell, directory: string): Promise<string> {
  const folder = basename(directory);
  const result = await $`git -C ${directory} rev-parse --path-format=absolute --git-common-dir`.nothrow().quiet();
  const common = result.exitCode === 0 ? result.text().trim() : "";
  if (!common) return folder;
  const name = basename(common);
  if (name === ".git" || name === ".bare") return basename(common.slice(0, -name.length - 1)) || folder;
  return name.endsWith(".git") ? name.slice(0, -4) : name;
}

function basename(path: string): string {
  return path.split("/").filter(Boolean).pop() ?? "";
}

// The subtitle is `<repo> · <task>`. The task is the tmux pane title without
// leading status glyphs, or the branch suffix when the title names no task.
async function computeSubtitle($: BunShell, directory: string): Promise<string> {
  const repo = await repoName($, directory);

  const tmuxPane = process.env.TMUX_PANE;
  if (tmuxPane) {
    const titleResult = await $`tmux display-message -t ${tmuxPane} -p '#T'`.nothrow().quiet();
    if (titleResult.exitCode === 0) {
      const title = titleResult
        .text()
        .trim()
        .replace(/^[^\p{L}\p{N}#([]+/u, "");
      // A shell's default user@host:path title names no task.
      const generic = PANE_TITLE_DEFAULTS.has(title) || title === repo || title === basename(directory) || /^[^\s@]+@[^\s:]+:/.test(title);
      if (!generic) return `${repo} · ${title}`;
    }
  }

  const branchResult = await $`git -C ${directory} branch --show-current`.nothrow().quiet();
  let branch = branchResult.exitCode === 0 ? branchResult.text().trim() : "";
  if (!branch) branch = "unknown";
  const slashIdx = branch.indexOf("/");
  if (slashIdx >= 0) branch = branch.slice(slashIdx + 1);

  return `${repo} · ${branch}`;
}

async function computeTmuxState($: BunShell): Promise<TmuxState | null> {
  const tmuxPane = process.env.TMUX_PANE;
  if (!tmuxPane) return null;

  const result = await $`tmux display-message -t ${tmuxPane} -p '#S|#I|#P'`.nothrow().quiet();
  if (result.exitCode !== 0) return null;

  const parts = result.text().trim().split("|");
  if (parts.length !== 3) return null;
  return { session: parts[0]!, window: parts[1]!, pane: parts[2]! };
}

// Returns the text of the current turn's last assistant message. The walk stops at
// the turn's user message, so a turn without text never shows an earlier reply.
async function lastAssistantText(client: Client, sessionID: string): Promise<string | null> {
  try {
    const result = await client.session.messages({ path: { id: sessionID } });
    const messages = result?.data ?? [];
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i];
      if (m?.info?.role === "user") return null;
      if (m?.info?.role !== "assistant") continue;
      const text = (m.parts ?? [])
        .filter((p): p is TextPart => p?.type === "text")
        .map((p) => p.text)
        .join("\n")
        .trim();
      if (text) return text;
    }
  } catch {
    return null;
  }
  return null;
}

interface ReplyUnit {
  text: string;
  kind: "prose" | "status" | "code";
}

const BLOCK_START = /^\s*(#{1,6}|[-*+>•]|[0-9]+\.)\s/u;

// Mirrors SUMMARY_JQ in ../scripts/notify; keep the two in step. Lengths count
// Unicode code points, as jq does.
// - Input past 20,000 characters is ignored.
// - A JSON object reply with a string `summary` is summarized from that field.
// - Headings, list items and paragraphs become separate sentences, joined by a
//   period when one lacks closing punctuation.
// - Prose wins. Without prose, status lines (a leading ▸, or two or more " · "
//   separators) are used; without either, the first code or table line is.
//   An unclosed fence is read as prose.
// - Whole sentences are kept in order within `limit`. A sentence that no longer
//   fits is cut at a word boundary with "…" when it is the first sentence or at
//   least 40 characters remain.
function summarizeReply(reply: string, limit: number): string {
  let text = reply;
  try {
    const parsed: unknown = JSON.parse(reply);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed) && typeof (parsed as { summary?: unknown }).summary === "string") {
      text = (parsed as { summary: string }).summary;
    }
  } catch {
    // Plain-text replies are the common case.
  }

  const units = replyUnits(Array.from(text).slice(0, 20000).join("").split("\n"))
    .map((u) => ({ ...u, text: u.text.replace(/\s+/gu, " ").trim() }))
    .filter((u) => u.text !== "");
  const kept = units.some((u) => u.kind === "prose") ? units.filter((u) => u.kind === "prose") : units.some((u) => u.kind === "status") ? units.filter((u) => u.kind === "status") : units.slice(0, 1);
  const sentences = kept.flatMap((u, i) => {
    const unit = i < kept.length - 1 && !/[.!?:]$/u.test(u.text) ? `${u.text}.` : u.text;
    return (unit.match(/(?:[^.!?]|[.!?]+(?!\s|$))+(?:[.!?]+(?=\s|$))?/gu) ?? []).map((s) => s.trimStart()).filter((s) => s !== "");
  });

  let out = "";
  for (const sentence of sentences) {
    const gap = out === "" ? "" : " ";
    const room = limit - codePoints(out) - gap.length;
    if (codePoints(sentence) <= room) {
      out += gap + sentence;
    } else {
      if (out === "" || room >= 40) out += gap + cutAtWord(sentence, room);
      break;
    }
  }
  return out;
}

// Splits reply lines into prose, status and code units. Fenced lines and table
// rows are code; a fence left open at the end is read again as prose.
function replyUnits(lines: string[]): ReplyUnit[] {
  const units: ReplyUnit[] = [];
  let fence = -1;
  let mark = 0;
  let current = "";
  const flush = () => {
    if (current !== "") units.push({ text: current, kind: "prose" });
    current = "";
  };
  lines.forEach((line, i) => {
    if (/^\s*(```|~~~)/u.test(line)) {
      flush();
      if (fence < 0) {
        fence = i;
        mark = units.length;
      } else {
        fence = -1;
      }
    } else if (fence >= 0) {
      units.push({ text: line, kind: "code" });
    } else if (/^\s*\|/u.test(line)) {
      if (!/^[\s|:-]+$/u.test(line)) {
        flush();
        units.push({
          text: line.replace(/^\s*\||\|\s*$/gu, "").replace(/\s*\|\s*/gu, " · "),
          kind: "code",
        });
      }
    } else if (/^\s*$/u.test(line)) {
      flush();
    } else if (isStatusLine(line)) {
      flush();
      units.push({ text: stripInline(line), kind: "status" });
    } else if (BLOCK_START.test(line)) {
      flush();
      current = stripInline(line);
    } else {
      current = `${current} ${stripInline(line)}`.trimStart();
    }
  });
  if (fence >= 0) return [...units.slice(0, mark), ...replyUnits(lines.slice(fence + 1))];
  flush();
  return units;
}

function stripInline(line: string): string {
  return line
    .replace(/\[([^\]]*)\]\([^)]*\)/gu, "$1")
    .replace(/\*\*|__|`/gu, "")
    .replace(/(?<![\p{L}\p{N}_*])\*([^*\s][^*]*)\*/gu, "$1")
    .replace(/^\s*(#{1,6}|[-*+>▸•]|[0-9]+\.)\s+/u, "");
}

function isStatusLine(line: string): boolean {
  return /^\s*▸/u.test(line) || line.split(" · ").length > 2;
}

function codePoints(text: string): number {
  return Array.from(text).length;
}

// Cuts to `limit` code points with "…", dropping a partial last word.
function cutAtWord(text: string, limit: number): string {
  const chars = Array.from(text);
  if (chars.length <= limit) return text;
  if (limit < 1) return "";
  const head = chars.slice(0, limit - 1).join("");
  const complete = /^\s/u.test(chars[limit - 1] ?? "") || !/\s/u.test(head);
  return (complete ? head : head.replace(/\s+\S*$/u, "")).replace(/\s+$/u, "") + "…";
}

interface ToolInfo {
  name: string;
  preview: string;
}

// `permission.updated` properties match the SDK's `Permission` type:
//   { id, type, pattern?, sessionID, messageID, callID?, title, metadata, time }
// `type` is the lowercase permission name ("bash", "edit", ...). File tools show
// their metadata path, relative to the repository so the file name stays.
// Otherwise the preview is the first non-empty of `title` (a pre-computed UI
// summary), `pattern`, `patterns`, per-tool `metadata`, then the older
// `tool`/`tool_name`/`tool_input`/`input` shapes some OpenCode versions emit.
function extractToolFromPermission(event: { properties: Record<string, unknown> }, root: string, directory: string): ToolInfo {
  const props = event.properties;

  const rawType = typeof props.type === "string" ? props.type : typeof props.tool === "string" ? props.tool : typeof props.tool_name === "string" ? props.tool_name : "";
  const name = toolDisplayName(rawType);
  const type = rawType.toLowerCase();

  if (FILE_TOOLS.has(type)) {
    const path = metadataPreview(props.metadata, rawType) || legacyInputPreview(props, rawType);
    if (path.trim()) return { name, preview: displayPath(path.trim(), [root, directory], BODY_LIMIT) };
  }

  const candidates: string[] = [typeof props.title === "string" ? props.title : "", patternToString(props.pattern), patternToString(props.patterns), metadataPreview(props.metadata, rawType), legacyInputPreview(props, rawType)];

  for (const candidate of candidates) {
    let trimmed = candidate.trim();
    if (type === "bash" || type === "shell") trimmed = stripWorkingCd(trimmed, [directory, root]);
    if (trimmed) {
      return {
        name,
        preview: truncate(trimmed.replace(/\n/g, " "), BODY_LIMIT),
      };
    }
  }

  return { name, preview: "" };
}

const FILE_TOOLS = new Set(["edit", "write", "read", "notebookedit"]);

// Shows a path relative to the repository root, or under ~, keeping its end.
// git resolves symlinks in the root, so the session directory is tried too.
function displayPath(path: string, bases: string[], limit: number): string {
  const home = process.env.HOME ?? "";
  const base = bases.find((b) => b && path.startsWith(`${b}/`));
  let shown = path;
  if (base) shown = path.slice(base.length + 1);
  else if (home && path.startsWith(`${home}/`)) shown = `~/${path.slice(home.length + 1)}`;
  const chars = Array.from(shown);
  if (chars.length <= limit) return shown;
  if (limit < 1) return "";
  return "…" + chars.slice(chars.length - limit + 1).join("");
}

// Drops a leading cd into the working directory or repository root, which
// says nothing.
function stripWorkingCd(command: string, dirs: string[]): string {
  for (const dir of dirs) {
    for (const quoted of [dir, `"${dir}"`, `'${dir}'`]) {
      for (const separator of [" && ", "; "]) {
        const prefix = `cd ${quoted}${separator}`;
        if (command.startsWith(prefix)) return command.slice(prefix.length);
      }
    }
  }
  return command;
}

function patternToString(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value) && value.length > 0) return String(value[0] ?? "");
  return "";
}

function metadataPreview(metadata: unknown, type: string): string {
  if (!metadata || typeof metadata !== "object" || Array.isArray(metadata)) return "";
  const m = metadata as Record<string, unknown>;
  switch (type.toLowerCase()) {
    case "bash":
    case "shell":
      return typeof m.command === "string" ? m.command : "";
    case "edit":
    case "write":
    case "read":
      for (const key of ["filepath", "file_path", "path"]) {
        const value = m[key];
        if (typeof value === "string") return value;
      }
      return "";
    case "webfetch":
      return typeof m.url === "string" ? m.url : "";
    case "grep":
    case "glob":
      return typeof m.pattern === "string" ? m.pattern : "";
    case "task":
      return typeof m.description === "string" ? m.description : "";
    case "notebookedit":
      return typeof m.notebook_path === "string" ? m.notebook_path : "";
    default:
      return "";
  }
}

function legacyInputPreview(props: Record<string, unknown>, type: string): string {
  const input = props.tool_input && typeof props.tool_input === "object" && !Array.isArray(props.tool_input) ? (props.tool_input as Record<string, unknown>) : props.input && typeof props.input === "object" && !Array.isArray(props.input) ? (props.input as Record<string, unknown>) : null;
  if (!input) return "";
  switch (type.toLowerCase()) {
    case "bash":
    case "shell":
      return typeof input.command === "string" ? input.command : "";
    case "edit":
    case "write":
    case "read":
      for (const key of ["file_path", "filepath", "path"]) {
        const value = input[key];
        if (typeof value === "string") return value;
      }
      return "";
    case "webfetch":
      return typeof input.url === "string" ? input.url : "";
    case "grep":
    case "glob":
      return typeof input.pattern === "string" ? input.pattern : "";
    case "task":
      return typeof input.description === "string" ? input.description : "";
    case "notebookedit":
      return typeof input.notebook_path === "string" ? input.notebook_path : "";
    default:
      return "";
  }
}

function toolDisplayName(type: string): string {
  return TOOL_DISPLAY_NAMES[type.toLowerCase()] ?? capitalize(type);
}

function capitalize(s: string): string {
  return s.length > 0 ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}

// Cuts to `limit` code points, so a cut never splits a surrogate pair.
function truncate(text: string, limit: number): string {
  const chars = Array.from(text);
  if (chars.length <= limit) return text;
  if (limit < 1) return "";
  return chars.slice(0, limit - 1).join("") + "…";
}
