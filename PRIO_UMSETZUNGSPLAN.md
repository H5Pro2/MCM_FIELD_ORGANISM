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
- ein tragfähiges organisches Memory im kontinuierlich weltberührten Feld,
- eine mögliche daraus hervorgehende, nicht gezielt programmierte
  Feldtopologie,
- innere Feldrückwirkung,
- semantische Resonanz,
- Reflexion und Offline-Erholung,
- Selbstregulation,
- Handlung.

Diese Liste ist keine gleichzeitige Implementierungsfreigabe. Nach Abschluss
der Kernmechanik wird zuerst organisches Memory als mögliches
Gehirnsubstrat des laufenden Feldes untersucht. Erst darauf folgen natürliche
Lösung und Wiederbindung, semantische Resonanz, Reflexionsrückwirkung,
selbstständige Eingangs- und Feldregulation sowie Resonanz zur Sprache. Die MCM
bleibt dabei die Möglichkeit der Feldwahrnehmung; mögliche Entwicklung kann
aus dem Zusammenspiel von Wahrnehmung und Memory hervorgehen, wird aber nicht
als Zielzustand programmiert.

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

Die Live-Brücke misst während der Startphase die tatsächlich gelieferte
Bildrate, statt die angeforderte Sollrate als reale Zeitlage auszugeben. Danach
bleiben beide Hardwareleser durchgehend aktiv. Auditive Callback-Zeiten und
visuelle Abschlusszeiten werden vorab begrenzten Organismusfenstern zugeordnet.
Ein Aufnahmeintervall darf eine Fenstergrenze überqueren; eindeutig ist die
Zuordnung über seinen Abschluss. Erst ein beidseitig abgeschlossenes Fenster
wird streng seriell in das Feld übernommen. Es gibt weder Rückdatierung noch
parallele Feldaktualisierung.

Der aktuelle reale Lauf über 30 aufeinanderfolgende Ein-Sekunden-Fenster
verarbeitete `442` visuelle und insgesamt `3.439` auditive und visuelle
Rezeptorabschlüsse in demselben 336-Neuronen-Feld. Zwischen den Fenstern
erfolgten 29 vollständige JSON-Checkpoints. Bei einer gemessenen visuellen Rate
von ungefähr `15` Bildern pro Sekunde trat kein Audioüberlauf auf.

Ein optionaler passiver Fensterbeobachter gab für jedes abgeschlossene Fenster
nur Zähler, Wertebereiche, Mittelbeträge und einen Felddigest aus. Er hält keine
Rohdaten, schreibt nicht in das Feld zurück und ist weder Memory noch
Feldmechanik. Der Lauf bestätigt damit den technischen Fortsetzungs- und
Beobachtungsweg, nicht Lernen oder die Qualität einer Feldentwicklung.

Der Beobachter kann jedes Fenster zusätzlich gegen eine getrennte exakte
B0-Wiederholung prüfen. Diese startet aus einer eigenständig wiederhergestellten
Kopie desselben Anfangsfelds, liest dieselben bereits reduzierten
Rezeptorabschlüsse und wird anschließend verworfen. Im realen Lauf über 30
Fenster lagen der maximale Aktivierungsfehler und der maximale Nachhallfehler
bei `0.0`; alle 30 vollständigen Felddigests stimmten überein. Die beobachtete
Änderung der Feldwerte ist damit vollständig durch Weltkontakt und die bekannte
schnelle Runtime reproduzierbar. Dies ist eine technische B0-Grenze und kein
Nachweis für oder gegen spätere organische Entwicklung.

Eine kontrollierte reale A-B-A-Außenwelt ist als nächster passiver
Beobachtungsrahmen angeschlossen. Sie gibt dem Feld 21 Sekunden ruhigen
audiovisuellen Kontakt A, sieben Sekunden bewegten und hörbaren Kontakt B und
danach erneut 21 Sekunden A. Die Außenwelt ist kein Bestandteil der Runtime,
speichert keine Rohdaten und schreibt nicht zurück.

Der erste technisch gültige Lauf umfasste 49 Feldfenster, `5.601`
Quellstützen, 48 Checkpoints und null Audioüberläufe. Die mittlere räumliche
Aktivierungsdistanz der einzelnen B-Fenster zur späten A-Referenz betrug
`0,000164`; die natürliche Streuung innerhalb der späten ersten A-Phase bereits
`0,000132`. Die späte zweite A-Phase lag mit `0,000352` noch weiter von der
ersten A-Referenz entfernt. Alle 49 Fenster blieben mit Fehler `0.0` exakt durch
B0 reproduzierbar.

Damit ist die notwendige A-B-A-Voraussetzung noch nicht erfüllt: B ist gegenüber
der realen A-Streuung nur schwach getrennt, und A nach B ist keine kontrolliert
wiederhergestellte A-Lage. Aus diesem Lauf darf weder Persistenz noch fehlendes
Memory abgeleitet werden.

Ein wiederholter reiner A-Stabilitätslauf beobachtete deshalb neben dem Feld
erstmals die bereits reduzierten Rezeptorprofile. Er verarbeitete `7.191`
Quellstützen in 63 Fenstern ohne Audioüberlauf. Alle Feldzustände blieben mit
Fehler `0.0` exakt B0-reproduzierbar.

Die auditive Lage änderte sich zwischen den Blöcken nur um etwa `0,000014` bis
`0,000019`. Die visuelle Lage driftete dagegen gegenüber Block 1 um `0,000659`
und `0,001262`. Nahezu parallel dazu driftete die Feldaktivierung um `0,000647`
und `0,001155`; beim Nachhall waren es `0,000576` und `0,001088`.

Die beobachtete A-Wanderung ist damit bereits überwiegend in der visuellen
Rezeptorlage vorhanden. Sie ist kein belastbarer Hinweis auf eigenständige
Feldentwicklung oder Memory. Vor einer erneuten A-B-A-Prüfung muss zuerst eine
äußerlich besser wiederholbare visuelle Weltlage hergestellt werden. Die
Runtime erhält dadurch keine neue Mechanik.

Eine Verlängerung der technischen Kamerastartphase von 30 auf 300 Bilder
verringerte die visuelle Drift nicht. Auch nach vom Kamerabackend akzeptierter
manueller Belichtungs-, Weißabgleichs- und Fokusanfrage stieg der visuelle
Abstand gegenüber Block 1 weiter auf `0,001501` und `0,002990`; die
Feldaktivierung folgte mit `0,001453` und `0,002539`.

Damit sind weder Kaltstart noch diese drei Kameraautomatiken als alleinige
Ursache tragfähig. Der physische Bildschirm-Kamera-Pfad liefert derzeit keine
hinreichend wiederholbare A-Welt. Als nächste Kontrolle wird deshalb zuerst
eine deterministische visuelle Rezeptorfolge durch denselben Rezeptor- und
Feldpfad geführt. Erst danach folgt eine neue reale Weltanordnung.

Diese deterministische Kontrolle ist abgeschlossen. Über 63 Fenster blieb die
visuelle 288-Träger-Lage mit maximalem Fehler `0.0` identisch. Zwei unabhängige
Feldläufe stimmten in allen 63 Zustandsdigests überein. Der
Aktivierungsunterschied zwischen Block 2 und Block 3 betrug nur
`4,3e-17`, beim Nachhall `6,3e-17`.

Damit erreicht die vorhandene Feldruntime unter wiederholbarem Weltkontakt
nach der schnellen Anfangsrelaxation eine wiederholbare Lage. Die zuvor
beobachtete Größenordnung von `0,001` bis `0,003` stammt nicht aus einer
fortlaufenden autonomen Drift des Feldkerns. Als nächster realer Schritt wird
eine unbewegte, nicht von einem Bildschirm erzeugte Szene verwendet; bis dahin
bleibt A-B-A geschlossen.

Die aktuell sichtbare reale Szene wurde anschließend erst über 21 und dann über
63 Fenster qualifiziert. Im kurzen Lauf lagen die visuellen Blockabstände nur
bei `0,000244` bis `0,000355`, im langen Bestätigungslauf stiegen sie jedoch
wieder auf `0,000635` und `0,001108` gegenüber Block 1. Die auditive Lage blieb
mit etwa `0,000015` eng; B0 erklärte alle 63 Feldfenster mit Fehler `0.0`.

Die aktuelle Szene ist besser als der frühere Bildschirmweg, aber über eine
Minute nicht stationär. A-B-A bleibt geschlossen, bis Kamera und Beleuchtung
auf eine tatsächlich unbewegte physische Szene ausgerichtet und mit demselben
63-Fenster-Lauf bestätigt wurden.

Eine passive räumliche Zerlegung der aktuellen visuellen Drift trennt nun
globalen Drei-Kanal-Versatz vom lokalen Rest. Für Block 3 gegenüber Block 1
betrug die gesamte visuelle L1-Differenz `0,000561`. Der globale Kanalanteil
lag nur bei `0,000097`, während der räumliche Rest `0,000554` und sein lokales
Maximum `0,005989` erreichte.

Die reale Drift ist damit nicht als bloßer globaler Helligkeits- oder
Weißabgleichsversatz erklärbar. Lokale Änderungen im physischen Bildweg
dominieren. Es wird nichts normalisiert oder aus dem Rezeptorkontakt entfernt;
die Zerlegung bleibt reiner Observer.

Ein weiterer 63-Fenster-Lauf fand nach bestätigter Außenbedingung in einem
unbewegten dunklen Raum statt: Das Licht war ausgeschaltet und es gab keine
Aktivität vor der Kamera. Dennoch erreichte die visuelle Gesamtdrift
`0,004522`. Die Zerlegung zeigte einen gleichgerichteten globalen Kanalversatz
von `0,004501` und zusätzlich `0,002253` räumlichen Rest.

Der Lauf zeigt damit: fehlendes Licht ist am realen Kamerapfad keine exakte
visuelle Null. Die Niedriglicht-Rezeptorlage selbst wandert, obwohl die äußere
Szene ruht. Die genaue technische Ursache innerhalb von Sensor, Verstärkung und
Treiber ist damit noch nicht getrennt. Es wird weder eine Rauschschwelle noch
eine Korrektur in den Organismus eingebaut.

Ein beleuchteter Vergleich mit einer anwesenden Person vor der Kamera war
bewusst reale Weltteilnahme und keine starre A-Szene. Gegenüber Block 1
veränderte sich die visuelle Rezeptorlage bis Block 3 um `0,005648`, die
auditive Lage um `0,001342`. Die Feldaktivierung folgte mit `0,003432`, der
Nachhall mit `0,003513`. Alle 63 Fenster blieben exakt durch B0 erklärt.

Ein zweiter beleuchteter Lauf mit anwesender Person verlief wesentlich ruhiger.
Die visuelle Differenz von Block 3 zu Block 1 betrug `0,000789`, die auditive
`0,000023`. Die Feldaktivierung folgte mit `0,000541`, der Nachhall mit
`0,000458`. Der visuelle globale Anteil lag bei `0,000508`, der räumliche Rest
bei `0,000794`. Alle 63 Fenster blieben mit Fehler `0.0` durch B0 erklärt.

Die Differenz zwischen beiden Personenszenen zeigt, dass „Person anwesend“ keine
definierte technische Außenweltlage ist. Bewegung, Haltung, Licht und Ton
bleiben reale Bestandteile des Weltkontakts. Der zweite Lauf trägt daher nur
eine ruhigere natürliche Teilnahme und weder Personenbegriff noch Erkennung,
Memory oder Semantik.

Damit funktioniert der gleichzeitige reale Seh- und Hörkontakt technisch durch
dieselbe gemeinsame Feldruntime. Der Lauf zeigt jedoch weder Memory noch
Semantik und darf nicht zur A-B-A-Kalibrierung verwendet werden. Für diese muss
die beleuchtete Szene ohne Person oder andere bewegliche Quelle wiederholt
werden.

Diese menschenleere beleuchtete Wiederholung ist abgeschlossen. Die visuelle
Differenz zu Block 1 sank auf `0,001480`, die auditive auf `0,000137`.
Gegenüber Dunkelheit (`0,004522`) und anwesender Person (`0,005648`) ist die
visuelle A-Lage damit deutlich ruhiger. Die Feldaktivierung lag bei `0,001534`,
der Nachhall bei `0,001276`; B0 erklärte erneut alle 63 Fenster exakt.

Stationär ist die Szene noch nicht. Der globale visuelle Kanalanteil betrug
`0,001434`, zusätzlich blieben `0,000935` räumlicher Rest. Vor A-B-A folgt
daher genau eine Wiederholung derselben menschenleeren Szene nach längerer
Lichtlaufzeit. Es wird keine technische Korrektur in den Eingang eingebaut.
Der zweite Personenkontakt ersetzt diese noch offene Wiederholung nicht.

Die geforderte menschenleere Wiederholung nach längerer Lichtlaufzeit ist
inzwischen abgeschlossen. Die visuelle Differenz von Block 3 zu Block 1 lag
bei `0,001762` und damit nicht unter dem ersten Wert von `0,001480`. Der globale
Anteil stieg auf `0,001615`, der räumliche Rest auf `0,001265`. Die auditive
Differenz blieb mit `0,000017` sehr klein. Aktivierung und Nachhall folgten mit
`0,001130` und `0,001107`; B0 erklärte alle 63 Fenster mit Fehler `0.0`.

Damit trägt die reale beleuchtete Leerszene keine hinreichend stationäre
A-B-A-Referenz. Weitere identische Wiederholungen werden gestoppt. Es wird
weder eine feste Toleranz passend zum Ergebnis gewählt noch die natürliche
Kameradrift aus dem Organismuseingang entfernt. Ein späterer Weltvergleich muss
die gemessene Rezeptoränderung als reale Eingangsbedingung mitführen und eine
behauptete Feldwirkung gegen B0 abgrenzen.

Dies ist nur technische Zustandserhaltung. JSON, Dateisystem oder ein späteres
Speicherbackend erzeugen keine Bedeutung, Beziehung oder Feldwirkung.

### Abschlusskriterium

- ununterbrochener und wiederaufgenommener Lauf stimmen überein,
- Persistenz speichert nur tatsächlichen Organismuszustand,
- kein externes Speicherbackend erzeugt Bedeutung oder Handlung,
- technische Diagnose verändert das Feld nicht.

## Priorität 5: Organisches Memory im kontinuierlichen Feld

### Voraussetzung

Prioritäten 1 bis 4 müssen technisch stehen. Erst dann darf eine langsamere
memoryfähige Organisationsrolle untersucht werden. Sie bleibt Teil desselben
fortlaufenden Feldes.

### Ziel

Wiederholte lokale gemeinsame Feldwirkung kann eine spätere Feldfunktion
verändern, ohne feste Kanten oder eine Datenbank einzuführen.

Eine Feldtopologie ist dabei kein Ziel und kein Abschlusskriterium. Falls eine
räumlich oder relational beschreibbare Ordnung entsteht, gilt sie nur als
möglicher Befund der fortlaufenden Memoryentwicklung durch Weltkontakt.

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
- keine globale Auswahl oder Zieltopologie entscheidet die Bindung,
- die Wirkung entsteht während fortlaufender Weltteilnahme und nicht erst
  durch Offline-Verarbeitung oder Snapshotladen.

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
- Offline-Erholung kann bei reduziertem Weltkontakt und weiterlaufendem Feld
  relaxieren, stabilisieren oder lösen.

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

Der erste kleinste passive Kandidatenvergleich ist ausgeführt. Er prüft
eine einzelne lokale, begrenzte Feldempfänglichkeit pro bestehendem Neuron.
Der Kandidat trug eine spätere kausale Feldwirkung, wurde aber vollständig
durch einen gewöhnlichen begrenzten Integrator derselben lokalen Evidenz und
die fest eingesetzte Leserfunktion erklärt.

C1 ist deshalb als Organisationskandidat geschlossen und wird nicht in die
Runtime übernommen. Die zusätzliche beobachtbare Funktion einer verteilten
lokalen Organisation ist nun gegenüber fair begrenzten unabhängigen lokalen
Zuständen formal abgegrenzt. Skalare sind als digitale Darstellung nicht
grundsätzlich ausgeschlossen; maßgeblich sind gekoppelte Beanspruchung,
vollständige Lösung und Wiederbindung.

Die passive Versuchsmatrix für überlappende lokale Möglichkeiten A und B
sowie eine getrennte Kontrolle U ist vorregistriert. Sie definiert
Interaktionsreste, zwei gewöhnliche Lösungschallenges und erneute
B-Beanspruchung, ohne Kapazität oder Kante einzuführen.

Der technische Grundlauf ist umgesetzt. A und U verändern das reale schnelle
Feld vor der Angleichung; danach sind `I_AB`, `I_UB`, beide Lösungschallenges
und beide Wiederbindungszweige exakt durch die neutrale Runtime erklärt.

Der Zulassungsvertrag für einen zweiten passiven Organisationskandidaten ist
formuliert. Er verlangt, dass A bereits die Zustandsentwicklung unter
identischer B-Evidenz verändert; eine erst im festen Leser entstehende Wirkung
ist unzulässig.

Der konzeptionelle Familienvergleich ist abgeschlossen. Unabhängige Spuren,
lokale Empfänglichkeit, explizite Kanten, Normalisierung, Oszillatoren,
Ressourcenträger und Reservoirs sind als C2-Familien verworfen. Nur eine
gekoppelte lokale Feldverformung bleibt bedingt offen.

Die Baselineklassen B1 bis B6 sind jetzt operational und durch einen
gemeinsamen Zustands-, Radius-, Parameter-, Präzisions-, Zeit- und Leserbudget
gebunden. B5 ist auf eine feste lokale Rekurrenz mit konstanten Koeffizienten
und genau einer vorregistrierten punktweisen Nichtlinearität begrenzt. Sie ist
damit stark, umfasst aber nicht mehr jede beliebige lokale Zustandsmaschine.

Die K6-Vorprüfung ist abgeschlossen. Gekoppelte lokale Feldverformung benennt
die gewünschte geschichtsabhängige Mitprägung, begründet aber noch keine
lokale Naturbedingung für Bildung, vollständige Lösung und andere
Wiederbindung. Ihre konkreten Lesarten fallen derzeit in B1 bis B6 oder führen
Kante, Ressource beziehungsweise Historienarchiv wieder ein. K6 wird daher
nicht implementiert.

Der Rollenabgleich ist abgeschlossen. `activation` ist der schnelle kausale
Feldzustand, `afterimage` eine einseitige feste Kurzzeitspur, `perception` und
lokale Feldproben werden taktweise neu gebildet und Persistenz erhält nur
Vorhandenes. Keine Rolle trägt den vollständigen Memory-Lebenszyklus.

Eine zusätzliche kausal gelesene Zustandsrolle ist deshalb funktional
notwendig. Der darstellungsoffene Memory-Substratvertrag ist formuliert. Er
trennt feste digitale Naturbedingungen von den ausschließlich durch
Weltgeschichte entstehenden Prägungen, ohne Variable, Kante, Topologie oder
Gleichung festzulegen.

Der enge
[MINI_DIO-Abgleich](docs/architektur/049_MINI_DIO_MEMORY_SUBSTRAT_ABGLEICH.md)
ist abgeschlossen. Das alte System trug ein kontinuierliches Feld mit
selbstlimitierender Vorzustandsspur, intrinsisch beobachtbare Eigenform und
eine passive bewegliche Beziehungsgeschichte. Keine dieser Ebenen erfüllte
den vollständigen feldlokalen Memory-Lebenszyklus.

Die feste indexgerichtete Neuronenkette und die erst bei Weltfinalisierung
gebildeten Observerbeziehungen werden nicht übernommen.

Die
[lokale Ereignisquellgrenze](docs/architektur/050_LOKALE_EREIGNISQUELLGRENZE.md)
ist bestimmt. Der atomare `MCMNeuronDrive` trägt bereits Eigenzustand,
lokales Vorfeld, Weltkontakt und Organismuszeit. Eine eigene Ereignisprägung
existiert nicht; die frühere Übergangsevidenz war ein passiver fester Leser
und entsprach exakt der Ein-Schritt-Nachbarschaft.

Der
[atomare Zustandsrollen-Erweiterungsvertrag](docs/architektur/051_ATOMARER_ZUSTANDSROLLEN_ERWEITERUNGSVERTRAG.md)
ist formuliert. Eine spätere Memory-Rolle müsste sichtbar zum lokalen
Neuronenzustand gehören, atomar mit der vollständigen nächsten Schicht
veröffentlicht und vollständig im Snapshot getragen werden. Eine direkte
Memory-Nachbarprobe bleibt gesperrt, weil sie bereits eine feste zweite
Kopplungsarchitektur vorgeben würde.

Der
[Zulässigkeitsaudit der opaken Nullzustandshülle](docs/architektur/052_ZULAESSIGKEITSAUDIT_OPAKE_NULLZUSTANDSHUELLE.md)
ist abgeschlossen. Eine leere Hülle würde bereits lokalen Slot,
Serialisierungsform und Migration festlegen, aber keine Memory-Funktion
prüfen. Sie wird nicht implementiert.

Der Vertrag der
[kausalen Zustandsäquivalenz](docs/architektur/053_KAUSALE_ZUSTANDSAEQUIVALENZ.md)
ist formuliert. Nicht Rohdatenmenge, sondern unterschiedliche spätere
Feldtrajektorien unter identischen zulässigen Zukünften begrenzen den
notwendigen Informationsgehalt einer späteren Memory-Rolle.

Die
[weltbegründete Relevanzgrenze](docs/architektur/054_WELTBEGRUENDETE_RELEVANZGRENZE.md)
ist formuliert. Vergangene Weltgeschichte muss nach Angleichung des schnellen
Zustands Information über eine noch unbekannte spätere Rezeptorfortsetzung
tragen. Ein beliebiges Geschichtsbit mit festem Leser genügt nicht.

Die
[minimale passive Weltfamilie der verdeckten Fortsetzung](docs/architektur/055_MINIMALE_PASSIVE_WELTFAMILIE_VERDECKTE_FORTSETZUNG.md)
ist vorregistriert. Gespiegelte sichtbare Anfluggeschichten werden durch eine
lange verdeckte Phase bis zur exakten schnellen Zustandsangleichung von neuen
gespiegelten Holdoutaustritten getrennt.

Der
[Weltbefund der verdeckten Fortsetzung](docs/forschung/006_VERDECKTE_FORTSETZUNG_WELTBEFUND.md)
trägt die vorregistrierte Weltabhängigkeit nach exakter Kollision der heutigen
Rezeptionsnull. Der vorhandene visuelle Rezeptor- und Feldpfad blieb
unverändert.

Leaky-Spur, Übergangszähler und fester Bewegungsautomat erklären diese einfache
Welt jedoch vollständig. Die
[nichtstationäre Weltbeziehungsgrenze](docs/architektur/056_NICHTSTATIONAERE_WELTBEZIEHUNGSGRENZE.md)
ist deshalb formuliert. Sie fordert Erhaltung, bedingte Lösung und erneute
Relevanz ohne Phasenlabel in einem kontinuierlichen Weltstrom.

Die
[minimale kontinuierliche Zwei-Beziehungs-Weltfamilie](docs/architektur/057_MINIMALE_KONTINUIERLICHE_ZWEI_BEZIEHUNGS_WELTFAMILIE.md)
ist vorregistriert. Sie verwendet einen ununterbrochenen Weltstrom, technisch
symmetrische Beziehungen `R0` und `R1`, Erfahrungsstufen `0/1/2/4/8`,
verschobene Wechselstellen sowie K0 bis K7 und B0 bis B9.

Der äußere Generator, die passiven Observer und B0 bis B9 sind umgesetzt. Der
kanonische Lauf trägt `768` kontinuierliche Beobachtungen ohne Reset oder
Runtimemetadaten. Der
[Baselinebefund](docs/forschung/007_KONTINUIERLICHE_ZWEI_BEZIEHUNGS_BASELINEBEFUND.md)
zeigt, dass B6 nach mindestens einer neuen Erfahrung alle entscheidbaren
K3/K7-Holdouts vollständig erklärt.

Als Nächstes wird keine Memory-Datenform gewählt. Zuerst muss eine offene
Weltbeziehungsfunktion gegen den festen Zwei-Regime-Automaten abgegrenzt
werden. Updategleichung und Feldruntime bleiben gesperrt.

Die
[offene Weltbeziehungsform-Grenze](docs/architektur/058_OFFENE_WELTBEZIEHUNGSFORM_GRENZE.md)
ist formuliert. Nicht weitere Regime, sondern neue konkrete Beziehungswerte
und neue Anfluglagen bilden die nächste Funktionsgrenze. Feste Zwei-Punkt-,
Ausgleichs- und rekursive Schätzer bleiben zwingende Gegenmodelle.

Der
[Weltträgeraudit](docs/architektur/059_AUDIT_AFFINE_UND_LOKALE_DEFORMATIONSWELT.md)
ist abgeschlossen. Reine Verschiebung bleibt zu schwach, die affine Hauptwelt
zu global vorstrukturiert und eine freie Lookupwelt nicht identifizierbar.
Eine lokal stetige, nachweislich nichtaffine Deformationswelt ist bedingt
zugelassen.

Die
[minimale lokal stetige Deformationswelt](docs/architektur/060_MINIMALE_LOKAL_STETIGE_DEFORMATIONSWELT.md)
ist vorregistriert. Vier nichtaffine Formen, lokale Holdouts, D0 bis D5, G0
bis G7 sowie L0 bis L9 sind bindend festgelegt. Die erwartete Grenze ist eine
vollständige Erklärung durch die feste stückweise lineare Baseline L4. Der
[Baselinebefund](docs/forschung/008_LOKALE_DEFORMATIONSWELT_BASELINEBEFUND.md)
bestätigt diese Grenze für 110 von 110 fair identifizierbaren Holdouts.

Die
[feldgetragene Beziehungswirkungsgrenze](docs/architektur/061_FELDGETRAGENE_BEZIEHUNGSWIRKUNGSGRENZE.md)
definiert den offenen Mangel: Nicht eine bessere äußere Vorhersage fehlt,
sondern eine aus Weltkontakt entstandene lokale Zustandsdifferenz, die bereits
vor dem Austritt kausal im Feld wirkt.

Der
[Kandidatenfamilienaudit](docs/architektur/062_KANDIDATENFAMILIEN_FELDGETRAGENE_BEZIEHUNGSWIRKUNG.md)
verwirft zusätzliche Nachhallspuren, Kontaktpfade, unabhängige
Empfänglichkeit, adaptive Kanten, Ressourcen, Oszillatoren und Archive. Nur
ein lokales hysteretisches Feldmedium bleibt bedingt prüfbar.

Als Nächstes wird ausschließlich geprüft, ob die heutige atomare
Feldtransition eine intrinsische lokale Beanspruchungsquelle bereitstellt.
Memory-Rolle und Feldruntime bleiben geschlossen.

Der
[Audit der intrinsischen lokalen Feldbeanspruchungsquelle](docs/architektur/063_AUDIT_INTRINSISCHE_LOKALE_FELDBEANSPRUCHUNGSQUELLE.md)
bestätigt den momentanen Diffusionsfluss als bereits kausal vorhandene lokale
Feldwirkung. Gradient, Fluss und Divergenz sind jedoch vollständig aus
`activation`, fester Anatomie und Reaktionszeit ableitbar. Sie bilden keine
eigenständige geschichtliche Rolle.

Als Nächstes wird nur eine passive Redundanz-Nullprüfung umgesetzt. Sie darf
nichts akkumulieren, nichts zurückschreiben und die Runtime nicht verändern.

Die passive Prüfung ist umgesetzt. Der
[Redundanzbefund des instantanen Feldflusses](docs/forschung/009_INSTANTANER_FELDFLUSS_REDUNDANZBEFUND.md)
zeigt die vollständige Identität von gerichtetem Nachbarfluss, lokaler
Divergenz und bestehendem Diffusionsgenerator. Der Observer bleibt ohne
Rückschreibung und ohne neue Zustandsrolle.

Als Nächstes wird vor weiterer Mechanik ausschließlich auditiert, ob die feste
lokale Diffusionsanatomie natürliche Lösung und Wiederbindung grundsätzlich
ausschließt. F8, Memory-Rolle und Runtime bleiben geschlossen.

Der
[Audit der festen Diffusionsanatomie](docs/architektur/064_GRENZE_DER_FESTEN_DIFFUSIONSANATOMIE.md)
ist abgeschlossen. Die Runtime kann schnelle Feldlagen relaxieren und neuen
Weltkontakt aufnehmen. Sie kann aber keine funktionale Beziehung freigeben
oder anders neu binden, weil ihre Kopplung unverändert ist und keine gebundene
Beziehungsressource existiert.

Dies gibt keine adaptiven Kanten frei. Die technische Kandidatensuche wird
gestoppt, bis die allgemeine physische Grundanforderung eines prägbaren und
vollständig erneut prägbaren endlichen Substrats geklärt ist.

Die
[physische Mindestanforderung](docs/architektur/065_PHYSISCHE_MINDESTANFORDERUNG_ORGANISCHES_MEMORY_SUBSTRAT.md)
ist jetzt geklärt: Das Substrat muss begrenzte, lokal feldgetriebene und
funktional reversible Pfadabhängigkeit tragen. Die vorhandene Feldwirkung kann
Schreibursache sein, darf aber nicht einfach als zusätzliche Flussspur kopiert
werden.

Als Nächstes wird rein konzeptionell geprüft, ob ein einzelner begrenzter
lokaler Zustand diesen Lebenszyklus ohne Leaky-Spur, Schwellenautomat oder
adaptive Kante tragen kann. Runtime und Zustandsrollen bleiben geschlossen.

Der
[Audit des isolierten lokalen Substratzustands](docs/architektur/066_GRENZE_EINES_ISOLIERTEN_LOKALEN_SUBSTRATZUSTANDS.md)
ist abgeschlossen. Ein Skalar kann Pfadabhängigkeit tragen, aber keine neue
robuste Lösungsfunktion begründen: Leaky-Zerfall bleibt nur asymptotisch;
endliche Lösung entsteht erst durch programmierte Zustandskollision oder feste
Leseräquivalenz.

Als Nächstes wird nur eine verteilte homogene Substratklasse abgegrenzt. Es
wird weder eine zweite willkürliche Variable noch eine Gleichung oder
Runtime-Erweiterung freigegeben.

Der
[Audit des homogen verteilten Skalarsubstrats](docs/architektur/067_GRENZE_EINES_HOMOGEN_VERTEILTEN_SKALARSUBSTRATS.md)
ist abgeschlossen. Das vorhandene Feld ist bereits räumlich verteilt; seine
positive symmetrische Diffusion dämpft nichtkonstante Modi und liefert keine
neue Memory- oder Wiederbindungsfunktion.

Priorität bleibt vor Runtime-Code die Prüfung genau einer minimalen
Rollenklasse: vorhandene schnelle Feldlage und eine mögliche lokale homogene
Materialdisposition. Es wird noch weder ein Zustand noch eine Reaktionsregel
ausgewählt.

Der
[Audit der reziproken Feld-Material-Kopplung](docs/architektur/068_REZIPROKE_FELD_MATERIAL_KOPPLUNG_UND_KONSTITUTIVE_SAETTIGUNG.md)
ist abgeschlossen. Reziprozität allein wählt keine Mechanik aus; alle
naheliegenden Lesarten fallen auf bereits geprüfte Spuren, Empfänglichkeit,
K6/F8, adaptive Leitfähigkeit, Ressourcen oder Attraktoren zurück.

Die abstrakte Kandidatensuche stoppt. Nächste Priorität ist keine
Runtime-Umsetzung, sondern die einmalige Klärung, ob ein unabhängiges lokales
Passivitäts- und Feldarbeitsprinzip eine Materialzustandsklasse tatsächlich
einschränkt. Ohne diese Begründung bleibt die Zustandsrolle geschlossen.

Der
[Passivitäts-Nullbefund](docs/forschung/010_PASSIVITAET_DES_BESTEHENDEN_FELDES_NULLBEFUND.md)
und der
[abschließende Architekturaudit](docs/architektur/069_PASSIVITAET_FELDARBEIT_UND_ENDE_DER_SUBSTRATHERLEITUNG.md)
zeigen: Die vorhandene Runtime ist bereits mathematisch dissipativ. Diese
Eigenschaft erzwingt keinen zusätzlichen Material- oder Memory-Zustand.

Die Substratkandidatensuche wird nicht automatisch fortgesetzt. Priorität ist
Weg A: bestehendes Feld unter längerer realer Audio- und Videoweltteilnahme
beobachten, ohne Runtime-Memory einzubauen. Eine explizite Materialhypothese
erfordert zuvor eine bewusste Richtungsentscheidung.

Diese Richtungsentscheidung ist inzwischen erfolgt: Für die technische
Entwicklung wird zunächst eine kontrollierte prozedurale Audio-Video-Welt
verwendet. Als ausdrückliche biologische Substrathypothese wird ein passiver
lokaler Synapsenkandidat mit flexibler und stabilisierter Zeitlage sowie lokaler
Homeostase geöffnet.

Die
[kontrollierte Testwelt und der lokale Synapsenkandidat](docs/architektur/070_KONTROLLIERTE_TESTWELT_UND_LOKALER_SYNAPSENKANDIDAT.md)
sind umgesetzt. Beide Testwelten durchlaufen dieselben Rezeptoren und dieselbe
gemeinsame Feldruntime. Der Kandidat liest nur abgeschlossene lokale
Koaktivität und schreibt noch nicht in die Runtime zurück.

Als Nächstes folgt kein direkter Memory-Einbau. Zuerst muss der passive
Kandidat in den identischen Weltzweigen gegen Null, unmittelbare Koaktivität,
eine Leaky-Spur und feste lokale Kopplung geprüft werden.

Dieser
[Baselinevergleich](docs/forschung/011_PASSIVER_SYNAPSENKANDIDAT_BASELINEBEFUND.md)
ist abgeschlossen. Die flexible Kandidatenlage ist exakt eine Leaky-Spur. Die
stabilisierte Lage trägt nach identischer Probe `0,000827` Zweigdifferenz, eine
faire Zwei-Leaky-Kaskade bereits `0,000796`.

Das genügt nicht für Runtime-Memory. Als nächstes wird der unveränderte
Kandidat einmal über Aufbau, Unterbrechung, Lösung und andere
Wiederbeanspruchung geführt. Bleibt auch dieser Lebenszyklus durch die
Zwei-Leaky-Baseline erklärt, wird der Kandidatenzweig beendet.

Der
[Lebenszyklusbefund](docs/forschung/012_SYNAPTISCHER_MEMORY_LEBENSZYKLUS_NEGATIVBEFUND.md)
beendet den Kandidatenzweig. Der Kandidat prägte alle 290 lokalen Beziehungen.
Nach acht Unterbrechungsphasen betrug die alte stabilisierte Lage `114,8 %`
ihres Aufbauwertes; vollständige Lösung trat nicht ein. Kontakt B veränderte
Kandidat und Zwei-Leaky-Baseline ähnlich.

Der Kandidat wird nicht parametrisch angepasst und nicht an die Runtime
angeschlossen. Vor neuem Memory-Code ist ausschließlich zu klären, ob lokale
zeitliche Ursache oder Reihenfolge eine selektive Prägungsquelle begründet,
ohne Schwelle, Gewinnerregel oder Zieltopologie.

Der
[passive Zeitrichtungsbefund](docs/forschung/013_LOKALE_ZEITRICHTUNG_KEINE_SELEKTIVE_PRAEGUNGSQUELLE.md)
beantwortet auch diese enge Frage negativ. Die Reihenfolge `A -> B` gegenüber
`B -> A` ist in den abgeschlossenen Feldzuständen sichtbar, betrifft aber alle
290 gerichteten lokalen Beziehungen. Der Wert ist vollständig ein fester
Ein-Schritt-Leser und keine lokale Zustandsänderung.

Priorität bleibt deshalb organisches Memory, aber nicht als weitere
Beobachterformel. Vor neuer Mechanik muss eine lokale physische Zustandsrolle
begründet werden, die zeitliche Ursache im Feld tragen, begrenzen und wieder
vollständig lösen kann. STDP-Gewichte, Schwellen und adaptive Kanten sind
nicht freigegeben.

Diese Rolle wird nun als bewusste, biologisch orientierte Hypothese geöffnet:
[strukturelles lokales Kontaktsubstrat](docs/architektur/071_BEWUSSTE_HYPOTHESE_STRUKTURELLES_LOKALES_KONTAKTSUBSTRAT.md).
Nicht ein Wert pro Beziehung, sondern begrenztes räumliches Kontaktmaterial
des einzelnen MCM-Neurons soll als mögliche Substratklasse untersucht werden.

Nächste Priorität ist ausschließlich der anatomische Zustandsvertrag. Er darf
noch keine Wachstumsregel, Kopplung, Stabilisierung oder Runtime-Rückwirkung
enthalten.

Der
[anatomische Zustandsvertrag](docs/architektur/072_ANATOMISCHER_ZUSTANDSVERTRAG_DES_KONTAKTSUBSTRATS.md)
ist umgesetzt. Die bestehende Welt erzeugt 84 neutrale Eigentümerzustände mit
insgesamt 336 partnerlosen lokalen Oberflächen. Sämtliches endliches Material
bleibt ungebunden; die Feldruntime bleibt unverändert.

Als Nächstes wird keine Wachstumsregel gebaut. Zuerst wird bestimmt, welche
bereits vorhandene lokale Feldursache das Material überhaupt kausal
beanspruchen dürfte, ohne durch einen nachträglichen Observer erzeugt zu
werden.

Die spätere Reflexionsrichtung ist parallel begrifflich geschlossen:
[Vorsprachliche Reflexion und spätere Sprachresonanz](docs/architektur/073_VORSPRACHLICHE_REFLEXION_UND_SPAETERE_SPRACHRESONANZ.md).
Sie verändert die aktuelle Priorität nicht. Organisches Memory und eine
getragene Erfahrungsstruktur müssen vor jeder inneren Rückführung stehen.

Kein Alphabet, Sprachmodell oder Wortschatz wird als Abkürzung in den
Organismuskern eingebaut.

Die lokale Quellzuordnung ist nun als
[passiver Schreibursachenvertrag](docs/architektur/074_PASSIVER_SCHREIBURSACHENVERTRAG_DES_KONTAKTSUBSTRATS.md)
umgesetzt. Vorhandene lokale Vortaktproben und der momentane gerichtete
Feldfluss lassen sich den 336 neutralen Oberflächenrichtungen zuordnen, ohne
Material oder Feld zu verändern.

Eigenaktivierung und realer Rezeptorkontakt bleiben Ursachen des jeweiligen
Neurons und wählen keine Oberfläche. Der Vertrag enthält deshalb weiterhin
keine Wachstums-, Gewinner- oder Materialtransportregel.

Nächste Priorität ist ein reiner Materialbilanz- und Symmetrievertrag. Er muss
klären, welche Erhaltung und welche lokale Gegenseitigkeit jede spätere
Umverteilung erfüllen müsste, bevor eine konkrete Dynamik gebaut wird.

Dieser
[Materialbilanz- und Symmetrievertrag](docs/architektur/075_MATERIALBILANZ_UND_SYMMETRIEVERTRAG_DES_KONTAKTSUBSTRATS.md)
ist festgelegt. Kontaktmaterial bleibt Eigentum des einzelnen Neurons.
Ungebundener Anteil und eigene Oberflächenmengen müssen in jedem atomaren
Übergang exakt dieselbe endliche Gesamtmenge erhalten.

Symmetrie bedeutet Äquivarianz: Die Welt darf räumliche Unterschiede
verursachen, die technische Regel darf jedoch keine Richtung, Modalität,
Neuronennummer oder Iterationsreihenfolge bevorzugen. Gegenseitige Berührung
wird nicht durch gleiche Werte oder automatische Kopplung erzwungen.

Als Nächstes wird nur ein passiver Zulassungsrahmen gebaut, der spätere
Kandidaten gegen diese Grenzen prüft. Er enthält selbst keine
Materialbewegung und keine Runtime-Rückwirkung.

Dieser
[passive Zulassungsrahmen](docs/architektur/076_PASSIVER_ZULASSUNGSRAHMEN_FUER_MATERIALFORTSCHREIBUNGEN.md)
ist umgesetzt. Er prüft Herkunft, Eigentümererhaltung, Nichtnegativität,
Nullinvarianz und transformierte Symmetrie eines vollständigen
Materialvorschlags. Der Vorschlag wird weder angewendet noch an das
Organismusfeld angeschlossen.

Vor einem ersten Kandidaten wird als Nächstes geprüft, welche Klassen lokaler
Umverteilung nicht bereits nur Flussintegrator, Leaky-Spur, Schwellenautomat
oder adaptives Kantengewicht unter anderem Namen sind.

Der
[Audit der reinen Oberflächenmenge](docs/architektur/077_GRENZE_DER_REINEN_OBERFLAECHENMENGE_UND_MINIMALE_MORPHOLOGIE.md)
zeigt eine Darstellungsgrenze: `surface_material` trägt Eigentümerschaft und
Bilanz, aber noch keine räumliche Berührung. Jeder direkte Mengenleser würde
wieder zu Richtungsgewicht, Integrator oder programmiertem Schwellenkontakt.

Die strukturelle Hypothese wird deshalb nicht verworfen, sondern präzisiert.
Vor einer Dynamik muss eine minimale partnerlose Morphologie Lage oder
Ausdehnung, Rückzug und geometrische Berührung unterscheiden können.

Nächste Priorität ist ausschließlich dieser räumliche Zustandsvertrag. Er
darf noch keine Wachstumsregel, Kollisionwirkung oder Feldrückwirkung
enthalten.

Der
[minimale räumliche Zustandsvertrag](docs/architektur/078_MINIMALER_RAEUMLICHER_ZUSTANDSVERTRAG_DES_KONTAKTMATERIALS.md)
ist festgelegt. Jede lokale Richtung erhält ein partnerloses radiales
Materialprofil zwischen neuronennaher Lage und geometrischer Grenzfläche.
Damit werden Rückzug, Annäherung und mögliche Berührung darstellbar, ohne eine
Kante zu speichern.

Die konkrete radiale Auflösung und jede Bewegung bleiben offen. Nächste
Priorität ist nur die neutrale endliche Profilanatomie: alle Profilbereiche
null, sämtliches Material ungebunden, keine Berührung und keine Feldwirkung.

Diese
[neutrale radiale Profilanatomie](docs/architektur/079_NEUTRALE_ENDLICHE_ANATOMIE_DER_RADIALEN_MORPHOLOGIE.md)
ist umgesetzt. In der kontrollierten Audio-Video-Anatomie entstehen bei
expliziter Vier-Zellen-Geometrie 336 Richtungsprofile mit 1344 leeren
radialen Zellen. Sämtliches Material bleibt ungebunden.

Nächste Priorität ist keine Bewegungsgleichung, sondern die Abgrenzung
konservativer radialer Transportklassen gegen Leaky-Spur, feste Zielposition,
Schwellenkontakt und bevorzugte Grenzfläche.

Die
[Transportklassenabgrenzung](docs/architektur/080_ABGRENZUNG_KONSERVATIVER_RADIALER_TRANSPORTKLASSEN.md)
verwirft positive Diffusion, feste Potentiale, Wachstum und Zerfall als
ersten Morphologiekandidaten. Nur konservative endliche Advektion bleibt
passiv offen, weil sie räumliche Unterstützung bewegen und geometrisch
trennen kann, ohne Material zu erzeugen oder ein Kontaktgewicht zu lesen.

Eine Geschwindigkeitsursache ist ausdrücklich noch nicht gewählt. Nächste
Priorität ist nur ein passiver radialer Flussvertrag, der Transportvorschläge
auf Bilanz, Nichtnegativität, Zeit und Auflösung prüft, aber selbst keine
Bewegung erzeugt.

Die bisherige Rezeptoranatomie wurde anschließend um eine zuvor fehlende
Ursachenklasse ergänzt:
[kontinuierlicher endogener Feldkontakt](docs/architektur/081_KONTINUIERLICHER_ENDOGENER_FELDKONTAKT.md).
Er bildet permanent möglichen Eigenkontakt nicht als künstliches Rauschen,
sondern als offene weitere Rezeptorherkunft im selben gemeinsamen MCM-Feld
ab. Die technische Rezeptorfläche ist zustandslos, hält keine Werte und
erzeugt weder Stimmung noch Memory.

Nächste Priorität ist eine kleine kontrollierte endogene Testquelle mit
langsamen und schnellen, aber unbezeichneten Verläufen. Sie muss zusammen mit
äußerem Kontakt durch dieselbe Feldruntime laufen. Erst danach wird beurteilt,
welche vorhandenen Feldursachen überhaupt als Kandidaten für den weiterhin
passiven radialen Flussvertrag infrage kommen.

Diese
[kontrollierte endogene Testquelle](docs/architektur/082_KONTROLLIERTE_ENDOGENE_TESTQUELLE.md)
ist umgesetzt. Ihre Verläufe sind endlich, explizit, reproduzierbar und
bedeutungsfrei. Äußerer und endogener Kontakt erreichen im selben atomaren
Schritt dieselbe MCM-Neuronenschicht, ohne im Verteiler fusioniert zu werden.

Nächste Priorität ist eine passive Ursachenüberlagerungs-Nullprüfung. Sie
muss zeigen, ob beide Herkünfte unter der bestehenden festen Felddiffusion
und dem schnellen Nachhall lokal unterscheidbar bleiben. Dabei wird weder
Memory noch Materialbewegung ergänzt.

Die
[passive Ursachenüberlagerungs-Nullprüfung](docs/architektur/083_PASSIVE_URSACHENUEBERLAGERUNGS_NULLPRUEFUNG.md)
ist umgesetzt. Äußerer und endogener Kontakt bleiben nach der vorhandenen
Felddiffusion und dem schnellen Nachhall als kausale Endsignaturen
unterscheidbar. Der gemeinsame Zweig ist vollständig aus beiden
Einzelwirkungen rekonstruierbar.

Damit ist zugleich die Grenze klar: Die bestehende Feldruntime überlagert die
Ursachen linear und erzeugt keinen zusätzlichen Organisationsrest. Der
endogene Kontakt ist eine tragfähige Feldursache, aber noch keine
Memory-Mechanik oder Materialgeschwindigkeit.

Nächste Priorität ist wieder der passive radiale Flussvertrag. Er darf
Transportvorschläge prüfen, aber weder aus äußerem noch aus endogenem Kontakt
selbst eine Bewegung erzeugen.

Der
[passive radiale Flussvertrag](docs/architektur/084_PASSIVER_RADIALER_FLUSSVERTRAG.md)
ist umgesetzt. Vollständige Grenzflussvorschläge werden auf Herkunft,
Auflösung, geschlossene Eigentümergrenzen, Nichtnegativität, lokale Bilanz,
Nullinvarianz und Iterationsneutralität geprüft.

Ein angenommener Vorschlag liefert nur einen passiv rekonstruierten möglichen
Folgezustand. Der Vertrag erzeugt keine Geschwindigkeit, verifiziert keine
kausale Quelle und schreibt nicht in die Runtime.

Nächste Priorität ist die Abgrenzung möglicher Flussursachen. Momentaner
lokaler Feldfluss, Aktivierungsdifferenz, äußerer und endogener
Rezeptorkontakt sowie schneller Nachhall werden zunächst darauf geprüft, ob
sie nur eine räumliche Integrator- oder feste Bewegungsregel erzeugen würden.

Die
[Abgrenzung direkter radialer Flussursachen](docs/architektur/085_ABGRENZUNG_DIREKTER_RADIALER_FLUSSURSACHEN.md)
ist abgeschlossen. Rezeptorkontakt, Eigenaktivierung und eigener schneller
Nachhall besitzen keine Oberflächenrichtung. Eine direkte Nutzung müsste
Außenbewegung, Innenbewegung oder isotrope Expansion programmieren.

Lokal abgetasteter Nachhall gehört nicht zum bestehenden
Kontakt-Drive-Vertrag und bleibt außerdem eine feste Leaky-Spur. Nur der
signierte momentane lokale Feldfluss besitzt bereits Richtung und
geometrisches Vorzeichen.

Nächste Priorität ist ausschließlich eine kontrafaktische passive Isolation
dieses Feldflusses. Sie darf einen Flussvorschlag erzeugen und durch Vertrag
084 prüfen, aber nicht in die Runtime schreiben.

Die
[kontrafaktische Feldfluss-Transportgrenze](docs/architektur/086_KONTRAFAKTISCHE_FELDFLUSS_TRANSPORTGRENZE.md)
ist erreicht. Beide globalen Vorzeichenabbildungen des signierten Feldflusses
sind bilanziell zulässig und bewegen gleich viel Material, erzeugen aber
unterschiedliche Morphologien.

Weder radiale Polarität noch Umrechnungsskala folgen aus dem MCM-Feld. Die
Materialänderung ist vollständig das Zeitintegral der von außen eingesetzten
Abbildung. Eine direkte Feldfluss-Geschwindigkeitsregel wird deshalb nicht
freigegeben.

Damit ist eine Stopplinie erreicht. Keine weitere Bewegungsformel wird
implementiert, bevor die physische Rolle des Kontaktmaterials konzeptionell
geklärt oder die Kontaktmorphologie als Memory-Substrathypothese neu bewertet
wurde.

Der
[konzeptionelle Substratrollenaudit](docs/architektur/087_KONZEPTIONELLER_SUBSTRATROLLENAUDIT.md)
ist abgeschlossen. Eine deformierbare Grenzflächenressource bleibt als
unabhängig denkbare Anatomie suspendiert, besitzt im heutigen Feld aber keine
begründete Materialphysik. Gespeicherte strukturelle Energie wird verworfen,
weil ohne Arbeits- und Speicherbilanz nur Integrator, Leaky-Spur oder
adaptives Gewicht umbenannt würden.

Aktueller Architekturstand ist deshalb: Die Kontaktmorphologie bleibt passive
Anatomie und Labor, aber kein aktiver Memory-Kandidat. Es entstehen keine
weitere Bewegungsformel und keine Runtime-Anbindung.

Nächste Priorität ist die Rückkehr zum darstellungsoffenen
Memory-Substratvertrag. Zunächst wird nur geklärt, welche organismuseigene
Zustandsgröße durch Feldteilnahme verändert werden kann und auch dann eine
unabhängige physische Rolle besitzt, wenn sie niemals eine Beziehung speichert.

Der
[Audit der Organismusgrenze](docs/architektur/088_AUDIT_DER_ORGANISMUSGRENZE.md)
ist abgeschlossen. Die heutige Runtime kann Aktivierung, Nachhall und
gegenwärtige Wahrnehmung verlieren, ohne ihre Fähigkeit zur nächsten
Feldaufnahme zu verlieren.

Feste Anatomie, Rezeptordocks, Feldparameter, Organismuszeit und Snapshot sind
technische Betriebsbedingungen. Sie werden durch Weltkontakt weder
beansprucht noch erhalten oder erneuert. Die bisherige Energie- und
Ressourcengrenze ist nur ein geschlossener Architekturvertrag und keine
vorhandene organismische Größe.

Damit besitzt das System ein gemeinsames Wahrnehmungsfeld, aber noch keine
eigenständige organismische Erhaltungsbedingung. Keine Energie-, Kapazitäts-,
Ermüdungs-, Kopplungs- oder Selbstregulationsvariable wird daraus freigegeben.

Nächste Priorität ist ein darstellungsoffener Erhaltungsfunktionsvertrag. Er
muss zuerst benennen, welche konkrete Feldfunktion beim Verlust einer
organismischen Größe beeinträchtigt wäre und wodurch Weltteilnahme dieselbe
Funktion erhalten oder erneuern könnte.

Der
[darstellungsoffene Erhaltungsfunktionsvertrag](docs/architektur/089_DARSTELLUNGSOFFENER_ERHALTUNGSFUNKTIONSVERTRAG.md)
ist formuliert. Er definiert observerunabhängigen Funktionsverlust, kausale
Veränderung durch reale Feldteilnahme, Wirkung auf die nächste Feldbildung und
Erneuerung durch weitere Teilnahme, ohne eine Zustandsgröße auszuwählen.

Der Abgleich bestätigt, dass keine vorhandene Runtime-Rolle diesen Vertrag
erfüllt. `activation`, `afterimage` und `perception` können Inhalt verlieren,
ohne die weitere Feldfähigkeit zu beeinträchtigen. Anatomie, Docks,
Feldparameter, Zeitvertrag und Snapshot sind technisch fest oder rein
rekonstruktiv.

Damit besitzt das System fortsetzbare Feldmechanik, aber noch keinen
nachgewiesenen Organismusprozess mit eigener Erhaltungsfunktion. Organisches
Memory und jede Energie-, Kapazitäts-, Ermüdungs-, Regenerations- oder
Selbstregulationsmechanik bleiben geschlossen.

Die nächste Priorität ist keine Implementierung. Zuerst ist grundsätzlich zu
entscheiden, ob nur das gemeinsame Wahrnehmungsfeld weiter untersucht oder
zusätzlich eine unabhängig von Memory begründete notwendige
Organismuserhaltungsfunktion gesucht werden soll.

Die Richtungsentscheidung für Weg B wurde im
[Vergleich notwendiger Organismusfunktionen](docs/architektur/090_VERGLEICH_NOTWENDIGER_ORGANISMUSFUNKTIONEN.md)
konzeptionell geprüft. Organisatorische Selbstaufrechterhaltung, Regulation
eigener Existenzbedingungen, eigenständige Weltbeteiligung und Stabilität
wurden als Funktionen verglichen, ohne biologische Mechanik zu übernehmen.

Keine dieser Funktionsfamilien ist im heutigen MCM-System intrinsisch
notwendig oder bereits organismisch getragen. Das Feld erzeugt und erhält
weder Anatomie, Docks, Zeitbasis noch Sensorquellen und besitzt keine autonome
Weltwirkung. Die simulierte Effektorwelt bleibt eine externe passive
Forschungsumgebung und beansprucht keine Autonomie.

Weg B gibt deshalb keinen Zustands- oder Runtime-Kandidaten frei. Das System
bleibt ein technisch fortsetzbares gemeinsames Wahrnehmungsfeld, aber noch
kein Organismusprozess im gewünschten Sinn. Organisches Memory bleibt
geschlossen.

Nächste Priorität ist kein weiterer Mechaniklauf. Für das langfristige Ziel
kann ein getrennter Grundlagenzweig untersuchen, ob ein digitaler Prozess die
Bedingungen seiner eigenen Weltteilnahme tatsächlich mit hervorbringen und
erhalten kann. Dieser Zweig beginnt ohne Zustandsvariable, Effektorfreigabe
oder Memory-Ziel.

Die Schlussfolgerung wurde anschließend enger gefasst: Geschlossen ist Weg B
als autonomer Organismusprozess mit eigener Selbstaufrechterhaltung. Ein
weltbezogener MCM-Speicher ist dadurch nicht grundsätzlich ausgeschlossen; ihm
fehlt nur eine automatisch tragende organismische Grundlage.

Der separate
[weltbezogene Sensorik-Handlungs-Konsequenzkreis](docs/architektur/091_WELTBEZOGENER_SENSORIK_HANDLUNGS_KONSEQUENZKREIS.md)
ist deshalb konzeptionell geöffnet. Die bestehende simulierte Welt kann eine
äußerlich ausgelöste Konsequenz bereits kausal und ursachenneutral über
Rezeptoren in das MCM zurückführen. Eine autonome Handlung ist dafür nicht
erforderlich.

Noch fehlen ein zweiter realer Konsequenzkanal und eine spätere Feldwirkung
über den schnellen Nachhall hinaus. Direkte Memory-, Ressourcen-, Reward-,
Objekt- und Effektorwahlmechanik bleiben geschlossen.

Nächste Priorität ist ausschließlich die passive Vorregistrierung einer
anonymen Welt-Konsequenz-Familie. Vor Code muss feststehen, dass die
Konsequenz ein tatsächlicher Weltzustand und kein Ergebnis- oder
Bedeutungslabel ist.

Die
[passive Vorregistrierung der anonymen Welt-Konsequenz-Testfamilie](docs/architektur/092_VORREGISTRIERUNG_ANONYME_WELT_KONSEQUENZ_TESTFAMILIE.md)
liegt nun vor. Sie verwendet ausschließlich den bestehenden
Welt-Rezeptor-MCM-Pfad und trennt vier Phasen: Ausgangskontakt, Konsequenz,
identische aktuelle Probe sowie eine zunächst geschlossene Angleichungs- und
Holdoutgrenze.

Der erste mögliche Befund bleibt eng:

```text
anonyme Weltkonsequenz
-> kausal unterscheidbare aktuelle MCM-Feldlage
```

Identische Gegenwartsproben, vollständige Zustandsausweisung,
Observerneutralität sowie Aufrufzahl- und Reihenfolgekontrollen sind
vorregistriert. Ein durch aktuellen Kontakt oder `afterimage` vollständig
erklärter Unterschied beendet den Schritt ohne neue Mechanik.

Nächste Priorität ist ein reiner Darstellbarkeitsaudit: Es wird geprüft, ob
Konsequenz, Nullkonsequenz, blockierte Rückkehr und gleiche Weltfolge bei
anderer technischer Provenienz bereits mit den vorhandenen Weltzuständen
ausgedrückt werden können. Noch wird kein Testcode ergänzt.

Der
[Darstellbarkeitsaudit der Welt-Konsequenzfälle](docs/architektur/093_DARSTELLBARKEITSAUDIT_WELT_KONSEQUENZFAELLE.md)
ist abgeschlossen. Konsequenz (`delta = -1 oder +1`), Nullkonsequenz
(`delta = 0`) und observerseitige Provenienz sind in der vorhandenen Ringwelt
eindeutig darstellbar. Die Provenienz erreicht den Rezeptor-MCM-Pfad
weiterhin nicht.

Die blockierte Rückkehr ist dort nicht darstellbar: Jeder Ringweltzustand
erzeugt zwingend einen one-hot Rezeptorkontakt. Die vorhandene
Verdeckungswelt kann zwar regulär kontaktfreie visuelle Rahmen erzeugen,
besitzt aber nicht denselben Interventions- und Provenienzvertrag. Ein
Vergleich über beide Weltmechaniken wäre kein kontrolliertes Gegenfaktum.

Der passive Lauf bleibt daher geschlossen. Nächste Priorität ist
ausschließlich die konzeptionelle Entscheidung für eine einzige vorhandene
Weltgrundlage, die sichtbare und weltseitig verdeckte Konsequenz unter
derselben Dynamik tragen kann. Es werden weder Sperrflag noch Rezeptorabbruch,
neue Weltmechanik oder Organismuszustand eingeführt.

Der erste Zehn-Sekunden-Lauf dieses Weges hat außerdem eine technische
Voraussetzung geklärt: Reale Rezeptorraten dürfen nicht aus angeforderten
Geräteraten abgeleitet werden, und langsame Feldberechnung darf den laufenden
Rezeptorkontakt nicht unterbrechen. Diese Vorarbeit verändert keine
Feldgleichung und führt keinen Memory-Zustand ein.
