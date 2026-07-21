import { mkdtempSync, realpathSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { isCliEntrypoint } from "../src/cli.js";

describe("isCliEntrypoint", () => {
  it("recognizes the real entry module when npm invokes it through a symlink", () => {
    const directory = mkdtempSync(
      join(tmpdir(), "type-mcp-api-cli-entrypoint-"),
    );
    const target = join(directory, "cli.js");
    const bin = join(directory, "type-mcp-api-cli");
    writeFileSync(target, "", "utf8");
    symlinkSync(target, bin);

    expect(
      isCliEntrypoint(new URL(`file://${realpathSync(target)}`).href, bin),
    ).toBe(true);
  });
});
