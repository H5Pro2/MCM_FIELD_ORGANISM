# S1-EC37: Statischer quantitativer P0-Integrationsvertrag

## Zweck

S1-EC37 bindet EC36 an einen spaeteren neuen Runner, ohne einen Feldlauf zu
erlauben. Der Vertrag bestimmt, wann und in welcher Form P0-Snapshots an das
quantitative Schema uebergeben werden muessen.

## Gebundene Quellen

- EC29-Pilotvertrag:
  `834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8`
- EC35-Identifizierbarkeitsaudit:
  `9423c4425de44ceb311c7600f0fcf2d57d2100831b2603a812a307a6ff0e290b`
- EC36-Schema: `e1.repetition-pilot-quantitative-p0.s1ec36.v1`

## Integrationsgrenze

Fuer jeden der sechs n1/n2-r2/r4/r8-Batches sind unmittelbar nach Abschluss
der beiden P0-Arme erforderlich:

1. ein frischer `p0_repeated`-Snapshot,
2. ein frischer `p0_continuous`-Snapshot,
3. sofortige Uebergabe beider Snapshots an EC36 vor dem Verwerfen der Felder.

Damit sind insgesamt genau zwoelf P0-Snapshots gebunden. Komponentenreihenfolge
und Restbildung bleiben an die geordneten Neuronenidentitaeten gekoppelt.

## Schutzgrenzen

- Das fluechtige EC34-Ergebnis wird nicht akzeptiert.
- Die verbrauchte EC34-Autorisierung ist nicht wiederverwendbar.
- Erlaubt ist nur die Runnerimplementierung.
- Feldlauf, Persistenz, Ergebnisentscheidung und Memory-Claim bleiben
  gesperrt.

Vertragsdigest:
`ad9200e960f6c0c68791a41cc2c8810af2d087a7ade4690593e226e1de37502e`

## Naechster Schritt

S1-EC38 sollte den neuen Runnerpfad mit synthetischen typisierten
Snapshot-Handoffs abnehmen. Dabei duerfen keine realen Feldkerne aufgerufen
und keine Ausfuehrungsfreigabe angenommen werden.

