# Gemeinsames MCM-Feld

## Status

Dieses Dokument ersetzt für die aktuelle Runtime-Architektur die frühere
Annahme getrennter sensorspezifischer MCM-Felder mit nachgeschalteter
multimodaler Feldkonstellation.

Historische Versuche und ihre damaligen Begriffe bleiben als
Forschungsprotokolle erhalten. Sie definieren nicht länger die aktive
Zustandsgrenze.

## Verbindlicher Pfad

```text
Weltkontakt
-> sensorspezifische Rezeptorflächen
-> neutraler Rezeptorenverteiler
-> offene MCM-Docks
-> eine gemeinsame MCM-Neuronenschicht
-> ein gemeinsamer MCM-Feldzustand
```

Die Rezeptorflächen dürfen technisch filtern, lokalisieren und normalisieren.
Sie erzeugen keine Objekte, Klassen oder Bedeutungen.

Der Rezeptorenverteiler:

- erhält nur abgeschlossene Rezeptorzustände;
- bewahrt Modalitätsherkunft, Geometrie und Zeitlage;
- ordnet jeden Zustand einem stabilen Dock zu;
- besitzt kein Memory;
- fusioniert keine Werte;
- bewertet und gewichtet keine Modalität.

## Ein Feld, eine Schicht

Alle Docks adressieren Neuronen derselben synchronen MCM-Neuronenschicht.
Innerhalb dieser Grenze existieren keine getrennten auditiven, visuellen oder
taktilen MCM-Felder.

Die technische Dock-Lage bewahrt die Herkunft eines Rezeptorkontakts. Sie ist
keine feste semantische Rolle des Neurons. Alle Feldneuronen verwenden
denselben lokalen Neuronenvertrag und denselben vorherigen Feldzustand.

Die Docks belegen eindeutige Positionen derselben Feldgeometrie. Es gibt keine
intern ergänzte Modalitätsachse, die auditive, visuelle oder taktile Neuronen
voneinander abschottet. Lokale Feldproben können Dockgrenzen überschreiten,
wenn ihre Positionen in der gemeinsamen technischen Geometrie benachbart sind.
Das erzeugt noch keine gespeicherte Beziehung oder semantische Fusion.

Eine Aktualisierung ist nur gültig, wenn:

- jeder für diesen Takt vorhandene Rezeptorzustand vollständig vorliegt;
- alle Kontakte dieselbe gemeinsame Organismuszeit tragen;
- jeder Rezeptorträger genau einen Dock-Neuronenkontakt besitzt;
- alle Neuronen atomar aus demselben vorherigen Zustand fortschreiten;
- die technische Iterations- oder Eingangsreihenfolge das Ergebnis nicht
  verändert.

Ein fehlender Sinneskanal blockiert das Feld nicht. Sein Dock bleibt Teil der
Feldanatomie, trägt in diesem Takt aber keinen Rezeptorkontakt. Abwesenheit wird
nicht als Messwert null ausgegeben.

## Feldtopologie und Memory

Feldtopologie und organisches Memory sind keine getrennten Module und keine
Datenbank. Falls sich dauerhafte wirksame Beziehungen entwickeln, sind sie Teil
desselben Organismuszustands wie die Neuronenaktivität und der Nachhall.

Nicht freigegeben sind derzeit:

- feste Kanten oder Gewichte als vorweggenommenes Memory;
- globale Gewinner- oder Auswahlregeln;
- Zieltopologien;
- semantische Klassen;
- Reward als Strukturformer;
- Rohdaten-, Objekt- oder Episodenspeicher.

Die aktuelle Runtime besitzt deshalb noch keine behauptete organische
Topologieentwicklung. Sie stellt nur die gemeinsame Zustandsgrenze bereit, in
der eine solche Entwicklung später untersucht werden kann.

Die verbindliche Richtung, Zeitrollen und Freigabereihenfolge stehen im
Vertrag
[Organisches Memory des gemeinsamen MCM-Feldes](028_ORGANISCHES_MEMORY_DES_GEMEINSAMEN_FELDES.md).

## Semantische Resonanz

Semantische Resonanz ist eine mögliche entstehende Feldfähigkeit. Sie darf
nicht als Mustererkenner oder Datenbank hinter das Feld gesetzt werden.

Ein späterer Nachweis müsste zeigen, dass wiederkehrende Feldformen und
Beziehungen aus Weltteilnahme eine eigene innere Bezeichnung tragen. Sprache
darf daran als weitere erfahrene Feldform anschließen, sie aber nicht
nachträglich erzeugen oder erzwingen.

## Reflexion und Offline-Erholung

Reflexion liegt außerhalb der unmittelbaren Weltkontaktstrecke und müsste auf
dieselbe MCM-Neuronenschicht zurückwirken. Eine technische Rückwirkungsgleichung
ist noch nicht freigegeben.

Offline-Erholung ist ein Betriebsmodus desselben Feldes bei reduziertem oder
unterbrochenem Weltkontakt. Sie ist kein Training, kein Replay und kein zweites
Memory-System. Relaxation, Stabilisierung oder Lösung dürfen erst als Mechanik
gelten, wenn sie einzeln kausal geprüft wurden.

## Selbstregulation

Für eine spätere organische Selbstregulation werden zwei getrennte
Funktionsgrenzen vorgemerkt:

1. Das gemeinsame MCM-Feld müsste seine eigene spätere lokale Rückwirkung aus
   Feldgeschichte und verfügbarer Ressource mitprägen können.
2. Eine solche getragene innere Regulation könnte danach die spätere lokale
   Rezeptoraufnahme mitprägen.

Beide Grenzen stehen auf E0 und besitzen keine Runtimefreigabe. Direkte
Geräteverstellung ist keine Abkürzung und bleibt ein gesonderter möglicher
Ausgabepfad. Verbindlich ist die
[doppelte Selbstregulationsgrenze](027_DOPPELTE_SELBSTREGULATION_GRENZE.md).

## Implementierter Stand

Implementiert sind:

- `ReceptorContactFrame`, `CommonFieldTime` und `ReceptorNeuronDockMap` als
  neutrale Verträge außerhalb historischer Sinnesfelder;
- `ReceptorDistributor` als passiver, zustandsloser Rezeptorenverteiler;
- offene `ReceptorDock`-Identitäten;
- `SharedMCMField` mit mehreren Docks und genau einer
  `MCMNeuronLayer`;
- ein atomarer endlicher Audio-Video-Weltkontakt in den gemeinsamen
  Feldzustand;
- Zeitintervalle jedes vollständig reduzierten auditiven und visuellen
  Rezeptorzustands auf derselben Organismusuhr sowie ein auswahlloser
  Mehrdeutigkeitsaudit;
- ein vor jedem Sensor-Read deklarierbarer gemeinsamer Zeitfensterplan und ein
  auswahlloser Audit der nativen Dockbelegung und Grenzübertritte;
- eine passive, verlustfreie Gruppierung nativer Rezeptorzustände nach ihrer
  realen Abschlusszeit, noch ohne Gleichsetzung mit einem Feldtick;
- eine passive Rateninvarianzprüfung, die verstrichene Organismusdauer als
  notwendige technische Zeitrolle von bloßer Ereignisanzahl trennt;
- eine lückenlose passive Zeitpartition realer Rezeptorabschlüsse, die noch
  ausdrücklich keine Feldschrittfolge darstellt;
- Kontrollen für Herkunftserhalt, gemeinsame Zeit,
  Reihenfolgeunabhängigkeit und abwesende Sinneskanäle.

Nicht implementiert sind organische Topologieentwicklung, semantische
Resonanz, Reflexionsrückwirkung, Offline-Dynamik, MCM-Selbstregulation und
Eingangs-Selbstregulation. Ebenfalls nicht implementiert ist ein gemeinsamer
fortlaufender Feldtakt, der unterschiedliche reale Rezeptorraten weder durch
Zwangsverdichtung noch durch einen vollständigen Feldschritt je Sensorereignis
technisch verzerrt. Organismuszeit, Rezeptorereignis und Feldfortschritt sind
noch nicht begründet voneinander getrennt.

Der aktuelle Neuronenantrieb trägt weiterhin nur einen ganzzahligen Tick und
kann nun optional eine neutrale `MCMFieldStepTime` erhalten. Der gemeinsame
Feldpfad erzeugt diesen Vertrag noch nicht automatisch. Die Dauer ist keine
Feldmechanik und wird nicht im Neuron gespeichert.

Weiterhin offen ist die zeitliche Stütze eines reduzierten Rezeptorzustands:
technischer Read, beschriebenes Rezeptorfenster und spätere Feldwirkung dürfen
nicht ohne Nachweis gleichgesetzt werden.

Die frühere Runtime mit `SensorMCMField`, `MCMDistributor`,
`MCMFieldWindow` und `MultimodalPatternChecker` bleibt ausschließlich in ihren
expliziten historischen Modulen für alte Versuche verfügbar. Diese Namen sind
kein Bestandteil des öffentlichen Paket-API und dürfen nicht zum Aufbau des
aktuellen Organismusfeldes verwendet werden.
