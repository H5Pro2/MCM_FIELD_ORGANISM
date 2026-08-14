# W1-A: Technischer Bestandsaudit der durchgaengigen Feldwahrnehmung

Stand: 2026-08-07

Entscheidung: `W1A_BROWSER_TO_FIELD_INTEGRATION_GAP_CONFIRMED`

Forschungslauf: nein

## Auftrag

W1-A bildet den vorhandenen technischen Wahrnehmungspfad gegen die aktive
Testweltgrenze ab und bestimmt genau eine reale Integrationsluecke. Der Audit
veraendert keine Runtime, fuehrt keine Testwelt aus und bewertet keine
Memory-, Organisations-, Semantik- oder KI-Faehigkeit.

## Verwendeter Bestand

Der Audit beruht auf folgenden aktiven Modulen und ihren fokussierten Tests:

| Abschnitt | Implementierung | Technische Absicherung |
| --- | --- | --- |
| Audioquelle und Reduktion | `live_audio_adapter.py`, `broadband_hearing_path.py` | `test_finite_audio_adapter.py` |
| Videoquelle und Reduktion | `finite_video_path.py` | `test_finite_video_path.py` |
| gemeinsame Audio-/Video-Uebergabe | `finite_audio_video_field_run.py`, `receptor_time_alignment.py` | `test_finite_audio_video_field_run.py`, `test_receptor_time_alignment.py` |
| kontrollierte AV-Testwelt | `controlled_audio_video_test_world.py` | `test_controlled_audio_video_test_world.py` |
| neutraler S/H-Feldlauf | `audio_video_neutral_field_runtime.py`, `neutral_asynchronous_field_runtime.py` | `test_audio_video_neutral_field_runtime.py`, `test_neutral_asynchronous_field_runtime.py` |
| Verteiler, Docks und gemeinsames Feld | `receptor_distributor.py`, `shared_mcm_field.py` | `test_receptor_distributor_and_shared_field.py` |
| allgemeine Browserwelt | `browser_world_contract.py`, `tools/controlled_browser_world/server.py` | `test_browser_world_contract.py`, `test_controlled_browser_world_assets.py`, `test_controlled_browser_world_server.py` |
| bisheriger Browser-Rezeptoradapter | `z4a_browser_receptor_adapter.py` | `test_z4a_browser_receptor_adapter.py` |

## Bestandskarte

### Audio und Video

Der allgemeine Audio-/Videopfad ist technisch durchgaengig:

```text
endliche kontrollierte Audio- und Videoquelle
-> modalitaetseigene Reduktion
-> ReceptorContactFrame
-> ReceptorTimeSequence auf gemeinsamer Uhr
-> ReceptorDistributor
-> offene auditive und visuelle Docks
-> gemeinsames lokales S/H-Feld
-> passive Observer und serialisierbarer Snapshot
```

Die Rezeptorvertraege erhalten Modalitaet, Geometrie, Traegeridentitaeten und
Zeitfenster. Der Verteiler uebergibt reduzierte Werte ohne semantische Fusion.
`SharedMCMField.snapshot()` und `restore_shared_mcm_field()` decken die
technische Wiederaufnahme ab. Observer lesen technische Verlaeufe, schreiben
aber keine Bedeutung oder Ziele in das Feld zurueck.

### Browserwelt

Fuer kontrollierte Browserwelten bestehen ein allgemeiner Weltvertrag,
reproduzierbare Assets und ein lokaler Server. Diese Schicht beschreibt und
liefert die Testwelt, erzeugt aber noch keine allgemeine
`ReceptorTimeSequence` fuer den aktiven W1-Feldpfad.

Der vorhandene direkte Browser-Rezeptoradapter kann PNG- und PCM-Nutzlasten
reduzieren und liefert technisch passende auditive und visuelle
`ReceptorTimeSequence`-Objekte. Er ist jedoch in Namen, Vertrag, festen
Inventaren, Uhr-ID und Assets an den geparkten Z4-A2-Zweig gebunden. Seine
Existenz schliesst daher nicht die aktive W1-Luecke und er darf nicht als
verdeckte Reaktivierung von Z4-A verwendet werden.

## Genau eine Integrationsluecke

```text
Es fehlt eine allgemeine, nicht an Z4 gebundene Browserausgabe-zu-
Rezeptorsequenz-Bruecke, welche kontrollierte Bild- und Audionutzlasten
unmittelbar reduziert und an den bestehenden neutralen S/H-Feldpfad uebergibt.
```

Diese Luecke liegt vor Distributor, Docks und gemeinsamem Feld. Dort ist kein
zweiter Feldmechanismus erforderlich. Ebenso fehlt kein neues Memory-Substrat:
W1-A betrifft ausschliesslich die technische Eingangsverbindung.

## Grenzen fuer die Schliessung

Eine spaetere W1-B-Implementierung muss:

- ausschliesslich kontrollierte Browserausgaben verarbeiten;
- Bild- und Audionutzlasten nach der Rezeptorreduktion verwerfen;
- die vorhandenen allgemeinen Rezeptor-, Zeit- und Feldvertraege verwenden;
- Modalitaet, Geometrie, Reihenfolge und gemeinsame Uhr explizit erhalten;
- ohne Labels, Reward, Zielverhalten, trainierten Readout oder Rueckschreibung
  arbeiten;
- Z4-Bezeichner, Z4-Assets, P0/F3/B3, Lauf 197 und Z4-Runner nicht importieren;
- keine Kamera, kein Live-Mikrofon und keine physische Sensorik einfuehren;
- nur technische Aussagen zu Durchgaengigkeit, Determinismus und
  Zustandsgrenzen erlauben.

## Nichtbefunde

W1-A weist keine Feldwahrnehmung im psychologischen Sinn, kein Lernen, keine
Praegung, kein Memory, keine Feldzeit, keinen inneren Kontext, keine
Organisation und keine feldbasierte KI nach. Der Audit bestaetigt nur den
technischen Bauzustand und lokalisiert eine Schnittstellenluecke.

## Technische Verifikation

Die fokussierte Testsuite der oben inventarisierten Audio-, Video-, AV-,
Zeit-, Feld-, Snapshot-, Observer- und Browservertraege bestand mit
`108 passed` und 9 Subtests. Die Pytest-Cachewarnung `WinError 183` betrifft
nur den bereits vorhandenen lokalen Cachepfad und keinen getesteten Vertrag.
Es wurde keine Browserwelt und kein Forschungslauf ausgefuehrt.

## W1-A-Entscheidung

```text
allgemeiner Audiopfad bis S/H-Feld:       vorhanden
allgemeiner Videopfad bis S/H-Feld:       vorhanden
kontrollierter AV-Testweltpfad:           vorhanden
Verteiler und offene Docks:               vorhanden
Snapshot und Wiederaufnahme:              vorhanden
passive technische Observer:              vorhanden
allgemeiner Browserweltvertrag:           vorhanden
allgemeiner Browser-Rezeptor-Feldpfad:     fehlt
Z4-A als Ersatz verwenden:                 nein
neue Feld- oder Substratmechanik noetig:   nein
Forschungslauf:                            nein
```

## Bester naechster Schritt

W1-B als kleinen technischen Schnittstellenvertrag fuer eine generische
Browserausgabe-zu-Rezeptorsequenz-Bruecke festlegen. Erst danach wird genau
diese Bruecke implementiert und mit synthetischen PNG-/PCM-Nutzlasten gegen
den bestehenden neutralen S/H-Feldpfad getestet. Keine Browserausfuehrung und
keine Wiederaufnahme von Z4-A oder Lauf 197.
