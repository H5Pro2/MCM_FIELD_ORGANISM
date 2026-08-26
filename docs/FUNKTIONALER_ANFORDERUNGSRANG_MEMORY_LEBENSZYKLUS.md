# Funktionaler Anforderungsrang des Memory-Lebenszyklus

> **Operative Einordnung:** Dieser Audit bleibt als Anforderungsanalyse
> erhalten. Sein damaliger naechster Schritt ist durch den
> [Richtungsentscheid `Substrat vor Memorybefund`](RICHTUNGSENTSCHEID_SUBSTRAT_VOR_MEMORYBEFUND.md)
> ueberholt. S0, die lineare Referenzgleichung S1-A und ihre technische
> S1-B-Implementierung sind inzwischen gebunden. S2-A registriert jetzt die
> ersten kontrollierten Kausalvergleiche vor. Erst an diesem vorhandenen Substrat
> werden die hier beschriebenen Kausalrollen kontrolliert untersucht.

## Status

```text
Pruefart:                           statischer Kausal- und Dimensionsaudit
notwendige Kausalrollen:            vier
zwingende neue lokale Dimension:    mindestens eine
zwingende zweite L-Dimension:       nein
zwingender L-Eigenfluss:            nein
heutige Runtime ausreichend:        nein
neue Architektur freigegeben:       nein
```

## Forschungsfrage

Welche voneinander unterscheidbaren Kausalrollen benoetigt der geforderte
Lebenszyklus aus Bildung, spaeterer Wirkung, funktionaler Loesung und anderer
Wiederpraegung? Welche davon koennen S, H und ein hypothetisches skalares L
darstellen, und folgt daraus zwingend eine groessere lokale oder raeumliche
Architektur?

`Anforderungsrang` bedeutet in diesem Dokument die Anzahl funktional zu
trennender Kausalrollen. Er ist kein berechneter Matrixrang und keine
Behauptung ueber die minimale Dimension eines noch unbekannten nichtlinearen
Systems.

## 1. Vier notwendige Kausalrollen

### R1: Weltbedingte Erreichbarkeit

Normale Weltgeschichte muss den spaeter wirksamen inneren Zustand ueber den
technischen Rezeptor- und S-Feldpfad veraendern koennen.

```text
unterschiedliche zulaessige Weltgeschichte
-> unterschiedlicher vollstaendiger innerer Zustand
```

Eine Initialisierung, ein Observer oder eine besondere Schreibphase erfuellt
diese Rolle nicht.

### R2: Geschichtliche Unterscheidbarkeit

Nach Angleichung der schnellen Feldlage muss mindestens ein innerer
Zustandsunterschied verbleiben koennen. Sonst ist jede Geschichte mit der
aktuellen S-Lage vollstaendig beendet.

```text
gleiches S + gleiche weitere Weltzufuhr
aber unterschiedliche Vorgeschichte
-> mindestens ein unterschiedlicher innerer Vorzustand
```

Diese Rolle behauptet nur Persistenz eines kausalen Unterschieds, noch kein
Memory.

### R3: Funktionale Beobachtbarkeit im Feld

Der verbliebene Zustandsunterschied muss innerhalb der normalen Naturform die
weitere S-Feldtrajektorie beeinflussen. Ein nur serialisierter oder vom
Observer lesbarer Wert ist fuer das Projektziel wirkungslos.

```text
gleiche schnelle Ausgangslage + identischer Probeverlauf
-> unterschiedliche vollstaendige S-Fortsetzung aufgrund des inneren Zustands
```

### R4: Erneute Erreichbarkeit nach Funktionsverlust

Weitere normale Weltgeschichte muss einen zuvor wirksamen Unterschied
funktional irrelevant machen koennen. Danach muss derselbe Zustandsraum
erneut in einen anders wirksamen Zustand erreichbar bleiben.

```text
alte Wirkung vorhanden
-> weitere normale Geschichte
-> alte Wirkung nicht mehr kausal nachweisbar
-> andere Geschichte kann andere Wirkung hervorbringen
```

R4 verbietet Reset, Ablaufzeit und besondere Loeschphase. R4 ist eine
Anforderung an die Zustandsuebergaenge, nicht automatisch ein eigener
Zustandswert.

## 2. Rollenbelegung der heutigen Runtime

| Komponente | R1 erreichbar | R2 ueber S hinaus | R3 wirkt auf S | R4 wieder erreichbar | Einordnung |
|---|---:|---:|---:|---:|---|
| S / Activation | ja | nein nach S-Angleichung | ja | nur schnelle Feldfortsetzung | schnelle Wahrnehmungsrolle |
| H / Afterimage | ja | kurzzeitig ja | nein | ja durch feste Relaxation | nachgelagerte Spur |
| hypothetisches skalares L | prinzipiell ja | prinzipiell ja | prinzipiell ja | prinzipiell ja | noch keine zugelassene Naturform |

H erhoeht den funktionalen Rang fuer das gesuchte Ein-/Ausgabeverhalten nicht,
weil H in der aktiven Runtime nicht auf Activation zurueckwirkt. Es ist
technisch vorhanden und beobachtbar, aber fuer R3 kausal stumm.

## 3. Was aus dem Lebenszyklus dimensional folgt

### Sichere Untergrenze

Die bestehende Runtime benoetigt mindestens einen weiteren inneren
Freiheitsgrad, der sowohl durch S erreichbar als auch fuer die spaetere
S-Fortsetzung beobachtbar ist. Mit null neuen rueckwirkenden Zustaenden gilt
weiterhin die bekannte Markov-Grenze der aktuellen Activation.

### Keine Untergrenze von zwei

Aus den vier Lebenszyklusphasen folgt keine Mindestdimension von vier, zwei
oder einer anderen Zahl. Ein einzelner skalarer Zustand kann in bekannten
Relaxations-, Gegenvariablen- und Hysteresemodellen:

- durch Geschichte veraendert werden;
- nach S-Angleichung verschieden bleiben;
- spaeter auf die Ausgabe wirken;
- abgeschwaecht, ueberschrieben und erneut angeregt werden.

Damit ist eine zusaetzliche skalare Dimension die einzige derzeit begruendete
Dimensionsuntergrenze. Gerade diese minimale Realisierung kollidiert jedoch
mit den bereits geschlossenen Baselines.

### Keine automatische Folgerung fuer raeumlichen Fluss

Auch eine begrenzte Lebensdauer, Loesung und Wiederverwendung verlangen
mathematisch keinen eigenen L-Fluss. Ein lokaler Zustand kann alle diese
Eigenschaften durch seine lokale Fortschreibung zeigen.

Darum duerfen aus dem Lebenszyklus allein nicht abgeleitet werden:

- zweiter L-Skalar;
- L-Eigenfluss oder Kreuzdiffusion;
- Materialbudget oder freie Slots;
- adaptive Kanten;
- variable lokale Topologie.

Jede dieser Erweiterungen benoetigt eine eigene physische Kausalfrage.

## 4. Warum der bisherige Anforderungsrang nicht genuegt

Die Rollen R1 bis R4 definieren einen funktionsfaehigen geschichtlichen
Zustand. Sie unterscheiden aber noch nicht zwischen:

```text
lokaler interner Zustandsvariable mit Hysterese
und
verteilter feldvermittelter Reorganisation
```

Beide koennen denselben abstrakten Lebenszyklus erfuellen. Wird allein der
Lebenszyklus als Erfolgskriterium verwendet, kann eine bekannte lokale
Hysteresemechanik faelschlich als organisches MCM-Memory interpretiert werden.

Der Engpass ist daher nicht nachgewiesenermassen die Zustandsdimension. Der
Engpass ist die fehlende operationale Zusatzanforderung an die verteilte
Feldnatur des gesuchten Effekts.

## 5. Noch fehlende Feldanforderung

Als naechste Hypothesenebene darf untersucht werden:

> Entsteht die spaetere kausale Wirkung aus einer verteilten Konfiguration im
> gemeinsamen MCM-Feld, die nicht als Summe unabhaengiger lokaler Spuren,
> Gegenvariablen oder Hystereseelemente erklaert werden kann?

Diese Frage wird vorlaeufig **verteilte kausale Nichtseparierbarkeit**
genannt. Der Begriff behauptet keine Organisation und kein Memory.

### Minimal erforderliche Interventionen

Eine spaetere Evidenzordnung muesste mindestens folgende statische
Versuchsvergleiche definieren:

1. **Gemeinsam gegen getrennt:** Eine gemeinsame raeumlich-zeitliche
   Geschichte wird mit der Summe beziehungsweise Zusammensetzung getrennt
   zugefuehrter Teilgeschichten verglichen.
2. **Geometrische Permutation:** Die raeumliche Konfiguration eines inneren
   Zustands wird bei gleicher Werteverteilung permutiert. Eine Wirkung muss an
   der Feldgeometrie und nicht nur am Histogramm haengen.
3. **Lokale Neutralisierung:** Die Wirkung lokaler Zustandsanteile wird
   neutralisiert, ohne den schnellen S-Zustand oder die restliche
   Konfiguration auszutauschen.
4. **Konfigurationstausch:** Vollstaendige innere Konfigurationen werden
   zwischen ansonsten angeglichenen Feldzustaenden getauscht.
5. **Rekonfiguration:** Weitere normale Weltgeschichte muss die Verteilung
   kausaler Beitraege veraendern, ohne Observerrueckschreibung oder
   Phasenregel.

Diese Interventionen sind Forschungsinstrumente ausserhalb der
Organismusfunktion.

## 6. Pflichtbaselines der Feldanforderung

Verteilte Nichtseparierbarkeit ist allein noch kein positiver Befund. Sie
kann bereits durch bekannte gekoppelte Dynamik entstehen. Mindestens
erforderlich sind:

- heutiges S-H-Feld;
- unabhaengige lokale Leaky-Spuren;
- unabhaengige lokale Hystereseelemente unter bestehendem S-Fluss;
- lineare gekoppelte S-L-Moden;
- lokaler S-L-Oszillator unter S-Fluss;
- eine konkrete Ein-Diffusor-Reaktions-Diffusionsbaseline;
- feste Attraktor- oder Musterkinetik;
- gleich budgetierte Permutations- und Richtungsablationen.

Kandidat und Baselines muessen denselben gesamten Verlauf mit jeweils einem
festen vorregistrierten Parametersatz tragen.

## 7. Ergebnis des Anforderungsrangs

```text
notwendige Kausalrollen:              R1 bis R4
heutige rueckwirkende Geschichtsrolle: fehlt
minimale neue Zustandsuntergrenze:     ein erreichbarer und beobachtbarer Wert
zweite lokale Dimension begruendet:    nein
eigener L-Fluss begruendet:            nein
R1 durch mehr Dimension ersetzen:      nein
fehlende naechste Spezifikation:        verteilte kausale Nichtseparierbarkeit
```

Der Audit schliesst keine feldbasierte Entwicklung aus. Er verhindert, dass
eine groessere Architektur ohne ableitbare Funktion eingefuehrt wird. Die
naechste Forschung muss zuerst sagen, welches beobachtbare Feldverhalten eine
lokale interne Zustandsbaseline nicht erklaert.

## Quellen

- M. Petreczky, L. Bako und J. H. van Schuppen,
  [Realization theory of discrete-time linear switched systems](https://arxiv.org/abs/1103.1343),
  2011. Dient methodisch zur Trennung von Erreichbarkeit,
  Beobachtbarkeit und minimaler Realisierung. Die MCM-Dynamik wird damit nicht
  als lineares geschaltetes System behauptet.
- A. F. Villaverde,
  [Observability and Structural Identifiability of Nonlinear Biological Systems](https://pmc.ncbi.nlm.nih.gov/articles/PMC5085250/),
  2016. Dient fuer die operationale Unterscheidung innerer Zustaende durch
  kontrollierte Eingabe-Ausgabe-Verlaeufe.
- M. Heredia-Perez, D. A. Alvarez und D. Bedoya-Ruiz,
  [A State-of-the-Art Review of the Bouc-Wen Class Model of Hysteresis](https://doi.org/10.1007/s11831-025-10301-z),
  2026. Dient als Grenze gegen die Annahme, ein mehrphasiger geschichtlicher
  Lebenszyklus verlange automatisch mehrere Zustaende oder neue Feldphysik.

Die Rangordnung und ihre Uebertragung auf S, H und L sind Ableitungen dieses
Audits, keine aus den Quellen uebernommenen MCM-Befunde.

## Bester naechster Schritt

Dieser historische Folgeschritt ist durch S0, S1-A, S1-B, S2-A und den
technischen S2-B-Runnervertrag abgeloest. Der S2-C-Kern ist implementiert;
S2-C2 bindet den transienten B0/B2-Einzelbatchpfad, S2-C3 den
r1.a, Probe P, N8, Observer, Einpaardistanzen und C1-Identitaetskontrolle.
S2-C16 schliesst die kanonische A8/B8-End-to-End-Komposition. Der
S2-Zwischenentscheid stoppt weitere Referenzerweiterung ohne Kandidaten. Der
statische S1-C-Kandidatenvertrag ist gebunden. S1-D reduziert die gepruefte
MCM-spezifische Naturannahme auf eine Relaxationsbaseline. S1-E bestaetigt
die hier gebundene Dimensionsgrenze und bestimmt verteilte kausale
Nichtseparierbarkeit als offene Feldanforderung. Ihr statischer
S1-F-Zulassungsvertrag ist inzwischen gebunden
und oeffnet keinen geschlossenen Traegerzweig. Der S1-G-Richtungsentscheid
ist inzwischen gebunden:
Feldwahrnehmung bleibt technisch aktiv, Substratimplementierung pausiert. Als
naechstes folgt W1-A mit dem technischen Wahrnehmungspfad-Bestandsaudit.
Daraus folgt noch keine Vollmatrix, Forschungsentscheidung oder
Memorybefund.
