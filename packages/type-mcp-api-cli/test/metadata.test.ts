import { describe, expect, it } from "vitest";

import {
  CLI_PROTOCOL_VERSION,
  MANIFEST_VERSION,
  metadata,
} from "../src/metadata.js";

describe("metadata", () => {
  it("returns the stable package, protocol, schema, and command contract", () => {
    expect(metadata()).toEqual({
      packageName: "type-mcp-api-cli",
      cliProtocolVersion: CLI_PROTOCOL_VERSION,
      manifestVersions: [MANIFEST_VERSION],
      commands: ["inspect", "metadata"],
    });
  });
});
