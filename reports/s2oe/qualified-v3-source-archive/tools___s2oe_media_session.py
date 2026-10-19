"""Private media source adapter using the OC session and native OB branches."""
from dataclasses import asdict
import json
from pathlib import Path
from threading import Lock
import numpy as np

from tools import _s2oe_media_binding as p
from tools._s2oe_decoder_worker import WorkerDecoder as Decoder, resource_profile, STOP_SECONDS
from tools import _s2oc_bound_session as oc

b, s, r = p.b, p.shared, p.b.r
QUAL_ID = "media-worker-qualification-20260911-01"
OWN = ("tools/_s2oe_media_binding.py", "tools/_s2oe_media_decoder.py",
       "tools/_s2oe_media_session.py", "tools/_s2oe_media_verification.py",
       "tests/test_s2oe_media.py", "reports/qualify_direct_media_once.py",
       "reports/prepare_direct_media_budget.py", "tools/_s2oe_decoder_worker.py",
       "tests/test_s2oe_worker.py", "tests/s2oe_neutral_worker.py",
       "reports/qualify_media_worker_once.py")


def inventory():
    return {name: [s.sha((b.ROOT/name).read_bytes()), (b.ROOT/name).stat().st_size] for name in OWN}


class NativeRuntime(b.CallerRuntime):
    def __init__(self, manifest):
        # Only the admission type changes. Branches and their native configuration
        # are the same constructions as CallerRuntime, with no synthetic Payloads.
        self.expected, self.manifest = p.validate(manifest), manifest
        self.config, self.run_id = r.nn.profile.build_config(), manifest.run_id
        self.inputs, self.packed, self.source = [], [], []
        self.binding = r.ng.build_binding(self.config, "ALL_BANDS_24")
        fs, ms = r.null_field(self.config), r.memory.initial_s2jv_composite_state(self.config)
        self.fb = r.ng.ObservedBranch(r.ng.field.build_s2lo_field_adapter(b.CLOCK), fs)
        self.mb, self.scans = r.MemoryBranch(self.config, self.run_id, ms), {}
        processor = r.ng.stream.RoleFreePerceptionStreamProcessor(field_adapter=self.fb, memory_adapter=self.mb,
            auditory_scan=r.ng.AudioAdapter(self.binding, self.config, False, self.scans),
            auditory_baseline=r.ng.AudioAdapter(self.binding, self.config, True, self.scans),
            visual_scan=r.ng.VisualAdapter(self.config, False, self.scans),
            visual_baseline=r.ng.VisualAdapter(self.config, True, self.scans))
        rc = r.ng.runtime.build_minimal_runtime_config(runtime_id=self.run_id,
            max_event_count=len(manifest.events), source_binding_digest=manifest.manifest_digest,
            component_binding_digest=self.binding.binding_digest)
        initial = r.ng.stream.initial_perception_stream_state(stream_id=self.run_id,
            field_state=fs, field_state_digest=fs.state_digest, memory_state=ms, memory_state_digest=ms.state_digest)
        self.subject = r.ng.runtime.MinimalMCMRuntime336(config=rc, processor=processor, initial_state=initial)
        self.rc, self.rows, self.states = asdict(rc), [], b.StateEvidencePool()
        self.states[ms.state_digest] = asdict(ms)
        self.initial = dict(snapshot=asdict(self.subject.snapshot()), field=r.ng.field_record(fs), memory=ms.state_digest)
        self.births = [None]*24
        self.chain = b.digest(dict(initial=ms.state_digest, config=self.config.config_digest))
        self.failed, self.phase, self.failure, self.closed = False, "INITIAL", None, False


class Materializer:
    def __init__(self, manifest, decoder):
        self.manifest, self.decoder = manifest, decoder
        self.config = r.nn.profile.build_config()
        self.audio = r.half.spectral.LogSpectralReceptor(r.nn.LogSpectralConfig())
        self.video = b.LocalChannelGridReceptor(b.VisualGridConfig())
        self.counts = dict(payloads=0, audio=0, nj=0, visual=0, materialized_events=0)
        self.receipts = []
        self.phase, self.source_id = "BINDINGS", None

    @property
    def read_account(self):
        return dict(actual_read_bytes=self.decoder.counters["container_read_bytes"],
            read_operations=self.decoder.counters["packets"])

    def next(self, event):
        p.need(event == self.manifest.events[self.counts["materialized_events"]], "MATERIALIZATION_ORDER_INVALID")
        self.source_id, self.phase = event.event_id, "PAYLOAD_READ"
        pcm, rgb, pts, next_pts = self.decoder.select(event.pass_number, event.window_number)
        times = p.runtime_times(event)
        raw = visual = ah = vh = None
        if event.kind != b.V:
            p.need(pcm.dtype == np.dtype("<f4") and pcm.shape == (4800,)
                and np.isfinite(pcm).all() and np.max(np.abs(pcm)) <= 1, "PCM_INVALID")
            ah = s.sha(pcm.tobytes())
            self.counts["payloads"] += 1
            self.phase = "AUDIO_ANALYSIS"
            values = tuple(self.audio.analyze(pcm))
            self.counts["audio"] += 1
            activity = r.half.AuditoryReceptorContact.ACTIVE_ENERGY if any(values) else r.half.AuditoryReceptorContact.ACTIVE_ZERO
            raw = r.half.AuditoryReceptorState("auditory", r.half.RAW_GEOMETRY,
                times["audio_index"], *times["audio_window"], self.audio.channel_ids, values, activity)
        if event.kind != b.A:
            p.need(rgb.dtype == np.uint8 and rgb.shape == (1080, 1920, 3), "RGB_INVALID")
            frame = rgb
            if event.kind == b.V:
                frame = rgb.copy()
                cells = frame.reshape(8, 135, 12, 160, 3)
                for i in range(32, 288):
                    cell, channel = divmod(i, 3)
                    row, col = divmod(cell, 12)
                    cells[row, :, col, :, channel] = 0
                del cells
            vh = s.sha(frame.tobytes())
            self.counts["payloads"] += 1
            self.phase = "VISUAL_ANALYSIS"
            state = self.video.analyze(frame, frame_index=times["visual_window"][0])
            self.counts["visual"] += 1
            visual = r.nn.OrganismTimedReceptorFrame(b.from_visual_receptor_state(state),
                r.nn.CommonFieldTime(b.CLOCK, *times["visual_common"]))
            del frame
        receipt = p.selection_receipt(self.manifest, event,
            None if event.kind == b.A else pts, None if event.kind == b.A else next_pts, ah, vh)
        self.phase = "NJ_CONTACT"
        item = b.bind_input(config=self.config, ordinal=event.ordinal, event_id=event.event_id,
            kind=event.kind, raw_audio=raw, visual=visual, pcm_digest=ah, rgb_digest=vh)
        self.counts["nj"] += int(raw is not None)
        self.counts["materialized_events"] += 1
        self.receipts.append(receipt)
        if event.kind == b.AV:
            self.decoder.release()
        return item


class Session(oc.Session):
    def _check_progress_budget(self):
        rows = {k:p.ledger(*pair,self._common,attachments=oc.ATTACHMENTS)
            for k,pair in zip(("success","failure"),self._forms())}
        p.enforce(rows,"EVIDENCE",min(len(self._runtime.rows)+1,24),len(self._runtime.rows))
        self._last_budget = rows

    def _publish(self, record):
        p.need(self._terminal is None,"SESSION_ALREADY_PUBLISHED")
        binding = self._binding(record)
        value = p.ledger(record,binding,self._common,attachments=oc.ATTACHMENTS)
        p.enforce({"actual":value},self._phase,None,len(self._runtime.rows) if self._runtime else 0)
        wr,ws = s.pack(record,binding,self._common)
        s.prior.save(self._path/"record.json",wr)
        s.prior.save(self._path/"session.json",ws)
        self._terminal = b.canonical(record)
        return self._terminal

    def _record(self, core=None, failure=None):
        value = super()._record(core, failure)
        value.pop("record_digest")
        value["media"] = dict(receipts=[] if self._materializer is None else self._materializer.receipts,
            decoder={} if self._materializer is None else dict(self._materializer.decoder.counters),
            resources=None if self._materializer is None else dict(self._materializer.decoder.resources))
        p.need(len(b.canonical(dict(decoder=value["media"]["decoder"],
            resources=value["media"]["resources"]))) <= 2048, "DECODER_EVIDENCE_LIMIT")
        return b.sealed(value, "record_digest")

    def process(self, event):
        p.need(self._lock.acquire(blocking=False), "SESSION_BUSY")
        try:
            p.need(self._terminal is None and not self._runtime.closed, "SESSION_CLOSED")
            n = len(self._runtime.rows)
            p.need(n < 24 and type(event) is p.Selection and event == self._manifest.events[n], "EVENT_ORDER_INVALID")
            p.need(b.canonical(asdict(self._manifest)) == self._manifest_bytes, "MANIFEST_CHANGED")
            try:
                self._phase = self._runtime.phase = "EVIDENCE"
                self._check_progress_budget()
                self._phase = "MATERIALIZATION"
                item = self._materializer.next(event)
                self._phase = self._runtime.phase = "EVENT"
                row = self._runtime.process(item)
                self._check_progress_budget()
                raw = b.canonical(row["step"])
                p.need(len(raw) <= 16384, "STEP_LIMIT")
            except Exception as exc:
                phase = self._materializer.phase if self._phase == "MATERIALIZATION" else self._runtime.phase
                self._fail(exc, phase, event.ordinal)
                raise
            if self._runtime.failed:
                core = self._runtime.record()
                self._materializer.decoder.close()
                self._publish(self._record(core, core["failure"]))
                raise p.MediaError(core["failure"]["code"])
            self._returned.append(dict(ordinal=event.ordinal, sha256=s.sha(raw), byte_count=len(raw)))
            return raw
        finally:
            self._lock.release()

    def next(self):
        p.need(self._terminal is None and len(self._returned) < 24, "SESSION_CLOSED")
        return self.process(self._manifest.events[len(self._returned)])

    def status(self):
        p.need(self._lock.acquire(blocking=False), "SESSION_BUSY")
        try:
            return b.canonical(dict(version=p.VERSION, closed=self._terminal is not None,
                completed=len(self._runtime.rows), snapshot=asdict(self._runtime.subject.snapshot()),
                decoder=dict(self._materializer.decoder.counters)))
        finally:
            self._lock.release()

    def _fail(self, exc, phase, ordinal):
        if self._materializer is not None:
            try:
                self._materializer.decoder.close()
            except Exception:
                # Preserve the primary failure; cleanup is bounded supplementary evidence.
                self._materializer.decoder.counters["close_errors"] = 1
        return super()._fail(exc, phase, ordinal)

    def close(self):
        p.need(self._lock.acquire(blocking=False), "SESSION_BUSY")
        try:
            if self._terminal is not None:
                return self._terminal
            try:
                self._check_progress_budget()
                self._materializer.decoder.close()
                if len(self._runtime.rows) != 24:
                    return self._fail(p.MediaError("INCOMPLETE"), "CLOSE", None)
                core = self._runtime.record()
                return self._publish(self._record(core, core["failure"]))
            except Exception as exc:
                if self._terminal is None:
                    self._fail(exc, "CLOSE", None)
                raise
        finally:
            self._lock.release()

    def stop(self):
        if self._terminal is not None:
            return self._terminal
        # Cancellation must not wait for the session lock held during selection.
        if self._lock.locked():
            if self._materializer is not None:
                self._materializer.decoder.cancel()
            p.need(self._lock.acquire(timeout=STOP_SECONDS + 5), "SESSION_STOP_TIMEOUT")
            self._lock.release()
        return self.close()


def bind_common(manifest, base, refs):
    p.validate(manifest)
    rule = base["rule_binding"]
    rc = r.ng.runtime.build_minimal_runtime_config(runtime_id=manifest.run_id,
        max_event_count=24, source_binding_digest=manifest.manifest_digest,
        component_binding_digest=rule["binding_digest"])
    return b.sealed(dict(version=p.VERSION, manifest=json.loads(b.canonical(asdict(manifest))),
        references=list(refs), inventory_sha256=base["inventory_sha256"],
        decoder_resource_profile=resource_profile(),
        rule_binding=rule, runtime_config=asdict(rc), qualification=base["qualification"],
        read_plan=dict(input_stock_bytes=manifest.source.size, planned_read_bytes=12*manifest.source.size)), "common_digest")


def check_common(manifest, common, inv):
    b.check_root(common, "common_digest")
    p.need(inv == s.inventory() and common["inventory_sha256"] == s.sha(b.canonical(inv)), "OC_CODE_CHANGED")
    # The unchanged OC qualification is checked as evidence, never re-executed.
    base_path = b.ROOT/"reports/s2oc"/s.QUAL_ID
    anchor = s.read_json(base_path/"caller-common.json")
    legacy_manifest = b.decode_manifest(anchor["manifest"])
    base, _ = s.qualified_common(legacy_manifest, base_path)
    p.need(common == bind_common(manifest, base, common["references"]), "COMMON_BINDING_INVALID")
    paths = set()
    for kind, name, size, sha in common["references"]:
        p.need(name not in paths, "REFERENCE_DUPLICATE")
        paths.add(name)
        p.need(s.file_reference(kind, b.ROOT/name) == [kind, name, size, sha], "REFERENCE_CHANGED")
    p.need(all(ref in common["references"] for ref in base["references"]), "OC_REFERENCE_MISSING")
    p.need(s.file_reference("metadata", base_path/"caller-common.json") in common["references"], "OC_ANCHOR_MISSING")
    p.need(all(s.file_reference("sources", b.ROOT/name) in common["references"] for name in OWN), "MEDIA_REFERENCE_MISSING")
    p.need(any(ref[0] == "sources" and ref[3] == manifest.code_digest for ref in common["references"]), "MEDIA_INVENTORY_MISSING")


def start(manifest, common, inv, directory, *, neutral=False):
    try:
        p.need(p.MAIN_GATE is True, "MAIN_GATE_CLOSED")
        p.MAIN_GATE = False
        p.validate(manifest)
        p.need(manifest.code_digest == b.digest(inventory()), "CURRENT_CODE_CHANGED")
        check_common(manifest, common, inv)
        if not neutral:
            q = s.read_json(b.ROOT/"reports/s2oe"/QUAL_ID/"result.json")
            b.check_root(q, "result_digest")
            p.need(q["status"] == "QUALIFIED" and q["sources"] == inventory()
                and s.file_reference("metadata", b.ROOT/"reports/s2oe"/QUAL_ID/"result.json")
                in common["references"], "MEDIA_NOT_QUALIFIED")
        else:
            p.need(Path(manifest.source.path).resolve().is_relative_to(b.ROOT/"sources/s2oe-worker-neutral"), "REAL_MEDIA_BLOCKED")
        path = Path(directory)
        p.need(not path.exists() and path.parent.is_dir(), "OUTPUT_CONFLICT")
        from reports.prepare_direct_media_budget import prepare, META_PARTS
        upper = prepare()
        p.need(all(not row[k]["violations"] for row in upper["positions"]
            for k in ("success", "failure")), "PREFLIGHT_LIMIT")
        from tools._s2oc_shared_verification import synthetic_forms
        reserve = tuple(("metadata", k, n) for k,n in META_PARTS.items())
        for n in range(25):
            for pair in synthetic_forms(common, n):
                p.need(not p.ledger(*pair, common, attachments=reserve)["violations"], "ACTUAL_BINDING_LIMIT")
        c = Session.__new__(Session)
        c._lock, c._manifest = Lock(), manifest
        c._manifest_bytes = b.canonical(asdict(manifest))
        c._common, c._sources, c._refs = json.loads(b.canonical(common)), json.loads(b.canonical(inv)), s.references(common)
        c._active_qualification = common["qualification"]
        c._path, c._mode, c._terminal, c._returned = path, "MEDIA", None, []
        c._runtime = c._materializer = None
        c._phase = "RUNTIME_INIT"
        path.mkdir()
        s.prior.save(path/"common.json", common)
        try:
            c._runtime = NativeRuntime(manifest)
            c._materializer = Materializer(manifest, Decoder(manifest.source))
            c._check_progress_budget()
        except Exception as exc:
            c._fail(exc, "RUNTIME_INIT", None)
            raise
        return c
    finally:
        p.MAIN_GATE = False
