# W3-I: Komponentenlokalisierung der Reihenfolgedifferenz

Stand: 2026-08-09

Entscheidung: `ORDER_DIFFERENCE_FAST_ACTIVATION_ONLY_AFTERIMAGE_DISABLED`

Implementierung: technischer Test

Formaler Forschungslauf: nein

## Auftrag

W3-I lokalisiert die in W3-G und W3-H beobachteten Endfelddifferenzen in den
oeffentlichen Snapshotkomponenten. Die endpunktkontrollierten visuellen und
auditiven Reihenfolgepaare bleiben unveraendert.

## Gepruefte Komponenten

Fuer beide Kontrollpaare werden getrennt verglichen:

- Aktivierungsvektor;
- Nachhallvektor;
- optionaler Substratzustand;
- optionaler Entwicklungszustand.

Es wird kein erwarteter Traeger vorgegeben und keine neue Feldkomponente
eingefuehrt.

## Ergebnis

| Reihenfolgepaar | Aktivierung | Nachhall | Substrat | Entwicklung |
|---|---|---|---|---|
| visuell W3-G | verschieden | exakt gleich | abwesend | abwesend |
| auditiv W3-H | verschieden | exakt gleich | abwesend | abwesend |

Der Nachhall ist in diesem Browserpayload-Consumeraufbau nicht konfiguriert
und bleibt deshalb null. Die Digestdifferenzen aus W3-G und W3-H liegen
vollstaendig im vorhandenen schnellen Aktivierungszustand. Sie sind kein
Hinweis auf einen zusaetzlichen langsamen Traeger.

## Verifikation

```text
gezielter Consumertest: 6 passed
aktiver Architekturverbund: 217 passed
389 subtests passed
visuelle Aktivierung Kontrolle != Gegenbaseline
auditive Aktivierung Kontrolle != Gegenbaseline
Nachhall jeweils Kontrolle == Gegenbaseline
substrate is None
development is None
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- W3-G und W3-H als endpunktkontrollierte Reihenfolgepaare;
- `SharedMCMFieldSnapshot.activation` und `.afterimage`;
- `SharedMCMFieldSnapshot.substrate` und `.development`;
- `current_api` als einziger Projektimport des Consumers.

## Aussagegrenze

W3-I belegt eine technische schnelle Zustandsdifferenz. Er belegt keinen
Nachhallbeitrag, kein Substrat, kein Memory, Lernen, Feldzeit, inneren Kontext,
Organisation, Semantik, Selbstregulation oder KI. Die bestehende schnelle
Aktivierung darf nicht als Memory oder Feldzeit umbenannt werden. Es wurde
kein Browser oder Playwright gestartet und keine Kamera, kein Live-Mikrofon
oder andere physische Sensorik aktiviert. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

W3-J wiederholt beide endpunktkontrollierten Reihenfolgepaare mit der bereits
vorhandenen neutralen schnellen Nachhallkonfiguration:

1. Die bisherige Konfiguration ohne Nachhall bleibt Nullbaseline.
2. Genau eine feste inhaltsneutrale Nachhallzeit wird fuer beide Arme genutzt.
3. Aktivierung und Nachhall werden wieder getrennt verglichen.
4. Substrat und Entwicklungszustand muessen abwesend bleiben.
5. Ein Nachhallunterschied waere nur bekannte schnelle Feldfortsetzung, kein
   Memory- oder Feldzeitbefund.

## Spaeterer Umsetzungsstand W3-J

W3-J ist am 2026-08-09 umgesetzt worden. Bei fester neutraler Nachhallzeit
von 0.5 s unterscheiden sich Aktivierung und Nachhall in beiden
Reihenfolgepaaren. Substrat und Entwicklung bleiben abwesend. Der aktive
Architekturverbund besteht mit `218 passed` und 389 Subtests.
