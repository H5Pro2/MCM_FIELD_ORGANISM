# 224 - Unabhaengige statische Implementierungspruefung des Bindungs-Preflight-Supervisors

## 1. Forschungsfrage und Auftrag

Bilden `tools/binding_preflight_supervisor.py` und
`tests/test_binding_preflight_supervisor_structure.py` Dokument 218, die
Nutzlastbindung aus Dokument 215 und die zuvor gebundenen Vertragsgrenzen
vollstaendig und widerspruchsfrei ab?

Freigegeben und durchgefuehrt wurde ausschliesslich diese statische
Implementierungspruefung. Sie ist kein Forschungs- oder Programmlauf.

## 2. Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/215_BINDUNGS_PREFLIGHT_STDIN_NUTZLAST.txt`
- `docs/forschung/217_VORREGISTRIERUNG_EINMAL_AUSFUEHRUNGSAUFTRAG_BINDUNGS_PREFLIGHT.md`
- `docs/forschung/218_STATISCHER_IMPLEMENTIERUNGSVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `tools/binding_preflight_supervisor.py`
- `tests/test_binding_preflight_supervisor_structure.py`
- aktueller Freigabe-Eingang des Forschungshelfers

Keine externe Quelle wurde verwendet.

## 3. Verwendete Dateien und Schnittstellen

Die genannten Dateien wurden ausschliesslich als Text gelesen und statisch
verglichen. Fuer Dokument 215 wurden Byteumfang und SHA-256 mit rein lesenden
Dateisystemwerkzeugen abgeglichen. Es wurden keine Tests, Projektimporte,
Python-Parser, Prozessstarts, stdin-Transporte, Runtime-Fixierungen oder
Preflight-Schnittstellen ausgefuehrt.

## 4. Durchgefuehrte Schritte

1. Die aktuellen Projektleitdokumente gelesen.
2. Konstanten und Nutzlastidentitaet gegen Dokumente 215, 217 und 218
   abgeglichen.
3. Prozessreihenfolge, Job-, Handle-, Stream-, Zeit- und Fehlerpfade statisch
   verfolgt.
4. Workspace-Vorher-/Nachher-Pruefung und Ergebnisvalidierung gegen den
   gebundenen Vertrag abgeglichen.
5. Die statischen Strukturtests auf Abdeckung der vorgeschriebenen
   Vertragsmerkmale geprueft.

## 5. Statische Befunde

### 5.1 Kritisch - Workspace-Nachmanifest fehlt auf Abbruchpfaden

Das Vorzustandsmanifest wird in `execute_once()` vor dem Prozessaufbau
gebildet. Das Nachmanifest wird jedoch nur im Erfolgspfad nach
Ergebnisvalidierung aufgenommen. Jeder Fehler nach einem Prozessstart springt
direkt in `except` und `finally`, ohne dass derselbe Workspace-Umfang erneut
aufgenommen und verglichen wird.

Dokumente 217 und 218 verlangen das Nachmanifest unmittelbar nach Prozessende
oder Abbruch. Damit koennen gerade bei einem technischen Abbruch erzeugte oder
veraenderte Artefakte unentdeckt bleiben.

### 5.2 Hoch - Wandzeitvertrag endet vor vollstaendiger EOF-Pruefung

Die monotone Zeitmarke wird vor dem `CreateProcessW`-Aufruf gesetzt, nicht mit
dessen erfolgreichem Abschluss. Nach dem Prozess-Wait duerfen die beiden
Reader ausserdem jeweils weitere fuenf Sekunden auf EOF warten. Diese
Join-Zeiten werden nicht gegen die verbleibende 60-Sekunden-Grenze gerechnet.

Dokument 218 bindet die Wandzeit an den erfolgreichen Prozessstart und umfasst
Suspendierungs-, Job-, Handle-, Leser-, stdin-, Prozessende- und EOF-Phase.
Die Implementierung bildet diese Grenze daher weder am exakten Startpunkt noch
bis zum exakten Endpunkt ab.

### 5.3 Hoch - Thread- und Handle-Beobachtungen fehlen

Dokumente 217 und 218 verlangen Beobachtungen der Thread- und Handlewerte vor
Start, waehrend des Wartens und nach Prozessende. Die Implementierung enthaelt
weder entsprechende Abfragen noch interne Beobachtungswerte. Die vorhandene
Handle-Eigentumsverwaltung ersetzt diese Betriebssystembeobachtungen nicht.

### 5.4 Hoch - Nicht gebundener Ersatzabbruch ueber TerminateProcess

Bei fehlgeschlagener Job-Zuweisung ruft die Implementierung
`TerminateProcess` auf. Dokumente 217 und 218 binden den Fehlerabbruch an die
Terminierung des Job Objects und nennen `TerminateProcess` weder als
zulaessigen Ersatz noch als Vertragsbestandteil.

Der Ersatzpfad adressiert zwar das reale Problem eines noch nicht dem Job
zugewiesenen suspendierten Prozesses, erweitert aber den vorregistrierten
Vertrag. Vor einer Korrektur muss der statische Vertrag diesen Fall explizit
und widerspruchsfrei binden; die Implementierung darf ihn nicht eigenstaendig
ergaenzen.

### 5.5 Mittel - Doppelte JSON-Schluessel werden akzeptiert

Die Ergebnisvalidierung verwendet `json.loads` mit dem normalen
Dictionary-Aufbau. Doppelte Schluessel werden dadurch auf den letzten Wert
reduziert. Eine Ausgabe mit mehrfach vorkommendem gebundenem Schluessel kann
somit nach dem Parsen dieselbe Schluesselmenge und dieselben Werte besitzen.

Der Vertrag erlaubt exakt die fuenf benannten Schluessel und keine
zusaetzlichen Inhalte. Die Implementierung muss doppelte Vorkommen daher
fail-closed erkennen.

### 5.6 Hoch - Statische Tests sichern die Abweichungen nicht ab

Die Testdatei prueft die Zeitmarke nur als vorhandenen Text, aber weder ihre
Position relativ zum erfolgreichen `CreateProcessW` noch die Einbeziehung der
EOF-Phase. Sie prueft kein Nachmanifest auf allen Abbruchpfaden, keine
Thread-/Handle-Beobachtungen und keine Ablehnung doppelter JSON-Schluessel.

Zudem fordert `test_workspace_manifest_has_no_dynamic_exclusions_or_writes`,
dass `__pycache__` im Supervisorquelltext nicht vorkommt. Dokument 218 fordert
dagegen statische Abdeckung der gesperrten Artefaktklassen einschliesslich
`__pycache__`, Bytecode, Cache-, Temp-, Log-, Dump-, Datenbank-, Zustands- und
Memory-Artefakten. Der Test bildet diese Vorgabe damit nicht ab.

## 6. Bestaetigte statische Vertragsanteile

- Dokument 215 besitzt den gebundenen Byteumfang 1806 und den gebundenen
  SHA-256-Wert.
- Die Implementierung enthaelt keinen automatischen Einstiegspunkt, keinen
  Projektimport, kein `subprocess` und keinen Shell-Aufruf.
- Die absoluten Prozessdaten, vier Erzeugungsflags, drei Child-Handles,
  Environmenteintraege, Nutzlastgrenzen, fuenf Job-Limit-Flags und
  Ergebnisfelder sind textuell vorhanden.
- Es gibt jeweils genau einen syntaktischen Aufrufpfad fuer `CreateProcessW`,
  `WriteFile` und `ResumeThread`.
- Die Testdatei importiert oder startet den Supervisor nicht; ihre vorgesehene
  Arbeitsweise ist auf Quelltext und AST begrenzt.

Diese bestaetigten Anteile heben die Befunde aus Abschnitt 5 nicht auf.

## 7. Messergebnisse und Gegenbaseline

Es wurde kein Test, Prozess oder Preflight ausgefuehrt. Es gibt keine
Laufmessung und keine experimentelle Gegenbaseline.

Beobachtetes statisches Ergebnis: Die Nutzlastidentitaet und mehrere zentrale
Strukturmerkmale stimmen, die Implementierung bildet den Gesamtvertrag aus
Dokument 218 jedoch nicht vollstaendig ab.

Technische Interpretation: Die Implementierung ist derzeit keine positive
Grundlage fuer eine spaetere Prozessstartentscheidung. Die festgestellten
Abweichungen betreffen insbesondere Abbruchbeobachtung, Zeitgrenze und eine
nicht vorregistrierte Abbruchoperation.

## 8. Grenzen, Nichtnachweis und offene Annahmen

- Windows-ABI, `ctypes`-Strukturgroessen und Funktionssignaturen wurden nicht
  gegen eine externe Primaerquelle fixiert oder zur Laufzeit geprueft.
- Die Dateien wurden nicht durch Python geparst oder importiert.
- Die statischen Tests wurden nicht ausgefuehrt.
- Runtimeverhalten, Deadlockfreiheit, Ressourcenwirksamkeit und reale
  Seiteneffektfreiheit sind nicht nachgewiesen.
- `_verify_external_activity_absence()` sperrt aktuell jeden Aufruf vor dem
  Prozessaufbau. Das ist fail-closed und keine externe Aktivitaetsfreigabe,
  bedeutet aber zugleich, dass kein ausfuehrbarer Preflightpfad vorliegt.
- Es liegt kein technischer Erfolg, Preflight-Ergebnis oder wissenschaftlicher
  Befund vor.
- Memory, Organisation, Topologie, Bedeutung, Selbstregulation und KI sind
  nicht nachgewiesen.

## 9. Schlussfolgerung und naechster Schritt

Die Implementierung besteht die unabhaengige statische Implementierungspruefung
nicht. Vor jeder weiteren Pruefung muessen mindestens alle Befunde aus
Abschnitt 5 geschlossen werden. Eine Ausfuehrung bleibt gesperrt.

Der kleinste naechste Entwicklungsschritt ist ein eng begrenzter
Korrekturvorschlag, der zuerst den Widerspruch beim Abbruch vor erfolgreicher
Job-Zuweisung vertraglich klaert und danach Nachmanifest, durchgehende
Wandzeitgrenze, Thread-/Handle-Beobachtungen, eindeutige JSON-Schluessel und
die zugehoerigen statischen Tests bindet. Erst nach separater Freigabe darf
Code korrigiert werden; anschliessend ist erneut ausschliesslich eine statische
Implementierungspruefung zulaessig.

Es wurde keine Zielabweichung vom aktuellen Projektziel festgestellt.
