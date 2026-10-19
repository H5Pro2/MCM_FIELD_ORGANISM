# S2-TS: kanonische Offset- und Anschlussqualifikation

Qualifikations-ID: `S2TS-TEMPORAL-TRACE-RUN-QUAL-20260919-03`.

Die einzige Änderung liegt an der unabhängigen Beleggrenze. `offsets` wird
als geordnete Folge von Integern `0..2` kanonisch in eine Liste überführt.
Weder Reihenfolge noch Anzahl werden verändert.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2ts_temporal_trace_run.py` | `281a074e74a6055883435106d89b44aaf3e262b33c5cace06b0f13990df097e6` |
| `tools/_s2ts_temporal_trace_verification.py` | `78454262237971c8d27cdc4999d026be6125b16c0f0aa4e325de74c5f226bc6d` |
| `tests/test_s2ts_temporal_trace_run.py` | `266155bd3ddce8bf5915c3405a691b72ad649e4b3bf0c6f22563f3afe7604504` |

Der einmalige Aufruf erreicht die vollständige neue Anschlussprüfung:
NU-Planauflösung, 18 Endpunkte, unabhängige Direktverifikation, äquivalente
Tupel-/Listenform sowie abweichende, fehlende, zusätzliche und untypisierte
Offsets. NU-Payloads bleiben im Neutraltest ausgeschlossen.
