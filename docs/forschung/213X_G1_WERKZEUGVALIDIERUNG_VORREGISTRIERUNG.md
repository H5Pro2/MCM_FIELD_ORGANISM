# 213X - G1 Werkzeugvalidierung Vorregistrierung

## Einordnung

213X ist ein rein statisches Vorregistrierungspaket, kein Forschungslauf,
keine Testimplementierung und keine Lauffreigabe. Es legt einen spaeteren,
gesondert freizugebenden Validierungsschritt fuer
`tools/static_binary_evidence.py` fest.

In 213X werden keine Python-Anweisung und kein Test ausgefuehrt. Es werden
keine Fixtures erzeugt. Die Projektsteuerdatei und alle 54 realen
Zielbinaries sind fuer die gesamte hier vorregistrierte Validierung
ausgeschlossen.

## Forschungsfrage und Auftrag

Wie kann die durch 213W statisch abgenommene Werkzeugdatei in einem kleinen,
reproduzierbaren Schritt auf Syntax sowie die korrigierten Zaehler-,
Alignment- und Fehlerkontextpfade geprueft werden, ohne Projektsteuerdatei,
reale CPython-Binary, reale `.pyd`-Dateien, Manifesterzeugung oder Resolver zu
verwenden?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `tools/static_binary_evidence.py`;
- `docs/forschung/213W_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213V.md`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Gebundener Pruefling

Die spaetere Validierung darf nur gegen exakt diese Werkzeugbindung erfolgen:

- Pfad: `tools/static_binary_evidence.py`;
- Groesse: 42.225 Bytes;
- SHA-256:
  `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286`.

Bei jeder Abweichung von Pfad, Groesse oder SHA-256 ist die Validierung vor
dem ersten Python-Aufruf mit `TOOL_BINDING_MISMATCH` abzubrechen. Eine
abweichende Datei darf nicht ersatzweise akzeptiert werden.

## Verwendete Dateien und erlaubte Schnittstellen des spaeteren Schritts

Erlaubt sind spaeter ausschliesslich:

1. die gebundene Werkzeugdatei als Quelltext;
2. genau ein noch zu implementierender Test-Runner unter `tests/`, dessen
   eigene Bytebindung vor seinem Lauf festgehalten werden muss;
3. ein neuer, leerer, laufgebundener Temporaerordner innerhalb des Workspace;
4. der auf der Plattform fest gebundene CPython-3.14.4-Interpreter;
5. Python-Standardbibliothek, insbesondere `ast`, `hashlib`, `json`,
   `pathlib`, `runpy`, `struct`, `tempfile` und `unittest`;
6. Rohbyte-Fixtures, die der Test-Runner deterministisch selbst im
   laufgebundenen Temporaerordner erzeugt.

Nicht erlaubt sind Projektimporte, NumPy, Netzwerk, Browser, Subprozesse aus
dem Test-Runner, dynamische Paketinstallation, DLL-Laden, `ctypes`,
`importlib`, `exec`, `eval`, `pickle`, Shellaufrufe aus Python oder Zugriff auf
andere Projektdateien.

Der Interpreter darf genau einmal fuer die Syntaxpruefung und genau einmal
fuer den Test-Runner gestartet werden. Die konkreten Befehle, Interpreter-
Pfadbindung und Ausgabeziele muessen vor einem spaeteren Lauf im Laufprotokoll
stehen.

## Harte Ausschlussbindung

Der spaetere Test-Runner darf nicht oeffnen, hashen, lesen, kopieren oder
erzeugen:

- eine Projektsteuerdatei fuer `static_binary_evidence.py`;
- die gebundene CPython-Binary `python314.dll`;
- einen der 53 realen `.pyd`-Kandidaten;
- Projektmanifeste oder Resolverausgaben.

Er darf `main()` und `collect()` nicht aufrufen. Dadurch werden weder eine
Steuerdatei noch die Rollenmenge `1 + 53 = 54` fuer den Test benoetigt. Alle
PE-Fixtures muessen neue synthetische Dateien mit reservierten Testnamen und
deterministisch erzeugten Rohbytes sein. Ein Pfadvergleich vor dem Test muss
bestaetigen, dass kein Fixture-Pfad einem realen gebundenen Zielpfad
entspricht. Fehlt die spaetere Liste der ausgeschlossenen Realpfade, ist der
Lauf mit `EXCLUSION_SET_MISSING` abzubrechen.

## Phase A - vorregistrierte Syntaxpruefung

Die Syntaxpruefung darf die gebundene Datei nur als UTF-8-Quelltext lesen und
mit `ast.parse` analysieren. Sie darf das Modul nicht importieren und keinen
Bytecode schreiben. `py_compile`, `compileall` und `__pycache__` sind in
dieser Phase ausgeschlossen.

Pflichtausgabe `syntax_validation.json`:

- `schema`: `mcm-g1-static-binary-syntax-validation-v1`;
- Werkzeugbindung;
- Interpreterbindung und `sys.version`;
- `parse_ok`;
- bei Fehler: Typ, Nachricht, Zeile und Spalte;
- `module_executed: false`;
- `bytecode_generated: false`;
- Start- und Endzeit in UTC.

Akzeptanzkriterium: `parse_ok` ist exakt `true`; andernfalls endet die gesamte
Validierung ohne Fixture-Phase.

## Phase B - synthetische Minimalfixtures

Phase B darf nur nach erfolgreicher Phase A beginnen. Der spaetere Runner darf
die gebundene Werkzeugdatei genau einmal mit `runpy.run_path` unter dem festen
Namen `mcm_g1_static_binary_evidence_fixture_target` laden. Damit gilt
`__name__ != "__main__"`. Direkte Verwendung von `exec`, `eval` oder
`importlib` bleibt verboten. Ein Aufruf von `main()` oder `collect()` bleibt
ebenfalls verboten. Vor und nach dem Laden wird bestaetigt, dass
weder `__pycache__` noch eine andere Datei ausserhalb des laufgebundenen
Temporaer- und Ergebnisordners entstanden ist.

Jeder Fall besitzt eine feste ID, Eingabeparameter, erwartete Ausgabe oder
Fehlerklasse sowie genau eine variierte Bedingung. Nicht aufgefuehrte
Variationen duerfen nicht spontan ergaenzt werden.

### B1 - Zaehlerfixtures

Der Runner konstruiert ausschliesslich In-Memory-Dictionaries in derselben
Form wie `table_result` und `export_results`. Er darf weder PE-Dateien noch
Steuerdaten lesen. Die Zaehlerlogik ist ueber eine testseitige, AST-gebundene
Auswertung der konkreten `counts`-Ausdruecke zu pruefen; die Auswertung darf
kein `eval`, `exec` oder allgemeines Ausdrucksinterpreter-Verhalten enthalten,
sondern nur die vorregistrierten Operationen `len`, feste Indexe, den Slice
`1:4` und Summation der Eintragslaengen abbilden.

Feste Faelle:

| ID | Builtin | Bootstrap | Stdlib | Test | Override | Alias | Native Dateien | Init-Exporte | Erwartete Zaehler |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| C-EMPTY | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | `0,0,0,0,0,0` |
| C-DISJOINT | 2 | 3 | 5 | 7 | 11 | 13 | 2 | 3 | `2,15,11,13,2,3` |
| C-ALIAS-ONLY | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | `0,0,0,4,0,0` |
| C-OVERRIDE-ONLY | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | `0,0,6,0,0,0` |

Die Reihenfolge der erwarteten Zaehler ist: `builtin_entries`,
`frozen_entries`, `frozen_override_entries`, `frozen_alias_entries`,
`native_candidates`, `native_init_exports`.

Akzeptanz: Alle vier Faelle stimmen exakt. Insbesondere darf eine Aenderung
nur der Alias- oder Override-Anzahl `frozen_entries` nicht veraendern.

### B2 - Alignmentfixtures

Der Runner erzeugt je Fall ein minimales PE32+/AMD64-Rohbytebild. DOS-Header,
PE-Signatur, COFF-Header, Optional Header und genau eine Section sind in jedem
Fall identisch, soweit die Tabelle keine Variation vorgibt. Basiswerte des
positiven Fixtures:

- Machine `0x8664`;
- PE32+ Magic `0x20B`;
- ImageBase `0x0000000180000000`;
- FileAlignment `0x200`;
- SectionAlignment `0x1000`;
- SizeOfHeaders `0x200`;
- SizeOfImage `0x2000`;
- eine Section bei RVA `0x1000`, Raw Offset `0x200` und Raw Size `0x200`;
- keine Data Directories.

Feste Faelle:

| ID | Variation | Erwartung |
|---|---|---|
| PE-VALID-NORMAL | keine | Konstruktion von `PEImage` erfolgreich |
| PE-VALID-LOW | FileAlignment und SectionAlignment `0x200` | erfolgreich |
| PE-IMAGEBASE-ZERO | ImageBase `0` | `UNSUPPORTED_PE_FORMAT` |
| PE-IMAGEBASE-MISALIGNED | ImageBase plus `0x1000` | `UNSUPPORTED_PE_FORMAT` |
| PE-FILE-BELOW | FileAlignment `0x100` | `UNSUPPORTED_PE_FORMAT` |
| PE-FILE-ABOVE | FileAlignment `0x20000` | `UNSUPPORTED_PE_FORMAT` |
| PE-FILE-NONPOWER | FileAlignment `0x300` | `UNSUPPORTED_PE_FORMAT` |
| PE-SECTION-BELOW-FILE | SectionAlignment `0x100`, FileAlignment `0x200` | `UNSUPPORTED_PE_FORMAT` |
| PE-LOW-MISMATCH | SectionAlignment `0x800`, FileAlignment `0x200` | `UNSUPPORTED_PE_FORMAT` |

Bei negativen Faellen muessen Fehlercode und Abbruch vor Data-Directory- und
Section-Auswertung belegt werden. Andere Fehlercodes gelten nicht als Erfolg.

### B3 - Fehlerkontextfixtures

Diese Faelle verwenden ausschliesslich synthetische `Binding`-Objekte mit
reservierten, nicht existierenden Testpfaden. `_write_error_only` darf nur in
jeweils einen neuen leeren Fixture-Ausgabeordner schreiben. `_verify_binding`,
`collect()` und `main()` werden nicht aufgerufen.

Feste Faelle:

| ID | gesetzter Kontext | erwartete JSON-Belegung |
|---|---|---|
| E-NONE | nur Startzeit | alle Bindungsfelder `null`, `input_bindings=[]` |
| E-EXPECTED | erwartete Steuerbindung | nur `control_binding_expected` gesetzt |
| E-CONTROL | plus verifizierte Steuerbindung | beide Steuerfelder gesetzt |
| E-TOOL | plus Werkzeugbindung | zusaetzlich `tool_binding` gesetzt |
| E-CONTRACT | plus Vertragsbindung | zusaetzlich `contract_binding` gesetzt |
| E-INPUT-1 | plus eine Zielbindung | exakt eine Zielbindung in Eingabereihenfolge |
| E-INPUT-3 | plus drei Zielbindungen | exakt drei Zielbindungen in Eingabereihenfolge |

Jeder Fall muss `complete=false`, exakt einen vorregistrierten Testfehler,
denselben Fehlercode in `stops`, unveraenderte Bindungswerte und ein gueltiges
UTC-Zeitfeld enthalten. Nicht gesetzte Werte duerfen nicht aus dem Dateisystem
rekonstruiert werden.

## Pflichtausgaben des spaeteren Validierungsschritts

Der Ergebnisordner muss atomar neu entstehen und genau enthalten:

- `syntax_validation.json`;
- `synthetic_fixture_validation.json`;
- `validation_report.json`.

`synthetic_fixture_validation.json` enthaelt fuer jeden festen Fall ID,
Eingaben, erwartetes Ergebnis, beobachtetes Ergebnis, `passed` und Fehler.
`validation_report.json` enthaelt Werkzeug-, Runner- und Interpreterbindung,
Fallzahlen je Gruppe, Gesamtzahl, bestandene und fehlgeschlagene Faelle,
Start-/Endzeit, Ausschlusspruefung und die Flags:

- `project_control_opened: false`;
- `real_target_binary_opened: false`;
- `manifest_generated: false`;
- `resolver_run: false`;
- `g2_touched: false`.

Die Ausgabe darf keine Manifestdaten, keine aus realen Binaries stammenden
Exporte und keine CPython-Tabellennamen enthalten.

## Akzeptanzkriterien und Gegenbaselines

Die spaetere Werkzeugvalidierung ist nur bestanden, wenn:

1. alle Bytebindungen vor dem ersten Python-Aufruf stimmen;
2. Phase A `parse_ok=true` liefert;
3. alle 4 Zaehlerfaelle exakt bestehen;
4. alle 9 Alignmentfaelle exakt bestehen;
5. alle 7 Fehlerkontextfaelle exakt bestehen;
6. Gesamtzahl `20`, bestanden `20`, fehlgeschlagen `0` ist;
7. keine ausgeschlossene Datei geoeffnet wurde;
8. keine unerwartete Datei oder `__pycache__` entstand;
9. alle drei Pflichtausgaben vollstaendig und widerspruchsfrei vorliegen.

Gegenbaselines sind die jeweils benachbarten positiven und negativen
Einzelfaelle. Ein erwarteter Fehler gilt nur mit exakt passendem Fehlercode als
bestanden. Teilresultate, ein Testabbruch oder fehlende Ausgaben duerfen nicht
auf eine kleinere Fallzahl normalisiert werden.

## Stopplinien

Sofortiger Gesamtstopp ohne Fortsetzung oder Ergebnisumdeutung bei:

- abweichender Werkzeug-, Runner- oder Interpreterbindung;
- fehlender Realpfad-Ausschlussliste;
- Syntaxfehler;
- Zugriff auf Projektsteuerdatei oder eines der 54 realen Zielbinaries;
- Aufruf von `main()` oder `collect()`;
- Import eines Projektmoduls oder Drittanbieterpakets;
- Netzwerk-, DLL-, Prozess- oder Shellzugriff aus dem Runner;
- unerwarteter Datei ausserhalb der erlaubten Ordner;
- abweichendem Fehlercode, fehlendem Fall oder unvollstaendiger Ausgabe.

Ein Stopp ist kein G1-Bestehen und darf nicht durch manuelle Korrektur eines
Ergebnis-JSON aufgehoben werden.

## Durchgefuehrte Schritte und beobachtetes Ergebnis in 213X

Der bestehende Quelltext und 213W wurden statisch gelesen. Anschliessend wurden
die festen Validierungsphasen, 20 Minimalfaelle, Pflichtausgaben,
Akzeptanzkriterien, Gegenbaselines und Stopplinien dokumentiert. Es wurde kein
Runner erstellt und kein Fall ausgefuehrt.

Beobachtet ist nur die Existenz dieser Vorregistrierung. Es gibt keine
Syntaxmessung und keine Fixture-Messergebnisse.

## Grenzen und nicht gepruefte Annahmen

- Die Umsetzbarkeit des spaeteren Runners ist noch nicht praktisch geprueft.
- Der gebundene Werkzeugquelltext wurde nicht geparst oder geladen.
- Die synthetischen PE-Rohbytes wurden nicht erzeugt.
- Fehler-JSON und atomare Ausgabe wurden nicht ausgefuehrt.
- Keine Aussage ueber reale Exporte, Relocations oder CPython-Tabellen folgt
  aus den synthetischen Fixtures.
- Ein spaeter bestandenes Paket waere nur Werkzeugvalidierung, kein G1-
  Resolvernachweis und kein Nachweis einer MCM-Funktion.

## Konkrete Schlussfolgerung

Ein begrenzter, synthetischer Validierungsvertrag ist vorregistriert. Er
isoliert die drei zuletzt korrigierten Werkzeugbereiche und sperrt die
Projektsteuerdatei sowie alle 54 realen Zielbinaries. Aktuell liegt kein
Validierungsergebnis vor.

G1 bleibt nicht bestanden, G0 bleibt abhaengig, G2 und Huerde G bleiben
gesperrt. Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes sollte 213X unabhaengig statisch geprueft werden, insbesondere
auf vollstaendige Fixture-Abdeckung, Widerspruchsfreiheit der Ausschlussregeln,
feste Fallzahl, eindeutige Fehlerorakel und die Trennung von synthetischer
Werkzeugvalidierung und realem G1-Zielkorpus.

Noch keine Runnerimplementierung, keine Syntaxpruefung, keine Kompilierung,
kein Test, kein Werkzeuglauf, keine Steuerdateierzeugung, kein Oeffnen realer
Zielbinaries, keine Manifesterzeugung, kein Resolverlauf, keine G2-Bearbeitung
und keine Oeffnung von Huerde G.
