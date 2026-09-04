# S2-LQ Rollenfreier Mehrmusterlauf 20260904-02

Lauf-ID: `s2lq-role-free-multipattern-20260904-02`

Technischer Status: `RECORDING_COMPLETE`

Funktionsstatus: `S2LQ_MULTIPATTERN_STREAM_CONFIRMED`

Der Hauptaufruf wurde genau einmal ausgefuehrt. Der atomare Ergebnisbeleg
enthaelt 29 Ereignisse, davon 21 Formationen sowie vier auditive und vier
visuelle Teilhinweise. Die unabhaengige read-only Verifikation wurde danach
genau einmal ausgefuehrt und meldete `RECORDING_COMPLETE`.

In beiden Slow-Banken erreichten p00 und p01 Support `3`. p02 erreichte
Support `2` und blieb damit instabil. Fuer p03 entstand kein eigener
Slow-Slot. Alle vier Inhalte waren am Ende aus `A_RECENT` verschwunden; B4
enthielt die Formationsindizes 13 bis 21.

Alle acht Scanentscheidungen entsprachen der Vorbindung und waren mit der
jeweiligen unabhaengigen Direktbaseline identisch. Die auditive p03-nach-p00-
Verwechslung wurde ausdruecklich als
`SENSOR_CONFUSION_WITH_EXISTING_STABLE_CONTENT` klassifiziert, nicht als
eigene Verdichtung von p03.

Alle Teilhinweiszugriffe waren read-only. Es gab keinen Retry und keine
Parameter-, Fixture-, Schwellen- oder Quellcodeaenderung. Die gebundenen
Quellhashes waren vor und nach dem Lauf identisch; das Gate war danach
`False`. Der fruehere Lauf `s2lq-role-free-multipattern-20260904-01` bleibt
unveraendert `NOT_EVALUABLE`.

Ergebnisdatei: `result.json`

Ergebnis-SHA-256:
`b1f871135f9a9b1c7d37ac7407fb5731d62410b66ada5c86b918ba8ae59accc3`
