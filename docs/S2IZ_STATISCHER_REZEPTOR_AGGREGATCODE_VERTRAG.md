# S2-IZ: Statischer Rezeptor-Aggregatcode-Vertrag

## Status und Richtungsentscheidung

`STATIC_RECEPTOR_AGGREGATE_CODE_EQUIVALENCE_CONTRACT_BOUND`

S2-IZ ersetzt den geplanten 2812-Zellen-Ausfuehrungspfad durch eine
allgemeinere Integer-Invariante und eine kleine prospektive Qualifikation.
Der S2-IX-Vertrag bleibt unveraendert als blockkonstanter Spezialvertrag
dokumentiert, wird aber nicht implementiert.

S2-IV bleibt dauerhaft technisch gueltig und fachlich falsifiziert. S2-IZ
aendert keine historischen Belege, keine Rezeptorwerte, keine Memory-Kerne,
keine Schwelle und keinen bestehenden Kontextstatus.

Noch nicht freigegeben sind Implementierung, Tests, Zustandsaufrufe oder ein
neuer Kontextstatuslauf.

## Technische Invariante

Der gebundene visuelle Rezeptor verwendet fuer jede Block-/Kanalkomponente:

```text
sample_count = 40 * 40 = 1600
byte_sum     = Summe der 1600 uint8-Bytes
0 <= byte_sum <= 1600 * 255 = 408000
receptor_value = byte_sum / 408000
```

`byte_sum` wird mit ganzzahliger Arithmetik direkt aus dem validierten
Rohblock gebildet, bevor der fertige Floatwert fuer irgendeine
Gleichheitsentscheidung gelesen wird. Der Rezeptorfloat bleibt unveraendert
und dient nur als separat digestgebundener Funktionswert.

## `ReceptorAggregateCodeV1`

Ein unveraenderliches, prospektiv gebildetes Evidenzobjekt enthaelt exakt:

```text
schema
source_frame_digest
raw_block_digest
receptor_config_digest
geometry_digest
carrier_id
block_row
block_column
channel
sample_count                 exakt 1600
byte_sum                     ganzzahlig 0..408000
value_numerator              identisch byte_sum
value_denominator            exakt 408000
receptor_state_digest
receptor_receipt_digest
aggregate_code_digest
evidence_digest
```

Die beiden Digeste haben getrennte Rollen:

- `aggregate_code_digest` bindet ausschliesslich Schema der
  Gleichheitsrolle, Geometrie, `carrier_id`, Block-/Kanalrolle,
  `sample_count` und `byte_sum`;
- `evidence_digest` bindet zusaetzlich alle Quellen-, Rohblock-, Rezeptor- und
  Receiptfelder sowie den `aggregate_code_digest`.

Damit koennen zwei verschiedene Rohbloecke unterschiedliche
`evidence_digest`-Werte, aber denselben `aggregate_code_digest` besitzen.
Genau dann sind sie fuer diese Rezeptorschicht funktional gleich. Der
Quelldigest wird nicht aus der Provenienz entfernt; er beeinflusst nur nicht
die fachliche Gleichheit zweier nachweislich gleich aggregierter Quellen.

## Gleichheitsregel

Vor jedem Vergleich muessen Geometrie, `carrier_id`, Block-/Kanalrolle und
`sample_count` identisch und beide Evidenzen vollstaendig gueltig sein.
Andernfalls stoppt die Funktion fail-closed.

Bei gueltigen Rollen gilt ausschliesslich:

```text
probe.aggregate_code_digest == candidate.aggregate_code_digest
    -> SAME_RECEPTOR_AGGREGATE

probe.aggregate_code_digest != candidate.aggregate_code_digest
    -> DIFFERENT_RECEPTOR_AGGREGATE
```

Da alle nichtnumerischen Rollen vorgelagert identisch sein muessen, ist dies
aequivalent zu exakter Integergleichheit der beiden `byte_sum`-Werte.

Direkt benachbarte Summen bleiben verschieden:

```text
abs(probe.byte_sum - candidate.byte_sum) >= 1
    -> DIFFERENT_RECEPTOR_AGGREGATE
```

Es existiert keine Float-, Epsilon-, ULP- oder L1-Schwelle in dieser Regel.
Der Aggregatcode darf niemals durch `round`, Multiplikation oder sonstige
Rueckrechnung aus `receptor_value` beziehungsweise einem Prototypfloat
entstehen.

## Blockkonstanter Spezialfall

Fuer einen Block, dessen 1600 Bytes alle den Wert `k in 0..255` besitzen,
gilt exakt:

```text
byte_sum = 1600 * k
receptor_value = (1600 * k) / 408000 = k / 255
```

Damit ist jeder S2-IX-Gittercode eine spezielle S2-IZ-Summe. S2-IZ leitet
diese Beziehung von den Rohbytes ab und verwendet S2-IX weder als Quelle noch
als Auswertungsersatz.

## Nicht uniforme Bloecke

Nicht uniforme Rohbloecke sind zulaessig. Fuer jede Summe `S in 0..408000`
existiert eine kanonische Rohblockkonstruktion:

```text
q = S div 1600
r = S mod 1600

falls q < 255:
    r Bytes mit q+1
    1600-r Bytes mit q

falls q == 255:
    r = 0 und alle Bytes sind 255
```

Diese Konstruktion beweist ohne exhaustive Ausfuehrung, dass jeder
ganzzahlige Aggregatcode des Bereichs erreichbar ist.

Verschiedene Rohbloecke koennen dieselbe Summe besitzen. Fuer jedes
blockkonstante `k in 1..254` haben beispielsweise folgende Bloecke dieselbe
Summe `1600*k`:

```text
Block A: 1600 Bytes mit k
Block B: ein Byte k-1, ein Byte k+1, 1598 Bytes mit k
```

Ihre Rohblockdigests unterscheiden sich, ihr `aggregate_code_digest` ist
identisch. Diese Gleichsetzung ist keine Informationsvernichtung durch
S2-IZ: Der bestehende Rezeptor hat die Anordnung innerhalb derselben
Block-/Kanalkomponente bereits auf ihren Mittelwert reduziert.

## PPB-Kandidatenherkunft

Ein PPB-Kandidat darf fuer jede seiner 18 visuellen Koordinaten genau eine
prospektive `PPBAggregateLineageV1` besitzen. Sie bindet:

```text
schema, lineage_id, bank_id, slot_id, ppb_config_digest,
ordered_formation_receipt_digests,
ordered_source_aggregate_evidence_digests,
ordered_prestate_digests, ordered_poststate_digests,
support_sequence, final_support, stabilized,
final_prototype_digest,
homogeneous_aggregate_code_digest,
lineage_digest
```

Die Linie ist nur homogen, wenn alle geordneten Quellbelege derselben
Koordinate denselben `aggregate_code_digest` tragen. Unterschiedliche
`evidence_digest`-Werte sind zulaessig, weil unterschiedliche Frames denselben
Aggregatcode liefern koennen.

Erzeugung, Updates, Support, Slot und Vor-/Nachzustandskette muessen
lueckenlos zum finalen Kandidaten passen. Ein anderer Aggregatcode, fehlender
Schritt, vertauschte Reihenfolge, fremder Slot oder nur ein fertiger
Prototypfloat erzeugt `MIXED_OR_UNBOUND_AGGREGATE_LINEAGE` und stoppt vor
einem regulaeren Gleichheitsbefund fail-closed.

Die gespeicherten Prototypwerte werden weder quantisiert noch veraendert.
Maskierte Ergaenzungswerte bleiben exakt die bestehenden Kandidatenwerte.

## Daten-, Owner- und Digestgrenze

Eine spaetere private Implementierung darf ausschliesslich folgende Rollen
neu einfuehren:

```text
ReceptorAggregateCodeV1
PPBAggregateLineageV1
AggregateEquivalenceInputV1
AggregateEquivalenceOwnerV1
AggregatePositionFindingV1
AggregateApplicabilityFindingV1
AggregateEquivalenceLedgerV1
AggregateEquivalenceReceiptV1
AggregateEquivalenceErrorReceiptV1
```

Jeder Aufruf besitzt genau einen Einmal-Owner mit
`READY -> CONSUMED | FAILED`. Fehler veroeffentlichen keinen Teilbefund.

Der Digestgraph ist vorwaertsgerichtet:

```text
Rohframe + Geometrie + Block-/Kanalrolle
-> ReceptorAggregateCodeV1

geordnete AggregateCodes + geordnete PPB-Formationsbelege
-> PPBAggregateLineageV1

ProbeCode + direkter Kandidatencode oder PPB-Linie
-> AggregateEquivalenceInput + READY-Owner
-> Positionsbefunde
-> Anwendbarkeitsbefund + Ledger
-> Owner CONSUMED + Receipt

unabhaengiger Sollplan + fertiges Receipt
-> spaeterer reiner Auswertungsbefund
```

Kein erwarteter Befund, Baselinewert oder fertiger Float ist Elternquelle
eines Aggregatcodes oder einer PPB-Linie.

## Gegenbaselines

Die technische Qualifikation fuehrt auf denselben gueltigen Eingaben drei
diagnostische Gegenbaselines:

1. exakte binaere Floatgleichheit;
2. native visuelle L1-Regel mit `0.01`;
3. funktionale visuelle L1-Regel mit `44/765`.

Die Baselines erhalten keine Aggregatcodeentscheidung und besitzen getrennte
Owner. Ihre Ergebnisse aendern die Integer-Sollwerte nicht. Exakte
Floatgleichheit kann homogene PPB-Linien wegen Rechenresten trennen; beide
L1-Regeln koennen direkt benachbarte Summen gleichsetzen.

## Mathematische Vollstaendigkeit

Die gesamte Domaene wird durch Integerinvarianten abgedeckt, nicht durch eine
Zelle je Summe:

1. **Abgeschlossenheit:** Die Summe von 1600 Bytes aus `0..255` ist immer
   eine ganze Zahl in `0..408000`.
2. **Erreichbarkeit:** Die Quotient-/Rest-Konstruktion erzeugt jede ganze
   Zahl des Bereichs.
3. **Eindeutigkeit des Funktionswerts:** Bei festem Samplezaehler, Geometrie
   und Rolle bestimmt `byte_sum` den mathematischen Rezeptorwert eindeutig.
4. **Aequivalenzrelation:** Integergleichheit ist reflexiv, symmetrisch und
   transitiv.
5. **Nachbarschaftstrennung:** Fuer jedes `S in 0..407999` gilt
   `S != S+1`; der Abstand im Rezeptorwert ist exakt `1/408000`.
6. **PPB-Homogenitaet:** Eine endliche Linie ist genau dann homogen, wenn die
   Menge ihrer prospektiv gebundenen Aggregatcodedigests einelementig ist.

Diese Aussagen decken alle 408001 Codes und alle direkt benachbarten Paare
ohne 408001 einzelne Laufzellen ab.

## Vorregistrierte technische Qualifikation

Eine spaetere Qualifikation ist auf exakt 50 neutrale Faelle begrenzt.

### Q1: Arithmetik und Randwerte, 12 Faelle

```text
S = 0, 1, 1599, 1600, 1601,
    203199, 203200, 203201,
    204799, 204800, 407999, 408000
```

Jeder Fall prueft Rohbytesumme, Bereich, Nenner, Rolle, Code- und
Evidenzdigest sowie den unveraenderten Rezeptorwert.

### Q2: Verschiedene Rohbloecke mit gleicher Summe, 6 Faelle

```text
S = 1600, 3200, 203200, 204800, 404800, 406400
```

Je Fall werden ein blockkonstanter und ein positionsweise perturbierter
Rohblock gebunden. Rohblock- und Evidenzdigest muessen verschieden,
Aggregatcodedigest und Gleichheitsbefund muessen identisch sein.

### Q3: Direkt benachbarte Codes, 12 gerichtete Faelle

Beide Richtungen der sechs Paare:

```text
(0,1), (1599,1600), (1600,1601),
(203199,203200), (204799,204800), (407999,408000)
```

Jeder Fall muss `DIFFERENT_RECEPTOR_AGGREGATE` liefern.

### Q4: Homogene PPB-Linien, 12 Faelle

Alle Kombinationen aus:

```text
S = 0, 1, 1600, 203201, 407999, 408000
identische Updates = 2, 31
```

Jede Linie muss trotz moeglicher Floatreste denselben Aggregatcode behalten.
Niedriger Support erzeugt dadurch keinen oeffentlichen stabilen Kontext.

### Q5: Fail-Closed, 8 Faelle

```text
1. gemischte Linie 1600 -> 1601
2. gemischte Linie 1601 -> 1600
3. fehlender Formationsschritt
4. doppelter Formationsschritt
5. vertauschte Formationsreihenfolge
6. fremder Slot oder fremde PPB-Konfiguration
7. falsche Geometrie oder Block-/Kanalrolle
8. nur Floatwert ohne prospektive Quell- und Summenevidenz
```

Funktionale Negativfaelle besitzen konsistente Quellen- und Digests bis zur
gezielt mutierten Rolle. Andernfalls waere nur eine allgemeine
Digestablehnung geprueft.

## Verhaeltnismaessiges Budget

Die Qualifikation verwendet keinen eigenen Forschungsrunner und kein
ereignisweises append-only Journal. Zulaessig sind spaeter genau eine
vorregistrierte `unittest`-Suite, vollstaendige Standardausgabe, Exit-Code,
Quellhashes und ein kompaktes kanonisches Ergebnisobjekt.

Gebundene Obergrenzen:

```text
Qualifikationsfaelle                       = 50
Rohblock-/Quellmaterialisierungen          <= 286
Aggregatcodebildungen                      <= 286
PPB-Formationsschritte                     <= 214
Aggregatcodevergleiche                     <= 50
diagnostische Baselinevergleiche           <= 126
validierte PPB-Linienschritte              <= 230
gesamte logische Arbeitspositionen         <= 1192
unittest-Aufrufe                           = 1
kanonische Ergebnisdatei                   <= 2097152 Byte
Memory-, Lern- oder Feldaufrufe
  innerhalb der Gleichheitsfunktion        = 0
```

Die Obergrenzen sind wie folgt hergeleitet:

```text
Quellmaterialisierungen
  Q1 12 + Q2 12 + Q3 24 + Q4 (210 Formation + 12 Probe)
  + Q5 maximal 16                                      = 286

PPB-Formationen
  Q4: 6 Codes * ((1 CREATED + 2 UPDATE) +
                  (1 CREATED + 31 UPDATE))             = 210
  Q5: zwei echte gemischte Linien * 2 Schritte         =   4
                                                        -----
                                                          214

Baselinevergleiche
  42 regulaer auswertbare Faelle * 3 Baselines         = 126

Linienschrittvalidierungen
  210 gueltige Q4-Schritte + maximal 20 Q5-Schritte    = 230

Gesamt
  286 + 286 + 214 + 50 + 126 + 230                    = 1192
```

Die restlichen sechs Q5-Faelle verwenden gezielt synthetisch mutierte
Belegketten und duerfen keine zusaetzlichen PPB-Zustandsaufrufe ausloesen.

Die PPB-Schritte gehoeren nur zu den vorab gebundenen Qualifikationsfixtures;
die reine Gleichheitsfunktion selbst schreibt keinen Zustand. Ein technischer
Fehler macht die Qualifikation ungueltig. Es gibt keinen automatischen Retry.

## Erfolg, Falsifikation und Stopp

Die Aggregatregel ist nur qualifiziert, wenn gleichzeitig gilt:

- alle 12 Rand-/Innenwerte besitzen den exakt gebundenen Integercode;
- alle sechs unterschiedlichen Rohblockpaare mit gleicher Summe gelten als
  gleich;
- alle 12 gerichteten Nachbarfaelle bleiben verschieden;
- alle 12 homogenen PPB-Linien bleiben gleich;
- alle acht ungueltigen oder gemischten Faelle stoppen fail-closed;
- Baselineeingaben, Zustandsdigests und read-only Grenzen stimmen;
- kein Code wird aus einem Float zurueckgerechnet.

Bei gueltiger Beweiskette ist die Funktion falsifiziert, sobald gleiche
Summen getrennt, unterschiedliche Summen gleichgesetzt oder gemischte Linien
regulaer klassifiziert werden.

`NOT_EVALUABLE` gilt bei Quellen-, Geometrie-, Rollen-, Samplezahl-,
Owner-, Digest-, Reihenfolge-, Read-only- oder Budgetbruch. Ein solcher
Fehler ist kein negativer Memory-Befund.

Der maximal zulaessige spaetere positive Status lautet:

`S2IZ_RECEPTOR_AGGREGATE_EQUIVALENCE_VALID_INTEGER_INVARIANT_EXPLAINS`

Er bestaetigt nur eine robuste numerische Gleichheitsrolle fuer die bereits
bestehende Rezeptoraggregation. Er ist keine neue Wahrnehmungsschwelle, keine
Memory-Mechanik und keine MCM-spezifische Physik.

## Freigabegrenze

S2-IZ ist statisch gebunden. Als naechster Schritt ist ausschliesslich ein
enger statischer Materialisierbarkeits-, Datenform-, Nichtzirkularitaets- und
Budgetaudit der vorhandenen Rohframe-, Rezeptor- und PPB-Uebergangstypen
zulaessig.

Erst nach bestandenem Audit duerfen die private Aggregatcodeprojektion und
die reine Gleichheitsfunktion implementiert werden. Qualifikation und ein
neuer Kontextstatuslauf bleiben jeweils separat freizugeben.
