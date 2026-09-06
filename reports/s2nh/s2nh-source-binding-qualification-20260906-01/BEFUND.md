# S2-NH: neutrale Quellenbindungsqualifikation

Status: `S2NH_SOURCE_BINDING_QUALIFIED`. Genau ein Testaufruf,
**18/18**, Exit-Code `0`, abschliessend `OK`.
Qualifikations-ID: `s2nh-source-binding-qualification-20260906-01`.

Aufrufer aus dem Workspace-Root:

```text
C:/Python314/python.exe -B -m reports.s2nh.qualify_once
```

Dieser Aufrufer startete einmal `unittest` fuer
`tests.test_s2nh_private_source_binding`, keine historischen Tests.
Das Testinventar, Kommando, Interpreter und saemtliche gebundenen Quellhashes
wurden vor dem Aufruf in `preregistration.json` gespeichert. Nachherhashes
sind identisch. Vollstaendiges Protokoll: `stderr.txt`.

Die 18 Gruppen pruefen Quellenidentitaet und unveraenderliche SourceSpec,
ungueltige Quellen, Binary32-Reihenfolge, Seed-/Variantenrelationen,
PCM-Normalformfehler, vollstaendige RGB-Zellgeometrie, Maskengeometrie,
ungueltige Geometrie, literale Ereignisfolge, native Zeitfortschreibung,
Zeitmanipulation, getrennte Planwurzeln, unveraenderliche Bindungspruefung,
Built-in-math, Payloadgroessen/Exaktkopien, Ausgabe-/Schreibgrenzen,
Import-/Gategrenze sowie Profil- und Inventarformen.

Nur ein neutrales PCM-Fenster und zwei nacheinander gehaltene neutrale
Vollformat-RGB-Frames wurden erzeugt. Ihre Seeds lauten ausdruecklich nicht
wie der NH-Korpus. Alle 4800 neutralen PCM-Samples wurden gegen die separat
formulierte struct.pack/unpack-Rechenfolge geprueft. RGB-Zellen und Masken
wurden ohne Rezeptor ausgewertet. Weitere ungueltige neutrale Eingaben
wurden vor der Payloadbildung abgewiesen.

Die realen NH-Rezept-/Ereignismetadaten durften gebunden werden; fuer die
neutralen Planpruefungen wurden synthetische Payloadhashes eingesetzt.
**Keine S2-NH-Payloads, Rezeptorzustaende oder Rezeptorwerte** wurden in
dieser Qualifikation erzeugt oder verwendet. Memory, Feld, Kontext und
Runtime wurden nicht importiert oder aufgerufen. Hauptgate `False`.

Die reine historische `_f32`-Funktion und die qualifizierte
`math_identity`-Pruefung werden wiederverwendet, nicht die historischen
Haupteinstiege. Die neue Seed-/RGB-Bindung bildet die im Plan festgelegte
Generatorform ab; keine Quellensuche oder Regelanpassung.

Ergebnisdigest:
`7dac3dbf7c26c68763005803a1bd56f24fbf9af63f8e7d3b947835ef6d50664f`.

Diese Qualifikation prueft Quellenbindung, nicht Rezeptorkompatibilitaet,
Abrufselektivitaet oder Memoryfunktion. Danach wurde aufgrund der bereits
vorliegenden bedingten Benutzerfreigabe genau eine Vorversiegelung gestartet;
deren separater Befund liegt im Nachbarverzeichnis.
