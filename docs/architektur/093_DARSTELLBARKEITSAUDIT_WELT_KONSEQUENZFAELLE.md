# Darstellbarkeitsaudit der Welt-Konsequenzfälle

## Status

```text
Audit:                                      abgeschlossen
neuer Testcode:                             nicht erzeugt
neue Weltmechanik:                          nicht erzeugt
neue Speichergröße:                         nicht erzeugt

Konsequenz:                                 darstellbar
Nullkonsequenz:                             darstellbar
Provenienz der Weltquelle:                  observerseitig darstellbar
blockierte Rückkehr in derselben Welt:      nicht darstellbar

gesamte Testfamilie eindeutig darstellbar:  nein
passiver Lauf:                              noch nicht freigegeben
```

Der Audit prüft ausschließlich die vorhandenen Welt- und
Rezeptorschnittstellen. Er verändert weder Runtime noch Testwelt.

Grundlage ist die
[Vorregistrierung der anonymen Welt-Konsequenz-Testfamilie](092_VORREGISTRIERUNG_ANONYME_WELT_KONSEQUENZ_TESTFAMILIE.md).

## 1. Auditfrage

```text
Können Konsequenz, Nullkonsequenz, blockierte Rückkehr
und observerseitige Provenienz mit den vorhandenen
Welt- und Rezeptorschnittstellen eindeutig, anonym
und kausal in einer kontrollierten Testfamilie dargestellt werden?
```

Die Fälle müssen nicht nur einzeln irgendwo im Projekt vorkommen. Sie müssen
innerhalb einer gemeinsamen kausalen Weltfamilie so vergleichbar sein, dass
kein Wechsel der Weltmechanik den gemessenen Unterschied erklärt.

## 2. Geprüfte vorhandene Schnittstellen

### Simulierter Effektor-Weltvertrag

Die vorhandene `SimulatedEffectorWorld` besitzt:

```text
SimulatedWorldState:
tick
position

WorldIntervention:
source_tick
delta
cause

SimulatedWorldReceptorFrame:
source_tick
contact_values
```

Der Weltübergang lautet unverändert:

```text
next_position = (previous_position + delta) modulo 7
```

Zulässig sind:

```text
delta = -1, 0, +1
cause = external, effector
```

`cause = effector` ist nur technische Provenienz. Es existiert weiterhin kein
Feld-zu-Effektor-Pfad.

### Simulierter Welt-Rezeptor-MCM-Pfad

Der vorhandene Adapter liest aus dem abgeschlossenen
`SimulatedWorldReceptorFrame` ausschließlich:

```text
source_tick
contact_values
```

Er besitzt keinen Zugriff auf:

```text
cause
delta
effort
vorherigen Weltzustand
Provenienzdigest
```

Damit bleibt technische Herkunft außerhalb des Feldes.

### Vorhandene Verdeckungswelt

Die vorhandene `OccludedContinuationWorld` kann eine leere sichtbare
Weltprojektion erzeugen:

```text
verdeckte Weltphase
-> schwarzer Bildrahmen
-> reguläre visuelle Rezeptoranalyse
-> kein aktiver visueller Kontakt
```

Die Verdeckung ist dort eine Weltbedingung. Der Rezeptorpfad wird nicht
technisch übersprungen.

Diese Verdeckungswelt ist jedoch eine eigene Weltfamilie. Sie besitzt nicht
den Interventions- und Provenienzvertrag der `SimulatedEffectorWorld`.

## 3. Fall A: Konsequenz

### Vorhandene Darstellung

```text
gleicher SimulatedWorldState
+ delta = -1 oder +1
-> andere position im abgeschlossenen Folgezustand
-> anderer one-hot Rezeptorkontakt
-> andere aktuelle MCM-Aktivierung
```

Die Konsequenz ist eine messbare räumliche Änderung der Weltquelle. Sie ist
keine Bedeutung und kein Ergebnislabel.

### Entscheidung

```text
eindeutig:  ja
anonym:     ja
kausal:     ja
```

## 4. Fall B: Nullkonsequenz

### Vorhandene Darstellung

```text
gleicher SimulatedWorldState
+ delta = 0
-> Weltzeit schreitet um einen Takt fort
-> position bleibt identisch
-> Rezeptorkontakt bleibt an derselben Position
```

Die Nullkonsequenz ist ein regulärer Weltübergang. Sie ist kein Reset und kein
Auslassen eines Takts.

### Entscheidung

```text
eindeutig:  ja
anonym:     ja
kausal:     ja
```

## 5. Fall C: Provenienz der Weltquelle

### Vorhandene Darstellung

Die Weltintervention kann dieselbe räumliche Folge mit verschiedener
technischer Ursache erzeugen:

```text
gleicher Ausgangszustand
+ gleiches delta
+ verschiedene cause
-> gleiche Weltfolge
-> gleicher Rezeptorrahmen
-> gleiche MCM-Feldlage
```

Nur der Provenienzdigest des abgeschlossenen äußeren Weltübergangs darf sich
unterscheiden.

Die Bezeichnung `effector` ist keine organismische Handlung. Sie bleibt eine
äußere Testkennung.

### Entscheidung

```text
observerseitig eindeutig:      ja
im Feld vorhanden:             nein
für die Leckkontrolle geeignet: ja
```

Diese Trennung entspricht der geforderten Grenze.

## 6. Fall D: blockierte Rückkehr

### Erforderliche Darstellung

```text
Weltkonsequenz entsteht
+ Weltbedingung verhindert ihre aktuelle Sichtbarkeit
-> regulärer Rezeptorrahmen ohne Konsequenzkontakt
-> kein künstlich blockierter Organismuspfad
```

### Grenze der Ringwelt

`SimulatedWorldState` enthält nur:

```text
tick
position
```

Jeder Zustand erzeugt zwingend einen exakt one-hot codierten
`SimulatedWorldReceptorFrame`. Ein Rahmen ohne aktiven Kontakt wird von dieser
Schnittstelle ausdrücklich abgelehnt.

Die Ringwelt besitzt keine vorhandene weltseitige Rolle für:

- Verdeckung;
- fehlende Sichtlinie;
- außerhalb der Rezeptorreichweite;
- neutralen Hintergrund ohne Kontakt;
- getrennten verborgenen und sichtbaren Weltzustand.

Das Auslassen von `receptor_frame_from_world`, das Unterbrechen des Adapters
oder das Verwerfen eines fertigen Rezeptorrahmens wäre eine technische Sperre
im Wahrnehmungspfad. Das ist nach der Vorregistrierung unzulässig.

### Grenze der Verdeckungswelt

Die vorhandene `OccludedContinuationWorld` kann zwar einen regulären
kontaktfreien visuellen Rezeptorrahmen erzeugen. Sie besitzt aber keinen
`WorldIntervention`-Übergang, keine gepaarte Nullkonsequenz und keinen
zugehörigen Provenienzvertrag.

Ein Konsequenzzweig aus der Ringwelt und ein Blockadezweig aus der
Verdeckungswelt wären deshalb keine kontrollierten Gegenfakten. Der
Mechanikwechsel könnte jeden Unterschied erklären.

### Entscheidung

```text
als allgemeine Weltbedingung vorhanden:        ja
in der Konsequenzwelt vorhanden:               nein
innerhalb derselben Testfamilie kontrollierbar: nein
```

## 7. Gesamtmatrix

| Fall | Vorhandene Welt | Regulärer Rezeptorpfad | Observerneutral | Gemeinsam kontrollierbar |
|---|---|---:|---:|---:|
| Konsequenz | Ringwelt | ja | ja | ja |
| Nullkonsequenz | Ringwelt | ja | ja | ja |
| Provenienz | Ringwelt | ja, ohne Provenienzfeld | ja | ja |
| blockierte Rückkehr | Verdeckungswelt | ja | ja | nein |

Die letzte Spalte ist für die Freigabe entscheidend.

## 8. Nicht zulässige Abkürzungen

Die fehlende Darstellung darf nicht ersetzt werden durch:

- ein `blocked`-Flag im MCM;
- ein Sperrbit im Rezeptoradapter;
- das Nichtaufrufen des Rezeptors;
- das Löschen eines fertigen Rezeptorrahmens;
- einen künstlichen Nullvektor nach der Weltprojektion;
- eine Memory-, Aufmerksamkeits- oder Inhibitionsvariable;
- eine neue Bedeutungsrolle wie `nicht sichtbar`;
- den Vergleich zweier verschiedener Weltmechaniken als wären sie ein
  kausales Paar.

## 9. Schlussfolgerung

Drei der vier Fälle sind in der bestehenden Ringwelt eindeutig, anonym und
kausal darstellbar:

```text
Konsequenz
Nullkonsequenz
observerseitige Provenienz
```

Die blockierte Rückkehr ist nur in einer anderen vorhandenen Weltfamilie
darstellbar. Damit kann die vollständig vorregistrierte Testfamilie noch nicht
als ein gemeinsamer kontrollierter Weltvertrag ausgeführt werden.

Der Audit ist deshalb negativ:

> Die vorhandenen Schnittstellen tragen alle benötigten Einzelrollen, aber
> noch nicht ihre kausal kontrollierte Vereinigung in derselben
> Konsequenzwelt.

Dies ist keine fehlende Memory-Funktion und kein Grund, einen
Organismuszustand zu ergänzen.

## 10. Freigabegrenze

```text
passiver Konsequenzlauf:        gesperrt
Holdoutlauf:                    gesperrt
neue Memory-Mechanik:           gesperrt
neue Organismus-Sperrregel:     gesperrt
konzeptionelle Weltprüfung:     freigegeben
```

## 11. Wie es am besten weitergeht

Als nächster Schritt muss ausschließlich konzeptionell entschieden werden,
welche bereits vorhandene Weltfamilie die gemeinsame Grundlage bilden kann:

1. Kann die Ringwelt ohne Bedeutungsrolle als sichtbare Projektion eines
   bereits vorhandenen äußeren Zustands verstanden werden?
2. Oder kann die vorhandene Verdeckungswelt Konsequenz und Nullkonsequenz als
   reale Weltübergänge tragen, ohne neue Organismusmechanik einzuführen?

Die Entscheidung muss eine einzige abgeschlossene Weltfamilie ergeben, in der
sichtbare Konsequenz und weltseitig verdeckte Konsequenz dieselbe zugrunde
liegende Dynamik besitzen.

Bis diese Frage ohne zusätzliche künstliche Zustände beantwortet ist, bleibt
der passive Lauf geschlossen.
