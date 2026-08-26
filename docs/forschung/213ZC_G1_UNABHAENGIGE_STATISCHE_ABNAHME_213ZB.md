# 213ZC - G1 Unabhaengige statische Abnahme von 213ZB

## Einordnung

`213ZC` ist eine unabhaengige statische Abnahme, kein Forschungslauf und
keine Ausfuehrungsfreigabe. Eine Laufnummer wird nicht vergeben.

## Forschungsfrage und Auftrag

Erfuellen `tests/validate_static_binary_evidence.py` und die Dokumentation
`213ZB` den in `213X`, `213Z` und `213ZA` abgenommenen Vertrag vollstaendig,
insbesondere hinsichtlich Bytebindungen, 54er-Ausschlussmenge, genau einer
Zielmodulausfuehrung, 21 eindeutigen Orakeln, Einprozess-Atomaritaet,
Importgrenzen und Realpfadsperren?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`;
- `docs/forschung/213Y_G1_UNABHAENGIGE_STATISCHE_PRUEFUNG_213X.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`;
- `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md`;
- `docs/forschung/213ZA_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213Z.md`;
- `docs/forschung/213ZB_G1_EINPROZESS_CONTROLLER_IMPLEMENTIERUNG.md`;
- `tests/validate_static_binary_evidence.py`;
- `tools/static_binary_evidence.py`, ausschliesslich statisch gelesen.

Keine externe Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Verwendet wurden nur statisches Textlesen, Textsuche, Dateigroesse,
SHA-256 und strukturvergleichende Codeverfolgung. Weder Controller noch
Werkzeug wurden importiert, geparst oder ausgefuehrt. Es erfolgten keine
Syntaxpruefung und kein Test.

Kontrollierte Bindungen:

| Datei | Bytes | SHA-256 |
|---|---:|---|
| `tests/validate_static_binary_evidence.py` | 25.727 | `50AD8FC8B08946B2BC584913F208C45592F9568A8DE9B8C00BF8B04FD6ABB3CD` |
| `213ZB_G1_EINPROZESS_CONTROLLER_IMPLEMENTIERUNG.md` | 5.165 | `1302BEB67F32E746B46ED7BDF5CC91806CF7B326BA028E9DA7F03CAAEBBE42A0` |
| `213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md` | 13.427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` |
| `213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | 6.253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` |
| `213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md` | 12.309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` |
| `tools/static_binary_evidence.py` | 42.225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` |

## Durchgefuehrte Schritte

1. Bytebindungen von Controller, Implementierungsdokument und Vertragsteilen
   kontrolliert.
2. CLI-Bindungsreihenfolge und Ausschlussartefakt-Pruefung verfolgt.
3. Importanweisungen, `ast.parse` und alle `runpy.run_path`-Stellen gesucht.
4. Alle festen Fall-IDs ausgezaehlt und den vier Gruppen zugeordnet.
5. Zaehl-, PE-, Fehlerkontext- und Routingorakel gegen die Muss-Regeln aus
   `213X` und `213Z` verfolgt.
6. Erfolgs- und Fehlerpfad ueber Staging, `fsync`, Rename, Aufraeumen und
   Ausnahmebehandlung verfolgt.
7. Realpfadvergleich und Schutz gegen unerwartete Dateien beziehungsweise
   `__pycache__` statisch gesucht.

## Messergebnisse und Gegenbaselines

### Bestaetigte statische Eigenschaften

- Controllerdatei: `1`;
- direkte `runpy.run_path`-Stellen: `1`;
- feste Fall-IDs: `21`;
- Gruppen: `4 + 9 + 7 + 1`;
- Erfolgspaket-Namen: exakt die drei vorregistrierten Namen;
- Fehlerpaket-Namen: exakt `validation_error.json`;
- Zielimport-Positivliste entspricht den elf statisch sichtbaren
  Werkzeugimporten;
- keine Runnerimporte von Projektmodulen, Drittanbietern, `importlib`,
  `ctypes` oder `subprocess`;
- keine direkten Aufrufe von Werkzeug-`main`, `collect` oder
  `_verify_binding`;
- Ausschlussartefakt wird gebunden und auf Schema, `1 + 53 = 54`, Rollen,
  Eindeutigkeit und absolute Slash-Pfadform geprueft.

Gegenbaseline war jeweils der vollstaendige, fail-closed Vertrag. Ein
vorhandener Fallname oder Ergebniszaehler gilt nicht als ausreichende
Abdeckung, wenn das zugehoerige Orakel die vorregistrierte Eigenschaft nicht
misst.

## Abnahmehemmende Befunde

### Befund 1 - Erfolg und Fehler koennen nach dem Erfolgs-Rename koexistieren

Schwere: hoch.

Der Controller publiziert zuerst den Erfolg durch
`publish_directory(staging, args.success_dir)`. Erst danach wird der
Temporaerordner mit `shutil.rmtree(args.temp_dir)` entfernt. Schlaegt diese
nachgelagerte Bereinigung fehl, erreicht die Ausnahme den gemeinsamen
Fehlerhandler. Dieser kann anschliessend zusaetzlich das Fehlerpaket unter
`args.error_dir` publizieren.

Damit koennen ein vollstaendig publiziertes Erfolgspaket und ein Fehlerpaket
fuer denselben Prozess koexistieren. Dies widerspricht der geforderten
atomaren Alternative: Fehler vor vollstaendigem Erfolg verwirft das
Erfolgs-Staging; nach erfolgreicher Publikation darf derselbe Lauf nicht mehr
als Fehler publiziert werden.

Erforderliche Korrektur: Alle fehlerfaehigen Bereinigungen muessen vor dem
Erfolgs-Rename abgeschlossen sein oder nach dem Rename ausserhalb des
Fehlerpublikationspfads liegen. Ein expliziter Publikationszustand muss eine
Fehlerpublikation nach erfolgreichem Rename ausschliessen.

### Befund 2 - vorgeschriebene Nebenwirkungs- und Bytecodekontrolle fehlt

Schwere: hoch.

`213X` verlangt vor und nach der Zielmodulausfuehrung die Bestaetigung, dass
weder `__pycache__` noch eine andere Datei ausserhalb der erlaubten Temporaer-
und Ergebnisordner entstanden ist. Der Controller setzt in
`syntax_validation.json` lediglich `bytecode_generated=false` und vergleicht
`sys.path` sowie `sys.meta_path`.

Es existiert keine statische Implementierung einer Vorher-/Nachher-Inventur
der erlaubten Dateigrenzen und keine Kontrolle bekannter `__pycache__`-Pfade.
Das gesetzte Ergebnisflag wird daher nicht gemessen.

Erforderliche Korrektur: Eine eng begrenzte, vorregistrierungskonforme
Vorher-/Nachher-Pruefung implementieren, die keine Realpfade beruehrt, aber
unerwartete Dateien und Bytecode ausserhalb der erlaubten Ordner erkennt.
Das Flag darf nur aus dieser Beobachtung abgeleitet werden.

### Befund 3 - Zaehlerfaelle messen nicht die Werkzeugausdruecke

Schwere: hoch.

`count_oracle` kontrolliert nur, ob jeder AST-Dump zwei unspezifische
Textfragmente enthaelt. Danach werden die beobachteten Zaehler direkt aus den
testseitigen Eingabewerten berechnet. Die in `213X` geforderten
In-Memory-Dictionaries in Form von `table_result` und `export_results` werden
nicht konstruiert; die konkreten Werkzeugausdruecke werden nicht mit dem
begrenzten Operatorinterpreter ausgewertet.

Ein Werkzeugausdruck koennte zusaetzliche Terme oder eine falsche Semantik
enthalten und dennoch die gesuchten Fragmente tragen, waehrend das manuell
berechnete `observed` weiterhin dem erwarteten Wert entspricht.

Erforderliche Korrektur: Die vier vorregistrierten Datenstrukturen wirklich
konstruieren und exakt die sechs zugelassenen AST-Ausdrucksformen mit einem
geschlossenen Auswerter fuer `len`, feste Indexe, Slice `1:4` und Summation
auswerten. Jede weitere AST-Form muss fail-closed stoppen.

### Befund 4 - Fehlerkontextorakel prueft die gestuften Bindungsfelder nicht

Schwere: hoch.

Die sieben Fehlerkontextfaelle setzen zwar schrittweise Kontextfelder, das
Akzeptanzprädikat prueft jedoch nur `complete`, Fehlercode, Stop, Anzahl der
Eingabebindungen und Zeitfelder. Es prueft nicht, ob
`control_binding_expected`, `control_binding_verified`, `tool_binding` und
`contract_binding` je Fall exakt gesetzt oder `null` sind. Ebenso wird bei
E-INPUT-1 und E-INPUT-3 weder Inhalt noch Eingabereihenfolge verglichen.

Damit koennen vertauschte, verlorene oder unerlaubt rekonstruierte Bindungen
bei allen sieben Faellen als bestanden gelten.

Erforderliche Korrektur: Fuer jeden Fall das vollstaendige erwartete
Bindungsbild einschliesslich aller `null`-Felder und der exakten geordneten
`input_bindings` gegen das erzeugte JSON vergleichen.

### Befund 5 - PE-Negativorakel belegt den geforderten fruehen Abbruch nicht

Schwere: mittel bis hoch.

Bei den sieben negativen PE-Faellen wird nur der Fehlercode
`UNSUPPORTED_PE_FORMAT` verglichen. `213X` verlangt zusaetzlich den Beleg,
dass der Fehler vor Data-Directory- und Section-Auswertung eintritt. Der
Controller instrumentiert oder prueft diese Auswertungsgrenze nicht.

Ein spaeter Fehler mit demselben Code koennte deshalb den Fall bestehen.

Erforderliche Korrektur: Das Orakel statisch an den Alignment-Pruefblock vor
Directory-Schleife und Section-Auswertung binden oder eine begrenzte
Instrumentierung vorregistrieren, die deren Nichterreichung beobachtet.

### Befund 6 - Realpfadvergleich prueft nur exakte Gleichheit

Schwere: mittel.

`verify_exclusion` bildet fuer geschuetzte Controllerpfade eine Menge und
prueft nur deren Schnittmenge mit den ausgeschlossenen Pfaden. `213Z` fordert
auch den Ausschluss, dass Fixture-, Staging-, Ergebnis- oder Runnerpfade unter
einem ausgeschlossenen Pfad liegen. Diese zweite lexikalische Relation wird
nicht implementiert.

Erforderliche Korrektur: Den fallgefalteten Windows-Pfadvergleich um eine
separatorbewusste Unterpfadpruefung erweitern, ohne Existenzabfrage, `stat`,
Oeffnen oder Aufloesen eines ausgeschlossenen Pfades.

## Grenzen und nicht gepruefte Annahmen

- Die Befunde beruhen ausschliesslich auf statischer Codeverfolgung.
- Syntax und Laufzeitverhalten des Controllers wurden nicht geprueft.
- Keines der 21 Fixtures wurde erzeugt oder ausgefuehrt.
- Keiner der 54 ausgeschlossenen Realpfade wurde geoeffnet, auf Existenz
  geprueft, aufgeloest oder gehasht.
- Weitere Syntax- oder Laufzeitfehler koennen erst nach statischer Korrektur,
  erneuter Abnahme und gesonderter Freigabe untersucht werden.
- Aus der Controllerpruefung folgt keine G1-Evidenz und keine Aussage ueber
  eine MCM-Funktion.

## Konkrete Schlussfolgerung

`213ZB` ist in Bindung, Grundstruktur, Fallzahl und Importgrenze weitgehend
vertragsnah, aber wegen sechs statisch abnahmehemmender Befunde noch nicht
ausfuehrungsreif. Insbesondere sind die atomare Ergebnisalternative und drei
zentrale Fixture-Orakel nicht hinreichend umgesetzt.

G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt.
Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Entwicklungsschritt

Als naechstes sollte genau ein statisches Korrekturpaket fuer
`tests/validate_static_binary_evidence.py` erstellt werden, das ausschliesslich
die sechs Befunde dieses Dokuments schliesst und Controller sowie
Korrekturdokument neu bytegenau bindet.

Danach ist erneut eine unabhaengige statische Abnahme erforderlich. Bis dahin
bleiben Syntaxpruefung, Tests, Controller- und Werkzeugausfuehrung, Zugriff auf
die 54 Realpfade, Manifest, Resolver, G2 und Huerde G gesperrt.
