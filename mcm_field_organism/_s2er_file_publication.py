"""Private S2-EO E0-E8 publisher. No runner, activation, recovery writes or CLI."""

from __future__ import annotations

from pathlib import Path, PureWindowsPath
import platform
import sys
from threading import Lock

from ._s2er_publication_records import (
    BACKEND, STUDY, PrivateRecord, PublicationError, _core, digest, encoded,
    file_references, loads, make_record, raw_digest, require, validate_bundle,
)
from ._s2er_windows_files import WindowsFiles


_PUBLICATION_RELEASE_ENABLED = False
_CLAIM_LOCK = Lock()
_CLAIMED_STUDIES: set[str] = set()


class FilePublication:
    """One private owner. Inputs and persisted expectations are immutable bytes.

    A future separately authorized runner may supply committed cell evidence.
    This class never constructs a cell owner or calls its state operators.
    """

    def __init__(self, bundle: bytes):
        require(type(bundle) is bytes, "immutable publication input required")
        self._bundle = bundle
        self._lock = Lock()
        self._status = "FRESH"
        self._files = None
        self._registry = None
        self._inputs = None
        self._reservation = None
        self._target = None
        self._starts: list[bytes] = []
        self._evidence: list[bytes] = []
        self._results: list[object] = []
        self._journal: list[bytes] = []
        self._persisted: list[tuple[object, bytes]] = []
        self._sources: list[tuple[object, bytes]] = []
        self._final_barrier_confirmed = False
        self._marker_barrier_confirmed = False
        self._rename_started = False
        self._failure = None
        self._close_errors = ()

    @property
    def status(self):
        return self._status

    def _invoke(self, allowed, action, *args):
        if not self._lock.acquire(blocking=False):
            raise PublicationError("PUBLICATION_OWNER_BUSY", "publication owner busy")
        try:
            require(self._status not in ("COMPLETED", "FAILED", "ABORTED_INCOMPLETE", "BLOCKED_PLATFORM_PREREQUISITE"),
                    "publication owner is terminal", "PUBLICATION_TERMINAL")
            try:
                require(self._status in allowed, "wrong publication phase", "PUBLICATION_TERMINAL")
                require(_PUBLICATION_RELEASE_ENABLED is True and _core()._EXECUTION_RELEASE_ENABLED is True,
                        "publisher and matrix releases remain separate and closed", "PUBLICATION_NOT_AUTHORIZED")
                return action(*args)
            except BaseException as error:
                self._failure = (type(error).__name__, getattr(error, "code", None),
                                 getattr(error, "native_error", None))
                self._status = "ABORTED_INCOMPLETE" if self._rename_started else "FAILED"
                if self._reservation is None and isinstance(error, PublicationError) and (
                    error.code == "BLOCKED_PLATFORM_PREREQUISITE" or error.native_error in (2, 3)
                ):
                    self._status = "BLOCKED_PLATFORM_PREREQUISITE"
                if self._files is not None:
                    self._close_errors = self._files.close_all(suppress=True)
                raise
        finally:
            self._lock.release()

    def begin(self) -> bytes:
        return self._invoke(("FRESH",), self._begin)

    def _begin(self):
        core = _core()
        values = validate_bundle(self._bundle)
        self._inputs = values
        # A failed E0/E1 must not become a second attempt via a fresh owner in
        # this process. Across processes the durable reservation and separate
        # one-shot admission remain required; absent files never install a pin.
        with _CLAIM_LOCK:
            require(STUDY not in _CLAIMED_STUDIES, "study already attempted in this process", "PUBLICATION_ALREADY_CONSUMED")
            _CLAIMED_STUDIES.add(STUDY)
        s, p, a, w = (values[k] for k in "SPAW")
        self._registry = core._validate_execution_sources(core._unrecord("SourceManifest", s),
                                                          core._unrecord("ExecutionPlan", p))
        require(w["platform_context"]["windows_version"] == platform.version()
                and w["platform_context"]["windows_build"] == str(sys.getwindowsversion().build),
                "Windows profile changed", "BLOCKED_PLATFORM_PREREQUISITE")
        expected_sources = {item["repository_relative_path"]: item["raw_sha256"] for item in s["project_sources"]}
        for name in ("_s2er_file_publication.py", "_s2er_publication_records.py", "_s2er_windows_files.py"):
            identity = core._file_identity(Path(__file__).with_name(name))
            expected_sources[identity["repository_relative_path"]] = identity["raw_sha256"]
        require(w["publisher_sources"] == [{"repository_relative_path": path, "raw_sha256": expected_sources[path]}
                                            for path in sorted(expected_sources)], "publisher closure differs")
        self._files = WindowsFiles()
        self._files.pin_parents(w["parent_directories"])
        paths = w["publication_paths"]
        for role in ("study_reservation", "target_reservation", "staging", "final", "completion_marker"):
            self._files.require_absent(paths[role])
        for ordinal in range(1, 57):
            for prefix in ("cell-start", "cell-evidence"):
                self._files.require_absent(self._ledger_path(f"{prefix}-{ordinal:03d}.json"))
        for ordinal in range(1, 114):
            self._files.require_absent(self._ledger_path(f"journal-{ordinal:03d}.json"))
        self._pin_sources(values)
        self._refresh()
        r = core._record("AttemptReservation", execution_authorization_digest=a["record_digest"],
                         execution_plan_digest=p["record_digest"], study_id=STUDY,
                         execution_domain_digest=digest(p["execution_domain"]), attempt_id="001", status="RESERVED").payload()
        # E1 consumption begins at CREATE_NEW, not only after a successful flush.
        self._reservation = encoded(r)
        self._write(paths["study_reservation"], self._reservation)
        t = make_record("TargetReservation", backend_contract_id=BACKEND, study_id=STUDY, attempt_id="001",
                        status="RESERVED", publication_plan_digest=w["record_digest"],
                        publication_authorization_digest=values["U"]["record_digest"],
                        execution_plan_digest=p["record_digest"], execution_authorization_digest=a["record_digest"],
                        reservation_digest=r["record_digest"], canonical_final_path=paths["final"],
                        parent_directory_identity=w["parent_directories"]["output"])
        self._target = encoded(t)
        self._write(paths["target_reservation"], self._target)
        self._refresh()
        self._status = "READY"
        return self._reservation

    def _pin_sources(self, values):
        paths = values["W"]["publication_paths"]
        references = {r["path"]: r for r in file_references(values)}
        root = PureWindowsPath(values["P"]["execution_domain"]["canonical_repository_path"])
        for source in (*values["W"]["publisher_sources"], *values["F"]["recorder_sources"]):
            path = str(root.joinpath(*source["repository_relative_path"].split("/")))
            handle, raw = self._files.read_source(path)
            require(raw_digest(raw) == source["raw_sha256"], "source bytes changed")
            self._sources.append((handle, raw))
        forbidden = {paths[k] for k in ("study_reservation", "target_reservation", "staging", "final", "completion_marker")}
        for path, reference in references.items():
            require(path not in forbidden and not PureWindowsPath(path).name.startswith(STUDY + "."),
                    "platform evidence aliases study output")
            handle, raw = self._files.read_source(path, reference["byte_count"])
            require(raw_digest(raw) == reference["raw_sha256"], "review or platform file changed")
            self._sources.append((handle, raw))
        handle, raw = self._files.read_source(paths["authorization"])
        require(raw == encoded(values["A"]), "original execution authorization changed")
        self._sources.append((handle, raw))

    def _refresh(self):
        require(validate_bundle(self._bundle) == self._inputs, "input or admission changed")
        core = _core()
        core._validate_execution_sources(core._unrecord("SourceManifest", self._inputs["S"]),
                                         core._unrecord("ExecutionPlan", self._inputs["P"]))
        self._files.verify_parents()
        for handle, expected in (*self._sources, *self._persisted):
            self._files.verify(handle, expected)

    def _ledger_path(self, name):
        return str(PureWindowsPath(self._inputs["W"]["publication_paths"]["durable_ledger_root"]) / (STUDY + "." + name))

    def _write(self, path, raw, *, rename=False):
        handle = self._files.create(path, rename=rename)
        self._files.write_complete(handle, raw)
        self._files.flush(handle)
        self._files.verify(handle, raw)
        self._persisted.append((handle, raw))
        return handle

    def _journal_record(self, status, *, start=None, evidence=None, artifact=None):
        return _core()._record("AttemptJournalEntry", reservation_digest=loads(self._reservation)["record_digest"],
                               journal_ordinal=len(self._journal) + 1,
                               previous_journal_entry_digest_or_null=loads(self._journal[-1])["record_digest"] if self._journal else None,
                               status=status, cell_start_digest_or_null=start, cell_evidence_digest_or_null=evidence,
                               sealed_artifact_digest_or_null=artifact, error_or_null=None).payload()

    def _append_journal(self, **values):
        raw = encoded(self._journal_record(**values))
        self._write(self._ledger_path(f"journal-{len(self._journal) + 1:03d}.json"), raw)
        self._journal.append(raw)

    def start_cell(self) -> bytes:
        """Persist a start only; caller receives no cell execution through this module."""
        return self._invoke(("READY",), self._start_cell)

    def _start_cell(self):
        self._refresh()
        ordinal = len(self._starts) + 1
        require(ordinal <= 56 and len(self._evidence) == ordinal - 1, "start order differs")
        plan = self._registry[3][ordinal - 1]
        r_digest = loads(self._reservation)["record_digest"]
        suffix = f"{r_digest}.{ordinal:03d}"
        start = _core()._record("CellStart", reservation_digest=r_digest, ordinal=ordinal,
                                cell_id=plan.cell_id, cell_plan_digest=plan.cell_plan_digest,
                                owner_id="s2ee.owner." + suffix, consumption_id="s2ee.consume." + suffix,
                                expected_initial_state_digest=plan.initial_state_digest).payload()
        raw = encoded(start)
        self._write(self._ledger_path(f"cell-start-{ordinal:03d}.json"), raw)
        self._append_journal(status="RUNNING", start=start["record_digest"])
        self._starts.append(raw)
        self._status = "AWAITING_CELL"
        return raw

    def record_cell(self, owner, result) -> bytes:
        return self._invoke(("AWAITING_CELL",), self._record_cell, owner, result)

    def _record_cell(self, owner, result):
        self._refresh()
        core = _core()
        ordinal = len(self._starts)
        config, fixtures, arms, plans, _ = self._registry
        plan = plans[ordinal - 1]
        require(type(owner) is core.S2DRCellOwner and type(result) is core.S2DRCellResult, "exact owner/result required")
        core.validate_s2dr_cell_result(config, next(f for f in fixtures if f.history_id == plan.history_id),
                                       next(a for a in arms if a.arm_id == plan.arm_id), plan, result)
        snapshot, start = owner.snapshot(), loads(self._starts[-1])
        require(snapshot.status == "COMMITTED" and snapshot.owner_id == start["owner_id"]
                and snapshot.consumption_id == start["consumption_id"] and snapshot.cell_id == plan.cell_id
                and snapshot.authorization_digest == plan.authorization_digest
                and snapshot.cell_plan_digest == plan.cell_plan_digest and snapshot.internal_error_code is None
                and snapshot.committed_result_digest == result.cell_result_digest
                and result.cell_receipt.owner_id == snapshot.owner_id, "owner/result source differs")
        evidence = core._record("CellEvidence", cell_start_digest=start["record_digest"],
                                core_cell_result=core._canonical(result), core_cell_result_digest=result.cell_result_digest,
                                owner_terminal_snapshot=core._canonical(snapshot),
                                checkpoint_evidence=[f["checkpoint_evidence"] for f in result.finding_payloads],
                                observations=[f["observation"] for f in result.finding_payloads],
                                cost_evidence={"formation": [e["cost_evidence"] for e in result.event_payloads],
                                               "probe": [f["cost_evidence"] for f in result.finding_payloads]},
                                source_manifest_digest=self._inputs["S"]["record_digest"]).payload()
        raw = encoded(evidence)
        self._write(self._ledger_path(f"cell-evidence-{ordinal:03d}.json"), raw)
        self._append_journal(status="RUNNING", start=start["record_digest"], evidence=evidence["record_digest"])
        self._evidence.append(raw)
        self._results.append(result)
        self._status = "READY"
        return raw

    def _validate_artifact(self, raw):
        core = _core()
        artifact = core._unrecord("MatrixArtifact", loads(raw)).payload()
        require(encoded(artifact) == raw and len(self._evidence) == len(self._starts) == 56, "incomplete artifact")
        s, p, a = (self._inputs[k] for k in "SPA")
        r = loads(self._reservation)
        require(artifact["execution_plan_digest"] == p["record_digest"]
                and artifact["execution_authorization_digest"] == a["record_digest"]
                and artifact["reservation_digest"] == r["record_digest"] and artifact["status"] == "COMPLETED",
                "artifact source differs")
        require(artifact["ordered_cell_evidence"] == [loads(x) for x in self._evidence]
                and artifact["ordered_cell_evidence_digests"] == [loads(x)["record_digest"] for x in self._evidence],
                "artifact evidence differs")
        require(artifact["source_final_check"] == {"unchanged": True, "source_manifest": s, "execution_plan": p,
                                                  "authorization": a, "reservation": r,
                                                  "cell_starts": [loads(x) for x in self._starts]}, "final source check differs")
        config, fixtures, arms, plans, _ = self._registry
        by_role = {}
        for plan, result, raw_evidence in zip(plans, self._results, self._evidence, strict=True):
            require(encoded(core._canonical(result)) == encoded(loads(raw_evidence)["core_cell_result"]), "mutable result changed")
            core.validate_s2dr_cell_result(config, next(f for f in fixtures if f.history_id == plan.history_id),
                                           next(a for a in arms if a.arm_id == plan.arm_id), plan, result)
            by_role[plan.history_id, plan.arm_id] = result
        # Reuse the existing pure comparator projections, never its runner or
        # attestation type. No decision threshold or ordering is introduced here.
        metrics = {arm: core._per_arm_metrics(by_role, arm) for arm in core.ARM_IDS}
        vectors = {arm: tuple(metrics[arm]["predicate_vector"]) for arm in core.ARM_IDS}
        errors = {arm: sum(by_role[h, arm].cell_receipt.internal_error_code is not None for h in core.HISTORY_IDS)
                  for arm in core.ARM_IDS}
        exact = all(core._exact_reduction_projection(by_role[h, "R0"]) ==
                    core._exact_reduction_projection(by_role[h, "TSPM1"]) for h in core.HISTORY_IDS)
        keys = core._ee_contract()["source_and_receipt_contract"]["r0_observation_projection_fields"]
        exact = exact and all(tuple(tuple(f["observation"][k] for k in keys) for f in by_role[h, "R0"].finding_payloads) ==
                              tuple(tuple(f["observation"][k] for k in keys) for f in by_role[h, "TSPM1"].finding_payloads)
                              for h in core.HISTORY_IDS)
        decision, strongest = core._decision_from_vectors(vectors, errors, exact, metrics)
        expected = core._record("ComparisonPayload", evaluation_id=core.S2EE_EVALUATION_ID,
                                registry_digest=p["registry_digest"],
                                ordered_cell_evidence_digests=tuple(loads(x)["record_digest"] for x in self._evidence),
                                per_arm_metrics=tuple((arm, metrics[arm]) for arm in core.ARM_IDS),
                                all_arm_ranking=tuple(sorted(core.ARM_IDS, key=lambda arm: core._rank_key(arm, metrics))),
                                simple_baseline_ranking=tuple(sorted(core.SIMPLE_BASELINE_ORDER, key=lambda arm: core._rank_key(arm, metrics))),
                                strongest_simple_baseline_id=strongest, r0_exact_equivalence=exact, decision=decision,
                                structural_representation_status="NOT_ASSESSED_BY_BOUND_FIXTURES").payload()
        require(artifact["comparison_payload"] == expected and artifact["comparison_digest"] == expected["record_digest"]
                and artifact["technical_errors"] == errors and not any(errors.values()) and decision != "METHOD_INVALID"
                and artifact["structural_representation_status"] == "NOT_ASSESSED_BY_BOUND_FIXTURES", "comparison or technical result differs")
        return artifact

    def finish(self, artifact_raw: bytes) -> bytes:
        return self._invoke(("READY",), self._finish, artifact_raw)

    def _finish(self, raw):
        require(type(raw) is bytes and len(self._journal) == 112, "full immutable result required")
        self._refresh()
        artifact = self._validate_artifact(raw)
        paths = self._inputs["W"]["publication_paths"]
        staging = self._write(paths["staging"], raw, rename=True)
        self._validate_artifact(self._files.read(staging, len(raw)))
        self._append_journal(status="SEALED", artifact=artifact["record_digest"])
        self._status = "SEALED"
        self._refresh()
        self._files.require_absent(paths["final"])
        try:
            self._files.rename_no_replace(staging, paths["final"])
        finally:
            self._rename_started = staging.rename_attempted
        self._files.flush(staging)
        self._files.verify(staging, raw)
        self._files.verify_final_name(staging)
        self._validate_artifact(self._files.read(staging, len(raw)))
        self._final_barrier_confirmed = True
        terminal = self._journal_record("COMPLETED", artifact=artifact["record_digest"])
        w, p, a, s = (self._inputs[k] for k in "WPAS")
        marker = make_record("CompletionMarker", backend_contract_id=BACKEND, study_id=STUDY, attempt_id="001",
                             execution_plan_digest=p["record_digest"], execution_authorization_digest=a["record_digest"],
                             source_manifest_digest=s["record_digest"], platform_acceptance_digest=w["platform_acceptance_digest"],
                             reservation_digest=loads(self._reservation)["record_digest"],
                             target_reservation_digest=loads(self._target)["record_digest"],
                             canonical_final_path=paths["final"], parent_directory_identity=w["parent_directories"]["output"],
                             result_volume_identity=staging.identity["volume"], result_file_identity=staging.identity,
                             result_byte_count=len(raw), result_raw_sha256=raw_digest(raw),
                             result_artifact_digest=artifact["record_digest"], terminal_journal_entry=terminal)
        marker_raw = encoded(marker)
        marker_handle = self._write(paths["completion_marker"], marker_raw)
        PrivateRecord("CompletionMarker", self._files.read(marker_handle, len(marker_raw))).payload()
        self._journal.append(encoded(terminal))
        self._marker_barrier_confirmed = True
        self._refresh()
        require(self._final_barrier_confirmed and self._marker_barrier_confirmed, "barriers unconfirmed")
        self._files.close_all()
        self._status = "COMPLETED"
        return marker_raw

    def abort(self):
        """Explicit terminal closure only; no cleanup writes or resume path."""
        with self._lock:
            if self._status == "COMPLETED":
                return
            self._status = "ABORTED_INCOMPLETE" if self._rename_started else "FAILED"
            if self._files is not None:
                self._close_errors = self._files.close_all(suppress=True)
