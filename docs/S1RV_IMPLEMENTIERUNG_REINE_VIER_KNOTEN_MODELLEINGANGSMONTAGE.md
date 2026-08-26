# S1-RV: Implementierung der reinen Vier-Knoten-Modelleingangsmontage

## Status und Umfang

S1-RV implementiert innerhalb des S1-RU-Budgets die reine Montage eines
abgenommenen `FourNodeFreshBundle` zu einem
`FourNodeModelInputAssembly`. Kein Modellkern, Adapter, Intervall oder
Feldschritt wird aufgerufen.

```text
PURE_FOUR_NODE_MODEL_INPUT_ASSEMBLY_IMPLEMENTED
FOURTEEN_ROLE_SURFACE_IDS_BOUND
B3_B6_NATIVE_SUBSTRATE_FIELD_COPY_IMPLEMENTED
FIFTEEN_FOCUSED_TESTS_DEFINED_NOT_EXECUTED
NO_MODEL_KERNEL_NO_ADAPTER_NO_FIELD_ADVANCE
```

## Produktionsoberflaeche

Neu angelegt wurde:

```text
mcm_field_organism/four_node_model_input_assembly.py
```

Die einzige konstruktive Funktion lautet:

```text
assemble_four_node_model_input(bundle) -> FourNodeModelInputAssembly
```

Der unveraenderliche Ergebnisrecord bindet:

- Modellrolle und rollenfeste Adapteroberflaechenkennung;
- oeffentliches Frischfeld und montiertes Modellfeld;
- nativen Privatstatus oder explizite Zustandslosigkeit;
- Konfigurationsbindung und privaten Manifestdigest;
- getrennte registrierte und native Kanten- sowie Geometriedigestrollen;
- den Einbettungsmodus;
- einen kanonischen Assembly-Digest.

## Feldmontage

Fuer A0, A1, B1, B2, A3, M1, beide M2-Modi, M4 und M5 gilt
`PUBLIC_FIELD_IDENTITY`. Das montierte Modellfeld ist dasselbe unveraenderte
substrat- und entwicklungsfreie Feldobjekt aus dem Frischbundle.

Fuer B3-B6 gilt `NATIVE_SUBSTRATE_COPY`. `dataclasses.replace` erzeugt eine
neue `SharedMCMField`-Huelle und bettet ausschliesslich den bereits von der
Rollenfabrik erzeugten nativen `MCMSubstrateState` ein. Das oeffentliche
Frischfeld bleibt substratfrei. Layer, Knoten, Dock, Geometrie, Feldwerte,
Wahrnehmungen und Feldzeit werden nicht veraendert.

## Validierung und Fail-Closed-Verhalten

Die Montage validiert vor Ausgabe:

- die exakte Vier-Knoten-Feld-, Layer-, Geometrie-, Knoten- und Dockform;
- Nullwerte, Tick null, leere lokale Samples und fehlende letzte Verteilung;
- die exakten Stateless-Marker von A0/A1;
- den rollenrichtigen nativen Zustandstyp aller zwoelf privaten Rollen;
- die registrierten privaten Manifestdigests;
- `norm`/`leak`, DELAY/REPLAY und den fehlenden M4-Kandidatensidecar;
- die exklusive Substrateinbettung fuer B3-B6;
- die Identitaet der Feldhuelle vor und nach der Einbettung;
- den kanonischen Assembly-Digest.

Fehler werden als `FourNodeModelInputAssemblyError` mit technischer
Fehlerklasse ausgegeben. Es gibt keine Reparatur oder Ersatzrolle.

## Definierte Testoberflaeche

Neu angelegt wurde:

```text
tests/test_four_node_model_input_assembly.py
```

Die 15 Tests definieren Pruefungen fuer:

- alle 14 Rollen und 14 getrennte Oberflaechenkennungen;
- strikte Zustandslosigkeit von A0/A1;
- Feldidentitaet aller Nichtsubstratrollen;
- neue B3-B6-Feldhuellen mit nativer M-Einbettung;
- vollstaendige Feldidentitaeten vor und nach Einbettung;
- Privatobjekt-, Konfigurations- und Manifestdigesttreue;
- getrennte Kanten- und M2-Geometriedigestrollen;
- externe M4-Anatomie ohne Kandidatensidecar;
- deterministische Assembly-Digests und getrennte Frischobjektgraphen;
- Unveraenderlichkeit sowie Digest-, Rollen-, Manifest- und
  Fremdsubstratfehler;
- Abwesenheit von Modellkern-, historischem Adapter- und
  Orchestratorimport.

Diese Tests wurden in S1-RV nicht ausgefuehrt.

## Statische Pruefung

Beide neuen Python-Dateien wurden ausschliesslich per AST geparst:

```text
AST_OK mcm_field_organism/four_node_model_input_assembly.py
AST_OK tests/test_four_node_model_input_assembly.py
```

`git diff --check` meldete keinen Inhaltsfehler. Eine Quelltextsuche fand im
Produktionsmodul keinen Import eines neutralen Feldkerns, F3-Kerns,
DTS-1-Kerns, historischen privaten Baselineadapters oder alten
Ein-Replik-Orchestrators.

## Nicht implementiert oder ausgefuehrt

S1-RV enthaelt nicht:

- Modell- oder Baselineaufrufe;
- Verteilungen, Intervalle, Ereignisse, Profile oder Refinements;
- Carry- oder Ergebniszustandsmontage;
- Comparator, Matrixzelle oder Gesamtpaket;
- Feldentwicklung oder Feldlauf;
- Testausfuehrung;
- Befund zu einer hypothetischen MCM-Memory.

## Paketstatus

```text
S1RV_PURE_MODEL_INPUT_ASSEMBLY_IMPLEMENTED
FIFTEEN_FOCUSED_TESTS_AWAIT_EXECUTION
MODEL_ADAPTER_INVOCATION_NOT_PRESENT
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

```text
S1-RW - fokussierter unveraenderter Testlauf und technische Abnahme
        der Vier-Knoten-Modelleingangsmontage
```

S1-RW darf genau `tests/test_four_node_model_input_assembly.py` einmal
ausfuehren. Bei einem Fehler wird nur ein Fehlerrecord gebunden; keine
Korrektur im selben Schritt. Kein Modellkern, kein Adapter, kein Intervall,
keine Matrixzelle und kein Feldlauf.
