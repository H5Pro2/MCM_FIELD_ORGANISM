# S1-SO: Statischer Realpfad-, Serialisierungs-, Artefakt-, Quellbeleg- und Einmallaufvertrag

## Status und Zweck

S1-SO bindet den technischen Persistenz- und Einmallaufpfad oberhalb der in
S1-SN synthetisch abgenommenen atomaren Matrixhuelle. Der Vertrag legt fest,
wie ein spaeteres vollstaendiges `FourNodeMatrixResult` kanonisch belegt und
genau einmal als carryfreies Ergebnisartefakt publiziert werden duerfte.

S1-SO implementiert keinen Serializer oder Runner, materialisiert keine
Reportdatei, definiert oder startet keinen Test und ruft weder Zelle noch
Matrix auf.

## Praezisierung der Fehlergrenze

S1-SN nannte als offene Anforderung `keine Datei oder Teilmatrix bei
Fehler`. Fuer einen technisch erzwungenen Einmallauf ist `keine Datei`
zu weit gefasst: Ohne persistenten Versuchsnachweis koennte ein gestarteter
Fehler spaeter nicht von einem noch nie gestarteten Lauf unterschieden
werden.

S1-SO praezisiert deshalb ausschliesslich die Ausfuehrungsprovenienz:

- bei einem gestarteten Fehler entstehen kein Ergebnisartefakt und keine
  Teilmatrix;
- ein kleiner technischer Versuchsnachweis und die Sperrdatei bleiben
  bestehen;
- dadurch ist jeder weitere Lauf ohne neue fachliche Freigabe blockiert.

Diese Korrektur veraendert weder Feldmechanik, Modellrollen, Exposition,
Matrixordnung noch Ergebnisinhalt.

## Feste Ausfuehrungsidentitaet

```text
schema_id       = mcm.s1so.four-node-matrix-artifact.v1
source_contract = S1-SO
execution_id    = mcm.s1ss.four-node-matrix.once.v1
canonicalizer   = compact-json-ascii-sort-keys-no-nan-sha256-v1
authorization   = S1-SS_REAL_FOUR_NODE_MATRIX_ONCE
```

Die Kennung ist technische Provenienz. Sie enthaelt weder Ergebnisrichtung
noch Modellurteil.

## Feste Projektpfade

Alle Laufdateien liegen im bestehenden Projekt unter `reports`:

```text
Ergebnis:
reports/s1ss_four_node_matrix_once_v1.json

Versuchsnachweis:
reports/s1ss_four_node_matrix_once_v1.attempt.json

Sperre:
reports/s1ss_four_node_matrix_once_v1.lock

gleichverzeichnisige Ergebnisstufe:
reports/.s1ss_four_node_matrix_once_v1.json.staging
```

Vor einer spaeteren Ausfuehrungsfreigabe muessen alle vier Pfade fehlen.
Symlinks, Junctions, abweichende Gross-/Kleinschreibung, alternative
Ausgabepfade und Pfade ausserhalb des Projektroots sind unzulaessig.

## Kanonische JSON-Regel

Jeder kanonische Record wird als ASCII-kompatibles UTF-8 mit diesen
Parametern gebildet:

```text
ensure_ascii = true
allow_nan    = false
sort_keys    = true
separators   = (",", ":")
```

Der Digest eines Records ist SHA-256 ueber seine Compact-JSON-Praeimage
ohne das eigene Digestfeld. Persistierte JSON-Dateien enthalten genau den
vollstaendigen kanonischen Record und einen abschliessenden LF-Bytewert.
Parser muessen die Eingabebytes nach Validierung erneut kanonisieren und
Bytegleichheit verlangen. Doppelte Schluessel, unbekannte Felder,
nichtendliche Zahlen, negative Null und nichtkanonische Zahlenformen werden
fail-closed abgewiesen.

## Lokales Quellinventar

Der spaetere Runner bindet nicht nur einen Git- oder Dokumentstand, sondern
die tatsaechlich erreichbaren lokalen Produktionsbytes.

Inventarwurzeln sind:

```text
mcm_field_organism/four_node_matrix_single_run.py
mcm_field_organism/four_node_matrix_artifact.py
mcm_field_organism/four_node_matrix_lifecycle.py
```

Ausgehend von diesen Wurzeln wird per Python-AST die transitive Menge aller
relativen Imports unter `mcm_field_organism` gebildet. Fuer jedes erreichbare
lokale Modul wird der projektrelative POSIX-Pfad und SHA-256 der Dateibytes
gebunden. Standardbibliothek, Tests, Dokumente, historische Orchestratoren
und nicht erreichbare Projektmodule gehoeren nicht in das Inventar.

Ein dynamischer lokaler Import, ein nicht aufloesbarer relativer Import,
eine Quelle ausserhalb des Projektroots, ein doppelter Pfad oder ein
Symlink stoppt den Preflight. Die sortierte Pfad-/Digestliste besitzt einen
eigenen `source_inventory_digest`.

Zusatzdateien werden separat bytegebunden:

```text
reports/s1rk_four_node_fresh_manifest.json
reports/s1sd_four_node_fresh_matrix_registration.json
```

Das kanonische Expositionsfixture wird aus der validierten Registrierung
erzeugt und mit seinem bereits abgenommenen Fixturedigest
`ca66f3a673eaca663a0973f7e956a90f4788e6f51963b71de4952801936bac3e`
belegt.

Quellinventar und Zusatzdateidigest werden unmittelbar vor dem ersten
Matrixaufruf und nach dessen Rueckkehr erneut berechnet. Jede Abweichung
stoppt vor Ergebnisbildung oder Publikation.

## Laufzeitbeleg

Der Artefaktbeleg darf nur technisch stabile Laufzeitrollen enthalten:

```text
python_implementation
python_major_minor_micro
platform_system
platform_machine
```

Absolute Pfade, Benutzername, Hostname, Prozess-ID, Systemzeit,
Zeitzone und zufaellige Kennungen sind gesperrt. Sie beeinflussen die
Feldrechnung nicht und wuerden reproduzierbare Artefaktdigests verhindern.

## Versuchsnachweis und Sperre

Nach vollstaendig bestandenem Vorstart-Preflight, aber vor dem ersten
Matrixaufruf, wird die Sperrdatei mit exklusiver Neuerstellung angelegt und
auf den Datentraeger geschrieben. Sie bindet mindestens:

```text
execution_id
authorization
source_inventory_digest
manifest_file_digest
registration_file_digest
lock_digest
```

Danach wird der Versuchsnachweis kanonisch und exklusiv publiziert. Er
bindet dieselben Identitaeten, den Status `STARTED`, das Matrixbudget
`238/1778/238/560` und einen `attempt_digest`.

Existiert Ergebnis, Versuchsnachweis, Sperre oder Staging bereits, startet
kein fachlicher Aufruf. Nach einem gestarteten Fehler bleiben
Versuchsnachweis und Sperre unveraendert erhalten. Es gibt keinen
automatischen Retry, Resume, Reset oder Cleanup dieser beiden Belege.

## Exakter spaeterer Prozessweg

Nach Implementierung und gesondertem finalem Preflight darf ein spaeterer
Lauf nur als ein neu gestarteter Python-Prozess im Projektroot gelten:

```text
python -B -m mcm_field_organism.four_node_matrix_single_run \
  --authorization S1-SS_REAL_FOUR_NODE_MATRIX_ONCE
```

Der Runner akzeptiert keinen Rollen-, Plan-, Refinement-, Pfad-, Parallel-,
Retry- oder Comparatorparameter. Er startet keinen Unterprozess, Thread,
Netzwerkzugriff oder Geraetekontakt.

Im Prozess gilt exakt:

```text
1 Matrixproducer-Aufruf
238 atomare Einzelzellenaufrufe
1778 Modellintervalle
238 zeitlose Alignoperationen
560 passive Checkpoints
0 Comparatoraufrufe
0 automatische Wiederholungen
```

Die Matrix bleibt sequentiell. Nur der aktuelle Zellcarry darf neben den
carryfreien Zellsummarys und Checkpointrecords erreichbar sein.

## Erfolgsbedingung vor Serialisierung

Nach Rueckkehr des einzigen Matrixproducer-Aufrufs muessen gelten:

- `status=COMPLETED` und leere Fehlercodes;
- oeffentliche `validate_four_node_matrix_result`-Pruefung besteht;
- exakt 238 Summarys, 560 Checkpointrecords und 14
  Rollenkonfigurationsdigests liegen vor;
- Budgetidentitaet ist exakt `238/1778/238/560` samt F3-Unterbudget;
- terminaler Matrixkettendigest und Matrixresultatdigest sind gueltig;
- weder Matrixresultat noch Summary besitzt ein Carryobjekt;
- erneutes Quell- und Zusatzdateiinventar ist bitidentisch zum Vorzustand.

Ein `NOT_COMPUTABLE`-Resultat oder eine Validierungsabweichung erzeugt kein
Ergebnisartefakt.

## Ergebnisartefakt

Das Rootobjekt traegt exakt:

```text
schema_id
source_contract_id
execution_id
canonicalization_id
authorization_digest
source_inventory
source_inventory_digest
input_file_digests
validated_input_identity
runtime_identity
budget_identity
matrix_result
artifact_digest
```

`authorization_digest` bindet nur SHA-256 der exakten
Autorisierungszeichenfolge, nicht die Zeichenfolge selbst.

### `validated_input_identity`

```text
fresh_manifest_digest
matrix_registration_digest
exposure_fixture_digest
axis_digest
```

### `matrix_result`

Die Projektion enthaelt exakt:

```text
status = COMPLETED
ordered_238_cell_summaries
ordered_560_checkpoint_records
per_role_configuration_digests
terminal_matrix_chain_digest
matrix_result_digest
```

Zellsummarys und Checkpointrecords verwenden die bereits gebundenen Felder
und Reihenfolgen aus S1-SL/S1-SM. Finale Carryobjekte, private Rohzustaende,
Feldobjekte, Zwischenreceipts, erwartete Richtungen, Comparatorwerte,
Rangfolgen und Funktionsentscheidungen sind gesperrt.

Private Zustandsdigests in bereits abgenommenen Checkpointrecords bleiben
reine Integritaetsbelege; private Payloads werden nicht serialisiert.

## Atomare Ergebnisveroeffentlichung

Nach vollstaendiger In-Memory-Validierung gilt:

1. Staging wird im selben Verzeichnis exklusiv neu angelegt.
2. Vollstaendige kanonische Artefaktbytes werden geschrieben, geflusht und
   mit `fsync` bestaetigt.
3. Staging wird erneut gelesen, streng geparst und bytegleich validiert.
4. Das Ergebnis wird ausschliesslich durch einen exklusiven
   Same-Directory-Hardlink vom Stagingpfad zum noch fehlenden Zielpfad
   sichtbar gemacht.
5. Nach erfolgreichem Link wird Staging entfernt.
6. Versuchsnachweis und Sperre werden erst nach bestaetigtem Ergebnislink
   entfernt.

Ein vorhandener Zielpfad darf nie ueberschrieben werden. Schlaegt ein
Schritt vor dem Ergebnislink fehl, wird Staging bestmoeglich entfernt;
Versuchsnachweis und Sperre bleiben. Schlaegt nur die Bereinigung nach dem
Ergebnislink fehl, ist das vollstaendige Ergebnis bereits gueltig und jeder
weitere Lauf bleibt durch Ziel oder Restbelege gesperrt.

## Zulaessige Ausgabe und Seiteneffekte

Bei Erfolg darf der Prozess auf Standardausgabe ausschliesslich
Ausfuehrungskennung, Status, Ergebnisrelativpfad, Artefaktdigest,
Matrixresultatdigest und die vier Gesamtbudgets melden. Bei Fehler duerfen
nur technischer Fehlercode und der relative Versuchsnachweispfad gemeldet
werden.

Gesperrt sind:

- Feld-, Checkpoint- oder private Zwischenwerte auf stdout/stderr;
- Zwischenreports, CSV, Pickle, Cache oder Debugdump;
- Aenderungen ausserhalb der vier festen Laufpfade;
- Netzwerk, Telemetrie, externe APIs oder Geraete;
- Comparatoren und Ergebnisinterpretation;
- automatische Git-Operationen innerhalb des Runners.

## Implementierungs- und Testbudget fuer S1-SP

S1-SP darf genau bearbeiten:

```text
mcm_field_organism/four_node_matrix_lifecycle.py
mcm_field_organism/four_node_matrix_artifact.py
mcm_field_organism/four_node_matrix_single_run.py
tests/test_four_node_matrix_artifact_and_single_run.py
```

Im Matrixmodul ist nur eine reine
`validate_four_node_matrix_result`-Rolle zulaessig. Artefaktmodul und Runner
duerfen keine Modellkerne direkt importieren oder aufrufen.

S1-SP darf hoechstens 20 fokussierte Tests definieren, aber nicht
ausfuehren. Sie muessen mindestens pruefen:

- strikte Zellsummary-, Checkpoint- und Matrixresultatdigests;
- kanonische Artefaktbytes und Roundtrip;
- Ablehnung unbekannter, fehlender, doppelter und nichtkanonischer Felder;
- Ausschluss von Carryobjekten und privaten Payloads;
- deterministisches transitives lokales Quellinventar;
- Vor-/Nachlauf-Quelldrift;
- feste Pfade und Autorisierungsdigest;
- Vorstartabbruch ohne Laufbeleg;
- exklusiven Versuchsnachweis und Wiederholungsschutz;
- gestarteten Fehler ohne Ergebnis oder Teilmatrix;
- genau einen synthetischen Matrixproducer-Aufruf;
- exklusive Same-Directory-Ergebnisveroeffentlichung;
- Erfolgscleanup und Sperre vorhandener Ergebnisse;
- fehlende Comparator-, Netzwerk-, Thread-, Unterprozess- und Gitpfade.

Alle Tests muessen einen synthetischen Matrixproducer verwenden. Kein Test
darf `execute_four_node_matrix` mit realen Zellproducern aufrufen.

## Weitere Stufen und Aussagegrenze

Nach S1-SP ist S1-SQ ausschliesslich fuer einen einmaligen unveraenderten
synthetischen Testlauf zulaessig. Erst danach darf S1-SR einen letzten
statischen Realpreflight mit konkreten Implementierungs- und
Quellinventardigests bilden. Eine reale Ausfuehrung bliebe bis zu einer
danach ausdruecklich gebundenen S1-SS-Einmallauffreigabe gesperrt.

S1-SO ist reine technische Persistenz- und Ausfuehrungsmethodik. Sie
bestaetigt keine Modellfunktion, keine Kandidatenwirkung und keine
Faehigkeit einer hypothetischen MCM-Memory-Entwicklungsrichtung.

```text
CANONICAL_CARRY_FREE_MATRIX_ARTIFACT_SOURCE_INVENTORY_AND_ONE_SHOT_CONTRACT_BOUND
NO_IMPLEMENTATION_NO_TEST_NO_CELL_NO_MATRIX_NO_RESULT_DECISION
```

Der einzige naechste Schritt ist S1-SP im oben gebundenen Dateibudget.
