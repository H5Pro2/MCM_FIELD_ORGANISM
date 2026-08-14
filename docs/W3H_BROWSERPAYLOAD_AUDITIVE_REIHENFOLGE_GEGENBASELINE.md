# W3-H: Browserpayload auditive Reihenfolge-Gegenbaseline

Stand: 2026-08-09

Entscheidung: `BROWSER_PAYLOAD_AUDIO_ORDER_PRESERVED_IN_FIELD_PATH`

Implementierung: technischer Test

Formaler Forschungslauf: nein

## Auftrag

W3-H spiegelt die endpunktkontrollierte visuelle Reihenfolgepruefung W3-G
fuer den auditiven Browserpayloadpfad. Bei identischem PCM-Inventar wird nur
die fruehere Zeitposition zweier Amplituden vertauscht.

## Kontrollpaar

Beide Arme enthalten 15 PCM-Hops einer 100-Hz-Sinusquelle. Zwoelf Hops haben
Amplitude 0.25. Je ein Hop besitzt Amplitude 0.15 beziehungsweise 0.35.

```text
Kontrolle:       Hop 7 = 0.15, Hop 11 = 0.35
Gegenbaseline:   Hop 7 = 0.35, Hop 11 = 0.15
letzter Hop:     in beiden Armen 0.25
visuelle Frames: in beiden Armen (48, 128, 208)
```

Amplitude, Frequenz, Samplezahl, ungeordnetes Amplitudeninventar und letzter
Eingangskontakt sind damit kontrolliert. Nur die fruehere auditive Reihenfolge
ist verschieden.

## Ergebnis

- Das ungeordnete PCM-Amplitudeninventar ist identisch.
- Der letzte PCM-Eingangskontakt ist identisch.
- Die visuelle reduzierte Sequenz ist exakt identisch.
- Die auditive reduzierte Sequenz ist verschieden.
- Browserbatch-Digest und Endfeld-Snapshot-Digest sind verschieden.

Der vorhandene kontrollierte Rezeptor- und Feldpfad bewahrt damit in diesem
Aufbau die auditive Zeitordnung ueber einen identischen spaeteren
Eingangskontakt hinaus.

## Verifikation

```text
gezielter Consumertest: 5 passed
aktiver Architekturverbund: 216 passed
389 subtests passed
PCM-Inventar Kontrolle == Gegenbaseline
letzter PCM-Kontakt Kontrolle == Gegenbaseline
visuelle Sequenz Kontrolle == Gegenbaseline
auditive Sequenz Kontrolle != Gegenbaseline
Felddigest Kontrolle != Gegenbaseline
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- W3-D bis W3-G als bestehender facade-only Browserpayloadpfad;
- `current_api` als einziger Projektimport des Consumers;
- kontrollierte synthetische PNG- und PCM-Payloads;
- reduzierte Sequenzen, Browserbatch- und Feldsnapshot-Digests.

## Aussagegrenze

W3-H belegt nur technische Reihenfolgeerhaltung im konkreten kontrollierten
Aufbau. Die Differenz kann aus dem rollenden Audiorezeptorfenster und der
bekannten transienten Feldfortsetzung entstehen. Sie belegt keine Feldzeit,
kein Memory, Lernen, inneren Kontext, Organisation, Semantik,
Selbstregulation oder KI. Es wurde kein Browser oder Playwright gestartet und
keine Kamera, kein Live-Mikrofon oder andere physische Sensorik aktiviert.
Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

W3-I lokalisiert fuer die endpunktkontrollierten visuellen und auditiven
Reihenfolgepaare die Endfelddifferenz komponentenweise:

1. Aktivierung und Nachhall werden getrennt verglichen.
2. Substrat und Entwicklungszustand muessen weiterhin abwesend sein.
3. Es wird vorab keine Komponente als erwarteter Traeger festgelegt.
4. Die Auswertung verwendet Feldwerte statt nur Snapshot-Digests.
5. Das Ergebnis bleibt eine technische Lokalisierung ohne Feldzeit-, Kontext-
   oder Memoryclaim.

## Spaeterer Umsetzungsstand W3-I

W3-I ist am 2026-08-09 umgesetzt worden. Bei den visuellen und auditiven
Reihenfolgepaaren unterscheidet sich nur die schnelle Aktivierung. Der in
diesem Aufbau nicht konfigurierte Nachhall bleibt gleich; Substrat und
Entwicklung sind abwesend. Der aktive Architekturverbund besteht mit
`217 passed` und 389 Subtests.
