import { createHash } from "node:crypto";
import { readFileSync, realpathSync } from "node:fs";
import { extname } from "node:path";

import { parseDocument } from "yaml";

const OPENAPI_3_VERSION = /^3\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?$/;
const HTTP_METHODS = new Set([
  "delete",
  "get",
  "head",
  "options",
  "patch",
  "post",
  "put",
  "trace",
]);

export interface InspectedStructuredSpec {
  readonly ok: true;
  readonly kind: "openapi" | "swagger";
  readonly declaredVersion: string;
  readonly mediaType: "application/json" | "application/yaml";
  readonly contentHash: string;
  readonly opaqueLocalId: string;
  readonly operationCount: number;
}

export interface SafeInspectionError {
  readonly ok: false;
  readonly error: {
    readonly code:
      | "SOURCE_UNREADABLE"
      | "SOURCE_PARSE_FAILED"
      | "UNSUPPORTED_STRUCTURED_SPEC";
    readonly message: string;
  };
}

export type InspectionResult = InspectedStructuredSpec | SafeInspectionError;

function sha256(value: string | Uint8Array): string {
  return `sha256:${createHash("sha256").update(value).digest("hex")}`;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parseSource(
  content: string,
  extension: string,
): unknown | SafeInspectionError {
  if (extension === ".json") {
    try {
      return JSON.parse(content) as unknown;
    } catch {
      return {
        ok: false,
        error: {
          code: "SOURCE_PARSE_FAILED",
          message: "Unable to parse API specification",
        },
      };
    }
  }

  if (extension === ".yaml" || extension === ".yml") {
    const document = parseDocument(content, { uniqueKeys: true });
    if (document.errors.length > 0) {
      return {
        ok: false,
        error: {
          code: "SOURCE_PARSE_FAILED",
          message: "Unable to parse API specification",
        },
      };
    }
    return document.toJS();
  }

  return {
    ok: false,
    error: {
      code: "UNSUPPORTED_STRUCTURED_SPEC",
      message: "Unsupported API specification",
    },
  };
}

function countOperations(paths: unknown): number {
  if (!isRecord(paths)) {
    return 0;
  }

  let count = 0;
  for (const pathItem of Object.values(paths)) {
    if (!isRecord(pathItem)) {
      continue;
    }
    for (const method of Object.keys(pathItem)) {
      if (HTTP_METHODS.has(method)) {
        count += 1;
      }
    }
  }
  return count;
}

function getField(record: Record<string, unknown>, key: string): unknown {
  return record[key];
}

function isSafeError(value: unknown): value is SafeInspectionError {
  return (
    isRecord(value) &&
    getField(value, "ok") === false &&
    isRecord(getField(value, "error"))
  );
}

export function inspectLocalSpec(path: string): InspectionResult {
  let sourceBytes: Uint8Array;
  let content: string;
  let resolvedPath: string;
  try {
    resolvedPath = realpathSync(path);
    sourceBytes = readFileSync(resolvedPath);
    content = Buffer.from(sourceBytes).toString("utf8");
  } catch {
    return {
      ok: false,
      error: {
        code: "SOURCE_UNREADABLE",
        message: "Unable to read API specification",
      },
    };
  }

  const parsed = parseSource(content, extname(resolvedPath).toLowerCase());
  if (isSafeError(parsed)) {
    return parsed;
  }
  if (!isRecord(parsed)) {
    return {
      ok: false,
      error: {
        code: "UNSUPPORTED_STRUCTURED_SPEC",
        message: "Unsupported API specification",
      },
    };
  }

  const openapi = getField(parsed, "openapi");
  if (typeof openapi === "string" && OPENAPI_3_VERSION.test(openapi)) {
    return {
      ok: true,
      kind: "openapi",
      declaredVersion: openapi,
      mediaType:
        extname(resolvedPath).toLowerCase() === ".json"
          ? "application/json"
          : "application/yaml",
      contentHash: sha256(sourceBytes),
      opaqueLocalId: `local:${sha256(resolvedPath)}`,
      operationCount: countOperations(getField(parsed, "paths")),
    };
  }

  if (getField(parsed, "swagger") === "2.0") {
    return {
      ok: true,
      kind: "swagger",
      declaredVersion: "2.0",
      mediaType:
        extname(resolvedPath).toLowerCase() === ".json"
          ? "application/json"
          : "application/yaml",
      contentHash: sha256(sourceBytes),
      opaqueLocalId: `local:${sha256(resolvedPath)}`,
      operationCount: countOperations(getField(parsed, "paths")),
    };
  }

  return {
    ok: false,
    error: {
      code: "UNSUPPORTED_STRUCTURED_SPEC",
      message: "Unsupported API specification",
    },
  };
}
