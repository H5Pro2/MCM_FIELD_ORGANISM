# S1-XN: Statischer Engineering- und Fixture-Korrekturvertrag

## Zweck und Grenze

S1-XN trennt die weiter nutzbare PPB-1-Engineeringinfrastruktur vom
geschlossenen registrierten Forschungsvergleich. Der Schritt definiert nur
einen Vertrag. Er implementiert keine Fixture, aendert keine Runtime und
fuehrt weder Matrix noch Feld aus.

## Historischer Bestand bleibt unveraendert

S1-XC, S1-XI, das S1-XL-Receipt und der S1-XM-Audit bleiben unveraendert.
Insbesondere wird die auditive `0.2`-Grenzzelle nicht nachtraeglich repariert
oder erneut ausgefuehrt. Eine neue technische Fixture muss eine neue Schema-
und Digestidentitaet erhalten.

## Erhaltene Engineeringrollen

Als private technische Infrastruktur bleiben erhalten:

- begrenzte, nach Modalitaet getrennte Prototypbankzustaende;
- deterministische Initialisierung und atomare Zustandsuebergaenge;
- Aktualisierung, Stabilisierung, Abschwaechung und Kapazitaetsregeln;
- Zustands-, Herkunfts- und Receipt-Digests;
- read-only Distanzprobe und Zustandsunveraenderlichkeitspruefung;
- fail-closed Validierung von Konfiguration, Eingabe und Ergebnis.

Diese Rollen bilden eine technische Wahrnehmungsspeicher-Infrastruktur. Sie
sind kein Befund einer MCM-spezifischen oder endogenen Memory-Mechanik.

## Neue robuste Verhaltensfixture

Die spaetere private Fixture verwendet keine Verhaltensprobe direkt auf der
Schwelle. Alle Werte sind binaer exakt darstellbar und besitzen einen
expliziten Abstand:

| Modalitaet | Schwelle | positiv nah | positiv mit Abstand | negativ mit Abstand | deutlich negativ |
| --- | ---: | ---: | ---: | ---: | ---: |
| auditiv | 0.25 | 0.125 | 0.1875 | 0.3125 | 0.625 |
| visuell | 0.125 | 0.0625 | 0.09375 | 0.15625 | 0.5 |

Der kleinste Schwellenabstand ist auditiv `0.0625` und visuell `0.03125`.
Bei der spaeteren Materialisierung muss die tatsaechliche Produktionsmetrik
die Distanz vor Testnutzung berechnen. Stimmt ihre Klassenseite nicht mit
der gebundenen Erwartung ueberein, stoppt die Fixture fail-closed.

## Separater Operator-Numeriktest

Die Semantik von `distance <= threshold` wird nicht in der Verhaltensmatrix
versteckt. Ein eigener kleiner Numeriktest soll spaeter den unmittelbar
darunterliegenden Float, die exakte Schwelle und den unmittelbar
darueberliegenden Float pruefen. Dieser Test erzeugt keine Kandidaten- oder
Baselineentscheidung.

## Engineeringabnahme

Die neue Fixture dient nur der Regression von begrenztem Prototypzustand und
read-only Wiedererkennung. Eine einfache statische Prototypbank bleibt die
Pflichtreferenz. Erwartete Verhaltensgleichheit ist fuer diese Fixture weder
Fehler noch Forschungsneuheit.

## Entscheidung

`PASS_ENGINEERING_DISPOSITION_AND_NUMERIC_MARGIN_FIXTURE_CONTRACT_BOUND`

## Naechster Schritt

S1-XO darf die neue private Margin-Fixture und ihren reinen Validator mit
synthetischen Tests implementieren. Nicht zulaessig sind Aenderungen an
S1-XC, S1-XI, Distanzmetrik oder Schwellenoperator sowie Runner-, Matrix-,
Feld-, API- oder Produktionsausfuehrung.
