# S2-NR: fokussierter Abschluss der neutralen Testbindung

ID: `s2nr-main-binding-focused-qualification-20260908-01`.
Ein einziger unittest-Aufruf, genau drei unabhaengige Tests der Klasse
`NRFailureBindingTests`. Kein Aufruf von `NRRunTests.setUpClass`, keine
Wiederholung der bestandenen elf Tests oder der historischen 16/16-Pruefung.
Kein Failfast zwischen den drei unabhaengigen Kontrollen; kein Retry.

## Feste Kontrollen

1. Frische Kopie des gespeicherten neutralen Payloadfehlerbelegs. Den dazu
   gehoerenden neutralen Plan allein durch die belegte Metadatenaenderung aus
   Test 05 herstellen: Payloadhash der ersten Quelle auf 64 Nullen, Quellen-
   und Plandigest neu binden. Der Digest muss dem im Fehlerbeleg entsprechen.
   Keine PCM-Erzeugung. Danach Ordinal auf 2 setzen. Erwartet exakt
   `S2NRRunError`, Code `FAILURE_PHASE_PROGRESS_INVALID`; Eintritt in die
   Fehlerfortschrittspruefung muss beobachtet werden.
2. Frische Kopien des gespeicherten neutralen Erfolgsbelegs und seiner
   Verifikation. Nur den Ziel-Recorddigest des Pruefbelegs auf 64 Nullen setzen
   und dessen eigenen Digest binden. Erwartet exakt `S2NRRunError`, Code
   `EVALUATION_REQUIRES_VERIFICATION`. Keine fachliche Auswertung danach.
3. Neue frische Fehlerbelegkopie mit dem unveraenderten urspruenglichen,
   unpassenden neutralen Plan. Erwartet exakt `S2NRRunError`, Code
   `TOTAL_BINDING_INVALID`; die tiefere Fehlerpruefung darf nicht erreicht sein.

Jede Kontrolle prueft unveraenderte Eingabekopien nach der Ablehnung. Keine
pauschale Exceptionakzeptanz. Erzeugung, Materialisierung, Runtime und die
vollstaendige Kompositionsverifikation sind im Test mit Aufrufsperren versehen.

## Administrative Testbindung

Der Produktverifikator prueft auch den Hash der Testdatei. In den neuen,
ausdruecklich synthetischen Fehlerbelegkopien wird deshalb ausschliesslich
diese administrative Bindung auf die korrigierte Testdatei gesetzt. Vorher
muss die Differenzmenge zwischen historischen und aktuellen Codebindungen
exakt `tests/test_s2nr_private_run.py` sein. Keine weitere Hashausnahme und
keine Produktlockerung. Historische Dateien bleiben bytegleich.

## Umfang und Grenzen

Zwei Fehlerpfad-Eintritte im Gesamtverifikator; ein Auswertereintritt, der an
der Verifikationsbindung stoppt. Null Payloads, Rezeptoren, NJ, Formation,
Runtime, Feldkontakte, Scans und neue Distanzberechnungen. Keine neuen Grenzen:
bestehendes Artefaktlimit 4194304 Byte; kleine Kontrollbelege <=65536 Byte.
Quellhashes, historisches Testinventar und alle bisherigen Belegdateien werden
vor/nach dem Aufruf gebunden. Die elf alten Testkoerper werden gegen ihren
Git-Stand `161c058a` rein statisch auf Unveraendertheit verglichen.

Bei Bestehen tragen gemeinsam: historische 16/16-Typ-/Maskenanbindung,
elf erfolgreiche Laufanbindungspruefungen aus dem unveraenderten 11/12-Lauf
und die drei neuen Kontrollen. Dies ist kein neuer 12/12-Komplettlauf und kein
NR-Funktionsbefund. Der alte Fehlbefund bleibt `NOT_QUALIFIED`.

Der Produktcode bleibt bytegleich, einschliesslich seines Verweises auf den
historischen `QUAL_ID`-Beleg. Die neue zusammengefuehrte Qualifikationsdeckung
schreibt diesen nicht um und oeffnet keinen Haupteinstieg. Eine spaetere
Hauptlauffreigabe muss auch diese rein administrative Aufrufbindung explizit
beruecksichtigen. Alle Gates bleiben False.
