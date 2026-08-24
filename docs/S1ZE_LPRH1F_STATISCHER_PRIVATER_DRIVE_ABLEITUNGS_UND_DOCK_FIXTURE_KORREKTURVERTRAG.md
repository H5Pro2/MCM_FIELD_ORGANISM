# S1-ZE: Statischer privater Drive-Ableitungs- und Dock-Fixture-Vertrag

## Vorab-Drive-Ableitung

S1-ZE schliesst die erste S1-ZD-Luecke statisch. Ein spaeterer privater,
reiner Helper darf fuer jedes geordnete Layerneuron genau einmal die bereits
vorhandene und quelldigestgebundene `MCMNeuronLayer._perception_for`-Logik
verwenden. Aus Neuron, abgeleiteter Wahrnehmung, Zielschritt und zugeordnetem
Transientinput entsteht der Drive vor der Proposal-Bildung.

Ein Derived-Drive-Satz bindet Layerdigest, Inputbundledigest, Zielschritt,
geordnete Drivedigests und einen eigenen Receipt. Derselbe Drive muss in
Vorbereitung und im spaeteren Callback des einzigen `advance`-Aufrufs
digest- und objektidentisch wiederkehren. Ein Capture-Vorlauf oder eine
duplizierte Wahrnehmungslogik ist nicht zulaessig.

## Dockkonsistente Fixture

Die korrigierte Fixture besitzt genau ein gedocktes Neuron. Dockinventar,
Kontaktinventar und Transientinventar enthalten jeweils `neuron.0`. Der
Kontaktwert ist `0.0`; die abgeleitete Wahrnehmung hat Tick `1`, denselben
Kontakt und keine lokalen Samples. Damit ist der vorbereitete Drive durch
den spaeteren Layerpfad exakt reproduzierbar.

Alle acht Source-Arme teilen denselben Derived-Drive-Satz und dasselbe
Inputbundle. Kandidat und wertgleiche generische Baseline bleiben in den
Folgelayern paarweise exakt gleich.

## Grenze

S1-ZE implementiert und fuehrt nichts aus. Kern, API und `SharedMCMField`
bleiben unveraendert. S1-ZF muss die Korrektur und ihre eindeutige
Materialisierbarkeit statisch abnehmen, bevor privater Code freigegeben
werden kann.

Maschinenlesbarer Vertrag:
[S1ZE_LPRH1F_STATISCHER_PRIVATER_DRIVE_ABLEITUNGS_UND_DOCK_FIXTURE_KORREKTURVERTRAG_V1.json](S1ZE_LPRH1F_STATISCHER_PRIVATER_DRIVE_ABLEITUNGS_UND_DOCK_FIXTURE_KORREKTURVERTRAG_V1.json).
