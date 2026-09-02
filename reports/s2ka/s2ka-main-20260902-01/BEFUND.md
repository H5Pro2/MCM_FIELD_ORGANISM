# S2-KA Funktionsbefund

Status:

`S2KA_WITHHELD_VARIANT_GENERALIZATION_CONFIRMED`

Der Lauf `s2ka-main-20260902-01` wurde genau einmal mit 17 Formationen,
acht read-only Proben und 157 gebundenen funktionalen Operationen ausgefuehrt.
Die Aufzeichnung ist vollstaendig und wurde danach genau einmal unabhaengig
read-only verifiziert. Der Verifikator meldete `RECORDING_COMPLETE`.

## Ergebnis

- `H1` und `N0` kamen weder im Memory- noch im Baselinetraining vor.
- Vor Training bestand fuer `H1` kein Memorytreffer.
- Nach der variierten Bildung war der adaptive Slow-Prototyp stabil.
- Nach D1 bis D9 war `H1` weder in B4 noch in TSPM-Fast vorhanden.
- Beide TSPM-Slow-Banken erkannten `H1` final mit Support `3`.
- Der eingefrorene Erstprototyp und Replay/Nearest wiesen `H1` bei einer
  visuellen Distanz von `3/255` beziehungsweise
  `0.011764705882352955` ab.
- Der erfahrungsabhaengig verschobene adaptive Prototyp nahm `H1` bei
  `0.00968699522058819` an.
- `N0` wurde an allen vier Checkpoints von Memory und final von allen drei
  Baselines abgewiesen.
- Alle acht Memory- und Baselineproben hatten identische Vor- und
  Nachzustandsdigests.

## Einordnung

Damit ist fuer diese synthetische, vorab gebundene 336-Werte-Fixture erstmals
belegt, dass mehrere Trainingsvarianten die spaetere Behandlung einer nie
trainierten visuellen Variante veraenderten. Nach Entfernung aus B4 und Fast
stammte der positive Treffer ausschliesslich aus `B_STABLE`.

Dies ist begrenztes erfahrungsabhaengiges Lernen und Generalisieren. Die
adaptive Prototypbank erklaert den Befund vollstaendig; er belegt weder ein
allgemeines Identitaetskonzept noch besondere MCM-Physik. Eine entsprechende
auditive Holdout-Generalisation wurde nicht ausgefuehrt.

Der Hauptgate wurde nach dem Lauf wieder geschlossen. Es gab keinen Retry,
keine Parameter-, Fixture- oder Schwellenaenderung und keine Feld- oder
Kontextausfuehrung.
