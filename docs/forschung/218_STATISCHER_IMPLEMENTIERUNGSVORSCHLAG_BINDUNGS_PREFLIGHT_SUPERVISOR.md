# 218 - Statischer Implementierungsvorschlag fuer den Bindungs-Preflight-Supervisor

## 1. Status und Auftrag

Dieses Dokument ist ausschliesslich ein statischer Implementierungsvorschlag. Es ist kein Forschungs- oder Preflight-Lauf und enthaelt keine Freigabe zur Implementierung oder Ausfuehrung.

Auftrag ist die exakte technische Abbildung des in Dokument 217 vorregistrierten einmaligen Ausfuehrungsvertrags in einen spaeter implementierbaren Windows-Supervisor. Der Vorschlag trennt verbindlich vier Phasen:

1. diesen statischen Vorschlag,
2. eine spaetere ausdrueckliche Implementierungsentscheidung,
3. eine danach erforderliche unabhaengige statische Implementierungspruefung,
4. einen nur nochmals separat freizugebenden einmaligen Prozessstart.

Keine spaetere Phase wird durch dieses Dokument vorweggenommen.

## 2. Forschungsfrage

Kann Dokument 217 ohne Erweiterung seines Vertrags in eine eng begrenzte, statisch pruefbare Supervisorstruktur ueberfuehrt werden, die Handle-Eigentum, Prozessreihenfolge, Ressourcenbegrenzung, Datenstroeme, Environment und alle Ausfuehrungssperren explizit abbildet?

## 3. Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/214_STATISCHE_VORREGISTRIERUNG_STDIN_TRANSPORT_BINDUNGS_PREFLIGHT.md`
- `docs/forschung/215_BINDUNGS_PREFLIGHT_STDIN_NUTZLAST.txt`
- `docs/forschung/216_VORREGISTRIERUNG_EINMALIGER_BINDUNGS_PREFLIGHT_STDIN.md`
- `docs/forschung/217_VORREGISTRIERUNG_EINMAL_AUSFUEHRUNGSAUFTRAG_BINDUNGS_PREFLIGHT.md`
- aktueller freigegebener Uebergabe-Eingang

Keine externe Quelle wurde verwendet.

## 4. Vorgeschlagene Dateien und Schnittstellen

Eine spaetere Implementierung soll auf genau zwei neue Dateien begrenzt werden:

- `tools/binding_preflight_supervisor.py`: Windows-spezifische Supervisorlogik ohne Projektimporte und ohne automatische Ausfuehrung.
- `tests/test_binding_preflight_supervisor_structure.py`: ausschliesslich statische Quelltext- und AST-Pruefungen; die Zieldatei darf weder importiert noch ausgefuehrt werden.

Die Supervisor-Datei soll nur Python-Standardbibliothek verwenden. Windows-Aufrufe werden direkt ueber `ctypes` und `ctypes.wintypes` gebunden. `subprocess`, Shell-Aufrufe, Projektmodule, dynamische Paketinstallation und alternative Prozessstarter sind ausgeschlossen.

Die Implementierungsphase soll bewusst keinen CLI-Einstiegspunkt und keinen `if __name__ == "__main__"`-Block enthalten. Dadurch bleibt die spaetere Ausfuehrungsentscheidung technisch und pruefbar von der Implementierung getrennt. Eine spaetere Aufrufstelle ist nicht Bestandteil dieses Vorschlags und muss vor einem Prozessstart separat gebunden und geprueft werden.

## 5. Vorgeschlagene interne Struktur

### 5.1 Konstanten und unveraenderliche Vertragsdaten

Ein zentraler, unveraenderlicher Konstantenblock bildet ausschliesslich die Werte aus Dokument 217 ab:

- Arbeitsordner: `C:\\Users\\TV\\Documents\\MCM_FIELD_ORGANISM\\workspace`
- `lpApplicationName`: `C:\\Users\\TV\\Documents\\MCM_FIELD_ORGANISM\\workspace\\.venv\\Scripts\\python.exe`
- `lpCommandLine`: `"C:\\Users\\TV\\Documents\\MCM_FIELD_ORGANISM\\workspace\\.venv\\Scripts\\python.exe" -B -I -`
- Erzeugungsflags: `CREATE_SUSPENDED | CREATE_NO_WINDOW | EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT`
- stdin-Nutzlast: exakt `1806` Bytes
- erwarteter SHA-256: `d86be4be95ed54ea461aea4c538639cec179726ccca30b14dd762a605351b393`
- stdout-Grenze: `4096` Bytes; Abbruch beim 4097. Byte
- stderr-Grenze: `0` Bytes; Abbruch beim ersten Byte
- Wall-Time: `60` Sekunden
- User-CPU-Zeit: `300000000` Einheiten zu 100 ns
- Prozess- und Job-Speicher: jeweils `1 GiB`
- aktive Prozesse: `1`
- Kindprozesse des Python-Prozesses: `0`
- zulaessiger Erfolgs-Exitcode: `0`
- Environment: ausschliesslich `SystemRoot=C:\\Windows` und `WINDIR=C:\\Windows`

Die Nutzlast wird in einer spaeteren Implementierung ausschliesslich aus Dokument 215 gelesen. Sie wird nicht dupliziert, rekonstruiert oder geparst. Vor dem Prozessaufbau werden Bytezahl, SHA-256, ASCII und zugleich gueltiges UTF-8, fehlender BOM, ausschliessliche LF-Zeilenenden und das abschliessende LF fail-closed geprueft. Nutzlast, Digest oder Byteumfang duerfen weder korrigiert oder normalisiert noch neu berechnet und danach als Ersatzbindung akzeptiert werden.

### 5.2 Windows-API-Bindungen

Die Implementierung bindet mit vollstaendigen `argtypes` und `restype` mindestens:

- `CreatePipe`
- `SetHandleInformation`
- `InitializeProcThreadAttributeList`
- `UpdateProcThreadAttribute`
- `DeleteProcThreadAttributeList`
- `CreateProcessW`
- `CreateJobObjectW`
- `SetInformationJobObject`
- `QueryInformationJobObject`
- `AssignProcessToJobObject`
- `ResumeThread`
- `WriteFile`
- `ReadFile`
- `WaitForSingleObject`
- `GetExitCodeProcess`
- `TerminateJobObject`
- `CloseHandle`

Erforderliche Strukturen und Konstanten werden lokal nach Windows-ABI definiert. Die spaetere statische Pruefung muss Strukturfelder, Groessenannahmen und Funktionssignaturen gegen eine ausdruecklich freigegebene Primaerquelle pruefen; diese Runtime-/ABI-Fixierung ist nicht Teil des vorliegenden Vorschlags.

### 5.3 Handle-Eigentum

Eine kleine interne Eigentumsverwaltung protokolliert fuer jedes erzeugte Handle genau einen Besitzer, die vorgesehene Schliessstelle und den Schliesszustand. Sie darf keine automatische Ausfuehrung ausloesen.

Vorgesehene Handle-Gruppen:

- Supervisor: `supervisor_stdin_write`, `supervisor_stdout_read`, `supervisor_stderr_read`, Prozess-Handle, Thread-Handle und Job-Handle.
- Child: `child_stdin_read`, `child_stdout_write`, `child_stderr_write`.

Nur die drei Child-Handles werden ueber `PROC_THREAD_ATTRIBUTE_HANDLE_LIST` vererbt. `bInheritHandles` ist `TRUE`. Dieselben drei Handles werden mit `STARTF_USESTDHANDLES` als `hStdInput`, `hStdOutput` und `hStdError` gesetzt. Alle anderen Supervisor-Handles bleiben nicht vererbbar. Jedes weitere vererbbare oder in der Attributliste enthaltene Handle sperrt den Auftrag vor `ResumeThread`. Die Supervisor-Kopien der drei Child-Handles werden nach erfolgreicher Job-Zuweisung und deren Rueckpruefung exakt einmal geschlossen, bevor stdin uebertragen oder `ResumeThread` aufgerufen wird.

Jeder Fehler vor oder nach der Zuweisung fuehrt fail-closed zur Job-Terminierung, sofern ein Job mit Child existiert, und anschliessend zur einmaligen Schliessung aller noch im Besitz des Supervisors befindlichen Handles.

### 5.4 Prozessaufbau und Reihenfolge

Die spaetere Funktion `execute_once()` bildet folgende feste Zustandsfolge ab:

1. Nutzlast und Workspace-Ausgangsmanifest rein lesend in den Speicher aufnehmen.
2. stdin-, stdout- und stderr-Pipes erzeugen und Vererbbarkeit exakt setzen.
3. Job-Objekt erzeugen, alle Limits setzen und per `QueryInformationJobObject` ruecklesen.
4. Attributliste mit genau den drei Child-Handles aufbauen.
5. Child mit `CreateProcessW`, dem exakten absoluten `lpApplicationName`, dem exakten veraenderbaren und nullterminierten UTF-16-`lpCommandLine`-Puffer, `CREATE_SUSPENDED | CREATE_NO_WINDOW | EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT`, `bInheritHandles=TRUE`, `STARTF_USESTDHANDLES`, explizitem Unicode-Environment und ohne Shell erzeugen. Mit dem erfolgreichen `CreateProcessW`-Start beginnt sofort die monotone 60-Sekunden-Wandzeitmessung.
6. Child dem Job zuweisen und die Zuweisung beziehungsweise die wirksamen Jobbedingungen rueckpruefen.
7. Supervisor-Kopien von `child_stdin_read`, `child_stdout_write` und `child_stderr_write` exakt einmal schliessen.
8. Zwei parallele rohe `ReadFile`-Leser fuer stdout und stderr starten und deren Bereitschaft bestaetigen.
9. Exakt einen `WriteFile`-Aufruf mit allen 1806 Bytes ausfuehren; `bytesWritten == 1806` verlangen; kein `FlushFileBuffers` verwenden; danach `supervisor_stdin_write` exakt einmal schliessen.
10. `ResumeThread` exakt einmal aufrufen.
11. Wall-Time ab erfolgreichem `CreateProcessW`, Job-Grenzen, Streamgrenzen, Prozessbaum, Prozessende und EOF beider Leser ueberwachen; Thread- und Handlewerte vor Start, waehrend des Wartens und nach Prozessende nur beobachten.
12. eindeutigen Exitcode `0`, exakte stdout-Bytes, leeres stderr und Workspace-Nachmanifest pruefen.
13. Ergebnis nur als internes Rueckgabeobjekt bereitstellen und alle restlichen Ressourcen schliessen.

Vor Schritt 10 darf kein Child-Code ausgefuehrt werden. Nach einem Fehler darf kein Resume, Retry oder zweiter Start stattfinden.

### 5.5 stdin, stdout und stderr

stdin wird als roher Bytepuffer in genau einem `WriteFile` geschrieben. Teilwrites, Wiederholungen oder ein zweiter Schreibaufruf sind ein Vertragsfehler und fuehren zur Terminierung.

stdout und stderr werden vor `ResumeThread` durch zwei gleichzeitig laufende Leser aufgenommen. Die Leser verwenden `ReadFile` direkt und keine Textwrapper. stdout reserviert 4097 Bytes, damit das 4097. Byte unmittelbar erkannt und der Job terminiert werden kann. stderr reserviert ein Byte und terminiert beim ersten Byte. Beide Streams muessen nach Prozessende EOF erreichen; fehlendes EOF ist ein Fehler.

Die spaetere Implementierung darf stdout erst nach vollstaendig erfolgreicher Begrenzungs-, EOF- und Schema-Pruefung als Ergebniswert zurueckgeben. Sie schreibt keine Protokoll- oder Ergebnisdatei.

### 5.6 Job- und Zeitgrenzen

Der Job wird vor `ResumeThread` mit folgenden Grenzen konfiguriert:

- `JOB_OBJECT_LIMIT_PROCESS_TIME`
- `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`
- `JOB_OBJECT_LIMIT_ACTIVE_PROCESS` mit Wert 1
- `JOB_OBJECT_LIMIT_PROCESS_MEMORY` mit exakt 1073741824 Byte
- `JOB_OBJECT_LIMIT_JOB_MEMORY` mit exakt 1073741824 Byte
- User-CPU-Zeit exakt `300000000` Einheiten zu je 100 Nanosekunden

Die gesetzten Flags und Werte werden vor der Child-Freigabe rueckgelesen und exakt verglichen. Die Wall-Time wird im Supervisor mit einer monotonen Uhr ab dem erfolgreichen `CreateProcessW`-Start ueberwacht und schliesst damit Suspendierungs-, Job-, Handle-, Leser- und stdin-Phase ein. Jede Grenzverletzung, jeder beobachtete Kindprozess, jeder nicht eindeutige Exit, jeder Exitcode ungleich 0 oder jeder sonst nicht eindeutig pruefbare Zustand terminiert den gesamten Job beziehungsweise sperrt nach bereits eingetretenem Prozessende das Ergebnis. Beim Schliessen oder Verlust des Supervisor-Jobhandles muss der Prozess beendet werden. Thread- und Handlewerte werden vor Start, waehrend des Wartens und nach Prozessende beobachtet, begruenden aber keine wissenschaftliche Messung.

### 5.7 Environment- und Kommandozeilenvertrag

`CreateProcessW` erhaelt einen expliziten, alphabetisch sortierten und doppelt NUL-terminierten UTF-16-Environmentblock mit genau:

```text
SystemRoot=C:\Windows\0
WINDIR=C:\Windows\0
\0
```

Es wird kein Parent-Environment geerbt. `lpApplicationName`, `lpCommandLine` und Arbeitsordner werden ohne Pfadauflosung, Quoting-Aenderung oder sonstige Transformation exakt aus Abschnitt 5.1 uebernommen. Die Runtime-Identitaet bleibt bis zu einer separaten Runtime-Fixierung eine ungepruefte Voraussetzung; sie darf in der Implementierung nicht stillschweigend ersetzt werden. Weitere Environmentvariablen, insbesondere `PATH`, `PYTHONPATH`, `PYTHONHOME`, Benutzerprofil-, Netzwerk-, Proxy-, Temp- oder Laufzeitvariablen, sind verboten. Kann der Interpreter mit dem exakten Block nicht erzeugt oder ausgefuehrt werden, endet der Einmalauftrag ohne Erweiterung oder Ersetzung des Blocks.

### 5.8 Workspace-Nebenwirkungspruefung

Unmittelbar vor dem Prozessstart und unmittelbar nach Prozessende oder Abbruch werden rein lesende Workspace-Manifeste gleichen Umfangs im Speicher gebildet. Sie enthalten mindestens relative Pfade, Dateityp, Dateilaenge, SHA-256 regulaerer Dateien und Schreibzeitpunkte; der unveraenderte `.git`-Bestand wird nicht traversiert. Neu angelegte, geloeschte oder veraenderte Dateien und Verzeichnisse sowie `__pycache__`, Bytecode, Cache-, Temp-, Log-, Dump-, Datenbank-, Zustands- oder Memory-Artefakte sperren das Ergebnis. Der Supervisor erzeugt selbst keine Datei und schreibt die Vergleichsdaten nicht in den Workspace.

Aus dem Workspace-Vergleich darf ausschliesslich der unveraenderte `.git`-Bestand ausgeschlossen werden. Weitere oder spaeter definierbare Pfadausschluesse, Ausschlusslisten und Ausnahmen vom Vorher-/Nachher-Vergleich sind unzulaessig. Kann der so festgelegte Vergleichsumfang nicht stabil und verlaesslich entschieden werden, endet der Einmalauftrag als technischer Abbruch; der Vergleichsumfang darf deshalb weder eingeschraenkt noch nachtraeglich veraendert werden.

Netzwerk-, Geraete-, Kamera-, Mikrofon-, Anzeige-, Zwischenablage-, Dienst- und sonstige externe Aktivitaet ist unzulaessig. Kann ihre Abwesenheit im spaeter gebundenen Ausfuehrungsweg nicht verlaesslich entschieden werden, ist dies ein technischer Abbruch und kein Anlass, die Grenze zu lockern.

### 5.9 Ergebnisvalidierung

Die stdout-Nutzlast wird erst nach eindeutigem Exitcode 0, beiden EOF-Signalen und bestaetigten Bytegrenzen als ASCII dekodiert. Sie muss genau eine JSON-Zeile mit abschliessendem LF und exakt diesen Schluesseln enthalten:

```text
contract_digest
effect_measurement_allowed
execution_locked
field_execution_allowed
hook_execution_allowed
```

Gleichzeitig muessen gelten:

```text
contract_digest: genau 64 kleingeschriebene Hexzeichen
effect_measurement_allowed: false
execution_locked: true
field_execution_allowed: false
hook_execution_allowed: false
```

Zusaetzliche Schluessel, Rohdaten, Einzeldigests, Kontaktwerte, Feldwerte, Zwischenobjekte, freie Texte oder mehr als eine Zeile sind unzulaessig. Der `contract_digest` ist nur ein technischer Integritaetswert. Die Validierung begruendet keinen wissenschaftlichen Befund.

Ein outward-facing Ausgabeformat des Supervisors wird in diesem Vorschlag nicht neu erfunden. `execute_once()` liefert stattdessen ein unveraenderliches internes Ergebnisobjekt mit den validierten Rohbytes, Exitcode und technischen Pruefflags. Eine spaetere einmalige Aufrufstelle muss vor ihrer Freigabe festlegen, wie dieses Objekt ohne Vertragsveraenderung entgegengenommen wird.

## 6. Vorgeschlagene statische Tests

Die Tests duerfen die Supervisor-Datei nicht importieren. Sie lesen nur deren Quelltext und AST. Vorgesehen sind:

- kein `subprocess`, kein Projektimport, kein Shell-Aufruf und kein automatischer Einstiegspunkt,
- alle geforderten Windows-API-Namen vorhanden,
- `CreateProcessW` statt alternativer Starter,
- genau ein syntaktisch vorgesehener `WriteFile`-Pfad und ein `ResumeThread`-Pfad,
- `TerminateJobObject` in allen zentralen Fehlerpfaden,
- Konstanten fuer Nutzlast, Hash, Stream-, Zeit-, CPU-, Speicher- und Prozessgrenzen stimmen mit Dokument 217 ueberein,
- Nutzlastmerkmale ASCII/UTF-8, kein BOM, nur LF und Schluss-LF sind gebunden; Normalisierung oder Ersatzbindung ist ausgeschlossen,
- absoluter Arbeitsordner, `lpApplicationName`, exakter veraenderbarer `lpCommandLine`-Puffer und alle vier Erzeugungsflags sind gebunden,
- Environment-Schluessel sind exakt begrenzt,
- Handle-Liste enthaelt nur die drei Child-Handles,
- `bInheritHandles=TRUE` und `STARTF_USESTDHANDLES` binden dieselben drei Handles,
- alle fuenf Job-Limit-Flags und ihre exakten Werte sind vorhanden,
- Wandzeit beginnt mit erfolgreichem `CreateProcessW`, Erfolgs-Exitcode ist 0 und Kindprozesse sind 0,
- exaktes fuenfteiliges ASCII-JSON-Erfolgsschema einschliesslich Schluss-LF ist gebunden,
- Workspace-Schreibzeitpunkte, Verzeichnisaenderungen, gesperrte Artefaktklassen und externe Seiteneffektgrenzen sind enthalten,
- kein Retry-, Wiederholungs- oder automatischer Fortsetzungspfad,
- keine Schreiboperation fuer Workspace-Artefakte.

Diese Tests koennen nur Strukturabweichungen erkennen. Sie sind kein Beweis fuer korrekte Windows-ABI-Nutzung, Runtimeverhalten, Deadlockfreiheit oder wirksame Ressourcenlimits.

## 7. Ausfuehrungssperren

Der Vorschlag erteilt insbesondere keine Freigabe fuer:

- Erstellung oder Aenderung von Supervisorcode,
- Import oder Ausfuehrung eines Supervisor-Moduls,
- Prozessstart oder `ResumeThread`,
- stdin-Transport oder Python-Parsing,
- Projektimporte,
- Runtime- oder ABI-Fixierung,
- Konstruktion eines neuen Vertrags,
- Preflight-Ausfuehrung,
- Bereinigung des Arbeitsbaums,
- Wiederholung oder automatische Fortsetzung,
- wissenschaftliche Interpretation.

Nach jeder Vertragsverletzung und ebenso nach einem akzeptierten technischen Erfolg folgen weder zweiter Versuch noch Korrekturlauf, Runtime-Aktivierung oder Runner-, Integrator-, Executor- beziehungsweise Hook-Aufruf. Auch ein technischer Erfolg erteilt keine Freigabe fuer Wiederholung oder einen nachgelagerten Pfad.

## 8. Durchgefuehrte Schritte und statische Beobachtungen

Durchgefuehrt wurden nur das Lesen der genannten Projektquellen, der Abgleich des Vertrags aus Dokument 217 und eine statische Suche nach bereits vorhandenen Implementierungsmustern fuer die benoetigten Windows-Prozess-, Job- und Handle-APIs in `tools`, `tests` und `mcm_field_organism`.

Beobachtetes Ergebnis: In den durchsuchten Codebereichen wurde kein bestehendes lokales Implementierungsmuster fuer `CreateProcessW`, `STARTUPINFOEX`, Job-Objekte oder die zugehoerige Handle-Liste gefunden. Daher verweist der Vorschlag nicht auf eine bestehende Projektabstraktion.

Messergebnisse und Gegenbaselines: Es wurde kein Prozess und kein Preflight ausgefuehrt. Es gibt keine Laufmessung und keine experimentelle Gegenbaseline. Der statische Gegenabgleich bestand ausschliesslich darin, jeden vorgeschlagenen Baustein auf eine Vorgabe aus Dokument 217 zurueckzufuehren und nicht gebundene Ausgaben oder Ausnahmen als offen zu markieren.

## 9. Grenzen und nicht gepruefte Annahmen

- Die korrekte ABI-Definition der Windows-Strukturen und Konstanten ist noch nicht geprueft.
- Die konkrete Python-Runtime und ihre Identitaet sind nicht fixiert.
- Die Funktionsfaehigkeit von Job-Zuweisung, Handle-Vererbung, Parallel-Lesern und EOF-Verhalten ist nicht getestet.
- Es ist nicht nachgewiesen, dass das Workspace-Manifest ohne vertragliche Ausnahmen stabil bleibt.
- Die spaetere Aufrufstelle und Ergebnisentgegennahme sind absichtlich nicht festgelegt.
- Statische AST-Tests koennen Runtimefehler nicht ausschliessen.
- Es liegt kein Preflight-Ergebnis und kein wissenschaftlicher Befund vor.

## 10. Schlussfolgerung und naechster Schritt

Dokument 217 laesst sich als eng begrenzte Windows-Supervisorstruktur abbilden, ohne Projektlogik oder wissenschaftliche Interpretation einzufuehren. Die zehn in Dokument 219 benannten Vertragsluecken wurden in diesem Vorschlag statisch geschlossen. Zwei Punkte bleiben vor jeder Ausfuehrung bewusst offen: die unabhaengig zu pruefende Windows-ABI-/Runtime-Fixierung und die separat zu bindende einmalige Aufrufstelle.

Der kleinste naechste Entwicklungsschritt ist die unabhaengige statische Pruefung dieses Vorschlags auf vollstaendige und widerspruchsfreie Abbildung von Dokument 217. Erst nach positiver Pruefung kann eine getrennte Entscheidung ueber die Implementierung der zwei vorgeschlagenen Dateien getroffen werden. Nach einer Implementierung waere erneut eine statische Implementierungspruefung erforderlich; auch deren Bestehen waere noch keine Freigabe zum Prozessstart.

Keine Zielabweichung vom aktuellen Projektziel wurde festgestellt.
