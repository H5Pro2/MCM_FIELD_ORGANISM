# S1-EC31: Statischer Real-Preflight fuer den n1/n2-Pilot

## Zweck

S1-EC31 prueft statisch, ob die vorhandene n1/n2-Pilotmatrix technisch an
die realen Feldkerne angebunden werden kann. Der Schritt baut keinen
Real-Adapter, fuehrt keinen Feldschritt aus und erteilt keine
Ausfuehrungsfreigabe.

## Gebundene Vorstufen

- S1-EC27 Plan-Set: `b53d1e1c94dedaf4d7cd8aac250d8c81bd0ebc0b0e2ea69ecd7e0e3716b365ea`
- S1-EC29 Pilotvertrag: `834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8`
- S1-EC30 synthetischer Runner: `700b0296be5cc04ac5049a447d0c6feb9f6b6ec50eb19915fc235c0c2fd697c0`

Die sechs Rollen bleiben getrennt:

- P0 wiederholt und kontinuierlich verwenden den neutralen asynchronen
  Feldkern ohne E1-Zustand und ohne Adapter.
- Bildungsablation wiederholt und kontinuierlich verwenden den vorbereiteten
  realen Bildungskern mit neutralisiertem E1-Zustand.
- Aktiv wiederholt und kontinuierlich verwenden denselben Bildungskern mit
  aktivierter E1-Zustandsbildung.

## Ergebnis

Die technische Vorpruefung besteht. Der bei der Abnahme erfasste
Ressourcensnapshot weist `8121556992` freie Speicherbytes und
`236527480832` freie Plattenbytes aus. Damit liegen die registrierten
Mindestgrenzen von 4 GiB RAM und 1 GiB Platte vor.

- erfuellte Checks: `11/13`
- Entscheidung: `VORBEREITET_NICHT_FREIGEGEBEN`
- Ressourcendigest: `31e42aa88eb0c0ed46125e1e3b8ddf7b9239fa0115d2d1bd776da71fcea369c6`
- Preflight-Digest: `3be17db1add68da25efb73210c9e7ab88ae34614bbcac5e19df6f30c3abb7f3c`

Die zwei absichtlich offenen Gates sind:

1. Der reale Sechs-Rollen-Adapter ist noch nicht implementiert.
2. Eine ausdrueckliche Freigabe fuer den spaeteren Pilotlauf liegt nicht vor.

Deshalb bleiben Pilotlauf, Persistenz, Ergebnisentscheidung und alle
Memory-, Praegungs- oder KI-Claims gesperrt.

## Naechster Schritt

S1-EC32 darf ausschliesslich den realen Sechs-Rollen-Adapter implementieren
und an einer kleinen vorhandenen Fixture abnehmen. Die volle n1/n2-Matrix
darf dabei nicht ausgefuehrt werden. Erst nach erfolgreicher Adapterabnahme
ist ein neuer Preflight mit separater Ausfuehrungsfreigabe zulaessig.

