# S2-SFA: Neutrale Laufanschlussqualifikation

**Qualifikations-ID:** `s2sfa-run-connection-qualification-20260919-01`  
**Status:** `2/2 QUALIFIED` für den Anschluss, reale Laufbindung weiterhin gesperrt

Der einmalige repositorygebundene Aufruf

```text
C:\Python314\python.exe -m unittest tests.test_s2sfa_visual_run_connection
```

endete mit Exitcode 0:

```text
Ran 2 tests in 0.060s
OK
```

Bestätigt sind der atomare neutrale Erfolgsweg mit unabhängiger read-only
Verifikation und nachgelagerter Auswertung sowie die Abweisung einer
manipulierten Planbindung. Ein neutraler degenerierter Lernbestand endet mit
`SFA_TRAINING_DEGENERATE`; die Verifikation akzeptiert den Fehlerabschluss,
aber sperrt die Auswertung. Keine 32 Planframes, Rezeptor-, NJ-, Feld- oder
Memoryaufrufe wurden erreicht.

## Aktiver Budgetblocker

Die neutrale Erfolgsfixture enthält kurze Zahlen und ist keine konservative
Obergrenze für den echten Beleg. Der derzeitige Runner speichert im Erfolg
gleichzeitig:

- 32 × 288 Rezeptorwerte,
- 24 × 288 normalisierte Rohwerte für Referenz- und Prüffolgen,
- 24 skalare SFA-Werte,
- 3 × 288 Werte des eingefrorenen Zustands.

Schon eine konservative Reserve von 26 Zeichen je gespeicherten Binär64-Wert
ergibt für diese drei Vektorgruppen mindestens
`(32×288 + 24×288 + 3×288) × 26 = 441.792` Byte, vor JSON-Struktur,
Digests, Scores und Fehlerhülle. Das überschreitet die im Runner gebundene
Recordgrenze von `262.144` Byte. Diese Rechnung ist keine Messung des
Planbestands; sie belegt, dass die aktuelle Erfolgsform nicht vorab gesichert
ist.

Der reale Methodenvergleich ist deshalb weiterhin **nicht ausführungsbereit**.
Eine spätere Korrektur müsste die verlustfreie, vom Verifikator auflösbare
Erfolgsform und ihre vollständige Bilanz separat entscheiden. Keine
Budgeterhöhung, keine Kürzung und keine Materialisierung sind durch diesen
Befund freigegeben.
