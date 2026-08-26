# S1-TL: Statischer Nichtduplizierungs-, Informationsfluss- und Implementierungsreifeaudit der Kandidatenhuelle

## Auftrag und Grenze

S1-TL prueft den vorhandenen Python-Bestand gegen den S1-TK-Schemavertrag.
Der Audit entscheidet nur:

- welche vorhandenen Formen fachlich wiederverwendbar sind;
- welche konkreten Klassen oder Module nicht importiert werden duerfen;
- welche neutralen Recordtypen neu erforderlich sind;
- ob ein rein struktureller Validator ohne Kandidatenmechanik
  implementierbar ist.

Es wurde keine Datei importiert oder ausgefuehrt, kein Test gestartet und
kein Code veraendert. Kandidatenanatomie, Gleichung, Parameter und Lauf
bleiben gesperrt.

## Gepruefter Quellbestand

```text
four_node_cell_lifecycle.py
  d2d0649c3505de6d70ac0d1f5e99f24454700df0262cc89dfe7215cf9e2d99b0
four_node_baseline_reference_comparator.py
  10b3c92b35e6199e4c7e4dce2a83f67aa4da6ab67050e174accdaf853232430d
four_node_exposure_fixture.py
  d3a470818fd8afbcaf1765649a5b8c24e3c3de14fd0c71c7fb0456d635a372b4
four_node_matrix_artifact.py
  b8ca95abf3723317c0d6f68f26e0df174d26f8f2a02ee6af20d371864842fb43
four_node_model_invocation.py
  c1bf5b6287ae6e075294c8c3622d117be77b527429c74962384019eff2488083
four_node_fresh_manifest.py
  780c7475d2fa52cafa7da988df6f32331b9bbca99f3ca5aa3c6df04875e45220
four_node_fresh_matrix_registration.py
  39cc053c876968c1909acc3c188b30fbb9b8e50b38ed40287135a1138d30d0b1
root_lazy_exports.py
  ff6689dfebbe8ba415753c7d509175322229a0c48d8d2670c2f6ec3257bfa016
```

Zusaetzlich wurde der allgemeiner benannte
`kfs1_schema_validator.py` statisch auf Eignung geprueft.

## Wiederverwendbare fachliche Formen

Folgende bereits abgenommene Formen werden unveraendert als Vertragsquelle
uebernommen:

| Bestehender Bestand | Wiederverwendbare Form |
|---|---|
| `FourNodeCheckpointRecord` | Feld-, Carry-, Konfigurations-, Ereignisketten-, Align- und Vektoroberflaeche |
| `FourNodeExposureFixture` | 17 Planrollen, 127 Intervalle, 17 Aligns und 40 Checkpoints |
| Baselinecheckpoint und -profil | geordnete R/S/H-Vektoren, 40 Checkpoints und 320 signed S/H-Komponenten |
| Matrixartefakt | strikte Schluesselmenge, Duplicate-Key-Stopp, atomare kanonische Bytes und Digestpruefung |
| Manifest und Registrierung | getrennte Identitaetsrollen, exakte Achsen und fail-closed Cross-Identity-Pruefung |
| S1-TG-Comparator | endliche Vektoren, feste Achsen, vollstaendige Profile und passiver Vergleich ohne Modellaufruf |

Wiederverwendung bedeutet hier Form- und Invariantenuebernahme. Sie bedeutet
nicht automatisch Python-Import oder Typidentitaet.

## Nicht direkt importierbare Klassen

### Lebenszyklusrecords

`FourNodeCheckpointRecord` besitzt die passende oeffentliche Feldform, liegt
aber in `four_node_cell_lifecycle.py`. Dieses Modul importiert Fixture,
Frischfabrik, Modellinput, Modellinvocation und Feldklassen. Ein neutraler
Validator wuerde durch den Klassenimport die Producer- und Runtimekette
laden.

Entscheidung:

```text
FORM_REUSABLE
DIRECT_TYPE_IMPORT_FORBIDDEN
```

Die Kandidatenhuelle benoetigt einen eigenen unveraenderlichen
Feldcheckpointtyp mit denselben oeffentlichen Rollen plus eigener
S1-TK-Identitaet.

### Baselinecheckpoint und Comparator

`FourNodeBaselineCheckpointVector` und
`FourNodeBaselineModelProfile` sind absichtlich Eigentum des fixierten
Baselinecomparators. Dieser akzeptiert exakt 14 Rollen und setzt
`S1PX_CANDIDATE_GATES_NOT_APPLICABLE`.

Entscheidung:

```text
FIELD_AXIS_AND_VECTOR_FORM_REUSABLE
COMPARATOR_TYPE_IMPORT_FORBIDDEN
```

Der Kandidatenvalidator darf weder den Comparator importieren noch dessen
14-Rollen-Eingabetyp erweitern.

### Fixturetypen

`FourNodeExposureFixture` bindet die korrekte 17/127/17/40-Achse, ist aber
ein Fixturegenerator mit Registrierungs-, Zeit-, Rezeptor- und
Distributionsabhaengigkeiten. S1-TJ sperrt Fixturegeneratoren fuer passive
Consumer.

Entscheidung:

```text
AXIS_VALUES_REUSABLE_AS_S1TK_CONSTANTS
FIXTURE_BUILD_OR_IMPORT_FORBIDDEN
```

Der neutrale Validator muss die in S1-TK bereits gebundene Achse als eigene
unveraenderliche Vertragskonstante fuehren.

### Matrixartefakthelfer

`canonical_json_bytes` in `four_node_matrix_artifact.py` implementiert die
passende kompakte ASCII-Kanonisierung. Sein Modul importiert jedoch
Zelllebenszyklus, Matrixlebenszyklus und Modellinvocation. Ein einzelner
Helferimport wuerde damit die gesperrte Ausfuehrungskette transitiv laden.

Entscheidung:

```text
CANONICALIZATION_RULE_REUSABLE
MATRIX_ARTIFACT_HELPER_IMPORT_FORBIDDEN
```

Eine kleine lokale Standardbibliotheksimplementierung derselben gebundenen
Regel ist hier sachlich notwendige Entkopplung und keine neue
Kanonisierungsvariante.

### KFS-1-Schemahelfer

`kfs1_schema_validator.py` ist zwar passiv und exportiert
`canonical_json_bytes` sowie `sha256_hex`, ist aber an die geschlossene
KFS-1-Anatomie mit festen `free/bound/blocked`-Rollen gebunden. Seine
Kanonisierung verwendet UTF-8 mit `ensure_ascii=False`; der S1-TG-Pfad ist
auf ASCII mit `ensure_ascii=True` gebunden.

Entscheidung:

```text
KFS1_VALIDATOR_NOT_MODEL_NEUTRAL
KFS1_CANONICALIZATION_NOT_BYTE_COMPATIBLE
DIRECT_REUSE_FORBIDDEN
```

KFS-1- oder G2/D3-Fehlerklassen und Ressourcenrollen duerfen nicht in die
neue Huelle uebernommen werden.

## Direkt zulaessige technische Primitive

Ein spaeteres neutrales Strukturmodul darf direkt nur verwenden:

```text
dataclasses
hashlib
json
math
re
typing / collections.abc fuer reine Typpruefung
```

Es darf keine Projektmodule importieren. Dadurch bleiben Modellproducer,
Feldruntime, Runner, Orchestrator, Comparator, Fixturegeneratoren,
geschlossene Kandidaten und Root-Lazy-Exports ausserhalb des Importgraphen.

## Neu erforderliche neutrale Typen

Die S1-TK-Familien benoetigen eigene `frozen=True, slots=True`-Records:

```text
CandidateEnvelopeIdentity
CandidatePlanRecord
CandidateFieldCheckpointRecord
CandidateFieldProfile
CandidateStateCheckpointRecord
CandidateTransitionRecord
CandidateBalanceCheckpointRecord
CandidateTransitionBalanceRecord
ReadoutAblationRecord
DisabledFullPathProfile
NullPathPairRecord
ReleaseLifecycleLink
ReuseLifecycleLink
EnvelopeCompletionRecord
CandidateObservationEnvelope
CandidateEnvelopeValidationResult
```

Diese Typen tragen nur bereits abgeschlossene Werte und Referenzen. Sie
duerfen keine Methode besitzen, die Feld, Kandidat oder Baseline
fortschreibt.

## Kanonisierungs- und Digestgrenze

Das neue Modul darf lokal genau eine private Kanonisierungsfunktion und eine
private SHA-256-Funktion besitzen. Gebunden bleibt:

```text
compact JSON
sortierte Schluessel
ASCII-Ausgabe
ensure_ascii = true
allow_nan = false
keine negative Null
keine unbekannten Pythonobjekte
SHA-256 ueber kanonische Bytes
```

Die Funktionen duerfen keine Dateien lesen, keine Laufzeitidentitaet
ermitteln und keine Quelleninventare bilden. Artefaktpublikation und
Filesystemprovenienz gehoeren nicht zum Strukturvalidator.

## Informationsfluss

```text
abgeschlossene Producerwerte
  -> CandidateObservationEnvelope
  -> reiner Strukturvalidator
  -> atomarer Validierungsstatus
```

Verboten sind Rueckkanten vom Validator zu:

- Kandidaten- oder Baselineproducer;
- Feldzustand oder Carryobjekt;
- Fixture oder Registrierungsbuilder;
- Comparator oder Atlasproducer;
- Parameter-, Retry-, Reparatur- oder Optimierungslogik.

Der Validator nimmt keine Dateipfade, Callbacks oder Modellobjekte entgegen.
Er erhaelt ausschliesslich die vollstaendige unveraenderliche Huelle.

## Implementierungsreife

Ein rein struktureller S1-TK-Validator ist ohne Kandidatenmechanik
implementierbar. Er kann bereits pruefen:

- exakte Recordtypen, Schluessel, Ordnungen und Kardinalitaeten;
- endliche Werte und R-Nullabilitaet;
- Digest- und Referenzkonsistenz;
- lueckenlose Plan-, Checkpoint-, Carry- und Ereignisketten;
- deklarierte Bilanzrollenachse und vollstaendige Buchungsrecords;
- 17 Ablationsrecords und ihre Identitaetsgleichheit;
- beide Nullvollpfade und bitgenaue Feldcheckpointgleichheit;
- R-vor-U-Referenzrichtung;
- erste Fehlerklasse ohne Teilresultat.

Ohne spaetere Kandidatenanatomie kann er bewusst nicht pruefen:

- fachliche Bedeutung deklarierter Ressourcenrollen;
- konkrete Erhaltungs- oder Dissipationsgleichung;
- zulaessigen numerischen Bilanzrest;
- Funktionsverlust-, Freigabe- oder Wiederverwendungsschwellen;
- Kandidatenwirkung oder Baselinereduktion.

Ein syntaktisch gueltiges abstraktes Testpaket waere deshalb nur
Schemaevidenz. Es waere keine Kandidatenzulassung.

## Dateigrenze einer spaeteren Umsetzung

Eine spaetere reine Strukturimplementierung kann auf genau zwei neue Dateien
begrenzt werden:

```text
mcm_field_organism/four_node_candidate_observation_envelope.py
tests/test_four_node_candidate_observation_envelope.py
```

Bestehende Module, Root-Exports, Feldkern, Atlas, Runner und Dokumentartefakte
muessen dabei unveraendert bleiben. Ein Root-Export ist fuer die private
Forschungsoberflaeche nicht erforderlich.

## Auditentscheidung

```text
S1_TL_STRUCTURAL_VALIDATOR_IMPLEMENTATION_READY
EXISTING_FORMS_REUSED_WITHOUT_RUNTIME_OR_COMPARATOR_IMPORTS
NEW_NEUTRAL_RECORD_TYPES_REQUIRED_IN_ONE_LOW_DEPENDENCY_MODULE
NO_CANDIDATE_SEMANTICS_NO_FUNCTION_DECISION
```

Es liegt kein methodischer Richtungswechsel vor. Die Implementierungsreife
gilt nur fuer Schema und Fail-Closed-Struktur.

## Naechster Schritt

Der einzige naechste Schritt ist S1-TM als statischer Implementierungs-,
Mutations- und Testbudgetvertrag fuer die zwei genannten neuen Dateien.
S1-TM muss genaue oeffentliche Typen, reine Funktionen, Fehlerprioritaet,
synthetische Positiv- und Negativgruppen sowie ein enges noch nicht
ausgefuehrtes Testbudget binden. Kandidatenanatomie, Producer, Runtime,
Comparatoranschluss, Testausfuehrung und Feldlauf bleiben gesperrt.
