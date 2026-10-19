# ER1-v2: abgeschlossener E/F-Forschungsvergleich

Workflow 35ed7d72-d2bc-4a38-9376-6a4f15897bfb, 2026-10-18.

## Ergebnis und Aussagegrenze

TERMINAL_COMPLETE: 32/32 Geschichten nach vollständiger unabhängiger Archivprüfung und Cleanup quittiert. Genau 64 Policy-Arme, getrennt 64 Live-Referenzen und 64 Archivrekonstruktionen; keine zusätzlichen Policy-Messungen. Ein einziger Aufruf, kein Retry, Resume, Ersatzlauf oder Tuning. Die Freigabe ist verbraucht.

Einziger Primärvergleich: E−F über alle 511 beobachtbaren Ziele jeder Geschichte, 32 Geschichten gleichgewichtet, insgesamt 16352 Ziele. Mittelwert −45/65408 = −0,0006879892. Das vorgebundene stratifizierte Bootstrapverfahren mit 10000 Ziehungen ergibt das 95%-Intervall [−89/65408; 1/16352] = [−0,0013606898; +0,0000611546]. Ergebnis: INCONCLUSIVE. Das Intervall schließt null ein; ein globaler Vorteil von E ist nicht nachgewiesen. Dies ist auch kein Gleichwertigkeitsnachweis.

E/F-Regeldifferenz, U-Auswahl, Feedback und sämtliche Grenzen blieben gebunden und unverändert. Warme oder erhaltungsbezogene Teilmengen wurden nicht zum Primärnenner gemacht. Die reine Fehlerbilanz und die 32 Paardifferenzen stimmen exakt mit der unabhängigen Statistikreferenz überein.

## Nutzen und Gegenkosten

| Vollständige Zielbilanz E gegenüber F | Ergebnis |
|---|---:|
| Ziele mit kleinerem Fehler bei E | 343 |
| Ziele mit größerem Fehler bei E | 298 |
| Gleicher Fehler | 15711 |
| Summe der Fehlerverminderungen | 85,75 |
| Summe der Fehlererhöhungen | 74,50 |
| Größte lokale Fehlererhöhung | 0,25 |

Die Summen sind Fehlerbeträge, keine zusätzlichen Beobachtungen. Netto beträgt die Fehlerminderung 11,25 über alle 16352 Ziele. Die ungünstigste Geschichte für E ist Nummer 20 mit E−F = 5/1022 (rund +0,00489237). Eine günstige warme Teilmenge ersetzt nicht die vollständige Bilanz: bei warmem E 261 bessere und 111 schlechtere Ziele, bei kaltem E 82 bessere und 187 schlechtere Ziele. Diese Partitionen sind deskriptiv.

## Mechanistische Zeugen

| Ereignisbezogene Diagnose | E erhält Erfahrung | F erhält Erfahrung |
|---|---:|---:|
| Erhaltungsereignisse | 171 | 343 |
| Ereignisbezogene warme Nutzungen | 327 | 320 |
| Ereignisbezogene lokale Gewinne | 141 | 166 |

Diese Ereigniszahlen können sich überlappen und werden weder untereinander noch zum Zielnenner addiert. Sie belegen lokale Mechanismen, keine globale Überlegenheit.

Konkreter E-Zeuge: Geschichte 1, Ursprung [13,14,15,16], letzte Beobachtung 40, ungleicher Block 44, Konkurrenz/Promotion 48 und warme Nutzung an Ziel 51, Offset 0. Vorheriges Live-Feedback [19,35,39]; E-Fehler 0, F-Fehler 0,25. E bewahrt den Ursprung, den F verliert, während E den neueren Ursprung [21,22,23,24] verdrängt.

Konkreter Gegenzeuge: Geschichte 1, F bewahrt [21,22,23,24] über die Konkurrenz bei 48 und nutzt ihn an Ziel 103, Offset 0. Vorheriges Live-Feedback [27,31]; F-Fehler 0, E-Fehler 0,25. Damit ist die Gegenkostenseite verlorener Erfahrung bei E ebenfalls belegt.

Die Archivprüfung rekonstruiert die Policy mit unabhängiger Referenz, prüft vollständige Bestände, Auswahl, Ausgabe und Feedback, rekonstruiert den Observer und gleicht daraus die mechanistischen Zeugen über ARCHIVE_MECHANISMS ab. Die Zeugenrekonstruktion verwendet dieselbe gebundene Zeugenfunktion; eine zweite unabhängig implementierte Zeugenlogik wird nicht behauptet. Der Abschlussabgleich bestätigt zusätzlich die Aggregation aus allen 32 Fallzusammenfassungen. Keine erneute Policy- oder Archivreferenz-Ausführung nach dem Lauf.

## Herkunft und Bindung

Vorstart-SHA256: `0d67e76c14afa1e74a19dd7190857e68a19062abd26fd2af484c85b761a8f2b7`.

Vor Ausführung tatsächlicher Validator erfolgreich, Forschungsziel und Verbrauchsmarker abwesend, authorization.json exklusiv mit ER1_V2_RESEARCH_ONCE und exakt diesem SHA erstellt. Anschließend ausschließlich die Argumentliste aus prestart.json einmal aufgerufen.

Alle 32 Quellen stammen aus MCM-ER1/source/v2 und wurden vor dem ersten Arm unabhängig rekonstruiert, geprüft und versiegelt. Manifest-SHA: `c02123440d8e6e5c47816284329c694703e055f98671ef93f273fd75ba1452da`. START.json und CONSUMED.json belegen den verbrauchten Einmalstart. Alte Quellen und das historische Abbrucharchiv gingen nicht in diesen Versuch ein.

Nach dem Lauf tatsächlicher Bindungsvalidator erneut erfolgreich: 2979 Dateien und 72 gebundene Qualifikationsartefakte unverändert. Alle 135 Dateien aus closure.json sowie sämtliche 32 Quellenhashes geprüft. Die historische v1-Bindung mit 2967 Dateien und 43 Qualifikationsartefakten sowie alle 43 historischen Abbruchbelege bleiben unverändert. Historischer ER1-Lauf bleibt TECHNICAL_ABORT mit verbrauchter Freigabe.

## Gemessene Ressourcen und Abschluss

Laufzeit 4246,9734 s (70,78 Minuten), innerhalb 54000 s Worker- und 57600 s Gesamtgrenze. Gemeinsamer harter Windows-Job mit Supervisor und einem geerbten Worker: Peak 432316416 Bytes (412,29 MiB), Grenze 536870912 Bytes (512 MiB). Prozesspeak 332869632 Bytes. Diese Messung gilt für diese konkrete Serie, nicht als allgemeine Wachstumsgarantie.

| Archivgröße, maximal pro Geschichte | Messung | Grenze |
|---|---:|---:|
| gzip | 180593 | 524288 |
| encoded | 1055121 | 4194304 |
| dictionary | 1000786 | 4194304 |
| nodes | 14678 | 65536 |
| edges | 134010 | 262144 |
| indices | 10292 | 65536 |
| collections | 14 | 16 |
| record | 16845 | 262144 |

Archive zusammen 5485911 Bytes; Quellen zusammen 238048 Bytes. Beobachterheap maximal 4947590 Bytes, Mechanismenbelege 64087 Bytes. Die gemessene Gesamtzeit liegt über der linearen Kurzfall-Hochrechnung (1929,2 s), aber unter dem vorsichtigen Planungsansatz (16034 s). Worker-Inventur 2310,75 s und Supervisor-Inventur 2664,02 s überlappen und dürfen nicht addiert werden. Keine getrennte neue Vergleichsmessung im Forschungslauf.

Worker beendet (Exitcode 0), Armcleanup und Dateicleanup CONFIRMED, keine Partialdateien, keine erste oder nachfolgende Fehlerursache. Maßgeblich ist TERMINAL_COMPLETE samt Prüfbelegen, nicht allein der Prozess-Exitcode.

## Belege und Anschlussvorschlag

- terminal.json: autoritativer Endstatus, Zeit, Jobpeak, Cleanup, Quittungen.
- result.json und worker.json: vollständiger fachlich-technischer Abschluss.
- statistics.json und statistics-reference.json: Primärvergleich, Kosten, Zeugen und unabhängige Statistik.
- case-01 bis case-32: Capture-Anker, Archive und Fallzusammenfassungen.
- sources-manifest.json: 32 vor dem ersten Arm versiegelte Quellen.
- closure.json: ursprünglicher unveränderter Laufabschluss.
- verification.json: nachträglicher reiner Hash-/Belegabgleich ohne erneute Forschungsausführung.
- delivery-closure.json: ergänzende Lieferung einschließlich dieses Berichts, ersetzt closure.json nicht.

Keine verbleibenden technischen Hindernisse. Fachlicher Anschlussvorschlag: Der Projektleiter ordnet die vorhandenen beidseitigen Zeugen und die vollständige Kostenbilanz lesend ein und entscheidet, ob daraus eine neue falsifizierbare Gegenprognose folgt. Aus INCONCLUSIVE folgt keine automatische Wiederholung oder Optimierung. Keine weitere Ausführung ist aus diesem Abschluss freigegeben.
