# S1-QV: Statischer M2-Kapazitaets-, Positions- und Divergenzregistrierungsvertrag

## Status und Umfang

S1-QV registriert fuer die in S1-QU gebundene M2-Modusfamilie genau eine
gemeinsame Recordkapazitaet und genau eine kleinste positionsgebundene
Divergenzfolge. Die Pruefung ist statisch: Sie bindet erwartete Quellrollen,
ohne einen M2-Zustand oder ein Feld fortzuschreiben.

S1-QV implementiert keine Datentypen, keinen Kompositor, keine Fixture und
keinen Runner. Es wird kein Test und kein Feldlauf ausgefuehrt. API,
primaerer Feldkern, Runtime, Runner und Orchestrator bleiben unveraendert.

Vertragsentscheidung:

```text
M2_COMMON_CAPACITY_TWO_RECORDS_REGISTERED
FIVE_POSITION_A_B_C_D_E_SEQUENCE_REGISTERED
ORDER_IDENTIFIABILITY_REQUIRES_A_NOT_EQUAL_B
FIRST_MODE_DIVERGENCE_BOUND_AT_P4_WITH_C_NOT_EQUAL_E
DELAY_AND_ONE_SHOT_REPLAY_REMAIN_POSITIONALLY_DISTINCT
CANONICAL_REGISTRATION_PAYLOAD_AND_DIGEST_BOUND
NO_IMPLEMENTATION_NO_TEST_NO_FIELD_EXECUTION
```

## Auswahl der kleinsten Kapazitaet

Verbindlich gilt fuer beide M2-Modi:

```text
K = 2 Records
```

Die Auswahl ist minimal:

- `K = 1` koennte einen Ein-Schritt-Delay zeigen, aber keine geordnete
  Replayfolge mit mindestens zwei unterscheidbaren Quellpositionen;
- `K = 2` erlaubt die Pruefung von Aufnahmeordnung, geordneter Ausgabe,
  Erschoepfung und anschliessender Modusdivergenz;
- `K > 2` fuegt fuer diese strukturelle Trennung nur weitere Records und
  Freiheitsgrade hinzu.

`K` ist in jedem Arm unveraenderlich. Es bezeichnet keine Zeitdauer und darf
nicht aus Intervalllaenge, Expositionsfamilie oder Ergebnis abgeleitet
werden.

## Registrierte Record- und Positionsordnung

Die kanonische Recordordnung lautet:

```text
A -> B -> C -> D -> E
```

Die zugehoerige Positionsordnung lautet:

```text
P0 -> P1 -> P2 -> P3 -> P4
```

Jede Position steht fuer genau ein erfolgreich abgeschlossenes Intervall mit
genau einem aktuellen validierten A1-Vorschlag und genau einem daraus
gebildeten M2-Record. Alle fuenf Records muessen dieselbe Feldgeometrie und
kanonische Neuronenreihenfolge besitzen. Ihre Recorddigests muessen paarweise
verschieden sein.

Die Registrierung waehlt noch keine numerischen S-Vektoren. Fuer die
spaetere Identifizierbarkeit gelten jedoch verbindlich:

```text
S_A != S_B
S_C != S_E
```

`S_A != S_B` macht die Reihenfolge des zweigliedrigen Prefix sichtbar.
`S_C != S_E` macht die erste Modusdivergenz sichtbar. Weitere
Wertungleichheiten sind nicht erforderlich und duerfen nicht nach
Ergebnissicht ergaenzt werden.

## Erwarteter Quellplan

| Position | aktueller Record | DELAY-Ausgaberolle | DELAY-Quelle | REPLAY-Ausgaberolle | REPLAY-Quelle | REPLAY-Phase danach |
|---|---|---|---|---|---|---|
| `P0` | `A` | `CURRENT_A1_WARMUP` | `A` | `CURRENT_A1_CAPTURE` | `A` | `CAPTURE` |
| `P1` | `B` | `CURRENT_A1_WARMUP` | `B` | `CURRENT_A1_CAPTURE` | `B` | `EMIT` |
| `P2` | `C` | `DELAY_OLDEST_RECORD` | `A` | `REPLAY_PREFIX_RECORD` | `A` | `EMIT` |
| `P3` | `D` | `DELAY_OLDEST_RECORD` | `B` | `REPLAY_PREFIX_RECORD` | `B` | `EXHAUSTED` |
| `P4` | `E` | `DELAY_OLDEST_RECORD` | `C` | `CURRENT_A1_EXHAUSTED` | `E` | `EXHAUSTED` |

Der Plan folgt ausschliesslich aus `K = 2`, der Position und der in S1-QU
gebundenen Modusanatomie. Er liest weder Recordinhalt noch ein externes
Ereignislabel.

## Statische Zustandsfolge

### DELAY

Die erwartete Pufferfolge nach jeder Position lautet:

| Position | ausgegebene Quelle | Puffer danach, aeltester zuerst |
|---|---|---|
| `P0` | aktuelles `A` | `(A)` |
| `P1` | aktuelles `B` | `(A,B)` |
| `P2` | Record `A` | `(B,C)` |
| `P3` | Record `B` | `(C,D)` |
| `P4` | Record `C` | `(D,E)` |

### REPLAY

Die erwartete Prefix- und Cursorfolge lautet:

| Position | ausgegebene Quelle | Prefix danach | Zustand danach |
|---|---|---|---|
| `P0` | aktuelles `A` | `(A)` | `CAPTURE` |
| `P1` | aktuelles `B` | `(A,B)` | `EMIT:A` |
| `P2` | Record `A` | `(A,B)` | `EMIT:B` |
| `P3` | Record `B` | `(A,B)` | `EXHAUSTED` |
| `P4` | aktuelles `E` | `(A,B)` | `EXHAUSTED` |

`C`, `D` und `E` werden von Replay als aktuelle Inputs vollstaendig gesehen
und ueber den aktuellen A1-Vorschlag validiert. Sie werden jedoch nicht in
das eingefrorene Prefix aufgenommen.

## Kausale Divergenzbindung

Bis einschliesslich `P3` besitzen beide Modi dieselbe S-Ausgabequellenfolge:

```text
A, B, A, B
```

Bei deterministischem A1 und digestgleichem Frischfeld bleiben dadurch auch
die gemeinsamen Feldzustaende bis zum Eingang von `P4` gleich. Beide Modi
sehen an `P4` denselben aktuellen Record `E`.

Die erste registrierte Modusdivergenz lautet:

```text
P4:
  DELAY  -> gespeicherter Record C
  REPLAY -> aktueller Record E nach EXHAUSTED
```

Da `S_C != S_E` vorab gefordert ist, muessen sich die finalen S-Vektoren an
`P4` unterscheiden. H, Perzeption, Docks und Feldzeit muessen dennoch in
beiden Modi vom jeweils aktuellen A1-Vorschlag an `P4` stammen und
bitidentisch bleiben.

Die Trennung wird primaer durch verschiedene Ausgaberollen, Recordidentitaet
und Quelldigests belegt. Die numerische S-Ungleichheit ist nur die sichtbare
Fixturebedingung und darf die Provenienzpruefung nicht ersetzen.

## Kanonische Registrierung

Die kanonische kompakte UTF-8-JSON-Payload lautet exakt:

```json
{"capacity_records":2,"contract_id":"m2-capacity-position-divergence/s1qv.v1","first_divergence_position":"P4","pairwise_distinct_record_digests":true,"position_order":["P0","P1","P2","P3","P4"],"record_order":["A","B","C","D","E"],"required_equal_output_sources_through":"P3","required_s_distinctions":[["A","B"],["C","E"]],"source_schedule":[{"delay_role":"CURRENT_A1_WARMUP","delay_source":"A","position_id":"P0","replay_phase_after":"CAPTURE","replay_role":"CURRENT_A1_CAPTURE","replay_source":"A"},{"delay_role":"CURRENT_A1_WARMUP","delay_source":"B","position_id":"P1","replay_phase_after":"EMIT","replay_role":"CURRENT_A1_CAPTURE","replay_source":"B"},{"delay_role":"DELAY_OLDEST_RECORD","delay_source":"A","position_id":"P2","replay_phase_after":"EMIT","replay_role":"REPLAY_PREFIX_RECORD","replay_source":"A"},{"delay_role":"DELAY_OLDEST_RECORD","delay_source":"B","position_id":"P3","replay_phase_after":"EXHAUSTED","replay_role":"REPLAY_PREFIX_RECORD","replay_source":"B"},{"delay_role":"DELAY_OLDEST_RECORD","delay_source":"C","position_id":"P4","replay_phase_after":"EXHAUSTED","replay_role":"CURRENT_A1_EXHAUSTED","replay_source":"E"}]}
```

Ihr SHA-256-Digest ist:

```text
6abe7781ffd1d1b238b5e3302960b41d8e98dc880432869187f8eafdb8b95810
```

Jede Aenderung an Kapazitaet, Positions- oder Recordordnung, Ausgaberolle,
Quelle, Replayphase, Distinktionsbedingung oder erster Divergenzposition
erzeugt eine andere Registrierung und ist fuer S1-QV unzulaessig.

## Verwerfungsbedingungen

Die Registrierung ist ungueltig oder spaeter `NOT_COMPUTABLE`, wenn:

- ein Modus eine andere Kapazitaet als zwei Records verwendet;
- weniger oder mehr als die fuenf registrierten Positionen fuer die
  Minimalpruefung ausgewertet werden;
- Record- oder Positionsordnung wechselt;
- Recorddigests nicht paarweise verschieden sind;
- `S_A = S_B` oder `S_C = S_E` gilt;
- die Ausgaberollen oder Quellen vom kanonischen Plan abweichen;
- Replay `C`, `D` oder `E` speichert, vor `P2` ausgibt oder nach `P3` erneut
  startet;
- Delay bei `P4` nicht `C` selektiert;
- Replay bei `P4` nicht aktuelles `E` selektiert;
- die Modi vor `P4` unterschiedliche S-Ausgabequellen besitzen;
- ein Ereignis-, Arm-, Gap-, Probe- oder Ergebnislabel den Phasenwechsel
  steuert;
- eine numerische Differenz ohne korrekte Quellprovenienz als Trennung gilt;
- nach einer ungueltigen Position eine staerkere Folge nachregistriert wird.

## Paketstatus und Aussagegrenze

Nach S1-QV gilt:

```text
M2_CAPACITY_AND_MINIMAL_POSITION_AXIS_REGISTERED
M2_DELAY_REPLAY_STATIC_SOURCE_DIVERGENCE_PRESENT
M2_STATE_COMPOSITOR_ERRORS_AND_TEST_BUDGET_UNBOUND
M2_IMPLEMENTATION_AND_EXECUTION_NOT_AUTHORIZED
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

Die statische Quelltrennung bestaetigt keine Delay- oder Replaywirkung im
Feld. Sie ist kein Kandidaten- und kein Befund zu einer hypothetischen
MCM-Memory. M2 bleibt ausschliesslich eine private technische Gegenbaseline.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QW - statischer M2-Zustands-, Kompositor-, Fehlercode- und
        Testbudgetvertrag
```

S1-QW darf konkrete private Datentypen, atomare Fortschreibungsphasen,
deterministische Fehlercodes, Mutationsklassen, eine endliche Fixture fuer
die registrierte Fuenf-Positionen-Folge und ein einmaliges Testbudget binden.
Keine Implementierung, Testausfuehrung oder Feldentscheidung.
