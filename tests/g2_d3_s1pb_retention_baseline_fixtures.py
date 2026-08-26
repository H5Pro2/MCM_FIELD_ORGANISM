"""Byte-bound S1-PB fixtures for the matched retention baseline."""

from __future__ import annotations

from mcm_field_organism.kfs1_schema_validator import sha256_hex


CONFIGURATION_RAW = (
    b'{"baseline_class_id":"G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE",'
    b'"configuration_record_digest":"68226a0df481c9ae938cc260c386ccbfb0c19444756f6a1d99001fd68602414e",'
    b'"configuration_schema_id":"g2_d3_single_state_retention_configuration",'
    b'"configuration_schema_version":"s1oy.v1","initial_retained_capacity":0.5,'
    b'"retention_fraction_per_fresh_continuation":0.5,'
    b'"update_rule_id":"ONE_STATIONARY_RETENTION_UPDATE_PER_FRESH_CONTINUATION"}'
)
INITIAL_STATE_RAW = (
    b'{"baseline_class_id":"G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE",'
    b'"retained_capacity":0.5,'
    b'"state_record_digest":"c51470d4cdf0fc5d24b50a6e7617a7e72346217880a302b0adf5905b0390d0ec",'
    b'"state_schema_id":"g2_d3_single_state_retention_state",'
    b'"state_schema_version":"s1oy.v1","state_status":"valid"}'
)
CONTINUATION_EVENT_RAW = (
    b'{"event_class_id":"G2_D3_FRESH_CONTINUATION",'
    b'"event_schema_id":"g2_d3_model_neutral_continuation_event",'
    b'"event_schema_version":"s1oy.v1"}'
)

CONFIGURATION_RETENTION_025_RAW = (
    b'{"baseline_class_id":"G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE",'
    b'"configuration_record_digest":"0462044471e26a7fe6975e7c8a0be49cef6ae80c0f2bb3f18785cb8949a7e7d5",'
    b'"configuration_schema_id":"g2_d3_single_state_retention_configuration",'
    b'"configuration_schema_version":"s1oy.v1","initial_retained_capacity":0.5,'
    b'"retention_fraction_per_fresh_continuation":0.25,'
    b'"update_rule_id":"ONE_STATIONARY_RETENTION_UPDATE_PER_FRESH_CONTINUATION"}'
)
STATE_NEGATIVE_RAW = (
    b'{"baseline_class_id":"G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE",'
    b'"retained_capacity":-0.5,'
    b'"state_record_digest":"294ed5b040da553b7aa045c0f7ca8b96f2d8249edc9fa9e231f9a3ef9275cd46",'
    b'"state_schema_id":"g2_d3_single_state_retention_state",'
    b'"state_schema_version":"s1oy.v1","state_status":"valid"}'
)
STATE_BOOL_RAW = (
    b'{"baseline_class_id":"G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE",'
    b'"retained_capacity":true,'
    b'"state_record_digest":"a3026e15bd60eef5b4cab645daf79d647be6543141933796e59262394feed8ba",'
    b'"state_schema_id":"g2_d3_single_state_retention_state",'
    b'"state_schema_version":"s1oy.v1","state_status":"valid"}'
)
EVENT_VERSION_RAW = (
    b'{"event_class_id":"G2_D3_FRESH_CONTINUATION",'
    b'"event_schema_id":"g2_d3_model_neutral_continuation_event",'
    b'"event_schema_version":"changed"}'
)

XXX_FIRST = "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c"
XXX_SECOND = "6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a"
YYY_FIRST = "2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b"
YYY_SECOND = "dc772636ed23e9cf9a904fd9943a7a1bcfacafe08aed9e60a65ac93f3d266d32"

VALID_BASELINE_FIXTURES = {
    "PA_V_XXX": (
        XXX_FIRST, XXX_SECOND, INITIAL_STATE_RAW, CONTINUATION_EVENT_RAW, CONFIGURATION_RAW
    ),
    "PA_V_YYY": (
        YYY_FIRST, YYY_SECOND, INITIAL_STATE_RAW, CONTINUATION_EVENT_RAW, CONFIGURATION_RAW
    ),
}

INVALID_BASELINE_FIXTURES = {
    "PA_I_PROVENANCE_CROSS": (
        XXX_FIRST, YYY_SECOND, INITIAL_STATE_RAW, CONTINUATION_EVENT_RAW, CONFIGURATION_RAW
    ),
    "PA_I_CONFIG_RETENTION_025": (
        XXX_FIRST, XXX_SECOND, INITIAL_STATE_RAW, CONTINUATION_EVENT_RAW,
        CONFIGURATION_RETENTION_025_RAW,
    ),
    "PA_I_STATE_NEGATIVE": (
        XXX_FIRST, XXX_SECOND, STATE_NEGATIVE_RAW, CONTINUATION_EVENT_RAW, CONFIGURATION_RAW
    ),
    "PA_I_STATE_BOOL": (
        XXX_FIRST, XXX_SECOND, STATE_BOOL_RAW, CONTINUATION_EVENT_RAW, CONFIGURATION_RAW
    ),
    "PA_I_EVENT_VERSION": (
        XXX_FIRST, XXX_SECOND, INITIAL_STATE_RAW, EVENT_VERSION_RAW, CONFIGURATION_RAW
    ),
}

EXPECTED_FAILURES = {
    "PA_I_PROVENANCE_CROSS": "OY_SEQUENCE_PROVENANCE_INVALID",
    "PA_I_CONFIG_RETENTION_025": "OY_CONFIGURATION_INVALID",
    "PA_I_STATE_NEGATIVE": "OY_INITIAL_STATE_INVALID",
    "PA_I_STATE_BOOL": "OY_INITIAL_STATE_INVALID",
    "PA_I_EVENT_VERSION": "OY_EVENT1_INVALID",
}

INPUT_DIGESTS = {
    "configuration": "12e6d381c0dcc0f170c39453bde291152bc55499e0292edacb2d0a09c27e1d93",
    "initial_state": "f67406ef5f4da6ecd3775ab8c12139dbee607dd33b0c89e14842774c48d0ffd2",
    "event": "dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f",
    "configuration_025": "a72ed7075acd3bc2937bbf12dd5ca209e7d9df6ecc126dc5df6763228b5e6543",
    "state_negative": "3181d6b69b8b3f572f300c75c330603dd619d7e3ad33f9b1ba4935f658283c61",
    "state_bool": "327d58f0ba6cd60e8d54a27b15fd51010a886efe2001a9eb6d8c7df2d0feb334",
    "event_version": "ad08cd7ae7f8575dda4142147aa6239ecd10a4f4415f5eb4a68dda0eed37ed35",
}

EXPECTED_STATE_INPUT_DIGESTS = (
    "f67406ef5f4da6ecd3775ab8c12139dbee607dd33b0c89e14842774c48d0ffd2",
    "2eb320f35971b2d29fc5f07adcee5d2e8d05b68398d6655b42086d7ea1a05eb7",
    "4978a6221f1da66a2959e2661ee335f1c491b127af4a22f18da440f335f3be48",
)
EXPECTED_STATE_RECORD_DIGESTS = (
    "c51470d4cdf0fc5d24b50a6e7617a7e72346217880a302b0adf5905b0390d0ec",
    "183125e5c5b45acd56314bee5ec3453fd7676f57fb76e965e3f9b6793debce91",
    "0a65c70bee3b6bb7c6b6a8a4a5f69aae1bca0e00b1b0ca0494ec6a594195cb6b",
)
EXPECTED_VALUES = (0.5, 0.25, 0.125)
EXPECTED_COMPONENTS = (-0.25, -0.125, -0.375)
EXPECTED_COMPARISON_DIGEST = (
    "5c8d3b60bbc205594974f632a878472bf628426dc914af72514cf7b42e8a86a5"
)
EXPECTED_CLOSURE_PAYLOAD_DIGEST = (
    "bce12955a3df61976dcf650b9dba93a59c5894d148a07414efd44489d5f2af15"
)
DEFENSIVE_BASELINE_CODES = (
    "OY_CP0_READOUT_FAILED",
    "OY_UPDATE1_FAILED",
    "OY_CP1_READOUT_FAILED",
    "OY_EVENT2_INVALID",
    "OY_UPDATE2_FAILED",
    "OY_CP2_READOUT_FAILED",
    "OY_COMPONENT_EVALUATION_FAILED",
)
DEFENSIVE_COMPARATOR_CODES = (
    "PA_CHECKPOINT_IDENTITY_MISMATCH",
    "PA_RESIDUAL_IDENTITY_MISMATCH",
)


def fixture_input_digests() -> dict[str, str]:
    return {
        "configuration": sha256_hex(CONFIGURATION_RAW),
        "initial_state": sha256_hex(INITIAL_STATE_RAW),
        "event": sha256_hex(CONTINUATION_EVENT_RAW),
        "configuration_025": sha256_hex(CONFIGURATION_RETENTION_025_RAW),
        "state_negative": sha256_hex(STATE_NEGATIVE_RAW),
        "state_bool": sha256_hex(STATE_BOOL_RAW),
        "event_version": sha256_hex(EVENT_VERSION_RAW),
    }
