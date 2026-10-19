# S2-SP-Slow-Diagnose: Übergangsbelegbindung

Auftragskennung: `S2SP-SLOW-DIAGNOSTIC-QUAL-20260919-01`

Die private Formationsergebnisform enthält zusätzlich die bereits atomar
erzeugte `TSPM1TransitionReceipt`. Es wird keine zweite Transition und keine
zusätzliche Fortschreibung ausgelöst.

Der private Diagnosebeleg führt daraus nur: Formationsgeneration vorher/nachher,
ausgewählter Fast-Slot, primäres Fast-Ereignis, Matchstatus, Support vorher/
nachher, Konsolidierungsstatus, visuelle PPB-Aktion, visuelle PPB-Readout- und
Stabilitätsbindung sowie PPB-Schrittzahl vorher/nachher. Eine native
Fast-Slotgeneration existiert nicht; sie ist fest als
`NOT_AVAILABLE_IN_NATIVE_SLOT` und `null` gebunden.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2jw_profiled_memory_coordinator.py` | `ce6155d8a6b98076a414d6f389e921c72f074a5b4016fd82e2efcafa2fe83ef0` |
| `tools/_s2sp_private_memory_compare.py` | `c252a1f6ceb4495866da9174436e2fad56f902ba9dd811787bdfc5c97f6dee7a` |
| `tests/test_s2sp_private_memory_compare.py` | `46afbf2938f24adf5143dfc47cd33f11fa40ba5b4d817518d0454ab879faa977` |
| `reports/run_s2sp_slow_prefix_once.py` | `0210051a208fbd11be5ed5f66e2b52e37b80db5a46110532efba4669dd1beb81` |

Die neue fokussierte Qualifikation prüft unveränderte atomare Formation,
read-only Vergleich, B4-Ersetzung und die neue Receipt-Ableitung. Sie
materialisiert keine gebundene S2-SP-Präfixquelle.

Der spätere Diagnoselauf ist davon getrennt und auf den unveränderten Präfix
`e01` bis `e06` begrenzt: vier Formationen sowie zwei read-only Hinweise. Er
führt keine Konkurrenzfolge und keinen vollständigen S2-SP-Memoryvergleich aus.
