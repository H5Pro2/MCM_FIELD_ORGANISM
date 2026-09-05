# S2-MI: Bindungsbeobachtbarkeitsaudit

## Status

`S2MI_INVARIANT_EXPERIENCE_BINDING_NOT_OBSERVABLE_WITH_CURRENT_SIGNALS`

S2-MI prueft statisch, welche bereits vor einer Memoryformation verfuegbare,
rollenfreie Evidenz begruenden kann, dass zwei unterschiedliche
Wahrnehmungszustaende zu derselben fortlaufenden Erfahrung gehoeren.

Der Audit fuehrt keine Rezeptor-, Feld-, Memory-, Kontext- oder
Auswertungsfunktion aus. Er implementiert keine neue Zuordnungsregel und
waehlt keine Schwelle. S2-ME bleibt fuer die S2-MG-Variationsklasse
geschlossen. S2-MD bleibt hinsichtlich einer generalisierten,
selbstgelernten Kontextzulassung blockiert. Der extern kalibrierte S2-MC-
Befund bleibt unveraendert gueltig.

Ausgangscommit ist `ae6f03319917339dba4ea473b6cd8ace8b201238`.

## Auditkriterium

Eine vorhandene Evidenz waere nur dann als Erfahrungsbindung zulaessig, wenn
sie gleichzeitig:

1. vor dem betroffenen Memoryentscheid vollstaendig beobachtbar ist;
2. aus funktionaler Sensor-, Rezeptor- oder bereits vorhandener Feldinformation
   stammt;
3. quellenneutral sowie frei von Familie, Ziel, Holdout und Auswertungsrolle
   bleibt;
4. dieselbe fortlaufende Erfahrung von bloss gleicher Uhr, Geometrie oder
   zeitlicher Nachbarschaft unterscheidet;
5. bei wechselnden Wahrnehmungsinhalten ohne versteckte Periodenregel
   funktioniert;
6. nur vorwaertsgerichtete Elternbelege verwendet und weder PPB-Ergebnis noch
   spaetere Evaluation zurueckfuehrt.

Ein Signal, das nur technische Gueltigkeit oder Gleichzeitigkeit belegt,
erfuellt dieses Kriterium nicht.

## Gebundener Quellenstand

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| kanonische AV-Grenze | `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| Rezeptorkontakt | `mcm_field_organism/receptor_contract.py` | `af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71` |
| Rezeptorzeitfolge | `mcm_field_organism/receptor_time_model.py` | `268eaab0505c78f5053aa1f1671ec3a503fa080774a3fb71c4719c2239c596aa` |
| Abschlussgruppen | `mcm_field_organism/asynchronous_receptor_events.py` | `e6cac9e72fe8e8b25a32b68bbff69e537f99ac0d51dc87e4a5cabae0dfe2a7a6` |
| Feldzeit und Feldbeobachtung | `tools/_s2jt_private_timed_field_projection.py` | `91604184325192b6a6291785f713c44fc8fac1d7614234279f635032160c4a4e` |
| neutraler Feldkern | `mcm_field_organism/neutral_local_field_substrate.py` | `ed559b75e73c4bc40f8706608e8d4e602c4ec2e4466841fbb2f3baac281328cd` |
| rollenfreier Stromprozessor | `tools/_s2lm_private_role_free_stream_processor.py` | `84c5650f7f52fe13eb0b8248ab73656dbb67f17fbdd93b2dfc520bacfec7e127` |
| Pose-/Formprojektion | `tools/_s2lv_private_pose_form_projection.py` | `64125b0ff0e469b792c1969f35b9972ca60723fd2503b1194fc703042eba34e4` |
| kontrollierte AV-Welt | `mcm_field_organism/controlled_audio_video_test_world.py` | `af677b52130f355dc24eb6b6ed0bcc9cfc204db94f2f7326ddebf5d6dcb85f5c` |
| Browserquellgenerator | `mcm_field_organism/browser_payload_source.py` | `db4cee84c33e9ccdfc2ddee9a8bbeae5090cccf3370d0db0566af1a8564fa149` |
| vorversiegelter S2-MG-Plan | `tools/_s2mg_private_presealed_applicability_corpus.py` | `3ed54b65d6eea6d72c5b03b883d25c884ff29fa7482c6451aa8d9a491993a639` |
| S2-MG-Materialisierung | `reports/s2mh/s2mh-s2mg-receptor-ppb-materialization-20260905-01/materialization.json` | `b2843606276f0c9eb371ca4efff8a0aa6fb84be3d0158a5df27f7a868c91effd` |

## Konkrete S2-MG-Grenze

Die ersten zehn Formationsevents lauten im Ausfuehrungspfad:

```text
event-001 input-001
event-002 input-007
event-003 input-002
event-004 input-008
event-005 input-003
event-006 input-009
event-007 input-004
event-008 input-010
event-009 input-001
event-010 input-007
```

Alle Ereignisse verwenden dieselbe technische Quelluhr und direkt
aufeinanderfolgende Fenster von je `100.000.000` Ticks. Die Zuordnung von
`input-001..004` beziehungsweise `input-007..010` zu zwei Familien existiert
ausschliesslich in der getrennten Evaluationswurzel. Der Ausfuehrungspfad
bindet ausdruecklich `evaluation_roles_available = False`.

Damit gilt:

- Das zeitlich naechste Ereignis gehoert aus Sicht des spaeteren Auswerters
  jeweils zur anderen Familie.
- Eine Regel "jedes zweite Ereignis" wuerde die verbotene, vorgegebene
  Versuchsanordnung kodieren.
- `input-001` und `input-007` werden spaeter exakt wiederholt. Ihr
  Payloadbeleg kann exakte Wiederholung, aber nicht die Zugehoerigkeit der
  jeweils drei abweichenden Varianten nachweisen.
- Die direkte PPB-Materialisierung erzeugte `17` Slotgenerationen und keine
  Folge `CREATED -> MATCHED -> MATCHED`. Zwei Generationen erreichten nur
  `REPLACED -> MATCHED` mit Support `2`.

Der fehlende Bindungsbeleg liegt deshalb vor der geplanten slotgebundenen
Huelle.

## Signalaudit

| Vorhandenes Signal | Vor Memory beobachtbar | Rollenfrei | Belegt | Belegt nicht | Befund |
| --- | --- | --- | --- | --- | --- |
| Quell-ID und Payloaddigest | ja | technisch ja | exakte Quell- oder Payloadidentitaet | Invarianz zwischen verschiedenen Payloads | nur fuer bitidentische Wiederholung |
| native Quelluhr und Fenster | ja | ja | Reihenfolge, Dauer, Monotonie | gemeinsame Erfahrungsidentitaet | nicht selektiv |
| gemeinsame Feldzeit | ja | ja | zeitliche Gruppierung von Abschluessen | Objekt- oder Erfahrungszugehoerigkeit | nicht selektiv |
| Rezeptorgeometrie und Carrierinventar | ja | ja | technische Vergleichbarkeit | inhaltliche Kontinuitaet | fuer alle S2-MG-Ereignisse gleich |
| 288 Rezeptorwerte und Wahrnehmungsdigest | ja | ja | gegenwaertigen reduzierten Inhalt | invariante Bindung verschiedener Inhalte | rohe L1-Vorzuordnung ist gerade falsifiziert |
| `POSE_V1` | als reine Projektion ja | ja | aktuelle Lage, Ausdehnung und Aktivierung | zeitliche Objektkorrespondenz | moegliche Beobachtung, keine Bindung |
| Formdeskriptor | als reine Projektion ja | ja | posebereinigte aktuelle Struktur | selbstkalibrierte Kontinuitaetsentscheidung | Merkmal vorhanden, Regel fehlt |
| Rezeptor-/Dockabschlussfolge | ja | ja | welche Modalitaet wann abgeschlossen ist | welcher Inhalt fortbesteht | reine Ereignisordnung |
| Feldaktivierung und Nachbild | vorheriger Zustand ja | ja | raeumlich-zeitlichen Feldrest | Objektspur, Quellenkorrespondenz oder Variantenzugehoerigkeit | keine Bindungsautoritaet |
| Generatorbewegung | nur in kontrollierten Quellenrezepten | nein als funktionale Evidenz | vorprogrammierte Quellbewegung | gemessene Bewegung | unzulaessige Metadatenquelle |
| gemessene Sensor- oder Eigenbewegung | nein | nicht anwendbar | nichts | Flow, Odometrie, IMU, Blick- oder Kamerabahn | im relevanten Pfad nicht vorhanden |
| AV-Simultanitaet | allgemein teilweise | ja | gemeinsame Abschlusszeit | gemeinsame verursachende Entitaet | fuer S2-MG zudem nicht vorhanden |

## Einzelbefunde

### Quelle und Zeit

`CanonicalVisualFrameV1`, `CanonicalPCMAudioHopV1` und
`ReceptorContactFrame` binden Quelle, Payload, Geometrie und native Fenster.
Diese Formen beweisen Herkunft und Zeitordnung. Sie enthalten keine
beobachtete Entitaets-, Track- oder Fortsetzungsidentitaet.

`SourceAuditProvenanceV1` enthaelt Adapter- und Quellenklasse. Diese
Provenienz ist bewusst vom funktionalen Wahrnehmungsdigest getrennt und darf
keinen Memoryentscheid beeinflussen. Sie kann daher nicht als Ersatz fuer
Kontinuitaetsevidenz verwendet werden.

Zeitliche Naehe allein ist im S2-MG-Strom widerlegt: unmittelbare Nachbarn
wechseln zwischen den spaeteren Evaluationsfamilien. Groessere Zeitfenster
erhoehen nur die Zahl moeglicher Zuordnungen. Ohne weiteren beobachteten
Bezug entsteht daraus keine eindeutige Bindung.

### Rezeptorgeometrie, Pose und Form

Die konstante `12 x 8 x 3`-Geometrie macht alle 288-Werte-Zustaende
vergleichbar, ist aber fuer alle Inhalte identisch. Sie ist eine
Schnittstelleninvariante, keine Erfahrungsinvariante.

`PoseV1` wird deterministisch aus denselben 288 Werten gebildet und enthaelt
unter anderem Schwerpunkt, Bounding Box, Ausdehnung und gewichtete
Streuung. Es gibt jedoch keinen vorhandenen Trackzustand, keine
Korrespondenz zwischen Supportzellen zweier Zeitpunkte, keine
Okklusionsbehandlung und keine gebundene Bewegungsunsicherheit. Raeumliche
Ueberdeckung kann daher Kompatibilitaet anzeigen, aber weder Fortbestand noch
Identitaet eindeutig belegen.

Der vorhandene Formdeskriptor ist ebenfalls rollenfrei und vor Memory
berechenbar. Eine Distanz-, Radius-, Nearest- oder Clusterregel ueber diese
Deskriptoren waere aber genau eine neue Zuordnungsregel. Die bisherigen
Open-Set-Huellen waren extern kalibriert; S2-ME sollte diese Abhaengigkeit
gerade beseitigen. Der Deskriptor allein schliesst die Bindungsluecke daher
nicht.

Quellenrezepte mit Translation, Formlayout oder Generatorart duerfen fuer
diese Entscheidung nicht gelesen werden. Sie sind keine beobachtete
Rezeptorevidenz.

### Wahrnehmungs- und Feldtrajektorie

`ReceptorTimeSequence`, Abschlussgruppen und `TransientDockTrajectory`
ordnen reduzierte Zustaende verlustfrei nach Zeit und Dock. Der Begriff
"Trajectory" bezeichnet hier die technische Folge von Dockuebergaben, nicht
eine erkannte Objektbahn.

S2-JT kann fuer jeden Feldschritt 336 Aktivierungs- und 336 Nachbildwerte
beobachten. Diese Werte besitzen feste Docks und tragen zeitlichen Rest,
aber keine Objekt-, Quellen- oder Trackidentitaet. Der aktuelle Feldpoststate
ist ausserdem Ergebnis des unabhaengigen Feldgeschwisterzweigs. Ihn zur
Autorisierung derselben Memoryformation zu machen, wuerde die in S2-LL
explizit getrennten Feld- und Memoryzweige erneut koppeln. Der vorherige
Feldzustand ist zulaessig beobachtbar, liefert aber ohne Korrespondenzregel
ebenfalls keine eindeutige Erfahrungsbindung.

### Bewegungs- und Sensorzustand

`ControlledWorldPhase.visual_velocity` sowie `motion_axis` und
`motion_amplitude_fraction` der Browserquelle sind Generatorparameter. Sie
beschreiben vorprogrammierte Welten, nicht eine vom System gemessene
Bewegung. Ihre funktionale Nutzung waere quellenabhaengige Metadatenkopplung.

Im qualifizierten kanonischen Eingangs-, Rezeptor-, Strom- und Feldpfad gibt
es keinen gebundenen optischen Fluss, keine Featurekorrespondenz, keine
Odometrie, keine IMU-, Blick-, Kamera- oder sonstige Eigenbewegungsevidenz.
Somit existiert kein unabhaengiger Bewegungsbeleg, der die S2-MG-Varianten
ueber ihre unterschiedlichen Payloads hinweg verbinden koennte.

## Nichtzirkularitaet

Folgende scheinbare Abkuerzungen sind unzulaessig:

- Familie aus der Evaluationswurzel in den Laufpfad uebernehmen;
- jedes zweite S2-MG-Ereignis gruppieren;
- PPB-Slot, PPB-Distanz oder spaeteren Support als Eltern der vorangehenden
  Erfahrungsbindung verwenden;
- Formdeskriptoren nach dem PPB-Ergebnis passend clustern;
- Generatortranslation oder bekannte Quellbewegung als gemessenen Sensorwert
  ausgeben;
- den aktuellen Feldpoststate zum notwendigen Elternbeleg derselben
  Memoryformation machen;
- exakte Payloadwiederholung auf abweichende Varianten ausdehnen.

Jeder dieser Wege wuerde die gesuchte Bindung aus Versuchswissen,
Memoryergebnis oder Quellmetadaten rekonstruieren.

## Entscheidung

Keine aktuell vorhandene Evidenz erfuellt das Auditkriterium vollstaendig.
Vorhanden sind technische Zeit-, Quellen- und Geometriebindungen sowie
rollenfreie aktuelle Pose-, Form- und Feldwerte. Nicht vorhanden ist eine
beobachtete, selektive Kontinuitaet, die unterschiedliche Wahrnehmungen ohne
Evaluationswissen derselben fortlaufenden Erfahrung zuordnet.

Deshalb wird keine neue Zuordnungsregel implementiert. Der verbindliche
Befund lautet:

> Invariante Erfahrungsbindung benoetigt fuer diese Variationsklasse
> zusaetzliche Wahrnehmungs- oder sensorische Bewegungsevidenz auf der
> Eingangsseite.

Das ist ein neues Forschungsgebiet vor `B_STABLE`, kein Patch an PPB, keine
weitere Memoryebene und keine nachtraegliche Reparatur von S2-ME. Eine
spaetere Untersuchung muesste zunaechst prospektiv messbare Kontinuitaet wie
Pixel-/Merkmalsbewegung, kontrollierte Eigenbewegung oder eine andere
source-neutrale Korrespondenz bereitstellen und unabhaengig qualifizieren.
S2-MI autorisiert keine dieser Moeglichkeiten.

## Auditgrenze

- geaenderte Produktionsmodule: `0`;
- neue Lauf-, Recorder- oder Memorymodule: `0`;
- Rezeptor-, Feld-, Memory- und Kontextaufrufe: `0`;
- Tests und Funktionslaeufe: `0`;
- README-Aenderungen: `0`.

Geprueft wurden ausschliesslich versionierte Quellen, Vertraege und der
unveraenderte S2-MG-Materialisierungsbeleg.
