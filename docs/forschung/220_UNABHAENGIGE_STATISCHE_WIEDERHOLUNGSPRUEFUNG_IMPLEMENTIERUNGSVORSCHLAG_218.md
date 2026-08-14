# 220 - Unabhaengige statische Wiederholungspruefung des Implementierungsvorschlags 218

## 1. Forschungsfrage und Auftrag

Bildet die korrigierte Fassung von Dokument 218 den in Dokument 217
vorregistrierten Vertrag vollstaendig und widerspruchsfrei ab, schliesst sie
alle zehn Befunde aus Dokument 219 und wahrt sie die Trennung zwischen
Vorschlag, Implementierungsentscheidung, statischer Implementierungspruefung
und einem moeglichen separat freizugebenden einmaligen Prozessstart?

Freigegeben und durchgefuehrt wurde ausschliesslich dieser statische
Dokumentenabgleich. Dieses Dokument ist kein Forschungslauf.

## 2. Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/217_VORREGISTRIERUNG_EINMAL_AUSFUEHRUNGSAUFTRAG_BINDUNGS_PREFLIGHT.md`
- `docs/forschung/218_STATISCHER_IMPLEMENTIERUNGSVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/219_UNABHAENGIGE_STATISCHE_PRUEFUNG_IMPLEMENTIERUNGSVORSCHLAG_218.md`
- aktueller Freigabe-Eingang des Forschungshelfers

Keine externe Quelle wurde verwendet.

## 3. Verwendete Dateien und Schnittstellen

Die genannten Markdown-Dateien wurden ausschliesslich statisch gelesen und
inhaltlich verglichen. Es wurden keine Projekt- oder Supervisormodule
importiert, keine Tests ausgefuehrt und keine Prozess-, stdin-, Python-, Job-,
Runtime- oder Preflight-Schnittstelle aufgerufen.

## 4. Durchgefuehrte Schritte

1. Die aktuellen Projektleitdokumente gelesen.
2. Alle zehn Befunde aus Dokument 219 einzeln gegen die korrigierte Fassung
   von Dokument 218 abgeglichen.
3. Dokument 218 zusaetzlich vollstaendig gegen den Vertrag aus Dokument 217
   auf fortbestehende oder neu sichtbare Widersprueche geprueft.
4. Ausfuehrungssperren und die Trennung der vier Freigabephasen kontrolliert.

## 5. Statisches Pruefergebnis

### 5.1 Geschlossene Befunde aus Dokument 219

Die korrigierte Fassung von Dokument 218 schliesst alle zehn dort benannten
Vertragsluecken textuell:

1. Arbeitsordner, `lpApplicationName` und der veraenderbare
   `lpCommandLine`-Puffer sind absolut und exakt gebunden.
2. Alle vier Erzeugungsflags, `bInheritHandles=TRUE` und
   `STARTF_USESTDHANDLES` mit denselben drei Childhandles sind enthalten.
3. Bytezahl, Digest, ASCII/UTF-8, BOM-Freiheit, LF-Bindung, Schluss-LF und das
   Verbot einer Ersatzbindung oder Normalisierung sind enthalten.
4. `JOB_OBJECT_LIMIT_PROCESS_TIME` und die vier weiteren Job-Limit-Flags samt
   Werten und Rueckpruefung sind enthalten.
5. Die Wandzeit beginnt mit erfolgreichem `CreateProcessW` und umfasst die
   suspendierte Vorbereitungsphase.
6. Exitcode 0, Kindprozesse 0, eindeutiger Exit sowie die rein beobachtende
   Thread- und Handleerfassung sind enthalten.
7. Die einzelne ASCII-JSON-Zeile, Schluss-LF, exakt fuenf Schluessel, vier
   feste Booleanwerte und 64 kleingeschriebene Hexzeichen sind gebunden.
8. Schreibzeitpunkte, Verzeichnisaenderungen und alle geforderten sperrenden
   Artefaktklassen sind enthalten.
9. Die externen Seiteneffektgrenzen und der technische Abbruch bei fehlender
   Entscheidbarkeit sind enthalten.
10. Der vollstaendige Abbruch-, Einmaligkeits- und Nachlaufvertrag ist
    enthalten.

Die vier Freigabephasen bleiben getrennt. Dokument 218 gibt weder
Implementierung noch Prozessstart implizit frei.

### 5.2 Verbleibender Vertragswiderspruch

Dokument 218, Abschnitt 5.8, stellt in Aussicht, bereits vorhandene,
laufzeitbedingt veraenderliche Pfade vor einer Ausfuehrung gegebenenfalls
vertraglich aus dem Workspace-Vergleich auszuschliessen. Dokument 217 sieht
als einzigen Ausschluss den unveraenderten `.git`-Bestand vor. Es verlangt
denselben Vergleichsumfang vor und nach dem Prozess und sperrt das Ergebnis bei
neu angelegten, geloeschten oder veraenderten Dateien und Verzeichnissen.

Die in 218 offengehaltene spaetere Ausschlussliste ist deshalb keine exakte
Abbildung von 217. Sie eroeffnet eine nachtraegliche Vertragsaenderung, obwohl
218 den Vertrag laut eigenem Auftrag weder erweitern noch ersetzen darf.

Kleinste erforderliche Korrektur: In Abschnitt 5.8 von Dokument 218 den Absatz
ueber moegliche spaetere Pfadausschluesse entfernen und ausdruecklich binden,
dass ausser dem unveraenderten `.git`-Bestand keine Ausschlussliste und keine
Ausnahme vom Vorher-/Nachher-Vergleich zulaessig ist. Sollte der festgelegte
Vergleichsumfang nicht stabil entscheidbar sein, muss dies gemaess Dokument
217 als technischer Abbruch behandelt werden.

## 6. Messergebnisse und Gegenbaseline

Es wurde kein Prozess und kein Preflight ausgefuehrt. Es gibt keine
Laufmessung und keine experimentelle Gegenbaseline. Die statische
Vertragsgegenbaseline war Dokument 217; Dokument 219 lieferte die zehn erneut
zu pruefenden Befundgruppen.

Beobachtetes statisches Ergebnis: Alle zehn Befunde aus Dokument 219 sind
geschlossen, aber die zusaetzliche Ausschlussmoeglichkeit in Abschnitt 5.8
verhindert weiterhin eine vollstaendige widerspruchsfreie Vertragsabbildung.

## 7. Grenzen und nicht gepruefte Annahmen

- Geprueft wurde nur die textuelle Vertragsabbildung.
- Windows-ABI, `ctypes`-Definitionen und Runtime-Identitaet wurden nicht
  geprueft oder fixiert.
- Supervisorimplementierung und statische Implementierungstests existieren
  weiterhin nicht und waren nicht Gegenstand dieses Auftrags.
- Runtimeverhalten, Ressourcenwirksamkeit, Deadlockfreiheit und reale
  Seiteneffektfreiheit sind nicht nachgewiesen.
- Es liegt kein technischer Erfolg, Preflight-Ergebnis oder wissenschaftlicher
  Befund vor.

## 8. Schlussfolgerung und naechster Schritt

Die korrigierte Fassung von Dokument 218 besteht die statische
Wiederholungspruefung noch nicht vollstaendig. Die zehn Befunde aus Dokument
219 sind geschlossen, doch die moegliche spaetere Workspace-Ausschlussliste
widerspricht dem unveraenderten Vertrag aus Dokument 217.

Der kleinste naechste Schritt ist ausschliesslich die genannte statische
Korrektur in Abschnitt 5.8 von Dokument 218. Danach ist erneut nur eine
unabhaengige statische Pruefung zulaessig. Implementierung, Tests,
Projektimporte, Prozessstart, stdin-Transport, Python-Parsing,
Runtime-Fixierung, Preflight-Ausfuehrung und wissenschaftliche Interpretation
bleiben gesperrt.

Es wurde keine Zielabweichung vom aktuellen Projektziel festgestellt.
