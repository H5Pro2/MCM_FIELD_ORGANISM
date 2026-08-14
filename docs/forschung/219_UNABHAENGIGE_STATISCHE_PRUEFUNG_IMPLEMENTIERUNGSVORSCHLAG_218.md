# 219 - Unabhaengige statische Pruefung des Implementierungsvorschlags 218

## 1. Einordnung und Auftrag

Dieses Dokument ist ausschliesslich eine unabhaengige statische Pruefung von
Dokument 218 gegen den vorregistrierten Vertrag aus Dokument 217. Es ist kein
Forschungslauf, keine Implementierungsfreigabe und keine Ausfuehrungsfreigabe.

Geprueft wird, ob Dokument 218 den Vertrag aus Dokument 217 vollstaendig und
widerspruchsfrei abbildet, keine implizite Ausfuehrung freigibt und die vier
Phasen Vorschlag, Implementierungsentscheidung, statische
Implementierungspruefung und moeglicher einmaliger Prozessstart getrennt
haelt.

## 2. Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/217_VORREGISTRIERUNG_EINMAL_AUSFUEHRUNGSAUFTRAG_BINDUNGS_PREFLIGHT.md`
- `docs/forschung/218_STATISCHER_IMPLEMENTIERUNGSVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- aktueller Freigabe-Eingang des Forschungshelfers

Keine externe Quelle wurde verwendet.

## 3. Verwendete Dateien und Schnittstellen

Die genannten Markdown-Dateien wurden ausschliesslich statisch gelesen und
inhaltlich gegeneinander abgeglichen. Es wurden keine Supervisor- oder
Projektmodule importiert, keine Tests ausgefuehrt, keine Nutzlast geparst und
keine Prozess-, stdin-, Job- oder Runtime-Schnittstelle aufgerufen.

## 4. Pruefergebnis

Dokument 218 bildet wesentliche Teile von Dokument 217 korrekt ab, ist aber
nicht vollstaendig und an einer Stelle widerspruechlich zum vorregistrierten
Zeitvertrag. Eine spaetere Implementierungsentscheidung kann auf dieser
Fassung noch nicht eindeutig gegen Dokument 217 geprueft werden.

### 4.1 Korrekt und widerspruchsfrei abgebildete Punkte

- Die vier Freigabephasen sind ausdruecklich getrennt.
- Es gibt keinen automatischen Einstiegspunkt und keine implizite
  Ausfuehrungsfreigabe.
- `CreateProcessW`, suspendierter Start, `STARTUPINFOEXW`, die Allowlist aus
  genau drei Childhandles und nicht vererbbare Supervisor-Gegenhandles sind
  vorgesehen.
- Die drei supervisorseitigen Childhandle-Kopien werden nach Jobzuordnung und
  Rueckpruefung, vor stdin und vor `ResumeThread`, jeweils genau einmal
  geschlossen; Schliessfehler fuehren fail-closed zur Jobterminierung.
- stdin ist auf einen einzigen 1806-Byte-`WriteFile`-Aufruf ohne Flush, danach
  `CloseHandle` und erst danach genau ein `ResumeThread` begrenzt.
- Zwei vor `ResumeThread` bereite Rohbyte-Leser, stdout-Kapazitaet 4097,
  stderr-Kapazitaet 1, unmittelbare Jobterminierung an der Grenze und EOF-Pflicht
  sind vorgesehen.
- Prozess- und Jobspeicher, aktive Prozesse, CPU-Grenze, Kill-on-close,
  explizites Minimal-Environment und fehlende Wiederholung sind grundsaetzlich
  enthalten.
- Workspace-Vorher-/Nachher-Pruefung und rein interne Ergebnisrueckgabe sind
  vorgesehen.
- Die wissenschaftliche Aussagegrenze bleibt erhalten; es wird kein MCM-Befund
  behauptet.

### 4.2 Erforderliche Korrekturen

1. **Prozessidentitaet ist nicht exakt gebunden.** Abschnitt 5.1 von 218 nennt
   `.venv\\Scripts\\python.exe` relativ. Dokument 217 bindet dagegen
   `lpApplicationName`, Arbeitsordner und den vollstaendigen veraenderbaren
   `lpCommandLine`-Puffer absolut. Die drei exakten Werte muessen in 218
   ausgeschrieben werden; eine spaetere Pfadauflosung ist nicht zugelassen.

2. **Erzeugungsflags sind unvollstaendig.** Die Prozessfolge in 218 nennt
   `CREATE_SUSPENDED` und `EXTENDED_STARTUPINFO_PRESENT`, aber nicht die in 217
   ebenfalls zwingenden Flags `CREATE_NO_WINDOW` und
   `CREATE_UNICODE_ENVIRONMENT`. Alle vier Flags muessen gemeinsam gebunden
   werden, ebenso `bInheritHandles=TRUE` und `STARTF_USESTDHANDLES` mit den drei
   identischen Allowlist-Handles.

3. **Die Nutzlastvorpruefung ist unvollstaendig.** 218 verlangt nur Bytezahl
   und SHA-256. Dokument 217 bindet zusaetzlich ASCII beziehungsweise gueltiges
   UTF-8, fehlenden BOM, ausschliessliche LF-Zeilenenden und ein abschliessendes
   LF. Es verbietet ausserdem Korrektur, Normalisierung und Neuberechnung mit
   anschliessender Akzeptanz. Diese Bedingungen muessen in Vorschlag und
   statischen Pruefkriterien enthalten sein.

4. **Das Job-Limit-Flag fuer CPU-Zeit fehlt.** Abschnitt 5.6 von 218 nennt den
   Zahlenwert, listet aber `JOB_OBJECT_LIMIT_PROCESS_TIME` nicht. Dokument 217
   verlangt dieses Flag ausdruecklich zusammen mit den vier weiteren
   Job-Limit-Flags und deren Rueckpruefung.

5. **Der Beginn der Wandzeit wurde verschoben.** Dokument 217 bindet maximal
   60 Sekunden Wandzeit ab erfolgreichem Prozessstart. Dokument 218 beginnt die
   monotone Messung erst unmittelbar vor `ResumeThread`. Die Suspendierungs-,
   Job-, Handle-, Leser- und stdin-Phase waere dadurch ungebunden. 218 muss den
   Zeitbeginn auf den erfolgreichen `CreateProcessW`-Start legen.

6. **Exit- und Prozessbaumvertrag sind nicht vollstaendig.** Der zulaessige
   Erfolgs-Exitcode `0`, Kindprozesse `0`, kein eindeutiger Exit als Abbruch
   sowie die Beobachtung von Thread- und Handlewerten vor Start, waehrend des
   Wartens und nach Prozessende muessen ausdruecklich aufgenommen werden.

7. **Die Erfolgsannahme ist zu indirekt.** 218 verweist auf das Schema aus 217,
   schreibt aber nicht fest, dass stdout genau eine ASCII-JSON-Zeile mit
   Schluss-LF, exakt den fuenf vorgegebenen Schluesseln, ohne Zusatzschluessel
   und mit den vier festen Booleanwerten sowie einem Digest aus genau 64
   kleingeschriebenen Hexzeichen enthalten muss. Fuer eine statisch
   pruefbare Implementierung muessen diese Bedingungen im Vorschlag selbst
   vollstaendig gebunden sein.

8. **Das Workspace-Manifest ist unvollstaendig.** 218 nennt Pfad, Dateityp,
   Groesse und SHA-256, laesst aber die in 217 mindestens geforderten
   Schreibzeitpunkte sowie die explizite Erkennung neu angelegter, geloeschter
   oder veraenderter Verzeichnisse aus. Auch `__pycache__`, Bytecode sowie
   Cache-, Temp-, Log-, Dump-, Datenbank-, Zustands- und Memory-Artefakte
   muessen als sperrende Klassen ausdruecklich abgebildet werden.

9. **Externe Seiteneffektgrenzen fehlen.** Dokument 217 verbietet Netzwerk-,
   Geraete-, Kamera-, Mikrofon-, Anzeige-, Zwischenablage-, Dienst- und sonstige
   externe Aktivitaet und wertet eine nicht verlaesslich entscheidbare
   Seiteneffektpruefung als technischen Abbruch. Dokument 218 bildet diese
   Grenze nicht ab.

10. **Der vollstaendige Abbruch- und Nachlaufvertrag fehlt.** 218 muss
    ausdruecklich festhalten, dass nach jeder Verletzung und auch nach einem
    akzeptierten technischen Erfolg weder zweiter Versuch noch Runtime-
    Aktivierung oder Runner-, Integrator-, Executor- beziehungsweise
    Hook-Aufruf folgen darf. Ein Erfolg darf keine Wiederholung oder
    nachgelagerte Ausfuehrung freigeben.

## 5. Durchgefuehrte Schritte

1. Die aktuellen Projektleitdokumente gelesen.
2. Prozessidentitaet und Erzeugungsflags aus 217 gegen 218 abgeglichen.
3. Handle-Allowlist, Handle-Schliessungen, stdin-Reihenfolge und Fehlerabbruch
   verglichen.
4. Job-, Zeit-, Prozess-, Ausgabe- und EOF-Grenzen verglichen.
5. Environment-, Erfolgs-, Workspace- und externe Seiteneffektbedingungen
   verglichen.
6. Einmaligkeits- und Nachlaufsperren verglichen.
7. Die Trennung der vier Freigabephasen geprueft.

## 6. Messergebnisse und Gegenbaseline

Es wurde kein Prozess und kein Preflight ausgefuehrt. Es gibt keine
Laufmessung und keine experimentelle Gegenbaseline.

Die statische Vertragsgegenbaseline war Dokument 217. Ergebnis des
Punktabgleichs:

- korrekt abgebildete Kerngruppen: Handle-Reihenfolge, einmaliger
  stdin-Transport, parallele Rohbyte-Leser, grundlegende Jobgrenzen,
  Minimal-Environment, Phasentrennung und wissenschaftliche Sperre;
- korrekturbeduerftige Vertragsgruppen: exakte Prozessidentitaet,
  Erzeugungsflags, Nutzlastmerkmale, CPU-Limit-Flag, Wandzeitbeginn,
  Exit/Prozessbaum/Beobachtung, exaktes Erfolgsschema, Workspace-Mindestumfang,
  externe Seiteneffekte und vollstaendiger Nachlaufvertrag.

## 7. Grenzen und nicht gepruefte Annahmen

- Es wurde nur die textuelle Vertragsabbildung geprueft.
- Windows-ABI, `ctypes`-Strukturen und Funktionssignaturen wurden nicht gegen
  externe Primaerquellen geprueft.
- Es existiert weiterhin keine Supervisorimplementierung und kein statischer
  Implementierungstest.
- Runtimeverhalten, Deadlockfreiheit, Ressourcenwirksamkeit und
  Seiteneffektfreiheit sind nicht nachgewiesen.
- Es liegt kein technischer Erfolg, kein Preflight-Ergebnis und kein
  wissenschaftlicher Befund vor.

## 8. Schlussfolgerung und naechster Schritt

Dokument 218 besteht die unabhaengige statische Pruefung noch nicht. Es gibt
keine implizite Ausfuehrungsfreigabe, und die vier Phasen sind korrekt
getrennt. Die zehn benannten Luecken verhindern jedoch die behauptete exakte
und vollstaendige Abbildung von Dokument 217.

Der kleinste naechste Schritt ist ausschliesslich eine statische Korrektur von
Dokument 218 entlang der zehn Punkte. Implementierung, Tests, Prozessstart,
stdin-Transport, Parsing, Projektimporte, Runtime-Fixierung, Preflight und
wissenschaftliche Interpretation bleiben gesperrt. Nach der Korrektur ist
erneut eine unabhaengige statische Pruefung erforderlich.

Keine Zielabweichung vom aktuellen Projektziel wurde festgestellt.
