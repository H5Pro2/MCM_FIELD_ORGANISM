"""Byte-bound S1-OC transient boundary fixtures and mutations."""

from __future__ import annotations

import json
from typing import Any

from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1nr_fixtures import D3_V_C0, SINGLE_MUTATIONS


EDGE_ID = "edge:carrier-a:carrier-b"
FIELD_REFERENCE_DIGEST = (
    "8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835"
)
SOURCE_D3_ANATOMY_RECORD_DIGEST = (
    "1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f"
)
ZERO_DIGEST = "0" * 64


def _contact_digest(record: dict[str, Any], prefix: str) -> str:
    return sha256_hex(
        canonical_json_bytes(
            {
                "edge_id": record[f"{prefix}_edge_id"],
                "field_reference_digest": record[f"{prefix}_field_reference_digest"],
                "interval_closed": record[f"{prefix}_interval_closed"],
                "interval_ordinal": record[f"{prefix}_interval_ordinal"],
                "orientation": record[f"{prefix}_orientation"],
            }
        )
    )


def _reseal(record: dict[str, Any], *contacts: str) -> bytes:
    for prefix in contacts:
        record[f"{prefix}_contact_digest"] = _contact_digest(record, prefix)
    record["boundary_record_digest"] = sha256_hex(
        canonical_json_bytes(
            {key: value for key, value in record.items() if key != "boundary_record_digest"}
        )
    )
    return canonical_json_bytes(record)


def build_boundary(
    current_orientation: str,
    current_interval_ordinal: int,
    prior_orientation: str | None = None,
) -> bytes:
    if current_orientation not in ("X", "Y"):
        raise ValueError("current_orientation must be X or Y")
    if type(current_interval_ordinal) is not int or current_interval_ordinal < 0:
        raise ValueError("current_interval_ordinal must be a non-negative integer")
    if prior_orientation is not None and prior_orientation not in ("X", "Y"):
        raise ValueError("prior_orientation must be X, Y, or None")
    if prior_orientation is None and current_interval_ordinal != 0:
        raise ValueError("a first contact must have ordinal zero")
    if prior_orientation is not None and current_interval_ordinal == 0:
        raise ValueError("a predecessor requires a positive current ordinal")

    record: dict[str, Any] = {
        "schema_id": "g2_d3_transient_boundary_record",
        "schema_version": "s1oa.v1",
        "candidate_class_id": "G2_D3_TRANSIENT_LOCAL_CONTINUATION_GATED_REPARTITION",
        "current_edge_id": EDGE_ID,
        "current_field_reference_digest": FIELD_REFERENCE_DIGEST,
        "current_interval_ordinal": current_interval_ordinal,
        "current_orientation": current_orientation,
        "current_interval_closed": True,
        "current_contact_digest": "",
        "prior_edge_id": None,
        "prior_field_reference_digest": None,
        "prior_interval_ordinal": None,
        "prior_orientation": None,
        "prior_interval_closed": None,
        "prior_contact_digest": None,
        "source_d3_anatomy_record_digest": SOURCE_D3_ANATOMY_RECORD_DIGEST,
        "boundary_record_digest": "",
    }
    contacts = ["current"]
    if prior_orientation is not None:
        record.update(
            {
                "prior_edge_id": EDGE_ID,
                "prior_field_reference_digest": FIELD_REFERENCE_DIGEST,
                "prior_interval_ordinal": current_interval_ordinal - 1,
                "prior_orientation": prior_orientation,
                "prior_interval_closed": True,
                "prior_contact_digest": "",
            }
        )
        contacts.append("prior")
    return _reseal(record, *contacts)


OA_V_FIRST_X = build_boundary("X", 0)
OA_V_FIRST_Y = build_boundary("Y", 0)
OA_V_XX = build_boundary("X", 1, "X")
OA_V_YY = build_boundary("Y", 1, "Y")
OA_V_XY = build_boundary("Y", 1, "X")
OA_V_YX = build_boundary("X", 1, "Y")

POSITIVE_FIXTURES = {
    "OA_V_FIRST_X": OA_V_FIRST_X,
    "OA_V_FIRST_Y": OA_V_FIRST_Y,
    "OA_V_XX": OA_V_XX,
    "OA_V_YY": OA_V_YY,
    "OA_V_XY": OA_V_XY,
    "OA_V_YX": OA_V_YX,
}
POSITIVE_EVENTS = {
    "OA_V_FIRST_X": "NO_PREDECESSOR",
    "OA_V_FIRST_Y": "NO_PREDECESSOR",
    "OA_V_XX": "LOCAL_CONTINUATION",
    "OA_V_YY": "LOCAL_CONTINUATION",
    "OA_V_XY": "LOCAL_SWITCH",
    "OA_V_YX": "LOCAL_SWITCH",
}
POSITIVE_DIGESTS = {
    "OA_V_FIRST_X": (
        "078d6250bee7a51093bde34f00d4faa33ad329f0c21fd103475d168907710027",
        "bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228",
    ),
    "OA_V_FIRST_Y": (
        "1f6cdf067d253d0f8fa300f7074ab4ea6bb5568d4b193e0b274a12b104f6f89c",
        "3da5f86db0772fb339b25c6e916bf0a13dfde6f5e144a8e48cb7eea62cc43769",
    ),
    "OA_V_XX": (
        "15502f7ba7dedc0046d67cbdd66f0de4cfb0b8023d871bda34060358a17c2716",
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
    ),
    "OA_V_YY": (
        "59fb36e54c8c2214e51014009c67452249d030e846366a30dcf367c341be4326",
        "2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b",
    ),
    "OA_V_XY": (
        "90f2bd6a4fe9cd82d40d950dd1a7288b6b98e064905dfcacb1538e5947aa34f4",
        "d9db45ac53bcbddda68555ff398e7ea0f8f45f33979e84a7208d07fca965d1d0",
    ),
    "OA_V_YX": (
        "19be56470b54b8d074f423cb264fad33024cc17959a89cd7bb5f76f97efd3488",
        "68a94dc17f18afb4418e0d79f54f9a148d2c4eb8d9ced0f7607f372d9c2ff63e",
    ),
}


def build_history(orientations: tuple[str, ...]) -> tuple[bytes, ...]:
    return tuple(
        build_boundary(
            orientation,
            ordinal,
            None if ordinal == 0 else orientations[ordinal - 1],
        )
        for ordinal, orientation in enumerate(orientations)
    )


HISTORIES = {
    "H0": build_history(("X", "Y", "X", "Y")),
    "H1": build_history(("X", "X", "Y", "Y")),
    "H1M": build_history(("Y", "Y", "X", "X")),
}
HISTORY_EVENTS = {
    "H0": ("NO_PREDECESSOR", "LOCAL_SWITCH", "LOCAL_SWITCH", "LOCAL_SWITCH"),
    "H1": ("NO_PREDECESSOR", "LOCAL_CONTINUATION", "LOCAL_SWITCH", "LOCAL_CONTINUATION"),
    "H1M": ("NO_PREDECESSOR", "LOCAL_CONTINUATION", "LOCAL_SWITCH", "LOCAL_CONTINUATION"),
}
HISTORY_DIGESTS = {
    "H0": (
        ("078d6250bee7a51093bde34f00d4faa33ad329f0c21fd103475d168907710027", "bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228"),
        ("90f2bd6a4fe9cd82d40d950dd1a7288b6b98e064905dfcacb1538e5947aa34f4", "d9db45ac53bcbddda68555ff398e7ea0f8f45f33979e84a7208d07fca965d1d0"),
        ("587271311881f7621bd7db9c393231c93a880303f6fd47dab217917550c7eaf9", "4bcd1825e7ccd7fda01a345640e6959b9ecabab3ea5442cea6964adb21ae1817"),
        ("6c1da794ec37b88f094fd927e1404f1635163d1f606d253b0603d442a5815263", "cc51ced1142f606d5bd9dd22c743f2bab51828569bb56e8855bd80e3c2654618"),
    ),
    "H1": (
        ("078d6250bee7a51093bde34f00d4faa33ad329f0c21fd103475d168907710027", "bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228"),
        ("15502f7ba7dedc0046d67cbdd66f0de4cfb0b8023d871bda34060358a17c2716", "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c"),
        ("040d538164d7f9d405725cc72bda26c86738100534949a6f079e52f03caaa8ff", "c438484e53ca01b1d2382a9a9ce57fee743bf41bd8270d62af7cf9bb5af372d9"),
        ("3372d7e9b24bb6cf8a426b2fd08d8418fd2a407bd7eb8788b5b43b90a026118c", "0c0d53a9e47417ad2bca11707612c2977e5f7caced7a5127b496f4a4db1e2b25"),
    ),
    "H1M": (
        ("1f6cdf067d253d0f8fa300f7074ab4ea6bb5568d4b193e0b274a12b104f6f89c", "3da5f86db0772fb339b25c6e916bf0a13dfde6f5e144a8e48cb7eea62cc43769"),
        ("59fb36e54c8c2214e51014009c67452249d030e846366a30dcf367c341be4326", "2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b"),
        ("587271311881f7621bd7db9c393231c93a880303f6fd47dab217917550c7eaf9", "4bcd1825e7ccd7fda01a345640e6959b9ecabab3ea5442cea6964adb21ae1817"),
        ("e5c710170b305b52772188d0cfde78f9bf218315dd1d852094b3cdd8aa88a4bf", "a7001cf3bc1044f3e2897e61d9b4973c9922f03758b5068974b059b593482335"),
    ),
}


def _record(raw: bytes) -> dict[str, Any]:
    return json.loads(raw)


def _mutation(base: bytes, changes: dict[str, Any], contacts: tuple[str, ...] = ()) -> bytes:
    record = _record(base)
    record.update(changes)
    return _reseal(record, *contacts)


def _missing() -> bytes:
    record = _record(OA_V_FIRST_X)
    del record["candidate_class_id"]
    return _reseal(record)


def _noncanonical() -> bytes:
    return json.dumps(_record(OA_V_FIRST_X), indent=2, sort_keys=True).encode("utf-8")


NEGATIVE_FIXTURES = {
    "OA_I_VERSION": (_mutation(OA_V_FIRST_X, {"schema_version": "s1oa.v2"}), D3_V_C0),
    "OA_I_MISSING": (_missing(), D3_V_C0),
    "OA_I_EXTRA": (_mutation(OA_V_FIRST_X, {"unknown_field": True}), D3_V_C0),
    "OA_I_NONCANONICAL": (_noncanonical(), D3_V_C0),
    "OA_I_CLASS": (_mutation(OA_V_FIRST_X, {"candidate_class_id": "OTHER"}), D3_V_C0),
    "OA_I_FORBIDDEN": (_mutation(OA_V_FIRST_X, {"raw_data": []}), D3_V_C0),
    "OA_I_CURRENT_DIGEST": (_mutation(OA_V_FIRST_X, {"current_contact_digest": ZERO_DIGEST}), D3_V_C0),
    "OA_I_PRIOR_NULLABILITY": (_mutation(OA_V_FIRST_X, {"prior_orientation": "X"}), D3_V_C0),
    "OA_I_PRIOR_DIGEST": (_mutation(OA_V_XX, {"prior_contact_digest": ZERO_DIGEST}), D3_V_C0),
    "OA_I_D3_SOURCE_INVALID": (OA_V_FIRST_X, SINGLE_MUTATIONS["D3_I_RECORD_DIGEST"]),
    "OA_I_D3_SOURCE_DIGEST": (_mutation(OA_V_FIRST_X, {"source_d3_anatomy_record_digest": ZERO_DIGEST}), D3_V_C0),
    "OA_I_EDGE": (_mutation(OA_V_XX, {"prior_edge_id": "edge:wrong"}, ("prior",)), D3_V_C0),
    "OA_I_ORDINAL": (_mutation(OA_V_XX, {"current_interval_ordinal": 2}, ("current",)), D3_V_C0),
    "OA_I_CLOSED": (_mutation(OA_V_XX, {"prior_interval_closed": False}, ("prior",)), D3_V_C0),
    "OA_I_ORIENTATION": (_mutation(OA_V_XX, {"current_orientation": "Z"}, ("current",)), D3_V_C0),
    "OA_I_BOUNDARY_DIGEST": (canonical_json_bytes({**_record(OA_V_FIRST_X), "boundary_record_digest": ZERO_DIGEST}), D3_V_C0),
    "OA_I_TRANSIENT": (_mutation(OA_V_FIRST_X, {"event_role": "LOCAL_CONTINUATION"}), D3_V_C0),
}
NEGATIVE_EXPECTED = {
    "OA_I_VERSION": ("OA_UNKNOWN_SCHEMA_OR_VERSION",),
    "OA_I_MISSING": ("OA_MISSING_OR_UNKNOWN_FIELD",),
    "OA_I_EXTRA": ("OA_MISSING_OR_UNKNOWN_FIELD",),
    "OA_I_NONCANONICAL": ("OA_NONCANONICAL_SERIALIZATION",),
    "OA_I_CLASS": ("OA_CLASS_ID_MISMATCH",),
    "OA_I_FORBIDDEN": ("OA_FORBIDDEN_PAYLOAD_PRESENT",),
    "OA_I_CURRENT_DIGEST": ("OA_CURRENT_CONTACT_DIGEST_MISMATCH",),
    "OA_I_PRIOR_NULLABILITY": ("OA_PRIOR_NULLABILITY_MISMATCH",),
    "OA_I_PRIOR_DIGEST": ("OA_PRIOR_CONTACT_DIGEST_MISMATCH",),
    "OA_I_D3_SOURCE_INVALID": ("OA_D3_SOURCE_RECORD_INVALID",),
    "OA_I_D3_SOURCE_DIGEST": ("OA_D3_SOURCE_DIGEST_MISMATCH",),
    "OA_I_EDGE": ("OA_EDGE_OR_FIELD_REFERENCE_MISMATCH",),
    "OA_I_ORDINAL": ("OA_INVALID_INTERVAL_ORDINAL",),
    "OA_I_CLOSED": ("OA_INTERVAL_NOT_CLOSED",),
    "OA_I_ORIENTATION": ("OA_UNKNOWN_ORIENTATION",),
    "OA_I_BOUNDARY_DIGEST": ("OA_BOUNDARY_RECORD_DIGEST_MISMATCH",),
    "OA_I_TRANSIENT": ("OA_TRANSIENT_PERSISTENCE_FIELD_PRESENT",),
}
NEGATIVE_INPUT_DIGESTS = {
    "OA_I_VERSION": "2ef258e62980c27b31f36d271615d2e8c8323aa12e5f4e0d5f0c7254b7d99493",
    "OA_I_MISSING": "47c94ff9586fb10e25a4466d02a181405dd10d1d8a6ee608838fbd3ec9114574",
    "OA_I_EXTRA": "a59245f6ee3f0f296e0dcecfda791c7e4521c6ab216bd43af20f004f12666cb1",
    "OA_I_NONCANONICAL": "cc21ccf5b5f1c4250b490924a538e7007b846596e98fd39aa9309be2cf48d0f4",
    "OA_I_CLASS": "c2e7c0d1058ed6e1cf67bf6a314dc358153a1c84c78ccf6c1c399220b434606c",
    "OA_I_FORBIDDEN": "9cf428b696690525e95c1a9d1b8c2e989c820f110f1eb0faa5839984164a7efb",
    "OA_I_CURRENT_DIGEST": "a07443aae5a5c699367aa620ccd7238104fe28bd42b85c060a623d171aea515b",
    "OA_I_PRIOR_NULLABILITY": "a10b5e6270756db626a7510125b4170eaa3f38289ebe8be8f0a4c25de24fed7d",
    "OA_I_PRIOR_DIGEST": "4f5cb94a3f9367773811bfb11e822784c2ca81c0cb8314ac2e06fbbcf0c1a570",
    "OA_I_D3_SOURCE_INVALID": "bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228",
    "OA_I_D3_SOURCE_DIGEST": "6c67dae202f90f05d55dae04b35db15d955d770d547738c37fca1f727e09e335",
    "OA_I_EDGE": "98c33e6184bb992bd33a2ebef9725a7d745384e65379a037ab5d83732bed81ca",
    "OA_I_ORDINAL": "8f28c49597cf1b09b1a7fd8e419577b9ee04f06a5eb1b4bee700b824e51d93fc",
    "OA_I_CLOSED": "4421a6cb76c62ba3e6aa3cd888f5ae854a9c5b40254c0c8d469c13b9aac24fa2",
    "OA_I_ORIENTATION": "895a0b39c83c05b4df3a1383d67e68a05b4bb3510da98fdbba93038f908fdae0",
    "OA_I_BOUNDARY_DIGEST": "b80e5aea4a795ece90c7f7c0589820479114425335472273b76e95eabfef1a0a",
    "OA_I_TRANSIENT": "7a6b422e93f1096f03c2c81b6ee4d07e6dcc574e4dedcb748e77fc925cdbbc85",
}
