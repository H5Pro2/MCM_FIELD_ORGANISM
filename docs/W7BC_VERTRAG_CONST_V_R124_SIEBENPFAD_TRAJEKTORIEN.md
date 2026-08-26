# W7-BC: Vertrag fuer CONST-V-R1/R2/R4-Siebenpfad-Trajektorien

## Zweck

W7-BC registriert den kleinsten Feldtrajektorien-Anschluss fuer die in W7-AU
priorisierte enge Gegenbaseline `CONST-V`. Die Gleichung besteht bereits, aber
bislang fehlt ihr ein Verbraucher fuer die sieben W7-Y-Pfade bei R1, R2 und R4.
Diese Datei beschreibt nur den spaeteren Aufbau. Sie enthaelt keinen Lauf und
keinen Befund.

## Gebundene Grundlage

- W7-M-Matrix-Digest:
  `a1e3f8a08fbef760c8f0b147f99cbebfcc05621c2265a70d853dd3d4863ffb6a`
- W7-Y-Siebenpfadplan-Digest:
  `c771a3c28c04e04a61fa24d187416ef65b17597f9af759682deb576a28c25b32`
- Modell: `const-v`
- Gleichung: `baseline.k2-f3.const-v.v1`
- Parameter: `eta=1.0`, `kappa=0.5`, `lambda_sm=0.5`
- Ein technischer Skalar je Neuron; dieser ist weder freie Kapazitaet noch
  Memory.

Vor jedem ersten Safe-Step muss eine frische Kopie des W7-M-Ausgangsfeldes den
eingefrorenen CONST-V-Substratarm tragen. Nur einen CONST-V-Kopplungsrechner in
ein CAP-Feld einzuspritzen waere unzureichend, weil die Schrittweitenpruefung
den Substratarm des Feldes liest.

## Spaetere Trajektorienbelegung

Die Pfade `AB`, `AG`, `BA`, `BG`, `UA`, `UB` und `UG` werden unveraendert aus
W7-Y uebernommen. Pro Aufloesung entstehen 35 Rollen aus sieben Pfaden und
fuenf Checkpoints. Die Primaerreihenfolge ist R1, R2, R4; die exakte
Wiederholung laeuft R4, R2, R1. Damit sind jeweils 105 Primaer- und 105
Wiederholungstrajektorien vorgegeben.

An jedem Checkpoint wird der vollstaendige Zustand kopiert. Nur `S` und `H`
werden auf der Kopie auf null angeglichen; der technische Skalar bleibt
erhalten. Die Probe kehrt nicht in die Hauptkette zurueck. Gemessen werden
`S`, `H` und der technische Skalar an Rezeptorabschluss- und Endgrenzen.

## Eigene numerische Grenze

Die CAP-Schwelle aus W7-AT darf nicht direkt auf CONST-V uebertragen werden.
Fuer jede der 35 Rollen und fuer `S` und `H` muss gelten:

`D24 < D12` oder beide Distanzen sind exakt null.

Erst wenn alle 70 Vergleiche aufgeloest sind, ist `epsilon_const_v` das Maximum
aller 70 R2/R4-Linf-Distanzen. Ein spaeterer CAP-CONST-V-Vergleich verwendet:

`epsilon_gemeinsam = max(epsilon_cap, epsilon_const_v)`

`effect_floor_gemeinsam = 10 * epsilon_gemeinsam`

Der W7-AT-Wert `epsilon_cap = 1.891576895118874e-08` ist hier nur gebundene
Provenienz und kein CONST-V-Ergebnis.

## Evidenzgrenze

W7-BC erlaubt weder Ausfuehrung noch Ergebniswerte. Es begruendet keine
Profilentscheidung, Feldfunktion oder Memory. CAP-Ledger, freie Kapazitaet und
Zielkapazitaet duerfen nicht auf den CONST-V-Skalar umgedeutet werden.

## Naechster Anschluss

W7-BD hat den privaten minimalen CONST-V-Feldzustands- und Runtimeadapter
gegen diesen Vertrag implementiert. W7-BE bindet als naechstes genau einen
Pfad bei einer Aufloesung. Noch folgt kein R1/R2/R4-Gesamtlauf.
