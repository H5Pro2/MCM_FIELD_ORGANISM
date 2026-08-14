# 228 - Getrennte Entscheidung zur Korrekturimplementierung des Bindungs-Preflight-Supervisors

## 1. Forschungsfrage und Auftrag

Soll auf Grundlage des positiv statisch geprueften Dokuments 225 eine spaetere
Korrekturimplementierung in den zwei bereits gebundenen Dateien vorgeschlagen
werden, ohne sie in diesem Schritt auszufuehren?

Dieses Dokument trifft ausschliesslich die getrennte Implementierungsentscheidung.
Es implementiert, importiert, testet oder startet nichts und ist kein
Forschungs-, Test- oder Programmlauf.

## 2. Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/224_UNABHAENGIGE_STATISCHE_IMPLEMENTIERUNGSPRUEFUNG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/225_STATISCHER_KORREKTURVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/226_UNABHAENGIGE_STATISCHE_PRUEFUNG_KORREKTURVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/227_ERNEUTE_UNABHAENGIGE_STATISCHE_PRUEFUNG_KORREKTURVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- aktueller Freigabe-Eingang des Forschungshelfers

Keine externe Quelle wurde verwendet.

## 3. Betroffene Dateien und Schnittstellen

Die vorgeschlagene spaetere Korrekturimplementierung ist exakt auf diese
beiden vorhandenen Dateien begrenzt:

- `tools/binding_preflight_supervisor.py`
- `tests/test_binding_preflight_supervisor_structure.py`

Weitere Projekt-, Runner-, Aufruf-, Runtime-, ABI-, Ergebnis- oder
Dokumentationsdateien sind nicht Teil der Implementierungsentscheidung.

## 4. Inhalt der Entscheidung

Es wird entschieden, dem Forschungshelfer die spaetere Korrekturimplementierung
der beiden benannten Dateien zur ausdruecklichen Freigabe vorzuschlagen. Eine
solche Implementierung darf ausschliesslich die in Dokument 225 gebundenen
Korrekturen abbilden:

1. Workspace-Nachmanifest und Vergleich nach jedem bestaetigten Prozessende
   oder bestaetigten Abbruch, mit ausdruecklicher Nichtentscheidbarkeit bei
   nicht bestaetigtem Endzustand.
2. 60-Sekunden-Erfolgsfrist und davon getrennte, rein technische
   5-Sekunden-Finalisierungsfrist.
3. Eng bewachter einmaliger `TerminateProcess`-Pfad vor erfolgreicher
   Job-Zuweisung mit exakt `PRE_JOB_ABORT_EXIT_CODE = 1`; danach
   ausschliesslich `TerminateJobObject`.
4. Fest gebundene Betriebssystem-Thread- und Handlebeobachtung mit den in
   Dokument 225 benannten APIs, `THREADENTRY32`, Fehlerregeln,
   Snapshot-Eigentum und unveraenderlicher interner Dreiphasenstruktur.
5. Fail-closed Ablehnung doppelter JSON-Schluessel vor Dictionary-Bildung.
6. Ausschliesslich statische Quelltext- und AST-Testabdeckung fuer diese
   Korrekturen sowie fuer die gebundenen gesperrten Artefaktklassen.

Alle bereits bestaetigten Vertragsanteile aus Dokument 224 bleiben
unveraendert. Die Korrektur darf keine neue Aufrufstelle, keinen automatischen
Einstiegspunkt, keinen Projektimport, keinen alternativen Prozessstarter und
keine wissenschaftliche Auswertung hinzufuegen.

## 5. Verbindliche Phasentrennung

Diese Entscheidung ist keine Implementierungsfreigabe. Die Reihenfolge bleibt:

1. vorliegende getrennte Implementierungsentscheidung,
2. unabhaengige statische Pruefung dieser Entscheidung,
3. ausdrueckliche Freigabe der Korrekturimplementierung,
4. Korrektur ausschliesslich der zwei benannten Dateien,
5. erneute unabhaengige statische Implementierungspruefung.

Testausfuehrung, Projektimport, Prozessstart, stdin-Transport,
Runtime-/ABI-Fixierung und Preflight-Ausfuehrung benoetigen weiterhin eigene
spaetere Entscheidungen. Keine dieser Phasen wird durch dieses Dokument
freigegeben oder vorweggenommen.

## 6. Durchgefuehrte Schritte, Messergebnisse und Gegenbaselines

Durchgefuehrt wurden nur das Lesen der aktuellen Projektregeln, der Dokumente
224 bis 227 und des aktuellen Uebergabe-Eingangs sowie die statische
Formulierung dieser Entscheidung. Supervisor- und Testdatei wurden nicht
geaendert.

Es wurden keine Tests, Projektimporte, Python-Parser, Prozesse,
stdin-Transporte oder Preflights ausgefuehrt. Es gibt keine Laufmessung und
keine experimentelle Gegenbaseline. Der statische Gegenabgleich bestand
ausschliesslich in der Begrenzung jedes spaeteren Korrekturpunkts auf Dokument
225 und die dort geschlossenen Befunde.

## 7. Grenzen, Nichtnachweis und offene Annahmen

- Die Entscheidung weist keine korrekte Implementierung nach.
- Windows-ABI, Runtime und API-Wirksamkeit wurden nicht geprueft.
- Kontrollfluss, Terminierung, EOF-, Handle- und Workspace-Verhalten wurden
  nicht ausgefuehrt.
- Die statischen Tests wurden nicht geaendert oder ausgefuehrt.
- Die fail-closed externe Aktivitaetsgrenze bleibt unveraendert und begruendet
  keinen ausfuehrbaren Preflightpfad.
- Es liegt kein technischer Erfolg, Preflight-Ergebnis oder wissenschaftlicher
  Befund vor.
- Memory, Organisation, Topologie, Bedeutung, Selbstregulation und KI sind
  nicht nachgewiesen.

## 8. Schlussfolgerung und naechster Schritt

Die spaetere Korrekturimplementierung der zwei benannten Dateien wird als
kleinster begrenzter Entwicklungsschritt zur Freigabe vorgeschlagen. Die
Entscheidung bleibt vollstaendig von Implementierung und Ausfuehrung getrennt
und verschiebt weder Projektziel noch Aussagegrenze.

Der naechste zulaessige Schritt ist ausschliesslich die unabhaengige statische
Pruefung dieses Entscheidungsdokuments. Erst nach positivem Pruefergebnis und
einer anschliessenden ausdruecklichen Implementierungsfreigabe duerfen die
beiden Dateien korrigiert werden.

Keine Zielabweichung vom aktuellen Projektziel wurde festgestellt.
