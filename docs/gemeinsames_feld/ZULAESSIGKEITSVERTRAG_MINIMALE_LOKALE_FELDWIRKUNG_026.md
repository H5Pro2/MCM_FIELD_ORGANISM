# Zulässigkeitsvertrag minimale lokale Feldwirkung 026

## Status

Dieser Vertrag ist eine unveränderliche Architektur- und Prüfgrenze auf
Evidenzstufe E0. Seine Runtimefreigabe lautet `CONTRACT_ONLY`.

Er ist keine Neuronenübergangsfunktion und enthält keine Feldgleichung,
Gewichtung, Schwelle oder Zeitkonstante.

## Ausgangspunkt

Die [Aktuelle Feldruntime-Geschichtsnullfunktion 025](AKTUELLE_FELDRUNTIME_GESCHICHTSNULLFUNKTION_025.md)
zeigt:

```text
lokale Vorfeldproben sind im MCMNeuronDrive vorhanden
-> Rezeptorprojektionsbaseline ignoriert sie
-> nach vollständiger Angleichung bleibt keine Geschichtswirkung
```

Vor Memory, Beziehung oder Topologie fehlt damit zuerst eine einfachere
Funktion:

> Ein lokaler Feldzustand aus dem vollständig abgeschlossenen Vortakt muss die
> nächste lokale Neuronenantwort kausal mitbestimmen können.

## Zugelassene Eingangsrollen

Ein erster isolierter Kandidat darf ausschließlich lesen:

1. aktuellen eigenen Rezeptorkontakt oder dessen ausdrückliche Abwesenheit,
2. lokale Feldproben aus dem vorherigen abgeschlossenen Takt,
3. deren technische relative Positionen.

Nicht zugelassen sind für diesen ersten Versuch:

- vorherige eigene Aktivierung oder eigener Nachhall als Rückkopplung,
- ältere Feldtakte,
- zusätzlicher Geschichtsträger,
- gespeicherte Nachbaridentitäten, Kanten oder Gewichte.

Die Eigenzustandsrückkopplung wird nicht grundsätzlich für das spätere System
verworfen. Sie bleibt nur für `GF_001` ausgeschlossen, damit lokale Feldwirkung
nicht mit Persistenz vermischt wird.

## Atomare Kausalität

Der einzige zulässige Zeitpfad lautet:

```text
vollständiges Feld(t)
+ Weltkontakt(t+1)
-> lokale Wahrnehmung für jedes Neuron
-> unabhängige Vorschläge
-> vollständiges Feld(t+1)
```

Kein Neuron darf einen bereits aktualisierten Nachbarn desselben Takts lesen.
Technische Iterationsreihenfolge darf das Ergebnis nicht verändern.

## Räumliche Anforderungen

Die technische Anatomie stellt zu jedem Offset sein Gegenstück bereit. Ein
Kandidat muss deshalb:

- gegenüber der Reihenfolge lokaler Samples invariant sein,
- bei Spiegelung der Geometrie kanonisch mitspiegeln,
- dieselbe Übergangsfunktion an jedem Neuron verwenden,
- dieselbe Funktion an allen Docks verwenden,
- ohne Quelle exakt ruhig bleiben.

Spiegeläquivaranz bedeutet nicht, dass links und rechts im selben Weltzustand
unterscheidungslos sein müssen. Es bedeutet:

```text
gespiegelte Welt + gespiegelte Anatomie
-> gespiegelte Feldantwort
```

Eine im Code versteckte Vorzugsrichtung ist unzulässig.

## Zustandsgrenze

Der erste Kandidat darf nur eine begrenzte aktuelle Aktivierung ausgeben.

Für `GF_001` bleiben ausgeschlossen:

- Nachhalländerung,
- Eigenzustandsrückkopplung,
- langsame Spur,
- Beziehung oder Ressource,
- adaptive Parameter,
- Update einer Topologie.

Damit kann ein positiver Ein-Takt-Befund keine Geschichte über den vorhandenen
lokalen Vortakt hinaus tragen.

## Pflichtkontrollen

Jede Methodik für `GF_001` benötigt mindestens:

1. reine Rezeptorprojektionsbaseline,
2. Hold-State-Baseline,
3. Ablation aller lokalen Feldproben,
4. Ablation des aktuellen Rezeptorkontakts,
5. Permutation der Sample-Iteration,
6. Permutation der Neuronen-Iteration,
7. Spiegelung der vollständigen Geometrie,
8. Nullquellenkontrolle,
9. getrennte Prüfung von Nullkontakt und Rezeptorabwesenheit,
10. lokale Wirkung innerhalb und zwischen Docks,
11. unabhängigen Neuaufbau jedes Zweigs,
12. vollständige Observerentfernung.

Nur wenn eine Wirkung bei Ablation der lokalen Proben verschwindet, ist sie
kausal lokale Feldwirkung.

## Verbotene Rollen

Nicht eingeführt werden dürfen:

- Nachhallupdate oder Zerfallsrate,
- vorherige Eigenzustandsrückkopplung,
- Geschichtsträger oder Sequenzarchiv,
- persistente oder adaptive Kante,
- Beziehung, Ressource oder Allokation,
- Schwelle oder Spikepflicht,
- Richtungslabel oder Modalitätsgewicht,
- globale Normalisierung oder Gewinnerwahl,
- Musterklasse, Semantik oder Zielantwort,
- Reward, Lernregel oder Zieltopologie,
- Observer-Writeback.

## Interpretationsgrenze

Ein positiver Versuch darf höchstens tragen:

```text
lokale Vorfeldprobe
-> kausaler Anteil an der nächsten Aktivierung
```

Er zeigt nicht:

- organische Entwicklung,
- Memory,
- Beziehung oder Topologie,
- Lernen,
- Musterbildung,
- semantische Resonanz,
- eine später möglicherweise als Feldintelligenz interpretierbare offene
  Feldfähigkeit.

Eine feste Übergangsfunktion bleibt eine Forschungsbaseline. Wiederholte
Ausbreitung derselben Funktion ist feste Rekurrenz und kein entwickeltes
Nervengerüst.

## Evidenzgrenze

```text
Vertragsinvarianten:       E1
lokale Feldwirkung:        E0
organische Felddynamik:    E0
entwickelte Topologie:     E0
organisches Memory:        E0
```

Feldintelligenz ist weder Versuchsziel noch Bewertungsachse dieses Vertrags.
Der Begriff darf nur rückblickend erwogen werden, falls spätere offene
Feldentwicklung über die hier geprüften festen Baselines hinausgeht.

## Stopplinie

`GF_001` bleibt bis zu einer vollständigen Methodik geschlossen. Die
[GF_001-Methodik](GF_001_METHODIK_MINIMALE_LOKALE_FELDWIRKUNG.md) erfüllt
diese Bedingung inzwischen ausschließlich für einen passiven synthetischen
Lauf. Dieser Vertrag gibt weiterhin weder eine konkrete MCM-Gleichung noch
eine Runtime-Änderung frei.

## Nächster Prüfpunkt

`GF_001` ist für eine kleine synthetische gemeinsame Feldgeometrie
vorregistriert. Mehrere einfache symmetrische lokale Wirkungsbaselines müssen
im nächsten passiven Lauf gegeneinander geprüft werden, ohne eine davon als
MCM-Mechanik auszuwählen.

Der Lauf muss zuerst klären:

```text
Welche beobachtbare Ein-Takt-Funktion entsteht überhaupt
durch das Lesen lokaler Vorfeldproben,
und welche Teile sind nur Folge der fest gewählten Baseline?
```

Reale asynchrone Audio-Video-Zeit bleibt davon getrennt und weiterhin
geschlossen.
