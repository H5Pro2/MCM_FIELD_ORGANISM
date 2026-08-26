# S1-ST: Statischer Artefakt-zu-Comparator-Eignungs- und Provenienzaudit

## Auftrag und Grenze

S1-ST prueft ausschliesslich, ob das in S1-SS publizierte Artefakt die
bereits vor dem Lauf gebundenen Vollstaendigkeits- und
Provenienzanforderungen fuer einen spaeteren technischen Comparator traegt.

Es wurde kein Modell aufgerufen, kein Test wiederholt, kein Kontrast
berechnet und keine Metrik, Toleranz, Rangfolge oder Ergebnisrichtung
gewaehlt.

## Gepruefte Artefaktoberflaeche

Der strikte Parser bestaetigt unveraendert:

```text
status                       = COMPLETED
ordered_cell_summaries       = 238
ordered_checkpoint_records   = 560
per_role_configuration       = 14
plan_roles                   = 17
checkpoint_positions/role    = 40
```

Jeder Zellsummary bindet Ordinal, Modellrolle, Planposition und -rolle,
Manifest-, Registrierungs-, Fixture- und Konfigurationsidentitaet,
Refinement, terminalen Carry- und Ereigniskettendigest, seine geordneten
Checkpointdigests sowie Summary- und Matrixkettendigest.

Jeder Checkpoint bindet:

```text
Modell-, Plan- und Checkpointrolle
Checkpoint- und Feldtick
Fixtureereignis- und Ereigniskettendigest
Feld-, Carry- und Privatstatusdigest
Konfigurations- und Abhaengigkeitsdigests
Distributionsdigest
vollstaendigen signed Rezeptorkontaktvektor
vollstaendigen signed Aktivierungsvektor S
vollstaendigen signed Nachhallvektor H
Alignreceipt soweit fuer diese Ereignisposition zulaessig
Checkpointdigest
```

Alle drei Vektoren besitzen exakt vier Komponenten in der in S1-SI
gebundenen Ordnung `node-a, node-b, node-c, node-d`. `activation` ist S,
`afterimage` ist H.

## Gruppen- und Provenienzaudit

Die 560 Records bilden exakt 40 Plan-/Checkpointgruppen mit jeweils 14
Modellrollen. Fuer jede Gruppe sind Checkpointtick, Fixtureereignisdigest,
vollstaendiger Rezeptorkontakt und gemeinsamer Feldendtick zwischen allen
Rollen bitgleich. Es gibt keine abweichende oeffentliche
Expositionsgeschichte innerhalb einer Vergleichsgruppe.

Alle 560 Checkpoints lassen sich eindeutig einem Zellsummary und dessen
geordneter Checkpointdigestliste zuordnen. Alle 40 Gruppen lassen sich
eindeutig gegen das aus der digestgebundenen Registrierung neu gebildete
kanonische Fixture rekonstruieren. Es gibt:

```text
public_provenance_group_failures  = 0
fixture_reconstruction_failures   = 0
summary_checkpoint_join_failures  = 0
```

Die Abhaengigkeitsachse ist in allen Checkpoints exakt:

```text
configuration_binding
registered_edge_inventory
native_edge_inventory
registered_geometry
native_geometry
```

Die beiden zustandslosen Rollen `A0_CURRENT_CONTACT` und `A1_FAST_SH`
tragen durchgehend die kanonische `None`-Markierung. Die uebrigen Rollen
tragen Privatstatusdigests. `PRE_COMPETITION` und `POST_COMPETITION`
besitzen vertragsgemaess kein Alignreceipt, weil sie vor dem Align liegen;
`ALIGNED_PRE_PROBE` und `POST_PROBE_READOUT` tragen den zugehoerigen
Alignbeleg.

## Rekonstruktionspflicht statt stiller Annahmen

Das Artefakt traegt nicht jeden abgeleiteten Beleg redundant in jedem
Checkpoint. Insbesondere werden Plandigest, Geometriedigest, Knotenordnung
und oeffentlicher Frischprojektionsdigest ueber die gemeinsame
Artefaktidentitaet gebunden und muessen von einem spaeteren Consumer aus
den exakt bytegebundenen Eingaben rekonstruiert werden:

```text
physical_geometry_digest
  e0c416cc4aa97a66960640a2ff8fbe5d75edcc1f7a603c66b1efbf09ea820884
public_fresh_projection_digest
  ce6912af2bc94458c2ba4243fa6df7b8b05494d956ef96730f4faf7ec5a8a879
reconstructable_plan_digests = 17
```

Ein Comparator darf deshalb nicht nur die Ergebnisdatei lose laden. Sein
spaeterer Preflight muss zwingend:

1. das Artefakt streng und bytekanonisch parsen;
2. Quellinventar und beide Eingabedateidigests erneut pruefen;
3. Manifest und Registrierung gemeinsam validieren;
4. das kanonische Fixture neu bilden und seinen Digest verlangen;
5. jeden Checkpoint ueber Planposition, Rolle, Ereignisdigest und
   Summarydigestliste eindeutig verbinden;
6. erst danach die vollstaendigen S-/H-Vektoren als Comparatorinput
   freigeben.

Fehlt eine dieser Rekonstruktionen, ist der Comparatorinput
`NOT_COMPUTABLE`. Positionsnummern, Dateinamen oder aktuelle Projektwerte
duerfen keinen Digestbeleg ersetzen.

## Ausschluesse fuer die spaetere Auswertung

Die vorhandenen Feld-, Carry-, Privatstatus- und Distributionsdigests sind
Integritaets- und Identitaetsbelege. Sie sind keine numerischen Distanzen
und duerfen nicht als Ersatz fuer die vollstaendigen signed S-/H-Vektoren
verwendet werden.

Die Rollenordnung ist keine Rangfolge. Ein spaeterer Comparator darf weder
beim ersten passenden Modell stoppen noch Toleranzen aus den vorhandenen
Werten ableiten. Kandidatenbilanz, neue Ressourcenmechanik und private
Rohzustaende gehoeren nicht zum Comparatorinput.

## Auditentscheidung

```text
S1_SS_ARTIFACT_CONDITIONALLY_COMPARATOR_INPUT_READY
REQUIRES_STRICT_MANIFEST_REGISTRATION_FIXTURE_RECONSTRUCTION
NO_MATRIX_RERUN_REQUIRED
NO_METRIC_NO_COMPARISON_NO_FUNCTIONAL_DECISION
```

Die Bedingung ist technisch schliessbar; es fehlt keine nur durch einen
neuen Matrixlauf erzeugbare Pflichtinformation. Der einzige naechste
Schritt ist S1-SU als statischer Comparator-Eingabe-, Kontrast-, Metrik-,
Toleranz- und Falsifikationsvertrag. Alle Regeln muessen vor der ersten
numerischen Auswertung feststehen. S1-SU darf keinen Comparator
implementieren und keine Ergebniswerte lesen oder entscheiden.
