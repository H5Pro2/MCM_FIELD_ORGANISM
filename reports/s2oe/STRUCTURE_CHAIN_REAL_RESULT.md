# Direkte PPB-Kette: Ergebnis

`structure-location-chain-20260912-01`: einmal RECORDING_COMPLETE,
einmal EVIDENCE_VALID, danach einmal DESCRIPTIVE_ONLY-Auswertung.
Keine Wiederholung der 19 Tests. Gespeicherte Quellenwerte wiederverwendet.

| Folge | Schritt 1 | Schritt 2 | Schritt 3 |
| --- | --- | --- | --- |
| q04/q05/q06 | CREATE 000, S1 | MATCH 000, S2 | MATCH 000, S3 stabil |
| q01/q02/q03 | CREATE 000, S1 | CREATE 001, S1 | MATCH 000, S2 |
| q01/q03/q04 | CREATE 000, S1 | MATCH 000, S2 | CREATE 001, S1 |

Generation bleibt bei MATCH erhalten. Prototypupdates sind gespeichert und
unabhängig geprüft. Keine Ankerentscheidung am dritten Eingang verändert:
K1 bleibt passend (Distanz leicht verändert), K2 bleibt passend (Anker zuvor
nicht aktualisiert), K3 bleibt ausgeschlossen trotz kleinerer Distanz.
Alle Kandidatenterme, Zustände und Generationen stehen in record.json;
Original-/Aktualabstände in evaluation.json desselben Laufverzeichnisses.

Neun Übergänge; 2.016 produktive, 4.032 diagnostische und 2.016 unabhängige
Differenzen. Abschlussledger 1.778.341 Byte einschließlich Reserven,
keine Verletzung. Kein Nachsättigungsupdate, Ersatz- oder Gesamtsystemnachweis.
Keine Rezeptor-/Feldaufrufe. Gate zurückgesetzt; Freigabe verbraucht.
