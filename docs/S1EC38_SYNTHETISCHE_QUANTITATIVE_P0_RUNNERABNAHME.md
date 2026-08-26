# S1-EC38: Synthetische quantitative P0-Runnerabnahme

## Zweck

S1-EC38 implementiert den durch EC37 gebundenen Snapshot-Handoff-Pfad als
synthetische Runner-Fixture. Kein realer Feldkern wird aufgerufen.

## Ablauf

Fuer jeden der sechs n1/n2-r2/r4/r8-Batches erzeugt ein synthetischer Kernel
zwei getrennte typisierte Snapshot-Kopien. Der Runner:

1. validiert beide Snapshots,
2. uebergibt sie unmittelbar an den EC36-Collector,
3. erzeugt genau ein quantitatives P0-Paar,
4. bildet erst nach drei vollstaendigen Paaren das jeweilige n1- oder
   n2-Verfeinerungsprofil.

Fehlerhafte Snapshot-Rueckgaben brechen vor einem Teilresultat ab.

## Ergebnis

- Snapshot-Handoffs: `12`
- quantitative Paare: `6`
- vollstaendige Profile: `2`
- fokussierte gemeinsame Tests: `34 passed`
- Fixture-Digest:
  `e8f6b0d4140e95fffd33096cbb7a35bea455924a420efbdbaaf1fc188bb3b53e`

## Grenze

Die Fixture konsumiert keine Autorisierung, fuehrt keine Felddynamik aus,
persistiert nichts und erzeugt keine Forschungsentscheidung oder Claims.
Ihre synthetischen Zahlen sind keine P0- oder Wiederholungsevidenz.

## Naechster Schritt

S1-EC39 sollte den korrigierten realen Messpfad statisch vorpruefen. Dabei
sind die unveraenderte 25.368-Schritte-Matrix, Ressourcen, zwoelf frische
P0-Snapshots, In-Memory-Grenze und eine neue separate Einmallauffreigabe zu
pruefen. Noch kein Feldlauf.

