import { createHash } from "node:crypto";

import { describe, expect, it } from "vitest";

import {
  canonicalizeJson,
  computeManifestDigest,
  validateManifestV1,
} from "../src/manifest.js";

const digest = (value: string): string =>
  `sha256:${createHash("sha256").update(value, "utf8").digest("hex")}`;

interface MutableManifest extends Record<string, unknown> {
  manifestDigest: unknown;
  approval: unknown;
  operations: unknown;
}

function manifest(): MutableManifest {
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

describe("manifest contract", () => {
  it("canonicalizes object keys using RFC 8785-compatible JSON ordering", () => {
    expect(canonicalizeJson({ z: [true, null], a: { b: 2, a: 1 } })).toEqual({
      ok: true,
      value: '{"a":{"a":1,"b":2},"z":[true,null]}',
    });
  });

  it("computes the digest from the exact payload that excludes approval and manifestDigest", () => {
    const value = manifest();
    const canonicalPayload =
      '{"authentication":[],"baseUrl":"https://api.example.test","cliProtocolVersion":1,"manifestVersion":1,"operations":[],"source":{"contentHash":"sha256:1111111111111111111111111111111111111111111111111111111111111111","kind":"openapi"},"warnings":[]}';

    expect(computeManifestDigest(value)).toEqual({
      ok: true,
      manifestDigest: digest(canonicalPayload),
    });
  });

  it("accepts only a schema-valid manifest with an exact declared digest", () => {
    const value = manifest();
    const computed = computeManifestDigest(value);
    if (!computed.ok) {
      throw new Error("Fixture manifest must be digestible");
    }
    value.manifestDigest = computed.manifestDigest;
    value.approval = {
      requirement: "none",
      manifestDigest: computed.manifestDigest,
    };

    expect(validateManifestV1(value)).toEqual({
      ok: true,
      manifestDigest: computed.manifestDigest,
    });
  });

  it("does not leak getter errors during digest payload extraction", () => {
    const value = manifest();
    let reads = 0;
    Object.defineProperty(value, "source", {
      configurable: true,
      enumerable: true,
      get() {
        reads += 1;
        if (reads >= 4) {
          throw new Error("SECRET raw payload at /private/path");
        }
        return {
          kind: "openapi",
          contentHash: `sha256:${"1".repeat(64)}`,
        };
      },
    });

    expect(computeManifestDigest(value)).toEqual({
      ok: false,
      error: {
        code: "CANONICALIZATION_FAILED",
        message: "Value cannot be represented as canonical JSON",
      },
    });
  });

  it("does not leak getter errors while comparing a declared digest", () => {
    const value = manifest();
    let reads = 0;
    Object.defineProperty(value, "manifestDigest", {
      configurable: true,
      enumerable: true,
      get() {
        reads += 1;
        if (reads >= 7) {
          throw new Error("SECRET digest getter at /private/path");
        }
        return `sha256:${"0".repeat(64)}`;
      },
    });

    expect(validateManifestV1(value)).toEqual({
      ok: false,
      error: {
        code: "CANONICALIZATION_FAILED",
        message: "Value cannot be represented as canonical JSON",
      },
    });
  });

  it("fails closed for a digest mismatch and schema-invalid values", () => {
    expect(validateManifestV1(manifest())).toEqual({
      ok: false,
      error: {
        code: "MANIFEST_DIGEST_MISMATCH",
        message: "Manifest digest does not match canonical payload",
      },
    });

    const invalid = manifest();
    invalid.operations = ["not-an-operation"];
    expect(validateManifestV1(invalid)).toEqual({
      ok: false,
      error: {
        code: "MANIFEST_SCHEMA_INVALID",
        message: "Manifest does not satisfy schema version 1",
      },
    });
  });

  it("rejects non-finite numbers, lone surrogates, and sparse arrays before canonicalization", () => {
    expect(canonicalizeJson(Number.NaN)).toEqual({
      ok: false,
      error: {
        code: "CANONICALIZATION_FAILED",
        message: "Value cannot be represented as canonical JSON",
      },
    });
    expect(canonicalizeJson("\ud800")).toEqual({
      ok: false,
      error: {
        code: "CANONICALIZATION_FAILED",
        message: "Value cannot be represented as canonical JSON",
      },
    });
    const sparse = new Array<number>(3);
    sparse[0] = 1;
    sparse[2] = 2;
    expect(canonicalizeJson(sparse)).toEqual({
      ok: false,
      error: {
        code: "CANONICALIZATION_FAILED",
        message: "Value cannot be represented as canonical JSON",
      },
    });
  });
});
