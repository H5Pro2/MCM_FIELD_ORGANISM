"""S1-EC106 immutable producer receipts and combined ingress attestation."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_common_probe_ec96_authorized_r4_r8_once import (
    E1CommonProbeEC96AtomicResult,
)
from .e1_common_probe_ec103_synthetic_coordinator_e2e_fixture import (
    build_e1_common_probe_ec103_synthetic_r2_result,
    build_e1_common_probe_ec103_synthetic_r4_r8_result,
)
from .e1_common_probe_ec105_atomic_producer_attestation_contract import (
    S1_EC105_PRODUCER_SEQUENCE,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC106AttestationReceiptError(ValueError):
    """Raised when an EC106 receipt or attestation leaves its closed scope."""


S1_EC106_R2_RECEIPT_ID = "e1.common-probe-r2-producer-receipt.s1ec106.v1"
S1_EC106_R4_R8_RECEIPT_ID = "e1.common-probe-r4-r8-producer-receipt.s1ec106.v1"
S1_EC106_INGRESS_ATTESTATION_ID = (
    "e1.common-probe-combined-ingress-attestation.s1ec106.v1"
)
S1_EC106_FIXTURE_ID = "e1.common-probe-attestation-receipts-fixture.s1ec106.v1"


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _producer_payload(receipt: object) -> dict[str, object]:
    return {
        name: getattr(receipt, name)
        for name in receipt.__dataclass_fields__
        if name not in {"receipt_digest", "source_result"}
    }


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC106R2ProducerReceipt:
    receipt_id: str
    producer_id: str
    one_shot_authorization_digest: str
    source_result_digest: str
    source_probe_receipt_digests: tuple[str, ...]
    accounted_field_steps: int
    producer_sequence_index: int
    emitted_atomically_with_result: bool
    contractual_not_cryptographic: bool
    receipt_digest: str
    source_result: E1CommonProbeN2R2RealModeCoordinatorResult = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = _producer_payload(self)
        if (
            self.receipt_id != S1_EC106_R2_RECEIPT_ID
            or self.producer_id != "EC67-r2"
            or not _valid_digest(self.one_shot_authorization_digest)
            or self.source_result_digest != self.source_result.result_digest
            or self.source_probe_receipt_digests
            != tuple(item.receipt_digest for item in self.source_result.probes)
            or len(self.source_probe_receipt_digests) != 8
            or len(set(self.source_probe_receipt_digests)) != 8
            or self.accounted_field_steps != 3208
            or self.producer_sequence_index != 0
            or self.emitted_atomically_with_result is not True
            or self.contractual_not_cryptographic is not True
            or self.receipt_digest != _digest(payload)
        ):
            raise E1CommonProbeEC106AttestationReceiptError(
                "S1-EC106 r2 producer receipt changed"
            )
        self.source_result.__post_init__()


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC106R4R8ProducerReceipt:
    receipt_id: str
    producer_id: str
    one_shot_authorization_digest: str
    source_result_digest: str
    source_probe_receipt_digests: tuple[str, ...]
    accounted_field_steps: int
    producer_sequence_index: int
    emitted_atomically_with_result: bool
    contractual_not_cryptographic: bool
    receipt_digest: str
    source_result: E1CommonProbeEC96AtomicResult = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        payload = _producer_payload(self)
        probes = tuple(
            probe
            for refinement in self.source_result.refinements
            for probe in refinement.probes
        )
        if (
            self.receipt_id != S1_EC106_R4_R8_RECEIPT_ID
            or self.producer_id != "EC96-r4-r8"
            or self.one_shot_authorization_digest
            != self.source_result.authorization_digest
            or not _valid_digest(self.one_shot_authorization_digest)
            or self.source_result_digest != self.source_result.result_digest
            or self.source_probe_receipt_digests
            != tuple(item.receipt_digest for item in probes)
            or len(self.source_probe_receipt_digests) != 16
            or len(set(self.source_probe_receipt_digests)) != 16
            or self.accounted_field_steps != 19248
            or self.producer_sequence_index != 1
            or self.emitted_atomically_with_result is not True
            or self.contractual_not_cryptographic is not True
            or self.receipt_digest != _digest(payload)
        ):
            raise E1CommonProbeEC106AttestationReceiptError(
                "S1-EC106 r4/r8 producer receipt changed"
            )
        self.source_result.__post_init__()
        for refinement in self.source_result.refinements:
            refinement.__post_init__()


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC106CombinedIngressAttestation:
    attestation_id: str
    r2_producer_receipt_digest: str
    r4_r8_producer_receipt_digest: str
    source_result_digests: tuple[str, ...]
    source_probe_receipt_digests: tuple[str, ...]
    accounted_field_steps: int
    producer_sequence: tuple[str, ...]
    both_receipts_validated: bool
    same_objects_forwarded_to_ec102: bool
    contractual_not_cryptographic: bool
    attestation_digest: str
    r2_receipt: E1CommonProbeEC106R2ProducerReceipt = field(
        repr=False, compare=False
    )
    r4_r8_receipt: E1CommonProbeEC106R4R8ProducerReceipt = field(
        repr=False, compare=False
    )
    source_probe_objects: tuple[object, ...] = field(repr=False, compare=False)
    forwarded_probe_objects: tuple[object, ...] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name
            not in {
                "attestation_digest",
                "r2_receipt",
                "r4_r8_receipt",
                "source_probe_objects",
                "forwarded_probe_objects",
            }
        }
        expected_probe_digests = (
            *self.r2_receipt.source_probe_receipt_digests,
            *self.r4_r8_receipt.source_probe_receipt_digests,
        )
        if (
            self.attestation_id != S1_EC106_INGRESS_ATTESTATION_ID
            or self.r2_producer_receipt_digest != self.r2_receipt.receipt_digest
            or self.r4_r8_producer_receipt_digest
            != self.r4_r8_receipt.receipt_digest
            or self.source_result_digests
            != (
                self.r2_receipt.source_result_digest,
                self.r4_r8_receipt.source_result_digest,
            )
            or self.source_probe_receipt_digests != expected_probe_digests
            or len(self.source_probe_receipt_digests) != 24
            or len(set(self.source_probe_receipt_digests)) != 24
            or self.accounted_field_steps != 22456
            or self.producer_sequence != S1_EC105_PRODUCER_SEQUENCE
            or self.both_receipts_validated is not True
            or self.same_objects_forwarded_to_ec102 is not True
            or self.contractual_not_cryptographic is not True
            or len(self.source_probe_objects) != 24
            or len(self.forwarded_probe_objects) != 24
            or tuple(item.receipt_digest for item in self.source_probe_objects)
            != expected_probe_digests
            or any(
                source is not forwarded
                for source, forwarded in zip(
                    self.source_probe_objects,
                    self.forwarded_probe_objects,
                    strict=True,
                )
            )
            or self.attestation_digest != _digest(payload)
        ):
            raise E1CommonProbeEC106AttestationReceiptError(
                "S1-EC106 combined ingress attestation changed"
            )
        self.r2_receipt.__post_init__()
        self.r4_r8_receipt.__post_init__()


def _build_e1_common_probe_ec106_synthetic_r2_producer_receipt(
    source_result: E1CommonProbeN2R2RealModeCoordinatorResult,
    one_shot_authorization_digest: str,
) -> E1CommonProbeEC106R2ProducerReceipt:
    """Build only the private synthetic r2 contract fixture."""

    if not isinstance(source_result, E1CommonProbeN2R2RealModeCoordinatorResult):
        raise E1CommonProbeEC106AttestationReceiptError(
            "S1-EC106 r2 receipt requires one typed source result"
        )
    values = {
        "receipt_id": S1_EC106_R2_RECEIPT_ID,
        "producer_id": "EC67-r2",
        "one_shot_authorization_digest": one_shot_authorization_digest,
        "source_result_digest": source_result.result_digest,
        "source_probe_receipt_digests": tuple(
            item.receipt_digest for item in source_result.probes
        ),
        "accounted_field_steps": source_result.actual_field_steps_executed,
        "producer_sequence_index": 0,
        "emitted_atomically_with_result": True,
        "contractual_not_cryptographic": True,
    }
    return E1CommonProbeEC106R2ProducerReceipt(
        **values, receipt_digest=_digest(values), source_result=source_result
    )


def _build_e1_common_probe_ec106_synthetic_r4_r8_producer_receipt(
    source_result: E1CommonProbeEC96AtomicResult,
) -> E1CommonProbeEC106R4R8ProducerReceipt:
    """Build only the private synthetic r4/r8 contract fixture."""

    if not isinstance(source_result, E1CommonProbeEC96AtomicResult):
        raise E1CommonProbeEC106AttestationReceiptError(
            "S1-EC106 r4/r8 receipt requires one typed source result"
        )
    probes = tuple(
        probe
        for refinement in source_result.refinements
        for probe in refinement.probes
    )
    values = {
        "receipt_id": S1_EC106_R4_R8_RECEIPT_ID,
        "producer_id": "EC96-r4-r8",
        "one_shot_authorization_digest": source_result.authorization_digest,
        "source_result_digest": source_result.result_digest,
        "source_probe_receipt_digests": tuple(
            item.receipt_digest for item in probes
        ),
        "accounted_field_steps": source_result.total_field_steps,
        "producer_sequence_index": 1,
        "emitted_atomically_with_result": True,
        "contractual_not_cryptographic": True,
    }
    return E1CommonProbeEC106R4R8ProducerReceipt(
        **values, receipt_digest=_digest(values), source_result=source_result
    )


def _build_e1_common_probe_ec106_synthetic_combined_ingress_attestation(
    r2_receipt: E1CommonProbeEC106R2ProducerReceipt,
    r4_r8_receipt: E1CommonProbeEC106R4R8ProducerReceipt,
    source_probe_objects: tuple[object, ...],
    forwarded_probe_objects: tuple[object, ...],
) -> E1CommonProbeEC106CombinedIngressAttestation:
    """Bind only synthetic fixture receipts without invoking EC102."""

    if (
        not isinstance(r2_receipt, E1CommonProbeEC106R2ProducerReceipt)
        or not isinstance(r4_r8_receipt, E1CommonProbeEC106R4R8ProducerReceipt)
    ):
        raise E1CommonProbeEC106AttestationReceiptError(
            "S1-EC106 ingress requires both typed producer receipts"
        )
    r2_receipt.__post_init__()
    r4_r8_receipt.__post_init__()
    source = tuple(source_probe_objects)
    forwarded = tuple(forwarded_probe_objects)
    values = {
        "attestation_id": S1_EC106_INGRESS_ATTESTATION_ID,
        "r2_producer_receipt_digest": r2_receipt.receipt_digest,
        "r4_r8_producer_receipt_digest": r4_r8_receipt.receipt_digest,
        "source_result_digests": (
            r2_receipt.source_result_digest,
            r4_r8_receipt.source_result_digest,
        ),
        "source_probe_receipt_digests": (
            *r2_receipt.source_probe_receipt_digests,
            *r4_r8_receipt.source_probe_receipt_digests,
        ),
        "accounted_field_steps": (
            r2_receipt.accounted_field_steps + r4_r8_receipt.accounted_field_steps
        ),
        "producer_sequence": S1_EC105_PRODUCER_SEQUENCE,
        "both_receipts_validated": True,
        "same_objects_forwarded_to_ec102": all(
            left is right for left, right in zip(source, forwarded, strict=True)
        ) if len(source) == len(forwarded) else False,
        "contractual_not_cryptographic": True,
    }
    return E1CommonProbeEC106CombinedIngressAttestation(
        **values,
        attestation_digest=_digest(values),
        r2_receipt=r2_receipt,
        r4_r8_receipt=r4_r8_receipt,
        source_probe_objects=source,
        forwarded_probe_objects=forwarded,
    )


def run_e1_common_probe_ec106_synthetic_fixture(
) -> E1CommonProbeEC106CombinedIngressAttestation:
    """Exercise only the receipt contracts with synthetic EC103 containers."""

    r2_result = build_e1_common_probe_ec103_synthetic_r2_result()
    r4_r8_result = build_e1_common_probe_ec103_synthetic_r4_r8_result()
    r2_receipt = _build_e1_common_probe_ec106_synthetic_r2_producer_receipt(
        r2_result, _digest((S1_EC106_FIXTURE_ID, "r2-authorization"))
    )
    r4_r8_receipt = _build_e1_common_probe_ec106_synthetic_r4_r8_producer_receipt(
        r4_r8_result
    )
    probes = (
        *r2_result.probes,
        *(probe for refinement in r4_r8_result.refinements for probe in refinement.probes),
    )
    return _build_e1_common_probe_ec106_synthetic_combined_ingress_attestation(
        r2_receipt, r4_r8_receipt, probes, probes
    )
