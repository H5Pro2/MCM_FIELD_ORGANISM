# S2-TS: vollständige Quellen- und Verifikationsqualifikation

Qualifikations-ID: `S2TS-TEMPORAL-TRACE-RUN-QUAL-20260919-02`.

Die frühere `1/1`-Folgeprüfung und die Spurzustandsdeckung `3/3` werden nur
referenziert. Dieser neue einzelne Aufruf erreicht ausschließlich die zuvor
fehlenden Anschlüsse: NU-Planauflösung, 18 Quellenbelege, gespeicherte
Halbwerte, unabhängige Direktverifikation, Quellen-/Wertmanipulation und
unvollständige Folgen.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2ts_temporal_trace.py` | `64d1e7f9ff54d898996974d960bfb58ac7386165846aeec0ea253079e0a8e6d8` |
| `tools/_s2ts_temporal_trace_run.py` | `281a074e74a6055883435106d89b44aaf3e262b33c5cace06b0f13990df097e6` |
| `tools/_s2ts_temporal_trace_verification.py` | `184eb3e630af2ed3f9e5853d7e5390563dadd6341e8cc76d949276cefce565b5` |
| `tests/test_s2ts_temporal_trace_run.py` | `c4bf147f05580baa93dd664151525c2e44311dc06cfffc7f832b3c132c44285e` |
| NU-Ausführungsplan | `6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10` |

Die gebundene Ergebnisform enthält pro Audioendpunkt Quellen-ID, vorab
geprüften Payloadhash, Rohwertdigest, 48 Halbwerte als Binary64-Hexwerte und
Zeitbindungen. Die Obergrenzen lauten 20 Ereignisse, 18 Analysen, 18
NJ-Projektionen, 0 Feldkontakte, 0 Scans, 98.304 Zustands-, 65.536
Metadaten- und 262.144 Zusatzbytes. Der reale Record wird vor Auswertung
gegen 262.144 Byte geprüft.
