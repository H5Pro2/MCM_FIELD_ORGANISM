# S1-EC35: Statischer P0-Identifizierbarkeitsaudit

## Zweck

S1-EC35 untersucht ohne Feldlauf und ohne Zugriff auf ein persistiertes
EC34-Ergebnis, ob das EC34-Schema die Groesse eines P0-Unterschieds
quantitativ bestimmen kann.

## Statische Ursache

Bei n1 sind die wiederholte und kontinuierliche Zeitlage identisch. Bei n2
sind die Zeitlagen verschieden, obwohl AV-Werte, Gesamtexposition,
Kontaktintegrale und letzter Kontaktabschluss uebereinstimmen.

Ein dynamisches Feld gewichtet Kontakte anhand ihrer Zeitlage. Gleiche
Exposition und gleicher Abschluss implizieren deshalb nicht automatisch
einen bit-identischen terminalen Feldzustand.

## Messluecke

Der EC34-Armcontainer behaelt fuer P0 nur einen Ausgabedigest. Der
Kontrastcontainer behaelt lediglich die boolesche Digest-Gleichheit. Nicht
enthalten sind:

- terminale P0-Aktivierungs-Linf-Distanz,
- terminale P0-Nachhall-Linf-Distanz,
- komponentenweise r2/r4/r8-P0-Reste.

Eine Digest-Ungleichheit zeigt nur, dass mindestens ein serialisierter Wert
abweicht. Sie zeigt weder Groesse noch numerische Robustheit der Abweichung.

## Entscheidung

```text
P0_MAGNITUDE_NOT_IDENTIFIABLE_FROM_EC34_SCHEMA
```

Audit-Digest:
`9423c4425de44ceb311c7600f0fcf2d57d2100831b2603a812a307a6ff0e290b`

Das ist kein Memory-, Praegungs- oder Wiederholungsbefund. Es wurde kein
neuer Feldlauf ausgefuehrt und kein EC34-Rohresultat gespeichert.

## Naechster Schritt

S1-EC36 darf nur das Ergebnisschema und den In-Memory-Runner um die drei
fehlenden quantitativen P0-Messrollen erweitern und synthetisch pruefen. Ein
erneuter n1/n2-Feldlauf bleibt gesperrt und benoetigt eine neue ausdrueckliche
Freigabe.

