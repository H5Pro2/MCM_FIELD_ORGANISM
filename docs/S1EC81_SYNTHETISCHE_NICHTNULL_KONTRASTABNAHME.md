# S1-EC81: Synthetische Nichtnull-Kontrastabnahme

## Zweck

S1-EC81 prueft die EC80-Reduktion mit acht festen synthetischen
Rollenvektoren. Anders als der Nullsatz aus EC80 besitzt jeder der sechs
Kontraste eine vorab bekannte Nichtnullsignatur fuer `activation` und
`afterimage`.

## Erwartetes Profil

1. P0-Reset-Ordnung: `(1, 2)`;
2. aktive E1-Ordnung: `(3, 4)`;
3. Probe-Rueckwirkungsablationsordnung: `(4, 5)`;
4. Bildungsablationsordnung: `(5, 6)`;
5. AB aktiv gegen Probe-Rueckwirkungsablation: `(5, 5)`;
6. BA aktiv gegen Probe-Rueckwirkungsablation: `(6, 6)`.

EC80 gibt dieses Profil exakt und deterministisch zurueck. Damit sind
Rollenpaarung, Komponentenbehandlung und L-unendlich-Reduktion fuer den
synthetischen Pruefraum technisch abgenommen.

## Grenzen

Die Werte wurden absichtlich eingesetzt. Sie sind kein Feldbefund und keine
Baseline fuer einen spaeteren Realwert. EC81 fuehrt keine Feldschritte aus,
persistiert nichts und trifft keine EC46- oder Forschungsentscheidung. Es
gibt keinen Memory-, Feldzeit-, Organisations-, Topologie-, Semantik-,
Selbstregulations- oder KI-Nachweis.

Am besten geht es mit S1-EC82 weiter: einen statischen In-Memory-Handoff vom
EC67-Koordinatorergebnis an EC80 definieren. Er muss die acht realen
Probequittungen direkt nach der Rueckgabe reduzieren, bevor das
nicht persistente Ergebnisobjekt den Prozess verlaesst, darf aber noch keine
neue Ausfuehrung autorisieren.
