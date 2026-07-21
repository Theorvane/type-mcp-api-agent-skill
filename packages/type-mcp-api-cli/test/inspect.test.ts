import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { inspectLocalSpec } from "../src/inspect.js";

function withTemporarySource(
  fileName: string,
  content: string,
  run: (path: string) => void,
): void {
  const directory = mkdtempSync(join(tmpdir(), "type-mcp-api-cli-inspect-"));
  const path = join(directory, fileName);
  writeFileSync(path, content, "utf8");

  try {
    run(path);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
}

describe("inspectLocalSpec", () => {
  it("summarizes a local OpenAPI JSON document without exposing its path", () => {
    withTemporarySource(
      "openapi.json",
      JSON.stringify({
        openapi: "3.0.3",
        paths: {
          "/pets": { get: {}, post: {} },
          "/pets/{id}": { get: {}, parameters: [] },
        },
      }),
      (path) => {
        const result = inspectLocalSpec(path);

        expect(result).toMatchObject({
          ok: true,
          kind: "openapi",
          declaredVersion: "3.0.3",
          mediaType: "application/json",
          operationCount: 3,
        });
        expect(JSON.stringify(result)).not.toContain(path);
        expect(JSON.stringify(result)).toMatch(/sha256:[0-9a-f]{64}/);
      },
    );
  });

  it("summarizes a local Swagger YAML document", () => {
    withTemporarySource(
      "swagger.yaml",
      [
        "swagger: '2.0'",
        "paths:",
        "  /pets:",
        "    get: {}",
        "    delete: {}",
      ].join("\n"),
      (path) => {
        expect(inspectLocalSpec(path)).toMatchObject({
          ok: true,
          kind: "swagger",
          declaredVersion: "2.0",
          mediaType: "application/yaml",
          operationCount: 2,
        });
      },
    );
  });

  it("rejects an OpenAPI value that is not a numeric 3.x version", () => {
    withTemporarySource(
      "unsupported-openapi.json",
      JSON.stringify({ openapi: "3.not-a-version", paths: {} }),
      (path) => {
        expect(inspectLocalSpec(path)).toEqual({
          ok: false,
          error: {
            code: "UNSUPPORTED_STRUCTURED_SPEC",
            message: "Unsupported API specification",
          },
        });
      },
    );
  });

  it("returns a safe error for unsupported documents", () => {
    withTemporarySource(
      "private-contract.json",
      '{"token":"do-not-display"}',
      (path) => {
        const result = inspectLocalSpec(path);

        expect(result).toEqual({
          ok: false,
          error: {
            code: "UNSUPPORTED_STRUCTURED_SPEC",
            message: "Unsupported API specification",
          },
        });
        expect(JSON.stringify(result)).not.toContain(path);
        expect(JSON.stringify(result)).not.toContain("do-not-display");
      },
    );
  });
});
