# ER1 v2: Ressourcenplanung mit strukturellem Bestandsvergleich

2026-10-18. Messung und Planung werden getrennt; kein vollständiger Forschungsfall.

## Ausführungen und Grenzen

32 Geschichten, 64 einmalig gemessene und protokollierte Policy-Arme, 64 begleitende
Live-Referenzen und 64 zusätzliche Archivrekonstruktionen. Keine zusätzlichen
Mess-/Capture-Policyarme. Hinzu kommen 32 Quellenrekonstruktionen und eine
unabhängige Serienstatistik. Die Grenzen bleiben unverändert: Worker 54000 s,
Gesamt 57600 s einschließlich Abschlussreserve 3600 s, gemeinsamer 512-MiB-Job,
höchstens zwei Prozesse. Vorbereitung 8 MiB, Administration 2 MiB, Closure 1 MiB,
Export einschließlich Vorbereitung/Temporärdaten 64 MiB.

## Tatsächlich gemessene neue Integration

Zwei neutrale Fälle mit je 80 Frames pro Arm, zehn echte Promotionen und
Generationen 9/10; ein positiver Lauf und vier gezielte Fehlerläufe.
Die Gesamtvorbereitung erzeugte damit 20 kurze Policy-Arme. Diese Prüfungen sind
keine späteren Forschungsarme und werden nicht im Forschungsauftrag wiederholt.
99/100 wurde synthetisch geprüft, ohne große Policyfolge.

Der neue Stock- und Observervergleich ist Bestandteil aller unten gemessenen
Archivprüfzeiten. Eine zusätzliche reine Messung des vollständigen neutralen
E-Bestands an Frame 80 führte 100 Strukturvergleiche ohne Policy oder Referenzreplay
aus: 0.271765 s, 100733 Bytes Pythonpeak; 0.00271765 s/Vergleich unter
tracemalloc. Dieser instrumentierte Wert ist kein Serienbenchmark und wird nicht
zusätzlich zur bereits enthaltenen Archivprüfzeit addiert.

Lineare Projektion aus den neuen kurzen Zeitmessungen für 32 Geschichten:

- Policy, Capture, Einzeloperationsmessung und Live-Referenzen zusammen:
  1213.8 s.
- Archivprüfung einschließlich neuer Strukturvergleiche und Referenzrekonstruktionen:
  378.7 s.
- Gesamte Fallarbeit einschließlich Kodierung, Beobachter, Mechanismen und Inventur:
  1929.2 s; die obigen Posten sind darin enthalten.

Planungsansatz: Faktor 8 auf die gesamte Fallarbeit plus 600 s für Quellen,
Statistik und Verwaltung = 16034 s, anschließend 3600 s
Abschlussreserve innerhalb der Gesamtfrist. Hochrechnung ist keine Garantie;
Grenzüberschreitung bleibt technischer Abbruch ohne Teilserienurteil.

## Daten- und Beobachterplanung

Die neuen Grenzübergangsfälle enthalten keine langen Erhaltungszeugen. Für die
Mechanismenbelege wird deshalb zusätzlich der unveränderte neutrale frühere
44-/32-Frame-Kostentest als Größenuntergrenze berücksichtigt. Keine alten
Forschungsresultate oder Quellen werden verwendet. Die jeweils größere lineare
Projektion der neutralen Fälle ergibt pro Geschichte:

| Größe | Lineare Planung | Grenze |
|---|---:|---:|
| gzip_bytes | 298624 | 524288 |
| encoded_bytes | 1375424 | 4194304 |
| dictionary | 1307456 | 4194304 |
| nodes | 31680 | 65536 |
| edges | 120856 | 262144 |
| indices | 10217 | 65536 |

Beobachterheap linear 4551130 Bytes; Mechanismenbelege
165344 Bytes. Beide zählen zum gemeinsamen Jobpeak.
14 produktive Collections bleiben unverändert; Negativtestarchive haben eine
zusätzliche Originalsequenz (15), damit manipulierte Daten nicht schon wegen
einer unreferenzierten Sequenz abgewiesen werden. Produktive Grenze 16.
Die Recordgrenze 256 KiB bleibt pro Einfügung geprüft.

Archive insgesamt linear 9555968 Bytes, Grenze 32 MiB;
32 × individuelles gzip-Limit ergeben höchstens 16 MiB. Kompakte Quellen je
höchstens 32 KiB, 32 Quellen somit höchstens 1 MiB innerhalb der 2-MiB-Gesamtgrenze.
Forschungsquellen des Namensraums v2 sind noch nicht erzeugt.

Vollständige Herkunftsdaten verbleiben in begrenzten Archivsequenzen. Nur eine
Geschichte mit ihrem Codecstore ist gleichzeitig aktiv; die kleinen vollständigen
Statistikzeilen aller Geschichten verbleiben bis zur Gesamtauswertung im Worker.
Vorbereitungsdaten, Quellen, Capture-Anker, Fallzusammenfassungen und Abschluss
werden mitgezählt. Der absichtliche Administrationsfüllbestand eines Negativtests
bleibt als Vorbereitungsbeleg erhalten; er ist keine erlaubte Budgetüberschreitung
im späteren Forschungslauf.

## Unsicherheit und Fehlerabschluss

Es gibt keinen neuen Vollgrößenbeleg. Lange Feedback-/Erhaltungsketten,
Kompression, Python-Objektwachstum und Spitzen beim Strukturvergleich können
nicht aus 80 Frames garantiert werden. Alle ursprünglichen harten Grenzen gelten.
Bei Fehlern bleibt die erste Ursache im reservierten Terminalslot, auch wenn
das normale Schreibbudget erschöpft ist. Quittung nur nach vollständiger
Archivprüfung und Cleanup. Kein Retry, Resume oder nachträgliche Anerkennung
des alten Forschungsarchivs.
