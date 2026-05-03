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

// OpenCode's permission.updated event carries varying shapes by version. Try
// the documented properties; fall back to empty if the field is missing.
function extractToolFromPermission(event: { properties: Record<string, unknown> }): ToolInfo {
  const props = event.properties;
  const name = (typeof props.tool === "string" ? props.tool : typeof props.tool_name === "string" ? props.tool_name : "") || "";

  let input: Record<string, unknown> | null = null;
  if (props.tool_input && typeof props.tool_input === "object") {
    input = props.tool_input as Record<string, unknown>;
  } else if (props.input && typeof props.input === "object") {
    input = props.input as Record<string, unknown>;
  }

  let raw = "";
  if (input) {
    switch (name) {
      case "Bash":
        raw = String(input.command ?? "");
        break;
      case "Edit":
      case "Write":
      case "Read":
        raw = String(input.file_path ?? input.path ?? "");
        break;
      case "WebFetch":
        raw = String(input.url ?? "");
        break;
      case "Grep":
      case "Glob":
        raw = String(input.pattern ?? "");
        break;
      case "Task":
        raw = String(input.description ?? "");
        break;
      case "NotebookEdit":
        raw = String(input.notebook_path ?? "");
        break;
    }
  }

  return {
    name,
    preview: raw ? truncate(raw.replace(/\n/g, " "), TASK_LIMIT_DEFAULT) : "",
  };
}

function truncate(text: string, limit: number): string {
  if (text.length <= limit) return text;
  return text.slice(0, limit) + "…";
}
