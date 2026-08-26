# NASA-Audio-Video-Rezeptorlauf ohne Feldanschluss

## Zweck

Dieser Schritt prueft einmalig, ob die auditierte oeffentliche NASA-Audio-Video-Quelle
fuer einen stark begrenzten Rezeptorlauf ohne Feldanschluss reduziert werden kann.

Der Lauf darf nur reduzierte auditive und visuelle Rezeptorzustaende mit ihren
Zeitintervallen ausgeben. Rohsamples, Pixel, Containerdaten und Metadaten duerfen
nicht im Ergebnis erscheinen. Feldverarbeitung bleibt gesperrt.

## Quelle

- source_id: `public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20`
- lokale Datei: `sources/media/NASA Earthrise Realtime Apollo 8.mp4`
- erwartete Groesse: `13547755` Byte
- erwarteter SHA-1: `c63198a925ad227950cca597c4a8500656bacdfc`

Die Quelle wurde nur nach positivem Integritaetsaudit geoeffnet.

## Rezeptorvertrag

```text
Audio:
  Rezeptor: LogSpectralReceptor ueber BroadbandHearingPath
  Samplerate: 48000 Hz
  Container-Hop: 480 Samples
  Rezeptorfenster: 0,1 s

Video:
  Rezeptor: LocalChannelGridReceptor
  Eingang: uint8 BGR, 320 x 240 x 3
  Raster: 10 x 8

Gemeinsame Uhr:
  public.media.pts_ns

Begrenzung:
  0,5 s
```

## Befund

```text
duration_limit_ticks:      500000000
auditory_frames:           41
visual_frames:             15
repeatable:                true
raw_payload_retained:      false
metadata_used_by_receptor: false
field_run_allowed:         false
```

Die reduzierten Sequenzen waren wiederholbar:

```text
auditory_sequence_digest:
501476111cdd3d17e9b5249b3774dc7918c8ffb8123264c16ce775ba5f6a175f

visual_sequence_digest:
86e9d1a2b1c01959f52d2446f855078dc313341f638bc8e23f43fcf79ea48d93
```

Die ausgegebenen Einzelereignisse enthalten nur:

- Modalitaetskennung;
- Geometriekennung;
- Sequenzindex;
- Start- und Endtick;
- Digest des reduzierten Rezeptorzustands.

Sie enthalten keine Rohsamples, keine Pixel, keine Containerdaten und keine
Metadaten.

## Grenze

Dieser Lauf ist kein Feldlauf. Er speist kein gemeinsames MCM-Feld, schreibt keine
Feldzustande zurueck und erzeugt keine Memory-Auswertung.

Der Befund belegt ausschliesslich, dass eine auditierte oeffentliche Audio-Video-
Quelle fuer 0,5 s reproduzierbar in reduzierte auditive und visuelle
Rezeptorzustaende auf derselben PTS-Zeitachse zerlegt werden kann.

Er belegt weder Bedeutung noch innere Organisation, Memory oder eigenstaendige KI.

## Naechster begrenzter Schritt

Vor einem Feldanschluss ist separat zu pruefen, ob ein streng begrenzter passiver
gemeinsamer Verlaufslauf gegen die vorhandenen Einzelmodalitaets- und
Zeitteilungsbaselines vorregistriert werden darf.

Eine solche Freigabe ist in diesem Dokument nicht enthalten.
