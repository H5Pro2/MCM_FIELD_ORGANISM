# S2TV-MEDIA-SAMPLING-QUAL-20260919-01

Status vor Aufruf: gebunden, nicht ausgeführt. Dies ist eine einmalige
neutrale Anschlussqualifikation, keine Medienanalyse.

| Datei | SHA-256 | Byte |
| --- | --- | ---: |
| `tools/_s2tv_sampled_media_adapter.py` | `ee08ce2fb9339e090aee2c8a98e5875f6d3112d0decc6869a67d56163f21319d` | 5.446 |
| `tests/test_s2tv_sampled_media_adapter.py` | `cd200c881a0e7f8cba0b2537c037c67215b04190bb710d61e1f0490b14bf89fc` | 2.287 |
| `docs/S2TV_MEDIENZEIT_AUSWAHLANSCHLUSS.md` | `45d5d9a1b763154ee63b1af353ce52b1cbbb20da7a486868d7cb7960b53e2ad8` | 2.293 |

Der eine Aufruf umfasst drei neue Prüfgruppen: feste 24-Ereignis-/20-
Formationsbilanz, PTS- und `30000/1001`-Bindung sowie `open`/`next`/`status`/
`stop` mit Reihenfolge- und Neustartabwehr. Er nutzt ausschließlich synthetische
PTS-Receipts; weder die ausgewählte YouTube-Quelle noch andere Payloads werden
geöffnet oder ausgewertet.
