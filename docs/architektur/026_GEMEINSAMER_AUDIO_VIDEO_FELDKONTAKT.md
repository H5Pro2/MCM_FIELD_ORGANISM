# Gemeinsamer Audio-Video-Feldkontakt

## Zweck

Der endliche Audio-Video-Lauf prüft erstmals den vollständigen technischen
Weltkontakt zweier realer Sinnespfade bis in dasselbe MCM-Feld:

```text
Mikrofon -> auditive Rezeptoren --\
                                   -> Rezeptorenverteiler -> offene Docks
Kamera   -> visuelle Rezeptoren --/                         |
                                                             v
                                                eine MCM-Neuronenschicht
                                                             |
                                                             v
                                                  ein Feldzustand
```

Der Lauf ist eine Integrationsprüfung der aktuellen Architektur. Er ist keine
Lern-, Beziehungs- oder Semantikprüfung.

## Zustandsgrenze

Audio- und Videorohdaten bleiben innerhalb ihrer technischen Adapter. In den
gemeinsamen Pfad gelangen nur abgeschlossene reduzierte Rezeptorzustände:

- auditive Energieverteilung auf logarithmischen Frequenzträgern,
- lokale visuelle Kanalwerte auf der Rezeptorfläche,
- technische Herkunft und Geometrie,
- die gemessenen technischen Read-Intervalle auf derselben Organismusuhr.

Weder Bilder noch Audiosamples werden im Ergebnis oder im MCM-Feld gespeichert.
Eine Überlappung der Read-Intervalle belegt keine gleichzeitige
Außenweltstütze.

## Gemeinsame Feldgeometrie

Die auditiven und visuellen Docks belegen unterschiedliche Positionen derselben
zweidimensionalen Feldgeometrie. An der gemeinsamen Dockgrenze können Neuronen
lokale Feldproben aus dem jeweils anderen Rezeptorbereich wahrnehmen.

Diese Nachbarschaft ist eine transparente räumliche Ausgangsbedingung. Sie ist
noch keine entwickelte Beziehung. Der Lauf verwendet ausschließlich die
zustandslose Rezeptorprojektion und erzeugt genau einen Feldtakt.

## Technischer Lauf

Das Werkzeug verlangt explizite Geräte und wählt keine Hardware selbst:

```powershell
python tools/run_live_audio_video_field.py `
  --camera-device 0 `
  --audio-device 1 `
  --duration-seconds 1
```

Ausgegeben werden nur technische Summen, Zeitüberlappung und der Digest des
Feldzustands.

## Geprüfter Stand vom 18. Juli 2026

Ein realer Ein-Sekunden-Lauf ergab:

- 30 vollständige visuelle Rezeptorzustände,
- 91 vollständige auditive Rezeptorzustände nach der Anlaufphase,
- etwa 1,05 Sekunden Überlappung der technischen Read-Intervalle,
- keine Audioüberläufe,
- 336 Rezeptorträger in einem gemeinsamen Feldzustand,
- keine gespeicherten Rohdaten.

Der Lauf zeigt damit den gemeinsamen technischen Eingangspfad: abgeschlossene
auditive und visuelle Rezeptorzustände aus überlappenden Aufnahmefenstern
werden über getrennte Docks in dieselbe MCM-Neuronenschicht übergeben. Im
gemeinsamen Feldzustand liegen dabei nur reduzierte Rezeptorzustände und
technische Metadaten; Bild- und Audiorohdaten bleiben außerhalb des Feldes.

Nicht gezeigt sind:

- exakt zeitgestempelte Paarung einzelner Audio- und Videozustände,
- entwickelte Feldtopologie,
- dauerhafte oder lösbare Beziehungen,
- hypothetische MCM-Memory,
- semantische Resonanz,
- Reflexion,
- Offline-Erholung,
- eine später möglicherweise als Feldintelligenz interpretierbare offene
  Feldfähigkeit.

Der spätere
[Technische Zeitaudit 001](../archiv/vorarbeiten_bis_forschungsstart/gemeinsames_feld/TECHNISCHER_ZEITAUDIT_001.md)
misst inzwischen jeden reduzierten Zustand auf derselben Organismusuhr. Er
zeigt jedoch null eindeutige 1:1-Paare und hält diese Grenze daher weiterhin
offen.

## Nächste Grenze

Die nachfolgenden technischen Audits 002 bis 009 zeigen: Native
Rezeptorzustände können kausal an derselben Organismusuhr übergeben werden,
ohne äußere Gleichzeitigkeit zu behaupten. Offen bleibt eine
rateninvariante kontinuierliche Feldzeit, die Übergabeereignis und
vollständigen MCM-Feldschritt nicht gleichsetzt.
