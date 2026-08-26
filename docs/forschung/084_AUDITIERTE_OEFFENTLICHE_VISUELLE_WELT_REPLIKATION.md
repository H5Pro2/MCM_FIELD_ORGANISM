# Auditierte oeffentliche visuelle Welt: Replikation

## Auftrag und Grenze

Nach Freigabe der observerseitigen Quellenintegritaetskontrolle wurde die lokal
vorhandene Originalrevision von `Street traffic.webm` zuerst gegen Groesse und
SHA-1 geprueft und erst danach durch den bestehenden visuellen Medienrunner
verarbeitet.

Der Lauf prueft ausschliesslich reproduzierbaren visuellen Weltkontakt. Er
prueft keine Feldrueckschreibung, kein Memory, keine Bedeutung, keine
Organisation und keine KI-Funktion.

## Quellenaudit

```text
source_id:                public.visual.street-traffic.commons.2013-02-02
file_present:             true
observed_size_bytes:      26490572
size_matches:             true
observed_sha1:            7f916030f14d84a65aa92077339f472897915fef
sha1_matches:             true
accepted:                 true
receptor_release_granted: false
```

`accepted=true` bestaetigt nur die observerseitige Quellenidentitaet. Die
Integritaetskontrolle selbst erteilt keine Rezeptorfreigabe und decodiert keine
Medienframes.

## Ausfuehrung

```powershell
$env:PYTHONPATH='.'
.\.venv\Scripts\python.exe tools\run_public_visual_world.py `
  "sources\media\Street traffic.webm" `
  --sampling-interval-ms 125 `
  --max-duration-ms 35000
```

## Ergebnis

```text
duration_ms:                                  35000
sampling_interval_ms:                         125
sampled_frame_count:                          280
decoded_frame_count:                          1048
receptor_geometry_id:                         visual.grid8x6.channels3.source1920x1080.v1
reduced_sequence_digest:                      f147109d3ac2c411328b0a514119df8fd18abd0bded487056d4a6502bc70780f
repeated_sequence_digest:                     f147109d3ac2c411328b0a514119df8fd18abd0bded487056d4a6502bc70780f
exact_reduced_repeat:                         true
receptor_value_span_max:                      0.6645475671750183
field_activation_min:                         0.2100632279327689
field_activation_max:                         0.6460159928525693
field_afterimage_min:                         0.21409402783402193
field_afterimage_max:                         0.6345833965100298
static_baseline_activation_max_difference:    0.14294861141440907
static_baseline_afterimage_max_difference:    0.1439472231286799
audio_used:                                   false
metadata_used_by_receptor:                    false
raw_frames_retained:                          false
semantic_roles_used:                          false
```

Die lokal auditierte Quelle reproduziert den vorgegebenen reduzierten Digest
exakt. Die wiederholte Decodierung ist identisch. Die zeitliche Bildfolge
unterscheidet sich in Aktivierung und schnellem Nachhall von der statischen
Bildbaseline.

## Aussagegrenze

Getragen ist nur:

> Eine integritaetsgepruefte oeffentliche Bildfolge erreicht den bestehenden
> visuellen Rezeptor-MCM-Pfad reproduzierbar und unterscheidet sich von einer
> zeitgleichen statischen Bildbaseline.

Nicht getragen sind Memory, fortwirkende Feldbeziehung nach Angleichung,
natuerliche Organisation, Semantik, autonome Weltteilnahme oder KI.

## Naechster Pruefantrag

Vor weiterer technischer Entwicklung soll der MCM-Benutzer
entscheiden, ob als naechster begrenzter Schritt die vorhandene passive
zeitliche Verlaufskarte derselben auditierten Quelle erneut ausgefuehrt werden
darf. Dabei bleiben Quelle, 125-ms-Abtastung, 35-Sekunden-Grenze, Pixelpfad und
Feldmechanik unveraendert. Es werden keine neue Zustandsrolle und keine
Memory-Mechanik eingefuehrt.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag und Benutzerfreigabe,
- `mcm_field_organism/public_media_source_contract.py`,
- `mcm_field_organism/public_visual_world.py`,
- `tools/audit_public_media_source.py`,
- `tools/run_public_visual_world.py`,
- `sources/README.md`,
- lokale Originaldatei `sources/media/Street traffic.webm`.

Eine Zielabweichung ist nicht erkennbar.
