# W3-G: Browserpayload visuelle Reihenfolge-Gegenbaseline

Stand: 2026-08-09

Entscheidung: `BROWSER_PAYLOAD_VISUAL_ORDER_PRESERVED_IN_FIELD_PATH`

Implementierung: technischer Test

Formaler Forschungslauf: nein

## Auftrag

W3-G prueft, ob der facade-only Browserpayloadpfad bei identischem visuellen
Payloadinventar eine veraenderte zeitliche Reihenfolge technisch erhaelt oder
auf einen reinen Inventarwert kollabiert.

## Kontrollpaar

```text
Kontrolle:       PNG-Grauwerte (48, 128, 208)
Gegenbaseline:   PNG-Grauwerte (128, 48, 208)
Audio in beiden: 15 identische PCM-Hops mit Amplitude 0.25
```

Beide Arme verwenden eine frische Browserbruecke, frische Rezeptoren und ein
frisches neutrales Feld. Die drei visuellen reduzierten Werte sind als
ungeordnetes Inventar identisch. Nur die beiden ersten Frames tauschen ihre
Zeitposition; der letzte visuelle Kontakt bleibt identisch.

## Ergebnis

- Das ungeordnete visuelle Werteinventar ist identisch.
- Der letzte visuelle reduzierte Zustand ist identisch.
- Die auditive reduzierte Sequenz ist exakt identisch.
- Die geordnete visuelle reduzierte Sequenz ist verschieden.
- Browserbatch-Digest und Endfeld-Snapshot-Digest sind verschieden.

Der vorhandene kontrollierte Rezeptor- und Feldpfad bewahrt damit in diesem
Aufbau die visuelle Zeitordnung. Er reduziert die drei Frames nicht auf eine
ungeordnete Menge.

## Verifikation

```text
gezielter Consumertest: 4 passed
aktiver Architekturverbund: 215 passed
389 subtests passed
visuelles Inventar Kontrolle == Gegenbaseline
auditive Sequenz Kontrolle == Gegenbaseline
visuelle Sequenz Kontrolle != Gegenbaseline
Felddigest Kontrolle != Gegenbaseline
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- W3-D bis W3-F als bestehender facade-only Browserpayloadpfad;
- `current_api` als einziger Projektimport des Consumers;
- kontrollierte synthetische PNG- und PCM-Payloads;
- reduzierte Sequenzen, Browserbatch- und Feldsnapshot-Digests.

## Aussagegrenze

W3-G belegt nur technische Reihenfolgeerhaltung im konkreten kontrollierten
Aufbau. Die Differenz ist durch die bekannte transiente Rezeptor- und
Felddynamik erklaerbar. Sie belegt keine Feldzeit, kein Memory, Lernen,
inneren Kontext, Organisation, Semantik, Selbstregulation oder KI. Es wurde
kein Browser oder Playwright gestartet und keine Kamera, kein Live-Mikrofon
oder andere physische Sensorik aktiviert. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

W3-H bildet die modalitaetsgespiegelte auditive Reihenfolge-Gegenbaseline:

1. Alle drei PNG-Frames bleiben exakt gleich.
2. Beide Arme enthalten dasselbe kontrollierte PCM-Amplitudeninventar.
3. Nur zwei vorab festgelegte spaetere PCM-Hops tauschen ihre Zeitposition.
4. Die visuelle Sequenz muss identisch bleiben.
5. Auditive Sequenz, Batch und Endfeld werden auf Erhaltung oder Kollaps der
   auditiven Zeitordnung geprueft, ohne Feldzeit- oder Memoryclaim.

## Spaeterer Umsetzungsstand W3-H

W3-H ist am 2026-08-09 umgesetzt worden. Bei identischem
PCM-Amplitudeninventar bleiben letzter PCM-Kontakt und visuelle Sequenz
gleich. Auditive Sequenz, Batch und Endfeld unterscheiden die vertauschte
fruehere Hop-Reihenfolge. Der aktive Architekturverbund besteht mit
`216 passed` und 389 Subtests.
