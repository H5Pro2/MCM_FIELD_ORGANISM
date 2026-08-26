# Lauf 173: Physischer Prozesspfad - technische Vorabnahme

## Forschungsfrage und Auftrag

Geprueft wurde, ob der vorhandene physische Feld-Welt-Feld-Aufbauvertrag und
die in Lauf 172 stabilisierte Prozessruntime technisch so vorbereitet sind,
dass ein spaeterer manueller Aufbau und vier getrennte Kausalkontrollarme
ausgefuehrt werden koennen.

Freigegeben war nur eine technische Vorabnahme. Eine Kameraoeffnung,
Effektorpraesentation, menschliche Aufbauentscheidung oder Kausalpruefung war
nicht Bestandteil dieses Laufs.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- der aktuelle freigegebene Uebergabeeingang
- `AGENTS.md`
- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/forschung/047_REALE_PHYSISCHE_AUFBAUABNAHME_LAUF_125.md`
- `docs/forschung/052_REALE_AUFBAUABNAHME_NO_DECISION_LAUF_152.md`
- `docs/forschung/070_PROZESS_ENTKOPPELTE_120S_LANGZEITSTABILITAET_LAUF_172.md`
- `docs/architektur/104_TECHNISCHER_VERTRAG_VISUELLE_MCM_EFFEKTORFLAECHE.md`
- `docs/architektur/105_KAUSALVERTRAG_GETRENNTE_VISUELLE_WELTWIRKUNG.md`
- bestehende Effektor-, Zielpraesentations-, Kamera- und Prozessrunner
- zugehoerige fokussierte Tests

Externe Quellen und projektweite Wissensdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu erstellt wurden:

- `tools/run_physical_process_preflight.py`
- `tests/test_physical_process_preflight_tool.py`
- dieser Bericht

Geprueft wurden:

- `OpenCVVideoFrameSource`
- `run_physical_setup_acceptance.run_preview`
- `project_visual_mcm_effector_surface`
- `prepare_independent_visual_target_plan`
- `run_live_process_decoupling_probe.run_process_decoupled`

Das bestehende feldfreie menschliche Rohkamera-Abnahmewerkzeug wurde nicht
veraendert. Insbesondere wurde keine Rezeptor- oder Feldlogik in seine
manuelle Sichtpruefung eingebaut.

## Durchgefuehrte Schritte

1. Physischer Aufbau- und Kausalvertrag gegen den aktuellen Codebestand
   geprueft.
2. Effektorprojektion, getrennte Zielpraesentation, Rohkamera-Abnahme und
   Prozessruntime als getrennte Komponenten verifiziert.
3. Vier Kontrollarme ohne erwartetes Ergebnis maschinenlesbar
   vorregistriert.
4. Physische und technische Freigaben als getrennte Aussagen modelliert.
5. Das Vorabnahmewerkzeug ausgefuehrt.
6. Effektor-, Presenter-, Kamera-, Prozess- und Architekturtests ausgefuehrt.

## Messergebnisse und Gegenbaselines

```text
Physischer Aufbauvertrag vorhanden:          ja
Kausalvertrag vorhanden:                     ja
Menschliches Rohkamera-Werkzeug vorhanden:   ja
Getrennter Zielpresenter vorhanden:           ja
Prozessruntime vorhanden:                    ja
120-Sekunden-Runtimeevidenz vorhanden:        ja

Komponenten-Vorabnahme bereit:               ja
Physischer Aufbau beobachtet:                nein
Kamera schliesst Effektor aus bestaetigt:    nein
Passive Zielflaechen bestaetigt:             nein
Optische Trennung bestaetigt:                nein
Geschlossener Ablaufkoordinator vorhanden:        nein
Kausallauf freigegeben:                      nein
```

Vorregistrierte Arme:

```text
ORIGINAL_EFFECT       nichtneutraler Snapshot, offener Lichtweg, Rueckkehr an
BLOCKED_LIGHT_PATH    gleicher Snapshot, physisch blockierter Lichtweg
NEUTRAL_OUTPUT        neutraler Snapshot, offener Lichtweg
INTERRUPTED_RETURN    gleicher Snapshot, Rueckkehr im Testfenster unterbrochen
```

Keiner der Arme enthaelt ein erwartetes Resultat, Reward, adaptive Wartezeit
oder aus Kamerapixeln gesteuerte Ausgabe.

```text
Kamera geoeffnet:              nein
Effektor praesentiert:         nein
Rezeptorzustand erzeugt:       nein
Feld fortgesetzt:              nein
Bildanalyse ausgefuehrt:       nein
Bilddatei geschrieben:         nein
Rohsensorpayload behalten:     nein
Tests: 27 bestanden, 6 Subtests bestanden
```

## Einordnung

**Beobachtet:** Alle benoetigten Einzelkomponenten und Vertragsdateien sind
vorhanden und aufrufbar. Die vier Kontrollarme sind eindeutig beschrieben.
Keine physische Aufbaubedingung wurde beobachtet oder bestaetigt.

**Technische Interpretation:** Der digitale Bestand reicht fuer die manuelle
Aufbauabnahme und die Vorbereitung der Kontrollarme. Der Prozessrunner gibt
derzeit jedoch keinen abgeschlossenen Feldsnapshot an einen physischen
Effektor-Ablaufkoordinator weiter; ein geschlossener Lauf ist deshalb noch nicht
implementiert und bleibt zusaetzlich von menschlicher Aufbauannahme abhaengig.

**Hypothese:** Nach bestandener manueller Sichtpruefung kann ein eng begrenzter
Ablaufkoordinator die vorhandenen Komponenten verbinden, ohne Feld- oder
Rezeptormechanik zu aendern. Das wurde in Lauf 173 nicht implementiert.

**Offene Frage:** Ist der reale optische Aufbau so hergestellt, dass die
Kamera ausschliesslich die passiven Zielflaechen und weder Effektor,
Kanaloeffnung noch Reflexion sieht?

## Grenzen und nicht gepruefte Annahmen

Software kann Abschirmung, Mattheit, Reflexionsfreiheit und Kamerasicht nicht
aus dem Workspace bestaetigen. Eine automatische Bildanalyse waere kein
zulaessiger Ersatz fuer die menschliche Rohbildentscheidung.

Fruehere `NO_DECISION`-Abnahmen gelten nicht als Annahme oder Ablehnung. Es
wurde keine Feld-Welt-Feld-Wirkung, Kausalitaet, Organisation oder Memory
beobachtet. Eine Zielabweichung liegt nicht vor.

## Konkrete Schlussfolgerung

Die technische Vorabnahme der Einzelkomponenten ist bestanden. Der reale
Kausallauf bleibt aus zwei unabhaengigen Gruenden gesperrt:

1. Der physische Aufbau wurde nicht menschlich mit `HUMAN_ACCEPTED` bestaetigt.
2. Ein begrenzter Ablaufkoordinator fuer Snapshot, Effektor, feste Wartezeit,
   Kameraaufnahme und Prozessrueckkehr ist noch nicht vorhanden.

Diese Grenzen duerfen weder durch synthetische Frames noch durch eine
automatische Aufbauentscheidung umgangen werden.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Lauf 174 muss ausschliesslich die einmalige menschliche Rohkamera-Abnahme des
fertig aufgebauten optischen Pfads ausfuehren. Das ist eine notwendige
physische Handlung und kann nicht durch einen Agenten ersetzt werden.

Exakter Aufruf:

```powershell
.\.venv\Scripts\python.exe tools\run_physical_setup_acceptance.py --camera-device 0
```

Im fokussierten Vorschaufenster ist nur `A` bei vollstaendiger Erfuellung
aller zehn Punkte oder `R`/`Esc` bei Ablehnung zulaessig. `NO_DECISION` gibt
keinen weiteren Versuch oder Kausallauf frei. Erst `HUMAN_ACCEPTED` darf die
enge Implementierung des fehlenden Kontrollarm-Ablaufkoordinators begruenden.
