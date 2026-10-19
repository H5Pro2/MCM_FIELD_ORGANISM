# S2-UC V6: begrenzte Validierungskorrektur

Status: neutrale Entwicklung, keine formale Qualifikation. Unabhaengige Abnahme offen.

## Umgesetzt

- Vollstaendige, eindeutige und nichtnegative Metadaten-/Shared-Posten; exakte Groessen gegen Referenzen.
- Pflichtzweige success/failure/minimal und genau vier Beitragsschluessel; Beitraege, Summen und feste Reserven werden unabhaengig nachgerechnet.
- Alle drei Qualifikationsartefakte in der Schlussbilanz; inhaltliche Pruefung von Ergebnis, Testanzahl, vollstaendigen IDs der beiden aktuellen Testdateien, Befehl, Qualifikations-ID und Code-/Testreferenzen.
- Positivbelege tragen SYNTHETIC-TEST-DATA-NOT-A-QUALIFICATION. Sie sind Testdaten, kein Nachweis einer ausgefuehrten Qualifikation.
- Separates Schema s2uc.qualification-budget.v1 fuer das referenzierte Qualifikationsbudget: Manifest, gebundene Abhaengigkeiten, Summary/Protokoll und Terminalreserve; dieselben festen alternativen Record-/Verifikationsreserven. Dessen Dateigroesse geht in den finalen V6-Ledger ein.
- Kandidatenverifizierer tools/_s2ub_candidate_verification.py in den bisherigen Laufzeitbestand _ACTIVE aufgenommen.

## Exakte Groessenbindung

`final_binding_reserve` bleibt trotz seines historischen Namens eine EXAKTE Dateigroessenbindung. Auch gueltiger JSON-Whitespace von einem Byte fuehrt zur Abweisung. Es ist keine Obergrenzenreserve. Recordreserve 245760 und absolute Recordgrenze 262144 bleiben unveraendert.

## Regression

Befehl: `C:\Python314\python.exe -m unittest -v tests.test_s2uc_neutral_connection tests.test_s2uc_materialization_connection`

50/50 Tests bestanden, Exitcode 0. Vor-/Nachhashes waehrend des Tests identisch. Die ersten drei V6-Faelle sind erhalten. Neue Negativfaelle pruefen den echten Starter mit Supplier=0, geschlossenem Gate und nicht angelegtem Ausgabeordner. Kein Validator wird ersetzt; der Spy verwendet wraps.

Erste Regression: 50 Tests, ein Fixturefehler durch geteilte Code-Referenzen (falsche fruehe Abweisung FINAL_DEPENDENCY_INVALID). Durch deepcopy der Qualifikationsdateiliste korrigiert. Originalausgabe bleibt in regression-initial.txt.

Alle konkreten Test-IDs und Ergebnisse: test-result.json und test-output.txt.

## Abhaengigkeitsabgleich und verbleibende Luecke

Statische Importverfolgung ab tools/s2uc_run_bound_once.py: 28 Projektdateien, 469701 Quellbytes. Relative Importe, lokale/verzoegerte Importe und Paketinitialisierer wurden einbezogen; keine Quelle wurde produziert oder geoeffnet.

Der bisherige, um den Kandidatenverifizierer erweiterte _ACTIVE-Teilbestand hat 123115 Byte. Es fehlen weiterhin 12 transitiv importierte Projektdateien, die dependency-audit.json einzeln mit Groesse, SHA-256 und Importkanten ausweist.

Vollstaendige Projektquellbytes ueberschreiten active_bindings=131072 um 338629 Byte und bereits ohne weitere Shared-Artefakte die Shared-Grenze 262144 um 207557 Byte. Die externe Laufzeit (Standardbibliothek und NumPy mit Versionen) ist getrennt ausgewiesen, nicht als 0 Byte Prozessspeicher behauptet.

Der V6-Validator prueft den angegebenen Abhaengigkeitsbestand und dessen Referenzen, erzwingt bislang aber NICHT dessen Gleichheit mit der vollstaendigen transitiven Importmenge. Die Positivfixture bindet bewusst einen begrenzten neutralen Codebestand; ihr Erfolg ist kein Vollstaendigkeitsnachweis fuer eine reale Bindung. Diese Luecke ist offen, das Gesamtpaket daher noch nicht als vollstaendig geschlossen abnehmbar.

Historische V14-Bindung nur lesend abgeglichen: historical-binding-comparison.json. Keine historischen Inventare oder Laufartefakte geaendert. Keine neue finale Hauptlaufbindung. Historischer Lauf bleibt NOT_EVALUABLE.

Naechster Vorschlag / RUECKMELDUNG ERFORDERLICH: vollstaendige Abhaengigkeitsmenge zwingend vor dem Starter pruefen und den realen Pfad bei der gemessenen Budgetueberschreitung geschlossen halten; synthetische Unit-Fixtures ausdruecklich isolieren. Keine automatische Grenzerhoehung oder Umdeutung von Quellbytes in Referenzbytes. Eine spaetere Budget-/Architekturentscheidung muss separat erfolgen.

## Geaenderte Dateien (SHA-256)

- `tools/_s2uc_run_binding.py`
  - vorher: `2a9987ce26589789a3ec24da9af56afdd2d420b24987571bd71ae42b2b95f06c`
  - nachher: `b7fb03a947fbd959800e59a7e85cbf0c3b390f60e1bbd1541a9e18a72f1bb67a`
- `tools/_s2uc_run_entry.py`
  - vorher: `ae84f3a4138adab29937578a52e7abca675f710365cab55f11f1f8309c21597f`
  - nachher: `1005335a67c6bf089dbc2399fb0b874d062924537b7522982f4c73f030778349`
- `tests/test_s2uc_materialization_connection.py`
  - vorher: `dcfa65627a01384c62167adb3e3bfb51f2d23b83e8e9169f0b63196cf67aede4`
  - nachher: `ba25a563f4b020e243ebd074e2a0c84dc2df9997fbc3a5e7220881630b01908a`

## Neue Testmethoden

- `tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests.test_v6_final_binding_accepts_only_the_prepared_identity_and_resolved_artifacts`: OK
- `tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests.test_v6_starter_rejects_actual_final_file_above_bound_reserve`: OK
- `tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests.test_v6_starter_rejects_changed_reserves_and_qualification_artifact_sizes`: OK
- `tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests.test_v6_starter_rejects_duplicate_negative_missing_and_noninteger_items`: OK
- `tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests.test_v6_starter_rejects_empty_qualification_artifacts`: OK
- `tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests.test_v6_starter_rejects_inconsistent_branch_contributions_with_current_digests`: OK
- `tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests.test_v6_starter_rejects_mismatched_qualification_ids_results_tests_and_code`: OK
- `tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests.test_v6_starter_rejects_missing_or_extra_branches_and_contribution_keys`: OK
- `tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests.test_v6_starter_rejects_undercounted_single_item_with_current_digests`: OK
