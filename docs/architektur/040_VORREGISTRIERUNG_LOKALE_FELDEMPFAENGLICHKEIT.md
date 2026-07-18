# Vorregistrierung einer lokalen Feldempfänglichkeit

## Status

Passiver Kandidatenvergleich auf `E0 / PREREGISTERED`.

Dieses Dokument gibt genau einen isolierten Kandidaten für eine technische
Vergleichsprüfung frei. Es ergänzt weder den Runtime-Zustand noch die
Neuronenschnittstelle. Ein positiver Lauf wäre kein Nachweis für entwickelte
Topologie, organisches Memory oder Feldintelligenz.

## Forschungsfrage

Der kleinste Vergleich fragt:

> Reicht eine einzige lokale, begrenzte und geschichtsabhängige
> Feldempfänglichkeit pro bestehendem MCM-Neuron aus, um nach Angleichung von
> Aktivierung und schnellem Nachhall eine spätere lokale Feldweiterleitung
> kausal zu verändern?

Damit wird zunächst nur geprüft, ob ein minimaler lokaler Träger die in der
Grundnull fehlende Funktion technisch tragen kann. Beziehungen, Mitglieder,
Richtung und Semantik werden nicht dargestellt.

## Kandidat C1

Für die passive Prüfung erhält jedes vorhandene Neuron genau einen zusätzlichen
skalaren Kandidatenzustand:

```text
z_i in [-1, 1]
```

`z_i` wird vorläufig als lokale Feldempfänglichkeit bezeichnet. Der Name ist
keine Funktionsbehauptung und keine spätere Runtime-Bezeichnung.

Für die vorhandene lokale Aktivierung `x_i` sei:

```text
L_i(x) = Summe über lokale Nachbarn j: (x_j - x_i)
```

Bei real vorhandenem lokalem Rezeptorkontakt `c_i` lautet der isolierte
Bildungskandidat:

```text
dz_i/dt = (1 - z_i^2) * c_i * L_i(x)
```

Bei Kontaktabwesenheit gilt:

```text
dz_i/dt = 0
```

Es gibt keine Lernrate, Schwelle, feste Zerfallszeit oder globale
Normalisierung. Die Faktoren `1 - z_i^2` begrenzen nur den offenen
Kandidatenzustand. Ein gemessener Nullkontakt bleibt von Kontaktabwesenheit
getrennt.

## Spätere passive Leserfunktion

Nach zeitlich abgeschlossener Bildung wird eine kontaktfreie, in allen Zweigen
identische lokale Feldprobe verwendet. Der Kandidat verändert dabei nur die
symmetrische lokale Weiterleitung:

```text
dx_i/dt = (1 / tau) * [
    Summe über lokale Nachbarn j:
        (1 + (z_i + z_j) / 2) * (x_j - x_i)
]
```

Für:

```text
z_i = 0 für alle i
```

entsteht exakt die heutige kontaktfreie neutrale Feldgleichung. Der
paarweise symmetrische Faktor erhält ohne Weltkontakt den Feldmittelwert und
führt keine technische Vorzugsrichtung ein.

Der Leser enthält weiterhin die feste lokale Anatomie. Er zeigt deshalb
höchstens eine geschichtsabhängige Verformung dieser vorhandenen Anatomie,
nicht die freie Entstehung einer Beziehung.

## Strikte Phasentrennung

Der Vergleich umfasst nur drei Phasen:

```text
P0  frischer Kandidatenzustand z = 0
P1  lokale Weltgeschichte bildet einen möglichen Zustand z
P2  Aktivierung und Nachhall werden konstruktiv angeglichen
P3  eine identische kontaktfreie Feldprobe prüft genau eine spätere Wirkung
```

Während P3 fehlt Rezeptorkontakt. Dadurch gilt `dz/dt = 0`; die Probe schreibt
keine neue Kandidatengeschichte. Eine neu entstandene Aktivierung darf in
diesem Vergleich keinen weiteren Kandidatenzyklus auslösen.

Die konstruktive Angleichung in P2 ist eine experimentelle Isolation und keine
natürliche Feldkonvergenz.

## Versuchszweige

Mindestens folgende Zweige werden aus unabhängigen frischen Feldern aufgebaut:

```text
H+  lokale kausale Weltgeschichte
H-  vollständig gespiegelte Weltgeschichte
N   gleiche Kontaktmengen ohne lokale gemeinsame Feldwirkung
Z   Kandidatenzustand vor der Probe exakt auf null gesetzt
S   Kandidatenzustände von H+ und H- vor der Probe getauscht
E   Kandidatenzustände von H+ und H- vor der Probe gleichgesetzt
```

H+, H- und N müssen übereinstimmen in:

- realer Gesamtdauer,
- Zahl und Dauer der Rezeptorkontakte,
- Kontaktenergie pro Position nach kanonischer Spiegelabbildung,
- Neuronengeometrie,
- Feldparametern,
- Aktivierung und Nachhall zu Beginn von P3.

Sie dürfen sich nur in der zeitlichen lokalen gemeinsamen Feldwirkung während
P1 unterscheiden.

## Primäre Messung

Gemessen wird nicht `z` allein, sondern die vollständige Aktivierungsantwort
nach P3.

Ein enger kausaler Kandidatenbefund liegt nur vor, wenn:

1. H+ und H- in derselben festen Raumlage verschieden reagieren, nach
   kanonischer Spiegelrückabbildung aber exakt entsprechen,
2. der Unterschied beim Tausch von `z` vollständig mitwandert,
3. der Unterschied bei Gleichsetzung von `z` verschwindet,
4. der Unterschied im Nullzweig Z exakt verschwindet,
5. N trotz gleicher Kontaktmengen keine entsprechende Wirkung trägt,
6. Aktivierung und Nachhall vor P3 elementweise gleich sind.

## Pflichtkontrollen

Der isolierte Kandidat muss zusätzlich bestehen:

- grobe und feine Zeitteilung derselben P1-Geschichte,
- umgekehrte technische Neuronen- und Zweigreihenfolge,
- vollständige räumliche Spiegelung,
- zusätzliche Sensorabschlüsse ohne neue Quellenstütze,
- Snapshot und Wiederaufnahme zwischen P1 und P2,
- Snapshot und Wiederaufnahme unmittelbar vor P3,
- Beobachtung ohne Rückschreibung,
- vollständiger frischer Neuaufbau jedes Zweigs.

## Verbindliche Baselines

```text
B0  heutige neutrale Runtime mit z = 0
B1  schneller leaky Nachhall
B2  mehrere feste Nachhall-Zeitskalen
B3  unabhängiger Sättigungsintegrator des eigenen Kontakts
B4  begrenzter Integrator des Produkts c_i * L_i(x)
B5  feste statische lokale Weiterleitungsfaktoren
B6  Observer-Auswertung derselben Geschichte
```

B4 ist das stärkste Gegenmodell. Er verwendet dieselbe lokale Evidenz, ohne
eine organische Interpretation. Erklärt B4 Bildung und Spätwirkung vollständig,
ist C1 nur ein begrenzter lokaler Integrator mit nachgeschaltetem Leser.

Das wäre kein Fehlschlag des Vergleichs, sondern seine korrekte
Klassifikation.

## Vorab festgelegte Interpretationsgrenze

Ein positiver C1-Befund dürfte höchstens tragen:

```text
ein lokaler zusätzlicher Zustand kann die fehlende Spätwirkung technisch tragen
```

Er trägt nicht:

- entstandene Beziehung,
- entwickelte Feldtopologie,
- Ressourcenbeanspruchung,
- Abschwächung oder vollständige Lösung,
- Wiederbindung,
- organisches Memory,
- semantische Resonanz,
- Feldintelligenz.

Insbesondere zeigt die eingesetzte Leserfunktion nur kausale Mediation, weil
sie `z` ausdrücklich liest.

## Scheiterkriterien

C1 wird verworfen, wenn:

- Zeitteilung, Ereignisrate oder Iterationsreihenfolge das Ergebnis bestimmt,
- Spiegelung nicht kanonisch mitwandert,
- der Nullzustand nicht exakt die neutrale Feldgleichung ergibt,
- schnelle Zustände vor P3 nicht vollständig angeglichen sind,
- N dieselbe Wirkung ohne lokale gemeinsame Feldwirkung erzeugt,
- Wirkung ohne `z` oder trotz blockierter lokaler Weiterleitung bestehen
  bleibt,
- ein Cache, Observer oder nicht serialisierter Zustand benötigt wird,
- die Wirkung nur an `z`, nicht aber im Feldzustand sichtbar ist.

## Bewusste offene Grenzen

Dieser erste Vergleich prüft noch nicht:

- natürliche Abschwächung,
- vollständige Lösung,
- lokale Ressourcenfreigabe,
- andere Wiederbindung,
- Mehrzyklen,
- reale Audio-Video-Lebensgeschichte.

Der Kandidat hält ohne Bildungsevidenz seinen Zustand. Genau deshalb darf ein
positiver P3-Befund nicht als organisches Memory bezeichnet werden.

## Freigabegrenze

```text
passive isolierte Implementierung: freigegeben
Runtime-Zustand:                    gesperrt
Live-Pfad:                          gesperrt
Mehrzyklen:                         gesperrt
Topologiebehauptung:                gesperrt
Memorybehauptung:                   gesperrt
```

## Nächster Schritt

C1 wird ausschließlich in einem passiven Forschungsmodul implementiert. Der
erste Lauf endet nach P3 und berichtet Kandidat, Interventionen und B0 bis B6
getrennt. Erst der Befund entscheidet, ob der Kandidat technisch weiter
untersucht oder als bloßer Sättigungsintegrator geschlossen wird.
