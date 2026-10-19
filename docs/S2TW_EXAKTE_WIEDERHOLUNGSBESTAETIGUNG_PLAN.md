# S2-TW: Exakte Wiederholungsbestätigung abgeschlossener Spuren

Status: statischer Plan. Keine Quellenproduktion, Implementierung,
Qualifikation oder Ausführung ist freigegeben.

## Frage und Grenze

S2-TW prüft nur, ob eine später **vollständig wahrgenommene und exakt gleiche**
Vierframefolge eine eindeutig vorhandene S2-TU-Spur bestätigt, anstatt einen
zweiten FIFO-Platz zu belegen. Dies ist keine Mittelung, Variantenbindung,
semantische Verdichtung oder Priorisierung. Es bleibt insbesondere offen, ob
eine nicht identische Wahrnehmung zu derselben Quelle oder zu einem selben
Inhalt gehört.

Die Gleichheit wird erst nach Aufnahme des vierten Frames einer Formation
geprüft. Verglichen werden in aufsteigender Positionsfolge die vier
gespeicherten 48-Wert-Halbprofilvektoren. Quellen-ID, Rezept, Rollenname,
Hinweis und Teilabschnitt gehören nicht zur Gleichheitsentscheidung. Ein
gemeinsames Paar oder ein gemeinsamer Inhalt genügt nicht.

## Zwei gebundene Vergleichsarme

Beide Arme erhalten denselben einmal materialisierten Wahrnehmungsstrom und
besitzen je eine getrennte `RetainedTraceStore`-Instanz mit Kapazität `2`:

| Arm | Abschluss einer vollständigen Formation |
| --- | --- |
| `S2TU_UNVERAENDERT` | Jede vollständige Spur wird unverändert übernommen; die dritte Übernahme verdrängt FIFO die älteste Generation. |
| `S2TW_EXACT_CONFIRM` | Vor der Übernahme werden alle gehaltenen Spuren auf die vier geordneten Werte geprüft. Bei genau einer vollständigen Gleichheit entsteht `TRACE_CONFIRMED`: kein neuer Speicherplatz, keine neue Generation und keine Änderung der FIFO-Position. Bei keiner Gleichheit gilt die unveränderte S2-TU-Übernahme. Bei mehr als einer Gleichheit wird nichts bestätigt oder übernommen und `CONFIRMATION_AMBIGUOUS_EXISTING_TRACE` ohne Zustandsänderung belegt. |

Die bestätigte Spur behält also ihr ursprüngliches Alter und ihre ursprüngliche
Generation. Eine Bestätigung verlängert weder ihre FIFO-Lebensdauer noch
erhöht sie Support, Schutz oder Priorität. Dadurch verdrängt die spätere
dritte tatsächlich neue Spur die bestätigte erste Spur wie jede andere älteste
Spur. Read-only Hinweise können nie `TRACE_CONFIRMED` auslösen.

## Vorab gebundene Folge

`a` bis `e` bezeichnen hier ausschließlich fünf später vorab gebundene
48-Wert-Eingangspositionen. Sie sind Planabkürzungen und dürfen im produktiven
Gleichheitsvergleich nicht als Quellenidentitäten verwendet werden.

| Ordinale | Abschnitt | Wahrnehmungsereignisse | Erwartung im Bestätigungsarm |
| --- | --- | --- | --- |
| e01-e05 | P1 | Formation `a,b,c,d`; Abschluss | Generation 1 wird übernommen. |
| e06-e10 | P2 | Formation `a,b,c,d`; Abschluss | Vollgleichheit zu Generation 1; `TRACE_CONFIRMED`, weiter genau eine gehaltene Spur. |
| e11-e12 | H1 | read-only Hint `b,c` | Bestätigungsarm eindeutig Generation 1; unveränderter Arm wegen zweier exakt gleicher Generationen mehrdeutig. |
| e13-e17 | P3 | Formation `d,c,b,a`; Abschluss | Keine Vollgleichheit; reguläre neue Generation 2. |
| e18-e19 | H2 | read-only Hint `d,c` | In beiden Armen eindeutiger Abruf der umgekehrten Folge. |
| e20-e24 | P4 | Formation `a,b,c,e`; Abschluss | Keine Vollgleichheit trotz dreier gleicher Positionen; reguläre Generation 3. Im Bestätigungsarm verdrängt sie die weiterhin älteste Generation 1. Der native Close-Receipt und das Inventar belegen diese Verdrängung. |
| e25-e26 | H3 | read-only Hint `d,a` | Reine Negativkontrolle: keine gehaltene Spur enthält dieses Nachbarpaar. Sie belegt keine Verdrängung. |

P3 ist die Gegenkontrolle für umgekehrte Ordnung mit denselben vier Werten.
P4 ist eine nur teilweise gleiche Folge; der vierte Zustand weicht ab. Das
belegt an realen Rezeptorwerten zunächst nur eine Zustandsabweichung. Ob genau
eine einzelne Rezeptorkomponente abweicht, bleibt einer getrennten neutralen
Fixture mit explizitem Einzelwertebeleg vorbehalten. P4 darf weder als
Bestätigung noch als nachträgliche Variantenbeziehung behandelt werden.

## Auswertung und Baselines

Die vorhandene S2-TU-Direktbaseline wird je Arm unabhängig aus denselben
gespeicherten Vierframevektoren nachgerechnet; sie übernimmt keinen
produktiven Suchhelfer. Getrennt auszuweisen sind:

1. belegte Speicherplatzdifferenz nach P2: Bestätigungsarm `1`,
   unveränderter Arm `2` gehaltene Spuren;
2. erhaltene oder verlorene eindeutige Abrufe je Hint und Arm;
3. Mehrdeutigkeiten, insbesondere H1 im unveränderten Arm;
4. die reguläre FIFO-Verdrängung der bestätigten Generation nach P4 anhand
   des nativen Close-Receipts und des aktuellen Inventars, getrennt von H3;
5. abweichende oder nicht erreichte Zustandsfolgen ohne Umdeutung als
   technischen Fehler.

Ein möglicher eindeutiger H1-Abruf im Bestätigungsarm ist ein begrenzter
Effekt fehlender Doppelbelegung. Er beweist weder eine richtige
Objektzuordnung noch eine zulässige Variation.

## Ressourcen und Anschlussgrenzen

Die `26` Ereignisse bestehen aus `22` materialisierten Audioendpunkten und
vier Segmentabschlüssen. Die Endpunkte werden nur einmal materialisiert und
an beide getrennten Stores übergeben. Der Plan benötigt `16` Formationen,
sechs Hintframes, drei Hintentscheidungen je Arm, vier Segmentabschlüsse je
Arm und zusätzlich je Arm einen finalen Owner-Abschluss. Das sind `22`
Audioanalysen und NJ-Projektionen, keine Feldkontakte und keine A/B-Scans.

Die Folge bleibt unter den vorhandenen Obergrenzen von `28` Ereignissen,
`20` Formationen und `22` Audioendpunkten. Konservativ benötigen beide Stores
zusammen höchstens `10.752` native Vektorbytes: je zwei gehaltene
Vierframe-Spuren, ein aktiver Vierframepuffer und ein Zweierhintpuffer. Die
vollständige Quellen-, Generations-, Fehler-, Verifikations- und
Ergebnishülle muss vor einer späteren Implementierung separat gegen die
unveränderten Grenzen von `98.304` Zustands-, `65.536` Metadaten- und
`262.144` Zusatzbytes gebunden werden.

Feld, bestehendes A/B-Memory, öffentliche Hypothesen und alle historischen
Defaults bleiben außerhalb dieses Plans unverändert.

## Falsifikation

Der Ansatz ist in diesem Umfang falsifiziert oder begrenzt, wenn P2 ohne
vollständige Vierframegleichheit bestätigt wird, bei Vollgleichheit einen
zweiten Platz belegt, eine Bestätigung das FIFO-Alter erneuert, P3 oder P4
bestätigt wird, ein Hint den Bestand verändert oder die bestätigte Generation
nach P4 entgegen der regulären FIFO-Reihenfolge weiter verfügbar bleibt.
