"""Atomic JSON MCP configuration mutation with fingerprint and rollback gates."""
from __future__ import annotations
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Callable
from agent_clients import McpServerSpec
from config_codecs import UnsupportedConfigFormat, render_codex_toml
from install_plan import InstallPlan, InstallPlanError, InstallTarget, validate_install_receipt


class InstallError(RuntimeError):
    pass


@dataclass(frozen=True)
class ApplyResult:
    config_path: Path
    backup_path: Path
    status: str


def _fingerprint(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise InstallError("configuration target must remain a regular non-symlink file")
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def _entry(spec: McpServerSpec) -> dict[str, object]:
    return {"command": spec.command, "args": list(spec.args), "cwd": str(spec.cwd)}


def _atomic_write(path: Path, content: bytes) -> None:
    parent = path.parent
    if parent.is_symlink() or not parent.is_dir():
        raise InstallError("configuration parent must be an existing non-symlink directory")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=parent)
    temp = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp, 0o600)
        os.replace(temp, path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def _backup(path: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise InstallError("refusing to overwrite an existing backup")
    shutil.copyfile(path, destination)
    os.chmod(destination, 0o600)


def _server_container(config: dict[str, object], client_id: str) -> dict[str, object]:
    if client_id == "opencode":
        mcp = config.setdefault("mcp", {})
        if not isinstance(mcp, dict):
            raise InstallError("OpenCode configuration mcp must be an object")
        servers = mcp.setdefault("servers", {})
    else:
        servers = config.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise InstallError("configuration MCP server collection must be an object")
    return servers


def _apply_json_target(
    target: InstallTarget,
    spec: McpServerSpec,
    *,
    verifier: Callable[[], bool] | None = None,
) -> ApplyResult:
    """Apply a target after the caller has consumed the plan confirmation."""
    path = target.config_path
    if path.is_symlink() or not path.is_file():
        raise InstallError("configuration target must be an existing regular JSON file")
    if _fingerprint(path) != target.config_fingerprint:
        raise InstallError("configuration changed since the reviewed plan")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise InstallError("configuration JSON is invalid") from exc
    if not isinstance(config, dict):
        raise InstallError("configuration root must be an object")
    servers = _server_container(config, target.client_id)
    if spec.name in servers:
        raise InstallError("server name already exists; replacement needs a fresh plan")
    _backup(path, target.backup_path)
    servers[spec.name] = _entry(spec)
    try:
        _atomic_write(path, (json.dumps(config, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        if verifier is not None and not verifier():
            raise InstallError("target verification failed")
    except Exception as exc:
        try:
            _atomic_write(path, target.backup_path.read_bytes())
        except Exception as rollback_error:
            raise InstallError("installation failed and rollback failed") from rollback_error
        if isinstance(exc, InstallError):
            raise
        raise InstallError("installation failed; target was restored") from exc
    return ApplyResult(path, target.backup_path, "verified" if verifier else "written")


def _apply_codex_target(target: InstallTarget, spec: McpServerSpec) -> ApplyResult:
    path = target.config_path
    if path.is_symlink() or not path.is_file() or _fingerprint(path) != target.config_fingerprint:
        raise InstallError("Codex configuration changed since the reviewed plan")
    try:
        rendered = render_codex_toml(path.read_text(encoding="utf-8"), spec)
    except (UnicodeDecodeError, UnsupportedConfigFormat) as exc:
        raise InstallError("Codex configuration is not safely editable") from exc
    _backup(path, target.backup_path)
    try:
        _atomic_write(path, rendered.encode("utf-8"))
    except Exception as exc:
        try: _atomic_write(path, target.backup_path.read_bytes())
        except Exception as rollback_error: raise InstallError("Codex installation failed and rollback failed") from rollback_error
        raise InstallError("Codex installation failed; target was restored") from exc
    return ApplyResult(path, target.backup_path, "written")


def apply_native_plan(
    plan: InstallPlan,
    spec: McpServerSpec,
    *,
    verifiers: dict[str, Callable[[], bool]] | None = None,
) -> tuple[ApplyResult, ...]:
    """Consume one receipt and apply each supported native adapter once."""
    if plan.server != spec:
        raise InstallError("server specification is not bound to the supplied plan")
    allowed = {"codex", "cursor", "vscode-copilot", "gemini-cli", "opencode"}
    if any(target.client_id not in allowed for target in plan.targets):
        raise InstallError("plan contains an export-only or unsupported target")
    try: validate_install_receipt(plan)
    except InstallPlanError as exc: raise InstallError(str(exc)) from exc
    checks = verifiers or {}
    results: list[ApplyResult] = []
    for target in plan.targets:
        if target.client_id == "codex":
            results.append(_apply_codex_target(target, spec))
        else:
            results.append(_apply_json_target(target, spec, verifier=checks.get(target.client_id)))
    return tuple(results)


def apply_json_plan(
    plan: InstallPlan,
    spec: McpServerSpec,
    *,
    verifiers: dict[str, Callable[[], bool]] | None = None,
) -> tuple[ApplyResult, ...]:
    """Consume one receipt and apply every selected JSON target in plan order."""
    if plan.server != spec:
        raise InstallError("server specification is not bound to the supplied plan")
    allowed = {"cursor", "vscode-copilot", "gemini-cli", "opencode"}
    if any(target.client_id not in allowed for target in plan.targets):
        raise InstallError("plan contains a target that requires a non-JSON adapter")
    try:
        validate_install_receipt(plan)
    except InstallPlanError as exc:
        raise InstallError(str(exc)) from exc
    checks = verifiers or {}
    return tuple(
        _apply_json_target(target, spec, verifier=checks.get(target.client_id))
        for target in plan.targets
    )


def apply_json_target(
    target: InstallTarget,
    spec: McpServerSpec,
    *,
    plan: InstallPlan,
    verifier: Callable[[], bool] | None = None,
) -> ApplyResult:
    """Compatibility single-target entry point with the same receipt boundary."""
    if plan.targets != (target,):
        raise InstallError("single-target apply requires a plan containing exactly that target")
    return apply_json_plan(plan, spec, verifiers={target.client_id: verifier} if verifier else None)[0]
