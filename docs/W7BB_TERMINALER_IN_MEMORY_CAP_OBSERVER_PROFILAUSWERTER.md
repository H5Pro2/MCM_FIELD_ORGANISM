# W7-BB: Terminaler In-Memory-CAP-Observer-Profilauswerter

## Entscheidung

`TERMINAL_DIMENSIONLESS_PROFILE_EVALUATOR_IMPLEMENTED`

W7-BB implementiert den W7-BA-Vertrag als privaten Einmal-Auswerter. Er
vergleicht ausschliesslich vorhandene dimensionslose W7-AX- und W7-AZ-
Profile. Erfolg und Fehler sperren denselben Auswerter terminal.

## Auswertung

Wenn ein Profil nicht aufgeloest ist, endet die Auswertung mit
`NOT_RESOLVED` ohne Distanzen. Andernfalls entstehen fuer LEAK, SAT und NORM
je ein AB- und BA-Linf-Abstand ueber 15 Profilkoordinaten. Das Maximum beider
Richtungen wird gegen `0.05` geprueft. Bei mehreren Treffern gilt
`LEAK > SAT > NORM`.

Der Auswerter persistiert nichts, schreibt nichts zur Runtime zurueck und
liefert nur eine Observer-Erklaerungsklasse. Feldfunktion und Memory bleiben
unabhaengig vom Ergebnis gesperrt.

## Kanonisches Ergebnis

Die einmalige kanonische In-Memory-Auswertung liefert:

```text
outcome = PROFILE_NOT_MATCHED
LEAK  AB = 0.37376973451226625
LEAK  BA = 0.5020091546372206
SAT   AB = 0.3728441556612728
SAT   BA = 0.5006989248287649
NORM  AB = 0.7076166568111883
NORM  BA = 0.8553914373192324
evaluation_digest = bf840aa0...1f89
```

Kein Modell erreicht die Grenze `0.05`. LEAK, SAT und NORM erklaeren die
Form beider CAP-Lebenszyklusprofile unter diesem Vertrag nicht. Das ist
keine positive Feldfunktionsaussage.

## Naechster Schritt

W7-BC muss als naechstes den siebenpfadigen R1/R2/R4-Trajektorienvertrag fuer
CONST-V als primaere enge Feldbaseline statisch festlegen. Erst der direkte
Feld-gegen-Feld-Vergleich kann die naechste Funktionsfrage entscheiden.
