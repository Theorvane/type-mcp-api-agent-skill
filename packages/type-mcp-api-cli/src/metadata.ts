export const CLI_PROTOCOL_VERSION = 1;
export const MANIFEST_VERSION = 1;

export interface CliMetadata {
  readonly packageName: "type-mcp-api-cli";
  readonly cliProtocolVersion: typeof CLI_PROTOCOL_VERSION;
  readonly manifestVersions: readonly [typeof MANIFEST_VERSION];
  readonly commands: readonly ["inspect", "metadata"];
}

export function metadata(): CliMetadata {
  return {
    packageName: "type-mcp-api-cli",
    cliProtocolVersion: CLI_PROTOCOL_VERSION,
    manifestVersions: [MANIFEST_VERSION],
    commands: ["inspect", "metadata"],
  };
}
