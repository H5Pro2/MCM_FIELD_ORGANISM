# S1-EC32: Reale Sechs-Rollen-Adapter-Fixture

## Zweck

S1-EC32 implementiert die in S1-EC31 noch fehlende Abbildung der sechs
n1/n2-Pilotrollen auf die vorhandenen realen Feldkerne. Die Abnahme ist auf
die kleine n2/r2-Fixture mit vier AV-Supports und acht Feldschritten je Arm
begrenzt.

## Rollenbindung

- `p0_repeated` und `p0_continuous`: neutraler asynchroner Feldkern ohne
  E1-Zustand oder E1-Adapter.
- `repeated_formation_ablated` und `continuous_formation_ablated`:
  vorbereiteter E1-Bildungskern mit neutralem Zustand und deaktivierter
  Bildung.
- `repeated_active` und `continuous_active`: derselbe vorbereitete
  E1-Bildungskern mit aktivierter unveraenderter E1-Mechanik.

Jeder Arm beginnt mit getrennten Kopien derselben Anfangseingaben. Die
Quellplaene und Anfangsobjekte bleiben unveraendert.

## Ergebnis

- Rollen: `6/6`
- P0 / Bildungsablation / aktiv: jeweils `2/2/2`
- Feldschritte: `6 * 8 = 48`
- Ergebnisdigest: `04ae04944fcace37a60b0f39417b233991886bf24dfe24819e8b47aeab1e2d12`
- fokussierte gemeinsame Tests: `15 passed`

Der Vollpilot mit 25.368 Feldarm-Schritten wurde nicht ausgefuehrt. Es gab
keine Persistenz, Ergebnisentscheidung oder Memory-, Praegungs- oder
KI-Aussage.

## Naechster Schritt

S1-EC33 sollte EC31 mit dem nun nachgewiesenen Adapterzustand statisch neu
bewerten. Dabei sind aktuelle Ressourcen, unveraenderte Vorstufendaten,
Laufzeitgrenze, fehlende Persistenz und eine separate ausdrueckliche
Ausfuehrungsfreigabe zu pruefen. Ohne diese Freigabe bleibt der Pilot
gesperrt.

