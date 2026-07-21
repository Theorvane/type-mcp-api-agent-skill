import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

import {
  Ajv2020,
  type AnySchema,
  type ValidateFunction,
} from "ajv/dist/2020.js";

const MANIFEST_SCHEMA_URL = new URL(
  "../schemas/api-manifest-1.schema.json",
  import.meta.url,
);

const DIGEST_PAYLOAD_KEYS = [
  "manifestVersion",
  "cliProtocolVersion",
  "source",
  "baseUrl",
  "operations",
  "authentication",
  "warnings",
] as const;

type DigestPayloadKey = (typeof DIGEST_PAYLOAD_KEYS)[number];

export interface CanonicalJsonSuccess {
  readonly ok: true;
  readonly value: string;
}

export interface ManifestDigestSuccess {
  readonly ok: true;
  readonly manifestDigest: string;
}

export interface ManifestContractError {
  readonly ok: false;
  readonly error: {
    readonly code:
      | "CANONICALIZATION_FAILED"
      | "MANIFEST_DIGEST_MISMATCH"
      | "MANIFEST_SCHEMA_INVALID";
    readonly message: string;
  };
}

export type CanonicalJsonResult = CanonicalJsonSuccess | ManifestContractError;
export type ManifestDigestResult =
  | ManifestDigestSuccess
  | ManifestContractError;
export type ManifestValidationResult =
  | ManifestDigestSuccess
  | ManifestContractError;

let validator: ValidateFunction | undefined;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isSchema(value: unknown): value is AnySchema {
  return (
    typeof value === "boolean" || (typeof value === "object" && value !== null)
  );
}

function getSchemaValidator(): ValidateFunction {
  if (validator !== undefined) {
    return validator;
  }

  const parsed = JSON.parse(
    readFileSync(MANIFEST_SCHEMA_URL, "utf8"),
  ) as unknown;
  if (!isSchema(parsed)) {
    throw new Error("Manifest schema must be a JSON Schema");
  }

  validator = new Ajv2020({
    strict: true,
    formats: { "date-time": true },
  }).compile(parsed);
  return validator;
}

function hasLoneSurrogate(value: string): boolean {
  for (let index = 0; index < value.length; index += 1) {
    const codeUnit = value.charCodeAt(index);
    if (codeUnit >= 0xd800 && codeUnit <= 0xdbff) {
      const next = value.charCodeAt(index + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) {
        return true;
      }
      index += 1;
      continue;
    }
    if (codeUnit >= 0xdc00 && codeUnit <= 0xdfff) {
      return true;
    }
  }
  return false;
}

function canonicalizeValue(value: unknown, ancestors: WeakSet<object>): string {
  if (
    value === null ||
    typeof value === "boolean" ||
    typeof value === "string"
  ) {
    if (typeof value === "string" && hasLoneSurrogate(value)) {
      throw new Error("Invalid Unicode");
    }
    return JSON.stringify(value);
  }

  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      throw new Error("Non-finite number");
    }
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    if (ancestors.has(value)) {
      throw new Error("Cyclic array");
    }
    ancestors.add(value);
    try {
      const serializedItems: string[] = [];
      for (let index = 0; index < value.length; index += 1) {
        if (!Object.hasOwn(value, index)) {
          throw new Error("Sparse array");
        }
        serializedItems.push(canonicalizeValue(value[index], ancestors));
      }
      return `[${serializedItems.join(",")}]`;
    } finally {
      ancestors.delete(value);
    }
  }

  if (!isRecord(value)) {
    throw new Error("Non-JSON value");
  }
  if (ancestors.has(value)) {
    throw new Error("Cyclic object");
  }

  ancestors.add(value);
  try {
    const keys = Object.keys(value).sort();
    return `{${keys
      .map((key) => {
        if (hasLoneSurrogate(key)) {
          throw new Error("Invalid Unicode");
        }
        return `${JSON.stringify(key)}:${canonicalizeValue(value[key], ancestors)}`;
      })
      .join(",")}}`;
  } finally {
    ancestors.delete(value);
  }
}

function canonicalizationError(): ManifestContractError {
  return {
    ok: false,
    error: {
      code: "CANONICALIZATION_FAILED",
      message: "Value cannot be represented as canonical JSON",
    },
  };
}

function schemaError(): ManifestContractError {
  return {
    ok: false,
    error: {
      code: "MANIFEST_SCHEMA_INVALID",
      message: "Manifest does not satisfy schema version 1",
    },
  };
}

function manifestDigestMismatch(): ManifestContractError {
  return {
    ok: false,
    error: {
      code: "MANIFEST_DIGEST_MISMATCH",
      message: "Manifest digest does not match canonical payload",
    },
  };
}

function validatedManifest(
  value: unknown,
): Record<string, unknown> | ManifestContractError {
  try {
    if (!isRecord(value) || !getSchemaValidator()(value)) {
      return schemaError();
    }
    return value;
  } catch {
    return schemaError();
  }
}

function getField(record: object, key: string): unknown {
  return Reflect.get(record, key);
}

function isContractError(
  value: Record<string, unknown> | ManifestContractError,
): value is ManifestContractError {
  return getField(value, "ok") === false && isRecord(getField(value, "error"));
}

function digestPayload(
  manifest: Record<string, unknown>,
): Record<DigestPayloadKey, unknown> {
  return {
    manifestVersion: getField(manifest, "manifestVersion"),
    cliProtocolVersion: getField(manifest, "cliProtocolVersion"),
    source: getField(manifest, "source"),
    baseUrl: getField(manifest, "baseUrl"),
    operations: getField(manifest, "operations"),
    authentication: getField(manifest, "authentication"),
    warnings: getField(manifest, "warnings"),
  };
}

export function canonicalizeJson(value: unknown): CanonicalJsonResult {
  try {
    return {
      ok: true,
      value: canonicalizeValue(value, new WeakSet<object>()),
    };
  } catch {
    return canonicalizationError();
  }
}

export function computeManifestDigest(value: unknown): ManifestDigestResult {
  const manifest = validatedManifest(value);
  if (isContractError(manifest)) {
    return manifest;
  }

  let payload: Record<DigestPayloadKey, unknown>;
  try {
    payload = digestPayload(manifest);
  } catch {
    return canonicalizationError();
  }

  const canonical = canonicalizeJson(payload);
  if (!canonical.ok) {
    return canonical;
  }

  return {
    ok: true,
    manifestDigest: `sha256:${createHash("sha256")
      .update(canonical.value, "utf8")
      .digest("hex")}`,
  };
}

export function validateManifestV1(value: unknown): ManifestValidationResult {
  const manifest = validatedManifest(value);
  if (isContractError(manifest)) {
    return manifest;
  }

  const computed = computeManifestDigest(manifest);
  if (!computed.ok) {
    return computed;
  }
  let declaredDigest: unknown;
  try {
    declaredDigest = getField(manifest, "manifestDigest");
  } catch {
    return canonicalizationError();
  }
  if (declaredDigest !== computed.manifestDigest) {
    return manifestDigestMismatch();
  }
  return computed;
}
