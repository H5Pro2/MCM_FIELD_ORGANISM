# S2-BM: Private AVPC-1-Audio-only-Huelle

## Umsetzung

S2-BM implementiert den in S2-BL abgegrenzten privaten Anschluss. Das neue
Modul enthaelt genau drei unveraenderliche Werttypen und drei reine Binder:

- einen auditiven Quellbeleg;
- eine eingefrorene Zeitpartitionsbindung;
- eine Probenhuelle mit genau einem auditiven und null visuellen Eingaengen.

Der Quellbinder validiert den vorhandenen Browserweltvertrag und den
reduzierten Browser-Batch. In sein Ergebnis gelangen ausschliesslich die
auditive Sequenzidentitaet und ihre Provenienz. Der visuelle Elterninhalt
wird weder kopiert noch digestgebunden.

Die Partitionsbindung haelt nur die gemeinsame Felduhr, das spaeteste Ende
der Relationsexpositionen und die geordneten Frame-Provenienzen fest. Sie
bildet, aktualisiert oder liest keine Assoziation.

## Synthetische Abnahme

Das fokussierte Testmodul wurde zweimal ausgefuehrt. Beide Laeufe bestanden
alle acht Tests; der Endlauf benoetigte laut `unittest` 0,032 Sekunden.

Geprueft wurden der vollstaendige Bindungsweg, unveraenderliche Ausgaben,
visuelle Unabhaengigkeit des auditiven Quellbelegs sowie Fail-Closed-Verhalten
bei Frameanzahl, Quellsubstitution, Profil, Zustand, Quellzeit und Feldzeit.

Besonders wichtig: Zwei Eltern-Batches mit identischer Audiosequenz und
unterschiedlichem visuellen Inhalt erzeugten exakt denselben auditiven
Quellbeleg. Damit kann der visuelle Elterninhalt die spaetere auditive Probe
nicht ueber diesen Beleg beeinflussen.

## Grenze

Es wurden weder `advance_ppb1_bank` noch die vorhandene read-only Probe
aufgerufen. Ebenso gab es keine Relationsbildung, keinen Feldzugriff, keine
Produktions- oder Liveausfuehrung und keinen oeffentlichen Export.

Der Befund schliesst den technischen Audio-only-Eingabeblocker. Er ist noch
kein Wiedererkennungs-, Assoziations-, Feldwirkungs- oder MCM-Memory-Befund.

## Naechster Schritt

S2-BN nimmt Implementierung, Digests, visuelle Unabhaengigkeit, Zeitgrenzen
und private Oberflaeche statisch ab, ohne die Binder oder Tests erneut
auszufuehren.
