# Evidenzvertrag fuer verteilte kausale Nichtseparierbarkeit

## Status

```text
Vertragstyp:                       statische Evidenz- und Falsifikationsgrenze
zulaessige Welten:                 kontrolliertes Browser, Video und Audio
vorhandene schnelle AV-Infrastruktur: ja
langsamer rueckwirkender Traeger:  nicht vorhanden
konkreter Mechanikkandidat:        nicht gewaehlt
Runner, Ausfuehrung oder Test:     nicht zugelassen
Memory- oder Organisationsclaim:   nein
```

## Forschungsfrage

Kann eine spaetere kausale Wirkung nur aus einer verteilten Konfiguration im
gemeinsamen MCM-Feld erklaert werden, oder genuegen unabhaengige lokale
Spuren, Gegenvariablen beziehungsweise Hystereseelemente unter dem bereits
vorhandenen S-Feldfluss?

Der Begriff **verteilte kausale Nichtseparierbarkeit** bezeichnet vorlaeufig
nur folgende pruefbare Eigenschaft:

> Die vollstaendige spaetere S-Feldwirkung einer entstandenen inneren
> Konfiguration kann mit einem festen Parametersatz nicht als Zusammensetzung
> unabhaengiger lokaler Geschichtstraeger plus bestehendem schnellen S-Fluss
> reproduziert werden.

Das ist weder Memory noch Organisation, Topologie, Semantik oder KI.

## 1. Technischer Ausgangspunkt

Im Projekt sind statisch bereits vorhanden:

- kontrollierte synthetische Audio-only-, Video-only-, gemeinsame AV- und
  Nullwelten;
- reproduzierbare Rezeptorereignisse mit gemeinsamer Organismuszeit;
- grobe und feine verlustlose Zeitpartitionierung;
- Reihenfolgekontrolle gleichzeitiger Audio- und Videouebergaben;
- vollstaendige Activation- und Afterimage-Vektoren;
- Feld-, Layer- und Snapshot-Digests;
- eine externe passive Browserwelt mit `static -> moving -> static` und
  synchronem Tonkontakt.

Diese Infrastruktur belegt Reproduzierbarkeit des schnellen Weltpfads. Sie
belegt keinen langsamen inneren Traeger und fuehrt diesen Vertrag nicht aus.

## 2. Zulaessige Testweltfamilie

Die erste spaetere Evidenzfamilie darf ausschliesslich technische,
bedeutungsfreie Verlaeufe verwenden.

| Arm | Verlauf | Kontrollzweck |
|---|---|---|
| `N` | Nullkontakt | technischer Nullpfad |
| `A` | Audio-only-Verlauf | auditive Teilgeschichte |
| `V` | Video-only-Verlauf | visuelle Teilgeschichte |
| `AV` | gemeinsamer zeitlich festgelegter AV-Verlauf | gemeinsame Feldteilnahme |
| `A+V-getrennt` | dieselben marginalen Ereignisse in getrennten Zeitfenstern | gemeinsame gegen getrennte Geschichte |
| `AV-versetzt` | gleiche Ereignisse und Dauer, veraenderte relative AV-Lage | relative Ordnung |
| `AV-umgekehrt` | gleiche Ereignisbudgets in umgekehrter Zeitordnung | reine Summenwerte ausschliessen |
| `V-raumpermutiert` | gleiche visuellen Werte, permutierte feste Geometrie | Geometriebezug |
| `AV-partitioniert` | derselbe Quellenverlauf mit anderer technischer Teilung | Segmentartefakt ausschliessen |
| `B` | unabhaengiger budgetgleicher AV-Verlauf | Verlaufsspezifitaet |

Die Bezeichnungen A, V und B tragen keine Objekt- oder Bedeutungsklasse.
Medieninhalte duerfen weder gelabelt noch vom Organismus interpretiert werden.

### Gemeinsames Budget

Wo ein Arm als Budgetkontrolle dient, werden vorab angeglichen:

- Anzahl und Werte der Rezeptorereignisse;
- reale Gesamtdauer;
- Audio- und Video-Einzelbudgets;
- Feldgeometrie und aktive Docks;
- Zeitpraezision und Partitionierungsregel;
- Startzustand und technische Konfiguration.

Gleiches Budget bedeutet nicht gleiche Feldgeschichte. Genau dieser
Unterschied soll spaeter kontrolliert werden.

## 3. Phasen eines spaeteren Vergleichs

Jeder Arm besitzt dieselbe technische Phasenordnung:

```text
frischer Nullzustand
-> kontrollierte Bildungsgeschichte
-> definierte schnelle Zustandsangleichung
-> optionale Forschungsintervention
-> byteidentische reduzierte Probe P
-> normale weitere Weltgeschichte
-> erneut byteidentische Probe P oder Q
```

Es gibt in der Runtime keinen Schreib-, Probe-, Loesch- oder Abrufmodus. Die
Phasen existieren nur im externen Versuchsprotokoll.

### Schnelle Zustandsangleichung

Vor der Probe muessen Activation und Afterimage entweder komponentengenau
angeglichen oder ihr verbleibender Unterschied vollstaendig ausgewiesen
werden. Ein langsamer Effekt darf nicht aus unterschiedlich gebliebenem
schnellem Nachhall abgeleitet werden.

Ein technischer Alignment-Operator ist nur als externe Forschungsintervention
zulaessig. Er darf keinen spaeteren Organismuszustand anhand des Ergebnisses
optimieren.

## 4. Vorregistrierte Kausalinterventionen

Diese Interventionen werden erst formulierbar, wenn ein Kandidat einen
vollstaendig serialisierten langsamen Zustand besitzt.

### I0: unveraenderte Fortsetzung

Der gebildete Gesamtzustand wird ohne Eingriff mit der identischen Probe
fortgesetzt. Dies ist die Referenz fuer jede Intervention.

### I1: langsame Wirkungsablation

Nur die L-zu-S-Wirkungsrichtung wird neutralisiert. Der gespeicherte
L-Zustand und der schnelle Pfad bleiben unveraendert.

```text
erwartete Kausalgrenze:
behauptete langsame Zusatzwirkung verschwindet
```

### I2: vollstaendiger Konfigurationstausch

Die gesamte langsame Konfiguration wird zwischen zwei ansonsten
angeglichenen Armen getauscht.

```text
erwartete Kausalgrenze:
spaetere Zusatzwirkung wandert mit der Konfiguration
```

### I3: geometrische Permutation

Die Werteverteilung der langsamen Konfiguration bleibt exakt erhalten, ihre
Zuordnung zu den bestehenden Feldorten wird jedoch durch eine vorab
festgelegte geometrische Permutation veraendert.

Eine Permutation darf keine Werte neu berechnen und keine besten oder
schlechtesten Orte aus einem Ergebnis auswaehlen.

### I4: lokale Neutralisierung

Eine vorab geometrisch definierte Teilmenge langsamer Feldorte wird auf den
neutralen Kandidatenzustand gesetzt. Activation, Afterimage und alle anderen
L-Orte bleiben unveraendert.

Mehrere Masken muessen vorab festgelegt sein; eine nach Ergebnis gewaehlte
Maskierung ist verboten.

Bei einem konservativen Traeger ist diese Intervention nur zusammen mit
vollstaendiger Mengenbilanz und einer gleich budgetierten Kontrolle
interpretierbar. Entfernte Menge muss als externe Auditdifferenz ausgewiesen
oder innerhalb des Feldes in eine vorab bestimmte neutrale Kontrollregion
verschoben werden. Eine unverbuchte Mengenloeschung darf nicht als
funktionale Loesung gelten.

### I5: S-zu-L-Ablation

Die weitere Bildung des langsamen Zustands aus S wird entfernt, waehrend eine
bereits vorhandene L-zu-S-Wirkung technisch fortgesetzt wird. Damit werden
Bildung und Wirkung kausal getrennt, ohne zwei Runtime-Modi zu behaupten.

Alle Interventionen sind Observerwerkzeuge. Keine gehoert in die produktive
Naturform.

## 5. Bedeutungsfreie Observablen

Primaer zulaessig sind nur vollstaendige technische Zustands- und
Trajektoriengroessen:

- Activation-Vektor jedes abgeschlossenen Feldschritts;
- Afterimage-Vektor separat, nicht in Activation eingemischt;
- vollstaendiger hypothetischer L-Vektor;
- lokaler bestehender S-Nachbarschaftsfluss;
- Feld-, Layer- und Snapshot-Digests;
- komponentenweise Differenz sowie vorregistrierte `L_inf`- und
  quadratische Normen zwischen Armen;
- Reproduktionsfehler und Baseline-Residuen ueber den gesamten Verlauf.

Nicht zulaessig sind:

- Objekt-, Ereignis-, Szenen- oder Bedeutungslabels;
- Cluster-IDs oder vom Observer erzeugte Aehnlichkeitsklassen in der Runtime;
- semantische Scores, Embeddings oder Klassifikationsgenauigkeit;
- Reward, Loss gegen eine Zielantwort oder Auswahl der besten Probe;
- nachtraeglich gewaehlte Zeitfenster, Orte oder Schwellen.

Ein passiver Observer darf nach Abschluss technische Strukturen beschreiben.
Seine Beschreibung wird weder zur Bildung noch zur Fortsetzung
zurueckgeschrieben.

## 6. Evidenzstufen

### E0: technische Integritaet

- Byteidentische Weltereignisse erzeugen aus identischem Zustand denselben
  Snapshot.
- Grobe und feine verlustlose Partitionierung stimmen innerhalb der
  vorregistrierten numerischen Grenze ueberein.
- Gleichzeitige Uebergabereihenfolge veraendert den atomaren Abschluss nicht.
- Null- und Einzelmodalitaetsarme bleiben technisch getrennt ausweisbar.

Ohne E0 wird der Vergleich gestoppt.

### E1: langsamer kausaler Traeger

Bei angeglichenem S und H muss eine spaetere S-Differenz:

- mit L zwischen Armen tauschen;
- bei L-zu-S-Ablation verschwinden;
- ohne Observer bestehen;
- aus normaler Weltgeschichte erreichbar sein.

E1 belegt nur einen rueckwirkenden Geschichtstraeger.

### E2: geometrisch verteilte Kausalitaet

Die spaetere Wirkung muss kontrolliert auf I3 und I4 reagieren. Dabei muss
die Wirkung von der konkreten Zuordnung der inneren Werte zur Feldgeometrie
abhaengen und darf nicht allein durch die Werteverteilung oder einen globalen
Summenwert erklaert sein.

E2 belegt nur Geometrieabhaengigkeit.

### E3: Nichtseparierbarkeit gegen enge Baselines

Ein Kandidat muss die gesamte Matrix aus Weltarmen, Proben und Interventionen
mit einem festen Parametersatz tragen. Danach wird geprueft, ob gleich
budgetierte lokale Baselines dieselben vollstaendigen S-Trajektorien
reproduzieren.

Nur wenn die vorregistrierten lokalen Baselines systematisch scheitern, ohne
dass eine andere enge Feldbaseline den Verlauf erklaert, bleibt verteilte
kausale Nichtseparierbarkeit als Befund offen.

### E4: Rekonfiguration

Weitere normale Weltgeschichte muss:

- die alte Zusatzwirkung auf ihrer alten Probe funktionslos machen;
- die Verteilung der kausalen Beitraege veraendern;
- danach eine andere Wirkung unter derselben Naturform ermoeglichen;
- ohne Reset, Ablaufzeit, Ergebnisrueckschreibung oder besondere Phase
  auskommen.

Erst E0 bis E4 gemeinsam erlauben die spaetere Pruefung eines
Memory-Lebenszyklus. Sie beweisen ihn noch nicht automatisch.

## 7. Pflichtbaselines

Jeder Kandidat wird mindestens verglichen mit:

1. heutiger S-H-Nullruntime;
2. einer und mehreren unabhaengigen lokalen Leaky-Spuren;
3. unabhaengigen lokalen linearen Gegenvariablen;
4. unabhaengigen lokalen glatten Hystereseelementen;
5. lokalem S-L-Oszillator unter bestehendem S-Fluss;
6. linearen gekoppelten S-L-Moden;
7. konkreter Ein-Diffusor-Reaktions-Diffusionskinetik;
8. fester Attraktor- oder Musterkinetik;
9. globalem Summen- oder Momentenintegrator ausserhalb der Runtime;
10. I1-, I3-, I4- und Richtungsablationen des Kandidaten.

Alle Baselines erhalten dasselbe lokale Zustands-, Parameter-,
Praezisions-, Geometrie-, Zeit- und Beobachtungsbudget, soweit ihre Klasse
dies zulaesst. Keine Baseline wird fuer einzelne Phasen neu angepasst.

## 8. Entscheidungsregeln

### STOPP

Der Zweig wird geschlossen, wenn einer der folgenden Befunde eintritt:

- S oder H waren vor der Probe nicht kontrolliert;
- die Wirkung bleibt bei L-zu-S-Ablation bestehen;
- die Wirkung wandert beim vollstaendigen L-Tausch nicht mit;
- eine lokale Spur-, Gegenvariablen- oder Hysteresebaseline erklaert den
  gesamten Verlauf gleichwertig;
- nur ein Summenwert, eine feste Musterwellenlaenge oder ein Attraktor wird
  beobachtet;
- das Ergebnis haengt von Observer, Label, Schwelle oder ausgewaehlter Probe
  ab;
- funktionaler Verlust ist nur Leaky-Zerfall, Reset oder Ablaufzeit.

### KORREKTUR

Der Vertrag wird korrigiert, wenn technische Reproduzierbarkeit,
Zustandsangleichung oder gleiches Baselinebudget nicht nachweisbar sind. Eine
Korrektur darf keine Mechanik anhand eines gewuenschten Resultats erweitern.

### OFFEN

Der Befund bleibt nur offen, wenn E0 bis E4 vorregistriert gemeinsam getragen
werden und keine enge Baseline den gesamten Verlauf mit festem Parametersatz
reproduziert. Die zulaessige Bezeichnung bleibt dann zunaechst:

> verteilte kausale Nichtseparierbarkeit im gemeinsamen MCM-Feld

Memory, Organisation und Topologie benoetigen weitere eigene Nachweise.

## 9. Was dieser Vertrag noch nicht freigibt

Der Vertrag waehlt nicht:

- eine L-Dimension oder L-Gleichung;
- lokalen L-Fluss, Kreuzdiffusion oder Materialerhaltung;
- eine Testdatei, ein Video, einen Ton oder eine Browserseite;
- konkrete Dauer, Amplitude, Schwelle oder Stichprobengroesse;
- einen Runner oder produktive Runtimeaenderung.

Die vorhandene AV-Infrastruktur ist nur technische Anschlussfaehigkeit. Eine
Ausfuehrung ohne kausal begruendeten Traeger waere lediglich eine erneute
Messung des bekannten schnellen Feldes.

## Quellen und Projektgrundlagen

- `mcm_field_organism/browser_world_contract.py`: passive externe
  `static -> moving -> static`-Browserwelt ohne Rohbildspeicherung,
  Sensorspeisung oder Rueckschreibung.
- `mcm_field_organism/asynchronous_audio_video_partition_probe.py`:
  kontrollierte Null-, Audio-, Video- und AV-Arme sowie Reproduktion,
  Partitionierungs- und Reihenfolgekontrolle.
- A. F. Villaverde,
  [Observability and Structural Identifiability of Nonlinear Biological Systems](https://pmc.ncbi.nlm.nih.gov/articles/PMC5085250/),
  2016. Methodische Grundlage fuer unterscheidbare innere Zustaende ueber
  kontrollierte Ein-/Ausgabeverlaeufe.
- H. Miyazako, Y. Hori und S. Hara,
  [Turing Instability in Reaction-Diffusion Systems with a Single Diffuser](https://arxiv.org/abs/1309.0111),
  2013. Grenze gegen die Umdeutung geometrischer Muster in eine neue
  verteilte Organismusfunktion.

## Bester naechster Schritt

Als naechstes wird ein **statischer Traegerfamilienvergleich fuer verteilte
kausale Nichtseparierbarkeit** durchgefuehrt. Er vergleicht ohne Gleichung:

1. nur S-vermittelte Kopplung ortsgebundener lokaler Zustaende;
2. nichtkonservativen L-Eigenfluss auf der bestehenden Geometrie;
3. konservative Umverteilung einer begrenzten lokalen Feldgroesse;
4. variable Beziehungen oder Topologie nur als verbotene Gegenfamilie.

Der Vergleich muss entscheiden, ob eine Familie eine eigene physische
Traegerrolle besitzt, die durch den Evidenzvertrag pruefbar waere. Erst dann
darf hoechstens eine neue Mechanikfamilie wieder geoeffnet werden.
