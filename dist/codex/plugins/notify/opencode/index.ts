import type { Plugin, PluginInput } from "@opencode-ai/plugin";
import type { TextPart } from "@opencode-ai/sdk";

const TITLE = "Claude Code";
const PING = "Ping";
const GLASS = "Glass";
const TASK_LIMIT = 80;

type BunShell = PluginInput["$"];
type Client = PluginInput["client"];

const seenPermissions = new Set<string>();
const seenCompactions = new Set<string>();

export const Notify: Plugin = async ({ $, client, directory }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        const sessionID = event.properties.sessionID;
        const subtitle = await projectAndBranch($, directory);
        const task = await lastUserMessage(client, sessionID);
        await notify($, TITLE, subtitle, task ?? "Task completed", GLASS);
        return;
      }

      if (event.type === "permission.updated") {
        const id = event.properties.id;
        if (seenPermissions.has(id)) return;
        seenPermissions.add(id);
        await notify($, TITLE, "", "Needs permission…", PING);
        return;
      }
    },

    "experimental.session.compacting": async (input) => {
      if (seenCompactions.has(input.sessionID)) return;
      seenCompactions.add(input.sessionID);
      await notify($, TITLE, "", "Auto-compacting…", PING);
    },
  };
};

async function notify($: BunShell, title: string, subtitle: string, message: string, sound: string): Promise<void> {
  await $`terminal-notifier -title ${title} -subtitle ${subtitle} -message ${message} -sound ${sound} -group claude-code -activate com.apple.Terminal`.nothrow().quiet();
}

async function projectAndBranch($: BunShell, directory: string): Promise<string> {
  const project = directory.split("/").filter(Boolean).pop() ?? "";
  const result = await $`git -C ${directory} branch --show-current`.nothrow().quiet();
  const branch = result.exitCode === 0 ? result.text().trim() || "unknown" : "unknown";
  return `${project} @ ${branch}`;
}

async function lastUserMessage(client: Client, sessionID: string): Promise<string | null> {
  try {
    const result = await client.session.messages({ path: { id: sessionID } });
    const messages = result?.data ?? [];
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i];
      if (m?.info?.role !== "user") continue;
      const text = (m.parts ?? [])
        .filter((p): p is TextPart => p?.type === "text")
        .map((p) => p.text)
        .join(" ")
        .trim();
      if (text) return truncate(text, TASK_LIMIT);
    }
  } catch {
    return null;
  }
  return null;
}

function truncate(text: string, limit: number): string {
  if (text.length <= limit) return text;
  return text.slice(0, limit) + "…";
}
