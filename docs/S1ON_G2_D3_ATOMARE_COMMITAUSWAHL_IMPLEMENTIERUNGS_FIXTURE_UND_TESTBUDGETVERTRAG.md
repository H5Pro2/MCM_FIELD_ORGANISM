# S1-ON G2/D3 atomare Commitauswahl: Implementierungs-, Fixture- und Testbudgetvertrag

## Status

S1-ON bindet ausschliesslich die Dateigrenze, kanonische Fixtures,
Fehlermutationen und ein endliches Einmaltestbudget fuer die spaetere reine
atomare Commitauswahl aus S1-OK. Es wird keine Implementierung geaendert und
kein Test ausgefuehrt.

Entscheidung:

```text
G2_D3_PURE_ATOMIC_COMMIT_SELECTION_IMPLEMENTATION_FIXTURES_AND_SINGLE_TEST_BUDGET_BOUND
```

`Commit` bezeichnet weiterhin nur die Auswahl vollstaendig gepruefter
in-memory D3-Bytes im Rueckgabeobjekt. S1-ON gibt keinen Runtime-Speicher,
keine Publikation und keine Feldintegration frei.

## Gebundene Dateigrenze

S1-OO darf genau diese Produktions- und Testdateien bearbeiten:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/g2_d3_target_projection.py` | bestehende Registry um Commitrollen ergaenzen und reine Commitauswahl implementieren |
| `tests/g2_d3_s1oo_fixtures.py` | kanonische Commitfixtures und gezielte Mutationen |
| `tests/test_g2_d3_s1oo_atomic_commit.py` | fokussierte technische Abnahme |

Die beiden Testdateien sind neu; das akzeptierte S1-OM-Produktionsmodul wird
nur um die S1-OK-Commitoberflaeche erweitert. Alle anderen Produktions-,
Fixture- und Testdateien bleiben unveraendert. Statusdokumente duerfen nach
der einmaligen Abnahme nur das tatsaechliche Ergebnis aufnehmen.

## Erlaubte Produktionsabhaengigkeiten

Es bleiben exakt die von S1-OL gebundenen Imports zulaessig. Die Commitauswahl
muss die bestehende reine Funktion
`project_g2_d3_conservative_target` im selben Modul aufrufen und darf keinen
zweiten Projektionsweg implementieren.

Zusaetzliche Feld-, Admissibility-, O3-, Transfer-, Runner-, Medien-,
Browser-, Netzwerk-, Speicher- oder Dateischreibmodule sind verboten.

## Gebundene oeffentliche Commitoberflaeche

S1-OO darf zusaetzlich genau bereitstellen:

```text
verify_and_commit_g2_d3_projected_target(
    boundary_raw_bytes,
    source_d3_raw_bytes,
    current_d3_raw_bytes,
    proposed_target_d3_raw_bytes,
    formation_enabled,
    target_commit_registry,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3AtomicCommitResult
```

Zulaessig sind ausserdem nur die unveraenderlichen Typen
`G2D3AtomicCommitReceipt` und `G2D3AtomicCommitResult` sowie die bereits in
S1-OK gebundenen Commit-Schema-, Phasen-, Status- und Fehlercodekonstanten.

Die Funktion akzeptiert keinen Projektions-, Betrags-, Validierungs- oder
Commitbeleg. Alle vier Byteeingaben muessen exakt `bytes`, der Schalter exakt
`bool` und alle Registries exakt vorregistriert sein. Falsche Typen oder
Registries scheitern vor einem Resultat.

## Feste Commitwerte

```text
commit_receipt_schema
= g2_d3_atomic_commit_receipt/s1ok.v1

commit_contract_digest
= 4cae38e9c7986ff6099cfd8c2c742a2c11465bb61a9885441a403fab9b5859b5

accepted_projector_contract_digest
= c761d3f5b2dc486ca6cb9389d305e9b2ec8d847812bac72e40d89995a66f6e2b

accepted_amount_operator_contract_digest
= 396bd7b9fde4b7ee3b268e1d53245fd2a950cf4d8d9464f084d9b498c17de83b

accepted_boundary_validator_contract_digest
= 7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0

accepted_d3_validator_contract_digest
= b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c
```

Die bestehende Registry wird exakt um folgende Werte erweitert:

```text
commit_receipt_schema_id
commit_receipt_schema_version
commit_statuses
commit_phases
commit_failure_codes
```

## Gebundene Pruefreihenfolge

Jeder fachlich erreichbare Aufruf verwendet exakt:

```text
1. api_intake
2. source_projection_recomputation
3. proposed_target_validation
4. proposed_target_comparison
5. current_source_validation
6. stale_source_gate
7. atomic_selection
8. persistence_guard
9. commit_receipt
```

Der erste Fehler beendet die nachgelagerten Phasen. Ein Vorschlag wird nie
repariert, neu digestiert oder auf den aktuellen Zustand umgerechnet.

## Fixtureform

Jedes Commitfixture ist ein unveraenderliches Tupel:

```text
(
    boundary_raw_bytes,
    source_d3_raw_bytes,
    current_d3_raw_bytes,
    proposed_target_d3_raw_bytes,
    formation_enabled,
)
```

Die Fixturedatei importiert die S1-OM-Grenzen, Quellen und Zielbytes sowie
den einzelnen bestehenden D3-Fehlerrecord `D3_I_RECORD_DIGEST`. Sie erzeugt
keine Projektion und kennt keinen Receiptwert. Wertgleiche aktuelle und
vorgeschlagene Bytes duerfen testseitig als getrennte Byteobjekte erzeugt
werden, damit die Rueckgabeidentitaet eindeutig pruefbar bleibt.

## Fuenf gueltige Kontrollen

| Fixture | Grenze/Quelle | aktueller Zustand | Vorschlag | Status | Rueckgabeobjekt |
|---|---|---|---|---|---|
| `ON_V_NO_CHANGE_FIRST_X` | first X / C0 | C0 | C0 | `NO_CHANGE_COMMITTED` | aktuelles Byteobjekt |
| `ON_V_NO_CHANGE_XY` | X/Y / C0 | C0 | C0 | `NO_CHANGE_COMMITTED` | aktuelles Byteobjekt |
| `ON_V_PROJECTED_XX` | X/X / C0 | C0 | Mixed | `PROJECTED_COMMITTED` | vorgeschlagenes Byteobjekt |
| `ON_V_PROJECTED_YY` | Y/Y / C0 | C0 | Mixed | `PROJECTED_COMMITTED` | vorgeschlagenes Byteobjekt |
| `ON_V_PROJECTED_SECOND` | X/X / Mixed | Mixed | Second | `PROJECTED_COMMITTED` | vorgeschlagenes Byteobjekt |

Gebundene D3-Inputdigests:

```text
C0
= d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7

Mixed
= 2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8

Second
= a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab
```

Die Boundary-Inputdigests bleiben exakt die S1-OH-/S1-OL-Werte der
zugehoerigen first-X-, X/Y-, X/X-, Y/Y- und Mixed-X/X-Grenzen.

## Fuenf Rekonstruktionsfehler

Die fuenf unveraenderten S1-OI-Negativinputs werden jeweils mit
`current_d3_raw_bytes = source_d3_raw_bytes` und einem beliebigen
bytegleichen Vorschlag gebunden. Sie muessen vor jeder Vorschlagsvalidierung
exakt liefern:

```text
commit_status = not_computable
committed_d3_raw_bytes = not_computable
failure_reasons = (OK_COMMIT_PROJECTION_RECOMPUTATION_FAILED,)
```

Es sind genau:

```text
ON_I_RECOMPUTE_SOURCE
ON_I_RECOMPUTE_NUMERIC_DOMAIN
ON_I_RECOMPUTE_HALVING_INVARIANT
ON_I_RECOMPUTE_TARGET_REPRESENTATION
ON_I_RECOMPUTE_EXACT_LEDGER
```

## Vier getrennte Commitfehler

### Ungueltiger Vorschlag

`ON_I_PROPOSED_INVALID` verwendet die gueltige X/X-C0-Projektion, aber
`D3_I_RECORD_DIGEST` als Vorschlag.

```text
invalid proposed input digest
= 1e101961c98475ef1015c85f5eb68de4ef101b977b5db435294a6e822c931a9f

expected
= OK_COMMIT_PROPOSED_TARGET_INVALID
```

Die aktuelle Quelle ist gueltig und unveraendert, wird wegen des frueheren
Vorschlagsfehlers aber noch nicht als Commitquelle ausgewertet.

### Gueltiger, aber falscher Vorschlag

`ON_I_PROPOSED_MISMATCH` verwendet die gueltige X/X-C0-Projektion, aber den
gueltigen C1-Record statt Mixed:

```text
proposed C1 input digest
= 058ae964682a9750a316d1db1b2e155714c18bc5adab9eb71fbc6e85e3be54b5

expected
= OK_COMMIT_PROPOSED_TARGET_MISMATCH
```

Der Vorschlag wird nicht auf Mixed korrigiert.

### Ungueltiger aktueller Zustand

`ON_I_CURRENT_INVALID` verwendet die gueltige X/X-C0-Projektion und Mixed
als korrekten Vorschlag, aber `D3_I_RECORD_DIGEST` als aktuellen Zustand:

```text
expected
= OK_COMMIT_CURRENT_SOURCE_INVALID
```

### Stale Source

`ON_I_STALE_SOURCE` verwendet X/X mit C0 als Originalquelle und Mixed als
korrekten Vorschlag. Der aktuelle Zustand ist ebenfalls der gueltige
Mixed-Record und damit nicht mehr die Originalquelle:

```text
source anatomy_record_digest
= 1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f

current anatomy_record_digest
= d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c

commit_status = STALE_SOURCE
failure_reasons = (OK_COMMIT_STALE_SOURCE,)
committed_d3_raw_bytes = not_computable
```

Der stale Zustand wird nicht erneut projiziert. Der Aufruf muss mit frischen
Originalbytes neu begonnen werden.

## Passive Belegregeln

Der Commitbeleg enthaelt exakt die in S1-OK gebundenen Felder. Er enthaelt
keine Rohbytes und keinen verschachtelten Projektionsbeleg. Sein Digest wird
ueber die kanonische Payload ohne `commit_receipt_digest` berechnet.

Bei jedem Fehler bleiben nicht belastbar erreichte Rollen
`not_computable`. Pro Fehlerbeleg ist exakt ein Fehlercode gebunden. Ein
Beleg darf weder als Commitinput noch als spaetere Autorisierung akzeptiert
werden.

## Fokussierte Testmatrix

| Test-ID | Abnahme |
|---|---|
| `T01` | alle Fixture-, Boundary-, Quell-, Current- und Proposed-Digests sind exakt gebunden |
| `T02` | fuenf gueltige Kontrollen liefern exakt Status und ausgewaehlte Bytes |
| `T03` | Nullcommit gibt exakt das aktuelle Byteobjekt zurueck |
| `T04` | positiver Commit gibt exakt das vorgeschlagene Byteobjekt zurueck |
| `T05` | fuenf Rekonstruktionsfehler sperren jede Vorschlagspruefung mit Einzelcode |
| `T06` | ungueltiger Vorschlag scheitert vor Vergleich und Currentpruefung |
| `T07` | gueltiger falscher Vorschlag scheitert ohne Reparatur |
| `T08` | ungueltiger aktueller Zustand scheitert vor Stale-Gate |
| `T09` | stale Quelle liefert `STALE_SOURCE` und keine Zustandsbytes |
| `T10` | Completed-Checks belegen fuer alle Fehler das Voraussetzungsgating |
| `T11` | alle Digestrollen und der kanonische Commitbelegdigest bleiben getrennt |
| `T12` | gleiche Originalinputs und Registries liefern bitgleiche Resultate und Belege |
| `T13` | Eingaben/Registries bleiben unveraendert; falsche Typen, Registries und Belege scheitern vor Resultat |
| `T14` | Moduloberflaeche erreicht keinen Runtime-, O3-, Feld-, Runner-, I/O-, Medien- oder Netzwerkpfad |

Die Tests verwenden ausschliesslich `unittest` und Python-Standardbibliothek.
Erwartete Projektionen werden nicht aus dem vorgeschlagenen Ziel abgeleitet.
Fixtures, Digests und Erwartungen duerfen nach dem Testresultat nicht
angepasst werden.

## Endliches S1-OO-Ausfuehrungsbudget

S1-OO darf genau einmal ausfuehren:

```text
python -m unittest tests.test_g2_d3_s1oo_atomic_commit
```

Innerhalb dieser Abnahme gelten maximal:

```text
verify_and_commit_g2_d3_projected_target:    45 Aufrufe
project_g2_d3_conservative_target:           40 interne Aufrufe
evaluate_g2_d3_continuation_halving_amount:  40 interne Aufrufe
validate_g2_d3_transient_boundary:           40 interne Aufrufe
validate_g2_d3_anatomy_record:              160 interne Aufrufe
O3-Auswertungen:                               0
MCM-Feldschritte:                               0
Runtime-/Speicherpublikationen:                 0
Transfer-/Runner-/Medien-/Netzwerkaufrufe:      0
Dateischreibzugriffe des Operators:             0
read-only Quelltextzugriffe:           maximal 2
```

Bei einem Fehler wird der S1-OO-Test nicht erneut ausgefuehrt. Die
Implementierung wird gegen den unveraenderten Vertrag korrigiert, ohne
Fixtures oder Erwartungen nachtraeglich umzudeuten.

## Aussagegrenze

S1-ON bindet nur eine spaetere reine Zustandsauswahl. Es gibt noch keine
implementierte Commitauswahl, keine Runtimepublikation, keine Sequenzruntime,
keine O3- oder Feldwirkung und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OO darf ausschliesslich die gebundene Produktionsdatei erweitern, die zwei
Testdateien anlegen, den fokussierten Test genau einmal ausfuehren und das
tatsaechliche Ergebnis in den Statusdokumenten festhalten.

Runtimepublikation, O3, Feld, Transfer, Runner und Medienpfade bleiben
unveraendert und gesperrt.
