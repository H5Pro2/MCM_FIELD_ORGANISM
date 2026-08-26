# S1-TC: Statischer Nullabilitaets-, Serialisierungs-, Test- und getrennter Neulaufvertrag

## Status und Zweck

S1-TC bindet die engste technische Korrektur des in S1-TB falsifizierten
Rezeptor-Provenienztyps. Es wird keine Feldmechanik, Metrik, Toleranz,
Profilachse oder Ergebnisregel geaendert.

S1-TC aendert keinen Code, definiert oder startet keinen Test, ruft keinen
Comparator auf und entfernt keinen S1-TB-Beleg.

## Bestehende Architekturregel

Die aktuelle MCM-Architektur unterscheidet bereits verbindlich:

```text
kein Rezeptorkontakt      = receptor_contact: None
gemessener Nullkontakt    = receptor_contact: 0.0
gemessener Kontakt        = receptor_contact: endlicher Zahlenwert
```

`MCMFieldPerception.receptor_contact` ist deshalb bereits als
`float | None` implementiert. Der S1-TB-Stop entstand nicht aus einer neuen
fachlichen Ausnahme, sondern aus einer zu engen Projektion dieser
bestehenden Zustandsgrenze in den passiven Comparatorinput.

Die historische Annotation des bereits publizierten
`FourNodeCheckpointRecord` wird nicht nachtraeglich geaendert. Ihre Bytes
gehoeren zum S1-SS-Quellinventar. Der neue Adapter muss die tatsaechlich
kanonisch publizierten Werte typgerecht projizieren, ohne den historischen
Beleg umzuschreiben.

## Drei getrennte Vektorrollen

### Numerisches Aktivierungsprofil S

```text
activation: tuple[float, float, float, float]
```

Alle vier Komponenten muessen endliche reelle Zahlen sein. `None`, NaN,
Unendlich und Bool sind unzulaessig.

### Numerisches Nachbildprofil H

```text
afterimage: tuple[float, float, float, float]
```

Es gilt dieselbe strikte Zahlenregel wie fuer S.

### Rezeptorprovenienz R

```text
receptor_contact:
  tuple[float, float, float, float]
  oder
  tuple[None, None, None, None]
```

Zulaessig sind nur zwei vollstaendige Formen:

1. vier endliche reelle Kontaktwerte;
2. vier `None`-Marker fuer vollstaendige Kontaktabwesenheit.

Gemischte Formen wie `(None, 0.0, None, 0.0)`, Boolwerte,
nichtendliche Zahlen oder eine andere Vektorlaenge sind ungueltig.

## Eng gebundene reale Nullabilitaetslage

Fuer das feste S1-SS-Artefakt ist die all-null-Form ausschliesslich hier
zulaessig:

```text
plan_role       = C_GAP
checkpoint_role = POST_COMPETITION
Modellrollen    = alle 14 registrierten Rollen
Anzahl Records  = exakt 14
```

An jedem anderen der 560 Checkpoints muss R aus vier endlichen Zahlen
bestehen. Eine zusaetzliche oder fehlende nullable Lage stoppt fail-closed.

Die 14 R-Vektoren muessen am gebundenen Checkpoint untereinander exakt
gleich sein. Es findet keine numerische Distanzbildung ueber R statt.

## Unveraenderte Comparatorarithmetik

Das numerische Profil bleibt exakt:

```text
40 Checkpoints x (S mit 4 Werten + H mit 4 Werten) = 320 Komponenten
```

R ist ausschliesslich Provenienz und gehoert weder zu den 320 Komponenten
noch zu Kontrast-, `Linf`-, Skalierungs- oder relativen Distanzoperationen.

Unveraendert bleiben:

```text
322 Rohkontraste
91 Profilpaare
absolute_control_tolerance = 1e-12
profile_equivalence_limit  = 0.05
links-minus-rechts-Residualregel
```

`None` darf niemals als `0.0` numerisiert, imputiert oder aus dem Profil
entfernt werden. Dadurch bleiben Abwesenheit und expliziter Nullkontakt
unterscheidbar.

## Kanonische Serialisierung

Im neuen Atlasartefakt gilt:

- endliche R-Zahlen werden als kanonische JSON-Zahlen serialisiert;
- R-Abwesenheit wird komponentenweise als JSON-`null` erhalten;
- S und H duerfen niemals `null` enthalten;
- Parser und typisierte Rekonstruktion muessen die beiden R-Formen
  unterscheiden;
- Profil- und Quelldigests binden die unveraenderte R-Darstellung mit;
- Roundtrip muss bytegleich sein.

## Methodischer Mini-DIO- und Biocomputing-Abgleich

Aus MINI_DIO wird keine Variable oder Mechanik uebernommen. Der relevante
methodische Punkt bleibt, Architektur- und Encodingursachen getrennt von
Feldgeschichte zu kontrollieren.

Der Biocomputing-Abgleich fuegt ebenfalls keine biologische Annahme hinzu.
Er bestaetigt nur die Schnittstellenpflicht: Ein Encoder darf
`Kontaktabwesenheit` und `gemessenen Nullkontakt` nicht auf denselben Zustand
reduzieren. Damit ist kein neuer Forschungszweig und keine Aenderung des
MCM-Wahrnehmungsfeldes begruendet.

## Dauerhafte S1-TB-Sperre

Diese Belege bleiben bytegleich und dauerhaft erhalten:

```text
reports/s1tb_baseline_reference_atlas_once_v1.attempt.json
  sha256 = e746f02cb0cfaa219a59ae2a1d7a8768925a52710ba0316aacd8bddd7eb795e5
reports/s1tb_baseline_reference_atlas_once_v1.lock
  sha256 = 42a66cbd8e32bfba04655617cb56f53220029f155a7b320c57239261b409600e
```

S1-TB wird nicht wiederholt. Der alte Ergebnis- und Stagingpfad bleiben
unbenutzt.

## Getrennte Neulaufidentitaet

Ein spaeterer korrigierter Einmallauf erhaelt vollstaendig neue Provenienz:

```text
schema_id       = mcm.s1tc.baseline-reference-atlas-artifact.v2
source_contract = S1-TC
execution_id    = mcm.s1tg.baseline-reference-atlas.once.v2
authorization   = S1-TG_REAL_BASELINE_REFERENCE_ATLAS_ONCE_V2
authorization_sha256
  4b26b9c6cf66b18946dab58fb674889c7fa89fc1909144731378c3884d52b062
```

Neue feste Pfade:

```text
reports/s1tg_baseline_reference_atlas_once_v2.json
reports/s1tg_baseline_reference_atlas_once_v2.attempt.json
reports/s1tg_baseline_reference_atlas_once_v2.lock
reports/.s1tg_baseline_reference_atlas_once_v2.json.staging
```

Die S1-TB-Pfade werden weder als Eingabe noch als Laufsteuerung verwendet.
Ihre Belegdateien bleiben nur historische Ausfuehrungsprovenienz.

## Implementierungs- und Testgrenze fuer S1-TD

S1-TD darf ausschliesslich bearbeiten:

```text
mcm_field_organism/four_node_baseline_reference_comparator.py
mcm_field_organism/four_node_baseline_reference_input.py
mcm_field_organism/four_node_baseline_reference_artifact.py
mcm_field_organism/four_node_baseline_reference_single_run.py
tests/test_four_node_baseline_reference_artifact_and_single_run.py
```

Historische S1-SS-Produktionsmodule und beide S1-TB-Belege bleiben
unveraendert.

Der bestehende synthetische Katalog darf auf hoechstens 20 Tests angepasst,
aber in S1-TD nicht ausgefuehrt werden. Er muss mindestens pruefen:

- rein numerisches R bleibt gueltig;
- exakt all-null R ist nur an der gebundenen C-Gap-Lage gueltig;
- gemischtes R wird abgewiesen;
- zusaetzliches all-null R wird abgewiesen;
- `None` in S oder H wird abgewiesen;
- Kontaktabwesenheit und expliziter Nullkontakt bleiben verschieden;
- JSON-`null` uebersteht den kanonischen Roundtrip;
- neue Schema-, Autorisierungs- und Pfadidentitaet gilt;
- vorhandene S1-TB-Belege blockieren den neuen S1-TG-Pfad nicht und werden
  nicht veraendert;
- gestarteter S1-TG-Fehler bleibt erneut fail-closed.

Kein Test darf das reale S1-SS-Artefakt numerisch vergleichen oder einen
Modellproducer aufrufen.

## Entscheidung und naechster Schritt

```text
NULLABLE_RECEPTOR_PROVENANCE_CONTRACT_BOUND
S_H_NUMERICAL_PROFILE_AND_COMPARATOR_METRICS_UNCHANGED
S1_TB_PROVENANCE_PERMANENTLY_PRESERVED
DISTINCT_V2_ONE_SHOT_IDENTITY_AND_PATHS_BOUND
NO_CODE_NO_TEST_NO_COMPARATOR_NO_RUN
```

Der einzige naechste Schritt ist S1-TD fuer die eng begrenzte
Implementierung und Anpassung von hoechstens 20 noch nicht ausgefuehrten
synthetischen Tests. Eine reale Auswertung bleibt bis nach separater
Testabnahme und neuem statischem Preflight gesperrt.
