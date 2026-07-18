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
- das gemessene Überlappungsfenster beider Aufnahmen.

Weder Bilder noch Audiosamples werden im Ergebnis oder im MCM-Feld gespeichert.

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
- etwa 1,05 Sekunden gemessene zeitliche Überlappung,
- keine Audioüberläufe,
- 336 Rezeptorträger in einem gemeinsamen Feldzustand,
- keine gespeicherten Rohdaten.

Damit ist der gemeinsame technische Eingangspfad für letzte vollständige
Rezeptorzustände aus überlappenden Aufnahmefenstern getragen.

Nicht gezeigt sind:

- exakt zeitgestempelte Paarung einzelner Audio- und Videozustände,
- entwickelte Feldtopologie,
- dauerhafte oder lösbare Beziehungen,
- organisches Memory,
- semantische Resonanz,
- Reflexion,
- Offline-Erholung,
- Feldintelligenz.

Der spätere
[Technische Zeitaudit 001](../gemeinsames_feld/TECHNISCHER_ZEITAUDIT_001.md)
misst inzwischen jeden reduzierten Zustand auf derselben Organismusuhr. Er
zeigt jedoch null eindeutige 1:1-Paare und hält diese Grenze daher weiterhin
offen.

## Nächste Grenze

Der nächste Versuch darf keine neue Lernregel einführen. Zuerst ist über mehrere
aufeinanderfolgende gemeinsame Feldtakte zu prüfen, ob die vorhandene lokale
Feldwahrnehmung auditiv-visuelle Gegenwart kausal trägt oder nur zwei
gleichzeitige Rezeptorprojektionen nebeneinander abbildet.
