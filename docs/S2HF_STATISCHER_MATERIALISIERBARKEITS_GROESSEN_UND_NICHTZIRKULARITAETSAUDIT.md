# S2-HF: Statischer Materialisierbarkeits-, Groessen- und Nichtzirkularitaetsaudit

Status: `S2HF_BLOCKED_TWO_VALIDATION_BINDINGS`

## Grenze

S2-HF prueft ausschliesslich den statischen S2-HE-Vertrag. Es wurden keine
Projektmodule importiert, keine Funktionen oder Tests ausgefuehrt und keine
Speicher-, Rezeptor-, Kontext- oder Feldzustaende erzeugt. S2-HC bleibt
dauerhaft `NOT_EVALUABLE`.

Der Audit aendert weder S2-HE noch Produktivcode. Sein Ergebnis ist
fail-closed: Die Groessen- und Graphbindung ist tragfaehig, aber zwei fuer die
Offline-Validierung erforderliche Digests fehlen in den gebundenen kompakten
Feldmengen. Deshalb darf die Implementierung noch nicht beginnen.

## Auditquellen

Statisch abgeglichen wurden:

- `docs/S2HE_KOMPAKTE_AUFZEICHNUNGSPROJEKTIONEN_VERTRAG.md`;
- `reports/s2he-static-compact-projection-contract.json`;
- `docs/S2GR_OPERATION_REGISTRY.csv`;
- `tools/_s2gt_private_runner.py`;
- `tools/_s2gt_private_append_only_recorder.py`;
- `tools/_s2gt_private_result_verifier.py`;
- `tools/_s2fs_b4_tspm1_private_coordinator.py`;
- `tools/_s2gb_private_perceptual_context_bundle.py`;
- `tools/_s2gi_private_two_area_context_projection.py`;
- `tools/_s2gk_private_masked_visual_completion_evaluator.py`.

Die Groessenberechnung verwendete dieselbe kanonische Form wie der Recorder:
ASCII-JSON, sortierte Schluessel, Trenner `,` und `:`, `ensure_ascii = true`
und genau ein abschliessendes LF. Die unveraenderte Recorderhuelle sowie eine
maximal 96 Zeichen lange gueltige Lauf-Owner-ID wurden mitgerechnet.

## Kanonische Groessen

### Formation

Alle 52 Operationen sind gebunden:

- 36 APPENDED-Formen, Schritte 1 bis 9: je 2.697 Byte;
- 16 EVICTED-Formen, Schritte 10 bis 13: je 2.710 Byte;
- Maximum: 2.710 Byte;
- Reserve zu 4.095 Byte: 1.385 Byte.

Erfasste Operationen:

```text
h01: op-0003..op-0027, ungerade
h02: op-0029..op-0053, ungerade
h03: op-0055..op-0079, ungerade
h04: op-0081..op-0105, ungerade
```

Die Einzellisten stimmen mit dem S2-HE-Maschinenbeleg ueberein. Keine
Formation ueberschreitet die engere 3.200-Byte-Grenze.

### S2-GC

Alle vier Operationen sind gebunden:

| Operation | Form | Groesse |
| --- | --- | ---: |
| `op-0116` | stabile Vollform | 3.112 Byte |
| `op-0117` | stabile Vollform | 3.112 Byte |
| `op-0118` | stabile Vollform | 3.112 Byte |
| `op-0119` | `ABSENT_VALID` | 2.596 Byte |

Maximum: 3.112 Byte. Reserve zu 4.095 Byte: 983 Byte.

### S2-GI

Alle vier Operationen sind gebunden:

| Operation | Form | Groesse |
| --- | --- | ---: |
| `op-0120` | stabile Vollform | 2.977 Byte |
| `op-0121` | stabile Vollform | 2.977 Byte |
| `op-0122` | stabile Vollform | 2.977 Byte |
| `op-0123` | `ABSENT_VALID` | 2.509 Byte |

Maximum: 2.977 Byte. Reserve zu 4.095 Byte: 1.118 Byte.

### Groessenergebnis

Die in S2-HE genannten Maxima `2.710 / 3.112 / 2.977` sind fuer die dort
gebundenen Feldmengen und kanonischen Vollhuellen reproduziert. Alle 60
Vorkommen bleiben unter 3.200 Byte. Der Groessenteil des Audits ist bestanden.

Dieser Befund gilt jedoch nur fuer die aktuell gebundenen Feldmengen. Die zwei
unten genannten fehlenden Validierungsfelder duerfen nicht nachtraeglich ohne
erneute Groessenberechnung eingefuegt werden.

## Keine indirekte Vollobjekteinbettung

Die drei S2-HE-Projektionen enthalten keine der folgenden Vollobjekte:

- `B4TSPM1CompositeState` oder `B4TSPM1StepResult`;
- B4-Slotinhalte als vollstaendige Bank;
- TSPM-Fast-Slots oder PPB-1-Baenke;
- `B4TSPM1ReadOnlyFinding`;
- `PerceptualContextBundle` oder dessen vollstaendige Komponentenwerte;
- `TwoAreaContextBundle` oder dessen vollstaendige Komponentenwerte.

Formation bindet Nachzustaende ueber vorhandene Komponenten- und
Resultdigests. S2-GC bindet Werte ueber die bereits vollstaendig
aufgezeichnete `ContextReadOnlyReceipt`-Quelle. S2-GI bindet seine oeffentlichen
Bereiche ueber das unmittelbar vorausgehende S2-GC-Artefakt. Die vollstaendigen
Objekte bleiben ausschliesslich im funktionalen In-Memory-Pfad.

Kein Nachfolger darf einen Zustand oder Wertevektor aus einem Digest
rekonstruieren. Der Vollobjekttrennungsteil des Audits ist bestanden.

## Quellen- und Digestgraph

### Formation

```text
ExecutionPlan/Reservation
  -> Formation START
  -> ReceptorReceipt-Artefakt
  -> CompactCompositeFormationReceiptV1
  -> naechster Composite-Vorzustandsdigest
```

Der Recorderartefaktdigest entsteht erst nach vollstaendiger Projektion. Die
naechste Operation darf ihn und den semantischen Nachzustandsdigest nur lesen.

### Kontextprojektionen

```text
ContextReadOnlyReceipt
  -> CompactS2GCProjectionReceiptV1
  -> CompactS2GIProjectionReceiptV1
  -> ArmReceipt
  -> EvaluationRunBinding
  -> EvaluationReceipt
```

`projection_digest` wird jeweils ueber die Projektion ohne sich selbst
gebildet. Kein Ausfuehrungsartefakt bindet Evaluationsergebnisse als Eltern.
Alle neuen Kanten zeigen auf eine fruehere Operation. Die bestehenden
Operationen und Nachfolger bleiben eindeutig.

Owner, Reservation und START werden in der unveraenderten Recorderhuelle
gebunden. Die kompakte Projektion erhaelt zusaetzlich ihre semantischen Quellen.
Es wurde keine Selbstkante, Rueckkante oder Mehrdeutigkeit gefunden. Der
Nichtzirkularitaetsteil ist bestanden.

## Validator- und Auswertungsabgleich

### Auswertung

Der reine S2-GJ-Auswerter benoetigt weiterhin die Armresultate und die getrennt
gebundene Zielwertfixture. Er wertet keine Formation- oder Projektionsreceipts
als Funktionsobjekte aus. Die kompakten Belege erhalten die fuer die
Provenienz erforderlichen Rollen-, Status-, Werte-, Kandidaten-, Zustands- und
Bundledigestbindungen. Der Funktionsauswerter verliert dadurch kein benoetigtes
Eingabefeld.

### Offline-Verifikator

Der Verifikator muss ohne Projektfunktion mindestens folgende semantische
Digests nachrechnen koennen:

- Formation: Ressourcenledger, Owner-Nachzustand, Step-Receipt und
  Step-Result;
- S2-GC: Komponenten-, Kandidaten-, Rollen-, Sequenz-, Ledger- und
  Bundledigest;
- S2-GI: Bereichs-, Ledger- und Bundledigest.

Die direkten Elternartefakte liefern die nicht erneut gespeicherten Werte und
Quell-IDs. Zwei notwendige Digestrollen sind im S2-HE-Feldvertrag jedoch nicht
vorhanden.

## Blocker HF-B01

`CompactCompositeFormationReceiptV1` enthaelt nicht den separaten
`owner_prestate_digest` aus `B4TSPM1StepReceipt`.

Dieser Digest ist nicht identisch mit
`owner_authorized_digests[1]`. Letzterer ist der autorisierte
Composite-Vorzustandsdigest. `owner_prestate_digest` ist dagegen der Digest des
Ownerzustands vor dem Verbrauch.

Der Step-Receipt-Digest wird ueber folgende Rollen gebildet:

```text
config_digest
owner_prestate_digest
input_digest
composite_prestate_digest
b4_event
b4_slot_id
b4_poststate_digest
tspm_result_digest
tspm_receipt_digest
tspm_poststate_digest
resource_ledger_digest
composite_poststate_digest
```

Ohne `owner_prestate_digest` kann der Offline-Verifikator
`step_receipt_digest` nicht nachrechnen. Ein blosses Vertrauen in den bereits
eingetragenen Step-Receipt-Digest waere keine vollstaendige relationale
Validierung.

## Blocker HF-B02

`CompactS2GCProjectionReceiptV1` enthaelt den
`sequence_finding_digest`, aber nicht den zugrunde liegenden
`ValidatedB4ShortSequenceEvidence.evidence_digest`.

Der `B4ShortSequenceFinding` bindet:

```text
status
reference_digests
observed_b4_state_digest
source_evidence_digest
```

Der beobachtete B4-Zustandsdigest ist im direkten
`ContextReadOnlyReceipt` vorhanden. Der `source_evidence_digest` wird jedoch
erst fuer die S2-GC-Projektion gebildet und ist in keinem frueheren Artefakt
gespeichert. Ohne ihn kann der Offline-Verifikator den Sequence-Finding-Digest
nicht nachrechnen.

Eine Ableitung aus dem bekannten Status `NOT_REQUESTED` waere eine
nachtraegliche Rekonstruktion und widerspraeche dem S2-HE-Vertrag.

## Budget- und Fehleraudit

Die Registrygrenzen bleiben unveraendert. Daher bleiben auch die bereits
gebundenen Pfadmaxima unveraendert:

```text
MAX_SUCCESS_PATH_BYTES = 2.009.088
MAX_FAILURE_PATH_BYTES = 2.045.952
MAX_RUN_PATH_BYTES     = 2.045.952
```

Diese Werte sind die Summe der registrierten Einzelobergrenzen und
Eventobergrenzen, nicht der tatsaechlich kleineren Dateien. Erfolgspfad und
Fehlerpfad bleiben gegenseitig exklusiv.

Die drei Projektionen verwenden weiterhin dieselbe 4.096-Byte-Registryrolle.
Eine Groessenverletzung bleibt `E008`. Phasenunpassende registrierte Fehler
bleiben `E002`; unregistrierte und sonstige Ausnahmen bleiben `E009`. Es ist
keine Aenderung am Fehlerabschluss oder an den 140 Fehlerpfaden erforderlich.

Budgetaddition und Fehlercodewege sind bestanden.

## Korrekturraum ohne Freigabe

Der Audit implementiert oder bindet keine Korrektur. Er weist nur nach, dass
eine enge statische Folgeberichtigung moeglich ist:

- Formation benoetigt zusaetzlich `owner_prestate_digest`.
- S2-GC benoetigt den expliziten Sequence-Evidence-Digest. Eine kompakte
  positionsgebundene Digestform kann dabei den vorhandenen
  `sequence_finding_digest` einschliessen.
- Anschliessend sind alle 60 Huellengroessen erneut kanonisch zu berechnen.

Eine rein additive Referenzrechnung ergibt fuer Formation etwa 2.800 Byte.
Fuer S2-GC waere eine naive additive Form groesser als die interne
3.200-Byte-Grenze. Deshalb muss die Korrektur als Feldsubstitution und nicht als
ungeprueftes Anhaengen gebunden werden. Das ist Gegenstand eines separaten
Korrekturvertrags, nicht dieses Audits.

## Entscheidung

S2-HF ist in folgenden Teilen bestanden:

- 60 kanonische Groessenprojektionen;
- Maxima und Registryreserven;
- Ausschluss indirekter Vollobjekte;
- Quellen-, Owner-, Operations-, Eltern- und Nachfolgergraph;
- Zyklenfreiheit;
- Auswertungsversorgung;
- Budgets und Fehlercodewege.

S2-HF ist insgesamt **nicht bestanden**, weil HF-B01 und HF-B02 die
vollstaendige Offline-Validierung verhindern. Die Implementierung der
kompakten Projektionen bleibt gesperrt. Als naechster Schritt ist ausschliesslich
ein enger statischer Korrekturvertrag fuer diese zwei Bindungen zulaessig.
