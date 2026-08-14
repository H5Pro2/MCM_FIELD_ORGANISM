from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_marker_audit import audit_receptor_markers
from mcm_field_organism.receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


def sequence(modality, values):
    frames = []
    for index, value in enumerate(values):
        start = index * 1_000_000_000
        frames.append(OrganismTimedReceptorFrame(
            frame=ReceptorContactFrame(
                modality, f"{modality}.grid", f"{modality}.{index}",
                "sensor.clock", index, index + 1, ("cell.0",), (value,),
            ),
            field_time=CommonFieldTime("organism.monotonic_ns", start, start + 1),
        ))
    return ReceptorTimeSequence(modality, f"{modality}.grid", "organism.monotonic_ns", tuple(frames))


def test_pairs_three_post_baseline_transients_in_time_order():
    auditory = sequence("auditory", (0, .01, 0, .01, 0, .8, 0, .7, 0, .6, 0))
    visual = sequence("visual", (0, .01, 0, .01, 0, 0, .8, 0, .7, 0, .6))
    result = audit_receptor_markers(
        (auditory, visual), baseline_seconds=3, marker_delay_seconds=1,
        expected_marker_count=3, minimum_separation_seconds=1.5,
    )
    assert result.complete_order_pairing
    assert result.visual_minus_auditory_nanoseconds == (
        1_000_000_000, 1_000_000_000, 1_000_000_000,
    )


def test_withholds_offsets_when_one_modality_lacks_marker_count():
    auditory = sequence("auditory", (0, .01, 0, .01, 0, .8, 0, .7, 0, .6, 0))
    visual = sequence("visual", (0, .01, 0, .01, 0, 0, 0, 0, 0, 0, 0))
    result = audit_receptor_markers(
        (auditory, visual), baseline_seconds=3, marker_delay_seconds=1,
        expected_marker_count=3, minimum_separation_seconds=1.5,
    )
    assert not result.complete_order_pairing
    assert result.visual_minus_auditory_nanoseconds == ()
