# Audiovisueller Decoder-Gate positiv

## Auftrag und Grenze

Nach der gestoppten Container-Vorabnahme wurde nur die unabhaengige lokale
Decoder-Voraussetzung hergestellt. Die oeffentliche Originaldatei liegt
weiterhin nicht lokal vor. Es wurde kein Container decodiert, kein Adapter
implementiert, kein Rezeptor gespeist und kein Feldlauf ausgefuehrt.

## Umsetzung

In der vorhandenen Projekt-venv wurde installiert:

```text
PyAV 16.1.0
```

Die optionale reproduzierbare Abhaengigkeit ist in
`requirements-public-av.txt` festgehalten. Sie erweitert keine Feldmechanik
und gibt keine Metadaten an den Rezeptorpfad weiter.

## Wiederholter Preflight

```text
file_present:                            false
accepted:                                false
opencv_available:                        true
pyav_available:                          true
vp9_opus_container_decoder_available:    true
adapter_prerequisites_met:               false
adapter_implementation_allowed:          false
field_run_allowed:                       false
metadata_receptor_release_granted:       false
```

Damit ist genau die Decoder-Voraussetzung positiv. Das Integritaetsgate der
Originaldatei bleibt negativ und blockiert weiterhin Adapter und Feldlauf.

## Verifikation

```text
20 passed in 1.06s
```

## Entscheidung

Der neutrale Containeradapter bleibt gesperrt. Der naechste ausfuehrbare
Schritt ist ausschliesslich die lokale Bereitstellung der vorregistrierten
Originaldatei und die erneute Groessen-/SHA-1-Pruefung. Erst wenn
`accepted=true` ist, kann der bestehende Preflight
`adapter_prerequisites_met=true` ergeben.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `docs/forschung/088_AUDIOVISUELLE_CONTAINER_VORABNAHME_STOPP.md`;
- `mcm_field_organism/public_av_container_preflight.py`;
- `tools/audit_public_av_container_preflight.py`;
- `tests/test_public_av_container_preflight.py`;
- lokaler Python-Paketindex und installiertes PyAV-Wheel 16.1.0.

Eine Zielabweichung ist nicht erkennbar.
