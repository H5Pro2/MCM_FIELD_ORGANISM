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
Modalitätsfolgen bleiben unsichtbar. Die Projektion ist noch nicht mit
`MCMNeuronDrive` verbunden.

Als Nächstes wird ausschließlich der Neuronenantriebsvertrag erweitert. Die
lokale Folge muss optional und transient bleiben; bestehende Transitionen
müssen ohne sie exakt unverändert arbeiten.

Erst nach dieser Freigabe wird die erste wirkliche Forschungsfrage gewählt.
