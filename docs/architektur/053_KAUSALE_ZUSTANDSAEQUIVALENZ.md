# Kausale Zustandsäquivalenz

## Status

Darstellungsoffener Funktionsvertrag auf `E1 / FUNCTIONAL_EQUIVALENCE`.

```text
theoretische Äquivalenzgrenze:  formuliert
operative Prüfgrenze:           formuliert
aktuelle Runtime-Null:          getragen
weltbegründete Relevanz:        formuliert
digitale Darstellung:          offen
Runtime-Erweiterung:            gesperrt
```

Dieser Vertrag folgt aus dem
[Zulässigkeitsaudit der opaken Nullzustandshülle](052_ZULAESSIGKEITSAUDIT_OPAKE_NULLZUSTANDSHUELLE.md).
Er begründet zusätzlichen Zustand nicht durch Rohdatenmenge, sondern
ausschließlich durch notwendige spätere kausale Unterscheidbarkeit.

## Grundgedanke

Zwei Weltgeschichten können äußerlich verschieden sein und für den Organismus
trotzdem denselben gegenwärtigen funktionalen Zustand bedeuten.

```text
andere Bilder, Töne oder Reihenfolgen
+ keine unterschiedliche mögliche spätere Feldwirkung
-> kein notwendiger zusätzlicher Memory-Unterschied
```

Umgekehrt kann eine kleine frühere Differenz einen zusätzlichen Zustand
erfordern, wenn sie unter mindestens einer identischen späteren Weltfolge
einen anderen Feldweg tragen muss.

Memory soll deshalb keine Vergangenheit archivieren. Es soll nur den Teil
eigener Weltgeschichte tragen, der für spätere Feldbildung kausal noch nicht
gleich geworden ist.

## 1. Geschichte

Eine lokale Geschichte `H` ist kein gespeichertes Runtimeobjekt. Für die
Forschung bezeichnet sie nur eine kontrollierte Folge realer lokaler
Weltkontakte bis zu einem Zeitpunkt `t`.

Sie kann umfassen:

- Rezeptorkontakte;
- deren lokale räumliche Lage;
- deren abgeschlossene zeitliche Folge;
- kontaktfreie Zwischenzeiten;
- daraus entstandene schnelle Feldzustände.

Welt-, Objekt-, Personen-, Episoden- oder Bedeutungslabels gehören nicht zur
kausalen Geschichte.

## 2. Gemeinsame Angleichungsgrenze

Vor einer Memory-Prüfung müssen alle bereits bekannten kausalen Rollen
kontrolliert werden:

```text
gleiche Feldanatomie und Parameter
gleiche Organismuszeitgrenze
gleiche activation
gleicher afterimage
keine offenen transienten Rezeptorabschlüsse
gleiche gegenwärtige kausal gelesene Wahrnehmungsgrundlage
```

Technische Diagnosefelder, die von der Runtime nicht gelesen werden, dürfen
nicht als Scheindifferenz gewertet werden.

Eine spätere Memory-Rolle würde bei dieser Angleichung absichtlich
unangetastet bleiben. Andernfalls könnte ihre Wirkung nicht isoliert werden.

## 3. Identische zukünftige Weltfolge

Nach der Angleichung erhalten beide Zweige dieselbe zulässige zukünftige
lokale Weltfolge `U`.

`U` muss vor der Auswertung festgelegt sein und darf enthalten:

- einen einzelnen Holdout-Kontakt;
- eine endliche lokale Kontaktfolge;
- kontaktfreie Fortsetzung;
- veränderte Amplitude oder Zeitteilung;
- räumliche Spiegelung oder Übersetzung;
- mehrere aufeinanderfolgende kontrollierte Proben.

Nicht zulässig sind:

- Auswahl der Probe nach Sichtung des Ergebnisses;
- branchenspezifische Weltkontakte;
- semantisch bezeichnete Zielantwort;
- Reward oder Gewinnerregel;
- Observerrückwirkung.

## 4. Feldantwort

Die Antwort `R(H, U)` ist die vollständige kausale Feldtrajektorie nach Beginn
von `U`.

Primär gemessen werden:

```text
activation aller betroffenen Feldorte
afterimage aller betroffenen Feldorte
späterer vollständig deklarierter Memory-Zustand, falls vorhanden
Zeitpunkt jeder abgeschlossenen Feldlage
```

Die Messung liegt vor semantischer Auswertung, Klassifikation oder Handlung.
Ein späterer Berichtsscore allein ist keine Feldantwort.

Nur den Endzustand zu vergleichen genügt nicht. Zwei Trajektorien können
zwischenzeitlich funktional verschieden sein und später wieder
zusammenfallen.

## 5. Theoretische Äquivalenz

Zwei Geschichten `H1` und `H2` sind für das Feld kausal äquivalent, wenn nach
der gemeinsamen Angleichungsgrenze jede zulässige identische Zukunft dieselbe
Feldtrajektorie erzeugt:

```text
H1 ≡ H2

genau dann, wenn

für jede zulässige Zukunft U gilt:
R(H1, U) = R(H2, U)
```

Diese Definition speichert keine Zukunft und verlangt keine Runtime-Suche.
Sie ist eine Forschungsgrenze für die Bewertung von Zuständen.

## 6. Kausale Nichtäquivalenz

Zwei Geschichten sind nicht äquivalent, sobald mindestens eine identische
zulässige Zukunft einen reproduzierbaren Feldunterschied zeigt:

```text
H1 ≢ H2

wenn eine Zukunft U existiert mit:
R(H1, U) != R(H2, U)
```

Der Unterschied muss:

- innerhalb des Feldes entstehen;
- vor dem Observer vorliegen;
- bei Wiederholung reproduzieren;
- bei Tausch des isolierten Zustands mitwandern;
- bei Gleichsetzung dieses Zustands verschwinden;
- über `activation` und `afterimage` hinausgehen;
- gegenüber B0 bis B6 abgegrenzt sein.

## 7. Operative endliche Prüfung

Alle möglichen zukünftigen Weltfolgen können experimentell nicht vollständig
geprüft werden. Deshalb wird eine endliche Holdout-Familie `F` vorregistriert.

```text
H1 ≡F H2

wenn für jedes U aus F gilt:
R(H1, U) = R(H2, U)
```

Eine endliche Prüfung trägt nur Äquivalenz innerhalb von `F`. Sie beweist
keine universelle Gleichheit.

Nichtäquivalenz ist stärker: Ein einziger sauber kontrollierter und
reproduzierbarer Gegenfall genügt, um Äquivalenz zu widerlegen.

## 8. Exakte und numerische Gleichheit

Wo die Runtime deterministisch und bitgenau ist, gilt exakte Gleichheit.

Eine numerische Toleranz ist nur zulässig, wenn:

- sie vor dem Lauf feststeht;
- sie aus numerischer Reproduktion und nicht aus gewünschtem Ergebnis folgt;
- zusätzlich die erwartete Fehlerfortpflanzung angegeben wird;
- sie nicht als Schwelle in die Mechanik eingeht.

Ein kleiner messbarer Rest darf nicht allein wegen seiner Größe als
funktional bedeutungslos erklärt werden. Funktionale Wirkungslosigkeit muss
durch die vorgesehenen Kausalproben getragen werden.

## 9. Aktuelle Runtime-Null

Die vorhandene Geschichtsnull zeigt:

```text
verschiedene frühere Kontaktreihenfolgen
-> zunächst verschiedene vollständige Feldzustände
-> natürliche Angleichung der schnellen Zustände
-> vollständige Angleichung des kausal gelesenen Schichtzustands
-> identische spätere Probe
-> identische vollständige Feldantwort
```

Die aktuelle Runtime ist deterministisch. Sind ihr vollständiger kausal
gelesener Zustand, ihre Anatomie, Parameter und zukünftigen Eingaben gleich,
bleibt jede weitere Fortsetzung gleich.

Damit gilt für die heutige Runtime:

> Nach vollständiger Zustandsangleichung sind unterschiedliche frühere
> Weltgeschichten kausal äquivalent.

Das ist die Grundnull, die eine spätere Memory-Rolle gezielt und kausal
überwinden müsste.

## 10. Kein Rohdatenzwang

Aus unterschiedlichen Geschichten folgt nicht, dass unterschiedliche
Rohbilder, Audiosegmente oder Kontaktlisten gespeichert werden müssen.

Wenn viele Geschichten unter allen relevanten Zukünften dieselbe Feldwirkung
tragen, gehören sie funktional derselben Äquivalenzklasse an.

```text
viele konkrete Erlebnisse
-> eine gemeinsame spätere Feldfunktion
-> kein Bedarf für einzelne Roharchive
```

Das entspricht der gewünschten Verdichtung: Entscheidend ist nicht, wie eine
Sache vollständig aussah oder klang, sondern welche wiederkehrende
Feldwirkung sie im Organismus tragen kann.

## 11. Minimaler Informationsgehalt

Eine spätere Memory-Darstellung muss mindestens so viele funktional
verschiedene Zustände tragen können, wie operational nichtäquivalente
Geschichtsklassen nachgewiesen sind.

Bei `C` gleichzeitig notwendigen Klassen beträgt die reine
informationstheoretische Untergrenze:

```text
log2(C) unterscheidbare Bits
```

Diese Untergrenze:

- wählt keine Binärdarstellung;
- fordert keine feste Kapazität;
- bestimmt keine Neuronenzahl;
- begründet keine Semantik;
- erlaubt kein Vorabreservieren von Klassen.

Sie zeigt nur: Ein Zustand ohne genügend unterscheidbare Lagen kann die
geforderte kausale Unterscheidung nicht tragen.

## 12. Funktionale Lösung

Eine frühere Prägung ist vollständig gelöst, wenn zuvor nichtäquivalente
Geschichten unter den vollständigen alten Kausalproben wieder äquivalent
werden:

```text
zuvor: H1 ≢F H2

nach weiterer realer Weltgeschichte:
H1 ≡F H2
```

Dabei darf:

- kein Reset verwendet werden;
- keine alte Wirkung durch Intervention wieder freilegbar sein;
- keine passive Rückkehr allein die Gleichheit erklären;
- kein versteckter Archivzustand die alte Klasse weiter konservieren.

Digitale Werte müssen nicht zwingend identisch oder null sein. Entscheidend
ist vollständige funktionale Äquivalenz.

## 13. Erneute Prägbarkeit

Nach funktionaler Lösung muss neue reale lokale Weltgeschichte wieder eine
kausale Nichtäquivalenz bilden können:

```text
alte Klassen funktional gelöst
+ neue lokale Weltgeschichte
-> neue nichtäquivalente Feldlage
```

Die neue Unterscheidung darf nicht durch die frühere Geschichte heimlich
bevorzugt werden. Ohne neue Weltgeschichte darf sie nicht entstehen.

Damit werden Lösung und Wiederprägung ohne Speicherplatz-, Lösch- oder
Wiederbindungsoperation beschrieben.

## 14. Interventionslogik

Ist später eine konkrete Zustandsrolle vorhanden, muss geprüft werden:

```text
Zustand tauschen     -> Feldunterschied wandert mit
Zustand gleichsetzen -> Feldunterschied verschwindet
Zustand nullsetzen   -> heutige Runtime-Null erscheint
Bildungsquelle entfernen -> Nichtäquivalenz entsteht nicht
Wirkpfad trennen     -> Prägung bleibt, Feldwirkung verschwindet
```

Nur so lässt sich zeigen, dass nicht die Geschichte als Versuchslabel, sondern
der innere Zustand die spätere Feldantwort vermittelt.

## 15. Stärkstes Gegenargument

Ein künstlich eingeführter Zustand kann zwei Geschichten absichtlich
unterscheiden und dadurch selbst verschiedene zukünftige Feldantworten
erzeugen.

```text
beliebiges Geschichtsbit
-> fest programmierter Leser
-> verschiedene Antwort
```

Damit wäre interne Nichtäquivalenz konstruiert, aber noch keine
weltbegründete Relevanz gezeigt.

Kausale Zustandsäquivalenz begrenzt den notwendigen Informationsgehalt. Sie
beantwortet noch nicht, **warum gerade eine bestimmte Unterscheidung aus der
Weltgeschichte fortbestehen soll**.

## Freigabegrenze

```text
Geschichte als Forschungsursache definiert: ja
Feldantwort vor Observer definiert:         ja
Äquivalenz und Nichtäquivalenz definiert:   ja
Lösung funktional definiert:                ja
erneute Prägbarkeit definiert:              ja
aktuelle Runtime-Null getragen:             ja
Relevanzgrenze formuliert:                  ja
weltbegründete Relevanz empirisch getragen: nein
digitale Darstellung freigegeben:           nein
Runtime-Erweiterung freigegeben:             nein
```

Die anschließende
[weltbegründete Relevanzgrenze](054_WELTBEGRUENDETE_RELEVANZGRENZE.md)
ist inzwischen formuliert. Sie verlangt, dass vergangene Weltgeschichte nach
Angleichung des schnellen Zustands Information über eine noch unbekannte
spätere Rezeptorfortsetzung trägt. Ein beliebiges Geschichtsbit mit festem
Leser genügt damit nicht.

## Nächster Schritt

Als Nächstes wird eine minimale passive Weltfamilie vorregistriert. Sie prüft
zunächst nur, ob eine nicht tautologische Abhängigkeit zwischen vergangener
Kontaktgeschichte und neuer konkreter Holdoutfortsetzung besteht. Memory-Rolle,
Darstellung und Runtime bleiben geschlossen.
