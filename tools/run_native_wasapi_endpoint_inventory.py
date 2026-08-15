from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from run_native_wasapi_capture_probe import (
    CLSCTX_ALL,
    CLSID_MMDEVICE_ENUMERATOR,
    COINIT_MULTITHREADED,
    DEVICE_STATE_ACTIVE,
    E_CAPTURE,
    GUID,
    IID_IAUDIOCLIENT,
    IID_IMMDEVICE_ENUMERATOR,
    IID_IMMENDPOINT,
    PKEY_DEVICE_FRIENDLY_NAME,
    PROPVARIANT,
    ProbeContractError,
    STGM_READ,
    VT_LPWSTR,
    WAVEFORMATEX,
    _check_hresult,
    _com_method,
    _release,
)


SOUNDDEVICE_INDEX = 5
ROLE_NAMES = ("console", "multimedia", "communications")
RPC_E_CHANGED_MODE = -2147417850


@dataclass(frozen=True, slots=True)
class NativeEndpointInventoryRow:
    endpoint_id: str
    display_name: str
    data_flow: str
    device_state: int
    default_roles: tuple[str, ...]
    mix_format_channels: int
    mix_format_sample_rate_hz: int
    mix_format_bits_per_sample: int


@dataclass(frozen=True, slots=True)
class SoundDeviceInventoryRow:
    index: int
    name: str
    hostapi_index: int
    hostapi_name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float
    default_low_input_latency: float
    default_high_input_latency: float


def sounddevice_inventory_row(sd, index: int = SOUNDDEVICE_INDEX) -> SoundDeviceInventoryRow:
    device = dict(sd.query_devices(index))
    hostapi_index = int(device["hostapi"])
    hostapi = dict(sd.query_hostapis(hostapi_index))
    return SoundDeviceInventoryRow(
        index=index,
        name=str(device["name"]),
        hostapi_index=hostapi_index,
        hostapi_name=str(hostapi["name"]),
        max_input_channels=int(device["max_input_channels"]),
        max_output_channels=int(device["max_output_channels"]),
        default_samplerate=float(device["default_samplerate"]),
        default_low_input_latency=float(device["default_low_input_latency"]),
        default_high_input_latency=float(device["default_high_input_latency"]),
    )


class NativeEndpointInventory:
    def __init__(self) -> None:
        self._ole32 = None
        self._enumerator = ctypes.c_void_p()
        self._com_initialized = False

    def _device_id(self, device: ctypes.c_void_p) -> str:
        value = wintypes.LPWSTR()
        _check_hresult(
            _com_method(
                device, 5, wintypes.HRESULT, ctypes.POINTER(wintypes.LPWSTR)
            )(device, ctypes.byref(value)),
            "IMMDevice::GetId",
        )
        try:
            if not value.value:
                raise ProbeContractError("active capture endpoint has no endpoint ID")
            return str(value.value)
        finally:
            if value:
                self._ole32.CoTaskMemFree(ctypes.cast(value, ctypes.c_void_p))

    def _friendly_name(self, device: ctypes.c_void_p) -> str:
        store = ctypes.c_void_p()
        _check_hresult(
            _com_method(
                device,
                4,
                wintypes.HRESULT,
                wintypes.DWORD,
                ctypes.POINTER(ctypes.c_void_p),
            )(device, STGM_READ, ctypes.byref(store)),
            "IMMDevice::OpenPropertyStore",
        )
        value = PROPVARIANT()
        try:
            _check_hresult(
                _com_method(
                    store,
                    5,
                    wintypes.HRESULT,
                    ctypes.POINTER(type(PKEY_DEVICE_FRIENDLY_NAME)),
                    ctypes.POINTER(PROPVARIANT),
                )(
                    store,
                    ctypes.byref(PKEY_DEVICE_FRIENDLY_NAME),
                    ctypes.byref(value),
                ),
                "IPropertyStore::GetValue(PKEY_Device_FriendlyName)",
            )
            if value.vt != VT_LPWSTR or not value.pwszVal:
                raise ProbeContractError("active capture endpoint has no friendly name")
            return str(value.pwszVal)
        finally:
            self._ole32.PropVariantClear(ctypes.byref(value))
            _release(store)

    def _capture_state(self, device: ctypes.c_void_p) -> int:
        endpoint = ctypes.c_void_p()
        _check_hresult(
            _com_method(
                device,
                0,
                wintypes.HRESULT,
                ctypes.POINTER(GUID),
                ctypes.POINTER(ctypes.c_void_p),
            )(device, ctypes.byref(IID_IMMENDPOINT), ctypes.byref(endpoint)),
            "IMMDevice::QueryInterface(IMMEndpoint)",
        )
        try:
            flow = ctypes.c_int()
            _check_hresult(
                _com_method(
                    endpoint, 3, wintypes.HRESULT, ctypes.POINTER(ctypes.c_int)
                )(endpoint, ctypes.byref(flow)),
                "IMMEndpoint::GetDataFlow",
            )
            if flow.value != E_CAPTURE:
                raise ProbeContractError("enumerated endpoint is not capture data flow")
        finally:
            _release(endpoint)
        state = wintypes.DWORD()
        _check_hresult(
            _com_method(
                device, 6, wintypes.HRESULT, ctypes.POINTER(wintypes.DWORD)
            )(device, ctypes.byref(state)),
            "IMMDevice::GetState",
        )
        if state.value != DEVICE_STATE_ACTIVE:
            raise ProbeContractError("enumerated capture endpoint is not active")
        return int(state.value)

    def _mix_format(self, device: ctypes.c_void_p) -> tuple[int, int, int]:
        audio_client = ctypes.c_void_p()
        _check_hresult(
            _com_method(
                device,
                3,
                wintypes.HRESULT,
                ctypes.POINTER(GUID),
                wintypes.DWORD,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_void_p),
            )(
                device,
                ctypes.byref(IID_IAUDIOCLIENT),
                CLSCTX_ALL,
                None,
                ctypes.byref(audio_client),
            ),
            "IMMDevice::Activate(IAudioClient) for metadata",
        )
        mix_format = ctypes.POINTER(WAVEFORMATEX)()
        try:
            _check_hresult(
                _com_method(
                    audio_client,
                    8,
                    wintypes.HRESULT,
                    ctypes.POINTER(ctypes.POINTER(WAVEFORMATEX)),
                )(audio_client, ctypes.byref(mix_format)),
                "IAudioClient::GetMixFormat",
            )
            return (
                int(mix_format.contents.nChannels),
                int(mix_format.contents.nSamplesPerSec),
                int(mix_format.contents.wBitsPerSample),
            )
        finally:
            if mix_format:
                self._ole32.CoTaskMemFree(ctypes.cast(mix_format, ctypes.c_void_p))
            _release(audio_client)

    def _default_ids(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for role, role_name in enumerate(ROLE_NAMES):
            device = ctypes.c_void_p()
            call_result = _com_method(
                self._enumerator,
                4,
                wintypes.HRESULT,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_void_p),
            )(
                self._enumerator,
                E_CAPTURE,
                role,
                ctypes.byref(device),
            )
            if not (int(call_result) & 0x80000000):
                try:
                    result[role_name] = self._device_id(device)
                finally:
                    _release(device)
        return result

    def collect(self) -> tuple[NativeEndpointInventoryRow, ...]:
        if sys.platform != "win32":
            raise ProbeContractError("native WASAPI inventory requires Windows")
        self._ole32 = ctypes.OleDLL("ole32")
        try:
            _check_hresult(
                self._ole32.CoInitializeEx(None, COINIT_MULTITHREADED),
                "CoInitializeEx",
            )
            self._com_initialized = True
        except OSError as exc:
            if exc.winerror != RPC_E_CHANGED_MODE:
                raise
        collection = ctypes.c_void_p()
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
                    3,
                    wintypes.HRESULT,
                    ctypes.c_int,
                    wintypes.DWORD,
                    ctypes.POINTER(ctypes.c_void_p),
                )(
                    self._enumerator,
                    E_CAPTURE,
                    DEVICE_STATE_ACTIVE,
                    ctypes.byref(collection),
                ),
                "IMMDeviceEnumerator::EnumAudioEndpoints",
            )
            default_ids = self._default_ids()
            count = wintypes.UINT()
            _check_hresult(
                _com_method(
                    collection,
                    3,
                    wintypes.HRESULT,
                    ctypes.POINTER(wintypes.UINT),
                )(collection, ctypes.byref(count)),
                "IMMDeviceCollection::GetCount",
            )
            rows: list[NativeEndpointInventoryRow] = []
            for index in range(count.value):
                device = ctypes.c_void_p()
                _check_hresult(
                    _com_method(
                        collection,
                        4,
                        wintypes.HRESULT,
                        wintypes.UINT,
                        ctypes.POINTER(ctypes.c_void_p),
                    )(collection, index, ctypes.byref(device)),
                    "IMMDeviceCollection::Item",
                )
                try:
                    endpoint_id = self._device_id(device)
                    channels, rate, bits = self._mix_format(device)
                    rows.append(
                        NativeEndpointInventoryRow(
                            endpoint_id=endpoint_id,
                            display_name=self._friendly_name(device),
                            data_flow="capture",
                            device_state=self._capture_state(device),
                            default_roles=tuple(
                                role
                                for role in ROLE_NAMES
                                if default_ids.get(role) == endpoint_id
                            ),
                            mix_format_channels=channels,
                            mix_format_sample_rate_hz=rate,
                            mix_format_bits_per_sample=bits,
                        )
                    )
                finally:
                    _release(device)
            return tuple(rows)
        finally:
            _release(collection)
            _release(self._enumerator)
            self._enumerator = ctypes.c_void_p()
            if self._com_initialized:
                self._ole32.CoUninitialize()
                self._com_initialized = False


def inventory_document(
    native_rows: tuple[NativeEndpointInventoryRow, ...],
    sounddevice_row: SoundDeviceInventoryRow,
    *,
    run_number: int = 120,
    review_mapping: bool = False,
) -> dict[str, object]:
    mapping = mapping_review(native_rows, sounddevice_row) if review_mapping else None
    return {
        "run_number": run_number,
        "native_active_capture_endpoints": [asdict(row) for row in native_rows],
        "sounddevice_comparison_device": asdict(sounddevice_row),
        "mapping_decision": (
            mapping["decision"]
            if mapping is not None
            else "UNDECIDED_REQUIRES_EXPLICIT_REVIEW"
        ),
        "mapping_review": mapping,
        "automatic_endpoint_selection_performed": False,
        "audio_client_initialize_called": False,
        "stream_start_called": False,
        "packet_capture_performed": False,
        "support_mapping_applied": False,
        "field_advance_performed": False,
    }


def mapping_review(
    native_rows: tuple[NativeEndpointInventoryRow, ...],
    sounddevice_row: SoundDeviceInventoryRow,
) -> dict[str, object]:
    candidates = tuple(
        row
        for row in native_rows
        if row.display_name == sounddevice_row.name
        and row.mix_format_channels == sounddevice_row.max_input_channels
    )
    evidence = {
        "required_exact_display_name": sounddevice_row.name,
        "required_input_channels": sounddevice_row.max_input_channels,
        "matching_endpoint_ids": [row.endpoint_id for row in candidates],
        "candidate_count": len(candidates),
        "api_identity_proven": False,
    }
    if len(candidates) == 1:
        return {
            "decision": "LOCALLY_UNIQUE_METADATA_MATCH_NOT_API_IDENTITY",
            "mapped_endpoint_id": candidates[0].endpoint_id,
            "reason": "exact display name and input-channel match is unique in the active capture inventory",
            "evidence": evidence,
        }
    reason = (
        "no active capture endpoint matches exact display name and input channels"
        if not candidates
        else "multiple active capture endpoints match exact display name and input channels"
    )
    return {
        "decision": "NOT_UNIQUELY_MAPPABLE",
        "mapped_endpoint_id": None,
        "reason": reason,
        "evidence": evidence,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventory active native capture endpoints without opening a stream."
    )
    parser.add_argument("--run-number", type=int, default=120)
    parser.add_argument("--review-mapping", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    import sounddevice as sd

    args = parse_args([] if argv is None else argv)
    native_rows = NativeEndpointInventory().collect()
    document = inventory_document(
        native_rows,
        sounddevice_inventory_row(sd),
        run_number=args.run_number,
        review_mapping=args.review_mapping,
    )
    print(json.dumps(document, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
