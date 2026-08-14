# S1-FG: Statischer Frischlauf-Einfuegepunkt

## Gefundener Architekturpunkt

Die bestehende Vollformationsarchitektur liefert nach
`consume_prepared_full_formation` ein typisiertes
`E1PreparedFullFormationResult`. Darin liegen r2, r4 und r8 mit jeweils allen
fuenf Formationsergebnissen vor. Erst danach baut die historische Kette den
S1-EC14-Handoff auf; die Probe gehoert zu einem spaeteren, getrennten Pfad.

Der engste zulaessige Einfuegepunkt liegt deshalb zwischen:

1. `execute-full-r2-r4-r8-five-arm-formation`
2. `build-complete-s1ec14-payload-while-states-are-live`

An diesem Punkt koennen die 15 lebenden Arm-Ergebnisse in kanonischer
Verfeinerungs- und Armreihenfolge an S1-FF uebergeben und danach mit S1-FD
diagnostisch ausgewertet werden, bevor Handoff, Persistenz oder Probe beginnen.

## Historische Grenze

S1-EC16 wird nur als statische Architekturreferenz verwendet. Seine alte
Identitaet, Freigabe, Ergebnisse, Attempt-, Lock- oder Reportpfade duerfen
nicht wiederverwendet werden. Ein spaeterer Lauf braucht einen neuen
Laufvertrag, eine neue ausdrueckliche Besitzerfreigabe und erneut bestandene
Ressourcenpruefungen. Persistenz bleibt gesperrt.

## Entscheidung

`INSERTION_POINT_BOUND_FRESH_RUN_CONTRACT_MISSING`

S1-FG fuehrt keine Formation, keinen Capture, keine Probe und keine
Dateioperation aus. Es folgt kein Nachweis von Memory, Feldzeit, Organisation,
Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

Am besten geht es mit S1-FH weiter: einen neuen, nicht persistenten
Formation-Capture-Einmallaufvertrag fuer genau r2/r4/r8 mal fuenf Arme binden.
Der Vertrag muss eine neue Besitzerfreigabe verlangen und die Probe weiterhin
geschlossen halten. Noch keine Ausfuehrung.
