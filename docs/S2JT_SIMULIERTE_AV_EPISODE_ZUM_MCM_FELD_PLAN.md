# S2-JT - Simulierte AV-Episode zum MCM-Feld

## Status und Ziel

`S2JT_STATIC_COMPATIBILITY_AND_FUNCTION_PLAN_COMPLETE`

S2-JT bindet einen einzelnen endlichen Funktionspfad:

```text
kanonische simulierte AV-Episode
-> unveraenderte Rezeptoren
-> gemeinsame Zeitordnung
-> aktueller neutraler MCM-Wahrnehmungsfeldpfad
```

Der Plan autorisiert noch keine Implementierung, Tests oder Ausfuehrung.
Quellenadapterforschung fuer Browser, Video, Desktop, Kamera, Mikrofon und
Systemaudio pausiert. Memory, Kontext, PPB-1, TSPM-1 und die bisherige
26-Werte-Memorylinie sind vollstaendig ausgeschlossen.

S2-JT ist eine Wahrnehmungs- und Feldpruefung im Default-Live-Profil. Es ist
keine Memoryskalierung und kein Nachweis einer zweiten realen Quelle.

## Ausgangsstand

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| kanonische Episode und Simulation | `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| S2-JO-Qualifikation | `reports/s2jo/S2JO_SIMULATION_REFERENZ_QUALIFIKATION.md` | `1b7f7f0c18d92bddbc588cd4f87deb02a8191ec719de3ba1177153ba3ec37674` |
| Rezeptorkontaktform | `mcm_field_organism/receptor_contract.py` | `af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71` |
| Zeitsequenzform | `mcm_field_organism/receptor_time_model.py` | `268eaab0505c78f5053aa1f1671ec3a503fa080774a3fb71c4719c2239c596aa` |
| Ereignisordnung | `mcm_field_organism/asynchronous_receptor_events.py` | `e6cac9e72fe8e8b25a32b68bbff69e537f99ac0d51dc87e4a5cabae0dfe2a7a6` |
| Zeitpartition | `mcm_field_organism/field_time_partition.py` | `81affdb99bc1878dc6e1f915e093754106a0013acabc7c8131026a3ef4814706` |
| Handoff | `mcm_field_organism/receptor_proposal_handoff.py` | `ce3cb2c5553d455c52870998ff044b03ff9da5c66b68b2592c394efbb7d8ac0c` |
| AV-Dockgeometrie | `mcm_field_organism/audio_video_field_geometry.py` | `35688f5628c880cd71d1470b42b4cb8d8648484b248478832042ca80f9925244` |
| Feldaufbau | `mcm_field_organism/shared_mcm_field.py` | `1a41ed28f17375b06d7c12b0907c4e696fe25ae9ea26f207c29962829ae720cc` |
| Feldintegration | `mcm_field_organism/neutral_local_field_substrate.py` | `ed559b75e73c4bc40f8706608e8d4e602c4ec2e4466841fbb2f3baac281328cd` |
| direkter asynchroner Lauf | `mcm_field_organism/neutral_asynchronous_field_runtime.py` | `566e65005cc22749e279f5660fe894499d649dc378e877374b5b659047d8991a` |
| bestehender AV-Komfortpfad | `mcm_field_organism/audio_video_neutral_field_runtime.py` | `323a07ade30156c87c798dc211453c74c7c7c15aa2ccf25d783733857a6f3a52` |

Diese Hashes binden den gelesenen Quellstand. Sie sind kein vorweggenommener
Feldbefund.

## Gebundene Episode und Profile

Unveraendert aus S2-JO gelten:

- Episode `s2jn.digital.av.episode.v1`;
- Uhr `s2jn.digital.av.clock` mit `1_000_000_000` Ticks pro Sekunde;
- Dauer `200_000_000` Ticks;
- sechs visuelle `1920 x 1080 RGB8`-Frames bei 30 Hz;
- 20 mono `PCM_F32LE`-Hops mit je 480 Samples bei 48 kHz;
- visuelles Profil `VisualGridConfig(1920, 1080, 12, 8, 30.0)`;
- auditives Profil `LogSpectralConfig(48000, 4800, 480, 50.0, 18000.0, 48)`;
- 288 visuelle und 48 auditive Werte, zusammen 336 Feldkontakte;
- sechs visuelle und elf auditive reduzierte Zustaende, zusammen 17;
- exakt `37_363_200` gestreamte Rohpayloadbytes und hoechstens ein
  kanonisches Payloadobjekt gleichzeitig.

Der auditive Warm-up von zehn Hops ist kein fehlendes Ereignis. Die Hops
`0..8` erzeugen noch keinen vollstaendigen Spektralzustand. Hop `9` erzeugt
den ersten und Hop `19` den elften auditiven Abschluss.

## Notwendige private Zeitbindung

S2-JO liefert bereits reduzierte `VisualReceptorState`- und
`AuditoryReceptorState`-Objekte. Der vorhandene Feldpfad erwartet dagegen
zwei `ReceptorTimeSequence`-Objekte. Die einzige notwendige
Kompatibilitaetsanpassung ist deshalb eine private reine Projektion:

```text
CanonicalReductionResultV1
+ CanonicalAVEpisodeReceiptV1.bindings
-> (auditory ReceptorTimeSequence, visual ReceptorTimeSequence)
```

Sie darf keine Rezeptorfunktion erneut aufrufen und keine Werte veraendern.
Fuer jeden Zustand wird zuerst die vorhandene
`from_auditory_receptor_state`- beziehungsweise
`from_visual_receptor_state`-Projektion verwendet. Deren technische
Quelluhr bleibt im `ReceptorContactFrame` erhalten. Erst die aeussere
`OrganismTimedReceptorFrame.field_time` bindet das zugehoerige S2-JO-Fenster
auf `s2jn.digital.av.clock`.

Die visuelle Zuordnung ist positionsgleich `V_i -> VISUAL_FRAME[i]`. Fuer
den auditiven Zustand `A_j`, `j = 0..10`, gilt zwingend:

```text
ausloesender Hop h = j + 9
state.window_start_sample = j * 480
state.window_end_sample   = (j + 10) * 480
field_time                = AUDIO_HOP[h].window
```

Eine Zuordnung aus Snapshotnamen allein, eine Interpolation, Paarbildung
oder nachtraegliche Zeitrekonstruktion ist unzulaessig. Zustand, ausloesende
Inputbindung, Episodendigest und reduzierter Sequenzdigest muessen
relational uebereinstimmen.

## Vollstaendige gemeinsame Zeitordnung

Die 17 Abschluesse bilden genau 15 geordnete Abschlussgruppen:

| Gruppe | Abschluss-Tick | Ereignisse | kumulierter Support |
| ---: | ---: | --- | ---: |
| 1 | `33_333_333` | `V0` | 1 |
| 2 | `66_666_666` | `V1` | 2 |
| 3 | `100_000_000` | `A0`, `V2` | 4 |
| 4 | `110_000_000` | `A1` | 5 |
| 5 | `120_000_000` | `A2` | 6 |
| 6 | `130_000_000` | `A3` | 7 |
| 7 | `133_333_333` | `V3` | 8 |
| 8 | `140_000_000` | `A4` | 9 |
| 9 | `150_000_000` | `A5` | 10 |
| 10 | `160_000_000` | `A6` | 11 |
| 11 | `166_666_666` | `V4` | 12 |
| 12 | `170_000_000` | `A7` | 13 |
| 13 | `180_000_000` | `A8` | 14 |
| 14 | `190_000_000` | `A9` | 15 |
| 15 | `200_000_000` | `A10`, `V5` | 17 |

Die Gruppen bei `100_000_000` und `200_000_000` sind simultane
audiovisuelle Abschluesse. Innerhalb einer Gruppe gibt es keine erfundene
Reihenfolge. `partition_receptor_completion_time` bildet aus den 15
Abschluss-Ticks genau 15 zusammenhaengende Feldzeitscheiben ueber
`0..200_000_000`.

Jedes Ereignis muss genau einmal im Handoff erscheinen. Ereignisse vor dem
Horizont, nach dem Horizont, doppelte Supports oder widerspruechliche Werte
unter derselben technischen Quelle stoppen fail-closed.

## Feldgeometrie und Parameter

Das gemeinsame Feld wird frisch und ausschliesslich aus der Geometrie der
ersten auditiven und visuellen Kontaktframes aufgebaut. Deren Werte werden
dabei nicht vor ihrem Abschluss in das Feld eingespeist.

Gebunden sind:

- 48 auditive Docks auf Feldzeile `0`, Spalten `0..47`;
- 288 visuelle Docks auf acht Feldzeilen, je 36 Kanalpositionen;
- insgesamt 336 eindeutige Neuronen ohne Dockueberlappung;
- `ORTHOGONAL_FIELD_SAMPLE_OFFSETS`;
- `NeutralLocalFieldSubstrateConfig(1.0)`;
- `NeutralFastAfterimageConfig(0.5)`;
- keine zusaetzliche Dissipation;
- frischer Nullzustand, keine Wiederaufnahme eines frueheren Feldes.

Es werden weder modality-spezifische Feldregeln noch Memory-, Kontext- oder
Semantikrollen eingefuehrt.

## Trajektorienarm und Direktreferenz

Zwei frische Felder erhalten dieselben unveraenderlichen Zeitsequenzen und
dieselben 15 Feldzeitscheiben.

### Trajektorienarm

Ein kleiner privater Beobachtungsadapter verwendet die vorhandenen
Funktionen fuer Handoff, Transient-Dock-Projektion,
Neuroneneingangsprojektion und
`advance_neutral_fast_shared_field_transient`. Er implementiert keine
eigene Feldgleichung. Der bestehende read-only `_state_observer` erfasst an
jedem der 15 Abschluss-Ticks eine Kopie von Aktivierung und Nachhall.

Jeder Trajektorienpunkt enthaelt ausschliesslich:

- Abschluss-Tick und kumulierten Support;
- zugehoerige Snapshot- und Modalitaetsrollen;
- 336 Aktivierungswerte;
- 336 Nachhallwerte;
- Digest des vollstaendigen Punktes.

### Direkter Referenzarm

`run_neutral_asynchronous_field` verarbeitet auf einem zweiten frischen
Feld dieselben Sequenzen und dieselben 15 Schritte ohne Observer. Dieser Arm
ist die unveraenderte bestehende Feldreferenz.

Der letzte Trajektorienpunkt und der finale Zustand des Direktarms muessen
komponentenweise identische Aktivierungs- und Nachhallwerte sowie denselben
kanonischen Zustandsdigest besitzen. Der Trajektorienadapter ist damit nur
eine Beobachtungsgrenze und keine alternative Felddynamik.

## Funktions- und Falsifikationsfragen

Ein spaeterer Lauf beantwortet genau vier Fragen:

1. Werden sechs visuelle und elf auditive Abschluesse ohne Verlust oder
   Doppelzaehlung in eine gemeinsame 15-stufige Zeitordnung uebergeben?
2. Erreichen alle 48 auditiven und 288 visuellen Werte ausschliesslich ihre
   gebundenen Docks?
3. Entsteht aus dem frischen Nullfeld eine endliche, geordnete
   15-Punkte-Trajektorie mit Werten innerhalb `-1..1`?
4. Ist ihr Endzustand exakt gleich dem Ergebnis des vorhandenen direkten
   asynchronen Feldpfads?

`S2JT_AV_FIELD_PATH_CONFIRMED` ist nur zulaessig, wenn alle vier Fragen
positiv beantwortet sind.

Ein vollstaendig gueltiger Lauf falsifiziert die Kompatibilitaet, wenn die
zeitliche Projektion zwar korrekt ist, aber Trajektorien- und Direktarm am
Ende voneinander abweichen. Ein unveraendertes Nullfeld trotz gueltiger
nichtnulliger Kontakte ist ebenfalls eine funktionale Falsifikation.

Quellen-, Form-, Dimensions-, Zeit-, Support-, Dock-, Digest- oder
Aufzeichnungsbruch ergibt dagegen `NOT_EVALUABLE`, nicht einen negativen
Feldbefund.

## Ressourcen- und Operationsplan

Funktionale Maxima:

- 26 kanonische Eingaben;
- 17 reduzierte Rezeptorzustaende;
- 2.256 reduzierte Rezeptorwerte;
- 15 Abschlussgruppen und 15 Feldzeitscheiben;
- zwei frische Felder mit je 336 Neuronen;
- 30 gezaehlte Feld-Batch-Fortschreibungen, je 15 pro Arm;
- 15 Trajektorienpunkte mit je 672 Feldwerten, insgesamt 10.080;
- ein finaler Direktzustand mit 672 Feldwerten;
- maximal 13.008 persistierte numerische Rezeptor- und Feldwerte,
  entsprechend 104.064 Byte als binaere Float64-Nutzwerte;
- maximal `1_048_576` Byte fuer den vollstaendigen kanonischen Ergebnis- und
  Fehlerbeleg ohne Rohpixel oder PCM.

Der funktionale Arbeitszaehler ist auf maximal 140 Einheiten begrenzt:

| Arbeit | Einheiten |
| --- | ---: |
| qualifizierte S2-JO-Reduktion | 55 |
| Zeitprojektion der Zustaende | 17 |
| Abschlussgruppen/Partition | 15 |
| zwei Feldaufbauten | 2 |
| Feld-Batch-Fortschreibungen | 30 |
| Trajektorienmaterialisierung | 15 |
| Validierung, Vergleich und Abschluss | maximal 6 |

Tatsaechliche Laufzeit, Prozessspeicher und temporaere lineare Algebra des
336-Neuronen-Feldes werden separat gemessen. Sie sind keine funktionalen
Erfolgskriterien, muessen aber endlich bleiben und im Befund erscheinen.
Es gibt keinen automatischen Retry.

## Beleg- und Digestfolge

Die spaetere Beweiskette ist vorwaertsgerichtet:

```text
S2JTEpisodePlan
-> S2JO CanonicalAVEpisodeReceiptV1
-> S2JO CanonicalReducedReceptorSequenceReceiptV1
-> S2JTTimedSequenceReceipt
-> S2JTCompletionPartitionReceipt
-> S2JTTrajectoryReceipt[0..14]
-> S2JTDirectFieldReceipt
-> S2JTFieldComparison
-> S2JTResult
```

Rohpixel und PCM bleiben fluechtig. Quellenprovenienz darf die
Rezeptorwerte, Zeitordnung und Felddynamik nicht beeinflussen. Ergebnis- und
Sollwerte duerfen keine frueheren Eingaben oder Feldschritte autorisieren.

Eine unvollstaendige Ergebnisdatei ist `NOT_EVALUABLE`. Eine Wiederholung
bedarf einer neuen ausdruecklichen Freigabe und Lauf-ID.

## Spaeterer enger Implementierungsumfang

Eine spaetere Freigabe sollte auf genau Folgendes begrenzt bleiben:

1. ein privates Modul fuer die reine S2-JO-Zeitprojektion und den
   beobachteten Feldarm;
2. eine fokussierte Testdatei fuer Inventar, Zeitabbildung, Geometrie,
   Handoff, Observer-Read-only-Grenze und exakte Direktarmgleichheit;
3. nach bestandener Qualifikation genau ein 200-ms-Funktionslauf mit
   einfacher atomarer Ergebnisdatei, ohne neue Registry-, Recorder- oder
   Plattformarchitektur.

Der Hauptlauf, Tests und jede Implementierung bleiben bis zu einer neuen
Freigabe gesperrt.

## Verbleibende Entscheidungen

Erst nach einem gueltigen S2-JT-Funktionsbefund wird separat entschieden:

- ob die bestehende Memorylinie kontrolliert auf 336 Werte skaliert wird;
- ob sie vorerst im kleinen 26-Werte-Forschungsprofil verbleibt;
- welche zweite reale AV-Quelle spaeter eine Quellenunabhaengigkeit prueft.

S2-JT nimmt keine dieser Entscheidungen vor. Es prueft ausschliesslich, ob
die bereits qualifizierte Simulation als zeitlich geordnete audiovisuelle
Wahrnehmung in den vorhandenen MCM-Feldpfad eintritt.
