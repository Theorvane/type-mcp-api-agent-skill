import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { runCli } from "../src/cli.js";

describe("runCli", () => {
  it("writes metadata JSON without secrets", () => {
    const output: string[] = [];

    const exitCode = runCli(["metadata", "--json"], (line) =>
      output.push(line),
    );

    expect(exitCode).toBe(0);
    expect(JSON.parse(output.join("\n"))).toMatchObject({
      packageName: "type-mcp-api-cli",
      cliProtocolVersion: 1,
      manifestVersions: [1],
      commands: ["inspect", "metadata"],
    });
  });

  it("writes a safe inspect JSON result for a local specification", () => {
    const directory = mkdtempSync(join(tmpdir(), "type-mcp-api-cli-command-"));
    const path = join(directory, "openapi.json");
    writeFileSync(
      path,
      JSON.stringify({ openapi: "3.1.0", paths: { "/health": { get: {} } } }),
    );
    const output: string[] = [];

    try {
      const exitCode = runCli(["inspect", "--file", path, "--json"], (line) =>
        output.push(line),
      );

      expect(exitCode).toBe(0);
      expect(JSON.parse(output.join("\n"))).toMatchObject({
        ok: true,
        kind: "openapi",
        declaredVersion: "3.1.0",
        operationCount: 1,
      });
      expect(output.join("\n")).not.toContain(path);
    } finally {
      rmSync(directory, { recursive: true, force: true });
    }
  });
});
