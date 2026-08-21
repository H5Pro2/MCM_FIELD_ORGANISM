# S1-RY: Implementierung der gemeinsamen Vier-Knoten-Modellaufruf- und atomaren Ergebnisoberflaeche

## Status und Umfang

S1-RY implementiert die in S1-RX gebundene gemeinsame Aufrufhuelle, ohne
einen Test oder Modellkern auszufuehren.

```text
FOURTEEN_ROLE_ATOMIC_DISPATCH_IMPLEMENTED
FRESH_ASSEMBLY_AND_PRIOR_CARRY_INPUT_IMPLEMENTED
SYNC_TRANSIENT_GATES_IMPLEMENTED
COMPLETE_CARRY_OR_NOT_COMPUTABLE_IMPLEMENTED
ELEVEN_FOCUSED_TESTS_DEFINED_NOT_EXECUTED
```

## Produktionsoberflaeche

Neu angelegt wurde:

```text
mcm_field_organism/four_node_model_invocation.py
```

Die oeffentliche Funktion lautet:

```text
invoke_four_node_model(
    source,
    distribution,
    interval_input,
    refinement=None,
) -> FourNodeModelStepResult
```

`source` ist entweder ein technisch abgenommenes
`FourNodeModelInputAssembly` oder der vollstaendige
`FourNodeModelCarry` des unmittelbar vorherigen erfolgreichen Intervalls.

## Implementierte Rollenpfade

- A0 und A1 dispatchen auf ihre synchronen oder transienten Feldkerne;
- B1 baut aus dem Vier-Knoten-Festadapterzustand den nativen
  Kantenratenadapter und verwendet den vorhandenen exakten Feldschritt;
- B2 bildet S/H/L in den vorhandenen S2-Referenzkern ab und projiziert den
  vollstaendigen L-Folgezustand zurueck;
- B3-B6 verwenden den vorhandenen synchronen oder transienten F3-Kern mit
  ihrem rollenfesten Kopplungsrechner;
- A3, M1, beide M2-Modi und M5 kapseln ihre vorhandenen atomaren
  Replace-S-Kompositoren;
- M4 bildet seine drei Raten nach Feldnamen ab und kapselt den vorhandenen
  gekoppelten DTS-1/S/H-Schritt ohne T1-Laufzeittransition.

B1, B2 und M4 liefern bei transienter Eingabe vor jedem Kerndispatch
`NOT_COMPUTABLE`. F3-Rollen verlangen einen expliziten positiven
Refinementwert; alle anderen Rollen lehnen einen Refinementwert ab.

## Atomare Ausgabe

Ein erfolgreicher Aufruf liefert gemeinsam:

- vollstaendiges Folgefeld;
- rollenrichtigen vollstaendigen Privatfolgezustand oder Zustandslosigkeit;
- neuen Carry mit Feld-, Privat-, Konfigurations- und Digestrollen;
- native Receipt- oder Diagnostikidentitaet;
- exakt einen Feldzeitfortschritt;
- kanonischen Ergebnisdigest.

Bei jeder abgefangenen Kernausnahme werden Folgefeld, Privatfolgezustand und
Carry gemeinsam auf `None` gesetzt. Der Status lautet `NOT_COMPUTABLE`, der
Feldzeitfortschritt null. Ein Teilresultat wird nicht publiziert.

Bei B3-B6 referenziert der neue private Wrapper exakt
`result.field.substrate`. Es gibt keine zweite M-Fortschreibung. B1 traegt
denselben unveraenderten Festadapterzustand weiter. M4 traegt die
vollstaendige Folgeanatomie und dieselbe Ratenbindung ohne Sidecar weiter.

## Definierte Testoberflaeche

Neu angelegt wurde:

```text
tests/test_four_node_model_invocation.py
```

Elf Tests definieren:

- einen synchronen Aufruf fuer alle 14 Rollen;
- transiente Aufrufe fuer alle elf dafuer zugelassenen Rollen;
- die vorzeitige Sperre der drei synchron-only Rollen;
- lueckenlosen Carry in ein zweites Intervall;
- B3-M-Einfachidentitaet;
- B1-Zustandskonstanz und vollstaendigen B2-L-Zustand;
- M4-Folgeanatomie ohne Sidecar;
- Refinementpflicht und -verbot;
- atomare Fehlerkapselung ohne Teilresultat;
- deterministische Ergebnis- und Carrydigests;
- Abwesenheit historischer Adapter-, Materializer- und Orchestratorimporte.

Diese Tests wurden in S1-RY nicht ausgefuehrt.

## Statische Pruefung

Beide neuen Dateien wurden per AST geprueft:

```text
AST_OK mcm_field_organism/four_node_model_invocation.py
AST_OK tests/test_four_node_model_invocation.py
```

`git diff --check` blieb ohne Inhaltsfehler. Es wurde kein historischer
privater Baselineadapter, Common-Interval-Materializer oder Ein-Replik-
Orchestrator importiert.

## Nicht ausgefuehrt

S1-RY enthaelt keinen Testlauf, keine Expositionsreplik, keine Matrixzelle,
keinen Comparator und keinen Forschungsbefund. Die implementierten
Kernaufrufe sind nur Codepfade und wurden in diesem Schritt nicht aktiviert.

## Paketstatus

```text
S1RY_FOUR_NODE_MODEL_INVOCATION_IMPLEMENTED
ELEVEN_FOCUSED_TESTS_AWAIT_EXECUTION
NO_MODEL_INVOCATION_EXECUTED_IN_THIS_STAGE
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

```text
S1-RZ - fokussierter unveraenderter Testlauf und technische Abnahme
        der gemeinsamen Vier-Knoten-Modellaufrufoberflaeche
```

S1-RZ darf genau `tests/test_four_node_model_invocation.py` einmal
ausfuehren. Bei einem Fehler wird nur ein Fehlerrecord dokumentiert; keine
Korrektur im selben Schritt. Keine Matrixzelle und kein Forschungslauf.
