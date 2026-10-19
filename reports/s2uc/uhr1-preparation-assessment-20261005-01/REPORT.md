# UHR1 Implementierung und neutrale Qualifikation abgeschlossen

Stand 2026-10-05. Status **PASS_PREPARATION_NO_RESEARCH**.
Der fachlich abgenommene UHR1-Vertrag ist umgesetzt. Genau ein neutraler
Größenablauf ist COMPLETE; die Qualifikation und unabhängige Archivprüfung
sind PASS. Keine Forschungsquelle erzeugt oder gesichtet, kein Forschungsarm
aufgerufen, keine operative Forschungsautorisierung angelegt. Dieser Abschluss
ist kein Nachweis eines U- oder H-Vorteils.

## Umsetzung und unveränderte Verfahren

Neue Dateien:

- `tools/_s2uc_uhr1_sources.py`: gesperrter Forschungszugang, neue SHA-Streams,
  unabhängige Rezeptprüfung, vollständige Quellenversiegelung und erneute Hashprüfung.
- `tools/_s2uc_uhr1_stats.py`: unveränderte rationale UH1-Aggregation und
  geschichtete Bootstrapmethode; UHR1-Namensraum und vorregistrierte neue Urteile.
- `tools/s2uc_uhr1.py`: Vorbereitung, harte Windows-Job-Grenze, exklusiver
  Einmalstart, neutraler Größenablauf, Paket- und Vorstartbindung.
- `tools/_s2uc_uhr1_archive.py`: unabhängige Dekodierung und Auswertungsprüfung
  ohne Policy-Aufruf oder Quellenerzeugung.
- `tests/test_s2uc_uhr1.py`: N1–N7 und G1–G7.

Alle **150/150 geerbten UH1-Dateihashes unverändert**.
U/H, Referenzen, Replaypfad und laufwirksame Abhängigkeiten wurden nicht editiert.
Neue Codebindung: 159 Dateien einschließlich unverändertem Bestand.
H behält Phasenwissen und zwei Schlüssel-/Mittelwertslots, U seine reguläre
begrenzte Spurverwaltung. Unterschiedliche Speicher und Heapmessgrenzen bleiben
bestehen; keine Ressourcenangleichung oder zusätzliche Variante.

## Prüfungen und Ergebnisse

Die formale Qualifikation hat **14/14 Prüfgruppen** bestanden, darin zusätzlich
**11/11 U-Untertests**. Entwicklungsprüfungen davor waren fokussierte neutrale
Prüfungen, kein weiterer vollständiger Größenablauf.

| ID | Inhalt | Ergebnis |
| --- | --- | --- |
| N1 | Eingänge, Indexfolge, Bitunterschiede, +0/−0, Zugriffssperre | PASS |
| N2 | Erstaufnahme, bekannte Hinweise, eingefrorene Ausgabe vor Feedback | PASS |
| N3 | Zwei Slots, dritter Hinweis, Verdrängung und keine Wiederbelebung | PASS |
| N4 | Rundung, Tickets, erkannte U/H-Referenzkorruption | PASS |
| N5 | Zählergrenzen, Teilblockende, Cleanup und injizierte Schreib-/Allokationsfehler | PASS |
| N6 | Elf U-Untertests, rationale Statistik, Schichtung, vollständige Zielreihen | PASS |
| N7 | Eigenheap, Exportgrenzen, Startfehler, Crash, Timeout, Abbruch, harte Speicherablehnung, Bindungen | PASS |
| G1 | Forschungszugriffe vor jeder Forschungs-Hashziehung abgewiesen | PASS |
| G2 | Rejection-Grenze L−1/L, n=1, 4.096-Rohziehungsgrenze | PASS |
| G3 | Zwei unabhängige Generatoren auf neutralem Namensraum; D-Quoten, Orientierung, unselektierte N-Tabelle | PASS |
| G4 | 64 Quellen und Manifest, erneute Hashprüfung, Manipulation terminal | PASS |
| G5 | Beide exakten Nullränder ohne Richtungsnachweis, fehlerhafte Paarzuordnung | PASS |
| G6 | Alle 64 Quellen versiegelt und vorhanden vor dem ersten Policy-Aufruf | PASS |
| G7 | Verlustfreier LZMA-/gzip-Roundtrip; Archivkorruption abgewiesen | PASS |

N7-Negativkontrollen endeten erwartungsgemäß NOT_EVALUABLE ohne lebenden Worker.
Der absichtliche 600-MiB-Allokationsversuch wurde abgewiesen; ein dabei erhöhter
Windows-Roh-Peak wurde nicht als bestandener Ressourcenlauf ausgegeben.
Vorhandene Zielordner wurden separat abgewiesen und nicht überschrieben.
N1–N7/G1–G7 nutzen ausschließlich Handwerte, feste neutrale Muster oder
MCM-UHR1/neutral/v1. Generator-/Manifesttests führen keinen 128-Armlauf aus.

## Genau ein neutraler Größenablauf

Fester Achtblockplan gemäß Vertrag, 64 × 1.024 Frames, 128 frische U/H-Armläufe.
65.536 Quellframes, 131.072 Armverarbeitungen und 131.072 unabhängige
Referenzfortschritte. Je Arm 32.704 beobachtete Ziele, davon 16.384 Q-Ziele.
Terminaler Status COMPLETE, Worker Exitcode 0, Worker beendet, kein Resume.
Neutraler Ergebnisstatus NEUTRAL_TECHNICAL_ONLY; keine Nutzeninterpretation.

| Ressource | Beobachtet | Grenze |
| --- | ---: | ---: |
| Workerzeit | 481.353942 s | 3.540 s |
| Supervisorzeit | 482.526054 s | 3.600 s |
| Gemeinsamer privater Job-Peak | 130842624 Byte | 536870912 Byte |
| U-Zusatzheap | 5263 Byte | 16384 Byte |
| H-Eigenheap | 3991 Byte | 32768 Byte |
| H konservative Numerik | 3928 Byte | 4096 Byte |
| U Receipt / UTF-8-Obergrenze | 751 / 1502 Byte | 16384 / 32768 Byte |
| Quellen gesamt | 391936 Byte | 2097152 Byte |
| Fallarchive gesamt | 14242407 Byte | 33554432 Byte |
| Größtes Fallarchiv gzip / expandiert | 226504 / 1677623 Byte | 524288 / 4194304 Byte |
| Verwaltung | 168565 Byte | 2097152 Byte |
| Terminaler Abschluss | 16081 Byte | 1048576 Byte |
| Export plus konservativ 8 MiB Vorbereitung | 23207597 Byte | 67108864 Byte |

U-Bank 416 Byte, H-Bank 3520 Byte; Ausgabeslots U/H 2/1. Konservative
Original-/Kombinationsbelegung U 16/18 unter 18/20. H geliehener Eingangsframe
384 Rohbytes / 1584 Objektbytes, Receipts 0. Beobachter- und Referenzspeicher
sind extern zu den Armen, aber innerhalb des gemeinsamen Prozesslimits.
Deaktivierte Rohframe-Traces mit Wert 0 bedeuten keine Nullbelegung.
Fehlerpfad- und Dritthinweismessungen stehen zusätzlich in den N5-/N7-Belegen.

## Archivrekonstruktion und Bindungen

133 Dateien des Größenablaufs hash- und längengeprüft.
65.536 H-Bankzustände aus XOR/zlib-Deltas dekodiert; 32.704 H-Ausgaben aus
vorherigen eingefrorenen Zuständen unabhängig bewertet. 32.704 U-Ausgaben
anhand ihrer archivierten Original-/Persistenzzuordnung unabhängig bewertet.
Vollständige U-Ereignisse, Prognosen, Fehler und H-Zustände liegen im Archiv.
Primärintervall, alle 30 Sekundärintervalle, Interaktion, 512 Diagnosezeilen,
Gewinne/Schäden, Maximalpositionen und kumulierte Verläufe unabhängig nachgerechnet.
Diese Prüfung wiederholt keine Policies.

Das gebundene LZMA-Paket enthält 174 Qualifikationsdateien.
Jede Datei wurde daraus bytegenau rekonstruiert, einschließlich deterministischer
Wiederherstellung aller gzip-Fallarchive. Paketgröße 6174451 Byte.
Kanonische operative Vorbereitung einschließlich zukünftiger Autorisierungsbytes:
**8212164 Byte**, unter 8.388.608 Byte. Die losen Qualifikationsarchive sind
Auditbelege; der spätere Starter lädt das gebundene kanonische Vorbereitungspaket.
Der reale Forschungsquellen- und Ergebnisexport wird später zusätzlich belastet.

Bootstrapmatrix: 320.000 Byte, 10.000 Zeilen, 16+16 orientierungsgeschichtete
Paarindices. Produktion und unabhängige Indexberechnung stimmen überein.
SHA256: `f3fe9e2c6159eed9d34b16cf44b5c158226fd3e77176fed9f3afbc659842551a`.

Codebindung SHA256: `b595f719d256cefbeb92f419e8ee5b59f884d32a31e86bf1b713b15b4cd0bfb1`.

**Vorstart-SHA256:** `91a770a4b5ba5e442807abc50bd458c194e57c6c8cebfc135102bbca304c6355`.

Der abschließende Aufruf `C:/Python314/python.exe -m tools.s2uc_uhr1 check`
lieferte PASS_UHR1_PRESTART_NO_RESEARCH. Alle gebundenen Dateien und Runtimewerte
stimmen; Forschungszielordner und operative Autorisierungsdatei fehlen weiterhin.

[Vorstartbindung](../../../docs/S2UC_UHR1_V1_20261005_VORSTARTBINDUNG.json),
[Codebindung](../../../docs/S2UC_UHR1_V1_20261005_CODEBINDUNG.json),
[gebundener späterer Aufruf](../../../docs/S2UC_UHR1_V1_20261005_START.md),
[ausführliche Prüfbilanz](verification.json),
[neutrale Qualifikation](../uhr1-neutral-20261005-01/closure.json),
[Archivprüfung](../uhr1-neutral-20261005-01/archive-verification.json).

## Fachlicher Anschluss

Empfehlung an den Projektleiter: dieses abgeschlossene Umsetzungspaket anhand
der Bindungen abnehmen und danach die separate Entscheidung über genau einen
UHR1-Forschungsversuch treffen. Eine etwaige Beauftragung muss ausdrücklich den
oben genannten Vorstart-SHA256 und den gebundenen Aufruf referenzieren.
Kein erneuter neutraler Größenablauf ist erforderlich oder aus diesem Abschluss
freigegeben. UHR1-Ergebnisse bleiben später strikt von UH1 getrennt; die Aussage
betrifft ausschließlich neue Folgen derselben Aufgabenfamilie.
