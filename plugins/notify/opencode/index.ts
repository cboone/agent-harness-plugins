import type { Plugin, PluginInput } from "@opencode-ai/plugin";
import type { TextPart } from "@opencode-ai/sdk";

const TITLE_BASE = "OpenCode";
const TASK_LIMIT_USER_HEAD = 55;
const TASK_LIMIT_ASSISTANT_TAIL_PAIRED = 60;
const TASK_LIMIT_USER_FALLBACK = 120;
const TASK_LIMIT_DEFAULT = 140;
const FIRE_TIMEOUT = 86400;

const PANE_TITLE_DEFAULTS = new Set(["", "zsh", "bash", "fish", "sh", "tmux", "ssh", "nvim", "vim", "-zsh", "-bash"]);

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
const seenCompactions = new Set<string>();
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

export const Notify: Plugin = async ({ $, client, directory }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        const sessionID = event.properties.sessionID;
        const subtitle = await computeSubtitle($, directory);
        const userMsg = await lastMessage(client, sessionID, "user", TASK_LIMIT_USER_HEAD);
        const assistantTail = await lastMessage(client, sessionID, "assistant", TASK_LIMIT_ASSISTANT_TAIL_PAIRED);
        const message = await composeStopBody(client, sessionID, userMsg, assistantTail);
        const tmux = await computeTmuxState($);

        fireAlerterDetached($, {
          title: `${TITLE_BASE} · Done`,
          subtitle,
          message,
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
          title: `${TITLE_BASE} · Error`,
          subtitle,
          message: truncate(body.replace(/\n/g, " "), TASK_LIMIT_DEFAULT),
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
        const tmux = await computeTmuxState($);
        const tool = extractToolFromPermission(event);
        const fullSubtitle = tool.name ? `${subtitle} · ${tool.name}` : subtitle;
        const body = tool.preview || tool.name || "Needs permission";

        fireAlerterDetached($, {
          title: `${TITLE_BASE} · Permission`,
          subtitle: fullSubtitle,
          message: body,
          sound: "Funk",
          group: "opencode-permission",
          icon: ICON_PATH,
          tmux,
        });
        return;
      }
    },

    "experimental.session.compacting": async (input) => {
      if (seenCompactions.has(input.sessionID)) return;
      seenCompactions.add(input.sessionID);

      const subtitle = await computeSubtitle($, directory);
      const tmux = await computeTmuxState($);

      fireAlerterDetached($, {
        title: `${TITLE_BASE} · Compacting`,
        subtitle,
        message: "Auto-compacting context",
        sound: "Pop",
        group: "opencode-compact",
        icon: ICON_PATH,
        tmux,
      });
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

async function computeSubtitle($: BunShell, directory: string): Promise<string> {
  const project = directory.split("/").filter(Boolean).pop() ?? "";

  const tmuxPane = process.env.TMUX_PANE;
  if (tmuxPane) {
    const titleResult = await $`tmux display-message -t ${tmuxPane} -p '#T'`.nothrow().quiet();
    if (titleResult.exitCode === 0) {
      const title = titleResult.text().trim();
      if (!PANE_TITLE_DEFAULTS.has(title) && title !== project) {
        return `${project} · ${title}`;
      }
    }
  }

  const branchResult = await $`git -C ${directory} branch --show-current`.nothrow().quiet();
  let branch = branchResult.exitCode === 0 ? branchResult.text().trim() : "";
  if (!branch) branch = "unknown";
  const slashIdx = branch.indexOf("/");
  if (slashIdx >= 0) branch = branch.slice(slashIdx + 1);

  return `${project} · ${branch}`;
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

async function lastMessage(client: Client, sessionID: string, role: "user" | "assistant", limit: number): Promise<string | null> {
  try {
    const result = await client.session.messages({ path: { id: sessionID } });
    const messages = result?.data ?? [];
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i];
      if (m?.info?.role !== role) continue;
      const text = (m.parts ?? [])
        .filter((p): p is TextPart => p?.type === "text")
        .map((p) => p.text)
        .join(" ")
        .trim();
      if (text) return truncate(text, limit);
    }
  } catch {
    return null;
  }
  return null;
}

async function composeStopBody(client: Client, sessionID: string, userMsg: string | null, assistantTail: string | null): Promise<string> {
  if (userMsg && assistantTail) return `${userMsg} → ${assistantTail}`;
  if (userMsg) {
    const longer = await lastMessage(client, sessionID, "user", TASK_LIMIT_USER_FALLBACK);
    return longer ?? userMsg;
  }
  if (assistantTail) return assistantTail;
  return "Task completed";
}

interface ToolInfo {
  name: string;
  preview: string;
}

// `permission.updated` properties match the SDK's `Permission` type:
//   { id, type, pattern?, sessionID, messageID, callID?, title, metadata, time }
// `type` is the lowercase permission name ("bash", "edit", ...). `title` is a
// pre-computed UI summary; `pattern` and `metadata` are the per-tool fall-backs
// when no title is set. Older shapes (`tool`, `tool_name`, `tool_input`) are
// still accepted defensively in case an older OpenCode emits them.
function extractToolFromPermission(event: { properties: Record<string, unknown> }): ToolInfo {
  const props = event.properties;

  const rawType = typeof props.type === "string" ? props.type : typeof props.tool === "string" ? props.tool : typeof props.tool_name === "string" ? props.tool_name : "";
  const name = toolDisplayName(rawType);

  const candidates: string[] = [typeof props.title === "string" ? props.title : "", patternToString(props.pattern), patternToString(props.patterns), metadataPreview(props.metadata, rawType), legacyInputPreview(props, rawType)];

  for (const candidate of candidates) {
    const trimmed = candidate.trim();
    if (trimmed) {
      return {
        name,
        preview: truncate(trimmed.replace(/\n/g, " "), TASK_LIMIT_DEFAULT),
      };
    }
  }

  return { name, preview: "" };
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

function truncate(text: string, limit: number): string {
  if (text.length <= limit) return text;
  if (limit < 1) return "";
  return text.slice(0, limit - 1) + "…";
}
