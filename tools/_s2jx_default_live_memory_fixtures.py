"""Bound streaming fixtures for the private S2-JX default-live memory run."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools._s2jw_default_live_av_pairing import (
    S2JVBoundAVPairV1,
    bind_s2jv_default_live_pair,
    build_s2jv_pairing_plan,
)
from tools._s2jw_default_live_profile import S2JWDefaultLiveProfileV1


S2JX_FIXTURE_SCHEMA = "s2jx.default-live-memory-fixtures.v1"
S2JV_FIXTURE_RECIPE_DIGEST = "de1871c8f9059ae6ef4b5b0aaabc967080e9f91eeee0bd2c2626ae061e4e054d"
FORMATION_SEQUENCE = (
    "X", "X", "X", "X", "Y", "Y", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"
)
PROBE_SEQUENCE = ("D9", "X", "Y")
SOURCE_CONTRACT_ID = "s2jx-default-live-source"
FIELD_CLOCK_ID = "s2jx-default-live-clock"


class S2JXFixtureError(ValueError):
    """A generated raw fixture or receptor result differs from S2-JV."""


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class S2JXFixtureSpecV1:
    label: str
    ordinal: int
    period: int
    visual_payload_digest: str
    auditory_payload_digest: str
    visual_values_digest: str
    auditory_values_digest: str


_ROWS = (
    ("X", 0, 960, "68d7b1a28b79359d09b8e283d1edd3ee7bf3a7aa899fad60305c9435a3c3aee6", "dd5f35aa7a6b8802712a7bdac5d3040e38bdbf68d398483d352fe43a168d8038", "46ee578128cfde13f300b2d03bcbd2df7a57d278174abb2d3a2a22c2c6d5855b", "76636a67276d7d3158330bd5dc7705d88fc8cc626b59f8b2911b4439d699b021"),
    ("Y", 1, 600, "702938c656d7486cf3b009fa52ea7aa1dfe0d93477f4e8827976e92244167c5f", "383a00f9dc02d8b1bee7007e9536d127ae221df4fa295ba287bebf68bacb1463", "109c23b93156d53373207bd23333f16b45bfff9fa2b79372c9b775f54b815f63", "dc692a8918e4c1912b5a55eb8713f1cb27d625d325fd16007dda2112d012d35f"),
    ("D1", 2, 400, "cd7faff71d59428d6a68a77427d6d9b8d4fc4d26f3b35b24a47760186d4106b8", "d2ba7671773e607d66d2e9d15bc133c98bd8c58a800464beea61cece83344189", "28d859a5c74258de1e9cf8f47134dd87939254b501b958cb03cc9f244ec48f9b", "c628fb56f3bc93d6df6bd7fb3465cdd97749c10e89a39f9b9adb2a711006adee"),
    ("D2", 3, 300, "0a8ea1fa775d43946c3788d5deffe0b082c91c75bd6489674e572e1e1c448960", "f10a835d6d8264d3efe6869afd17556df0aeb7a11d61162d58ea32c1c0b6cdad", "070c4474fe9e97441864ed6861ec687593fd48b4ff104aee55508013274151b3", "9ab34eaee70984318f838436d6b8c120bca71e82d1d961ca8528a3b7dc62504b"),
    ("D3", 4, 240, "5e2a628ad25ac1f5ae9a36f6c24f91d8daf952048f42a43f25911abf533c6d1f", "75700a0fde2bc500394a6024d341e1cb061fc4fe58a23073c993ef702c897236", "ecb72ef43026805d8067f1cd882b5ad67d1285abf107d23859af3359721c1d73", "017bc24ab3335564adcd497b479b01aca154a988d86e3a1b6b8991ef0ccc0d0d"),
    ("D4", 5, 160, "8846cd7252d493b46f87bf3645ead8b650e8c16ef40817ebf0d8c8861714dd9d", "73ca0a06eeb7db4065ad366310bf716c2da3657a1c24d876a8410b62de54e420", "4d5dd97f1bcb19bdfedde37d810cc56399afb8a33d912e3c4a626d6a09290991", "ed0fbc9c617ceaafbd0c72960fdd2f915c892fa69d04294318e309dd1b615960"),
    ("D5", 6, 120, "c7ae7b15352555a4fb8a8254f65cb6f85f0e792d2228465eeef625d3e7696dba", "cfdb33799badd368cd5e3c4b8e82a4f28b9781bdaf6ab844a6b4512265094b7e", "ec9ddc3b42fe73c44fd384f5048cfc34ec7780a8295f1136e397ce601b14f49f", "111f96df08a931cc96064c289ffc32570519694eef82113880bd94bcb1fb27cb"),
    ("D6", 7, 80, "dc7f22f628260215041b263de559e42d4c2070dc9cba1256f3f5defdedee03bc", "9717868f7c99e4f62cdb80226f0f6b537b9498442b0c62ae5eceb5f3c305ac10", "6598cc54ac4859618c286b8437e231a62a5dafb72fb18271805d463ad8723a9f", "1b17a89a25f53cf68306f8b14749916586f35072f99eba787bcc42dbf14bc180"),
    ("D7", 8, 60, "d6e86a187af900547e72dff68679d028627b65ebcf2b5872228e04bd8f5b876d", "aa07d7c4a2886586bfb78423bede462ba2de6a978d4da301ecb491608e904587", "4d57c5025ad9d889af966afd2bdcdb716ee222598233863d5cf4f0a556babbab", "004235506f1b6d0fd80b2302441bccd3dcb1c87d77867bc474e1feca098bb1da"),
    ("D8", 9, 40, "d0f4205d392d70ef0730e83572ba8a4e419592906f2c93732d9aa9451a962135", "23b5216f007dc27a2626fdc72e5ef81dfc502525ed83035f8a0eb92e976c6760", "d9118dfed11e645486bb229a67518a8b92f4f2db81415734aad9bc174ba68ed7", "d3b677f16c12221d8591cc6bc99de061b82ba2b83c2b9c0f2b8a00293aa328e6"),
    ("D9", 10, 30, "32226986f06d628a511793b2f3ddc74e0dccb65268cd7342eae0d80c791fd122", "7cc5dae151b952409623ed608a9e3c44ab2d3fe8de40cd342b3abb77359c8441", "1ad80c4b23dd0d1556312205802fd8cbcae4d760cd417bb7efc8f287a2e739e4", "dd8f9e68221fa328fa9e63dc59e224ad3305bcd5e0ca21eba711f02c0cfd9038"),
)
FIXTURES = tuple(S2JXFixtureSpecV1(*row) for row in _ROWS)
FIXTURE_BY_LABEL = {item.label: item for item in FIXTURES}


def _square_window(period: int) -> tuple[float, ...]:
    half = period // 2
    return tuple(0.5 if (index // half) % 2 == 0 else -0.5 for index in range(4800))


def _visual_image(ordinal: int) -> np.ndarray:
    grid = np.zeros((8, 12, 3), dtype=np.uint8)
    flat = grid.reshape(-1)
    for index in range(288):
        flat[index] = 255 if (index + ordinal) % 11 in {1, 3, 4, 5, 9} else 0
    return np.repeat(np.repeat(grid, 135, axis=0), 160, axis=1)


class S2JXFixtureStream:
    """Materialize the bound sequence once while retaining only receptor state."""

    def __init__(self, profile: S2JWDefaultLiveProfileV1) -> None:
        if type(profile) is not S2JWDefaultLiveProfileV1:
            raise S2JXFixtureError("exact S2-JW profile required")
        self._profile = profile
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self._next_block = 0

    def materialize(self, label: str, block_index: int) -> S2JVBoundAVPairV1:
        if label not in FIXTURE_BY_LABEL or block_index != self._next_block:
            raise S2JXFixtureError("fixture label or source order differs")
        spec = FIXTURE_BY_LABEL[label]
        image = _visual_image(spec.ordinal)
        visual_bytes = image.tobytes(order="C")
        window = _square_window(spec.period)
        audio_bytes = np.asarray(window, dtype="<f4").tobytes()
        if (
            hashlib.sha256(visual_bytes).hexdigest() != spec.visual_payload_digest
            or hashlib.sha256(audio_bytes).hexdigest() != spec.auditory_payload_digest
        ):
            raise S2JXFixtureError("raw fixture digest differs")

        auditory_state = None
        for hop_index in range(10):
            start = hop_index * 480
            auditory_state = self._hearing.push(window[start : start + 480])
        if auditory_state is None or auditory_state.snapshot_index != block_index * 10:
            raise S2JXFixtureError("auditory rolling endpoint differs")
        visual_state = self._visual.analyze(image, frame_index=3 * block_index + 2)
        if (
            _digest(list(auditory_state.energy)) != spec.auditory_values_digest
            or _digest(list(visual_state.channel_values)) != spec.visual_values_digest
        ):
            raise S2JXFixtureError("receptor value digest differs")

        auditory = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(auditory_state),
            CommonFieldTime(
                FIELD_CLOCK_ID,
                100_000_000 * block_index + 90_000_000,
                100_000_000 * (block_index + 1),
            ),
        )
        visual = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual_state),
            CommonFieldTime(
                FIELD_CLOCK_ID,
                ((3 * block_index + 2) * 1_000_000_000) // 30,
                100_000_000 * (block_index + 1),
            ),
        )
        plan = build_s2jv_pairing_plan(
            pair_id=f"s2jx-pair-{block_index:02d}",
            source_contract_id=SOURCE_CONTRACT_ID,
            profile=self._profile,
            auditory=auditory,
            visual=visual,
            auditory_payload_digest=spec.auditory_payload_digest,
            visual_payload_digest=spec.visual_payload_digest,
        )
        pair = bind_s2jv_default_live_pair(
            pairing_plan=plan,
            profile=self._profile,
            auditory=auditory,
            visual=visual,
        )
        self._next_block += 1
        return pair

