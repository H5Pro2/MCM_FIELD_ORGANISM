# H2-B: Vergleich passiver Materialklassen

## Status

```text
Vergleichsart:                 statisch / konzeptionell
Materialklassen:              drei
Gleichung implementiert:      nein
Runtime veraendert:           nein
Klasse direkt zugelassen:     keine
H2-B-Ergebnis:                kein minimaler Kandidat gefunden
```

## Bewertungsfrage

Gesucht wird keine Materialklasse, die bereits technisch `Memory` genannt
wird. Gesucht wird eine unabhaengig definierte passive Materialphysik, die mit
dem MCM-Feld gekoppelt werden koennte und dabei gleichzeitig:

- eine begrenzte lokale Stoff- oder Zustandsrolle besitzt;
- Pfadabhaengigkeit nicht nur als gespeicherte Sequenz traegt;
- einen neutralen Nullpfad fuer die heutige MCM-Runtime besitzt;
- spaetere Feldwirkung kausal vermitteln kann;
- durch gewoehnliche weitere Feldgeschichte vollstaendig funktionslos werden
  kann;
- danach mit derselben Kapazitaet anders praegbar bleibt;
- nicht vollstaendig auf Leaky-Spuren, adaptive Gains, feste Attraktoren oder
  programmierte Hystereseschleifen faellt.

## Klasse P: konservativer lokaler Phasenanteil

### Physischer Kern

Cahn und Hilliard beschreiben einen raeumlich verteilten, konservierten
Zusammensetzungs- oder Dichteanteil. Die Dynamik wird durch eine vorgegebene
freie Energie eines inhomogenen Systems bestimmt. Konzentrationsgradient und
freie Energiedichte legen damit fest, welche raeumlichen Entwicklungen
energetisch bevorzugt sind.

Primaerquelle:
[Cahn und Hilliard, Free Energy of a Nonuniform System I](https://doi.org/10.1063/1.1744102).

### Anschluss an H2

Positiv sind:

- konservierte endliche Materialmenge;
- lokale raeumliche Verteilung;
- nachvollziehbare Energie- und Passivitaetsstruktur;
- Aufloesung von Materialbewegung statt blossen Kantengewichts.

### Kollision mit den Projektgrenzen

Die freie Energiedichte und ihre Parameter bestimmen bereits bevorzugte
Phasen, Grenzflaechen und Skalen. Ohne eine MCM-unabhaengig begruendete
Energielandschaft waere genau die gewuenschte Materialorganisation in das
Modell geschrieben.

Ferner erzeugt konservative Koarsening-Dynamik nicht automatisch funktionales
Vergessen. Sie kann alte Gebiete vergroessern, verschieben oder zusammenlegen,
ohne ihre spaetere Wirkung vollstaendig freizugeben. Eine erneute Praegung
waere von der gesetzten Energielandschaft abhaengig.

### Entscheidung

```text
Stoffrolle unabhaengig begruendbar:          ja
lokale Erhaltung:                           ja
neutrale MCM-Kopplung bestimmt:             nein
freie Energielandschaft ohne Zielvorgabe:   nein
Loesung und Wiederpraegung automatisch:     nein
direkter H2-B-Kandidat:                     nein
```

Das Phasenfeld bleibt eine starke Ressourcen- und Transportbaseline, aber
keine ausgewaehlte MCM-Memory-Physik.

## Klasse V: passives viskoelastisches internes Material

### Physischer Kern

Ein Standard-Linear-Solid beziehungsweise Zener-Material kombiniert
elastische und viskose Anteile. Unter Beanspruchung entsteht ein interner
verzoegerter Zustand; bei Entlastung relaxiert das Material entsprechend
seinen konstitutiven Zeitkonstanten. Positive Materialparameter koennen eine
passive dissipative Antwort tragen.

Vergleichsquellen:

- [Physical interpretation and essence of the standard linear solid model](https://doi.org/10.1016/j.ijmecsci.2025.111139)
- [Passivity criterion for simulation of viscoelastic soft tissues](https://doi.org/10.1177/0959651816663971)

### Anschluss an H2

Positiv sind:

- klare lokale Eingangs- und Antwortrollen;
- intrinsischer interner Materialzustand;
- passive Dissipation;
- Entlastung und Wiederbeanspruchung mit derselben Materialkapazitaet;
- neutraler unbelasteter Zustand.

### Kollision mit den Projektgrenzen

Das lineare viskoelastische Material besitzt feste Relaxationsmoden. Digital
ist seine Geschichte durch eine endliche Kaskade exponentieller interner
Zustaende darstellbar. Damit liegt es genau in der bereits verpflichtenden
Klasse mehrerer Leaky-Spuren mit festem Leser.

Seine Rueckkehr ist durch feste Materialzeitkonstanten bestimmt. Das ist eine
saubere physische Relaxation, aber noch keine feldzeitliche Loesung durch
konkurrierende MCM-Entwicklung.

### Entscheidung

```text
unabhaengige Materialphysik:                 ja
Passivitaet:                                ja
neutraler Nullpfad:                         ja
oberhalb fairer Leaky-Baselines:            nein
feldzeitliche statt feste Loesung:          nein
direkter H2-B-Kandidat:                     nein
```

Das viskoelastische Modell wird als staerkste physische Leaky-Baseline
beibehalten.

## Klasse M: memristive oder Duhem-hysteretische Materialantwort

### Physischer Kern

Chuas idealer Memristor wird durch eine konstitutive Beziehung zwischen
Ladung und Flussverkettung definiert. Allgemeinere memristive Systeme und
Duhem-Operatoren tragen eine eingangsabhaengige interne Zustands- oder
Hysteresewirkung. Fuer geeignete Duhem-Klassen lassen sich
Dissipativitaetsbedingungen und Speicherfunktionen angeben.

Primaerquellen:

- [Chua, Memristor - The Missing Circuit Element](https://doi.org/10.1109/TCT.1971.1083337)
- [Jayawardhana, Ouyang und Andrieu, Stability of systems with the Duhem hysteresis operator](https://doi.org/10.1016/j.automatica.2012.06.069)

### Anschluss an H2

Positiv sind:

- echte Pfadabhaengigkeit der Materialantwort;
- spaetere Ausgabe haengt vom inneren Materialzustand ab;
- Passivitaet ist fuer geeignete Klassen analysierbar;
- kein Rohdaten- oder Sequenzarchiv erforderlich;
- Nullzustand und Zustandstausch sind technisch definierbar.

### Kollision mit den Projektgrenzen

Die konstitutive Kennlinie beziehungsweise Hysteresefunktion legt bereits
fest, wie Geschichte geschrieben und spaeter gelesen wird. Ohne unabhaengige
MCM-spezifische Stoffbegruendung ist sie ein programmierter adaptiver Gain
oder Hystereseautomat.

Ideale nichtfluechtige memristive Zustaende besitzen gerade keine natuerliche
vollstaendige Funktionslosigkeit. Fuegt man Relaxation hinzu, entsteht erneut
eine feste Leaky- oder Schwellenmechanik. Fuegt man Konkurrenz hinzu, ist eine
weitere Ressourcenphysik notwendig, die nicht aus der Memristorbeziehung
folgt.

### Entscheidung

```text
Pfadabhaengigkeit:                           ja
spaetere kausale Materialwirkung:            ja
Passivitaet prinzipiell pruefbar:            ja
Kennlinie ohne programmierte Praegungsform:  nein
natuerliche vollstaendige Loesung:           nein
andere Wiederpraegung ohne Zusatzmechanik:   nein
direkter H2-B-Kandidat:                      nein
```

Die Klasse bleibt eine starke Hysterese- und adaptive-Gain-Gegenbaseline.

## Vergleichsmatrix

| Kriterium | Phasenanteil P | Viskoelastik V | Hysterese M |
|---|---:|---:|---:|
| unabhaengige Materialinterpretation | ja | ja | ja |
| lokale Passivitaet formulierbar | ja | ja | bedingt ja |
| begrenzter Zustand | ja | ja | bedingt |
| Pfadabhaengigkeit | ja | ja | ja |
| neutraler MCM-Nullpfad ohne Zusatzwahl | nein | anschlussfaehig | anschlussfaehig |
| oberhalb Leaky-/Gain-/Attraktorbaselines | offen, aber Energielandschaft gesetzt | nein | nein |
| Loesung durch weitere Feldgeschichte | nicht automatisch | feste Relaxation | nicht automatisch |
| andere Wiederpraegung derselben Kapazitaet | nicht automatisch | technisch ja, aber baselinegleich | nur mit Zusatzmechanik |
| direkt auswaehlbar | nein | nein | nein |

## Forschungsentscheidung

Keine der drei etablierten passiven Materialklassen erfuellt die H2-B-Grenzen
als minimaler eigenstaendiger Kandidat:

- Das Phasenfeld benoetigt eine vorgegebene freie Energielandschaft.
- Viskoelastik faellt auf feste Leaky-Zeitlagen zurueck.
- Memristive und Duhem-Hysterese faellt ohne weitere Physik auf adaptive
  Kennlinie oder Hystereseautomat zurueck und traegt keine natuerliche
  vollstaendige Loesung.

H2 wird deshalb nicht implementiert. Das Ergebnis ist kein
Unmoeglichkeitsbeweis gegen ein digitales MCM-Material. Es zeigt, dass die
derzeit betrachteten Standardklassen das gesuchte Zusammenspiel aus
Feldzeitverdichtung, funktionaler Loesung und Wiederpraegung nicht ohne
zusaetzlich gewaehlte Organisation tragen.

## Verbleibender Erkenntnisgewinn

Die drei Klassen werden als Baselines erhalten:

```text
P = konservierte Ressourcen- und Attraktorbaseline
V = physische Mehrfach-Leaky-Baseline
M = hysteretische adaptive-Gain-Baseline
```

Damit ist fuer einen spaeteren Kandidaten klar, welche einfacheren
Materialerklaerungen ausgeschlossen werden muessen.

## Bester naechster Schritt

H2 ist unter den geprueften Materialklassen methodisch ausgeschoepft. Als
naechstes wird H3 untersucht: eine lokale relationsabhaengige Materialantwort,
die nicht auf globale MINI_DIO-Raenge, gespeicherte Zyklen oder einfache
Produktmomente zurueckgreift.

Der erste H3-Schritt ist erneut statisch: Es muss bestimmt werden, ob lokale
relative Feldbewegung ueberhaupt eine observerfreie Ereignisquelle besitzt,
die mehr Information traegt als momentaner Feldfluss, Aktivitaetsdifferenz
oder ein Produktintegrator. Ist das nicht der Fall, wird auch H3 geschlossen,
bevor eine Gleichung entsteht.
