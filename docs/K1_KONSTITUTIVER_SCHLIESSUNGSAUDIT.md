# K1: konstitutiver Schliessungsaudit

## Status

```text
Auditart:                         statisch / mathematisch-konzeptionell
gepruefte Schliessungsklassen:    drei
lineare passive Klasse:           Baseline
monotone nichtlineare Klasse:     kontraktive Baseline
konservativ-dissipative Klasse:   Oszillator-/Relaxationsbaseline
konkrete K1-Gleichung zugelassen: nein
Runtime-Aenderung:                nein
```

## Prueffrage

Die K1-Hypothese nimmt eine reziproke lokale Akkommodation zwischen schneller
MCM-Rolle S und langsamer Entwicklungsrolle L an.

Der Audit fragt:

> Kann eine der drei kleinsten konstitutiven Schliessungsklassen Bildung,
> spaetere Feldwirkung, vollstaendige funktionale Loesung und andere
> Wiederpraegung tragen, ohne bereits Leaky-Memory, feste Rekurrenz,
> Hystereseautomat oder programmierte Attraktorstruktur zu sein?

Es wird keine konkrete Diskretisierung, Parametrisierung oder Testwelt
ausgewaehlt.

## Gemeinsame lokale Form

Alle Klassen muessen als ein atomarer lokaler Gesamtuebergang darstellbar
sein:

```text
dS/dt = vorhandene schnelle MCM-Wirkung + interne Wirkung R(S,L)
dL/dt = langsame interne Wirkung Q(S,L)
```

`R` und `Q` sind nur Platzhalter. Sie duerfen keine Labels, Phasenkennungen,
Ziele oder spaetere Proben lesen.

## Klasse C1: lineare passive Kopplung

### Formklasse

Die allgemein lokale lineare Schliessung besitzt eine feste Koeffizienten-
beziehungsweise Operatormatrix:

```text
d/dt [S,L] = A [S,L] + B * Weltkontakt
```

Passivitaet und Stabilitaet beschraenken die zulaessigen Koeffizienten.

### Dynamische Konsequenz

Bei stabiler passiver Wahl zerfaellt die Antwort in feste Eigenmoden. Jeder
Modus traegt eine exponentielle oder gedaempft oszillatorische Zeitkomponente.

Damit ist die gesamte Geschichte durch eine endliche Bank fester linearer
Zustaende bestimmt:

```text
Weltkontakt
-> feste lineare Moden
-> feste lokale Ausgabe
```

### Lebenszyklusgrenze

- Bildung ist technisch moeglich.
- Zustandstausch kann eine spaetere S-Wirkung verschieben.
- Loesung folgt festen Zeitkonstanten oder bleibt bei neutralen Moden aus.
- Wiederpraegung ist nur erneute Anregung desselben linearen Filters.
- Es entsteht keine feldgeschichtlich veraenderte Entwicklungsbedingung.

### Entscheidung

**Nicht als K1-Kandidat zugelassen.**

C1 ist exakt die feste gekoppelte Rekurrenz-, Viskoelastik- und
Mehrfach-Leaky-Baseline.

## Klasse C2: begrenzte monotone nichtlineare Kopplung

### Formklasse

Die interne Wirkung ist stetig, schwellenfrei, beschraenkt und monoton zur
lokalen S-L-Abweichung. Beispiele waeren glatte Saettigungen, ohne dass eine
bestimmte Funktion ausgewaehlt wird.

### Dynamische Konsequenz

Eine global monotone dissipative Kopplung kann Amplituden begrenzen und
Relaxationsgeschwindigkeit zustandsabhaengig machen. Sie erzeugt damit
nichtlineares Fading Memory.

Solange die Kopplung kontraktiv bleibt und nur ein neutraler Gleichgewichts-
bereich existiert, verlieren unterschiedliche Geschichten unter identischer
weiterer Anregung ihre Differenz. Die Geschwindigkeit kann variieren; die
Entwicklungsordnung bleibt dennoch durch eine feste Kennlinie bestimmt.

### Lebenszyklusgrenze

- Begrenzte geschichtliche Wirkung ist moeglich.
- Saettigung kann scheinbare Verdichtung erzeugen.
- Vollstaendige Loesung ist nur asymptotische Konvergenz oder eine
  programmierte endliche Zustandskollision.
- Andere Wiederpraegung ist erneute Anregung derselben festen Kennlinie.
- Ein dauerhafter organisationsaehnlicher Rest benoetigt Nichtkontraktivitaet,
  mehrere Attraktoren oder Hysterese.

### Baselinekollision

Diese Klasse faellt auf:

- begrenzte Leaky-Spur;
- feste nichtlineare Rekurrenz;
- Saettigungsintegrator;
- feste monotone Gain-Kennlinie.

### Entscheidung

**Nicht als K1-Kandidat zugelassen.**

Monotone Nichtlinearitaet veraendert die Form des Fading Memory, aber nicht
seine funktionale Klasse.

## Klasse C3: konservative Kopplung mit separater Dissipation

### Formklasse

S und L tauschen intern eine begrenzte Groesse reziprok aus. Ein getrennter
dissipativer Anteil begrenzt die Gesamtdynamik.

Abstrakt:

```text
interner S-L-Austausch: bilanziell reziprok
Dissipation:            entfernt oder verteilt dynamische Wirkung
Weltkontakt:            einzige aeussere Anregung
```

### Dynamische Konsequenz

Es entstehen zwei Grundfaelle:

1. **Dissipation dominiert:** Die Trajektorie relaxiert auf eine durch die
   feste Physik bestimmte Ruhelage. Das ist gedaempfte Rekurrenz oder
   Viskoelastik.
2. **Konservative Moden bleiben:** Phase oder interne Schwingung kann
   Geschichte tragen. Ohne weitere Physik wird alte Wirkung jedoch nicht
   vollstaendig funktionslos.

Eine Mischung kann lange Nachwirkung und relative Phase erzeugen. Sie
begruendet aber noch keine feldgeschichtlich veraenderte Organisations-
faehigkeit.

### Lebenszyklusgrenze

- Eigene innere Zeitordnung ist prinzipiell moeglich.
- Unterschiedliche Geschichte kann unterschiedliche Phase erzeugen.
- Bei Dissipation wird die Wirkung durch feste Rate geloest.
- Ohne Dissipation bleibt alte Phase erhalten.
- Andere Wiederpraegung ist nur Ueberlagerung oder erneute Phasenverschiebung.

### Entscheidung

**Nicht als K1-Kandidat zugelassen.**

C3 bleibt eine wichtige Oszillator-, Resonanz- und viskoelastische
Gegenbaseline fuer spaetere Feldzeitbefunde.

## Gemeinsame Entscheidungsmatrix

| Klasse | Geschichtswirkung | relative innere Zeit | vollstaendige Loesung | neue Entwicklungsbedingung | Einordnung |
|---|---:|---:|---:|---:|---|
| C1 linear passiv | ja | feste Moden | feste Relaxation | nein | Rekurrenz/Leaky |
| C2 monoton nichtlinear | ja | zustandsabhaengige Rate | Konvergenz oder Kollision | nein | nichtlineares Fading Memory |
| C3 konservativ-dissipativ | ja | Phase/Schwingung | feste Dissipation oder keine | nein | Oszillator/Viskoelastik |

## Zentrale Schlussfolgerung

Reziprozitaet, Passivitaet, Begrenzung und zwei Zeitskalen genuegen nicht fuer
den gesuchten Memory-Lebenszyklus.

Die drei kleinsten Schliessungen koennen:

- Geschichte tragen;
- inneren Kontext technisch vermitteln;
- Nachwirkung und Resonanz erzeugen;
- unter identischer Probe verschiedene schnelle Antworten erzeugen.

Sie koennen aber keine alte lokale Entwicklungsbedingung durch weitere
Feldgeschichte funktional umbauen und danach anders neu tragen, ohne eine
zusaetzliche strukturveraendernde Naturfunktion einzufuehren.

## Welche Eigenschaft mathematisch fehlt

Mindestens eine der folgenden Eigenschaften waere notwendig:

- nichtkontraktive lokale Umorganisation;
- metastabile oder strukturell veraenderliche Zustandslandschaft;
- zustandsabhaengige Veraenderung der Kopplungsform;
- lokale Erzeugung und Loesung von Freiheitsgraden;
- offene Umverteilung einer begrenzten Organisationsfaehigkeit.

Alle diese Eigenschaften liegen ausserhalb der drei minimalen Klassen. Sie
sind zugleich gefaehrlich, weil sie leicht als Attraktor, adaptive Kante,
Ressourcenregel oder Zieltopologie vorprogrammiert werden koennen.

## Wissenschaftliche Korrektur der Erwartung

Es ist nicht realistisch, eine entwicklungsfaehige digitale Substratphysik zu
erhalten, ohne irgendeine strukturveraendernde Naturbedingung festzulegen.

Der saubere Anspruch lautet daher nicht:

```text
keine Entwicklungsphysik programmieren
```

sondern:

```text
allgemeine lokale Entwicklungsphysik transparent festlegen
aber konkrete Inhalte, Bindungen, Bedeutungen und Zieltopologien
nicht vorprogrammieren
```

Auch die heutige schnelle MCM-Feldwirkung beruht auf festgelegter lokaler
Physik. Organisch oder emergent kann nur die daraus entstehende konkrete
Geschichte und Organisation sein, nicht die Existenz einer Naturregel selbst.

## Forschungsentscheidung

Keine der drei geprueften Schliessungen wird implementiert. Die
K1-Akkommodationshypothese bleibt als allgemeiner Rahmen bestehen, besitzt
aber noch keine tragfaehige konstitutive Schliessung.

Der naechste Schritt darf nicht wieder eine weitere Relaxationskurve sein. Er
muss offen deklarieren, welche minimale strukturveraendernde Naturbedingung
zugelassen wird und welche konkreten Strukturen weiterhin nicht vorgegeben
werden.

## Bester naechster Schritt

Als naechstes wird ein **Zulassungsvertrag fuer strukturveraendernde lokale
MCM-Physik** erstellt.

Er soll drei Grenzen sauber trennen:

1. Was darf als allgemeine digitale Naturbedingung fest programmiert werden?
2. Welche konkrete Organisation muss ausschliesslich aus Weltkontakt und
   Feldgeschichte entstehen?
3. Welche Mechaniken bleiben trotz dieser Oeffnung verboten, insbesondere
   adaptive Kanten, Zielattraktoren, Clusterbildung, Reward und feste
   Loeschregeln?

Der
[Zulassungsvertrag fuer strukturveraendernde lokale MCM-Physik](ZULASSUNGSVERTRAG_STRUKTURVERAENDERNDE_LOKALE_MCM_PHYSIK.md)
ist inzwischen formuliert. Er trennt allgemeine digitale Naturbedingungen
von der konkreten Organisation, die ausschliesslich aus Weltkontakt entstehen
muss. Noch wird keine Gleichung implementiert.
