# S2-FX Auswertungsbefund

- Lauf-ID: `s2fx-main-20260830-01`
- Hauptaufrufe: genau 1
- technischer Laufabschluss: Exit-Code `0`
- unabhaengige Verifikationen: genau 1
- Verifikation: `RECORDING_COMPLETE`, `103/206`, Issues `0`
- Aufruf von `evaluate_s2fu`: `0`
- Auswertungsmaterialisierung: fail-closed gestoppt

Status:

`S2FX_FUNCTION_EVALUATION_NOT_EVALUABLE_EVIDENCE_CONTRADICTION`

Der Formationsbeleg meldet visuellen P1-Support ab Schritt 8 als `0`, waehrend
der gespeicherte visuelle PPB-1-Zustand und der finale read-only Befund einen
stabilen P1-Slot mit Support `3` enthalten. Der Widerspruch entsteht durch
exakte Float-Tupelgleichheit im Support-Beleghelfer nach Prototypmittelung.

Es erfolgten keine Wiederholung, Nachkorrektur, Parameteranpassung oder
positive Gesamtwertung. Die deskriptiven Rohbelege zeigen fruehen B4-
Folgenabruf, finales Fehlen von P1/P2 aus B4 und Fast, P1-Slow-Support `3`,
P2-Slow-Support `1` und unveraenderte Probevor-/nachzustaende. Diese
Einzelbefunde ersetzen keine gueltige Funktionsauswertung.
