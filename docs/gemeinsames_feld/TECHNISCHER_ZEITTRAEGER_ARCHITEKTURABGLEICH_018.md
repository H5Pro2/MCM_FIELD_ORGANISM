# Technischer Zeitträger-Architekturabgleich 018

## Status

Passiver Architekturvergleich vor `GF_001`.

Nach Audit 017 stehen zwei mögliche Träger für zeitlich mehrere
Rezeptorzustände im Raum:

1. eine zeittragende Rezeptorwahrnehmung innerhalb eines atomaren
   Feldvorschlags,
2. lokale asynchrone Rezeptorwirkung zwischen gemeinsamen Feldfortschritten.

Der Audit implementiert keine dieser Hypothesen. Er prüft nur, was die bereits
vorhandenen Verträge unter dichter und dünner Darstellung desselben
kontrollierten konstanten Kontakts leisten.

## Kontrollierter Verlauf

Beide Zweige besitzen:

- denselben Organismushorizont `0..10`,
- ausschließlich den reduzierten Kontaktwert `0,5`,
- denselben Endpunkt,
- dieselbe Dockgeometrie.

Sie unterscheiden sich nur in der technischen Ereignisdichte:

```text
dicht:  10 abgeschlossene Zustände
dünn:    2 abgeschlossene Zustände
```

Diese Kontrolle behauptet keine rekonstruierte reale Außenweltstütze. Sie
isoliert die Wirkung unterschiedlicher technischer Darstellung im bekannten
Organismuszeitraum.

## Hypothese A: zeittragender Vorschlagsträger

Die verlustfreie Vorschlagsübergabe aus Audit 016 bewahrt beide Folgen
vollständig. Der dichte Träger enthält zehn, der dünne zwei reduzierte Frames.

Positiv:

- keine Lage geht verloren,
- Reihenfolge und Abschlussgruppen bleiben erhalten,
- der vorherige Feldzustand wird nicht verändert,
- keine Endpunktauswahl ist nötig.

Offen:

- die Nutzlastgröße bleibt unmittelbar rezeptorratenabhängig,
- die aktuelle `SharedMCMField`-Schnittstelle weist den Batch ab,
- ohne Zeitwirkungsregel ist nicht bestimmt, ob zehn gleiche Frames anders
  wirken als zwei gleiche Frames.

```text
verlustfreie zeitliche Nutzlast
!= ratenneutrale Feldwirkung
```

## Hypothese B: lokale asynchrone Wirkung

Die aktuelle Runtime besitzt keinen getrennten Einstieg für lokale
Rezeptorwirkung. Der vorhandene serielle Weg verarbeitet deshalb jeden Frame
über einen vollständigen `SharedMCMField.advance`.

| Darstellung | vollständige Feldfortschritte | Endaktivierung B0 |
|---|---:|---:|
| dicht | 10 | 0,5 |
| dünn | 2 | 0,5 |

Die Endaktivierung der zustandslosen Rezeptorprojektion ist gleich. Die Zahl
der vollständigen Feldfortschritte ist es nicht. Jede tickgebundene spätere
Relaxation oder Nachbarschaftswirkung würde dadurch erneut die Rezeptorrate
lesen.

Der `ReceptorDistributor` bleibt dabei anatomisch unverändert und besitzt
keinen lokalen Wirkzustand.

```text
asynchroner Sensorabschluss
-> vorhandener Weg: vollständiger Feldfortschritt
-> weiterhin ratenabhängige Tickzahl
```

## Befund

Keine der beiden Architekturhypothesen ist derzeit als Runtime-Kandidat
getragen:

| Kriterium | zeittragender Träger | lokale asynchrone Wirkung |
|---|---|---|
| vollständige Folge erhalten | ja | nur über Einzelübergaben |
| bestehende Feldschnittstelle | nein | kein eigener Wirkungseinstieg |
| ohne neue Regel ratenneutral | nicht gezeigt | nein |
| neue Zustandsmechanik nötig | für Verarbeitung offen | ja |

Der wichtigste Befund lautet:

> Verlustfreier Transport verpflichtet das Feld nicht dazu, jeden technischen
> Frame als eigenständige Wirkung oder dauerhaftes Erlebnis zu übernehmen.

Eine solche Verpflichtung würde technische Abtastrate mit organischer
Wahrnehmungsintensität verwechseln.

## Stopplinie

`GF_001` bleibt geschlossen. Keine Architekturvariante wird ausgewählt.

Nicht freigegeben sind:

- Sequenzinput in `MCMFieldPerception`,
- lokaler asynchroner Feldzustand,
- ereignisweise Aktivierungs- oder Nachhalländerung,
- Zeitgewichtung, Integration oder Verdichtung,
- ein Feldtakt,
- Memory, Topologie oder Lernen.

## Nächste Untersuchung

Vor weiterer Mechanik muss ein funktionaler Zeitwirkungsvertrag formuliert
werden. Er darf keine Gleichung vorgeben, muss aber mindestens trennen:

```text
gleicher konstanter Kontakt
+ gleiche Organismusdauer
+ unterschiedliche technische Ereignisdichte
-> gleiche Feldkonsequenz
```

von:

```text
unterschiedliche zeitliche Kontaktordnung
+ gleicher Endpunkt
-> darf unterscheidbar bleiben
```

Erst danach kann geprüft werden, ob eine Architektur diese beiden Forderungen
zugleich trägt. Wegen der fehlenden realen Weltstütze visueller Frames muss
diese Prüfung zunächst in einer vollständig kontrollierten synthetischen Welt
bleiben.

Semantik, Reflexion, Offline-Erholung und Selbstregulation bleiben geschlossen.

Der nachfolgende
[Funktionale Zeitwirkungsvertrag 019](FUNKTIONALER_ZEITWIRKUNGSVERTRAG_019.md)
registriert deshalb Darstellungsinvarianz und Ordnungszugänglichkeit getrennt,
ohne eine Feldgleichung oder Architekturvariante auszuwählen.
