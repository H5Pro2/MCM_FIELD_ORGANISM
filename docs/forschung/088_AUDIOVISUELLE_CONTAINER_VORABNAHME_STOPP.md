# Audiovisuelle Container-Vorabnahme: Stopp vor Adapter

## Auftrag und Grenze

Geprueft wurden nur die zwei Voraussetzungen fuer einen spaeteren neutralen
Container-zu-Quellen-Adapter:

1. lokale Originaldatei mit positivem Groessen- und SHA-1-Audit;
2. lokaler VP9/Opus-Decoder, der Audio- und Videointervalle aus demselben
   Containerzeitstrahl liefern kann.

Es wurde kein Container decodiert, kein Rezeptor gespeist, kein Feldlauf
ausgefuehrt und keine Memory-, Bedeutungs-, Organisations- oder KI-Aussage
ergaenzt.

## Technische Umsetzung

Neu erstellt:

- `mcm_field_organism/public_av_container_preflight.py`
- `tools/audit_public_av_container_preflight.py`
- `tests/test_public_av_container_preflight.py`

Der Preflight prueft observerseitig:

- Quellenintegritaet ueber den vorregistrierten Brokindsleden-Vertrag;
- lokale Verfuegbarkeit von `ffmpeg` und `ffprobe`;
- lokale Python-Verfuegbarkeit von `av`, `soundfile` und `cv2`;
- ob die Adaptervoraussetzungen vollstaendig erfuellt sind.

Der Preflight darf keine Feldlaeufe oder Metadatenfreigaben erteilen.

## Ergebnis

Ausgefuehrt wurde:

```powershell
.\.venv\Scripts\python.exe tools\audit_public_av_container_preflight.py `
  "sources\media\Brokindsleden - The sounds of traffic.webm"
```

Ergebnis:

```text
source_id:                               public.audiovisual.brokindsleden-traffic-sound.commons.2018-12-18
file_present:                            false
accepted:                                false
ffmpeg_path:                             null
ffprobe_path:                            null
opencv_available:                        true
pyav_available:                          false
soundfile_available:                     false
vp9_opus_container_decoder_available:    false
adapter_prerequisites_met:               false
adapter_implementation_allowed:          false
field_run_allowed:                       false
metadata_receptor_release_granted:       false
```

Damit sind beide Voraussetzungen nicht erfuellt. Der Adapter darf noch nicht
implementiert werden.

## Entscheidung

Der naechste technische Schritt bleibt gesperrt, bis die lokale Originaldatei
positiv auditiert wurde und ein geeigneter lokaler VP9/Opus-Decoder verfuegbar
ist. Erst danach ist ein neutraler Container-zu-Quellen-Adapter zulaessig, der
ausschliesslich Rohsamples, Pixel und ihre Intervalle an die bestehenden
`AudioFrameSource`- und `VideoFrameSource`-Protokolle liefert.

Ein Feldlauf bleibt auch nach einem spaeteren Adaptertest separat gesperrt.

## Verifikation

```text
20 passed in 1.02s
```

`git diff --check` meldete keinen Befund.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `docs/forschung/087_SYMMETRISCHER_AUDIO_VIDEO_QUELLZEITVERTRAG.md`;
- `mcm_field_organism/receptor_time_alignment.py`;
- `mcm_field_organism/public_media_source_contract.py`;
- `tools/audit_public_media_source.py`;
- lokaler Workspace-Bestand unter `sources/media`;
- lokale Decoder-/Python-Modulpruefung.

Eine Zielabweichung ist nicht erkennbar.
