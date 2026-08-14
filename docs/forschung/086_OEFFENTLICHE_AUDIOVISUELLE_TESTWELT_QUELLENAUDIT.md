# Oeffentliche audiovisuelle Testwelt: Quellen- und Schnittstellenaudit

## Auftrag und Grenze

Als naechster begrenzter Schritt wurde eine oeffentliche audiovisuelle
Testwelt recherchiert und zunaechst nur observerseitig bewertet. Es wurde kein
Audio-Video-Feldlauf ausgefuehrt.

Nicht in den Rezeptorpfad gelangen:

- Dateiname, Beschreibung, Herkunftsseite, Lizenztext oder Metadaten;
- Untertitel, Labels, Objekt-, Sprach- oder Bedeutungsangaben;
- Webseitentext oder YouTube-Beschreibung.

## Quellenkandidat

Ausgewaehlt wurde:

```text
Commons-Datei: Brokindsleden - The sounds of traffic.webm
Commons-Seite: https://commons.wikimedia.org/wiki/File:Brokindsleden_-_The_sounds_of_traffic.webm
Medientyp:     WebM audio/video, VP9/Opus
Dauer:         90.147 s
Aufloesung:    1920 x 1080
Quelle:        YouTube-Import, auf Commons als Datei gefuehrt
Autor:         Sounds of Changes / Fredrik Johansson
Lizenz:        Creative Commons Attribution 3.0 Unported
Lizenzreview:  YouTubeReviewBot, 14. Februar 2020
```

Der Kandidat ist methodisch geeignet, weil Bild und Originalton in einer
zusammenhaengenden Datei vorliegen und beide Modalitaeten zeitliche Variation
enthalten. Die Datei ist lang genug, um spaeter einen kurzen, vorregistrierten
Abschnitt ohne Sonderregeln auszuschneiden.

## Vorregistrierte Integritaetswerte

Die strukturierten Commons-Daten nennen:

```text
Dateigroesse: 94052425 Byte
SHA-1:        672be38ca918858ec0973b85401a832e3fc592e1
```

Diese Werte wurden als observerseitiger Vertrag erfasst:

```text
source_id: public.audiovisual.brokindsleden-traffic-sound.commons.2018-12-18
```

## Lokales Audit

Ausgefuehrt wurde:

```powershell
.\.venv\Scripts\python.exe tools\audit_public_media_source.py `
  "sources\media\Brokindsleden - The sounds of traffic.webm" `
  --source brokindsleden-av
```

Ergebnis:

```text
file_present=false
size_matches=false
sha1_matches=false
accepted=false
receptor_release_granted=false
```

Damit liegt nur ein negativer lokaler Verfuegbarkeitsbefund vor. Die
oeffentliche Quelle wurde nicht decodiert und keinem Rezeptor uebergeben.

## Schnittstellenpruefung vor Feldlauf

Der vorhandene asynchrone Audio-Video-Pfad arbeitet bereits mit getrennten
reduzierten Quellen:

```text
AudioFrameSource -> BroadbandHearingPath
VideoFrameSource -> LocalChannelGridReceptor
capture_timed_audio_video_receptor_sequences
run_neutral_asynchronous_field
```

Fuer lokale WebM-Containerdateien existiert im aktuellen Workspace jedoch noch
kein Adapter, der dieselbe Originaldatei ohne Sonderregeln in eine
`AudioFrameSource` und eine `VideoFrameSource` zerlegt. Vor einem realen
oeffentlichen Audio-Video-Lauf ist deshalb zunaechst ein reiner
Schnittstellenvertrag noetig:

- Integritaetsaudit der lokalen Originaldatei muss positiv sein;
- Audio und Video duerfen nur als zeitliche Rohsignal-/Pixelspuren gelesen
  werden;
- Container-, Lizenz-, Beschreibungs- und Untertiteldaten bleiben
  observerseitig;
- die erzeugten Quellen muessen die bestehenden `AudioFrameSource`- und
  `VideoFrameSource`-Protokolle bedienen;
- keine Feldmechanik, keine Gewichte, keine Zustandsrolle und keine Memory-
  oder Bedeutungsvariable werden ergaenzt.

## Entscheidung

Die Quelle ist als oeffentlicher audiovisueller Kandidat akzeptierbar, aber der
eigentliche MCM-Lauf ist nicht freigegeben. Es fehlen noch:

1. lokale Originaldatei mit positivem Groessen- und SHA-1-Audit;
2. ein neutraler Container-zu-Rezeptorquellen-Adapter fuer denselben WebM-
   Bestand;
3. eine Schnittstellenpruefung, dass dieser Adapter den vorhandenen
   asynchronen Audio-Video-Pfad ohne Sonderregeln speisen kann.

Erst danach darf eine passive gemeinsame Verlaufskarte gegen die vorhandenen
Einzelmodalitaets- und Zeitteilungsbaselines vorregistriert werden.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- Wikimedia-Commons-Seite zu `Brokindsleden - The sounds of traffic.webm`;
- Wikimedia-Commons-Suchergebnis mit strukturierten Daten zu SHA-1,
  Dateigroesse, Dauer, Hoehe und Breite;
- `mcm_field_organism/public_media_source_contract.py`;
- `tools/audit_public_media_source.py`;
- `mcm_field_organism/audio_video_neutral_field_runtime.py`;
- `mcm_field_organism/receptor_time_alignment.py`;
- `mcm_field_organism/live_audio_adapter.py`;
- `mcm_field_organism/finite_video_path.py`;
- `docs/forschung/085_AUDITIERTE_PASSIVE_VISUELLE_VERLAUFSKARTE.md`.

Eine Zielabweichung ist nicht erkennbar.
