# W3-D: current_api Browserpayload-Consumertest

Stand: 2026-08-09

Entscheidung: `CURRENT_API_CONTROLLED_BROWSER_PAYLOAD_PATH_COMPLETE`

Implementierung: technischer Test

Formaler Forschungslauf: nein

## Auftrag

W3-D prueft den kontrollierten kamerafreien Browserpayloadpfad als
eigenstaendigen Verbraucher der kuratierten `current_api`, ohne einen Browser
oder Playwright zu starten.

## Statische Vorpruefung

Elf benoetigte Projektrollen wurden vor der Implementierung gegen
`CURRENT_CONTROLLED_FIELD_EXPORTS` geprueft:

```text
BrowserReceptorBridge
BrowserWorldContract
BrowserWorldPhase
BroadbandHearingPath
LocalChannelGridReceptor
LogSpectralConfig
LogSpectralReceptor
VisualGridConfig
NeutralLocalFieldSubstrateConfig
advance_audio_video_receptor_sequences
restore_shared_mcm_field
```

Ergebnis: keine fehlende Rolle und keine Ueberschneidung mit
`F3_REFERENCE_EXPORTS`.

## Kontrollierter Pfad

Der neue Test `test_current_api_browser_payload_consumer.py` importiert als
Projektcode ausschliesslich aus `mcm_field_organism.current_api`.

```text
3 deterministische PNG-Frames
+ 15 deterministische PCM-Hops
-> BrowserReceptorBridge
-> 11 auditive + 3 visuelle reduzierte Zustaende
-> neutrales gemeinsames Feld
-> Snapshot
-> Restore
```

OpenCV dient nur zur PNG-Kodierung der kontrollierten Testarrays. Die Bruecke
dekodiert und reduziert die Payloads unmittelbar. Weder Batch noch Bruecke
halten Rohpayloads nach der Uebergabe.

## Verifikation

```text
121 passed
350 subtests passed
Python-Kompilierung erfolgreich
14 von 14 Supports zugewiesen
raw_payloads_retained == False
Snapshot-Digest nach Restore identisch
substrate is None
development is None
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- Browserwelt- und Browserbrueckenrollen aus `current_api`;
- kontrollierte synthetische PNG- und PCM-Testdaten;
- neutraler AV-Feldpfad sowie Snapshot/Restore aus `current_api`;
- W2-J als geschlossene Importgrenze.

## Aussagegrenze

W3-D belegt nur die technische Vollstaendigkeit des kontrollierten
Browserpayloadpfads. Er belegt kein Memory, Lernen, Feldzeit, Organisation,
Semantik, Selbstregulation oder KI. Es wurde kein Browser oder Playwright
gestartet und keine Kamera, kein Live-Mikrofon oder andere physische Sensorik
aktiviert. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

W3-E bindet Reproduzierbarkeit und eine minimale technische Gegenbaseline fuer
den Fassade-only Browserpayloadpfad:

1. Derselbe Payloadverlauf wird auf zwei frischen Bruecken wiederholt.
2. Batch- und Endfelddigests muessen exakt gleich sein.
3. Eine einzige kontrollierte visuelle Payloadaenderung bildet die
   Gegenbaseline.
4. Deren Batch- und Endfelddigest muessen sich vom unveraenderten Verlauf
   unterscheiden.
5. Daraus folgt nur technische Reproduzierbarkeit und Eingangssensitivitaet,
   keine Bedeutung, Organisation oder Memory.

## Spaeterer Umsetzungsstand W3-E

W3-E ist am 2026-08-09 umgesetzt worden. Kontrolle und identische
Wiederholung bleiben in Batch und Endfeld exakt digestgleich. Eine einzelne
visuelle Grauwertaenderung laesst die auditive Sequenz identisch und
veraendert visuelle Sequenz, Batchdigest und Felddigest. Der aktuelle Verbund
besteht mit `122 passed` und 350 Subtests.
