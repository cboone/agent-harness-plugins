import type { Plugin } from "@opencode-ai/plugin";

const RECURSIVE_RM = /\brm\s+(-[a-zA-Z]*r|-R|--recursive)/;

export const BlockRmRf: Plugin = async () => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool !== "bash") return;
      const command = typeof output.args?.command === "string" ? output.args.command : "";
      if (RECURSIVE_RM.test(command)) {
        throw new Error("Use 'trash' instead of recursive rm. It moves files to the system Trash instead of permanently deleting them.");
      }
    },
  };
};
