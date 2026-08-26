# S1-OV G2/D3 O3-Checkpoints: Refaktorierungs-, Fixture-, Regressions- und Testbudgetvertrag

## Status

S1-OV bindet ausschliesslich die spaeter zulaessigen Dateien, die mechanische
Executorrefaktorierung, zwei bestehende gueltige Chains, sieben bestehende
Sequenzfehlermutationen, defensive Gates und ein endliches Einmaltestbudget
fuer den S1-OU-Checkpointpfad. Der Schritt implementiert nichts und fuehrt
keinen Test aus.

Entscheidung:

```text
G2_D3_O3_CHECKPOINT_REFACTOR_FIXTURES_REGRESSION_AND_SINGLE_TEST_BUDGET_BOUND
```

## Gebundene Dateigrenze

S1-OW darf genau diese Dateien bearbeiten oder neu anlegen:

| Datei | Aenderung | Aufgabe |
|---|---|---|
| `mcm_field_organism/g2_d3_two_step_composition.py` | bestehend, nur mechanischer Refaktor | gemeinsamer privater Executor und unveraenderte oeffentliche Komposition |
| `mcm_field_organism/g2_d3_two_step_o3_checkpoints.py` | neu | reine Checkpointregistry, Auswertung und passiver Beleg |
| `tests/g2_d3_s1ow_o3_checkpoint_fixtures.py` | neu | Verweise auf zwei gueltige Chains und sieben Sequenzfehlermutationen |
| `tests/test_g2_d3_s1ow_o3_checkpoints.py` | neu | fokussierte S1-OW-Abnahme |

Nach dem einmaligen Test duerfen nur die drei Statusdokumente
`AKTUELLER_FORSCHUNGSWEG.md`, `README.md` und
`docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md` um das tatsaechliche Ergebnis
ergaenzt werden.

Alle anderen Produktions-, Fixture-, Test- und Paketdateien bleiben
unveraendert. Insbesondere werden weder `mcm_field_organism/__init__.py` noch
ein Runtime-, Feld-, Transfer-, Runner- oder Medienmodul erweitert.

## Eingefrorene Regressionsgrundlage

Vor der Refaktorierung gelten exakt:

```text
mcm_field_organism/g2_d3_two_step_composition.py
= dc316c48043fd0bd3b4fac3f80971c73b68c065e08c850b3a9126942bfb338ea

mcm_field_organism/g2_d3_admissibility.py
= 00ac323fdf26a68b7b86c751c5c7fe8d4a2456aee0e76fca41499e959202a96e

tests/g2_d3_s1os_fixtures.py
= 58cd3e4505657fc6b964cb0dbc370d22e94261e626e67f652d43670e22f79a41

tests/test_g2_d3_s1os_two_step_composition.py
= f96527e4d7611a47c5e5cf1c083ed9d3db59ead3564ea6e2e0a81c379b4cbae6
```

Die letzten drei Dateien muessen nach S1-OW byteidentisch dieselben Digests
tragen. Das S1-OS-Testmodul mit seinen 14 Tests wird im gemeinsamen
Einmallauf unveraendert erneut ausgefuehrt. Fixtures, Erwartungen,
Receiptfelder, Fehlercodes oder Completed-Checks duerfen nicht an den
Refaktor angepasst werden.

Der Quellhash des Kompositionsmoduls darf sich nur durch folgende
mechanische Aufteilung aendern:

```text
bisheriger Funktionsrumpf
-> _execute_g2_d3_two_step(...) -> _G2D3TwoStepExecutionTrace
-> compose_g2_d3_two_step_continuation(...) gibt nur
   trace.composition_result zurueck
```

Alle bisherigen Gates, Aufrufreihenfolgen, Resultate und Belege bleiben im
privaten Executor sachlich unveraendert. Es ist verboten, bei dieser
Aufteilung einen Fehler zu reparieren, eine Reihenfolge zu optimieren, einen
Digest neu zu definieren oder eine zweite Zweischrittlogik anzulegen.

## Erlaubte Produktionsabhaengigkeiten

Das refaktorierte Kompositionsmodul behaelt exakt seine bisherigen Imports.
Das neue Checkpointmodul darf nur importieren:

- Python-Standardbibliothek fuer unveraenderliche Datentypen;
- `_execute_g2_d3_two_step`, die gebundenen Kompositionsdatentypen und den
  Kompositionsvertragsdigest aus `g2_d3_two_step_composition`;
- den bestehenden O3-Operator, seinen Receipttyp und Vertragsdigest aus
  `g2_d3_admissibility`;
- die bereits akzeptierten Registrytypen aus Projektions-, Betrags-, Grenz-
  und D3-Modulen;
- `canonical_json_bytes` und `sha256_hex` aus dem KFS-1-Validator.

JSON darf im Checkpointmodul nicht zum Rekonstruieren von D3-Zustaenden
verwendet werden. Feld-, Transfer-, Runtime-, Runner-, Medien-, Browser-,
Netzwerk-, Cache-, Speicher- und Dateischreibimporte sind verboten.

## Gebundene Oberflaechen

Im Kompositionsmodul kommt nur paketprivat hinzu:

```text
_G2D3TwoStepExecutionTrace
_execute_g2_d3_two_step(...)
```

Beide Namen bleiben ausserhalb von `__all__`. Die bestehende oeffentliche
Oberflaeche bleibt unveraendert.

Das neue Checkpointmodul darf genau die in S1-OU gebundenen Konstanten,
unveraenderlichen Registry-, Record-, Resultat- und Belegtypen sowie diese
beiden Funktionen oeffentlich machen:

```text
build_g2_d3_two_step_o3_checkpoint_registry()
evaluate_g2_d3_two_step_o3_checkpoints(...)
```

Es gibt keinen oeffentlichen Tracebuilder, keinen Callback, keinen
Checkpointbytezugriff und keinen alternativen Kompositionsaufruf.

## Zwei gueltige Checkpointchains

Die neue Fixturedatei importiert die bestehenden Tupel aus
`tests/g2_d3_s1os_fixtures.py` und bindet nur neue Namen:

| Fixture | unveraenderte Quelle | Chainrolle | erwarteter Vektor |
|---|---|---|---|
| `OV_V_XXX` | `OR_V_XXX` | `OP_CHAIN_XXX` | `(0.5, 0.25, 0.125)` |
| `OV_V_YYY` | `OR_V_YYY` | `OP_CHAIN_YYY` | `(0.5, 0.25, 0.125)` |

Es werden keine Grenzen oder D3-Bytes neu erzeugt. Beide Fixtures tragen
weiterhin exakt die in S1-OU gebundenen CP0-, CP1- und CP2-Digests.

Bei beiden gilt:

```text
directed components = (-0.25, -0.125, -0.375)
comparison digest
= 5c8d3b60bbc205594974f632a878472bf628426dc914af72514cf7b42e8a86a5
```

Die vollstaendigen Checkpointbelegdigests muessen wegen verschiedener
Sequenzprovenienz verschieden sein. Die drei korrespondierenden
O3-Belegdigests muessen dagegen fuer XXX und YYY jeweils bitidentisch sein.

## Sieben externe Sequenzfehlermutationen

Die Fixturedatei uebernimmt unveraendert genau:

```text
OR_I_UNKNOWN_FIRST
OR_I_UNKNOWN_INITIAL
OR_I_FORMATION_DISABLED
OR_I_SECOND_INVALID
OR_I_SECOND_SOURCE_C0
OR_I_SECOND_CONTACT_CROSS
OR_I_SECOND_CONTACT_RESET
```

Sie duerfen unter neuen `OV_I_*`-Namen referenziert, aber nicht kopiert,
repariert oder neu versiegelt werden. Jeder dieser Eingaben muss im
Checkpointpfad exakt liefern:

```text
checkpoint_values = not_computable
checkpoint_status = not_computable
validation_status = invalid
failure_reasons = (OU_TWO_STEP_EXECUTION_FAILED,)
O3 calls = 0
```

Der jeweilige interne OQ-Code bleibt ausschliesslich im passiven
Kompositionsbeleg gebunden. Er wird nicht als zweiter OU-Code publiziert.
Teilwerte fuer CP0 oder CP1 sind verboten.

## Defensive Gates ohne Fake-Fixtures

Folgende sechs Codes bleiben registrierte Sicherheitsgrenzen:

```text
OU_COMPOSITION_IDENTITY_MISMATCH
OU_CP0_EVALUATION_FAILED
OU_CP1_EVALUATION_FAILED
OU_CP2_EVALUATION_FAILED
OU_CHECKPOINT_IDENTITY_MISMATCH
OU_COMPONENT_IDENTITY_MISMATCH
```

Mit exakten Registries, dem gemeinsamen Executor und dem unveraenderten
O3-Operator sind sie ueber keine zusaetzliche externe Eingabe erreichbar.
S1-OV verbietet deshalb Monkeypatching, Dependency-Ersatz, gefaelschte
Traces, manipulierte Resultatobjekte und Produktionshooks nur zur
kuenstlichen Fehlererzeugung.

Die Abnahme prueft statisch, dass jeder Code registriert ist und direkt an
seinem Voraussetzungsgate fail-closed endet. Jeder solche Pfad muss alle
drei Werte und alle gerichteten Komponenten auf `not_computable` setzen.

## Aufruf- und Persistenzregeln

Pro oeffentlichem Aufruf gilt:

| Pfad | privater Executor | oeffentliche Komposition | O3 |
|---|---:|---:|---:|
| gueltige Komposition | `1` | eigener Aufruf | `0` |
| ungueltige Komposition | `1` | eigener Aufruf | `0` |
| gueltiger Checkpoint | `1` | `0` | `3` |
| Sequenzfehler im Checkpoint | `1` | `0` | `0` |

Der Checkpointpfad darf nicht zur Kontrolle erneut komponieren. Die drei
O3-Aufrufe erhalten ausschliesslich die private CP0-/CP1-/CP2-Trace in
dieser Reihenfolge.

Weder Trace noch Checkpointbytes duerfen in Resultat, Beleg, Modulzustand,
Cache oder Datei erscheinen. Die Abnahme prueft Dataclassfelder,
`__all__`, AST-Imports und verbotene Schreiboberflaechen.

## Fokussierte Testmatrix

Das neue Testmodul enthaelt genau 16 Tests:

| Test-ID | Abnahme |
|---|---|
| `T01` | die drei eingefrorenen unveraenderten Datei-Digests stimmen |
| `T02` | Registry, Records, Schemadigest und alle akzeptierten Vertragsdigests sind exakt gebunden |
| `T03` | XXX liefert Rollen, drei Werte und drei O3-Belege exakt |
| `T04` | YYY liefert denselben Vektor und Vergleichsdigest, aber einen anderen Gesamtbelegdigest |
| `T05` | korrespondierende XXX-/YYY-O3-Belege sind bitidentisch und stimmen mit drei direkten read-only O3-Auswertungen ueberein |
| `T06` | alle drei gerichteten Komponenten und Halbierungsidentitaeten stimmen exakt |
| `T07` | der passive Beleg enthaelt keine Bytes/Traces und sein Eigendigest wird unabhaengig rekonstruiert |
| `T08` | alle sieben Sequenzmutationen liefern nur `OU_TWO_STEP_EXECUTION_FAILED` und keinen Teilvektor |
| `T09` | Completed-Checks belegen Sequenzgate, O3-Sperre und Fail-Closed-Reihenfolge |
| `T10` | gleiche Inputs liefern bitgleiche Resultate; Inputs und Registries bleiben unveraendert |
| `T11` | falsche API-Typen, falsche Registries und Belege als Eingaben scheitern vor Resultat |
| `T12` | alle sieben OU-Codes sind registriert; sechs defensive Codes besitzen keine Fake-Fixtures |
| `T13` | beide oeffentlichen Pfade rufen syntaktisch nur den gemeinsamen privaten Executor auf und der Checkpointpfad nie die oeffentliche Komposition |
| `T14` | private Trace und Executor fehlen in `__all__`; keine Checkpointbytes werden publiziert oder gespeichert |
| `T15` | O3 wird nur nach vollstaendiger gueltiger Trace in der Reihenfolge CP0, CP1, CP2 ausgewertet |
| `T16` | beide Produktionsmodule besitzen keinen Feld-, Runtime-, Transfer-, Runner-, I/O-, Medien- oder Netzwerkpfad |

Die Tests verwenden ausschliesslich `unittest` und Python-Standardbibliothek.
Fixtures und Erwartungen werden nach einem Ergebnis nicht angepasst.

## Endliches S1-OW-Ausfuehrungsbudget

S1-OW darf genau einmal ausfuehren:

```text
python -m unittest \
  tests.test_g2_d3_s1os_two_step_composition \
  tests.test_g2_d3_s1ow_o3_checkpoints
```

Die Abnahme muss exakt 30 Tests entdecken: 14 unveraenderte S1-OS-Tests und
16 neue S1-OW-Tests.

Innerhalb dieses einen Laufs gelten maximal:

```text
compose_g2_d3_two_step_continuation:          35 Aufrufe
evaluate_g2_d3_two_step_o3_checkpoints:       30 Aufrufe
_execute_g2_d3_two_step:                      65 Aufrufe
evaluate_g2_d3_local_admissible_engagement:  100 Aufrufe
project_g2_d3_conservative_target:           220 interne Aufrufe
verify_and_commit_g2_d3_projected_target:    110 interne Aufrufe
evaluate_g2_d3_continuation_halving_amount:  220 interne Aufrufe
validate_g2_d3_transient_boundary:           280 interne Aufrufe
validate_g2_d3_anatomy_record:               700 interne Aufrufe
MCM-Feldschritte:                               0
Runtime-/Speicherpublikationen:                 0
Transfer-/Runner-/Medien-/Netzwerkaufrufe:      0
Dateischreibzugriffe der Operatoren:             0
read-only Quelltextzugriffe:            maximal 8
```

Bei einem Fehler wird der kombinierte Test nicht erneut ausgefuehrt. Die
Implementierung wird gegen den unveraenderten Vertrag korrigiert, ohne
Fixtures, Digests, Erwartungen, Testzahl oder Budgets umzudeuten.

## Aussagegrenze

S1-OV bindet nur die spaetere mechanische Refaktorierung und technische
Abnahme einer konstruktiv erwarteten O3-Checkpointfolge. Es gibt noch keinen
Checkpointoperator, keinen neuen Testlauf, keine Feldrueckwirkung und keinen
Funktionsbefund gegen eine angepasste zustandsbehaftete Gegenbaseline.

Der Schritt ist kein Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OW darf ausschliesslich die vier gebundenen Produktions- und Testdateien
bearbeiten beziehungsweise anlegen, den kombinierten Test genau einmal im
Budget ausfuehren und danach nur das tatsaechliche Ergebnis dokumentieren.

Runtimepublikation, Feld, Transfer, Runner, Medienpfade und eine
Funktionsentscheidung bleiben gesperrt.
