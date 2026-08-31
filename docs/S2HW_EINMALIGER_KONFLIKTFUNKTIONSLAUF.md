# S2-HW - Einmaliger Konfliktfunktionslauf

## Status

`S2HW_NOT_EVALUABLE_RUNNER_FIXTURE_ATTRIBUTE_MISMATCH`

Lauf-ID: `s2hw-role-conflict-20260831-01`

Der einmalig freigegebene Hauptlauf wurde genau einmal gestartet. Er endete
fail-closed bei `hs-op-005` und wurde durch genau eine unabhaengige read-only
Verifikation als technisch konsistenter `NOT_EVALUABLE`-Pfad bestaetigt.

Es gab keinen Retry, keine Teilfortsetzung, keine Parameteraenderung und keine
fachliche Funktionsauswertung.

## Laufbefund

- `run_main_once`-Aufrufe: `1`;
- Verifikatoraufrufe: `1`;
- Prozess-Exit-Code: `0`;
- terminaler Laufstatus: `NOT_EVALUABLE`;
- Fehlercode: `HS-E009`;
- fehlgeschlagene Operation: `hs-op-005` / `RECEPTOR_ANALYZE`;
- aufgezeichnete Ereignisse: `14`;
- verifizierte Belegfehler: keine;
- Gate nach dem Lauf: `False`;
- S2-HU-Quellhashes vor und nach dem Lauf: identisch.

## Ursache

Der visuelle Rezeptor erzeugte den 18-Werte-Zustand. Unmittelbar danach sollte
der Zustand gegen die gebundene Byte-Block-Fixture geprueft werden. Der Runner
verwendet dazu in `tools/_s2hu_private_runner.py` das nicht vorhandene Attribut
`visual_fixture.values`.

Der konkrete Fixture-Typ `ByteBlockVisualFixture` stellt den erwarteten
normalisierten Rezeptorzustand ausschliesslich ueber die Property
`visual_fixture.receptor_values` bereit. Der Attributzugriff erzeugte deshalb
eine nicht registrierte Ausnahme, die korrekt als `HS-E009` weitergereicht und
fail-closed abgeschlossen wurde.

Die Ursache liegt in der privaten Runner-/Fixture-Adapterbindung. Sie ist kein
negativer Befund zu A/B-Konflikt, Rollenadressierung, B4, TSPM-1 oder Memory.

## Aussagegrenze

Keine Formation wurde ausgefuehrt. `A_RECENT` und `B_STABLE` wurden nicht
gebildet. Die vier Rollenfaelle, Verbraucher, Direktbaseline und fachliche
Auswertung wurden nicht erreicht. Aus S2-HW folgt daher kein Funktions- oder
Falsifikationsbefund.

## Belege

- Run: `reports/s2hw-role-conflict/s2hw-role-conflict-20260831-01/`
- Kontrolle: `reports/s2hw-role-conflict/s2hw-control-20260831-01/`
- Journal-SHA-256:
  `78534cf3215c678ec8192adc06b08e4db0972efdc077d65786b2d43b4528de5e`
- Fehlerreceipt-SHA-256:
  `b010846bfe17baf26c2fd9f34bb1dd2085b6fce043ff854d2406eea02ff0c051`
- Terminal-SHA-256:
  `c5df776e8b35023d4a615f345f5fed2f7d0ef35b0612b2da5aa86e48cc7a8d02`

## Weiter

Der naechste Schritt ist eine eng begrenzte Runnerkorrektur von
`visual_fixture.values` auf `visual_fixture.receptor_values`. Danach muss ein
fokussierter neutraler Adaptertest den realen Byte-Block-Rezeptorweg und die
exakte 18-Werte-Gleichheit qualifizieren. Ein neuer Hauptlauf benoetigt eine
neue Lauf-ID und eine separate Freigabe; S2-HW bleibt dauerhaft
`NOT_EVALUABLE`.
