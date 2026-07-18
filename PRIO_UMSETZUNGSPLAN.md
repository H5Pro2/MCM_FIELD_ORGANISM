# Priorisierter Umsetzungsplan

## Zweck

Dieser Plan steuert die praktische Umsetzung von `MCM_FIELD_ORGANISM`.

Die Mechanik wird zuerst als zusammenhängendes System aufgebaut. Technische
Tests sichern Kausalität, Zustandsgrenzen und Reproduzierbarkeit. Sie ersetzen
die Umsetzung nicht und werden während des Grundaufbaus nicht als eigene
Forschungsserie behandelt.

Umfangreiche Feldforschung beginnt erst, wenn der reale Wahrnehmungspfad und
das gemeinsame MCM-Feld technisch durchgängig arbeiten.

## Verbindliche Leitlinie

Programmiert werden die digitalen Naturbedingungen:

- Weltgrenze und Rezeptorübersetzung,
- gemeinsame Zeit,
- Lokalität,
- atomare Feldfortschreibung,
- begrenzte Zustände,
- technische Persistenz,
- lösbare Rückwirkungswege.

Nicht programmiert werden:

- Bedeutung oder Objektklassen,
- gewünschte Feldmuster,
- feste semantische Beziehungen,
- Zieltopologien,
- globale Gewinner,
- Reward als Strukturformer,
- direkte Wenn-dann-Handlungen,
- Observer-Rückwirkung.

Eine lokale Feldgleichung darf fest definiert sein. Organisch entwickeln soll
sich später die wirksame und wieder lösbare Organisation innerhalb dieser
Naturbedingungen.

## Aktueller Ausgangspunkt

Technisch vorhanden sind:

- realer Audio- und Videoeingang,
- auditive und visuelle Rezeptorflächen,
- neutraler Rezeptorenverteiler,
- offene MCM-Docks,
- eine gemeinsame MCM-Neuronenschicht,
- lokale Vorfeldproben,
- atomare Feldfortschreibung,
- gemeinsamer technischer Feldzustand,
- Snapshot und exakte Wiederherstellung,
- passive Beobachtung ohne Rückschreibung,
- technische Kontrollen für Zeit, Rate, Kausalität, Gleichzeitigkeit,
  Geometrie und Wiederaufnahme.

Noch nicht als aktive Mechanik vorhanden sind:

- eine begründete lokale MCM-Felddynamik,
- ein fortlaufender realer Audio-Video-Mehrtaktbetrieb,
- aktiver schneller Nachhall im gemeinsamen Feld,
- entwickelte Feldtopologie,
- organisches Memory,
- innere Feldrückwirkung,
- semantische Resonanz,
- Reflexion und Offline-Erholung,
- Selbstregulation,
- Handlung.

## Priorität 1: Lokale MCM-Felddynamik

### Ziel

Jedes MCM-Neuron bildet seinen nächsten Zustand aus:

```text
eigenem abgeschlossenem Vorzustand
+ aktuellem oder transientem lokalem Weltkontakt
+ lokaler Vorfeldlage
+ real verstrichener Organismuszeit
```

### Umsetzung

1. Genau eine minimale, einheitliche und semantikfreie lokale Feldfunktion
   mathematisch festlegen.
2. Parameter, Begrenzung und Zustandsrollen offen ausweisen.
3. Die Funktion als explizit auswählbare Transition implementieren.
4. Sie an `SharedMCMField.advance()` anschließen, ohne sie zunächst als
   versteckten Standard zu installieren.
5. Weltkontakt, Abwesenheit und lokale Feldwirkung getrennt behandeln.

### Abschlusskriterium

- dieselbe Funktion arbeitet an allen Neuronen und Modalitäten,
- Weltkontakt und lokale Vorfeldlage sind beide kausal wirksam,
- kein zukünftiger Kontakt wirkt vor seinem Abschluss,
- Aktualisierungsreihenfolge bleibt wirkungslos,
- Zustand bleibt numerisch begrenzt,
- Snapshot und Wiederaufnahme bleiben exakt,
- keine Bedeutung, Beziehung oder Zielstruktur ist enthalten.

## Priorität 2: Fortlaufender gemeinsamer Audio-Video-Feldbetrieb

### Ziel

Reale auditive und visuelle Rezeptorzustände wirken mit ihren eigenen
Zeitlagen fortlaufend auf dasselbe MCM-Feld.

### Umsetzung

1. Audio- und Videoereignisse auf derselben Organismusuhr führen.
2. Unterschiedliche Rezeptorraten verlustfrei bis zu den Docks erhalten.
3. Ereignisse nur nach ihrem tatsächlichen Abschluss wirksam werden lassen.
4. Fehlende Modalität als Abwesenheit und nicht als künstliche Null behandeln.
5. Einen begrenzten realen Mehrtaktlauf bereitstellen.

### Abschlusskriterium

- ein zusammenhängender realer Audio-Video-Lauf erreicht das gemeinsame Feld,
- kein Rezeptorereignis wird verloren oder doppelt verarbeitet,
- keine Modalität bestimmt allein den Feldfortschritt,
- keine versteckte Fusion, Auswahl oder Ratennormalisierung entsteht,
- der Lauf ist reproduzierbar und snapshotfähig.

## Priorität 3: Schneller Feldzustand und Nachhall

### Ziel

Die gegenwärtige Feldlage trägt unmittelbare Weltwirkung und eine kurze,
natürlich abklingende geschichtsabhängige Gegenwart.

### Umsetzung

1. Aktivierung und Nachhall als zwei Zeitrollen desselben Neurons verwenden.
2. Nachhall lokal, begrenzt und zeitbezogen fortschreiben.
3. Abwesenheit, Nullkontakt und Abklingen sauber trennen.
4. Nachhall vollständig lösbar halten.

### Abschlusskriterium

- kurze Geschichte verändert die gegenwärtige Feldlage,
- die Wirkung folgt realer Dauer und nicht technischer Schrittzahl,
- Nachhall kann vollständig abklingen,
- nach vollständiger Lösung bleibt keine versteckte schnelle Spur,
- Nachhall wird nicht als langfristiges Memory bezeichnet.

## Priorität 4: Technischer Dauerbetrieb und Persistenz

### Ziel

Der Organismuszustand kann über längere Sitzungen stabil fortgeführt,
unterbrochen und exakt wieder aufgenommen werden.

### Umsetzung

1. Begrenzte längere Feldsitzungen ermöglichen.
2. Vollständigen Feldzustand serialisieren.
3. Wiederaufnahme ohne versteckte Prozess- oder Closure-Zustände sichern.
4. Observer-, Debug- und Archivdaten von der Runtime trennen.

### Abschlusskriterium

- ununterbrochener und wiederaufgenommener Lauf stimmen überein,
- Persistenz speichert nur tatsächlichen Organismuszustand,
- kein externes Speicherbackend erzeugt Bedeutung oder Handlung,
- technische Diagnose verändert das Feld nicht.

## Priorität 5: Entwickelbare Feldtopologie und organisches Memory

### Voraussetzung

Prioritäten 1 bis 4 müssen technisch stehen. Erst dann wird eine langsamere
Organisationsrolle ergänzt.

### Ziel

Wiederholte lokale gemeinsame Feldwirkung kann eine spätere Feldfunktion
verändern, ohne feste Kanten oder eine Datenbank einzuführen.

### Erforderlicher Lebenszyklus

```text
lokale gemeinsame Feldwirkung
-> mögliche Stabilisierung
-> spätere kausale Wirkung
-> Abschwächung
-> vollständige Lösung
-> Ressourcenfreigabe
-> mögliche andere Wiederbindung
```

### Abschlusskriterium

- Beziehungen werden nicht vorgegeben,
- entstandene Organisation wirkt später kausal,
- Restnachhall erklärt die Wirkung nicht vollständig,
- Organisation kann Wirkung verlieren und sich vollständig lösen,
- freigewordene lokale Möglichkeit kann anders wieder gebunden werden,
- keine globale Auswahl oder Zieltopologie entscheidet die Bindung.

## Priorität 6: Innere Feldrückwirkung und Selbstregulation

### Ziel

Der eigene Feldzustand kann spätere innere Aufnahme und später die
Rezeptoraufnahme mitprägen.

### Reihenfolge

1. MCM-interne Rückwirkung auf dieselbe Neuronenschicht,
2. Regulation der Rezeptorempfindlichkeit,
3. erst danach mögliche technische Geräteverstellung.

### Abschlusskriterium

- innere und äußere Ursache sind kausal trennbar,
- Regulation folgt eigener Feldlage statt fester Zielwerte,
- Eingänge können weder dauerhaft geschlossen noch unbegrenzt verstärkt
  werden,
- Rückwirkung bleibt begrenzt und reversibel.

## Priorität 7: Semantische Resonanz, Reflexion und Offline-Erholung

### Voraussetzung

Eine wirksame, lösbare Feldorganisation muss bereits vorhanden sein.

### Ziel

- wiederkehrende Feldformen können als innere Bezeichnungen wirken,
- Sprache kann als weitere erfahrene Feldform anschließen,
- Reflexion kann gegenwärtige innere Feldlage erneut in dasselbe Feld bringen,
- Offline-Erholung kann bei reduziertem Weltkontakt relaxieren, stabilisieren
  oder lösen.

### Ausschlüsse

- keine Wort-IDs als Bedeutung,
- keine Objekt- oder Musterklassifikation als inneres Memory,
- kein Replay als Reflexion,
- kein Training im Schlaf,
- kein LLM als eigenes Denken,
- keine vorgegebene richtige Bezeichnung.

## Priorität 8: Sichere Weltwirkung und offene Entwicklung

### Ziel

Erst nach einem tragfähigen Wahrnehmungs-, Feld- und Memorysystem wird ein
begrenzter Sensor-Effektor-Kreis untersucht.

### Abschlusskriterium

- Handlung entsteht nicht aus Reward oder fester Strategie,
- jede Wirkung ist sicher begrenzt und unterbrechbar,
- neue Weltgeschichte kann innere Organisation verändern,
- das System bleibt auch nach längerer Laufzeit lösbar und reorganisierbar.

## Test- und Dokumentationsregel

Während der Umsetzung werden nur die für den jeweiligen Mechanikblock
notwendigen Tests ergänzt:

- Unit-Tests für lokale Verträge,
- Integrations-Tests für den zusammenhängenden Pfad,
- kurze reale Smoke-Tests für Kamera und Mikrofon,
- Regressions-Tests gegen bekannte statische Sackgassen.

Nicht jeder technische Lauf erhält Methodik, Forschungsnummer und Befund.
Dokumentiert werden nur echte Architektur- oder Umsetzungsmeilensteine.

Eine größere Forschungsreihe beginnt erst, wenn Prioritäten 1 bis 4 als
zusammenhängendes Grundsystem stehen.

## Unmittelbar nächster Arbeitsschritt

Als Nächstes wird Priorität 1 umgesetzt:

> Eine minimale, lokale, zeitbezogene und semantikfreie MCM-Felddynamik wird
> festgelegt, implementiert und als explizite Transition an das gemeinsame
> MCM-Feld angeschlossen.

Sie erhält noch keine Feldtopologie, kein organisches Memory, keine
Selbstregulation und keine Semantik.
