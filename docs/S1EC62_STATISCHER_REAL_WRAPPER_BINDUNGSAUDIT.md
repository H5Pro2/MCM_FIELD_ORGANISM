# S1-EC62: Statischer Real-Wrapper-Bindungsaudit

## Zweck

S1-EC62 prueft, ob die drei injizierten EC61-Schnittstellen ohne
Zwischenschritt an die realen EC54-Wrapper gebunden werden koennen. Der Audit
untersucht nur Signaturen, Ausgabefelder und Typinvarianten. Kein Koordinator,
Wrapper oder Feldkern wird aufgerufen.

## Kompatibilitaetsbefund

Die Aufrufsignaturen passen strukturell:

- Bildung: aufgeloester Slot, Ausgangsfeld, Ausgangszustand
- Fresh Field: Slot-Binding, Ausgangsfeld
- Probe: aufgeloester Slot, Fresh Field, optionaler eingefrorener Zustand

Das EC54-Fresh-Field-Ergebnis ist bereits direkt mit EC61 kompatibel. Die
realen Bildungs- und Probeausgaben enthalten ebenfalls alle benoetigten
Zustaende, Beobachtungen, Digests und Schrittzahlen.

Die Bindung scheitert jedoch an einer beabsichtigten EC61-Fixturegrenze:

- `E1CoordinatorFormationReceipt` akzeptiert nur `0` Feldschritte.
- `E1CoordinatorProbeReceipt` akzeptiert nur `0` Feldschritte.
- Das EC61-Gesamtergebnis akzeptiert nur `0` Feldschritte.

Reale EC54-Ausgaben wuerden positive Schrittzahlen tragen und deshalb von
den EC61-Typen abgelehnt. Eine direkte Bindung waere damit technisch
unehrlich oder wuerde reale Schrittzahlen verwerfen.

Entscheidung:

`KORREKTUR_POSITIVE_STEP_RECEIPTS_MISSING`

Audit-Digest:

`77137cc066c0c7f41ed5b95e2f5ae2da502bdb824f0a36f6fc6f4a124b61140c`

## Grenze

**STOPP fuer die reale Wrapperbindung und Ausfuehrung.** Die
Orchestrierungslogik aus EC61 bleibt gueltig; es fehlt ein getrennter,
positiver-Schritt-faehiger Ergebnisvertrag. Dies ist eine korrigierbare
Implementierungsluecke und keine wissenschaftliche Sackgasse.

Am besten geht es mit S1-EC63 weiter: getrennte Real-Receipt-Typen fuer vier
Bildungsoutputs, acht Probeoutputs und das auf exakt 1.608/1.600/3.208
Schritte begrenzte Gesamtergebnis definieren. Diese Typen werden nur mit
synthetischen positiven Schrittwerten abgenommen; reale Wrapper bleiben
weiterhin unaufgerufen.
