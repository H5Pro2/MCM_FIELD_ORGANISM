# S1-QW: Statischer M2-Zustands-, Kompositor-, Fehlercode- und Testbudgetvertrag

## Status und Umfang

S1-QW bindet die vollstaendige private Implementierungsoberflaeche fuer die
in S1-QU und S1-QV registrierte M2-Familie. Festgelegt werden Dateigrenze,
Konfiguration, Record- und Pufferzustand, Kompositionsordnung, atomare
Resultate, Fehlercodes, Mutationsklassen, synthetische Fixture und das
einmalige Testbudget.

S1-QW implementiert und testet nichts. Es gibt keine API-, Runtime-, Runner-
oder Orchestratorfreigabe und keinen Feldlauf.

Vertragsentscheidung:

```text
M2_REGISTERED_TWO_MODE_CONFIGURATION_AND_BOUNDED_STATE_BOUND
M2_A1_REPLACE_S_PRIVATE_COMPOSITOR_SURFACE_BOUND
M2_EIGHTEEN_FAILURE_CODES_AND_TWENTY_FIVE_TEST_METHODS_BOUND
THREE_FILE_IMPLEMENTATION_AND_SINGLE_TEST_PROCESS_BOUND
NO_IMPLEMENTATION_NO_EXECUTION
```

## Gebundene Dateigrenze

Ein spaeterer S1-QX-Schritt darf genau drei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/m2_bounded_buffer_replace_s_compositor.py` | registrierte Konfigurationen, Record, Pufferzustand, Kompositor, Receipt und Resultat |
| `tests/m2_bounded_buffer_replace_s_s1qx_fixtures.py` | kanonische Fuenf-Positionen- und Fehlermutationsfixtures |
| `tests/test_m2_bounded_buffer_replace_s_s1qx_compositor.py` | exakt 25 fokussierte Abnahmetests |

Alle vorhandenen Produktions- und Testdateien bleiben unveraendert. Das gilt
insbesondere fuer:

- `local_state_replace_s_compositor_core.py`;
- die A3-, M1- und M5-Kompositoren;
- Rezeptor-, Eingabe-, A1- und Shared-Field-Kerne;
- `current_api.py`, Paketroot und Root-Exports;
- Runtime, Runner und Orchestrator;
- Kandidaten-, E1-, DTS-1-, G2/D3- und Entwicklungsdateien.

Nach dem einmaligen Testprozess duerfen nur `README.md`,
`AKTUELLER_FORSCHUNGSWEG.md` und
`docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md` um das tatsaechliche Ergebnis
ergaenzt werden.

## Vertrags- und Registrierungsidentitaet

Der private Kompositor verwendet:

```text
CONTRACT_ID = m2-bounded-buffer-replace-s/s1qw.v1
SOURCE_S1QV_DIGEST =
6abe7781ffd1d1b238b5e3302960b41d8e98dc880432869187f8eafdb8b95810
CAPACITY_RECORDS = 2
MODE_IDS = (DELAY, REPLAY)
RECORD_SCHEMA_ID = canonical-a1-s-evidence/v1
CURRENT_FALLBACK_ID = current-a1-s/v1
```

Das Modul darf genau eine reine Konfigurationsfabrik bereitstellen:

```text
build_registered_m2_configuration(mode_id)
    -> M2BoundedBufferConfiguration
```

`M2BoundedBufferConfiguration` enthaelt genau:

- `source_registration_digest`;
- `mode_id`;
- `capacity_records`;
- `record_schema_id`;
- `current_fallback_id`.

Nur `DELAY` und `REPLAY` sind gueltig. Beide Konfigurationen unterscheiden
sich ausschliesslich in `mode_id`. Alle anderen Rollen muessen exakt der
registrierten Frischfabrik entsprechen.

## Kanonischer Evidencerecord

Das Modul bindet:

```text
M2EvidenceRecord
    s_evidence: tuple[float, ...]
    input_field_digest: str
    geometry_digest: str
    neuron_order: tuple[str, ...]
    distribution_digest: str
    interval_digest: str
    a1_proposal_digest: str
    record_digest: str
```

`record_digest` wird ausschliesslich aus den vorstehenden Nutzfeldern in
genau dieser fachlichen Payload gebildet. Der Record ist nur gueltig, wenn:

- S vollstaendig, endlich, nicht leer und innerhalb `[-1,1]` liegt;
- S-Laenge und `neuron_order` identisch sind;
- Neuronenidentitaeten eindeutig und kanonisch geordnet sind;
- alle Quelldigests gueltige kleingeschriebene SHA-256-Werte sind;
- der gespeicherte Recorddigest exakt reproduzierbar ist.

Der Typ besitzt keine Felder fuer Rohkontakte, H, vollstaendige Felder,
Kandidaten-, Observer-, Arm- oder Ergebnisrollen.

## Vollstaendiger M2-Pufferzustand

Das Modul bindet:

```text
M2BoundedBufferState
    mode_id: str
    geometry_digest: str
    neuron_order: tuple[str, ...]
    records: tuple[M2EvidenceRecord, ...]
    replay_phase: str
    replay_cursor: int
```

Fuer `DELAY` gilt:

- `replay_phase = NOT_APPLICABLE`;
- `replay_cursor = 0`;
- `records` ist aeltester zuerst geordnet und enthaelt null bis zwei
  Records.

Fuer `REPLAY` gilt:

- die Phase ist `CAPTURE`, `EMIT` oder `EXHAUSTED`;
- in `CAPTURE` enthaelt der Zustand null oder einen Record und Cursor null;
- in `EMIT` enthaelt er genau zwei Records und Cursor null oder eins;
- in `EXHAUSTED` enthaelt er genau zwei Records und Cursor zwei.

Jeder Record muss Geometrie und Neuronenordnung des Zustands tragen. Modus,
Geometrie und Ordnung sind ueber den gesamten Carry unveraenderlich. Es gibt
keinen absoluten Ereigniszaehler und keinen Zustand ausserhalb dieser Rollen.
`configuration.mode_id` und `state.mode_id` muessen bei jedem Aufruf exakt
uebereinstimmen. Ein Zustand darf nie unter der jeweils anderen
Moduskonfiguration fortgesetzt werden.

Die Frischfabrik lautet:

```text
build_empty_m2_buffer(configuration, field)
    -> M2BoundedBufferState
```

Sie liest nur Modus, Geometrie und kanonische Neuronenordnung. Der
Recordbestand ist leer. DELAY startet mit `NOT_APPLICABLE`; REPLAY startet in
`CAPTURE`.

## Private Aufrufoberflaeche

S1-QX darf genau eine neue ausfuehrende Funktion bereitstellen:

```text
advance_m2_bounded_buffer_replace_s(
    field,
    distribution,
    interval_input,
    neutral_substrate_config,
    fast_afterimage_config,
    m2_configuration,
    m2_prestate,
    dissipation_config=None,
) -> M2BoundedBufferReplaceSResult
```

`interval_input` ist exakt:

```text
MCMFieldStepTime | TransientNeuronInputSet
```

Der Typ waehlt nur den vorhandenen synchronen oder transienten A1-Fast-Pfad.
Modus und Zustand bleiben explizit und duerfen nicht aus Eingabeinhalt oder
Orchestrierungslabels abgeleitet werden.

## Gebundene Phasenordnung

Jeder fachlich erreichbare Aufruf folgt exakt:

```text
1.  api_intake
2.  common_identity_validation
3.  interval_discrimination
4.  a1_fast_proposal
5.  a1_proposal_validation
6.  evidence_record_materialization
7.  mode_transition
8.  source_selection_validation
9.  replace_s_materialization
10. final_field_validation
11. next_state_validation
12. atomic_receipt
```

Der erste Fehler beendet alle nachfolgenden Phasen. Kein Fehlerpfad darf
reparieren, umordnen, begrenzen, nachregistrieren oder erneut rechnen.

## Modusfortschreibung und Auswahl

Nach genau einem gueltigen A1-Vorschlag wird genau ein aktueller
`M2EvidenceRecord` gebildet. Eine reine private Modusfortschreibung liefert
gemeinsam:

- den vollstaendigen M2-Folgezustand;
- genau eine der fuenf S1-QU-Ausgaberollen;
- den vollstaendigen selektierten S-Vektor;
- optional genau den selektierten historischen Record;
- die begrenzte Auswahlposition.

Fuer DELAY gilt exakt:

- bei null oder einem Vorrecord: aktuelles A1-S ausgeben und aktuellen
  Record anhaengen;
- bei zwei Vorrecords: aeltesten Vorrecord ausgeben, ihn entfernen und den
  aktuellen Record anhaengen.

Fuer REPLAY gilt exakt:

- `CAPTURE`: aktuelles A1-S ausgeben und bis zu zwei Prefixrecords aufnehmen;
- `EMIT`: Record am Cursor ausgeben, Prefix unveraendert lassen und Cursor
  vorwaertssetzen;
- `EXHAUSTED`: aktuelles A1-S ausgeben und Zustand unveraendert lassen.

Eine Recordausgabe darf niemals den aktuellen Record desselben Intervalls
als historischen Record ausgeben.

## Atomare Feldkomposition

Der vorhandene private modellneutrale Hilfskern wird unveraendert verwendet
fuer Intervall- und Geometriepruefung, genau einen A1-Vorschlag,
`REPLACE_S`, Identitaetspruefung und Feldzeitkardinalitaet.

Finales S stammt vollstaendig aus der gebundenen Auswahl. Gegen den aktuellen
A1-Vorschlag bleiben bitgleich:

- H, Perzeption und Rezeptorprovenienz;
- Docks, Neuronen-, Feld- und Geometrieidentitaeten;
- Tick, Distribution und Feldzeitbezug;
- Abwesenheit aktiver Substrat- und Entwicklungszustaende.

Der A1-Vorschlag, aktuelle Record und selektierte S-Vektor werden nur durch
Digests belegt und nicht als weitere Felder oder Carryzustaende publiziert.

## Resultat- und Receiptrollen

`M2BoundedBufferReplaceSResult` enthaelt genau:

```text
field: SharedMCMField | NOT_COMPUTABLE
next_m2_state: M2BoundedBufferState | NOT_COMPUTABLE
receipt: M2BoundedBufferReplaceSReceipt
```

Ein gueltiger Receipt bindet mindestens:

- Vertrags-, S1-QV-, Modus- und Konfigurationsidentitaet;
- Intervallform sowie Feld-, Distribution- und Intervallprovenienz;
- Geometrie-, Neuronenordnungs- und M2-Vorzustandsdigest;
- internen A1-Vorschlagsdigest und aktuellen Recorddigest;
- Ausgaberolle und begrenzte Auswahlposition;
- optionalen historischen Quellrecorddigest samt seinen Quelldigests;
- Digest des vollstaendigen selektierten S-Vektors;
- M2-Folgezustandsdigest, Phase und Cursor;
- finalen Felddigest;
- Beleg vollstaendiger S-Ersetzung und H-/Provenienzidentitaet;
- Beleg genau einer Feldzeitfortschreibung;
- kanonische Phasen, Status, Fehlercodes und Receiptdigest.

Es gibt genau die Status `COMPLETED` und `NOT_COMPUTABLE`. Bei
`NOT_COMPUTABLE` sind Feld und gesamter M2-Folgezustand gemeinsam nicht
berechenbar. Record, selektiertes S oder Digest allein sind kein Sachoutput.

## Endliches Fehlervokabular

S1-QW bindet exakt diese 18 Fehlercodes in dieser Reihenfolge:

```text
QW_INPUT_TYPE_INVALID
QW_FIELD_ROLE_INVALID
QW_DISTRIBUTION_OR_INTERVAL_INVALID
QW_CONFIGURATION_INVALID
QW_M2_PRESTATE_INVALID
QW_GEOMETRY_OR_ORDER_MISMATCH
QW_A1_ADVANCE_FAILED
QW_A1_PROPOSAL_INVALID
QW_RECORD_MATERIALIZATION_FAILED
QW_RECORD_INVALID
QW_DELAY_TRANSITION_INVALID
QW_REPLAY_TRANSITION_INVALID
QW_SOURCE_SELECTION_INVALID
QW_S_REPLACEMENT_FAILED
QW_H_OR_PROVENANCE_CHANGED
QW_FIELD_TIME_CARDINALITY_FAILED
QW_NEXT_STATE_INVALID
QW_ATOMIC_OUTPUT_FAILED
```

Die Codes entsprechen der ersten erreichbaren Fehlergrenze. Ein
modusfremder Transitionfehler darf nicht anstelle des zum konfigurierten
Modus gehoerenden Codes erscheinen.

## Genau 18 Fehlermutationsklassen

Die spaetere Fixture- und Testgrenze bindet isoliert:

1. falschen Typ an einer Pflichtgrenze;
2. Feld mit Substrat- oder Entwicklungszustand;
3. unpassende Distribution oder Intervallform;
4. veraenderten S1-QV-Digest, Modus, Kapazitaet oder Schemaidentitaet;
5. unvollstaendigen, moduswidrigen oder digestinkonsistenten Vorzustand;
6. abweichende Geometrie, Knotenanzahl oder Neuronenreihenfolge;
7. kontrolliertes Scheitern des A1-Aufrufs;
8. ungueltigen oder zeitlich abweichenden A1-Vorschlag;
9. kontrolliertes Scheitern der Recordmaterialisierung;
10. nicht endlichen, bereichsverletzenden oder digestfalschen Record;
11. ungueltigen DELAY-Fuellstand oder simulierten DELAY-Uebergang;
12. ungueltige REPLAY-Phase, Cursorposition oder simulierten
    REPLAY-Uebergang;
13. falsche Ausgaberolle, Recordquelle oder Auswahlposition;
14. partielle oder falsche S-Ersetzung;
15. veraendertes H oder veraenderte Feldprovenienz;
16. zweiten Tick oder abweichendes Zeitfenster;
17. ungueltigen, uebervollen oder geometriefremden Folgezustand;
18. simuliertes Scheitern vor atomarer Resultatpublikation.

Jede Mutation muss genau ihren vorregistrierten Code liefern und Feld sowie
gesamten Pufferfolgezustand gemeinsam sperren.

## Kanonische Fuenf-Positionen-Fixture

Die spaetere Fixture verwendet genau ein synthetisches Drei-Knoten-
Auditory-Line-Feld und pro Position genau ein abgeschlossenes synchrones
Intervall von zehn Ticks bei zehn Ticks pro Sekunde. Die Intervalle sind
lueckenlos:

```text
P0 = [0,10]
P1 = [10,20]
P2 = [20,30]
P3 = [30,40]
P4 = [40,50]
```

Die aktuellen Rezeptorkontaktvektoren werden vorab gebunden als:

```text
A = ( 0.80, -0.40,  0.20)
B = (-0.60,  0.70, -0.10)
C = ( 0.30,  0.90, -0.50)
D = (-0.20, -0.80,  0.60)
E = ( 0.95, -0.15, -0.70)
```

Gemeinsam gelten:

```text
NeutralLocalFieldSubstrateConfig.response_time_seconds = 1.0
NeutralFastAfterimageConfig.time_constant_seconds = 0.5
dissipation_config = None
```

DELAY und REPLAY starten aus getrennten digestgleichen Frischfeldern und
ihren jeweiligen leeren registrierten M2-Zustaenden. Beide sehen A bis E in
derselben Reihenfolge. Die Fixture ist `NOT_COMPUTABLE`, falls die daraus
gebildeten A1-S-Records nicht die S1-QV-Bedingungen `S_A != S_B` und
`S_C != S_E` sowie paarweise verschiedene Recorddigests erfuellen. Werte,
Zeitrollen oder Geometrie duerfen dann nicht nachgebessert werden.

Zusaetzlich darf dieselbe kleine Anatomie fuer einzelne transiente
Intervalltests mit lokal vollstaendig uebergebenen Kontakten verwendet
werden. Die registrierte Fuenf-Positionen-Divergenz bleibt synchron und wird
nicht doppelt ausgefuehrt.

## Genau 25 neue Testmethoden

Die S1-QX-Abnahme prueft exakt:

1. Modul-, Typ-, Status-, Phasen- und Fehlercodeoberflaeche;
2. beide exakten S1-QV-Konfigurationen samt Registrierungsdigest;
3. deterministische getrennte DELAY- und REPLAY-Frischzustaende;
4. kanonische Recordpayloads, Digests und ausgeschlossene Rohdatenrollen;
5. gueltige synchrone DELAY-Warm-up-Schritte `P0` und `P1`;
6. gueltige synchrone rollende DELAY-Schritte `P2` bis `P4`;
7. gueltige synchrone REPLAY-Capture-Schritte `P0` und `P1`;
8. gueltige synchrone REPLAY-Emit-Schritte `P2` und `P3`;
9. gueltigen synchronen REPLAY-Exhausted-Schritt `P4`;
10. gueltigen einzelnen transienten DELAY-Schritt;
11. gueltigen einzelnen transienten REPLAY-Schritt;
12. exakte S1-QV-Ausgaberollen und Quellenfolge beider Modi;
13. exakte DELAY-Puffer- und REPLAY-Phasen-/Cursorfolge;
14. bitidentische Felder bis `P3` und erste S-Divergenz an `P4`;
15. paarweise Recorddigests sowie `S_A != S_B` und `S_C != S_E`;
16. vollstaendige signed S-Ersetzung aus aktueller oder historischer Quelle;
17. bitgleiche H-, Perzeptions-, Dock- und Identitaetsrollen sowie genau eine
    Feldzeitfortschreibung;
18. deterministischen Carry und Resultat-, Zustands- und Receiptdigests;
19. gemeinsame Geometriepermutation ohne Listenpositionssemantik;
20. Armtrennung, unveraenderte Modusidentitaet und kein Cross-State-Read;
21. private Import-, Export-, Seiteneffekt- und geschlossene-Zweig-Grenze;
22. Mutationsklassen 1 bis 6 und exakte Fehlercodes;
23. Mutationsklassen 7 bis 12 und exakte Fehlercodes;
24. Mutationsklassen 13 bis 18 und exakte Fehlercodes;
25. atomare `NOT_COMPUTABLE`-Paarung ohne Teiloutput.

Die Tests sind kleine synthetische In-memory-Komponentenpruefungen. Sie sind
keine Feldstudie und kein Lebenszyklusvergleich.

## Einmalige Ausfuehrungsgrenze

S1-QX darf nach vollstaendiger Implementierung genau diesen kombinierten
Testprozess einmal starten:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_m2_bounded_buffer_replace_s_s1qx_compositor tests.test_m1_parallel_leak_replace_s_s1qs_compositor tests.test_m5_direct_replace_s_s1qn_compositor tests.test_a3_norm_replace_s_s1qj_compositor tests.test_neutral_local_field_substrate tests.test_w7n_capacity_function_baselines tests.test_transient_neuron_input tests.test_receptor_distributor_and_shared_field
```

Dieser Prozess ist das gesamte S1-QX-Ausfuehrungsbudget. Nicht freigegeben
sind Gesamtsuite, Retry, Runner, Orchestrator, reale Medien,
Lebenszyklusprofile, Parameterwahl oder Ergebnisentscheidung.

Ein Fehlschlag darf analysiert, aber nicht innerhalb S1-QX still korrigiert
und erneut getestet werden. Eine Reparatur benoetigt einen neuen statischen
Vertrag.

## Abnahmekriterien

S1-QX ist nur technisch abgeschlossen, wenn gemeinsam gilt:

```text
PRIVATE_THREE_FILE_COMPONENT_ONLY
EXACT_S1QV_CONFIGURATION_CAPACITY_AND_DIGEST_CONFIRMED
CANONICAL_A1_S_RECORD_WITHOUT_RAW_DATA_CONFIRMED
SYNC_AND_TRANSIENT_M2_INTERVALS_CONFIRMED
DELAY_WARMUP_AND_ROLLING_SELECTION_CONFIRMED
REPLAY_CAPTURE_EMIT_EXHAUSTED_CONFIRMED
P0_P4_SOURCE_SCHEDULE_AND_FIRST_DIVERGENCE_CONFIRMED
EXACT_REPLACE_S_AND_CURRENT_A1_H_CONFIRMED
ONE_FIELD_TIME_ADVANCE_PER_INTERVAL_CONFIRMED
ATOMIC_FAIL_CLOSED_CONFIRMED
NO_ACTIVE_API_RUNNER_OR_RUNTIME_INTEGRATION
```

Auch eine erfolgreiche Komponentenabnahme macht das Pflichtbaselinepaket
nicht ausfuehrbar. Die gemeinsame Lebenszyklus-, Matrix- und
Comparatoroberflaeche bleibt offene Arbeit.

## Aussagegrenze

S1-QW spezifiziert nur eine technische M2-Gegenbaseline. Es gibt keinen
Kandidaten, keinen Feldlauf und keinen Befund zu einer hypothetischen
MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QX - begrenzte Drei-Dateien-Implementierung und einmalige technische
        Abnahme des privaten M2-Pufferkompositors
```

S1-QX darf ausschliesslich die drei gebundenen Dateien anlegen, danach den
einen gebundenen Testprozess ausfuehren und bei Erfolg nur den tatsaechlichen
Status dokumentieren. Keine API- oder Runtimeintegration, kein Orchestrator,
kein Feldlauf und keine Ergebnisentscheidung.
