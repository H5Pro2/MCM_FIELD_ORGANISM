# S1AO: C_i-Parameter- und Zeitschritt-Robustheit

## Status

Technischer Robustheitsabgleich der aktuellen C_i-Baseline im kontrollierten
synthetischen Audio-/Video-Testfeld. Dieser Lauf ist kein Memory-, Lern- oder
Organismusnachweis.

## Fragestellung

Bleibt die gekoppelte technische C_i-Akkommodation bei mehreren zulaessigen
Parametern und Zeitschritten endlich und reproduzierbar? Geprueft wurden die
beiden bereits definierten Holdout-Welten `history.same` und
`history.changed`.

## Durchfuehrung

Verwendet wurden ausschliesslich:

- `controlled_history_holdout_world_family()`;
- die bestehende neutrale Audio-/Video-Feldpipeline;
- `C_i` mit `dC_i/dt = alpha * (1-C_i^2) * (E_i-C_i)`;
- die technische Rueckwirkung als Projektion auf den naechsten Feldzustand;
- keine Kamera, kein Mikrofon und keine externe Datenquelle.

Gepruefte Paare `(alpha, dt)`:

```text
(0.25, 0.05), (0.50, 0.10), (1.00, 0.10), (1.00, 0.20), (2.00, 0.10)
```

Alle Paare erfuellen die aktuelle Schrittgrenze `alpha * dt <= 0.25`.

## Ergebnisse

Die Digest-Praefixe, der maximale Betrag der technischen Feldaktivierung und
der maximale Betrag von C_i waren:

```text
alpha dt   same digest    same max activation  same max C_i  changed digest  changed max activation  changed max C_i
0.25  0.05  c1296451d8cc  0.232005011          0.007533243   68b9588b5e74   0.273742764            0.007117267
0.50  0.10  c1ea0c7a3247  0.229979622          0.028337045   186b5b666937   0.271234863            0.027445317
1.00  0.10  03034c16fbe6  0.227546887          0.052170023   fb0432a87f9d   0.268009195            0.052244374
1.00  0.20  5d0af4a71f18  0.223454112          0.088224592   52e4f8a9aaad   0.261928497            0.094484434
2.00  0.10  5d0af4a71f18  0.223454112          0.088224592   52e4f8a9aaad   0.261928497            0.094484434
```

## Einordnung

1. Die Baseline blieb in allen geprueften Faellen numerisch beschraenkt.
2. Unterschiedliche Parameter veraendern den technischen Verlauf und damit
   den Digest; die World-Trennung bleibt sichtbar.
3. Gleiche Produkte `alpha*dt` liefern hier denselben Verlauf. `alpha` und
   `dt` sind deshalb in dieser Minimalgleichung nicht unabhaengig identifiziert.
4. Die wachsende C_i-Amplitude bei groesserem `alpha*dt` ist ein
   Stabilitaets-/Kalibrierungsthema, keine nachgewiesene Prägung oder Memory.

## Grenze und naechster Schritt

Damit ist nur die technische Integrationsform belastbarer eingegrenzt. Es ist
noch nicht gezeigt, dass C_i eine unabhaengige, wiederverwendbare oder
vergessende Memorystruktur bildet. Der naechste zulassige Schritt ist ein
kleiner kontrollierter Reiz-Gap-Reiz-Vergleich mit identischer Feldbaseline,
bei dem ausschliesslich geprueft wird, ob der C_i-Zustand nach einer Luecke
eine messbare, reproduzierbare Abweichung im zweiten Reiz hinterlaesst. Die
Auswertung muss gegen den unveraenderten P0-Arm und gegen einen leaky
Integrator erfolgen.
