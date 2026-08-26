# S2-AI: Statischer Abnahme- und Implementierungsfreigabeaudit

## Ergebnis

S2-AI nimmt die Browserwelt-Quellbindung aus S2-AH auf Vertragsniveau ab.
Das validierte `BrowserWorldContract` ist nun eine verbindliche Eingabe. Seine
ID und sein neu berechneter Digest koennen vor dem Aufbau einer Huelle exakt
gegen den Batch geprueft werden. Der S2-AG-Blocker ist damit geschlossen.

Die private Bindung ist trotzdem noch nicht implementierungsreif. Der Audit
findet genau eine weitere Zeitidentitaetsluecke.

## Verbleibende Quellclock-Luecke

S2-AF fordert innerhalb jeder Modalitaet streng steigende Quell-Endticks. Es
fordert aber noch nicht ausdruecklich, dass alle Frames dieser Modalitaet
denselben Quellclock verwenden.

`ReceptorTimeSequence` prueft den gemeinsamen Feldclock, nicht den Quellclock
der eingebetteten Rezeptorframes. PPB-1 bindet dagegen beim ersten akzeptierten
Frame einen Quellclock an den Bankzustand und verwirft jeden spaeteren
Clockwechsel. Ohne eine feste Clockidentitaet waere bereits der Vergleich der
Quellticks methodisch nicht eindeutig.

Die Audio- und Videostroeme duerfen unterschiedliche Quellclocks verwenden.
Innerhalb jedes einzelnen Stroms muss jedoch genau ein `source_clock_id`
gelten. Nur innerhalb dieses Clocks wird die streng steigende Endtickfolge
geprueft.

## Einmalaufruf und Reinheit

Die S2-AF-Angabe eines Aufrufs pro `binding_id` wird als vorregistriertes
Aufrufbudget des spaeteren Runners oder Fixtures eingeordnet. Die reine
Bindefunktion erhaelt keinen globalen Einmaligkeitsledger und verbraucht keine
Freigabe. Ein solcher Ledger wuerde einen neuen Zustand einfuehren und gehoert
nicht in diesen reinen Anschluss.

## Entscheidung und naechster Schritt

Die private Implementierung bleibt gesperrt. S2-AJ soll ausschliesslich den
statischen Vertrag um einen festen Quellclock je Modalitaetsstrom, die exakte
Frame-Clock-Uebereinstimmung und den zugehoerigen Fail-Closed-Fehler ergaenzen.
Neue Parameter, Implementierung, Tests und Ausfuehrung bleiben dabei gesperrt.

Maschinenlesbarer Audit:
[S2AI_STATISCHER_KORRIGIERTER_AKTIVBATCH_BINDUNGS_ABNAHME_UND_IMPLEMENTIERUNGSFREIGABEAUDIT_V1.json](S2AI_STATISCHER_KORRIGIERTER_AKTIVBATCH_BINDUNGS_ABNAHME_UND_IMPLEMENTIERUNGSFREIGABEAUDIT_V1.json).
