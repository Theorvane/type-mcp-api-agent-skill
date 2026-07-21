import { readFileSync } from "node:fs";
import { Ajv2020, type AnySchema } from "ajv/dist/2020.js";

import { describe, expect, it } from "vitest";

const schemaPath = new URL(
  "../schemas/api-manifest-1.schema.json",
  import.meta.url,
);
const schema = JSON.parse(readFileSync(schemaPath, "utf8")) as unknown;

function isSchema(value: unknown): value is AnySchema {
  return (
    typeof value === "boolean" || (typeof value === "object" && value !== null)
  );
}

function compileSchema() {
  if (!isSchema(schema)) {
    throw new Error("Schema must be a JSON Schema object or boolean");
  }

  return new Ajv2020({
    strict: true,
    formats: { "date-time": true },
  }).compile(schema);
}

function validManifest(): Record<string, unknown> {
  return {
    manifestVersion: 1,
    cliProtocolVersion: 1,
    manifestDigest: `sha256:${"0".repeat(64)}`,
    source: {
      kind: "openapi",
      contentHash: `sha256:${"1".repeat(64)}`,
    },
    baseUrl: "https://api.example.test",
    operations: [],
    authentication: [],
    warnings: [],
    approval: {
      requirement: "none",
      manifestDigest: `sha256:${"0".repeat(64)}`,
    },
  };
}

describe("api-manifest-1 schema", () => {
  it("rejects unknown fields in nested approval objects", () => {
    const validate = compileSchema();
    const manifest = validManifest();
    manifest["approval"] = {
      requirement: "none",
      manifestDigest: `sha256:${"0".repeat(64)}`,
      injected: true,
    };

    expect(validate(manifest)).toBe(false);
  });

  it("rejects non-object operation array items", () => {
    const validate = compileSchema();
    const manifest = validManifest();
    manifest["operations"] = ["not-an-operation"];

    expect(validate(manifest)).toBe(false);
  });
});
