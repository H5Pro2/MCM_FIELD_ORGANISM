# S1-TV: Statischer Funktions- und Falsifikationsvertrag relationale Feldmotivwirkung

## Status und neue Richtungsentscheidung

S1-TV oeffnet nach der abgeschlossenen Konsolidierung S1-TU genau eine neue
Forschungsrichtung fuer eine feldinterne geschichtsabhaengige Wirkung. Das
Ziel ist keine klassische Speicherung und kein Wiedereroeffnen der
geschlossenen Substrat-, DTS-1-, G2/D3- oder Capacity-Clamp-Zweige.

S1-TV bindet nur Funktion, Gegenprognosen, Interventionen,
Verwerfungsbedingungen und Aussagegrenzen. Es enthaelt keine Gleichung,
Parameter, Zustandsanatomie, Runtime, Implementierung, Testausfuehrung oder
Feldlauf.

```text
ONE_RELATIONAL_TWO_EDGE_FIELD_MOTIF_FUNCTION_DIRECTION_BOUND
NO_STORAGE_MODEL_NO_EQUATION_NO_RUNTIME_NO_RUN
```

## Geometrische Ausgangslage

Die vorhandene kontrollierte Vier-Knoten-Geometrie ist eine offene Linie:

```text
node-a -- node-b -- node-c -- node-d
```

Sie besitzt drei kanonische ungerichtete Kanten:

```text
e_ab, e_bc, e_cd
```

Ein geschlossener Zyklus ist nicht vorhanden und wird nicht hinzugefuegt.
Die kleinsten vorhandenen relationalen Nachbarschaften sind deshalb die
beiden ueberlappenden Zwei-Kanten-Motive:

```text
M_left  = e_ab : e_bc
M_right = e_bc : e_cd
```

S1-TV veraendert weder Geometrie noch Kanteninventar.

Statischer Herkunftsbeleg:

```text
reports/s1rk_four_node_fresh_manifest.json
  SHA-256 19cc753c110b64d1d48cabe46be190a01247995053da442dd4cefcd344ea8bfc
edge_inventory.digest
  9961eddd8c8a7ad845c9ab43af23f8ae5380c72ffae06c2e0af202cda49c3529
geometry_class
  FOUR_NODE_OPEN_LINE_S1PZ
```

## Genau eine Kandidatenrichtung

```text
RFM-1_LOCAL_RELATIONAL_TWO_EDGE_FIELD_MOTIF
lokale relationale Zwei-Kanten-Feldmotivwirkung
```

RFM-1 fragt, ob normale Feldgeschichte neben aktuellen Knoten- und
Einzelkantenlagen eine lokale gemeinsame Disposition zweier aneinander
anschliessender Kanten hervorbringen kann. Diese Disposition darf keinen
Eingangsinhalt, kein Ereignislabel, keine Armrolle und keine historische
Sequenz speichern.

Sie ist nur dann fachlich eigenstaendig, wenn sie nicht aus der getrennten
Menge der beiden beteiligten Kantenwerte, ihrer Summe, einem Knotenwert oder
einer festen Kopplung berechnet werden kann.

## Eigene Funktionsprognose

Die kleinste Gegenprognose lautet:

```text
identischer aktueller Rezeptorkontakt
+ identische aktuelle S- und H-Vektoren
+ identische Einzelkantenlagen und lokale Randwerte
+ identische lokale und globale Gesamtbudgets
+ unterschiedliche endogen entstandene relationale Motivdisposition
-> unterschiedliche signed Fortsetzung der naechsten identischen Feldprobe
```

Die Prognose betrifft die weitere Feldfortsetzung, nicht das Auslesen eines
gespeicherten Inhalts. Die Wirkung muss am gemeinsamen Mittelknoten und an
mindestens einem nachgelagerten Knoten messbar sein, ohne einen globalen
Zuteiler oder einen getrennten Lesepfad zu verwenden.

## Strenge Nichtseparierbarkeitsbedingung

RFM-1 ist nur dann nicht trivial, wenn fuer mindestens ein vorregistriertes
Zustandspaar gemeinsam gilt:

- jeder aktuelle Knotenwert ist gleich;
- jeder aktuelle Einzelkantenwert ist gleich;
- jede lokale Kantensumme und jedes Gesamtbudget ist gleich;
- aktuelle Eingabe, S, H, Feldtick und Geometrie sind gleich;
- nur der gemeinsame relationale Motivbeleg unterscheidet sich;
- die naechste identische Probe erzeugt eine unterschiedliche signed
  Feldfortsetzung.

Kann die relationale Rolle aus unabhaengigen Kantenrecords rekonstruiert oder
als zusaetzlicher Skalar pro Kante umgeschrieben werden, wird RFM-1 verworfen.

## Endogene Bildung

Die unterschiedliche Motivdisposition darf ausschliesslich durch normale
Rezeptor- und Feldgeschichte entstehen. Zulaessig ist nur kausale lokale
Feldfortschreibung entlang der vorhandenen Geometrie.

Verboten sind:

- explizite A-/B-/Arm- oder Ergebnislabels;
- Ereigniszaehler, Phasencodes oder Sequenzpuffer;
- Reward, Zielwert oder nachtraegliche Auswahl;
- Replay frueherer Rezeptordaten;
- Reset, Neustart oder armweise Initialisierung;
- Zugriff auf Comparatorresultate oder spaetere Checkpoints.

## Pflichtintervention

Vor jeder Gleichung muss eine direkte relationale Intervention spezifiziert
werden, die zwei formal gueltige Zustandslagen erzeugt oder konstruktiv
angleicht:

```text
alle Knoten-, S/H-, Einzelkanten- und Budgetmarginalen unveraendert
relationale Motivdisposition vertauscht oder neutralisiert
identische anschliessende Probe
```

Die Intervention darf keine Kante, keinen Knotenwert und keine Probe
skalieren. Verschwindet die Felddifferenz bei unveraenderter relationaler
Disposition oder bleibt sie trotz neutralisierter Disposition bestehen, ist
die behauptete relationale Ursache nicht isoliert.

## Symmetrieprognose

Die offene Linie besitzt eine Spiegelung:

```text
node-a <-> node-d
node-b <-> node-c
M_left <-> M_right
```

Gespiegelte Geschichte, gespiegelter relationaler Zustand und gespiegelte
Probe muessen eine entsprechend gespiegelte signed Feldfortsetzung liefern.
Ein fester Links-/Rechts-Bias oder eine von Knotennamen abhaengige Wirkung ist
ungueltig.

## Pflichtgegenbaselines

RFM-1 muss spaeter mit jeweils einem unveraenderten Parametersatz ueber alle
Arme gegen mindestens folgende Erklaerungen bestehen:

| Baseline | Zu widerlegende einfachere Erklaerung |
|---|---|
| aktueller Kontakt und schneller S/H-Kern | die Differenz liegt noch in Eingang, S oder H |
| Fixed Adapter und permanentes Gewicht | eine feste Kopplung erklaert die Fortsetzung |
| Leaky, Integrator und Retentionswert | ein unabhaengiger lokaler Skalar traegt die Geschichte |
| B4 Linear Coupled und statische Rekurrenz | lineare Nachbarschaftskopplung erklaert die Motivwirkung |
| Mehrzeitskalenbank | mehrere passive Nachwirkungen erklaeren die Differenz |
| Delay und Replay | fruehere Eingaben werden nur verzoegert erneut wirksam |
| F3, CONST-V und Normalisierung | bestehende Feldumformung oder Skalierung reicht aus |
| DTS-1/T1 und Capacity-Clamp | freie oder blockierte Einzelkantenkapazitaet erklaert den Verlauf |
| G2/D3 und Free/Blocked | bekannte Zustandsunterteilungen werden nur umbenannt |
| unabhaengige Einzelkantenbank | zwei getrennte Kantenrecords reproduzieren alle Readouts |
| statischer Zweikantenoperator | eine zustandslose nichtlineare Funktion der aktuellen beiden Kanten reicht aus |
| gemeinsamer multivariater Integrator | ein Vektorintegrator ohne relationale lokale Ursache reproduziert den Verlauf |

Die letzten drei Rollen sind notwendige neue Gegenbaselinefunktionen, noch
keine Implementierungsfreigabe.

## Messrollen

Ein spaeterer Kandidatenvertrag muss vor seiner Gleichung direkt binden:

- vollstaendige aktuelle Rezeptor-, S- und H-Lage;
- alle aktuellen Knoten- und Einzelkantenmarginalen;
- beide kanonischen Zwei-Kanten-Motivrollen;
- endogene Bildung unter mindestens zwei kontrollierten Geschichten;
- S/H- und Marginalangleichung vor derselben Probe;
- signed Feldfortsetzung an allen vier Knoten;
- relationale Intervention und Nullintervention;
- Spiegelpaarbeleg fuer `M_left` und `M_right`;
- vollstaendig deaktivierten bitgenauen Feldkern-Nullpfad;
- Residuen gegen alle Pflichtgegenbaselines.

Eine unterschiedliche interne Digestidentitaet allein ist kein Beleg.

## Verwerfungsbedingungen

RFM-1 wird fail-closed verworfen oder als Baseline eingeordnet, wenn:

- nach Angleichung von Eingang, S, H und Marginalen keine Feldwirkung bleibt;
- die Motivrolle aus Knoten- oder Einzelkantenwerten rekonstruiert werden kann;
- ein zusaetzlicher unabhaengiger Kanten-, Leaky-, Integrator- oder
  Retentionszustand alle Readouts reproduziert;
- ein statischer Zweikantenoperator der aktuellen Lage ausreicht;
- Delay, Replay, Mehrzeitskalenbank, DTS-1/T1, Clamp oder G2/D3 den
  Gesamtverlauf fair erklaert;
- die Wirkung Labels, Sequenzpuffer, Ergebniszugriff oder Reset benoetigt;
- die Spiegelprognose verletzt wird;
- die relationale Intervention zugleich andere Feld- oder Marginalwerte
  aendert;
- der deaktivierte Pfad vom unveraenderten Feldkern abweicht;
- verschiedene Arme nachtraeglich verschiedene Parameter benoetigen.

Ein Negativbefund darf nicht innerhalb desselben registrierten Schritts durch
neue Rollen, Messwerte oder Parameter repariert werden.

## Beziehung zur hypothetischen MCM-Memory-Entwicklungsrichtung

RFM-1 ist zunaechst eine Hypothese ueber geschichtsabhaengige relationale
Feldfortsetzung. Es muss keine klassische Speicherfunktion nachbilden und ist
nicht selbst die gesuchte hypothetische MCM-Memory.

Erst falls eine spaetere technische Abnahme zusaetzlich kontrollierte
Abschwaechung, Interferenz, endliche Beanspruchung, Freigabe und erneute
Nutzbarkeit zeigt, darf getrennt geprueft werden, ob die Wirkung fuer die
hypothetische MCM-Memory-Entwicklungsrichtung relevant ist.

Die S1-TU-Kandidatenhuelle bleibt inaktiv und wird durch S1-TV nicht
reaktiviert. Ob sie spaeter fuer RFM-1 geeignet ist, muss erst nach Anatomie-
und Bilanzbindung separat auditiert werden.

## Aussagegrenze

S1-TV bindet eine technische Forschungsfrage. Es existiert noch keine
relationale Motivmechanik und kein Funktionsbefund. Weitergehende
Faehigkeits- oder Interpretationsaussagen sind nicht Gegenstand dieses
Vertrags.

## Verbindliche Entscheidung

```text
S1_TV_RFM1_RELATIONAL_FIELD_MOTIF_FUNCTION_AND_FALSIFICATION_BOUND
OPEN_LINE_TWO_EDGE_MOTIFS_WITH_NONSEPARABLE_COUNTERPREDICTION
NO_STORAGE_CLAIM_NO_ANATOMY_NO_EQUATION_NO_IMPLEMENTATION_NO_RUN
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-TW als statischer Geometrie-, Symmetrie-
und Nichtseparierbarkeitsanatomie-Audit. Er muss ausschliesslich klaeren:

- welche kanonischen Zwei-Kanten-Motive die offene Linie besitzt;
- welche relationale Zustandsrolle ueber Einzelkantenmarginalen hinaus
  minimal erforderlich waere;
- welche Symmetrie-, Null- und Rekonstruktionszustaende ungueltig sind;
- ob die Rolle strukturell von einer Einzelkantenbank, einem multivariaten
  Integrator und einem statischen Zweikantenoperator verschieden bleibt.

S1-TW darf keine Dynamikgleichung, Parameter, Runtime, Implementierung,
Testausfuehrung oder Ergebnisentscheidung enthalten. Bleibt keine
nichtseparierbare Rolle uebrig, wird RFM-1 sofort gestoppt.
