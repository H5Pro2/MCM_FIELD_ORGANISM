"""Private OS-limited decoder; one bounded output slot, no system state."""
import ctypes as ct
from ctypes import wintypes as wt
import json
import mmap
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
import traceback
import uuid

VERSION = "s2oe.decoder-job.v2-phase-diagnostic"
COMMIT_BYTES = 512 * 1024 * 1024
PCM_BYTES = 4800 * 4
RGB_BYTES = 1080 * 1920 * 3
SLOT_BYTES = PCM_BYTES + RGB_BYTES
MESSAGE_BYTES = 4096
REQUEST_SECONDS = 30.0
STOP_SECONDS = 5.0
ISOLATION_VERSION = "s2oe.decoder-isolation.v1"


def arm_limit(arm):
    require(arm is None or arm in ("COMMIT_512", "COMMIT_1024"), "DECODER_ARM_INVALID")
    return 1073741824 if arm == "COMMIT_1024" else COMMIT_BYTES


def resource_profile():
    return dict(version=VERSION, process_commit_bytes=COMMIT_BYTES,
        job_commit_bytes=COMMIT_BYTES, slot_bytes=SLOT_BYTES, queue_capacity=1,
        message_bytes=MESSAGE_BYTES, request_seconds=REQUEST_SECONDS,
        stop_seconds=STOP_SECONDS, active_processes=1)


class WorkerError(ValueError):
    def __init__(self, code, detail=None):
        self.code, self.balance = code, detail
        super().__init__(code)


def require(condition, code):
    if not condition:
        raise WorkerError(code)


def need(condition, code):
    require(condition, code)


def moment(pts, time_base):
    from fractions import Fraction
    require(type(pts) is int and pts >= 0 and type(time_base) is tuple
        and len(time_base) == 2 and all(type(x) is int and x > 0 for x in time_base), "PTS_INVALID")
    return pts * Fraction(*time_base)


class BasicLimits(ct.Structure):
    _fields_ = [("process_time", ct.c_longlong), ("job_time", ct.c_longlong),
        ("flags", wt.DWORD), ("min_working_set", ct.c_size_t),
        ("max_working_set", ct.c_size_t), ("active_processes", wt.DWORD),
        ("affinity", ct.c_size_t), ("priority", wt.DWORD), ("scheduling", wt.DWORD)]


class IoCounters(ct.Structure):
    _fields_ = [(name, ct.c_ulonglong) for name in
        ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]


class ExtendedLimits(ct.Structure):
    _fields_ = [("basic", BasicLimits), ("io", IoCounters),
        ("process_memory", ct.c_size_t), ("job_memory", ct.c_size_t),
        ("peak_process", ct.c_size_t), ("peak_job", ct.c_size_t)]


class CompletionPort(ct.Structure):
    _fields_ = [("key", ct.c_void_p), ("port", wt.HANDLE)]


class DecoderJob:
    """Cap committed process/job memory, not RSS or the parent process."""
    def __init__(self, diagnostic_arm=None):
        commit_limit = arm_limit(diagnostic_arm)
        require(os.name == "nt", "DECODER_OS_UNSUPPORTED")
        self.api = ct.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([ct.c_void_p, wt.LPCWSTR], wt.HANDLE),
            "SetInformationJobObject": ([wt.HANDLE, ct.c_int, ct.c_void_p, wt.DWORD], wt.BOOL),
            "QueryInformationJobObject": ([wt.HANDLE, ct.c_int, ct.c_void_p, wt.DWORD, ct.c_void_p], wt.BOOL),
            "OpenProcess": ([wt.DWORD, wt.BOOL, wt.DWORD], wt.HANDLE),
            "AssignProcessToJobObject": ([wt.HANDLE, wt.HANDLE], wt.BOOL),
            "IsProcessInJob": ([wt.HANDLE, wt.HANDLE, ct.POINTER(wt.BOOL)], wt.BOOL),
            "TerminateJobObject": ([wt.HANDLE, wt.UINT], wt.BOOL),
            "CloseHandle": ([wt.HANDLE], wt.BOOL),
            "CreateIoCompletionPort": ([wt.HANDLE, wt.HANDLE, ct.c_size_t, wt.DWORD], wt.HANDLE),
            "GetQueuedCompletionStatus": ([wt.HANDLE, ct.POINTER(wt.DWORD),
                ct.POINTER(ct.c_size_t), ct.POINTER(ct.c_void_p), wt.DWORD], wt.BOOL),
        }
        for name, (args, result) in signatures.items():
            function = getattr(self.api, name)
            function.argtypes, function.restype = args, result
        self.name = "Local\\MCMDecoderJob-" + uuid.uuid4().hex
        self.handle = self.api.CreateJobObjectW(None, self.name)
        self.port = None
        self.memory_limit_hit = False
        self.limit_messages = set()
        try:
            require(bool(self.handle), "DECODER_JOB_CREATE_FAILED")
            limit = ExtendedLimits()
            limit.basic.flags = 0x100 | 0x200 | 0x2000 | 0x8
            limit.basic.active_processes = 1
            limit.process_memory = limit.job_memory = commit_limit
            self._set(9, limit)
            self.port = self.api.CreateIoCompletionPort(wt.HANDLE(-1), None, 0, 1)
            require(bool(self.port), "DECODER_JOB_PORT_FAILED")
            self._set(7, CompletionPort(1, self.port))
            actual = self.snapshot()
            require(actual["flags"] == limit.basic.flags
                and actual["process_commit_limit"] == commit_limit
                and actual["job_commit_limit"] == commit_limit
                and actual["active_process_limit"] == 1, "DECODER_JOB_LIMIT_NOT_ACTIVE")
        except BaseException:
            self.close()
            raise

    def _set(self, kind, data):
        require(bool(self.api.SetInformationJobObject(self.handle, kind,
            ct.byref(data), ct.sizeof(data))), "DECODER_JOB_CONFIG_FAILED")

    def attach(self, pid):
        process = self.api.OpenProcess(0x100 | 0x1 | 0x1000 | 0x400, False, pid)
        require(bool(process), "DECODER_PROCESS_HANDLE_FAILED")
        try:
            require(bool(self.api.AssignProcessToJobObject(self.handle, process)),
                "DECODER_JOB_ASSIGN_FAILED")
            active = wt.BOOL()
            require(bool(self.api.IsProcessInJob(process, self.handle, ct.byref(active)))
                and active.value, "DECODER_JOB_MEMBERSHIP_FAILED")
        finally:
            self.api.CloseHandle(process)

    def snapshot(self):
        data = ExtendedLimits()
        require(bool(self.api.QueryInformationJobObject(self.handle, 9,
            ct.byref(data), ct.sizeof(data), None)), "DECODER_JOB_QUERY_FAILED")
        if self.port:
            # Bounded diagnostic draining; allocation denial does not depend on this queue.
            for _ in range(64):
                message, key, pointer = wt.DWORD(), ct.c_size_t(), ct.c_void_p()
                if not self.api.GetQueuedCompletionStatus(self.port, ct.byref(message),
                        ct.byref(key), ct.byref(pointer), 0):
                    break
                self.memory_limit_hit |= message.value in (9, 10)
                if message.value in (9, 10):
                    self.limit_messages.add(message.value)
        return dict(flags=data.basic.flags, active_process_limit=data.basic.active_processes,
            process_commit_limit=data.process_memory, job_commit_limit=data.job_memory,
            peak_process_commit=data.peak_process, peak_job_commit=data.peak_job,
            memory_limit_notification=self.memory_limit_hit,
            memory_limit_messages=sorted(self.limit_messages))

    def terminate(self):
        require(bool(self.api.TerminateJobObject(self.handle, 1)), "DECODER_JOB_TERMINATE_FAILED")

    def close(self):
        for name in ("handle", "port"):
            handle = getattr(self, name, None)
            if handle:
                self.api.CloseHandle(handle)
                setattr(self, name, None)


def encode(message):
    data = json.dumps(message, allow_nan=False, separators=(",", ":")).encode("utf-8")
    require(len(data) <= MESSAGE_BYTES, "DECODER_MESSAGE_LIMIT")
    return data + b"\n"


def read_message(stream):
    data = stream.readline(MESSAGE_BYTES + 2)
    require(data.endswith(b"\n") and len(data) <= MESSAGE_BYTES + 1,
        "DECODER_MESSAGE_INVALID")
    value = json.loads(data)
    require(type(value) is dict, "DECODER_MESSAGE_INVALID")
    return value


def confirm_worker_job(name, diagnostic_arm=None):
    commit_limit = arm_limit(diagnostic_arm)
    require(os.name == "nt" and type(name) is str and name.startswith("Local\\MCMDecoderJob-"),
        "DECODER_JOB_BINDING_INVALID")
    api = ct.WinDLL("kernel32", use_last_error=True)
    api.OpenJobObjectW.argtypes, api.OpenJobObjectW.restype = [wt.DWORD, wt.BOOL, wt.LPCWSTR], wt.HANDLE
    api.GetCurrentProcess.restype = wt.HANDLE
    api.IsProcessInJob.argtypes = [wt.HANDLE, wt.HANDLE, ct.POINTER(wt.BOOL)]
    api.QueryInformationJobObject.argtypes = [wt.HANDLE, ct.c_int, ct.c_void_p, wt.DWORD, ct.c_void_p]
    api.CloseHandle.argtypes = [wt.HANDLE]
    job = api.OpenJobObjectW(4, False, name)
    require(bool(job), "DECODER_JOB_OPEN_FAILED")
    try:
        member, limit = wt.BOOL(), ExtendedLimits()
        require(bool(api.IsProcessInJob(api.GetCurrentProcess(), job, ct.byref(member)))
            and member.value, "DECODER_JOB_MEMBERSHIP_FAILED")
        require(bool(api.QueryInformationJobObject(job, 9, ct.byref(limit), ct.sizeof(limit), None)),
            "DECODER_JOB_QUERY_FAILED")
        require(limit.basic.flags == 0x2308 and limit.basic.active_processes == 1
            and limit.process_memory == commit_limit and limit.job_memory == commit_limit,
            "DECODER_JOB_LIMIT_NOT_ACTIVE")
    finally:
        api.CloseHandle(job)


class WorkerDecoder:
    """One outstanding selection and one fixed-size shared output slot."""
    def __init__(self, source, *, diagnostic_arm=None, mode=None):
        require(mode in (None, "s2oe.full-file-sampled.v1"), "DECODER_MODE_INVALID")
        self.mode = mode
        arm_limit(diagnostic_arm)
        from dataclasses import asdict
        self.counters = dict(container_read_bytes=0, packets=0, video_frames=0,
            audio_frames=0, audio_samples=0, selected_windows=0, passes=0)
        self.resources = dict(version=VERSION, slot_bytes=SLOT_BYTES, queue_capacity=1,
            request_seconds=REQUEST_SECONDS, read_counters_complete=True)
        self._request_lock = threading.Lock()
        self._call_lock = threading.Lock()
        self._cancelled = threading.Event()
        self._job_lock = threading.Lock()
        self.closed = False
        self.process = self.slot = self.job = None
        self._responses = queue.Queue(maxsize=1)
        self._sequence = 0
        self.last_confirmed_phase = None
        self.native_logs = []
        self.native_log_bytes = 0
        self.native_log_overflow = False
        try:
            self.job = DecoderJob(diagnostic_arm)
            name = "Local\\MCMDecoder-" + uuid.uuid4().hex
            self.slot = mmap.mmap(-1, SLOT_BYTES, tagname=name, access=mmap.ACCESS_WRITE)
            self.process = self._launch([sys.executable, str(Path(__file__).resolve()), "--worker"],
                cwd=str(Path(__file__).resolve().parents[1]), stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0,
                creationflags=subprocess.CREATE_NO_WINDOW)
            # Child waits on stdin. No source or import command is sent before assignment.
            self.job.attach(self.process.pid)
            self._reader = threading.Thread(target=self._read, daemon=True)
            self._reader.start()
            self._rpc(dict(op="init", source=asdict(source), slot=name,
                job=self.job.name, version=VERSION, diagnostic_arm=diagnostic_arm,
                **({} if mode is None else dict(mode=mode))))
            self.resources["job_confirmed_before_media"] = True
            if diagnostic_arm:
                self.resources.update(isolation_version=ISOLATION_VERSION, diagnostic_arm=diagnostic_arm)
        except BaseException:
            self.close()
            raise

    @staticmethod
    def _launch(*args, **kwargs):
        return subprocess.Popen(*args, **kwargs)

    def _read(self):
        try:
            while not self._cancelled.is_set():
                value = read_message(self.process.stdout)
                if value.get("kind") == "native_log":
                    require(value.get("sequence") == self._sequence, "DECODER_LOG_BINDING_INVALID")
                    size = len(encode(value))
                    if len(self.native_logs) >= 32 or self.native_log_bytes + size > 32768:
                        self.native_log_overflow = True
                    else:
                        self.native_logs.append(value)
                        self.native_log_bytes += size
                    continue
                if value.get("kind") == "phase":
                    require(value.get("sequence") == self._sequence
                        and set(value) == {"kind", "sequence", "phase", "operation"}
                        and all(type(value[k]) is str and len(value[k]) <= 64
                            for k in ("phase", "operation")), "DECODER_PHASE_INVALID")
                    self.last_confirmed_phase = value
                    continue
                self._responses.put_nowait(value)
        except BaseException:
            try:
                self._responses.put_nowait(dict(error="DECODER_CHANNEL_CLOSED"))
            except queue.Full:
                pass

    def _request_deadline(self):
        return time.monotonic() + REQUEST_SECONDS

    def _prepare_select(self, repeat, window):
        pass

    def _rpc(self, message):
        require(self._request_lock.acquire(blocking=False), "DECODER_BUSY")
        try:
            require(not self.closed and not self._cancelled.is_set(), "DECODER_CANCELLED")
            self._sequence += 1
            message["sequence"] = self._sequence
            command = encode(message)
            require(len(command) <= 2048, "DECODER_COMMAND_LIMIT")
            self.process.stdin.write(command)
            self.process.stdin.flush()
            deadline = self._request_deadline()
            while True:
                if self._cancelled.is_set():
                    raise WorkerError("DECODER_CANCELLED")
                try:
                    result = self._responses.get(timeout=min(0.05, max(0.001, deadline-time.monotonic())))
                    break
                except queue.Empty:
                    if time.monotonic() >= deadline:
                        self.cancel()
                        raise WorkerError("DECODER_TIMEOUT")
            require(not self._cancelled.is_set(), "DECODER_CANCELLED")
            with self._job_lock:
                self.resources.update(self.job.snapshot())
            if result.get("error") == "DECODER_CHANNEL_CLOSED":
                code = "DECODER_MEMORY_LIMIT" if self.resources["memory_limit_notification"] else "DECODER_WORKER_EXIT"
                self.resources.update(last_confirmed_phase=self.last_confirmed_phase,
                    original_worker_error=None, exact_failure_location_known=False,
                    process_exit_before_cancel=self.process.poll())
                raise WorkerError(code, self.resources.copy())
            require(result.get("sequence") == self._sequence, "DECODER_RESPONSE_BINDING_INVALID")
            if "decoder_versions" in result:
                self.resources["decoder_versions"] = result["decoder_versions"]
            if "restart_work" in result:
                self.resources["restart_work"] = result["restart_work"]
            if "counters" in result:
                require(set(result["counters"]) == set(self.counters)
                    and all(type(v) is int and v >= self.counters[k]
                        for k, v in result["counters"].items()), "DECODER_COUNTER_INVALID")
                self.counters = dict(result["counters"])
            with self._job_lock:
                self.resources.update(self.job.snapshot())
            if result.get("error"):
                code = "DECODER_MEMORY_LIMIT" if self.resources["memory_limit_notification"] else result["error"]
                self.resources.update(last_confirmed_phase=self.last_confirmed_phase,
                    original_worker_error={k: result.get(k) for k in
                        ("error", "exception_type", "exception_module", "errno", "traceback", "native_exception")},
                    exact_failure_location_known=False,
                    process_exit_before_cancel=self.process.poll())
                raise WorkerError(code, self.resources.copy())
            require(not self.native_log_overflow, "DECODER_NATIVE_LOG_LIMIT")
            return result
        except BaseException as exc:
            self.resources["read_counters_complete"] = False
            self.resources["last_confirmed_phase"] = self.last_confirmed_phase
            try:
                self.cancel()
            except Exception:
                self.resources["cancel_errors"] = 1
            if isinstance(exc, (OSError, ValueError)) and not isinstance(exc, WorkerError):
                raise WorkerError("DECODER_CHANNEL_FAILED", self.resources.copy()) from exc
            raise
        finally:
            self._request_lock.release()

    def select(self, repeat, window):
        import numpy as np
        require(self._call_lock.acquire(blocking=False), "DECODER_BUSY")
        try:
            self._prepare_select(repeat, window)
            result = self._rpc(dict(op="select", repeat=repeat, window=window))
            require(result.get("repeat") == repeat and result.get("window") == window,
                "DECODER_SELECTION_BINDING_INVALID")
            pcm = np.frombuffer(self.slot, dtype="<f4", count=4800).copy()
            rgb = np.frombuffer(self.slot, dtype=np.uint8, count=RGB_BYTES,
                offset=PCM_BYTES).reshape(1080, 1920, 3).copy()
            pcm.flags.writeable = rgb.flags.writeable = False
            return pcm, rgb, result["pts"], result["next_pts"]
        finally:
            self._call_lock.release()

    def release(self):
        require(self._call_lock.acquire(blocking=False), "DECODER_BUSY")
        try:
            self._rpc(dict(op="release"))
        finally:
            self._call_lock.release()

    def drain(self):
        require(self.mode == "s2oe.full-file-sampled.v1", "DRAIN_MODE_INVALID")
        require(self._call_lock.acquire(blocking=False), "DECODER_BUSY")
        try:
            result = self._rpc(dict(op="drain"))
            ends = result.get("stream_ends")
            require(type(ends) is dict and set(ends) == {"video_eof", "audio_eof",
                "last_video_pts", "audio_end_sample", "selected_windows"}
                and ends["video_eof"] is True and ends["audio_eof"] is True
                and ends["selected_windows"] == 20, "STREAM_ENDS_INVALID")
            self.resources["stream_ends"] = ends
            return dict(ends)
        finally:
            self._call_lock.release()

    def cancel(self):
        self._cancelled.set()
        with self._job_lock:
            if self.job and self.process and self.process.poll() is None:
                self.resources.update(self.job.snapshot())
                self.job.terminate()

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            self.cancel()
            if self.process:
                # Assignment can fail before the waiting child becomes a job member.
                if self.process.poll() is None:
                    self.process.kill()
                self.process.wait(timeout=STOP_SECONDS)
                self.resources["worker_exit_code"] = self.process.returncode
                self.resources["worker_closed"] = True
                self.resources.update(native_logs=self.native_logs,
                    native_log_bytes=self.native_log_bytes, native_log_overflow=self.native_log_overflow)
        finally:
            if self.process:
                for stream in (self.process.stdin, self.process.stdout):
                    if stream:
                        stream.close()
            if self.slot:
                self.slot.close()
            with self._job_lock:
                if self.job:
                    self.job.close()


def worker_main(decoder_factory=None, evidence_factory=None, operation_handler=None):
    decoder = slot = None
    sequence = 0
    def phase(name, operation):
        sys.stdout.buffer.write(encode(dict(kind="phase", sequence=sequence,
            phase=name, operation=operation)))
        sys.stdout.buffer.flush()
    try:
        initial = read_message(sys.stdin.buffer)
        sequence = initial["sequence"]
        require(initial.get("op") == "init" and initial.get("version") == VERSION,
            "DECODER_INIT_INVALID")
        # Independently confirm job membership before importing PyAV or opening media.
        diagnostic_arm = initial.get("diagnostic_arm")
        confirm_worker_job(initial.get("job"), diagnostic_arm)
        phase("INITIALIZE", "import_decoder")
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from types import SimpleNamespace
        if decoder_factory is None:
            from tools._s2oe_media_decoder import Decoder
            decoder_factory = Decoder
        source = initial["source"]
        for key in ("video_time_base", "audio_time_base", "frame_rate", "video_size"):
            source[key] = tuple(source[key])
        slot = mmap.mmap(-1, SLOT_BYTES, tagname=initial["slot"], access=mmap.ACCESS_WRITE)
        phase("INITIALIZE", "construct_decoder")
        mode = initial.get("mode")
        require(mode in (None, "s2oe.full-file-sampled.v1"), "DECODER_MODE_INVALID")
        decoder = (decoder_factory(SimpleNamespace(**source)) if mode is None else
                   decoder_factory(SimpleNamespace(**source), mode=mode))
        decoder.progress = phase
        versions = None
        if diagnostic_arm:
            from tools._s2oe_isolation_log import install
            def send_log(value):
                value.update(kind="native_log", sequence=sequence)
                sys.stdout.buffer.write(encode(value))
                sys.stdout.buffer.flush()
            install(decoder.av, send_log)
            versions = dict(pyav=decoder.av.__version__,
                ffmpeg=decoder.av.ffmpeg_version_info, libraries=decoder.av.library_versions)
        sys.stdout.buffer.write(encode(dict(sequence=sequence, counters=decoder.counters,
            decoder_versions=versions, **({} if evidence_factory is None else evidence_factory(decoder)))))
        sys.stdout.buffer.flush()
        while True:
            message = read_message(sys.stdin.buffer)
            require(message.get("sequence") == sequence + 1, "DECODER_COMMAND_ORDER_INVALID")
            sequence += 1
            response = dict(sequence=sequence)
            extra = None if operation_handler is None else operation_handler(decoder, message)
            if extra is not None:
                response.update(extra)
            elif message.get("op") == "select":
                pcm, rgb, pts, next_pts = decoder.select(message["repeat"], message["window"])
                require(pcm.nbytes == PCM_BYTES and rgb.nbytes == RGB_BYTES, "DECODER_SLOT_SHAPE_INVALID")
                phase("OUTPUT", "write_shared_slot")
                slot.seek(0)
                slot.write(memoryview(pcm).cast("B"))
                slot.write(memoryview(rgb).cast("B"))
                response.update(repeat=message["repeat"], window=message["window"], pts=pts, next_pts=next_pts)
                del pcm, rgb
            elif message.get("op") == "video_point":
                require(callable(getattr(decoder, "video_point", None)), "VIDEO_DIAGNOSTIC_UNAVAILABLE")
                rgb, evidence = decoder.video_point(message["window"], message["frame_budget"])
                require(rgb.nbytes == RGB_BYTES and len(encode(evidence)) <= 4096,
                    "VIDEO_DIAGNOSTIC_SIZE_INVALID")
                slot.seek(PCM_BYTES)
                slot.write(memoryview(rgb).cast("B"))
                response.update(video=evidence)
                del rgb
            elif message.get("op") == "release":
                decoder.release()
            elif message.get("op") == "drain":
                require(mode == "s2oe.full-file-sampled.v1", "DRAIN_MODE_INVALID")
                response["stream_ends"] = decoder.drain()
            else:
                raise WorkerError("DECODER_COMMAND_INVALID")
            response["counters"] = dict(decoder.counters)
            if evidence_factory is not None:
                response.update(evidence_factory(decoder))
            sys.stdout.buffer.write(encode(response))
            sys.stdout.buffer.flush()
    except BaseException as exc:
        code = "DECODER_MEMORY_ALLOCATION_FAILED" if isinstance(exc, MemoryError) else getattr(exc, "code", "DECODER_WORKER_FAILED")
        try:
            response = dict(sequence=sequence, error=code, exception_type=type(exc).__name__,
                exception_module=type(exc).__module__,
                errno=getattr(exc, "errno", None),
                traceback=[dict(file=Path(f.filename).name, line=f.lineno, function=f.name)
                    for f in traceback.extract_tb(exc.__traceback__)[-6:]])
            if type(exc).__module__ == "av.error":
                response["native_exception"] = dict(strerror=getattr(exc, "strerror", None))
            if decoder:
                response["counters"] = dict(decoder.counters)
                if evidence_factory is not None:
                    response.update(evidence_factory(decoder))
            sys.stdout.buffer.write(encode(response))
            sys.stdout.buffer.flush()
        except BaseException:
            pass
    finally:
        if decoder:
            decoder.close()
        if slot:
            slot.close()


if __name__ == "__main__":
    require(sys.argv[1:] == ["--worker"], "DECODER_ENTRY_INVALID")
    worker_main()
