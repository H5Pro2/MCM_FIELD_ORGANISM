# S2-IN: Private Bootstrap-Lifecycle-Implementierung und statischer Codeaudit

## Status

`S2IN_PRIVATE_BOOTSTRAP_LIFECYCLE_IMPLEMENTED_STATIC_AUDIT_VALID`

S2-IN setzt ausschliesslich die unter S2-IM gebundene Korrektur des fruehen
Startlebenszyklus um. Geaendert wurden genau drei private S2-IG-Module:

- `tools/_s2ig_private_append_only_recorder.py`;
- `tools/_s2ig_private_runner.py`;
- `tools/_s2ig_private_result_verifier.py`.

Operationsregistry, ParentSetV1, S2-IC-Signallogik, Tests, README,
Memory-Kerne, API und Feldpfad blieben unveraendert. Es wurden keine Tests
oder Funktionslaeufe ausgefuehrt und keine Projektmodule importiert.

## Recorder-Lifecycle

Der Recorder beginnt intern jetzt mit:

```text
BOOTSTRAPPING
```

Er darf erst nach dem vollstaendigen Bootstrap nach `ACTIVE` wechseln. Die
Bootstrap-Sequenz umfasst unveraendert die ersten beiden Registryoperationen:

```text
ie-op-001 RUN_PREPARE
ie-op-002 SOURCE_MANIFEST
```

Beide Operationen werden in einem privaten Stagingverzeichnis vollstaendig
materialisiert. Vor der finalen Publikation prueft der Recorder:

- Zustand weiterhin `BOOTSTRAPPING`;
- naechste Operation exakt `ie-op-003`;
- exakt vier START-/RESULT-Ereignisse;
- vorhandene Ergebnisdigests fuer `ie-op-001` und `ie-op-002`;
- SHA-256-Uebereinstimmung der beiden geschriebenen Artefakte;
- registrierte Einzelgroessen;
- vier kanonische Journalzeilen;
- Gleichheit von tatsaechlichen Datei- und intern gezaehlten Bytes;
- Gesamtmaximum `11.264` Byte.

Erst danach wird das Stagingverzeichnis exklusiv auf den finalen Laufpfad
publiziert. Anschliessend werden Laufpfad und Journalpfad auf den finalen
Ort gebunden und der Recorder wechselt auf `ACTIVE`.

Ein Fehler vor dieser Publikation erzeugt ausschliesslich einen
`StartRejected`-Befund. Er erzeugt keinen neuen finalen Lauf und keinen
regulaeren `NOT_EVALUABLE`-Pfad.

## `StartRejected`

Die unveraenderliche private Datenform bindet:

- Schema `s2im.start-rejected.v1`;
- Status `START_REJECTED`;
- Run-ID, Owner-ID und Plan-Digest;
- Pfadrolle `RUN_DIRECTORY`;
- Vorhandensein eines fremden oder frueheren Zielpfads;
- `publication_performed = false`;
- Fehlercode `IG-E001` oder `IG-E010`;
- keinen Reservierungsdigest;
- null Ereignisse und null Artefakte;
- kanonischen Selbst-Digest.

Die statische Worst-Case-Serialisierung mit maximaler 96-Zeichen-Run- und
Owner-ID betraegt `626` Byte und bleibt unter der Grenze von `768` Byte.

Die alten S2-IG-Bezeichnungen `StartBlocked` und `START_BLOCKED` kommen in
den drei aktuellen S2-IG-Modulen nicht mehr vor.

## Manifestgrenze

Die Manifestbildung wurde aus `_execute()` entfernt und in die
Bootstrap-Grenze des Recorders verlagert. Es existiert in den geaenderten
Modulen nur noch eine Quelle fuer `s2ig.source-manifest.v1`.

Das Manifest wird ausschliesslich aus bereits vor dem Lauf verfuegbaren
Bindungen erzeugt:

- ExecutionPlan;
- Registry-Bundledigest;
- Execution-Fixture-Digest;
- getrennte Kontext- und Signalrollen;
- `evaluation_plan_digest = null`.

Runtime, Geschichten, Memory-Zustaende oder Auswertungsergebnisse werden
nicht zur Manifestbildung verwendet.

## Runnergrenze

`run_main_once` akzeptiert jetzt als Vorlaufergebnis entweder:

```text
StartRejected
oder
AppendOnlyRunRecorder im Zustand ACTIVE
```

Der aktive Recorder steht bereits auf `ie-op-003`. Erst danach wird die
Runtime erzeugt. Ein Runtime- oder spaeterer Fehler wird deshalb als
regulaerer Fehler ab `ie-op-003` geschlossen und besitzt zwingend
`reservation.json`, `manifest.json` sowie die vier Bootstrap-Ereignisse.

Das Hauptgate bleibt an beiden unveraenderten Stellen `False` beziehungsweise
wird im `finally` wieder auf `False` gesetzt.

## Verifikatorgrenze

Der unabhaengige read-only Verifikator besitzt jetzt drei getrennte
Lifecycle-Ausgaenge:

1. `START_REJECTED` fuer einen gueltigen In-Memory-Startablehnungsbeleg ohne
   durch diesen Versuch publizierten Lauf;
2. `NOT_EVALUABLE` fuer einen gestarteten Lauf mit vollstaendigem Bootstrap
   und gueltigem Fehlerterminal;
3. `RECORDING_COMPLETE` fuer den vollstaendig verifizierten Erfolgsweg mit
   `COMPLETE`-Marker.

Eine beschaedigte Startablehnung ergibt `LIFECYCLE_INVALID`, nicht
`NOT_EVALUABLE`. Ein final sichtbarer Laufpfad ohne Reservierung oder Manifest
ergibt `NOT_EVALUABLE` mit `lifecycle bootstrap is incomplete` und gilt nicht
als sauber geschlossener Fehlerpfad.

Auch auf einem fruehen Fehlerpfad prueft der Verifikator jetzt vor der
terminalen Rueckgabe:

- vollstaendige Reservation- und Manifestformen;
- Plan-, Owner-, Registry-, Fixture- und Quellbindungen;
- Reservation-Core-Digest;
- ExecutionPlan-Digest;
- Artefakt- und START-Eventbindung;
- Elternbezug von `ie-op-002` auf `ie-op-001`;
- viergliedrige Ereignisreihenfolge;
- Bootstrap-Maximum `11.264` Byte.

Ein Fehlerpfad vor `ie-op-003` wird abgewiesen. Der frueheste gueltige
post-reservation Fehlerpfad wird zusaetzlich gegen `22.528` Byte geprueft.
Ein frueher `COMPLETE`-Marker bleibt durch die bestehenden Operations-,
Ereignis- und Terminalpruefungen unerreichbar.

## Unveraenderte Vertragsgrenzen

Statisch bestaetigt wurden:

| Grenze | Wert |
| --- | ---: |
| Registryoperationen | 183 |
| Registryereignisse | 366 |
| Mehr-Eltern-Operationen | 76 |
| ParentSetV1-Worst-Case `ie-op-171` | 814 Byte |
| Eventgrenze | 1.536 Byte |
| Bootstrap-Maximum | 11.264 Byte |
| fruehester gueltiger Fehlerpfad | 22.528 Byte |
| `StartRejected`-Maximum | 768 Byte |
| berechneter `StartRejected`-Worst-Case | 626 Byte |

Die bestehenden Erfolgs- und maximalen Fehlerpfadbudgets wurden nicht
veraendert. Das Gesamtmaximum liegt weiterhin bei einem spaeteren
Registryfehler und wird durch den Bootstrap nicht erhoeht.

## Statischer Codeaudit

Der Audit bestand ohne Import oder Ausfuehrung von Projektcode:

- alle drei geaenderten Python-Dateien sind AST-lesbar;
- nur diese drei privaten Dateien besitzen Codeaenderungen;
- `s2ig.source-manifest.v1` besitzt genau eine Producerstelle;
- `StartBlocked` und `START_BLOCKED` sind aus dem S2-IG-Pfad entfernt;
- `BOOTSTRAPPING` ist von `ACTIVE` getrennt;
- der Runner besitzt keinen Manifestproduzenten mehr;
- Registry-, ParentSetV1-, S2-IC-, Test- und README-Dateien sind diff-frei;
- die arithmetischen Grenzen `11.264` und `22.528` wurden unabhaengig
  nachgerechnet;
- das Hauptgate bleibt geschlossen.

## Noch nicht qualifiziert

S2-IN ist nur eine statisch abgenommene Implementierung. Die vorhandenen
S2-IH-/S2-IL-Testhelfer erwarten noch den alten Rueckgabepunkt nach
`ie-op-001` und die alte Bezeichnung `StartBlocked`. Sie wurden in diesem
Schritt absichtlich weder geaendert noch ausgefuehrt.

Die naechste gemeinsame Qualifikation muss unter neuer ID mindestens binden:

- gueltiges `START_REJECTED` ohne neuen finalen Laufpfad;
- vollstaendiger Bootstrap bis `ie-op-002`;
- korrigierter Test-21-Fehler an `ie-op-003`;
- `NOT_EVALUABLE` ohne Bootstrapfehler;
- unveraenderte 28 bereits bestandene Pruefbereiche;
- Quellhashes vor und nach genau einem Testaufruf.

Bis zu deren vollstaendigem Bestehen bleibt der reale Fuenf-Status-
Funktionslauf gesperrt.
