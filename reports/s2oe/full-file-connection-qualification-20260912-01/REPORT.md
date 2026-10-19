# Dateibetrieb: Vorabstopp vor Qualifikation

Auftrag `DATEILERNBETRIEB-LAENGERE-SITZUNG`.
Bezugscommit `537109994cf777f8d36cda617aafe12226806c25` plus Arbeitsbaum.
**PRECONDITION_BLOCKED, null Testaufrufe.** Keine reale Datei verarbeitet.
Keine neue Qualifikation behauptet; die 13 Prüfgruppen sind nur vorbereitet.

## Vorbereiteter Code

Eigene Modusversion `s2oe.full-file-sampled.v1`: 20 Formationen,
Auswahl 0; 1,4; …; 26,6 s, ein Durchlauf, unveränderte Runtimezeit.
Decoderdeckel nur in diesem Modus: 1.024 Video-, 2.048 Audioframes,
4.096 Pakete. Die historischen Deckel bleiben im alten Modus wirksam.

Der vorhandene Worker-RPC führt Auswahl und EOF-Drain. Beim Drain werden
Frames validiert und verworfen, nicht zu zusätzlichen RGB-Ausgaben oder
Formationen. Sitzung und Player erhalten DRAINING, manifestabhängige
Abschlussprüfung, EOF-Belege sowie getrennte Medien-/Runtimeanzeige.
Die aktuelle Transaktionsanzeige zeigt Aktionen und Generationsbezug ohne
Wiedererkennungsbehauptung. Native Memoryregeln bleiben unverändert.

Neue Profil-/Bilanzdatei: `tools/_s2oe_full_file.py`.
Geänderte bestehende Anschlüsse: Medienbindung, Decoder, Decoderworker,
Mediensitzung, Medienverifikator, Player und dessen HTML.
Alle aktuellen Quellenhashes in `inventory.json`; Inventardigest:
`a5652cbb357d0ab95bf407da11483fd1f875e7abfba1a16a231057889a212a10`.
Der vorbereitete Aufruf ist `reports/qualify_full_file_once.py`.

## Vollständige Vorrechnung

Alle Fortschritte 0…20 und beide Abschlussalternativen wurden mit der
vorhandenen synthetischen Beleggrammatik und maximalen nativen Einzelgrößen
rein administrativ bilanziert. Keine Memorygeschichte nachgerechnet.
Die Sitzungstabellen sind in `preflight.json` vollständig erhalten.

| Gemeinsame Qualifikationsbindung | Byte | Grenze |
| --- | ---: | ---: |
| Metadaten | **215.530** | **131.072** |
| Quellen | 243.809 | 327.680 |
| Verifikation | 262.144 | 262.144 |
| NJ | 20.480 | 22.528 |
| Formationen | 30.720 | 30.720 |
| Generationen | 30.720 | 30.720 |
| Gemeinsame Zusatzhülle | 325.729 | 393.216 |
| Gesamt | 3.539.531 | 4.194.304 |

Metadatenrechnung: 45.458 vollständiger neutraler Erfolgsabschluss +
35.227 separater Ein-Schritt-Fehlerabschluss - 6.340 einmalig gezählte
gemeinsame Metadatenreferenzen + 10.113 separate neutrale Quellenbindung +
131.072 vollständige lokale Datei-/Abschlussreserven = **215.530 Byte**.
Überschreitung: **84.458 Byte**. Die beiden neutralen Fixtures sind zwei
tatsächlich vorgesehene Prüfbelege; innerhalb jeder Sitzung bleiben Erfolg
und Fehler Alternativen, nicht addierte Abschlüsse.

Die lokalen Reserven stehen einzeln in `preregistration.json`. Sie enthalten
auch die spätere Quellen-/Settings-/Budgetbindung. Ein günstigerer bisheriger
Istbeleg wurde nicht zur neuen Obergrenze erklärt. Die modellierte einzelne
20er-Erfolgshülle erreicht 3.353.075 Byte; das ist noch keine vollständige
reale Laufzulassung einschließlich der fehlenden Qualifikation.

## Noch nicht erreichte Prüfdeckung

13 vorbereitete Gruppen: Auswahl/Zeiten, Frameauswahl, Modustrennung,
Video-/Audio- und Paketgrenzen, frühes EOF, Drain ohne Konversion,
Worker-Drain-Protokoll, Abbruch beim Drain, alle Hüllen, native 20er-Sitzung,
Primärfehler nach Formation sowie Player-Stopp in DRAINING.
Keine dieser Gruppen wurde ausgeführt. Keine echten OS-/Codec-Voll-Datei-
Eigenschaften aus den vorbereiteten neutralen Fixtures ableiten.

Die Codefassung ist unqualifiziert; eine endgültige Laufbindung wurde nicht
ausgegeben. Nächste notwendige Korrekturrichtung ist eine gemeinsam abgeleitete,
nicht mehrfach abgelegte administrative Abschlussbindung innerhalb der Grenzen,
nicht eine weitere Decoder- oder Memoryänderung. Keine Grenzerhöhung vorgenommen.
Historische Belege bleiben erhalten; aktuelle Codehashes ersetzen keine alte
Zulassung. Gates False; kein Hauptlauf, keine Rezeptoren oder Feld-/Memoryaufrufe.
