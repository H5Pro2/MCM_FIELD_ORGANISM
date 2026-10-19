# S2-SP-Slow-Präfixdiagnose

Auftragskennung: `S2SP-SLOW-DIAGNOSTIC-20260919-01`

Technischer Abschluss: `RECORDING_COMPLETE`, unabhängig verifiziert.
Der Lauf umfasst ausschließlich `e01` bis `e06`: vier Formationen, zwei
read-only Hinweise, vier Audio- und sechs visuelle Analysen. Er wiederholt
weder die Konkurrenzfolge noch den vollständigen Memoryvergleich.

| Formation | Fast-Ereignis | Support | Konsolidierung | Visuelle PPB |
| --- | --- | --- | --- | --- |
| e01 | `FAST_CREATED` | `null → 1` | `NOT_ELIGIBLE` | nicht fortgeschrieben |
| e03 | `FAST_UPDATED` | `1 → 2` | `COMMITTED` | `0 → 1` |
| e04 | `FAST_UPDATED` | `2 → 2` | `COMMITTED` | `1 → 2` |
| e05 | `FAST_UPDATED` | `2 → 2` | `COMMITTED` | `2 → 3` |

Bei e06 besteht ein visueller Slow-Kandidat. Der Exaktvergleich und der
private Teilstrukturvergleich liefern dennoch beide `HINT_NOT_APPLICABLE`.
Die gespeicherten PPB-Werte sind gegenüber der Cue nicht bitgleich; die
unveränderte Vergleichsregel rekonstruiert oder glättet sie nicht.

Damit scheitert keine erwartete Fast-/Support-/Konsolidierungskette. Die
frühere Deutung einer leeren Slow-Bank war eine Auswertungsfehlinterpretation:
der historische e06-Scan enthielt denselben Slow-Kandidaten bereits. Der
vorliegende Befund begründet keine Änderung an Memory, PPB, Masken, Schwellen
oder der öffentlichen Abrufentscheidung.

Native Fast-Slotgenerationen stehen im verwendeten Zustand nicht bereit und
sind ausdrücklich als `null` mit `NOT_AVAILABLE_IN_NATIVE_SLOT` dokumentiert;
sie wurden nicht rekonstruiert.
