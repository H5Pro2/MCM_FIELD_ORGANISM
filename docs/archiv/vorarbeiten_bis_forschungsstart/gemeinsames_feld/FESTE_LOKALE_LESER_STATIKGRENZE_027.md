# Feste lokale Leser und Statikgrenze 027

## Status

Passiver Architektur- und Funktionsabgleich nach `GF_001`.

Dieses Dokument führt keine Mechanik, keinen Zustand und keinen Versuchslauf
ein. Es begrenzt nur, was mit einer überall gleichen, unveränderlichen lokalen
Leserfunktion grundsätzlich gezeigt werden kann.

`GF_002` bleibt geschlossen.

## Ausgangspunkt

Der [GF_001-Befund](GF_001_BEFUND_MINIMALE_LOKALE_FELDWIRKUNG.md) zeigt:

```text
lokale Vorfeldprobe
-> feste symmetrische Leserform
-> kausale nächste Aktivierung
```

B2 und B3 tragen diese Wirkung technisch sauber. Die Wirkung ist jedoch
vollständig durch die jeweils vorgegebene Mittelungsform bestimmt.

## Formale Grenze

Ein zustandsloser lokaler Leser habe die Form:

```text
x_i(t+1) = F(
    aktueller Rezeptorkontakt_i(t+1),
    lokale schnelle Feldproben_i(t)
)
```

Dabei ist `F`:

- an jedem Neuron gleich,
- über die Zeit unverändert,
- ohne weiteren lokal entwickelten Zustand,
- ohne veränderliche Beziehung oder Topologie.

Für zwei unabhängig entstandene Feldzweige gilt dann zwingend:

```text
gleicher aktueller Rezeptorkontakt
+ gleiche lokalen schnellen Feldproben
+ gleiche Geometrie
-> gleiche nächste Aktivierung
```

Die Aussage folgt direkt aus der Funktionsform. Sie benötigt keine Annahme
über Mittelwert, Summe oder eine bestimmte Nichtlinearität.

## Was feste Rekurrenz trotzdem kann

Eine feste lokale Funktion kann:

- Aktivität räumlich weitertragen,
- Wellen, Oszillation oder Attraktoren erzeugen,
- Eingangsunterschiede über mehrere Takte sichtbar halten,
- komplexe und empfindliche Trajektorien erzeugen.

Diese Dynamik kann reich sein. Daraus folgt aber noch keine entwickelte
Disposition des Feldes.

Solange dieselbe Funktion `F` unverändert bleibt, liegt die gesamte
Geschichtswirkung nur im noch vorhandenen schnellen Feldzustand. Werden
aktueller Kontakt und schnelle lokale Feldproben vollständig angeglichen,
bleibt kein erworbener Funktionsunterschied.

## Präzise Statikgrenze

„Statisch“ bedeutet hier nicht:

```text
Aktivität bewegt sich nicht.
```

Gemeint ist:

```text
Die lokale Möglichkeit, auf eine Feldlage zu reagieren,
hat sich durch Weltteilnahme nicht verändert.
```

Ein fest rekurrentes Feld kann dynamische Zustände besitzen und dennoch eine
statische Übergangsdisposition haben.

## Fehlende nicht-statische Funktion

Für eine tatsächlich entwickelte Feldorganisation müsste mindestens folgende
Beobachtung möglich sein:

```text
verschiedene lokale Weltgeschichte
+ gleicher aktueller Rezeptorkontakt
+ vollständig angeglichener schneller Feldzustand
+ identische spätere lokale Probe
-> möglicherweise unterschiedliche lokale Feldantwort
```

Die Richtung des Unterschieds wird nicht vorgegeben. Es gibt keinen
gewünschten Gewinner und keine Zieltopologie.

Entscheidend wäre nur, dass ein Unterschied:

- aus lokaler Weltteilnahme entstanden ist,
- eine spätere Feldfunktion kausal verändert,
- nicht im schnellen Restzustand liegt,
- nicht durch einen globalen Zähler oder eine Uhr erklärt wird,
- wieder vollständig an Wirkung verlieren kann.

## Keine Vorentscheidung über die Darstellung

Aus der fehlenden Funktion folgt noch nicht, dass eine bestimmte digitale
Variable gebaut werden muss.

Nicht vorgegeben werden:

- Kante,
- Gewicht,
- Kontinuitätswert,
- Spur,
- Lernrate,
- Schwelle,
- Zähler,
- Ressourcenzahl,
- Gewinnerregel,
- feste Lebensdauer.

Begriffe wie Disposition, Beziehung oder Organisation bezeichnen an dieser
Stelle nur die gesuchte beobachtbare Funktionsänderung, nicht ihre technische
Speicherform.

## Minimaler späterer Gegenversuch

Ein zukünftiger Versuch müsste zwei unabhängige lokale Geschichten mit
gleichen Randgrößen erzeugen:

```text
H1: lokal zusammenhängende gemeinsame Feldwirkung
H2: gleiche Einzelkontakte und gleiche Gesamtwirkung,
    aber andere lokale Zusammenstellung
```

Danach:

```text
1. aktuellen Kontakt angleichen
2. schnellen Feldzustand vollständig angleichen
3. identische bisher unbenutzte lokale Probe geben
4. räumliche Feldantwort vergleichen
```

Ein Nullbefund ist zulässig. Er würde zeigen, dass der geprüfte Kandidat keine
über den schnellen Zustand hinausgehende Entwicklung trägt.

Ein Unterschied wäre erst dann relevant, wenn zusätzlich ausgeschlossen sind:

- Restaktivierung und Nachhall,
- versteckte Zweigidentität,
- globale Zeit und Schrittzahl,
- ungleiche Kontaktmengen,
- technische Reihenfolge,
- Observereinfluss,
- fest eingebaute Antwort auf die Geschichtsbezeichnung.

## Vollständiger organischer Lebenszyklus

Auch ein positiver erster Geschichtsunterschied wäre noch keine organische
Feldorganisation. Ein späterer Kandidat müsste nacheinander tragen:

```text
lokale Entstehung
-> spätere kausale Wirkung
-> Stabilisierung durch weitere tragende Weltgeschichte
-> Abschwächung
-> vollständige funktionale Lösung
-> mögliche andere lokale Wiederbildung
```

Bleibt eine Wirkung nur bestehen oder wächst monoton, entsteht erneut eine
statische Sackgasse.

## Konsequenz für GF_002

`GF_002` wird noch nicht implementiert.

Vor seiner Methodik fehlt ein darstellungsoffener Zustandsvertrag, der nur
festlegt:

1. welche Zustände vor der Holdout-Probe exakt angeglichen werden,
2. welche spätere Feldfunktion gemessen wird,
3. woran lokale Entstehung erkannt wird,
4. woran vollständige Lösung erkannt wird,
5. welche einfacheren statischen Baselines den Befund erklären könnten.

Erst danach darf über einen minimalen passiven Kandidaten gesprochen werden.

## Evidenzgrenze

```text
Statikgrenze fester zustandsloser Leser: E1
fehlende nicht-statische Feldfunktion:   präzisiert
darstellungsoffener Zustandsvertrag:     offen
GF_002:                                  geschlossen
Runtimefreigabe:                         keine
```

## Nächster sinnvoller Schritt

Als Nächstes wird ausschließlich der darstellungsoffene Zustandsvertrag für
den späteren Zwei-Geschichten-Holdout formuliert. Dabei wird noch keine
Variable, Gleichung oder Updatefunktion programmiert.
