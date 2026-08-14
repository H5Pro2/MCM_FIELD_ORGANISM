# Z4-A3: Generischer P0/F3/B3-Trajektorienrunnervertrag

Stand: 2026-08-06

Status:

- generische Welt-, Arm-, Modell-, Handoff- und Trajektorienschnittstelle
  statisch gebunden;
- Implementierungsscheibe 1, rollenvariable passive Trajektorie und
  generischer Completion-Support, synthetisch abgenommen;
- Implementierungsscheibe 2, passiver P0-Completion-Callback, synthetisch
  abgenommen;
- Implementierungsscheibe 3, generischer Welt-/Arm-/Modellrunner mit exakt
  42 Aufgaben je Welt, synthetisch abgenommen;
- technisches Aufgabeninventar und Stopplinien statisch gebunden;
- Ergebnisschema und one-shot Forschungseinstieg in Z4-A4 technisch gebunden;
- kein Forschungslauf ausgefuehrt.

## Zweck

Z4-A3 schliesst die statische Runnerluecke der
[Z4-A-Mehrwelt-Vorregistrierung](Z4A_MEHRWELT_FELDENCODER_VORREGISTRIERUNG_UND_AUSFUEHRUNGSSPERRE.md).
Der Vertrag loest die wiederverwendbaren P0-, F3-, B3- und
Trajektorienbestandteile aus ihrer bisherigen Z1-Quellenbindung, ohne eine
Feldgleichung, einen Parameter oder eine Sachentscheidung zu veraendern.

Z4-A3 erzeugt keinen Forschungsauftrag. Der spaetere technische Runner darf
weder Lauf-ID noch Forschungsentscheidung enthalten.

## Statischer Bestandsbefund

### Bereits generisch verwendbar

- `run_mcm_f3_causal_comparison` akzeptiert beliebige
  `ReceptorTimeSequence`-Objekte und prueft eindeutige Quellsupports;
- `handoff_receptor_completion_groups` erzeugt einen selection-free Handoff;
- `advance_neutral_fast_shared_field_transient` bildet die exakte P0-S/H-
  Dynamik;
- `advance_mcm_f3_shared_field_transient` bildet F3 und kann einen festen
  Kopplungsrechner erhalten;
- `compute_mcm_f3_linear_coupled_baseline` bildet B3 mit demselben lokalen
  Zustands- und Geometriebudget;
- die Z1-Pfadmetrik normiert kumulative Pfadlaenge auf 101 Punkte.

### Noch Z1-gebunden

- `mcm_f3_z1_runner.py` baut seine Quelle und 6-mal-4-Geometrie selbst;
- Modell- und Arm-IDs sind fest auf Z1 codiert;
- `MCMF3Z1TrajectorySample` erzwingt fuer jedes Modell S, H und `mass`;
- der Completion-Support wird erneut aus `build_mcm_f3_z1_source()` gelesen;
- B3 und F3 werden nur unter Z1-Bezeichnungen gemeinsam ausgefuehrt;
- P0 besitzt im neutralen transienten Pfad noch keinen passiven
  Completion-Observer.

Diese Bindungen duerfen nicht durch Importtricks oder nachtraegliches
Umschreiben eines Z1-Pakets kaschiert werden. Z4-A benoetigt eigene generische
Vertraege.

## Runneridentitaet

```text
runner_contract_id:  z4a.generic-field-trajectory-runner.v1
trajectory_id:       z4a.component-trajectory.v1
support_id:          z4a.completion-support.v1
technical_packet_id: z4a.technical-packet.v1
```

Der Runner liest nur bereits technisch gebundene Rezeptorsequenzen. Er
decodiert keine Medien, startet keinen Browser und erzeugt keine Quelle.

## Weltpaket

Ein `Z4AWorldInput` muss vor jeder Feldausfuehrung unveraenderlich enthalten:

```text
world_id
world_contract_digest
source_binding_digests
modality_ids
clock_id
ticks_per_second
horizon_start_tick
horizon_end_tick
dock_anatomies
field_sample_offsets
arms
```

`dock_anatomies` und `field_sample_offsets` sind Teil der Weltbindung. Sie
werden nicht aus Dateinamen, Labels oder einem Ergebnis abgeleitet.

Gebundene Weltreihenfolge der spaeteren Vollmatrix:

1. `z4a.video.street-traffic.v1`;
2. `z4a.av.nasa-earthrise.v1`;
3. `z4a.audio.sound-mute-sound.v1`;
4. `z4a.browser.direct.reference.v2`.

Fehlt eine Welt, wird kein Drei-Welten- oder Teilpaket erzeugt.

## Quellenarme

Jedes Weltpaket enthaelt in exakt dieser Reihenfolge:

```text
reference
reproduction
partitioned
reversed
permuted
independent
```

Ein `Z4AWorldArmInput` enthaelt:

```text
arm_id
sequences
sequence_digest
proposal_steps
proposal_digest
execution_digest
```

Vor dem Feldbau muessen alle sechs Arme dieselben Modalitaeten,
Rezeptorgeometrien, Carrierreihenfolgen, Quellsupportzahlen,
Abschluss-Supports und denselben Horizont besitzen.

Zusaetzliche Regeln:

- `reference` und `reproduction` besitzen denselben Sequenzdigest;
- `partitioned` besitzt denselben Sequenzdigest wie `reference`, aber einen
  anderen Proposal-Digest;
- `reversed` und `permuted` besitzen dasselbe Werte- und Supportinventar wie
  `reference`, jedoch den vorregistrierten anderen Werteverlauf;
- `independent` besitzt dasselbe Geometrie- und Supportbudget, aber einen von
  `reference` verschiedenen Sequenzdigest;
- kein Arm darf Phasen-IDs, Welt-ID oder Medienmetadaten in den
  Rezeptorwerten tragen.

Der Runner berechnet jeden Handoff genau einmal pro Quellenarm und verwendet
dasselbe unveraenderliche Handoff-Objekt fuer P0, F3, B3 und alle
Verfeinerungen dieses Arms.

## Gemeinsames neutrales Basisfeld

Je Welt wird genau ein `SharedMCMField` ohne Substrat erzeugt. Der Feldbau
verwendet aus `reference` nur die erste Frameidentitaet jeder Modalitaet,
Carrierreihenfolge und Rezeptorgeometrie. Die Framewerte initialisieren keine
Feldaktivierung; S und H starten ueberall bei null.

Kontrollen:

```text
base_field.substrate:       None
initial_activation:         0 an jedem Feldort
initial_afterimage:         0 an jedem Feldort
base_layer_digest:          fuer alle Modelle derselben Welt identisch
dock_map_digest:            fuer alle Arme und Modelle identisch
field_position_inventory:   fuer alle Arme und Modelle identisch
```

P0 verwendet dieses Feld direkt. F3 und B3 erhalten jeweils frisch dieselbe
gleichfoermige Zusatzstate-Anfangsverteilung. Kein Modell startet aus dem
Endzustand eines anderen Modells oder Arms.

## Modellformen

### P0

```text
model_id:                         p0.exact
state_roles:                      activation, afterimage
response_time_seconds:            1.0
afterimage_time_constant_seconds: 0.5
dissipation:                      None
integration:                      exact neutral transient
refinements:                      exact
dynamic_scalar_state_budget:      2 * field_node_count
```

P0 besitzt keinen M- oder Baselinezustand. Eine technisch angehaengte
konstante Nullmasse darf weder beobachtet noch als Zustandsbudget ausgegeben
werden.

### F3

```text
model_id:                         f3.candidate
state_roles:                      activation, afterimage, mcm_mass
response_time_seconds:            1.0
afterimage_time_constant_seconds: 0.5
dissipation:                      None
lambda_sm_per_second:             1.0
kappa:                            0.5
eta:                              1.0
initial_total_mass:               1.0
integration:                      SSPRK(3,3)
refinements:                      1, 2, 4
dynamic_scalar_state_budget:      3 * field_node_count
coupling_calculator:              compute_mcm_f3_coupling
```

### B3

```text
model_id:                         b3.linear-coupled
state_roles:                      activation, afterimage, baseline_state
response_time_seconds:            1.0
afterimage_time_constant_seconds: 0.5
dissipation:                      None
lambda_sm_per_second:             1.0
kappa:                            0.5
eta:                              1.0
container_initial_total_mass:     1.0
integration:                      SSPRK(3,3)
refinements:                      1, 2, 4
dynamic_scalar_state_budget:      3 * field_node_count
coupling_calculator:              compute_mcm_f3_linear_coupled_baseline
```

B3 darf intern denselben validierten `MCMSubstrateState`-Container und dessen
bestehende Feldnamen verwenden. Sein dritter Observerwert heisst jedoch
`baseline_state`. Er wird nicht als MCM-Mass, Memory oder Organismuszustand
interpretiert.

## Aufgabeninventar

Je Welt gelten exakt:

```text
P0: 6 Quellenarme * 1 exakte Aufgabe       =  6
F3: 6 Quellenarme * 3 Verfeinerungen       = 18
B3: 6 Quellenarme * 3 Verfeinerungen       = 18
                                                --
Aufgaben je Welt                              42
Aufgaben in vier Welten                      168
```

Deterministische Aufgabenreihenfolge:

1. Weltreihenfolge;
2. Modellreihenfolge `p0.exact`, `f3.candidate`,
   `b3.linear-coupled`;
3. Quellenarmreihenfolge;
4. Verfeinerung aufsteigend.

`reproduction` ist bereits ein frisch erzeugter Quellenarm. Es wird deshalb
kein zusaetzliches verborgenes Reproduction-Flag je Aufgabe eingefuehrt.

## Rollenvariabler Trajektorienvertrag

Ein generischer `Z4ATrajectorySample` enthaelt:

```text
tick
components: geordnetes Tupel aus (component_id, values)
```

Erlaubte Komponenteninventare:

```text
p0.exact:          activation, afterimage
f3.candidate:      activation, afterimage, mcm_mass
b3.linear-coupled: activation, afterimage, baseline_state
```

Alle Wertevektoren eines Samples besitzen dieselbe Feldgeometrie. Innerhalb
einer Trajektorie bleiben Komponentenreihenfolge und Vektordimension
unveraendert. Komponenten anderer Modelle werden nicht durch Nullvektoren
aufgefuellt.

## Vollsupport und Entscheidungssupport

Der passive Observer fuehrt zwei strikt getrennte Sichten:

1. `technical_trajectory`: Start, reale Rezeptorabschluesse und zusaetzliche
   technische Proposal-Enden;
2. `decision_trajectory`: neutraler Start und ausschliesslich reale
   Rezeptorabschlussgruppen.

Der erforderliche Entscheidungssupport wird direkt aus dem bereits
validierten Handoff gebildet:

```text
required_ticks = (horizon_start_tick,) + completion_group_ticks
```

Es gibt keine Interpolation, Wertpruefung oder erneute Quellenkonstruktion bei
der Supportauswahl. Alle sechs Arme einer Welt muessen dasselbe
`required_ticks`-Inventar besitzen. `partitioned` darf nur im technischen
Vollsupport zusaetzliche leere Proposal-Enden enthalten.

Die neutrale P0-Runtime erhaelt fuer diesen Zweck spaeter einen rein passiven
Callback nach jeder vollstaendig angewendeten Abschlussgruppe und am
technischen Proposal-Ende. Der Callback darf keine Gleichung, Reihenfolge,
Rundung oder Feldtransition beeinflussen. F3 und B3 verwenden denselben
Callbackvertrag ueber ihren bestehenden State-Observer.

Observer an/aus muss fuer jede Aufgabe denselben finalen Snapshotdigest
liefern. Andernfalls wird das gesamte Weltpaket technisch gesperrt.

## Pfadmetrik und numerische Huelle

Fuer jede aktive Komponente bleibt die Z1-Metrik unveraendert:

- kumulative euklidische Pfadlaenge;
- Normierung auf `q = 0..1`;
- lineare Abtastung auf 101 Punkten;
- skalenrelative L-inf-Distanz.

Eine Komponente ist nur auswertbar, wenn ihre Referenztrajektorie eine
endliche Pfadlaenge groesser als `1e-12` besitzt. Ist `activation` oder
`afterimage` nicht auswertbar, lautet der technische Status der Welt
`FIELD_ENCODER_NOT_TECHNICALLY_STABLE`. Ein inaktiver Zusatzstate darf nicht
als positive Trennung verwendet werden.

Fuer F3 und B3 gilt je Welt, Arm und Komponente:

```text
epsilon = max(1e-12, 4 * D(2n, 4n))
```

Fuer einen Vergleich zu `reference` wird komponentenweise das Maximum der
Referenz- und Armhuelle verwendet. Zusaetzlich muss
`D(2n,4n) <= D(n,2n)` gelten.

P0 wird exakt integriert. Seine numerische Huelle ist deshalb fest
`1e-12`; es werden keine bedeutungslosen Pseudo-Verfeinerungen erzeugt.

Modelle werden nur ueber gleichnamige Komponenten direkt verglichen. Der
F3-Zusatzstate und der B3-Zusatzstate werden nicht gegeneinander umbenannt.
Die Z4-A-F3-Vorteilsentscheidung vergleicht ihre stabilen kausalen
Klassifikationen und verlangt weiterhin einen Unterschied in S oder H.

## Technische Invarianten

Vor jeder Sachmetrik muessen gleichzeitig gelten:

- Quellen-, Sequenz-, Proposal- und Ausfuehrungsdigests stimmen;
- jeder eindeutige Quellsupport wird genau einmal uebergeben;
- alle Modelle eines Arms erhalten dasselbe Handoff-Objekt;
- jedes Modell startet vom festgeschriebenen neutralen Basisfeld;
- Voll- und Entscheidungssupport sind streng geordnet;
- alle erforderlichen Completion-Ticks sind in jeder Trajektorie vorhanden;
- alle S/H-Werte sind endlich und bleiben in `-1..1`;
- F3-Gesamtmasse und B3-Gesamtstate bleiben jeweils innerhalb `1e-12` bei
  ihrem Anfangswert und lokal nichtnegativ;
- Referenz und Reproduktion bleiben innerhalb ihrer Huellen;
- Referenz und Teilungsarm besitzen identischen Entscheidungssupport;
- n/2n/4n-Konvergenz nimmt fuer F3 und B3 nicht zu;
- Observer an/aus veraendert keinen finalen Zustand;
- Zustandsbudget und Feldgeometrie bleiben waehrend jeder Aufgabe konstant;
- keine NaN-, Inf- oder Rohdatenpersistenz tritt auf.

Scheitert eine Kontrolle, endet die betreffende Welt vor jeder
Sachklassifikation mit `FIELD_ENCODER_NOT_TECHNICALLY_STABLE`. Die anderen
Welten werden nicht als Ersatzvollmatrix interpretiert.

## Technisches Paket

Das spaetere `Z4ATechnicalPacket` darf im Arbeitsspeicher enthalten:

```text
technical_packet_id
runner_contract_id
world_binding_digests
base_field_digests
task_inventory
handoff_controls
full_trajectories
decision_trajectories
final_snapshot_digests
integration_diagnostics
runtime_and_state_budgets
technical_controls
research_decision = None
run_id = None
```

Trajektorien sind nur kurzlebige Auswertungsobjekte. Die Serialisierung des
technischen Pakets muss Voll- und Entscheidungstrajektorien ablehnen. Ein
spaeteres Ergebnisartefakt darf nur Digests, Supportzahlen, skalare Metriken,
Huellen, Kontrollen, Laufzeiten und Zustandsbudgets enthalten.

## Implementierungsscheiben

Nach gesonderter Freigabe ist Z4-A3 in genau drei technischen Scheiben zu
implementieren:

1. rollenvariable passive Trajektorie und generischer Completion-Support;
2. passiver P0-Completion-Callback ohne Aenderung der neutralen Gleichung;
3. generischer Welt-/Arm-/Modellrunner mit 42 Aufgaben pro Welt.

Jede Scheibe wird nur synthetisch und ohne Forschungsnummer geprueft. Es gibt
keinen Teilwelt-Feldlauf und keine Vorabeinsicht in reale Z4-A-Sachwerte.

## Verwendete Projektquellen

- `mcm_field_organism/mcm_f3_causal_runner.py`;
- `mcm_field_organism/mcm_f3_z1_runner.py`;
- `mcm_field_organism/mcm_f3_z1_trajectory.py`;
- `mcm_field_organism/mcm_f3_z1_completion_support.py`;
- `mcm_field_organism/mcm_f3_runtime.py`;
- `mcm_field_organism/mcm_f3_baseline_coupling.py`;
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`;
- `mcm_field_organism/neutral_local_field_substrate.py`;
- `mcm_field_organism/receptor_proposal_handoff_audit.py`;
- `mcm_field_organism/shared_mcm_field.py`;
- [Z4-A1-Audiovertrag](Z4A1_REINE_AUDIO_REZEPTORSEQUENZ_UND_KONTROLLVERTRAG.md);
- [Z4-A2-Browservertrag](Z4A2_KAMERAFREIER_BROWSERWELT_REZEPTORVERTRAG.md).

## Aussagegrenze

Der Vertrag spezifiziert nur eine gemeinsame technische Ausfuehrung und
Beobachtung dreier Feldformen. Er belegt keine Wahrnehmung,
Wiedererkennung, Praegung, Semantik, Organisation, relative Feldzeit, Memory
oder KI.

## Aktuelle Entscheidung

`Z4A3_TECHNICALLY_BOUND`

Die statische Runnerluecke und alle drei Implementierungsscheiben sind
geschlossen.
Die rollenvariablen P0-, F3- und B3-Trajektorien enthalten ausschliesslich
ihre gebundenen Komponenten. Der Entscheidungssupport wird ohne
Interpolation direkt aus einem bereits validierten Handoff gebildet. Die
rollenvariable Scheibe bestand fokussiert mit `7 passed` und 6 Subtests.

Der passive P0-Callback beobachtet nach jeder vollstaendig angewendeten
Abschlussgruppe und an einem davon verschiedenen Proposal-Ende ausschliesslich
Kopien von Aktivierung und Nachhall. Observer an/aus und selbst eine Mutation
der uebergebenen Kopien lassen den finalen Snapshotdigest unveraendert. Seine
fokussierte Abnahme bestand mit `5 passed`; die verbundene Regression bestand
mit `39 passed` und 13 Subtests.

Der generische Runner bindet sechs Arme in fester Reihenfolge, erzeugt jeden
Handoff einmal und verwendet genau dieses Objekt fuer P0, F3 und B3. Sein
Aufgabeninventar umfasst 6 exakte P0-, 18 F3- und 18 B3-Aufgaben. P0 bleibt
substratfrei; F3-Mass und B3-Baseline-State bleiben getrennte Rollen. Die
fokussierte Vollabnahme bestand mit `7 passed`, die verbundene Regression mit
`49 passed` und 13 Subtests. Alle technischen Paketkontrollen waren wahr.

Finales Ergebnisschema und one-shot Einstieg sind in Z4-A4 technisch
gebunden. Die Z4-A-Vollmatrix bleibt wegen Z4-A2 gesperrt. Es wurde nur eine
kleine synthetische technische Welt ausgefuehrt und keine Laufnummer vergeben.

## Bester naechster Schritt

Z4-A2 mit kontrollierten v2-Browserassets, direktem kamerafreiem
Browser-zu-Rezeptor-Adapter und unabhaengiger Kontrollquelle implementieren.
Noch keine reale Vier-Welten-Matrix und keinen Lauf 197 starten.
