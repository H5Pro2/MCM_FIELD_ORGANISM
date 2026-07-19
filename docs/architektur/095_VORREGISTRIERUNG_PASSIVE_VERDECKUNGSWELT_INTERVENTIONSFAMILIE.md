# Vorregistrierung: passive Interventionsfamilie der Verdeckungswelt

## Status

```text
Weltmethodik V0, V1, H0, H1, P0:        vorregistriert
deterministische Welt- und Rezeptorfolge: verbindlich
künstliches Rauschen:                    ausgeschlossen
künstliche Varianzregel:                 ausgeschlossen
Nullpunkt- oder Ruhepunktdynamik:         ausgeschlossen
neue Organismusmechanik:                 ausgeschlossen
neue Speichergröße:                      ausgeschlossen
spätere Feldantwort als Auswahlkriterium: ausgeschlossen
minimaler passiver Lauf:                  danach freigegeben
```

Diese Methodik operationalisiert den
[einheitlichen Interventionsvertrag der Verdeckungswelt](094_EINHEITLICHER_INTERVENTIONSVERTRAG_VERDECKUNGSWELT.md).

Sie ergänzt keine Mechanik. Sie legt vor dem Lauf Weltgeometrie,
Interventionszeitpunkte, Zweigpaare, Budgets, Holdoutfortsetzungen,
Observergrenzen und zulässige Aussagen fest.

## 1. Enge Forschungsfrage

Der passive Lauf darf ausschließlich prüfen:

```text
deterministische Weltregel
-> sichtbare Weltprojektion
-> regulärer visueller Rezeptorkontakt
-> aktuelle MCM-Feldlage
```

Zusätzlich wird als Weltkontrolle geprüft:

```text
dieselbe Weltintervention innerhalb der Verdeckung
-> veränderter äußerer Weltzustand
-> aktuell kontaktfreie sichtbare Projektion
-> späterer, durch die Außenwelt bestimmter Austritt
```

Der zweite Pfad ist kein Memory-Test. Er weist nur nach, dass die
Weltkonsequenz während fehlender Sichtbarkeit fortbesteht.

## 2. Verbindlicher Ausschluss künstlicher Dynamik

Der Lauf erzeugt intern nicht:

- weißes, farbiges oder zufälliges Rauschen;
- Jitter;
- zufällige Startlagen;
- zufällige Amplituden;
- zufällige Interventionszeitpunkte;
- künstliche Varianz;
- Varianzverstärkung oder Varianzunterdrückung;
- Nullpunktanziehung;
- Ruhepunktdynamik;
- spontane Rückkehr zu einem Mittelwert;
- künstliche Relaxation der Welt;
- zusätzliche Feldstimulation;
- geglättete Rezeptorwerte;
- Rauschunterdrückung im MCM.

Alle Welt- und Rezeptorfolgen sind vollständig deterministisch.

Reales Sensorrauschen ist in diesem simulierten Lauf nicht vorhanden. In
späteren Live-Läufen darf gemessenes Sensorrauschen nur als Eigenschaft des
realen Weltkontakts auftreten. Es darf ausschließlich observerseitig
dokumentiert und weder intern erzeugt noch als Bedeutung interpretiert
werden.

## 3. Gemeinsame Weltgeometrie

Alle Zweige verwenden dieselbe eindimensionale visuelle Welt:

```text
Positionen q:              0, 1, 2, 3, 4, 5, 6, 7, 8
Geschwindigkeit v:         1 Position pro Weltintervall
Verdeckungsmaske O:        3, 4, 5
sichtbarer linker Bereich: 0, 1, 2
sichtbarer rechter Bereich:6, 7, 8
```

Die visuelle Rezeptorfläche besitzt neun lokale Positionsträger mit
verlustfreier 1:1-Dockzuordnung.

Für sichtbare Weltlagen gilt:

```text
genau ein lokaler visueller Kontakt
alle übrigen visuellen Kontaktwerte = 0
```

Für verdeckte Weltlagen gilt:

```text
alle visuellen Kontaktwerte = 0
```

Der kontaktfreie Rahmen wird durch die reguläre visuelle Projektion erzeugt.
Er wird nicht nach der Rezeptoranalyse hergestellt.

## 4. Gemeinsame Weltregel

Jeder Zweig verwendet:

```text
s ∈ {-1, +1}
d'(t) = s * d(t)
q(t + 1) = q(t) + d'(t) * v
```

Dabei gilt:

```text
s = +1: Richtungserhaltung
s = -1: Richtungsumkehr
```

Es existiert keine zweite Regel für verdeckte Weltlagen.

Die Sichtbarkeit wird erst nach Abschluss des Weltübergangs aus `q(t + 1)`
und `O` bestimmt.

## 5. Feste technische Reizlage

Alle Zweige verwenden dieselben technischen Reizeigenschaften:

```text
eine visuelle Zeile
ein visueller Farbkanal
eine konstante ungeclippte Reizstärke
eine konstante lokale Ausdehnung
keine Audiospur
keine zweite Modalität
keine Hintergrundvariation
```

Die konkreten Werte werden einmal im Testmodul als technische Konstanten
festgelegt. Sie dürfen nicht aus Zweig, Intervention, Observerkennung oder
späterem Ergebnis abgeleitet werden.

## 5.1 Verbindliche MCM-Transition

Der erste passive Lauf verwendet ausschließlich die bereits vorhandene:

```text
receptor_projection_baseline
```

Sie ist auch die bestehende Transition der bisherigen Verdeckungswelt.

Verbindlich gilt:

```text
activation = aktueller lokaler Rezeptorkontakt
afterimage = 0
```

Diese Null ist keine Nullpunktanziehung und keine Ruhepunktdynamik. Die
Baseline besitzt überhaupt keine innere Entwicklung und keine Relaxation. Sie
isoliert nur den aktuellen technischen Transport vom Rezeptor bis zum
MCM-Feldfenster.

Der Lauf darf aus dem konstanten `afterimage = 0` keine biologische oder
organismische Aussage ableiten. Eine nachhalltragende Transition wird in
diesem ersten Kausaltransportlauf nicht verwendet.

## 6. Zweig V0: sichtbare Nullkonsequenz

### Weltzustand vor der Intervention

```text
q(t) = 1
d(t) = +1
v = 1
s = +1
```

### Abgeschlossener Folgezustand

```text
d'(t) = +1
q(t + 1) = 2
```

`q(t + 1)` liegt außerhalb von `O`. Der reguläre Rezeptorrahmen enthält einen
sichtbaren Kontakt an Position `2`.

### Bedeutung des Zweigs

V0 ist eine echte Richtungserhaltung innerhalb eines regulär fortschreitenden
Weltintervalls. Der Weltprozess wird nicht ausgelassen und nicht angehalten.

## 7. Zweig V1: sichtbare Konsequenz

### Weltzustand vor der Intervention

```text
q(t) = 1
d(t) = +1
v = 1
s = -1
```

### Abgeschlossener Folgezustand

```text
d'(t) = -1
q(t + 1) = 0
```

`q(t + 1)` liegt außerhalb von `O`. Der reguläre Rezeptorrahmen enthält einen
sichtbaren Kontakt an Position `0`.

### Bedeutung des Zweigs

V1 ist eine echte äußere Richtungsumkehr. Sie enthält keine Aussage darüber,
warum oder wozu die Richtung verändert wurde.

## 8. Sichtbares Kausalpaar V0/V1

V0 und V1 besitzen identisch:

```text
Weltgeometrie
Ausgangsposition
Ausgangsrichtung
Geschwindigkeit
Reizstärke
Interventionszeit
Weltintervall
Rezeptorgeometrie
MCM-Anatomie
```

Sie unterscheiden ausschließlich `s`.

Budget:

```text
ein Ausgangskontakt
ein Folgerahmen
ein sichtbarer Folgerahmen
keine verdeckte Phase
```

Zulässiger Vergleich:

```text
V1 gegen V0
```

Nicht zulässig ist eine Wirkungsdifferenz `V gegen H`, weil Sichtbarkeit dort
absichtlich verschieden ist.

## 9. Gemeinsame Vorgeschichte für H0 und H1

Die verdeckten Zweige besitzen vor der Intervention dieselbe deterministische
Weltfolge:

```text
t0: q = 2, d = +1 -> sichtbarer Eingangskontakt links
t1: q = 3, d = +1 -> verdeckt, kontaktfreier Rahmen
t2: q = 4, d = +1 -> verdeckt, Interventionsgrenze
```

An `t2` sind Weltzustand, Rezeptorhistorie, MCM-Anatomie und sämtliche
Observer-unabhängigen Zustände zwischen H0 und H1 identisch.

## 10. Zweig H0: verdeckte Nullkonsequenz

### Intervention

```text
q(t2) = 4
d(t2) = +1
s = +1
```

### Fortsetzung

```text
t3: q = 5, d = +1 -> verdeckt, kontaktfrei
t4: q = 6, d = +1 -> sichtbarer Austritt rechts
t5: q = 7, d = +1 -> zweiter sichtbarer Kontakt rechts
```

H0 erhält die Richtung. Weltzeit und Dynamik laufen unverändert weiter.

## 11. Zweig H1: verdeckte Konsequenz

### Intervention

```text
q(t2) = 4
d(t2) = +1
s = -1
```

### Fortsetzung

```text
t3: q = 3, d = -1 -> verdeckt, kontaktfrei
t4: q = 2, d = -1 -> sichtbarer Austritt links
t5: q = 1, d = -1 -> zweiter sichtbarer Kontakt links
```

H1 kehrt die Richtung innerhalb derselben Verdeckungsmaske um. Der erste
Folgerahmen nach der Intervention bleibt wie in H0 regulär kontaktfrei.

## 12. Verdecktes Kausalpaar H0/H1

H0 und H1 besitzen identisch:

```text
Weltgeometrie
vollständige Vorgeschichte bis t2
Ausgangsposition an t2
Ausgangsrichtung an t2
Geschwindigkeit
Reizstärke
Interventionszeit
Verdeckungsdauer nach der Intervention
Zeit des ersten erneuten Kontakts
Gesamtdauer
Kontaktanzahl
Rezeptorgeometrie
MCM-Anatomie
```

Sie unterscheiden ausschließlich `s`.

Budget je Zweig:

```text
6 Welt- und Rezeptorrahmen t0 bis t5
3 sichtbare Kontaktframes
3 kontaktfreie Frames
1 Interventionsgrenze
2 sichtbare Holdoutkontakte
```

Die Austritte sind räumlich gespiegelt:

```text
H0: 6, 7
H1: 2, 1
```

## 13. Budgetregel

Gleiche Budgets gelten innerhalb jedes kausalen Vergleichspaars:

```text
V0 = V1
H0 = H1
P0-Kopien = jeweiliger Quellzweig
```

V- und H-Familie besitzen absichtlich unterschiedliche Kontaktbudgets, weil
die eine Intervention sichtbar und die andere verdeckt erfolgt. Sie werden
nicht gegeneinander als Wirkungspaar ausgewertet.

Es wird kein künstlicher Kontakt, kein künstlicher Nullrahmen und keine
Ruhephase ergänzt, um ihre Budgets äußerlich anzugleichen.

## 14. Konkrete Holdoutfortsetzungen

Die einzigen Holdoutfortsetzungen dieses ersten Laufs sind die bereits vor
dem Lauf festgelegten Weltkontakte:

```text
H0-Holdout: q = 6, danach q = 7
H1-Holdout: q = 2, danach q = 1
```

Sie werden direkt durch den äußeren Weltzustand nach `t3` erzeugt.

Sie dürfen nicht:

- anhand einer Feldantwort ausgewählt werden;
- bei unerwarteter Feldantwort verlängert werden;
- zwischen Wiederholungen vertauscht werden;
- als richtige oder falsche Antwort bewertet werden;
- als Memory-Ausgabe bezeichnet werden.

Der Holdout prüft in diesem Lauf nur:

```text
verdeckter Weltzustand
-> deterministische spätere sichtbare Weltprojektion
```

## 15. Zweig P0: strenge Provenienznull

P0 ist kein eigener Weltverlauf.

Für jeden Quellzweig `V0`, `V1`, `H0` und `H1` werden zwei vollständig
identische Läufe erzeugt. Sie unterscheiden sich ausschließlich in einer
observerseitigen Ereigniskennung, die erst nach Abschluss des Weltlaufs
zugeordnet wird.

Verbindlich verboten sind in Welt-, Rezeptor- und Organismusrollen:

- `branch_id`;
- `phase_id`;
- `event_id`;
- `intervention_family_id`;
- `provenance`;
- `visible_intervention`;
- `hidden_intervention`;
- `consequence`;
- `null_consequence`;
- `expected_exit`;
- `holdout`;
- Weltseed;
- Testreihenfolge;
- Aufrufzahl;
- Rauschkennung.

P0 darf keine Kennung vor oder während der Welt-, Projektions-, Rezeptor- oder
MCM-Berechnung bereitstellen.

Erwartung:

```text
verschiedene observerseitige Ereigniskennung
+ bitgleiche Weltfolge
-> bitgleiche Projektionsfolge
-> bitgleiche Rezeptorfolge
-> bitgleiche aktuelle MCM-Feldfolge
```

## 16. Keine Ereignis-ID beim erneuten Kontakt

Die sichtbaren Holdoutframes enthalten ausschließlich:

```text
aktuelle sichtbare Position
konstante technische Reizlage
reguläre Rezeptorzeit
reguläre Trägeridentitäten
```

Sie enthalten keine Referenz auf:

- H0 oder H1;
- `s`;
- frühere Richtung;
- Interventionszeit;
- Ereigniskennung;
- Verdeckung;
- erwartete Austrittsseite.

## 17. Kausale Zeitordnung

Für jeden Frame gilt:

```text
1. vorheriger abgeschlossener Weltzustand
2. vorregistrierter äußerer Interventionswert
3. abgeschlossener Folgeweltzustand
4. sichtbare Projektion
5. visuelle Rezeptoranalyse
6. regulärer Rezeptorrahmen
7. bestehender MCM-Feldschritt
8. passiver Observer
```

Eine aktuelle MCM-Feldantwort darf keinen folgenden Weltzustand,
Interventionswert oder Holdoutrahmen verändern.

## 18. Passive Messgrößen

Nach jedem abgeschlossenen Schritt darf der Observer lesen:

```text
Weltzustandsdigest
Weltübergangsdigest
Projektionsdigest
Rezeptordigest
activation
afterimage
Digest aller weiteren bekannten MCM-Zustände
Organismuszeitgrenze
```

Die Provenienzkennung wird nur in einem getrennten äußeren Prüfprotokoll
geführt.

Vor und nach jedem Observeraufruf müssen die Digests aller gelesenen
Quellobjekte identisch bleiben.

## 19. Keine Auswertung anhand späterer Feldantworten

Vor dem ersten Lauf sind fest:

- alle Weltzustände;
- alle Interventionswerte;
- alle Zeitpunkte;
- alle sichtbaren und verdeckten Projektionen;
- alle Holdoutkontakte;
- alle Wiederholungen;
- alle Auswertungsreihenfolgen.

Es gibt:

- keine adaptive Zweigauswahl;
- keinen vorzeitigen Abbruch aufgrund einer Feldantwort;
- keine Verlängerung aufgrund einer Feldantwort;
- keine Auswahl eines besseren Holdouts;
- keine Schwellenoptimierung;
- keine Parameteranpassung.

Die Weltfamilie wird unabhängig von den MCM-Ergebnissen vollständig
ausgeführt.

## 20. Reihenfolge- und Aufrufzahlkontrolle

Die vollständige Familie wird ausgeführt als:

```text
V0, V1, H0, H1
H1, H0, V1, V0
eine feste kanonische Permutation
```

Zusätzlich werden die abgeschlossenen Ergebnisse gelesen mit:

```text
keinem optionalen Observer
einem Observeraufruf
mehreren identischen Observeraufrufen
```

Nach kanonischer Sortierung müssen Welt-, Projektions-, Rezeptor- und
MCM-Digests identisch sein.

Jeder Lauf verwendet frische Welt-, Rezeptor-, Dock- und MCM-Instanzen.

## 21. Pflichtkontrollen

Der minimale passive Lauf trägt nur, wenn:

1. V0 und V1 vor der Intervention bitgleich sind.
2. H0 und H1 bis einschließlich `t2` bitgleich sind.
3. `s = +1` die Richtung exakt erhält.
4. `s = -1` die Richtung exakt umkehrt.
5. sichtbare Folgezustände den korrekten lokalen Kontakt erzeugen.
6. verdeckte Folgezustände regulär kontaktfreie Rahmen erzeugen.
7. H0 und H1 an `t3` denselben kontaktfreien Rezeptorrahmen besitzen.
8. H0 und H1 an `t4` gleichzeitig und spiegelbildlich wieder sichtbar werden.
9. Weltprojektion und Rezeptorwerte verlustfrei übereinstimmen.
10. Rezeptorwerte und aktuelle MCM-Aktivierung nach der unveränderten Runtime
    übereinstimmen.
11. Provenienzkennungen keine öffentliche Rolle erreichen.
12. P0-Kopien ab dem Weltzustand vollständig kollidieren.
13. Reihenfolge und Observeraufrufzahl neutral bleiben.
14. kein Rausch-, Varianz-, Ruhe- oder Nullpunktparameter existiert.

## 22. Zulässige Befunde

### Sichtbarer Kausaltransport

```text
V0 gegen V1
-> verschiedene abgeschlossene Weltfolge
-> verschiedene aktuelle Rezeptorlage
-> verschiedene aktuelle MCM-Feldlage
```

Zulässige Aussage:

> Eine deterministische äußere Richtungsumkehr erreicht über die reguläre
> sichtbare Projektion die aktuelle MCM-Feldlage.

### Verdeckte aktuelle Null

```text
H0 gegen H1 an t3
-> verschiedene äußere Richtung
-> identische kontaktfreie Projektion
-> identische aktuelle Rezeptorlage
```

Zulässige Aussage:

> Die aktuelle Verdeckung hält die unterschiedliche äußere Weltfortsetzung
> aus dem gegenwärtigen Rezeptor-MCM-Kontakt heraus.

### Erneuter Weltkontakt

```text
H0 gegen H1 an t4 und t5
-> verschiedene äußere Position
-> verschiedene sichtbare Rezeptorlage
-> entsprechend verschiedene aktuelle MCM-Feldlage
```

Zulässige Aussage:

> Die während der Verdeckung fortgeführte Außenweltdynamik wird beim erneuten
> Sichtkontakt wieder rezeptorisch wirksam.

Dies ist kein Memory-Befund.

## 23. Nicht zulässige Befunde

Der Lauf zeigt nicht:

- eine gespeicherte Konsequenz;
- eine MCM-Feldbeziehung;
- Lernen;
- Semantik;
- Objekt- oder Funktionsverständnis;
- autonome Handlung;
- organisches Memory;
- Feldintelligenz.

Ein Unterschied beim erneuten Kontakt ist vollständig durch die
unterschiedliche aktuelle Außenwelt und den aktuellen Rezeptorrahmen erklärt.

## 24. Spätere Memory-Grenze

Ein weltbezogener Feldbeziehungs-Kandidat wäre erst methodisch prüfbar, wenn:

```text
vollständiger aktueller Rezeptorkontakt identisch
vollständige activation identisch
vollständiger afterimage identisch
alle weiteren bekannten MCM-Zustände identisch
+ kontrolliert verschiedene frühere Weltkonsequenz
-> unterschiedliche spätere Feldbildung
```

Diese Bedingung wird im jetzt freigegebenen passiven Lauf nicht hergestellt
und nicht ausgewertet.

## 25. Stopplinie

Der Lauf wird beendet und nicht in Richtung Memory fortgesetzt, wenn:

- Welt- und Rezeptorfolge nicht vollständig deterministisch sind;
- eine Kennung aus P0 in eine öffentliche Rolle gelangt;
- sichtbare und verdeckte Intervention verschiedene Weltregeln benötigen;
- H0 und H1 an `t3` nicht dieselbe kontaktfreie Projektion besitzen;
- H0 und H1 unterschiedliche Dauer- oder Kontaktbudgets besitzen;
- Reihenfolge oder Observeraufrufzahl ein Ergebnis verändert;
- ein Ergebnis nur durch aktuellen Kontakt oder bekannten Nachhall erklärt
  wird.

Aus dem Lauf darf keine Speichergröße oder neue Organismusmechanik abgeleitet
werden.

## 26. Freigabe

Nach dieser Vorregistrierung ist ausschließlich die minimale passive
Implementierung der Welt-, Projektions-, Rezeptor- und aktuellen MCM-Kette
für V0, V1, H0, H1 und P0 freigegeben.

Nicht freigegeben sind:

- Feldrückschreibung;
- Effektorsteuerung;
- Memory;
- neue Zeitlage;
- neue Kopplung;
- künstliches Rauschen;
- künstliche Varianz;
- Ruhe- oder Nullpunktdynamik;
- Wenn-X-dann-Y-Regeln im Organismus.

## 27. Wie es am besten weitergeht

Als nächster Durchlauf wird der minimale passive Lauf exakt nach dieser
Methodik implementiert. Er verwendet die bestehende visuelle Rezeptorfläche,
den bestehenden Rezeptorvertrag, den bestehenden Dockpfad und die
unveränderte MCM-Neuronenschicht.

Zuerst wird nur die neue Testdatei ausgeführt. Danach folgen die direkt
betroffenen bestehenden Welt-, Rezeptor- und MCM-Tests.
