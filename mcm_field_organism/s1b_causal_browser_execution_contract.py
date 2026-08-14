"""Static one-shot browser execution contract for the S1-B causal check."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from importlib import metadata
import json
from pathlib import Path
import re

from .browser_payload_runtime import (
    BrowserPayloadRuntimeBinding,
    browser_payload_runtime_binding_json_value,
    verify_browser_payload_runtime_binding,
)
from .browser_payload_source import browser_payload_asset_digests
from .s1b_causal_browser_world import S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST


class S1BCausalBrowserExecutionContractError(ValueError):
    """Raised when the one-shot browser preflight is not reproducible."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_EXPECTED_ASSETS = (
    ("index.html", "74fc372a3eff08ac38e803689e562ce5acbb39d56d3351db475c768457e32af8"),
    ("styles.css", "f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594"),
    ("world.js", "fda8c774708af883eb97625b7064ec288c06e2819619fb2eb93e281212d32158"),
)
_REPORT_NAME = "s1b_causal_browser_w6i_once_v1.json"
_DECISIONS = {
    "READY_FOR_EXPLICIT_ONE_SHOT_BROWSER_EXECUTION",
    "BLOCKED_PYTHON_PLAYWRIGHT_PACKAGE_MISSING",
    "BLOCKED_PYTHON_PLAYWRIGHT_VERSION_MISMATCH",
}
_REPORT_FIELDS = (
    "execution_id",
    "world_set_digest",
    "runtime_binding_digest",
    "asset_digests",
    "history_a_batch_digest",
    "history_b_batch_digest",
    "probe_batch_digest",
    "formation_support_count_a",
    "formation_support_count_b",
    "probe_support_count",
    "l_a_linf",
    "l_b_linf",
    "l_ab_linf",
    "d_rn_s",
    "d_rx_s",
    "d_xn_s",
    "d_rn_h",
    "d_rx_h",
    "fast_r_n_equal",
    "fast_r_x_equal",
    "null_formation_equal",
    "null_probe_equal",
    "technical_decision",
    "raw_payloads_retained",
    "audio_buffers_released",
    "pages_closed",
    "contexts_closed",
    "browser_closed",
)


@dataclass(frozen=True, slots=True)
class S1BCausalBrowserExecutionContract:
    """Immutable static preflight; it never launches a browser."""

    execution_id: str
    preflight_decision: str
    execution_permitted: bool
    world_set_digest: str
    runtime_binding_digest: str
    asset_digests: tuple[tuple[str, str], ...]
    python_playwright_version: str | None
    context_count: int
    fresh_isolated_contexts: bool
    persistent_profiles: bool
    extensions_enabled: bool
    headless: bool
    network_requests_allowed: bool
    report_path: str
    attempt_path: str
    lock_path: str
    report_paths_absent: bool
    report_fields: tuple[str, ...]
    attempt_marker_before_launch: bool
    exclusive_lock: bool
    close_pages_contexts_and_browser: bool
    browser_started: bool = False

    def __post_init__(self) -> None:
        if self.execution_id != "s1b.causal.browser.w6i.once.v1":
            raise S1BCausalBrowserExecutionContractError(
                "browser execution identity changed"
            )
        if self.preflight_decision not in _DECISIONS:
            raise S1BCausalBrowserExecutionContractError(
                "browser preflight decision is invalid"
            )
        expected_permission = self.preflight_decision.startswith("READY_")
        if self.execution_permitted is not expected_permission:
            raise S1BCausalBrowserExecutionContractError(
                "browser execution permission contradicts preflight"
            )
        if self.world_set_digest != S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST:
            raise S1BCausalBrowserExecutionContractError(
                "browser execution world set changed"
            )
        if not _SHA256.fullmatch(self.runtime_binding_digest):
            raise S1BCausalBrowserExecutionContractError(
                "browser runtime binding digest is invalid"
            )
        if tuple(self.asset_digests) != _EXPECTED_ASSETS:
            raise S1BCausalBrowserExecutionContractError(
                "browser execution asset inventory changed"
            )
        if (
            self.context_count != 3
            or self.fresh_isolated_contexts is not True
            or self.persistent_profiles is not False
            or self.extensions_enabled is not False
            or self.headless is not True
            or self.network_requests_allowed is not False
        ):
            raise S1BCausalBrowserExecutionContractError(
                "browser execution isolation boundary changed"
            )
        paths = tuple(
            Path(value) for value in (self.report_path, self.attempt_path, self.lock_path)
        )
        if (
            paths[0].name != _REPORT_NAME
            or paths[1].name != f"{_REPORT_NAME}.attempted"
            or paths[2].name != f"{_REPORT_NAME}.lock"
            or len({path.parent for path in paths}) != 1
            or paths[0].parent.name != "reports"
            or self.report_paths_absent is not True
            or any(path.exists() for path in paths)
        ):
            raise S1BCausalBrowserExecutionContractError(
                "browser one-shot report reservation is invalid"
            )
        if self.browser_started:
            raise S1BCausalBrowserExecutionContractError(
                "static browser contract cannot start a browser"
            )
        if (
            tuple(self.report_fields) != _REPORT_FIELDS
            or self.attempt_marker_before_launch is not True
            or self.exclusive_lock is not True
            or self.close_pages_contexts_and_browser is not True
        ):
            raise S1BCausalBrowserExecutionContractError(
                "browser report and lifecycle boundary changed"
            )
        object.__setattr__(self, "report_fields", tuple(self.report_fields))

    def canonical_payload(self) -> dict[str, object]:
        return asdict(self)

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        return hashlib.sha256(encoded).hexdigest()


def _runtime_binding_digest(binding: BrowserPayloadRuntimeBinding) -> str:
    encoded = json.dumps(
        browser_payload_runtime_binding_json_value(binding),
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _installed_playwright_version() -> str | None:
    try:
        return metadata.version("playwright")
    except metadata.PackageNotFoundError:
        return None


def prepare_s1b_causal_browser_execution_contract(
    binding: BrowserPayloadRuntimeBinding,
    *,
    asset_directory: Path,
    report_directory: Path,
) -> S1BCausalBrowserExecutionContract:
    """Perform static reads only and reserve no files on disk."""

    if not isinstance(binding, BrowserPayloadRuntimeBinding):
        raise S1BCausalBrowserExecutionContractError(
            "browser execution contract requires one runtime binding"
        )
    try:
        verify_browser_payload_runtime_binding(binding)
    except ValueError as exc:
        raise S1BCausalBrowserExecutionContractError(str(exc)) from exc
    assets = browser_payload_asset_digests(Path(asset_directory))
    if assets != _EXPECTED_ASSETS:
        raise S1BCausalBrowserExecutionContractError(
            "browser execution assets differ from W6-G"
        )
    reports = Path(report_directory)
    if reports.is_symlink():
        raise S1BCausalBrowserExecutionContractError(
            "browser report directory cannot be a symlink"
        )
    try:
        reports = reports.resolve(strict=True)
    except OSError as exc:
        raise S1BCausalBrowserExecutionContractError(
            "browser report directory does not exist"
        ) from exc
    if not reports.is_dir() or reports.name != "reports":
        raise S1BCausalBrowserExecutionContractError(
            "browser report directory is invalid"
        )
    report = reports / _REPORT_NAME
    attempt = reports / f"{_REPORT_NAME}.attempted"
    lock = reports / f"{_REPORT_NAME}.lock"
    if any(path.exists() for path in (report, attempt, lock)):
        raise S1BCausalBrowserExecutionContractError(
            "browser one-shot report path is already used"
        )

    installed_version = _installed_playwright_version()
    if installed_version is None:
        decision = "BLOCKED_PYTHON_PLAYWRIGHT_PACKAGE_MISSING"
    elif installed_version != binding.package_version:
        decision = "BLOCKED_PYTHON_PLAYWRIGHT_VERSION_MISMATCH"
    else:
        decision = "READY_FOR_EXPLICIT_ONE_SHOT_BROWSER_EXECUTION"
    return S1BCausalBrowserExecutionContract(
        execution_id="s1b.causal.browser.w6i.once.v1",
        preflight_decision=decision,
        execution_permitted=decision.startswith("READY_"),
        world_set_digest=S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST,
        runtime_binding_digest=_runtime_binding_digest(binding),
        asset_digests=assets,
        python_playwright_version=installed_version,
        context_count=3,
        fresh_isolated_contexts=True,
        persistent_profiles=False,
        extensions_enabled=False,
        headless=True,
        network_requests_allowed=False,
        report_path=str(report),
        attempt_path=str(attempt),
        lock_path=str(lock),
        report_paths_absent=True,
        report_fields=_REPORT_FIELDS,
        attempt_marker_before_launch=True,
        exclusive_lock=True,
        close_pages_contexts_and_browser=True,
    )
