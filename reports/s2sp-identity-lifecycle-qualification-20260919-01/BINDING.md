# S2-SP: Bindung des identitätserhaltenden Lebenszyklusvergleichs

Auftragskennung: `S2SP-IDENTITY-LIFECYCLE-QUAL-20260919-01`

Der spätere Vergleich bindet pro Arm 16 Ereignisse, zwölf Formationen und vier
read-only Hinweise. Beide Arme erhalten dieselben zwölf einmal materialisierten
AV-Paare; getrennt bleiben ausschließlich ihre Zustände und die feste
Updatebindung. Die Folge umfasst Zielstabilisierung, einen tatsächlich
veränderten Konkurrenzinput, Fast-Druck, einen Zielhinweis vor Slow-Ersetzung,
Slow-Ersetzung und einen Zielhinweis danach.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2sp_private_memory_compare.py` | `e4b1ad68df2edfea41f8d33f2135dbd3ef392b0e909da8a1ad4ee3abb44c02f7` |
| `reports/run_s2sp_identity_lifecycle_once.py` | `beeff1b87504be9de682bdbb7d6fbe47bd75ae92cba6ea1d1a7a54f52ec8a002` |
| `tests/test_s2sp_identity_lifecycle.py` | `88671843957a615f96cdf376622e9305ee4a38d52f485e1455b393dde23e07b2` |

Die zusätzliche Qualifikation prüft die gebundene Folgegröße, dieselben
Eingänge für getrennte Arme, Read-only-Hinweise und die begrenzte
Materialisierung. Die bereits qualifizierte PPB-Aktualisierungsformel wird
nicht erneut als vollständige frühere Testserie ausgegeben.
