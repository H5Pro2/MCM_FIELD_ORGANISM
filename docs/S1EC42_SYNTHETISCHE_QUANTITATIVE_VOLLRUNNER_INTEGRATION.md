# S1-EC42: Synthetische quantitative Vollrunner-Integration

## Zweck

S1-EC42 integriert die komplette Sechs-Batch-Ablaufkoordination mit dem
quantitativen P0-Handoff. Alle realen Kernaufrufe werden durch typisierte
synthetische Receipts und Snapshot-Paare ersetzt.

## Gebundener Ablauf je Batch

1. `p0_repeated`-Receipt,
2. `p0_continuous`-Receipt,
3. sofortige Uebergabe zweier P0-Snapshots an EC36,
4. `repeated_formation_ablated`-Receipt,
5. `continuous_formation_ablated`-Receipt,
6. `repeated_active`-Receipt,
7. `continuous_active`-Receipt.

Nach dem vollstaendigen r2/r4/r8-Trio wird je Kontaktzahl genau ein
quantitatives P0-Profil gebildet.

## Ergebnis

- Batchanzahl: `6`
- Arm-Receipts: `36`
- P0-Snapshots: `12`
- quantitative P0-Paare: `6`
- P0-Profile: `2`
- geplante Feldarm-Schritte: `25.368`
- ausgefuehrte Feldschritte: `0`
- fokussierte gemeinsame Tests: `31 passed`
- Integrationsdigest:
  `9073aa10c0ee6c3ca906efacc198bcdaef16782346af4b720df05a8c605eafc9`

## Grenze

Die Integration konsumiert keine Autorisierung, ruft keine realen Feldkerne
auf, persistiert nichts und erzeugt keine Forschungsentscheidung oder
Claims. Synthetische Profilwerte sind keine Evidenz.

## Naechster Schritt

S1-EC43 sollte den integrierten Realpfad abschliessend statisch vorpruefen:
aktuelle Ressourcen, exakt einmalige Autorisierung, 900-Sekunden-Limit,
In-Memory-Grenze, zwoelf unmittelbare P0-Handoffs und Ausschluss des alten
EC34-Ergebnisses. Noch kein Feldlauf.

