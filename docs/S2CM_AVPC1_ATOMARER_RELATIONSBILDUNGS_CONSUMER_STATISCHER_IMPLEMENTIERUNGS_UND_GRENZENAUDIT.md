# S2-CM: Statischer Implementierungs- und Grenzenaudit

## Bestandene Bereiche

Der private Owner, die Einmaligkeit, die Trennung von Bildung und spaeterer
Exposition, die Quellzeitpruefung, die kanonische Relationspartition, die
read-only Prototypbefunde, der Ueberlappungsbeleg, die
Relationsfortschreibung, die Ergebniskapselung und die privaten Grenzen sind
statisch nachvollziehbar. Die gebundenen Testbefunde aus S2-CL werden ohne
erneute Ausfuehrung uebernommen.

Die Kindaufrufe stehen in der gebundenen Reihenfolge und an genau den erlaubten
Aufrufstellen: ein Zeitaudit, zwei read-only Proben, ein Ueberlappungsbeleg und
eine Relationsfortschreibung.

## Offener Blocker

Das Ergebnis des Zeitaudits wird noch nicht vollstaendig gegen die
tatsaechlichen Feldfenster des spaeteren Expositionsumschlags zurueckgebunden.
Der Consumer prueft derzeit, ob das Audit vollstaendig und eindeutig ist und
ob es die ausgewaehlten Snapshot-IDs enthaelt. Er berechnet jedoch nicht nach,
ob jedes gemeldete Ueberlappungsintervall exakt dem Maximum beider Startwerte
und dem Minimum beider Endwerte entspricht.

Ein manipuliertes, aber strukturell vollstaendiges Audit koennte deshalb fuer
dasselbe Frame-Paar ein verschobenes positives Intervall melden. Der
Ueberlappungsbeleg uebernimmt dieses Intervall. Die anschliessende Pruefung
vergleicht den Beleg wiederum mit demselben fehlerhaften Audit und waere damit
zirkulaer.

## Begrenzte Korrektur

Die Implementierung muss den vollstaendigen erwarteten Auditinhalt rein aus
den eingefrorenen spaeteren Streams nachbilden: Uhr, Modalitaeten,
Frameanzahlen, geordnete Paarueberlappungen sowie eindeutige, mehrdeutige und
nicht zugeordnete Snapshot-Inventare. Das einmalige Kindresultat muss vor der
ersten Probe exakt dieser Projektion entsprechen.

Es wird kein zweiter Auditaufruf und keine neue Zeit- oder Relationsregel
eingefuehrt. Ein adversarialer Test muss ein formal vollstaendiges Audit mit
verschobenem Ueberlappungsintervall vor den Proben fail-closed stoppen.

## Einordnung

S2-CM schliesst die Implementierung noch nicht ab. Der gefundene Punkt ist ein
technischer Quellenrueckbindungsfehler, kein Befund gegen den grundsaetzlichen
Engineeringweg und kein neuer Feld- oder Memory-Befund.

## Naechster Schritt

S2-CN darf ausschliesslich die vollstaendige Audit-zu-Stream-Rueckbindung und
den einen adversarialen Intervalltest implementieren und ausfuehren.
