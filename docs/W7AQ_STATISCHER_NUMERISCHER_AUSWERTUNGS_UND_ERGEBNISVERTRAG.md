# W7-AQ: Statischer numerischer Auswertungs- und Ergebnisvertrag

## Entscheidung

`W7AQ_NUMERICAL_RESOLUTION_EVALUATION_CONTRACT_BOUND`

Vertragsdigest:

```text
66717c7bb1947d44253573a275f326944e5d9aa623389b55162b81a5ea886ee3
```

W7-AQ wurde vor einem realen W7-AP-Zahlenergebnis gebunden. Der Builder
akzeptiert keine Ergebniswerte und kennt keinen zukuenftigen W7-AP-
Ergebnisdigest.

## Erforderliche Provenienz

Eine spaetere Auswertung darf nur ein W7-AP-Ergebnis akzeptieren, das
unmittelbar auf Folgendem beruht:

- kanonischer W7-AN-Containerdigest `4f150aad...f3e5`;
- W7-AO-Vertragsdigest `14455f15...067dc`;
- W7-AP-Kompositor
  `w7ap.raw-r1-r2-r2-r4-resolution-distance-compositor.v1`;
- 35 Rollen, 70 R1/R2- und R2/R4-Distanzen und 105 exakte
  Same-Resolution-Nullkontrollen;
- gebundene kanonische Primaer-/Gegenlaufgleichheit und bestandene
  Reihenfolgekontrolle.

Ein abweichender Digest, eine fehlende Rolle oder eine nicht exakte
Identitaetsnull ist kein numerisches Ergebnis, sondern ein Eingabefehler.

## Einmalige Konvergenzpruefung

Fuer jede der 35 Rollen werden S-Linf und H-Linf getrennt geprueft. Damit
existieren genau 70 Komponentenpruefungen. Eine Komponente besteht nur bei:

```text
D24 < D12
```

oder bei der einzigen exakten Ausnahme:

```text
D12 = 0 und D24 = 0
```

Es gibt keine Mittelung, Rundung, Toleranznull, Pfadauswahl oder Auswertung
des diagnostischen SH-L2. Sobald eine Komponente scheitert, lautet das
einzige Ergebnis `NUMERICALLY_UNRESOLVED`. In diesem Zustand bleiben
`epsilon_num` und `effect_floor` unbelegt.

## Numerischer Boden

Nur wenn alle 70 Komponenten bestehen, gilt:

```text
epsilon_num = Maximum aller 70 R2/R4-S/H-Linf-Distanzen
effect_floor = 10 * epsilon_num
outcome = RESOLUTION_COMPARISON_CONVERGED
```

Dieser positive Zustand besagt ausschliesslich, dass der technische
Aufloesungsvergleich nach der vorregistrierten Regel konvergiert. Er sagt
nicht, dass ein CAP-Effekt funktional, spezifisch oder gegen andere
Mechanismen abgegrenzt ist.

## Gesperrte Funktionsentscheidung

Im aktuellen W7-AN/AP-Container fehlen weiterhin:

`LEAK`, `LIN`, `F3`, `CONST-V`, `SAT`, `MOB`, `NORM`, `ETA0`, `KAPPA0` und
`SIGN`.

Deshalb bleiben `field_function_decision_allowed` und
`memory_claim_allowed` in jedem Ergebnis `false`. Beide zulaessigen
numerischen Ausgaenge sind weder Memory-, Feldzeit-, Organisations-,
Semantik- noch KI-Befunde.

## Verifikation und naechster Schritt

Der schnelle W7-AN/AO/AP/AQ-Verbund besteht mit `62 tests, OK`. W7-AR darf
als naechstes den reinen Einmal-Auswerter fuer ein zukuenftiges echtes
W7-AP-Ergebnis implementieren. Er darf nur die 70 Komponenten pruefen, den
zulaessigen Ergebniszustand bilden und gegebenenfalls den numerischen Boden
berechnen. Er darf weder den langen W7-AN-Lauf starten noch eine
Feldfunktionsentscheidung treffen.
