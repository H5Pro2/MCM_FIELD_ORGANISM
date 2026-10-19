# S2-UA: Statische Entscheidung zu kurzfristiger Verlaufsaufnahme und Übernahme

Stand: 2026-09-20. Dieser Befund ist reine Codelektüre. Er erzeugt keine
Quellen, Rezeptorwerte, Tests oder Läufe. ME/MI bleiben gesperrt.

## Frage und Aussagegrenze

S2-TZ hat gezeigt, dass die unmittelbare Übernahme jedes überlappenden
Viererfensters bei zwei FIFO-Slots selbst Verdrängung erzeugt. Hier wird nur
geprüft, ob eine vollständige neue Viererfolge zunächst flüchtig bleiben und
erst eine zweite exakte, zeitlich nichtüberlappende Beobachtung ihre Übernahme
begründen könnte.

Das wäre eine handkonstruierte Regel für die Aufbewahrung. Sie belegt weder
Identität noch Relevanz, Variantenbindung oder biologische Festigung.

## Vorhandener Bestand

| Komponente | Vorhandene Fähigkeit | Grenze für den Kandidaten |
| --- | --- | --- |
| `TemporalTrace` (S2-TS) | hält einen bildenden oder aktiven Vierertrace getrennt von Feld und A/B-Memory; Hints sind read-only | Nach einer aktiven Spur verwirft die nächste Formation die Spur und startet keine Ersatzspur. Der Zustand reicht daher nicht als Kandidatenbestand über mehrere Abschnitte. |
| `RetainedTraceStore` (S2-TU) | hält nach `close_segment` höchstens zwei vollständige Traces FIFO und prüft zweiframige Hints read-only | Seine `_forming`-Map ist nicht global begrenzt. Sie darf nicht als impliziter Kandidatenpool für einen fortlaufenden Strom verwendet werden. |
| `ExactConfirmationStore` (S2-TW) | bestätigt eine bereits retained, vollständig wertgleiche Folge ohne Altersänderung | Er vergleicht nicht gegen eine flüchtige Kandidatenspur und führt keine Übernahmeregel. |

Damit existiert eine begrenzte kurzfristige Viereraufnahme, aber kein
vorhandener, begrenzter Kandidatenbestand, der eine spätere zweite Beobachtung
über Segmentgrenzen fair verwalten könnte.

## Einzige geprüfte Übernahmeregel

Für einen späteren, getrennt freizugebenden Vergleich wäre nur diese Regel
zulässig:

1. Eine neue vollständige, nicht bereits retained Viererfolge belegt einen
   flüchtigen Kandidatenplatz, nicht einen Retained-Slot.
2. Eine zweite vollständig exakte Folge mit disjunkten Ereignisordinalen zum
   Kandidaten fördert genau diesen Kandidaten in den Retained-Bestand.
3. Eine teilweise passende, umgekehrte oder überlappende Folge fördert nicht.
4. Ein read-only Hint verändert weder Kandidat noch Retained-Reihenfolge.
5. Eine bereits retained exakte Folge folgt unverändert S2-TW:
   `TRACE_CONFIRMED` ohne Verjüngung.

"Zeitlich nichtüberlappend" bedeutet hier nur, dass die vier
Ereignisordinalen der zweiten Beobachtung disjunkt zu denen des Kandidaten
sind. Es bedeutet nicht, dass beide Folgen dieselbe Quelle, ein Objekt oder
eine Episode darstellen.

## Faire Speicherbilanz

Ein Vorteil darf nicht aus zusätzlichem Speicher folgen. Der unmittelbare
S2-TW-Arm verwendet die bestehende S2-TW-Exaktbestätigung über dem
S2-TU-Retained-Store und kann gleichzeitig zwei retained Vierertraces und eine noch bildende
Viererfolge führen: höchstens zwölf vollständige Frames. Der Kandidatenarm
dürfte bei derselben Obergrenze höchstens einen retained Vierertrace, einen
flüchtigen Kandidatentrace und eine noch bildende Viererfolge führen: ebenfalls
zwölf vollständige Frames.

| Arm | Retained | flüchtiger vollständiger Kandidat | bildende Folge | maximale Frames |
| --- | ---: | ---: | ---: | ---: |
| unmittelbare S2-TW-Übernahme | 2 × 4 | 0 | 4 | 12 |
| geprüfte Kandidatenregel | 1 × 4 | 1 × 4 | 4 | 12 |

Alle Rahmen-, Herkunfts-, Zeit-, Generationen-, Hint- und Receiptbindungen
müssten zusätzlich in beiden Armen gleich vollständig gezählt werden. Ein
zweiter Kandidatenplatz oder zwei Retained-Slots zusätzlich zum Kandidaten
wäre ein Speicherzuwachs und kein fairer Vergleich.

## Statische Gegenüberstellung

`A`, `B` und `C` stehen für unterschiedliche vollständige Viererfolgen. Ein
Pfeil bedeutet Abschluss der jeweiligen Folge; er enthält keine Quelle oder
Rolle.

| Folge | Unmittelbare Übernahme | Kandidatenregel mit 1 Retained + 1 Kandidat | Erhaltung und Verlust |
| --- | --- | --- | --- |
| `A -> A -> B -> C` | `A` wird angelegt und bestätigt; `B` belegt den zweiten Retained-Slot; `C` verdrängt `A`. | Erstes `A` wird Kandidat, zweites disjunktes `A` wird retained. `B` wird Kandidat; `C` ersetzt den unbestätigten Kandidaten `B`. | `A` bleibt unter einmaligem Druck erhalten. `B` geht verloren, obwohl die unmittelbare Übernahme es noch retained hätte. Der Erhaltungsgewinn und dieser Verlust sind getrennt. |
| `A -> B -> A` | `A` und `B` werden retained; das spätere `A` bestätigt `A`. | Erstes `A` wird Kandidat; `B` ersetzt es; spätes `A` ist nur ein neuer Kandidat. | Wiederholung nach Unterbrechung fördert nicht. Der Kandidat zeigt keinen Vorteil; die Unterbrechung zerstört die einzige vorläufige Evidenz. |
| `A -> A -> B -> B` | `A` und `B` werden beide retained. | `A` wird retained. `B` wird Kandidat und müsste bei seiner zweiten Beobachtung entweder `A` FIFO-verdrängen oder trotz exakter Wiederholung nicht übernommen werden. | Zwei bestätigte konkurrierende Folgen passen nicht gleichzeitig in die faire Partition. Die nötige Entscheidung darf nicht verborgen bleiben. |
| `A -> A' -> A` oder `A -> reverse(A) -> A` | Jede vollständige Folge wird unmittelbar retained, soweit Kapazität besteht. | `A'` beziehungsweise `reverse(A)` bestätigt den Kandidaten `A` nicht; sie ersetzt ihn. Das spätere `A` beginnt nur erneut als Kandidat. | Teil- oder Reihenfolgeähnlichkeit wird nicht fälschlich gefördert; zugleich kann eine wiederkehrende Störung den Kandidatenverlust verursachen. |
| `A -> A -> B -> C -> A` | Nach `C` ist `A` bei FIFO-Druck nicht mehr retained; das letzte `A` wird neu angelegt. | Nach der Bestätigung von `A` bleiben `B` und `C` nur wechselnde Kandidaten; das letzte `A` ist bereits retained und wird unverändert bestätigt. | Ein enger Erhaltungsvorteil für eine früh bestätigte Spur ist plausibel. Die anderen Folgen werden nicht dauerhaft bewahrt. |

Die Hints eines späteren Vergleichs müssen jeweils vor einer erneuten
Formation der geprüften Folge ausgeführt werden. Sie prüfen den vorbestehenden
Retained-Bestand; ein Kandidat und seine noch bildende Wiederholung dürfen den
Hinweis nicht zuerst erzeugen und dann als ältere Erinnerung ausgeben.

## Minimaler Anschluss und offene Grenze

Eine spätere Umsetzung bräuchte einen privaten, streng begrenzten
Kandidatenkoordinator mit genau einem Kandidatenplatz und einer expliziten
Übernahme- oder FIFO-Verdrängungsentscheidung für den einzigen Retained-Slot.
Er könnte vorhandene Framevalidierung, S2-TU-Hints und S2-TW-Bestätigung
wiederverwenden. `TemporalTrace`, `RetainedTraceStore` und
`ExactConfirmationStore` selbst sollten dabei unverändert bleiben.

Ohne diese neue Koordinatorregel gibt es keinen vorhandenen Anschluss: S2-TS
verwirft die aktive Spur beim nächsten Formationsschritt, S2-TU begrenzt
offene Segmente nicht und S2-TW kennt keine flüchtige Vergleichsspur.

## Entscheidung

Ein konkreter, aber enger Erhaltungsvorteil ist statisch plausibel: Nach
`A -> A` kann ein einmaliger Druck durch `B -> C` die bestätigte Spur im
fair partitionierten Kandidatenarm erhalten, während die unmittelbare
Zwei-Slot-FIFO sie verliert. Derselbe Vergleich weist zugleich den Verlust
von `B` und die Unfähigkeit nach, zwei bestätigte konkurrierende Folgen
gleichzeitig zu bewahren.

Damit ist der Kandidat nicht allgemein vorteilhaft. Die statische Entscheidung
gab nur eine private neutrale Kompositionsprüfung frei. Ein späterer
Funktionsvergleich müsste den Nutzen gegen die einzeln ausgewiesenen Verluste
unter exakt derselben Gesamtframekapazität testen. Gibt es keinen solchen
getrennten Erhaltungsgewinn oder verlangt die Implementierung mehr als einen
Kandidaten, einen Retained-Slot und eine bildende Folge, ist der Kandidat
ohne Ersatzregel zu verwerfen.

## Private Anschlussprüfung

Die begrenzte private Vergleichskomposition ist anschließend implementiert,
ohne TS, TU oder TW zu ändern. Der unmittelbare Arm kapselt den unveränderten
`ExactConfirmationStore`; der Kandidatenarm hält genau einen bildenden Trace,
einen Kandidaten und einen retained Trace. Die Promotion prüft vollständige
Wertegleichheit und disjunkte Ordinalmengen. Eine bereits retained exakte
Folge bestätigt ohne Verjüngung und lässt einen eventuell vorhandenen
Kandidaten unverändert.

| Fall | Unmittelbarer S2-TW-Arm | Kandidatenarm | Neutral geprüft |
| --- | --- | --- | --- |
| `A -> A -> B -> C` | `A` wird nach `C` FIFO-verdrängt; `B` bleibt abrufbar | `A` bleibt retained; `B` wird durch `C` als Kandidat ersetzt | ja |
| `A -> B -> A` | S2-TW behält `A` und `B` | `A` wird vor der zweiten Beobachtung als Kandidat ersetzt | ja |
| `A -> A -> B -> B` | beide Spuren sind retained | zweite Promotion ersetzt die erste retained Generation | ja |
| Teilabweichung, Umkehrung | keine Exaktbestätigung | Kandidat wird ersetzt, nicht gefördert | ja |
| gleiche Ordinale erneut | nicht Teil der S2-TW-Promotion | `TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED`; Kandidat bleibt | ja |
| Hint mit Kandidat | S2-TW liest nur retained | Kandidat ist nicht hintlesbar; Hint lässt Zustand unverändert | ja |

Die unabhängige Direktnachrechnung verwendet keine Methoden des produktiven
Kandidatenarms und stimmt für die gebundene Übergangsfolge bei Aktionen,
Retained-Inventar und Kandidatengeneration überein.

### Ressourcenbilanz der neutralen Komposition

| Belegklasse | unmittelbarer S2-TW-Arm | Kandidatenarm |
| --- | ---: | ---: |
| retained Traceframes | höchstens 8 | höchstens 4 |
| Kandidatenframes | 0 | höchstens 4 |
| bildende Traceframes | höchstens 4 | höchstens 4 |
| produktive Traceframes gesamt | höchstens 12 | höchstens 12 |
| getrennter Hintbuffer | höchstens 2 | höchstens 2 |

Die Hintframes sind nicht Teil der Tracekapazität und werden nach jeder
Zweiframe-Prüfung verworfen. Die direkte Nachrechnung führt nur ihren
eigenen Kandidaten- und Retained-Zustand; Testgruppen und Transition-Receipts
sind externe neutrale Testbelege und keine produktiven Memoryzustände.

`tests.test_s2ub_candidate_confirmation` bestand mit `11/11` Tests. Das ist
eine neutrale Kompositionsprüfung, keine Quellen-, Rezeptor- oder
Systemqualifikation und keine Freigabe für einen realen Lauf.

## Codebezüge

- [S2-TS: begrenzte aktive Viereraufnahme und Verfall](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2ts_temporal_trace.py:58)
- [S2-TS: Hint bleibt read-only](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2ts_temporal_trace.py:90)
- [S2-TU: Segmentbildung und nicht global begrenzte `_forming`-Map](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2tu_retained_trace.py:41)
- [S2-TU: Zwei-Slot-FIFO beim Abschluss](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2tu_retained_trace.py:61)
- [S2-TU: read-only Hintentscheidung](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2tu_retained_trace.py:73)
- [S2-TW: exakte Bestätigung nur gegen Retained-Spuren](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2tw_exact_confirmation.py:10)
