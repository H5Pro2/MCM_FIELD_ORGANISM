# W7-BO: Privater CONST-V-Konvergenzauswerter

## Zweck

W7-BO vergleicht die vollstaendige W7-BN-Rollenbasis numerisch. Fuer jeden
der sieben Pfade und die Komponenten `S` und `H` werden genau `D12` (R1/R2)
und `D24` (R2/R4) als rohe Linf-Abstaende gebildet: insgesamt 70 Komponenten.

## Entscheidungsregel

Eine Komponente konvergiert nur bei `D24 < D12` oder wenn beide Werte exakt
null sind. Erst wenn alle 70 Komponenten konvergieren, werden Epsilon als
Maximum der 70 `D24`-Werte und der technische Effektboden `10 * Epsilon`
gebildet.

## Evidenzgrenze

Der Auswerter liefert ausschliesslich numerische Aufloesungsdaten. Er erlaubt
keine Aussage ueber Memory, Feldfunktion, Organisation, Semantik oder KI.
Die Auswertung ist erst mit der vollstaendigen W7-BN-Rollenbasis zulaessig.

## Technischer Lauf

Die vollstaendige Auswertung hat 70 von 70 Komponenten geprueft und ist nach
der registrierten Regel konvergent. `epsilon_const_v` ist
`1.8938127538392635e-08`; der technische Effektboden ist
`1.8938127538392635e-07`. Ergebnisdigest:
`f8d936624c9a66b02501dbda9b8478245c8cdb84a5ababbe6816887cc6040a1b`.
Dieser Befund bleibt rein numerisch.
