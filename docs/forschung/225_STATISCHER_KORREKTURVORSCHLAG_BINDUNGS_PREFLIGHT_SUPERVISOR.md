# 225 - Statischer Korrekturvorschlag fuer den Bindungs-Preflight-Supervisor

## 1. Forschungsfrage und Auftrag

Wie koennen die sechs statischen Befunde aus Dokument 224 geschlossen werden,
ohne einen Prozessstart, eine Runtime-Fixierung oder eine Erweiterung des
wissenschaftlichen Auftrags freizugeben?

Freigegeben ist ausschliesslich dieser Korrekturvorschlag. Er aendert keinen
Code und ist kein Forschungs-, Test- oder Preflight-Lauf. Vor jeder
Korrekturimplementierung ist eine unabhaengige statische Pruefung dieses
Vorschlags erforderlich.

## 2. Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/217_VORREGISTRIERUNG_EINMAL_AUSFUEHRUNGSAUFTRAG_BINDUNGS_PREFLIGHT.md`
- `docs/forschung/218_STATISCHER_IMPLEMENTIERUNGSVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/224_UNABHAENGIGE_STATISCHE_IMPLEMENTIERUNGSPRUEFUNG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/226_UNABHAENGIGE_STATISCHE_PRUEFUNG_KORREKTURVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- aktueller Korrektur-Eingang des Forschungshelfers

Keine externe Quelle wurde verwendet.

## 3. Betroffene Dateien und Schnittstellen

Eine spaetere, gesondert freizugebende Korrektur bleibt auf genau diese beiden
Dateien begrenzt:

- `tools/binding_preflight_supervisor.py`
- `tests/test_binding_preflight_supervisor_structure.py`

Der Vorschlag betrifft nur die bereits gebundenen Windows-Prozess-, Job-,
Handle-, Stream-, Zeit-, JSON- und Workspace-Pruefflaechen. Projektimporte,
eine Aufrufstelle und ein automatischer Einstiegspunkt bleiben ausgeschlossen.

## 4. Vorrangige Vertragsklaerung: Abbruch vor Job-Zuweisung

Dokument 218 verlangt bei Fehlern eine Job-Terminierung, sofern ein Job mit
Child existiert. Nach erfolgreichem `CreateProcessW`, aber fehlgeschlagenem
`AssignProcessToJobObject`, existiert jedoch noch kein Job mit diesem Child.
Der Child ist weiterhin suspendiert und darf niemals fortgesetzt werden.

Fuer ausschliesslich diesen Zustand wird folgende enge Abbruchregel
vorgeschlagen:

1. `CreateProcessW` war erfolgreich.
2. Der initiale Thread ist weiterhin suspendiert und `ResumeThread` wurde nie
   aufgerufen.
3. `AssignProcessToJobObject` ist fehlgeschlagen; der Child wurde dem Job nicht
   erfolgreich zugewiesen.
4. Es wurde kein stdin geschrieben und kein Child-Code freigegeben.
5. `TerminateProcess` darf dann genau einmal mit dem fest gebundenen
   numerischen Abbruchcode `1` aufgerufen werden. Eine spaetere Implementierung
   muss diesen Wert als unveraenderliche Konstante
   `PRE_JOB_ABORT_EXIT_CODE = 1` fuehren.
6. Das Prozessende muss innerhalb der in Abschnitt 5.2 gebundenen Fristen
   abgewartet und durch einen eindeutigen Exitcode ungleich `STILL_ACTIVE`
   bestaetigt werden.
7. Danach werden die noch besessenen Handles exakt einmal geschlossen und das
   Workspace-Nachmanifest gebildet und verglichen.

Schlaegt die Terminierung fehl oder kann das Prozessende nicht innerhalb der
gebundenen technischen Finalisierungsfrist bestaetigt werden, endet der
Auftrag technisch unentscheidbar und ohne Ergebnisannahme. Es gibt weder
Resume, Retry, zweiten Start noch eine alternative Terminierungsfolge.

Diese Ausnahme gilt nicht nach erfolgreicher Job-Zuweisung. Ab diesem Zustand
bleiben alle Fehlerpfade ausschliesslich an `TerminateJobObject` gebunden. Der
Vorschlag macht damit den bereits technisch notwendigen Sonderfall explizit,
statt ihn als ungebundene Implementierungsentscheidung zu belassen.

## 5. Eng begrenzte Korrekturpunkte

### 5.1 Workspace-Nachmanifest auf jedem Endpfad

Nach erfolgreicher Aufnahme des Vorzustandsmanifests muss eine gemeinsame
Finalisierung das Nachmanifest nach Prozessende oder bestaetigtem Abbruch
aufnehmen. Sie wird sowohl im Erfolgspfad als auch nach jedem spaeteren Fehler
erreicht. Vor- und Nachmanifest verwenden denselben Umfang; nur `.git` bleibt
wie in Dokument 218 ausgeschlossen.

Ein fehlgeschlagenes Nachmanifest oder jede Differenz sperrt die
Ergebnisannahme. Ein vorheriger technischer Fehler wird nicht verdeckt; beide
Fehlerlagen werden intern erhalten. Der Supervisor bereinigt oder veraendert
keine Workspace-Artefakte.

### 5.2 Erfolgsfrist und technische Finalisierungsfrist

Die Startmarke wird unmittelbar nach erfolgreicher Rueckkehr von
`CreateProcessW` gesetzt. Aus ihr wird die absolute Erfolgsfrist
`success_deadline = started_at + 60.0` abgeleitet. Job-Zuweisung,
Handle-Schliessung, Leserbereitschaft, stdin, Resume, regulaeres Prozessende
und EOF beider Leser muessen bis zu dieser Frist erfolgreich abgeschlossen
sein. Nur dann darf der Erfolgspfad fortgesetzt werden.

Sobald eine Grenzverletzung festgestellt oder die Erfolgsfrist erreicht ist,
ist die Ergebnisannahme unwiderruflich gesperrt. Der Child darf ab diesem
Zeitpunkt nicht mehr regulaer weiterlaufen. Unmittelbar mit dem ersten
erforderlichen Terminierungsaufruf wird genau eine technische
Finalisierungsfrist
`finalization_deadline = time.monotonic() + 5.0` gebildet. Diese fuenf
Sekunden dienen ausschliesslich:

- der Bestaetigung des Prozessendes,
- dem Abschluss beziehungsweise der eindeutigen Beendigung beider Reader,
- der einmaligen Schliessung noch besessener Handles,
- der Thread-/Handle-Nachbeobachtung nach bestaetigtem Prozessende,
- der Aufnahme und dem Vergleich des Workspace-Nachmanifests.

Die Finalisierungsfrist verlaengert niemals die 60-Sekunden-Erfolgsfrist,
erlaubt keine weitere Child-Ausfuehrung als Erfolg, kein Resume, keinen Retry
und keine Ergebnisannahme. Alle Finalisierungsschritte verwenden nur ihre
jeweils verbleibende Zeit; serielle feste Reader-Joins sind unzulaessig.

Kann das Prozessende bis zur Finalisierungsfrist nicht bestaetigt werden,
bleibt der Zustand technisch unentscheidbar. In diesem Fall wird kein
Workspace-Nachmanifest als stabiler Nachzustand behauptet. Nach Schliessung
aller noch schliessbaren Supervisorhandles, insbesondere des mit
`KILL_ON_JOB_CLOSE` gebundenen Jobhandles, endet der Auftrag ohne Ergebnis.
Diese ausdrueckliche Nichtentscheidbarkeit ist kein erfolgreich vollzogener
Abbruch und kein Seiteneffektfreiheitsnachweis.

### 5.3 Thread- und Handle-Beobachtung

Die spaetere Korrektur ergaenzt rein technische, nur im Speicher gehaltene
Beobachtungen fuer den Supervisorprozess in drei benannten Phasen:

- vor `CreateProcessW`,
- waehrend der Prozess-Wartephase,
- nach bestaetigtem Prozessende und abgeschlossener Reader-Finalisierung.

Die Beobachtungsschnittstelle wird auf genau folgende Windows-APIs begrenzt:

- `GetCurrentProcessId() -> DWORD`,
- `GetCurrentProcess() -> HANDLE`,
- `GetProcessHandleCount(HANDLE, PDWORD) -> BOOL`,
- `CreateToolhelp32Snapshot(DWORD, DWORD) -> HANDLE`,
- `Thread32First(HANDLE, LPTHREADENTRY32) -> BOOL`,
- `Thread32Next(HANDLE, LPTHREADENTRY32) -> BOOL`,
- das bereits gebundene `CloseHandle(HANDLE) -> BOOL`.

Fuer den Thread-Snapshot gilt ausschliesslich
`TH32CS_SNAPTHREAD = 0x00000004` mit zweitem Argument `0`. Die lokale
`THREADENTRY32`-Struktur enthaelt in dieser Reihenfolge `dwSize: DWORD`,
`cntUsage: DWORD`, `th32ThreadID: DWORD`, `th32OwnerProcessID: DWORD`,
`tpBasePri: LONG`, `tpDeltaPri: LONG` und `dwFlags: DWORD`; `dwSize` wird vor
`Thread32First` auf `sizeof(THREADENTRY32)` gesetzt. Gezaehlt werden nur
Eintraege mit `th32OwnerProcessID == GetCurrentProcessId()`. Ein
`INVALID_HANDLE_VALUE`, ein erster Abfragefehler oder ein Iterationsende, das
nicht dem normalen `ERROR_NO_MORE_FILES = 18` entspricht, ist fail-closed ein
technischer Beobachtungsfehler. `kernel32` wird dafuer mit
`ctypes.WinDLL(..., use_last_error=True)` gebunden; unmittelbar nach dem
fehlgeschlagenen `Thread32Next` wird der Fehler ausschliesslich mit
`ctypes.get_last_error()` gelesen.

Jeder Snapshot ist ein temporaeres, nicht vererbbares Supervisorhandle mit
genau einem Besitzer und genau einer `CloseHandle`-Schliessstelle. Er wird in
derselben Beobachtungsfunktion in einem `finally`-Pfad geschlossen, bevor
`GetProcessHandleCount(GetCurrentProcess(), ...)` aufgerufen wird. Das von
`GetCurrentProcess()` gelieferte Pseudohandle wird niemals geschlossen. So
geht das temporaere Snapshot-Handle nicht dauerhaft in die anschliessende
Handlezahl ein.

Die Werte werden in den unveraenderlichen internen Strukturen
`TechnicalObservation(thread_count: int, handle_count: int)` und
`TechnicalObservations(before, during, after)` gehalten. Die drei Felder der
zweiten Struktur sind jeweils `TechnicalObservation | None`. Ein technischer
Erfolg verlangt drei vorhandene Werte. Ein Abbruch bewahrt alle bis dahin
vorhandenen Werte in seinem internen technischen Abbruchobjekt; fehlende
spaetere Phasen bleiben explizit `None`. Das bereits gebundene stdout-JSON
wird dadurch nicht erweitert.

Die genannten API-Namen, Konstanten, Strukturfelder, `argtypes` und `restype`
sowie das Handle-Eigentum muessen in der spaeteren statischen
Implementierungspruefung gegen eine ausdruecklich freigegebene Windows-
Primaerquelle geprueft werden. Diese spaetere ABI-Pruefung ist keine
Voraussetzung, die eine weitere Vertragsentscheidung zwischen diesem
Vorschlag und der Implementierung erfordert.

Die Werte sind technische Beobachtungen. Sie erweitern weder das
Erfolgsschema noch bilden sie eine neue Sperrschwelle oder wissenschaftliche
Messung.

### 5.4 Eindeutige JSON-Schluessel

Die JSON-Ausgabe wird mit einer Paarfolge dekodiert, die jeden mehrfach
auftretenden Schluessel vor der Dictionary-Bildung fail-closed ablehnt. Erst
danach werden die exakt fuenf gebundenen Schluessel, ihre Werte, die einzelne
ASCII-Zeile und das Schluss-LF geprueft. Weder erster noch letzter Wert eines
doppelten Schluessels darf akzeptiert werden.

### 5.5 Statische Testabdeckung

Die statischen Tests bleiben auf Quelltext und AST begrenzt und duerfen den
Supervisor weder importieren noch ausfuehren. Sie muessen zusaetzlich sichern:

- Nachmanifest und Vergleich sind nach jedem Endpfad erreichbar, nachdem ein
  Vorzustandsmanifest aufgenommen wurde.
- Die absolute Frist entsteht nach erfolgreichem `CreateProcessW`; Prozess-
  und EOF-Warten koennen die 60-Sekunden-Erfolgsfrist nicht erweitern. Die
  technische Finalisierungsfrist ist exakt fuenf Sekunden lang und kann nur
  nach unwiderruflicher Ergebnissperre entstehen.
- Thread- und Handlebeobachtungen sind mit den festgelegten APIs, Strukturen,
  Besitzregeln und internen Datensaetzen in allen drei Phasen gebunden.
- `TerminateProcess` ist nur im bewachten Zustand vor erfolgreicher
  Job-Zuweisung und vor jedem Resume mit exakt dem Abbruchcode `1` zulaessig;
  nach Job-Zuweisung wird nur `TerminateJobObject` verwendet.
- Doppelte JSON-Schluessel werden vor der Dictionary-Bildung abgelehnt.
- `__pycache__`, Bytecode, Cache-, Temp-, Log-, Dump-, Datenbank-, Zustands-
  und Memory-Artefakte sind als gesperrte Klassen statisch abgedeckt. Der
  bisherige Gegentest, der die Nennung von `__pycache__` verbietet, wird
  ersetzt.

Reine Namens- oder Stringvorkommen genuegen fuer Kontrollflussvertraege nicht.
Die AST-Pruefungen muessen Reihenfolge, Zustandswaechter und gemeinsame Frist
strukturell absichern, soweit dies ohne Import oder Ausfuehrung moeglich ist.

## 6. Unveraenderte Vertragsgrenzen

- Genau ein syntaktischer `CreateProcessW`-, `WriteFile`- und
  `ResumeThread`-Pfad bleibt bestehen.
- Kein Child-Code darf vor erfolgreicher Job-Zuweisung, deren Rueckpruefung,
  Readerbereitschaft und stdin-Vertrag freigegeben werden.
- Die Nutzlast, Limits, Environment-, Stream- und Ergebnisschemabindungen aus
  Dokument 218 bleiben unveraendert.
- Die externe Aktivitaetspruefung bleibt fail-closed; dieser Vorschlag erfindet
  keinen ausfuehrbaren Ersatz.
- Es entstehen keine Ergebnis-, Log-, Temp- oder Bereinigungsdateien.
- Ein positives statisches Ergebnis waere keine Test- oder Prozessstartfreigabe.

## 7. Durchgefuehrte Schritte, Messergebnisse und Gegenbaselines

Durchgefuehrt wurden nur das Lesen der aktuellen Projektregeln und der
Dokumente 217, 218 und 224 sowie die statische Ableitung dieses eng begrenzten
Korrekturvorschlags. Supervisor und Testdatei wurden nicht geaendert.

Es wurden keine Tests, Projektimporte, Python-Parser, Prozesse, stdin-
Transporte oder Preflights ausgefuehrt. Daher gibt es keine Laufmessung und
keine experimentelle Gegenbaseline. Die einzige Gegenpruefung war der
statische Abgleich jedes Korrekturpunkts mit einem Befund aus Abschnitt 5 von
Dokument 224.

## 8. Grenzen, Nichtnachweis und offene Annahmen

- Die Beobachtungs-APIs und ihre Vertragssignaturen sind festgelegt; ihre
  korrekte Windows-ABI-Abbildung ist noch nicht unabhaengig gegen eine
  Primaerquelle geprueft.
- Kontrollfluss, Terminierungswirksamkeit, EOF-Verhalten und Wandzeitgrenze
  sind nicht ausgefuehrt oder nachgewiesen.
- Die statischen Tests wurden nicht implementiert oder ausgefuehrt.
- Der Workspace-Vergleich wurde nicht praktisch auf Stabilitaet geprueft.
- Ein aufrufbarer Preflightpfad bleibt wegen der fail-closed externen
  Aktivitaetsgrenze nicht nachgewiesen.
- Es liegt kein technischer Erfolg und kein wissenschaftlicher Befund vor.
- Memory, Organisation, Topologie, Bedeutung, Selbstregulation und KI sind
  nicht nachgewiesen.

## 9. Schlussfolgerung und naechster Schritt

Der Vorschlag klaert zuerst den bislang ungebundenen Abbruch vor erfolgreicher
Job-Zuweisung und beschraenkt alle weiteren Aenderungen auf die sechs Befunde
aus Dokument 224. Die drei Korrekturen aus Dokument 226 sind mit Abbruchcode
`1`, getrennter 60-Sekunden-Erfolgs- und 5-Sekunden-Finalisierungsfrist sowie
fest gebundener Beobachtungsschnittstelle geschlossen. Er verschiebt weder
Projektziel noch Aussagegrenze.

Der kleinste naechste Entwicklungsschritt ist die unabhaengige statische
Pruefung dieses Dokuments gegen Dokumente 217, 218 und 224. Erst nach einer
ausdruecklichen Freigabe duerfen die zwei benannten Dateien korrigiert werden.
Danach ist erneut ausschliesslich eine getrennte statische
Implementierungspruefung zulaessig; Tests und Prozessstart bleiben weiterhin
gesondert gesperrt.
