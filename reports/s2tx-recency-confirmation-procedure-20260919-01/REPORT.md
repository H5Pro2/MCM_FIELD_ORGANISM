# S2-TX-Verfahrensabweichung und nachträgliche Prüfdeckung

Der Lauf `s2tx-recency-confirmation-real-20260919-01` startete vor der
vollständigen neutralen Qualifikation. Sein Record und seine unabhängige
Verifikation bleiben unverändert; sie werden nicht rückwirkend qualifiziert.

Vor dem Start erforderlich waren sechs Gegenkontrollen: exakte Verjüngung,
umgekehrte Folge, teilweise beziehungsweise einzeln abweichende Folge,
unvollständige Formation, mehrdeutige Vollgleichheit und read-only Hint. Der
tatsächlich ausgeführte Aufruf lief nur die drei zuvor vorhandenen
Prüfmethoden. Die später ergänzten Methoden wurden damals nicht erreicht.
Der danach dokumentierte `IndentationError` betrifft die spätere Fassung der
ergänzten Testdatei. Er belegt die spätere Unausführbarkeit dieser Fassung,
nicht allein die Ursache des früheren Drei-Methoden-Aufrufs. Eine genauere
Kausalverknüpfung ist aus den vorhandenen Logs und Bindungen nicht belegt.

Nachträglich wurden die sechs fehlenden beziehungsweise korrigierten neutralen
Methoden unter aktueller Codebindung ausgeführt und bestanden. Zusätzlich
prüft `_s2tx_qualification_gate.py` künftig fail-closed die exakte Menge der
sechs Test-IDs sowie die aktuellen Hashes von Bestätigungs-, Quellen-, Runner-
und Verifikatorcode. Ein vollständiger Receipt wird akzeptiert; eine leere
ID-Menge wurde mit `QUALIFICATION_TEST_SET_INVALID` abgewiesen. Ergänzend
wurden eine teilweise vollständige ID-Menge, ein formell vollständiger Receipt
mit Status `FAILED` und ein Receipt mit abweichendem Codehash jeweils
fail-closed geprüft.

Diese Deckung gilt nur prospektiv. Der bereits ausgeführte Lauf bleibt ein
technisch verifizierter, aber nicht qualifizierter Beobachtungsrecord. Es wird
kein weiterer S2-TX-Hauptlauf vorbereitet oder ausgeführt.
