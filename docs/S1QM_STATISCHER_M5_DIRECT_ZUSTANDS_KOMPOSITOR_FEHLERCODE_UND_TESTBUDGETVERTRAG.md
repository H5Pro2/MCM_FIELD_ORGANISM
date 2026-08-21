# S1-QM: Statischer M5_DIRECT-Zustands-, Kompositor-, Fehlercode- und Testbudgetvertrag

## Status und Umfang

S1-QM bindet ausschliesslich die spaetere begrenzte Implementierung von
`M5_DIRECT_LOCAL_STATE` aus S1-QL. Der Vertrag legt fest:

- das vollstaendige private M5-Zustandsinventar;
- die unveraenderte W7-N-`LEAK`-Konfigurationsidentitaet;
- einen modellneutralen privaten A1/REPLACE_S-Hilfskern;
- getrennte A3-NORM- und M5_DIRECT-Modulrollen;
- eine atomare M5-Aufruf-, Resultat- und Receiptoberflaeche;
- vierzehn deterministische Fehlercodes und Mutationsklassen;
- genau achtzehn neue Testmethoden und einen Einmallauf.

S1-QM enthaelt keine neue Gleichung, Parameterwerte, Fixturewerte,
Implementierung, Runtimeintegration oder Ausfuehrung. Es wird kein Feldlauf
und keine Ergebnisentscheidung freigegeben.

Verbindliche Entscheidung:

```text
M5_DIRECT_COMPLETE_LOCAL_STATE_AND_REGISTERED_LEAK_SPEC_BOUND
MODEL_NEUTRAL_A1_REPLACE_S_PRIVATE_CORE_EXTRACTION_BOUND
A3_NORM_AND_M5_DIRECT_MODEL_SEMANTICS_REMAIN_SEPARATE
M5_ATOMIC_RESULT_FAILURE_CODES_AND_SINGLE_TEST_BUDGET_BOUND
NO_EQUATIONS_NO_VALUES_NO_IMPLEMENTATION_NO_EXECUTION
```

## Gebundene Dateigrenze

Ein spaeterer S1-QN-Schritt darf genau diese fuenf Dateien bearbeiten:

| Datei | Aenderung | Aufgabe |
|---|---|---|
| `mcm_field_organism/local_state_replace_s_compositor_core.py` | neu | modellneutrale kanonische A1/REPLACE_S-Hilfen |
| `mcm_field_organism/a3_norm_replace_s_compositor.py` | Refaktorierung | identische A3-Funktion ueber den neuen neutralen Hilfskern |
| `mcm_field_organism/m5_direct_replace_s_compositor.py` | neu | M5_DIRECT-Modellvalidierung, Fortschreibung, Receipt und Resultat |
| `tests/m5_direct_replace_s_s1qn_fixtures.py` | neu | kleine kanonische Gueltig- und Fehlermutationsfixtures |
| `tests/test_m5_direct_replace_s_s1qn_compositor.py` | neu | exakt achtzehn fokussierte Abnahmetests |

Bestehende A3-Fixtures und A3-Tests bleiben unveraendert. Alle anderen
Produktions-, Test-, Runner-, Runtime- und API-Dateien bleiben ebenfalls
unveraendert. Nach dem Einmallauf duerfen nur die drei vorrangigen
Statusdokumente um das tatsaechliche Ergebnis ergaenzt werden.

Insbesondere bleiben gesperrt:

- `mcm_field_organism/current_api.py` und Root-Exports;
- der primaere `SharedMCMField`- und A1-Fast-Kern;
- der vorhandene W7-N-Kern;
- Orchestrator-, Runner-, Medien- und Lebenszyklusmodule;
- Kandidaten-, Substrat-, Entwicklungs-, G2/D3- und DTS-1-Module.

## Modellneutraler privater Hilfskern

`local_state_replace_s_compositor_core.py` darf nur Rollen enthalten, die
fuer A3-NORM und M5_DIRECT wert- und bedeutungsgleich sind:

- kanonisches JSON und SHA-256 fuer technische Payloads;
- vollstaendiger Feld- und Geometriedigest;
- kanonische synchrone oder transiente Intervallprojektion;
- Pruefung der neutralen Feld-, Distribution- und Intervallidentitaet;
- genau ein Aufruf des passenden vorhandenen A1-Fast-Pfads;
- Validierung des internen vollstaendigen A1-Vorschlags;
- vollstaendige positionsgleiche `REPLACE_S`-Materialisierung;
- Pruefung unveraenderter H-, Perzeptions-, Dock-, Identitaets- und
  Feldzeitrollen;
- Berechnung der Anzahl technischer Feldzeitfortschreibungen.

Der Hilfskern darf nicht enthalten:

- Modellkennung `norm`, `leak`, A3 oder M5;
- W7-M-Spezifikationsauswahl oder W7-N-Zustandsfortschreibung;
- NORM-Skalierungsrecord oder globalen Nenner;
- M5-Direktoutput- oder Einzustandsprognose;
- Receiptstatus, Fehlercode oder Abschlussentscheidung;
- Arm-, Kandidaten-, Comparator- oder Ergebnisinformation.

Er ist privat und wird weder aus `current_api` noch aus dem Paketroot
exportiert.

## A3-Refaktorierungsinvariante

Die A3-Datei darf nur ihre bereits vorhandenen modellneutralen Hilfen durch
Imports aus dem neuen privaten Kern ersetzen. Unveraendert bleiben muessen:

- `CONTRACT_ID`, Status, Phasen und alle vierzehn A3-Fehlercodes;
- die oeffentliche private Funktion `advance_a3_norm_replace_s`;
- Argumentreihenfolge, Resultat- und Receipttypen;
- NORM-Spezifikationspruefung, Zustand und Skalierungsprovenienz;
- synchrone und transiente Outputs;
- kanonische Resultat- und Receiptdigests;
- Fail-Closed-Reihenfolge und `NOT_COMPUTABLE`-Paarung.

Eine Digest- oder Verhaltensaenderung ist kein zulaessiger Refaktorierungseffekt.
Scheitert diese Invariante im Einmallauf, wird M5 nicht teilweise akzeptiert.

## Vollstaendiges M5-Zustandsinventar

M5_DIRECT traegt genau einen `W7NLocalBaselineState` mit:

- Modellrolle `leak`;
- genau einer endlichen lokalen Koordinate pro kanonischem Feldknoten;
- derselben Knotenanzahl und Reihenfolge wie das vollstaendige Feld;
- einem unabhaengigen W7-N-Nullfrischzustand pro Arm;
- einem kanonischen Vor- beziehungsweise Folgezustandsdigest.

Nicht zum M5-Zustand gehoeren:

- A1-S, H, Rezeptorkontakt oder Feldreadout;
- vorheriger direkter Output;
- NORM-Nenner oder Skalierungsrecord;
- M-, Edge-, Ressourcen- oder Entwicklungszustand;
- Puffer, Replayfolge, Ereigniszaehler oder Checkpointrolle;
- Arm-, Familien-, Ziel- oder Ergebnislabel.

Nach einem gueltigen Intervall wird nur der vollstaendige lokale
`LEAK`-Folgezustand gemeinsam mit dem finalen Feld getragen.

## Konfigurationsbindung

Zulaessig ist ausschliesslich die unveraenderte registrierte
W7-M-Baselinespezifikation mit Modellrolle `leak`, wie sie
`build_w7m_capacity_function_matrix_adapter` bereits liefert.

Der spaetere Kompositor darf:

- die registrierte Spezifikation exakt vergleichen;
- `build_zero_w7n_local_baseline` fuer den Frischzustand verwenden;
- `advance_w7n_local_baseline` genau einmal pro Intervall aufrufen.

Er darf keine lokale Gleichung kopieren, keinen Zeitparameter neu binden,
keinen alternativen `LEAK`-Kern waehlen und keine SAT- oder
NORM-Spezifikation akzeptieren.

## Private Aufrufoberflaeche

S1-QN darf genau eine neue ausfuehrende M5-Funktion bereitstellen:

```text
advance_m5_direct_replace_s(
    field,
    distribution,
    interval_input,
    neutral_substrate_config,
    fast_afterimage_config,
    leak_spec,
    m5_prestate,
    dissipation_config=None,
) -> M5DirectReplaceSResult
```

`interval_input` ist exakt:

```text
MCMFieldStepTime | TransientNeuronInputSet
```

Der Typ waehlt nur den vorhandenen synchronen oder transienten A1-Fast-Pfad.
Eine implizite Konvertierung, Doppelbelegung oder Auswahl durch
Orchestrierungslabels ist unzulaessig.

## Gebundene Phasenordnung

Jeder fachlich erreichbare Aufruf folgt exakt:

```text
1. api_intake
2. common_identity_validation
3. interval_discrimination
4. a1_fast_proposal
5. a1_proposal_validation
6. m5_leak_advance
7. direct_output_validation
8. replace_s_materialization
9. final_field_validation
10. atomic_receipt
```

Der erste Fehler beendet alle nachfolgenden Phasen. Kein Fehlerpfad darf
Werte reparieren, umsortieren, begrenzen, normalisieren oder erneut rechnen.

## Direkte Outputinvariante

Das vorhandene W7-N-`LEAK`-Resultat ist nur gueltig, wenn:

- Folgezustand und Output vollstaendig und endlich sind;
- beide dieselbe kanonische Ortsanzahl besitzen;
- der Output an jedem Ort exakt dem vorhandenen lokalen Folgezustand
  entspricht;
- keine SAT-Begrenzung oder NORM-Skalierung auftritt;
- der Output nicht als zusaetzlicher Carryzustand gespeichert wird.

Diese Pruefung fuegt keinen Readout hinzu. Sie bestaetigt die bereits
vorhandene direkte `LEAK`-Outputsemantik.

## Atomare Feldkomposition

Der M5-Kompositor muss intern genau diese Kausalordnung einhalten:

```text
gueltige Eingaben
    -> genau ein vollstaendiger A1-Fast-Vorschlag
    -> dessen vollstaendiges S als LEAK-Evidence
    -> genau ein vollstaendiges W7-N-LEAK-Resultat
    -> finales Feld durch vollstaendige S-Ersetzung
    -> genau ein atomarer Resultatabschluss
```

Gegen den A1-Vorschlag muessen bitgleich bleiben:

- Feld-, Schicht-, Geometrie- und Knotenidentitaeten;
- Positionen, Docks, Modalitaetsrollen und Perzeptionen;
- H an jedem Feldknoten;
- Tick, Distribution und Feldzeitbezug;
- Abwesenheit von Substrat- und Entwicklungszustand.

Der interne A1-Vorschlag und der direkte Output werden nur durch Digests
belegt. Sie sind weder separates Feldresultat noch zusaetzlicher Carry.

## Resultat- und Receiptrollen

`M5DirectReplaceSResult` enthaelt genau:

```text
field: SharedMCMField | NOT_COMPUTABLE
next_m5_state: W7NLocalBaselineState | NOT_COMPUTABLE
receipt: M5DirectReplaceSReceipt
```

Ein gueltiger Receipt bindet mindestens:

- Vertrags- und registrierte Konfigurationsidentitaet;
- Intervallform und Eingabeprovenienz;
- Feldvorzustands-, M5-Vorzustands- und Geometriedigest;
- internen A1-Vorschlagsdigest;
- M5-Folgezustandsdigest;
- Digest des vollstaendigen signed direkten Outputs;
- Beleg der exakten Zustands-/Outputidentitaet;
- finalen Felddigest;
- Beleg vollstaendiger S-Ersetzung und H-Identitaet;
- Beleg genau einer Feldzeitfortschreibung;
- Phasen, Status, Fehlercodes und Receiptdigest.

Es gibt genau die Status `COMPLETED` und `NOT_COMPUTABLE`. Bei
`NOT_COMPUTABLE` sind Feld und M5-Folgezustand gemeinsam nicht berechenbar.
Diagnostik oder Digest allein ist kein Sachoutput.

## Endliches Fehlervokabular

S1-QN bindet exakt diese vierzehn Fehlercodes:

```text
QM_INPUT_TYPE_INVALID
QM_FIELD_ROLE_INVALID
QM_DISTRIBUTION_OR_INTERVAL_INVALID
QM_CONFIGURATION_INVALID
QM_M5_PRESTATE_INVALID
QM_GEOMETRY_OR_ORDER_MISMATCH
QM_A1_ADVANCE_FAILED
QM_A1_PROPOSAL_INVALID
QM_LEAK_ADVANCE_FAILED
QM_DIRECT_OUTPUT_INVALID
QM_S_REPLACEMENT_FAILED
QM_H_OR_PROVENANCE_CHANGED
QM_FIELD_TIME_CARDINALITY_FAILED
QM_ATOMIC_OUTPUT_FAILED
```

Die Codes sind eindeutig, deterministisch und in der gebundenen
Pruefreihenfolge sortiert. Kein Fehler erzeugt einen reparierten Wert oder
Teiloutput.

## Genau vierzehn Fehlermutationsklassen

Die spaetere Fixturedatei bindet isoliert:

1. falschen Typ an einer Pflichtgrenze;
2. Feld mit Substrat- oder Entwicklungszustand;
3. unpassende Distribution oder Intervallform;
4. nicht registrierte, SAT- oder NORM-Konfiguration;
5. falschen oder unvollstaendigen M5-Vorzustand;
6. abweichende Knotenanzahl oder Ortsordnung;
7. kontrolliertes Scheitern des A1-Aufrufs;
8. ungueltigen oder zeitlich abweichenden A1-Vorschlag;
9. kontrolliertes Scheitern des W7-N-`LEAK`-Aufrufs;
10. unvollstaendigen, nicht endlichen oder nicht direkten Output;
11. partielle oder falsche S-Ersetzung;
12. veraendertes H oder veraenderte Feldprovenienz;
13. zweiten Tick oder abweichendes Zeitfenster;
14. simuliertes Scheitern vor atomarer Resultatpublikation.

Jede Mutation muss genau ihren vorregistrierten Code liefern und Feld sowie
Folgezustand gemeinsam sperren.

## Genau achtzehn neue Testmethoden

Die S1-QN-Abnahme prueft exakt:

1. Modul-, Typ-, Status-, Phasen- und Fehlercodeoberflaeche;
2. deterministische kanonische Frischfixtures;
3. gueltigen synchronen M5_DIRECT-Schritt;
4. gueltigen transienten M5_DIRECT-Schritt;
5. exakte Uebereinstimmung mit dem vorhandenen W7-N-`LEAK`-Kern;
6. vollstaendige signed S-Ersetzung ohne Zusatzreadout;
7. bitgleiche H-, Perzeptions-, Dock- und Identitaetsrollen;
8. genau eine Feldzeitfortschreibung in beiden Intervallformen;
9. gemeinsamen Carry aus finalem Feld und M5-Folgezustand;
10. deterministische Resultat- und Receiptdigests;
11. Nullzustands- und Nulloutputstruktur;
12. lokale Invarianz gegen isolierte entfernte M5-Zustandslast;
13. gemeinsame Geometriepermutation ohne Listenpositionssemantik;
14. private Import-, Export-, Seiteneffekt- und A3-Refaktorierungsgrenze;
15. Mutationsklassen 1 bis 5 und exakte Fehlercodes;
16. Mutationsklassen 6 bis 10 und exakte Fehlercodes;
17. Mutationsklassen 11 bis 14 und exakte Fehlercodes;
18. atomare `NOT_COMPUTABLE`-Paarung ohne Teiloutput.

Die neuen Tests verwenden nur kleine synthetische In-memory-Fixtures. Sie
sind Komponentenpruefungen, keine Feldstudie.

## Einmalige Ausfuehrungsgrenze

S1-QN darf nach vollstaendiger Implementierung genau diesen kombinierten
Testprozess einmal starten:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_m5_direct_replace_s_s1qn_compositor tests.test_a3_norm_replace_s_s1qj_compositor tests.test_neutral_local_field_substrate tests.test_w7n_capacity_function_baselines tests.test_transient_neuron_input tests.test_receptor_distributor_and_shared_field
```

Dieser Prozess ist das gesamte S1-QN-Ausfuehrungsbudget. Nicht freigegeben
sind die Gesamtsuite, ein Retry, Runner, Orchestrator, reale Medien,
Profilvergleich, Parameterwahl oder Ergebnisentscheidung.

Ein Fehlschlag darf analysiert, aber nicht innerhalb von S1-QN still
korrigiert und erneut getestet werden. Eine Reparatur benoetigt einen neuen
statischen Vertrag.

## Abnahmekriterien

S1-QN ist nur technisch abgeschlossen, wenn gemeinsam gilt:

```text
PRIVATE_COMPONENT_ONLY
MODEL_NEUTRAL_CORE_CONTAINS_NO_NORM_OR_M5_SEMANTICS
A3_NORM_OUTPUTS_AND_DIGESTS_UNCHANGED
REGISTERED_W7N_LEAK_KERNEL_REUSED
SYNC_AND_TRANSIENT_M5_INTERVALS_CONFIRMED
DIRECT_OUTPUT_EQUALS_LOCAL_NEXT_STATE
EXACT_REPLACE_S_AND_SHARED_A1_H_CONFIRMED
ONE_FIELD_TIME_ADVANCE_CONFIRMED
ATOMIC_FAIL_CLOSED_CONFIRMED
NO_ACTIVE_API_RUNNER_OR_RUNTIME_INTEGRATION
```

Auch eine erfolgreiche Komponentenabnahme macht das Pflichtbaselinepaket
noch nicht ausfuehrbar. M1, M2 und die gemeinsamen Lebenszyklus-, Matrix- und
Comparatorrollen bleiben getrennte offene Arbeit.

## Aussagegrenze

S1-QM spezifiziert nur den technischen M5_DIRECT-Vertreter. Es gibt keinen
Kandidaten, keinen Feldlauf und keinen Befund zu einer hypothetischen
MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QN - begrenzte Implementierung, A3-Refaktorierung und einmalige
        technische Abnahme des privaten M5_DIRECT-Kompositors
```

S1-QN darf ausschliesslich die fuenf gebundenen Dateien bearbeiten, danach
den einen gebundenen Testprozess ausfuehren und bei Erfolg nur den
tatsaechlichen Status dokumentieren. Keine API- oder Runtimeintegration,
kein Orchestrator, kein Feldlauf und keine Ergebnisentscheidung.
