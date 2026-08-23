# S1-YP: Statischer LPRH-1F-Feldnutzungs- und Falsifikationsvertrag

## Ausgewaehlte Funktion

S1-YP bindet genau eine moegliche private Engineeringfunktion:
`LPRH1F_PRIVATE_CONTEXT_CONDITIONED_LOCAL_PROPOSAL`. Ein gueltiger,
einmaliger LPRH-1-Kontext soll einen lokalen Neuronenvorschlag in Richtung
des gebundenen Prototypwerts verschieben koennen. Der bestehende
`MCMNeuronDrive`, die aktuelle Wahrnehmung, der Rezeptorkontakt, der
Nachhallwert und die Topologie bleiben unveraendert.

Der Kontext bleibt ein eigener Eingang. Er darf weder als Rezeptorkontakt
umbenannt noch in den Feldsnapshot uebernommen werden.

## Gegenprognose

Zwei verschiedene PPB-1-Vorgeschichten muessen bei identischem spaeterem
Feldvorzustand, Rezeptorinput und Feldschritt unterschiedliche stabile
Prototypen liefern. Nur am exakt zugeordneten Knoten darf sich dadurch die
Aktivierungsrichtung gegenueber LPRH-1F-OFF unterscheiden. Nicht zugeordnete
Knoten und der Nachhallwert muessen im unmittelbaren Vorschlag gleich
bleiben.

Die staerkste Baseline ist ein generischer Zusatzvektor mit denselben
Werten, derselben lokalen Zuordnung und demselben Budget. Reproduziert er
alle numerischen Ausgaben, ist die Wirkung vollstaendig als transparente
Engineeringkopplung erklaert. Daraus entsteht kein MCM-spezifischer
Mechanismusbefund.

Weitere Pflichtbaselines sind aktueller Input als Kopie, Fixed Adapter,
Digest ohne Werte, ein unverbundener stabiler Prototyp und bestehender
Nachhall beziehungsweise Integrator bei angeglichenem Feldvorzustand.

## Grenze

S1-YP enthaelt keine Gleichung, Parameter, Implementierung oder Ausfuehrung.
Vor Code muss S1-YQ statisch pruefen, ob insbesondere Effektstaerke,
Baselinebudgets und der getrennte private Drive ohne Zirkelschluss eindeutig
materialisierbar sind.

Maschinenlesbarer Vertrag:
[S1YP_LPRH1F_STATISCHER_FELDNUTZUNGS_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_V1.json](S1YP_LPRH1F_STATISCHER_FELDNUTZUNGS_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_V1.json).
