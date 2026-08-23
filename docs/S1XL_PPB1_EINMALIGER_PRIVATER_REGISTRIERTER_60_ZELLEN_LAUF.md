# S1-XL: Einmaliger privater registrierter 60-Zellen-Lauf

## Ausfuehrung

Nach erfolgreicher Digest- und Arbeitsverzeichnispruefung wurde der private
registrierte S1-XI-Runner genau einmal aufgerufen. Der Unlock galt nur im
Prozessspeicher und wurde im `finally`-Pfad zurueckgesetzt. Die Quelldatei
blieb unveraendert. Es gab keinen Retry, keinen Ersatzlauf, keinen Feldschritt
und keinen Produktionsaufruf.

## Atomarer Befund

Beide real ausgefuehrten synthetischen PPB-1-Bildungen entsprachen ihren
vollstaendigen Vorlagen. Alle 60 registrierten Zellen wurden verarbeitet und
das Matrixreceipt ist intern methodisch gueltig.

```text
method_valid:                    true
candidate_pass_cell_count:       9 von 10
technical_function_decision:     TECHNICAL_MEMORY_FUNCTION_FAIL
baseline_explanation_decision:   null
final_decision:                  TECHNICAL_MEMORY_FUNCTION_FAIL
matrix_receipt_digest:           c854345e708175ef4473b1044d3ab1cd40f48c39c0676789523fd8a52297e2ce
```

Die Entscheidungsreihenfolge stoppt nach dem Kandidatenfehler. Die
Baselineerlaeuterung wird deshalb nicht zur finalen Entscheidung erhoben.
Der Aggregator zeigt fuer das tatsaechliche Verhalten dennoch vollstaendige
Uebereinstimmung mit Replay, statischer Prototypbank, gleitendem Zustand und
letzter Vektordistanz. No-Memory stimmt nicht ueberein.

## Einzige abweichende Kandidatenzelle

```text
cell_id:               s1xa.auditory.ppb1.boundary-positive
expected_recognized:   true
observed_recognized:   false
expected_distance:     0.2
observed_distance:     0.20000000000000004
state_unchanged:       true
cell_receipt_digest:   ae30f7249a697a73efe1a070799befa3f8e8a7c6c67fdded4e4cbd22bfcc59e1
```

Die statische Quellpruefung zeigt eine naheliegende numerische Ursache: Die
auditive Schwelle und der Grenzreiz sind jeweils als `0.2` vorgegeben. Die
normalisierte L1-Rechnung ergibt in dieser Dimension jedoch
`0.20000000000000004`; die Probe prueft strikt `distance <= threshold`.
Diese Einordnung ist vor S1-XM nur eine gebundene
Gleitkomma-Grenzwert-Hypothese.

## Fachliche Grenze

Das Ergebnis ist die vorab gebundene technische
`TECHNICAL_MEMORY_FUNCTION_FAIL`-Entscheidung. Es weist weder eine
Memory-Faehigkeit noch eine MCM-spezifische Speicherwirkung nach. Eine
Korrektur, Neuinterpretation oder Wiederholung dieses Laufs ist nicht
zulaessig.

## Naechster Schritt

S1-XM prueft den vorhandenen Ergebnis- und Receiptstand unabhaengig und rein
statisch. Insbesondere muss er unterscheiden, ob ein Kandidatenfehler oder
eine vorregistrierte Grenzwertinkonsistenz vorliegt. S1-XM darf keine
Zustandsfunktion, Probe oder Matrix erneut ausfuehren und darf den
S1-XL-Befund nicht reparieren.
