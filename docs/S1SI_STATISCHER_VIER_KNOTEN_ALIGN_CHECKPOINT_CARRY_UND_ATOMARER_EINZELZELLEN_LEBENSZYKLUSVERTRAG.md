# S1-SI: Statischer Vier-Knoten-Align-, Checkpoint-, Carry- und atomarer Einzelzellen-Lebenszyklusvertrag

## Status und Umfang

S1-SI bindet die aeussere technische Lebenszyklushuelle fuer genau eine
spaetere Zelle aus einer Modellrolle und einem der 17 technisch
abgenommenen S1-SF-Plaene.

Der Vertrag legt fest:

- wie ein Frischbundle einmalig montiert wird;
- wie synchrone Fixtureintervalle lueckenlos aufgerufen werden;
- wie das zeitlose Alignziel als gueltiger Feldcarry materialisiert wird;
- wie passive Checkpoints intern erfasst werden;
- wie der Carry nach Align neu gebunden wird;
- wie Erfolg oder Fehler atomar publiziert werden.

S1-SI implementiert nichts, fuehrt keinen Test, keinen Modellaufruf und
keine Matrixzelle aus und trifft keine Ergebnisentscheidung.

Vertragsentscheidung:

```text
ONE_MODEL_ROLE_BY_ONE_EXPOSURE_PLAN_CELL_LIFECYCLE_BOUND
ALIGN_REPLACES_CURRENT_DISTRIBUTION_PROJECTION_WITHOUT_TIME_ADVANCE
PRIVATE_STATE_IDENTITY_AND_FIELD_TIME_PRESERVED_ACROSS_ALIGN
CHECKPOINTS_PASSIVE_AND_CELL_PUBLICATION_ATOMIC
NO_IMPLEMENTATION_NO_TEST_NO_MODEL_EXECUTION
```

## Bestandsbefund zur Alignkompatibilitaet

`SharedMCMField` prueft konstruktiv, dass `last_distribution` exakt zu den
aktuellen `MCMFieldPerception.receptor_contact`-Werten aller Knoten passt.
Eine Feldkopie mit Nullkontakten und unveraenderter vorheriger
Kontaktverteilung ist deshalb ungueltig.

Die S1-SF-Formulierung, der historische `last_distribution`-Beleg bleibe im
ausgerichteten Feld selbst erhalten, ist technisch nicht anschliessbar. S1-SI
ersetzt genau diesen Teil:

- der vollstaendige Vor-Align-Distributionsdigest bleibt im aeusseren
  Alignreceipt erhalten;
- das ausgerichtete Feld erhaelt eine eigene Nullframe-
  Projektionsdistribution fuer dieselbe abgeschlossene Zeitgrenze;
- kein Modell wird aufgerufen und weder gemeinsame Feldzeit noch Layertick
  schreiten fort.

Damit bleibt die Kausalprovenienz erhalten, ohne einen intern
widerspruechlichen Feldzustand zu erzeugen.

## Zellenidentitaet

Eine Einzelzelle wird aeusserlich durch genau folgende Identitaeten
bestimmt:

```text
matrix_registration_digest
exposure_fixture_digest
model_role
exposure_plan_position
exposure_plan_role
fresh_manifest_digest
model_configuration_digest
refinement_or_none
```

Planrolle und Position sind nur Huellemetadaten. Sie gelangen niemals in
`invoke_four_node_model`.

Jede Zelle startet aus einem eigenen Aufruf von
`build_four_node_role_fresh_bundle` und genau einer anschliessenden
`assemble_four_node_model_input`-Operation. Ein Frischbundle, Assembly oder
Carry darf von keiner anderen Zelle uebernommen werden.

## Gemeinsame Refinementbindung

Die vier F3-Rollen B3 bis B6 erhalten an jeder ihrer 127
Intervallpositionen:

```text
refinement = 2
```

Alle anderen zehn Rollen erhalten:

```text
refinement = None
```

Der Wert `2` ist der kleinste in der technisch abgenommenen
Vier-Knoten-Aufrufoberflaeche bereits verwendete nichttriviale positive
Integrationskontrollwert. Er bleibt ueber Replik, Ereignis und F3-Rolle
konstant. Er ist kein Ergebnisfit und darf nicht nach einem Zwischenstand
veraendert werden.

## Intervalloperation

Bei einem Fixtureereignis `INTERVAL` gilt:

1. Die Huelle entnimmt nur `distribution` und `step_time` aus dem
   kanonischen Ereignis.
2. Beim ersten Intervall ist die validierte Assembly Aufrufquelle; danach
   ausschliesslich der vollstaendige vorherige Carry.
3. `distribution.field_time` und `step_time` muessen wertgleich sein.
4. Der Starttick muss exakt dem Endtick der vorherigen modellwirksamen
   Distribution entsprechen; beim ersten Intervall muss er `0` sein.
5. Die Rolle erhaelt den oben gebundenen Refinementwert oder `None`.
6. Genau ein `invoke_four_node_model`-Aufruf ist zulaessig.
7. Nur `COMPLETED`, `field_time_advance_count=1` und ein vollstaendiger
   `next_carry_or_none` erlauben den internen Fortschritt.

Nach Erfolg muessen zusaetzlich gelten:

- Output-`last_distribution` ist wertgleich zum Fixtureinput;
- der gemeinsame Feldzeit-Endtick entspricht dem Ereignisende;
- der Layertick ist gegenueber dem Vorfeld exakt um eins gestiegen;
- Folgetick, Geometrie, Modellrolle, Konfiguration und Digestrollen passen;
- fuer B3-B6 referenziert der private Wrapper weiterhin exakt dasselbe
  Substratobjekt wie das Folgefeld;
- der neue Carry ist die einzige Quelle der Folgeoperation.

Ein Ergebnis wird intern als Ereignisreceipt gebunden, aber noch nicht nach
aussen publiziert.

## Zeitlose Alignprojektion

Ein Fixtureereignis `ALIGN_READOUT_SH` ist nur nach mindestens einem
erfolgreichen Modellintervall und unmittelbar vor
`ALIGNED_PRE_PROBE` zulaessig.

Sei `t` der im Alignziel gebundene gemeinsame Feldzeit-Endtick. Die
Projektionsdistribution traegt:

```text
field clock       = mcm.s1sf.field
field window      = [t-10, t)
source clock      = mcm.s1sf.source
source window     = [t-10, t)
snapshot_id       = s1si.align.<t-10>.<t>
dock              = dock.s1rf.technical-control.4n
carrier order     = carrier-a, carrier-b, carrier-c, carrier-d
values            = (0.0, 0.0, 0.0, 0.0)
```

Diese Distribution ist eine aeussere Projektionsprovenienz und kein
Kontakt-, Gap- oder Probeintervall. Sie wird keinem Modell uebergeben und
erzeugt keinen Feldzeitfortschritt.

## Ausgerichtetes Feld

Das neue Feld wird ausschliesslich aus dem vollstaendigen Vor-Align-Feld
rekonstruiert. Pro Knoten duerfen genau folgende Werte ersetzt werden:

```text
activation                 -> 0.0
afterimage                 -> 0.0
perception.receptor_contact -> 0.0
```

Bit- und objektidentisch zu erhalten sind, soweit unveraenderlich:

- Neuron-, Feld-, Modalitaets- und Geometrieidentitaeten;
- Position und Perceptiontick;
- alle lokalen Samples samt Reihenfolge und Digests;
- Layeridentitaet, Layertick, Sampleoffsets, periodische Achsen und
  Rezeptordockrollen;
- Docks und Dockmaps;
- Substrat- und Entwicklungsobjektreferenz;
- der vollstaendige private Modellzustand;
- Konfigurations-, Kanten- und Geometriedigestrollen.

`last_distribution` wird als einzige weitere notwendige Feldkomponente
durch die oben gebundene Nullframe-Projektionsdistribution ersetzt. Der
Vor-Align-Distributionsdigest bleibt im Alignreceipt.

Der Konstruktor von `SharedMCMField` muss das neue Feld ohne Sonderweg
akzeptieren. Ein direkter Mutationszugriff auf bestehende Neuronen, Layer
oder Feldobjekte ist verboten.

## Carry-Neubindung

Weil sich der oeffentliche Felddigest durch Align aendert, darf der alte
`FourNodeModelCarry.carry_digest` nicht weiterverwendet werden. Gleichzeitig
darf kein privater Zustand neu serialisiert oder rekonstruiert werden.

Die spaetere Implementierung muss deshalb in
`four_node_model_invocation.py` drei schmale oeffentliche Rollen anbieten:

```python
def four_node_model_field_digest(field: SharedMCMField) -> str: ...

def four_node_model_private_state_digest(value: object | None) -> str | None: ...

def rebind_four_node_model_carry_field(
    source: FourNodeModelCarry,
    aligned_field: SharedMCMField,
) -> FourNodeModelCarry: ...
```

Die beiden Digestoperationen muessen exakt die bereits intern verwendeten
Kanonisierungen delegieren; keine zweite Digestdefinition ist zulaessig.

Die Rebindoperation darf nur:

- den vollstaendigen Felddigest neu berechnen;
- denselben privaten Objektverweis und Privatdigest verwenden;
- alle sechs Rollen-, Konfigurations-, Kanten- und Geometriefelder
  unveraendert uebernehmen;
- den kanonischen Carrydigest mit derselben bestehenden Praeimageform neu
  berechnen.

Sie muss vor Publikation Feldrolle, Geometrie, Docks, Layertick,
Substrat-/Entwicklungsreferenz und die oben erlaubte Align-Differenz pruefen.
Ein allgemeines Ersetzen des Carryfelds ist unzulaessig.

## Alignreceipt

Nach erfolgreicher Projektion wird intern genau ein unveraenderliches
Alignreceipt erzeugt mit:

```text
model_role
plan_position
align_event_digest
common_field_end_tick
layer_tick
pre_field_digest
post_field_digest
pre_last_distribution_digest
projection_distribution_digest
private_state_digest
pre_carry_digest
post_carry_digest
configuration_and_dependency_digests
receipt_digest
```

Der private Zustand wird nur ueber denselben Digest belegt. Ein privater
Rohpayload gehoert nicht in das Receipt.

Erforderliche Identitaeten:

```text
pre_private_digest = post_private_digest
pre_layer_tick      = post_layer_tick
pre_field_time      = post_field_time
pre_carry_digest    != post_carry_digest
pre_field_digest    != post_field_digest
```

Die beiden Ungleichheiten folgen aus der gebundenen oeffentlichen
Projektion und sind kein funktionaler Befund.

## Passive Checkpoints

Ein `CHECKPOINT`-Ereignis ruft weder Modell noch Align auf und erzeugt keinen
neuen Carry. Der aktuelle Carry bleibt objekt- und digestidentisch.

Ein interner Checkpointrecord traegt mindestens:

```text
model_role
plan_position_and_role
checkpoint_role_and_tick
fixture_event_digest
event_chain_digest
field_digest
carry_digest
private_state_digest_or_none
configuration_and_dependency_digests
last_distribution_digest
signed_receptor_contact_vector
signed_activation_vector
signed_afterimage_vector
layer_tick
common_field_end_tick
align_receipt_digest_or_none
checkpoint_digest
```

Die Vektoren stehen in der kanonischen Knotenordnung
`node-a, node-b, node-c, node-d`. Private Rohzustaende, erwartete
Kontrastrichtung und Comparatorwerte sind gesperrt.

`ALIGNED_PRE_PROBE` verlangt unmittelbar vorher das zugehoerige
Alignreceipt. `POST_PROBE_READOUT` verlangt unmittelbar vorher das
vollstaendig abgeschlossene Probeintervall. C-Checkpoints duerfen kein
Alignreceipt tragen, solange noch kein Align stattgefunden hat.

## Ereignisreceiptkette

Jede erfolgreiche Operation erzeugt intern genau ein Receipt. Der
Kettendigest bindet:

```text
vorheriger Kettendigest oder CELL_CHAIN_ORIGIN
Fixtureereignisdigest
Operationsart
Vorcarry- und Nachcarrydigest
Operationsreceipt-Digest
```

Checkpointreceipts besitzen denselben Vor- und Nachcarrydigest.
Alignreceipts besitzen verschiedene Carrydigests bei identischer Feldzeit.
Intervallreceipts besitzen verschiedene Carrydigests und genau einen
Feldzeitfortschritt.

Kein Ereignis darf uebersprungen, wiederholt, neu geordnet oder nach einem
Fehler erneut versucht werden.

## Atomarer Zellerfolg

Eine Zelle ist `COMPLETED`, wenn und nur wenn:

- alle Fixtureereignisse in kanonischer Reihenfolge abgeschlossen sind;
- Intervall-, Align- und Checkpointanzahl dem Plan entsprechen;
- der terminale gemeinsame Feldtick dem Plan entspricht;
- alle Pflichtcheckpoints vollstaendig intern vorliegen;
- die Receiptkette lueckenlos ist;
- der finale Carry vollstaendig und gueltig ist.

Erst dann darf ein `FourNodeCellResult` atomar publizieren:

```text
status = COMPLETED
cell_identity
fixture_and_plan_digests
model_configuration_digest
refinement_or_none
final_carry
ordered_checkpoint_records
terminal_event_chain_digest
cell_result_digest
failure_codes = ()
```

Zwischenreceipts duerfen im Erfolgsresultat nur als Digestkette, nicht als
private Rohzustandsfolge erscheinen.

## Atomarer Zellfehler

Jede ungueltige Eingabe, jedes `NOT_COMPUTABLE`, jede Carry-, Zeit-, Align-,
Checkpoint- oder Digestabweichung stoppt die Zelle sofort. Publiziert wird
nur:

```text
status = NOT_COMPUTABLE
cell_identity soweit vorab validiert
fixture_and_plan_digests soweit vorab validiert
failure_codes
failure_receipt_digest
cell_result_digest
final_carry = None
checkpoint_records = ()
```

Kein letzter gueltiger Carry, Zwischencheckpoint oder Teilfeld darf nach
aussen gelangen. Es gibt keinen Retry, Reset, Ersatzplan oder Weiterlauf.

## Informationsgrenze

Der spaetere Zellrunner darf einem Modellaufruf ausschliesslich geben:

- Assembly oder vorherigen Carry;
- aktuelle Fixturedistribution;
- aktuelle Fixturestepzeit;
- rollenfest `2` oder `None` als Refinement.

Planrolle, Zellidentitaet, Checkpoint, Alignreceipt, Ereigniskette,
Comparatorrolle, erwartete Richtung und Zukunftszustand bleiben ausserhalb
des Modells.

## Implementierungs- und Testbudget

S1-SJ darf genau folgende Produktionsgrenze bearbeiten:

```text
mcm_field_organism/four_node_model_invocation.py
mcm_field_organism/four_node_cell_lifecycle.py
tests/test_four_node_cell_lifecycle.py
```

Die bestehende Aufruflogik darf nur um die drei gebundenen reinen
Digest-/Rebindrollen erweitert werden. Dispatch, Modellkonfigurationen und
Kernpfade bleiben unveraendert.

S1-SJ darf hoechstens 16 fokussierte Tests definieren, aber nicht
ausfuehren. Sie muessen mindestens pruefen:

- zulaessige und unzulaessige Carry-Neubindung;
- private Objekt- und Digestidentitaet ueber Align;
- Nullframe-Projektionsdistribution und unveraenderte Feldzeit;
- gueltige SharedMCMField-Konstruktion nach Align;
- passive Checkpointidentitaet;
- C-Checkpointordnung;
- rollenfestes Refinement;
- einen synthetisch isolierten Ein-Intervall-Lebenszyklus ohne vollen
  17-Plan-Lauf;
- atomare Fehlerausgabe ohne Teilcarry oder Checkpoints;
- fehlende Plan-/Checkpoint-/Ergebnislabels im Modellaufruf.

Keine vollstaendige Matrixzelle und kein 17-Plan- oder 238-Zellen-Lauf.

## Aussagegrenze

S1-SI bindet nur die technische Huelle zwischen bereits abgenommenem
Fixture und bereits abgenommenem Modellaufruf. Sie ist kein Feldlauf, kein
Baselineergebnis und kein Befund einer hypothetischen
MCM-Memory-Entwicklungsrichtung.

## Genau ein naechster Schritt

S1-SJ ist ausschliesslich fuer die Implementierung der drei schmalen
Carryrollen, der atomaren Einzelzellen-Lebenszyklushuelle und hoechstens 16
noch nicht ausgefuehrter fokussierter Tests zulaessig.

Keine Testausfuehrung, keine vollstaendige Matrixzelle, kein Gesamtpaket,
kein Comparator und kein Forschungslauf.
