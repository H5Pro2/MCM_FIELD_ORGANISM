# S1-NV G2/D3 Admissibilitaetsoperator-Implementierungs-, Fixture- und Testbudgetvertrag

## Status

S1-NV bindet ausschliesslich die spaetere isolierte Implementierung und
Abnahme des in S1-NU ausgewaehlten reinen O3-Operators. Dieser Schritt legt
Dateien, API, Beleg, Fixtures, Fehlerverhalten und ein endliches Testbudget
fest. Er implementiert oder fuehrt O3 noch nicht aus.

Entscheidung:

```text
G2_D3_ADMISSIBILITY_IMPLEMENTATION_FIXTURES_AND_TEST_BUDGET_BOUND
```

## Gebundene Dateigrenze

S1-NW darf genau zwei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/g2_d3_admissibility.py` | reiner validierungsgebundener O3-Operator und unveraenderlicher Beleg |
| `tests/test_g2_d3_s1nw_admissibility.py` | fokussierte technische Abnahme |

Alle bestehenden Dateien bleiben unveraendert. Insbesondere duerfen der
akzeptierte D3-Validator und `tests/g2_d3_s1nr_fixtures.py` weder erweitert
noch repariert werden.

## Erlaubte Abhaengigkeiten

Das neue Produktionsmodul darf nur importieren:

- Python-Standardbibliothek fuer unveraenderliche Datentypen und internes
  JSON-Lesen;
- `G2D3ValidationRegistry` und
  `validate_g2_d3_anatomy_record` aus dem akzeptierten D3-Validator;
- `canonical_json_bytes` und `sha256_hex` aus dem unveraenderten
  KFS-1-Validator.

Feld-, Runner-, Transfer-, Medien-, Netzwerk- oder I/O-Module sind
unzulaessig.

## Reine oeffentliche API

Das Modul darf genau eine oeffentliche Operatorfunktion bereitstellen:

```text
evaluate_g2_d3_local_admissible_engagement(
    raw_bytes,
    registry,
) -> G2D3AdmissibilityReceipt
```

Zusaetzlich duerfen nur der unveraenderliche Belegtyp, Schema- und
Fehlercodekonstanten oeffentlich sein. Reines Parsing und die O3-Berechnung
bleiben privat.

Die API validiert `raw_bytes` zuerst mit
`validate_g2_d3_anatomy_record`. Nur ein gueltiger D3-Record erreicht die
private Berechnung:

```text
local_admissible_engagement
= max(0.0, free - bound_configured)
```

Es gibt keine API fuer ungepruefte Zahlen und keine stillschweigende
Konvertierung eines aggregierten Dreirollenrecords.

## Operatorbeleg

`G2D3AdmissibilityReceipt` bindet genau:

```text
receipt_schema_id = g2_d3_admissibility_receipt
receipt_schema_version = s1nv.v1
input_bytes_digest
source_validation_receipt_digest
source_anatomy_record_digest oder not_computable
free oder not_computable
bound_configured oder not_computable
local_admissible_engagement oder not_computable
evaluation_status = valid oder invalid
failure_reasons
operator_contract_digest
admissibility_receipt_digest
```

Der Beleg ist unveraenderlich. Sein Digest bindet alle Felder ausser sich
selbst in kanonischer Form. Der Operatorvertragsdigest lautet:

```text
6f63fcf075a95b6e22ff9cbad9d1326d99478900f6ae613e4cd95da7eacbc756
```

Er ist SHA-256 der ASCII-Kennung
`g2.d3.admissibility.contract.s1nv.v1`.

## Fail-Closed-Verhalten

Ein durch den D3-Validator abgelehnter Record liefert exakt:

```text
evaluation_status = invalid
failure_reasons = (D3_ADMISSIBILITY_SOURCE_RECORD_INVALID,)
free = not_computable
bound_configured = not_computable
local_admissible_engagement = not_computable
```

Der vorgelagerte D3-Beleg bleibt ueber
`source_validation_receipt_digest` referenziert. Seine internen Fehlercodes
werden nicht dupliziert oder als Operatorfehler umgedeutet.

Falsche API-Typen oder eine ungueltige Registryinstanz duerfen wie im
D3-Validator `TypeError` beziehungsweise `ValueError` vor einem Operatorbeleg
ausloesen. Es entsteht kein Teilbeleg.

## Gebundene positive Erwartungen

Die bestehenden bytefesten S1-NR-Fixtures werden unveraendert wiederverwendet:

| Fixture | `free` | `bound_configured` | Erwartetes `local_admissible_engagement` |
|---|---:|---:|---:|
| `D3_V_C0` | `0.5` | `0.0` | `0.5` |
| `D3_V_C1` | `0.5` | `0.5` | `0.0` |
| `D3_V_MIXED` | `0.5` | `0.25` | `0.25` |
| `D3_V_C1_IDENTITY_CONTROL` | `0.5` | `0.5` | `0.0` |
| `D3_V_C1_AGGREGATE_CONTROL` | `0.25` | `0.75` | `0.0` |

Damit sind insbesondere vorab gebunden:

```text
Delta_G2 = A_C1 - A_C0 = -0.5
A_MIXED = 0.25
A_C1_IDENTITY_CONTROL = A_C1
```

Die Identitaetskontrolle zeigt nur, dass der Sachwert nicht aus Kanten- oder
Traegerlabels stammt. Sie ist keine gueltige F1-Paarung mit C0.

## Ablations- und Aggregationskontrollen

Die reine S1-NO-Ablation von C1 entspricht byteinhaltlich dem C0-
Ressourcenzustand. Deshalb muss gelten:

```text
A_C0 = 0.5
A_ablate_C1 = 0.5
Delta_G2_ablated = 0.0
```

Ein aggregiert geformtes Recordobjekt mit nur
`free`, `bound` und `blocked` wird vom D3-Validator abgelehnt und liefert nur
`D3_ADMISSIBILITY_SOURCE_RECORD_INVALID`. Ein fehlendes
`bound_configured` wird niemals als `0.0` ergaenzt.

## Repraesentative Invalidklassen

Die fokussierte Abnahme verwendet genau diese drei unveraenderten
S1-NR-Mutationen:

| Fixture | D3-Ursache | Operatorerwartung |
|---|---|---|
| `D3_I_RECORD_DIGEST` | falscher Recorddigest | source record invalid, kein Sachwert |
| `D3_I_NEGATIVE` | negative Ressourcenrolle | source record invalid, kein Sachwert |
| `D3_I_NEGATIVE_ZERO` | nichtkanonische Serialisierung | source record invalid, kein Sachwert |

Die vollstaendige D3-Fehlermatrix bleibt Eigentum der akzeptierten
Validatorabnahme und wird hier nicht erneut ausgefuehrt.

## Fokussierte Testmatrix

| Test-ID | Abnahme |
|---|---|
| `T01` | alle fuenf positiven Records liefern exakt die gebundenen Sachwerte |
| `T02` | C0/C1 liefert exakt `Delta_G2=-0.5` |
| `T03` | reine C1-Ablation liefert exakt die C0-Ausgabe und Null-Differenz |
| `T04` | drei Invalidklassen liefern fail-closed keinen Sachwert |
| `T05` | aggregierte Dreirollenform wird abgelehnt und nicht ergaenzt |
| `T06` | gleiche Bytes und Registry liefern bitgleiche Belege |
| `T07` | Eingabebytes und Registry bleiben unveraendert |
| `T08` | Eingabe-, Record-, Validierungs-, Vertrags- und Belegdigests bleiben getrennt |
| `T09` | falsche API-Typen und veraenderte Registry scheitern vor einem Teilbeleg |
| `T10` | Moduloberflaeche erreicht keinen Feld-, Transfer-, Runner-, I/O-, Medien- oder Netzwerkpfad |

Die Tests verwenden ausschliesslich `unittest` aus der Standardbibliothek.

## Endliches S1-NW-Ausfuehrungsbudget

S1-NW darf genau einmal fokussiert ausfuehren:

```text
python -m unittest tests.test_g2_d3_s1nw_admissibility
```

Innerhalb der Abnahme gelten maximal:

```text
evaluate_g2_d3_local_admissible_engagement: 24 Aufrufe
validate_g2_d3_anatomy_record:               24 interne Aufrufe
validate_g2_d3_f1_pair:                       0 Aufrufe
MCM-Feldschritte:                              0
Transferbuchungen:                             0
Runner-/Medien-/Netzwerkaufrufe:               0
Dateischreibzugriffe:                           0
read-only Quelltextzugriffe:              maximal 2
```

Bei einem Fehler werden Vertrag und Implementierung getrennt geprueft. Kein
Fixture, Erwartungswert oder Fehlercode darf anhand des Ergebnisses angepasst
und der Lauf nicht innerhalb S1-NW wiederholt werden.

## Aussagegrenze

S1-NV bindet nur eine spaetere statische Operatorabnahme. Es gibt noch keinen
implementierten O3-Befund, keinen Transfer, keine Bildung, Abschwaechung,
Interferenz, Dynamik oder Feldwirkung und keinen Befund zur hypothetischen
MCM-Memory.

## Naechster erlaubter Schritt

S1-NW darf ausschliesslich die zwei gebundenen Dateien implementieren, den
fokussierten Test genau einmal innerhalb des Budgets ausfuehren und den Befund
dokumentieren. Alle bestehenden Dateien und alle Feld- und Dynamikpfade
bleiben unveraendert.
