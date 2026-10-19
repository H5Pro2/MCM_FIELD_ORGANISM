# S2-TZ: Statische Anschlussentscheidung für fortlaufende Viererfenster

Stand: 2026-09-20. Dieser Befund ist eine Codelektüre. Er erzeugt keine
Quellen, keine Rezeptorwerte, keine Tests und keinen Lauf.

## Frage und Grenze

Untersucht wird ausschliesslich, ob ein fortlaufender Wahrnehmungsstrom nach
jedem Endpunkt höchstens ein technisches Viererfenster an die vorhandene
exakte Spurbetätigung übergeben könnte. Die feste Länge vier ist eine
Buffergrenze, keine Episode, kein Objekt und keine semantische Zuordnung.

## Bestehender Anschluss

`RetainedTraceStore` verlangt pro Frame bereits einen nichtleeren
`segment`-Wert, sammelt pro Segment höchstens vier Frames und legt beim
Schliessen eine Spur ab. Die Aufbewahrung enthält nur zwei Spuren; die dritte
verdrängt die älteste FIFO-Generation. Der bestehende Hint-Pfad liest zwei
Frames und verändert die Aufbewahrung nicht.

`ExactConfirmationStore` erweitert nur den Abschluss: Eine vollständig
wertegleiche, noch aufbewahrte Viererfolge wird bestätigt, ohne Generation
oder FIFO-Position zu erneuern. Die vorhandene S2-TY-Steuerung und ihr
Adapter erwarten dagegen vorab bekannte Segmentnamen und explizite
`CLOSE`-Ereignisse. Sie können einen fortlaufenden Strom daher nicht
unverändert führen.

## Kleinster mögliche Anschluss

Ein privater, profilgebundener Rolling-Adapter wäre ausreichend; Kern,
Defaults und bestehende Segmentvalidatoren bleiben unverändert.

1. Er hält höchstens die vier letzten aufsteigenden Endpunkte samt bestehender
   Profil-, Owner-, Zeit- und Herkunftsbindung.
2. Ab dem vierten Endpunkt bildet er genau ein Fenster aus den letzten vier
   Endpunkten. Seine interne technische Segmentkennung wird deterministisch
   aus erstem und letztem Ordinal abgeleitet. Sie ist keine vom Aufrufer
   gelieferte Inhaltsrolle.
3. Der Adapter übergibt genau diese vier Frames an einen eigenen bestehenden
   `ExactConfirmationStore` und schliesst nur dieses technische Segment.
   Anschliessend verwirft er die temporäre Segmentbildung und verschiebt den
   Buffer um genau einen Endpunkt.
4. Ein Endpunkt erzeugt somit höchstens ein neues Kandidatenfenster. Eine
   Viererfolge wird nicht aus einem vorherigen Trace rekonstruiert.

Die bestehende S2-TY-Ereignissteuerung darf hierfür nicht umgedeutet werden:
Ihr vorab ermitteltes Segmentinventar ist gerade die zu ersetzende
Aufruferannahme. Die kleinste Änderung wäre ein neuer privater Adapter mit
einem engen Receipt, nicht eine Änderung von `RetainedTraceStore`,
`ExactConfirmationStore` oder des historischen S2-TY-Adapters.

## Fairer späterer Vergleich

Vor einer Implementierung muss eine neue, endliche neutrale Folge vor jeder
Materialisierung festgelegt werden. Sie benötigt mindestens diese getrennten
Fälle:

| Fall | Vorab gebundene Struktur | Zu prüfende Aussage |
| --- | --- | --- |
| Verschobene Wiederholung | dieselbe geordnete Viererfolge an einem späteren Startordinal | Bestätigung nur, wenn die ursprüngliche Generation noch tatsächlich retained ist; sonst neue Belegung statt stillschweigender Bestätigung |
| Reihenfolgekontrolle | dieselben vier Werte in anderer Reihenfolge | keine exakte Bestätigung durch Multisetgleichheit |
| Konkurrenz | mindestens eine weitere geordnete Viererfolge zwischen den Wiederholungen | Inventar, Generationen und jeden FIFO-Verlust getrennt festhalten |

Als einfache Baseline dient derselbe fest gebundene Endpunktstrom mit
nichtüberlappenden, explizit geschlossenen Vierergruppen. Sie verwendet
denselben `ExactConfirmationStore`, dieselben zwei Retained-Slots und dieselbe
Hint-Regel, aber keine verschobenen Kandidatenfenster. Verglichen werden
nicht nur Treffer, sondern Anzahl der Retentionen, Bestätigungen,
Generationen, Verdrängungen und die read-only Entscheidungen.

Überlappung ist ein konkretes Verlustrisiko: Aus `a,b,c,d,e` entstehen bereits
`a,b,c,d` und `b,c,d,e`. Die zweite, normalerweise nicht exakt gleiche Spur
belegt den zweiten Slot; ein weiteres geschobenes Fenster verdrängt die
erste. Eine spätere Wiederholung von `a,b,c,d` kann dann nicht mehr
bestätigen, sondern wird neu angelegt. Dieses Risiko darf nicht durch einen
Erhaltungsgewinn verrechnet werden.

## Zeitliche Trennung von Prüfung und Aufnahme

Jede spätere Kontrollprüfung erhält einen Snapshot von Inventar und
Generationen **vor** einer etwaigen Übergabe ihres letzten Endpunkts an den
Rolling-Adapter. Die Prüfung läuft ausschliesslich über den vorhandenen
read-only Hint-Pfad. Erst danach darf ein nachfolgender, als Formation
gebundener Endpunkt in den Buffer gelangen. Damit kann ein Prüffenster weder
zuerst gespeichert werden noch sich selbst unmittelbar abrufen.

Die Receipts müssen die Reihenfolge `CHECK -> SNAPSHOT -> optional
ROLLING_ACCEPT` sichtbar machen. Ein Hint darf weder eine Generation erneuern
noch die FIFO-Position verändern.

## Ressourcen und offene Bindungen

Die Kernnutzlast bleibt begrenzt: pro Arm zwei retained Vierertraces
(`2 * 4 * 48` Binary64-Werte) und ein Rolling-Buffer mit höchstens vier
Frames. Der geplante S2-TY-Ledger ist dafür nicht verwendbar, weil er fest
auf 26 Ereignisse, 22 Endpunkte, 16 Formationen, sechs Hintframes und vier
Segmentabschlüsse gebunden ist.

Eine spätere Anschlussbindung muss deshalb vorab separat festlegen und
bilanzieren:

- Endpunktzahl, Kandidatenzahl und Zahl der read-only Hintframes;
- je Kandidat vier Formation-Übergaben und einen Abschluss pro Vergleichsarm;
- vollständige Receipts für Start-/Endordinal, Generation, Bestätigung oder
  Verdrängung und die Prüfreihenfolge;
- die bestehenden Artefakt- und Gesamtgrenzen ohne Übernahme der S2-TY-Form.

Für Quellen-, Rezeptor-, Feld- und Laufbudgets gibt es aus der reinen
Kernlektüre noch keine tragfähige konkrete Zahl. Diese Informationen müssen
mit der späteren endlichen Quellfolge gebunden werden; sie dürfen nicht aus
dem bisherigen S2-TY-Plan übernommen werden.

## Anschlussentscheidung

Der technische Anschluss ist mit einem kleinen privaten Rolling-Adapter
möglich. Ein Nutzen ist daraus nicht abgeleitet. Vor einer Implementierung
muss der Vergleich zeigen können, ob die zusätzliche Überlappung eine noch
retained exakte Wiederholung bestätigt und zugleich welchen validen Abruf sie
durch FIFO-Verdrängung verliert.

**Abbruchkriterium:** Falls der vorab gebundene Vergleich keine überprüfbare
Unterscheidung gegenüber der nichtüberlappenden Baseline liefert oder die
überlappenden Kandidaten nur zusätzliche Verdrängungen ohne getrennt belegten
read-only Nutzen erzeugen, wird kein Rolling-Anschluss implementiert. Es
wird keine Ersatzsegmentierung, Schutzschwelle oder zusätzliche Memoryregel
eingeführt.

## Endliche symbolische Gegenprobe

Die folgenden Endpunkte sind nur unterscheidbare Symbole, keine
Rezeptorwerte oder Quellen. In beiden Armen beginnt die nichtüberlappende
Baseline verbindlich bei Ordinal 1 und schliesst nur die Gruppen `1–4`,
`5–8`, `9–12` und so weiter. Der Rolling-Arm bildet ab Ordinal 4 genau das
letzte Viererfenster. `gN` bedeutet neu angelegte Generation N; `-gN`
deren FIFO-Verdrängung. `C(gN)` bedeutet exakte Bestätigung der noch
retained Generation ohne Altersänderung. Die Klammer am Ende jeder Zelle ist
das Inventar nach diesem Aufnahmeschritt.

| Fall und Strom | Nichtüberlappende Baseline | Rolling-Arm: vollständige Kandidatenableitung | read-only Prüfung vor möglicher weiterer Aufnahme |
| --- | --- | --- | --- |
| Ausgerichtete Wiederholung unter Druck: `a b c d e f g h a b c d` | `1–4: abcd -> g1 [g1]`; `5–8: efgh -> g2 [g1,g2]`; `9–12: abcd -> C(g1) [g1,g2]` | `4: abcd -> g1 [g1]`; `5: bcde -> g2 [g1,g2]`; `6: cdef -> g3 -g1 [g2,g3]`; `7: defg -> g4 -g2 [g3,g4]`; `8: efgh -> g5 -g3 [g4,g5]`; `9: fgha -> g6 -g4 [g5,g6]`; `10: ghab -> g7 -g5 [g6,g7]`; `11: habc -> g8 -g6 [g7,g8]`; `12: abcd -> g9 -g7 [g8,g9]`. Keine Bestätigung: die ursprüngliche `g1` ist vor der Wiederholung verdrängt. | Vor Ordinal 9 prüft die Baseline `a,b` eindeutig in `g1` an Position 0. Der Rolling-Arm hat nach Ordinal 8 nur `g4` und `g5`, die `a,b` nicht enthalten, und enthält sich. Die späteren neuen Fenster liefern zwar `a,b` in `g7`/2 und `g8`/1, aber diese Treffer stammen bereits aus der neuen Wiederholung und sind kein älterer Abrufgewinn. |
| Tatsächlich verschobene Wiederholung: `a b c d e f g a b c d x` | `1–4: abcd -> g1 [g1]`; `5–8: efga -> g2 [g1,g2]`; `9–12: bcdx -> g3 -g1 [g2,g3]`. Die Wiederholung an `8–11` ist keine Baselinegruppe. | `4: abcd -> g1 [g1]`; `5: bcde -> g2 [g1,g2]`; `6: cdef -> g3 -g1 [g2,g3]`; `7: defg -> g4 -g2 [g3,g4]`; `8: efga -> g5 -g3 [g4,g5]`; `9: fgab -> g6 -g4 [g5,g6]`; `10: gabc -> g7 -g5 [g6,g7]`; `11: abcd -> g8 -g6 [g7,g8]`; `12: bcdx -> g9 -g7 [g8,g9]`. Das verschobene `abcd` wird neu angelegt, weil `g1` bereits verdrängt ist. | Vor Ordinal 8 ist `a,b` in der Baseline eindeutig in `g1`/0. Der Rolling-Arm führt nach Ordinal 7 nur `g3` und `g4` und enthält sich. `g7`/1 und `g8`/0 enthalten `a,b` erst nach Beginn der neuen verschobenen Wiederholung; sie sind kein Abruf einer älteren Spur. |
| Reihenfolgekontrolle: `a b c d d c b a` | `1–4: abcd -> g1 [g1]`; `5–8: dcba -> g2 [g1,g2]` | `4: abcd -> g1 [g1]`; `5: bcdd -> g2 [g1,g2]`; `6: cddc -> g3 -g1 [g2,g3]`; `7: ddcb -> g4 -g2 [g3,g4]`; `8: dcba -> g5 -g3 [g4,g5]`. | Vor Aufnahme von Ordinal 5 ist `a,b` in `g1`/0 eindeutig. Nach dem Strom ist `d,c` in der Baseline nur `g2`/0. Im Rolling-Arm treffen `g4`/1 (`ddcb`) und `g5`/0 (`dcba`); das Ergebnis ist `ABSTAIN_AMBIGUOUS_RETAINED_TRACE`. Die geänderte Reihenfolge bestätigt keine frühere Spur und erzeugt zusätzlich Mehrdeutigkeit. |
| Konkurrenz und Abrufverlust: `x y z w a b c d q r s t` | `1–4: xyzw -> g1 [g1]`; `5–8: abcd -> g2 [g1,g2]`; `9–12: qrst -> g3 -g1 [g2,g3]` | `4: xyzw -> g1 [g1]`; `5: yzwa -> g2 [g1,g2]`; `6: zwab -> g3 -g1 [g2,g3]`; `7: wabc -> g4 -g2 [g3,g4]`; `8: abcd -> g5 -g3 [g4,g5]`; `9: bcdq -> g6 -g4 [g5,g6]`; `10: cdqr -> g7 -g5 [g6,g7]`; `11: dqrs -> g8 -g6 [g7,g8]`; `12: qrst -> g9 -g7 [g8,g9]`. | Unmittelbar nach Ordinal 8, vor jeder weiteren Aufnahme, prüft die Baseline `a,b` eindeutig in `g2`/0. Der Rolling-Arm findet `a,b` gleichzeitig in `g4`/1 und `g5`/0 und muss daher `ABSTAIN_AMBIGUOUS_RETAINED_TRACE` liefern. Die Konkurrenz erzeugt einen konkreten Verlust eines zuvor eindeutigen Abrufs. |

Die Hintregel durchsucht in jeder noch retained Spur alle drei möglichen
Zweiframe-Positionen. Die Tabelle zählt daher nicht nur eine Zielposition;
die zusätzlichen passenden Positionen der überlappenden Spuren sind Teil der
Entscheidung.

### Prüfreihenfolge

Für jede Tabelle gilt verbindlich: `Vorzustand sichern -> read-only prüfen ->
Unverändertheit von Inventar und Generationen bestätigen -> optional
aufnehmen`. Der jeweilige Hint wird nicht als Formation in den Rolling-Buffer
übergeben. Dadurch wird kein Treffer, den erst frühere Frames desselben
Prüfvorgangs gebildet haben, als Erinnerung an eine ältere Erfahrung gezählt.

### Entscheidung aus der Tabelle

Die Gegenprobe zeigt keinen eindeutig zurechenbaren Abrufgewinn des
Rolling-Kandidaten gegenüber der festen nichtüberlappenden Baseline. Sowohl
die ausgerichtete als auch die tatsächlich verschobene Wiederholung verlieren
ihre bestätigbare ursprüngliche Generation. Der Reihenfolgewechsel und die
Konkurrenz erzeugen Mehrdeutigkeit, während die Baseline jeweils eindeutig
bleibt. Damit entstehen in dieser vollständig abgeleiteten, kleinsten
Vergleichsform zusätzliche Belegung, Verdrängung und Mehrdeutigkeit, jedoch
kein belegbarer Nutzen.

**Statische Entscheidung: STOPP.** Der Rolling-Anschluss wird nicht
implementiert. Eine andere Fensterlänge, Segmentierungsregel, FIFO-Ausnahme,
Schutzschwelle oder zusätzliche Memoryregel wäre ein neuer Auftrag und wird
aus dieser Tabelle nicht abgeleitet.

## Codebezüge

- [RetainedTraceStore: Framebindung, Viererbildung, FIFO und Hint](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2tu_retained_trace.py:32)
- [RetainedTraceStore.form](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2tu_retained_trace.py:53)
- [RetainedTraceStore.close_segment](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2tu_retained_trace.py:61)
- [ExactConfirmationStore.close_segment](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2tw_exact_confirmation.py:10)
- [S2-TY-Steuerung mit vorab bekannten Segmenten](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2ty_event_control.py:17)
- [S2-TY-Adapter mit Segmentinventar](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2ty_perception_trace_adapter.py:7)
- [Fest gebundener S2-TY-Ledger](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2ty_resource_ledger.py:31)
