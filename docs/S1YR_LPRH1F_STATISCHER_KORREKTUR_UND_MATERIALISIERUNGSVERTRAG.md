# S1-YR: Statischer LPRH-1F-Korrektur- und Materialisierungsvertrag

## Ergebnis

S1-YR schliesst die acht S1-YQ-Blocker statisch. Die lokale Wirkung wird
durch eine feste Mittelpunktregel eindeutig:

`Ausgabeaktivierung = (OFF-Aktivierung + lokaler Prototypwert) / 2`

Der Nachhallwert bleibt exakt der OFF-Wert. Weil beide Eingangswerte bereits
im normalisierten Bereich liegen, ist kein zusaetzlicher Clamp erforderlich.
Ein Prototypwert gleich dem OFF-Wert macht die Richtungsfixture ungueltig.

## Atomare Trennung

Alle Arme verwenden denselben einmal berechneten unveraenderlichen
OFF-Ausgabesatz. Sechs private Typen binden Kontextinput, generischen
Vergleich, lokale Ausgabe, Ausgabesatz, Feldnutzungsreceipt und atomaren
Gesamtbefund.

Die spaetere Feldnutzung erhaelt einen eigenen `field_use_id`-Namensraum und
ein eigenes Ledger. Dieser Verbrauch ist vom bereits abgeschlossenen
S1-YN-Handoff-Verbrauch getrennt. Der bestehende `MCMNeuronDrive` und
`SharedMCMField` bleiben unveraendert.

## Baselinekonsequenz

Der generische Vergleich erhaelt dieselben Werte, dieselbe Zuordnung,
denselben OFF-Ausgabesatz und dieselbe Mittelpunktregel. Daher ist numerisch
exakte Gleichheit zu erwarten. Ein gueltiges Ergebnis waere
`TECHNICAL_PASS_GENERIC_REDUCTION`: Die Provenienzbindung funktioniert als
Engineeringgrenze, aber es entsteht kein eigener MCM-Feldmechanismus.

## Grenze

S1-YR implementiert und testet nichts. S1-YS muss die acht Schliessungen,
sechs Typen, endliche Fixture, Aufrufbudgets und Entscheidungsreihenfolge
nochmals rein statisch pruefen, bevor privater Consumer-Code zulaessig wird.

Maschinenlesbarer Vertrag:
[S1YR_LPRH1F_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json](S1YR_LPRH1F_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json).
