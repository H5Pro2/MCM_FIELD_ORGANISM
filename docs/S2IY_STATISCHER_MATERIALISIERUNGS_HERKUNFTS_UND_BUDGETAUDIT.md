# S2-IY: Statischer Materialisierungs-, Herkunfts- und Budgetaudit

## Status

`PASS_S2IY_PROSPECTIVE_UNIFORM_UINT8_BLOCK_GRID_MATERIALIZABLE`

S2-IY prueft den S2-IX-Vertrag ausschliesslich statisch. Es wurden keine
Module importiert, keine Rezeptor-, PPB-, Memory- oder Signalfunktion
aufgerufen und keine Tests ausgefuehrt. S2-IV bleibt unveraendert technisch
gueltig und fachlich falsifiziert.

Der Audit besteht fuer die vorregistrierte blockkonstante S2-IX-Domaene. Er
erteilt keinen Herkunftsclaim fuer beliebige `uint8`-Bilder.

## Reale Rezeptorgeometrie

Der bestehende `LocalChannelGridReceptor` mit der gebundenen Konfiguration

```text
source = 120 x 80 x 3
grid   = 3 x 2 x 3
block  = 40 x 40 Pixel je Kanal
```

berechnet pro Rezeptorkoordinate den Mittelwert von 1600 `uint8`-Bytes und
teilt anschliessend durch 255. Seine allgemeine kleinste Summenstufe ist
daher `1 / (1600 * 255) = 1/408000`, nicht `1/255`.

Die S2-IX-Fixtures sind enger: Jede der 18 Block-/Kanalkomponenten besteht
vollstaendig aus demselben Byte `g`. Nur fuer diese nachweislich
blockkonstante Unterdomaene ist der Rezeptorwert exakt dem Quellcode `g`
zugeordnet. Eine volle Aenderung `g -> g+1` aendert alle 1600 Bytes der
betroffenen Block-/Kanalkomponente und erzeugt den gebundenen Abstand
`1/255`.

Damit gilt prospektiv:

```text
block_min == block_max == g  -> UNIFORM_UINT8_BLOCK_GRID_BOUND
block_min != block_max       -> NON_UNIFORM_RECEPTOR_SOURCE, fail-closed
```

Der Gittercode wird aus den vor der Rezeptoranalyse gebundenen Blockbytes
uebernommen. Er wird niemals aus `channel_values` oder einem Prototypfloat
berechnet.

## Vorhandene Quellpunkte

Die fuer eine prospektive Projektion benoetigten Daten existieren an zwei
privaten Uebergangspunkten:

1. `ByteBlockVisualFixture` bindet 18 `uint8`-Blockwerte, den vollstaendig
   expandierten Rohbilddigest und eine deterministische Bildmaterialisierung.
2. Am PPB-/TSPM-Formationuebergang liegen validierter Vorzustand, gebundener
   Eingabeframe, native Konfiguration, Ergebnisreceipt und vollstaendiger
   Nachzustand gleichzeitig vor. Die visuelle PPB-Zustandsdifferenz bindet
   den tatsaechlich erzeugten, aktualisierten oder ersetzten Slot.

Die bestehenden kompakten S2-IG-Receipts reichen rueckwirkend nicht aus:

- `compact-receptor-receipt` enthaelt Rohbild- und Wertedigests, aber keine
  18 Blockcodes oder Blockkonstanzbelege;
- `compact-formation-receipt` enthaelt Zustands- und Ergebnisdigests, aber
  keine geordnete positionsweise PPB-Herkunftslinie.

Historische Gittercodes duerfen deshalb nicht aus diesen Digests oder aus
fertigen Floats rekonstruiert werden. Materialisierbar ist ausschliesslich
eine neue private, prospektive Aufzeichnungsprojektion an den genannten
Uebergangspunkten. Sie veraendert weder Rezeptor noch PPB/TSPM-Zustand.

## Vollstaendige Registry

Die 2812 Zellen werden in einer kanonischen Reihenfolge auf neutrale IDs
`s2ix-cell-0001` bis `s2ix-cell-2812` abgebildet:

| Ordinalbereich | Schluesselraum | Anzahl |
| --- | --- | ---: |
| 1..1792 | `g=0..255`, `r=(0,1,2,3,8,31,255)` in dieser Reihenfolge | 1792 |
| 1793..2302 | `g=0..254`, Richtung vorwaerts/rueckwaerts | 510 |
| 2303..2812 | `g=0..254`, gemischte Linie vorwaerts/rueckwaerts | 510 |

Die drei Ordinalbereiche sind disjunkt. Innerhalb jedes Bereichs ist die
Abbildung aus Schluesseltupel und Ordinalzahl bijektiv. Damit existieren
exakt 2812 eindeutige Zellen ohne Duplikat oder Luecke.

Die Ausfuehrungsregistry enthaelt keine Sollentscheidung. Eine getrennte,
vorab versiegelte Evaluationsregistry bindet erst nach neutraler Zell-ID den
erwarteten Funktions- oder Fail-Closed-Befund.

Es werden exakt 511 Quellfixtures benoetigt:

- 256 blockkonstante Basisfixtures fuer `g=0..255`;
- 255 Ein-Stufen-Fixtures, in denen nur `p(g) =
  VISIBLE_POSITIONS[g mod 9]` von `g` auf `g+1` geaendert ist.

Vorwaerts-/Rueckwaerts- und gemischte Zellen referenzieren diese unveraendert
gebundenen Quellen; sie erzeugen keine inhaltlich duplizierten Fixtures.

Fuer jedes `g=0..254` liefert die geaenderte Blockkomponente rechnerisch
exakt `(g+1)/255` statt `g/255`; der Abstand ist damit immer genau `1/255`.
Der 18-Werte-L1-Mittelwert betraegt `1/4590` und liegt unter `0.01`. Die
gemischten Linien erreichen deshalb bei unveraendertem PPB-Matching
tatsaechlich denselben Slot und pruefen eine reale gemischte Herkunft statt
eines vorzeitig getrennten Kandidaten. `g=0`, `g=255` und das Randpaar
`254 -> 255` sind durch die kanonischen Bereiche zwingend enthalten.

## Prospektive Herkunftsformen

### `Uint8FrameGridEvidenceV1`

Die Form bindet exakt:

```text
schema, source_id, fixture_id, frame_index, window,
raw_image_digest, frame_digest, receptor_config_digest,
receptor_state_digest, receptor_receipt_digest,
grid_codes[18], normalized_values_digest,
owner_prestate_digest, evidence_digest
```

Vor Bildung des Evidence-Digests wird fuer jede Block-/Kanalkomponente der
Rohbytes `min == max == grid_code` geprueft. Danach wird unabhaengig
validiert, dass der Rezeptorwert dem aus den Quellbytes vorgegebenen
`grid_code/255` entspricht. Die Pruefrichtung ist immer Quelle zu Rezeptor,
nie Float zu Gittercode.

### `PPBFormationLineageStepV1`

Jeder tatsaechliche PPB-Erzeugungs- oder Aktualisierungsschritt bindet:

```text
schema, lineage_id, step_ordinal, event,
source_grid_evidence_digest, previous_lineage_step_digest,
ppb_config_digest, bank_id, slot_id,
ppb_input_frame_digest, ppb_result_digest, ppb_receipt_digest,
ppb_readout_digest, ppb_prestate_digest, ppb_poststate_digest,
prototype_digest, support_before, support_after, stabilized_after,
owner_prestate_digest, step_digest
```

Der erste Schritt muss `CREATED` sein und besitzt keinen vorherigen
Liniendigest. Jeder weitere Schritt muss `MATCHED` sein, denselben Bank-/Slot-
und Konfigurationsbezug tragen und unmittelbar an den vorigen Nachzustand
anschliessen. `REPLACED`, Slotwechsel oder eine fremde Quelle beendet die
vorige Linie; sie darf nicht fortgesetzt werden.

### `PPBHomogeneousLineageSummaryV1`

Die Summary bindet ausschliesslich bereits vollstaendig aufgezeichnete
Schritte:

```text
schema, lineage_id, bank_id, slot_id, ppb_config_digest,
step_count, first_step_digest, head_step_digest,
ordered_step_set_digest, homogeneous_grid_codes[18],
final_prototype_digest, support, stabilized,
owner_prestate_digest, summary_digest
```

`homogeneous_grid_codes` entsteht positionsweise aus den Quellcodes der
geordneten Frame-Evidenzen. Mehr als ein Code an einer Koordinate,
unvollstaendige Ordinale, falscher Supportverlauf oder nicht eindeutige
Slotrelation erzeugt keine Summary.

Niedrige Supports duerfen in der numerischen Qualifikation vorkommen, werden
aber nicht als oeffentlicher `B_STABLE`-Kontext ausgegeben.

### Gleichheits-, Owner-, Ledger- und Receiptformen

Prospektiv sind ausserdem exakt folgende unveraenderliche Rollen gebunden:

```text
VisibleGridEquivalenceOwnerV1
VisibleGridEquivalenceInputV1
VisibleGridPositionSetFindingV1
VisibleGridApplicabilityFindingV1
VisibleGridEquivalenceLedgerV1
VisibleGridEquivalenceReceiptV1
VisibleGridEquivalenceErrorReceiptV1
```

Jeder der vier Arme besitzt einen eigenen atomaren Einmal-Owner. Der
zulaessige Uebergang ist `READY -> CONSUMED` oder `READY -> FAILED`.
Wiederverwendung, Teilbefund oder ein gemeinsamer Owner zwischen Kandidaten-
und Baselinearmen ist unzulaessig.

## Ketten- und Kandidatenvalidierung

Eine Linie ist nur gueltig, wenn alle folgenden Relationen gemeinsam gelten:

- Ordinale sind lueckenlos `1..L`;
- jeder Schritt referenziert genau eine vorher gebildete Frame-Evidenz;
- Bank, Slot und Konfiguration bleiben bis zum Linienende identisch;
- der PPB-Vorzustand jedes Folgeschritts entspricht dem Nachzustand des
  vorigen Schritts;
- Support beginnt bei 1, steigt bei `MATCHED` bis zur nativen Saettigung und
  stimmt mit dem ausgewaehlten Nachzustandsslot ueberein;
- Readout-, Receipt-, Ergebnis- und Nachzustandsdigests beziehen sich auf
  denselben Kandidatenslot;
- der finale Prototypdigest stammt aus genau diesem Slot;
- jeder verwendete Gittercode stammt aus der jeweiligen vorgelagerten
  `Uint8FrameGridEvidenceV1`.

Gemischte, lueckenhafte, vertauschte, fremde oder nach dem Kind erzeugte
Schritte werden vor jeder Gleichheitsausgabe fail-closed verworfen. Ein
passender Endfloat, ULP-Abstand oder L1-Wert kann keinen Kettenbruch heilen.

## Baselinegleichheit

Jede Zelle bindet genau dieselbe Probe, denselben finalen Kandidaten und
dieselben Zustandsdigests an vier getrennte Arme:

1. `UINT8_GRID_EQUIVALENCE`;
2. `EXACT_FLOAT_EQUALITY`;
3. `NATIVE_VISUAL_L1_0_01`;
4. `FUNCTIONAL_VISUAL_L1_44_OVER_765`.

Nur Funktionsrolle, Owner und Algorithmus unterscheiden sich. Kein Arm darf
das Ergebnis eines anderen lesen. Die beiden L1-Arme verwenden weiterhin
den vollstaendigen 18-Werte-Vektor; die Gitter- und Exaktarme vergleichen die
neun gebundenen sichtbaren Positionen.

## Operationsbudget

Die homogenen Checkpoints werden aus genau einer 256-Schritt-PPB-Linie je
Gittercode gewonnen. Dadurch werden keine Formationen fuer jeden Checkpoint
dupliziert.

```text
homogene PPB-Schritte       = 256 Codes * (1 CREATED + 255 MATCHED)
                            = 65536
gemischte PPB-Schritte      = 510 Linien * 2
                            = 1020
PPB-Formationsoperationen   = 66556

Formation-Rezeptoranalysen  = 66556
eine Probenanalyse je Zelle = 2812
Rezeptoroperationen gesamt  = 69368

Zelloperationen             = 2812 * 12 = 33744
feste Laufhuellenoperationen = 7

Erfolgs-/Qualifikationsmaximum = 169675 Operationen
START-/RESULT-Ereignisse       = 339350
```

Die zwoelf Zelloperationen sind literal:

```text
C01 Zellplan und Quellen binden
C02 Probe-Evidenz validieren
C03 Kandidatenlinie/Summary validieren
C04 Gitterarm und Owner binden
C05 Gitterarm atomar auswerten
C06 Exaktarm und Owner binden
C07 Exaktarm atomar auswerten
C08 native L1 und Owner binden
C09 native L1 atomar auswerten
C10 funktionale L1 und Owner binden
C11 funktionale L1 atomar auswerten
C12 Ledger, getrennte Receipts und Zellabschluss binden
```

Die sieben Huellenoperationen sind `RUN_PREPARE`, `SOURCE_MANIFEST`,
`EXECUTION_SEAL`, `EVALUATION_BIND`, `AGGREGATE`, `TERMINAL` und `COMPLETE`.
Ein Fehlerpfad endet exklusiv in `NOT_EVALUABLE`; erwartete Fail-Closed-
Mutationen werden erst durch den getrennten Auswerter als bestaetigte
Negativzelle gewertet.

Das Zellledger bindet fuer eine Linie mit `L` Schritten mindestens:

```text
frame_evidence_count              = L + 1
lineage_step_validation_count     = L
coordinate_source_validation_count = 18 * (L + 1), maximal 4626
grid_visible_compare_count        = 9
exact_visible_compare_count       = 9
native_l1_term_count              = 18
functional_l1_term_count          = 18
comparison_term_count             = 54
arm_owner_count                   = 4
storage_learning_or_field_calls_in_evaluator = 0
```

## Kanonische Artefaktgroessen

Die statische ASCII-Serialisierung mit maximal 96 Zeichen langen IDs,
64-stelligen Digests, maximalem Schritt 256 und Zeilenabschluss ergibt:

| Form | berechnete Bytes | verbindliches Maximum |
| --- | ---: | ---: |
| `S2IXFixtureRegistryRowV1` | 540 | 768 |
| `S2IXExecutionRegistryRowV1` | 1267 | 1536 |
| `S2IXEvaluationRegistryRowV1` | 487 | 768 |
| `Uint8FrameGridEvidenceV1` | 1118 | 1280 |
| `PPBFormationLineageStepV1` | 1550 | 1792 |
| `PPBHomogeneousLineageSummaryV1` | 1149 | 1280 |
| `VisibleGridEquivalenceOwnerV1` | 667 | 768 |
| `VisibleGridEquivalenceInputV1` | 962 | 1152 |
| `VisibleGridPositionSetFindingV1` | 1148 | 1280 |
| `VisibleGridApplicabilityFindingV1` | 902 | 1024 |
| `VisibleGridEquivalenceLedgerV1` | 527 | 768 |
| `VisibleGridEquivalenceReceiptV1` | 1286 | 1536 |
| `VisibleGridEquivalenceErrorReceiptV1` | 702 | 896 |

Keine Form erreicht 2048 Byte. Vollstaendige Frames, PPB-Zustaende oder
Prototypobjekte werden nicht in Receipts dupliziert; sie bleiben ueber
typisierte Digests und die append-only Elternbelege offline pruefbar.

Das vollstaendige konservative Artefaktbudget lautet:

```text
511 Fixturezeilen * 768                         =     392448
2812 Ausfuehrungszeilen * 1536                  =    4319232
2812 Evaluationszeilen * 768                    =    2159616
69368 Frame-Evidenzen * 1280                    =   88791040
66556 Linienschritte * 1792                     =  119268352
2302 Linien-Summaries * 1280                    =    2946560
11248 Owner * 768                               =    8638464
11248 Inputs * 1152                             =   12957696
11248 Positionsbefunde * 1280                   =   14397440
11248 Anwendbarkeitsbefunde * 1024              =   11517952
11248 Ledger * 768                              =    8638464
11248 Erfolgs-/Fehlerreceipts * 1536            =   17276928
Manifest, Indizes und Terminalformen             =      65536
Gesamtmaximum                                    =  291369728 Byte
```

Das Maximum zaehlt pro Arm den groesseren Erfolgs- oder Fehlerbeleg, nicht
beide gegenseitig ausgeschlossenen Formen. Eine unabhaengige read-only
Verifikation ist ein separater Aufruf und muss alle 339350 Ereignisse und
169675 Operationsreceipts pruefen.

## Digestgraph und Nichtzirkularitaet

```text
Fixturebytes + Rezeptorkonfiguration
-> Uint8FrameGridEvidence

FrameEvidence + PPB-Vorzustand + native Formation
-> PPBFormationLineageStep
-> naechster LineageStep
-> PPBHomogeneousLineageSummary

ProbeEvidence + KandidatenEvidence + neutraler Zellplan
-> vier getrennte ArmInputs + vier READY-Owner
-> vier getrennte Befunde/Ledger
-> vier terminale Owner/Receipts

vollstaendige Ausfuehrungsevidenz + unabhaengige Evaluationsregistry
-> Zell- und Aggregatbefund
```

Evaluationserwartungen, Endfloats und Baselinebefunde sind keine Eltern von
Quell-, Linien- oder Kandidatenevidenz. Kein Digest bindet sich selbst oder
einen spaeteren Beleg.

## Auditentscheidung

Die S2-IX-Regel ist prospektiv materialisierbar, weil die benoetigten
Quellbytes und Zustandsrelationen vor beziehungsweise waehrend der Formation
vorhanden sind. Sie ist nicht aus den bestehenden historischen
Kompaktbelegen nachtraeglich materialisierbar.

Der bestandene Audit gilt deshalb nur unter folgenden harten Grenzen:

- ausschliesslich blockkonstante `uint8`-Quellen mit explizitem
  `UNIFORM_UINT8_BLOCK_GRID_BOUND`;
- prospektive Evidenzbildung vor Informationsverlust;
- keine Herleitung aus Rezeptor- oder Prototypfloats;
- kein regulaerer Befund fuer nicht uniforme Quellen oder gemischte Linien;
- keine Aenderung an Rezeptor, PPB/TSPM, Kontextsignal oder L1-Regeln.

Als naechster Schritt darf eine private reine Gitteraequivalenzfunktion samt
den hier gebundenen privaten Evidenztypen implementiert werden. Tests,
Qualifikation und Kontextstatuslauf benoetigen weiterhin gesonderte
Freigaben. Der vorhandene S2-IC-Signalgeber bleibt bis zu einer unabhaengig
bestandenen Qualifikation unveraendert.
