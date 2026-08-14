# S1-EC80: In-Memory-r2-Kontrast- und Skalarvertrag

## Zweck

S1-EC80 schliesst die in EC79 bestimmte Messluecke fuer einen kuenftigen
Lauf. Genau acht bereits erzeugte `r2`-Probequittungen werden noch im selben
Prozess auf sechs vorregistrierte Kontraste reduziert. EC80 startet selbst
kein Feld.

## Messraum

Fuer jeden Kontrast wird die L-unendlich-Distanz getrennt fuer
`activation` und `afterimage` gebildet:

1. P0-Reset AB gegen BA;
2. E1 aktiv AB gegen BA;
3. Probe-Rueckwirkungsablation AB gegen BA;
4. Bildungsablation AB gegen BA;
5. AB aktiv gegen AB Probe-Rueckwirkungsablation;
6. BA aktiv gegen BA Probe-Rueckwirkungsablation.

Die Eingangsreihenfolge, alle acht Rollen, Quittungsdigests und der Digest
des Quellergebnisses werden gebunden. Fehlende, doppelte oder umgeordnete
Rollen werden fail-closed abgelehnt.

## Grenzen

- ausschliesslich Reduktion bereits vorhandener In-Memory-Quittungen;
- keine Feld-, Wrapper-, Adapter- oder Koordinatorausfuehrung;
- keine Rohvektorpersistenz;
- keine EC46-Gesamtentscheidung;
- keine Nachparametrierung;
- kein Memory-, Feldzeit-, Organisations-, Topologie-, Semantik-,
  Selbstregulations- oder KI-Claim.

Der synthetische EC63-Nullsatz ergibt reproduzierbar sechs Nullkontraste und
dient nur der technischen Abnahme. Er ist kein Forschungsbefund.

Am besten geht es mit S1-EC81 weiter: gezielte synthetische Nichtnullvektoren
fuer jeden der sechs Kontraste einspeisen und nachweisen, dass EC80 jede
Komponente numerisch korrekt, rollenrein und ablationsgetrennt reduziert.
