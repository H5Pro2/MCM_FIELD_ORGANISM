# MCM_FIELD_ORGANISM

`MCM_FIELD_ORGANISM` entwickelt ein technisches audiovisuelles
MCM-Wahrnehmungssystem mit gemeinsamen Rezeptoren, einem dynamischen Feld und
einer davon getrennten perzeptiven Zwei-Bereich-Memory.

Faehigkeiten werden nur benannt, wenn sie durch vorab gebundene,
reproduzierbare Befunde gestuetzt sind. Bekannte Engineeringverfahren bleiben
der verbindliche Vergleichsmassstab.

## Systemstand

```text
kanonische RGB-/PCM-Quelle
-> auditive und visuelle Rezeptoren
-> 336 reduzierte Wahrnehmungswerte
   |-> MCM-Feldkontakt
   `-> atomare Zwei-Bereich-Memory
       -> read-only Teilhinweisabruf
       -> Kontexthypothese oder Enthaltung
```

Das Default-Live-Profil erzeugt `288` visuelle und `48` auditive Werte.
Feld und Memory erhalten unabhaengige Geschwisterprojektionen desselben
Wahrnehmungszustands. Rohbilder, PCM-Fenster und Feldsnapshots werden nicht als
Memoryinhalt gespeichert.

Die Memory besitzt genau zwei oeffentliche Bereiche:

- `A_RECENT`: B4-Inhalte und Kurzfolge mit interner Fast-Spur;
- `B_STABLE`: getrennte auditive und visuelle stabile Prototypen.

Bestaetigt sind ein nichttrivialer AV-Feldpfad, wiederholungsabhaengige
Verdichtung, kontrolliertes Vergessen, begrenzte Holdout-Generalisation sowie
visueller und auditiver Teilhinweisabruf. Rollenfreie AV-Stroeme koennen mehrere
Erfahrungen bilden und bei fehlendem, unpassendem oder mehrdeutigem Kontext
kontrolliert enthalten. Alle Abruf- und Kontextoperationen bleiben read-only;
Kontext wirkt nicht in Feld oder Memory zurueck.

Die Funktionen werden durch Slotscans, L1-Vergleiche, adaptive Prototypbildung
und transparente Entscheidungstabellen erklaert. Das ist ein technischer
Memory- und Kontextnutzen, aber kein Nachweis besonderer MCM-Speicherphysik.

## Forschungsgrenze

Ein vorab versiegeltes, unabhaengig erzeugtes AV-Korpus zeigt, dass der Pfad
noch nicht robust auf ungefilterte Varianten uebertraegt:

- Blockmittelung komprimiert unterschiedliche visuelle Texturen unter die
  bestehende Slow-Schwelle und vermischt ihre Prototypen.
- Vollvektorvergleich und exakter maskierter Positionsscan besitzen dort keine
  kompatible visuelle Anwendbarkeitsgrenze.
- Audio trennt die Familien besser, bleibt durch breite B4-/Fast-Treffermengen
  und einzelne Druckaktualisierungen jedoch mehrdeutig.

Das System enthaelt sich dabei korrekt. Ein breiterer Formenvergleich zeigt,
dass die bestehenden 288 Blockmittelwerte raeumliche Struktur tragen. Der
aktuelle Engpass liegt bei der Kompatibilitaet der festen Matchinggrenzen und
der raeumlich einseitigen Teilhinweismaske, nicht bei einer groesseren
Repraesentation oder weiteren Memoryebene.

## Aussagegrenzen

Nicht belegt sind semantisches Verstehen, automatische Erinnerungsauswahl,
offene Welt, allgemeine Langzeit-Memory, autonome Handlung oder Feldrueckwirkung
innerer Kontexte. Die Simulation ist als Quellenreferenz qualifiziert;
Quellengleichheit zwischen zwei realen digitalen oder physischen Quellen ist
noch nicht nachgewiesen.

## Dokumentation

- [Gemeinsames MCM-Feld](docs/architektur/024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md)
- [Rezeptorvertrag und Dockgrenze](docs/architektur/025_REZEPTORVERTRAG_UND_DOCKGRENZE.md)
- [336-Werte-Memorybefund](docs/S2JX_DEFAULT_LIVE_MEMORY_FUNKTIONSBEFUND.md)
- [Rollenfreier Wahrnehmungsstrom](docs/S2LL_ROLLENFREIER_WAHRNEHMUNGSSTROM_PROZESSOR_VERTRAG.md)
- [Vorab versiegeltes AV-Korpus](docs/S2LS_VORAB_EINGEFRORENES_AV_TRAIN_HOLDOUT_KORPUS_VERTRAG.md)
- [Read-only Ursachenbefund](docs/S2LS_READONLY_URSACHENBEFUND.md)
- [Visueller Struktur-Rezeptorvergleich](docs/S2LT_VISUELLER_STRUKTURREZEPTORVERGLEICH.md)
- [Rezeptor-Memory-Kompatibilitaet](docs/S2LU_VISUELLE_REZEPTOR_MEMORY_KOMPATIBILITAET.md)

Historische Vertraege und Laufbelege bleiben unter `docs/` und `reports/`.
Die README ist eine kompakte Projektuebersicht, kein Forschungsjournal.

Vorarbeiten aus [MINI_DIO](https://github.com/H5Pro2/MINI_DIO) und der
[Mental-Core-Matrix](https://github.com/H5Pro2/Mental-Core-Matrix-MCM) sind
Forschungsreferenzen und gelten nicht automatisch als Evidenz dieses Projekts.
