# F3-Schliessungsformen-Audit fuer konservativen S-M-Austausch

## Status

```text
Pruefart:                           statischer algebraischer Familienaudit
Form 1 konstante lineare Kreuzung: geschlossen
Form 2 M-abhaengige Kreuzmobilitaet: geschlossen als Primaerform
Form 3 bilinearer Kraft-Fluss-Austausch: bedingt offen
konkrete diskrete Gleichung:        nicht gewaehlt
Implementierung oder Versuch:       nicht zugelassen
```

Der nachfolgende
[mathematische Minimalvertrag](MATHEMATISCHER_MINIMALVERTRAG_BILINEARER_KONSERVATIVER_SM_AUSTAUSCH.md)
zeigt, dass die bedingt offene Form 3 an der gemeinsamen Forderung nach
aktivem neutralem M-Gleichzustand, weltbedingter Umverteilung und sofort
gebundener S-Rueckarbeit scheitert. Form 3 ist bis zu einer ausdruecklichen
Nullpfad-Korrektur geschlossen.

Der spaetere
[Nullpfad-Korrekturvertrag](NULLPFAD_KORREKTURVERTRAG_GEKOPPELTE_SUBSTRATPHYSIK.md)
hat inzwischen K2 Parameterneutralitaet gewaehlt. Dadurch wird nicht diese
alte Form freigegeben, sondern genau eine erneute mathematische
Existenzpruefung unter einem festen Nullparameterarm.

## Forschungsfrage

Bleibt innerhalb der unteilbaren lokal konjugierten S-M-Kreuzwirkung eine
kleinste Schliessungsform uebrig, die nicht nur feste Eigenmoden,
Keller-Segel-Drift, zustandsabhaengige Mobilitaet, Cross-Diffusionsmuster oder
einen gespeicherten M-Patternzustand mit festem Leser erzeugt?

Der Audit verwendet nur algebraische Platzhalter. Er legt weder Parameter
noch eine ausfuehrbare Fortschreibung fest.

## 1. Gemeinsame lokale Kantenbeschreibung

Fuer eine vorhandene ungerichtete Nachbarschaft zwischen Feldorten i und j
werden nur folgende abgeschlossene Vorzustandsdifferenzen betrachtet:

```text
dS_ij = S_j - S_i
dM_ij = M_j - M_i
```

Ein konservativer M-Fluss muss unter Kantenumkehr sein Vorzeichen wechseln:

```text
J_M(j,i) = -J_M(i,j)
```

Die Summe aller lokalen M-Aenderungen ist dadurch null, sofern jede Kante
genau einmal bilanziert und kein Randfluss zugelassen wird.

Eine S-Rueckwirkung ist nur dann unteilbar, wenn sie aus derselben
Kantenwechselwirkung entsteht. Ein zusaetzlicher ortsweiser Leser
`Ausgabe = f(M_i)` ist in allen drei Formen verboten.

## 2. Form 1: konstante lineare reziproke Kreuzkopplung

### Formklasse

Der M-Fluss ist eine feste lineare Kombination aus M- und S-Unterschied. Der
S-Gegenbeitrag ist entsprechend eine feste lineare Kombination derselben
lokalen Unterschiede.

Abstrakt besitzt der raeumliche S-M-Anteil damit eine konstante
Koeffizientenmatrix vor dem vorhandenen Graph-Laplace-Operator:

```text
raeumliche Fortsetzung von [S,M]
= konstante 2x2-Kopplungsmatrix
  mal lokale Differenzen von [S,M]
```

### Algebraische Reduktion

Ist die konstante Matrix diagonalisierbar, zerfaellt der gekoppelte Prozess
durch einen festen Komponentenwechsel in zwei feste raeumliche Eigenmoden.
Ist sie nicht diagonalisierbar, bleibt eine feste nichtnormale lineare
Rekurrenz mit moeglicher transienter Verstaerkung.

Die M-Erhaltung kann eine der Moden einschraenken, erzeugt aber keine
geschichtlich veraenderliche Kopplungsform. Jede spaetere Wirkung ist durch
dieselben festen Moden bestimmt.

### Baselineeinordnung

- lineare Cross-Diffusion;
- feste gekoppelte Eigenfluesse;
- nichtnormale lineare Rekurrenz;
- viskoelastische beziehungsweise diffusive Modenbaseline.

### Entscheidung

```text
Form 1: geschlossen
Grund: feste lineare Moden mit konservierter M-Komponente
```

Form 1 bleibt eine zwingende gleich budgetierte Baseline.

## 3. Form 2: begrenzte M-abhaengige Kreuzmobilitaet

### Formklasse

Die Flussrichtung folgt einer festen lokalen Kraft, waehrend die Menge oder
Geschwindigkeit des Flusses durch den gegenwaertigen M-Zustand skaliert wird.

Abstrakt:

```text
M-Fluss = Mobilitaet(M_i, M_j) mal feste lokale Kraft(S,M)
```

Die Mobilitaet kann an leeren oder vollen Orten verschwinden und dadurch
Nichtnegativitaet oder eine Obergrenze unterstuetzen.

### Reduktion

Liegt die neue Funktion ausschliesslich in der M-abhaengigen Skalierung, ist
die Form per Definition zustandsabhaengige Mobilitaet. Faktoren wie
`M_i`, `M_max - M_j` oder glatte Saettigungen bestimmen bereits, wie leere
und volle Bereiche Transport zulassen.

Das kann:

- Transport bei Materialmangel stoppen;
- Stau, Fronten und Saettigungsbereiche erzeugen;
- effektive Diffusions- oder Driftgeschwindigkeit veraendern;
- lange Transienten und lokale Sperrung erzeugen.

Diese Effekte bilden noch keine unteilbare S-M-Funktion. Eine getrennte
S-Rueckwirkung wuerde erneut einen Leser hinzufuegen. Wird der Gegenbeitrag
nur mit derselben Mobilitaet skaliert, bleibt die neue Rollenart weiterhin
die Mobilitaetskennlinie.

### Entscheidung

```text
Form 2: geschlossen als primaere Schliessung
Grund: neue Funktion liegt vollstaendig in zustandsabhaengiger Mobilitaet
```

Eine massenabhaengige Mobilitaet kann spaeter als technische
Invarianzbedingung einer anderen Form notwendig sein. Sie darf dann nicht als
deren Forschungsbefund ausgegeben werden.

## 4. Form 3: lokale bilineare S-M-Kraft-Fluss-Kopplung

### Formklasse

Eine lokale S-Differenz und die gegenwaertig an der Kante verfuegbare
M-Menge bestimmen gemeinsam einen gerichteten M-Austausch. Derselbe
tatsaechliche Austausch erzeugt gleichzeitig einen gebundenen additiven
Gegenbeitrag in der S-Fortsetzung.

Die Rollenstruktur lautet:

```text
gegenwaertige S-Kraft an Kante
mal gegenwaertig verfuegbares M an Kante
-> antisymmetrischer M-Transport
-> gleichzeitig gebundener additiver S-Gegenbeitrag
```

`Bilinear` bezeichnet hier nur die kleinste gemeinsame Abhaengigkeit von
einer S-Kraft und einer M-Menge. Noch ist keine konkrete Mittelung,
Richtungsfunktion oder Diskretisierung gewaehlt.

### Unterschied zu einem Pattern-Leser

Ein ruhendes M-Muster erzeugt nicht automatisch eine Ausgabe. Wirkung
entsteht erst, wenn eine gegenwaertige lokale S-Kraft mit der vorhandenen
M-Verteilung einen tatsaechlichen Austausch verursacht.

Dadurch ist ein spaeterer identischer Probeverlauf kausal formulierbar:

```text
gleiche S-Probe
+ unterschiedliche M-Verteilung
-> unterschiedlicher M-Austausch
-> unterschiedlicher gebundener S-Gegenbeitrag
```

Die M-Verteilung ist dabei Materialbedingung der aktuellen Wechselwirkung,
nicht ein durch `f(M_i)` ausgelesenes Zielpattern.

### Verbleibende Reduktionsrisiken

Die M-Transportseite allein liegt weiterhin nahe an:

- massengewichteter S-Gradientendrift;
- Keller-Segel-artigem Transport;
- nichtlinearer Cross-Diffusion;
- zustandsabhaengiger Mobilitaet.

Die S-Seite allein kann auf einen additiven Flussgegenimpuls oder eine feste
lineare Ausgabe fallen. Der moegliche Rest liegt deshalb ausschliesslich in
der unteilbaren Bindung beider Seiten an denselben tatsaechlichen
Kantenaustausch.

### Warum die Form bedingt offen bleibt

Im Gegensatz zu Form 2 ist die M-abhaengige Transportmenge nicht als
eigenstaendige Anpassungsfunktion gemeint. Sie ist die vorhandene endliche
Substanz, die bewegt wird. Im Gegensatz zu F2 des Transportfamilienvergleichs
gibt es keinen spaeteren Leser des entstandenen Musters.

Die Form besitzt damit eine eng benennbare physische Hypothese:

> Ein lokaler konservativer Materialaustausch leistet waehrend seines
> Vollzugs eine gekoppelte Rueckarbeit auf das schnelle Feld.

Diese Hypothese ist bekannte gekoppelte Transportphysik, keine neue
Naturwissenschaft. Sie kann dennoch als transparente digitale Naturannahme
des MCM-Systems untersucht werden, weil konkrete Inhalte und Verteilungen
nicht vorgegeben werden.

### Noch ungeloeste mathematische Bedingungen

Vor einer Gleichung muss gezeigt werden, dass eine konkrete Minimalform
gleichzeitig:

1. M exakt konserviert;
2. `0 <= M_i <= M_max` ohne Clipping invariant haelt;
3. bei gleichfoermigem M und fehlender S-Differenz exakt neutral ist;
4. unter Kantenumkehr und Spiegelung aequivariant bleibt;
5. den S-Gegenbeitrag ausschliesslich an den realisierten M-Austausch bindet;
6. keine globale Normierung oder gerichtete Fallunterscheidung benoetigt;
7. nicht algebraisch nur eine feste Kombination aus S und M transportiert;
8. bei ausgeschaltetem Kopplungsparameter einen exakten Nullpfad zur heutigen
   S-H-Runtime besitzt.

### Entscheidung

```text
Form 3 als physische Hypothese:       bedingt offen
Nichtnegativitaet/Obergrenze:         noch nicht nachgewiesen
Reduktion auf Drift/Cross-Diffusion:  weiterhin starke Baseline
mathematischer Minimalvertrag:        zugelassen
diskrete Gleichung/Runtime:           noch nicht zugelassen
```

## 5. Warum `beliebige Cross-Diffusion` keine Abschlussbaseline ist

Jede gekoppelte raeumliche S-M-Form kann abstrakt als Cross-Diffusion oder
gekoppelter Transport beschrieben werden. Diese Oberklasse enthaelt den
Kandidaten selbst und kann ihn definitionsgemaess identisch darstellen.

Zulaessige enge Baselines bleiben:

- konstante lineare Kreuzmatrix;
- einseitige S-Gradientendrift ohne Rueckarbeit;
- dieselbe Drift mit separatem M-Pattern-Leser;
- reine M-abhaengige Mobilitaet;
- passive M-Diffusion;
- Cahn-Hilliard- und Wave-Pinning-Kinetik;
- Ablation der gebundenen S-Rueckarbeit.

Ein spaeterer positiver Befund waere kein Nachweis ausserhalb der
Cross-Diffusionsmathematik. Er waere hoechstens Evidenz fuer eine bestimmte
gekoppelte Traegerfunktion oberhalb dieser engeren Erklaerungen.

## 6. Gesamtentscheidung

| Form | Konservative M-Rolle | unteilbare S-Rueckarbeit | engste Reduktion | Entscheidung |
|---|---:|---:|---|---|
| konstante lineare Kreuzung | ja | formal ja | feste Eigenmoden | geschlossen |
| M-abhaengige Kreuzmobilitaet | ja | nicht eigenstaendig | variable Mobilitaet | geschlossen |
| bilinearer Kraft-Fluss-Austausch | ja | prinzipiell ja | Drift/Cross-Diffusion | bedingt offen |

Es ist weiterhin kein Memory-Mechanismus nachgewiesen. Zum ersten Mal ist
jedoch eine konkrete physische Rollenform eng genug abgegrenzt, um ihre
mathematische Existenz und Invarianten zu pruefen.

## Quellen

- E. F. Keller und L. A. Segel,
  [Initiation of slime mold aggregation viewed as an instability](https://doi.org/10.1016/0022-5193(70)90092-5),
  1970. Dient als Gegenbaseline fuer massengewichtete Signalfelddrift.
- L. Onsager,
  [Reciprocal Relations in Irreversible Processes II](https://doi.org/10.1103/PhysRev.38.2265),
  1931. Dient nur als Existenzhinweis fuer gekoppelte Kraft-Fluss-Rollen.
- V. K. Vanag und I. R. Epstein,
  [Cross-diffusion and pattern formation in reaction-diffusion systems](https://doi.org/10.1039/B813825G),
  2009. Dient als starke Muster- und Cross-Diffusionsbaseline.

## Bester naechster Schritt

Als naechstes wird ein **mathematischer Minimalvertrag fuer bilinearen
konservativen S-M-Kraft-Fluss-Austausch** formuliert. Er darf noch keinen Code
erzeugen, muss aber eine kleinste diskrete Kantenform so weit bestimmen, dass
statisch geprueft werden koennen:

1. Antisymmetrie und exakte M-Erhaltung;
2. Invarianz von Nichtnegativitaet und Obergrenze ohne Clipping;
3. Neutralitaet der gleichfoermigen M-Verteilung;
4. gebundener additiver S-Gegenbeitrag aus demselben Austausch;
5. Atomaritaet und Zeitpartitionsgrenze;
6. Nullparameterfall der heutigen S-H-Runtime;
7. genaue Ablationen gegen Drift, Mobilitaet und Pattern-Leser.

Scheitert eine nichttriviale Minimalform an diesen Bedingungen, wird auch
Form 3 vor Implementierung geschlossen.
