# S2-CJ: Korrigierter privater AVPC-1-Relationsbildungsvertrag

## Zeitlich getrennte Quellen

S2-CJ ersetzt ausschliesslich die fehlerhafte Expositionsquelle aus S2-CH.
Das authentische PPB-1-Bildungsergebnis und sein Bildungsumschlag binden
weiterhin die stabilen auditiven und visuellen Bankzustaende. Die Frames dieses
abgeschlossenen Bildungsstreams duerfen jedoch keine Relationsbeobachtungen
mehr bilden.

Die Relationsbeobachtung stammt aus einem zweiten, eigenstaendigen reduzierten
audiovisuellen Umschlag. Seine auditiven und visuellen Quellfenster beginnen
jeweils fruehestens nach dem Ende des zugehoerigen Bildungszustands. Beide
Umschlaege verwenden dasselbe Profil und dieselbe Feldzeit.

## Interne Ableitung

Der Aufrufer liefert kein Zeitaudit, keine Paar-ID und keine Prototyp-ID. Der
Consumer baut aus den vollstaendigen Streams des spaeteren Umschlags zwei
Zeitsequenzen und berechnet das vorhandene Ausrichtungsaudit genau einmal.
Das ausgewaehlte Frame-Paar muss darin genau eine eindeutige Ueberlappung
bilden.

Die eingefrorene Relationspartition muss exakt den gesamten spaeteren
Expositionsumschlag enthalten: zuerst alle auditiven, danach alle visuellen
Framebindungen in Streamreihenfolge. Der Relationsvorzustand muss genau dieses
Partitionsobjekt halten.

Erst danach prueft die unveraenderte read-only Probe je ein ausgewaehltes
spaeteres Frame gegen den passenden stabilen Bildungszustand. Aus den beiden
quellgebundenen Befunden entstehen genau ein Ueberlappungsbeleg und genau eine
Relationsfortschreibung.

## Eigentum und Atomaritaet

Eine private Owner-Instanz autorisiert genau einen begonnenen Versuch. Ein
vollstaendiges Ergebnis ist nur bei `PAIR_CREATED_PENDING`,
`PAIR_CONFIRMED_STABLE` oder `KEY_MARKED_CONFLICTED` und einem geaenderten
Relationszustand zulaessig. Jede Quellenabweichung, negative Probe,
zustandserhaltende Relationsablehnung oder fehlerhafte Kindausgabe beendet den
Owner terminal ohne Teilresultat.

## Einordnung

Die Korrektur fuegt keine Speicher-, Distanz-, Kapazitaets-, Support-,
Konflikt- oder Matchregel hinzu. Sie stellt nur die kausal gueltige Quelle fuer
die bestehende generische Relationskomponente her. Daraus folgt weder eine
Feldwirkung noch ein Nachweis einer MCM-spezifischen Memory.

## Naechster Schritt

S2-CK soll den korrigierten Vertrag statisch auf Typwiederverwendung,
Zeitmaterialisierbarkeit, interne Auditbildung, Rueckbindungen, Atomaritaet und
einen endlichen synthetischen Testplan pruefen.

Implementierung, Tests, Zustandsausfuehrung, Feldwirkung, Produktion,
Livepfade und oeffentliche API bleiben gesperrt.
