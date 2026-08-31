# S2-HX - Byte-Block-Runner-Adapterregression

## Status

`S2HX_BYTE_BLOCK_RUNNER_ADAPTER_REGRESSION_VALID`

Qualifikations-ID: `s2hx-byte-block-adapter-20260831-01`

Der private S2-HU-Runner verwendet fuer die reale Q0/Q1-Byte-Block-Fixture nun
die vertraglich vorhandene Property `receptor_values`. Es wurde kein Alias,
Fallback oder toleranter Attributzugriff eingefuehrt.

## Korrektur

Im privaten Runner wurde ausschliesslich der Zugriff
`visual_fixture.values` durch `visual_fixture.receptor_values` ersetzt. Die
bestehende strikte Gleichheitspruefung gegen den vom visuellen Rezeptor
erzeugten 18-Werte-Zustand bleibt erhalten.

Datentyp, Dimension, Bilddigest, AV-Bindung und Eingabedigest werden weiterhin
unveraendert validiert. Speicherkerne, Fixtures, Registry, Recorder,
Verifikator, Budgets und Hauptgate wurden nicht geaendert.

## Einmalausfuehrung

- genau ein Aufruf von `python -m unittest`;
- ein fokussierter Test mit getrennten Q0- und Q1-Unterfaellen;
- Ergebnis: `1/1` bestanden;
- Exit-Code: `0`;
- terminale Ausgabe: `OK`;
- Laufzeit: `0.074s`;
- kein Retry und keine Nachkorrektur;
- alle sechs gebundenen Quellhashes vor und nach dem Lauf identisch;
- Hauptgate vor und nach dem Test: `False`.

## Abgedeckte Grenze

Der Test durchlaeuft fuer die echten Q0- und Q1-Byte-Bilder den privaten
Runnerpfad bis einschliesslich `hs-op-005`. Er bestaetigt, dass der reale
Rezeptor exakt 18 `float`-Werte erzeugt und dass der gebundene
Formationseingang genau diese `receptor_values` erhaelt. Bild-, Werte-, AV- und
Eingabedigests bleiben konsistent; `hs-op-006` wird nicht ausgefuehrt.

Es wurden keine Formation, keine Memory-Geschichte, keine Rollenentscheidung
und keine Konfliktfunktionsauswertung ausgefuehrt.

## Belege

- `reports/s2hx-byte-block-adapter-20260831-01/unittest-output.txt`
- `reports/s2hx-byte-block-adapter-20260831-01/exit-code.txt`
- `reports/s2hx-byte-block-adapter-20260831-01/source-hashes-pre.json`
- `reports/s2hx-byte-block-adapter-20260831-01/source-hashes-post.json`
- `reports/s2hx-byte-block-adapter-20260831-01/qualification.json`

## Aussagegrenze

S2-HX qualifiziert ausschliesslich die korrigierte Byte-Block-Fixturebindung im
Runner. S2-HW bleibt dauerhaft
`S2HW_NOT_EVALUABLE_RUNNER_FIXTURE_ATTRIBUTE_MISMATCH`. Aus S2-HX folgt kein
Memory- oder Konfliktfunktionsbefund.

Ein neuer Hauptlauf benoetigt eine neue Lauf-ID und eine separate Freigabe.
