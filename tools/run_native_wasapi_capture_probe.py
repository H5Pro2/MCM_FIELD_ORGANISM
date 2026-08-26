from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from dataclasses import asdict, dataclass
import json
import sys
import time
from typing import Protocol
import uuid


SAMPLE_RATE = 48_000
CHANNEL_COUNT = 1
BITS_PER_SAMPLE = 32
PACKET_LIMIT = 100
TIMEOUT_SECONDS = 10.0

AUDCLNT_SHAREMODE_SHARED = 0
AUDCLNT_S_BUFFER_EMPTY = 0x08890001
AUDCLNT_BUFFERFLAGS_DATA_DISCONTINUITY = 0x1
AUDCLNT_BUFFERFLAGS_SILENT = 0x2
AUDCLNT_BUFFERFLAGS_TIMESTAMP_ERROR = 0x4
COINIT_MULTITHREADED = 0
CLSCTX_ALL = 23
DEVICE_STATE_ACTIVE = 1
E_CAPTURE = 1
STGM_READ = 0
VT_LPWSTR = 31
WAVE_FORMAT_IEEE_FLOAT = 3


class ProbeContractError(RuntimeError):
    pass


class ProbeRunError(ProbeContractError):
    def __init__(self, message: str, packets: tuple["NativePacket", ...]) -> None:
        super().__init__(message)
        self.packets = packets


@dataclass(frozen=True, slots=True)
class NativePacket:
    packet_index: int
    frame_count: int
    device_position: int
    qpc_position_100ns: int
    flags: int
    get_buffer_hresult: int
    release_buffer_hresult: int


@dataclass(frozen=True, slots=True)
class EndpointMetadata:
    endpoint_id: str
    display_name: str
    data_flow: str
    device_state: int


class CaptureBackend(Protocol):
    endpoint: EndpointMetadata

    def open(self) -> None: ...

    def next_packet(self) -> NativePacket | None: ...

    def close(self) -> None: ...


def _hresult_code(value: int) -> int:
    return int(value) & 0xFFFFFFFF


def _hresult_failed(value: int) -> bool:
    return bool(_hresult_code(value) & 0x80000000)


def validate_packet_sequence(
    packets: tuple[NativePacket, ...], *, expected_count: int = PACKET_LIMIT
) -> None:
    if len(packets) != expected_count:
        raise ProbeContractError(
            f"expected {expected_count} non-empty packets, received {len(packets)}"
        )
    previous: NativePacket | None = None
    for expected_index, packet in enumerate(packets):
        integer_values = (
            packet.packet_index,
            packet.frame_count,
            packet.device_position,
            packet.qpc_position_100ns,
            packet.flags,
        )
        if any(type(value) is not int or value < 0 for value in integer_values):
            raise ProbeContractError("packet fields must be non-negative integers")
        if packet.packet_index != expected_index:
            raise ProbeContractError("packet indexes must be contiguous from zero")
        if packet.frame_count == 0:
            raise ProbeContractError("non-empty packet has zero frames")
        if _hresult_failed(packet.get_buffer_hresult):
            raise ProbeContractError("GetBuffer returned a failure HRESULT")
        if _hresult_failed(packet.release_buffer_hresult):
            raise ProbeContractError("ReleaseBuffer returned a failure HRESULT")
        if packet.flags & AUDCLNT_BUFFERFLAGS_DATA_DISCONTINUITY:
            raise ProbeContractError("DATA_DISCONTINUITY flag observed")
        if packet.flags & AUDCLNT_BUFFERFLAGS_TIMESTAMP_ERROR:
            raise ProbeContractError("TIMESTAMP_ERROR flag observed")
        if previous is not None:
            if packet.device_position <= previous.device_position:
                raise ProbeContractError("device position is not strictly monotonic")
            expected_position = previous.device_position + previous.frame_count
            if packet.device_position != expected_position:
                raise ProbeContractError("device position is not packet-contiguous")
            if packet.qpc_position_100ns <= previous.qpc_position_100ns:
                raise ProbeContractError("QPC position is not strictly monotonic")
        previous = packet


def capture_packets(
    backend: CaptureBackend,
    *,
    clock=time.monotonic,
    sleep=time.sleep,
) -> tuple[NativePacket, ...]:
    packets: list[NativePacket] = []
    start = clock()
    failure: ProbeContractError | None = None
    try:
        backend.open()
        while len(packets) < PACKET_LIMIT:
            if clock() - start >= TIMEOUT_SECONDS:
                raise ProbeContractError(
                    "100 non-empty packets were not received within 10 seconds"
                )
            packet = backend.next_packet()
            if packet is None:
                sleep(0.001)
                continue
            packets.append(packet)
            validate_packet_sequence(tuple(packets), expected_count=len(packets))
    except ProbeContractError as error:
        failure = error
    finally:
        try:
            backend.close()
        except ProbeContractError as error:
            if failure is None:
                failure = error
    if failure is not None:
        raise ProbeRunError(str(failure), tuple(packets)) from failure
    return tuple(packets)


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    @classmethod
    def from_text(cls, value: str) -> "GUID":
        raw = uuid.UUID(value).bytes_le
        result = cls()
        ctypes.memmove(ctypes.byref(result), raw, 16)
        return result


class PROPERTYKEY(ctypes.Structure):
    _fields_ = [("fmtid", GUID), ("pid", wintypes.DWORD)]


class PROPVARIANT_UNION(ctypes.Union):
    _fields_ = [("pwszVal", wintypes.LPWSTR), ("uhVal", ctypes.c_ulonglong)]


class PROPVARIANT(ctypes.Structure):
    _anonymous_ = ("value",)
    _fields_ = [
        ("vt", wintypes.USHORT),
        ("reserved1", wintypes.USHORT),
        ("reserved2", wintypes.USHORT),
        ("reserved3", wintypes.USHORT),
        ("value", PROPVARIANT_UNION),
    ]


class WAVEFORMATEX(ctypes.Structure):
    _fields_ = [
        ("wFormatTag", wintypes.WORD),
        ("nChannels", wintypes.WORD),
        ("nSamplesPerSec", wintypes.DWORD),
        ("nAvgBytesPerSec", wintypes.DWORD),
        ("nBlockAlign", wintypes.WORD),
        ("wBitsPerSample", wintypes.WORD),
        ("cbSize", wintypes.WORD),
    ]


CLSID_MMDEVICE_ENUMERATOR = GUID.from_text(
    "bcde0395-e52f-467c-8e3d-c4579291692e"
)
IID_IMMDEVICE_ENUMERATOR = GUID.from_text(
    "a95664d2-9614-4f35-a746-de8db63617e6"
)
IID_IMMENDPOINT = GUID.from_text("1be09788-6894-4089-8586-9a2a6c265ac5")
IID_IAUDIOCLIENT = GUID.from_text("1cb9ad4c-dbfa-4c32-b178-c2f568a703b2")
IID_IAUDIOCAPTURECLIENT = GUID.from_text(
    "c8adbd64-e71e-48a0-a4de-185c395cd317"
)
PKEY_DEVICE_FRIENDLY_NAME = PROPERTYKEY(
    GUID.from_text("a45c254e-df1c-4efd-8020-67d146a850e0"), 14
)


def _com_method(
    interface: ctypes.c_void_p,
    index: int,
    restype,
    *argtypes,
):
    vtable = ctypes.cast(
        interface, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
    ).contents
    prototype = ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)
    return prototype(vtable[index])


def _check_hresult(value: int, role: str) -> int:
    code = _hresult_code(value)
    if _hresult_failed(value):
        raise ProbeContractError(f"{role} failed with HRESULT 0x{code:08X}")
    return code


def _release(interface: ctypes.c_void_p | None) -> None:
    if interface and interface.value:
        _com_method(interface, 2, wintypes.ULONG)(interface)


class NativeWasapiBackend:
    def __init__(self, endpoint_id: str) -> None:
        if not endpoint_id or endpoint_id != endpoint_id.strip():
            raise ProbeContractError("a complete explicit endpoint ID is required")
        self._endpoint_id = endpoint_id
        self.endpoint = EndpointMetadata(endpoint_id, "", "", 0)
        self._ole32 = None
        self._enumerator = ctypes.c_void_p()
        self._device = ctypes.c_void_p()
        self._audio_client = ctypes.c_void_p()
        self._capture_client = ctypes.c_void_p()
        self._com_initialized = False
        self._started = False
        self._packet_index = 0

    def _read_endpoint_metadata(self) -> EndpointMetadata:
        returned_id = wintypes.LPWSTR()
        _check_hresult(
            _com_method(
                self._device,
                5,
                wintypes.HRESULT,
                ctypes.POINTER(wintypes.LPWSTR),
            )(self._device, ctypes.byref(returned_id)),
            "IMMDevice::GetId",
        )
        try:
            if not returned_id.value or returned_id.value != self._endpoint_id:
                raise ProbeContractError(
                    "endpoint returned an ID different from the explicit endpoint ID"
                )
        finally:
            if returned_id:
                self._ole32.CoTaskMemFree(ctypes.cast(returned_id, ctypes.c_void_p))

        endpoint = ctypes.c_void_p()
        _check_hresult(
            _com_method(
                self._device,
                0,
                wintypes.HRESULT,
                ctypes.POINTER(GUID),
                ctypes.POINTER(ctypes.c_void_p),
            )(self._device, ctypes.byref(IID_IMMENDPOINT), ctypes.byref(endpoint)),
            "IMMDevice::QueryInterface(IMMEndpoint)",
        )
        try:
            data_flow = ctypes.c_int()
            _check_hresult(
                _com_method(
                    endpoint, 3, wintypes.HRESULT, ctypes.POINTER(ctypes.c_int)
                )(endpoint, ctypes.byref(data_flow)),
                "IMMEndpoint::GetDataFlow",
            )
            if data_flow.value != E_CAPTURE:
                raise ProbeContractError("explicit endpoint is not a capture endpoint")
        finally:
            _release(endpoint)

        state = wintypes.DWORD()
        _check_hresult(
            _com_method(
                self._device, 6, wintypes.HRESULT, ctypes.POINTER(wintypes.DWORD)
            )(self._device, ctypes.byref(state)),
            "IMMDevice::GetState",
        )
        if state.value != DEVICE_STATE_ACTIVE:
            raise ProbeContractError("explicit endpoint is not active")

        store = ctypes.c_void_p()
        _check_hresult(
            _com_method(
                self._device,
                4,
                wintypes.HRESULT,
                wintypes.DWORD,
                ctypes.POINTER(ctypes.c_void_p),
            )(self._device, STGM_READ, ctypes.byref(store)),
            "IMMDevice::OpenPropertyStore",
        )
        value = PROPVARIANT()
        try:
            _check_hresult(
                _com_method(
                    store,
                    5,
                    wintypes.HRESULT,
                    ctypes.POINTER(PROPERTYKEY),
                    ctypes.POINTER(PROPVARIANT),
                )(
                    store,
                    ctypes.byref(PKEY_DEVICE_FRIENDLY_NAME),
                    ctypes.byref(value),
                ),
                "IPropertyStore::GetValue(PKEY_Device_FriendlyName)",
            )
            if value.vt != VT_LPWSTR or not value.pwszVal:
                raise ProbeContractError("endpoint friendly name is unavailable")
            display_name = str(value.pwszVal)
        finally:
            self._ole32.PropVariantClear(ctypes.byref(value))
            _release(store)
        return EndpointMetadata(
            endpoint_id=self._endpoint_id,
            display_name=display_name,
            data_flow="capture",
            device_state=int(state.value),
        )

    def open(self) -> None:
        if sys.platform != "win32":
            raise ProbeContractError("native WASAPI probe requires Windows")
        self._ole32 = ctypes.OleDLL("ole32")
        _check_hresult(
            self._ole32.CoInitializeEx(None, COINIT_MULTITHREADED),
            "CoInitializeEx",
        )
        self._com_initialized = True
        try:
            _check_hresult(
                self._ole32.CoCreateInstance(
                    ctypes.byref(CLSID_MMDEVICE_ENUMERATOR),
                    None,
                    CLSCTX_ALL,
                    ctypes.byref(IID_IMMDEVICE_ENUMERATOR),
                    ctypes.byref(self._enumerator),
                ),
                "CoCreateInstance(MMDeviceEnumerator)",
            )
            _check_hresult(
                _com_method(
                    self._enumerator,
                    5,
                    wintypes.HRESULT,
                    wintypes.LPCWSTR,
                    ctypes.POINTER(ctypes.c_void_p),
                )(
                    self._enumerator,
                    self._endpoint_id,
                    ctypes.byref(self._device),
                ),
                "IMMDeviceEnumerator::GetDevice",
            )
            self.endpoint = self._read_endpoint_metadata()
            _check_hresult(
                _com_method(
                    self._device,
                    3,
                    wintypes.HRESULT,
                    ctypes.POINTER(GUID),
                    wintypes.DWORD,
                    ctypes.c_void_p,
                    ctypes.POINTER(ctypes.c_void_p),
                )(
                    self._device,
                    ctypes.byref(IID_IAUDIOCLIENT),
                    CLSCTX_ALL,
                    None,
                    ctypes.byref(self._audio_client),
                ),
                "IMMDevice::Activate(IAudioClient)",
            )
            block_align = CHANNEL_COUNT * (BITS_PER_SAMPLE // 8)
            wave_format = WAVEFORMATEX(
                WAVE_FORMAT_IEEE_FLOAT,
                CHANNEL_COUNT,
                SAMPLE_RATE,
                SAMPLE_RATE * block_align,
                block_align,
                BITS_PER_SAMPLE,
                0,
            )
            closest = ctypes.c_void_p()
            format_result = _com_method(
                self._audio_client,
                7,
                wintypes.HRESULT,
                ctypes.c_int,
                ctypes.POINTER(WAVEFORMATEX),
                ctypes.POINTER(ctypes.c_void_p),
            )(
                self._audio_client,
                AUDCLNT_SHAREMODE_SHARED,
                ctypes.byref(wave_format),
                ctypes.byref(closest),
            )
            if closest.value:
                self._ole32.CoTaskMemFree(closest)
            if _hresult_code(format_result) != 0:
                raise ProbeContractError(
                    "exact 48-kHz mono float32 shared format is unsupported"
                )
            _check_hresult(
                _com_method(
                    self._audio_client,
                    3,
                    wintypes.HRESULT,
                    ctypes.c_int,
                    wintypes.DWORD,
                    ctypes.c_longlong,
                    ctypes.c_longlong,
                    ctypes.POINTER(WAVEFORMATEX),
                    ctypes.POINTER(GUID),
                )(
                    self._audio_client,
                    AUDCLNT_SHAREMODE_SHARED,
                    0,
                    0,
                    0,
                    ctypes.byref(wave_format),
                    None,
                ),
                "IAudioClient::Initialize",
            )
            _check_hresult(
                _com_method(
                    self._audio_client,
                    14,
                    wintypes.HRESULT,
                    ctypes.POINTER(GUID),
                    ctypes.POINTER(ctypes.c_void_p),
                )(
                    self._audio_client,
                    ctypes.byref(IID_IAUDIOCAPTURECLIENT),
                    ctypes.byref(self._capture_client),
                ),
                "IAudioClient::GetService(IAudioCaptureClient)",
            )
            _check_hresult(
                _com_method(self._audio_client, 10, wintypes.HRESULT)(
                    self._audio_client
                ),
                "IAudioClient::Start",
            )
            self._started = True
        except BaseException:
            self.close()
            raise

    def next_packet(self) -> NativePacket | None:
        next_size = wintypes.UINT()
        _check_hresult(
            _com_method(
                self._capture_client,
                5,
                wintypes.HRESULT,
                ctypes.POINTER(wintypes.UINT),
            )(self._capture_client, ctypes.byref(next_size)),
            "IAudioCaptureClient::GetNextPacketSize",
        )
        if next_size.value == 0:
            return None

        data = ctypes.POINTER(ctypes.c_ubyte)()
        frames = wintypes.UINT()
        flags = wintypes.DWORD()
        device_position = ctypes.c_ulonglong()
        qpc_position = ctypes.c_ulonglong()
        get_result = _com_method(
            self._capture_client,
            3,
            wintypes.HRESULT,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)),
            ctypes.POINTER(wintypes.UINT),
            ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong),
        )(
            self._capture_client,
            ctypes.byref(data),
            ctypes.byref(frames),
            ctypes.byref(flags),
            ctypes.byref(device_position),
            ctypes.byref(qpc_position),
        )
        _check_hresult(get_result, "IAudioCaptureClient::GetBuffer")
        release_result = _com_method(
            self._capture_client, 4, wintypes.HRESULT, wintypes.UINT
        )(self._capture_client, frames.value)
        packet = NativePacket(
            packet_index=self._packet_index,
            frame_count=int(frames.value),
            device_position=int(device_position.value),
            qpc_position_100ns=int(qpc_position.value),
            flags=int(flags.value),
            get_buffer_hresult=_hresult_code(get_result),
            release_buffer_hresult=_hresult_code(release_result),
        )
        self._packet_index += 1
        return packet

    def close(self) -> None:
        stop_failure: ProbeContractError | None = None
        if self._started and self._audio_client.value:
            stop_result = _com_method(self._audio_client, 11, wintypes.HRESULT)(
                self._audio_client
            )
            if _hresult_failed(stop_result):
                stop_failure = ProbeContractError(
                    "IAudioClient::Stop failed with HRESULT "
                    f"0x{_hresult_code(stop_result):08X}"
                )
            self._started = False
        _release(self._capture_client)
        _release(self._audio_client)
        _release(self._device)
        _release(self._enumerator)
        self._capture_client = ctypes.c_void_p()
        self._audio_client = ctypes.c_void_p()
        self._device = ctypes.c_void_p()
        self._enumerator = ctypes.c_void_p()
        if self._com_initialized:
            self._ole32.CoUninitialize()
            self._com_initialized = False
        if stop_failure is not None:
            raise stop_failure


def result_document(
    *,
    endpoint: EndpointMetadata,
    packets: tuple[NativePacket, ...],
    decision: str,
    end_reason: str,
) -> dict[str, object]:
    return {
        "run_number": 119,
        "decision": decision,
        "end_reason": end_reason,
        "endpoint": asdict(endpoint),
        "requested_format": {
            "sample_rate_hz": SAMPLE_RATE,
            "channels": CHANNEL_COUNT,
            "sample_format": "float32",
            "share_mode": "shared",
            "loopback": False,
            "format_conversion": False,
        },
        "packet_limit": PACKET_LIMIT,
        "timeout_seconds": TIMEOUT_SECONDS,
        "packets": [asdict(packet) for packet in packets],
        "audio_payload_retained": False,
        "support_mapping_applied": False,
        "field_advance_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture raw native WASAPI packet-position metadata."
    )
    parser.add_argument("--endpoint-id", required=True)
    args = parser.parse_args()
    backend = NativeWasapiBackend(args.endpoint_id)
    packets: tuple[NativePacket, ...] = ()
    try:
        packets = capture_packets(backend)
        validate_packet_sequence(packets)
        document = result_document(
            endpoint=backend.endpoint,
            packets=packets,
            decision="PAKETPOSITION_KANDIDAT",
            end_reason="packet_limit_reached",
        )
        exit_code = 0
    except ProbeRunError as error:
        packets = error.packets
        document = result_document(
            endpoint=backend.endpoint,
            packets=packets,
            decision="TECHNISCH_NEGATIV",
            end_reason=str(error),
        )
        exit_code = 1
    except ProbeContractError as error:
        document = result_document(
            endpoint=backend.endpoint,
            packets=packets,
            decision="TECHNISCH_NEGATIV",
            end_reason=str(error),
        )
        exit_code = 1
    print(json.dumps(document, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
