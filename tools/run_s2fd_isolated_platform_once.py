"""Private child entrypoints; no command-line observer or execution grant.

Only the separately admitted outer observer creates the first child. No
package paths, environment switch or public field API are accepted here.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys


def _parent_pipe():
    import ctypes
    from ctypes import wintypes
    import msvcrt
    from mcm_field_organism._s2fd_start_contract import require
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetFileType.argtypes, kernel.GetFileType.restype = (wintypes.HANDLE,), wintypes.DWORD
    kernel.GetNamedPipeServerProcessId.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.ULONG))
    kernel.GetNamedPipeServerProcessId.restype = wintypes.BOOL
    handle = msvcrt.get_osfhandle(0)
    require(kernel.GetFileType(handle) == 3, "parent pipe required", "BLOCKED_PREREQUISITE")
    pid = wintypes.ULONG()
    require(kernel.GetNamedPipeServerProcessId(handle, ctypes.byref(pid)) and pid.value == os.getppid(),
            "original parent pipe origin not confirmed", "BLOCKED_PREREQUISITE")


def _read_bootstrap():
    from mcm_field_organism._s2fd_start_contract import loads, require

    def exact(size):
        parts, count = [], 0
        for _ in range(size):
            part = os.read(0, min(65536, size - count))
            require(bool(part), "bootstrap pipe closed")
            parts.append(part)
            count += len(part)
            if count == size:
                return b"".join(parts)
        raise ValueError("incomplete bootstrap")

    # The real parent owns the child and its startup deadline. Until this
    # length-delimited handoff is complete, no ledger/recorder operation runs.
    count = int.from_bytes(exact(8), "big")
    require(count > 0, "empty bootstrap")
    return loads(exact(count)), count + 8


def _open_child_gate(binding):
    from mcm_field_organism import _s2ex_recorder_native as native
    from mcm_field_organism._s2fd_start_contract import require
    require(native._PLATFORM_EXECUTION_RELEASED is False and not native._REVIEWED_BINDINGS,
            "child recorder gate reused")
    native._REVIEWED_BINDINGS = frozenset((binding.identity(),))
    native._PLATFORM_EXECUTION_RELEASED = True


def _ref(path, raw):
    from mcm_field_organism._s2fd_start_contract import sha
    return {"path": path, "byte_count": len(raw), "raw_sha256": sha(raw)}


def _worker(package, handoff, channel):
    from mcm_field_organism._s2fd_start_contract import ATTEMPT, encoded, loads, require
    from mcm_field_organism._s2fd_start_owner import SourceLease, validate_handoff
    from mcm_field_organism._s2ex_recorder_binding import record
    from mcm_field_organism._s2ex_recorder_fixture import record_worker
    lease = SourceLease(package)
    try:
        validate_handoff(package, handoff, lease)
        require(channel.expect("START") == {"role": "worker"}, "worker release differs")
        binding = package.binding()
        _, _, profile, run, source, _, _, paths = binding.values()
        envelopes = package.value()["envelope_files"]
        reservation = record("s2eu.attempt-reservation.v1", attempt_id=ATTEMPT,
            profile_digest=profile["record_digest"], run_binding_digest=run["record_digest"],
            source_manifest_digest=source["record_digest"], explicit_authorization=envelopes["authorization_raw"],
            preregistration_review=envelopes["preregistration_raw"], status="RESERVED")
        lease.read_exact(_ref(paths.get(None, "platform_reservation").path, encoded(reservation)))
        _open_child_gate(binding)
        result = record_worker(binding, channel.io.write)
        lease.revalidate()
        return result
    finally:
        lease.close()


def _supervisor(package, handoff, channel):
    from dataclasses import asdict
    from mcm_field_organism._s2fd_start_contract import require
    from mcm_field_organism._s2fd_start_owner import (
        ChildOwner, ParentChannel, SourceLease, process_contract, validate_handoff, wire_package,
    )
    from mcm_field_organism._s2fd_completion_observer import NativePipeIO
    from mcm_field_organism._s2ex_recorder_supervisor import RecorderSupervisor
    lease, children, supervisor = SourceLease(package), ChildOwner(package), None
    try:
        validate_handoff(package, handoff, lease)
        require(channel.expect("START") == {"role": "supervisor"}, "supervisor release differs")
        binding = package.binding()
        _open_child_gate(binding)
        supervisor = RecorderSupervisor(binding)
        envelopes = package.value()["envelope_files"]
        supervisor.reserve(envelopes["authorization_raw"], envelopes["preregistration_raw"])
        require(supervisor.state == "RESERVED", "supervisor reservation missing")
        worker = children.spawn("worker")
        channel.send("CHILD", {"role": "worker", "source_role": "supervisor",
                               "handle": int(worker._handle), "pid": worker.pid})
        require(channel.expect("OWNED") == {"role": "worker"}, "independent worker ownership missing")
        io = NativePipeIO.for_child(worker, process_contract(package, "worker"))
        io.bootstrap(wire_package(package, handoff))
        child_channel = ParentChannel(package, "worker", io)
        child_channel.send("START", {"role": "worker"})
        # capture owns the original binary pipes and its two bounded drain
        # threads. Restore only their read mode before handing them over.
        os.set_blocking(worker.stdout.fileno(), True)
        os.set_blocking(worker.stderr.fileno(), True)
        supervisor.capture(worker)
        completion = supervisor.publish()
        require(supervisor.state == "RECORDING_PUBLICATION_COMPLETE", "publication not complete")
        published = {h.path: raw for h, raw in supervisor.published}
        paths = supervisor.paths
        manifest_path = paths.get(None, "recording_manifest").path
        marker_path = paths.get(None, "recording_marker").path
        from mcm_field_organism._s2ex_recorder_binding import ATTEMPT, record
        from mcm_field_organism._s2fd_start_contract import encoded, sha
        marker = record("s2eu.recording-marker.v1", attempt_id=ATTEMPT,
            manifest_raw_sha256=sha(published[manifest_path]), manifest_record_digest=completion.manifest_digest,
            profile_digest=supervisor.profile["record_digest"], run_binding_digest=supervisor.run["record_digest"])
        result = {"live_completion": asdict(completion), "manifest_file": _ref(manifest_path, published[manifest_path]),
                  "marker_file": _ref(marker_path, encoded(marker)),
                  "control_file": _ref(paths.get(None, "recorder.control.spool").path, b"".join(supervisor.control.parts)),
                  "pipe_closures": ["worker"]}
        lease.revalidate()
    except BaseException:
        if supervisor is not None:
            supervisor.abort()
        raise
    finally:
        try:
            children.close()
        finally:
            lease.close()
    channel.send("RESULT", result)
    return 0


def main():
    # No observer mode, --run, environment opt-in or package file argument.
    if os.name != "nt" or len(sys.argv) != 2 or sys.argv[1] not in ("starter", "supervisor", "worker"):
        return 2
    repository = str(Path(__file__).resolve().parents[1])
    sys.path.insert(0, repository)
    from mcm_field_organism._s2fd_start_contract import REPOSITORY, require
    from mcm_field_organism._s2fd_start_owner import ParentChannel, process_contract, start_once, unwire_package
    from mcm_field_organism._s2fd_completion_observer import NativePipeIO
    require(repository == REPOSITORY and sys.flags.isolated and sys.flags.dont_write_bytecode and sys.flags.no_site,
            "isolated pinned bootstrap required", "BLOCKED_PREREQUISITE")
    _parent_pipe()
    wire, consumed = _read_bootstrap()
    package, handoff = unwire_package(wire)
    role = sys.argv[1]
    plan = process_contract(package, role)
    require(consumed <= plan["maximum_ipc_bytes"], "bootstrap over budget")
    require(sys.executable == plan["interpreter_file"]["path"] and os.getcwd() == plan["cwd"], "bootstrap runtime/cwd differs")
    require(dict(os.environ) == plan["environment_allowlist"], "bootstrap environment differs")
    io = NativePipeIO(0, 1, None, plan)
    io.read_bytes = consumed
    channel = ParentChannel(package, role, io)
    if role == "starter":
        return start_once(package, handoff, channel)
    if role == "supervisor":
        return _supervisor(package, handoff, channel)
    return _worker(package, handoff, channel)


if __name__ == "__main__":
    raise SystemExit(main())
