# S2-IU Ergebnis

Qualifikations-ID: `s2iu-joint-qualification-20260901-01`

Status: `S2IU_CURRENT_SIGNAL_AND_RUN_SHELL_QUALIFICATION_VALID`

- Ein vorregistrierter `unittest`-Aufruf.
- `42/42` Tests bestanden, Exit-Code `0`, terminales `OK`.
- `14/14` aktuelle S2-IC-Status- und Fehlerpruefungen bestanden.
- `20/20` Bootstrap-, ParentSetV1-, Recorder- und Verifikatorpruefungen bestanden.
- `8/8` neue ID-, Receipt- und Offline-Rekonstruktionspruefungen bestanden.
- Alle `154` Invocation-/Owner-IDs und `183` Operations-IDs waren gueltig und eindeutig.
- Alle acht Signal-/Baseline-Aufrufpaare wurden neutral erreicht.
- Receiptgrenzen `1.299` und `1.999` Byte sowie Registry `183/366` und Budgets `1.037.466/1.044.634` blieben gebunden.
- Fehlende, vertauschte, fremde und manipulierte Rekonstruktionsfelder wurden getrennt fail-closed verworfen.
- Produkt- und Testquellhashes waren vor und nach dem Lauf identisch.
- `MAIN_EXECUTION_ENABLED` blieb `False`.
- S2-IQ bleibt unveraendert `NOT_EVALUABLE`.

Der Befund qualifiziert ausschliesslich die aktuelle Signallogik und Laufhuelle. Es wurden keine realen Memory-Geschichten ausgefuehrt; ein neuer Fuenf-Status-Hauptlauf bleibt separat freizugeben.
