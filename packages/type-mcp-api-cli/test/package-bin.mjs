import { execFileSync } from "node:child_process";
import { existsSync, mkdtempSync, rmSync, unlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const repositoryRoot = fileURLToPath(new URL("..", import.meta.url));
const consumerDirectory = mkdtempSync(join(tmpdir(), "type-mcp-api-cli-consumer-"));
let tarballPath;

try {
  const tarballName = execFileSync("npm", ["pack", "--silent"], {
    cwd: repositoryRoot,
    encoding: "utf8",
  }).trim();
  tarballPath = join(repositoryRoot, tarballName);
  if (!existsSync(tarballPath)) {
    throw new Error(`npm pack did not create ${tarballName}`);
  }

  execFileSync("npm", ["init", "--yes"], {
    cwd: consumerDirectory,
    stdio: "ignore",
  });
  execFileSync("npm", ["install", "--ignore-scripts", tarballPath], {
    cwd: consumerDirectory,
    stdio: "ignore",
  });

  const bin = join(consumerDirectory, "node_modules", ".bin", "type-mcp-api-cli");
  const output = execFileSync(bin, ["metadata", "--json"], {
    cwd: consumerDirectory,
    encoding: "utf8",
  });
  const parsed = JSON.parse(output);
  if (
    typeof parsed !== "object" ||
    parsed === null ||
    !("packageName" in parsed) ||
    parsed.packageName !== "type-mcp-api-cli"
  ) {
    throw new Error("Installed bin did not emit expected metadata JSON");
  }

  const inspectSource = join(consumerDirectory, "openapi.json");
  writeFileSync(
    inspectSource,
    JSON.stringify({ openapi: "3.0.3", paths: { "/health": { get: {} } } }),
    "utf8",
  );
  const inspectOutput = execFileSync(bin, ["inspect", "--file", inspectSource, "--json"], {
    cwd: consumerDirectory,
    encoding: "utf8",
  });
  const inspected = JSON.parse(inspectOutput);
  if (
    typeof inspected !== "object" ||
    inspected === null ||
    !("ok" in inspected) ||
    inspected.ok !== true ||
    !("operationCount" in inspected) ||
    inspected.operationCount !== 1 ||
    inspectOutput.includes(inspectSource)
  ) {
    throw new Error("Installed bin did not emit expected safe inspect JSON");
  }

  process.stdout.write(`verified installed bin from ${basename(tarballPath)}\n`);
} finally {
  if (tarballPath !== undefined && existsSync(tarballPath)) {
    unlinkSync(tarballPath);
  }
  rmSync(consumerDirectory, { recursive: true, force: true });
}
