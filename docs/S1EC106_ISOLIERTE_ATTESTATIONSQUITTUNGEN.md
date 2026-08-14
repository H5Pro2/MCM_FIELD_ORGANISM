# S1-EC106: Isolierte Attestationsquittungen

## Umsetzung

EC106 implementiert drei unveraenderliche Datentypen:

1. r2-Produzentenquittung fuer EC67;
2. r4/r8-Produzentenquittung fuer EC96;
3. kombinierte EC102-Einlassattestation.

Jede Produzentenquittung bindet Autorisierungsdigest, Resultatdigest,
Probequittungsdigests, Schrittbilanz und Produzentenposition. Die kombinierte
Attestation verlangt beide typisierten Quittungen, alle 24 verschiedenen
Probequittungsdigests, 22.456 Herkunftsschritte und dieselben Probeobjekte auf
Quell- und vorgesehener EC102-Seite.

## Synthetische Abnahme

Die isolierte Fixture verwendet ausschliesslich die synthetischen
EC103-Resultatcontainer. Sie ruft weder EC67 noch EC96 oder EC102 auf. Falsche
Schrittbilanz, vertauschte Quittungstypen und veraenderte Objektidentitaet
scheitern fail-closed.

Es gibt bewusst keinen oeffentlichen nachtraeglichen Quittungsbuilder. Die
Erzeuger sind private Fixture-Helfer. Produktive Quittungen duerfen spaeter nur
atomar innerhalb der jeweiligen Koordinator-Rueckgabe entstehen.

Die Fixture belegt nur die interne Konsistenz der Quittungsdatentypen. Sie ist
keine reale Produzentenattestation und oeffnet den EC104-Einlass nicht.

## Aussagegrenze

Die Quittungen sind prozessinterne Digestvertraege, keine kryptographischen
Ausfuehrungsbeweise. EC106 veraendert keine Koordinatoren, fuehrt keinen
Feldschritt aus, persistiert nichts und trifft keine EC46- oder
Forschungsentscheidung.

## Bester naechster Schritt

Am besten geht es mit S1-EC107 weiter: statisch festlegen, wie EC67 eine neue
explizite Einmallaufautorisierung und seine r2-Produzentenquittung atomar
zurueckgeben muss. Noch keine Produktionsaenderung oder Ausfuehrung.
