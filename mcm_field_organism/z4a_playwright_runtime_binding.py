"""Static Playwright distribution and Chromium binary binding for Z4-A2."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from hashlib import sha256
from importlib import metadata
import json
from pathlib import Path
import re


class Z4APlaywrightRuntimeBindingError(ValueError):
    """Raised when a Playwright installation cannot be bound without execution."""


_VERSION = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}(?:[-+][0-9A-Za-z.-]+)?$")
_REVISION = re.compile(r"^[0-9]+$")
_BROWSER_ENTRIES = frozenset(("chromium", "chromium-headless-shell"))


@dataclass(frozen=True, slots=True)
class Z4APlaywrightRuntimeBinding:
    binding_id: str
    distribution_name: str
    package_version: str
    engine_id: str
    manifest_entry_name: str
    engine_version: str
    browser_revision: str
    manifest_path: str
    manifest_sha256: str
    executable_real_path: str
    executable_size_bytes: int
    executable_sha256: str
    browser_started: bool = False

    def __post_init__(self) -> None:
        if self.binding_id != "z4a.playwright-runtime.chromium.v1":
            raise Z4APlaywrightRuntimeBindingError("runtime binding identity changed")
        if self.distribution_name != "playwright" or self.engine_id != "chromium":
            raise Z4APlaywrightRuntimeBindingError("runtime binding engine changed")
        if not _VERSION.fullmatch(self.package_version):
            raise Z4APlaywrightRuntimeBindingError("Playwright package version is invalid")
        if self.manifest_entry_name not in _BROWSER_ENTRIES:
            raise Z4APlaywrightRuntimeBindingError("unsupported Chromium manifest entry")
        if not _VERSION.fullmatch(self.engine_version):
            raise Z4APlaywrightRuntimeBindingError("Chromium engine version is invalid")
        if not _REVISION.fullmatch(self.browser_revision):
            raise Z4APlaywrightRuntimeBindingError("Chromium revision is invalid")
        for role in ("manifest_sha256", "executable_sha256"):
            value = getattr(self, role)
            if not re.fullmatch(r"[0-9a-f]{64}", value):
                raise Z4APlaywrightRuntimeBindingError(f"{role} is invalid")
        if self.executable_size_bytes <= 0:
            raise Z4APlaywrightRuntimeBindingError("Chromium binary is empty")
        if self.browser_started:
            raise Z4APlaywrightRuntimeBindingError("static binding cannot start a browser")


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _regular_real_file(path: Path, role: str) -> Path:
    candidate = Path(path)
    if candidate.is_symlink():
        raise Z4APlaywrightRuntimeBindingError(f"{role} cannot be a symlink")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise Z4APlaywrightRuntimeBindingError(f"{role} does not exist") from exc
    if not resolved.is_file():
        raise Z4APlaywrightRuntimeBindingError(f"{role} must be a regular file")
    return resolved


def bind_z4a_playwright_runtime(
    *,
    package_version: str,
    manifest_path: Path,
    manifest_entry_name: str,
    executable_path: Path,
    installation_root: Path,
) -> Z4APlaywrightRuntimeBinding:
    """Bind one manifest entry and binary by static reads only."""

    if not isinstance(package_version, str) or not _VERSION.fullmatch(package_version):
        raise Z4APlaywrightRuntimeBindingError("Playwright package version is invalid")
    if manifest_entry_name not in _BROWSER_ENTRIES:
        raise Z4APlaywrightRuntimeBindingError("unsupported Chromium manifest entry")
    manifest = _regular_real_file(Path(manifest_path), "browser manifest")
    executable = _regular_real_file(Path(executable_path), "Chromium binary")
    root_input = Path(installation_root)
    if root_input.is_symlink():
        raise Z4APlaywrightRuntimeBindingError("installation root cannot be a symlink")
    try:
        root = root_input.resolve(strict=True)
    except OSError as exc:
        raise Z4APlaywrightRuntimeBindingError("installation root does not exist") from exc
    if not root.is_dir():
        raise Z4APlaywrightRuntimeBindingError("installation root must be a real directory")
    if not executable.is_relative_to(root):
        raise Z4APlaywrightRuntimeBindingError("Chromium binary escaped installation root")

    manifest_bytes = manifest.read_bytes()
    try:
        payload = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Z4APlaywrightRuntimeBindingError("browser manifest is not valid UTF-8 JSON") from exc
    if (
        not isinstance(payload, dict)
        or "browsers" not in payload
        or not set(payload).issubset({"comment", "browsers"})
        or ("comment" in payload and not isinstance(payload["comment"], str))
    ):
        raise Z4APlaywrightRuntimeBindingError("browser manifest root changed")
    browsers = payload["browsers"]
    if not isinstance(browsers, list):
        raise Z4APlaywrightRuntimeBindingError("browser manifest inventory changed")
    matches = [
        item
        for item in browsers
        if isinstance(item, dict) and item.get("name") == manifest_entry_name
    ]
    if len(matches) != 1:
        raise Z4APlaywrightRuntimeBindingError("browser manifest entry is not unique")
    entry = matches[0]
    revision = entry.get("revision")
    engine_version = entry.get("browserVersion")
    if not isinstance(revision, str) or not _REVISION.fullmatch(revision):
        raise Z4APlaywrightRuntimeBindingError("browser revision is not bound")
    if not isinstance(engine_version, str) or not _VERSION.fullmatch(engine_version):
        raise Z4APlaywrightRuntimeBindingError("browser engine version is not bound")

    stat = executable.stat()
    return Z4APlaywrightRuntimeBinding(
        binding_id="z4a.playwright-runtime.chromium.v1",
        distribution_name="playwright",
        package_version=package_version,
        engine_id="chromium",
        manifest_entry_name=manifest_entry_name,
        engine_version=engine_version,
        browser_revision=revision,
        manifest_path=str(manifest),
        manifest_sha256=sha256(manifest_bytes).hexdigest(),
        executable_real_path=str(executable),
        executable_size_bytes=stat.st_size,
        executable_sha256=_sha256_file(executable),
    )


def bind_installed_z4a_playwright_runtime(
    *,
    manifest_entry_name: str,
    executable_path: Path,
    installation_root: Path,
) -> Z4APlaywrightRuntimeBinding:
    """Read the installed distribution metadata without importing Playwright."""

    try:
        distribution = metadata.distribution("playwright")
    except metadata.PackageNotFoundError as exc:
        raise Z4APlaywrightRuntimeBindingError("Playwright is not installed") from exc
    package_root = Path(distribution.locate_file("playwright")).resolve(strict=True)
    manifest = package_root / "driver" / "package" / "browsers.json"
    return bind_z4a_playwright_runtime(
        package_version=distribution.version,
        manifest_path=manifest,
        manifest_entry_name=manifest_entry_name,
        executable_path=executable_path,
        installation_root=installation_root,
    )


def z4a_playwright_runtime_binding_json_value(
    binding: Z4APlaywrightRuntimeBinding,
) -> dict[str, object]:
    if not isinstance(binding, Z4APlaywrightRuntimeBinding):
        raise Z4APlaywrightRuntimeBindingError("JSON projection requires a runtime binding")
    return asdict(binding)


def z4a_playwright_runtime_binding_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(Z4APlaywrightRuntimeBinding))
