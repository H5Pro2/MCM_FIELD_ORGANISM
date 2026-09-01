# S2-IV: Fuenf-Status-Funktionslauf

S2-IV fuehrte den einmalig freigegebenen realen Lauf mit sechs Memory-Geschichten,
38 Formationen und acht Kontextstatusfaellen aus. Die Aufzeichnung ist mit
`183/366`, unveraenderten Quellen und fehlerfreier unabhaengiger Verifikation
technisch vollstaendig.

Die vollstaendige Funktionsprognose wurde fuer die gebundenen Geschichten nicht
bestaetigt. Sechs von acht Faellen trafen die vorab festgelegte Erwartung. In
`c01` waren A und B vorhanden, aber nur A war auf die Signalprobe anwendbar; das
Ergebnis war `SINGLE_SOURCE` statt `CONSISTENT`. In `c05` war nur B vorhanden,
aber nicht anwendbar; das Ergebnis war `NO_APPLICABLE_CONTEXT` statt
`SINGLE_SOURCE`.

Die Konflikt-Spiegelungen, ein A-seitiger Einzelquellenfall, `NO_CONTEXT` und
beide `NO_APPLICABLE_CONTEXT`-Kontrollen wurden bestaetigt. Signalgeber und
unabhaengige Direktbaseline stimmten in allen acht Faellen ueberein. Alle
Signalproben blieben read-only.

Der Befund lautet daher
`S2IE_REAL_TWO_AREA_STATUS_FUNCTION_FALSIFIED`. Er ist eine auswertbare
funktionale Falsifikation der konkreten Fuenf-Status-Prognose und kein technischer
Abbruch. Er beweist weder automatische Kontextwahl noch eine besondere
MCM-Physik und widerlegt nicht die bereits bestaetigten begrenzten
Memory-Funktionen.
