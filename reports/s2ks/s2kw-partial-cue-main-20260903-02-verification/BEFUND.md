# S2-KW realer Teilhinweisabruf

Lauf-ID: `s2ks-real-partial-cue-336-20260903-02`

Technischer Status: `RECORDING_COMPLETE`

Funktionsstatus: `S2KS_FUNCTION_CONFIRMED`

Der genau einmal ausgefuehrte Hauptlauf erzeugte fuenf frische
Memorygeschichten mit insgesamt 59 Formationen, einen frischen Nullzustand
und acht strikt spaetere okkludierte visuelle Teilhinweise. Es wurde keine
Vollprobe ausgefuehrt. Das Hauptgate war vor dem Aufruf `False` und nach dem
Aufruf wieder `False`.

Die genau einmal ausgefuehrte unabhaengige read-only Verifikation meldete
`RECORDING_COMPLETE`, keine Issues und den Record-Digest
`40335dd87af38840d4a1aea84e92d1f025b8e34722c4d33de325fbe1df7ea340`.

## Funktionsbefunde

| Fall | A_RECENT | B_STABLE | Entscheidung |
| --- | --- | --- | --- |
| K1 | anwendbar | nicht anwendbar | A_RECENT zugelassen |
| K2 | nicht anwendbar | anwendbar | B_STABLE zugelassen |
| K3 | anwendbar | anwendbar | A/B-Mehrdeutigkeit, Enthaltung |
| K4 | intern mehrdeutig | gueltig abwesend | Enthaltung |
| K5 | interner B4/Fast-Konflikt | nicht anwendbar | Enthaltung |
| K6 | nicht anwendbar | intern mehrdeutig | Enthaltung |
| K7 | gueltig abwesend | gueltig abwesend | kein Kontext, Enthaltung |
| K8 | nicht anwendbar | nicht anwendbar | kein anwendbarer Kontext |

Alle acht S2-KQ-Ergebnisse stimmen mit der unabhaengigen Direktbaseline
ueberein. K1 und K2 binden zudem exakt die erwarteten 256 maskierten
Zielwerte. Jeder Arm scannte alle 16 Slots; die groesste tatsaechliche Zahl
von Wertvergleichen war `704` und blieb unter der Grenze `800`. Alle
Vor-/Nachzustandsdigests sind identisch. Rohpayloads wurden nicht behalten.

Der Befund bestaetigt einen begrenzten realen Teilhinweisabruf aus
unvollstaendiger visueller Wahrnehmung sowie kontrollierte Enthaltung. Die
Funktion bleibt durch einen generischen vollstaendigen Slotscan erklaert; sie
belegt weder automatische Kontextfuellung noch Feldwirkung oder eine neue
Memorymechanik.
