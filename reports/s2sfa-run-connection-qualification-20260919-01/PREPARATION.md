# S2-SFA: Vorbereitung der neutralen Laufanschlussqualifikation

**Qualifikations-ID:** `s2sfa-run-connection-qualification-20260919-01`

Einziger Aufruf aus `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`:

```text
C:\Python314\python.exe -m unittest tests.test_s2sfa_visual_run_connection
```

Die zwei neutralen Kontrollen verwenden ausschließlich 32 synthetische
288-Werte-Beobachtungen. Sie rufen weder `materialize_frame()` noch
`LocalChannelGridReceptor.analyze()` auf. Geprüft werden:

1. atomarer Erfolgspfad, unabhängige read-only Verifikation und danach
   getrennte Auswertung;
2. gebrochene Planbindung, `SFA_TRAINING_DEGENERATE`, Fehlerabschluss und
   Auswertungssperre.

Die neun bereits gebundenen Methodenkontrollen werden nicht wiederholt.
Der tatsächliche 32-Frame-Plan bleibt gesperrt.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2sfa_private_visual_method.py` | `0fe16352a5a15bc0cc73acde7f71a8bdfe57156c022d2b4f87404e76a333793d` |
| `tools/_s2sfa_private_visual_run.py` | `ef07b81486501200e2224f25d1cc3215e61fb551c14d24fe3f52a85e8bed9588` |
| `tests/test_s2sfa_visual_run_connection.py` | `b91574dee5949f1f093ca79a100ba7c63d9cd4e006d9be99908d2c8810fd59b` |
| Plan | `5dbe4e446bab5b4fb26ee342a8920ff4704f28dfb1892113dca8f5959b21960f` |

Gemeinsame Recordgrenze: `262.144` Byte. Der Fehlerabschluss speichert Phase,
Fortschritt und Primärfehler; erfolgreiche und fehlerhafte Formen sind
Alternativen.
