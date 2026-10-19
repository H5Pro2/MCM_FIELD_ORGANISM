# Fester Detailvergleich: Abschluss

Repository-Bezug: `537109994cf777f8d36cda617aafe12226806c25` plus das
vollständig hashgebundene Arbeitsinventar der Vorregistrierung. Fremde
Änderungen und historische Belege wurden nicht verändert.

## Technischer Nachweis

`fixed-detail-closure-qualification-20260912-01`: genau ein neutraler
Testaufruf, **8/8 bestanden**. Geprüft wurden vollständiger Einmalabschluss,
vorzeitiger Fehlerabschluss, manipulierte Bindung, falsche Framepaarung,
fehlende Belege, Budget, Auswertungssperre sowie reguläre gleiche und
unterschiedliche Ergebnisse. Keine Wiederholung der 16 Adapterprüfungen
oder der historischen 14 Medienanschlussprüfungen. Die neuen Anschluss-
fixtures sind synthetisch; die vorherige native Adapterdeckung bleibt ein
getrennter Nachweis. Vollständiges Log und Quelleninventar stehen in der
[Qualifikationsablage](fixed-detail-closure-qualification-20260912-01/preregistration.json).

Endgültige Hauptbindung SHA-256:
`88e745ade61dbf43cff43ce7badc5642b935e4edb4be144d3dbd13d198afbcb3`.
Die konservative Vorbilanz einschließlich gleichzeitig angesetzter möglicher
Abschlussdateien lag bei 2.571.184 Byte, zusätzlich 24.576 Byte Bindungs- und
Berichtreserve. Keine ausgewiesene Grenzverletzung.

`fixed-detail-comparison-20260912-01`: **RECORDING_COMPLETE**, genau eine
unabhängige read-only Verifikation **EVIDENCE_VALID**, danach einmal getrennt
ausgewertet. Kein Retry. Die lokale, bereits untersuchte MP4 wurde unverändert
wiederverwendet, nicht das ursprüngliche YouTube-Medium:
`C:/Users/TV/Downloads/17138816-uhd_3840_2160_30fps.mp4`, 83.498.438 Byte,
SHA-256 `df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.

Zehn ausgewählte Originalframes liefern zwanzig Ansichten und zwanzig
Rezeptoranalysen. Vier zusätzliche Analysen betreffen ausschließlich die
vorgebundene Informationsverlustkontrolle: insgesamt 6.912 gespeicherte
Rezeptorwerte. Übersicht unverändert aus dem nativen Gesamtframe;
Detailrechteck x=960, y=540, Breite=1920, Höhe=1080. Native Zeitbasis und
30000/1001-Bildrate bleiben getrennt von der Auswahlzeit gebunden.

## Getrennter Befund

Alle zehn Paare besitzen dieselbe belegte Originalherkunft und unterschiedliche
RGB-Payloadhashes. Sie beobachten unterschiedliche räumliche Abdeckungen.
Es wurden keine zusätzlichen L1-Abstände oder zeitlichen Kennzahlen berechnet.
**Ein Detailvorteil ist nicht nachgewiesen.** Die vollständigen Werte sind im
[Gesamtbeleg](fixed-detail-comparison-20260912-01/record.json) erhalten.

K0/K1 haben unterschiedliche Pixelbestände, liefern jedoch sowohl in der
Übersicht als auch im Detail jeweils 288 bitgleiche Rezeptorwerte. Die
576 Gleichheitsprüfungen wurden unabhängig kontrolliert. Dies ist eine
konkrete diagnostische Kollision, kein Stabilitäts- oder allgemeiner
Informationserhaltungsnachweis. Memory und Feld wurden nicht ausgeführt;
Memory-Stabilisierung bleibt NOT_TESTED. Die
[Auswertung](fixed-detail-comparison-20260912-01/evaluation.json) ist
ausdrücklich DESCRIPTIVE_ONLY.

Die Offline-Prüfung bestätigt Formen, Quellen-/Frame-/Raumbindungen,
Vollständigkeit, Ressourcen und Kontrollgleichheiten. Ohne gespeicherte
Roh-RGB-Payloads rekonstruiert sie die Rezeptorrechnung nicht unabhängig;
`numerical_receptor_reconstruction=false` bleibt ausdrücklich erhalten.

## Istbilanz und Abschluss

- Decoder: 140 Pakete, 138 Videoframes, zehn ausgewählte Fenster, ein Durchlauf.
- Container-Lesemenge: 99.889.199 Byte; keine Audioframes oder Audiosamples.
- Worker: Queue 1, gemeinsamer Slot 6.240.000 Byte; Spitzencommit Prozess
  612.188.160 Byte, Job 618.762.240 Byte, jeweils unter 1.073.741.824 Byte.
- Zwanzig Ansichten zurückgegeben, CLOSED_COMPLETE, Worker geschlossen.
  Der gespeicherte Prozess-Exitcode ist **1**, nicht 0; der bestehende
  schließende Workerpfad beendet den Prozess. Der Vollständigkeitsstatus
  bezieht sich auf die gelieferten Ansichten, nicht auf einen Exitcode 0.
- Physische Laufdateien: record 181.676, verification 221, evaluation 1.653,
  balance 245 und zwei Claims je 5 Byte: zusammen **183.805 Byte**.
- Aktive Referenzen: **1.887.142 Byte**. Physische Summe einschließlich
  Referenzen: **2.070.947 Byte**. Mit unverbrauchter voller Bindungs-/
  Berichtreserve 24.576 Byte: **2.095.523 / 4.194.304 Byte**.
- Abschlussmetadaten tatsächlich 2.129 Byte; mit voller Reserve
  **26.705 / 65.536 Byte**. Gesamtbeleg 181.676 / 327.680 Byte.

Die gespeicherte Bilanz setzt für ihre eigene Datei konservativ 4.096 statt
245 Byte an und nennt daher 2.074.798 Byte vor der zusätzlichen Reserve.
Diese Reservebilanz wurde nicht als physischer Istwert umgedeutet. Dieser
Bericht liegt außerhalb der unveränderten Laufablage und wird durch die
genannte Berichtreserve abgedeckt. Gates im Abschluss zuverlässig False;
kein weiterer Medienlauf und keine automatische Folgearbeit.
