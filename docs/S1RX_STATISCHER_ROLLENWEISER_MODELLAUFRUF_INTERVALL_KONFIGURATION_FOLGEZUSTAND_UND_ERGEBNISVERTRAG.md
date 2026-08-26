# S1-RX: Statischer rollenweiser Modellaufruf-, Intervall-, Konfigurations-, Folgezustands- und Ergebnisvertrag

## Status und Zweck

S1-RX bindet nach der technischen Abnahme der Modelleingangsmontage die
naechste Grenze fuer alle 14 Rollen. Der Vertrag legt fest, welche
Intervallform und registrierte Konfiguration ein Modellkern erhalten darf,
welcher Zustand weitergetragen wird und wie Erfolg oder Fehler atomar
auszugeben sind.

```text
FOURTEEN_ROLE_INVOCATION_SURFACES_BOUND
SYNC_AND_TRANSIENT_CAPABILITIES_EXPLICITLY_SEPARATED
REGISTERED_CONFIGURATION_MATERIALIZATION_BOUND
COMPLETE_FIELD_AND_PRIVATE_CARRY_BOUND
ATOMIC_COMPLETED_OR_NOT_COMPUTABLE_RESULT_BOUND
NO_IMPLEMENTATION_NO_TEST_NO_MODEL_INVOCATION
```

## Gemeinsame Aufrufgrenze

Eine spaetere `FourNodeModelInvocation` muss genau enthalten:

```text
model_input_assembly_or_prior_carry
receptor_distribution
interval_kind
step_time_or_transient_input_set
registered_configuration
refinement_or_none
input_field_digest
private_prestate_digest_or_none
configuration_digest
interval_digest
invocation_digest
```

Der Aufruf erhaelt keinen Repliknamen, keine Expositionsfamilie, keinen
Checkpoint, kein Ereignisziel, keinen Comparatorwert und kein erwartetes
Ergebnis. Kontakt und Nullkontakt unterscheiden sich nur durch die normale
`ReceptorDistribution`, nicht durch einen Modellschalter.

`ALIGN_READOUT_SH` und `OBSERVE` sind keine Modellaufrufe. Sie duerfen weder
Feldzeit noch Privatstatus veraendern.

## Intervallformen

### Synchrones Intervall

`SYNC` besteht aus genau einer `ReceptorDistribution` und einem
`MCMFieldStepTime`. Clock-ID, Starttick und Endtick muessen uebereinstimmen.
Das Intervall ist positiv und schliesst genau einen Felduebergang ab.

### Transientes Intervall

`TRANSIENT` besteht aus einer kontaktfreien `ReceptorDistribution` und
einem vollstaendigen `TransientNeuronInputSet`. Dessen `step_time` muss die
Verteilungsgrenze exakt wiedergeben und alle vier Dockneuronen genau einmal
adressieren.

Eine Intervallform darf nicht in die andere umgerechnet werden. Insbesondere
darf ein fehlender transienter Kern nicht durch einen synchronen
Nullkontaktschritt ersetzt werden.

## Rollenweise Intervallfaehigkeit

| Rolle | SYNC | TRANSIENT | Kernoberflaeche |
| --- | --- | --- | --- |
| `A0_CURRENT_CONTACT` | ja | ja | neutrale S-Feldkerne |
| `A1_FAST_SH` | ja | ja | schnelle S/H-Feldkerne |
| `A2_B1_FIXED_ADAPTER` | ja | nein | neuer Vier-Knoten-Festadapter |
| `A2_B2_INTEGRATOR` | ja | nein | neuer Vier-Knoten-S2-Formadapter |
| `A2_B3_LOCAL_LEAKY` | ja | ja | F3 mit Local-Leaky-Rechner |
| `A2_B4_LINEAR_COUPLED` | ja | ja | F3 mit Linear-Coupled-Rechner |
| `A2_B5_F3_FULL` | ja | ja | vollstaendiger F3-Rechner |
| `A2_B6_CONST_V` | ja | ja | F3 mit gebundener CONST-V-Spezifikation |
| `A3_NORM` | ja | ja | atomarer NORM-Replace-S-Kompositor |
| `M1_PARALLEL_LEAK` | ja | ja | atomarer Zweispur-Replace-S-Kompositor |
| `M2_DELAY` | ja | ja | atomarer DELAY-Puffer-Kompositor |
| `M2_REPLAY` | ja | ja | atomarer REPLAY-Puffer-Kompositor |
| `M4_DTS1_T1` | ja | nein | gekoppelter DTS-1/S/H-Feldschritt |
| `M5_DIRECT` | ja | ja | atomarer Direct-Leak-Replace-S-Kompositor |

Enthaelt ein spaeterer Pflichtplan ein `TRANSIENT`-Intervall fuer B1, B2
oder M4, bleibt die betreffende Zelle sichtbar `NOT_CONNECTABLE`. Da S1-RA
alle 224 Zellen fordert, bleibt dann das Gesamtpaket gesperrt. Die Rolle darf
nicht entfallen und das Intervall nicht ersetzt werden.

## Gemeinsame registrierte Feldkonfiguration

Die vorhandene technische Baselinebindung wird unveraendert materialisiert:

```text
NeutralLocalFieldSubstrateConfig(1.0)
NeutralFastAfterimageConfig(0.5)
NeutralFieldDissipationConfig(0.0)
```

A0 verwendet davon nur die neutrale Substratkonfiguration. Alle anderen
feldschnellen Rollen erhalten die fuer ihre vorhandene Signatur benoetigten
Teile. Eine Rolle darf diese Werte weder nach Expositionsreplik noch nach
Kontakt/Gap veraendern.

Die drei Werte sind Bestandsregistrierung und keine neue Parametersuche.
Ihr gemeinsamer kanonischer Digest wird pro Modellrolle zusammen mit der
jeweiligen privaten Rollenregistrierung gebunden.

## Rollenweise Zusatzkonfiguration

### A0 und A1

A0 besitzt keinen Privatstatus und keine Zusatzkonfiguration. A1 besitzt
ebenfalls keinen Privatstatus; sein schneller H-Zeitwert ist Teil der
gemeinsamen Feldkonfiguration.

### B1 und B2

B1 erhaelt exakt den `FourNodeFixedAdapterState` des Carryrecords. Seine
Basisrate, drei Kantenraten, Backreactionrolle und beide Kanten-Digestrollen
werden nicht neu berechnet.

B2 erhaelt exakt den geordneten Vier-Knoten-L-Zustand und die vorhandene
`S2ReferenceModelConfig()`. Die Formbruecke baut daraus gemeinsam mit S und H
einen `S2ReferenceState` und projiziert nur den vollstaendigen L-Folgezustand
zurueck.

### B3 bis B6

Alle vier Rollen erhalten die gemeinsame Feldkonfiguration, den bereits im
Feld eingebetteten rollenfesten M-Arm und ihren fest gebundenen
Kopplungsrechner. B6 erhaelt zusaetzlich nur die bereits digestgebundene
CONST-V-Spezifikation.

`refinement` ist ein positiver numerischer Integrationskontrollwert und kein
Modellzustand. Er muss aus einer spaeteren gemeinsamen Replikregistrierung
stammen, im Aufrufdigest stehen und fuer alle verglichenen F3-Rollen an
derselben Ereignisposition gleich sein. Eine Huelle darf keinen Defaultwert
stillschweigend einsetzen.

### A3, M1, M2 und M5

- A3 verwendet exakt die registrierte W7-M-Spezifikation `norm`;
- M1 verwendet `build_registered_m1_parallel_leak_configuration()`;
- M2 verwendet je Rolle `build_registered_m2_configuration("DELAY")` oder
  `build_registered_m2_configuration("REPLAY")`;
- M5 verwendet exakt die registrierte W7-M-Spezifikation `leak`.

Diese Werte werden typisiert materialisiert und gegen die bereits im
Frischbundle gebundene Konfigurationsidentitaet geprueft. Es gibt keine
rollen- oder repliklokale Anpassung.

### M4

M4 verwendet die gemeinsame Feldkonfiguration, den rollenprivaten
`FourNodeM4FreshState` und `backreaction_enabled=True`. Die Raten werden
ausschliesslich nach Feldnamen ueberfuehrt:

```text
DTS1StepRates(
    binding_rate = source.binding_rate,
    turnover_rate = source.turnover_rate,
    recovery_rate = source.recovery_rate,
)
```

Damit werden `turnover_rate` und `recovery_rate` trotz unterschiedlicher
Feldreihenfolge der Quell- und Zieltypen nicht vertauscht. Fuer den
registrierten Frischzustand sind die Werte 0.4, 0.3 und 0.2. Der
Kandidatensidecar bleibt `None`.

T1 wird nicht aufgerufen. Nach jedem M4-Schritt pruefen ausschliesslich die
vorhandenen lokalen DTS-1-Halbankteilsledger und das globale Ledger die
Erhaltung ohne Doppelzaehlung. Die eingefrorene T1-Vertragsidentitaet ist
nur Referenzbeleg mit `t1_runtime_transition_count=0`.

## Rollenweiser Folgezustand

| Rolle | Folgefeld | Rollenprivater Carry |
| --- | --- | --- |
| A0 | vollstaendiges Feld | keiner |
| A1 | vollstaendiges S/H-Feld | keiner |
| B1 | vollstaendiges Feld | derselbe unveraenderte Festadapterzustand |
| B2 | vollstaendiges Feld | vollstaendiger L-Folgezustand |
| B3-B6 | vollstaendiges Feld mit M | Wrapper auf exakt dasselbe M des Folgefeldes |
| A3 | vollstaendiges Feld | vollstaendiger NORM-Folgezustand |
| M1 | vollstaendiges Feld | vollstaendige FAST/SLOW-Folgebank |
| M2-DELAY | vollstaendiges Feld | vollstaendiger eigener DELAY-Puffer |
| M2-REPLAY | vollstaendiges Feld | vollstaendiger eigener REPLAY-Puffer |
| M4 | vollstaendiges Feld | vollstaendige Folgeanatomie, unveraenderte Ratenbindung |
| M5 | vollstaendiges Feld | vollstaendiger Direct-Leak-Folgezustand |

Bei B3-B6 gibt es nur eine dynamische M-Quelle: `result.field.substrate`.
Der private Wrapper referenziert genau dieses Objekt und bindet nur
Rueckprojektion und Digestrollen. Eine unabhaengige zweite M-Fortschreibung
oder Rekonstruktion aus dem Vorzustand ist verboten.

Der Folgezustand einer erfolgreichen Operation wird ohne Neumontage des
Frischzustands zum Vorzustand der naechsten Operation derselben Matrixzelle.
Zwischen Zellen wird kein Carry geteilt.

## Gemeinsamer atomarer Ergebnisrecord

Eine spaetere Huelle muss genau einen `FourNodeModelStepResult` liefern:

```text
status = COMPLETED | NOT_COMPUTABLE
model_role
interval_kind
invocation_digest
input_field_digest
private_prestate_digest_or_none
configuration_digest
output_field_or_not_computable
next_private_state_or_not_computable
output_field_digest_or_none
next_private_state_digest_or_none
native_receipt_or_diagnostics_digest_or_none
field_time_advance_count
failure_codes
result_digest
```

Bei `COMPLETED` muessen Folgefeld und rollenrichtiger Privatcarry gemeinsam
vorliegen. Der Feldzeitfortschritt betraegt exakt eins. A0/A1 verwenden eine
kanonische Zustandslosmarkierung statt eines Privatdigests.

Bei `NOT_COMPUTABLE` werden weder Teilfeld noch privater Teilfolgezustand
publiziert. Die Ausgabe enthaelt nur Eingangsprovenienz, kanonische
Fehlerklasse, letzte abgeschlossene Validierungsphase und Eigendigest.

Die vorhandenen atomaren Receipts von A3, M1, M2 und M5 werden unveraendert
gekapselt. A0, A1, B1-B6 und M4 erhalten durch die neue Huelle erst eine
gemeinsame atomare Fehleroberflaeche; native Diagnostik wird nicht
nachberechnet oder als Carry gespeichert.

## Rueckprojektions- und Integritaetsregeln

Jeder erfolgreiche Aufruf muss belegen:

- Ausgabegeometrie, Knotenordnung und Dockabbildung stimmen mit dem Eingang
  ueberein;
- Feldzeit und Wahrnehmung schreiten genau entsprechend dem Intervall fort;
- Konfiguration, Modellrolle und Replikprovenienz bleiben unveraendert;
- Privatfolgezustand besitzt denselben rollenrichtigen Typ;
- B1 bleibt zustandsidentisch;
- B3-B6 erhalten Arm, Gesamtmassenidentitaet und Kanteninventar;
- M1 behaelt zwei getrennte Spuren;
- M2 behaelt Modus, Geometrie, Reihenfolge und eigenen Puffer;
- M4 behaelt Knoten-/Kantenbestand, Gesamtkapazitaet, Ratenbindung und
  fehlenden Sidecar;
- ein nativer Kernreceipt und die gemeinsame Huelle bezeichnen denselben
  Feld- und Privatabschluss;
- Diagnostik beeinflusst weder Feld noch Privatcarry.

## Fail-Closed-Regeln

Der Aufruf bleibt `NOT_COMPUTABLE`, wenn:

- Rolle, Assembly, Carry, Konfiguration oder Intervalltyp nicht zueinander
  passen;
- Verteilung und Schrittzeit oder transiente Eingabe nicht exakt dieselbe
  Grenze besitzen;
- B1, B2 oder M4 ein transientes Intervall erhalten;
- ein synchrones Intervall als transient oder umgekehrt nachgebildet wird;
- ein Default-Refinement, eine Default-Konfiguration oder ein Default-Carry
  still eingesetzt wird;
- Kontakt-, Gap-, Replik- oder Ergebniswissen einen Modellparameter
  veraendert;
- B3-B6 zwei voneinander getrennte M-Folgezustaende erzeugen;
- M2-Puffer oder Carries zwischen Rollen oder Zellen geteilt werden;
- M4-Raten positional vertauscht, ein Sidecar aktiviert oder T1 ausgefuehrt
  wird;
- ein Kernfehler, ungueltiges Receipt, Digestbruch oder Geometriebruch
  auftritt;
- ein Teilresultat als erfolgreicher Carry freigegeben werden soll.

Historische S1-JN/S1-JW-Aufrufkontexte, alte Materializer und der
Ein-Replik-Orchestrator bleiben gesperrt.

## Begrenztes Implementierungsbudget

Der folgende Schritt darf genau eine neue Produktionsdatei und eine neue
fokussierte Testdatei fuer die Aufrufhuelle anlegen:

```text
mcm_field_organism/four_node_model_invocation.py
tests/test_four_node_model_invocation.py
```

Bestehende Modellkerne, Frischfabrik, Modelleingangsmontage, historische
Adapter und Orchestratoren bleiben unveraendert. Die Implementierung darf
nur registrierte Konfigurationen materialisieren, rollenfest dispatchen,
vollstaendige Folgezustaende rueckprojizieren und Fehler atomar kapseln.

Der Implementierungsschritt darf Tests definieren, aber nicht ausfuehren. Er
darf keine Expositionsreplik, Matrixzelle, Checkpoint- oder Comparatorlogik
enthalten.

## Aussagegrenze

S1-RX bindet nur eine technische Aufruf- und Carryoberflaeche. Es wurde kein
Modell ausgefuehrt und kein Funktionsbefund erzeugt. Eine hypothetische
MCM-Memory bleibt eine offene Entwicklungsrichtung ohne Faehigkeitsnachweis.

## Paketstatus

```text
S1RX_STATIC_ROLE_INVOCATION_AND_ATOMIC_RESULT_CONTRACT_BOUND
FOURTEEN_INTERVAL_CAPABILITY_ROWS_BOUND
REGISTERED_CONFIGURATION_AND_CARRY_RULES_BOUND
MODEL_INVOCATION_IMPLEMENTATION_NOT_PRESENT
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

```text
S1-RY - Implementierung der gemeinsamen Vier-Knoten-Modellaufruf- und
        atomaren Ergebnisoberflaeche fuer die 14 Rollen
```

S1-RY darf nur die in S1-RX gebundene Produktionsdatei und ihre noch nicht
ausgefuehrten fokussierten Tests implementieren. Keine Testausfuehrung,
keine Expositionsreplik, keine Matrixzelle, kein Comparator und kein
Forschungslauf.
