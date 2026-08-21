# S1-RU: Statischer rollenweiser Adapteranschluss-, Modelleingangsmontage- und Integritaetsvertrag

## Status und Zweck

S1-RU inventarisiert fuer alle 14 in S1-RT technisch abgenommenen
Frischbundle die vorhandene Modelloberflaeche und bindet die zulaessige
Montagegrenze. Dieser Schritt fuehrt keinen Modellkern aus und veraendert
keinen Feldzustand.

```text
FOURTEEN_MODEL_SURFACES_INVENTORIED
FOURTEEN_FRESH_BUNDLES_CONDITIONALLY_CONNECTABLE
PUBLIC_FIELD_AND_PRIVATE_STATE_ROLES_BOUND
LEGACY_TWO_THREE_NODE_CONTEXT_REUSE_FORBIDDEN
NO_IMPLEMENTATION_NO_TEST_NO_FIELD_ADVANCE
```

`CONDITIONALLY_CONNECTABLE` bedeutet nur, dass fuer jede Rolle eine
typisch passende bestehende technische Kernoberflaeche vorhanden ist. Eine
gemeinsame Vier-Knoten-Huelle ist noch nicht implementiert oder geprueft.

## Gemeinsame Montagegrenze

Jede Montage beginnt mit genau einem `FourNodeFreshBundle` aus der in S1-RT
abgenommenen Fabrik. Sie unterscheidet:

1. `public_fresh_field`: das unveraenderte Vier-Knoten-Nullfeld;
2. `model_input_field`: das Feld fuer die Rollenoberflaeche;
3. `native_private_state_or_none`: den getrennten Privatstatus, sofern die
   Rollenoberflaeche ihn separat erwartet.

Bei allen Rollen ausser B3-B6 sind `public_fresh_field` und
`model_input_field` dasselbe Feldobjekt. Bei B3-B6 ist
`model_input_field` eine neue `SharedMCMField`-Instanz, in die
ausschliesslich der native `MCMSubstrateState` des Rollenbundles eingebettet
wird. Das oeffentliche Frischfeld selbst bleibt unveraendert und substratfrei.

Die Montage darf keine Verteilung, kein Intervall, kein Ereignis, kein
Profil, kein Refinement und keine Replik hinzufuegen. Diese Werte gehoeren
in eine spaetere Aufrufhuelle.

## Rollenweiser Anschlussbestand

### A0 und A1

| Rolle | Vorhandene Oberflaeche | Montage |
| --- | --- | --- |
| `A0_CURRENT_CONTACT` | `advance_neutral_shared_field` oder die transiente Schwesteroberflaeche | oeffentliches Feld, kein Privatstatus |
| `A1_FAST_SH` | `advance_neutral_fast_shared_field` oder die transiente Schwesteroberflaeche | oeffentliches Feld, kein Privatstatus |

A0 darf keinen Nachhall- oder Privatcarry erhalten. A1 darf nur das im Feld
liegende S/H-Paar tragen. Synchroner oder transienter Kern wird erst anhand
eines spaeter validierten Intervalltyps ausgewaehlt.

### A2/B1 und A2/B2

| Rolle | Vorhandener Kern | Erforderliche neue Formbruecke |
| --- | --- | --- |
| `A2_B1_FIXED_ADAPTER` | exakter aktiver Feldschritt mit festem Kantenratenadapter | uebersetzt `FourNodeFixedAdapterState` ohne Wertneuberechnung in den bestehenden Adaptertyp |
| `A2_B2_INTEGRATOR` | `advance_s2_reference_model` plus atomare Felduebernahme | uebersetzt `FourNodeIntegratorState` in einen geordneten Vier-Knoten-L-Zustand und zurueck |

Das alte `DTS1PrivateBaselineAdapterContext` darf nicht verwendet werden. Es
bindet historische Kurzrollen, alte Konfigurationsdigests und die
Refinements 2/4/8. Diese Oberflaeche ist kein Vier-Knoten-Frischmodelleingang.

Die neuen Bruecken duerfen vorhandene Rechenkerne und registrierte
Konfigurationssemantik verwenden. Alte Profilhuellen, Fallrecords,
Geometrien und Ergebnisrollen bleiben ausgeschlossen. B1 bleibt
zustandskonstant. B2 traegt ausschliesslich seinen vollstaendigen L-Zustand.

### A2/B3 bis A2/B6

| Rolle | Modellkern | Kopplungsrechner | Montage |
| --- | --- | --- | --- |
| `A2_B3_LOCAL_LEAKY` | `advance_mcm_f3_shared_field` | `compute_mcm_f3_local_leaky_baseline` | native M-Einbettung |
| `A2_B4_LINEAR_COUPLED` | `advance_mcm_f3_shared_field` | `compute_mcm_f3_linear_coupled_baseline` | native M-Einbettung |
| `A2_B5_F3_FULL` | `advance_mcm_f3_shared_field` | `compute_mcm_f3_coupling` | native M-Einbettung |
| `A2_B6_CONST_V` | `advance_mcm_f3_shared_field` | `compute_w7n_coupling_baseline` mit gebundener CONST-V-Spezifikation | native M-Einbettung |

Die Montage entnimmt `FourNodeSubstrateFreshState` nur dessen nativen
`MCMSubstrateState`. Wrapper und registrierter Payload bleiben ausserhalb
des Modellfeldes als Digest- und Rueckprojektionsnachweis erhalten. S1-RU
bindet keinen Refinementwert; ein Modellaufruf bleibt bis zur spaeteren
Intervallhuelle gesperrt.

### A3, M1, M2 und M5

| Rolle | Vorhandene Oberflaeche | Getrennter Privatstatus |
| --- | --- | --- |
| `A3_NORM` | `advance_a3_norm_replace_s` | `W7NLocalBaselineState`, `model_id=norm` |
| `M1_PARALLEL_LEAK` | `advance_m1_parallel_leak_replace_s` | vollstaendige `M1ParallelLeakBankState` |
| `M2_DELAY` | `advance_m2_bounded_buffer_replace_s` | eigener `M2BoundedBufferState`, Modus DELAY |
| `M2_REPLAY` | `advance_m2_bounded_buffer_replace_s` | eigener `M2BoundedBufferState`, Modus REPLAY |
| `M5_DIRECT` | `advance_m5_direct_replace_s` | `W7NLocalBaselineState`, `model_id=leak` |

Diese Kompositoren erwarten ein substrat- und entwicklungsfreies Feld. Eine
Einbettung ihres Privatstatus ist verboten. M2-DELAY und M2-REPLAY duerfen
weder Puffer noch Cursor oder Carry teilen.

### M4

`M4_DTS1_T1` wird an `advance_dts1_coupled_fast_shared_field`
angeschlossen. Das Feld bleibt substrat- und entwicklungsfrei. Die
vollstaendige `DTS1ResourceAnatomy` und die daraus typisierten
`DTS1StepRates` bleiben getrennte Eingaben. Der Kandidatensidecar muss
`None` bleiben.

Die vorhandene M4-Oberflaeche akzeptiert nur synchrone positive
`MCMFieldStepTime`-Intervalle. Ein transienter M4-Aufruf darf nicht ersetzt
oder still gemappt werden, sondern bleibt bis zu einer eigenen statischen
Kompatibilitaetsentscheidung `NOT_CONNECTABLE`. T1 bleibt Struktur- und
Erhaltungsvalidierung und wird nicht als zweiter Zustand montiert.

## Gebundene Montageausgabe

Eine spaetere Implementierung darf genau einen unveraenderlichen Record
`FourNodeModelInputAssembly` erzeugen. Er muss mindestens enthalten:

```text
model_role
adapter_surface_id
public_fresh_field
model_input_field
native_private_state_or_none
registered_private_digest_or_none
registered_edge_inventory_digest_or_none
native_edge_inventory_digest_or_none
registered_geometry_digest_or_none
native_geometry_digest_or_none
field_embedding_mode
assembly_digest
```

Zulaessige Einbettungswerte sind `PUBLIC_FIELD_IDENTITY` und
`NATIVE_SUBSTRATE_COPY`. Letzterer ist nur fuer B3-B6 zulaessig. Der Record
ist keine Modellinvokation und enthaelt keine Verteilung, Zeit,
Konfiguration, Exposition oder Ausgabe.

## Integritaetsidentitaeten

Vor Freigabe eines Records muessen gelten:

- Rolle, Feld-ID, Layer-ID, Geometrie-ID, Modalitaet und Dockabbildung sind
  gegenueber dem Frischbundle identisch;
- Knotenreihenfolge, IDs, Positionen, S, H, Ticks, Wahrnehmungen und lokale
  Samples sind identisch;
- `last_distribution` und `development` bleiben `None`;
- `substrate` bleibt ausser bei B3-B6 `None`;
- bei B3-B6 stammen Zustand, vier Massen, Arm und nativer Kanteninventardigest
  unveraendert aus dem Rollenbundle;
- registrierter und nativer Kantenbestand bleiben explizit getrennte
  Digestrollen der abgenommenen Bruecke;
- bei M2 bleiben registrierter und nativer Geometriedigest getrennt;
- bei A0/A1 existiert kein privater Digest;
- bei allen zustandsbehafteten Rollen bleibt der Manifestdigest erhalten;
- verschiedene Repliken teilen keinen veraenderbaren Feld- oder
  Privatobjektgraphen.

Der `assembly_digest` bindet eine kanonische Projektion dieser Identitaeten
und Typentscheidungen. Er enthaelt keine Objektadresse und keinen Laufwert.

## Fail-Closed-Regeln

Die Montage bricht atomar ab, wenn:

- das Bundle nicht aus der validierten Vier-Knoten-Fabrik stammt;
- Rolle, Privatstatus und Stateless-Marker nicht exakt zusammenpassen;
- B3-B6 ohne native Einbettung oder eine andere Rolle mit Substrat montiert
  wird;
- eine bestehende Kanten- oder Geometriebruecke nicht uebereinstimmt;
- Knotenidentitaet, Reihenfolge, Geometrie, Dock, Feldzeit oder Frischwerte
  veraendert werden;
- M2-Modi, M1-Spuren oder Replikobjekte geteilt werden;
- M4 einen Sidecar, transienten Ersatz oder eine neue Ressourcenrolle
  erhalten soll;
- der alte S1-JN/S1-JW-Kontext, alte Frischbuilder oder der alte
  Ein-Replik-Orchestrator aufgerufen werden;
- die Montage einen Modellkern, Comparator oder Feldschritt ausfuehrt.

Es gibt keine Reparatur, Normalisierung oder Ersatzrolle. Ein unmontierbarer
Pflichtarm bleibt sichtbar `NOT_CONNECTABLE` und sperrt das Gesamtpaket.

## Begrenztes Implementierungsbudget

Der folgende Schritt darf genau diese zwei neuen Dateien betreffen:

```text
mcm_field_organism/four_node_model_input_assembly.py
tests/test_four_node_model_input_assembly.py
```

Die Produktionsoberflaeche darf Recordtypen, Fehlercodes und genau eine
reine Funktion bereitstellen:

```text
assemble_four_node_model_input(bundle) -> FourNodeModelInputAssembly
```

Sie darf keinen Modellkern aufrufen. Bestehende Fabrik-, Modell-,
Orchestrator- und Manifestdateien bleiben unveraendert. Die Tests duerfen
nur Typmontage, B3-B6-Feldkopie, Identitaetserhaltung, Digestbindung,
Objekttrennung und Fail-Closed-Verhalten pruefen. Ihre Ausfuehrung gehoert
nicht zum Implementierungsschritt.

## Aussagegrenze

S1-RU bestaetigt weder eine Baselinefunktion noch eine Kandidatenwirkung. Es
wurde keine Matrixzelle materialisiert und keine hypothetische
MCM-Memory-Faehigkeit untersucht oder nachgewiesen. Der primaere
MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Paketstatus

```text
S1RU_STATIC_MODEL_INPUT_ASSEMBLY_CONTRACT_BOUND
FOURTEEN_ROLE_SURFACE_MAP_COMPLETE
LEGACY_CONTEXT_REUSE_BLOCKED
ASSEMBLY_IMPLEMENTATION_NOT_PRESENT
MODEL_ADAPTER_INVOCATION_NOT_PRESENT
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

```text
S1-RV - Implementierung der reinen Vier-Knoten-Modelleingangsmontage
        fuer die 14 Frischbundle ohne Modellkernaufruf
```

S1-RV darf nur die gebundene Montagefunktion und ihre noch nicht
ausgefuehrten fokussierten Tests implementieren. Keine Adapterausfuehrung,
kein Intervall, keine Matrixzelle, kein Comparator und kein Feldlauf.
