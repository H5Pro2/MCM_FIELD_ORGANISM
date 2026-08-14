# S1-EC36: Quantitatives P0-Ergebnisschema

## Zweck

S1-EC36 schliesst die in EC35 festgestellte Ergebnisschema-Luecke. Es fuehrt
keinen Feldlauf aus, sondern verarbeitet ausschliesslich zwei bereits
abgeschlossene, typisierte P0-Snapshots je Kontaktzahl und Verfeinerung.

## Erfasste Messrollen

Fuer jedes wiederholt/kontinuierlich-Paar werden gespeichert:

- geordnete Neuronenidentitaeten,
- beide Snapshot-Digests,
- vorzeichenbehafteter Aktivierungskontrast je Neuron,
- vorzeichenbehafteter Nachhallkontrast je Neuron,
- Aktivierungs-Linf,
- Nachhall-Linf.

Aus dem geordneten r2/r4/r8-Trio werden komponentenweise bestimmt:

- Aktivierungsrest r2/r4,
- Aktivierungsrest r4/r8,
- Nachhallrest r2/r4,
- Nachhallrest r4/r8,
- feiner P0-Rest als Maximum der beiden r4/r8-Reste.

Damit wird nicht aus Digests auf eine Distanz geschlossen. Die numerischen
Komponenten bleiben explizit erhalten.

## Synthetische Abnahme

Eine rein synthetische Snapshot-Fixture mit bekannten Kontrasten bestaetigt
Vorzeichen, Linf und komponentenweise Restbildung.

- fokussierte gemeinsame Tests: `21 passed`
- synthetischer Profildigest:
  `e15b511d87a2e8c9f46ea5064c73cc055371891acb724764954c478500120912`

Der synthetische Wert ist keine P0-, Wiederholungs- oder Memory-Evidenz.

## Grenze

EC36 veraendert EC34 nicht und rekonstruiert keine verworfenen EC34-Felder.
Es fuehrt keine Felddynamik aus, persistiert nichts und erzeugt keine
Ergebnisentscheidung oder Claims.

## Naechster Schritt

S1-EC37 sollte statisch den Integrationsvertrag fuer einen spaeteren neuen
Runner binden. Dieser muss je Batch beide P0-Snapshots unmittelbar an EC36
uebergeben. Ein neuer realer Feldlauf bleibt gesperrt und braucht eine neue
ausdrueckliche Freigabe.

