"""Focused metadata admission checks; selected media is physically read-blocked."""
from dataclasses import asdict, replace, FrozenInstanceError
import json
import os
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from reports import run_selected_media_restart_once as entry
from tools import _media_restart_admission as a
from tools import _media_restart_checkpoint as c
from tools import _media_restart_evidence as e
from tools import _media_restart_player as p
from tools import _media_restart_work as w

OUT = Path(os.environ["MEDIA_ADMISSION_QUAL_OUT"])


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.root = OUT/self._testMethodName
        self.root.mkdir()
        self.inv = json.loads((OUT/"preregistration.json").read_bytes())["inventory"]
        self.manifest = c.p.build("media-admission-neutral-20260913-02",
            c.p.Source(str(a.SOURCE), a.SHA256, a.SIZE), c.b.digest(self.inv), mode=c.p.FULL_VERSION)
        m = self.manifest
        self.admission = a.Admission(a.VERSION, m.run_id, m.manifest_digest,
            m.code_digest, m.profile_digest, m.source.path, m.source.sha256, m.source.size, True)
        self.future = [dict(name="closure", paths=["result.json"], limit=4096, closed_by="result.json")]
        self.store = e.Store(self.root/"store", future=self.future)
        original = Path.open
        def read_guard(path, *args, **kwargs):
            if path.resolve() == a.SOURCE.resolve():
                raise AssertionError("REAL_PAYLOAD_ACCESS_FORBIDDEN")
            return original(path, *args, **kwargs)
        self.addCleanup(patch.stopall)
        patch.object(Path, "open", read_guard).start()
        patch.object(c, "QUALIFIED", True).start()
        self.addCleanup(setattr, c, "MAIN_GATE", False)

    def error(self, code, call):
        with self.assertRaises(w.RestartError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)

    def app(self, manifest=None, admission=None, mode=a.REAL):
        return p.Player(NS(manifest=manifest or self.manifest, source=a.SOURCE,
            output=self.store.root/"native", claim=self.store.root/"claim.json", mode=mode,
            admission=admission or self.admission), self.store)

    def both_reject(self, code, admission, manifest=None):
        m = manifest or self.manifest
        with patch.object(c.media, "NativeRuntime", side_effect=AssertionError("RUNTIME_FORBIDDEN")), \
             patch.object(w, "WorkerDecoder", side_effect=AssertionError("DECODER_FORBIDDEN")):
            self.error(code, lambda: self.app(m, admission)._authorize())
            c.MAIN_GATE = True
            self.error(code, lambda: c.Session(m, self.store.root/"native", self.store,
                mode=a.REAL, admission=admission))
            c.MAIN_GATE = False

    def test_01_valid_immutable_selected_admission(self):
        a.validate(self.manifest, a.REAL, self.admission)
        with self.assertRaises(FrozenInstanceError):
            self.admission.authorized = False
        self.assertEqual(self.manifest.source.sha256, a.SHA256)

    def test_02_source_fields_rejected_at_both_sites(self):
        for field, value in (("source_path", "C:/foreign.mp4"), ("source_sha256", "0"*64), ("source_size", 1)):
            with self.subTest(field=field):
                self.both_reject("RESTART_REAL_SOURCE", replace(self.admission, **{field: value}))

    def test_03_profile_run_manifest_code_at_both_sites(self):
        for field, code in (("profile_digest", "PROFILE"), ("run_id", "RUN"),
                            ("manifest_digest", "MANIFEST"), ("code_digest", "CODE")):
            with self.subTest(field=field):
                self.both_reject("RESTART_REAL_"+code, replace(self.admission, **{field: "0"*64}))

    def test_04_authorization_and_mode(self):
        self.both_reject("RESTART_REAL_AUTHORIZATION_REQUIRED", replace(self.admission, authorized=False))
        self.error("RESTART_REAL_ADMISSION_REQUIRED", lambda: a.validate(self.manifest, a.REAL))
        self.error("RESTART_PLAYER_NOT_ADMITTED", lambda: a.validate(self.manifest, "foreign", self.admission))

    def test_05_neutral_conditions_both_sites(self):
        m = c.p.build("neutral-admission-20260913-01", c.p.Source(
            str(c.b.ROOT/"sources/media-restart-neutral/unread.bin"), "1"*64, 16),
            self.manifest.code_digest, mode=c.p.FULL_VERSION)
        app = p.Player(NS(manifest=m, source=Path(m.source.path), output=self.store.root/"native",
            claim=self.store.root/"neutral.claim", mode=a.NEUTRAL), self.store)
        app._authorize()
        with patch.object(c.media, "NativeRuntime", side_effect=w.RestartError("AFTER_ADMISSION")) as reached:
            self.error("AFTER_ADMISSION", app._open_session)
            reached.assert_called_once_with(m)
        self.assertFalse(c.MAIN_GATE)
        self.error("REAL_MEDIA_RESTART_BLOCKED", lambda: a.validate(self.manifest))

    def test_06_real_player_to_session_reaches_post_admission(self):
        app = self.app()
        app._authorize()
        with patch.object(c.media, "NativeRuntime", side_effect=w.RestartError("AFTER_ADMISSION")) as reached:
            self.error("AFTER_ADMISSION", app._open_session)
            reached.assert_called_once_with(self.manifest)
        self.assertFalse(c.MAIN_GATE)
        self.assertEqual(self.store.read(self.store.root/"claim.json")["manifest"], self.manifest.manifest_digest)

    def fixture(self):
        inventory = {"reports/run_selected_media_restart_once.py":
                     self.inv["reports/run_selected_media_restart_once.py"]}
        self.manifest = c.p.build(self.manifest.run_id, self.manifest.source,
                                 c.b.digest(inventory), mode=c.p.FULL_VERSION)
        def write(name, value):
            target = self.root/name
            raw = e.canonical(value)
            with target.open("xb") as stream:
                stream.write(raw)
            return target, e.sha(raw)
        ipath, isha = write("synthetic-inventory.json", dict(inventory=inventory,
            charged_sources=list(inventory)))
        qpath, qsha = write("synthetic-proof.json", dict(status="QUALIFIED", inventory_digest=c.b.digest(inventory),
            preregistration_sha256=isha, hashes_unchanged=True,
            scope="Synthetic admission fixture, not a real grant"))
        external = [dict(path=str(qpath), category="metadata", **entry.identity(qpath))]
        data = dict(version=entry.VERSION, limits=e.LIMITS, stages=list(entry.STAGES),
            manifest=asdict(self.manifest), external=external, future=self.future,
            inventory_binding=dict(path=ipath.relative_to(c.b.ROOT).as_posix(), sha256=isha),
            output="reports/"+self.manifest.run_id,
            qualification=dict(path=qpath.relative_to(c.b.ROOT).as_posix(), sha256=qsha))
        path, sha = write("binding.json", data)
        authpath, authsha = write("authorization.json", dict(version=entry.VERSION, authorized=True,
            single_use=True, run_id=self.manifest.run_id, binding_sha256=sha))
        return path, sha, authpath, authsha

    def test_07_file_entry_load_binding_and_no_payload(self):
        args = self.fixture()
        data, m, admission, output, refs = entry.load(*args)
        self.assertEqual(m, self.manifest)
        a.validate(m, a.REAL, admission)
        self.assertTrue(all(any(Path(x["path"]) == path for x in refs) for path in (args[0], args[2])))
        self.assertFalse(output.exists())

    def test_08_entry_rejects_before_any_launch(self):
        args = self.fixture()
        with patch.object(entry, "launch", side_effect=AssertionError("LAUNCH_FORBIDDEN")):
            self.error("REAL_BINDING_HASH", lambda: entry.execute(args[0], "0"*64, *args[2:]))
            raw = json.loads(args[2].read_bytes())
            raw["authorized"] = False
            other = self.root/"not-authorized.json"
            data = e.canonical(raw)
            with other.open("xb") as stream:
                stream.write(data)
            self.error("RESTART_REAL_AUTHORIZATION_REQUIRED",
                lambda: entry.execute(args[0], args[1], other, e.sha(data)))

    def test_09_file_entry_stage_dispatch_and_single_verification(self):
        args = self.fixture()
        # Only the subprocess and numerical comparator are replaced. Loading,
        # authorization, output consumption and publication use the real entry.
        calls = []
        proof = dict(status="RECORDING_COMPLETE", evaluation_allowed=True)
        with patch.object(entry, "launch", side_effect=lambda *x: calls.append(x[-2])), \
             patch.object(p, "verify_comparison", return_value=proof) as verify, \
             patch.object(entry, "evaluate", return_value={}) as evaluate:
            entry.main(["run", *map(str, args)])
            self.assertEqual(calls, list(entry.STAGES))
            verify.assert_called_once()
            evaluate.assert_called_once()
            self.error("REAL_OUTPUT_USED", lambda: entry.execute(*args))
        self.assertFalse(c.MAIN_GATE)
        self.assertFalse(c.QUALIFIED)

    def test_10_hash_read_counted_before_decode_even_on_error(self):
        path = self.root/"neutral-bytes.bin"
        raw = bytes(range(16))
        with path.open("xb") as stream:
            stream.write(raw)
        for sha in (e.sha(raw), "0"*64):
            with self.subTest(correct=sha == e.sha(raw)):
                work = w.Work(len(raw))
                counters = dict(container_read_bytes=0)
                source = NS(path=str(path), size=len(raw), sha256=sha)
                if sha == e.sha(raw):
                    handle = w.CountedFile(source, counters, work)
                    handle.close()
                else:
                    self.error("RESTART_SOURCE_HASH", lambda: w.CountedFile(source, counters, work))
                self.assertEqual(work.totals()["container_read_bytes"], len(raw))
                self.assertEqual(counters["container_read_bytes"], len(raw))

    def test_11_stage_entry_reaches_both_guards_and_resets_gate(self):
        self.store.publish(self.store.root/"run.claim", dict(manifest=self.manifest.manifest_digest))
        seen = []
        validate = a.validate
        def observe(*args):
            seen.append(args[1])
            return validate(*args)
        with patch.object(a, "validate", side_effect=observe), \
             patch.object(c.media, "NativeRuntime", side_effect=w.RestartError("AFTER_ADMISSION")):
            self.error("REAL_STAGE_FAILED", lambda: entry.stage({}, self.manifest,
                self.admission, self.store.root, self.store, "reference"))
        self.assertEqual(seen, [a.REAL, a.REAL])
        self.assertFalse(c.MAIN_GATE)
        self.assertFalse(c.QUALIFIED)

    def test_12_failure_prevents_verify_and_preserves_full_diagnostic(self):
        # Independent administrative store; no success fixture dependency.
        args = self.fixture()
        data, manifest, admission, _, external = entry.load(*args)
        output = self.root/"entry-failure"
        with patch.object(entry, "load", return_value=(data, manifest, admission, output, external)), \
             patch.object(entry, "launch", side_effect=w.RestartError("BOUND_TEST_ERROR", {"actual": 17})), \
             patch.object(p, "verify_comparison") as verify:
            self.error("BOUND_TEST_ERROR", lambda: entry.execute(*args))
            verify.assert_not_called()
        store = e.Store(output, external, future=self.future)
        failure = store.read(output/"failure.json")
        self.assertEqual(failure["details"], {"actual": 17})
        self.assertEqual(failure["phase"], "reference")
        self.assertFalse(c.MAIN_GATE)


if __name__ == "__main__":
    unittest.main()
