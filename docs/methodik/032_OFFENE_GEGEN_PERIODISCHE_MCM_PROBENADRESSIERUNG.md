# Methodik 032: Offene gegen periodische MCM-Probenadressierung

## 1. Status

Vorregistrierter passiver Geometrievergleich auf Evidenzstufe E0.

Die bestehende `MCMNeuronLayer` bleibt unverändert. Eine periodische
Referenzadressierung darf ausschließlich im Versuch erzeugt werden und keinen
Zustand fortschreiben.

## 2. Forschungsfrage

Kann die zyklische Nachbarschaft der sieben Positionen aus der simulierten
Welt als reine technische Sensoranatomie abgebildet werden, sodass:

```text
offene und periodische Anatomie
→ im Inneren identische lokale Feldproben
→ nur an den beiden Rändern zusätzliche Wrap-Proben
→ keine Änderung von Aktivierung, Nachhall oder Rezeptorkontakt
```

Der Versuch fragt nicht, ob eine periodische Probe wirken soll.

## 3. Zu prüfende Behauptung

Für Positionen `p ∈ {0, 1, 2, 3, 4, 5, 6}` und die symmetrischen Offsets
`{-1, +1}` gelten zwei Adressierungen:

```text
open:
source = p + offset
Probe fehlt, wenn source außerhalb 0..6 liegt.

periodic:
source = (p + offset) modulo 7
```

Die erwartete Differenz ist vollständig vorgegeben:

```text
target 0 erhält periodisch zusätzlich source 6 bei offset -1
target 6 erhält periodisch zusätzlich source 0 bei offset +1
```

Alle anderen lokalen Proben müssen exakt übereinstimmen.

## 4. Feste technische Anatomie

Der Vergleich verwendet:

```text
Positionen       = (0,) ... (6,)
sample_offsets   = (-1,), (+1,)
offene Geometrie = simulated.field.line7.v1
Referenzgeometrie = simulated.field.ring7.reference.v1
```

Die Referenzgeometrie ist nur eine Versuchsrolle. Sie wird nicht als neue
Runtime-Geometrie registriert.

Jede Probe trägt weiterhin getrennt:

- Quellneuron,
- Quellfeld,
- abgeschlossenen Quelltick,
- relativen Offset,
- Aktivierung,
- Nachhall.

Es werden keine Gewichte, Kanten oder Beziehungen ergänzt.

## 5. Eingefrorene Signaturlage

Die Adressierung wird zuerst an einer vollständig unterscheidbaren
synthetischen Schichtlage geprüft:

```text
Position:    0    1    2    3    4    5    6
activation: 0.0  0.1  0.2  0.3  0.4  0.5  0.6
afterimage: 0.6  0.5  0.4  0.3  0.2  0.1  0.0
```

Alle Neuronen besitzen denselben Feld-, Modalitäts-, Geometrie- und Zeitbezug.
Die Werte dienen nur dazu, jede Quellprobe eindeutig zu erkennen. Sie werden
nicht als Feldregel interpretiert.

## 6. Offene Referenz B0

Die aktuelle `MCMNeuronLayer` erzeugt die offene Probenlage B0.

Ein passiver Übergangsobserver darf die ihm übergebene
`MCMFieldPerception` lesen. Er muss exakt den vorherigen eigenen
Aktivierungs- und Nachhallwert zurückgeben. Technische Identität, Position,
Aktivierung und Nachhall müssen deshalb mit dem eingefrorenen Eingangszustand
übereinstimmen. Die neue `perception` enthält dagegen erwartungsgemäß die
gerade beobachtete offene Probenlage und wird separat verglichen.

Der eingefrorene Eingangszustand selbst muss unverändert bleiben. Ein
vollständiger Schichtdigest wird nicht als Gleichheitskriterium verwendet,
weil die abgeschlossene Wahrnehmung eine neue legitime Zustandsrolle des
Ergebnisses ist.

B0 ist zugleich die Gegenprüfung, dass der Versuch die bestehende offene
Randbehandlung korrekt rekonstruiert.

## 7. Periodische Referenz P0

P0 berechnet aus derselben eingefrorenen Schichtlage ausschließlich die
Quellposition jeder lokalen Probe mit Modulo 7.

P0 darf nicht:

- `MCMNeuronLayer.advance` ersetzen,
- einen Neuronenzustand erzeugen,
- Aktivierung oder Nachhall verändern,
- Rezeptorkontakt lesen oder schreiben,
- eine Nachbarliste behalten,
- einen späteren Schritt beeinflussen.

Das Ergebnis von P0 ist nur eine unveränderliche Sammlung lokaler
Feldwahrnehmungen.

## 8. Exakte Positionsmatrix

Die erwarteten Quellpositionen sind:

| Ziel | Offen | Periodisch |
|---:|:---|:---|
| 0 | `(+1 → 1)` | `(-1 → 6), (+1 → 1)` |
| 1 | `(-1 → 0), (+1 → 2)` | identisch |
| 2 | `(-1 → 1), (+1 → 3)` | identisch |
| 3 | `(-1 → 2), (+1 → 4)` | identisch |
| 4 | `(-1 → 3), (+1 → 5)` | identisch |
| 5 | `(-1 → 4), (+1 → 6)` | identisch |
| 6 | `(-1 → 5)` | `(-1 → 5), (+1 → 0)` |

Es dürfen genau zwei zusätzliche gerichtete Proben auftreten. Zusammen bilden
sie einen symmetrischen technischen Randkontakt.

## 9. Reale Weltpfadfamilie

Zusätzlich zur Signaturlage werden alle 42 abgeschlossenen Feldfenster aus
Methodik 031 verwendet:

```text
7 Startpositionen
x 3 delta-Werte
x 2 äußere Ursachen
= 42 Zweige
= 21 Ursachenpaare
```

Die lokale Probenadressierung darf nur das jeweilige abgeschlossene
Feldfenster lesen.

Für jedes Ursachenpaar gilt:

```text
external gegen effector
→ äußere Provenienz verschieden
→ offene Probenlage gleich
→ periodische Probenlage gleich
```

Ursache, `delta`, Effort und Provenienzdigest dürfen in keiner Feldprobe
auftreten.

## 10. Rotationskontrolle

Die sieben zyklischen Umbenennungen

```text
p → (p + k) modulo 7, mit k = 0..6
```

werden vollständig geprüft.

Positionen, Trägeridentitäten und Zustandswerte werden gemeinsam rotiert. Das
periodische Probenergebnis muss exakt mitrotieren. Kein numerischer Ort darf
als Zentrum, Anfang oder bevorzugter Rand wirken.

## 11. Richtungsumkehr

Für jede der sieben Rotationen wird zusätzlich die technische Ringrichtung
umgekehrt:

```text
p → (-p + k) modulo 7
offset -1 ↔ offset +1
```

Damit entstehen insgesamt 14 starre Geometrietransformationen.

Nach kanonischer Rückabbildung müssen alle periodischen Probenergebnisse exakt
gleich sein. Die Vorzeichen der Offsets bleiben Koordinatenrichtungen und
werden nicht zu Rollen oder Wirkungswerten.

## 12. Mehrdeutigkeitskontrolle

Eine eigene Negativfamilie verwendet kleine periodische Achsen, bei denen
`-1` und `+1` für dasselbe Ziel auf denselben Quellträger fallen.

Solche Konfigurationen müssen abgelehnt werden. Die Referenz darf die beiden
Offsets weder:

- still zusammenfassen,
- doppelt zählen,
- durch Reihenfolge unterscheiden,
- noch mit Gewichten auseinanderhalten.

Der sieben Positionen breite Ring muss dagegen für jedes Ziel zwei
verschiedene Quellen besitzen.

## 13. Baseline-Ablationen

Aus identischen eingefrorenen Zuständen werden beide vorhandenen technischen
Baselines geprüft:

### B1: `hold_state_baseline`

```text
offene Proben gegen periodische Proben
→ identische Aktivierung
→ identischer Nachhall
```

### B2: `receptor_projection_baseline`

Bei identischem Rezeptorkontakt gilt:

```text
offene Proben gegen periodische Proben
→ identische Aktivierung gleich Rezeptorkontakt
→ identischer Nachhall gleich null
```

Diese Gleichheit ist ein erwarteter Nullbefund. Sie zeigt nur, dass beide
Baselines lokale Feldproben nicht als Wirkung lesen.

## 14. Observer- und Reihenfolgekontrolle

Der passive Observer wird in drei Varianten geprüft:

```text
kein Observer
leerer Observer
sammelnder Observer
```

Alle drei Varianten müssen denselben kanonischen Ergebnisdigest erzeugen.

Zielpositionen, Offsets, Weltzweige und die 14 Geometrietransformationen werden
jeweils auch in umgekehrter technischer Reihenfolge ausgewertet. Das Ergebnis
muss identisch bleiben.

## 15. Reset- und Restspurkontrolle

Nach einem vollständigen Neuaufbau der eingefrorenen Schicht darf die
periodische Referenz nur aus dem aktuellen Zustand dieselben Proben erneut
bilden.

Es darf nicht existieren:

- eine gespeicherte Wrap-Kante,
- eine Nutzungszahl,
- ein letzter Randpartner,
- eine Kontinuität,
- ein zusätzlicher Nachhall,
- ein Unterschied zwischen erstem und wiederholtem Lauf.

## 16. Entscheidungskriterien

Der technische Kandidat trägt nur, wenn gleichzeitig:

1. B0 die aktuelle offene Schicht exakt rekonstruiert.
2. P0 genau die beiden vorregistrierten Randproben ergänzt.
3. Alle inneren Proben exakt unverändert bleiben.
4. Jede periodische Probe Quellidentität, Offset, Aktivierung und Nachhall
   exakt bewahrt.
5. Alle 14 Geometrietransformationen äquivariant sind.
6. mehrdeutige kleine Geometrien abgelehnt werden.
7. alle 21 Ursachenpaare ab dem Feldfenster kollidieren.
8. B1 und B2 zwischen offener und periodischer Wahrnehmung exakt kollidieren.
9. Observer, Reihenfolge und Wiederholung neutral bleiben.
10. keine Runtime, Beziehung oder Effektorrolle geschrieben wird.

## 17. Scheiterkriterien

Die periodische Sensoranatomie bleibt geschlossen, wenn:

- sich eine innere Position verändert,
- mehr oder weniger als zwei Randproben hinzukommen,
- ein Randkontakt asymmetrisch ist,
- Rotation oder Richtungsumkehr das kanonische Ergebnis verändern,
- verschiedene Offsets auf dieselbe Quelle fallen und nicht abgelehnt werden,
- Ursache oder Intervention in die Probe gelangt,
- Aktivierung oder Nachhall durch die Referenz verändert werden,
- eine Probe über den Lauf hinaus gespeichert wird,
- die Prüfung eine Änderung der bestehenden Runtime benötigt.

## 18. Erwarteter Befund

Unter dem Vertrag aus Architektur 019 wird erwartet:

```text
Signale und innere lokale Proben bleiben identisch.
Nur 6 → 0 bei offset -1 und 0 → 6 bei offset +1 kommen hinzu.
Die vorhandenen Baselines erzeugen weiterhin identische Zustände.
```

Dies wäre ein technischer Anatomiebefund, keine MCM-Felddynamik.

## 19. Evidenzgrenze

Ein erfolgreicher Lauf kann höchstens tragen:

```text
periodische Referenzadressierung:            E1
technische Eignung für den Ringrezeptor:     E1
Integration in die MCMNeuronLayer-Runtime:   E0
kausale Wirkung lokaler Ringproben:          E0
entwickelte Beziehung oder Topologie:        E0
Eigenwirkung und Handlung:                   E0
Feldintelligenz:                             E0
```

## 20. Nicht freigegeben

- Änderung der `MCMNeuronLayer`,
- allgemeine Periodizität für andere Sensorfelder,
- Feldwirkung, Kopplung oder Ausbreitung,
- gespeicherte Beziehung oder Memory,
- Schwelle, Spike oder Gewinnerregel,
- Feld-zu-Effektor-Verbindung,
- Reward, Ziel, Semantik oder Reflexion.

## 21. Stärkstes Gegenargument

Ein positiver Lauf bestätigt nur, dass Modulo-Adressierung einen technisch
vorgegebenen Ring korrekt rekonstruiert. Die Ringstruktur stammt vollständig
aus dem Weltvertrag und ist nicht im MCM-Feld entstanden.

## 22. Bester nächster Schritt

Methodik 032 wird als isolierter passiver Referenzprüfer implementiert.

Erst nach einem exakten Befund wird entschieden, ob die periodische Randart als
optionale technische Eigenschaft der Neuronenschicht notwendig ist. Eine
Feldwirkung bleibt auch bei positivem Ergebnis geschlossen.
