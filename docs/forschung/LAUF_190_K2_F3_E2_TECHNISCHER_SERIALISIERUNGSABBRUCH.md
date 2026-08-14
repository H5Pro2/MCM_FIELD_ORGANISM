# Lauf 190

## Auftrag

Ausgefuehrt werden sollte der unveraenderte Vertrag aus
`docs/K2_F3_E2_GEOMETRISCHE_M_KAUSALITAET_VORREGISTRIERUNG.md`.

## Beobachteter technischer Abbruch

Quellen- und Geometrie-Gates wurden passiert und die Armrechnung erreichte
die Ergebnisbildung. Beim anschliessenden JSON-Schreiben brach der Prozess
jedoch ab:

```text
TypeError: Object of type bool is not JSON serializable
context: controls
```

Ursache auf Codeebene ist ein `numpy.bool_` aus einer Observerkontrolle. Der
Wert wurde von `dataclasses.asdict()` erhalten, vom Standard-JSON-Encoder
aber nicht als natives Python-`bool` akzeptiert.

## Evidenzgrenze

- `reports/mcm_f3_geometry_lauf_190.json` wurde nicht erzeugt.
- Es wurden keine Messwerte persistent uebernommen.
- Aus der Tatsache, dass die Rechnung bis zur Serialisierung gelangte, wird
  kein E2-Befund abgeleitet.
- Geometrie, Masken, F3-Parameter, Geschichten, Probe und wissenschaftliche
  Entscheidungskriterien werden nicht geaendert.

## Entscheidung

```text
decision: TECHNICALLY_UNDECIDABLE
E2 claim: none
```

## Kleinste Korrektur

Zulaessig ist nur, Observerkontrollwerte vor dem Ergebnisobjekt explizit mit
`bool(value)` in native Python-Boolwerte zu ueberfuehren und diese
Serialisierbarkeit technisch zu testen. Der fachlich unveraenderte Vertrag
kann danach unter der neuen Laufnummer 191 genau einmal ausgefuehrt werden.
