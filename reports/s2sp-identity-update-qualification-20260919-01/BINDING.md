# S2-SP: Bindung der identitätserhaltenden PPB-Aktualisierung

Auftragskennung: `S2SP-IDENTITY-UPDATE-QUAL-20260919-01`

Die private Variante `identity-preserving.v1` ist auf zwei feste Modi
beschränkt. Der historische Default `historical.v1` bleibt unverändert. Nur
bei `previous == current` bleibt die jeweilige gespeicherte Komponente
bitgleich; jede andere Komponente verwendet weiterhin die historische Formel.
Support, Zeit, Slotwahl, Konsolidierung und Generationen werden nicht
übersprungen.

| Datei | SHA-256 |
| --- | --- |
| `mcm_field_organism/_ppb1_reference.py` | `6bd905d86d88f8f5e43863cffcc587e86080f92cbf38c85b3d1cc8347396b4a5` |
| `mcm_field_organism/_tspm1_private.py` | `16c2e60810c4b3bb26c56b757a3723dd6c1dcb1e02914d6dae8193ee2f4c070b` |
| `tools/_s2jw_profiled_memory_coordinator.py` | `0f9e9bce24acd2b4338127c856cad62be5c53d5a3fe4ec12915ed64255875a91` |
| `tools/_s2sp_private_memory_compare.py` | `9da365d016949f627520c0928b0c74aabfcd0f789a978316e6f5d902794198cb` |
| `tests/test_s2sp_identity_preserving_update.py` | `75300046180f6449d029de9b74401d22905041f2b65e7d24ef09431b2c303dd6` |

Die Qualifikation verwendet ausschließlich neutrale Eingaben. Sie bindet
Bitstabilität, historische Formel, gemischte Komponenten sowie atomare
Fortschreibung ohne öffentliche Abrufentscheidung.

Die erste Ausführung (`3/4`) bleibt unverändert als Fehlbefund erhalten. Die
unabhängige Korrekturqualifikation
`S2SP-IDENTITY-UPDATE-QUAL-20260919-02` führte ausschließlich die zuvor nicht
erreichte atomare Anschlussprüfung aus. Der native Fast-Zähler heißt
`accepted_exposure_count` und zählt nach drei erfolgreichen Formationen `3`;
die visuelle PPB-Schrittzahl bleibt davon getrennt `2`.
