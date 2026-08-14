"""Static Playwright and Chromium binding for the generic browser payload path."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from hashlib import sha256
from importlib import metadata
import json
from pathlib import Path
import re


class BrowserPayloadRuntimeBindingError(ValueError):
    """Raised when the browser payload runtime cannot be bound statically."""


_VERSION = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}(?:[-+][0-9A-Za-z.-]+)?$")
_REVISION = re.compile(r"^[0-9]+$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MANIFEST_ENTRY = "chromium-headless-shell"


@dataclass(frozen=True, slots=True)
class BrowserPayloadRuntimeBinding:
    binding_id: str
    distribution_name: str
    package_version: str
    engine_id: str
    manifest_entry_name: str
    engine_version: str
    browser_revision: str
    requirements_path: str
    requirements_sha256: str
    manifest_path: str
    manifest_sha256: str
    executable_real_path: str
    executable_size_bytes: int
    executable_sha256: str
    browser_started: bool = False

    def __post_init__(self) -> None:
        if self.binding_id != "browser.payload.runtime.chromium.v1":
            raise BrowserPayloadRuntimeBindingError("runtime binding identity changed")
        if self.distribution_name != "playwright" or self.engine_id != "chromium":
            raise BrowserPayloadRuntimeBindingError("runtime binding engine changed")
        if self.manifest_entry_name != _MANIFEST_ENTRY:
            raise BrowserPayloadRuntimeBindingError(
                "runtime binding requires chromium-headless-shell"
            )
        if not _VERSION.fullmatch(self.package_version) or not _VERSION.fullmatch(
            self.engine_version
        ):
            raise BrowserPayloadRuntimeBindingError("runtime version is invalid")
        if not _REVISION.fullmatch(self.browser_revision):
            raise BrowserPayloadRuntimeBindingError("browser revision is invalid")
        for role in (
            "requirements_sha256",
            "manifest_sha256",
            "executable_sha256",
        ):
            if not _SHA256.fullmatch(getattr(self, role)):
                raise BrowserPayloadRuntimeBindingError(f"{role} is invalid")
        if (
            isinstance(self.executable_size_bytes, bool)
            or not isinstance(self.executable_size_bytes, int)
            or self.executable_size_bytes <= 0
        ):
            raise BrowserPayloadRuntimeBindingError("browser executable is empty")
        if self.browser_started:
            raise BrowserPayloadRuntimeBindingError(
                "static runtime binding cannot start a browser"
            )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _regular_real_file(path: Path, role: str) -> Path:
    candidate = Path(path)
    if candidate.is_symlink():
        raise BrowserPayloadRuntimeBindingError(f"{role} cannot be a symlink")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise BrowserPayloadRuntimeBindingError(f"{role} does not exist") from exc
    if not resolved.is_file():
        raise BrowserPayloadRuntimeBindingError(f"{role} must be a regular file")
    return resolved


def bind_browser_payload_runtime(
    *,
    package_version: str,
    requirements_path: Path,
    manifest_path: Path,
    executable_path: Path,
    installation_root: Path,
) -> BrowserPayloadRuntimeBinding:
    """Bind one generic headless Chromium runtime using static reads only."""

    if not isinstance(package_version, str) or not _VERSION.fullmatch(
        package_version
    ):
        raise BrowserPayloadRuntimeBindingError("Playwright package version is invalid")
    requirements = _regular_real_file(requirements_path, "browser requirements")
    manifest = _regular_real_file(manifest_path, "browser manifest")
    executable = _regular_real_file(executable_path, "browser executable")
    root_input = Path(installation_root)
    if root_input.is_symlink():
        raise BrowserPayloadRuntimeBindingError(
            "browser installation root cannot be a symlink"
        )
    try:
        root = root_input.resolve(strict=True)
    except OSError as exc:
        raise BrowserPayloadRuntimeBindingError(
            "browser installation root does not exist"
        ) from exc
    if not root.is_dir() or not executable.is_relative_to(root):
        raise BrowserPayloadRuntimeBindingError(
            "browser executable escaped its installation root"
        )

    requirements_bytes = requirements.read_bytes()
    try:
        requirement_lines = tuple(
            line.strip()
            for line in requirements_bytes.decode("utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    except UnicodeDecodeError as exc:
        raise BrowserPayloadRuntimeBindingError(
            "browser requirements are not UTF-8"
        ) from exc
    pins = tuple(line for line in requirement_lines if line.startswith("playwright=="))
    if pins != (f"playwright=={package_version}",):
        raise BrowserPayloadRuntimeBindingError(
            "Playwright package version differs from the exact requirements pin"
        )

    manifest_bytes = manifest.read_bytes()
    try:
        payload = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BrowserPayloadRuntimeBindingError(
            "browser manifest is not valid UTF-8 JSON"
        ) from exc
    if (
        not isinstance(payload, dict)
        or not isinstance(payload.get("browsers"), list)
        or not set(payload).issubset({"comment", "browsers"})
    ):
        raise BrowserPayloadRuntimeBindingError("browser manifest root changed")
    matches = [
        item
        for item in payload["browsers"]
        if isinstance(item, dict) and item.get("name") == _MANIFEST_ENTRY
    ]
    if len(matches) != 1:
        raise BrowserPayloadRuntimeBindingError(
            "chromium-headless-shell manifest entry is not unique"
        )
    revision = matches[0].get("revision")
    engine_version = matches[0].get("browserVersion")
    if not isinstance(revision, str) or not _REVISION.fullmatch(revision):
        raise BrowserPayloadRuntimeBindingError("browser revision is not bound")
    if not isinstance(engine_version, str) or not _VERSION.fullmatch(engine_version):
        raise BrowserPayloadRuntimeBindingError("browser engine version is not bound")

    stat = executable.stat()
    return BrowserPayloadRuntimeBinding(
        binding_id="browser.payload.runtime.chromium.v1",
        distribution_name="playwright",
        package_version=package_version,
        engine_id="chromium",
        manifest_entry_name=_MANIFEST_ENTRY,
        engine_version=engine_version,
        browser_revision=revision,
        requirements_path=str(requirements),
        requirements_sha256=sha256(requirements_bytes).hexdigest(),
        manifest_path=str(manifest),
        manifest_sha256=sha256(manifest_bytes).hexdigest(),
        executable_real_path=str(executable),
        executable_size_bytes=stat.st_size,
        executable_sha256=_sha256_file(executable),
    )


def bind_installed_browser_payload_runtime(
    *,
    requirements_path: Path,
    executable_path: Path,
    installation_root: Path,
) -> BrowserPayloadRuntimeBinding:
    """Locate the installed manifest without importing Playwright."""

    try:
        distribution = metadata.distribution("playwright")
    except metadata.PackageNotFoundError as exc:
        raise BrowserPayloadRuntimeBindingError("Playwright is not installed") from exc
    package_root = Path(distribution.locate_file("playwright")).resolve(strict=True)
    return bind_browser_payload_runtime(
        package_version=distribution.version,
        requirements_path=requirements_path,
        manifest_path=package_root / "driver" / "package" / "browsers.json",
        executable_path=executable_path,
        installation_root=installation_root,
    )


def verify_browser_payload_runtime_binding(
    binding: BrowserPayloadRuntimeBinding,
) -> None:
    """Verify that every statically bound runtime file is unchanged."""

    if not isinstance(binding, BrowserPayloadRuntimeBinding):
        raise BrowserPayloadRuntimeBindingError(
            "runtime verification requires a browser payload binding"
        )
    for path_value, size_role, digest_role in (
        (binding.requirements_path, None, "requirements_sha256"),
        (binding.manifest_path, None, "manifest_sha256"),
        (
            binding.executable_real_path,
            "executable_size_bytes",
            "executable_sha256",
        ),
    ):
        path = Path(path_value)
        if path.is_symlink() or not path.is_file():
            raise BrowserPayloadRuntimeBindingError(
                "bound runtime file is unavailable"
            )
        if size_role and path.stat().st_size != getattr(binding, size_role):
            raise BrowserPayloadRuntimeBindingError(
                "bound browser executable size changed"
            )
        if _sha256_file(path) != getattr(binding, digest_role):
            raise BrowserPayloadRuntimeBindingError(
                "bound runtime file digest changed"
            )


def browser_payload_runtime_binding_json_value(
    binding: BrowserPayloadRuntimeBinding,
) -> dict[str, object]:
    if not isinstance(binding, BrowserPayloadRuntimeBinding):
        raise BrowserPayloadRuntimeBindingError(
            "JSON projection requires a browser payload runtime binding"
        )
    return asdict(binding)


def browser_payload_runtime_binding_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(BrowserPayloadRuntimeBinding))
