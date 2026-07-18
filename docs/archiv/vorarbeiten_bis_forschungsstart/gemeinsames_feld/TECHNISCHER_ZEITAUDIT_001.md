# Technischer Zeitaudit 001

## Status

Technische Voruntersuchung vor `GF_001`.

Dieser Audit ist kein Feldversuch und erzeugt keinen gemeinsamen
Mehr-Takt-Feldzustand. Er prüft ausschließlich, ob einzelne reduzierte
auditive und visuelle Rezeptorzustände auf derselben Organismusuhr eindeutig
einander zugeordnet werden können.

## Fragestellung

Der bisherige reale Audio-Video-Lauf bewies nur:

```text
gesamtes Audioaufnahmefenster
überschneidet
gesamtes Videoaufnahmefenster
```

Offen blieb:

```text
ein einzelner auditiver Rezeptorzustand
<-> ein einzelner visueller Rezeptorzustand
```

## Neue technische Messgrenze

Jeder vollständig reduzierte Rezeptorzustand erhält:

- seine technische Modalitäts- und Geometrieherkunft,
- seine eigene unveränderte Rezeptorzeit,
- Start und Ende seines tatsächlichen Reads auf
  `organism.monotonic_ns`.

Der Audit bildet anschließend nur reale Intervallschnitte.

Er verwendet ausdrücklich keine:

- Mittelung,
- Interpolation,
- Wiederholung eines früheren Zustands,
- Auswahl des nächsten oder ähnlichsten Zustands,
- Sample-and-Hold-Regel,
- semantische oder feldbasierte Zuordnung.

## Synthetische Kontrollen

Geprüft wurden:

1. echte 1:1-Überlappungen,
2. vollständig getrennte Zustände,
3. unterschiedliche Zustandsraten,
4. umgekehrte Eingangsreihenfolge,
5. zeitlich überlappende Zustände desselben Rezeptors,
6. Ausschluss von Rohdaten- und Auswahlrollen.

Die Kontrollen zeigen:

- eindeutige 1:1-Intervalle werden vollständig erkannt,
- nicht überlappende Zustände bleiben ausdrücklich unmatched,
- ein langsamer Zustand gegen mehrere schnelle Zustände wird vollständig als
  mehrdeutig markiert,
- die Deklarationsreihenfolge verändert den Audit nicht,
- innerhalb eines einzelnen Rezeptors sind Überlappung und Zeitrücklauf
  unzulässig.

## Realer Ein-Sekunden-Lauf

Explizite Geräte:

- Kameraeingang `0`,
- Audioeingang `1`.

„Eine Sekunde“ bezeichnet in diesem Audit eine nominale Zustandsanzahl aus den
angeforderten Sensorraten. Es ist kein gemeinsames reales Zeitfenster.

Gemessen wurden:

| Größe | Auditiv | Visuell |
|---|---:|---:|
| vollständige reduzierte Zustände | 91 | 30 |
| tatsächliche Spanne des Zustandszugs | 0,931 s | 5,919 s |
| mediane Read-Dauer | 2,698 ms | 199,770 ms |
| minimale Read-Dauer | 1,638 ms | 103,541 ms |
| maximale Read-Dauer | 31,223 ms | 229,749 ms |

Zeitabgleich:

| Messung | Ergebnis |
|---|---:|
| reale Intervallschnitte | 95 |
| eindeutige 1:1-Überlappungen | 0 |
| an Mehrdeutigkeit beteiligte Zustände | 96 |
| Zustände ohne Überschneidung | 25 |
| Auswahl oder Interpolation angewendet | nein |
| vollständige 1:1-Zuordnung | nein |

Rohbilder und Audiosamples wurden nicht im Ergebnis gehalten.

## Befund

Eine gemeinsame Uhr ist notwendig, aber nicht hinreichend.

Die beiden Rezeptorpfade liefern unter realem Gerätezugriff weder dieselbe
tatsächliche Dauer noch eine eindeutige Zustandsrate. Die gemeldete
Kamerabildrate darf nicht als reale Zustandszeit verwendet werden. Eine
nachträgliche Paarung anhand bloßer Intervallüberschneidung wäre mehrdeutig.

```text
gemeinsame Uhr
≠ gemeinsamer Feldtakt
≠ eindeutige audiovisuelle Gegenwart
```

Der Audit widerlegt nicht die Ein-Feld-Architektur. Er zeigt eine noch
ungelöste technische Synchronisationsgrenze vor dem Feld.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Vor seiner Vorregistrierung muss ein gemeinsamer Feldtaktvertrag festlegen:

1. ein vor dem Read bekanntes gemeinsames reales Zeitfenster,
2. genau eine abgeschlossene technische Rezeptorlage je vorhandenem Dock und
   Feldtakt,
3. explizite Abwesenheit statt Wiederholung eines alten Zustands,
4. keine nachträgliche Auswahl anhand des Ergebnisses,
5. keine Mittelung oder Interpolation außerhalb des jeweiligen
   Rezeptorvertrags,
6. messbare Behandlung eines Reads, der eine Taktgrenze überschreitet.

Erst der Rezeptor darf seine nativen Sensordaten innerhalb eines vorgegebenen
gemeinsamen Fensters technisch reduzieren. Der Feldverteiler darf keine
unterschiedlichen Sensorraten nachträglich fusionieren.

## Nächster technischer Schritt

Vor einem weiteren realen Feldlauf ist ein externer gemeinsamer
Zeitfenstervertrag zu bauen und synthetisch zu falsifizieren. Dabei bleibt
offen, welche Feldtaktbreite beide realen Rezeptoren ohne versteckte
Wiederholung oder Auswahl zuverlässig erfüllen können.
