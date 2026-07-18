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
| 1. Fortlaufender Audio-Video-Pfad | teilweise; der mehrtaktige Sitzungskern steht, die direkte Brücke aus gemeinsam aufgenommenen Live-Rezeptorfenstern fehlt |
| 2. Herkunft, Geometrie und Zeitlage bis zum Dock | technisch getragen |
| 3. Alle Docks in derselben Neuronenschicht | technisch getragen |
| 4. Atomarer Feldtakt aus abgeschlossenem Vorzustand | technisch getragen |
| 5. Lokale semantikfreie Trägerzustände | technisch getragen |
| 6. Vollständiger Snapshot und unveränderte Wiederherstellung | technisch getragen |
| 7. Observer und Debug ohne Runtime-Rückschreibung | technisch getragen |
| 8. Reflexion und Offline-Erholung inaktiv | technisch getragen |
| 9. Reproduzierbarer Audio-Video-End-to-End-Lauf | teilweise; Ein-Takt-Livepfad und mehrtaktiger Sitzungskern stehen noch getrennt |
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

Als Nächstes wird die vorhandene gemeinsame Audio-Video-Fensteraufnahme mit dem
mehrtaktigen Sitzungskern verbunden. Nur Fenster mit genau einem vollständig
abgeschlossenen reduzierten Zustand je angeschlossener Modalität dürfen einen
Feldtakt bilden.

Die Brücke darf:

- keine Frames auswählen, wenn ein Fenster mehrdeutig ist,
- keine fehlende Modalität halten oder interpolieren,
- keine Rohdaten in das Feld übernehmen,
- keine feste Feldwirkung ergänzen,
- keine Beobachterausgabe zurückschreiben.

Damit wird erstmals derselbe technische Feldzustand über mehrere tatsächlich
gemeinsam aufgenommene Rezeptorfenster fortgesetzt.

Erst nach dieser Freigabe wird die erste wirkliche Forschungsfrage gewählt.
