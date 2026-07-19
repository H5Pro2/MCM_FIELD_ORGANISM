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
30 Ein-Sekunden-Fenster geöffnet. Die während der Startphase gemessene reale
Bildrate ersetzt im Live-Pfad die bloß angeforderte Sollrate. Beide
Hardwareleser laufen kontinuierlich. Auditive Callback-Zeiten und visuelle
Abschlusszeiten ordnen ihre reduzierten Zustände vorab begrenzten
Organismusfenstern zu. Erst wenn beide Rezeptorwege eine Fenstergrenze
abgeschlossen haben, wird dieses Fenster streng seriell im Feld fortgeschrieben.

Insgesamt wurden 442 visuelle und 3.439 auditive und visuelle Quellstützen
verarbeitet. 29 vollständige JSON-Checkpoints unterbrachen den Rezeptorkontakt
nicht, und es trat kein Audioüberlauf auf. Aufnahmeintervalle dürfen eine
Fenstergrenze überqueren; ihre eindeutige Zuordnung erfolgt nach Abschlusszeit.
Dadurch entstehen weder eine künstliche Lücke noch eine rückwirkende
Feldänderung.

Ein optionaler passiver Beobachter lieferte für alle 30 Fenster ausschließlich
Rezeptorzähler, Feldwertebereiche, Mittelbeträge, aktive Neuronenzahlen und
Felddigests. Er hält keine Rohdaten, ist kein gespeicherter Organismuszustand
und schreibt nicht zurück. Das Sitzungsergebnis hält weiterhin nur Feldzustand,
Fensterzahl, Quellstützenzahl und technische Zähler; Rezeptorsequenzen,
Handoffs und Gerätebezeichnungen wurden nicht gespeichert.

Für die erste passive Abgrenzung wiederholt der Beobachtungsweg jedes Fenster
außerdem in einem getrennten B0-Zweig. Dieser startet aus einer eigenständig
wiederhergestellten Kopie des wirklichen Fensteranfangszustands, verarbeitet
dieselben bereits reduzierten Rezeptorabschlüsse mit der unveränderten
schnellen Feld- und Nachhallmechanik und wird danach verworfen. Er besitzt keine
Rückwirkung und wird nicht Teil des Organismuszustands.

Im realen 30-Fenster-Lauf umfasste die Weltgeschichte 2.997 auditive und 443
visuelle Abschlüsse, insgesamt 3.440 Quellstützen. Kein Audioüberlauf trat auf.
Der maximale B0-Fehler betrug für Aktivierung und Nachhall jeweils `0.0`; alle
30 vollständigen Felddigests stimmten überein. Damit sind die wechselnden
beobachteten Feldlagen vollständig durch die bekannte schnelle Runtime und
ihren jeweiligen Weltkontakt reproduzierbar. Der Befund schließt spätere
organische Entwicklung nicht aus, weist sie im heutigen Beobachtungsraum aber
auch nicht nach.

Als nächster technischer Beobachtungsrahmen ist eine reale A-B-A-Außenwelt
angeschlossen. Der Browser zeigt und spielt eine äußere Folge aus 21 Sekunden
ruhigem Kontakt A, sieben Sekunden bewegtem und hörbarem Kontakt B und erneut
21 Sekunden A. Kamera und Mikrofon bleiben dabei die einzigen Zugänge. Der
Browser speist keine Daten direkt ein, hält keine Rohdaten und schreibt nicht
in das Feld zurück.

Für die räumliche Auswertung werden vollständige interne Feldlagen nur während
des passiven Laufs gelesen. Aus ihnen entstehen skalare L1-Abstände; die
Feldlagen selbst werden weder in der Runtime noch im Ergebnis als Memory
gehalten. Die verlängerte äußere Startreserve wird auditiv fortlaufend
verarbeitet, aber erst Abschlüsse ab dem gemeinsamen Phasenanker erreichen das
Feld. Dadurch bleibt das Gehör während der Vorbereitung aktiv, ohne den
Feldhorizont vorzeitig zu beginnen.

Der erste technisch gültige Lauf schloss 49 Ein-Sekunden-Fenster mit 5.601
Quellstützen, 48 Checkpoints und null Audioüberläufen ab. Alle Aktivierungs- und
Nachhallzustände waren mit maximalem B0-Fehler `0.0` reproduzierbar; alle 49
Felddigests stimmten überein.

Die A-B-A-Voraussetzung selbst wurde noch nicht erreicht. Die mittlere
Aktivierungsdistanz der einzelnen B-Fenster zur späten ersten A-Referenz betrug
`0,000164`, während die natürliche Streuung innerhalb dieser A-Referenz bereits
`0,000132` betrug. Die späte zweite A-Phase lag mit `0,000352` deutlich weiter
von der ersten A-Referenz entfernt. Nachhall zeigte dieselbe Driftgrenze.

Der Lauf trägt daher weder einen positiven noch einen negativen Memory-Befund.
Er zeigt einen vorgelagerten Funktionsmangel des Versuchsaufbaus: Die beobachtete
A-Feldlage ist noch nicht hinreichend wiederholbar, und B ist davon noch nicht
klar genug getrennt. Die Ursache darf aus diesem Lauf nicht allein Kamera,
Mikrofon oder Feld zugeschrieben werden.

Zur engeren Abgrenzung wurde anschließend ein reiner A-Stabilitätslauf ohne B
durchgeführt. Die beabsichtigte äußere Lage blieb über drei Blöcke zu je 21
Sekunden unverändert. Der Lauf schloss 63 Fenster, 7.210 Quellstützen und 62
Checkpoints ohne Audioüberlauf ab. B0 reproduzierte Aktivierung und Nachhall in
allen Fenstern mit Fehler `0.0`; alle 63 Felddigests stimmten überein.

Die späten Aktivierungsprofile lagen in Block 2 um `0,000429` und in Block 3 um
`0,000698` vom späten Profil des ersten Blocks entfernt. Der Abstand zwischen
Block 2 und 3 betrug `0,000339`. Zugleich sank die mittlere Streuung innerhalb
der drei späten Sieben-Fenster-Gruppen von `0,000222` über `0,000079` auf
`0,000037`. Beim Nachhall zeigte sich dieselbe blockweise Verschiebung.

Ein zweiter reiner A-Lauf trennte daraufhin reduzierte Rezeptorprofile und
Feldlage. Er schloss 63 Fenster, `7.191` Quellstützen, 895 Kamerabilder und 62
Checkpoints ohne Audioüberlauf ab. B0 reproduzierte alle Fenster mit Fehler
`0.0`; sämtliche 63 Felddigests stimmten überein.

Die auditive Rezeptorlage blieb eng: Ihre Blockabstände lagen zwischen
`0,000014` und `0,000019`. Die visuelle Rezeptorlage verschob sich gegenüber
Block 1 dagegen um `0,000659` in Block 2 und `0,001262` in Block 3. Die
Feldaktivierung verschob sich nahezu parallel um `0,000647` und `0,001155`, der
Nachhall um `0,000576` und `0,001088`.

Damit ist die frühere Mehrdeutigkeit wesentlich enger: Die blockweise
A-Wanderung ist bereits in der reduzierten visuellen Rezeptorlage vorhanden.
Sie belegt weder selbstständiges Feld-Einschwingen noch Memory. Für eine spätere
A-B-A-Prüfung wird zunächst eine äußerlich besser wiederholbare visuelle
Weltlage benötigt. Es wird weiterhin kein Memory-Zustand ergänzt.

Zwei zusätzliche technische Kontrollen schlossen einfache Ursachen enger aus.
Eine auf 300 Bilder verlängerte Kamerastartphase verringerte die visuelle Drift
nicht. In einem weiteren Lauf akzeptierte das OpenCV-Backend manuelle
Anforderungen für Belichtung, Weißabgleich und Fokus. Dennoch betrugen die
visuellen Abstände zu Block 1 `0,001501` und `0,002990`; Feldaktivierung
(`0,001453`, `0,002539`) und Nachhall (`0,001290`, `0,002562`) folgten.

Die Backend-Akzeptanz beweist keine unveränderliche Hardwareeinstellung. Der
Befund zeigt enger, dass weder längere Aufwärmung noch die angeforderten
manuellen Kamerakontrollen den physischen Bildschirm-Kamera-Pfad zu einer
wiederholbaren A-Quelle machen. Als nächste technische Nullkontrolle wird eine
deterministische Bildfolge direkt durch den vorhandenen visuellen Rezeptor- und
Feldpfad geführt. Die reale Kamera bleibt anschließend der Weltkontakt, wird
aber erst mit einer besser kontrollierten physischen Szene erneut verglichen.

Die deterministische visuelle Nullkontrolle ist nun ausgeführt. Ein einmal über
den unveränderten visuellen Rezeptor reduziertes räumliches Bild erzeugte in
allen 63 Fenstern exakt dieselbe 288-Träger-Lage. Zusammen mit 100 auditiven
Nullkontakten und 15 visuellen Kontakten pro Sekunde entstanden `7.245`
Quellstützen. Es wurden weder Bildfolgen gespeichert noch Werte in das Feld
zurückgeschrieben.

Der Abstand der späten Aktivierung zwischen Block 2 und Block 3 betrug
`4,3e-17`, beim Nachhall `6,3e-17`. Zwei unabhängig neu aufgebaute Läufe
stimmten in allen 63 Felddigests und im Enddigest überein. Die Differenz von
Block 1 zu den späteren Blöcken lag nur bei `3,3e-8` für Aktivierung und
`6,7e-8` für Nachhall und war nach Block 1 vollständig abgeklungen.

Damit ist der Feldkern unter exakt wiederholbarem Rezeptorkontakt stationär.
Die wesentlich größere Drift der realen Läufe entsteht vor dem Feld oder im
physischen Bildweg. Dieser Negativbefund trägt keine Memory- oder
Entwicklungsbehauptung. Als nächste reale Kontrolle ist eine unbewegte,
nichtleuchtende physische Szene erforderlich; erst danach kann A-B-A wieder
geöffnet werden.

Die daraufhin aktuell sichtbare reale Szene wurde zweistufig qualifiziert. Ein
21-Fenster-Lauf zeigte zunächst kleinere visuelle Blockabstände von
`0,000244` bis `0,000355`. Der 63-Fenster-Bestätigungslauf widerlegte jedoch
eine stationäre Langzeitlage: Die visuellen Abstände zu Block 1 betrugen
`0,000635` und `0,001108`, bei interner Streuung von `0,000248`, `0,000095`
und `0,000100`.

Die Feldaktivierung folgte mit `0,000481` und `0,000618`, während die auditive
Rezeptorlage mit Blockabständen um `0,000015` eng blieb. Alle 63 Fenster waren
weiterhin exakt B0-reproduzierbar und es trat kein Audioüberlauf auf. Die
aktuelle reale Szene ist damit ruhiger als der frühere Bildschirmweg, aber noch
nicht hinreichend wiederholbar. Kamera und Beleuchtung müssen vor dem nächsten
Lauf auf eine unbewegte physische Szene ausgerichtet werden; A-B-A bleibt bis
dahin geschlossen.

Zur Ursachenklärung wurde die visuelle Drift anschließend passiv in einen
globalen Kanalversatz und den verbleibenden räumlichen Rest zerlegt. Im
21-Fenster-Lauf betrug die visuelle Gesamtdifferenz zwischen Block 3 und Block 1
`0,000561`. Der mittlere globale Anteil der drei Farbkanäle betrug
`0,000097`; nach dessen Abzug verblieben `0,000554` räumliche L1-Differenz bei
einem lokalen Maximum von `0,005989`.

Die Größen sind nicht als additive Energiebilanz zu lesen. Sie zeigen jedoch
eindeutig, dass ein einzelner globaler Helligkeits- oder Farbsprung die Drift
nicht erklärt. Der lokale räumliche Anteil dominiert. Weder Normalisierung noch
Korrektur werden auf den Rezeptorinput angewendet; die Zerlegung liest nur die
bereits reduzierten 288 Träger und schreibt nichts zurück.

Die Außenbedingung des nächsten 63-Fenster-Laufs wurde nachträglich bestätigt:
Der Raum war unbewegt, das Licht ausgeschaltet und vor der Kamera fand keine
Aktivität statt. Die visuelle Gesamtdifferenz von Block 3 zu Block 1 betrug
dennoch `0,004522`. Alle drei Kanäle stiegen gemeinsam; der globale Anteil lag
bei `0,004501`. Zusätzlich blieben `0,002253` räumlicher Rest und ein lokales
Maximum von `0,014130`.

Die Feldaktivierung folgte mit `0,003895`, während die auditive Lage mit etwa
`0,000020` eng blieb. B0 reproduzierte wiederum alle 63 Fenster exakt. Der Lauf
zeigt somit eine stark wandernde visuelle Rezeptorlage, nicht autonome
Feldentwicklung. Genauer zeigt er, dass eine ruhende dunkle Außenwelt am realen
Kamerapfad keine ruhende Null-Rezeptorlage erzeugt. Sensor, technische
Verstärkung und Treiber sind in diesem Lauf nicht getrennt; daher wird die
Ursache nicht enger behauptet. Der Organismus erhält weder Rauschschwelle noch
Bildkorrektur. Die nächste A-Qualifikation benötigt stattdessen eine ruhig
beleuchtete unbewegte Szene.

Als beleuchteter Gegenlauf saß eine Person vor der Kamera. Diese Bedingung war
damit ausdrücklich keine starre A-Welt, sondern natürlicher visueller und
auditiver Weltkontakt. Über 63 Fenster stieg die visuelle Blockdifferenz bis
`0,005648`. Ihre Zerlegung enthielt `0,003138` globalen Kanalversatz,
`0,004583` räumlichen Rest und ein lokales Maximum von `0,039382`.

Anders als im ruhigen dunklen Raum veränderte sich nun auch die auditive
Rezeptorlage deutlich bis `0,001342`. Die gemeinsame Feldaktivierung folgte bis
`0,003432`, der Nachhall bis `0,003513`. Es gab keinen Audioüberlauf; alle 63
Fenster und Felddigests wurden durch B0 mit Fehler `0.0` reproduziert.

Der Lauf trägt damit E2 für den technischen gemeinsamen Audio-Video-Feldkontakt
unter natürlicher beleuchteter Teilnahme. Er zeigt nicht, dass das Feld die
Person erkennt, Bedeutungen bildet, lernt oder Memory organisiert. Für einen
späteren A-B-A-Vergleich wird weiterhin eine beleuchtete, menschenleere und
unbewegte Szene benötigt.

Ein zweiter beleuchteter Lauf mit anwesender Person umfasste erneut 63 Fenster.
Die visuelle Differenz von Block 3 zu Block 1 sank auf `0,000789`, die auditive
auf `0,000023`. Die Feldaktivierung lag bei `0,000541`, der Nachhall bei
`0,000458`. Die visuelle Zerlegung ergab `0,000508` globalen Anteil,
`0,000794` räumlichen Rest und ein lokales Maximum von `0,012265`.

Es trat kein Audioüberlauf auf. B0 reproduzierte alle 63 Fenster und Digests mit
Fehler `0.0`. Gegenüber dem ersten Personenkontakt war dieser Lauf deutlich
ruhiger. Das belegt keine Wiedererkennung und keine feste Repräsentation einer
Person, sondern die Abhängigkeit des Feldzustands von der konkreten laufenden
Außenwelt. Zwei verbal gleich bezeichnete Personenszenen sind technisch nicht
dieselbe Versuchsbedingung.

Diese menschenleere beleuchtete Kontrolle wurde anschließend über 63 Fenster
ausgeführt. Die visuelle Differenz von Block 3 zu Block 1 betrug `0,001480`,
die auditive `0,000137`. Damit lag die visuelle Änderung deutlich unter dem
dunklen Raum (`0,004522`) und der beleuchteten Personenszene (`0,005648`).

Die visuelle Zerlegung zeigte `0,001434` globalen Kanalversatz,
`0,000935` räumlichen Rest und ein lokales Maximum von `0,009048`. Die
Feldaktivierung folgte mit `0,001534`, der Nachhall mit `0,001276`. Es gab
keinen Audioüberlauf; B0 reproduzierte alle 63 Fenster und Digests exakt.

Der Lauf trägt eine klare Verbesserung der realen A-Bedingung, aber noch keine
stationäre A-Lage. Besonders der gleichgerichtete globale Kanalversatz bleibt
zu groß gegenüber der deterministischen Nullkontrolle. Da das Licht unmittelbar
vor dem Lauf eingeschaltet wurde, folgt genau eine Bestätigung nach längerer
Lichtlaufzeit. Diese Formulierung ist eine Versuchsbedingung, keine Freigabe
einer Helligkeitsregel oder Eingangsnormalisierung.

Der zweite Personenkontakt erfüllt diese offene Leerszenen-Wiederholung nicht.
Die A-B-A-Voraussetzung bleibt deshalb geschlossen.

Die anschließend tatsächlich menschenleere Wiederholung nach längerer
Lichtlaufzeit umfasste 63 Fenster und 7.483 Quellstützen. Die visuelle
Differenz von Block 3 zu Block 1 betrug `0,001762` und war damit größer als im
ersten Leerszenenlauf (`0,001480`). Die Zerlegung ergab `0,001615` globalen
Anteil, `0,001265` räumlichen Rest und ein lokales Maximum von `0,007571`.

Der auditive Eingang blieb mit `0,000017` ruhig. Feldaktivierung und Nachhall
folgten mit `0,001130` und `0,001107`. Es gab keinen Audioüberlauf; B0
reproduzierte alle 63 Fenster und Digests mit Fehler `0.0`.

Der Wiederholungslauf trägt daher den engen Negativbefund: Eine beleuchtete
menschenleere reale Kameraszene ist unter der vorhandenen Aufnahmebedingung
nicht stationär genug für eine exakte A-B-A-Referenz. Die Abweichung entsteht
bereits im visuellen Rezeptorprofil und wird von der unveränderten Feldruntime
erwartungsgemäß weitergetragen. Sie ist kein Hinweis auf autonome
Feldentwicklung.

Die Stabilitätssuche wird an dieser Stelle beendet. Eine passend gewählte
Toleranz, Rauschschwelle oder Eingangsnormalisierung würde die Außenwelt für den
gewünschten Versuch umdefinieren. Künftige Vergleiche müssen stattdessen die
tatsächlich gemessene Rezeptortrajektorie mitführen und jede zusätzliche
Feldbehauptung gegen die exakte B0-Vorhersage prüfen.

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

Der darstellungsoffene Memory-Substratvertrag ist jetzt formuliert. Fest
bleiben dürfen nur Kausalität, atomare Zeit, Lokalität, Gleichheit der lokalen
Naturbedingung, Endlichkeit, Organismuszeit, technische Fortsetzbarkeit und
passive Beobachtung.

Aus Weltgeschichte entstehen müssten konkrete Prägung, spätere kausale
Mitwirkung, Abschwächung, vollständige funktionale Wirkungslosigkeit und
erneute Prägbarkeit. Beziehung, Ressource, Topologie, Semantik und Bedeutung
werden nicht als Datenform oder Ergebnis vorgegeben.

Vor einem neuen Kandidaten folgt ein enger MINI_DIO-Abgleich zur
Memory-Substratfunktion. Übernommen werden nur getragene Funktionsgrenzen,
statische Sackgassen, Nullbefunde, Kontrollen und Baselines. Alte Variablen
oder Beziehungsmechaniken bleiben gesperrt.

Der MINI_DIO-Abgleich ist abgeschlossen. Das kontinuierliche Feld trug eine
reale, selbstlimitierende Nachhallspur und intrinsisch beobachtbare
Zustandsänderungen. Die bewegliche Beziehungsgeschichte entstand dagegen erst
passiv aus abgeschlossenen Weltprofilen. Sie war während des laufenden
Kontakts weder feldlokal verfügbar noch kausal zurückgelesen.

Die alte feste Neuronenkette mit indexabhängigen Gewichten, gerichteter
Vorgängerweitergabe und konstantem Kopplungsfaktor wird ausdrücklich nicht als
organische Ordnung übernommen. MINI_DIO liefert damit keinen fertigen
Memory-Substratmechanismus, sondern zwei getrennte Teilfunktionen und starke
Ausschlüsse.

Als Nächstes wird die lokale Ereignisquellgrenze der aktuellen MCM-Runtime
bestimmt. Vor jeder neuen Zustandsrolle muss getrennt werden, welche lokale
Zustandsänderung bereits im atomaren Feldfortschritt kausal vorliegt und
welche Form erst durch Feldprobe oder Observer entsteht. Darstellung,
Gleichung und Runtime bleiben geschlossen.

Die lokale Ereignisquellgrenze ist bestimmt. `MCMNeuronDrive` trägt bereits
den abgeschlossenen Eigenzustand, lokale Aktivierungs- und Nachhallproben,
aktuellen beziehungsweise transienten Rezeptorkontakt und die Organismuszeit.
Die nächste Aktivierung und der nächste Nachhall entstehen erst durch die
Transition und werden atomar mit der vollständigen nächsten Schicht wirksam.

Eine eigene Ereignisprägung existiert nicht. Die frühere passive
Übergangsevidenz wurde als festes Produkt aus aktuellem Kontakt und vorheriger
Nachbaraktivierung im Observer berechnet. Sie entsprach exakt der festen
Ein-Schritt-Nachbarschaft, wurde nicht gespeichert und wirkte nicht zurück.

Die Grenze wurde mit 54 gezielten Neuronen-, Schicht-, Feldsubstrat-,
Übergangsevidenz-, transienten Eingangs- und Geschichtsnulltests abgesichert;
alle bestanden.

Als Nächstes wird ausschließlich ein atomarer
Zustandsrollen-Erweiterungsvertrag formuliert. Er darf die Einbindung einer
noch opaken lokalen Memory-Rolle in Vorzustand, Vorschlag, nächste Schicht und
Snapshot bestimmen, aber keine Datenform, Dimension, Kopplung oder
Updategleichung wählen.

Der atomare Zustandsrollen-Erweiterungsvertrag ist formuliert. Eine spätere
Memory-Rolle müsste sichtbar zum lokalen Neuronenzustand gehören, aus dem
abgeschlossenen Vorzustand gelesen, gemeinsam mit dem vollständigen nächsten
Schichtzustand vorgeschlagen und vollständig im Snapshot getragen werden.
Fehlgeschlagene Vorschläge dürfen keinen Teilzustand hinterlassen.

Die Rolle wird nicht automatisch als neue lokale Nachbarprobe freigegeben.
Eine solche Probe würde bereits dieselbe feste Anatomie, Leserichtung und
Öffentlichkeit wie Aktivierung und Nachhall vorgeben. Auch vorherige
`perception`, Observerausgaben und transiente Dockverläufe dürfen nicht als
verdecktes Archiv fortgeschrieben werden.

Als Nächstes wird geprüft, ob eine reine opake Nullzustandshülle technisch und
methodisch sinnvoll implementierbar ist oder nur eine unbegründete leere
Datenstruktur in die Runtime einführt. Bis dahin bleibt die Runtime
unverändert.

Der Zulässigkeitsaudit der opaken Nullzustandshülle ist abgeschlossen. Eine
digitale Hülle kann nicht vollständig darstellungsneutral sein: `None`, leere
Bytes, Tupel oder abstrakte Objekte legen bereits Slot, Gleichheit,
Serialisierung und Migration fest.

Gleichzeitig würde eine solche Hülle keine Bildung, spätere Wirkung,
vollständige Lösung oder erneute Prägung prüfen. Sie würde 16
MCMNeuron-Konstruktionsmodule, 15 MCMNeuronOutput-Module, das Snapshot-Schema
und zahlreiche Verträge verändern, ohne eine neue kausale Aussage zu tragen.
Die Hülle wird deshalb nicht implementiert.

Als Nächstes wird kausale Zustandsäquivalenz formuliert. Eine zusätzliche
Darstellung ist erst begründet, wenn unterschiedliche frühere Weltgeschichten
nach Angleichung der schnellen Zustände unter mindestens einer identischen
späteren Weltfolge verschiedene Feldbildung tragen müssen.

Der Vertrag der kausalen Zustandsäquivalenz ist formuliert. Zwei
Weltgeschichten gelten funktional als gleich, wenn nach Angleichung aller
bekannten kausalen Rollen jede identische zulässige Zukunft dieselbe
Feldtrajektorie trägt. Ein reproduzierbarer Gegenfall genügt, um diese
Äquivalenz zu widerlegen.

Die bestehende Runtime-Null trägt den Gleichheitsfall: Nach vollständiger
Angleichung des kausal gelesenen Schichtzustands erzeugen unterschiedliche
frühere Kontaktfolgen unter identischer Fortsetzung dieselbe Feldantwort.
Rohdatenunterschiede allein begründen daher keinen Speicher.

Gleichzeitig wurde die stärkste verbleibende Lücke markiert: Ein willkürlich
gespeichertes Geschichtsbit könnte mit einem festen Leser künstlich
Nichtäquivalenz erzeugen. Als Nächstes muss deshalb weltbegründete Relevanz
von eingebauter Unterscheidung getrennt werden.

Die weltbegründete Relevanzgrenze ist formuliert. Sie trennt drei notwendige
Nachweise: Die vergangene Weltgeschichte muss nach Angleichung des schnellen
Zustands Information über eine noch unbekannte spätere Rezeptorfortsetzung
tragen; eine innere Spur muss ausschließlich aus dieser Geschichte entstehen;
und diese Spur muss die spätere Feldaufnahme kausal vermitteln.

Relevanz ist dabei kein Optimierungsziel. Das Feld erhält weder Zukunftslabel
noch Vorhersagefehler oder Reward. Der passive Observer prüft erst nachträglich
auf unabhängigen Holdoutfortsetzungen, ob Weltstruktur, innere Trägerspur und
Feldwirkung zusammenfallen.

Als Nächstes wird ausschließlich die minimale passive Weltfamilie
vorregistriert. Sie erhält noch keine Memory-Rolle und verändert die Runtime
nicht.

Die minimale passive Weltfamilie der verdeckten Fortsetzung ist
vorregistriert. Zwei gespiegelte sichtbare Anfluggeschichten laufen während
einer Verdeckung nach derselben äußeren Dynamik weiter. Der Vergleich erfolgt
erst, wenn `activation`, `afterimage` und der vollständige bekannte schnelle
Schichtzustand exakt kollidieren. Danach erzeugt die Welt neue gespiegelte
Austrittskontakte.

Die erwartete Trennung ist bewusst eng: Die Weltgeschichte trägt Information
über die spätere Rezeptorfortsetzung, während die heutige Runtime vor dem
Austritt keine geschichtsabhängige Feldwirkung mehr besitzt. Das zeigt noch
kein Memory, sondern begründet nur eine nicht tautologische Weltfunktion, die
ein späterer Träger erfüllen könnte.

Als Nächstes werden ausschließlich Weltgenerator, passive Leckprüfung und
kompakte Auswertung umgesetzt. Memory-Rolle und Feldmechanik bleiben
unverändert.

Der passive Weltlauf der verdeckten Fortsetzung ist umgesetzt. In 36
unabhängigen Zweigen kollidierten aktuelle Rezeptorlage, `activation`,
`afterimage`, vollständiger Layer-Digest und vollständiger Snapshot-Digest bei
Frameindex `3`. Erst danach entstanden die neuen gespiegelten
Austrittskontakte. Die unabhängige Fortsetzungspermutation W1 entfernte die
Abhängigkeit vollständig.

Damit ist weltbegründete Relevanz für diese enge Weltfamilie getragen. Der Lauf
zeigt zugleich eine klare Scheitergrenze: Eine endliche Leaky-Spur bewahrt
einen Richtungsrest; Übergangszähler und fester Bewegungsautomat erklären den
Austritt vollständig.

Es wird deshalb keine Memory-Rolle freigegeben. Als Nächstes wird eine
nichtstationäre Weltbeziehungsgrenze formuliert, die Erhaltung, natürliche
Lösung und erneute Relevanz ohne Phasenlabel gemeinsam prüfbar macht.

Die nichtstationäre Weltbeziehungsgrenze ist formuliert. Sie übersetzt den
Memory-Lebenszyklus in einen kontinuierlichen äußeren Weltstrom: Eine
Fortsetzungsbeziehung ist zunächst relevant, verändert sich später ohne
Umschaltlabel und wird erst durch neue reale Kontaktgeschichte ersetzt.

Lösung bedeutet dabei, dass die alte Geschichte nach neuer Erfahrung keine
zusätzliche Information über spätere Fortsetzung trägt. Erneute Prägung
bedeutet, dass die neue Geschichte diese Relevanz übernimmt. Eine sofortige
Anpassung beim ersten unbeobachtbaren Weltwechsel wird ausdrücklich nicht
gefordert.

Als Nächstes wird die minimale kontinuierliche Zwei-Beziehungs-Weltfamilie
vorregistriert. Eine innere Memory-Rolle bleibt weiterhin gesperrt.

Die minimale kontinuierliche Zwei-Beziehungs-Weltfamilie ist jetzt
vorregistriert. Ein Kontakt besteht aus sichtbarem Anflug, physischer
Verdeckung, sichtbarem Austritt und gewöhnlichem kontaktarmen Zwischenraum.
`R0` erhält die räumliche Fortsetzungsbeziehung, `R1` kehrt sie technisch
symmetrisch um. Beide verwenden dieselben Rezeptoren, Docks, Zeit-, Energie-
und Geometriebudgets.

Der Beziehungswechsel findet ausschließlich in der Außenwelt statt. Getrennte
kontinuierliche Lebensläufe prüfen neue Erfahrung nach `0/1/2/4/8`
abgeschlossenen Kontakten, ohne daraus eine feste Lernschwelle zu machen.
Verschobene Wechselstellen, K0 bis K7 und B0 bis B9 verhindern, dass
Phasenzeit, Ereigniszahl, Randhäufigkeit oder ein einfacher Leaky-Träger
übersehen werden.

Als Nächstes werden ausschließlich der äußere kontinuierliche Weltgenerator,
passive Observer und die vorregistrierten Baselines umgesetzt. Eine
Memory-Rolle, Updategleichung oder Feldruntime-Erweiterung bleibt gesperrt.

Der kontinuierliche äußere Weltgenerator und die passiven Observer sind nun
umgesetzt. Der kanonische Lauf umfasst `768` Beobachtungen über K0 bis K7,
Erfahrungsstufen `0/1/2/4/8`, Wechselstellen `6/8/10`, vier balancierte
Ordnungsvarianten, zwei Dauerzuordnungen und beide Holdoutseiten.

Alle Zweige bleiben vom ersten bis zum letzten Takt auf einem fortlaufenden
gemeinsamen Feld. Kontrollbezeichnungen und Weltbeziehungen erreichen die
Runtime nicht. Identische unveränderliche Lebenspräfixe dürfen technisch
wiederverwendet werden; jede Fortsetzung erzeugt weiterhin einen eigenen
neuen Feldzustand.

Dieser Stand prüft die Außenweltmechanik, nicht organisches Memory. Als
Nächstes werden ausschließlich B0 bis B9 umgesetzt.

B0 bis B9 sind nun passiv umgesetzt. B0 bestätigt vor den unbezeichneten
Holdouts die exakte Null von `activation` und `afterimage`. B1 und B4 liegen
insgesamt bei `0,5`; Ereigniszahl und exakte Templates tragen die
Weltfamilie nicht allgemein.

Die entscheidende Scheitergrenze ist B6. Ein fester Zwei-Regime-Leser, der
nur die zuletzt real beobachtete Beziehung verwendet, trägt nach mindestens
einem neuen Kontakt alle späteren K3- und K7-Holdouts. B9 mit permanenter
Doppelspeicherung erzeugt bei gleichem Leser exakt denselben Befund.

Damit gibt die Weltfamilie keine Memory-Mechanik frei. Als Nächstes muss vor
jeder weiteren Implementierung geklärt werden, welche kleinste reale
Weltfunktion eine neu erfahrbare Beziehungsform verlangt, ohne mögliche
Beziehungen bereits als feste Regime vorzugeben.

Die offene Weltbeziehungsform-Grenze ist nun formuliert. Sie ersetzt die
Auswahl zwischen bekannten Regimen durch neue konkrete Fortsetzungsformen,
deren Werte in früheren Lebensabschnitten nicht vorkamen. Neue Anfluglagen
prüfen zusätzlich, ob eine Beziehung statt einer konkreten Kontaktfolge
getragen wird.

Eine affine lokale Fortsetzung mit mindestens zwei Freiheitsgraden ist nur ein
möglicher kleinster Weltträger. Sie wird noch nicht implementiert. Selbst ein
positiver Lauf müsste gegen exakte Zwei-Punkt-, laufende Ausgleichs- und
rekursive Schätzer bestehen; deren Erfolg würde noch keine organische
Feldorganisation zeigen.

Als Nächstes wird deshalb nur auditiert, ob diese affine Prüfwelt minimal und
fair ist oder bereits unnötige mathematische Struktur vorgibt.

Der Weltträgeraudit ist abgeschlossen. Eine reine Verschiebung fällt erneut
auf einen letzten skalaren Beziehungswert zurück. Die affine Welt verlangt
zwar zwei Kontakte, legt aber eine globale Formel vor, die ein exakter
Zwei-Punkt-Schätzer vollständig trägt. Sie bleibt deshalb nur Baseline.

Eine freie Lookupwelt wurde ebenfalls verworfen, weil neue lokale Lagen ohne
Weltregularität nicht identifizierbar wären. Bedingt zugelassen ist eine
lokal stetige, nachweislich nichtaffine Deformationswelt. Sie gibt keine
globale Parameterform vor, erlaubt aber lokale Holdouts zwischen erfahrenen
Nachbarlagen.

Die
[minimale lokal stetige Deformationswelt](architektur/060_MINIMALE_LOKAL_STETIGE_DEFORMATIONSWELT.md)
ist vorregistriert. Sie legt die konkrete Außenwelt, D0 bis D5, G0 bis G7 und
L0 bis L9 fest. Bei vollständiger lokaler Erfahrung wird eine exakte Erklärung
durch L4 erwartet. Der
[Baselinebefund](forschung/008_LOKALE_DEFORMATIONSWELT_BASELINEBEFUND.md)
bestätigt L4 für alle 110 fair identifizierbaren Holdouts; daraus folgt keine
Memory-Freigabe.

Die
[feldgetragene Beziehungswirkungsgrenze](architektur/061_FELDGETRAGENE_BEZIEHUNGSWIRKUNGSGRENZE.md)
bestimmt den verbleibenden Mangel inzwischen als fehlende innere Feldwirkung
vor dem Austrittskontakt. Eine äußere Archiv- und Interpolatorausgabe erfüllt
diese Funktion nicht.

Der
[Kandidatenfamilienaudit](architektur/062_KANDIDATENFAMILIEN_FELDGETRAGENE_BEZIEHUNGSWIRKUNG.md)
verwirft die bekannten statischen Familien. Nur ein lokales hysteretisches
Feldmedium bleibt bedingt prüfbar, aber nicht als Kandidat zugelassen.

Als Nächstes wird ausschließlich seine mögliche intrinsische lokale
Beanspruchungsquelle in der heutigen Feldtransition auditiert. Memory-Rolle
und Feldruntime bleiben geschlossen.

Der
[Quellenaudit](architektur/063_AUDIT_INTRINSISCHE_LOKALE_FELDBEANSPRUCHUNGSQUELLE.md)
zeigt: Der feste lokale Diffusionsfluss wirkt bereits vor jedem Observer im
Feld. Er ist jedoch vollständig aus dem schnellen Zustand und der festen
Anatomie rekonstruierbar. Nach Angleichung von Aktivierung und Nachhall bleibt
keine geschichtliche Beanspruchungsdifferenz.

F8, eine neue Zustandsrolle und die Runtime bleiben deshalb geschlossen. Als
Nächstes wird ausschließlich die Redundanz des momentanen Flusses passiv
geprüft.

Die passive
[Fluss-Redundanzprüfung](forschung/009_INSTANTANER_FELDFLUSS_REDUNDANZBEFUND.md)
ist abgeschlossen. Sechs Kontrollen bestätigen: gerichtete Nachbarflüsse
rekonstruieren exakt den vorhandenen Diffusionsgenerator, die öffentlichen
Vortaktproben genügen vollständig und der Observer verändert das Feld nicht.

Damit ist der momentane Fluss kein eigener geschichtlicher Träger. Als
Nächstes wird keine Flussspur implementiert, sondern die feste
Diffusionsanatomie auf ihre Lösungs- und Wiederbindungsgrenze auditiert.

Der
[Audit der festen Diffusionsanatomie](architektur/064_GRENZE_DER_FESTEN_DIFFUSIONSANATOMIE.md)
trennt nun drei Vorgänge: schnelle Relaxation, erneute Aufnahme von Weltkontakt
und echte Wiederbindung. Die ersten beiden sind vorhanden. Wiederbindung ist
im heutigen Zustandsvertrag nicht darstellbar, weil keine Beziehung gebunden
oder freigegeben wird.

Veränderliche Kanten sind dadurch nicht freigegeben. Die Kandidatensuche ist
vor weiterer Mechanik an einer dokumentierten Sättigungsgrenze gestoppt.

Die anschließende
[physische Substratklärung](architektur/065_PHYSISCHE_MINDESTANFORDERUNG_ORGANISCHES_MEMORY_SUBSTRAT.md)
bestimmt die kleinste notwendige Eigenschaft als begrenzte, lokal
feldgetriebene und funktional reversible Pfadabhängigkeit. Sie korrigiert
zugleich eine mögliche Überdehnung des Flussbefunds: Der momentane Fluss trägt
keine zusätzliche Information, kann aber lokale Schreibursache eines anderen
Substrats sein.

Noch ist weder Zustandsform noch Gleichung ausgewählt. Vor jeder
Implementierung wird die Tragfähigkeit eines einzelnen lokalen
Substratzustands konzeptionell geprüft.

Der
[Audit des isolierten lokalen Substratzustands](architektur/066_GRENZE_EINES_ISOLIERTEN_LOKALEN_SUBSTRATZUSTANDS.md)
zeigt inzwischen seine Grenze: Ein einzelner Skalar kann zwar Geschichte
tragen, bleibt bei glattem Leaky-Zerfall aber nur asymptotisch lösbar. Endliche
funktionale Lösung fällt auf programmierte Kollisions- oder Leserbaselines
zurück.

Diese Klasse bleibt geschlossen. Als Nächstes wird ausschließlich geprüft, ob
eine räumlich verteilte homogene Substratlage eine grundsätzlich andere
Organisationsform erlaubt, ohne Kantenidentität oder Zieltopologie vorzugeben.

Der
[Audit des homogen verteilten Skalarsubstrats](architektur/067_GRENZE_EINES_HOMOGEN_VERTEILTEN_SKALARSUBSTRATS.md)
beantwortet diese enge Frage negativ. Die vorhandene MCM-Runtime besitzt
bereits viele lokal gekoppelte Träger. Gewöhnliche positive Diffusion glättet
deren räumliche Unterschiede und erzeugt keine neue geschichtliche
Übertragungsbedingung.

Komplexe räumliche Muster bleiben grundsätzlich möglich, benötigen aber
zusätzliche Reaktionsrollen, Attraktoren, Erhaltungs- oder Zielstrukturen. Eine
sichtbare Feldform wäre außerdem noch kein organisches Memory. Vor jeder
Implementierung wird deshalb nur geprüft, ob die vorhandene schnelle Feldlage
mit genau einer homogenen lokalen Materialdisposition reziprok gekoppelt
werden kann, ohne eine zweite Leaky-Spur oder versteckte adaptive Kante zu
programmieren.

Der
[Audit der reziproken Feld-Material-Kopplung](architektur/068_REZIPROKE_FELD_MATERIAL_KOPPLUNG_UND_KONSTITUTIVE_SAETTIGUNG.md)
gleicht diese letzte abstrakte Rollenklasse mit K2, K6 und F8 ab. Eine
wechselseitige Abhängigkeit zwischen schneller Feldlage und hypothetischer
Materialdisposition bestimmt noch keine Physik. Ihre konkreten Lesarten sind
bereits als Spur, fester Leser, Empfänglichkeit, implizite adaptive Kante,
Ressource oder Attraktor geprüft.

Damit ist nicht digitales organisches Memory widerlegt. Wohl aber ist die
abstrakte Kandidatensuche gesättigt. Vor einer Gleichung muss ein neutrales
Materialprinzip unabhängig von der gewünschten Memory-Funktion begründet
werden. Als engste verbleibende Frage wird nur lokale Feldarbeit unter einer
Passivitäts- oder Energiebilanz geprüft; auch dies gibt weder Zustand noch
Runtime frei.

Die abschließende passive
[quadratische Feldbilanz](forschung/010_PASSIVITAET_DES_BESTEHENDEN_FELDES_NULLBEFUND.md)
schließt für kontaktfreie und rezeptorgetriebene Zustände mit Fehler null.
Feld- und Verteilungsdigests bleiben unverändert; kein Akkumulator und kein
neuer Runtime-Zustand entstehen.

Der zugehörige
[Architekturaudit](architektur/069_PASSIVITAET_FELDARBEIT_UND_ENDE_DER_SUBSTRATHERLEITUNG.md)
zeigt damit den entscheidenden Nullbefund: Das heutige Feld ist bereits
mathematisch passiv, ohne organisches Memory zu besitzen. Passivität kann eine
spätere Materialhypothese kontrollieren, leitet sie aber nicht her.

Die automatische Substratkandidatensuche ist beendet. Empfohlen ist die
unveränderte Feldruntime unter längerer realer Weltteilnahme. Eine konkrete
Materialgleichung darf nur als ausdrücklich gewählte Hypothese und nicht als
zwingende Folge der bisherigen MCM-Befunde eingeführt werden.

Diese ausdrückliche Wahl wurde anschließend getroffen. Eine kontrollierte
prozedurale Audio-Video-Welt erzeugt nun zwei dreisekündige Verläufe mit
identischer Geschichte bis zur letzten Wiederkehr. Beide verwenden die
vorhandenen auditiven und visuellen Rezeptoren sowie dieselbe gemeinsame
Feldruntime; Rohmaterial, Labels und Bedeutungen werden nicht in den
Organismuszustand übernommen.

Parallel ist ein passiver lokaler Synapsenkandidat umgesetzt. Er trägt pro
lokaler Nachbarschaft eine flexible und eine stabilisierte Wirksamkeit.
Wiederholte lokale Koaktivität kann beide Lagen aufbauen, ausbleibende
Koaktivität schwächt sie, und ein lokales Budget begrenzt konkurrierende
Wirksamkeiten.

Dies ist noch kein organisches Memory. Der Kandidat besitzt keine
Runtime-Rückwirkung und die vollständige Lösung sowie andere Wiederbindung sind
noch nicht gezeigt. Vor jedem Anschluss an das gemeinsame Feld folgen
Vergleiche gegen Null, unmittelbare Koaktivität, Leaky-Spur und feste lokale
Kopplung.

Der erste passive Vergleich ist abgeschlossen. Die beiden Weltzweige waren im
gemeinsamen Präfix exakt identisch und erhielten nach unterschiedlicher dritter
Erfahrung eine identische frische Probe. Der flexible Kandidatenzustand trug
danach `0,001273` Zweigdifferenz und war damit exakt gleich einer Leaky-Spur.

Die stabilisierte Kandidatenlage trug `0,000827`; eine faire
Zwei-Leaky-Kaskade trug bereits `0,000796`. Der kleine verbleibende Unterschied
ist durch die eingesetzte Freigabe-, Sättigungs- und Budgetform mit verursacht
und noch keine eigenständige Memory-Funktion.

Die Runtime bleibt unverändert. Vor einer Rückwirkung folgt eine einzige
Lebenszyklusprüfung auf Aufbau, Unterbrechung, Lösung und andere
Wiederbeanspruchung. Falls die Zwei-Leaky-Kaskade auch diesen Verlauf erklärt,
wird dieser Kandidatenzweig geschlossen.

Die Lebenszyklusprüfung ist abgeschlossen. Vier Kontaktphasen A prägten alle
290 vorhandenen lokalen Beziehungen. Nach acht Unterbrechungsphasen lag die
stabilisierte Kandidatenlage bei `0,004225` gegenüber `0,003682` nach dem
Aufbau. Die alte Lage wuchs damit auf `114,8 %`, statt sich vollständig zu
lösen.

Kontakt B veränderte den Kandidaten um `0,003230` und die Zwei-Leaky-Baseline
bereits um `0,002995`. Das lokale Budget war mit maximal `0,117670` von `0,8`
nicht wirksam. Selektive Organisation, Lösung und Ressourcenwiederbindung sind
nicht gezeigt.

Der amplitudenbasierte Synapsenkandidat ist verworfen und wird weder optimiert
noch an die Runtime angeschlossen. Als nächste konzeptionelle Frage bleibt nur,
ob lokale zeitliche Ursache oder Reihenfolge eine selektive Prägung begründen
kann, ohne eine Schwelle, Gewinnerregel oder Zieltopologie einzubauen.

Diese Frage ist passiv geprüft. Zwei kontrollierte Audio-Video-Phasen wurden
als `A -> B` und `B -> A` durch dasselbe gemeinsame Feld geführt. Ein fester
antisymmetrischer Ein-Schritt-Leser unterschied die Reihenfolge, erzeugte aber
bei allen 290 gerichteten lokalen Beziehungen einen von null verschiedenen
Wert. 250 Beziehungen wechselten das Vorzeichen; die vollständige Umkehr blieb
wegen Feldgeschichte, Diffusion und Nachhall aus.

Damit ist zeitliche Richtung als Feldbeobachtung bestätigt, nicht als
selektive Prägungsquelle. Es entsteht kein neuer Zustand, keine Lösung, keine
Wiederbindung und keine spätere Wirkung. Eine neue Memory-Mechanik bleibt
geschlossen.

Die nächste Richtung ist deshalb keine weitere mathematische Leserform. Als
offen benannte biologische Hypothese wird strukturelles lokales
Kontaktmaterial gewählt. Anders als der verworfene Synapsenkandidat legt diese
Hypothese nicht für jede Nachbarschaft einen Beziehungszustand an.

Zunächst wird ausschließlich ein anatomischer Zustandsvertrag vorbereitet.
Konkrete Materialdynamik, Kopplung und Runtime-Rückwirkung bleiben
geschlossen.

Dieser Vertrag ist umgesetzt. Für 84 MCM-Neuronen entstehen 336 lokale
Oberflächenrichtungen ohne Partneridentität. Das gesamte Material liegt
neutral und ungebunden beim jeweiligen Neuron. Aufbau und Snapshot verändern
das gemeinsame Feld nicht.

Reflexion ist außerdem von Sprache getrennt. Der früheste mögliche innere
Dialog ist eine vorsprachliche, zeitlich getrennte Rückwirkung eigener
Feldgeschichte auf dasselbe gemeinsame Feld. Eigene Bezeichnungsformen und
weltlich erlernte Sprache liegen auf späteren Entwicklungsstufen.

Alphabet, Wörter, Grammatik und vortrainierte Sprachmodelle werden nicht in
den Organismuskern aufgenommen.

Der nächste technische Baustein richtet die bereits vorhandenen
Vortaktursachen passiv an den neutralen Kontaktoberflächen aus. Lokale
Feldprobe und momentaner gerichteter Fluss besitzen eine
Oberflächenrichtung. Eigenaktivierung und Rezeptorkontakt bleiben
neuronlokal.

Diese Abbildung verändert weder Kontaktmaterial noch MCM-Feld und enthält
keine Schreib-, Wachstums- oder Gewinnerregel. Sie bestimmt damit nur, welche
Ursachen räumlich vorhanden sind, nicht wie organisches Memory entsteht.

Für jede spätere Materialdynamik ist nun zusätzlich festgelegt: Die endliche
Materialmenge bleibt Eigentum des einzelnen MCM-Neurons. Nur ihre Verteilung
zwischen ungebundenem Anteil und eigenen Oberflächen darf sich ändern.

Fortschreibung muss atomar, nichtnegativ, iterationsneutral und geometrisch
äquivariant sein. Die Welt darf Asymmetrie erzeugen; der Code darf keine
Richtung, Modalität oder Verbindung bevorzugen. Eine konkrete
Umverteilungsregel ist noch nicht gewählt.

Ein passiver Zulassungsrahmen prüft nun vollständige
Materialfortschreibungsvorschläge gegen diese Grenzen. Er erkennt unter
anderem veränderte Eigentümergesamtmengen, spontane Struktur aus dem
Neutralzustand und feste Richtungsbevorzugung.

Der Rahmen wendet keinen Vorschlag an, enthält keine Materialregel und erteilt
keine Runtime-Freigabe.

Der anschließende Kandidatenklassenaudit zeigt eine Grenze der bisherigen
Darstellung. Eine skalare Materialmenge pro Oberfläche kann Bilanz und lokale
Konkurrenz ausdrücken, aber keine räumliche Berührung. Als funktionaler Leser
wäre sie erneut ein adaptives Richtungsgewicht oder ein Schwellenkontakt.

Für die strukturelle Hypothese fehlt daher noch eine minimale partnerlose
Morphologie, die Lage oder Ausdehnung, Rückzug und geometrische Berührung
unterscheidbar macht. Eine konkrete Darstellung oder Dynamik ist noch nicht
gewählt.

Als minimale Zustandsklasse ist nun ein radiales Eigentümerprofil pro lokaler
Oberflächenrichtung festgelegt. Es beschreibt Material entlang einer
normierten Raumkoordinate von neuronennaher Lage bis zur geometrischen
Grenzfläche.

Das Profil speichert weder Partner noch Beziehung. Radiale Auflösung,
Materialbewegung, Kontaktwirkung und Feldrückwirkung sind noch nicht
bestimmt.

Die neutrale endliche Profilanatomie ist umgesetzt. Bei einer expliziten
technischen Vier-Zellen-Auflösung entstehen für 84 Neuronen 336 radiale
Richtungsprofile und 1344 leere Materialzellen.

Alle Eigentümermengen bleiben vollständig ungebunden. Es existieren weder
Grenzflächenmaterial noch Berührung, Transport oder Feldwirkung. Die
Auflösung besitzt keinen versteckten Standardwert.

Die erste Transportklassenabgrenzung lässt nur konservative endliche
Advektion als passiven Morphologiekandidaten offen. Reine Diffusion,
Potentialangleichung sowie Wachstum und Zerfall fallen erneut auf Glättung,
Leaky-Spur, Attraktor oder Amplitudendynamik zurück.

Noch existieren weder Geschwindigkeit noch Materialbewegung. Zunächst wird
nur ein radialer Flussvertrag vorbereitet, der fremde Transportvorschläge
prüfen kann.

Als weitere reale Ursachenklasse ist nun endogener Eigenkontakt technisch
geöffnet. Eine zustandslose `EndogenousReceptorSurface` übergibt vollständig
vorgegebene lokale Messwerte über denselben Rezeptorenverteiler und dieselbe
gemeinsame MCM-Neuronenschicht wie äußere Sensoren.

Die Schnittstelle erzeugt kein Rauschen, keine Stimmung und keinen gehaltenen
Grundwert. Eine passive Kontinuitätsprüfung meldet Messlücken, ohne sie zu
füllen. Damit ist nur der fehlende Eingangsort vorbereitet; reale innere
Sensorik und jede Wirkung auf organisches Memory bleiben offen.

Als Nächstes wird eine begrenzte kontrollierte endogene Quelle vorbereitet.
Sie soll langsame und schnelle Eigenkontaktverläufe liefern, ohne diesen
Bedeutungen zuzuweisen. Danach kann ihr Zusammenspiel mit Audio- und
Videokontakt im selben Feld geprüft werden.

Die kontrollierte endogene Quelle ist nun umgesetzt. Sie besteht nur aus
expliziten technischen Trägerwerten und Zeitfenstern. Dieselbe Quelle erzeugt
reproduzierbar dieselben Rezeptorzustände; es existieren weder
Zufallsgenerator noch semantische Körperkategorien.

Eine technische gemeinsame Feldprobe bestätigt außerdem, dass äußerer und
endogener Kontakt über denselben Verteiler in dieselbe MCM-Neuronenschicht
gelangen. Ihre Werte bleiben an ihren jeweiligen lokalen Docks erhalten.

Als Nächstes wird ausschließlich passiv geprüft, ob beide Ursachen nach der
vorhandenen lokalen Feldwirkung weiterhin auseinandergehalten werden können.
Diese Nullprüfung ergänzt kein Memory und keine Kontaktmaterialbewegung.

Diese Ursachenüberlagerungs-Nullprüfung ist abgeschlossen. Vier kontrollierte
Zweige trennen gemeinsame Wirkung, äußere Einzelwirkung, endogene
Einzelwirkung und vollständigen Nullkontakt.

Beide Ursachen bleiben in Aktivierung und schnellem Nachhall ungleich null
und räumlich voneinander verschieden. Ihre gemeinsame Wirkung entspricht bis
zur numerischen Toleranz der Summe beider Einzelwirkungen über dem
Nullzweig.

Der Befund trägt nur die technische Koexistenz beider Ursachen im selben
Feld. Die vorhandene lineare Runtime erzeugt keinen unerklärten gemeinsamen
Rest und damit weder Memory noch entwickelte innere Organisation.

Als Nächstes wird der passive radiale Flussvertrag umgesetzt. Er prüft
vollständige Transportvorschläge, ohne selbst eine Geschwindigkeit oder
Wachstumsursache einzubauen.

Der passive radiale Flussvertrag ist nun umgesetzt. Er beschreibt vollständige
Grenzflüsse an jeder radialen Zellgrenze und rekonstruiert daraus nur dann
einen möglichen Folgezustand, wenn jede Eigentümerbilanz erhalten und jede
Materialmenge nichtnegativ bleibt.

Alle Richtungsprofile eines Neurons greifen auf denselben ungebundenen Anteil
zu. An der äußeren Grenze darf kein Material das Neuron verlassen. Abweichende
radiale Auflösungen werden nicht stillschweigend abgebildet.

Der Vertrag besitzt weiterhin keine Geschwindigkeit und keine kausal
zugelassene Bewegungsursache. Auch ein angenommener Vorschlag wird nicht an
die Runtime oder das gemeinsame Feld zurückgeschrieben.

Als Nächstes werden vorhandene Feld- und Rezeptorursachen einzeln gegen diesen
Vertrag abgegrenzt, bevor irgendeine Materialbewegung als Kandidat gebaut
wird.

Die erste Ursachenabgrenzung ist abgeschlossen. Direkter Rezeptorkontakt,
Eigenaktivierung und eigener schneller Nachhall sind neuronlokal und besitzen
keine Richtungswahl für radiale Oberflächen.

Ihre direkte Verwendung würde eine feste Außen-/Innenbewegung oder isotrope
Expansion ergänzen. Der lokal abgetastete Nachhall gehört nicht zum
bestehenden Kontakt-Drive und bliebe zusätzlich eine feste Leaky-Spur.

Nur der bereits vorhandene signierte lokale Feldfluss ist räumlich gerichtet
und besitzt ein geometrisches Vorzeichen. Er ist noch nicht als
Materialursache ausgewählt, sondern lediglich für die nächste passive
Isolation offen.

Als Nächstes wird kontrafaktisch geprüft, ob seine Nutzung über einen
gewöhnlichen räumlichen Integrator hinausgehen könnte. Es erfolgt keine
Runtime- oder Memory-Freigabe.

Diese kontrafaktische Prüfung ist abgeschlossen. Beide möglichen globalen
Vorzeichenabbildungen des signierten lokalen Feldflusses bestehen den
passiven Flussvertrag und bewegen in der kontrollierten Probe jeweils `0,12`
Materialeinheiten. Sie erzeugen jedoch unterschiedliche Morphologien.

Das Feld bestimmt weder, welches Vorzeichen radial nach außen wirken soll,
noch welche Skala Feldfluss in Materialgeschwindigkeit übersetzt. Eine
Halbierung der eingesetzten Skala halbiert die Materialänderung exakt.

Damit ist kein zusätzlicher Organisationseffekt gezeigt. Die Morphologie
integriert lediglich die eingesetzte Abbildung.

Die Materialdynamik bleibt geschlossen. Vor weiterer Implementierung muss
konzeptionell geklärt werden, welche physische Rolle Kontaktmaterial besitzt
oder ob diese Morphologie überhaupt das geeignete Substrat für organisches
Memory ist.

Der konzeptionelle Substratrollenaudit ist abgeschlossen. Kontaktmaterial als
deformierbare Grenzflächenressource bleibt nur als suspendierte anatomische
Möglichkeit bestehen. Für Bewegung fehlen weiterhin Beanspruchung,
Arbeitsbilanz, konstitutive Kopplung sowie begründete Polarität und Skala.

Kontaktmaterial als gespeicherte strukturelle Energie wird nicht
weiterverfolgt. Ohne eigenständige Energie- und Arbeitsrolle wäre es lediglich
eine umbenannte Leaky-Spur, ein Integrator oder ein adaptives Gewicht.

Die radiale Morphologie bleibt daher passive Anatomie und methodisches Labor.
Sie ist keine freigegebene Memory- oder Organismusmechanik. Die Suche kehrt zum
darstellungsoffenen Memory-Substratvertrag zurück und fragt zuerst nach einer
organismuseigenen Zustandsrolle, die unabhängig von einem gewünschten
Memory-Ergebnis physisch sinnvoll ist.

Der Audit der Organismusgrenze zeigt, dass eine solche Rolle in der heutigen
Runtime nicht vorhanden ist. Aktivierung und schneller Nachhall können
vollständig verloren gehen, ohne die Fähigkeit zur nächsten Feldaufnahme zu
vermindern.

Anatomie, Rezeptordocks, Reaktionsparameter, Zeitkontinuität und Snapshot sind
notwendige technische Bedingungen, aber keine durch Weltteilnahme
beanspruchten oder erneuerten Organismusgrößen. Auch die dokumentierte
Energie- und Ressourcengrenze ist nur ein geschlossener Vertrag.

Das System besitzt damit ein gemeinsames Wahrnehmungsfeld, aber noch keine
eigene Erhaltungsbedingung. Vor einer neuen Mechanik muss darstellungsoffen
geklärt werden, welche konkrete Feldfunktion bei Verlust beeinträchtigt wäre
und wodurch Weltteilnahme sie erhalten oder erneuern könnte.

Der darstellungsoffene Erhaltungsfunktionsvertrag ist nun formuliert. Er
verlangt einen observerunabhängigen Verlust zukünftiger Feldfähigkeit, eine
kausale Veränderung durch reale Teilnahme und eine ebenfalls
teilnahmeabhängige Wiederherstellung im selben gemeinsamen Feld.

Keine vorhandene Rolle erfüllt diese Grenze. Das System besitzt deshalb
weiterhin einen technisch fortsetzbaren Feldprozess, aber keinen
nachgewiesenen Organismusprozess mit eigener Erhaltungsfunktion.

An dieser Stelle gilt eine Stopplinie. Vor einer neuen Mechanik muss
grundsätzlich entschieden werden, ob das gemeinsame Wahrnehmungsfeld allein
weiter untersucht oder zusätzlich eine unabhängig von Memory begründete
Organismuserhaltungsfunktion gesucht werden soll.

Weg B wurde anschließend als reiner Funktionsvergleich geprüft.
Wechselseitige Selbstaufrechterhaltung, Regulation eigener
Existenzbedingungen, eigenständige Weltbeteiligung und Stabilität liefern
wichtige externe Abgrenzungen, aber keine direkt übertragbare digitale
Mechanik.

Im heutigen MCM-System ist keine dieser Funktionen intrinsisch notwendig. Der
Feldprozess erhält seine Anatomie, Docks, Zeitbasis und Sensorquellen nicht
selbst und besitzt keine autonome Weltwirkung. Die simulierte Effektorwelt ist
nur eine passive Forschungsumgebung.

Damit wird Weg B als unmittelbarer Implementierungsweg geschlossen. Das
System bleibt ein gemeinsames Wahrnehmungsfeld mit fortsetzbarer Feldmechanik,
aber ohne begründeten Organismusprozess. Ein späterer Grundlagenzweig müsste
unabhängig untersuchen, ob ein digitaler Prozess die Bedingungen seiner
eigenen Weltteilnahme mit hervorbringen und erhalten kann.

Diese Grenze wurde anschließend präzisiert. Geschlossen ist nur der autonome,
sich selbst erhaltende Organismusprozess als aktueller Kandidat. Ein
weltbezogener MCM-Speicher ist nicht grundsätzlich ausgeschlossen.

Ein separater Sensorik-Handlungs-Konsequenz-Zweig ist konzeptionell geöffnet.
Die vorhandene Simulationswelt kann eine äußerlich ausgelöste Weltveränderung
bereits ursachenneutral als neuen Rezeptorkontakt bis in das MCM-Feld
zurückführen. Das ist noch keine autonome Handlung.

Offen bleibt, ob ein zweiter realer Konsequenzkanal zusammen mit äußerer
Wahrnehmung eine spätere Feldbeziehung kausal mitbegründen kann. Zunächst wird
nur eine anonyme passive Welt-Konsequenz-Familie vorregistriert; Memory,
Reward, Objektlabel, Ressourcen und Effektorwahl bleiben geschlossen.

Die passive Vorregistrierung dieser Testfamilie ist nun abgeschlossen. Sie
führt keine neue Mechanik ein und begrenzt den ersten möglichen Befund auf den
kausalen Transport einer anonymen Weltkonsequenz bis in die aktuelle
MCM-Feldlage.

Konsequenz, Nullkonsequenz, blockierte rezeptorische Rückkehr, gleiche
Weltfolge bei anderer technischer Provenienz und Observerneutralität sind als
Kontrollgruppen festgelegt. Identische aktuelle Eingaben werden von
`activation`, `afterimage` und allen weiteren bekannten Zuständen getrennt
ausgewiesen.

Eine spätere Feldbeziehung darf nur als Kandidat vermerkt werden, wenn nach
natürlicher vollständiger Angleichung der bekannten aktuellen Feldlage eine
identische Holdoutprobe verschieden verarbeitet wird. Kann die Testfamilie
durch aktuellen Kontakt oder schnellen Nachhall vollständig erklärt werden,
endet der Schritt ohne neue Memory-Mechanik.

Als Nächstes wird nur die Darstellbarkeit dieser Gruppen in der vorhandenen
simulierten Welt geprüft. Testcode und Holdoutausführung bleiben bis zu diesem
Audit geschlossen.

Der Darstellbarkeitsaudit ist abgeschlossen. Die Ringwelt kann Konsequenz,
Nullkonsequenz und verschiedene technische Provenienz bei identischer
Weltfolge sauber ausdrücken. Ursache und Provenienz bleiben außerhalb von
Rezeptor und MCM.

Eine blockierte Rückkehr kann dieselbe Ringwelt dagegen nicht als
Weltbedingung darstellen, weil jeder ihrer Zustände zwingend genau einen
aktiven Rezeptorkontakt erzeugt. Die vorhandene Verdeckungswelt besitzt
kontaktfreie visuelle Phasen, aber keinen gemeinsamen Interventions- und
Provenienzvertrag mit der Ringwelt.

Damit sind alle Einzelrollen vorhanden, aber noch nicht als eine kontrollierte
Testfamilie vereinigt. Ein technisches Auslassen des Rezeptors oder ein
Sperrflag im Organismus wäre unzulässig. Der passive Lauf bleibt geschlossen,
bis eine einzige vorhandene Weltgrundlage die sichtbare und die weltseitig
verdeckte Konsequenz unter derselben Dynamik tragen kann.

Die Verdeckungswelt wurde nun als diese einheitliche Grundlage festgelegt.
Ihr konzeptioneller Interventionsvertrag nutzt nur die bereits vorhandenen
äußeren Weltrollen Position, Bewegungsrichtung, Geschwindigkeit und
Verdeckungsmaske.

Eine anonyme Richtungsinversion bildet die Konsequenz; die unveränderte
Richtung bildet die Nullkonsequenz. Beide folgen sichtbar und verdeckt
derselben Weltregel. Innerhalb der Verdeckung verändert sich die Außenwelt,
während ihre reguläre visuelle Projektion kontaktfrei bleibt.

Provenienz und Ereigniskennung bleiben ausschließlich im Observerprotokoll.
Die erneute sichtbare Projektion enthält keine frühere Intervention und kein
Objektlabel. Ihr Unterschied ist zunächst vollständig als Fortsetzung der
äußeren Welt erklärbar und nicht als Memory.

Damit ist als nächster Schritt die passive Methodik für die einheitlichen
Weltzweige freigegeben. Testcode, Holdout-Memory, Feldbeziehungsmechanik und
Rückschreibung bleiben geschlossen.

Die passive Methodik ist jetzt vollständig vorregistriert. Sie definiert V0
und V1 als sichtbares Kausalpaar, H0 und H1 als verdecktes Kausalpaar mit
identischen Budgets und P0 als strenge observerseitige Provenienznull.

Die Weltgeometrie, Interventionszeitpunkte, deterministischen
Rezeptorprojektionen und spiegelbildlichen Holdoutkontakte stehen vor dem Lauf
fest. Spätere Feldantworten dürfen weder Zweige auswählen noch Weltfolgen
verlängern oder verändern.

Künstliches Rauschen, künstliche Varianz, Glättung, Nullpunktanziehung und
Ruhepunktdynamik sind ausgeschlossen. Eine reale Sensorstörung darf erst in
einem späteren Live-Lauf als gemessener Weltkontakt observerseitig
dokumentiert werden.

Damit ist als nächster Schritt nur der minimale passive
Welt-Rezeptor-MCM-Lauf freigegeben. Er kann aktuellen Kausaltransport, aber
weder Memory noch eine fortwirkende Feldbeziehung zeigen.
