# W7-BK: CONST-V-AB/BA-R4-Executor

## Zweck

W7-BK setzt die letzte technische Aufloesung vor der Konvergenzauswertung um.
AB/R4 und BA/R4 werden aus dem bestehenden privaten CONST-V-Kern erzeugt.

## Ablauf

Die R4-Rollen werden in der Reihenfolge `AB/R4`, danach `BA/R4` erzeugt. Jede
Richtung umfasst fuenf Hauptproduktionen und fuenf isolierte Checkpointproben
mit je 91 rohen S/H/Skalar-Samples. Die R2-Rollenidentitaeten bleiben als
Vorgeschichte gebunden.

## Evidenzgrenze

W7-BK berechnet noch keine der 70 R2/R4-Distanzen. Es erzeugt kein Epsilon,
keinen Effektboden und kein Profil. Das Ergebnis ist rein technisch und kein
Memory- oder Feldfunktionsbefund.

## Naechster Anschluss

Technischer Befund: AB/R4-Digest `09cc1f20...8e9e`, BA/R4-Digest
`7496f414...faa`, terminaler Digest `9215994d...d551`. Die Ausfuehrung
umfasst nur zwei der sieben geplanten Pfade. W7-BL muss daher zuerst die
fehlenden sechs Pfade in R1/R2/R4 binden; erst danach ist die getrennte
numerische Konvergenzpruefung zulaessig.
