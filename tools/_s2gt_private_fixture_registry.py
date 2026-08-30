"""Literal S2-GT fixtures and read-only bindings to the S2-GR registries."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import json
from pathlib import Path
import re


S2GT_SCHEMA = "s2gt.private.functional-run.v1"
FIXTURE_SET_DIGEST = "0e9f26180b1f392a10fa727a5f320d2a2f2be1da8dc686cc4f82534a56d3a789"
MASKED_SOURCE_DIGEST = "4ba6dbcb31eea7ddb198a442e699aa7f73ee8785c494cbede92a2526b9385f81"
FUNCTIONAL_THRESHOLD = (44, 765)
NATIVE_THRESHOLD = (1, 5)
SUCCESS_OPERATION_COUNT = 139
SUCCESS_EVENT_COUNT = 278
FAILURE_PATH_COUNT = 140
ERROR_CODE_COUNT = 16
MAX_SUCCESS_PATH_BYTES = 2_009_088
MAX_FAILURE_PATH_BYTES = 2_045_952
MAX_RUN_PATH_BYTES = MAX_FAILURE_PATH_BYTES

REGISTRY_BINDINGS = (
    ("operation", "docs/S2GR_OPERATION_REGISTRY.csv", "8b900da51f6a8921c5231679570f0aa3e188d56b9bd5507f989038a354787d05"),
    ("failure_operation", "docs/S2GR_FAILURE_OPERATION_REGISTRY.csv", "f6d201e3c1f5bd91f244a065ef8e97129f39a829c3c50b74b0a697460793c721"),
    ("error_code", "docs/S2GR_ERROR_CODE_REGISTRY.csv", "a6db907bf9065fd6a7afcf631441c5eda5b8993db01972bb533a8cefa5ac2e09"),
    ("failure_path", "docs/S2GR_FAILURE_PATH_BUDGET_REGISTRY.csv", "fcebc195aeb3ebc51879d9b5eb3657fe59e3f9df6339892ffff1375325597024"),
)

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_NEUTRAL_ID = re.compile(r"^[a-z][a-z0-9.-]{0,95}$")


class S2GTRegistryError(RuntimeError):
    """A terminal static or runtime registry binding error."""


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(131_072), b""):
            hasher.update(block)
    return hasher.hexdigest()


@dataclass(frozen=True, slots=True)
class VisualFixture:
    fixture_id: str
    bits: str
    raw_sha256: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[A-Z0-9-]{2,5}", self.fixture_id):
            raise S2GTRegistryError("invalid visual fixture id")
        if not re.fullmatch(r"[01]{18}", self.bits):
            raise S2GTRegistryError("visual fixture must contain 18 bits")
        if _DIGEST.fullmatch(self.raw_sha256) is None:
            raise S2GTRegistryError("invalid visual raw-byte digest")

    @property
    def values(self) -> tuple[float, ...]:
        return tuple(float(value) for value in self.bits)


@dataclass(frozen=True, slots=True)
class HistoryStep:
    ordinal: int
    visual_fixture_id: str
    auditory_fixture_id: str
    window_start: int
    window_end: int


@dataclass(frozen=True, slots=True)
class HistoryFixture:
    history_id: str
    steps: tuple[HistoryStep, ...]
    full_probe_visual_id: str
    full_probe_auditory_id: str


@dataclass(frozen=True, slots=True)
class RegistryBundle:
    operation_rows: tuple[dict[str, str], ...]
    failure_operation_rows: tuple[dict[str, str], ...]
    error_code_rows: tuple[dict[str, str], ...]
    failure_path_rows: tuple[dict[str, str], ...]
    source_digests: tuple[tuple[str, str], ...]
    bundle_digest: str


VISUAL_FIXTURES = (
    VisualFixture("J1-T", "100110011001100110", "36b9c3295ab4130569bf69abe8375c8358c112cf016935478b62a0a81d4f94a9"),
    VisualFixture("J1-F", "110011001100110011", "8b06a64ad2b4c589a0eb32ce90bb2546ce06ea5cab00db4cc377210568e0db7e"),
    VisualFixture("J1-C", "000110011001100110", "c4c7ba6d0da052425937c0888b7b2c222abf04f051073bd600782329fb5fa01e"),
    VisualFixture("D1", "111111100000000000", "acbf5d3052e7bdd25027cddd46d11991e42e585e1599ed58628f5dcabb15fb16"),
    VisualFixture("D2", "111100011100000000", "162f321fe3aeaa2b9a20aaf36ca46197361987df1552b9acfeb972b79e9ee9e8"),
    VisualFixture("D3", "111100000011100000", "79d82f14640e3a78b0ee8d1fc73d7516d07befd8c73cdbf5e8daa1a6d4479053"),
    VisualFixture("D4", "111100000000011100", "4c4809a51aba4bdc718c73e8f9e8b01ba69ee9426497912088b97e201111722c"),
    VisualFixture("D5", "111010010010010000", "2c26c0f64bb0d0b7018328d8273b4bea46c8d616bc26e129267093d0328afd21"),
    VisualFixture("D6", "111010001001001000", "f668dcc5677dd625e2acc2a72cb00c71e432489ef1ae8492ceb491d31597c8c0"),
    VisualFixture("D7", "111010000100100100", "92ded1eb1875494e94256cc633fbc543e0ba921d8699792903b52f740315eeea"),
    VisualFixture("D8", "111001010001000100", "115596e84cba8d0d5ffeb018aa45b0eeb3460d1e38d84610e3b3fe237c2ec6b0"),
    VisualFixture("D9", "111001001010000010", "52354f306a7010fe295fc3f4d02dae3e464c070b481a9f2ccd3c87bfc18f247b"),
    VisualFixture("A1", "111001000100010001", "75b780558aea7c28a595d6ecbfb524f582cb50e408c6df340e4a8f6d41d1ad03"),
    VisualFixture("A2", "111000110000101000", "06862a7ef902262606f27ec27b8ad83c984dfbdc49fe4fb78b3b63a5a2a2cde5"),
    VisualFixture("A3", "111000101000000101", "31799ae00e8a698b3b7611aedfd26134d698ac9123a7cb9167ea9f27eb9ee301"),
    VisualFixture("A4", "111000100101000010", "84f7d6ae1b5664ad249b4e5675922661e95dc32b5e6b8741c13dc048a2a1dc46"),
    VisualFixture("A5", "110110010001000001", "1b2eefbc9bfd21520b6bb0b5454905e78bfa87eec6548cfec7a5fc15c7b26090"),
    VisualFixture("A6", "110110001010000100", "220babcdacc05a1c8faad77042cb96c9ab68da0b1c2127bdb96d97ff839e2b74"),
    VisualFixture("A7", "110110000100010010", "ced8867f594bbad2e915372b8ea49ccb9be1dcbb99b3167440fda6e3d6be7478"),
    VisualFixture("A8", "110101010010001000", "aa180051bec55126a890742b05f25b263795f99a5294ba9795837606a5cf7647"),
    VisualFixture("A9", "110101001001010000", "34c497af454e7113c4e5a3e30d3e8821a6c4a1703f866937fd0e859cc9cd4ee2"),
    VisualFixture("A10", "110101000000100110", "c3f0e1c3ede5264caeecc4f5a2c24cc2a22c25dfc8c3802839eb570c297ad446"),
    VisualFixture("A11", "110100101000001010", "c4af8113278e754be39bbfd86c60ce8501ff61b5f5897fef674798672ca0f2c1"),
    VisualFixture("A12", "110100100110000001", "6363776eb2805268e0f32d780a766e258fcc6d5ffd78489c963a37b16b555fd8"),
    VisualFixture("A13", "110011011000100000", "1664ac5850c81a523c2ecfd7d6b8785d7a4968de11ca1352dfff69cfcbd3c715"),
)
VISUAL_BY_ID = {item.fixture_id: item for item in VISUAL_FIXTURES}

AUDITORY_BITS = (
    ("Q0", "11110000"), ("Q1", "11101000"), ("Q2", "11100100"),
    ("Q3", "11100010"), ("Q4", "11100001"), ("Q5", "11011000"),
    ("Q6", "11010100"), ("Q7", "11010010"), ("Q8", "11010001"),
    ("Q9", "11001100"), ("Q10", "11001010"), ("Q11", "11001001"),
    ("Q12", "11000110"), ("Q13", "11000101"),
)
AUDITORY_BY_ID = {key: tuple(float(value) for value in bits) for key, bits in AUDITORY_BITS}


def _history(history_id: str, visual_ids: tuple[str, ...], auditory_ids: tuple[str, ...], probe_visual_id: str) -> HistoryFixture:
    if _NEUTRAL_ID.fullmatch(history_id) is None or len(visual_ids) != 13 or len(auditory_ids) != 13:
        raise S2GTRegistryError("history fixture shape differs")
    steps = tuple(HistoryStep(index, visual, auditory, index - 1, index) for index, (visual, auditory) in enumerate(zip(visual_ids, auditory_ids), 1))
    return HistoryFixture(history_id, steps, probe_visual_id, "Q0")


_D_IDS = tuple(f"D{index}" for index in range(1, 10))
_Q0_D = ("Q0",) * 4 + tuple(f"Q{index}" for index in range(1, 10))
HISTORIES = (
    _history("h01", ("J1-T",) * 4 + _D_IDS, _Q0_D, "J1-T"),
    _history("h02", ("J1-F",) * 4 + _D_IDS, _Q0_D, "J1-F"),
    _history("h03", ("J1-C",) * 4 + _D_IDS, _Q0_D, "J1-C"),
    _history("h04", tuple(f"A{index}" for index in range(1, 14)), tuple(f"Q{index}" for index in range(1, 14)), "J1-T"),
)

ARM_BINDINGS = (
    ("a01", "CURRENT_PERCEPTION_ONLY", None),
    ("a02", "CONTEXT_CONSUMER", "h01"),
    ("a03", "DIRECT_BASELINE", "h01"),
    ("a04", "CONTEXT_CONSUMER", "h02"),
    ("a05", "DIRECT_BASELINE", "h02"),
    ("a06", "CONTEXT_CONSUMER", "h04"),
    ("a07", "CONTEXT_CONSUMER", "h03"),
)


def validate_literal_fixtures() -> None:
    if len(VISUAL_FIXTURES) != 25 or len(VISUAL_BY_ID) != 25:
        raise S2GTRegistryError("exactly 25 unique visual fixtures required")
    if len(AUDITORY_BY_ID) != 14 or any(sum(values) != 4.0 for values in AUDITORY_BY_ID.values()):
        raise S2GTRegistryError("auditory fixture anatomy differs")
    if len(HISTORIES) != 4 or sum(len(item.steps) for item in HISTORIES) != 52:
        raise S2GTRegistryError("four 13-step histories required")


def _read_csv(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return tuple(dict(row) for row in csv.DictReader(handle))


def load_bound_registries(workspace_root: Path) -> RegistryBundle:
    """Read and validate the already approved S2-GR CSV sources on demand."""

    if type(workspace_root) is not Path or not workspace_root.is_absolute():
        raise S2GTRegistryError("absolute pathlib.Path workspace root required")
    rows: dict[str, tuple[dict[str, str], ...]] = {}
    source_digests: list[tuple[str, str]] = []
    for role, relative_path, expected_digest in REGISTRY_BINDINGS:
        path = workspace_root / relative_path
        actual_digest = file_digest(path)
        if actual_digest != expected_digest:
            raise S2GTRegistryError(f"{role} registry digest differs")
        rows[role] = _read_csv(path)
        source_digests.append((role, actual_digest))
    if len(rows["operation"]) != SUCCESS_OPERATION_COUNT:
        raise S2GTRegistryError("success registry count differs")
    if len(rows["failure_operation"]) != 3:
        raise S2GTRegistryError("failure operation registry count differs")
    if len(rows["error_code"]) != ERROR_CODE_COUNT:
        raise S2GTRegistryError("error code registry count differs")
    if len(rows["failure_path"]) != FAILURE_PATH_COUNT:
        raise S2GTRegistryError("failure path registry count differs")
    if tuple(row["operation_id"] for row in rows["operation"]) != tuple(f"op-{index:04d}" for index in range(1, 140)):
        raise S2GTRegistryError("success operation ids differ")
    payload = {"schema": S2GT_SCHEMA, "sources": source_digests, "counts": [139, 278, 140, 16], "budgets": [MAX_SUCCESS_PATH_BYTES, MAX_FAILURE_PATH_BYTES]}
    return RegistryBundle(rows["operation"], rows["failure_operation"], rows["error_code"], rows["failure_path"], tuple(source_digests), canonical_digest(payload))


__all__: tuple[str, ...] = ()
