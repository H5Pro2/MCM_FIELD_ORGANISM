# Minimaler simulierter Effektorvertrag

## 1. Status

Architekturvertrag auf Evidenzstufe E0. Es existiert noch keine
Effektor-Runtime und keine Auslösung durch das MCM-Feld.

## 2. Zweck

Der erste Effektor soll ausschließlich einen geschlossenen technischen
Weltkreis prüfbar machen:

```text
begrenzte Wirkung
→ veränderte simulierte Welt
→ neuer Rezeptorkontakt
→ neues sensorspezifisches MCM-Feld
```

Er dient nicht dazu, ein Ziel zu erreichen, Verhalten auszuwählen oder Erfolg
zu bewerten.

## 3. Minimale simulierte Welt

Die Referenzwelt besitzt sieben feste lokale Positionen auf einem Ring:

```text
0 -- 1 -- 2 -- 3 -- 4 -- 5 -- 6 -- zurück zu 0
```

Genau eine anonyme normierte Weltanregung befindet sich zu jedem Zeitpunkt an
einer Position. Die Weltanregung ist kein Objekt, keine Person und kein
Zielträger. Sie ist nur eine kontrollierbare Quelle für einen lokalen
Rezeptorkontakt.

Der passive Rezeptorrahmen lautet:

```text
Kontakt an Weltposition p = 1.0
alle anderen Kontakte      = 0.0
```

Die Weltposition oder ihre Änderungsursache wird nicht als Zusatzinformation
an das MCM-Feld übergeben.

## 4. Genau eine Effektorwirkung

Die einzige technische Wirkungsfamilie ist eine lokale Translation:

```text
delta ∈ {-1, 0, +1}
p(t+1) = (p(t) + delta) modulo 7
```

Dabei bedeutet:

- `-1`: genau ein lokaler Schritt in negativer technischer Ringrichtung,
- `0`: keine Weltwirkung,
- `+1`: genau ein lokaler Schritt in positiver technischer Ringrichtung.

Die Vorzeichen sind Koordinatenrichtungen und keine Aktionsklassen. `+1` und
`-1` sind exakte inverse Wirkungen. Eine Folge `+1, -1` beziehungsweise
`-1, +1` muss zur vorherigen Weltposition zurückkehren.

## 5. Technische Wirkungsgrenze

Pro Weltintervall ist höchstens ein Betrag von einer Position zulässig:

```text
|delta| <= 1
```

Der technische Wirkungsaufwand wird transparent als `|delta|` ausgewiesen.
Diese Größe ist noch keine organisch entwickelte Energie oder Ressource. Sie
ist nur die feste Sicherheitsgrenze des simulierten Effektors.

Nicht verbrauchter Aufwand wird nicht gespeichert, angesammelt oder später
verstärkt.

## 6. Externe und eigene Ursache

Dieselbe Welttranslation kann zwei technisch getrennte Ursachen besitzen:

```text
external_perturbation
effector_intervention
```

Die Ursache ist ausschließlich für den äußeren Forschungsobserver sichtbar.
Bei identischer Ausgangsposition und identischem `delta` müssen beide Ursachen
exakt denselben nächsten Welt- und Rezeptorzustand erzeugen.

Das MCM-Feld erhält kein Eigenwirkungslabel. Es darf eine eigene Wirkung später
nur über deren erneut eintretende sensorische Weltfolge erfahren.

## 7. Kausale Zeitfolge

Jeder technische Weltzyklus ist atomar getrennt:

```text
1. abgeschlossener Weltzustand W(t)
2. höchstens eine extern vorgegebene Intervention E(t)
3. abgeschlossener neuer Weltzustand W(t+1)
4. Rezeptoraufnahme aus W(t+1)
5. späterer MCM-Feldschritt aus diesem Rezeptorrahmen
```

Eine in Schritt 5 entstehende Feldaktivität darf nicht rückwirkend die bereits
abgeschlossene Intervention aus Schritt 2 verändern.

Im ersten Lauf stammt `E(t)` ausschließlich aus dem Testtreiber. Es gibt keinen
Pfad vom MCM-Feld zum Effektor.

## 8. Reset

Der Reset setzt explizit:

- die Weltanregung auf eine vorab benannte technische Startposition,
- den letzten Interventionsursprung auf `none`,
- den letzten Wirkungsbetrag auf null,
- alle schnellen MCM-Zustände separat über ihren vorhandenen Resetvertrag.

Der Reset erzeugt keine zusätzliche Rezeptor- oder Feldwirkung. Erst eine
nachfolgende reguläre Weltaufnahme darf den Startzustand wieder an die
Rezeptorgrenze bringen.

## 9. Pflichtinvarianten

1. Die Welt enthält immer genau eine normierte Anregung.
2. Jede zulässige Intervention verändert höchstens eine lokale Ringposition.
3. `+1` und `-1` sind exakte Inversen.
4. Sieben gleichgerichtete Schritte kehren exakt zur Ausgangsposition zurück.
5. `delta = 0` verändert die Welt nicht.
6. Identische externe und Effektorinterventionen erzeugen identische
   Weltfolgen.
7. Die Ursachenkennung gelangt nicht in den Rezeptorrahmen.
8. Der Rezeptor liest nur den abgeschlossenen neuen Weltzustand.
9. Technische Auswertungsreihenfolge verändert kein Ergebnis.
10. Der Observer verändert weder Welt noch Intervention noch Rezeptorrahmen.
11. Ungültige Beträge und mehrere Interventionen im selben Intervall werden
    abgelehnt.
12. Reset ist vollständig und reproduzierbar.

## 10. Verbindliche Null- und Gegenprüfungen

```text
N0: delta = 0
N1: +1 gefolgt von -1
N2: -1 gefolgt von +1
N3: siebenmal +1
N4: siebenmal -1
N5: externe Translation gegen identische Effektortranslation
N6: Observer an gegen Observer aus
N7: vertauschte unabhängige Auswertungsreihenfolge
N8: vollständiger Reset
```

## 11. Nicht freigegeben

- Verbindung eines MCM-Neurons mit `delta`,
- Schwelle oder Vorzeichenregel zur Effektorwahl,
- Gewinnerneuron oder Aktionsauswahl,
- Reward, Zielposition oder Sollzustand,
- Vermeidung, Annäherung oder Selbsterhaltung,
- adaptive Effektorstärke,
- reale Hardware- oder Systemsteuerung,
- Internet- oder Browserwirkung,
- Beziehungsmemory, Reflexion oder Syntax.

## 12. Abgrenzung zur Handlung

Eine extern ausgelöste reversible Translation ist noch keine Handlung des
Organismus. Sie beweist nur:

```text
eine begrenzte Wirkung kann die Welt verändern
+ diese Änderung kann ausschließlich über Rezeptoren zurückkehren
```

Von Eigenwirkung darf erst gesprochen werden, wenn eine spätere, separat
begründete Feldursache den Effektor kausal auslöst. Auch dann wären Ziel,
Auswahl und Organisation noch getrennt zu prüfen.

## 13. Evidenzgrenze

Ein erfolgreicher Vertragstest kann höchstens tragen:

```text
deterministische reversible Simulationswelt: E1
technische Effektor-Welt-Rezeptor-Kette:      E1
Eigenwirkung des MCM-Feldes:                  E0
Handlung:                                     E0
organische Feldorganisation:                  E0
Feldintelligenz:                              E0
```

## 14. Bester nächster Schritt

Methodik 030 registriert zuerst den unveränderlichen Welt-, Interventions- und
Rezeptorvertrag samt N0 bis N8.

Erst nach bestandenem passivem Vertragstest darf die transparente technische
Kette bis zu einem MCM-Feldfenster geführt werden. Eine Feldauslösung bleibt
weiter geschlossen.
