#!/usr/bin/env node

import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { inspectLocalSpec } from "./inspect.js";
import { metadata } from "./metadata.js";

export type WriteLine = (line: string) => void;

export function isCliEntrypoint(
  moduleUrl: string,
  argvEntry: string | undefined,
): boolean {
  if (argvEntry === undefined) {
    return false;
  }

  try {
    return realpathSync(fileURLToPath(moduleUrl)) === realpathSync(argvEntry);
  } catch {
    return false;
  }
}

export function runCli(args: readonly string[], writeLine: WriteLine): number {
  if (args.length === 2 && args[0] === "metadata" && args[1] === "--json") {
    writeLine(JSON.stringify(metadata()));
    return 0;
  }

  const filePath = args[2];
  if (
    args.length === 4 &&
    args[0] === "inspect" &&
    args[1] === "--file" &&
    filePath !== undefined &&
    args[3] === "--json"
  ) {
    const result = inspectLocalSpec(filePath);
    writeLine(JSON.stringify(result));
    return result.ok ? 0 : 65;
  }

  writeLine(
    "Usage: type-mcp-api-cli metadata --json | inspect --file <path> --json",
  );
  return 64;
}

if (isCliEntrypoint(import.meta.url, process.argv[1])) {
  process.exitCode = runCli(process.argv.slice(2), (line) =>
    process.stdout.write(`${line}\n`),
  );
}
