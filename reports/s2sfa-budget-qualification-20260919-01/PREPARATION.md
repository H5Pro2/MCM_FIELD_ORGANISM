# S2-SFA: Budgetprofil-Vorbindung

**Profil:** `SFA_EVIDENCE_2M_8M_V1`  
**Grenzen:** atomarer Record `2.097.152` Byte, gesamte Belegablage `8.388.608` Byte

Der Record enthält im Erfolg Rezeptorwerte, gefrorenen Zustand und Scores; der
Verifikator rekonstruiert Roh-/Merkmalsfolgen daraus. Die aktuell geschätzte
konservative JSON-Erfolgsform bleibt unter 2 MiB, weil die zuvor zusätzlich
gespeicherten Roh-/Merkmalsfolgen nicht mehr als Pflichtinhalt der
Veröffentlichung gezählt werden. Ein Fehlerrecord enthält nur Phase,
Fortschritt und Primärfehler. Erfolg und Fehler sind Alternativen.

Die Payloadhash-Regel ist `BIND_BEFORE_ANALYSIS`: Für den künftigen, aus Rezept
erzeugten Frame wird sein tatsächlich erzeugter SHA-256 vor `analyze()`
gebunden. Es gibt keinen unabhängig vorversiegelten Sollhash; daher ist dies
keine Prüfung gegen einen solchen Sollwert.

Einziger neutraler Aufruf:

```text
C:\Python314\python.exe -m unittest tests.test_s2sfa_budget_profile
```

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2sfa_private_visual_run.py` | `5c11a53479b3ebca3b96e323df7828395402d72a96651bc262d05030c73b9344` |
| `tests/test_s2sfa_budget_profile.py` | `c95ebd9e6225e5015a794555b9a6d4aa76eef685d56d45371aa8c7ff87e40112` |

Keine Planframes, Rezeptoren, Feld- oder Memoryaufrufe sind Bestandteil dieser
Qualifikation.
