# W3-K: Nachhall-Kausalrichtung gegen die Nullbaseline

Stand: 2026-08-09

Entscheidung: `FAST_AFTERIMAGE_ONE_WAY_NO_ACTIVATION_FEEDBACK`

Implementierung: technischer Test

Formaler Forschungslauf: nein

## Auftrag

W3-K prueft, ob die in W3-J zugeschaltete neutrale schnelle Nachhallspur die
Aktivierungsdynamik veraendert. Jeder der vier visuellen und auditiven
Reihenfolgearme wird frisch mit und ohne Nachhall aufgebaut.

## Ablationspaar

```text
Nullbaseline: Feldantwortzeit 1.0 s, kein Nachhall
Kontrolle:    Feldantwortzeit 1.0 s, Nachhallzeit 0.5 s
Eingang:      pro Arm exakt identisch
```

Geprueft werden beide visuellen Arme aus W3-G und beide auditiven Arme aus
W3-H. Es gibt keine Zustandsfortsetzung zwischen den Armen.

## Ergebnis

Fuer alle vier Arme gilt:

- Aktivierung mit Nachhall ist bitgenau gleich der Aktivierung ohne Nachhall;
- die Nullbaseline besitzt einen globalen Nullnachhall;
- die Nachhallkontrolle besitzt einen nichtleeren Nachhall;
- die Snapshotdigests unterscheiden sich nur wegen des zusaetzlichen
  Nachhallzustands;
- Substrat und Entwicklung bleiben abwesend.

Die vorhandene schnelle Nachhallkomponente verfolgt die Aktivierung
einseitig. In diesem Pfad wirkt sie nicht auf die Aktivierung zurueck.

## Verifikation

```text
gezielter Consumertest: 8 passed
aktiver Architekturverbund: 219 passed
389 subtests passed
Aktivierung ohne Nachhall == mit Nachhall, vier von vier Armen
Nullbaseline-Nachhall == 0
Nachhallkontrolle != 0
substrate is None
development is None
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- W3-G bis W3-J als kontrollierte Reihenfolge- und Nachhallpaare;
- `NeutralFastAfterimageConfig(0.5)` aus `current_api`;
- oeffentliche Aktivierungs-, Nachhall- und Snapshotrollen;
- `current_api` als einziger Projektimport des Consumers.

## Aussagegrenze

W3-K belegt die einseitige Kausalrichtung der vorhandenen schnellen
Nachhallspur im kontrollierten Browserpayloadpfad. Gerade deshalb ist sie
kein reziprokes Substrat und kein MCM-Memory. Der Test belegt kein Lernen,
keine Feldzeit, inneren Kontext, Organisation, Semantik, Selbstregulation
oder KI. Es wurde kein Browser oder Playwright gestartet und keine Kamera,
kein Live-Mikrofon oder andere physische Sensorik aktiviert. Lauf 197 bleibt
unberuehrt.

## Bester naechster Schritt

W3-L fuehrt eine direkte Nachhall-Zustandsintervention vor identischer
Fortsetzung aus:

1. Ein gemeinsamer Zustand mit nichtleerem Nachhall wird genau einmal erzeugt.
2. Ein Arm behaelt ihn, im zweiten wird nur der Nachhall extern neutralisiert.
3. Aktivierung, Geometrie, Docks, Zeit und letzter Eingang bleiben identisch.
4. Beide Arme erhalten dieselbe spaetere kontrollierte reduzierte Sequenz.
5. Identische Aktivierungsfortsetzung trotz verschiedener Nachhallzustaende
   wuerde die einseitige Kausalrichtung interventionsbasiert bestaetigen.

## Spaeterer Umsetzungsstand W3-L

W3-L ist am 2026-08-09 umgesetzt worden. Nach einer reinen
Nachhallneutralisierung bleibt die Aktivierungsfortsetzung unter identischer
spaeterer Sequenz bitgenau gleich; nur der Nachhall bleibt verschieden. Der
aktive Architekturverbund besteht mit `220 passed` und 389 Subtests.
