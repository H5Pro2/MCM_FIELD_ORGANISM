# 227 - Erneute unabhaengige statische Pruefung des Korrekturvorschlags zum Bindungs-Preflight-Supervisor

## 1. Forschungsfrage und Auftrag

Schliesst die korrigierte Fassung von Dokument 225 die drei Befunde aus
Dokument 226 eindeutig und statisch pruefbar, ohne Implementierung oder
Ausfuehrung freizugeben?

Freigegeben und durchgefuehrt wurde ausschliesslich die erneute unabhaengige
statische Pruefung von Dokument 225. Sie ist kein Forschungs-, Test- oder
Programmlauf.

## 2. Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/217_VORREGISTRIERUNG_EINMAL_AUSFUEHRUNGSAUFTRAG_BINDUNGS_PREFLIGHT.md`
- `docs/forschung/218_STATISCHER_IMPLEMENTIERUNGSVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/224_UNABHAENGIGE_STATISCHE_IMPLEMENTIERUNGSPRUEFUNG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/225_STATISCHER_KORREKTURVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/226_UNABHAENGIGE_STATISCHE_PRUEFUNG_KORREKTURVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- aktueller Freigabe-Eingang des Forschungshelfers

Keine externe Quelle wurde verwendet.

## 3. Verwendete Dateien und Schnittstellen

Die genannten Dokumente wurden ausschliesslich als Text gelesen und statisch
verglichen. Supervisor- und Testdatei wurden nicht geaendert, importiert,
geparst oder ausgefuehrt. Prozess-, stdin-, Runtime- und
Preflight-Schnittstellen wurden nicht verwendet.

## 4. Durchgefuehrte Schritte

1. Aktuelle Projektregeln und Ausfuehrungsgrenzen gelesen.
2. Den numerischen Vor-Job-Abbruchcode und seinen Zustandswaechter geprueft.
3. Erfolgsfrist, technische Finalisierungsfrist, Terminierungsbestaetigung,
   Reader-Abschluss und Nachmanifest statisch in ihrer Reihenfolge verfolgt.
4. Beobachtungs-APIs, `THREADENTRY32`, Fehlercodebehandlung,
   Snapshot-Handle-Eigentum und interne Dreiphasenstruktur abgeglichen.
5. Die zugehoerigen statischen Testsollmerkmale und die unveraenderten
   Projektgrenzen geprueft.

## 5. Statische Pruefergebnisse

### 5.1 Abbruchcode und Vor-Job-Zustand geschlossen

`PRE_JOB_ABORT_EXIT_CODE = 1` ist numerisch eindeutig gebunden.
`TerminateProcess` bleibt auf den Zustand nach erfolgreichem
`CreateProcessW`, vor erfolgreicher Job-Zuweisung, vor stdin und vor jedem
`ResumeThread` begrenzt. Nach erfolgreicher Job-Zuweisung bleibt
`TerminateJobObject` der einzige gebundene Terminierungsweg. Ein Retry,
zweiter Start oder alternativer Abbruchpfad wird nicht freigegeben.

### 5.2 Erfolgs- und Finalisierungsfristen geschlossen

Die 60-Sekunden-Erfolgsfrist beginnt unmittelbar nach erfolgreichem
`CreateProcessW` und umfasst den regulaeren Prozess- und EOF-Abschluss. Nach
Grenzverletzung oder Fristablauf ist die Ergebnisannahme unwiderruflich
gesperrt. Die danach einmalig gebildete technische Finalisierungsfrist von
fuenf Sekunden darf nur Terminierungsbestaetigung, Reader-Abschluss,
Handle-Schliessung, Nachbeobachtung und Nachmanifest dienen.

Ein nicht bestaetigtes Prozessende wird ausdruecklich als technisch
unentscheidbar behandelt. In diesem Zustand wird kein Nachmanifest als
stabiler Nachzustand und keine Seiteneffektfreiheit behauptet. Das steht nicht
im Widerspruch zur Nachmanifestpflicht nach bestaetigtem Prozessende oder
bestaetigtem Abbruch, weil gerade kein bestaetigter Endzustand vorliegt.

### 5.3 Beobachtungsmechanismus und Dokumentation geschlossen

Die Schnittstelle ist auf `GetCurrentProcessId`, `GetCurrentProcess`,
`GetProcessHandleCount`, `CreateToolhelp32Snapshot`, `Thread32First`,
`Thread32Next` und `CloseHandle` begrenzt. Snapshot-Flag,
`THREADENTRY32`-Felder, Besitzerfilter, normales Iterationsende und
`use_last_error` sind festgelegt.

Das Snapshot-Handle besitzt genau einen Supervisorbesitzer und wird vor der
Handlezahlabfrage geschlossen; das Prozess-Pseudohandle wird nicht
geschlossen. `TechnicalObservation` und `TechnicalObservations` binden die
drei Phasen unveraenderlich im Speicher. Erfolg verlangt alle drei Werte;
Abbruch bewahrt vorhandene Werte und kennzeichnet fehlende Phasen mit `None`.
Das stdout-Erfolgsschema wird nicht erweitert und es entsteht keine neue
wissenschaftliche Schwelle.

### 5.4 Befunde aus Dokument 224 bleiben abgedeckt

Die gemeinsame Workspace-Finalisierung, fail-closed Erkennung doppelter
JSON-Schluessel und korrigierte statische Abdeckung der gesperrten
Artefaktklassen bleiben erhalten. Die vorgesehenen AST-Pruefungen binden
Reihenfolge und Zustandswaechter statt blosser Namensvorkommen.

## 6. Messergebnisse und Gegenbaseline

Es wurde kein Test, Prozess oder Preflight ausgefuehrt. Es gibt keine
Laufmessung und keine experimentelle Gegenbaseline.

Beobachtetes statisches Ergebnis: Die drei offenen Vertragsstellen aus
Dokument 226 sind in Dokument 225 konkret und untereinander widerspruchsfrei
gebunden.

Technische Interpretation: Dokument 225 ist nun eine hinreichend eindeutige
Grundlage fuer eine getrennt zu entscheidende Korrekturimplementierung in den
zwei bereits benannten Dateien. Dies ist keine Implementierungs- oder
Ausfuehrungsfreigabe.

## 7. Grenzen, Nichtnachweis und offene Annahmen

- Die vertraglich benannten Windows-Signaturen und Strukturen wurden nicht
  gegen eine externe Primaerquelle oder zur Laufzeit geprueft.
- Kontrollfluss, Terminierungswirksamkeit, EOF-, Handle- und
  Workspace-Verhalten sind nicht praktisch nachgewiesen.
- Die statischen Tests wurden weder geaendert noch ausgefuehrt.
- Die fail-closed externe Aktivitaetsgrenze laesst weiterhin keinen
  nachgewiesenen ausfuehrbaren Preflightpfad entstehen.
- Es liegt kein technischer Erfolg, Preflight-Ergebnis oder wissenschaftlicher
  Befund vor.
- Memory, Organisation, Topologie, Bedeutung, Selbstregulation und KI sind
  nicht nachgewiesen.

## 8. Schlussfolgerung und naechster Schritt

Die korrigierte Fassung von Dokument 225 besteht die erneute unabhaengige
statische Pruefung. Die drei Beanstandungen aus Dokument 226 sind geschlossen;
Projektziel, Testwelt- und Aussagegrenzen bleiben unveraendert.

Der kleinste naechste Entwicklungsschritt ist eine getrennte Entscheidung
ueber die Korrekturimplementierung ausschliesslich in
`tools/binding_preflight_supervisor.py` und
`tests/test_binding_preflight_supervisor_structure.py`. Erst nach einer
ausdruecklichen Implementierungsfreigabe duerfen diese Dateien geaendert
werden. Danach ist erneut nur eine unabhaengige statische
Implementierungspruefung zulaessig. Testausfuehrung, Projektimport,
Prozessstart, stdin-Transport und Preflight bleiben gesperrt.

Keine Zielabweichung vom aktuellen Projektziel wurde festgestellt.

