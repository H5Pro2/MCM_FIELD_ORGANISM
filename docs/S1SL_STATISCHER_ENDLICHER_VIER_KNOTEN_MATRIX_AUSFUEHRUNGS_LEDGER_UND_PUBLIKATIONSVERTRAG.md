# S1-SL: Statischer endlicher Vier-Knoten-Matrix-Ausfuehrungs-, Ledger- und Publikationsvertrag

## Status und Zweck

S1-SL bindet ausschliesslich die technische Huelle oberhalb des in S1-SK
abgenommenen atomaren Einzelzellen-Lebenszyklus. Der Vertrag legt fest, wie
die 14 registrierten Modellrollen und 17 kanonischen Expositionsplaene
spaeter genau einmal zu einer endlichen Matrix verbunden werden duerfen.

S1-SL implementiert keinen Matrixrunner, definiert oder startet keinen Test,
ruft keine Modellrolle und keine Zelle auf und bildet weder Comparatoren
noch Ergebnisentscheidungen.

## Gebundene Eingangsidentitaeten

Ein spaeterer Matrixrunner darf nur aus diesen gemeinsam validierten
Eingaengen entstehen:

| Rolle | Gebundener Wert |
|---|---|
| Frischmanifest | `reports/s1rk_four_node_fresh_manifest.json` |
| Frischmanifestdigest | `ae7a7356a3e06776a000b6e9fafef75b717944f1d75da62d4418be98cc439c68` |
| Matrixregistrierung | `reports/s1sd_four_node_fresh_matrix_registration.json` |
| Matrixregistrierungsdigest | `edd3414b3dcc082c0ab7bec66f8dd278cedecd76d11e649ca7aff46a9317a4ba` |
| Expositionsfixture | `mcm.s1sf.four-node-exposure-fixture.v1` |
| Expositionsfixturedigest | `ca66f3a673eaca663a0973f7e956a90f4788e6f51963b71de4952801936bac3e` |
| Einzelzellenproducer | `execute_four_node_cell` |
| Einzelzellenabnahme | S1-SK, `14/14` Tests bestanden |

Manifest, Registrierung und Fixture muessen vor der ersten Zelle
vollstaendig fail-closed validiert werden. Ein passender Einzeldigest ersetzt
keine Queridentitaetspruefung.

## Modellrollenachse

Die Rollenpositionen stammen unveraendert aus dem abgenommenen
Frischmanifest:

```text
01 A0_CURRENT_CONTACT
02 A1_FAST_SH
03 A2_B1_FIXED_ADAPTER
04 A2_B2_INTEGRATOR
05 A2_B3_LOCAL_LEAKY
06 A2_B4_LINEAR_COUPLED
07 A2_B5_F3_FULL
08 A2_B6_CONST_V
09 A3_NORM
10 M1_PARALLEL_LEAK
11 M2_DELAY
12 M2_REPLAY
13 M4_DTS1_T1
14 M5_DIRECT
```

Keine Rolle darf umbenannt, ausgelassen, dupliziert oder durch einen
historischen Adapter ersetzt werden.

## Expositionsplanachse

Die Planpositionen stammen unveraendert aus Registrierung und Fixture:

| Position | Planrolle | Intervalle | Align | Checkpoints | Terminaltick |
|---:|---|---:|---:|---:|---:|
| 01 | `F_A` | 4 | 1 | 2 | 40 |
| 02 | `F_C` | 4 | 1 | 2 | 40 |
| 03 | `F_G` | 4 | 1 | 2 | 40 |
| 04 | `T_EARLY` | 3 | 1 | 2 | 30 |
| 05 | `T_LATER` | 5 | 1 | 2 | 50 |
| 06 | `I_LOCAL` | 7 | 1 | 2 | 70 |
| 07 | `I_REMOTE` | 7 | 1 | 2 | 70 |
| 08 | `I_GAP` | 7 | 1 | 2 | 70 |
| 09 | `C_LOCAL` | 7 | 1 | 4 | 70 |
| 10 | `C_REMOTE` | 7 | 1 | 4 | 70 |
| 11 | `C_GAP` | 7 | 1 | 4 | 70 |
| 12 | `R_EARLY` | 8 | 1 | 2 | 80 |
| 13 | `R_LATE` | 11 | 1 | 2 | 110 |
| 14 | `U_RELEASED` | 13 | 1 | 2 | 130 |
| 15 | `U_EARLY` | 10 | 1 | 2 | 100 |
| 16 | `U_FRESH_B_EARLY` | 10 | 1 | 2 | 100 |
| 17 | `U_FRESH_B_LATE` | 13 | 1 | 2 | 130 |

Die Spaltensummen pro Modellrolle sind exakt 127 Intervalle, 17
Alignoperationen und 40 Checkpoints.

## Kanonische Matrixordnung

Die Matrix wird planweise und innerhalb jedes Plans rollenweise gebildet:

```text
for plan_position in 01..17:
    for model_role_position in 01..14:
        exactly one isolated cell
```

Der lueckenlose Zellordinal ist:

```text
cell_ordinal = (plan_position - 1) * 14 + model_role_position
```

Damit besitzt `F_A/A0_CURRENT_CONTACT` Ordinal 1,
`F_A/M5_DIRECT` Ordinal 14, `F_C/A0_CURRENT_CONTACT` Ordinal 15 und
`U_FRESH_B_LATE/M5_DIRECT` Ordinal 238.

Die Ordnung ist reine aeussere Provenienz. `execute_four_node_cell` erhaelt
nur die bereits gebundenen Eingaben Manifest, Registrierung, Fixture,
Modellrolle und Planposition. Zellordinal, Modellrollenposition, Planrolle,
Nachbarrolle und Matrixstatus gelangen weder in die Zelle noch in einen
Modellaufruf. Die Einzelzellenhuelle haelt Modellrolle und Planposition
weiterhin ausserhalb des eigentlichen Modellinputs.

## Frischstart und Isolation

Fuer jeden Ordinal gilt:

1. `execute_four_node_cell` wird genau einmal mit Manifest,
   Matrixregistrierung, Fixture, Modellrolle und Planposition aufgerufen.
2. Die Zelle baut intern genau einen neuen rollenweisen Frischobjektgraphen.
3. Kein Bundle, keine Assembly, kein Carry, kein privater Zustand und kein
   Feldobjekt wird aus einer vorherigen Zelle uebernommen.
4. Digestgleiche Frischprojektionen bedeuten Wertgleichheit, nicht gemeinsam
   veraenderliche Objektidentitaet.
5. Nur ein atomar `COMPLETED` publiziertes `FourNodeCellResult` darf in das
   interne Matrixledger eingehen.

Es gibt keine Warmstarts, keine rollenweisen Dauerzustande und keine
Fortsetzung zwischen zwei Plaenen.

## Endliches Gesamtbudget

Aus den beiden Achsen folgen exakt:

```text
238 isolierte Frischzellen
1778 Modellintervalle
238 zeitlose Alignoperationen
560 passive Pflichtcheckpoints
```

Davon entfallen auf B3 bis B6:

```text
68 Zellen
508 Modellintervalle mit refinement=2
68 Alignoperationen
160 Checkpoints
```

Auf die uebrigen zehn Rollen entfallen:

```text
170 Zellen
1270 Modellintervalle mit refinement=None
170 Alignoperationen
400 Checkpoints
```

Die 560 Checkpoints teilen sich in 476 universelle Probecheckpoints und 84
zusaetzliche C-Familien-Checkpoints. Diese Zahlen sind harte
Vollstaendigkeitsgrenzen und keine Laufzeitabschaetzung.

## Zellannahme in das interne Ledger

Vor der Aufnahme eines Zellresultats muessen mindestens gelten:

- `status=COMPLETED` und `failure_codes=()`;
- Zellidentitaet entspricht exakt aktuellem Ordinal, Rolle und Plan;
- Manifest-, Registrierungs-, Fixture- und Plandigests stimmen;
- Modellkonfigurationsdigest bleibt fuer dieselbe Rolle ueber alle 17
  Plaene gleich;
- Refinement ist fuer B3 bis B6 exakt `2`, sonst `None`;
- Checkpointanzahl, Rollen, Ticks und Reihenfolge entsprechen dem Plan;
- finaler Feldtick entspricht dem gebundenen Terminaltick;
- finaler Carry, terminaler Ereigniskettendigest und Zellresultatdigest sind
  vorhanden;
- kein Zellresultat oder Checkpointordinal wurde bereits aufgenommen.

Der spaetere Runner benoetigt deshalb eine schmale oeffentliche
`validate_four_node_cell_result`-Rolle im Einzelzellenmodul. Sie darf nur
die bereits gebundene Resultatkanonisierung und Statusinvarianten pruefen;
sie darf keine Zelle erneut ausfuehren oder reparieren.

## Matrixereigniskette

Jede angenommene Zelle erweitert genau einmal einen Matrixkettendigest. Die
Praeimage bindet:

```text
vorheriger Matrixkettendigest oder MATRIX_CHAIN_ORIGIN
cell_ordinal
model_role_position und model_role
plan_position und plan_role
cell_identity
cell_result_digest
terminal_event_chain_digest
ordered_checkpoint_digests
```

Die Kette bindet nur bereits atomar publizierte Zellresultate. Sie darf
keinen privaten Rohzustand, kein Feldobjekt und keinen Comparatorwert
enthalten.

## Interner Zellsummary

Nach erfolgreicher Validierung wird pro Ordinal nur ein unveraenderlicher
Summary in das Matrixledger aufgenommen:

```text
cell_ordinal
model_role_position
model_role
plan_position
plan_role
cell_identity
model_configuration_digest
refinement_or_none
final_carry_digest
terminal_event_chain_digest
ordered_checkpoint_digests
cell_result_digest
matrix_chain_digest
cell_summary_digest
```

Der vollstaendige finale Carry wird nicht in das spaetere Matrixresultat
uebernommen. Er bleibt nur waehrend der Zellvalidierung erreichbar und wird
danach verworfen. Die 560 Checkpointrecords duerfen fuer eine spaetere,
getrennt zu bindende technische Vergleichsstufe erhalten bleiben.

## Atomarer Matrixerfolg

Eine Matrix ist nur dann `COMPLETED`, wenn alle 238 Ordinale lueckenlos
angenommen wurden und alle Gesamtbudgets exakt stimmen. Erst dann darf ein
`FourNodeMatrixResult` publiziert werden mit:

```text
status = COMPLETED
manifest_registration_fixture_digests
axis_and_budget_identity
ordered_238_cell_summaries
ordered_560_checkpoint_records
per_role_configuration_digests
terminal_matrix_chain_digest
matrix_result_digest
failure_codes = ()
```

Das Resultat enthaelt keine finalen Carryobjekte, privaten Rohzustaende,
Zwischenreceipts, Comparatoren, Rangfolgen oder Funktionsurteile.

## Atomarer Matrixfehler

Jede ungueltige Eingabe, jede nicht abgeschlossene Zelle, jede
Identitaetsabweichung und jede Ledger-, Digest-, Reihenfolge- oder
Budgetabweichung stoppt die Matrix unmittelbar. Publiziert wird nur:

```text
status = NOT_COMPUTABLE
manifest_registration_fixture_digests soweit validiert
failed_cell_ordinal_or_none
failed_cell_identity_or_none
cell_failure_digest_or_none
failure_codes
failure_receipt_digest
matrix_result_digest
ordered_cell_summaries = ()
ordered_checkpoint_records = ()
terminal_matrix_chain_digest = None
```

Auch bereits intern abgeschlossene Zellen und Checkpoints werden im
Fehlerresultat nicht publiziert. Es gibt keinen Retry, kein Ueberspringen,
keinen Ersatzwert, keine Teilmatrix und keine Fortsetzung ab dem
Fehlerordinal.

## Publikations- und Informationsgrenze

Der Matrixrunner darf keine Ergebnisse waehrend des Laufs auf eine
dauerhafte Ergebnisdatei schreiben. Eine spaetere Dateipublikation darf erst
nach dem atomaren Gesamterfolg aus dem vollstaendigen unveraenderlichen
Matrixresultat erfolgen.

Logausgaben duerfen nur Fortschrittsordinal und technischen Status tragen.
Feldwerte, Checkpointvektoren, private Digests und Zwischenkontraste bleiben
bis zur Gesamtpublikation intern. Damit kann keine Zwischenbeobachtung die
gebundene Reihenfolge, Konfiguration oder weitere Ausfuehrung beeinflussen.

## Implementierungs- und Testbudget fuer S1-SM

S1-SM darf genau bearbeiten:

```text
mcm_field_organism/four_node_cell_lifecycle.py
mcm_field_organism/four_node_matrix_lifecycle.py
tests/test_four_node_matrix_lifecycle.py
```

Im Einzelzellenmodul ist nur die reine Resultatvalidierungsrolle zulaessig.
Die neue Matrixhuelle darf ausschliesslich den abgenommenen
`execute_four_node_cell`-Producer verwenden. Modellinvocation, Fixture,
Frischfabrik, Modellkerne, Comparatoren und historische Orchestratoren
bleiben unveraendert.

S1-SM darf hoechstens 18 fokussierte Tests definieren, aber nicht
ausfuehren. Sie muessen mindestens pruefen:

- kanonische planweise und rollenweise Ordinalbildung;
- genau 238 getrennte Zellaufrufe ohne Objektgraphuebernahme;
- 1778/238/560-Gesamtbudget und F3-Aufteilung;
- konstante rollenweise Konfigurationsdigests;
- geordnete Zellsummary- und Checkpointledger;
- lueckenlose Matrixdigestkette;
- Verwerfen finaler Carryobjekte aus dem Matrixresultat;
- atomaren Fehler ohne Teilsummary oder Checkpointpublikation;
- Stopp am ersten Fehler ohne Retry;
- Ausschluss von Comparator-, Ergebnis- und Erwartungslabels aus
  Zellaufrufen.

Die Tests duerfen Zellresultate durch streng geformte synthetische
Testdoubles ersetzen, damit S1-SM keine 238 realen Zellen ausfuehrt.

## Aussagegrenze und Entscheidung

S1-SL ist reine technische Orchestrierungs- und Publikationsmethodik. Der
Vertrag bestaetigt keine Modellfunktion, keine Kandidatenwirkung und keine
Faehigkeit einer hypothetischen MCM-Memory-Entwicklungsrichtung.

```text
FINITE_238_CELL_MATRIX_ORDER_LEDGER_ATOMIC_PUBLICATION_CONTRACT_BOUND
NO_IMPLEMENTATION_NO_TEST_NO_CELL_OR_MATRIX_EXECUTION_NO_RESULT_DECISION
```

Der einzige naechste Schritt ist S1-SM im oben begrenzten Implementierungs-
und Testdefinitionsbudget.
