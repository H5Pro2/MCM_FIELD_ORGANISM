# S1-TM: Statischer Implementierungs-, Mutations- und Testbudgetvertrag der Kandidatenhuelle

## Status und Umfang

S1-TM bindet den spaeteren reinen Strukturcode fuer die in S1-TJ bis S1-TL
festgelegte Kandidaten-Beobachtungshuelle.

Festgelegt werden:

- genau zwei neue Dateien;
- oeffentliche Typ- und Funktionsoberflaeche;
- Registry-, Status- und Resultatrollen;
- kanonische Bytes- und Digestregeln;
- geordnete Validierungsphasen und Fehlerprioritaet;
- isolierte synthetische Mutationen;
- genau 24 noch nicht ausgefuehrte Testmethoden.

S1-TM implementiert nichts und fuehrt keinen Test aus. Kandidatenanatomie,
Producer, Runtime, Comparatoranschluss und Feldlauf bleiben gesperrt.

## Vertragsentscheidung

```text
S1_TM_CANDIDATE_ENVELOPE_IMPLEMENTATION_AND_TEST_BUDGET_BOUND
TWO_NEW_FILES_AND_TWENTY_FOUR_SYNTHETIC_TEST_METHODS_ONLY
STRUCTURAL_VALIDATION_WITHOUT_CANDIDATE_OR_MODEL_EXECUTION
NO_IMPLEMENTATION_NO_TEST_EXECUTION_NO_FIELD_RUN
```

## Gebundene Dateigrenze

Ein spaeterer S1-TN-Schritt darf genau zwei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/four_node_candidate_observation_envelope.py` | abhaengigkeitsarme unveraenderliche Records, Registry, kanonischer Bytesparser und reiner Strukturvalidator |
| `tests/test_four_node_candidate_observation_envelope.py` | synthetische Positivhuelle, isolierte Mutationen und exakt 24 Testmethoden |

Alle bestehenden Produktions-, Test-, Dokument- und Artefaktdateien bleiben
waehrend S1-TN unveraendert. Insbesondere gesperrt sind:

- `mcm_field_organism/__init__.py` und `root_lazy_exports.py`;
- Feldkern, Zell- und Matrixlebenszyklus;
- Fixture, Manifest, Registrierung und Frischfabrik;
- Modellinvocation und alle Modellproducer;
- Baselinecomparator, Atlasartefakt und Einmalrunner;
- KFS-1-, DTS-1-, G2/D3- und weitere geschlossene Kandidatenmodule;
- alle vorhandenen Tests und Reports.

Nach der statischen S1-TN-Abnahme duerfen nur die aktuellen Einstiegsdokumente
um den Implementierungsstand ergaenzt werden. Die 24 Tests bleiben bis zu
einem getrennten S1-TO-Einmallauf unausgefuehrt.

## Eingefrorene Herkunftsbelege

Vor und nach S1-TN muessen diese Dateien byteidentisch bleiben:

```text
reports/s1tg_baseline_reference_atlas_once_v2.json
  b8df5c0cb010169432b93b1af42b3e5720edc8299060a994298e996bfcbefe3a
four_node_cell_lifecycle.py
  d2d0649c3505de6d70ac0d1f5e99f24454700df0262cc89dfe7215cf9e2d99b0
four_node_baseline_reference_comparator.py
  10b3c92b35e6199e4c7e4dce2a83f67aa4da6ab67050e174accdaf853232430d
four_node_exposure_fixture.py
  d3a470818fd8afbcaf1765649a5b8c24e3c3de14fd0c71c7fb0456d635a372b4
four_node_matrix_artifact.py
  b8ca95abf3723317c0d6f68f26e0df174d26f8f2a02ee6af20d371864842fb43
kfs1_schema_validator.py
  c0355f6b98f129f2ce3743a409850b2d777f1c4b6ecc02d0971c2a523843162e
```

Die Belege sind Herkunfts- und Driftgrenzen, keine erlaubten Imports.

## Vertrags- und Schemaidentitaet

Das neue Modul bindet:

```text
CONTRACT_ID
  mcm.s1tm.candidate-observation-envelope-implementation.v1
CONTRACT_DIGEST
  ffc178618cf873f617d4d8238d6310a0994ef77572d51b8050e8f20ad5987ee4
SCHEMA_ID
  mcm.s1tk.candidate-observation-envelope.v1
VALIDATION_SCHEMA_ID
  mcm.s1tm.candidate-observation-envelope-validation.v1
SOURCE_CONTRACT_ID
  S1-TK
CANONICALIZATION_ID
  compact-json-ascii-sort-keys-no-nan-sha256-v1
VALID_STATUS
  CANDIDATE_ENVELOPE_STRUCTURALLY_VALID
INVALID_STATUS
  AUDIT_INVALID_NOT_COMPUTABLE
```

Der Vertragsdigest ist SHA-256 der ASCII-Bytes von `CONTRACT_ID`.

Die Registry bindet ausserdem nur als Identitaeten, nicht als geladene
Artefakte:

```text
S1-TG file SHA-256
  b8df5c0cb010169432b93b1af42b3e5720edc8299060a994298e996bfcbefe3a
S1-TG artifact digest
  b63c12967fbab69740341af2f011839652762efcd71c8b29c851511ce0c20a9f
S1-TG result digest
  dd38f95829e04934ffd678956d52e380729042fe5d7710e99d672a92885b3a56
exposure fixture digest
  ca66f3a673eaca663a0973f7e956a90f4788e6f51963b71de4952801936bac3e
axis digest
  124ee8e19a9e3ce35816ff65370f6775131b0be413c7a2816b01605cf3d03cfd
```

## Importgrenze

Das Produktionsmodul darf ausschliesslich importieren:

```text
dataclasses
hashlib
json
math
re
collections.abc
typing
```

Es darf keinen relativen oder absoluten Import aus
`mcm_field_organism` besitzen. Ein AST-Test muss diese Grenze pruefen.

Das Modul liest keine Dateien, Umgebungsvariablen oder Uhrzeit und besitzt
keine Netzwerk-, Thread-, Prozess- oder Geraeteoberflaeche.

## Oeffentliche Typoberflaeche

Alle Recordtypen sind `@dataclass(frozen=True, slots=True)`. `__all__` darf
neben den gebundenen Konstanten und zwei Funktionen genau folgende Typen
enthalten:

```text
CandidateEnvelopeValidationRegistry
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

Die fachlichen Felder, Kardinalitaeten und Referenzen entsprechen exakt
S1-TK. Kein Typ besitzt eine Fortschreibungs-, Builder-, Runner-, Callback-
oder Dateimethode.

## Genau zwei oeffentliche Funktionen

```text
build_candidate_envelope_validation_registry()
    -> CandidateEnvelopeValidationRegistry

validate_candidate_observation_envelope(
    raw_bytes: bytes,
    registry: CandidateEnvelopeValidationRegistry,
) -> CandidateEnvelopeValidationResult
```

Die Registryfabrik ist parameterlos und liefert immer dieselbe
unveraenderliche Registry. Der Validator verlangt exakten `bytes`-Typ und
eine strukturell exakt gleiche Registry. Falsche API-Typen loesen vor einem
Resultat `TypeError` aus.

Es gibt keine oeffentliche Parse-, Digest-, Serialize-, Repair-, Builder-
oder Teilvalidierungsfunktion. Private Parser duerfen nur innerhalb des
einzigen Validatoraufrufs verwendet werden.

## Validierungsresultat

`CandidateEnvelopeValidationResult` enthaelt exakt:

```text
status
envelope_or_none
failure_code_or_none
input_bytes_digest
registry_digest
result_digest
```

Bei `CANDIDATE_ENVELOPE_STRUCTURALLY_VALID` gilt:

- `envelope_or_none` ist die vollstaendig typisierte Huelle;
- `failure_code_or_none` ist `None`;
- alle Record- und Huellendigests sind reproduziert;
- das Resultat trifft keine Funktionsentscheidung.

Bei `AUDIT_INVALID_NOT_COMPUTABLE` gilt:

- `envelope_or_none` ist `None`;
- `failure_code_or_none` ist genau der erste priorisierte Fehlercode;
- es werden keine Teilrecords, Teilachsen oder Teilkontraste publiziert;
- `result_digest` bindet nur Status, Fehlercode, Eingabebytes- und
  Registrydigest.

## Kanonische Bytesgrenze

Der Validator muss vor jeder fachlichen Pruefung:

1. exakten Bytestyp verlangen;
2. UTF-8/ASCII-kompatibles JSON mit Duplicate-Key-Erkennung lesen;
3. nur JSON-Primitive, Listen und String-Key-Objekte zulassen;
4. nichtendliche Zahlen und negative Null verwerfen;
5. die Bytes als kompaktes JSON mit sortierten Schluesseln,
   `ensure_ascii=True`, `allow_nan=False` und ohne abschliessenden
   Zeilenumbruch neu bilden;
6. Bytegleichheit mit der Eingabe verlangen.

Jeder Recorddigest ist SHA-256 seines kanonischen Nutzpayloads ohne eigenes
Digestfeld. `result_digest` folgt derselben Regel.

## Registryachsen

Die Registry bindet unveraenderlich:

- 17 Planrollen in S1-TK-Reihenfolge;
- die daraus deterministisch gebildete 40-Checkpoint-Achse;
- 127 Intervallordinale;
- 17 `POST_PROBE_READOUT`-Ablationspositionen;
- Knotenordnung `node-a` bis `node-d`;
- R-Nullabilitaet nur an `C_GAP/POST_COMPETITION`;
- S1-TK-Wurzelfamilien und Recordfamilien;
- alle 32 Fehlercodes in Prioritaetsreihenfolge;
- verbotene Informationsrollen und Kontrollquellen;
- Atlas-, Fixture- und Achsenidentitaeten.

Der Registrydigest wird ueber alle Nutzfelder ohne eigenes Digestfeld
gebildet. Der Validator akzeptiert keine abweichend konstruierte Registry.

## Geordnete Validierungsphasen

```text
01 byte_intake
02 canonical_form
03 root_schema
04 envelope_identity
05 plan_axis
06 field_checkpoint_axis
07 field_vectors_and_profile
08 state_checkpoint_chain
09 transition_chain
10 balance_schema_and_checkpoints
11 transition_balances
12 ablation_controls
13 disabled_and_reference_null_paths
14 release_link
15 reuse_link
16 information_barriers
17 envelope_completion
18 validation_result
```

Der erste Fehler stoppt alle spaeteren Phasen. Der Validator sammelt keine
Mehrfachfehler und repariert keine Digests oder Referenzen.

## Fehlerprioritaet

Die 32 S1-TK-Codes bleiben in genau dieser Reihenfolge:

```text
01 ENVELOPE_CANONICAL_FORM_INVALID
02 ENVELOPE_ROOT_SCHEMA_INVALID
03 ENVELOPE_IDENTITY_INVALID
04 CANDIDATE_CONFIGURATION_IDENTITY_INVALID
05 ATLAS_REFERENCE_INVALID
06 EXPOSURE_REFERENCE_INVALID
07 PLAN_AXIS_INVALID
08 CHECKPOINT_AXIS_INVALID
09 FIELD_VECTOR_INVALID
10 RECEPTOR_NULLABILITY_INVALID
11 FIELD_PROFILE_DIGEST_INVALID
12 STATE_CHECKPOINT_COUNT_INVALID
13 STATE_CARRY_CHAIN_INVALID
14 TRANSITION_COUNT_INVALID
15 TRANSITION_CAUSAL_SOURCE_INVALID
16 BALANCE_SCHEMA_INVALID
17 BALANCE_CHECKPOINT_COUNT_INVALID
18 BALANCE_TRANSITION_COUNT_INVALID
19 BALANCE_RECORD_INVALID
20 ABLATION_COUNT_INVALID
21 ABLATION_PRECONDITION_MISMATCH
22 ABLATION_SCOPE_INVALID
23 NULL_PATH_CARDINALITY_INVALID
24 NULL_PATH_REFERENCE_INVALID
25 NULL_PATH_MISMATCH
26 NULL_PATH_CANDIDATE_STATE_LEAK
27 RELEASE_LINK_INVALID
28 REUSE_LINK_WITHOUT_RELEASE
29 REUSE_LINK_INVALID
30 INFORMATION_BARRIER_VIOLATION
31 ENVELOPE_COMPLETION_INVALID
32 PARTIAL_RESULT_FORBIDDEN
```

## Synthetische Positivhuelle

Die Testdatei baut ausschliesslich im Testprozess eine vollstaendige kleine
Zahlenbelegung der vollstaendigen S1-TK-Struktur. Sie verwendet:

- alle 17 Plaene, 40 Checkpoints und 127 Intervalle;
- eine synthetisch deklarierte generische Bilanzrollenachse ohne Bezug zu
  einer realen Kandidatenanatomie;
- endliche neutrale Zahlenwerte;
- 17 synthetische Readoutablationen;
- zwei bitgleiche synthetische Nullvollpfade;
- strukturell gueltige R- und U-Links;
- nur erfundene kleingeschriebene SHA-256-Identitaeten, ausser den fest
  gebundenen Registryreferenzen.

Die Positivhuelle ruft keinen Feld-, Modell-, Fixture- oder Atlascode auf.
Ihre Gueltigkeit ist nur Schemaevidenz.

## Isolierte Fehlermutationen

Die Tests muessen mindestens je eine Mutation fuer alle 32 Fehlercodes
enthalten. Jede Mutation rekonstruiert alle abhaengigen Digests, ausser wenn
genau ein Digest- oder kanonischer Bytesfehler geprueft wird.

Gebundene Mutationsgruppen:

| Gruppe | Isolierte Mutation |
|---|---|
| Bytes | nichtkompakte oder Duplicate-Key-Serialisierung |
| Root | Wurzelfamilie fehlt oder ist unbekannt |
| Identitaet | Schema-/Vertrags-/Kandidatenidentitaet geaendert |
| Konfiguration | planweise Konfigurationsreferenz abweichend |
| Atlas | gebundene Atlasidentitaet geaendert |
| Exposition | Fixture- oder Achsenidentitaet geaendert |
| Plaene | Plan fehlt, doppelt oder umgeordnet |
| Checkpoints | Checkpoint fehlt, doppelt oder umgeordnet |
| Feldvektor | falsche Laenge, nichtendlicher Wert oder falsche Knotenordnung |
| R-Nullabilitaet | gemischte oder unzulaessige nullable R-Lage |
| Profil | Profil- oder Checkpointdigest geaendert |
| Zustandsanzahl | nicht 40 Zustandsrecords |
| Carry | gebrochene Zustands-, Carry- oder Ereigniskette |
| Uebergangsanzahl | nicht 127 Uebergangsrecords |
| Kausalquelle | Comparator, Reset, Recovery oder Sidecar als Hauptquelle |
| Bilanzschema | Rollenachse fehlt, doppelt oder driftet |
| Bilanzcheckpoints | nicht 40 Bilanzrecords |
| Intervallbilanzen | nicht 127 Intervallbilanzrecords |
| Bilanzrecord | nichtendlich, ungebucht oder referenzinkonsistent |
| Ablationsanzahl | nicht 17 Ablationsrecords |
| Ablationspraekondition | Geschichte, Vorzustand, Probe oder S/H weicht ab |
| Ablationsumfang | mehr als die einzelne Readoutrueckwirkung deaktiviert |
| Nullpfadanzahl | Pfad-, Plan-, Checkpoint- oder Paaranzahl weicht ab |
| Nullpfadreferenz | Checkpointpositionen oder Feldkernreferenz falsch verbunden |
| Nullpfadwert | ein positionsgleicher Feldwert unterscheidet sich |
| Nullzustand | Kandidatenzustand oder -carry im deaktivierten Pfad vorhanden |
| R-Link | R-Referenz, Bilanz oder Ausschlussbeleg unvollstaendig |
| U ohne R | U-Link referenziert keinen gueltigen R-Link |
| U-Link | Frischkontrolle, Beanspruchung oder Rollenidentitaet falsch |
| Informationssperre | erlaubtes Metadatenfeld nennt Baselinewert, Ergebnis oder Zukunftszustand |
| Abschluss | Abschlussstatus, Familien- oder Huellendigest falsch |
| Teilresultat | Completion markiert oder traegt ein Teilresultat |

Jede Mutation muss exakt den zugeordneten ersten Code liefern und
`envelope_or_none = None` erhalten.

## Genau 24 Testmethoden

Die Testdatei bindet exakt:

1. Vertrags-, Schema-, Status- und Atlasidentitaeten;
2. parameterlose Registryfabrik und reproduzierbaren Registrydigest;
3. exaktes `__all__` und genau zwei oeffentliche Funktionen;
4. ausschliessliche Standardbibliotheksimports per AST;
5. alle oeffentlichen Records als frozen/slots-Dataclasses;
6. kanonische Positivbytes und vollstaendig typisierte Positivhuelle;
7. 17/40/127-Achsen und 320-Komponenten-Profil;
8. exakte R-Nullabilitaetslage;
9. 40 Zustands- und 127 Uebergangsreferenzen;
10. 40 Bilanz- und 127 Intervallbilanzreferenzen;
11. 17 vollstaendige Ablationsrecords;
12. beide Nullvollpfade und 40 Paarbelege;
13. R-Link und U-nach-R-Referenzrichtung;
14. reproduzierbare Record-, Huellen- und Resultatdigests;
15. Bytes-, Root- und Identitaetsmutationen;
16. Plan-, Checkpoint-, Feldvektor- und R-Mutationen;
17. Profil-, Zustand-, Carry- und Uebergangsmutationen;
18. Kausalquellen- und Bilanzschemamutationen;
19. Bilanzanzahl- und Bilanzrecordmutationen;
20. Ablationsanzahl-, Praekonditions- und Umfangsmutationen;
21. Nullpfadanzahl-, Referenz-, Wert- und Zustandsmutationen;
22. R-, U- und Informationsbarrierenmutationen;
23. Abschluss-, Teilresultat- und erste-Fehler-Prioritaetspruefung;
24. falsche API-Typen sowie Abwesenheit von Datei-, Producer-, Builder-,
    Parse-, Repair-, Runner- und Comparatoroberflaechen.

Subtests pruefen die 32 Einzelmutationen, ohne die Zahl der Testmethoden zu
erhoehen.

## S1-TN-Implementierungsgrenze

S1-TN darf:

- genau die zwei neuen Dateien anlegen;
- alle gebundenen Records, Registry und den reinen Validator implementieren;
- exakt 24 synthetische Testmethoden definieren;
- Syntax, AST-Importgrenze, Testmethodenzahl und Digests der eingefrorenen
  Herkunftsbelege statisch pruefen.

S1-TN darf nicht:

- die 24 Tests ausfuehren;
- einen vorhandenen Test starten;
- ein reales Artefakt parsen oder numerisch auswerten;
- Kandidaten-, Baseline-, Fixture- oder Feldcode importieren;
- einen Producer, Serializer, Runner oder Comparator anlegen;
- Root- oder aktive API-Exports aendern;
- Kandidatenanatomie, Bilanzgleichung, Schwellen oder Funktionsstatus binden.

## Abbruchbedingungen

S1-TN stoppt vor jeder Testausfuehrung, wenn:

- eine eingefrorene Herkunftsdatei driftet;
- mehr als zwei Dateien fuer den Strukturcode erforderlich erscheinen;
- ein Projektmodulimport notwendig wird;
- ein Fehler nicht auf genau einen priorisierten Code isolierbar ist;
- eine oeffentliche Builder-, Datei-, Runner- oder Comparatorfunktion
  erforderlich erscheint;
- Kandidatenrollen, Gleichung, Parameter oder Schwellen benoetigt werden;
- ein Test reale Reports, Feld- oder Modellproducer lesen muesste.

## Aussagegrenze und naechster Schritt

S1-TM autorisiert noch keine Implementierung. Der Vertrag zeigt nur, dass
eine enge technische Umsetzung mit isolierter synthetischer Abnahme
vorbereitbar ist. Daraus folgt kein Kandidaten- oder Memory-Befund.

Der einzige naechste Schritt ist S1-TN fuer die genau gebundene
Implementierung und Definition der 24 noch nicht ausgefuehrten synthetischen
Tests. Nach bestandener statischer S1-TN-Abnahme waere ausschliesslich S1-TO
fuer genau einen unveraenderten Lauf dieser einen Testdatei zulaessig.
