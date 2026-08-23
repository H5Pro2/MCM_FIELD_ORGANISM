# S1-YY: Statischer LPRH-1F-Layervertrag und Quellbindungskorrektur

## Ergebnis

S1-YY schliesst die in S1-YX gefundene Provenienzluecke auf Vertragsniveau.
Die private Vorbereitungsfunktion erhaelt kuenftig ein validiertes
`MCMNeuronLayer`-Objekt. `layer_id`, Layerdigest, Feld- und Geometrieidentitaet,
Tick sowie die geordneten Neuronendigests stammen ausschliesslich aus dieser
Quelle.

## Drive-Bindung

Die Drives muessen den Layerneuronen in Anzahl und aufsteigender
Neuron-ID-Reihenfolge exakt entsprechen. Jeder `drive.previous`-Vorzustand
muss dasselbe unveraenderliche Neuronenobjekt wie der entsprechende
Layereintrag sein und denselben Digest besitzen. Abweichende Layer-, Feld-,
Geometrie-, Tick- oder Zustandsidentitaeten werden ohne Teilausgabe verworfen.

Der vorbereitete private Satz bindet zusaetzlich den `source_layer_digest`.
Layer und Drives muessen vor und nach der Vorbereitung digestgleich bleiben.
Eine externe, synthetische oder aus `field_id` abgeleitete `layer_id` ist
nicht zulaessig.

## Grenze

S1-YY enthaelt keinen Consumer-Code und fuehrt keine Projektfunktion aus.
API, Exporte, `SharedMCMField`, bestehende Layer- und Drive-Typen, Snapshot,
Produktion und Feldwirkung bleiben unveraendert. Ein separater statischer
S1-YZ-Audit muss diese Korrektur abnehmen, bevor die private Implementierung
erneut freigegeben werden kann.

LPRH-1F bleibt eine generisch erklaerbare Engineeringkopplung.

Maschinenlesbarer Vertrag:
[S1YY_LPRH1F_STATISCHER_LAYERVERTRAG_UND_QUELLBINDUNGSKORREKTUR_V1.json](S1YY_LPRH1F_STATISCHER_LAYERVERTRAG_UND_QUELLBINDUNGSKORREKTUR_V1.json).
