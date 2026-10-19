# S2-SP-Memoryvergleich: Neuqualifikation

Auftragskennung: `S2SP-MEMORY-COMPARE-QUAL-20260919-02`

Die einzige Korrektur ersetzt in `Sources.formation()` den nicht vorhandenen
Attributzugriff `visual.frame.values` durch die native unveränderte
Rezeptorausgabe `visual.channel_values`. Ein statischer Zugriffsaudit des neuen
S2-SP-Anschlusses zeigt keine weitere Verwendung von `VisualReceptorState.frame`.

Die drei ursprünglichen Prüfgruppen bleiben vollständig: echter atomarer
Formationseingang mit read-only Versatzhinweis, Abweisung einer fremden
Innenstruktur und Nichtverfügbarkeit der ursprünglichen B4-Kandidatenbindung
nach Ersetzung. Zusätzlich prüft jede Formation die Gleichheit zwischen dem
zurückgegebenen nativen Vektor und `pair.visual.timed_frame.frame.values`.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2sp_private_memory_compare.py` | `2c8061c27bc246b5f3d906a9f9e1c0316da0995b817ff7e64fec454e35cfc758` |
| `tests/test_s2sp_private_memory_compare.py` | `e4d05cb1a3927c787a9250dbd7e9248c2f8d63bb3fc32e616759ac8d308acb70` |

Der frühere Aufruf `…-01` bleibt unverändert `NOT_QUALIFIED`.
