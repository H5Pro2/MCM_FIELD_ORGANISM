# Einheitlicher Interventionsvertrag für die Verdeckungswelt

## Status

```text
einheitliche Weltgrundlage:                 Verdeckungswelt
Interventionsvertrag:                       konzeptionell festgelegt
sichtbare Konsequenz:                       darstellbar
verdeckte Konsequenz:                       darstellbar
Nullkonsequenz:                             darstellbar
blockierte aktuelle Rückkehr:               weltseitig darstellbar
erneuter Weltkontakt:                       darstellbar
Provenienz und Konsequenz-ID im Feld:        ausgeschlossen

Runtime-Code:                               nicht ergänzt
Organismusmechanik:                         nicht ergänzt
Memory- oder Sperrvariable:                 nicht ergänzt
passiver Lauf:                              als nächster Schritt freigegeben
```

Dieser Vertrag schließt die im
[Darstellbarkeitsaudit](093_DARSTELLBARKEITSAUDIT_WELT_KONSEQUENZFAELLE.md)
gefundene Lücke konzeptionell. Er legt ausschließlich die äußere Testwelt fest.

Die Ringwelt bleibt unverändert als Vergleichs- und Kontrollwelt erhalten. Sie
wird im ersten Nachweis nicht mit der Verdeckungswelt vermischt.

## 1. Forschungsrolle

Die Verdeckungswelt muss folgende Folge innerhalb einer einzigen kausalen
Weltmechanik tragen:

```text
sichtbarer Kontakt
-> äußere Weltintervention
-> messbare Weltkonsequenz
-> sichtbare oder verdeckte Fortsetzung
-> regulärer Rezeptorkontakt oder reguläre Kontaktabwesenheit
-> erneuter sichtbarer Weltkontakt
```

Der Vertrag prüft noch keine Feldbeziehung und kein Memory. Er schafft nur
eine kontrollierte Weltgrundlage für den späteren passiven Kausalnachweis.

## 2. Unveränderter Weltzustand

Die Verdeckungswelt besitzt bereits die äußeren Zustandsrollen:

```text
q(t)    lokale Position
d(t)    lokale Bewegungsrichtung
v       konstante lokale Geschwindigkeit
O       feste Verdeckungsmaske
t       Weltzeit
```

Diese Größen gehören ausschließlich der simulierten Außenwelt.

Sie werden nicht an folgende Rollen übergeben:

- visuelle Rezeptorfläche;
- Rezeptorenverteiler;
- MCM-Dock;
- MCM-Neuron;
- gemeinsames MCM-Feld;
- späteren semantischen Leser.

Der Organismus erhält nur die reguläre sichtbare Projektion der Außenwelt.

## 3. Sichtbare Projektion

Die Projektion bleibt dieselbe wie in der bestehenden Verdeckungswelt:

```text
q(t) außerhalb O
-> lokaler sichtbarer Kontakt an q(t)

q(t) innerhalb O
-> regulärer kontaktfreier Bildrahmen
```

Die Verdeckung:

- stoppt den Weltprozess nicht;
- stoppt den Rezeptor nicht;
- erzeugt kein Sperrbit;
- kennzeichnet keinen Sonderzustand im MCM;
- löscht keinen bereits erzeugten Rezeptorrahmen;
- verändert nicht die Interventionsregel.

Kontaktabwesenheit entsteht damit in der Weltprojektion und nicht durch eine
Sperrregel im Organismus.

## 4. Äußere Intervention

Die kleinste anonyme Intervention verändert ausschließlich die bereits
vorhandene Bewegungsrichtung.

Der äußere Interventionswert lautet:

```text
s ∈ {-1, +1}
```

Seine technische Wirkung ist:

```text
d'(t) = s * d(t)
q(t + 1) = q(t) + d'(t) * v
```

Dabei gilt:

```text
s = +1 -> Nullkonsequenz: Richtung bleibt erhalten
s = -1 -> Konsequenz: Richtung kehrt sich um
```

Die Begriffe `Nullkonsequenz` und `Konsequenz` sind
Forschungsbeschreibungen. Im Weltzustand stehen nur `q`, `d`, `v`, `O` und
`t`.

Die Intervention:

- fügt kein Objekt hinzu;
- enthält keine Bedeutung;
- enthält keinen Reward;
- bezeichnet weder Erfolg noch Fehler;
- wählt keine Handlung des Organismus;
- schreibt nicht in das MCM;
- verändert keine Rezeptor- oder Feldregel.

## 5. Gleiche Ursache vor und während der Verdeckung

Die Interventionsgleichung gilt unabhängig von der Sichtbarkeit:

```text
q(t) außerhalb O:
d'(t) = s * d(t)

q(t) innerhalb O:
d'(t) = s * d(t)
```

Nur die Projektion unterscheidet sich:

```text
sichtbarer Eingriff:
veränderter Weltverlauf kann aktuell rezeptorisch erscheinen

verdeckter Eingriff:
veränderter Weltverlauf besteht,
aktuelle Rezeptorprojektion bleibt kontaktfrei,
sofern auch q(t + 1) innerhalb O liegt
```

Damit bleibt die Weltursache in beiden Fällen identisch. Es wird keine
besondere verborgene Interventionsmechanik eingeführt.

## 6. Observerseitige Provenienz

Der äußere Forschungsobserver darf nach einem abgeschlossenen Weltlauf lesen:

```text
intervention_family_id
event_id
source_tick
s
Weltzustand vor der Intervention
Weltzustand nach der Intervention
Sichtbarkeit zum Interventionszeitpunkt
```

Diese Rollen gehören ausschließlich zum äußeren Prüfprotokoll.

Verbindlich gilt:

```text
gleiche Weltfolge
+ verschiedene event_id oder Provenienzkennung
-> identische sichtbare Projektion
-> identischer Rezeptorrahmen
-> identische MCM-Feldlage
```

`event_id` und `intervention_family_id` dürfen nicht in Weltprojektion,
Rezeptorrahmen, Dock, Neuron oder Feldfenster vorkommen.

Dieselbe `intervention_family_id` wird für sichtbare und verdeckte
Richtungsänderungen verwendet. Sichtbarkeit erzeugt keine neue
Konsequenzklasse.

## 7. Nullkonsequenz

Die Nullkonsequenz verwendet denselben Weltübergang und dieselbe Zeitfolge:

```text
gleicher Ausgangsweltzustand
+ s = +1
-> Richtung bleibt erhalten
-> normale Weltfortsetzung
```

Sie ist:

- kein ausgelassener Interventionsaufruf;
- kein stehen gebliebener Weltprozess;
- kein Reset;
- kein kopierter Folgezustand;
- kein besonderer Rezeptorrahmen.

Weltzeit, Projektionszeit und Organismuszeit schreiten in Konsequenz- und
Nullzweig gleich fort.

## 8. Blockierte Rückkehr als Weltbedingung

Eine blockierte aktuelle Rückkehr liegt genau dann vor, wenn:

```text
s = -1
+ q(t) und q(t + 1) innerhalb O
-> d(t) ändert sich in der Außenwelt
-> Weltprozess setzt sich mit d'(t) fort
-> aktuelle sichtbare Projektion bleibt kontaktfrei
```

Liegt `q(t + 1)` bereits außerhalb von `O`, handelt es sich um einen regulären
sichtbaren Austritt und nicht um eine blockierte aktuelle Rückkehr.

Der Begriff `blockiert` bezeichnet nur die fehlende Sichtlinie der Welt.

Nicht blockiert werden:

- Bildgenerator;
- visuelle Rezeptorfläche;
- Rezeptoradapter;
- Verteiler;
- Dock;
- MCM-Neuronenschicht;
- Observer.

Der kontaktfreie Bildrahmen durchläuft den vollständigen regulären
Rezeptor-MCM-Pfad.

## 9. Erneuter Weltkontakt

Nach der Verdeckung entwickelt sich derselbe Weltzustand weiter:

```text
q(t + n) außerhalb O
-> erneuter lokaler sichtbarer Kontakt
```

Der erneute Kontakt enthält nur die aktuelle sichtbare Projektion.

Er enthält nicht:

- frühere `event_id`;
- Information, dass eine Intervention stattgefunden hat;
- die Bezeichnung `Konsequenz`;
- die Bezeichnung `Wiederkehr`;
- ein Objektlabel;
- eine erwartete Feldreaktion.

Ein späterer Unterschied zwischen Konsequenz- und Nullzweig ist in diesem
Weltvertrag zunächst vollständig durch die fortgesetzte äußere Weltlage
erklärbar. Er ist kein Memory-Befund.

## 10. Gemeinsame kausale Zweigfamilie

Alle Zweige verwenden dieselbe Weltgeometrie, Zustandsklasse,
Interventionsgleichung und Projektionsregel.

### V0: sichtbare Nullkonsequenz

```text
q außerhalb O
+ s = +1
-> Richtung bleibt
-> aktuelle sichtbare Fortsetzung
```

### V1: sichtbare Konsequenz

```text
q außerhalb O
+ s = -1
-> Richtung kehrt um
-> veränderte sichtbare Fortsetzung
```

### H0: verdeckte Nullkonsequenz

```text
q innerhalb O
+ s = +1
-> Richtung bleibt
-> aktuelle Projektion kontaktfrei
-> späterer Austritt gemäß unveränderter Richtung
```

### H1: verdeckte Konsequenz

```text
q innerhalb O
+ s = -1
-> Richtung kehrt um
-> aktuelle Projektion kontaktfrei
-> späterer Austritt gemäß veränderter Richtung
```

### P0: Provenienznull

```text
gleiche q-, d-, v-, O-, t- und s-Folge
+ andere observerseitige event_id
-> identische Weltfolge und Projektion
```

## 11. Paarbedingungen

Für jedes Vergleichspaar gelten:

```text
gleiche Startposition
gleiche Startrichtung
gleiche Geschwindigkeit
gleiche Verdeckungsmaske
gleiche Weltzeit
gleiche Reizstärke
gleiche technische Framezahl
gleiche Rezeptorgeometrie
gleiche MCM-Anatomie
```

Konsequenz gegen Nullkonsequenz unterscheidet ausschließlich `s`.

Sichtbar gegen verdeckt wird nicht als primärer Wirkungseffekt verglichen.
Diese Zweige prüfen verschiedene Projektionslagen derselben
Interventionsregel.

## 12. Kausale Zeitordnung

Die verbindliche Reihenfolge lautet:

```text
1. vollständiger Weltzustand W(t)
2. äußerer Interventionswert s(t)
3. abgeschlossener Folgeweltzustand W(t + 1)
4. sichtbare Projektion aus W(t + 1) und O
5. regulärer Rezeptorrahmen
6. reguläres MCM-Feldfenster
7. passiver Observer nach Abschluss
```

Der Observer darf keine Phase auswählen, wiederholen, verlängern oder in eine
folgende Phase zurückschreiben.

## 13. Kanonische Trennung der Digests

Der spätere passive Lauf muss getrennte Digests führen.

### Weltzustandsdigest

Enthält:

```text
t
q
d
v
O
```

### Weltübergangsdigest

Enthält:

```text
vorheriger Weltzustand
s
folgender Weltzustand
```

### Projektionsdigest

Enthält nur den tatsächlich sichtbaren Bildzustand.

### Rezeptordigest

Enthält nur die reguläre Rezeptorprojektion.

### Provenienzdigest

Enthält zusätzlich die observerseitigen Kennungen.

Verbindliche Kollisionsregel:

```text
gleicher Weltzustand und gleiche Projektion
+ andere observerseitige Provenienz
-> gleiche Projektions-, Rezeptor- und MCM-Digests
```

## 14. Keine neue Organismusmechanik

Der Vertrag ergänzt konzeptionell nur die Ursache-Wirkungs-Beschreibung der
Testwelt.

Er führt nicht ein:

- Organismushandlung;
- Effektorsteuerung;
- Aufmerksamkeit;
- Erwartung;
- Inhibition;
- Memory;
- Beziehungsspeicher;
- semantische Rolle;
- adaptive Kopplung;
- Energie- oder Ressourcenvariable.

Die Richtungsänderung ist eine äußere Weltintervention. Sie ist keine
Entscheidung des MCM.

## 15. Zulässige erste Aussage

Der erste passive Lauf darf höchstens zeigen:

```text
sichtbare Weltkonsequenz
-> kausal veränderte aktuelle Rezeptorlage
-> kausal veränderte aktuelle MCM-Feldlage

verdeckte Weltkonsequenz
-> veränderter äußerer Weltzustand
-> aktuell kontaktfreie reguläre Rezeptorlage
-> kein aktueller Konsequenzinhalt im MCM
```

Der spätere Austritt zeigt nur, dass der äußere Weltprozess während der
Verdeckung weiterlief.

Er zeigt nicht:

- dass das MCM die Konsequenz gespeichert hat;
- dass eine Feldbeziehung entstand;
- dass das System die Weltursache erkannte;
- dass Semantik oder Lernen vorliegt.

## 16. Stopplinie

Der passive Lauf wird nicht begonnen, wenn seine Umsetzung:

- ein Sichtbarkeits- oder Konsequenzflag an den Rezeptor übergibt;
- die Interventions-ID in den Organismuszustand schreibt;
- für H1 einen anderen Weltübergang als für V1 verwendet;
- den Rezeptor während der Verdeckung technisch aussetzt;
- einen Nullvektor erst nach der Rezeptoranalyse erzwingt;
- den späteren Austritt als Memory-Ausgabe bewertet;
- Ringwelt und Verdeckungswelt innerhalb eines Kausalpaars vermischt.

## 17. Freigabeentscheidung

Der Vertrag kann alle geforderten Fälle innerhalb einer einzigen
Verdeckungswelt kausal kontrollieren:

```text
sichtbare Konsequenz:          V1
sichtbare Nullkonsequenz:      V0
verdeckte Konsequenz:          H1
verdeckte Nullkonsequenz:      H0
observerseitige Provenienz:    P0
erneuter Kontakt:              natürliche Fortsetzung von H0 und H1
```

Damit ist die konzeptionelle Darstellbarkeitslücke geschlossen.

Freigegeben ist als nächster Schritt ausschließlich ein passiver Lauf der
Welt-, Projektions-, Rezeptor- und aktuellen MCM-Kausalkette.

Nicht freigegeben bleiben Holdout-Memory, Feldbeziehungsmechanik und jede
Rückschreibung.

## 18. Wie es am besten weitergeht

Als nächster Durchlauf wird die passive Methodik für V0, V1, H0, H1 und P0
exakt vorregistriert. Sie muss Zeitpunkte, Paarungen, Digests,
Reihenfolgekontrollen und zulässige Aussagen festlegen.

Erst danach wird der minimale passive Testlauf implementiert. Die bestehende
Organismus-Runtime bleibt dabei unverändert.
