# S2-IX: Prospektiver Rezeptorgitter-Aequivalenzvertrag

## Status und Grenze

`STATIC_UINT8_RECEPTOR_GRID_EQUIVALENCE_CONTRACT_BOUND`

S2-IX bindet ausschliesslich eine prospektive read-only Gleichheitsregel fuer
die sichtbaren Positionen eines visuellen Kontextkandidaten. Die Regel ist
keine neue Wahrnehmungs-, Match- oder Memory-Schwelle. Sie darf nur auf Werte
angewendet werden, deren `uint8`-Rezeptorherkunft und deren unveraenderter
PPB-Aktualisierungspfad vollstaendig belegt sind.

S2-IV bleibt dauerhaft technisch gueltig und fachlich falsifiziert. S2-IX
aendert weder seine Belege noch seine Auswertung. Implementierung, Tests,
Runner, Zustandsaufrufe und ein neuer Kontextstatuslauf bleiben gesperrt.

## Funktionsfrage

Fuer jede sichtbare Position wird nicht gefragt, ob zwei beliebige Floats
nahe beieinander liegen. Geprueft wird ausschliesslich:

```text
Stammen Probe und Kandidatenkoordinate nachweislich aus demselben
uint8-Rezeptorgittercode, und ist die Kandidatenlinie positionsweise homogen?
```

Die Antwort besitzt nur zwei regulaere Werte:

- `SAME_RECEPTOR_GRID_POINT`;
- `DIFFERENT_RECEPTOR_GRID_POINT`.

Fehlende, gemischte oder widerspruechliche Herkunft ist kein dritter
regulaerer Wert. Sie stoppt die gesamte Anwendbarkeitspruefung fail-closed.

## Zulaessige Herkunft

### Direkter Rezeptorwert

Eine Proben- oder A-Koordinate ist nur zulaessig, wenn ein validierter
ReceptorReceipt-Beleg mindestens bindet:

- Bildbytes- und Frame-Digest;
- Rezeptor-, Konfigurations- und Quellendigest;
- Kanalposition `0..17`;
- originalen `uint8`-Gittercode `g in 0..255`;
- normalisierten Wert `float(g) / 255.0` und dessen Digest;
- unveraenderliche Vor-/Nachzustandsdigests des read-only Zugriffs.

Ein nachtraeglich aus einem Float berechnetes `round(255*x)` ist kein
Herkunftsbeleg.

### PPB-Prototypwert

Eine B-Koordinate ist nur zulaessig, wenn eine validierte, lueckenlose
Formationskette bindet:

- visuelle PPB-Bank, Slot, Konfiguration und `update_rate = 0.01`;
- Erzeugungsreceipt und geordnet alle Update-Receipts;
- zu jedem Formationsschritt den vorgelagerten ReceptorReceipt-Digest;
- den originalen Gittercode der betreffenden Koordinate je Schritt;
- Vor- und Nachzustandsdigest jedes Schritts;
- finalen Prototypwert, Support, Stabilitaet und Slotdigest.

Die Koordinate ist `HOMOGENEOUS_GRID_BOUND`, wenn die Menge aller gebundenen
Gittercodes ihrer Erzeugungs- und Updateframes exakt `{g}` ist. Die
Gleitkommawerte der gespeicherten Zwischen- und Endprototypen werden gegen die
unveraenderte PPB-Rekurrenz validiert, bestimmen den Gittercode aber nicht.

Enthaelt die Linie mehr als einen Gittercode, fehlt ein Schritt oder laesst
sich ein Vor-/Nachzustand nicht verketten, lautet der methodische Befund
`MIXED_OR_UNBOUND_PROTOTYPE`. Er wird niemals durch Rundung, L1 oder den
naechstgelegenen Gitterpunkt repariert.

Die Homogenitaetspruefung gilt fuer alle 18 visuellen Koordinaten des
Kandidaten. Nur die neun bereits gebundenen sichtbaren Positionen nehmen an
der Gleichheitsentscheidung teil. Die neun maskierten Werte werden weder
quantisiert noch ersetzt oder neu berechnet.

## Gleichheitsregel

Seien `gp` der belegte Gittercode der sichtbaren Probenposition und `gc` der
homogen belegte Gittercode derselben Kandidatenposition. Dann gilt exakt:

```text
gp == gc  -> SAME_RECEPTOR_GRID_POINT
gp != gc  -> DIFFERENT_RECEPTOR_GRID_POINT
```

Damit bleibt jede volle Stufe erhalten:

```text
abs(gp - gc) >= 1 -> sichtbarer Unterschied
```

Es gibt keine Epsilon-, ULP-, Absolut-, Relativ- oder L1-Schwelle in dieser
Regel. ULP und L1 duerfen nur diagnostisch berichtet werden.

Ein Kontextkandidat ist auf den sichtbaren Positionen genau dann
`APPLICABLE`, wenn alle neun Positionsbefunde `SAME_RECEPTOR_GRID_POINT`
lauten. Mindestens ein gueltiger `DIFFERENT_RECEPTOR_GRID_POINT` ergibt den
bestehenden Befund `VISIBLE_CONFLICT`. Jeder Herkunfts- oder Homogenitaetsbruch
stoppt vor einem regulaeren Anwendbarkeitsbefund fail-closed.

## Unveraenderte Masken- und Memory-Grenze

S2-IX ersetzt ausschliesslich die sichtbare Floatgleichheit in einer spaeter
gesondert freizugebenden privaten Anwendbarkeitspruefung. Unveraendert bleiben:

- B4, TSPM-1 und PPB-1 einschliesslich aller Parameter;
- native PPB-L1-Schwellen und `44/765`;
- gespeicherte Prototypwerte;
- die neun maskierten Ergaenzungswerte;
- Statuslogik, A/B-Symmetrie und Direktbaseline;
- API, Snapshot und Feldpfad.

Insbesondere darf die Regel keine maskierte Position auf einen Gitterwert
runden. Ein spaeterer Verbraucher erhaelt weiterhin exakt den gespeicherten
Kandidatenwert.

## Prospektive neutrale Fixture-Domain

Die Qualifikationsdomain ist unabhaengig von P1 und S2-IV vollstaendig vorab
gebunden. Alle Bilder sind erzeugbare `uint8`-Byte-Block-Bilder mit 18
Rezeptorkanalkoordinaten.

### Basiswerte

Fuer jeden `g in 0..255` existiert genau eine neutrale Basisfixture:

```text
fixture_id = s2ix-grid-gNNN
block_values = (g,) * 18
```

`NNN` ist der dreistellige Dezimalcode. Damit sind alle 256 Gitterpunkte,
einschliesslich `0`, `1`, `127`, `128`, `254` und `255`, vor jeder spaeteren
Auswertung festgelegt.

### Homogene Wiederholung

Fuer jeden der 256 Basiswerte werden PPB-Linien mit der vorab gebundenen
Anzahl identischer Updates

```text
R = {0, 1, 2, 3, 8, 31, 255}
```

gebildet. Alle `256 * 7 = 1792` Zellen muessen
`SAME_RECEPTOR_GRID_POINT` liefern. Der Wert `2` deckt den in S2-IW
beobachteten Stabilisierungspfad ab, ohne P1 zu verwenden.

Die niedrigen Updatezahlen qualifizieren nur die numerische Herkunftsregel.
Sie duerfen einen nach bestehendem PPB-Vertrag instabilen Zwischenstand nicht
als oeffentlichen `B_STABLE`-Kandidaten ausgeben.

### Echte Ein-Stufen-Unterschiede

Fuer jedes `g in 0..254` wird genau eine sichtbare Position

```text
p(g) = VISIBLE_POSITIONS[g mod 9]
```

in einer zweiten Byte-Block-Fixture von `g` auf `g+1` gesetzt. Beide
Vergleichsrichtungen werden gebunden. Damit entstehen `255 * 2 = 510`
Zellen. Jede muss `DIFFERENT_RECEPTOR_GRID_POINT` liefern, auch wenn die
bestehenden L1-Regeln den Gesamtvektor noch akzeptieren wuerden.

### Gemischte Linien

Fuer dieselben 255 benachbarten Paare werden an `p(g)` beide geordneten
Formationslinien `g -> g+1` und `g+1 -> g` gebunden. Die anderen 17
Koordinaten bleiben homogen. Alle `255 * 2 = 510` Zellen muessen vor einer
regulaeren Gleichheitsentscheidung als `MIXED_OR_UNBOUND_PROTOTYPE`
fail-closed enden.

Die Primaerdomain umfasst damit exakt `2812` vorregistrierte Zellen. Es gibt
keine nachtraegliche Auswahl anhand eines Ergebnisses.

## Gegenbaselines

Jede gueltig materialisierte Zelle erhaelt dieselben Quellen und dieselben
sichtbaren Positionen in vier getrennten read-only Armen:

1. rezeptorgittergebundene Kandidatenregel;
2. exakte binaere Floatgleichheit;
3. bestehende native normalisierte L1-Regel mit visueller Schwelle `0.01`;
4. bestehende funktionale L1-Regel mit `44/765`.

Die Baselines duerfen weder Kandidatenregel noch deren Zwischen- oder
Endbefund verwenden. Baselineabweichungen sind diagnostische Ergebnisse und
duerfen die vorab gebundenen Sollwerte nicht aendern.

Erwartete Reduktionsgrenze:

- exakte Floatgleichheit darf homogene Linien wegen Rundungsresten falsch
  trennen;
- beide bestehenden L1-Regeln duerfen eine einzelne echte Rezeptorstufe im
  18-Werte-Mittel falsch gleichsetzen;
- nur die gebundene Herkunftsregel muss gleichzeitig alle homogenen Linien
  erhalten, alle Ein-Stufen-Unterschiede trennen und gemischte Linien
  abweisen.

## Daten- und Digestrollen

Eine spaetere Materialisierung muss unveraenderliche Formen fuer mindestens
folgende Rollen binden:

```text
Uint8CoordinateSourceEvidence
PPBHomogeneousCoordinateLineage
VisibleGridEquivalenceInput
VisibleGridPositionFinding
VisibleGridApplicabilityFinding
VisibleGridEquivalenceLedger
VisibleGridEquivalenceReceipt
```

Der vorwaertsgerichtete Digestgraph lautet:

```text
Bildbytes + Frame + Rezeptorkonfiguration
-> ReceptorReceipt + uint8-Koordinatencode

geordnete ReceptorReceipts + PPB-Konfiguration
+ geordnete Formation-Receipts + Zustandsdigests
-> PPBHomogeneousCoordinateLineage

Probequelle + Kandidatenquelle + sichtbare Positionsbindung
-> VisibleGridEquivalenceInput
-> neun Positionsbefunde
-> Anwendbarkeitsbefund + Ledger
-> Receipt

unabhaengiger Sollplan + fertige Receipts
-> spaeterer reiner Auswertungsbefund
```

Kein Gittercode darf aus einem Prototypfloat, einem erwarteten Status oder
einem spaeteren Ergebnis rekonstruiert werden. Die Kandidaten- und
Baselinearme besitzen getrennte Owner und Receipts.

## Endliche Ressourcenbindung

Die prospektive Qualifikation ist auf folgende funktionalen Maxima begrenzt:

```text
Primaerzellen                         = 2812
Arme je Zelle                         = 4
Armurteile                            = 11248
sichtbare Positionen je Arm           = 9
maximale sichtbare Vergleiche         = 101232
maximale PPB-Updates je homogene Linie = 255
Speicher-, Lern- oder Feldaufrufe
  innerhalb der Gleichheitsauswertung = 0
```

Die spaetere Materialisierbarkeitspruefung muss Formation, Provenienz,
Validierung, Digests, Owner, Receipts und Fehlerpfade zusaetzlich exakt
zaehlen. Native Laufzeit und Prozessspeicher werden getrennt berichtet und
duerfen keine funktionale Budgetposition ersetzen.

## Erfolg, Falsifikation und methodische Ungueltigkeit

Der prospektive Funktionsvertrag ist nur bestaetigt, wenn gleichzeitig gilt:

- alle 1792 homogenen Zellen werden als gleicher Gitterpunkt erkannt;
- alle 510 Ein-Stufen-Zellen bleiben sichtbare Unterschiede;
- alle 510 gemischten Linien stoppen vor einem regulaeren Befund fail-closed;
- die Werte `0` und `255` sowie alle Wiederholungsgrenzen sind enthalten;
- Kandidaten- und Baselineeingaben sind identisch gebunden;
- alle Probe-, Prototyp- und Memory-Zustaende bleiben unveraendert;
- kein maskierter Wert wird gerundet oder veraendert.

Bei vollstaendig gueltiger Beweiskette ist die Regel falsifiziert, wenn auch
nur eine homogene Zelle getrennt, eine Ein-Stufen-Zelle gleichgesetzt oder
eine gemischte Linie regulaer klassifiziert wird.

`NOT_EVALUABLE` gilt bei fehlender oder widerspruechlicher uint8-Herkunft,
unvollstaendiger PPB-Kette, fremdem Slot oder Frame, Digestbruch,
Owner-Wiederverwendung, Teilbefund, Read-only-Verletzung oder
Ressourcenueberschreitung. Ein solcher Fall ist kein negativer
Funktionsbefund.

Der maximal zulaessige spaetere positive Status lautet:

`S2IX_UINT8_GRID_EQUIVALENCE_VALID_EXACT_AND_L1_BASELINES_BOUNDED`

Er bestaetigt nur eine numerisch belastbare Gleichheitspruefung fuer
quellgebundene `uint8`-Rezeptorwerte und homogene PPB-Linien. Er belegt keine
neue Wahrnehmungsschwelle, keine Memory-Mechanik und keine MCM-Feldwirkung.

## Freigabegrenze

S2-IX ist mit diesem Dokument statisch gebunden. Als naechster Schritt ist
ausschliesslich ein statischer Materialisierbarkeits-, Provenienz-,
Nichtzirkularitaets- und Budgetaudit zulaessig. Er muss insbesondere klaeren,
ob die vorhandenen Receipts jeden benoetigten Gittercode und jede homogene
PPB-Linie ohne neue Speicherabfrage belegen koennen.

Implementierung, Qualifikation und ein neuer Kontextstatuslauf benoetigen
jeweils eine gesonderte Freigabe.
