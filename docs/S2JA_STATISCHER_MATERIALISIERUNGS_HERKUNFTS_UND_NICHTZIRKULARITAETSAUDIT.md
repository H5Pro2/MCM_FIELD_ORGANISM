# S2-JA: Statischer Materialisierungs-, Herkunfts- und Nichtzirkularitaetsaudit

## Status

`PASS_S2JA_PROSPECTIVE_AGGREGATE_PROVENANCE_MATERIALIZABLE`

S2-IZ ist fuer eine private, prospektive Aggregatcode-Erzeugung und eine
reine Gleichheitspruefung materialisierbar. Der Befund gilt nur unter der in
diesem Audit festgelegten Quell- und Lebenszyklusgrenze.

Der bestehende `LocalChannelGridReceptor` erzeugt derzeit keinen expliziten
Integer-Aggregatcode. Er validiert ein `uint8`-Bild, bildet mit `mean` einen
Floatmittelwert und normalisiert anschliessend durch `255.0`. Historische
Rezeptor-, PPB- oder S2-IV-Belege enthalten die dafuer erforderlichen
Integer-Summen nicht. Sie duerfen nicht nachtraeglich rekonstruiert werden.

Materialisierbar ist ausschliesslich eine neue private Analysehuelle, die aus
demselben validierten und fuer den Aufruf unveraenderten Rohframe zuerst die
Integer-Summen bildet, danach den unveraenderten Rezeptor aufruft und beide
Ausgaben bindet. Dieser prospektive Weg aendert weder den Rezeptor noch einen
Memory-Kern.

Keine Implementierung, kein Import neuer Module, kein Test, kein Rezeptor-,
Memory- oder Feldaufruf wurde in S2-JA ausgefuehrt.

## Gepruefte Quellen

| Rolle | Datei | SHA-256 |
|---|---|---|
| S2-IZ-Vertrag | `docs/S2IZ_STATISCHER_REZEPTOR_AGGREGATCODE_VERTRAG.md` | `bdf5a7f48c3ff9023d595128275041186d6b36f86ba2ba5928b0551269efab1f` |
| S2-IZ-Maschinenvertrag | `reports/s2iz/s2iz-static-contract.json` | `653ef0b351d9712104762b86177ea28e25dc8b835342197161f5f874c4049971` |
| visueller Rezeptor | `mcm_field_organism/finite_video_path.py` | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| PPB-Profilbindung | `mcm_field_organism/_ppb1_receptor_profiles.py` | `28f3ce1de5b0ade465fffaa7dd3064eb51688cfea39ebb6c853cb4328bc0e5e0` |
| PPB-1-Kern | `mcm_field_organism/_ppb1_reference.py` | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| TSPM-1-Kern | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| atomarer Memory-Koordinator | `tools/_s2fs_b4_tspm1_private_coordinator.py` | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |
| aktuelles Forschungsprofil | `tools/_s2ig_private_runner.py` | `1408971e056b08c718e3704d211d63b72a788b578ff70fe2077819a16a3c3e07` |

Die aktive visuelle Profilbindung ist literal:

```text
VisualGridConfig(120, 80, 3, 2, 30.0)
PPB1ModalityParameters(4, 0.01, 0.05, 3, 64)
```

Damit entstehen `2 * 3 * 3 = 18` visuelle Tragerwerte. Jeder Tragerwert
aggregiert einen Block mit `40 * 40 = 1600` Bytes. Die visuelle PPB-Bank hat
genau vier Slots.

## Quellnahe Aggregatbildung

Die spaetere private Analysehuelle muss folgende Reihenfolge atomar binden:

```text
E0  exakter ndarray-Typ, uint8-Datentyp und Form (80,120,3) pruefen
E1  unveraenderliche private Frameansicht bilden und Rohframedigest bilden
E2  Frame als (2,40,3,40,3) strukturieren
E3  je Block/Kanal np.sum(..., dtype=uint64) bilden
E4  18 ReceptorAggregateCodeV1-Belege bilden
E5  unveraenderten LocalChannelGridReceptor auf demselben Frame aufrufen
E6  Rollenfolge, Geometrie, Trager und 18 Rezeptorwerte abnehmen
E7  jeden Floatfunktionswert gegen byte_sum / 1600 / 255 abgleichen
E8  Frame-Nachhash pruefen und nur Digests, Rollen und Summen veroeffentlichen
```

E3 liegt vor jeder Floatnormalisierung und vor jeder Gleichheitsentscheidung.
Der Aggregatcode stammt deshalb direkt aus den validierten Quellbytes. E7
bindet nur den unveraenderten bestehenden Funktionswert an diese Quelle; E7
ist keine Quelle des Integercodes.

Der Frame darf waehrend E0 bis E8 nur in-memory vorliegen. Weder ein
Memory-Zustand noch ein Receipt enthaelt Rohbytes, Pixelarrays, Rohbloecke
oder eine Replaykopie.

## Integerinvariante

Fuer jede der 18 Koordinaten gilt:

```text
sample_count = 1600
0 <= byte_sum <= 1600 * 255 = 408000
receptor_value = byte_sum / 408000
```

Die Integeraddition mit `uint64` ist fuer das Maximum `408000` ohne
Ueberlauf materialisierbar. Der spaetere Codevergleich verwendet nur den
prospektiv gebildeten Integercode, niemals einen zurueckgerechneten Float.

Fuer blockkonstante Bloecke gilt vollstaendig:

```text
k in 0..255 -> byte_sum = 1600 * k
```

Die Abbildung ist injektiv und deckt einschliesslich `k=0` und `k=255` alle
256 blockkonstanten Spezialwerte ab.

## Gleiche Summe bei verschiedenen Rohquellen

Zwei unterschiedliche Rohbloecke duerfen unterschiedliche
`raw_block_digest`- und `evidence_digest`-Werte besitzen, aber denselben
`aggregate_code_digest`, wenn Geometrie, Block-/Kanalrolle, Samplezahl und
Bytesumme gleich sind.

Fuer `k in 1..254` sind beispielsweise materialisierbar:

```text
A: 1600-mal k
B: einmal k-1, einmal k+1, 1598-mal k
```

Beide Summen sind `1600*k`, die Rohbytes und Rohhashes sind verschieden.
Diese Gleichsetzung verliert auf der vorhandenen Rezeptorschicht keine
Information: Der bestehende Rezeptor gibt fuer beide nur denselben lokalen
Kanalmittelwert aus.

## Nachbartrennung

Direkt benachbarte Aggregatcodes bleiben fuer jede zulaessige Summe
verschieden. Die Qualifikation bindet insbesondere beide Richtungen von:

```text
0 / 1
1599 / 1600
1600 / 1601
203199 / 203200
204799 / 204800
407999 / 408000
```

Die Grenzpaare `0/1` und `407999/408000` sind erreichbar. Keine
Floattoleranz, L1-Schwelle oder ULP-Regel darf diese Integerentscheidung
ersetzen.

## Prospektive PPB-Herkunft

Die fuer eine PPB-Formation benoetigte Herkunft liegt am privaten
Uebergang gleichzeitig vor:

- validiertes `ReceptorAggregateCodeV1` je visueller Koordinate;
- der unveraenderte `ReceptorContactFrame` als PPB-Eingang;
- validierter PPB-Vorzustand;
- `PPB1StepResult` mit Readout und Nachzustand;
- ausgewaehlter Slot, Event, Support, Stabilitaet und Vor-/Nachzustandsdigest.

Die Linie wird in dieser Reihenfolge gebunden:

```text
Quellframe
-> 18 AggregateCodes
-> PPB-Eingabedigest
-> PPB-Vorzustand
-> PPB-Readout und PPB-Nachzustand
-> PPBAggregateLineageV1
```

`CREATED` und `REPLACED` beginnen fuer den ausgewaehlten Slot eine neue
Linie. `MATCHED` darf eine homogene Linie nur fortsetzen, wenn alle 18
Quellcodes mit den 18 gebundenen Slotcodes uebereinstimmen. Andernfalls wird
die Linie `MIXED_OR_UNBOUND_AGGREGATE_LINEAGE`; sie darf keinen regulaeren
Gleichheits- oder Anwendbarkeitsbefund erzeugen.

Die Supportfolge muss exakt mit dem PPB-Readout uebereinstimmen. Fuer das
aktive Profil gilt:

```text
CREATED: Support 1
erstes MATCHED: Support 2
zweites MATCHED: Support 3, stabil
weitere MATCHED: Support bleibt 3
```

Ein fehlender, doppelter, vertauschter, fremder oder nach dem Kind gebildeter
Formationsbeleg wird vor der Gleichheitsentscheidung abgewiesen.

## Keine dritte Memory-Schicht

`PPBAggregateLineageV1` ist ein prospektiver Herkunfts- und
Qualifikationsbeleg, kein zusaetzlicher Kontextspeicher. Fuer eine spaetere
private Laufzeitintegration gelten zwingend folgende Grenzen:

- hoechstens ein Provenienzsatz je vorhandenem visuellen PPB-Slot;
- exakt dieselbe Slotmenge und Kapazitaet wie die PPB-Bank, hier vier;
- `CREATED`, `MATCHED`, `REPLACED` und Freigabe folgen atomar dem PPB-Slot;
- keine eigene Kandidatensuche, Distanz, Rangfolge oder Abrufentscheidung;
- keine Rezeptorwerte, Prototypwerte oder Rohbytes im Provenienzsatz;
- nur 18 Aggregatecode-Digests, Status, Zaehler und Digestverkettung;
- kein Fortbestand nach PPB-Ersetzung oder Freigabe;
- keine Ausgabe als `A_RECENT`, `B_STABLE` oder dritte Kontextrolle.

Die geordneten Vollketten des S2-IZ-Vertrags werden nur in den endlichen
Qualifikationsfixtures beziehungsweise deren Testbelegen materialisiert. Ein
Produktionsjournal oder eine unbeschraenkt wachsende Ereignishistorie ist
nicht freigegeben. Fuer eine spaetere allgemeine Integration waere ein
eigener Vertrag fuer einen kapazitaetsgleichen rollenden Herkunftskopf
erforderlich.

## Datenformen

### `ReceptorAggregateCodeV1`

Die Felder aus S2-IZ sind vollstaendig aus Quellframe, `VisualGridConfig`,
Rezeptorzustand und Quellreceipt ableitbar. `aggregate_code_digest` schliesst
Quell- und Rohhash bewusst aus; `evidence_digest` schliesst sie ein.

Kanonisches ASCII-JSON mit maximalen gebundenen IDs belegt `926` Bytes. Die
verbindliche Huelle ist `1152` Bytes.

### `PPBAggregateLineageV1`

Die Form bindet zusaetzlich zur S2-IZ-Liste die einzelne
`coordinate_role`. Die laengste Qualifikationslinie besitzt 32 Formationen
(eine Erzeugung und 31 Updates). Ihre kanonische Vollform belegt maximal
`9620` Bytes; die Huelle ist `11264` Bytes.

Diese Vollform ist nur Qualifikationsevidenz. Der Memory-Zustand speichert
sie nicht.

### Gleichheitsformen

| Form | berechnetes Maximum | gebundene Huelle |
|---|---:|---:|
| `AggregateEquivalenceOwnerV1` | 599 | 768 |
| `AggregateEquivalenceInputV1` | 3049 | 3584 |
| `AggregatePositionFindingV1` | 611 | 768 |
| `AggregateApplicabilityFindingV1` | 1520 | 1792 |
| `AggregateEquivalenceLedgerV1` | 280 | 512 |
| `AggregateEquivalenceReceiptV1` | 575 | 768 |
| `AggregateEquivalenceErrorReceiptV1` | 535 | 768 |

Alle Formen sind unveraenderlich und canonical-JSON-digestgebunden. IDs
verwenden die vorhandene technische Form; Digests sind lowercase SHA-256.
Der Owner besitzt genau den Verlauf `READY -> CONSUMED | FAILED`. Ein Fehler
erzeugt keine Teilbefunde.

## Digestgraph und Nichtzirkularitaet

Der vollstaendige Graph ist vorwaertsgerichtet:

```text
Quellbytes + Konfiguration + Rollen
-> Rohframe-/Rohblockdigests
-> AggregateCodes
-> unveraenderter Rezeptorzustand + Rezeptorreceipt
-> PPB-Eingabe + PPB-Vorzustand
-> PPB-Readout + PPB-Nachzustand
-> PPB-Aggregatlinie
-> Gleichheitseingang + READY-Owner
-> Positionsbefunde
-> Anwendbarkeitsbefund + Ledger
-> CONSUMED-Owner + Receipt

unabhaengiger Sollplan + fertiges Receipt
-> reine Qualifikationsauswertung
```

Kein Kinddigest ist Bestandteil eines Elternobjekts. Der
`aggregate_code_digest` enthaelt weder `receptor_value` noch
`prototype_values`. Der Linienbeleg entsteht erst nach dem PPB-Ergebnis,
liefert aber keine Daten zurueck in den PPB-Aufruf. Sollwerte und Baselines
sind keine Eltern des Ausfuehrungspfads.

Historische S2-IV-Belege besitzen weder die Integercodes noch die geordneten
PPB-Ketten. S2-IV bleibt deshalb unveraendert falsifiziert und darf mit
S2-JA nicht neu ausgewertet werden.

## Fail-Closed-Matrix

Folgende Abweichungen stoppen vor einem regulaeren Befund:

1. kein exakter `uint8`-Frame oder falsche Geometrie;
2. fehlende oder ausserhalb `0..408000` liegende Summe;
3. Summe aus Float oder Prototyp zurueckgerechnet;
4. Block-, Kanal-, Trager- oder Samplezahl vertauscht;
5. Quellframe-, Rohblock-, Rezeptor- oder Konfigurationsdigest fremd;
6. PPB-Slot, Konfiguration, Vor- oder Nachzustand fremd;
7. Formationsschritt fehlt, ist doppelt oder nicht geordnet;
8. Linie enthaelt mehr als einen Aggregatcode einer Koordinate;
9. Support-, Stabilitaets- oder Kandidatenbezug widerspricht PPB-1;
10. Owner fremd, bereits verbraucht oder nicht atomar terminal;
11. Ledger- oder Artefaktgrenze ueberschritten;
12. Rohbytes oder eine Replaykopie in Memory-Zustand oder Receipt enthalten.

Gemischte Linien bleiben als technischer Ablehnungsbefund sichtbar, werden
aber nie als `SAME` oder `DIFFERENT` umgedeutet.

## Materialisierung der 50 Faelle

Die Registry ist lueckenlos und verwendet neutrale IDs
`s2ja-case-001` bis `s2ja-case-050`:

| IDs | Gruppe | Anzahl |
|---|---|---:|
| 001..012 | Q1 Arithmetik und Grenzen | 12 |
| 013..018 | Q2 verschiedene Rohbloecke, gleiche Summe | 6 |
| 019..030 | Q3 gerichtete Nachbarcodes | 12 |
| 031..042 | Q4 homogene PPB-Linien | 12 |
| 043..050 | Q5 isolierte Fail-Closed-Mutationen | 8 |

Q1, Q2 und Q3 sind aus den Quotient-/Rest- beziehungsweise
Perturbationskonstruktionen vollstaendig erzeugbar. Q4 bindet fuer jede der
sechs Summen genau die Updatezahlen 2 und 31. Q5 mutiert jeweils nur die
vorregistrierte Rolle; alle vorgelagerten Digests werden konsistent gebildet.

Es gibt keine doppelte ID und keine dynamisch erzeugte Zusatzzeile.

## Operations- und Ergebnisbudget

Die S2-IZ-Herleitung ist vollstaendig materialisierbar:

```text
Quellmaterialisierungen              <= 286
Aggregatcodebildungen                 <= 286
PPB-Formationsschritte                <= 214
Aggregatcodevergleiche                <=  50
diagnostische Baselinevergleiche      <= 126
validierte PPB-Linienschritte         <= 230
                                      ------
logische Arbeitspositionen            <=1192
```

Die 18 Koordinatenvalidierungen sind jeweils gebundene Teilpositionen ihrer
Code-, Linien- oder Vergleichsoperation und werden nicht als weitere
Memory- oder Rezeptoraufrufe gezaehlt.

Die spaetere kompakte Ergebnisdatei bleibt unter `2097152` Bytes:

```text
Manifest und Registry                  32768
50 Fallbelege * 16384                  819200
286 Codebelege * 1152                  329472
20 maximale Vollketten * 11264         225280
126 Baselinebelege * 512                64512
Hashes, Ledger, Ausgabe und Terminal   131072
                                      -------
Maximum                               1602304
Reserve                                494848
```

Die 20 Vollketten sind die zwoelf Q4-Linien plus hoechstens acht isolierte
Q5-Mutationsketten. Interne In-Memory-Objekte werden nicht zusaetzlich in
Receipts eingebettet.

## Auditentscheidung

Alle geforderten Quellenwerte sind am prospektiven Analyse- und
Formationuebergang vorhanden. Die 50 Faelle, 1192 Arbeitspositionen,
Ownerrollen, Digests und Artefaktgrenzen sind endlich und eindeutig
materialisierbar. Der Digestgraph ist azyklisch.

Der Audit besteht mit folgenden bindenden Grenzen:

- Aggregatcodes entstehen nur prospektiv aus validierten Rohbytes;
- historische Belege werden nicht rekonstruiert;
- der bestehende Rezeptor und alle Memory-Kerne bleiben unveraendert;
- PPB-Herkunft ist reine, slot- und kapazitaetsgebundene Provenienz;
- keine Rohbytes und keine eigenstaendige Kandidaten- oder Kontextschicht;
- die erste Implementierung bleibt auf private Erzeugung, Belegbindung und
  reine Gleichheit begrenzt;
- Tests, Qualifikation und Kontextstatuslauf brauchen separate Freigaben.

S2-JA autorisiert damit als naechsten Schritt ausschliesslich die private
Aggregatcode-Erzeugung, die prospektive PPB-Linienbindung fuer die endliche
Qualifikation und die reine Aggregatgleichheitsfunktion. S2-IV bleibt
unveraendert falsifiziert.
