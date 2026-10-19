# S2-UC V6: verbindliche Zulassungsvorpruefung

Entwicklerabschluss: begrenztes Korrekturpaket umgesetzt und neutral regressiv geprueft. Unabhaengige Abnahme offen. Keine formale Qualifikation, keine neue finale Hauptlaufbindung und kein realer Quellenlauf.

## Aenderung

- Der echte Starter ruft zwingend load_for_start auf. Kein Parameter, Umgebungswert oder Bindungsfeld kann die Zulassungspruefung abschalten oder die Scanwurzel/den Einstieg ersetzen.
- load bleibt die abgegrenzte Strukturvalidierung fuer synthetische Testdaten. Deren Erfolg bedeutet keine Zulassung. Die vorhandenen Groessen-, Beitrags- und Qualifikationsgegenproben behalten ihre jeweiligen Fehlergruende auf dieser Ebene.
- Markierte synthetische Belege bzw. unpassende Qualifikations-ID-Klasse werden am Starter mit FINAL_SYNTHETIC_QUALIFICATION_FORBIDDEN zurueckgewiesen. Danach werden aktuelle Referenzen, Inventar, die vollstaendige Importmenge und externe Laufzeitbindung geprueft.
- Ein konsistentes, aber unvollstaendiges Inventar scheitert mit FINAL_DEPENDENCY_INCOMPLETE. Vollstaendig gebundene, aber zu grosse Quellbestaende scheitern mit FINAL_DEPENDENCY_BUDGET_EXCEEDED. Erst danach koennte die vollstaendige Qualifikations-/Ledger-Strukturpruefung und anschliessend Ausfuehrung folgen.
- Alte Formate bleiben strukturell lesbar, begruenden aber keine Starterzulassung: FINAL_START_BINDING_VERSION_INVALID nach erfolgreicher Strukturpruefung. Damit existiert kein Rueckfall auf eine alte Bindung ohne Vollstaendigkeitspruefung.
- _s2uc_dependencies.current ermittelt read-only den festen aktuellen Einstieg. AST-Verfolgung umfasst lokale/verzoegerte und transitive Importe, relative Importe, Paketinitialisierer und statisch ausgewaehlte Lazy-Exports des bestehenden Pakets. Nicht aufloesbare dynamische Importaufrufe werden gesperrt (FINAL_DEPENDENCY_DISCOVERY_UNRESOLVED). Der bestehende Lazy-Dispatcher wird anhand seiner konkreten Aufrufform und Exporttabelle behandelt.

## Belegter realer Sperrgrund

29 Projektdateien: 477802 Quellbytes. Darin enthalten: root_lazy_exports.py mit 258911 Byte.

- active_bindings-Reserve unveraendert 131072: Ueberschreitung 346730 Byte.
- Shared-Grenze unveraendert 262144: allein Projektquellbytes bereits 215658 Byte darueber.
- Externe Laufzeit (Python-Standardbibliothek und NumPy) separat mit Versionen in dependency-inventory.json; keine Prozessspeichermessung und keine Umdeutung in Referenzbytes.
- Der historische _ACTIVE-Teilbestand ist nicht mehr der Zulassungsnachweis des realen Starters. Direkte neutrale Ausfuehrungstests unterhalb dieser Zulassung bleiben Komponentenpruefungen. Der reale Pfad kommt mit dem vollstaendigen Bestand nicht bis zur Gateoeffnung.

## Testnachweis

Befehl: `C:\Python314\python.exe -m unittest -v tests.test_s2uc_neutral_connection tests.test_s2uc_materialization_connection`

57 / 57 Tests bestanden, Exitcode 0. Alle 31 gebundenen Projekt-/Testdateien vor/nach dem Lauf identisch; aktueller Stand erneut gegen die Nachhashes gelesen.

Neue Starter-Negativtests ersetzen weder Admission noch Scanner durch Mocks. Ein wraps-Spy beobachtet lediglich, dass run_bound_once nicht aufgerufen wurde. Jeder prueft ValueError mit exaktem Fehlertext, Supplier=0, MAIN_GATE=False und fehlende Ergebnisablage.

Die vollstaendige Negativfixture deklariert ihre Budgetueberschreitung; die Zulassung weist sie bereits vorher anhand der Quellbytes zurueck. Die nichtsynthetisch benannten negativen Claims sind absichtlich gefaelschte Temporaer-Testdaten, keine Qualifikationsbelege.

Ein erster Lauf mit 54 Tests enthielt eine fehlgeschlagene reine Pfadvergleichsassertion (Windows-Trenner gegen POSIX-Inventarnamen). Nach Normalisierung und Ergaenzung weiterer Gegenproben erfolgte die erfolgreiche Regression. initial-test-output.txt und initial-exitcode.txt bleiben erhalten.

Wesentliche Test-IDs (jeweils tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests):

- `test_v6_real_starter_rejects_synthetic_qualification`: OK
- `test_v6_real_starter_rejects_matching_but_incomplete_dependencies`: OK
- `test_v6_real_starter_rejects_complete_but_oversized_dependencies`: OK
- `test_v6_real_starter_rejects_omitted_delayed_transitive_and_package_files`: OK
- `test_real_starter_rejects_structurally_valid_legacy_binding`: OK
- `test_v6_dependency_closure_includes_transitive_delayed_and_package_imports`: OK
- `test_v6_dependency_scanner_follows_nested_relative_and_delayed_imports`: OK

Alle 57 vollstaendigen IDs und Ergebnisse stehen in test-result.json; die unverkuerzte Prozessausgabe steht in test-output.txt.

## Zuordnung vorhandener Gegenproben

Die 8 vorhandenen Methoden mit Praefix test_v6_starter_rejects_ heissen jetzt test_v6_validation_rejects_. Inhaltliche Manipulationen und erwartete Fehler bleiben erhalten; sie rufen die echte Strukturvalidierung load statt den jetzt zwingend sperrenden Starter auf. Die positive test_v6_final_binding_accepts_only_the_prepared_identity_and_resolved_artifacts bleibt erhalten.

Der fruehere Starter-Erfolgstest mit gemocktem Binding-Loader wurde durch test_authorization_gate_and_isolated_neutral_execution ersetzt: fehlende Autorisierung am echten Starter; neutrale Ausfuehrung separat unterhalb der Zulassung. Kein simuliertes erfolgreiches Durchlaufen der realen Zulassungsbarriere wird behauptet.

## Geaenderte Dateien / SHA-256

- `tools/_s2uc_run_binding.py`
  - vorher: `b7fb03a947fbd959800e59a7e85cbf0c3b390f60e1bbd1541a9e18a72f1bb67a`
  - nachher: `2d2b359078ffbdd89edf36103f41d99ba33fcbdf0e31b4a34b40cc94fe75f591`
- `tools/s2uc_run_bound_once.py`
  - vorher: `a173834900fe7108ba676c69f46a0cf393f2ca006c8579ef8e9a7834802b45a0`
  - nachher: `bcdd6537958e019bd8ef713e89bba4e10e567d6285852f3725d5cdedd83d0e0e`
- `tests/test_s2uc_materialization_connection.py`
  - vorher: `ba25a563f4b020e243ebd074e2a0c84dc2df9997fbc3a5e7220881630b01908a`
  - nachher: `f84059d2fab384ec72b2c6f4d2d80ef95ee9e6efe8fdab9523b4b3a19f24a2f7`
- `tools/_s2uc_dependencies.py`
  - vorher: nicht vorhanden (neues Pruefmodul)
  - nachher: `57e38a7cac23976e2d16274907e9528afb986961e051475362ea0f7b8f65aaf2`

## Grenzen und naechster Schritt

Historische Inventare, V14-Bindung und Laufbefunde wurden nicht geaendert. Der historische Lauf bleibt NOT_EVALUABLE. Keine Grenzerhoehung, Architekturumbaumaßnahme, Quellenproduktion oder Hauptlaufwiederholung.

Naechster sinnvoller Schritt: unabhaengige Pruefung dieses begrenzten Korrekturpakets. Erst danach gegebenenfalls einen separaten, statischen Auftrag zur Verringerung des Abhaengigkeitsbestands vorbereiten; die Budgetueberschreitung ist kein MCM-Falsifikationsbefund. Im aktuellen Auftrag wird keine solche Architekturarbeit begonnen.
