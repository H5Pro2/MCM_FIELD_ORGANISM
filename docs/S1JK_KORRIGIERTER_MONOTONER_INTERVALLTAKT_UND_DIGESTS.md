# S1-JK: Korrigierter monotoner Intervalltakt und Digests

## Ergebnis

S1-JK ersetzt den nicht fortschreitenden S1-JH-Zeitplan durch einen endlichen
sequenzrelativen Takt. Alle zeitabhaengigen Sequenz-, Intervall- und
Carry-Digests sind neu registriert. Es wird weiterhin keine Huelle
materialisiert und kein Modell ausgefuehrt.

## Zeitplan

Jede unabhaengige Sequenz beginnt mit einem frischen Modellzustand bei Tick 0.
Bei `2 ticks/s` gelten ordinalabhaengig:

- Intervall 1: `0..1`, Dauer `0.5`,
- Intervall 2: `1..2`, Dauer `0.5`,
- Intervall 3: `2..3`, Dauer `0.5`,
- Intervall 4: `3..4`, Dauer `0.5`.

Innerhalb einer Sequenz entspricht jeder Starttick exakt dem vorherigen
Endtick. Jeder Endtick steigt strikt. Eine neue unabhaengige Sequenz darf mit
ihrem frischen Modellzustand wieder bei 0 beginnen. DTS-1 und B1 bis B6
erhalten fuer dasselbe Ordinal wertgleich dasselbe Zeitfenster; ein separates
Ordinallabel bleibt aus der Modellsicht ausgeschlossen.

Private Refinementsubschritte teilen nur das jeweilige physische
Gesamtintervall. Sie duerfen dessen Dauer oder aeussere Grenzen nicht
veraendern.

## Digestkorrektur

Der neue Sequenzdigest bindet:

- internen Sequenzschluessel, Profilblock und Geometrie-Digest,
- die vollstaendige Ereignisreihenfolge,
- Direktive und Quellfixture beziehungsweise symbolischen Carry-Verweis,
- Kontakt-Digest, konkretes Zeitfenster und Checkpointregel jedes Ereignisses.

Der Intervalldigest bindet wie in S1-JG alle neun vorherigen Huellenfelder.
Bei P_IE verweist die zweite Huelle konkret auf den neu berechneten Digest der
unmittelbar vorherigen Huelle. Ergebniswerte, Modelloutputs,
Refinementresiduen und spaetere Zustaende gehen in keinen vorregistrierten
Digest ein.

Alle sieben Sequenzdigests und alle 23 Intervalldigests sind eindeutig und
unterscheiden sich von den ersetzten S1-JH-Digests.

## Unveraenderte Bindungen

Bitgleich erhalten bleiben:

- Zwei- und Dreiknotengeometrien,
- P_IE-Anfangszustand sowie P_IH-, P_IK- und P_IN-Grenzwerte,
- geometriebreite Nullkontakte und Kontaktfixtures,
- kandidatenseitige Sidecars,
- Refinementstufen, Aufrufbudgets und Quarantaeneregeln,
- die Informationsgrenze und alle 24 blockierten Baselinefallidentitaeten.

## Entscheidung

`CORRECTED_MONOTONIC_COMMON_INTERVAL_TIMES_AND_DIGESTS_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`64ca5b895146fef453eb27945a1074f5d2b8e4c8834a94cc6f9b0a855a61824f`

S1-JK zeigt noch keine Materialisierbarkeit, numerische Zulaessigkeit,
Baselinepassung oder Kandidatenueberlegenheit. Speicher-, Lern- und KI-Claims
bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JL darf ausschliesslich den korrigierten statischen
Materialisierungsschemavertrag aus S1-JI auf Grundlage des neuen S1-JK-
Zeitplans binden: vollstaendige Rezeptor-/Dockidentitaeten, reine Feld-/Carry-
API, kanonische Wertpayloads und Digests sowie atomare Fail-Closed-Regeln.
Noch keine Implementierung, kein Adapter- oder Modellaufruf, keine Runtime und
keine Forschungsprobe.
