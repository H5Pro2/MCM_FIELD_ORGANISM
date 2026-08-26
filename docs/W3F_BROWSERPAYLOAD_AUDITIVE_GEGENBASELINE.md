# W3-F: Browserpayload-Audio-Gegenbaseline

Stand: 2026-08-09

Entscheidung: `BROWSER_PAYLOAD_AUDIO_CHANGE_MODALITY_ISOLATED_PROPAGATES`

Implementierung: technischer Test

Formaler Forschungslauf: nein

## Auftrag

W3-F spiegelt die visuelle Gegenbaseline W3-E fuer den auditiven
Browserpayloadpfad. Alle visuellen Payloads bleiben identisch; genau ein
kontrollierter PCM-Hop wird veraendert.

## Kontrollpaar

```text
Kontrolle:
PNG-Grauwerte (48, 128, 208)
15 PCM-Hops mit Amplitude 0.25

Gegenbaseline:
PNG-Grauwerte (48, 128, 208)
PCM-Hop 7 mit Amplitude 0.30, alle anderen 0.25
```

Beide Arme verwenden eine frische Browserbruecke, frische Rezeptoren und ein
frisches neutrales Feld. Vertrag, Frequenz, Zeitgrenzen und visuelle Payloads
sind identisch.

## Ergebnis

Die Gegenbaseline zeigt:

- visuelle reduzierte Sequenz exakt identisch;
- auditive reduzierte Sequenz verschieden;
- Browserbatch-Digest verschieden;
- Endfeld-Snapshot-Digest verschieden.

W3-E und W3-F bilden damit ein gespiegeltes technisches Kontrollpaar fuer die
getrennte Audio- und Videoreduktion vor dem gemeinsamen Feld.

## Verifikation

```text
123 passed
350 subtests passed
Python-Kompilierung erfolgreich
visuelle Kontrolle == visuelle Audio-Gegenbaseline
auditive Kontrolle != auditive Audio-Gegenbaseline
Felddigest Kontrolle != Felddigest Audio-Gegenbaseline
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- W3-D- und W3-E-Browserpayload-Consumertest;
- `current_api` als einziger Projektimport;
- kontrollierte synthetische PNG- und PCM-Payloads;
- Browserbatch- und Feldsnapshot-Digests als technische Identitaetsmasse.

## Aussagegrenze

W3-F belegt technische Modalitaetstrennung und Eingangsunterscheidbarkeit im
konkreten kontrollierten Aufbau. Er belegt keine semantische Unterscheidung,
kein Memory, Lernen, Feldzeit, Organisation, Selbstregulation oder KI. Es
wurde kein Browser oder Playwright gestartet und keine Kamera, kein
Live-Mikrofon oder andere physische Sensorik aktiviert. Lauf 197 bleibt
unberuehrt.

## Bester naechster Schritt

W3-G prueft eine reine visuelle Reihenfolge-Gegenbaseline bei identischem
Payloadinventar:

1. Kontrolle und Gegenbaseline enthalten exakt dieselben drei PNG-Frames und
   dieselben 15 PCM-Hops.
2. Nur die Reihenfolge der beiden spaeteren visuellen Frames wird vertauscht.
3. Die auditive Sequenz muss identisch bleiben.
4. Batch- und Endfelddigest muessen zeigen, ob der aktuelle kontrollierte Pfad
   diese zeitliche Ordnung technisch erhaelt oder kollabieren laesst.
5. Das Ergebnis wird ohne Feldzeit-, Kontext-, Memory- oder Bedeutungsclaim
   dokumentiert.

## Spaeterer Umsetzungsstand W3-G

W3-G ist am 2026-08-09 umgesetzt worden. Bei identischem visuellen
Werteinventar bleiben auditive Sequenz und ungeordnetes visuelles Inventar
gleich. Die geordnete visuelle Sequenz, Batch und Endfeld unterscheiden die
vertauschte Zeitposition. Der aktive Architekturverbund besteht mit
`215 passed` und 389 Subtests.
