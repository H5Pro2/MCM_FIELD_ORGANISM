# S2-SP: fehlgeschlagene Neutralqualifikation

Auftragskennung: `S2SP-IDENTITY-UPDATE-QUAL-20260919-01`

Status: `NOT_QUALIFIED` (`3/4`). Der einmalige Qualifikationsaufruf wurde
ausgeführt; der reale Zwei-Arm-Präfixvergleich wurde nicht gestartet.

Die Prüfungen für Bitstabilität bei identischen Eingängen, die historische
Formel bei abweichenden Eingängen und die komponentenweise Mischbehandlung
bestanden. Die atomare Anschlussprüfung brach vor ihrer Sollprüfung in
`tests/test_s2sp_identity_preserving_update.py` ab: Der Test liest am
`TSPM1FastState` das nicht vorhandene Attribut `accepted_step_count`. Das
native Attribut heißt `accepted_exposure_count`.

Dies ist eine Testbindungslücke. Der Fehler prüft keine Produktabweichung und
liefert keinen Befund über die PPB- oder Memorymechanik. Keine Testkorrektur,
Wiederholung oder reale Präfixausführung wurde aus diesem Fehlbefund abgeleitet.
