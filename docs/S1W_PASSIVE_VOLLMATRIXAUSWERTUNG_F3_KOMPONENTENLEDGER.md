# S1-W: Passive Vollmatrixauswertung F3-Komponentenledger

Stand: 2026-08-09

Direkter Antrieb: `ACTIVATION_FORCING_REQUIRED_FOR_LATE_MIXTURE`

Rueckwirkung: `RECIPROCAL_BACKREACTION_CHANGES_LATE_LEDGER`

Mechanik: `COMPONENT_LEDGER_CONTAINS_BASELINE_DIFFERENT_INTERVAL`

Formaler Forschungslauf: nein

## Ziel

S1-W komponiert die 28 in S1-V gebundenen Ledgerzellen ueber F3, lineare
Baseline, `kappa=0`, `eta=0` und die Verfeinerungen 2/4 vollstaendig im
Speicher. Ursachenentscheidungen verwenden ausschliesslich die 12 kausal
geschachtelten spaeten Intervalle.

## Kontrollstatus

| Kontrolle | Ergebnis |
|---|---|
| 28 eindeutige Ledgerzellen | bestanden |
| 16 fruehe kumulative / 12 spaete geschachtelte Zellen | bestanden |
| Komponenten- und Massenbilanz | bestanden |
| Observertransparenz aller Arme | bestanden |
| `kappa=0`-Antrieb | exakt null |
| P0 und uniforme aktive Null | exakt null |
| lange Randzelle wiederholt | bitgleich |
| endliche lokale 2/4-Metriken | bestanden |

Der groesste Bilanzrest aller Zellen und Arme betraegt
`3.346118954833388e-16`.

## Kompaktergebnis

```text
nachweisbare direkte D-/A-Vektoren:       56 / 56
spaete F3-Anstiegsintervalle:              3 / 12
spaete F3-Abnahmeintervalle:               9 / 12
spaete kappa=0-Anstiegsintervalle:         0 / 12
eta-verschiedene spaete Intervalle:       12 / 12
maximaler linearer Komponentenrest:        0.05752400477029081
lineare Aequivalenzgrenze:                 0.05
```

## Geschachtelte spaete Richtungen

| Dosis | Quellenform | 0.2->0.4 s | 0.4->0.8 s | 0.8->1.6 s |
|---:|---|---|---|---|
| 1 | wiederholt | Anstieg | Abnahme | Abnahme |
| 1 | kontinuierlich | Anstieg | Abnahme | Abnahme |
| 8 | wiederholt | Abnahme | Abnahme | Abnahme |
| 8 | kontinuierlich | Anstieg | Abnahme | Abnahme |

Alle drei Anstiege liegen im ersten spaeten Intervall 0.200 bis 0.400
Sekunden. Danach nehmen alle vier Kurven in beiden verbleibenden Intervallen
ab. Dies praezisiert die S1-S-Rolle, ohne eine nachtraegliche Peakgrenze zu
setzen.

## Direkter Antrieb

```text
ACTIVATION_FORCING_REQUIRED_FOR_LATE_MIXTURE
```

Im `kappa=0`-Arm bleibt M aus der uniformen Ausgangslage in allen spaeten
Intervallen stabil. Keiner der drei aktiven Anstiege wird durch reinen
massenausgleichenden Transport reproduziert.

Damit ist der bereits implementierte aktivierungsgradientengetriebene
Beitrag `A` fuer die spaeten Anstiege technisch erforderlich. Dies ist keine
erlernte oder neu entstandene Funktion; `A` ist Bestandteil der festen
transparenten F3-Gleichung.

## Reziproke Rueckwirkung

```text
RECIPROCAL_BACKREACTION_CHANGES_LATE_LEDGER
```

F3 und `eta=0` unterscheiden sich in allen 12 spaeten Intervallen oberhalb
ihrer lokalen 2/4-Boeden. Die Rueckwirkung von M auf S veraendert damit die
spaetere Beitragsfolge quantitativ.

Dies zeigt einen wirksamen geschlossenen S-M-Kreis, aber weder Reflexion noch
inneren Dialog, Selbstwahrnehmung oder Selbstregulation.

## Lineare Mechanikgrenze

```text
COMPONENT_LEDGER_CONTAINS_BASELINE_DIFFERENT_INTERVAL
```

Mindestens ein direkter D- oder A-Beitragsvektor ueberschreitet die feste
lineare 5-Prozent-Grenze. Der groesste relative Rest betraegt rund 5.7524
Prozent.

Dieser Wert liegt nur 0.7524 Prozentpunkte oberhalb der Grenze. Gleichzeitig
blieben in S1-S die zusammengesetzten M-/Probeverlaeufe mit maximal 4.359
Prozent linear erklaert. Ein Komponentenunterschied kann sich durch
Gegenwirkung von D und A im Gesamtinkrement teilweise aufheben.

Der Befund ist deshalb kein Nachweis neuer Feldphysik oder eines
funktionalen Vorteils. Er ist ein gezielt zu lokalisierender und mit hoeherer
Verfeinerung zu replizierender enger Komponentenrest.

## Testergebnis

Der fokussierte, in einem frischen Prozess reproduzierte Verbund besteht mit:

```text
4 passed
28 subtests passed
122.12 s
```

Die bekannte Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen
Cachepfad.

## Aussagegrenze

S1-W belegt keine Praegung, kein Lernen, kein Vergessen, keine Feldzeit und
kein MCM-Memory. Die technische S-M-Rueckkopplung ist kein innerer Kontext
und keine Reflexion. Es gibt keinen Befund zu Semantik, Organisation,
Topologie, Selbstregulation oder KI.

Es gab keinen Browserstart, keine reale Sensorik, keinen externen Runner,
keinen Report und keine neue Laufnummer. Lauf 197 und die geschlossenen
Zweige bleiben unberuehrt.

## Bester naechster Schritt

S1-X registriert zuerst eine gezielte Replikation des knappen linearen
Komponentenrests. Sie lokalisiert betroffene Zelle und Beitragsrolle aus der
unveraenderten S1-W-Ausgabe und bindet fuer genau diese Treffer F3 gegen
lineare Baseline bei Verfeinerung 4 und 8.

Zusaetzlich werden D-/A-Einzelrest, Gesamtinkrementrest und ihre
Gegenwirkungsbilanz getrennt ausgegeben. Erst wenn der Komponentenrest bei
4/8 oberhalb 5 Prozent reproduziert und numerisch konvergent bleibt, darf
ueber einen weiterfuehrenden technischen Mechanikvergleich entschieden
werden.

## Spaeterer Replikationsstand S1-X

S1-X hat drei Treffer deterministisch lokalisiert und bei Verfeinerung 4/8
repliziert. Alle liegen im Aktivierungsantrieb der wiederholten Dosis 8 und
bleiben knapp oberhalb 5 Prozent. Sie zeigen die bekannte nichtlineare lokale
Massengewichtung gegen ihre Linearisierung, aber keinen neuen
Gleichungsbeitrag oder funktionalen Memoryvorteil.
