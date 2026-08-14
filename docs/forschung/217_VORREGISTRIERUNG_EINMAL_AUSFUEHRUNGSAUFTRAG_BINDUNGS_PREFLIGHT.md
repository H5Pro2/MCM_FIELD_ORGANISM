# Vorregistrierung des Einmal-Ausfuehrungsauftrags fuer den Bindungs-Preflight

## 1. Forschungsfrage und Auftrag

Kann der bereits statisch gepruefte Bindungs-Preflight als genau ein spaeter
separat freizugebender Prozessstart vorregistriert werden, ohne ihn jetzt
auszufuehren oder seine fachliche Aussagegrenze zu erweitern?

Dieses Dokument registriert ausschliesslich den Einmal-Ausfuehrungsauftrag.
Es startet keinen Prozess, importiert kein Projektmodul und konstruiert weder
Runtime-Fixierung noch Vertrag oder Feld.

## 2. Verwendete Quellen und Dateien

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- aktueller Freigabe-Eingang des Forschungshelfers
- `docs/forschung/215_BINDUNGS_PREFLIGHT_STDIN_NUTZLAST.txt`
- `docs/forschung/216_VORREGISTRIERUNG_EINMALIGER_BINDUNGS_PREFLIGHT_STDIN.md`

Keine externe Quelle wurde verwendet.

## 3. Unveraenderliche Auftragsidentitaet

Ein spaeterer Ausfuehrungsversuch muss vor jedem Prozessstart exakt folgende
Nutzlastbindung bestaetigen:

```text
Nutzlast: docs/forschung/215_BINDUNGS_PREFLIGHT_STDIN_NUTZLAST.txt
Byteumfang: 1806
SHA-256: d86be4be95ed54ea461aea4c538639cec179726ccca30b14dd762a605351b393
Kodierung: ASCII, zugleich gueltiges UTF-8
BOM: nein
Zeilenenden: ausschliesslich LF
abschliessendes LF: ja
```

Der Auftrag ist bei jeder Abweichung gesperrt. Weder Nutzlast noch Digest oder
Byteumfang duerfen fuer eine Ausfuehrung korrigiert, normalisiert oder neu
berechnet und anschliessend akzeptiert werden.

## 4. Exakter Prozessstart

Der spaeter separat freizugebende Versuch darf genau einen Kindprozess ohne
Shell starten:

```text
Arbeitsordner: C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace
lpApplicationName: C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\.venv\Scripts\python.exe
lpCommandLine: "C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\.venv\Scripts\python.exe" -B -I -
Shell: keine
Erzeugungszustand: CREATE_SUSPENDED | CREATE_NO_WINDOW | EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT
stdin: umgeleitet
stdout: umgeleitet
stderr: umgeleitet
```

`lpCommandLine` muss als eigener veraenderbarer, nullterminierter UTF-16-Puffer
mit exakt dem dargestellten Inhalt an `CreateProcessW` uebergeben werden. Es
duerfen weder weitere Argumente noch eine nachtraegliche Quoting-, Pfad- oder
Shelltransformation erfolgen.

Der Prozess wird mit `STARTUPINFOEXW` und `bInheritHandles=TRUE` erzeugt. Die
Attributliste `PROC_THREAD_ATTRIBUTE_HANDLE_LIST` darf exakt drei Handles
enthalten: `child_stdin_read`, `child_stdout_write` und
`child_stderr_write`. Dieselben drei Handles sind in
`STARTF_USESTDHANDLES` als `hStdInput`, `hStdOutput` und `hStdError` zu setzen.
Alle drei Kindhandles muessen vererbbar sein. Die supervisorseitigen
Gegenhandles sowie Prozess-, Thread- und Jobhandles muessen nicht vererbbar
sein. Weitere vererbbare oder in der Attributliste enthaltene Handles sperren
den Auftrag vor dem Fortsetzen des Hauptthreads.

Der Supervisor muss den Prozess ueber `CreateProcessW` suspendiert erzeugen,
vor der ersten Python-Instruktion dem in Abschnitt 6 festgelegten Windows Job
Object zuordnen und alle gesetzten Jobgrenzen zuruecklesen. Nach erfolgreicher
Jobzuordnung und Rueckpruefung muss der Supervisor seine eigenen Kopien von
`child_stdin_read`, `child_stdout_write` und `child_stderr_write` jeweils
genau einmal mit `CloseHandle` schliessen. Diese drei Schliessungen muessen vor
der stdin-Uebergabe und vor `ResumeThread` abgeschlossen sein. Schlaegt eine
Schliessung fehl, muss der Supervisor den Gesamtauftrag sofort abbrechen und
das Job Object terminieren. Die supervisorseitigen stdout- und stderr-
Lesehandles bleiben fuer die beiden Rohbyte-Leser geoeffnet; das
supervisorseitige stdin-Schreibhandle bleibt nur bis zu seiner Schliessung
gemaess Abschnitt 5 geoeffnet.

Erst nach der vollstaendigen stdin-Uebergabe und Schliessung aus Abschnitt 5
darf der Supervisor den initialen Hauptthread genau einmal fortsetzen.
Schlaegt Erzeugung, Jobzuordnung, Rueckpruefung, eine der drei
Childhandle-Schliessungen, stdin-Uebergabe oder Fortsetzung fehl, wird der
Prozess durch Terminierung des Job Objects beendet.

Es sind kein zweiter Prozessstart, keine Shellauswertung, kein `-c`, keine
temporaere Quelldatei, kein Retry, keine parallelen Kindprozesse und keine
automatische Fortsetzung zulaessig. Die in Abschnitt 6 festgelegten zwei
gleichzeitigen supervisorseitigen Ausgabeleser sind hiervon ausgenommen.

## 5. Einmaliger stdin-Transport

Der Supervisor muss die 1806 vorab geprueften Rohbytes vor Prozessstart im
Arbeitsspeicher halten. Die stdin-Pipe muss vor `CreateProcessW` durch genau
einen erfolgreichen Aufruf
`CreatePipe(&child_stdin_read, &supervisor_stdin_write, &sa, 4096)` erzeugt
werden. `sa.bInheritHandle` muss dabei `TRUE` sein. Anschliessend muss der
Supervisor die Vererbbarkeit von `supervisor_stdin_write` mit
`SetHandleInformation` entfernen; nur `child_stdin_read` darf als stdin-Handle
in der Handle-Allowlist aus Abschnitt 4 verbleiben.

Nach dem einzigen erfolgreichen, weiterhin suspendierten Prozessstart muss
der Supervisor genau einen `WriteFile`-Aufruf mit Offset 0 und Laenge 1806 auf
`supervisor_stdin_write` ausfuehren. Der Aufruf gilt nur dann als erfolgreich,
wenn er Erfolg meldet und `bytesWritten == 1806` gilt. Jeder andere
Rueckgabewert ist ein Teiltransport und beendet den Gesamtversuch.

`FlushFileBuffers` oder jede andere Flush-Operation auf der stdin-Pipe ist
verboten. Unmittelbar nach dem erfolgreichen `WriteFile` muss der Supervisor
`supervisor_stdin_write` genau einmal mit `CloseHandle` schliessen. Erst nach
dieser erfolgreichen Schliessung darf der initiale Hauptthread genau einmal
fortgesetzt werden.

Teilweises Schreiben, Textdekodierung, Zeilenumwandlung, BOM-Ergaenzung,
zweiter Schreibaufruf, Flush, interaktive Eingabe oder Nachlieferung sind
verboten. Jede Abweichung beendet den Gesamtversuch ohne Retry und ohne
Ergebnisannahme.

## 6. Zeit-, Prozess- und Ausgabegrenzen

Fuer den genau einen Prozess gelten:

```text
Wandzeit ab erfolgreichem Start: maximal 60 Sekunden
Benutzer-CPU-Zeit des Prozesses: maximal 30 Sekunden
Prozess-Commit-Speicher: maximal 1073741824 Byte
Job-Commit-Speicher: maximal 1073741824 Byte
Aktive Prozesse im Job: maximal 1
Kindprozesse des Python-Prozesses: 0
Retry oder Neustart: 0
stdout: maximal 4096 Byte
stderr: exakt 0 Byte im akzeptierten Ergebnis
zulaessiger Erfolgs-Exitcode: 0
```

Vor dem Fortsetzen des suspendierten Hauptthreads muss ein neues, nur fuer
diesen Versuch gehaltenes Windows Job Object exakt mit
`JOB_OBJECT_LIMIT_PROCESS_TIME`, `JOB_OBJECT_LIMIT_PROCESS_MEMORY`,
`JOB_OBJECT_LIMIT_JOB_MEMORY`, `JOB_OBJECT_LIMIT_ACTIVE_PROCESS` und
`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` konfiguriert sein. Die CPU-Grenze ist als
`300000000` Einheiten zu je 100 Nanosekunden zu setzen. Beide Speichergrenzen
sind auf `1073741824` Byte und die Aktivprozessgrenze auf `1` zu setzen. Der
Prozess darf erst nach erfolgreicher Rueckpruefung dieser Werte fortgesetzt
werden. Beim Schliessen oder Verlust des Supervisor-Jobhandles muss der
Prozess beendet werden.

Bei Zeitueberschreitung muss der Supervisor den Prozess mitsamt moeglichem
Prozessbaum beenden. Jede Ausgabegrenzueberschreitung, jeder nicht eindeutige
Exit, jeder andere Exitcode oder jeder beobachtete Kindprozess sperrt das
Ergebnis. Thread- und Handlewerte werden vor Start, waehrend des Wartens und
nach Prozessende nur beobachtet; aus ihnen folgt keine wissenschaftliche
Messung.

Vor dem Fortsetzen des Hauptthreads muessen genau zwei unabhaengige
supervisorseitige Rohbyte-Leser bereitstehen, je einer fuer stdout und stderr.
Beide lesen ab Fortsetzung gleichzeitig und ohne Textdekodierung bis EOF,
Grenzverletzung oder Abbruch. Der stdout-Puffer hat exakt 4097 Byte Kapazitaet,
der stderr-Puffer exakt 1 Byte Kapazitaet. Mit Eingang des 4097. stdout-Bytes
oder des ersten stderr-Bytes muss der Supervisor das gesamte Job Object sofort
beenden; das Ergebnis bleibt gesperrt. Ein Leserfehler, ein unvollstaendig
beobachtetes Pipe-Ende oder ein Prozessende ohne anschliessendes EOF auf beiden
Pipes ist ebenfalls ein technischer Abbruch. Eine Dekodierung oder JSON-Pruefung
darf erst nach Exitcode 0, beiden EOF-Signalen und bestaetigten Bytegrenzen
erfolgen.

## 6a. Exakter Environment-Block

`CreateProcessW` erhaelt keinen geerbten Environment-Block. Mit
`CREATE_UNICODE_ENVIRONMENT` wird exakt der folgende, alphabetisch sortierte
UTF-16-Block uebergeben:

```text
SystemRoot=C:\Windows\0
WINDIR=C:\Windows\0
\0
```

Die dargestellten `\0` bezeichnen jeweils ein einzelnes UTF-16-NUL; nach dem
letzten Eintrag folgt damit das vorgeschriebene zweite NUL. Weitere Variablen,
insbesondere `PATH`, `PYTHONPATH`, `PYTHONHOME`, Benutzerprofil-, Netzwerk-,
Proxy-, Temp- oder Laufzeitvariablen, sind verboten. Kann der Interpreter mit
diesem Block nicht erzeugt oder ausgefuehrt werden, endet der Einmalauftrag
ohne Erweiterung oder Ersetzung des Blocks.

## 7. Exakte Erfolgsannahme

Ein technischer Erfolg darf nur angenommen werden, wenn alle bisherigen
Grenzen eingehalten sind und `stdout` genau eine ASCII-JSON-Zeile mit
abschliessendem LF und exakt diesen Schluesseln enthaelt:

```text
contract_digest
effect_measurement_allowed
execution_locked
field_execution_allowed
hook_execution_allowed
```

Zusaetzlich muessen gleichzeitig gelten:

```text
contract_digest: genau 64 kleingeschriebene Hexzeichen
effect_measurement_allowed: false
execution_locked: true
field_execution_allowed: false
hook_execution_allowed: false
```

Zusaetzliche Schluessel, Rohdaten, Einzeldigests, Kontaktwerte, Feldwerte,
Zwischenobjekte, freie Texte oder mehr als eine Zeile sind unzulaessig. Der
`contract_digest` ist ausschliesslich ein technischer Integritaetswert.

## 8. Vorher-/Nachher-Grenze

Unmittelbar vor Prozessstart muss ein nur im Supervisorspeicher gehaltener
Workspace-Vorzustand aufgenommen werden. Unmittelbar nach Prozessende oder
Abbruch muss derselbe Umfang erneut aufgenommen werden. Mindestens zu
vergleichen sind vorhandene Pfade, Dateilaengen, SHA-256-Inhalte und
Schreibzeitpunkte unter Ausschluss des unveraenderten `.git`-Bestands.

Neu angelegte, geloeschte oder veraenderte Dateien und Verzeichnisse,
`__pycache__`, Bytecode, Cache-, Temp-, Log-, Dump-, Datenbank-, Zustand- oder
Memory-Artefakte sperren das Ergebnis. Die Vergleichsdaten duerfen waehrend
des Versuchs nicht in den Workspace geschrieben werden.

Netzwerk-, Geraete-, Kamera-, Mikrofon-, Anzeige-, Zwischenablage-, Dienst-
oder sonstige externe Aktivitaet ist unzulaessig. Eine nicht verlaesslich
entscheidbare Seiteneffektpruefung wird als technischer Abbruch behandelt.

## 9. Abbruch- und Einmaligkeitsvertrag

Der Gesamtversuch endet ohne Teilresultat, wenn eine Vorbedingung, Bytebindung,
Transportgrenze, Laufzeitgrenze, Ausgabegrenze, Sperrbedingung oder
Seiteneffektgrenze verletzt wird. Es folgen weder zweiter Versuch noch
Korrekturlauf, Runtime-Aktivierung, Runner-, Integrator-, Executor- oder
Hook-Aufruf.

Auch ein akzeptierter technischer Erfolg beendet den Auftrag unmittelbar. Er
erteilt keine Freigabe fuer eine Wiederholung oder einen nachgelagerten Pfad.

## 10. Laufnummer und Dokumentation

Diese Vorregistrierung ist kein Lauf und erhaelt keine Laufnummer. Erst
unmittelbar vor einem spaeter ausdruecklich freigegebenen realen Prozessstart
wird die naechste Laufnummer aus dem letzten nachweislich ausgefuehrten Lauf
bestimmt.

Ein spaeterer Ergebnisbericht muss mit `Lauf XX` beginnen und getrennt
ausweisen:

- beobachtete Prozess- und Vertragsmessung;
- technische Interpretation;
- Hypothese;
- Nichtnachweis;
- offene oder nicht gepruefte Annahmen.

## 11. Fortbestehende Sperren

Dieses Dokument setzt kein Freigabefeld. Gesperrt bleiben insbesondere:

- die Ausfuehrung des hier beschriebenen Auftrags;
- jede Wiederholung des Preflights;
- Feld- und Rezeptorkonstruktion;
- Runner-, Integrator-, Executor- und Hook-Ausfuehrung;
- Effektmessung und wissenschaftliche Interpretation;
- Public-AV, Live-Sensorik und physischer Weltkontakt;
- persistente Zustands- oder Memory-Artefakte;
- Produktionsanbindung und automatische Fortsetzung.

## 12. Durchgefuehrte Schritte und statisches Ergebnis

- Die verbindlichen Projektleitdokumente wurden gelesen.
- Die Nutzlastbindung wurde erneut ausschliesslich ueber Dateibytes geprueft.
- Byteumfang 1806, der gebundene SHA-256-Digest, fehlender BOM,
  ausschliessliche LF-Zeilenenden und Schluss-LF stimmen weiterhin.
- Prozess-, stdin-, Zeit-, Ausgabe-, Erfolgs-, Abbruch- und Nachlaufgrenzen
  wurden fuer genau einen spaeteren Start festgelegt.
- `lpApplicationName`, der veraenderbare `lpCommandLine`-Puffer, die exakte
  Handle-Allowlist, der vollstaendige 1806-Byte-Schreibnachweis, zwei
  gleichzeitige rohbytebasierte Ausgabeleser, die unmittelbaren
  Ausgabeabbrueche und der Environment-Block wurden statisch gebunden.
- Die supervisorseitigen Kopien von `child_stdin_read`,
  `child_stdout_write` und `child_stderr_write` muessen nach erfolgreicher
  Jobzuordnung und Rueckpruefung, vor stdin-Uebergabe und vor `ResumeThread`,
  jeweils genau einmal geschlossen werden; jeder Schliessfehler terminiert
  den Gesamtauftrag ueber das Job Object.
- Die stdin-Pipe ist mit `CreatePipe`, Pufferwert `4096`, genau einem
  `WriteFile`, verbotenem `FlushFileBuffers`, unmittelbarem `CloseHandle` und
  anschliessender einmaliger Fortsetzung des Hauptthreads gebunden.
- Es wurde kein Prozess gestartet und keine Projektfunktion ausgefuehrt.

Beobachtete Messung: ausschliesslich die erneut bestaetigten
Nutzlast-Bytemerkmale. Gegenbaselines wurden nicht ausgefuehrt. Diese Arbeit
erhaelt keine Laufnummer.

## 13. Grenzen, Nichtnachweis und offene Annahmen

Nicht geprueft sind Python-Parsing, Projektimports, Runtime-Fixierung,
Vertragskonstruktion, reale Laufzeit, realer Ressourcenverbrauch,
Vertragsdigest, Ausgabe, Prozessbaum und Seiteneffektfreiheit. Ob der
Supervisor alle vorregistrierten Grenzen auf der aktuellen Windows-Plattform
vollstaendig beobachten kann, bleibt vor Ausfuehrung technisch zu bestaetigen.
Eine passende Supervisorimplementierung wird durch dieses Dokument weder
bereitgestellt noch freigegeben.

Es gibt keinen Befund zu Vorzustandswirkung, Feldwirkung, Memory,
Organisation, Topologie, Bedeutung, Semantik, Selbstregulation oder KI.

## 14. Schlussfolgerung und naechster Schritt

Der Einmal-Ausfuehrungsauftrag ist mit unveraenderter 1806-Byte-Nutzlast,
festem Digest, genau einem Prozessstart sowie eindeutigem Windows-Prozess-,
Handle-, stdin-, Ausgabe- und Environment-Vertrag vorregistriert. Eine
Zielabweichung ist nicht erkennbar.

Kleinster naechster Schritt ist die unabhaengige statische Pruefung dieses
Dokuments. Erst eine ausdrueckliche anschliessende Freigabe darf genau diesen
Auftrag einmal ausfuehren.
