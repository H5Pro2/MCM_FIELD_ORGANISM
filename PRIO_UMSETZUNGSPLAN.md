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

**Status: technisch umgesetzt**

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

### Erste neutrale Umsetzung

Die erste explizite Substratfunktion ist als
`NeutralLocalFieldSubstrateConfig` und
`advance_neutral_shared_field()` vorhanden.

Für einen abgeschlossenen Feldschritt gilt:

```text
dx_i/dt = (1 / tau) * [
    Summe über lokale Nachbarn j: (x_j - x_i)
    + bei vorhandenem Rezeptorkontakt: (c_i - x_i)
]
```

Die Gleichung wird für die vollständige abgeschlossene Neuronenschicht exakt
über die reale Dauer `dt` integriert. Die technische Beobachtungsgrenze ist
damit kein versteckter Integrationsschritt:

```text
ein Intervall dt
= mehrere Teilintervalle mit demselben Weltkontakt
-> gleicher physischer Feldendzustand
```

`tau` ist die beim Aufbau zwingend offengelegte technische Reaktionszeit.
Es gibt keine Modalitätsgewichte, Neuronenrollen, Schwellen, Beziehungen oder
Zielmuster. Kontaktabwesenheit wird nicht als gemessener Nullkontakt behandelt.
Ohne Rezeptorkontakt wirkt nur die symmetrische lokale Diffusion. Sie erhält
den Feldmittelwert und reduziert räumliche Unterschiede.

Der Nachhall wird von dieser ersten Funktion nicht verändert. Transiente
asynchrone Rezeptorverläufe werden noch nicht gelesen. Beides gehört zu
späteren Prioritäten und wird nicht vorzeitig in diese Gleichung gemischt.

`SharedMCMField.advance()` akzeptiert dafür eine explizite
`MCMFieldStepTime`, deren Organismusintervall exakt zur verteilten Weltzeit
passen muss. `advance_neutral_shared_field()` bleibt explizit auswählbar und
ist kein versteckter Runtime-Standard.

Technisch geprüft sind:

- kausale lokale Ausbreitung aus demselben abgeschlossenen Vorzustand,
- identische räumliche Dynamik bei grober und feiner Zeitteilung,
- Trennung von Kontaktabwesenheit und gemessenem Nullkontakt,
- Begrenzung im normalisierten Feldbereich,
- Spiegelneutralität auf einer größeren Feldgeometrie,
- exakte Snapshot-Wiederaufnahme.

Die Mechanik ist ausdrücklich als feste lokale Reaktions-Diffusions-
Naturbedingung klassifiziert. Sie ist das technische Substrat und kein Befund
über organische Entwicklung.

### Abschlusskriterium

- dieselbe Funktion arbeitet an allen Neuronen und Modalitäten,
- Weltkontakt und lokale Vorfeldlage sind beide kausal wirksam,
- kein zukünftiger Kontakt wirkt vor seinem Abschluss,
- Aktualisierungsreihenfolge bleibt wirkungslos,
- Zustand bleibt numerisch begrenzt,
- Snapshot und Wiederaufnahme bleiben exakt,
- keine Bedeutung, Beziehung oder Zielstruktur ist enthalten.

## Priorität 2: Fortlaufender gemeinsamer Audio-Video-Feldbetrieb

**Status: technisch umgesetzt**

### Ziel

Reale auditive und visuelle Rezeptorzustände wirken mit ihren eigenen
Zeitlagen fortlaufend auf dasselbe MCM-Feld.

### Umsetzung

1. Audio- und Videoereignisse auf derselben Organismusuhr führen.
2. Unterschiedliche Rezeptorraten verlustfrei bis zu den Docks erhalten.
3. Ereignisse nur nach ihrem tatsächlichen Abschluss wirksam werden lassen.
4. Fehlende Modalität als Abwesenheit und nicht als künstliche Null behandeln.
5. Einen begrenzten realen Mehrtaktlauf bereitstellen.

### Bereits umgesetzt

`advance_neutral_shared_field_transient()` verbindet den vorhandenen
verlustfreien Rezeptorabschluss-Pfad direkt mit der neutralen Feldmechanik:

```text
ReceptorTimeSequence
-> Abschlussgruppen auf gemeinsamer Organismuszeit
-> transienter Dockverlauf
-> vollständige lokale Neuroneneingaben
-> neutrale gemeinsame Feldmechanik
```

Zwischen zwei Abschlusszeiten entwickelt sich das Feld kontinuierlich durch
seine lokale Gleichung. Ein Rezeptorzustand wird erst an seinem gemessenen
Abschlusszeitpunkt kausal wirksam. Seine gemessene Lesedauer bestimmt die
Stärke der lokalen verzögerten Kontaktwirkung. Der Abschluss erzeugt keinen
zusätzlichen technischen Feldtakt.

Die Übergabe verlangt eine kontaktfreie Randverteilung. Dadurch kann derselbe
Weltkontakt nicht gleichzeitig als skalarer Kontakt und als transientes
Ereignis doppelt in das Feld gelangen.

`run_neutral_asynchronous_field()` schließt zusätzlich einen vollständigen
begrenzten Lauf vor dem ersten Feldschritt. Eine Quellstütze wird technisch aus
Modalität, Quelluhr und Quellintervall bestimmt. Mehrere Fertigmeldungen
derselben Stütze werden nicht gemittelt, gewichtet oder mehrfach wirksam,
sondern vor jeder Feldänderung abgewiesen. Eine veränderte Rezeptor- oder
Trägergeometrie erzeugt dabei keine neue physische Quellstütze.
Widersprüchliche Werte derselben Stütze werden gesondert als ungültige Quelle
erkannt. Gleiche Zeitintervalle verschiedener Modalitäten bleiben unabhängig.

Der begrenzte Lauf akzeptiert nur eine vollständig innerhalb seines Horizonts
liegende Quellgeschichte. Diese technische Vollständigkeitsregel ist kein
Feld-Memory und kein lernender Zustand.

`capture_audio_video_into_neutral_field()` verbindet nun die vorhandene
gleichzeitige Audio-Video-Aufnahme mit diesem begrenzten Feldlauf. Rohdaten
werden nur von den technischen Adaptern gelesen und unmittelbar in auditive
beziehungsweise visuelle Rezeptorzustände überführt. Erst diese reduzierten
Zustände erreichen über ihre nativen Abschlusszeiten die Docks und dasselbe
MCM-Feld.

`capture_live_audio_video_into_neutral_field()` öffnet dafür ausschließlich
die ausdrücklich angegebenen Kamera- und Mikrofon-Geräte. Die
`NeutralLocalFieldSubstrateConfig` bleibt ein zwingend sichtbarer Parameter.
Die Live-Brücke besitzt keine Geräteauswahl, keine Ratennormalisierung und
keine eigene Feldmechanik.

Der konstante lokale Feldgenerator wird innerhalb eines begrenzten Laufs nur
einmal spektral zerlegt. Alle Abschlussintervalle verwenden dieselbe exakte
Zerlegung weiter. Das entfernt redundante Rechnung, ohne Gleichung,
Ereignisfolge oder Feldwirkung zu verändern.

Technisch geprüft sind:

- unterschiedliche auditive und visuelle Abschlusszeiten,
- gleichzeitige Abschlüsse ohne Deklarationspriorität,
- genau einmalige Zuordnung aller Ereignisse,
- identischer Endzustand bei grober und feiner Beobachtungsteilung,
- keine Wirkung eines noch nicht abgeschlossenen zukünftigen Kontakts,
- eindeutige Quellstützen vor dem ersten Feldschritt,
- geschlossener Abbruch bei identischer oder widersprüchlicher Doppelmeldung,
- realer Ein-Sekunden-Lauf mit freier Kamera, 91 auditiven und 30 visuellen
  Abschlüssen,
- aktive visuelle Rezeptorwerte zwischen 0,212 und 0,834,
- null gemeldete Audioüberläufe und 121 von 121 zugeordnete Quellstützen,
- gemeinsamer resultierender Feldzustand mit 336 MCM-Neuronen,
- exakte Snapshot-Wiederaufnahme.

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

Als Nächstes beginnt Priorität 3:

> Aktivierung und kurzer Nachhall werden als zwei lokale Zeitrollen desselben
> MCM-Neurons verbunden. Der Nachhall muss realzeitbezogen, begrenzt,
> vollständig abklingend und klar vom späteren organischen Memory getrennt
> bleiben.

Das System erhält dabei weiterhin keine Feldtopologie, kein organisches
Memory, keine Selbstregulation und keine Semantik.
