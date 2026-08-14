# W1-B: Schnittstellenvertrag der generischen Browser-Rezeptorbruecke

Stand: 2026-08-07

Entscheidung: `W1B_GENERIC_BROWSER_RECEPTOR_BRIDGE_CONTRACT_BOUND`

Forschungslauf: nein

## Auftrag

W1-B bindet die kleinste technische Schnittstelle, mit der kontrollierte
Browserausgaben den vorhandenen allgemeinen Rezeptorzeit- und S/H-Feldpfad
erreichen koennen. Der Vertrag fuegt keine neue Feldphysik hinzu und
uebernimmt keinen Teil der geparkten Z4-A-Ausfuehrungskette.

## Zielkette

```text
BrowserWorldContract
-> geordnete PNG-Bilder und normierte PCM-Bloecke
-> unmittelbare modalitaetseigene Reduktion
-> zwei ReceptorTimeSequence-Objekte auf einer gemeinsamen Uhr
-> vorhandener allgemeiner Audio-/Video-Sequenzhandoff
-> Verteiler, offene Docks und gemeinsames S/H-Feld
```

Die Bruecke endet fachlich an der neutralen Rezeptorsequenz. Der anschliessende
Feldhandoff bleibt allgemeine Audio-/Video-Infrastruktur und erhaelt keine
Browserlogik.

## Neue technische Rollen

Die spaetere Implementierung liegt in
`mcm_field_organism/browser_receptor_bridge.py` und enthaelt genau folgende
oeffentliche Rollen.

### `BrowserReceptorBridgeConfig`

```text
clock_id:             technischer Identifier
ticks_per_second:     positive endliche Taktrate
sequence_start_tick:  nichtnegativer gemeinsamer Starttick
```

Der Standard ist `browser.sequence.ns`, `1_000_000_000.0` und Starttick `0`.
Bildrate, Bildgeometrie, Audiotaktrate, FFT-Fenster und Hop stammen nicht aus
dieser Konfiguration, sondern aus den uebergebenen vorhandenen
`LocalChannelGridReceptor`- und `BroadbandHearingPath`-Objekten.

### `BrowserReceptorSequenceBatch`

```text
contract_id
contract_digest
sequences                 # exakt auditory, visual
raw_payloads_retained     # unveraenderlich False
```

Der Batch ist unveraenderlich. Er enthaelt weder PNG-, PCM- noch
Browserzustandsdaten und keine Phasenlabels, Objektklassen oder Bedeutungen.

### `BrowserReceptorBridge`

```python
BrowserReceptorBridge(
    contract: BrowserWorldContract,
    visual_receptor: LocalChannelGridReceptor,
    auditory_path: BroadbandHearingPath,
    config: BrowserReceptorBridgeConfig = BrowserReceptorBridgeConfig(),
)

push_visual_png(payload: bytes, *, frame_index: int) -> None
push_audio_chunk(samples: Iterable[float], *, chunk_index: int) -> None
finalize() -> BrowserReceptorSequenceBatch
```

Der auditive Pfad muss beim Aufbau frisch sein. Die Bruecke ist nach
`finalize()` geschlossen und kann weder erneut finalisiert noch weiter
beschrieben werden.

## Inventarableitung

Die erwarteten Eingaben werden ausschliesslich aus dem Welt- und
Rezeptorvertrag abgeleitet:

```text
duration_seconds = BrowserWorldContract.total_duration_ns / 1_000_000_000
visual_frame_count = duration_seconds * visual_frames_per_second
audio_chunk_count = duration_seconds * audio_sample_rate / audio_hop_size
```

Beide Ergebnisse muessen positive ganze Zahlen sein. Es gibt keine festen
W1-Zahlen fuer Dauer, Bildrate, Aufloesung, Chunkzahl, Frequenz oder
Bewegungsrichtung. Dadurch werden die festen Z4-A2-Inventare nicht kopiert.

## Eingangsgrenzen

### Visuell

- nur `bytes` mit gueltiger PNG-Signatur;
- Dekodierung genau einmal zu RGB `uint8`;
- exakte Hoehe und Breite aus `VisualGridConfig`;
- streng lueckenloser `frame_index` ab null;
- sofortige Reduktion durch `LocalChannelGridReceptor.analyze()`;
- keine Speicherung des PNG oder des dekodierten Bildes nach dem Aufruf.

### Auditiv

- genau ein Hop `audio_hop_size` je Aufruf;
- nur endliche Werte innerhalb `-1..1`;
- streng lueckenloser `chunk_index` ab null;
- sofortige Reduktion durch `BroadbandHearingPath.push()`;
- Warmup darf noch keinen Rezeptorzustand erzeugen;
- keine Speicherung des PCM-Blocks nach dem Aufruf.

Die Bruecke puffert nur bereits reduzierte
`OrganismTimedReceptorFrame`-Objekte bis zur atomaren Finalisierung.

## Gemeinsame technische Zeit

Beide Modalitaeten verwenden `config.clock_id`. Zeitgrenzen werden aus Index,
Rezeptortaktrate und gemeinsamem Starttick berechnet, nicht aus Aufrufzeit,
Browser-Wanduhr oder nachtraeglicher Paarung.

Fuer visuelle Bildgrenze `k`:

```text
tick(k) = sequence_start_tick
        + floor(k * ticks_per_second / visual_frames_per_second)
```

Fuer auditive Samplegrenze `s`:

```text
tick(s) = sequence_start_tick
        + floor(s * ticks_per_second / audio_sample_rate)
```

Jeder visuelle Zustand erhaelt `[tick(k), tick(k+1))`. Jeder ausgegebene
auditive Zustand erhaelt sein nicht ueberlappendes Abschlussintervall
`[tick(window_end_sample-hop_size), tick(window_end_sample))`. Das vollstaendige
und absichtlich ueberlappende FFT-Analysefenster bleibt separat als
`window_start_sample` und `window_end_sample` im `ReceptorContactFrame`
erhalten. Unterschiedliche native Raten bleiben erhalten; die Bruecke
interpoliert, mittelt und paart nicht.

## Atomare Finalisierung

`finalize()` ist nur erfolgreich, wenn:

1. alle erwarteten visuellen Bilder genau einmal vorliegen;
2. alle erwarteten Audiohops genau einmal vorliegen;
3. beide reduzierten Sequenzen nicht leer sind;
4. Modalitaet, Geometrie und Uhr innerhalb jeder Sequenz konstant sind;
5. die letzte Zeitgrenze beider Eingangsfolgen dem Weltende entspricht;
6. keine Rohpayload im Ergebnis enthalten ist.

Bei einer Verletzung entsteht kein partieller Batch. Bereits reduzierte
interne Zwischenzustaende werden nicht als gueltige Ausgabe freigegeben.

## Allgemeiner Sequenzhandoff

Die vorhandene interne Funktion
`_advance_captured_audio_video_sequences()` in
`audio_video_neutral_field_runtime.py` bildet bereits reduzierte auditive und
visuelle Sequenzen auf den neutralen S/H-Feldpfad ab. W1-C darf sie ohne
Verhaltensaenderung als
`advance_audio_video_receptor_sequences()` oeffentlich machen und den alten
internen Namen vollstaendig ersetzen.

Dieser Schritt ist Teil derselben Integrationsluecke. Er fuegt keine zweite
Browserruntime und keinen neuen Feldpfad hinzu. Der Browseradapter importiert
nur diese allgemeine Audio-/Video-Grenze oder gibt seinen Batch an den
Aufrufer zur dortigen Uebergabe zurueck.

## Harte Abgrenzung von Z4-A

`browser_receptor_bridge.py` darf nichts aus folgenden Namensraeumen
importieren oder referenzieren:

- `z4a_browser_receptor_adapter`;
- `z4a_playwright_capture`;
- `z4a_playwright_smoke` und `z4a_playwright_audio_smoke`;
- `mcm_f3_*`, P0, F3 oder B3;
- Lauf 197, dessen Sperr- oder Ergebnisdateien;
- `tools/z4a_browser_world_v2`.

Auch die kamera- und mikrofongebundenen Coordinator-Klassen aus
`tools/controlled_browser_world/server.py` sind kein Eingangsweg fuer W1-C.
Die technische Abnahme verwendet ausschliesslich synthetische PNG- und
PCM-Payloads im Prozess.

## W1-C-Abnahme

Die Implementierung ist technisch geschlossen, wenn fokussierte Tests
mindestens nachweisen:

- Konfiguration und abgeleitetes Inventar sind deterministisch;
- ungueltige, falsche oder ungeordnete PNG-/PCM-Eingaben scheitern geschlossen;
- unvollstaendige und doppelte Finalisierung scheitern geschlossen;
- Warmup und auditive Fensterzeit sind korrekt;
- visuelle und auditive Zeitintervalle sind lueckenlos und teilen eine Uhr;
- gleiche Payloadfolgen ergeben gleiche Rezeptorsequenzen und Digests;
- der Batch enthaelt keine Rohpayload und keine semantischen Rollen;
- ein synthetischer Batch erreicht ueber den allgemeinen Handoff das
  vorhandene gemeinsame S/H-Feld;
- Quelltext und Importe bleiben frei von Z4-, Kamera-, Mikrofon-, Label-,
  Reward- und Writeback-Rollen.

Diese Tests sind technische Tests ohne Forschungslaufnummer. Es wird kein
Browser gestartet.

## Nichtziele und Nichtbefunde

W1-B definiert keine Weltinterpretation, keine Objekterkennung, kein Lernen,
keine Praegung, kein Memory, keine Feldzeit, keinen inneren Kontext, keine
Organisation, keine Semantik und keine KI. Die Phasen des Weltvertrags dienen
nur der kontrollierten Quellenordnung und werden nicht als Bedeutung in das
Feld eingespeist.

## W1-B-Entscheidung

```text
generische Eingaben:                  PNG und normierte PCM-Hops
Ausgabe:                              auditory/visual ReceptorTimeSequence
gemeinsame Zeit:                      index- und taktratenbasiert
Rohdatenhaltung:                      nein
Phasenlabels im Rezeptorpfad:         nein
neue Feldphysik:                      nein
Z4-Import oder Z4-Ausfuehrung:        nein
Kamera oder Live-Mikrofon:            nein
Forschungslauf:                       nein
naechste Implementierungsscheibe:     W1-C
```

## Bester naechster Schritt

W1-C ist gemaess
`W1C_IMPLEMENTIERUNG_GENERISCHE_BROWSER_REZEPTORBRUECKE.md` technisch
geschlossen. Die Bruecke, der oeffentliche allgemeine Sequenzhandoff und die
synthetischen Vertragstests sind implementiert. Als naechstes prueft W1-D
statisch den allgemeinen kamerafreien Browser-Payloadquellenrand. Keine
Wiederaufnahme von Z4-A oder Lauf 197.
