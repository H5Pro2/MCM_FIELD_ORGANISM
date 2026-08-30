# S2-FZ Funktionsbefund

Lauf-ID: `s2fz-confirmation-20260830-01`

Technische Verifikation:

- `RECORDING_COMPLETE`;
- 103 Operationen;
- 206 Ereignisse;
- Issues `0`.

Kanonische reine Funktionsauswertung:

- Status `S2FU_FUNCTION_CONFIRMED`;
- Method issues `0`;
- Functional findings `0`;
- P2 unstable trace present `true`.

Gemeinsam bestaetigt sind frueher B4-Folgenabruf, finales P1-Slow mit Support
`3` sowie finales Vergessen von P2 bei instabiler Support-`1`-Spur. Alle
Sichten bleiben getrennt und read-only; eine automatische Auswahl existiert
nicht.

Die erste reine Materialisierung ist separat als ungueltig markiert, weil sie
das B4-Ereignisobjekt statt seines kanonischen Feldes `event` uebergab. Es gab
keinen erneuten Hauptlauf, keine erneute Verifikation und keine Aenderung der
aufgezeichneten Belege.

Status:
`S2FZ_LIMITED_ATOMIC_B4_TSPM1_MEMORY_FUNCTION_CONFIRMED`
