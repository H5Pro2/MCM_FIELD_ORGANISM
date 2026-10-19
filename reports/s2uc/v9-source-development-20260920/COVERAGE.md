# V9 Abdeckung und Grenzen

Die 138 bisherigen Test-IDs bleiben Pflicht. Alte V7-/V8-Tests pruefen weiterhin ihre unveraenderten Zulassungsgrenzen; die V8-Lebenszyklustests laufen ueber denselben privaten Kern wie V9.

| Pflicht | Nachweisgruppe |
|---|---|
| Fuenf Quellen, Reihenfolge, Hash/Rezept/Profile/Zeit/Ziele | SourceExecutionTests.test_fixed_sources_targets_profiles_and_order |
| Kein NU-Aufruf bei Vorbereitung, feste Fensterwahl, kein Cache, keine zweite Kopie | test_prepared_supplier_is_lazy_fixed_five_uncached_no_copy, ausschliesslich Mock-Generator |
| Reale/Null-/Legacy-Mischungen, fehlende Autorisierung, stale Inventare | test_neutral_binding_rejects_real_null_legacy_and_missing_authorization; test_neutral_binder_rejects_resealed_real_manifest_and_stale_inventory |
| 58 Nichtnull-Receipts, fuenf Vektoren, unveraenderte Gain/Loss-Nichtmessung | test_nonzero_58_receipts_five_vectors_same_arm_values |
| 57/58-Praefix, Hashstop vor Rezeptor, Codecabschluss | test_failure_58_retains_57_and_primary; test_payload_hash_mismatch_before_receptor; test_codec_failure_closes_owners_and_gate |
| Recordformen mit langen Hexwerten und Flaglisten, exakte Reserve/+1 | test_nonzero_codec_vectors_flags_and_boundary |
| Belegvollstaendigkeit, Fixture-/Formal-/Real-Ablehnung | test_qualification_fixture_and_mutations_never_authorize |
| Vollstaendiger Werkzeugbestand; konstante Artefaktgrenzen | test_inventory_complete_tools_and_limits_unchanged; SourceProcessTests.test_missing_parent_or_child_inventory_prevents_process |
| Aktive Commitgrenze und Mitgliedschaft vor Produktimport | test_limited_nonzero_success_before_imports; test_missing_or_false_admission_stops_before_imports |
| Begrenzter injizierter MemoryError im 58. Versuch | test_limited_memoryerror_58_is_not_evaluable |
| Unbedingte reale Sperre auch nach Strukturpruefung | test_public_real_entry_unconditionally_closed; test_public_cli_has_no_real_mode; unveraenderter V8-Startertest |

Beobachtete neutrale technische Funktion ist kein wissenschaftlicher Quellennachweis. Der synthetische Testlauf misst keine Erinnerungsgewinne/-verluste. Unabhaengige Abnahme und eine etwaige spaetere reale Laufentscheidung bleiben getrennt offen.

## Zusaetzliche V9-Abschlussgegenproben

- test_nonzero_pending_receipt_and_owner_constructor_failure: Nichtnull-Receipt zwischen Armaufrufen bleibt erhalten; verbrauchte Identitaet bleibt gesperrt.
- test_constructor_failure_zero_sources_closes_owners: Konstruktorfehler vor dem ersten Supplier schliesst beide registrierten Owner.
- test_publication_terminal_failure_counts_minimal_and_record: Record, Verifikation, Fehler, Terminal und Minimalterminal werden gemeinsam bilanziert.
- test_staging_failure_counts_all_remaining_bytes: verbliebene 73 Stagingbytes bleiben im Konto, fehlender dauerhafter Abschluss bleibt sichtbar.
- test_source_preparation_reader_has_no_authority: statischer Quellenleser erzeugt trotz konsistenter Belege keine Ausfuehrungsfreigabe.
- test_external_child_abort_never_substitutes_product_closure: echter Kindprozessabbruch vor dem Produktimport liefert EXTERNAL_ABORT_NO_PRODUCT_SUCCESS und keinen Produktabschluss.

Die Quellendaten des NU-Plans werden ausschliesslich gelesen. Der reale Supplieranschluss ist vorbereitet und mit einem Mock geprueft, aber kein NU-Payload wurde fuer dieses Paket produziert.
