# Lokale Ereignisquellgrenze der MCM-Runtime

## Status

Codegestützter Architekturabgleich auf `E2 / CAUSAL_BOUNDARY`.

```text
lokale Weltursachen offengelegt:          ja
atomare Zustandsbildung offengelegt:      ja
feldinterne Ereignisprägung vorhanden:    nein
Observer als Ereignisquelle ausgeschlossen: ja
neue Zustandsdarstellung gewählt:         nein
Runtime-Erweiterung freigegeben:           nein
```

Dieser Abgleich folgt auf den
[MINI_DIO-Abgleich zum Memory-Substrat](049_MINI_DIO_MEMORY_SUBSTRAT_ABGLEICH.md).
Er prüft die aktuelle Runtime und ergänzt keine Variable, Gleichung oder
Mechanik.

## Prüffrage

> Welche Ursachen und Zustandsänderungen besitzt ein MCM-Neuron während eines
> atomaren Feldfortschritts bereits selbst, und welche Ereignisform entsteht
> erst durch Transition, Feldprobe oder Observer?

Die Frage ist wichtig, weil eine spätere Memory-Prägung nur aus kausal
verfügbarer lokaler Weltgeschichte entstehen darf. Eine nachträglich
berechnete Diagnose darf nicht zur vermeintlich natürlichen Quelle erklärt
werden.

## Atomare Runtimegrenze

Der Feldfortschritt besitzt drei klar getrennte Stufen:

```text
1. abgeschlossener Vorzustand der gesamten Neuronenschicht
2. lokale Drives und vollständige, noch unveröffentlichte Vorschläge
3. gemeinsam abgeschlossene nächste Neuronenschicht
```

Alle Neuronen werden aus derselben abgeschlossenen Schicht gelesen. Erst wenn
sämtliche Vorschläge erfolgreich sind, entsteht die nächste Schicht. Eine neu
erzeugte Aktivierung kann deshalb nicht im selben Takt erneut als lokale
Ursache gelesen werden.

## Was lokal kausal verfügbar ist

Ein `MCMNeuronDrive` trägt für genau ein Neuron:

### Abgeschlossener eigener Vorzustand

```text
previous.activation
previous.afterimage
technische Identität und Position
vorherige abgeschlossene perception
```

Die vorherige `perception` gehört zwar zum Snapshot, wird von der neutralen
Runtime aber nicht rekursiv als Geschichte gelesen.

### Gegenwärtige lokale Wahrnehmungsgrundlage

```text
aktueller Rezeptorkontakt am eigenen Dock
lokale activation-Proben aus dem abgeschlossenen Vortakt
lokale afterimage-Proben aus dem abgeschlossenen Vortakt
relative technische Probenpositionen
```

Die Feldproben werden bei jedem Takt neu aus der festen lokalen
Probenanatomie erzeugt. Sie sind keine gespeicherten Beziehungen.

### Organismuszeit und transienter Dockverlauf

Falls der zeitaufgelöste Pfad verwendet wird, trägt der Drive zusätzlich:

```text
abgeschlossene Zeitspanne des Feldschritts
lokale geordnete Rezeptorabschlüsse innerhalb dieser Zeitspanne
```

Der transiente Dockverlauf ist Eingabe für diesen einen Vorschlag. Er wird
nicht als Feldzustand persistiert.

## Was erst durch die Transition entsteht

Die Transition liest den `MCMNeuronDrive` und gibt ausschließlich zurück:

```text
MCMNeuronOutput.activation
MCMNeuronOutput.afterimage
```

Erst daraus wird der nächste abgeschlossene `MCMNeuron` gebaut. Die Differenz
zwischen Vor- und Folgezustand ist daher kein vorab vorhandenes Eingabesignal.
Sie ist das Ergebnis der jeweiligen Übergangsregel.

In der neutralen Runtime werden die vollständigen Aktivierungs- und
Nachhallausgaben durch die offengelegte Diffusions- und Zeitintegration
berechnet. Der lokale Callback übernimmt danach exakt diese Ausgaben. Es
existiert kein zusätzliches verborgenes Ereignisobjekt.

## Was erst ein Observer erzeugt

Die frühere passive Übergangsevidenz verwendete:

```text
aktueller lokaler Rezeptorkontakt
* vorherige lokale Nachbaraktivierung
```

Der dafür nötige Quellraum liegt zwar im `MCMNeuronDrive`. Das konkrete
Produkt wurde jedoch im Transition-Callback ausschließlich für die
Beobachtung berechnet, nicht vom Feld als Zustand gebildet oder später
gelesen.

Die vollständige Prüfung zeigte:

- alle Ereignisse entsprachen exakt der festen Ein-Schritt-Nachbarschaft;
- Spiegelung und Kanaltausch änderten nur die technische Lage;
- Unterbrechung entfernte die Ereignisse;
- stationärer Kontakt erzeugte nur Selbstüberlappung;
- der schnelle Nachhall war in dieser Probe null;
- Observerreihenfolge und Wiederholung waren neutral;
- es gab kein Writeback und keine Speicherung.

Damit ist diese Ereignisform eine zulässige Diagnose und eine starke
Baseline, aber kein Memory-Substrat.

## Quellen- und Darstellungsgrenze

Die aktuelle Runtime trägt bereits die notwendigen **Weltquellen**:

```text
lokaler Vorzustand
+ lokales Vorfeld
+ aktueller oder transienter Rezeptorkontakt
+ verstrichene Organismuszeit
```

Sie trägt nicht:

```text
eine eigene geschichtlich fortwirkende Prägung dieser Quellen
```

Eine lokale Zustandsänderung kann aus zwei aufeinanderfolgenden Snapshots
rekonstruiert werden. Diese Rekonstruktion ist aber:

- abgeleitet statt persistent;
- vollständig durch Vorzustand, Weltkontakt und feste Transition erklärt;
- nach Angleichung von `activation` und `afterimage` ohne weiteren Rest;
- ohne eigene spätere kausale Wirkung.

## Verbotene Fehlinterpretationen

Aus der lokalen Quellenverfügbarkeit folgt nicht, dass:

- Kontakt mal Nachbaraktivierung eine natürliche Lernregel ist;
- jede Zustandsdifferenz gespeichert werden muss;
- relative Probenpositionen spätere Beziehungsidentitäten sind;
- eine Übergangshäufigkeit Relevanz oder Bedeutung ausdrückt;
- ein Zähler, eine Kante oder ein Leaky-Integrator freigegeben ist;
- die feste Probenanatomie eine entwickelte Topologie darstellt;
- ein Observerereignis in die Runtime zurückgeschrieben werden darf.

Insbesondere würde das Speichern jeder Zustandsdifferenz lediglich ein
Verlaufsarchiv erzeugen. Das widerspricht dem Memory-Substratvertrag.

## Kausale Einbindungsgrenze einer späteren Rolle

Soll eine neue geschichtstragende Zustandsrolle untersucht werden, kann sie
nicht hinter dem Observer oder nach Weltfinalisierung liegen. Sie müsste
atomar an derselben Grenze teilnehmen wie die schnellen Zustände:

```text
abgeschlossener lokaler Organismuszustand(t)
+ lokale Weltursachen(t -> t+1)
-> vollständiger lokaler Zustandsvorschlag(t+1)
```

Dabei gilt verbindlich:

1. Alle Vorschläge lesen denselben abgeschlossenen Vorzustand.
2. Die neue Rolle wird erst mit der vollständigen nächsten Schicht wirksam.
3. Eine neue Wirkung darf im selben Takt nicht ihre eigene Bildungsursache
   werden.
4. Der Observer erhält nur den abgeschlossenen Zustand und schreibt nicht
   zurück.
5. Snapshot und Wiederherstellung müssen die Rolle vollständig tragen.
6. Der Nullzustand muss exakt die heutige Runtime ergeben.

Diese Grenze bestimmt nur den Ort einer möglichen Zustandsrolle. Sie bestimmt
weder ihre digitale Form noch ihre Bildungs- oder Lösungsregel.

## Technische Absicherung

Geprüft wurden:

```text
MCMNeuron-Vertrag
atomare MCM-Neuronenschicht
neutrales lokales Feldsubstrat
passive lokale Übergangsevidenz
transiente lokale Neuroneneingabe
aktuelle Feldgeschichtsnull
```

Ergebnis:

```text
54 Tests
54 bestanden
0 Fehler
```

## Schlussfolgerung

Die Suche scheitert nicht an fehlender lokaler Weltevidenz. Die aktuelle
Runtime stellt Weltkontakt, Vorfeld, Eigenzustand und Zeit bereits kausal
sauber bereit.

Es fehlt ausschließlich die noch darstellungsoffene Fähigkeit, aus diesen
Quellen im laufenden Feld eine eigene, später kausal wirksame und wieder
vollständig lösbare Erfahrungsprägung zu tragen.

Die alte Übergangsevidenz löst diesen Mangel nicht. Sie zeigt nur, dass ein
fester Leser eine lokale Abfolge aus vorhandenen schnellen Zuständen erkennen
kann.

## Freigabegrenze

```text
lokale Quellen ausreichend offengelegt: ja
atomare Einbindungsstelle bestimmt:     ja
Memory-Prägung vorhanden:               nein
digitale Darstellung bestimmt:          nein
Updategleichung bestimmt:                nein
passiver Kandidat freigegeben:           nein
Runtime-Erweiterung freigegeben:         nein
```

## Nächster Schritt

Der
[atomare Zustandsrollen-Erweiterungsvertrag](051_ATOMARER_ZUSTANDSROLLEN_ERWEITERUNGSVERTRAG.md)
ist inzwischen formuliert. Er bestimmt die lokale Zugehörigkeit, atomare
Vorschlagsgrenze, Nullwirkung, Snapshotpflicht und Observergrenze einer noch
opaken Memory-Rolle, ohne ihre Darstellung oder Updategleichung auszuwählen.

Als Nächstes wird geprüft, ob eine reine opake Nullzustandshülle überhaupt
zulässig und nützlich wäre oder bereits eine leere bevorzugte Datenform in die
Runtime einschreibt. Bis zu diesem Audit bleibt die Runtime unverändert.
