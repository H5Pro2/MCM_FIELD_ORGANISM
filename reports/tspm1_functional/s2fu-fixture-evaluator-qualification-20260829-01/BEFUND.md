# Technischer Befund: S2-FU Fixture-/Auswerterqualifikation

## Status

`S2FU_FIXTURE_EVALUATOR_QUALIFICATION_VALID`

Die freigegebene Qualifikation wurde mit der Lauf-ID
`s2fu-fixture-evaluator-qualification-20260829-01` genau einmal ausgefuehrt:

```text
python -m unittest -v tests/test_s2fu_fixture_evaluator_qualification.py
```

Ergebnis: `12/12`, Exit-Code `0`, terminal `OK`. Es gab keine Korrektur,
Wiederholung oder Teilfortsetzung nach dem Lauf. Das vollstaendige, auf
LF-Zeilenenden normalisierte Transkript liegt in `unittest-output.txt`;
`run-metadata.json` bindet Lauf-ID, Exit-Code und Quelldigests.

## Qualifizierter technischer Umfang

Die eine neutrale Testsuite bestaetigt:

- elf literale Muster, 18 Schritte und sechs Probeinputs;
- auditive 4-von-8-Masken mit Mindestabstand `0,25`;
- visuelle Gleichhistogramme mit Mindestabstand `180/765`;
- Zeitfenster, Metadatentrennung und Ressourcenarithmetik
  `11106/8424/972`;
- `S2FU_FUNCTION_CONFIRMED` fuer ein vollstaendiges synthetisches
  Referenz-Bundle;
- `S2FU_FUNCTION_FALSIFIED` bei falscher B4-Folge, fehlendem stabilen
  P1-Slow-Befund, stabil erkanntem P2 und unzulaessiger
  TSPM-Folgenbehauptung;
- konsistent neu berechnete Evidence- und Bundle-Digests fuer alle vier
  funktionalen Negativfaelle;
- `NOT_EVALUABLE` bei Digest-, Quellen-, Tick-, Komponenten-, Ledger- oder
  read-only-Bruch.

## Abgrenzung

Die erzeugten Evidence-Bundles sind ausschliesslich synthetische
Vertragsbelege. Sie sind keine Versuchsergebnisse. Die Tests importierten nur
das private Fixture-Modul und den reinen Auswerter; Speicher-, Rezeptor-,
Koordinator-, Runner- und Dateifunktionen wurden nicht ausgefuehrt.

Der Befund qualifiziert damit ausschliesslich die S2-FU-Fixtures und die
Klassifikationsgrenzen des reinen Auswerters. Er bestaetigt weder die
18-Schritt-Funktion noch einen Memory-Verbund. Runner, Ergebnisablage fuer
einen Hauptlauf und Hauptausfuehrung bleiben gesperrt.
