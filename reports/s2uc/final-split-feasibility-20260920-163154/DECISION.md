# Abschliessende statische Machbarkeitspruefung der S2-UC-Modultrennung

**Befund: Diese Trennung traegt unter den unveraenderten Grenzen nicht. Keine Umsetzung vorgeschlagen.** Die Untersuchung endet hier; keine weitere Optimierungsrunde wird daraus gestartet.

Die fachliche Vergleichsfrage bleibt unveraendert: unmittelbares Sequenzspeichern gegen Behalten nach wiederholter Bestaetigung einschliesslich Erinnerungsverlusten. Dieser Befund betrifft Quellbyte-Budgets, nicht die Forschungsrichtung und nicht Prozessspeicher.

## 1. Vorabpruefung der maximalen Einsparung innerhalb einer reinen Trennung

Ausgang: 477802 Byte / 29 Projektdateien. Fuer eine bewusst ueberoptimistische Rechnung werden die drei grossen Kopplungsbereiche vollstaendig aus dem aktiven Bestand gestrichen: gesamter bisheriger NU/NP/Versiegelungsapparat; gesamtes bisheriges run_binding-Modul; Rootinitialisierer und Exporttabelle. Zusaetzlich entfallen TS-Runner/TS-Trace und der unbenutzte TY-Ledgerimport. Kein Posten wird doppelt abgezogen.

Verbleibende unveraenderte Dateien nach Abzug der 49-Byte-Importzeile: **116339 Byte**. Eine leere Ersatzimplementierung haette 14733 Byte Platz bis 131072. Sie waere natuerlich nicht funktionsfaehig.

| Zwingend zu erhaltender vorhandener Implementierungsbestand | LF/UTF-8-Quellbytes |
|---|---:|
| Verbleibende Dateien (Originalbytes, nur unbenutzte Importzeile abgezogen) | 116339 |
| Ausgewaehlte NU-Funktionen/Klasse mit Fehlervertraegen | 3803 |
| Ausgewaehlte V6-Funktionen mit bestehenden Pruefpflichten | 15231 |
| **Teilbestand vor Imports, Konstanten, V6-Lesezweig und neuen Hüllen** | **135373** |
| **Ueberschreitung aktive Bindungen** | **4301** |

Die Grenze ist bereits ohne die neue Quellenplanhilfe, ohne den 2309-Byte-V6-Lesezweig, ohne Generator-/Bindungskonstanten, ohne canonical/digest und ohne irgendeine Rezeptor-Kompatibilitaetshuelle verletzt. Die Rootentkopplung ist hierbei sogar mit NULL Zusatzkosten angesetzt. Deshalb muss fuer diesen negativen Machbarkeitsentscheid keine hypothetische Rootloesung als gelungen behauptet werden.

Aussagegrenze: Die 4301 Byte sind eine exakt nachgezaehlte Untergrenze fuer das Herausloesen der vorhandenen Implementierungsbloecke, keine mathematische Mindestgroesse beliebiger Neuimplementierungen. Eine zusaetzliche statische AST-Darstellung ohne Funktionsdocstrings und Kommentare ergab fuer V6 13512 und NU 3859 Byte, damit noch 133710 Byte gesamt bzw. 2638 Byte Ueberschreitung ohne die restlichen Pflichtteile. Codekompression oder inhaltliche Neuschreibung wird nicht als Modultrennung eingeschmuggelt.

## 2. NU-Generator: vollstaendiger benoetigter Ausschnitt

`_s2nu_private_source_binding.py:35-147` liefert:

- S2NUError und require: typisierter ValueError mit unveraendertem code.
- WindowSpec mit stream/window-Validierung, recipe und payload; native_index fuer den bestehenden payload-Vertrag.
- PERMUTATION und GROUPS; groups_payload; prepare_groups mit SHA-256-basierter Phase und unveraenderter Reihenfolge.
- group_value, sample_value, render und pcm_window. Zeit-/Amplitudenausdruecke, math.sin-Aufrufe und Akkumulationsreihenfolge bleiben exakt erhalten. Keine Vektorisierung oder Vorberechnung als vermeintlich gleiche Optimierung.
- render prueft Indextupelgroesse, jeden endlichen Domaenenwert und schreibt mit struct.pack_into("<f", ...) einmalig Float32 nach Binary64-Rechnung; Rueckgabe bleibt bytearray.
- WindowSpec.payload benoetigt canonical/digest: die 2 reinen Funktionen aus reports/s2nd/seal_inventory.py:28-34 muessen lokal/shared rein ausgelagert werden. Rueckimport in den historischen Versiegeler wuerde die Einsparung wieder aufheben.

Nicht fuer pcm_window benoetigt: watched, generator_identity, preseal_once, execution_plan, evaluation_plan, controls, budgets, correspondences, Publikation und Umgebungs-/Profilversiegelung. Die historischen Module bleiben ausserhalb des aktiven Pfads bestehen. Ein spaeterer gemeinsamer Kern muesste von historischen Fassaden reexportiert werden, damit insbesondere `type(spec) is WindowSpec` keine zweite inkompatible Klasse erzeugt. Das ist eine offene Kompatibilitaetsarbeit, im Nullkosten-/Teilbestandsmodell nicht als erledigt ausgegeben.

## 3. V6-Bindung: benoetigt versus historisch

Benoetigt sind _sha, _run_pair, build, validate, reference, _resolve_reference, _validate_inventory, _v6_rows, _v6_alternatives, _validate_v6_budget, _v6_test_ids, _validate_v6_qualification, load_for_start sowie der V6-Lesezweig aus load. RUNS/TARGETS und Test-/Befehlsbindung bleiben gleich.

`_s2uc_run_entry.py:210` ruft run_binding.validate auf: nur den Starterimport umzuschalten reicht deshalb nicht. Beide Verbraucher und die Source-Plan-Imports muessen auf denselben neuen Kern zeigen; _ACTIVE und der komplette Dependency-Scanner sind entsprechend neu zuzuordnen.

V1-V5-Zweige und die alten Qualifikations-/Budgetpruefer sowie Erzeugungshelfer koennen in der bisherigen Strukturlesefassade bleiben. Der V6-Einstieg darf diese Fassade nicht importieren, auch nicht verzoegert. Der jetzige load_for_start-Aufruf von load im Altformatfehlerzweig muss durch direkte Ablehnung des Formats ersetzt werden; die historische Lesbarkeit bleibt dann nur ueber den gesonderten Leser erhalten. Das aendert einen Fehlerpfad des Starters, darf aber keine fachliche Pruefung auf dem zugelassenen V6-Pfad entfernen.

Insbesondere unveraendert: synthetische Belege sperren, Referenzhash/Groesse, vollständige aktuelle Importmenge samt externer Runtime, aktive Quellbytegrenze, Pflichtzweige/Posten, exakte finale Dateigroesse, unveraenderte Reserven, Qualifikations-ID/Test-ID/Dateistandbindung, Gate vor Supplier, kein Ausgabeordner bei Vorabweisung.

## 4. Rezeptoreingang und Abbruch der Detailplanung

Der Import des bestehenden Paketinitialisierers zieht root_lazy_exports.py ein. Nur das Verschieben dieses Imports nach __getattr__ spart in der verbindlichen vollstaendigen Importverfolgung nichts. Eine neue Paketfassade, die wieder die alten Module importiert, spart ebenfalls nichts.

Der NJ-Code prueft in `_s2nj_private_auditory_output_projection.py:133-134` den SHA-256 der Datei `spectral.__file__`. `AuditoryReceptorState`/Contact haben eine gemeinsame Klassenidentitaet aus broadband_hearing_path.py; Kopieren und getrenntes Laden derselben Definitionen wuerde diese Identitaet nicht erhalten. Eine echte Auslagerung braeuchte somit byteidentisches Spektralmodul, konsistente relative Hilfsmodule und genau eine kanonische Definition mit kompatiblen alten Reexports. Alte Pins und Root-Exports duerften nicht stillschweigend angepasst werden.

Hier wird KEINE konkrete kompatible Rezeptortrennung als fertig nachgewiesen behauptet. Die vom Auftrag vorgegebene Stoppreihenfolge greift vorher: Selbst eine perfekte Entfernung beider Rootdateien bei kostenloser Erhaltung aller Schnittstellen laesst das aktive Defizit bestehen. Eine weitere Rootarchitekturplanung waere deshalb eine unautorisierte Fortsetzung der Optimierungsrunde.

## 5. Gemeinsame Dateizuordnung

Aus aktiver Erreichbarkeit optimistisch entfernt (historische Dateien nicht geloescht):

| Datei | Originalbytes |
|---|---:|
| `mcm_field_organism/__init__.py` | 940 |
| `mcm_field_organism/root_lazy_exports.py` | 258911 |
| `reports/s2nd/seal_inventory.py` | 17470 |
| `tools/_s2np_private_source_binding.py` | 15138 |
| `tools/_s2nu_private_source_binding.py` | 13635 |
| `tools/_s2ts_temporal_trace.py` | 5001 |
| `tools/_s2ts_temporal_trace_run.py` | 10468 |
| `tools/_s2ty_resource_ledger.py` | 5207 |
| `tools/_s2uc_run_binding.py` | 34644 |

Verbleibend; jeder Posten genau einmal gezaehlt:

| Datei | Byte |
|---|---:|
| `mcm_field_organism/broadband_hearing_path.py` | 7983 |
| `mcm_field_organism/carrier_baselines.py` | 3572 |
| `mcm_field_organism/controlled_audio_source.py` | 1237 |
| `mcm_field_organism/log_spectral_receptor.py` | 7024 |
| `tools/_s2nj_private_auditory_output_projection.py` | 7700 |
| `tools/_s2tu_retained_trace.py` | 3846 |
| `tools/_s2tw_exact_confirmation.py` | 1283 |
| `tools/_s2ty_audio_materialization.py` | 4090 |
| `tools/_s2ub_candidate_confirmation.py` | 9869 |
| `tools/_s2ub_candidate_verification.py` | 3075 |
| `tools/_s2uc_dependencies.py` | 4937 |
| `tools/_s2uc_evaluation.py` | 2341 |
| `tools/_s2uc_neutral_connection.py` | 8749 |
| `tools/_s2uc_record_codec.py` | 8529 |
| `tools/_s2uc_resource_ledger.py` | 2656 |
| `tools/_s2uc_run_entry.py` | 13581 |
| `tools/_s2uc_source_adapter.py` | 1442 |
| `tools/_s2uc_source_binding.py` | 6058 |
| `tools/_s2uc_verification.py` | 17086 |
| `tools/s2uc_run_bound_once.py` | 1281 |

Neue/ausgelagerte Bestandteile im vollstaendigeren Kostenmodell:

| Bestandteil | Byte | Grundlage |
|---|---:|---|
| `tools/_s2uc_pcm_generator.py` | 4493 | extracted plus 256 estimated |
| `tools/_s2uc_v6_binding.py` | 19030 | extracted plus 512 estimated |
| `tools/_s2uc_source_plan.py` | 976 | LF extracted text |
| `MODEL_ONLY/receptor_compatibility.py` | 0 | optimistic zero cost, NOT a solved interface |

**Aktivmodell gesamt: 140838 Byte; Defizit 9766 Byte.** Die 256/512 Byte Modulhuellenaufschlaege sind Schaetzungen. Null Byte fuer Rezeptorkompatibilitaet ist absichtlich ueberoptimistisch, nicht eine Umsetzungszusage.

## 6. Shared-Bilanz mit saemtlichen bisherigen Pflichtposten

| Pflichtposten | Byte (Modell) |
|---|---:|
| active_dependency_sources | 140838 |
| frozen_source_binding | 19210 |
| dependency_inventory | 5082 |
| qualification_summary | 4265 |
| qualification_protocol | 12538 |
| qualification_budget | 1060 |
| qualification_result | 640 |
| budget_ledger | 1318 |
| terminal_reserve | 16384 |
| **Summe** | **201335** |

Shared-Spielraum im Modell: 60809 Byte unter 262144. Die weiteren Artefaktgroessen uebernehmen die ausdruecklichen, eher groesseren Posten des vorherigen statischen Modells; es sind keine neuen Qualifikations-/Laufartefakte. Sie enthalten alle Pflichtartefakte und Referenzen auf Testdateien. Neue echte Pfadnamen, zusaetzliche Tests, Glue-Code und die noch ungeklaerte Root-Kompatibilitaet sind vor einer spaeteren Umsetzung neu zu vermessen. Bereits die aktive Grenze scheitert unabhaengig davon.

Python-Standardbibliothek und NumPy bleiben getrennte externe Laufzeitabhaengigkeiten; Quellbytes sind keine RAM-Messung. Keine Grenzaenderung und kein Wechsel von Quellbytes zu Referenzbytes.

## 7. Abschluss / Architekturentscheidung

Das beauftragte Ergebnis ist der negative Machbarkeitsbefund fuer diese zusammenhaengende Trennung, kein weiterer Bereinigungsauftrag. Keine Implementation, Quellenproduktion, Rezeptor-/Memoryausfuehrung oder Tests erfolgt. Es wurden ausschliesslich Textbereiche/ASTs gelesen und Groessen berechnet; die Ausgangshashes aller 29 Produktdateien stimmen weiterhin.

**Naechster Schritt fuer den Projektanalysten:** anhand dieses Defizits die Architekturentscheidung treffen. Ich schlage keine weitere Optimierungsrunde und keinen Teilumbau vor. Die unabhängige Abnahme des Zulassungspakets bleibt offen; der reale Vergleich bleibt gesperrt und der historische Lauf NOT_EVALUABLE.
