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

**Status: technisch umgesetzt**

### Ziel

Die gegenwärtige Feldlage trägt unmittelbare Weltwirkung und eine kurze,
natürlich abklingende geschichtsabhängige Gegenwart.

### Umsetzung

1. Aktivierung und Nachhall als zwei Zeitrollen desselben Neurons verwenden.
2. Nachhall lokal, begrenzt und zeitbezogen fortschreiben.
3. Abwesenheit, Nullkontakt und Abklingen sauber trennen.
4. Nachhall klar von Beziehungsressource und organischem Memory trennen.

### Erster technischer Kandidat

`NeutralFastAfterimageConfig` und die beiden ausdrücklich wählbaren Pfade
`advance_neutral_fast_shared_field()` sowie
`advance_neutral_fast_shared_field_transient()` verbinden Aktivierung und
Nachhall als zwei Zeitrollen desselben Neurons:

```text
dx/dt = bestehende neutrale lokale Feldgleichung
dh/dt = (x - h) / tau_h
```

`tau_h` ist eine zwingend offengelegte schnelle Zeitkonstante. Der Nachhall
wird nur von der eigenen Aktivierung getragen. Nachbar-Nachhall,
Rezeptormodalität, Semantik, Beziehung und Zielzustand gehen nicht direkt in
seine Gleichung ein.

Die gekoppelte Aktivierungs- und Nachhalldynamik wird exakt über die reale
Dauer integriert. Grobe und feine Teilung desselben Verlaufs liefern denselben
Zustand. Bei asynchronen Rezeptoren bleibt der Nachhall an der kausalen
Abschlussgrenze: Ein Kontakt kann ihn nicht vor seinem Abschluss beeinflussen.

Der Kandidat ist eine feste leaky Schnellzustands-Baseline. Bei neutraler
Aktivierung klingt er monoton und beliebig weit ab, erreicht mathematisch aber
ohne künstliche Nullschwelle erst asymptotisch exakt null. Diese Grenze bleibt
offen. Der Kandidat ist daher noch nicht als vollständig lösbarer Nachhall und
nicht als organisches Memory freigegeben.

### Isolierte Freigabeprüfung

Eine isolierte Rechnung zeigte für einen bereits ungetriebenen lokalen
Nachhallwert eine zweite mögliche Relaxationsform:

```text
dh/dt = -sign(h) * |h|^alpha / T
mit 0 < alpha < 1
```

Ihre exakte Lösung erreicht die mathematisch bestimmte Null in endlicher realer
Zeit. Die Null entsteht aus der Lösung selbst, nicht aus einer Toleranz,
Schwelle oder zusätzlichen Historienvariable. Die Funktion ist lokal,
vorzeichenneutral und zeitteilungsneutral. Ihre Lösungsdauer hängt von der
vorhandenen Amplitude ab.

Damit ist nur gezeigt, dass eine endliche lokale Freigabe grundsätzlich ohne
künstlichen Reset möglich ist. Noch offen ist die kausale Kopplung an eine
gleichzeitig weiterlaufende Aktivierung. Der Kandidat ist deshalb isoliert und
wird weder in die Feld-Runtime noch in den realen Audio-Video-Lauf eingebunden.
Nach dem fehlenden Funktionsvorteil wurde auch keine ungenutzte ausführbare
Kandidaten-API behalten. Die Prüfung beschreibt eine verworfene Möglichkeit,
keine Feldtopologie und kein organisches Memory.

### Ausgeschlossene Endwert-Kopplung

Eine naheliegende Abkürzung wurde geprüft und verworfen:

```text
aktuellen Aktivierungsendwert als festes Ziel einsetzen
-> endliche Freigabe über das ganze Intervall anwenden
```

Bei unveränderter Aktivierung ist diese Rechnung zeitteilungsneutral. Sobald
sich die Aktivierung innerhalb des Intervalls entwickelt, hängt das Ergebnis
jedoch davon ab, an welchen technischen Grenzen ihr Endwert gelesen wird. Ein
kontrollierter Verlauf ergab bei grober Auswertung `0,7500` und bei Aufteilung
desselben Verlaufs `0,6495`.

Diese Differenz stammt nicht aus dem Feld, sondern aus der technischen
Segmentierung. Eine Endwert-, Abtast- oder feste Mikroschritt-Kopplung ist daher
für die Runtime gesperrt. Eine zulässige Kopplung muss den kontinuierlichen
Aktivierungsverlauf selbst kausal tragen und unter bloßer Beobachtungsteilung
denselben Zustand ergeben. Kann dies ohne Hilfshistorie oder künstliche
Umschaltung nicht gezeigt werden, bleibt die leaky Baseline der einzige
freigegebene schnelle Kandidat.

### Kontinuierliche Kopplungsfähigkeit

Eine gemeinsame kontinuierliche Gleichung ist grundsätzlich ohne zusätzlichen
Memoryzustand möglich:

```text
dx/dt = bestehende neutrale lokale Feldgleichung
dh/dt = sign(x - h) * |x - h|^alpha / T
mit 0 < alpha < 1
```

`activation` und `afterimage` bilden dabei gemeinsam den vollständigen lokalen
Zustand. Eine adaptive Integration des kontinuierlich bewegten Feldes ergab bei
einem ungeteilten und einem unterbrochen fortgesetzten Verlauf nur eine
numerische Differenz von `4,44 * 10^-16`. Ein fester Mikrotakt oder eine
Hilfshistorie war dafür nicht nötig.

Dies ist noch keine Runtime-Freigabe. Für 336 gleichzeitig gekoppelte lokale
Werte benötigte eine simulierte Sekunde abhängig vom offenen Exponenten etwa
`0,15` bis `26,85` reale Sekunden. Gerade die stärkere endliche Nullbildung
erzeugte sehr viele adaptive Auswertungen nahe der bewegten Aktivierung. Eine
feste Wahl des rechnerisch bequemen Exponenten wäre keine inhaltliche
Begründung. Deshalb wird weder ein neuer Solver noch eine zusätzliche
Abhängigkeit in die Runtime übernommen.

### Funktionsabgleich und Runtime-Anschluss

Im aktuellen gemeinsamen Feld wird `afterimage` nicht als Eingabe der
Aktivierung, Rezeptorannahme oder Weiterleitung verwendet. Leaky und endliche
Relaxation unterscheiden daher nur die schnelle lesbare Zustandsrolle. Die
deutlich teurere nichtlineare Variante trägt gegenwärtig keine zusätzliche
kausale Feldfunktion und bleibt isoliert.

Der zeitstabile leaky Kandidat ist nun optional durch den vollständigen
asynchronen Runtime-Pfad geführt:

```text
native Audio- und Videoabschlüsse
-> neutrale Docks
-> gemeinsame Aktivierung
-> lokaler schneller Nachhall
```

`afterimage_config` muss ausdrücklich übergeben werden. Ohne diese Konfiguration
bleibt die bisherige reine Aktivierungsmechanik unverändert. Mit ihr bleibt
`activation` ebenfalls exakt gleich; zusätzlich wird nur der lokale schnelle
Nachhall fortgeschrieben. Grobe und feine Beobachtungsteilung ergeben denselben
Aktivierungs- und Nachhallzustand. Die synthetische Audio-Video-Klammer und die
Live-Brücke reichen dieselbe Konfiguration verlustfrei weiter.

Dies gibt keine Nachhall-Rückwirkung frei. Der schnelle Zustand ist weiterhin
kein organisches Memory und belegt keine Beziehungsressource.

Der verbundene Pfad wurde anschließend mit realer Hardware und einer
ausdrücklich gewählten schnellen Zeitkonstante verifiziert. In einer nominalen
Sekunde entstanden 91 auditive und 30 visuelle Rezeptorabschlüsse ohne
Audioüberlauf. Alle 121 Quellstützen wurden genau einmal in dasselbe
336-Neuronen-Feld übernommen. Alle 336 Neuronen trugen danach einen von null
verschiedenen schnellen Nachhall. Rohdaten und Gerätebezeichnungen wurden nicht
gespeichert.

### Abschlusskriterium

- kurze Geschichte verändert die gegenwärtige Feldlage,
- die Wirkung folgt realer Dauer und nicht technischer Schrittzahl,
- Nachhall relaxiert ohne künstliche Nullschwelle,
- der schnelle Zustand belegt keine Beziehungsressource,
- Nachhall wird nicht als langfristiges Memory bezeichnet.

## Priorität 4: Technischer Dauerbetrieb und Persistenz

**Status: technisch umgesetzt**

### Ziel

Der Organismuszustand kann über längere Sitzungen stabil fortgeführt,
unterbrochen und exakt wieder aufgenommen werden.

### Umsetzung

1. Begrenzte längere Feldsitzungen ermöglichen.
2. Vollständigen Feldzustand serialisieren.
3. Wiederaufnahme ohne versteckte Prozess- oder Closure-Zustände sichern.
4. Observer-, Debug- und Archivdaten von der Runtime trennen.

### Erster Sitzungsrahmen

`run_neutral_field_session()` führt mehrere vollständig abgeschlossene bounded
Feldfenster auf demselben aktuellen gemeinsamen Feld fort. Jedes Fenster
verwendet den bestehenden asynchronen Runtime-Pfad und kann den schnellen leaky
Nachhall tragen.

Der Sitzungszustand besteht ausschließlich aus:

```text
gemeinsames MCM-Feld
+ Anzahl abgeschlossener Fenster
+ Anzahl eindeutig verarbeiteter Quellstützen
```

Rezeptorsequenzen, Handoffs, Rohdaten und Observerausgaben werden nicht im
Ergebnis gehalten. Zwischen Fenstern kann der vollständige
`SharedMCMFieldSnapshot` als kanonisches JSON serialisiert, neu eingelesen und
wiederhergestellt werden. Ein ununterbrochener Drei-Fenster-Lauf und die
Fortsetzung nach diesem vollständigen JSON-Roundtrip ergeben exakt denselben
Snapshot-Digest.

Fenster müssen auf derselben Organismusuhr lückenlos anschließen. Auch eine
wiederaufgenommene Sitzung muss exakt an der im Snapshot gespeicherten
Feldgrenze fortsetzen. Die maximale Fensterzahl bleibt ausdrücklich begrenzt.

Ein längerer synthetischer Verlauf mit 24 Fenstern und 48 eindeutigen
Quellstützen wurde zusätzlich in mehreren Checkpoint-Rhythmen fortgesetzt:

```text
ununterbrochen
Checkpoint nach jedem Fenster
wechselnde Abstände 2, 3, 5 und 7
Abstände 11 und 13
```

Alle Varianten enden mit exakt demselben Snapshot-Digest. Auch bei einem
vollständigen JSON-Roundtrip nach jedem Fenster erscheinen weder
Rezeptorsequenzen noch technische Handoffs im gespeicherten Zustand.

Die Live-Brücke hält Kamera, Mikrofon und ihre technischen Rezeptorzustände
über mehrere begrenzte Fenster geöffnet. Auditiver Rollzustand und visuelle
Ereignisnummern laufen fort; nur das gemeinsame Feld wird an einer
Fenstergrenze optional als JSON serialisiert und wiederhergestellt. Das
Sitzungsergebnis enthält anschließend ausschließlich den aktuellen Feldzustand
und technische Zähler.

Ein realer Lauf über zwei aufeinanderfolgende Ein-Sekunden-Fenster verarbeitete
60 visuelle und insgesamt 251 auditive und visuelle Rezeptorabschlüsse in
demselben 336-Neuronen-Feld. Zwischen den Fenstern erfolgte ein vollständiger
JSON-Checkpoint. Ein Audioüberlauf wurde als Eingangshinweis gezählt; es wurden
keine Rohdaten oder Gerätebezeichnungen gespeichert. Der Lauf bestätigt den
technischen Fortsetzungsweg, nicht die Qualität einer Feldentwicklung.

Dies ist nur technische Zustandserhaltung. JSON, Dateisystem oder ein späteres
Speicherbackend erzeugen keine Bedeutung, Beziehung oder Feldwirkung.

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

Prioritäten 1 bis 4 stehen als zusammenhängender technischer Grundaufbau.
Der vorhandene MINI-DIO-Stand zur Feldtopologie ist gegen die aktuelle
gemeinsame Neuronenschicht abgeglichen.

Der kleinste konkrete Funktionsmangel lautet: Nach exakter Angleichung von
Aktivierung und schnellem Nachhall kann unterschiedliche Weltgeschichte unter
derselben späteren Probe keinen unterschiedlichen Feldweg tragen. Diese
technische Grundnull ist mit weiterhin verschiedenen früheren
Wahrnehmungsschnappschüssen reproduziert.

Der darstellungsoffene Zustandsvertrag ist formuliert. Er grenzt
Nichtredundanz, lokale Entstehung, spätere kausale Wirkung, vollständige
Lösung, Ressourcenfreigabe, andere Wiederbindung und Funktionswechsel ab,
ohne eine digitale Darstellung festzulegen.

Als Nächstes wird genau ein kleinster passiver Kandidatenvergleich
vorregistriert. Noch gesperrt bleiben Runtime-Erweiterung, Mehrzyklen,
Topologiewachstum und jede Semantikbehauptung.
