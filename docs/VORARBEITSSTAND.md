# Vorarbeitsstand bis zum Forschungsstart

## Zweck

`MCM_FIELD_ORGANISM` befindet sich im technischen Aufbau. Die gegenwärtige
Arbeit schafft das gemeinsame Substrat, auf dem später belastbare
Feldforschung stattfinden kann.

Nicht jede Schnittstellenprüfung, Nullkontrolle oder Architekturentscheidung
ist ein Forschungsversuch. Solche Arbeiten werden ab jetzt als **Vorarbeit**
geführt.

## Drei getrennte Arbeitsarten

### 1. Technische Vorarbeit

Hierzu gehören:

- Kamera-, Mikrofon- und spätere Sensoradapter,
- sensorspezifische Rezeptorflächen,
- Rezeptorenverteiler und offene Docks,
- gemeinsame Organismuszeit,
- atomare Aktualisierung der MCM-Neuronenschicht,
- Zustands-, Persistenz- und Observergrenzen,
- inaktive Anschlusspunkte für spätere Reflexion und Offline-Erholung.

Diese Arbeiten dürfen programmiert werden, weil sie die technische Weltgrenze
und das digitale Substrat herstellen. Sie dürfen keine Bedeutung,
Zieltopologie, feste Beziehung oder gewünschte Entwicklung vorgeben.

### 2. Technische Absicherung

Unit-, Integrations- und Smoke-Tests sichern ausschließlich:

- Datenformate,
- Kausalität,
- Herkunft,
- Zeitlage,
- numerische Grenzen,
- Reihenfolgeunabhängigkeit,
- Reproduzierbarkeit,
- Trennung von Runtime und Observer.

Solche Tests erhalten keine Forschungsnummer und normalerweise keinen eigenen
Methodik- oder Befundtext. Ein sinnvoller technischer Meilenstein wird kompakt
in diesem Dokument fortgeschrieben.

### 3. Spätere Forschungsversuche

Ein Forschungsversuch untersucht eine offene Feldfunktion, deren Ergebnis
nicht bereits durch die technische Konstruktion feststeht. Erst dann werden
Hypothese, Baselines, Interventionen, Abbruchkriterien und Befund getrennt
dokumentiert.

## Derzeit vorhandene Vorarbeit

Die technische Strecke umfasst:

```text
reale Audio- und Videoquelle
-> auditive und visuelle Rezeptoren
-> neutraler Rezeptorenverteiler
-> offene MCM-Docks
-> gemeinsame MCM-Neuronenschicht
-> gemeinsamer technischer Feldzustand
```

Zusätzlich vorhanden sind:

- passive Beobachtung ohne Rückschreibung,
- technische Audio- und Videozeitlagen,
- kontrollierte simulierte Weltkontakte,
- lokale Neuronen- und Vorfeldproben,
- vollständige JSON-Snapshots des aktuellen technischen Feldzustands,
- streng geprüfte Wiederherstellung mit identischer nächster Feldfortsetzung,
- begrenzte mehrtaktige Feldsitzungen mit lückenloser Organismuszeit,
- unveränderte Dock-, Neuronen- und Geometrieidentitäten über eine Sitzung,
- getrennte Verträge für spätere Selbstregulation,
- eine konzeptionelle Grenze für organisches Memory,
- die dokumentierte Abgrenzung statischer Leser und fester Rekurrenz.

Diese Punkte belegen technische Reife. Sie belegen noch keine entwickelte
Feldtopologie, kein organisches Memory und keine Semantik.

## Was bis zur Grundsystem-Freigabe noch fehlt

Das Grundsystem gilt erst dann als technisch stehend, wenn folgende Punkte in
einem zusammenhängenden Lauf erfüllt sind:

1. Audio und Video gelangen fortlaufend über ihre eigenen Rezeptoren in den
   neutralen Verteiler.
2. Herkunft, Geometrie und reale Zeitlage bleiben bis zu den Docks erhalten.
3. Alle Docks wirken auf dieselbe MCM-Neuronenschicht.
4. Ein Feldtakt wird vollständig aus einem abgeschlossenen vorherigen Zustand
   berechnet.
5. Die technische Neuronenschicht besitzt nur lokale, semantikfreie
   Trägerzustände.
6. Ein vollständiger Organismuszustand kann technisch als Snapshot gesichert
   und unverändert wiederhergestellt werden, ohne daraus eine
   Bedeutungsdatenbank zu machen.
7. Observer, Debugausgaben und Forschungsarchive können die Runtime nicht
   verändern.
8. Reflexion und Offline-Erholung sind bis zu ihrer späteren Untersuchung
   technisch inaktiv.
9. Ein endlicher Audio-Video-End-to-End-Lauf ist reproduzierbar und frei von
   versteckter Fusion, Auswahl oder Rückschreibung.
10. Der gesamte Pfad besitzt eine verständliche öffentliche
    Zustandsbeschreibung.

Die Erfüllung dieser Punkte ist eine **Grundsystem-Freigabe**, noch kein
Forschungsbefund.

## Aktueller Abgleich

| Kriterium | Stand |
|---|---|
| 1. Fortlaufender Audio-Video-Pfad | teilweise; reale Rezeptorzustände entstehen fortlaufend, ihre unterschiedlichen Eigenraten besitzen noch keine begründete gemeinsame Feldzeitübergabe |
| 2. Herkunft, Geometrie und Zeitlage bis zum Dock | technisch getragen |
| 3. Alle Docks in derselben Neuronenschicht | technisch getragen |
| 4. Atomarer Feldtakt aus abgeschlossenem Vorzustand | technisch getragen |
| 5. Lokale semantikfreie Trägerzustände | technisch getragen |
| 6. Vollständiger Snapshot und unveränderte Wiederherstellung | technisch getragen |
| 7. Observer und Debug ohne Runtime-Rückschreibung | technisch getragen |
| 8. Reflexion und Offline-Erholung inaktiv | technisch getragen |
| 9. Reproduzierbarer Audio-Video-End-to-End-Lauf | teilweise; Ein-Takt-Livepfad und synthetischer Mehrtaktkern stehen, ein unverzerrter realer Mehrtaktpfad ist nicht freigegeben |
| 10. Öffentliche Zustandsbeschreibung | technisch getragen |

„Technisch getragen“ bezeichnet eine implementierte und regressionsgesicherte
Zustandsgrenze. Es ist keine Evidenz für organische Feldentwicklung.

## Umgang mit MINI_DIO

[MINI_DIO](https://github.com/H5Pro2/MINI_DIO) wird als technischer und
methodischer Kenntnisstand genutzt.

Direkt wiederverwendbar sind insbesondere:

- erprobte Nullkontrollen,
- passive Observergrenzen,
- Reproduzierbarkeitsverfahren,
- bekannte statische Sackgassen,
- Begriffe für Nachhall, Feldzeit, Rollen und Topologie,
- Anforderungen an Abschwächung, Lösung und Wiederbindung.

Nicht direkt übernommen werden aktive Chartlogik, Reward, feste
Eingangsgewichte, Hashsyntax, globale Gewinner oder unveränderliche
Beziehungen.

Bis zum Forschungsstart wird daraus keine Folge einzelner
Replikationsversuche erzeugt. Relevante Erkenntnisse fließen in die
Zustandsgrenzen und technischen Gegenbaselines des Grundsystems ein.

## Historischer Bestand

Die früheren nummerierten Methodiken, Befunde und technischen
`GF_001`-Vorläufe befinden sich im
[Archiv der Vorarbeiten bis zum Forschungsstart](archiv/vorarbeiten_bis_forschungsstart/README.md).

Sie bleiben nachvollziehbar, gelten aber nicht als laufende Versuchsserie des
fertigen gemeinsamen MCM-Feldes. `GF_001` ist eine vorläufige synthetische
Aufbauprobe. `GF_002` wird nicht eröffnet.

## Dokumentationsregel ab jetzt

Während der Vorarbeit entstehen nur:

- Änderungen an verbindlichen Architekturverträgen,
- Fortschreibungen dieses Vorarbeitsstands bei echten Meilensteinen,
- technische Tests im Code,
- notwendige Bedien- oder Schnittstellendokumentation.

Nicht mehr angelegt werden:

- ein Methodiktext pro technischem Schritt,
- ein Befundtext pro technischem Testlauf,
- neue Forschungsnummern für Architekturarbeit,
- lange Registereinträge ohne neue Feldfunktion,
- wiederholte Dokumente mit derselben Stopplinie.

## Nächster technischer Abschnitt

Die Live-Abnahme gemeinsamer Rezeptorfenster bestätigt, dass auditive und
visuelle Rezeptoren innerhalb derselben Organismusdauer verschieden viele
vollständige Zustände abschließen. In den geprüften Ein-Sekunden-Fenstern lagen
ungefähr hundert auditive und vier bis fünf visuelle Zustände vor. Kein Fenster
enthielt genau einen Zustand jeder Modalität.

Damit ist die direkte Umwandlung solcher Fenster in Feldtakte nicht
freigegeben. Sie würde Zustände auswählen oder verdichten, fehlende Zustände
halten oder den Feldfortschritt an die schnellere Modalität binden. Der
gemeinsame Fensteraudit bleibt eine passive Kontrollgrenze. Der begrenzte
Mehrtaktkern bleibt ein synthetisches technisches Prüfwerkzeug und ist kein
freigegebener Live-Taktgeber.

Die konzeptionelle Grenze ist im Vertrag
[Feldzeitübergabe des gemeinsamen MCM-Feldes](architektur/031_FELDZEITUEBERGABE.md)
geschlossen. Sie trennt lokale Quellenstütze, Rezeptorabschluss und
Organismuszeit. Der Vertrag gibt noch keine Runtime frei.

Die Feldzeitübergabe muss:

- jeden nativen Rezeptorabschluss und seine reale Zeitlage nachvollziehbar
  erhalten,
- Organismusdauer, Rezeptorereignis und Feldfortschritt getrennt halten,
- einzelne Modalitäten auch ohne gleichzeitigen Kontakt anderer Modalitäten
  zulassen,
- einen vollständigen Feldschritt je Sensorereignis ausschließen,
- ohne gemeinsame Hopgröße, Halten, Interpolation, globale
  Ratennormalisierung, Modalitätsgewicht oder Gewinner auskommen,
- erst nach Gegenprüfungen in den realen Mehrtaktrahmen übergehen.

Die vorhandenen Zeit- und Übergabeaudits zeigen bereits: Die reduzierte
asynchrone Dockfolge kann verlustfrei in Vorschlagsspannen transportiert
werden, passt aber nicht ohne Auswahl oder Mehrfachschritte in den heutigen
skalaren Dockkontakt der Neuronenwahrnehmung.

Als Nächstes wird deshalb ausschließlich der Vertrag eines transienten lokalen
Dockverlaufs formuliert. Er darf die Folge während eines Feldvorschlags
zugänglich machen, sie aber weder speichern noch lesen, verdichten oder als
Feldrhythmus verwenden.

Dieser Vertrag ist inzwischen umgesetzt und regressionsgesichert. Die Folge
wird vollständig auf stabile Docks abgebildet, bleibt aber außerhalb von
Neuron, Feldwahrnehmung, Snapshot und Runtimewirkung.

Als Nächstes wird geklärt, welche reine Informationsrolle dieser transiente
Dockverlauf im Neuronenantrieb besitzen darf, ohne bereits eine feste
Zeitleser- oder Verdichtungsmechanik einzubauen.

Die lokale Rolle ist inzwischen getrennt: Jedes Dock-Neuron kann einen
eigenen transienten Trägerverlauf erhalten; fremde Docks und globale
Modalitätsfolgen bleiben unsichtbar.

Der Neuronenantriebsvertrag ist ebenfalls technisch geschlossen. Eine
Transition kann den eigenen lokalen Verlauf optional über `MCMNeuronDrive`
sehen. Sobald diese Rolle verwendet wird, müssen alle Dock-Neuronen atomar
ihren lokalen Verlauf erhalten; eine leere Folge bezeichnet Abwesenheit. Nicht
angedockte Neuronen erhalten keine solche Eingabe.

Die Folge wird weder in Neuron, Feldwahrnehmung noch Snapshot gespeichert. Es
existiert keine eingebaute Leser-, Auswahl-, Integrations- oder
Wirkungsfunktion. Bestehende Transitionen erzeugen mit einer ignorierten
transienten Eingabe exakt denselben Feldzustand wie ohne sie.

Die Übergabegrenze des gemeinsamen Feldes ist inzwischen technisch
geschlossen. `SharedMCMField.advance()` kann optional einen vollständigen
`TransientNeuronInputSet` übernehmen. Feld, Dockanatomie, Carrierzuordnung und
Organismusspanne müssen exakt zusammenpassen. Erst danach wird der lokale Satz
atomar an die Neuronenschicht gereicht.

Der bisherige Feldaufruf ohne transienten Satz bleibt unverändert. Auch mit
einem Satz entsteht keine automatische Wirkung; bei einer ignorierenden
Transition bleiben Feldzustand und Snapshot exakt gleich. Eine Live-Quelle ist
weiterhin nicht angeschlossen.

Die Zeitfrage ist konzeptionell geschlossen: Die Architektur besitzt derzeit
keinen begründeten natürlichen Feldtakt. Eine Feldvorschlagsspanne ist deshalb
ausschließlich ein extern gemessenes Beobachtungsintervall. Ihre Grenze darf
weder aus der Ereignisrate eines Sensors noch aus einer behaupteten
Eigenfrequenz des Feldes abgeleitet werden.

Rezeptorabschlüsse werden ihrer gemessenen Abschlusszeit entsprechend einem
solchen Intervall zugeordnet. Sie lösen das Intervall nicht aus. Unterschiedlich
feine Beobachtungsgrenzen dürfen einen späteren kontinuierlichen Feldverlauf
nicht verändern. Diese Zeitteilungsinvarianz ist eine bindende Voraussetzung
für jede künftige Feldmechanik.

Die kleinste lokale Feldentwicklungsrolle benötigt keinen neuen
Zustandscontainer. `MCMNeuronDrive` trägt bereits getrennt den eigenen
Vorzustand, die lokale Feldwahrnehmung, die verstrichene Organismusdauer und
den optionalen lokalen Dockverlauf. Eine zusätzliche Entwicklungsstruktur
würde dieselben Rollen nur verdoppeln und könnte versteckte Statik einführen.

Noch fehlt jede Feldentwicklungsgleichung. `hold_state_baseline` und
`receptor_projection_baseline` bleiben reine technische Gegenproben. Keine von
beiden ist eine MCM-Dynamik.

Der erste Funktionsmangel ist nun präzise: Keine vorhandene Transition trägt
gleichzeitig Weltkontakt, lokale Vorfeldwirkung, reale Dauer und die
asynchrone lokale Dockfolge unter Zeitteilungsinvarianz. Hold ignoriert die
Welt. Rezeptorprojektion ignoriert Vorfeld und Verlauf. Feste lokale Leser
erzeugen nur ihre vorgegebene Leserform.

Die zugehörige Zulässigkeitsmethodik wählt noch keine Feldgleichung. Sie
fordert zuerst einen passiven Vergleichsrahmen, der denselben kausalen Verlauf
grob und fein segmentiert, alle lokalen Rollen einzeln ablatiert und feste
Leser sowie einfache Zeitintegratoren als Baselines führt.

Als Nächstes wird ausschließlich dieser darstellungsoffene Vergleichsrahmen
technisch vorbereitet. Er darf beliebige explizit übergebene Kandidaten
prüfen, aber keinen Standardkandidaten, keine Runtimewirkung und keine
Live-Anbindung enthalten.

Die dafür notwendige Abwesenheitsgrenze ist jetzt geschlossen:
`ReceptorDistribution` kann ein gemessenes Intervall ohne neue Kontakte
darstellen. Die Docks bleiben vorhanden, alle lokalen Kontakte sind abwesend
und ein optionaler transienter Eingabesatz kann trotzdem atomar übergeben
werden. Snapshot und Wiederherstellung bewahren diesen Zustand ohne
Ersatzwert.

Der passive Vergleichsrahmen ist jetzt technisch aufgebaut. Er übergibt eine
Transition ausschließlich explizit, baut jeden groben und feinen Zweig samt
Wiederholung aus einem frischen identischen Feld auf und bewahrt alle
Rezeptorabschlüsse genau einmal. Kontaktfreie Beobachtungsgrenzen erzeugen
weder Nullkontakte noch gehaltene Endpunkte; die lokale transiente Folge bleibt
vollständig am jeweiligen Dock-Neuron verfügbar.

Der physische Vergleichsendpunkt enthält nur `activation` und `afterimage`.
Technische Taktzähler bleiben als Ablaufspur sichtbar, entscheiden aber nicht
über Zeitteilungsinvarianz. Die Hold-State-Nullkontrolle endet bei grober und
feiner Segmentierung identisch. Eine absichtlich taktgebundene technische
Gegenmechanik wird als segmentierungsabhängig erkannt. Damit ist nur die
Prüffähigkeit des Rahmens abgesichert; keine lokale Feldgleichung ist gewählt
oder freigegeben.

Die lokalen Informationsrollen sind jetzt innerhalb einer passiven,
identitätsfreien Ansicht einzeln ablatierbar. Die Ansicht enthält ausschließlich
schnellen Vorzustand, aktuellen skalaren Kontakt, lokale Vorfeldproben,
verstrichene Dauer und die lokale transiente Rezeptorfolge. Sie enthält keine
Neuron-, Modalitäts-, Dock- oder Clock-Identität.

Vollansicht und jede einzelne Rollenablation werden unabhängig neu aufgebaut.
Der Rahmen protokolliert nur, ob sich Endpunkte verändern. Er erzeugt daraus
keine Entwicklungs- oder Kausalitätsbehauptung.

Die festen Gegenbaselines B0 bis B3 sind ebenfalls ausdrücklich anschließbar.
B1 wählt keinen Endpunkt aus einer transienten Folge, B2 bleibt ein
zustandsloser symmetrischer Leser und B3 verlangt eine feste offengelegte
Zeitkonstante. Keine dieser Funktionen ist Standard, Runtimefreigabe oder
MCM-Feldgleichung.

Rezeptorrate und Kausalität sind jetzt als technische Kontrollachsen in
denselben passiven Rahmen eingebracht. Die Ratenskontrolle erlaubt nur
zusätzliche technische Abschlüsse derselben reduzierten Quellenstütze. Neue
Quellenzustände oder Geometrien werden abgewiesen. Hold bleibt neutral; eine
absichtlich ereigniszählende Gegenfunktion wird zuverlässig als
ratenabhängig erkannt.

Die Kausalitätskontrolle vergleicht denselben abgeschlossenen Verlauf bis zu
einer gemeinsamen Feldgrenze mit einem Zweig, der erst danach einen weiteren
Abschluss erhält. Der spätere Kontakt bleibt vor seinem Abschluss ohne Wirkung
und kann erst den nachfolgenden Endpunkt verändern. Das ist eine technische
Absicherung der Übergabe, kein Befund über Felddynamik.

Die Gleichzeitigkeit ist jetzt ebenfalls technisch kontrolliert. Zwei
Modalitäten mit gemeinsamen Abschlusszeiten wurden in umgekehrter
Deklarationsreihenfolge unabhängig neu aufgebaut. Die vollständigen groben und
feinen Feldspuren bleiben exakt gleich. Dafür wurde keine neue
Modalitätspriorität oder Sortiermechanik ergänzt; die Kontrolle prüft die
bereits vorhandene ungeordnete Abschlussgruppe und atomare Neuronenschicht.

Die Geometriekontrolle ist jetzt ebenfalls angeschlossen. Weltverlauf,
Rezeptorträger, Dock-Neuronen, Positionen und lokale Sample-Offsets müssen eine
vollständige bijektive Spiegelung bilden, bevor Feldspuren verglichen werden.
Eine symmetrische lokale Gegenfunktion spiegelt vollständig mit; eine
absichtlich richtungsabhängige Funktion wird zuverlässig als Verletzung
erkannt. Die Kontrolle wählt daraus keine Feldmechanik aus.

Die Snapshot-Wiederaufnahme ist jetzt als letzte vorgesehene technische
Kontrollachse angeschlossen. Ein passiver Verlauf wird ohne Unterbrechung und
über eine echte Snapshot-Wiederherstellung unabhängig aufgebaut. Bei einer
zustandslosen lokalen Gegenfunktion bleiben grobe und feine Feldspuren exakt
gleich. Snapshot und wiederhergestellter Zustand besitzen denselben Digest;
kein Rezeptorabschluss wird verdoppelt oder verloren.

Die Transition wird nach der Wiederherstellung bewusst neu erzeugt. Eine
absichtlich in einer Closure verborgene Schrittgeschichte führt deshalb
korrekt zu einer Abweichung. Der Vergleich kann somit unterscheiden, ob eine
Fortsetzung allein aus dem serialisierten Organismuszustand folgt oder von
einem nicht ausgewiesenen technischen Nebenzustand abhängt.

Damit sind Zeitteilung, Rollenablation, feste Baselines, Rezeptorrate,
Kausalität, Gleichzeitigkeit, Geometrie und Wiederaufnahme im passiven
Vergleichsrahmen technisch prüfbar. Daraus folgt noch kein Feldkandidat, keine
Runtimefreigabe und kein Befund über organisches Memory oder Feldentwicklung.

Der Abgleich mit dem kleinsten offenen Funktionsmangel ist jetzt erfolgt. Die
heutige Rezeptorprojektion kann bei gleichem aktuellem Weltkontakt keine
unterschiedliche lokale Vorfeldlage wirksam unterscheiden. Hold kann bei
gleicher Vorfeldlage keinen neuen Weltkontakt aufnehmen. Damit ist eine
fehlende Runtimeleistung beobachtbar: Weltkontakt und vorhandene lokale
Feldlage werden noch von keiner Runtime-Transition gemeinsam kausal getragen.

Der passive Rahmen kann beide Rollen einzeln ablatieren und alle vorgesehenen
technischen Pflichtachsen kontrollieren. Die anschließende methodische Prüfung
hat eine falsche Forderung offengelegt: Jeder deterministische digitale
Übergang ist mathematisch eine fest definierte Rekurrenz. Ein erster
Übergangskandidat kann daher nicht zugleich programmiert und „keine feste
Rekurrenz“ sein.

Fest sein darf nur eine einheitliche, lokale und semantikfreie digitale
Naturbedingung. Nicht festgelegt werden dürfen Beziehungen, Rollen,
Zieltopologie oder gewünschte Feldformen. Organische Entwicklung könnte erst
später an einer durch Weltgeschichte veränderten, kausal wirksamen und wieder
lösbaren Organisation desselben Feldes geprüft werden.

Die nicht-tautologische Zulassungsbedingung ist damit geschlossen: Ein
minimaler Substratkandidat muss Weltkontakt und lokale Vorfeldlage jeweils
kausal notwendig machen, alle Pflichtachsen bestehen und darf keine weitere
Zustandsrolle einführen. Er bleibt gegen B2, B3, feste Diffusion und statische
Rekurrenz zu prüfen. Erklärt eine einfachere Baseline seine Wirkung exakt,
wird die komplexere Form verworfen; daraus folgt aber nicht, dass ein
programmierbares digitales Substrat ohne feste lokale Naturbedingung möglich
sein müsste.

Als Nächstes darf genau ein minimaler lokaler Substratkandidat vorregistriert
werden. Runtimeübernahme, Topologie, Memory und organische
Entwicklungsbehauptungen bleiben geschlossen.

Dieser erste technische Umsetzungsschritt ist inzwischen erfolgt. Die
explizit auswählbare neutrale lokale Substratfunktion verbindet:

- den eigenen schnellen Vorzustand,
- den Mittelwert vorhandener lokaler Vorfeldaktivierungen,
- einen tatsächlich vorhandenen aktuellen Rezeptorkontakt,
- die gemessene Dauer des Feldschritts.

Sie verwendet eine einheitliche lokale Reaktions-Diffusions-Gleichung. Jeder
lokale Nachbar trägt nur seine Aktivierungsdifferenz zum betrachteten Neuron;
ein tatsächlich vorhandener Rezeptorkontakt wirkt auf dieselbe Weise als
lokale Randanregung. Eine zwingend offengelegte Reaktionszeit bestimmt nur die
technische Zeitskala. Modalitätsgewichte, Bedeutungen, Beziehungen, Schwellen
und Zielmuster existieren nicht.

Die erste Frozen-Neighborhood-Umsetzung erwies sich bei räumlich veränderlicher
Feldlage als abhängig von der Beobachtungsunterteilung und wurde deshalb vor
der Runtimefreigabe ersetzt. Die lokale Gleichung wird nun für die vollständige
abgeschlossene Neuronenschicht exakt über die reale Dauer integriert. Grobe
und feine Teilung desselben konstanten Weltkontakts führen dadurch zum selben
physischen Feldendzustand.

Abwesenheit wird nicht als Nullkontakt ergänzt. Ohne Rezeptorkontakt bleibt
nur symmetrische lokale Diffusion; sie erhält den Feldmittelwert und reduziert
räumliche Unterschiede. Der Nachhall bleibt unverändert, und transiente
asynchrone Rezeptorverläufe werden noch nicht gelesen.

`SharedMCMField.advance()` kann die dafür notwendige explizite
`MCMFieldStepTime` nun direkt entgegennehmen und prüft sie gegen das
Organismusintervall der Rezeptorverteilung. Snapshot und Wiederaufnahme der
ersten Mechanik bleiben exakt.

Priorität 1 ist damit als technisches Substrat umgesetzt. Zeitteilung,
Spiegelneutralität auf größerer Geometrie, Feldbegrenzung und exakte
Wiederaufnahme sind regressionsgesichert. Die Mechanik ist selbst eine feste
lokale Reaktions-Diffusions-Naturbedingung und kein Befund über organische
Feldentwicklung.

Als Nächstes beginnt Priorität 2: Die bereits vorhandenen transienten
asynchronen Rezeptorverläufe müssen fortlaufend und ohne Auswahl oder
Verdichtung auf diese Feldmechanik wirken können.

Der erste Priorität-2-Anschluss ist inzwischen umgesetzt. Vollständige
asynchrone Rezeptorabschlüsse werden über Abschlussgruppen, stabile Docks und
lokale transiente Neuroneneingaben an dieselbe neutrale Feldmechanik
übergeben. Zwischen Abschlusszeiten entwickelt sich das Feld kontinuierlich;
der Abschluss selbst erzeugt keinen Feldtakt.

Ein Kontakt wirkt erst an seiner gemessenen Abschlusszeit. Seine gemessene
Lesedauer trägt die lokale verzögerte Kontaktwirkung. Die technische
Randverteilung muss dabei kontaktfrei bleiben, damit kein Ereignis zusätzlich
als skalarer Endpunktkontakt doppelt wirkt.

Ein kontrollierter synthetischer Audio-Video-Verlauf mit unterschiedlichen
und gemeinsamen Abschlusszeiten trägt bei grober und feiner Segmentierung
denselben Feldendzustand. Alle fünf Ereignisse werden genau einmal zugeordnet,
zukünftige Abschlüsse verändern keinen früheren Präfix, Deklarationsreihenfolge
bleibt wirkungslos und Snapshot-Wiederaufnahme ist exakt.

Die offene Quellstützen-Grenze ist jetzt technisch geschlossen. Ein begrenzter
asynchroner Feldlauf prüft vor dem ersten Feldschritt, ob jede physische
Quellstütze genau einmal vorliegt und vollständig in den Laufhorizont fällt.
Identische Doppelmeldungen und widersprüchliche Werte derselben Stütze werden
abgewiesen, statt durch Mittelung, Gewichtung oder Wiederholung in die
Feldwirkung einzugehen. Gleiche Quellintervalle aus verschiedenen Modalitäten
bleiben getrennte Weltkontakte.

Diese Prüfung ist ein zustandsloser technischer Laufvertrag und kein Teil des
MCM-Memory.

Die bestehenden Audio- und Videoadapter sind jetzt an denselben begrenzten
Feldlauf angeschlossen. Die hardwareunabhängige Klammer nimmt native
Audio-/Videoquellen auf, erzeugt ausschließlich reduzierte zeitgetragene
Rezeptorzustände, baut daraus die explizite gemeinsame Dockgeometrie und führt
alle Abschlüsse genau einmal auf das gemeinsame Feld. Die Live-Klammer öffnet
nur ausdrücklich benannte Geräte und verlangt die Feldkonfiguration sichtbar
vom Aufrufer.

Für einen Lauf wird die unveränderte lokale Generatormatrix einmal zerlegt und
anschließend über alle realen Abschlussintervalle wiederverwendet. Dies ist
eine zustandslose Rechenoptimierung; die Feldgleichung und ihre kausale
Ereignisfolge bleiben gleich.

Der synthetisch gespeiste vollständige Pfad trägt sechs auditive und zwei
visuelle Rezeptorabschlüsse ohne Rohdatenhaltung genau einmal in dasselbe
16-Neuronen-Feld.

Der begrenzte reale Hardwarelauf ist ebenfalls abgeschlossen. Während einer
nominalen Sekunde wurden 30 Kameraframes vollständig gelesen. Daraus entstanden
30 visuelle Rezeptorzustände. Bei freier Kamera lagen ihre reduzierten lokalen
Werte zwischen 0,212 und 0,834; der visuelle Eingang trug damit tatsächlich
aktiven Weltkontakt. Parallel entstanden nach dem notwendigen auditiven
Fensteraufbau 91 auditive Rezeptorzustände; der Audioadapter meldete keinen
Überlauf. Alle 121 Quellstützen wurden genau einmal dem gemeinsamen
336-Neuronen-Feld zugeordnet und erzeugten einen serialisierbaren Feldzustand.
Gerätebezeichnungen, Rohdaten und laufbezogene Debugdaten werden nicht
dokumentiert oder gespeichert.

Priorität 2 ist damit technisch umgesetzt. Dies ist ein Nachweis des
zusammenhängenden realen Wahrnehmungs- und Feldpfads, kein Befund über Lernen,
Feldtopologie, organisches Memory oder Feldintelligenz. Als Nächstes beginnt
die Umsetzung des schnellen, vollständig lösbaren Nachhalls aus Priorität 3.

Der erste Priorität-3-Kandidat ist inzwischen als ausdrücklich wählbarer
schneller Feldpfad umgesetzt. Die vorhandene Aktivierung folgt unverändert der
neutralen lokalen Feldgleichung. Der Nachhall desselben Neurons folgt der
eigenen Aktivierung mit einer separat offengelegten schnellen Zeitkonstante.
Beide Rollen werden gekoppelt und exakt über reale Dauer integriert.

Geprüft sind Zeitteilungsneutralität, begrenzte lokale Wirkung, monotone
Relaxation bei neutraler Aktivierung, asynchrone Kausalität und exakte
Snapshot-Wiederaufnahme. Frühere Nachbarstellen bleiben bis auf numerische
Rundung im Bereich von etwa `10^-25` neutral; es wurde kein künstlicher
Nullschwellenwert ergänzt.

Die Grenze ist wesentlich: Der feste leaky Kandidat nähert sich ohne Schwelle
nur asymptotisch null. Er ist deshalb eine technische schnelle
Zustandsbaseline, noch kein vollständig gelöster Priorität-3-Nachhall und kein
organisches Memory. Vor der Anbindung an den realen Audio-Video-Feldlauf muss
geklärt werden, ob exakte endliche Lösung ohne Schwellenwert und ohne neue
versteckte Historienstruktur möglich ist.

Die isolierte Lösbarkeitsfrage ist inzwischen enger beantwortet. Eine lokale
nichtlineare Relaxation mit einem Exponenten zwischen null und eins erreicht
ihre mathematisch bestimmte Null in endlicher realer Zeit. Dafür sind weder
eine numerische Nullschwelle noch ein Reset oder zusätzlicher Historienzustand
nötig. Der Operator ist vorzeichenneutral, lokal und bei zeitlicher Aufteilung
konsistent; seine Lösungsdauer bleibt von der vorhandenen Amplitude abhängig.

Dies ist noch keine neue Feldmechanik. Ungeklärt ist, wie eine solche endliche
Freigabe an gleichzeitig laufende Aktivierung gekoppelt werden kann, ohne
technische Schrittfolge, künstliche Umschaltung oder verborgene Zustandsrolle.
Bis diese Grenze geklärt ist, bleibt der Kandidat außerhalb der Runtime und des
realen Audio-Video-Laufs.

Die einfachste Kopplung an laufende Aktivierung ist nicht zulässig. Wird der
Aktivierungsendwert jedes technischen Abschnitts als festes Ziel der endlichen
Freigabe behandelt, bleibt die Rechnung nur bei einem unveränderten Ziel
zeitteilungsneutral. Für einen kontrolliert bewegten Zielverlauf entstanden bei
grober und geteilter Auswertung Endwerte von `0,7500` und `0,6495`.

Der Unterschied ist ein Segmentierungsartefakt und keine Feldwirkung. Diese
Endwert-Kopplung wird deshalb nicht implementiert. Ebenfalls gesperrt sind eine
feste Abtastrate oder Mikroschritte, die das Problem lediglich hinter einem
technischen Takt verbergen würden. Eine weitere Kopplungsprüfung muss den
kontinuierlichen Aktivierungsverlauf kausal integrieren. Falls dies ohne
Hilfshistorie oder künstliche Umschaltung nicht gelingt, bleibt der endliche
Freigabeoperator isoliert.

Eine echte kontinuierliche Kopplung ist mathematisch und numerisch
grundsätzlich möglich. Wird der Nachhall unmittelbar durch den Abstand zur
gleichzeitig kontinuierlich entwickelten Aktivierung getragen, genügen die
beiden bereits vorhandenen Zustandsrollen `activation` und `afterimage`. Eine
zusätzliche Historienvariable ist nicht nötig. Ein ungeteilter Verlauf und
derselbe bei der Hälfte unterbrochen fortgesetzte Verlauf unterschieden sich in
der isolierten Rechnung nur um `4,44 * 10^-16`; ein fester Mikrotakt wurde nicht
verwendet.

Die Laufzeit verhindert dennoch eine vorschnelle Übernahme. Für 336 lokale
Nachhallwerte dauerte eine simulierte Sekunde je nach Freigabeexponent ungefähr
`0,15`, `0,39`, `0,63` oder `26,85` reale Sekunden. Die endliche Annäherung an
eine bewegte Aktivierung kann den adaptiven Solver besonders bei kleinen
Exponenten stark beanspruchen. Diese Werte sind eine lokale
Machbarkeitsmessung, kein Laufzeitversprechen für das Gesamtsystem.

Damit ist die Zustandsfrage enger beantwortet, die Mechanikfrage aber noch
offen. Es wurde keine Solverabhängigkeit ergänzt und keine Runtime verändert.
Vor einer Implementierung muss ein konkreter Funktionsunterschied zur bereits
zeitstabilen leaky Baseline benannt werden. Reine mathematische Endlichkeit
genügt nicht, wenn sie keine benötigte Feldfunktion trägt.

Der Funktionsabgleich zeigt derzeit keinen solchen Unterschied. Im aktuellen
gemeinsamen Feld wird `afterimage` nicht in Aktivierung, Rezeptorannahme oder
Weiterleitung zurückgeführt. Die endliche und die leaky Variante verändern
daher nur die schnelle lesbare Zustandsrolle. Die nichtlineare Variante bleibt
wegen fehlender zusätzlicher Feldfunktion und deutlich höherer Rechenlast
außerhalb der Runtime.

Der leaky Nachhall ist nun stattdessen optional durch den bestehenden bounded
Runtime-Pfad geführt. Der Aufrufer muss seine schnelle Zeitkonstante ausdrücklich
angeben. Dann verwenden synthetische und reale Audio-Video-Klammer dieselben
asynchronen Rezeptorabschlüsse für Aktivierung und Nachhall. Ohne
Nachhallkonfiguration bleibt der vorherige Pfad unverändert.

Geprüft ist, dass die Aktivierung mit und ohne Nachhall identisch bleibt, grobe
und feine Beobachtungsteilung denselben schnellen Zustand tragen und die
Live-Brücke die Konfiguration unverändert weitergibt. Damit ist die Mechanik
technisch verbunden, aber noch nicht mit einem erneuten realen Hardwarelauf
verifiziert.

Der erneute reale Hardwarelauf ist abgeschlossen. Während einer nominalen
Sekunde entstanden 30 visuelle und 91 auditive Rezeptorabschlüsse ohne
Audioüberlauf. Alle 121 Quellstützen wurden genau einmal verarbeitet. Das
gemeinsame Feld umfasste 336 Neuronen; Aktivierung und schneller Nachhall waren
beide endlich, begrenzt und auf allen Neuronen vorhanden. Es wurden keine
Rohdaten oder Gerätebezeichnungen gespeichert.

Damit trägt der reale Wahrnehmungspfad nun die beiden schnellen Zustandsrollen
des MCM-Neurons. Der Nachhall wirkt nicht auf die Aktivierung zurück, ist kein
organisches Memory und belegt keine Beziehungsressource. Der ungenutzte
nichtlineare Freigabekandidat wurde nach dem fehlenden Funktionsvorteil wieder
aus der ausführbaren öffentlichen API entfernt. Priorität 3 ist technisch
abgeschlossen; als Nächstes folgt der Dauerbetrieb und die Persistenz aus
Priorität 4.

Der erste Baustein von Priorität 4 ist nun umgesetzt. Ein aktueller
`NeutralFieldSession`-Rahmen führt mehrere abgeschlossene asynchrone
Rezeptorfenster auf demselben gemeinsamen Feld fort. Er verwendet unverändert
die neutrale Aktivierungsmechanik und den optionalen schnellen leaky Nachhall.

Im Sitzungsergebnis bleiben nur das vollständige Feld, die Zahl abgeschlossener
Fenster und die Zahl eindeutig verarbeiteter Quellstützen. Die eingegangenen
Rezeptorsequenzen, technischen Handoffs und Observerausgaben werden nicht als
Organismuszustand behalten.

Ein kontrollierter Drei-Fenster-Lauf wurde nach dem ersten Fenster vollständig
unterbrochen. Sein Feldsnapshot wurde als kanonisches JSON geschrieben, daraus
neu konstruiert und anschließend fortgesetzt. Der finale Digest stimmt exakt
mit dem ununterbrochenen Drei-Fenster-Lauf überein. Eine Wiederaufnahme an einer
anderen Zeitgrenze und eine Überschreitung der expliziten Fenstergrenze werden
geschlossen abgewiesen.

Dies zeigt technische Persistenz des vorhandenen Feldzustands, kein Lernen und
kein organisches Memory. Als Nächstes muss derselbe Vertrag über einen längeren
synthetischen Verlauf mit mehreren unabhängigen Checkpoints tragen, bevor ein
realer Mehrfensterlauf sinnvoll ist.

Der längere synthetische Verlauf ist inzwischen geprüft. Er umfasst 24
lückenlose Fenster und 48 eindeutig verarbeitete Quellstützen. Verglichen
wurden ein ununterbrochener Lauf, vollständige JSON-Checkpoints nach jedem
Fenster, wechselnde Checkpoint-Abstände von 2, 3, 5 und 7 Fenstern sowie zwei
Abschnitte mit 11 und 13 Fenstern.

Alle Fortsetzungen enden exakt im selben Snapshot-Digest. Die Checkpointfrequenz
erzeugt damit keinen technischen Feldtakt. Auch die häufigste Serialisierung
enthält keine Rezeptorsequenzen und keine Handoffs. Der nächste offene
Priorität-4-Schritt ist ein begrenzter realer Mehrfensterlauf ohne
Rohdatenhaltung.

Der begrenzte reale Mehrfensterlauf ist abgeschlossen. Kamera, Mikrofon,
auditiver Rollzustand und fortlaufende visuelle Ereignisnummern blieben über
zwei Ein-Sekunden-Fenster geöffnet. Das gemeinsame 336-Neuronen-Feld wurde nach
dem ersten Fenster vollständig als JSON serialisiert, wiederhergestellt und im
zweiten Fenster fortgesetzt.

Insgesamt wurden 60 visuelle und 251 auditive und visuelle Quellstützen
verarbeitet. Ein Audioüberlauf wurde als technischer Eingangshinweis gezählt.
Das Ergebnis hält nur Feldzustand, Fensterzahl, Quellstützenzahl und technische
Zähler; Rohdaten, Rezeptorsequenzen, Handoffs und Gerätebezeichnungen wurden
nicht gespeichert.

Priorität 4 ist damit technisch abgeschlossen. Persistenz ist weiterhin nur
Zustandserhaltung und weder Lernen noch organisches Memory. Vor Runtime-Code
für Priorität 5 folgt ein enger Abgleich des vorhandenen MINI-DIO-Wissens zur
Feldtopologie mit der gemeinsamen MCM-Neuronenschicht. Erst ein konkreter
Funktionsmangel darf den nächsten Mechanikkandidaten begründen.

Der MINI_DIO-Feldtopologie-Abgleich ist abgeschlossen. Die alten Befunde
tragen zwei getrennte Seiten: feldlokale Eigenform mit starker Abhängigkeit
von einer festen Indexrichtung und bewegliche relationale Erfahrung außerhalb
des laufenden Feldes. Kein alter Kandidat verbindet beide Seiten
architekturunabhängig. Deshalb wurden weder alte Beziehungen noch
`continuity`, `allocation`, Rangzyklen oder Observer-Nachbarschaften in die
neue Runtime übernommen.

Der konkrete Funktionsmangel des gemeinsamen Feldes ist nun benannt: Wenn
Aktivierung und schneller Nachhall nach verschiedenen Weltgeschichten exakt
gleich sind, kann eine identische spätere Probe keinen unterschiedlichen
kausalen Feldweg erzeugen. Feste Abtastgeometrie und schneller Zustand bilden
dann bereits den vollständigen aktuellen Funktionszustand.

Als nächster Schritt wird diese technische Grundnull mit der aktuellen
Runtime reproduziert. Die Prüfung ergänzt keine langsame Zustandsrolle und
keine Topologiemechanik. Erst nach dieser Null darf ein darstellungsoffener
Organisationsvertrag formuliert werden.

Die technische Grundnull ist reproduziert. Zwei unterschiedliche lokale
Kontaktgeschichten behielten verschiedene frühere
`perception`-Schnappschüsse. Aktivierung, schneller Nachhall und aktueller
Kontakt wurden kontrolliert exakt angeglichen. Vor der späteren Probe blieben
die vollständigen Snapshots deshalb verschieden.

Nach derselben lokalen Probe waren beide schnellen Feldrollen elementweise
exakt gleich; auch die vollständigen resultierenden Snapshot-Digests stimmten
überein. Die heutige neutrale Transition liest die verbliebene frühere
Wahrnehmung damit nicht als zusätzliche Organisationsgeschichte.

Dies ist eine konstruktiv kontrollierte Null und keine natürliche Konvergenz.
Sie gibt keine Memory-Mechanik frei. Als Nächstes folgt ausschließlich ein
darstellungsoffener Zustandsvertrag für eine mögliche lokale
Organisationsrolle.

Der darstellungsoffene Vertrag dieser möglichen Organisationsrolle ist jetzt
formuliert. Festgelegt sind nur ihre notwendigen beobachtbaren Funktionen:
Nichtredundanz zu schnellen Zuständen, lokale Entstehung, zeitlich getrennte
spätere Wirkung, vollständige Lösung, Ressourcenfreigabe, andere Wiederbindung
und ein kausaler Funktionswechsel unter identischer Probe.

Nicht festgelegt wurden Darstellung, Updategleichung, Kante, Paaridentität,
Gewicht, `continuity`, `allocation`, Lernrate, Schwelle oder feste
Zerfallszeit. Der Nullzustand eines späteren Kandidaten muss exakt die heutige
neutrale Runtime ergeben. Der nächste Schritt ist die Vorregistrierung genau
eines kleinsten passiven Kandidatenvergleichs; die Runtime bleibt geschlossen.

Dieser Kandidatenvergleich ist nun vorregistriert. C1 ergänzt ausschließlich
für einen isolierten passiven Lauf einen skalaren, begrenzten Zustand pro
bestehendem Neuron. Er entsteht aus gleichzeitigem lokalem Rezeptorkontakt und
lokaler Feldabweichung und kann in einer späteren kontaktfreien Probe nur die
symmetrische lokale Weiterleitung verformen.

Der Nullzustand von C1 ergibt exakt die heutige neutrale Feldgleichung.
Zustandstausch, Gleichsetzung und exakte Neutralisierung trennen seine
kausale Wirkung. Der stärkste Gegenvergleich ist ein gewöhnlicher begrenzter
Integrator derselben lokalen Evidenz. Erklärt dieser den gesamten Effekt, ist
keine Topologie entstanden; gezeigt wäre nur die technische Tragfähigkeit
eines zusätzlichen lokalen Zustands.

Als Nächstes wird C1 ausschließlich außerhalb der Runtime bis zu genau einer
späteren Feldprobe implementiert. Live-Pfad, Mehrzyklen, Lösung, Wiederbindung
und jede Memory- oder Topologiebehauptung bleiben geschlossen.

C1 ist inzwischen passiv ausgeführt. Der Kandidat trug nach Angleichung von
Aktivierung und schnellem Nachhall eine zeitlich getrennte Feldwirkung. Die
Wirkung wanderte bei Zustandstausch mit, verschwand im Null- und
Feldablationszweig und blieb unter Spiegelung, Zeitteilung, Zweigreihenfolge
sowie Snapshot-Wiederaufnahme stabil.

Der maximale Zeitteilungsfehler betrug `1,1102230246251565e-16`. Die gesamte
Suite bestand anschließend `756/756` Tests.

Der entscheidende Gegenbefund ist eindeutig: Ein begrenzter Integrator des
lokalen Produkts aus Rezeptorkontakt und Feldabweichung reproduzierte C1 und
seine spätere Leserwirkung exakt. C1 ist damit kein Topologiebefund, sondern
eine feste lokale Disposition. Er wird nicht in MCM-Neuron, Snapshot, Live-Pfad
oder Runtime übernommen.

Der nächste Schritt ist keine komplexere Zustandsgleichung. Zuerst wird die
Funktionsgrenze bestimmt, durch die eine verteilte lokale Organisation mehr
leisten müsste als eine beliebige Sammlung unabhängiger lokaler Skalare.

Diese Funktionsgrenze ist jetzt präzisiert. Eine grundsätzliche Abgrenzung
gegen „beliebig viele Skalare“ wäre mathematisch nicht prüfbar, weil endliche
digitale Zustände unterschiedlich codiert werden können. Deshalb werden
Kandidaten künftig bei gleichem Zustandsbudget, Wertebereich, Leseradius,
Zeitpräfix und Snapshotumfang mit faktorisierten lokalen Baselines verglichen.

Verteilte lokale Organisation bezeichnet dabei keine Datenform. Beobachtbar
wäre sie zuerst als kausale Wechselwirkung: Eine lokale Geschichte A verändert
die spätere Änderbarkeit einer überlappenden Möglichkeit B, eine getrennte
Kontrolle U bleibt neutral, und die vollständige Lösung von A stellt die
Möglichkeit für B wieder her. Ein Interaktionsrest allein genügt nicht, weil
auch Sättigung und feste nichtlineare Leser ihn erzeugen können.

Als Nächstes wird nur die passive A-B-U-Versuchsmatrix vorregistriert. Eine
Kapazitätsvariable, Kante, Gewinnerregel oder neue Runtime bleibt gesperrt.

Die A-B-U-Matrix ist nun vorregistriert. Eine lineare Welt mit acht Positionen
trägt die überlappenden Bereiche A und B sowie die gleich geformte, räumlich
getrennte Kontrolle U. Die Matrix misst vollständige Feldantworten und die
Interaktionsreste `I_AB` sowie `I_UB`.

Zwei gewöhnliche Lösungschallenges sind festgelegt: 16 Sekunden
Kontaktabwesenheit und eine alternative lokale Weltgeschichte. Danach wird B
erneut angeboten. Weder Lösung noch erneute Beanspruchung verwenden Reset,
Kapazitätsvariable, Kante oder Gewinnerregel.

Als Nächstes wird ausschließlich die erwartete Grundnull der heutigen Runtime
implementiert. Da die neutrale kontinuierliche Diffusion auch entfernte
Bereiche schwach beeinflussen kann, wird U nicht pauschal als wirkungslos
behandelt; ihre Wirkung muss durch B0 exakt vorhergesagt werden.

Die technische A-B-U-Grundnull ist umgesetzt. U erreichte den B-Bereich vor
der Angleichung mit einer maximalen Aktivierungsdifferenz von
`0,08343498474450703`. Nach der konstruktiven Angleichung waren `I_AB` und
`I_UB` exakt null. D0 und D1 sowie die anschließenden B-Zweige trugen ebenfalls
keinen verborgenen A-Rest.

Spiegelung, Übersetzung und Zeitteilung blieben innerhalb von
`4,440892098500626e-16`; Neuronenreihenfolge, Zweigreihenfolge und
Snapshot-Fortsetzung waren neutral. Der Befund trägt nur die Versuchsmatrix
und die Grenze der aktuellen Runtime. Als Nächstes wird ein reiner
Zulassungsvertrag für einen zweiten passiven Kandidaten formuliert, noch keine
Mechanik.

Der C2-Zulassungsvertrag liegt nun vor. Seine zentrale Verschärfung ist die
Trennung von Bildung und Leser: Eine A-Geschichte muss bereits die lokale
Zustandsentwicklung während identischer B-Evidenz verändern. Entsteht der
Unterschied erst in einer fest programmierten späteren Leserfunktion, wird der
Kandidat wie C1 geschlossen.

Der Vertrag verlangt außerdem vor jeder Implementierung eine gewählte
natürliche Lösungschallenge, faire Zustands- und Leserbudgets, vollständige
Kausalinterventionen sowie erneute B-Wirkung nach Lösung. Als Nächstes werden
nur Kandidatenfamilien konzeptionell ausgesiebt; noch entsteht kein neuer
Zustand.

Der konzeptionelle Familienvergleich ist abgeschlossen. K1 bis K5 sowie K7
und K8 scheitern bereits an Faktorisierbarkeit, vorgegebener Beziehung,
programmierter Konkurrenz, unnötiger Zusatzdynamik, direkter Ressource oder
Historienarchiv. Nur K6, eine gekoppelte lokale Feldverformung ohne Partner-ID,
bleibt bedingt offen.

Dabei wurde eine methodische Unschärfe sichtbar: Eine unbegrenzt verstandene
„statische lokale Rekurrenz“ würde jeden digitalen C2-Kandidaten umfassen und
den Vergleich unentscheidbar machen. Vor einer Kandidatenauswahl müssen daher
B1 bis B6 als endliche, faire Hypothesenklassen operational festgelegt werden.

Die C2-Baselineklassen B1 bis B6 sind nun operational abgegrenzt. Ein
gemeinsamer Budgetvertrag bindet persistenten Zustandsumfang, lokale
Reichweite, Parameterzahl, Präzision, Zeitpräfix, Leserbudget und
Snapshotumfang. B1 bis B3 prüfen unabhängige lineare, produktive und begrenzte
Spuren; B4 prüft eine feste Leserwirkung; B5 eine feste lokale Rekurrenz; B6
eine zustandslose lokale Normalisierung.

B5 bleibt stark, aber endlich: feste, translationsgleiche Koeffizienten, eine
vorregistrierte punktweise Nichtlinearität und keine zustandsabhängige
Kopplung. Damit umfasst die Baseline nicht mehr definitionsgemäß jede mögliche
digitale C2-Mechanik.

Es wurde weiterhin kein Kandidat, kein persistenter Zustand und keine
Runtime-Erweiterung ausgewählt. Als Nächstes darf nur geprüft werden, ob K6
unter dem geschlossenen Baselinevertrag überhaupt einen kleinsten
darstellungsoffenen Vorschlag zulässt. Vor einer Gleichung müssen
Funktionsmangel, Bildung unter identischer B-Evidenz, natürliche vollständige
Lösung, andere Wiederbindung und Freiheit von Kante, Ressource, Zieltopologie
und Semantik begründet sein.

Die K6-Vorprüfung ist nun abgeschlossen. Gekoppelte lokale Feldverformung
benennt zwar die notwendige geschichtsabhängige Änderung während neuer
Evidenz, liefert aber noch keine nicht tautologische Naturbedingung für
Bildung, vollständige Lösung und andere Wiederbindung.

Die verbleibenden technischen Lesarten fallen in die bereits gebundenen
Baselines oder verworfenen Familien: feste Kopplung in B5, unabhängige
Empfänglichkeit in B1 bis B4, lokale Konkurrenz in B6, explizite Beziehung in
K3, Ressource in K7 und Historienarchiv in K8. Eine zustandsabhängige Kopplung
wäre ohne weitere Begründung bereits die programmierte Memorywirkung.

K6 wird deshalb nicht implementiert. Als Nächstes wird rollenweise geprüft, ob
`activation`, `afterimage`, `perception`, lokale Feldprobe und technische
Persistenz bereits einen Teil des notwendigen Memory-Substrats tragen oder ob
eine neue Zustandsrolle funktional notwendig ist. Dieser Abgleich bleibt vor
jeder Darstellungs- oder Updateentscheidung.

Der Rollenabgleich ist abgeschlossen. `activation` trägt die schnelle kausale
Feldlage. `afterimage` bewahrt kurze Geschichte, folgt der Aktivierung aber
einseitig und löst sich als feste Leaky-Baseline. `perception` und lokale
Feldproben werden pro Takt neu aus dem abgeschlossenen Vorfeld gebildet.
Technische Persistenz erhält nur den bereits vorhandenen Zustand.

Keine Rolle trägt Bildung, spätere kausale Mitprägung, vollständige
funktionale Lösung und andere Wiederprägung gemeinsam. Werden Aktivierung und
Nachhall angeglichen, kann die heutige Runtime unter derselben späteren
Weltgeschichte keinen erworbenen Funktionsunterschied erzeugen.

Damit ist eine zusätzliche kausal gelesene Zustandsrolle für organisches
Memory funktional notwendig. Das legt weder eine neue Variable noch Kante,
Gewicht, Topologie oder Gleichung fest. Als Nächstes folgt ausschließlich ein
darstellungsoffener Rollenvertrag für dieses fehlende Memory-Substrat.

Die technische Einordnung wurde mit 53 gezielten Zustands-, Feld-,
Nachhall-, Snapshot- und Geschichtsnulltests abgesichert; alle bestanden.
