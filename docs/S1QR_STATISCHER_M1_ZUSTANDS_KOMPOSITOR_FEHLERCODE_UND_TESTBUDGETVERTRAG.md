# S1-QR: Statischer M1-Zustands-, Kompositor-, Fehlercode- und Testbudgetvertrag

## Status und Umfang

S1-QR bindet die vollstaendige private Implementierungsoberflaeche fuer die
in S1-QP und S1-QQ registrierte M1-Zweispurfamilie. Festgelegt werden
Dateigrenze, Konfiguration, Bankzustand, Kompositionsordnung, atomare
Resultate, Fehlercodes, Mutationsklassen und das einmalige Testbudget.

S1-QR implementiert und testet nichts. Es gibt keine API-, Runtime-, Runner-
oder Orchestratorfreigabe und keinen Feldlauf.

Vertragsentscheidung:

```text
M1_REGISTERED_CONFIGURATION_AND_ATOMIC_TWO_TRACE_STATE_BOUND
M1_A1_REPLACE_S_PRIVATE_COMPOSITOR_SURFACE_BOUND
M1_SIXTEEN_FAILURE_CODES_AND_TWENTY_TEST_METHODS_BOUND
THREE_FILE_IMPLEMENTATION_AND_SINGLE_TEST_PROCESS_BOUND
NO_IMPLEMENTATION_NO_EXECUTION
```

## Gebundene Dateigrenze

Ein spaeterer S1-QS-Schritt darf genau drei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/m1_parallel_leak_replace_s_compositor.py` | registrierte Spezifikationen, Konfiguration, Bankzustand, Kompositor, Receipt und Resultat |
| `tests/m1_parallel_leak_replace_s_s1qs_fixtures.py` | kleine kanonische Gueltig- und Fehlermutationsfixtures |
| `tests/test_m1_parallel_leak_replace_s_s1qs_compositor.py` | exakt zwanzig fokussierte Abnahmetests |

Alle vorhandenen Produktions- und Testdateien bleiben unveraendert. Das gilt
insbesondere fuer:

- `local_state_replace_s_compositor_core.py`;
- `m5_direct_replace_s_compositor.py`;
- `a3_norm_replace_s_compositor.py`;
- `w7n_capacity_function_baselines.py`;
- `w7m_capacity_function_matrix.py`;
- den primaeren Feldkern und `current_api.py`;
- Root-Exports, Runtime, Runner und Orchestrator;
- Kandidaten-, E1-, DTS-1-, G2/D3- und Entwicklungsdateien.

Nach dem einmaligen Testprozess duerfen nur `README.md`,
`AKTUELLER_FORSCHUNGSWEG.md` und
`docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md` um das tatsaechliche Ergebnis
ergaenzt werden.

## Vertrags- und Registrierungsidentitaet

Der private Kompositor verwendet:

```text
CONTRACT_ID = m1-parallel-leak-replace-s/s1qr.v1
SOURCE_S1QQ_DIGEST =
141b552532f0f43449e2d92c2d09274eae6acb66b224cd287b12b3a6d8d63f3b
READOUT_ID = pointwise-equal-mean/v1
TRACE_ORDER = (FAST, SLOW)
```

Das Modul darf genau eine reine Frischfabrik fuer die registrierte
Konfiguration bereitstellen:

```text
build_registered_m1_parallel_leak_configuration()
    -> M1ParallelLeakConfiguration
```

`M1ParallelLeakConfiguration` enthaelt genau:

- `source_registration_digest`;
- `trace_order`;
- `fast_spec`;
- `slow_spec`;
- `readout_id`.

`fast_spec` und `slow_spec` sind vollstaendige `W7MBaselineSpec`-Objekte mit
den in S1-QQ gebundenen Identitaeten und Zeitwerten. Die Gap-Checkpointwerte
sind keine Gleichungseingaben und werden nicht an W7-N uebergeben. Ihr
gemeinsamer S1-QQ-Digest bleibt ausschliesslich Konfigurationsprovenienz.

Eine Konfiguration ist nur gueltig, wenn alle Felder wertgleich zur
registrierten Frischfabrik sind. Ein alternatives Specobjekt mit nur
aehnlichem Verhalten ist unzulaessig.

## Vollstaendiger M1-Bankzustand

Das Modul bindet:

```text
M1ParallelLeakBankState
    fast_state: W7NLocalBaselineState
    slow_state: W7NLocalBaselineState
```

Verbindliche Invarianten:

- beide Zustandsrollen haben `model_id = leak`;
- beide Latentvektoren sind endlich, nicht leer und gleich lang;
- beide folgen derselben kanonischen Feldknotenordnung;
- `fast_state` und `slow_state` sind getrennte Objekte;
- Rollen werden nie anhand ihrer Werte umsortiert;
- kein Mittelwert oder Feldoutput wird als dritter Carry gespeichert.

Die Frischfabrik:

```text
build_zero_m1_parallel_leak_bank(configuration, location_count)
    -> M1ParallelLeakBankState
```

ruft den vorhandenen W7-N-Nullzustandskern fuer jede registrierte Spur genau
einmal auf. Auch bei wertgleichen Nullvektoren muessen zwei unabhaengige
Zustandsobjekte entstehen.

## Private Aufrufoberflaeche

S1-QS darf genau eine neue ausfuehrende M1-Funktion bereitstellen:

```text
advance_m1_parallel_leak_replace_s(
    field,
    distribution,
    interval_input,
    neutral_substrate_config,
    fast_afterimage_config,
    m1_configuration,
    m1_prestate,
    dissipation_config=None,
) -> M1ParallelLeakReplaceSResult
```

`interval_input` ist exakt:

```text
MCMFieldStepTime | TransientNeuronInputSet
```

Der Typ waehlt nur den vorhandenen synchronen oder transienten A1-Fast-Pfad.
Konfiguration, Zustand und Intervallform bleiben explizit; es gibt keine
Auswahl durch Arm-, Ereignis- oder Ergebnislabels.

## Gebundene Phasenordnung

Jeder fachlich erreichbare Aufruf folgt exakt:

```text
1.  api_intake
2.  common_identity_validation
3.  interval_discrimination
4.  a1_fast_proposal
5.  a1_proposal_validation
6.  fast_trace_advance
7.  slow_trace_advance
8.  trace_pair_validation
9.  equal_mean_readout
10. replace_s_materialization
11. final_field_validation
12. atomic_receipt
```

Der erste Fehler beendet alle nachfolgenden Phasen. Kein Fehlerpfad darf
Werte reparieren, neu ordnen, begrenzen, normalisieren oder erneut rechnen.

## Parallele Einzelspurfortschreibung

Nach genau einem gueltigen A1-Fast-Vorschlag wird dessen vollstaendiges S als
unveraenderlicher Evidencevektor gebildet. Danach gilt logisch:

```text
fast_result = advance_w7n_local_baseline(
    fast_spec, fast_prestate, evidence, duration_seconds
)

slow_result = advance_w7n_local_baseline(
    slow_spec, slow_prestate, evidence, duration_seconds
)
```

Beide Aufrufe erhalten dasselbe Evidenceobjekt beziehungsweise wertidentische
Evidence, dieselbe Dauer und dieselbe Ortsreihenfolge. Die textuelle
Aufrufreihenfolge erzeugt keine Kopplung. Der Slow-Aufruf darf weder
`fast_result` noch dessen Zustand oder Output lesen.

Jedes Resultat ist nur gueltig, wenn:

- Typ, Modellrolle, Ortsanzahl und Endlichkeit stimmen;
- der direkte Output exakt dem jeweiligen Folgezustand entspricht;
- FAST das FAST-Spec und SLOW das SLOW-Spec verwendet;
- beide Resultate vollstaendig vor dem Readout vorliegen.

## Gleichgewichteter Readout

Nach erfolgreicher Validierung beider Spurresultate wird genau einmal und
punktweise gebildet:

```text
mean_output_i = (fast_output_i + slow_output_i) / 2
```

Der vollstaendige Mittelwertvektor muss:

- dieselbe Ortsanzahl und Reihenfolge besitzen;
- ausschliesslich endliche Werte enthalten;
- im geschlossenen Bereich `[-1, 1]` bleiben;
- exakt aus den zwei registrierten direkten Outputs entstehen;
- keine weiteren Gewichte, Nenner, Gates oder Clippingoperationen verwenden.

Der Mittelwert ist temporaerer Output und kein dritter privater Zustand.

## Atomare Feldkomposition

Der private modellneutrale Hilfskern aus S1-QN wird unveraendert verwendet
fuer:

- Intervall- und Geometriepruefung;
- genau einen A1-Fast-Vorschlag;
- vollstaendige `REPLACE_S`-Materialisierung;
- H-, Perzeptions-, Dock-, Identitaets- und Feldzeitpruefung;
- kanonische Feld-, Geometrie- und Intervallprovenienz.

Finales S stammt vollstaendig aus `mean_output`. Gegen den A1-Vorschlag
bleiben H, Perzeption, Docks, Neuronenidentitaeten, Geometrie, Distribution
und Feldzeitrollen unveraendert. Es gibt genau eine Feldzeitfortschreibung.

Der A1-Vorschlag, die zwei Einzelspurausgaben und der Mittelwert werden nur
durch Digests belegt. Sie werden nicht als weitere Felder oder Carryzustaende
publiziert.

## Resultat- und Receiptrollen

`M1ParallelLeakReplaceSResult` enthaelt genau:

```text
field: SharedMCMField | NOT_COMPUTABLE
next_m1_state: M1ParallelLeakBankState | NOT_COMPUTABLE
receipt: M1ParallelLeakReplaceSReceipt
```

Ein gueltiger Receipt bindet mindestens:

- Vertrags-, S1-QQ- und Konfigurationsidentitaet;
- Intervallform sowie Feld-, Distribution- und Intervallprovenienz;
- Geometrie- und M1-Vorzustandsdigest;
- internen A1-Vorschlagsdigest;
- getrennte FAST- und SLOW-Folgezustandsdigests;
- Digest des atomaren M1-Folgezustands;
- getrennte direkte Outputdigests;
- Beleg beider Zustands-/Outputidentitaeten;
- Digest des vollstaendigen Mittelwertoutputs;
- Beleg des exakten gleichgewichteten Readouts;
- finalen Felddigest;
- Beleg vollstaendiger S-Ersetzung und H-Identitaet;
- Beleg genau einer Feldzeitfortschreibung;
- kanonische Phasen, Status, Fehlercodes und Receiptdigest.

Es gibt genau die Status `COMPLETED` und `NOT_COMPUTABLE`. Bei
`NOT_COMPUTABLE` sind Feld und gesamter M1-Folgezustand gemeinsam nicht
berechenbar. Ein einzelner Spurzustand, Mittelwert oder Digest ist kein
Sachoutput.

## Endliches Fehlervokabular

S1-QR bindet exakt diese sechzehn Fehlercodes in dieser Reihenfolge:

```text
QR_INPUT_TYPE_INVALID
QR_FIELD_ROLE_INVALID
QR_DISTRIBUTION_OR_INTERVAL_INVALID
QR_CONFIGURATION_INVALID
QR_M1_PRESTATE_INVALID
QR_GEOMETRY_OR_ORDER_MISMATCH
QR_A1_ADVANCE_FAILED
QR_A1_PROPOSAL_INVALID
QR_FAST_ADVANCE_FAILED
QR_SLOW_ADVANCE_FAILED
QR_TRACE_PAIR_INVALID
QR_MEAN_READOUT_INVALID
QR_S_REPLACEMENT_FAILED
QR_H_OR_PROVENANCE_CHANGED
QR_FIELD_TIME_CARDINALITY_FAILED
QR_ATOMIC_OUTPUT_FAILED
```

Die Codes sind deterministisch und entsprechen der ersten erreichbaren
Fehlergrenze. Kein Fehler erzeugt einen reparierten Wert oder Teiloutput.

## Genau sechzehn Fehlermutationsklassen

Die spaetere Fixture- und Testgrenze bindet isoliert:

1. falschen Typ an einer Pflichtgrenze;
2. Feld mit Substrat- oder Entwicklungszustand;
3. unpassende Distribution oder Intervallform;
4. veraenderte Registrierung, Spezifikation, Zeitrolle oder Readoutidentitaet;
5. falschen, aliasierten, umgeordneten oder unvollstaendigen M1-Vorzustand;
6. abweichende Knotenanzahl oder Ortsordnung;
7. kontrolliertes Scheitern des A1-Aufrufs;
8. ungueltigen oder zeitlich abweichenden A1-Vorschlag;
9. kontrolliertes Scheitern der FAST-Fortschreibung;
10. kontrolliertes Scheitern der SLOW-Fortschreibung;
11. unvollstaendiges, nicht endliches oder nicht direktes Spurresultat;
12. falschen, nicht endlichen oder bereichsverletzenden Mittelwert;
13. partielle oder falsche S-Ersetzung;
14. veraendertes H oder veraenderte Feldprovenienz;
15. zweiten Tick oder abweichendes Zeitfenster;
16. simuliertes Scheitern vor atomarer Resultatpublikation.

Jede Mutation muss genau ihren vorregistrierten Code liefern und Feld sowie
gesamten Bankfolgezustand gemeinsam sperren.

## Genau zwanzig neue Testmethoden

Die S1-QS-Abnahme prueft exakt:

1. Modul-, Typ-, Status-, Phasen- und Fehlercodeoberflaeche;
2. exakte S1-QQ-Konfigurationspayload und Registrierungsdigest;
3. deterministische getrennte Nullfrischzustaende;
4. gueltigen synchronen M1-Schritt;
5. gueltigen transienten M1-Schritt;
6. exakte FAST-Uebereinstimmung mit dem vorhandenen W7-N-`LEAK`-Kern;
7. exakte SLOW-Uebereinstimmung mit dem vorhandenen W7-N-`LEAK`-Kern;
8. exakten punktweisen Mittelwert und Bereichserhaltung;
9. vollstaendige signed S-Ersetzung;
10. bitgleiche H-, Perzeptions-, Dock- und Identitaetsrollen sowie genau eine
    Feldzeitfortschreibung;
11. gemeinsamen Carry und deterministische Resultat-, Zustands- und
    Receiptdigests;
12. lokale Invarianz gegen isolierte entfernte M1-Zustandslast;
13. gemeinsame Geometriepermutation ohne Listenpositionssemantik;
14. S1-QQ-G1/G4/G8-Referenzwerte und widerspruechliche Einspurzeitwerte;
15. private Import-, Export-, Seiteneffekt- und geschlossene-Zweig-Grenze;
16. Mutationsklassen 1 bis 5 und exakte Fehlercodes;
17. Mutationsklassen 6 bis 10 und exakte Fehlercodes;
18. Mutationsklassen 11 bis 16 und exakte Fehlercodes;
19. atomare `NOT_COMPUTABLE`-Paarung ohne Teiloutput;
20. wertidentische Evidence und Dauer fuer beide Spuren ohne Cross-Read.

Die neuen Tests verwenden nur kleine synthetische In-memory-Fixtures. Sie
sind technische Komponentenpruefungen, keine Feldstudie und kein
Lebenszyklusvergleich.

## Einmalige Ausfuehrungsgrenze

S1-QS darf nach vollstaendiger Implementierung genau diesen kombinierten
Testprozess einmal starten:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_m1_parallel_leak_replace_s_s1qs_compositor tests.test_m5_direct_replace_s_s1qn_compositor tests.test_a3_norm_replace_s_s1qj_compositor tests.test_neutral_local_field_substrate tests.test_w7n_capacity_function_baselines tests.test_transient_neuron_input tests.test_receptor_distributor_and_shared_field
```

Dieser Prozess ist das gesamte S1-QS-Ausfuehrungsbudget. Nicht freigegeben
sind die Gesamtsuite, ein Retry, Runner, Orchestrator, reale Medien,
Lebenszyklusprofile, Parameterwahl oder Ergebnisentscheidung.

Ein Fehlschlag darf analysiert, aber nicht innerhalb S1-QS still korrigiert
und erneut getestet werden. Eine Reparatur benoetigt einen neuen statischen
Vertrag.

## Abnahmekriterien

S1-QS ist nur technisch abgeschlossen, wenn gemeinsam gilt:

```text
PRIVATE_THREE_FILE_COMPONENT_ONLY
EXACT_S1QQ_CONFIGURATION_AND_DIGEST_CONFIRMED
TWO_DISTINCT_W7N_LEAK_STATES_CONFIRMED
SYNC_AND_TRANSIENT_M1_INTERVALS_CONFIRMED
SAME_EVIDENCE_AND_DURATION_WITH_NO_CROSS_READ_CONFIRMED
POINTWISE_EQUAL_MEAN_CONFIRMED
EXACT_REPLACE_S_AND_SHARED_A1_H_CONFIRMED
ONE_FIELD_TIME_ADVANCE_CONFIRMED
G1_G4_G8_ANALYTIC_REFERENCE_CONFIRMED
ATOMIC_FAIL_CLOSED_CONFIRMED
NO_ACTIVE_API_RUNNER_OR_RUNTIME_INTEGRATION
```

Auch eine erfolgreiche Komponentenabnahme macht das Pflichtbaselinepaket
nicht ausfuehrbar. M2 sowie die gemeinsamen Lebenszyklus-, Matrix- und
Comparatoroberflaechen bleiben offene Arbeit.

## Aussagegrenze

S1-QR spezifiziert nur eine technische M1-Gegenbaseline. Es gibt keinen
Kandidaten, keinen Feldlauf und keinen Befund zu einer hypothetischen
MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QS - begrenzte Drei-Dateien-Implementierung und einmalige technische
        Abnahme des privaten M1-Zweispurkompositors
```

S1-QS darf ausschliesslich die drei gebundenen Dateien anlegen, danach den
einen gebundenen Testprozess ausfuehren und bei Erfolg nur den tatsaechlichen
Status dokumentieren. Keine API- oder Runtimeintegration, kein Orchestrator,
kein Feldlauf und keine Ergebnisentscheidung.
