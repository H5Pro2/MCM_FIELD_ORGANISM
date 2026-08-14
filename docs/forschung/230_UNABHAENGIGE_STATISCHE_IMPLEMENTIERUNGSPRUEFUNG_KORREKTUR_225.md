# 230 - Unabhaengige statische Implementierungspruefung der Korrektur 225

## 1. Forschungsfrage und Auftrag

Bilden `tools/binding_preflight_supervisor.py` und
`tests/test_binding_preflight_supervisor_structure.py` die sechs in Dokument
225 gebundenen Korrekturflaechen vollstaendig und widerspruchsfrei ab?

Freigegeben und durchgefuehrt wurde ausschliesslich diese statische
Implementierungspruefung. Sie ist kein Forschungs-, Test- oder Programmlauf.

## 2. Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/225_STATISCHER_KORREKTURVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `tools/binding_preflight_supervisor.py`
- `tests/test_binding_preflight_supervisor_structure.py`
- aktueller Freigabe-Eingang des Forschungshelfers

Keine externe Quelle wurde verwendet. Eine ausdruecklich freigegebene
Windows-Primaerquelle lag fuer diese Pruefung nicht vor.

## 3. Verwendete Dateien und Schnittstellen

Die zwei Implementierungsdateien wurden ausschliesslich als Text gelesen und
statisch gegen Dokument 225 verglichen. Sie wurden nicht geaendert,
importiert, geparst oder ausgefuehrt. Tests, Prozesse, stdin-Transport und
Preflight-Schnittstellen wurden nicht verwendet. Der weitere abweichende
Arbeitsbaum wurde nicht als geprueft oder freigegeben behandelt.

## 4. Durchgefuehrte Schritte

1. Projekt-, Evidenz- und Ausfuehrungsgrenzen gelesen.
2. Konstanten, Windows-Bindungen und interne Beobachtungsstrukturen geprueft.
3. Erfolgs-, Abbruch- und technisch unentscheidbare Pfade statisch verfolgt.
4. Readerabschluss, Handle-Schliessung, Nachbeobachtung und Nachmanifest gegen
   die gemeinsamen Fristen aus Dokument 225 abgeglichen.
5. Die statischen Tests auf strukturelle Abdeckung dieser Pfade geprueft.

## 5. Statische Befunde

### 5.1 Hoch - Bestaetigtes Prozessende besitzt keinen vollstaendigen Finalisierungspfad

Nach `WaitForSingleObject == WAIT_OBJECT_0` wird `process_ended = True`
gesetzt. Schlaegt danach `_finish_readers(readers, success_deadline)` fehl,
wechselt der Fehlerpfad nicht in eine neue technische
5-Sekunden-Finalisierungsfrist. Er verwendet stattdessen die bereits
verbrauchte oder ablaufende `success_deadline`.

Damit kann gerade nach bestaetigtem Prozessende der Readerabschluss sofort
scheitern, obwohl Dokument 225 die technische Finalisierung von Readern,
Handles, Nachbeobachtung und Nachmanifest getrennt bindet. Die
Ergebnisannahme bleibt zwar gesperrt, aber die vorgeschriebene technische
Finalisierung ist nicht vollstaendig abgebildet.

### 5.2 Hoch - Ein Finalisierungsfehler ueberspringt nachfolgende Pflichtschritte

Readerabschluss, `_close_process_resources`, Nachbeobachtung und Nachmanifest
liegen im Abbruchpfad in einem einzigen `try`-Block. Wirft
`_finish_readers` oder eine Handle-Schliessung eine Ausnahme, werden alle
nachfolgenden Schritte uebersprungen. Der Fehler wird lediglich in
`finalization_errors` aufgenommen; `finally` schliesst verbleibende Handles,
nimmt aber weder die Nachbeobachtung noch das Nachmanifest auf.

Dokument 225 verlangt eine gemeinsame Finalisierung und die Erhaltung
mehrerer Fehlerlagen. Das erfordert, dass unabhaengig noch moegliche
Pflichtschritte jeweils versucht und ihre Fehler getrennt bewahrt werden.

### 5.3 Mittel - Finalisierungsfrist begrenzt nicht alle Finalisierungsschritte

Die verbleibende Frist wird fuer Prozess-Wait und Reader-Joins verwendet.
Handle-Schliessung, Nachbeobachtung sowie Aufnahme und Vergleich des
Workspace-Nachmanifests pruefen die `finalization_deadline` dagegen weder vor
noch nach ihrem Schritt. Damit ist statisch nicht gebunden, dass alle
Finalisierungsschritte nur ihre jeweils verbleibende Zeit verwenden.

### 5.4 Hoch - Statische Tests sichern die fehlerhaften Pfade nicht ab

`test_finalization_and_manifest_paths_are_structurally_bound` prueft nur
Textvorkommen, Reihenfolge eines Friststrings und die Anzahl zweier
Nachmanifest-Aufrufe. Der Test beweist weder:

- eine technische Finalisierungsfrist nach bestaetigtem Prozessende mit
  gescheitertem EOF-Abschluss,
- die Fortsetzung unabhaengiger Finalisierungsschritte nach einem Reader- oder
  Handlefehler,
- Fristpruefungen fuer Handle-Schliessung, Nachbeobachtung und Nachmanifest.

Die von Dokument 225 verlangte strukturelle Kontrollflussabdeckung ist damit
an den entscheidenden Fehlerpfaden nicht vorhanden.

### 5.5 Offen - Windows-ABI nicht gegen freigegebene Primaerquelle geprueft

API-Namen, Konstanten, `THREADENTRY32`, `argtypes` und `restype` sind im
Quelltext vorhanden. Dokument 225 verlangt fuer diese statische
Implementierungspruefung jedoch den Abgleich gegen eine ausdruecklich
freigegebene Windows-Primaerquelle. Eine solche Quelle lag nicht vor. Die
ABI-Abbildung kann deshalb weder bestaetigt noch verworfen werden.

## 6. Bestaetigte statische Vertragsanteile

- `PRE_JOB_ABORT_EXIT_CODE = 1` und `FINALIZATION_SECONDS = 5.0` sind fest
  gebunden.
- `TerminateProcess` liegt syntaktisch nur im Vor-Job-Zweig; nach
  Job-Zuweisung wird `TerminateJobObject` verwendet.
- Die Startmarke folgt dem erfolgreichen `CreateProcessW`-Aufruf.
- `TechnicalObservation` und `TechnicalObservations` sowie die drei
  Beobachtungsphasen sind vorhanden.
- Das Snapshot-Handle wird vor `GetProcessHandleCount` geschlossen; das
  Prozess-Pseudohandle wird nicht geschlossen.
- Doppelte JSON-Schluessel werden vor der Dictionary-Bildung abgelehnt.
- Die Workspace-Funktion schliesst nur `.git` aus und schreibt keine
  Artefakte.

Diese bestaetigten Anteile heben die Befunde aus Abschnitt 5 nicht auf.

## 7. Messergebnisse und Gegenbaseline

Es wurde kein Test, Prozess oder Preflight ausgefuehrt. Es gibt keine
Laufmessung und keine experimentelle Gegenbaseline.

Beobachtetes statisches Ergebnis: Mehrere Korrekturflaechen sind vorhanden,
aber die gemeinsame, fristgebundene Finalisierung ist auf wesentlichen
Fehlerpfaden unvollstaendig.

Technische Interpretation: Die Implementierung besteht die statische
Implementierungspruefung noch nicht und ist keine Grundlage fuer eine
Ausfuehrungsentscheidung.

## 8. Grenzen und Nichtnachweis

- Syntax, AST und Tests wurden nicht ausgefuehrt.
- Windows-ABI und Runtimeverhalten wurden nicht geprueft.
- Terminierungs-, EOF-, Handle- und Workspace-Verhalten sind nicht praktisch
  nachgewiesen.
- Der fail-closed externe Aktivitaetsschutz bleibt unveraendert.
- Es liegt kein technischer Erfolg oder wissenschaftlicher Befund vor.
- Memory, Organisation, Topologie, Bedeutung, Selbstregulation und KI sind
  nicht nachgewiesen.

## 9. Schlussfolgerung und naechster Schritt

Die Korrekturimplementierung besteht die unabhaengige statische Pruefung nicht.
Keine Zielabweichung wurde festgestellt; die Abweichungen betreffen allein den
gebundenen technischen Finalisierungsvertrag.

Der kleinste naechste Entwicklungsschritt ist ein eng begrenzter statischer
Korrekturvorschlag fuer die zwei bereits gebundenen Dateien. Er muss die
Finalisierungsfrist fuer jeden bestaetigten Endzustand mit gesperrter
Ergebnisannahme eindeutig festlegen, unabhaengige Finalisierungsschritte trotz
Einzelfehlern fortsetzen, verbleibende Fristen vor und nach jedem Schritt
pruefen und die zugehoerigen Kontrollfluesse strukturell testen. Vor einer
Codekorrektur ist dieser Vorschlag erneut getrennt freizugeben.
