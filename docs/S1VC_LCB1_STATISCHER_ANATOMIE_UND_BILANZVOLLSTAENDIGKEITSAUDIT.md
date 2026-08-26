# S1-VC: LCB-1 statischer Anatomie- und Bilanzvollstaendigkeitsaudit

> **Abschlussstatus nach S1-VD:** Die statisch konsistente Anatomie besitzt
> im vorhandenen Gradientenfeld keine endogen erreichbare
> Schleifenzirkulationsursache. LCB-1 ist terminal geschlossen.

## Freigabe und Grenze

S1-VC setzt die ausdrueckliche Freigabe fuer ausschliesslich den statischen
Anatomie- und Bilanzvollstaendigkeitsaudit von `LCB-1` um.

Nicht enthalten und weiterhin gesperrt sind:

- Bildungs-, Fortschreibungs-, Freigabe- oder Rueckwirkungsgleichung;
- Parameter, Schwellen, Raten und Zeitskalen;
- digitale Zustandsklasse oder Serialisierung;
- Runtime, API oder Snapshotintegration;
- Fixture, Testimplementierung oder Testausfuehrung;
- Feld-, Matrix- oder Realpfadlauf.

S1-VC prueft nur, ob das in S1-VB gebundene Motiv und seine Bilanzrollen
statisch eindeutig und fail-closed beschrieben werden koennen.

## Bestehende Feldanatomie

Der aktive Audio-Video-Feldpfad verwendet:

```text
zweidimensionale ganzzahlige Feldpositionen
symmetrische orthogonale Offsets (-1,0), (0,-1), (0,1), (1,0)
eindeutige Neuronenpositionen innerhalb einer Schicht
explizite visuelle Rasterzeilen und Rasterspalten
```

LCB-1 veraendert diese Anatomie nicht. Es werden keine Diagonalen, adaptiven
Kanten, Partnerkennungen oder neuen Nachbarschaftswege eingefuehrt.

## Exakter erster Ein-Schleifen-Korridor

### Geometrische Mindestbedingungen

Der erste Korridor ist nur zulaessig, wenn die vorhandene visuelle
Dockanatomie mindestens zwei Rasterzeilen und mindestens zwei benachbarte
Feldspalten enthaelt. Alle vier Orte muessen innerhalb desselben visuellen
Dockbereichs liegen; die Audio-/Visual-Dockgrenze und ein periodischer Wrap
duerfen nicht Teil des Motivs sein.

Vor jeder Geschichte werden zwei benachbarte Koordinatenwerte je Achse
gewaehlt. Daraus folgen genau vier vorhandene Feldorte:

```text
p00 = (r,   c)
p01 = (r,   c+1)
p10 = (r+1, c)
p11 = (r+1, c+1)
```

`r` und `c` sind feste Geometriekoordinaten, keine Kandidatenparameter.

### Vollstaendiges Kanteninventar

Genau die folgenden vier ungerichteten Nachbarschaftskanten bilden das
elementare Motiv:

```text
e_top    = {p00,p01}
e_right  = {p01,p11}
e_bottom = {p11,p10}
e_left   = {p10,p00}
```

Jede Kante muss bereits durch einen der vier orthogonalen Offsets und seinen
vorhandenen Gegenoffset getragen werden. Diagonalen und weitere Kanten
gehoeren nicht zur LCB-1-Anatomie.

### Eindeutige Schleifenidentitaet

Eine LCB-1-Schleife wird anatomisch durch folgende unveraenderliche Rollen
bestimmt:

```text
field_id
layer_id
geometry_id
vier verschiedene Feldpositionen
genau vier vorhandene ungerichtete Kanten
kanonische Achsenreihenfolge
```

Ein anderer Startpunkt derselben Rundfolge erzeugt keine zweite Schleife.
Die umgekehrte Rundfolge erzeugt ebenfalls keine zweite Schleife, sondern
nur die Gegenorientierung derselben Anatomie.

## Orientierungsanatomie

Aus der festen Achsenreihenfolge folgen ausschliesslich:

```text
CW:  p00 -> p01 -> p11 -> p10 -> p00
CCW: p00 -> p10 -> p11 -> p01 -> p00
```

Verbindliche Invarianten:

- eine reine Translation des gesamten Motivs erhaelt CW und CCW;
- eine orientierungserhaltende Vierteldrehung erhaelt die jeweilige
  Umlaufrichtung bei entsprechend permutierten Orten;
- eine Spiegelung vertauscht CW und CCW;
- eine zyklische Wahl eines anderen Startorts erhaelt die Orientierung;
- Umkehrung der Rundfolge vertauscht CW und CCW;
- Versuchsrolle, Dockinhalt oder Ergebnis darf keine Orientierung festlegen.

Eine Anatomie, die nach Spiegelung denselben absoluten Richtungsvorzug
behaelt, ist ungueltig.

## Ausschliessliche Bilanzanatomie

### Rollen

Fuer genau diese eine Schleife existieren konzeptionell nur:

```text
Q_cycle = endliche lokale Gesamtkapazitaet der Schleife
Q_free  = unbeanspruchter Anteil
Q_cw    = CW-beanspruchter Anteil
Q_ccw   = CCW-beanspruchter Anteil
```

Es gibt keine zusaetzlichen Knoten-, Kanten-, Partner-, Sequenz-, Welt- oder
Observerrollen innerhalb des Kandidatenzustands.

### Bilanzidentitaet

Die S1-VB-Identitaet ist anatomisch vollstaendig:

```text
Q_cycle = Q_free + Q_cw + Q_ccw
```

Sie ist eine statische Buchhaltungsidentitaet. Sie legt keine
Zustandsfortschreibung fest.

### Zulaessige Bilanzlagen

Anatomisch zulaessig sind nur endliche, nichtnegative Anteile, deren Summe
exakt `Q_cycle` ergibt. Darunter fallen:

- die neutrale Lage mit vollstaendig freier Kapazitaet;
- eine teilweise oder vollstaendig CW-beanspruchte Lage;
- eine teilweise oder vollstaendig CCW-beanspruchte Lage;
- eine gemischte Gegenbeanspruchung, solange beide Anteile dieselbe lokale
  Gesamtkapazitaet teilen.

Eine gemischte Lage wird nicht automatisch als neutral behandelt. Ob und wie
Gegenanteile spaeter funktional wirken oder sich freigeben, ist keine
Anatomiefrage und bleibt geschlossen.

### Verbotene Bilanzlagen

Fail-closed ungueltig sind:

1. fehlende oder mehrfach vorhandene Bilanzrolle;
2. nichtendliche Gesamtkapazitaet oder nichtendlicher Anteil;
3. negative Kapazitaet oder negativer Anteil;
4. `Q_cycle` ohne strikt positive endliche Kapazitaet;
5. Summe der drei Anteile ungleich `Q_cycle`;
6. unabhaengige Kapazitaet fuer CW und CCW statt einer gemeinsamen Grenze;
7. globale Kapazitaet, die mehrere Schleifen ausgleicht;
8. per Kante duplizierte Kopien derselben Schleifenkapazitaet;
9. Bilanzzustand ohne vollstaendige elementare Schleife;
10. Zustand auf einem offenen Drei-Kanten-Pfad;
11. Zustand auf einer Diagonale oder einer nicht vorhandenen Kante;
12. Kapazitaetsaenderung durch Observer, Ergebnis oder Versuchsrolle.

## Open-Path-Grenze

Der offene Kontrollarm wird als eigene frische Anatomie vor jeder Geschichte
gebildet. Ihm fehlt genau eine der vier Schleifenkanten.

Fuer diesen Arm gilt:

```text
keine geschlossene Schleife
-> keine LCB-1-Schleifenidentitaet
-> keine Q_cycle/Q_free/Q_cw/Q_ccw-Rollen
```

Das ist kein Reset und keine Loeschung eines vorhandenen Zustands, weil in
diesem Arm niemals eine LCB-1-Anatomie angelegt wurde. Unabhaengige
Kantenspuren der Gegenbaseline duerfen auf den drei vorhandenen Kanten
weiterhin existieren.

Eine Kante nach bereits erfolgter LCB-1-Bildung zu entfernen, ist in diesem
Korridor unzulaessig. Ohne separat gebundene lokale Freigabe- oder
Umlagerungsursache wuerde das Entfernen einer belegten Schleifenanatomie die
Bilanz nur verschwinden lassen. Eine solche Operation bleibt deshalb
fail-closed gesperrt.

## Ueberlappungsgrenze

In einem vollstaendigen Raster kann eine Kante zu zwei benachbarten
elementaren Schleifen gehoeren. S1-VC loest diese Mehrfachzuordnung nicht
durch geteilte oder globale Kapazitaet.

Fuer den ersten Korridor gilt daher:

- genau eine vorregistrierte Schleife besitzt eine LCB-1-Rolle;
- alle ueberlappenden oder angrenzenden Schleifen sind kandidatenseitig aus;
- die vorhandenen Feldkanten und der neutrale Feldfluss bleiben dennoch
  unveraendert;
- keine Kapazitaet wird zwischen Schleifen geteilt oder verschoben;
- eine spaetere Rastererweiterung benoetigt einen neuen ausdruecklichen
  Ueberlappungs- und Bilanzvertrag.

Damit ist der Ein-Schleifen-Korridor eindeutig, ohne bereits eine allgemeine
zweidimensionale LCB-1-Feldintegration zu behaupten.

## LCB-1-OFF- und Neutralgrenze

`LCB-1-OFF` bedeutet anatomisch:

```text
vorhandene Feldorte und Kanten unveraendert
keine LCB-1-Bilanzrolle vorhanden
keine LCB-1-Rueckwirkung zulaessig
```

LCB-1-OFF ist von einer aktiven neutralen LCB-1-Anatomie zu unterscheiden.
Die aktive neutrale Anatomie besitzt die endliche Gesamtkapazitaet vollstaendig
als `Q_free`, waehrend OFF gar keinen Kandidatenzustand besitzt. Eine spaetere
Abnahme muss dennoch fuer beide denselben unveraenderten Feldpfad fordern,
solange kein orientierter Anteil beansprucht ist.

## Statische Vollstaendigkeitsmatrix

| Anatomierolle | Vollstaendig gebunden | Offene Dynamikrolle |
|---|---:|---|
| vier verschiedene vorhandene Feldorte | ja | keine |
| vier orthogonale vorhandene Kanten | ja | Feldflussbildung |
| eine elementare geschlossene Schleife | ja | orientierte Ursache |
| CW/CCW unter Symmetrien | ja | Beanspruchungsrichtung |
| `Q_cycle/Q_free/Q_cw/Q_ccw` | ja | Fortschreibung und Freigabe |
| lokale Erhaltungsidentitaet | ja | atomarer Bilanzschritt |
| offene Kontrollanatomie | ja | kausal gematchte Exposition |
| Ein-Schleifen-Ueberlappungsgrenze | ja | spaetere Rasterkopplung |
| LCB-1-OFF gegen aktive Neutrallage | ja | spaetere Nullpfadabnahme |

Die offenen Dynamikrollen sind nicht verdeckte Anatomieluecken. Sie sind
ausdruecklich nicht Gegenstand von S1-VC und duerfen erst nach einem eigenen
Vertrag bearbeitet werden.

## Spaetere Fail-Closed-Anatomietests

S1-VC implementiert und startet keine Tests. Ein spaeterer reiner
Anatomievalidator muesste mindestens ablehnen:

- doppelte oder fehlende Feldorte;
- falsche Dimension oder nicht benachbarte Koordinaten;
- fehlende, zusaetzliche oder diagonale Kante;
- asymmetrischen Nachbarschaftsoffset;
- periodischen Wrap im ersten Korridor;
- Dockgrenzenueberschreitung;
- doppelte Schleifenregistrierung durch anderen Startpunkt;
- falsche CW/CCW-Transformation unter Spiegelung;
- offene Anatomie mit LCB-1-Bilanzrollen;
- ueberlappende aktive LCB-1-Schleifen;
- nichtendliche, negative oder nicht geschlossene Bilanz;
- Kapazitaetsaenderung ohne lokale Bilanzquelle.

Ein Validatorerfolg wuerde nur Anatomie und Bilanzformat bestaetigen. Er
koennte keine Bildungsursache oder Feldwirkung belegen.

## Auditentscheidung

```text
S1_VC_LCB1_SINGLE_ELEMENTARY_VISUAL_CYCLE_ANATOMY_COMPLETE
S1_VC_FOUR_NODE_FOUR_EDGE_IDENTITY_UNAMBIGUOUS
S1_VC_CW_CCW_SYMMETRY_INVARIANTS_BOUND
S1_VC_FINITE_SHARED_CYCLE_BALANCE_COMPLETE
S1_VC_TWELVE_INVALID_BALANCE_AND_ANATOMY_CLASSES_BOUND
S1_VC_OPEN_PATH_HAS_NO_LCB1_STATE
S1_VC_POST_FORMATION_EDGE_REMOVAL_FAIL_CLOSED
S1_VC_OVERLAPPING_CYCLES_EXCLUDED_FROM_FIRST_CORRIDOR
S1_VC_NO_EQUATION_NO_PARAMETER_NO_RUNTIME_NO_API_NO_SNAPSHOT_NO_TEST_NO_RUN
S1_VC_NO_MEMORY_OR_FIELD_CAPABILITY_CLAIM
```

Die LCB-1-Anatomie ist fuer genau einen begrenzten statischen
Ein-Schleifen-Korridor vollstaendig beschreibbar. Das bestaetigt weder ihre
Bildbarkeit noch ihre Feldwirkung.

## Bester naechster Schritt

S1-VD darf erst nach ausdruecklicher fachlicher Freigabe ausschliesslich als
statischer Kausalhistorien- und Angleichbarkeitsaudit pruefen, ob zwei
zulaessige normale Feldgeschichten `H_CW` und `H_CCW` fuer dieselbe
S1-VC-Schleife vorab konstruiert werden koennen und ob eine gemeinsame
Fortsetzung alle unabhaengigen Knoten-, Kanten- und Baselinezustaende vor der
Probe angleichen kann.

S1-VD darf keine LCB-1-Gleichung, Parameter, Zustandsimplementierung,
Runtime, API, Snapshotintegration, Fixture, Testausfuehrung oder Feldlauf
einfuehren. Ist die vollstaendige Angleichung bereits statisch unmoeglich,
wird der LCB-1-Vergleich als `INVALID_HISTORY_MATCH` gestoppt.

## Projektgrundlagen

- [S1-VB Funktions- und Falsifikationsvertrag](S1VB_LCB1_STATISCHER_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG.md)
- [S1-VA Kandidatenraumaudit](S1VA_STATISCHER_KANDIDATENRAUMAUDIT_LOKALE_TECHNISCHE_URSACHEN.md)
- [Aktive Audio-Video-Feldgeometrie](../mcm_field_organism/audio_video_field_geometry.py)
- [Aktive MCM-Neuronenschicht](../mcm_field_organism/mcm_neuron_layer.py)
