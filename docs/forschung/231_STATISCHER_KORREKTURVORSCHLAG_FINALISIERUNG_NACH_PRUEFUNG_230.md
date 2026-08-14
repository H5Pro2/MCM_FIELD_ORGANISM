# 231 - Statischer Korrekturvorschlag zur Finalisierung nach Pruefung 230

## 1. Forschungsfrage und Auftrag

Welche kleinste, statisch eindeutig pruefbare Korrektur ist erforderlich,
damit die in Dokument 230 festgestellten Finalisierungsmaengel in
`tools/binding_preflight_supervisor.py` und
`tests/test_binding_preflight_supervisor_structure.py` behoben werden?

Freigegeben ist ausschliesslich dieser Korrekturvorschlag. Es werden weder die
Implementierung geaendert noch Tests, Importe, Prozesse, stdin-Transport oder
Preflight ausgefuehrt. Diese Planung ist kein Forschungs- oder Programmlauf.

## 2. Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/230_UNABHAENGIGE_STATISCHE_IMPLEMENTIERUNGSPRUEFUNG_KORREKTUR_225.md`
- `tools/binding_preflight_supervisor.py`
- `tests/test_binding_preflight_supervisor_structure.py`
- aktueller Korrektur-Eingang des Forschungshelfers

Keine externe Quelle wurde verwendet. Der in Dokument 230 offene
Windows-ABI-Abgleich ist nicht Gegenstand dieses Vorschlags und bleibt offen.

## 3. Gebundener Aenderungsumfang

Eine spaetere Implementierung darf ausschliesslich diese zwei Dateien aendern:

1. `tools/binding_preflight_supervisor.py`
2. `tests/test_binding_preflight_supervisor_structure.py`

Alle anderen Dateien und der weitere abweichende Arbeitsbaum bleiben
ungeprueft und nicht freigegeben. Bestehende, in Dokument 230 bestaetigte
Vertragsanteile duerfen nicht abgeschwaecht werden.

## 4. Verbindlicher Korrekturvorschlag

### 4.1 Frische technische Finalisierungsfrist im Fehlerpfad

Sobald `execute_once` nach einem erfolgreich gestarteten Prozess in den
`except`-Pfad eintritt, wird genau einmal eine neue technische Frist gebildet:

```text
finalization_deadline = time.monotonic() + FINALIZATION_SECONDS
```

Diese Frist gilt unabhaengig davon, ob das Prozessende bereits bestaetigt ist.
Insbesondere darf nach einem gescheiterten
`_finish_readers(readers, success_deadline)` nicht auf die Erfolgsfrist
zurueckgegriffen werden. `success_deadline` darf im Finalisierungspfad weder
als Ersatzfrist noch als Fallback auftreten.

Wurde kein Prozess gestartet, wird keine prozessbezogene Finalisierung
behauptet; die bestehende allgemeine Handle-Bereinigung im `finally` bleibt
erhalten.

### 4.2 Terminierung und Endbestaetigung bleiben vorgelagert

Ist der Prozess noch nicht als beendet bestaetigt, bleibt die vorhandene
Trennung verbindlich:

- vor Job-Zuweisung genau ein `TerminateProcess` mit
  `PRE_JOB_ABORT_EXIT_CODE`;
- nach Job-Zuweisung genau ein `TerminateJobObject`;
- anschliessend Prozess-Wait und Exitcode-Abfrage ausschliesslich mit der
  verbleibenden technischen Frist;
- Reader-, Ressourcen-, Beobachtungs- und Manifestfinalisierung nur nach
  bestaetigtem Prozessende.

Eine fehlgeschlagene Terminierung oder unbestaetigtes Prozessende sperrt die
Ergebnisannahme weiterhin. Die allgemeine `finally`-Bereinigung bleibt davon
unberuehrt.

### 4.3 Pflichtschritte werden einzeln fehlertolerant ausgefuehrt

Nach bestaetigtem Prozessende werden die folgenden Schritte in dieser festen
Reihenfolge jeweils in einem eigenen Fehlerfang ausgefuehrt:

1. noch offene Supervisor- und Child-Pipe-Enden schliessen;
2. Reader bis EOF beziehungsweise Fristende abschliessen;
3. Prozess-, Thread- und Job-Ressourcen schliessen;
4. technische Nachbeobachtung aufnehmen;
5. Workspace-Nachmanifest aufnehmen und mit dem Vormanifest vergleichen.

Eine Ausnahme eines Schritts darf keinen spaeteren, innerhalb der Frist noch
moeglichen Schritt ueberspringen. Jeder Fehler wird mit eindeutiger
Schrittbezeichnung in `finalization_errors` erhalten. Der urspruengliche
`primary_error` bleibt Ursache des abschliessenden `TechnicalAbort`; die
gesammelten Finalisierungsfehler ersetzen ihn nicht.

Die Umsetzung darf dafuer einen kleinen lokalen Helfer verwenden, der eine
benannte Aktion mit Fristpruefung und eigenem Fehlerfang ausfuehrt. Der Helfer
darf keine Prozesse starten, keine Ergebnisse akzeptieren und keine Fehler
verschlucken.

### 4.4 Fristbindung jedes Pflichtschritts

Vor und nach jedem der fuenf Schritte wird `time.monotonic()` gegen dieselbe
`finalization_deadline` geprueft. Vor einem blockierbaren Aufruf wird nur die
verbleibende Zeit weitergegeben. Die Reader verwenden weiterhin die absolute
Frist; Prozess-Wait verwendet die daraus gebildeten verbleibenden
Millisekunden.

Ist die Frist vor einem Schritt bereits erschoepft, wird dieser Schritt nicht
als erfolgreich behauptet und ein schrittspezifischer Fristfehler gesammelt.
Die nachfolgenden Schritte werden weiterhin einzeln bewertet, damit kein
Fehlerpfad sie implizit ueberspringt. Die abschliessende `finally`-Bereinigung
darf offene Handles weiterhin bestmoeglich schliessen, gilt aber nicht als
Ersatz fuer Nachbeobachtung oder Nachmanifest.

Ein nach dem Schritt festgestellter Fristueberlauf macht den Schritt fuer die
technische Annahme ungueltig und wird ebenfalls gesammelt. Kein Teilresultat
darf dadurch in ein erfolgreiches `ExecutionResult` gelangen.

### 4.5 Erfolgspfad und Ergebnisgrenze

Der bestehende Erfolgspfad bleibt getrennt. Ein `ExecutionResult` darf nur
zurueckgegeben werden, wenn Erfolgsfrist, Readerabschluss, Exitcode,
stderr-Vertrag, Job-Leerstand, JSON-Vertrag, Ressourcenschliessung,
vollstaendige Beobachtungen und identisches Workspace-Manifest ohne Fehler
bestaetigt sind.

Der technische Finalisierungspfad endet immer mit `TechnicalAbort`. Er darf
weder wissenschaftliche Auswertung freigeben noch einen technischen Erfolg
behaupten.

## 5. Verbindliche statische Testkorrektur

Die Tests duerfen nicht allein auf Stringanzahl oder Textreihenfolge beruhen.
Sie muessen mit dem vorhandenen `ast` mindestens folgende Strukturen pruefen:

1. Im `except`-Handler von `execute_once` wird fuer jeden gestarteten Prozess
   genau eine Zuweisung von `finalization_deadline` aus
   `time.monotonic() + FINALIZATION_SECONDS` erreicht.
2. Im Finalisierungsteil gibt es keinen Bezug auf `success_deadline`.
3. Terminierung und Endbestaetigung sind nur im Zweig `not process_ended`
   enthalten; `TerminateProcess` und `TerminateJobObject` bleiben getrennt.
4. Die fuenf benannten Pflichtschritte sind als getrennte Aktionen in fester
   Reihenfolge vorhanden und nicht in einem gemeinsamen abbrechenden
   `try`-Block verkettet.
5. Jede Aktion besitzt statisch erkennbare Vor- und Nachfristpruefungen sowie
   einen eigenen Weg zum Erhalt eines schrittspezifischen Fehlers.
6. Nachbeobachtung und Nachmanifest bleiben auch nach einem vorangehenden
   Reader- oder Ressourcenschliessfehler als getrennte Aktionen erreichbar.
7. Der Fehlerpfad erzeugt ausschliesslich `TechnicalAbort`; nur der
   vollstaendige Erfolgspfad erzeugt `ExecutionResult`.

Falls ein lokaler Finalisierungshelfer eingefuehrt wird, pruefen die AST-Tests
dessen Funktionskoerper und die geordnete Aufrufliste im `except`-Handler.
Blosse Vorkommenszaehlung des Helfernamens ist nicht ausreichend.

## 6. Gegenbaseline und Entscheidungskriterien

Statische Gegenbaseline ist der in Dokument 230 beanstandete Ist-Zustand:

- Fallback auf `success_deadline` nach bereits bestaetigtem Prozessende;
- ein gemeinsamer abbrechender `try`-Block fuer mehrere Pflichtschritte;
- fehlende Vor- und Nachfristpruefung einzelner Schritte;
- Tests auf Basis von Textvorkommen und Aufrufanzahl.

Eine spaetere Implementierung ist statisch nur dann korrekturfaehig, wenn alle
vier Gegenbaseline-Merkmale entfernt sind und die sieben Testbindungen aus
Abschnitt 5 nachvollziehbar umgesetzt wurden. Teilumsetzung oder neue
Fallback-Fristen gelten als nicht freigabefaehig.

## 7. Grenzen und Nichtnachweis

- Der Vorschlag aendert keinen Code und bestaetigt keine Syntax.
- Windows-ABI und Runtimeverhalten bleiben ungeprueft.
- Terminierung, EOF, Handle-Schliessung, Beobachtung und Manifestvergleich
  sind nicht praktisch nachgewiesen.
- Es wurde keine Messung und keine experimentelle Gegenbaseline ausgefuehrt.
- Es liegt kein technischer Erfolg und kein wissenschaftlicher Befund vor.
- Memory, Organisation, Topologie, Bedeutung, Selbstregulation und KI sind
  nicht nachgewiesen.

## 8. Schlussfolgerung und naechster Schritt

Der Vorschlag bindet die kleinste Korrektur der vier Befundgruppen aus
Dokument 230, ohne den Prozess-, Preflight- oder Forschungspfad freizugeben.
Keine Zielabweichung ist erkennbar.

Der naechste zulaessige Schritt ist ausschliesslich die unabhaengige statische
Pruefung dieses Vorschlags. Erst nach einer getrennten Freigabe darf eine eng
begrenzte Implementierung in den zwei gebundenen Dateien erfolgen. Tests,
Importe, Prozessstart, stdin-Transport und Preflight bleiben bis zu einer
ausdruecklichen spaeteren Freigabe gesperrt.
