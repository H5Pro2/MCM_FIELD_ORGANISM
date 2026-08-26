# Symmetrischer Audio-Video-Quellzeitvertrag

## Auftrag und Grenze

Nach dem Quellen- und Schnittstellenaudit aus Forschung 086 wurde nur die
allgemeine Zeitgrenze des vorhandenen Audio-Video-Capturepfads geschlossen.
Es wurde kein Medien-, Rezeptor- oder Feldlauf ausgefuehrt und keine neue
Feld-, Memory-, Bedeutungs- oder Organisationsrolle eingefuehrt.

## Ausgangsluecke

Zeitgestempelte Audioquellen konnten bereits ihr tatsaechliches
Captureintervall ueber `read_timed_frame()` liefern. Videoquellen wurden
dagegen immer mit der Zeit vor und nach dem Decoderaufruf versehen. Bei einer
gemeinsamen Containerdatei waere diese Decoderlaufzeit nicht mit dem
Medienzeitstrahl gleichzusetzen.

## Umsetzung

`capture_timed_audio_video_receptor_sequences()` akzeptiert fuer Video nun
optional denselben allgemeinen Quellzeitvertrag wie fuer Audio:

```text
read_timed_frame() -> (frame, start_tick, end_tick)
capture_clock_id
capture_ticks_per_second
```

Die Quelle muss dieselbe benannte Organismusuhr und `1_000_000_000` Ticks pro
Sekunde verwenden. Eine abweichende Uhr wird vor der Rezeptorreduktion
abgewiesen. Quellen ohne `read_timed_frame()` verwenden unveraendert die
bisherige gemessene Lesezeit; bestehende Kamera- und synthetische Quellen
bleiben damit kompatibel.

Der Vertrag uebernimmt nur Zeitintervall und Pixelbild. Containername,
Beschreibung, Lizenz, Untertitel, Labels und andere Metadaten erreichen weder
Rezeptor noch Feld.

## Verifikation

Geprueft wurden:

- unveraenderte Audio-Zeituebernahme;
- neue Video-Zeituebernahme unabhaengig von Decoderlaufzeit;
- Ablehnung einer abweichenden Videoquellenuhr;
- alle direkt betroffenen Audio-Video-Runtime-Tests.

```text
23 passed in 0.88s
git diff --check: kein inhaltlicher Befund
```

## Verbleibende technische Grenzen

Die Originaldatei
`sources/media/Brokindsleden - The sounds of traffic.webm` liegt weiterhin
nicht lokal vor. Der direkte Bezug ueber PowerShell und curl scheiterte am
lokalen Windows-TLS-Transport. Der Browser bestaetigte den exakten
Commons-Originaldateilink, darf den Wikimedia-Uploadhost aufgrund einer
bestehenden Browserregel jedoch nicht fuer den Dateibezug verwenden. Diese
Regel wurde nicht umgangen.

Lokal sind OpenCV, aber weder FFmpeg, PyAV noch SoundFile verfuegbar. OpenCV
kann den VP9-Bildpfad pruefen, stellt hier aber keinen neutralen Opus-
Audioquellenadapter bereit. Deshalb wurde kein unvollstaendiger Adapter als
audiovisueller Containervertrag ausgegeben.

## Entscheidung

Der symmetrische allgemeine Quellzeitvertrag ist technisch hergestellt. Ein
oeffentlicher Audio-Video-Feldlauf bleibt geschlossen.

Der naechste zulaessige technische Schritt ist ein neutraler
Container-Decoderadapter erst dann, wenn beide Voraussetzungen vorliegen:

1. die lokale Originaldatei besteht Groessen- und SHA-1-Audit;
2. ein lokaler VP9/Opus-faehiger Decoder ist verfuegbar und kann Audio- und
   Videointervalle aus demselben Containerzeitstrahl liefern.

Der Adapter darf nur Rohsamples, Pixel und ihre Intervalle an die bestehenden
Quellenprotokolle geben. Ein positiver Adaptertest wuerde noch keinen Feldlauf
und keine Memory-Auswertung freigeben.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `docs/forschung/086_OEFFENTLICHE_AUDIOVISUELLE_TESTWELT_QUELLENAUDIT.md`;
- `mcm_field_organism/receptor_time_alignment.py`;
- `mcm_field_organism/audio_video_neutral_field_runtime.py`;
- `mcm_field_organism/live_audio_adapter.py`;
- `mcm_field_organism/finite_video_path.py`;
- `tests/test_receptor_time_alignment.py`;
- Wikimedia-Commons-Dateiseite und dort ausgewiesener Originaldateilink.

Eine Zielabweichung ist nicht erkennbar.
