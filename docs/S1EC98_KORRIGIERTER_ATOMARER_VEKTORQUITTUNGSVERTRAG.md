# S1-EC98: Korrigierter atomarer Vektorquittungsvertrag

## Korrektur

EC98 schliesst die in EC97 festgestellte Datenvertragsluecke. Aus 24
geordneten Probequittungen werden genau folgende Daten atomar reduziert:

- aktiver AB-minus-BA-Aktivierungsvektor fuer r2, r4 und r8;
- aktiver AB-minus-BA-Nachhallvektor fuer r2, r4 und r8;
- maximale L-infinity-Kontrollskalare fuer P0, Probe-Rueckwirkungsablation
  und Bildungsablation.

Die einzelnen 24 Rollenvektoren werden nach der Reduktion nicht im
Ergebniscontainer behalten. Alle Verfeinerungen muessen dieselbe
Vektorgeometrie besitzen und jede der acht Rollen exakt einmal liefern.

## Synthetische Abnahme

Eine Nullschritt-Fixture liefert 24 typisierte Eingaben mit drei
Komponenten. Alle sechs erwarteten aktiven Differenzvektoren werden exakt
behalten, waehrend die drei Kontrollmaxima null bleiben. Der Vertrag ruft
weder Feldkern noch EC46-Entscheider auf und persistiert nichts.

EC98 korrigiert nur die kuenftige Rueckgabeform. Die im abgeschlossenen
EC96-Prozess verworfenen Vektoren werden dadurch nicht nachtraeglich
wiederhergestellt. Es besteht kein Memory-, Feldzeit-, Organisations-,
Topologie-, Semantik-, Selbstregulations- oder KI-Nachweis.

Am besten geht es mit S1-EC99 weiter: typisierte, nicht ausfuehrende Adapter
von den bestehenden r2- und r4/r8-Probequittungen auf die 24 EC98-Eingaben
definieren und synthetisch pruefen. Noch keine reale Ausfuehrung und keine
neue Laufautorisierung.
