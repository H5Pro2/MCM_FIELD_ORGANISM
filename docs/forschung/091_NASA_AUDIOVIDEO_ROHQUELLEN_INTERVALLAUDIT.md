# NASA-Audio-Video-Rohquellen: Intervallaudit

## Auftrag und Grenze

Nach dem positiven Quellen- und Decoder-Gate der NASA-Testwelt wurde nur die
gemeinsame PTS-Zeitachse der erzeugten Audio- und Videorohquellen auditiert.

Es wurde kein Rezeptor gespeist, kein gemeinsames MCM-Feld ausgefuehrt, keine
Feldrueckschreibung vorgenommen und keine Memory-, Bedeutungs-, Organisations-
oder KI-Aussage ergaenzt.

## Ausfuehrung

```powershell
.\.venv\Scripts\python.exe tools\audit_public_av_intervals.py `
  "sources\media\NASA Earthrise Realtime Apollo 8.mp4" `
  --duration-seconds 0.5
```

Der Audit decodiert die auditierte Datei zweimal ueber den neutralen
Containeradapter und vergleicht nur Intervall- und Formdaten. Rohsamples und
Pixel werden nicht im Artefakt gespeichert.

## Ergebnis

```text
clock_id:                    public.media.pts_ns
ticks_per_second:            1000000000.0
duration_limit_ticks:        500000000
shared_clock:                true
common_axis_overlap_ticks:   500000000
repeatable:                  true
accepted_for_receptor_run:   false
field_run_allowed:           false
metadata_used_by_receptor:   false
raw_payload_retained:        false
```

Audio:

```text
modality_id:        auditory
frame_count:        50
first_start_tick:   0
last_end_tick:      500000000
monotonic:          true
non_overlapping:    true
gap_count:          0
max_gap_ticks:      0
bounded_to_limit:   true
interval_digest:    432b31fc3af3f836859e85400129a2f4f1fc35172b508fb0b1eaf184e7e587ef
repeat_digest:      432b31fc3af3f836859e85400129a2f4f1fc35172b508fb0b1eaf184e7e587ef
```

Video:

```text
modality_id:        visual
frame_count:        15
first_start_tick:   0
last_end_tick:      500000000
monotonic:          true
non_overlapping:    true
gap_count:          0
max_gap_ticks:      0
bounded_to_limit:   true
interval_digest:    b724ae692537ae7d294ca278ea0ab4f5bdc6a735b65cfa866175541bff8e0ad0
repeat_digest:      b724ae692537ae7d294ca278ea0ab4f5bdc6a735b65cfa866175541bff8e0ad0
```

## Entscheidung

Der observerseitige Intervallaudit ist positiv: Audio- und Videorohquellen
teilen dieselbe PTS-Uhr, sind monoton, nicht ueberlappend, lueckenfrei innerhalb
der geprueften Rohquellenfolge, auf die 0,5-Sekunden-Grenze begrenzt und bei
erneuter Decodierung exakt reproduzierbar.

Dieser Befund gibt noch keinen Rezeptorlauf frei. Ein spaeterer begrenzter
Rezeptorlauf muesste separat vorregistriert und gegen bestehende
Einzelmodalitaets- und Zeitteilungsbaselines geprueft werden.

## Technische Umsetzung

Neu erstellt:

- `mcm_field_organism/public_av_interval_audit.py`
- `tools/audit_public_av_intervals.py`
- `tests/test_public_av_interval_audit.py`

## Verifikation

```text
18 passed in 14.39s
git diff --check: kein Befund
```

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `mcm_field_organism/public_av_container_source.py`;
- `mcm_field_organism/public_media_source_contract.py`;
- `docs/forschung/090_AUDITIERTE_NASA_AUDIOVIDEO_ROHQUELLEN.md`;
- lokale Datei `sources/media/NASA Earthrise Realtime Apollo 8.mp4`;
- vorhandene Quellen-, Preflight- und Adaptertests.

Eine Zielabweichung ist nicht erkennbar.
