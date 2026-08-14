# W1-D: Bestandsaudit und Vertrag der kamerafreien Browser-Payloadquelle

Stand: 2026-08-07

Entscheidung: `W1D_GENERIC_CAMERA_FREE_BROWSER_SOURCE_CONTRACT_BOUND`

Forschungslauf: nein

## Auftrag

W1-D prueft den nach W1-C noch offenen Quellenrand und bindet die kleinste
allgemeine Browserquelle, die kontrollierte PNG- und PCM-Payloads unmittelbar
an `BrowserReceptorBridge` uebergibt. Der Schritt ist statisch. Es wird kein
Browser gestartet und kein alter Quellenrunner fortgesetzt.

## Bestandsbefund

### Alte allgemeine Browserwelt

`tools/controlled_browser_world/` enthaelt einen allgemeinen
`BrowserWorldContract`-gesteuerten visuellen und auditiven Ablauf. Der heutige
Ausgabepfad ist fuer W1 jedoch unzulaessig und nicht reproduzierbar genug:

- `Date.now()` und `requestAnimationFrame()` binden Bilder an Wanduhr und
  Scheduler;
- Canvasgroesse und Bewegung haengen von Fenster und Device-Pixel-Ratio ab;
- `AudioContext` erzeugt Live-Audio am Systemausgang;
- `/api/prepare` und `/api/start` fuehren zu Kamera- und
  Mikrofon-Coordinatoren;
- Vollbild, Fokus und Polling beeinflussen den Ablauf;
- es existiert keine direkte PNG-/PCM-Uebergabe an W1-C.

Dieser Bestand bleibt historisch nachvollziehbar, ist aber kein aktiver
W1-Quellenpfad.

### Geparkter Z4-Direktpfad

Der Z4-A2-Bestand zeigt statisch, dass Canvasbilder zu expliziten Zeitpunkten
und Audio ueber `OfflineAudioContext` ohne Kamera oder Mikrofon erzeugt werden
koennen. Er ist trotzdem kein zulaessiger W1-Baustein:

- Welt-IDs, Geometrie, Frequenzen und Inventare sind fest auf Z4-A2 gebunden;
- Adapter, Capture, Runtimebindung und Smokes gehoeren zur geparkten
  Z4-Ausfuehrungskette;
- seine weitere Nutzung wuerde die in S1-G und W1-A gebundene Abgrenzung
  umgehen.

W1-D uebernimmt deshalb weder Modul noch Asset noch Runner. Nur die allgemeine
technische Moeglichkeit einer direkten lokalen Canvas- und Offline-Audio-
Quelle ist als Bestandswissen relevant.

## Genau ein offener Quellenrand

```text
Es fehlt eine parametrierte lokale Browserseite mit einem allgemeinen
Capture-Handoff, die den BrowserWorldContract deterministisch als geordnete
Canvas-PNGs und Offline-PCM-Hops an BrowserReceptorBridge ausgibt.
```

Diese Quellenluecke liegt vor der fertigen W1-C-Bruecke. Sie erfordert keine
neue Rezeptor-, Verteiler-, Dock- oder Feldfunktion.

## Frischer W1-Quellenraum

Neue Assets liegen ausschliesslich unter:

```text
tools/controlled_browser_payload_world/
  index.html
  styles.css
  world.js
```

Neue Pythonrollen liegen ausschliesslich in:

```text
mcm_field_organism/browser_payload_source.py
```

Keines dieser Elemente importiert oder liest `tools/z4a_browser_world_v2`
oder ein `z4a_*`-Modul.

## Quellenkonfiguration

### `BrowserPayloadSourceConfig`

Der unveraenderliche Vertrag enthaelt nur technische Renderbedingungen:

```text
source_id
canvas_width
canvas_height
device_scale_factor             # exakt 1
visual_frames_per_second
motion_axis                     # horizontal oder vertical
motion_amplitude_fraction
foreground_size_fraction
background_rgb
foreground_rgb
audio_sample_rate
audio_hop_size
audio_channel_count             # exakt 1
oscillator_type                 # zunaechst exakt sine
```

Alle Zahlen muessen endlich, positiv und innerhalb expliziter Bild-, Farb-
und Normierungsgrenzen liegen. Die Konfiguration muss mit
`LocalChannelGridReceptor.config` und
`BroadbandHearingPath.receptor.config` der uebergebenen W1-C-Bruecke exakt
uebereinstimmen.

Der `BrowserWorldContract` bleibt getrennt und bestimmt:

- Phasenreihenfolge und Dauer;
- statische oder bewegte visuelle Phase;
- Tongain je Phase;
- Bewegungszyklen;
- Tonfrequenz.

Damit werden Weltprogramm und technische Rendergeometrie explizit gebunden,
ohne Inhalt, Objektklasse oder Bedeutung einzufuehren.

## Browserseitenvertrag

`world.js` stellt nach dem Laden genau folgende globale Funktionen bereit:

```javascript
configureWorld(worldContractPayload, sourceConfigPayload)
renderVisualFrame(frameIndex)
renderAudio()
readAudioChunk(chunkIndex)
releaseAudio()
```

### Visuelle Ausgabe

- `renderVisualFrame(frameIndex)` berechnet die Bildzeit nur aus Index und
  gebundener Bildrate;
- die aktive Phase folgt nur aus den kumulierten Vertragsdauern;
- statische Phasen bleiben zentriert;
- bewegte Phasen verwenden die gebundene Sinusbewegung und Zykluszahl;
- das Canvas besitzt feste Pixelmasse und Device-Scale 1;
- der Pythonhandoff liest ausschliesslich `canvas#world` als PNG.

### Auditive Ausgabe

- `renderAudio()` verwendet ausschliesslich einen monoauralen
  `OfflineAudioContext`;
- Samplezahl ist exakt `duration_seconds * audio_sample_rate`;
- Frequenz und Gainverlauf folgen dem Weltvertrag;
- `readAudioChunk()` gibt exakt einen gebundenen Hop zur unmittelbaren
  W1-C-Reduktion aus;
- `releaseAudio()` loescht den Browserpuffer im Erfolgs- und Fehlerfall.

## Verbotene Browserrollen

Die neuen Assets duerfen nicht enthalten:

- `Date.now`, `performance.now`, `requestAnimationFrame` oder Timersteuerung;
- `AudioContext` ausser `OfflineAudioContext`;
- `mediaDevices`, `getUserMedia`, `MediaRecorder` oder Systemaudioaufnahme;
- `fetch`, WebSocket oder andere Netzwerkzugriffe;
- `localStorage`, `sessionStorage`, IndexedDB, Download oder Dateiexport;
- Vollbild-, Fokus-, Tastatur- oder Mausabhaengigkeit;
- Labels, Objektklassen, Reward, Zielverhalten oder Feldrueckschreibung.

## Allgemeiner Capture-Handoff

Die spaetere Pythonfunktion lautet:

```python
capture_browser_payload_page(
    page: BrowserPayloadPage,
    contract: BrowserWorldContract,
    source_config: BrowserPayloadSourceConfig,
    receptor_bridge: BrowserReceptorBridge,
    *,
    asset_directory: Path,
    preflight: BrowserPayloadCapturePreflight,
) -> tuple[BrowserReceptorSequenceBatch, BrowserPayloadCaptureReceipt]
```

Sie startet selbst keinen Browser. Sie akzeptiert nur eine bereits erzeugte
Seite in einem frischen isolierten Kontext und erzwingt:

1. kein persistentes Profil und keine Erweiterungen;
2. Viewport gleich Canvas, Device-Scale 1 und JavaScript aktiv;
3. ausschliesslich die drei lokalen digestgebundenen Assets;
4. Abbruch vor Payloaduebergabe bei jedem fremden Request;
5. Konfiguration genau einmal aus den beiden gebundenen Vertraegen;
6. streng geordnete visuelle Frames und Audiohops gemaess W1-C-Inventar;
7. Audiopufferfreigabe auch bei einem Fehler;
8. Finalisierung ausschliesslich durch `BrowserReceptorBridge.finalize()`.

## Skalare Abnahme

`BrowserPayloadCaptureReceipt` darf nur enthalten:

```text
source_id
world_contract_digest
source_config_digest
asset_digests
local_request_count
blocked_request_count
visual_png_count
audio_chunk_count
rendered_audio_sample_count
batch_digest
audio_buffer_released
raw_payloads_retained            # unveraenderlich False
```

Es enthaelt keine PNGs, Pixel, Samples, Rezeptorwerte, Feldwerte oder
Phaseninterpretationen.

## W1-E-Abnahme ohne Browserstart

Die erste Implementierungsscheibe wird nur mit statischen Assetpruefungen und
einer kontrollierten Fake-Seite abgenommen:

- Konfigurationsvalidierung und Digestdeterminismus;
- Assetinventar und verbotene Browser-APIs;
- lokale Requestgrenze und Abbruch bei Fremdrequest;
- vollstaendige Aufruf- und Payloadreihenfolge;
- unmittelbare Uebergabe an die echte W1-C-Bruecke;
- Audiopufferfreigabe im Erfolgs- und Fehlerfall;
- skalarer Receipt ohne Rohpayload oder semantische Rolle;
- Quelltext frei von Z4-, Kamera-, Mikrofon-, P0-, F3- und B3-Importen.

W1-E startet keinen Browser. Ein realer technischer Browser-Smoke benoetigt
danach eine eigene begrenzte W1-F-Entscheidung, aber keine
Forschungslaufnummer.

## Grenzen und Nichtbefunde

W1-D definiert eine technische kontrollierte Testweltquelle. Er behauptet
keine Wahrnehmung, Wiedererkennung, Praegung, Feldzeit, Memory, Organisation,
Semantik oder KI. Browserphasen werden nicht als Bedeutung an Rezeptoren oder
Feld uebergeben.

Kamera, Live-Mikrofon, physische Sensorik, Netzwerkmedien und
Bildschirm-Kamera-Rueckkopplung bleiben ausgeschlossen. Lauf 197 und alle
Z4-Ausfuehrungsartefakte bleiben unangetastet.

## W1-D-Entscheidung

```text
alte allgemeine Browserwelt als Quelle:  ungeeignet
Z4-A2 als W1-Quelle:                     verboten
direkte Canvas-PNG-Ausgabe:              vertraglich vorgesehen
direkte Offline-PCM-Ausgabe:             vertraglich vorgesehen
neue allgemeine Assets:                  separat gebunden
W1-C-Rezeptorbruecke:                    unveraendert wiederverwendet
neue Feldphysik:                         nein
Browserausfuehrung:                      nein
Forschungslauf:                          nein
naechste Implementierungsscheibe:        W1-E
```

## Bester naechster Schritt

W1-E ist gemaess
`W1E_IMPLEMENTIERUNG_KAMERAFREIE_BROWSER_PAYLOADQUELLE.md` technisch
geschlossen. Assets, Quellenvertraege, Capture-Handoff und Fake-Seiten-
End-to-End-Abnahme sind implementiert. Als naechstes bindet W1-F zuerst nur
den minimalen realen Browser-Smoke und seine Schliessungsgrenzen; kein
Z4-Import und kein Forschungslauf.
