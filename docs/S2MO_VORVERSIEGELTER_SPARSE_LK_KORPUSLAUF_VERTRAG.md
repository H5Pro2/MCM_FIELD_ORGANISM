# S2-MO: Vorversiegelter Sparse-LK-Korpuslauf

## Zweck und Grenze

S2-MO prueft erstmals die unter S2-MN technisch qualifizierte sparse
Lucas-Kanade-Korrespondenz an den acht bereits vor Sparse-LK versiegelten
S2-MJ-Framepaaren. Es wird kein neuer oder angepasster Korpus erzeugt.

Die Ausgabe bleibt gemessene Bewegungskorrespondenz. Sie behauptet keine
Objektidentitaet und beeinflusst weder Memory, Kontext noch Feld.

## Unveraenderte Vorbindung

| Rolle | Digest oder SHA-256 |
| --- | --- |
| Source-Plan-Digest | `5a77dab593e7168afc210ccb7eccc4e7c50d3237868385e6d90dda68fa22849c` |
| `source-plan.json` | `e39fabcd207b45812cac80d9228d45e14740eba8e5329dfe92784e4c14f34b5d` |
| Execution-Plan-Digest | `561ae5179be4be724356588a5891e1748493b78df141a8a9914917743f61cd69` |
| `execution-plan.json` | `eb459bd1ade3b3f7eddd46d28b5354f1ddc5de624de760a608ead03ecace7780` |
| Evaluation-Plan-Digest | `412d128841b87d583e8fb22e35d28e21dcbf195d8c6f06b2b2f31aba181a44db` |
| `evaluation-plan.json` | `73ff71915293587113a3ddfac28a7c1dfdbb0453ba05f371cb91f353e90b85fc` |
| Preseal-Receipt-Digest | `d4f614aef4240babaaa7b1659cc60696f835ad9edb151b225023bc33fdc8fad5` |
| `preseal-receipt.json` | `7fafdc7e4d092add3dd78bd2015682e9094f4ba5aa2555ef2fec3bb986548034` |
| versiegelter Generator | `f55a2b1a1d920caec59941419b95fc21aa6bcb70fc8f06152df20bac9c9113a9` |
| qualifizierte S2-MN-Messquelle | `5bdde67336196ccc5abad85a503289339957122f8c9a81e35a3697db20dd2b88` |
| S2-MN-Capability-Digest | `2b6092b0d8b4165de60931d3e82747ef014085f6c1c5ee6120425f8b87fc6500` |

Alle 16 RGB8-Payloaddigests, Framebindungen, Quelluhren, Zeitfenster und
Paarbindungen werden literal aus diesen versiegelten Dateien uebernommen.
Vor jeder Messung wird der betreffende Frame genau einmal aus seinem
versiegelten Rezept materialisiert und sein Byte-Digest geprueft. Es gibt
keine Quellenersetzung, Parametersuche oder erneute Versiegelung.

## Ausfuehrung

Der einzige autorisierte Lauf ist
`s2mo-presealed-sparse-motion-corpus-20260905-01`.

Fuer jedes der acht neutralen Paare gilt:

1. beide Frame-, Payload-, Quellen- und Zeitbindungen validieren;
2. beide RGB8-Frames materialisieren und gegen die vorversiegelten
   Payloaddigests pruefen;
3. die unveraenderte ganzzahlige RGB-zu-Y-Projektion bilden;
4. genau einen Vorwaerts- und einen Rueckwaerts-LK-Aufruf mit der unter
   S2-MN qualifizierten Parameterbindung ausfuehren;
5. beide vollstaendigen Statusmasken binden;
6. gueltige Gitterindizes streng nach ihrem urspruenglichen Index ordnen;
7. Punkte, Fehler, Verschiebung, Zyklus- und RGB-Residuen ausschliesslich
   fuer diese gueltigen Indizes digestieren und zusammenfassen;
8. alle Rohframes und Arbeitsarrays vor dem naechsten Paar verwerfen.

Es gibt keine Reproduzierbarkeitswiederholung je Paar. Weniger als `1.152`
gemeinsam gueltige Tracks bei irgendeinem Paar ergibt fuer den gesamten
Lauf `NOT_EVALUABLE`.

Die LK-Bindung bleibt unveraendert: Punktgitter `12 x 8 x 4 x 4`, Fenster
`21 x 21`, Ebenen `0...3`, maximal `30` Iterationen, Epsilon `0,01`, Flags
`0`, `minEigThreshold=0,0001`, ein OpenCV-Thread und OpenCL aus. Es gibt
keine numerische Matchschwelle.

## Ausfuehrungs- und Evaluationswurzel

Der Lauf liest waehrend der acht Messungen ausschliesslich Source- und
Execution-Plan. Paarrollen und Sollrelationen sind dort nicht vorhanden.

Erst nachdem die vollstaendige neutrale Ausfuehrungsevidenz atomar
publiziert wurde, darf die bereits versiegelte Evaluationswurzel gelesen und
ueber einen neuen Run-Binding-Digest gebunden werden. Die Auswertung kann
keine Messung wiederholen oder veraendern.

## Ordinale Auswertung

Die zwei unveraenderten Vergleichsgruppen lauten:

| Gruppe | Fortsetzung | Formwechsel | Verdeckung | Szenensprung |
| --- | --- | --- | --- | --- |
| `comparison-group-01` | `pair-001` | `pair-003` | `pair-005` | `pair-007` |
| `comparison-group-02` | `pair-002` | `pair-004` | `pair-006` | `pair-008` |

Pro Gruppe werden genau die vier vorversiegelten Regeln ausgewertet:

1. Der Mittelwert des Zyklusresiduums der Fortsetzung ist kleiner als bei
   Formwechsel und Szenensprung.
2. Der Mittelwert des bewegungskompensierten RGB-Residuums der Fortsetzung
   ist kleiner als bei Formwechsel und Szenensprung.
3. Das p95-RGB-Residuum der Teilverdeckung ist groesser als bei der
   unbedeckten Fortsetzung.
4. Der Szenensprung ist nicht gleichzeitig beim mittleren Zyklus- und
   RGB-Residuum gleich gut oder besser als die Fortsetzung.

Es entstehen acht vorgebundene Boolesche Einzelbefunde. Es wird keine
Schwelle aus den Ergebnissen gewaehlt.

- `8/8`: `S2MO_MOTION_CORRESPONDENCE_OBSERVABLE`;
- `1...7/8`: `S2MO_MOTION_CORRESPONDENCE_MIXED`;
- `0/8`: `S2MO_MOTION_CORRESPONDENCE_NOT_SEPARABLE`.

Jeder dieser drei Werte ist ein regulaerer fachlicher Befund bei technisch
vollstaendiger Aufzeichnung. Quellen-, Digest-, Zeit-, Form-, Runtime-,
Track- oder Artefaktfehler ergeben ausschliesslich `NOT_EVALUABLE`.

## Ressourcen und Belege

Es duerfen hoechstens zwei Vollformat-RGB8-Frames eines Paars resident sein.
Die Prozessmessung muss unter `134.217.728` Byte zusaetzlichem Working Set
bleiben. Keine Rohframes, Graubilder, Punktarrays oder Fehlerarrays werden
persistiert.

Persistiert werden nur:

- eine neutrale Ausfuehrungsevidenz mit acht Paarbelegen;
- eine nachgelagerte Evaluationsbindung samt acht Regelbefunden;
- ein exklusiver Terminalbeleg.

Jede Datei bleibt unter `1.048.576` Byte. Der Lauf ist einmalig, nicht
ueberschreibbar und nicht fortsetzbar. Das Hauptgate ist vor und nach dem
Aufruf `False`.

## Ausschluesse

- neuer oder veraenderter Korpus;
- zweite Messung oder Retry;
- Matchschwelle, Toleranz oder Rundung;
- Auswertung ungueltiger Trackwerte;
- Rezeptor-, Memory-, Kontext- oder Feldaufruf;
- Nutzung von Fallrollen vor abgeschlossener Ausfuehrungsevidenz;
- Objektidentitaets- oder Erfahrungsbindungsclaim.
