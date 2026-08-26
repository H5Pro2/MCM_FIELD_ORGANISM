# S1-E: Audit der lokalen Skalardimension und verteilten Nichtseparierbarkeit

Stand: 2026-08-07

Status: `S1E_SECOND_LOCAL_STATE_NOT_JUSTIFIED_DISTRIBUTED_REQUIREMENT_OPEN`

Implementierung: nein

Forschungslauf: nein

## Forschungsfrage

Bildet die einzelne lokale Skalarrolle `L_i` selbst die strukturelle Grenze,
an der die bisher geprueften Substrathypothesen auf Relaxation, Spur,
Hysterese oder festen Gain zurueckfallen?

S1-E fuehrt keine neue Variable ein. Es prueft nur, ob eine zweite lokale
Zustandsdimension aus dem geforderten Lebenszyklus logisch folgt.

## Wichtige Dimensionskorrektur

Der S0-Vertrag bindet einen Skalar je bestehendem MCM-Feldort:

```text
lokal:       L_i in [-1, 1]
feldweit:    L = (L_1, L_2, ..., L_N) in [-1, 1]^N
```

Ein einzelner lokaler Skalar erzeugt daher keinen eindimensionalen
Gesamtzustand. Bei `N` Feldorten besitzt die verteilte L-Konfiguration bereits
`N` Freiheitsgrade. Ort, Nachbarschaft und die vorhandene MCM-Geometrie sind
Teil des Feldzustands, ohne dass L eigene Kanten oder Identitaeten erhaelt.

Mehr lokale Komponenten wuerden das Zustandsbudget vergroessern, aber nicht
automatisch eine offenere Entwicklung erzeugen. Zwei Leaky-Spuren bleiben
zwei Leaky-Spuren; ein Vektor fester Hystereseelemente bleibt eine
vorprogrammierte Kennlinienbank.

## Funktionsrollen des geforderten Lebenszyklus

Der bestehende funktionale Anforderungsrang trennt vier Rollen:

1. `R1` - Weltgeschichte kann einen inneren Zustand erreichen.
2. `R2` - Nach S/H-Angleichung kann ein geschichtlicher Unterschied bleiben.
3. `R3` - Dieser Unterschied kann die weitere S-Feldbildung beeinflussen.
4. `R4` - Weitere normale Weltgeschichte kann die alte Wirkung funktionslos
   und den Zustandsraum erneut anders erreichbar machen.

Ein einzelner skalarer Zustand kann diese Rollen prinzipiell in bekannten
Relaxations-, Gegenvariablen- oder Hysteresemodellen abbilden. Daraus folgt:

```text
notwendige zusaetzliche lokale Dimension: mindestens eine
notwendige zweite L-Dimension:             nicht hergeleitet
```

Der Lebenszyklus allein ist deshalb kein Dimensionsbeweis.

## Warum S1-D trotzdem scheiterte

S1-D verwendete an jedem Ort nur die lokale Differenz `S_i-L_i` und eine
feste zustandsabhaengige Mobilitaet. Der interne Austausch blieb auf einer
eindimensionalen lokalen Erhaltungslinie und zerfiel in dieselbe
B2-Ausgleichsbahn mit veraenderter Geschwindigkeit.

Das Scheitern folgt aus der gewaehlten separierbaren Austauschform, nicht aus
der Anzahl der L-Komponenten:

```text
Y_i = f(S_i, L_i)
X_i = h(S_i, L_i)
```

Jeder L-Ort traegt darin nur seine eigene feste Relaxationsantwort. Die
vorhandene S-Diffusion koppelt zwar die schnellen Feldorte, erzeugt aber keine
neue veraenderliche L-Konfigurationsfunktion.

## Fehlende strukturelle Eigenschaft

Die engste offene Zusatzanforderung lautet **verteilte kausale
Nichtseparierbarkeit**:

> Eine spaetere substratvermittelte Feldwirkung muss von der raeumlichen
> Konfiguration des verteilten L-Zustands abhangen und darf nicht als Summe
> unabhaengiger lokaler Spuren, Gegenvariablen, Mobilitaeten oder
> Hystereseelemente reproduzierbar sein.

Diese Anforderung behauptet noch keine Organisation, Topologie oder Memory.
Sie sagt nur, welche einfachere Erklaerung ein spaeterer Kandidat uebersteigen
muesste.

## Was daraus nicht folgt

S1-E gibt insbesondere nicht frei:

- einen zweiten L-Skalar je Ort;
- neue L-eigene Kanten oder adaptive Gewichte;
- globale Summen, Cluster oder Gewinner;
- eine feste Reaktions-Diffusionskinetik als Zielmechanik;
- vorgegebene Attraktor- oder Turingmuster;
- Ressourcenplaetze oder Materialtoken;
- eine Zieltopologie.

Auch direkter L-Fluss ist aus dem Lebenszyklus nicht zwingend ableitbar.
Falls er spaeter untersucht wird, ist einfache Diffusion die Pflichtbaseline
und kein Entwicklungsbefund.

## Statische Unterscheidung von Dimension und Nichtseparierbarkeit

| Frage | Dimensionsfrage | Nichtseparierbarkeitsfrage |
| --- | --- | --- |
| Wie viele Werte liegen pro Ort vor? | ein L-Skalar | unveraendert ein L-Skalar moeglich |
| Kann Geschichte lokal fortwirken? | prinzipiell ja | noch keine Feldorganisation behauptet |
| Wirken Orte nur unabhaengig? | durch Dimension nicht entschieden | muss gegen lokale Spurmodelle geprueft werden |
| Ist Geometrie kausal relevant? | nicht automatisch | Konfigurationsintervention erforderlich |
| Entsteht eine neue Topologie? | nein | ebenfalls nicht vorausgesetzt |
| Wird eine zweite Variable benoetigt? | nicht bewiesen | erst bei eigener Funktionsrolle begruendbar |

## Mindestinterventionen fuer eine spaetere Form

Eine spaetere konkrete Hypothese muesste mindestens erlauben:

1. **Gemeinsam gegen getrennt:** Gemeinsame raeumlich-zeitliche Geschichte
   gegen die Zusammensetzung getrennt gebildeter lokaler Zustaende.
2. **Geometrische Permutation:** Gleiche L-Werteverteilung bei veraenderter
   raeumlicher Anordnung.
3. **Lokale Neutralisierung:** Ein lokaler L-Anteil wird extern neutralisiert,
   ohne S/H oder die restliche L-Konfiguration zu veraendern.
4. **Konfigurationstausch:** Vollstaendige L-Konfigurationen wandern zwischen
   ansonsten angeglichenen Feldarmen.
5. **Rekonfiguration:** Weitere normale Weltgeschichte veraendert die
   Verteilung kausaler Beitraege ohne Phasenregel oder Observerrueckwirkung.

Diese Punkte sind nur externe Forschungsinterventionen. Sie werden nicht in
die Organismusfunktion geschrieben.

## Pflichtbaselines

Vor jeder positiven Aussage bleiben mindestens erforderlich:

- unabhaengige lokale Leaky-Spuren;
- unabhaengige lokale Hystereseelemente;
- lineare gekoppelte S-L-Moden;
- die S1-D-Mobilitaetsbaseline;
- lokaler S-L-Oszillator unter bestehendem S-Fluss;
- eine Ein-Diffusor-Reaktions-Diffusionsbaseline;
- feste Attraktor- oder Musterkinetik;
- geometrisch permutierte Sham-Konfigurationen;
- gleiches gesamtes Zustands- und Parameterbudget.

Ein Effekt, den eine dieser Formen erklaert, ist keine neue verteilte
Substratfunktion.

## Bedingung fuer eine spaetere zweite lokale Variable

Eine weitere lokale Rolle `K_i` waere erst zulaessig, wenn vor ihrer
Einfuehrung eine eigenstaendige Funktion benannt wird, die `L_i` und die
vorhandene MCM-Geometrie nicht tragen koennen. Zulaessige Begruendung waere
beispielsweise eine unabhaengige lokal bilanzierbare Eigenschaft mit eigener
Intervention und Gegenprognose.

Nicht ausreichend sind:

- mehr Kapazitaet;
- laengere Erinnerung;
- bessere Trennbarkeit;
- erwartete Clusterbildung;
- die Hoffnung auf komplexeres oder organischeres Verhalten.

## S1-E-Entscheidung

```text
ein L-Skalar je Ort als sichere Untergrenze:     ja
zweite lokale L-Dimension logisch erforderlich:  nein
S1-D durch Zustandszahl gescheitert:              nein
lokale Separierbarkeit als erkannte Grenze:       ja
verteilte Nichtseparierbarkeit nachgewiesen:      nein
Zustandsraumerweiterung zugelassen:               nein
Implementierung:                                  nein
Forschungslauf:                                   nein
```

S1-E verwirft die Annahme, dass mehr lokale Zustandsdimension automatisch den
fehlenden Entwicklungsschritt liefert. Der bestehende skalare L-Raum bleibt
offen. Die naechste Frage betrifft seine moegliche verteilte Feldfunktion.

## Aussagegrenze

Der Audit belegt keine nichtseparierbare Wirkung. Er belegt weder Praegung,
relative Feldzeit, Memory, inneren Kontext, Organisation, Topologie,
Semantik, Selbstregulation noch KI.

## Bester naechster Schritt

Der
[S1-F-Zulassungsvertrag](S1F_ZULASSUNGSVERTRAG_VERTEILTE_KAUSALE_NICHTSEPARIERBARKEIT.md)
ist gebunden. Er uebernimmt die belastbaren Evidenzstufen, Interventionen und
Gegenbaselines, ohne einen geschlossenen Traegerzweig wieder zu oeffnen. Als
naechstes folgt der inzwischen gebundene S1-G-Richtungsentscheid:
Feldwahrnehmung bleibt technisch aktiv, Substratimplementierung pausiert.
Darauf folgt W1-A mit dem technischen Wahrnehmungspfad-Bestandsaudit. Noch
keine Gleichung, Substratimplementierung oder Forschungslauf.
