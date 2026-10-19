# UF1 Implementierung und neutrale Qualifikation abgeschlossen

Stand 2026-10-05. Status **PASS_PREPARATION_NO_RESEARCH**.
F und die unabhängige Referenz sind implementiert. N1–N7/G1–G6 bestanden;
genau ein neutraler Größenablauf COMPLETE und unabhängige Archivprüfung PASS.
Keine Forschungsquellen erzeugt oder gesichtet, kein Forschungsversuch und
keine operative Forschungsautorisierung. Kein Leistungsnachweis für U oder F.

## Implementierung und unverändertes U

- `tools/_s2uc_uf1_f.py`: gepackte Zwei-Hinweis-/Zweiwerte-Baseline, exakte
  Bitvergleiche und Zähler, Vorhersage vor Feedback, terminale Domänengrenze.
- `tools/_s2uc_uf1_reference.py`: unabhängiger eigener Objektzustand, eigene
  Schlüssel/Wertlisten und Gewinnerwahl; keine Importe aus der Produktionsbaseline.
- `tools/_s2uc_uf1_engine.py`: unveränderter U-Replayanschluss, U/F-Referenzvergleich,
  Ressourcenmessung und verlustfreie F-Zustandsdeltas.
- `tools/_s2uc_uf1_sources.py`: gesperrter Forschungszugang, UF1-Rezept,
  unabhängiger Generator, vollständige Manifestversiegelung und erneute Hashprüfung.
- `tools/_s2uc_uf1_stats.py`: rationale U−F-Auswertung, UF1-Bootstrapnamespace,
  30 Nebenbilanzen, 704 Diagnosezeilen und 640 armweise Geschichtenmittelwerte.
- `tools/_s2uc_uf1_archive.py`: unabhängige Dekodierung, Ausgabe-, Zähler-,
  Klassen-, Feedbackhistorien- und Statistikprüfung ohne Policy-Aufruf.
- `tools/s2uc_uf1.py`: gebundene Vorbereitung, Qualifikation, Supervisor,
  Paketrekonstruktion und Einmalstart für eine spätere separate Forschungsfreigabe.
- `tests/test_s2uc_uf1.py`: Hand-/Neutralprüfungen und Fehlerkontrollen.

**159/159 Vorgängerdateien sind hashgleich geblieben.** U und seine laufwirksamen
Abhängigkeiten wurden nicht geändert. Die neue operative Codebindung umfasst
160 Dateien: sämtliche geerbten Pythondateien sowie die neuen UF1-
Dateien und aktuellen Eingabebindungen. Historische Matrizen/Versuchspläne sind
keine aktiven UF1-Eingaben; ihre Originaldateien bleiben unverändert und über
die Vorgänger-/Vorregistrierungsbindung nachvollziehbar.

F lernt beobachtete Werte erst nach dem tatsächlichen Ziel. Strikte Mehrheit
liefert den gespeicherten Vektor; Gleichstand oder unbekannter Hinweis liefert
Persistenz. Dritter Wert für einen gehaltenen Hinweis stoppt terminal vor dem
Lernen. Dritter Hinweis wird erst beim Feedback nach ältestem Stempel ersetzt.
Häufigkeiten verdrängter Hinweise kehren nicht zurück. F besitzt Hs Phasenwissen
und ein größeres numerisches Budget; keine Gleichbudgetbehauptung und keine
allgemeine Lernfähigkeit außerhalb der definierten Zweiwerte-Domäne.

## Test-IDs und Ergebnisse

Formale Qualifikation: **18/18 Testmethoden bestanden**, verteilt auf sämtliche
vertraglichen Gruppen N1–N7/G1–G6. Zusätzlich **11/11 U-Untertests** bestanden.
Vorherige fokussierte Entwicklungstests und Nachprüfungen waren ausschließlich
neutral; kein weiterer vollständiger Größenablauf.

| Vertragsgruppe | Testmethoden / Prüfgegenstand | Ergebnis |
| --- | --- | --- |
| N1 | input_and_bits: Dimension, Index, NaN/Inf, Bitunterschiede, +0/−0 bei Hinweisen und Zielen | PASS |
| N2 | freeze_and_feedback: Persistenz vor Erstaufnahme, eingefrorene Ausgabe, 1:1-Gleichstand erst nach Feedback | PASS |
| N3 | majority_changes: a,b,a,b,b sowie umgekehrte Aufnahmereihenfolge, beide Mehrheitswechsel | PASS |
| N4 | hint_eviction: getrennte Hinweise, Ersatz beim Feedback, Stempeltie, keine Altzähler | PASS |
| N5 | third_value_terminal_before_learning: dritter Wert/Ein-Bit-Variante/+0/−0; keine Lernmutation vor Abbruch | PASS |
| N6 | invariants_tickets_end_and_faults: Ziel/Slot/Wert/Grund, Duplikate, Ausgabekorruption, c/t=256, Teilende, Cleanup, Kopier-/Schreibfehler | PASS |
| N7 | full_bank_transients: Vollbelegung, Mehrheits-/Gleichstandspfade, Ersatz, Fehlerheap, getrennte numerische Nutzdatenmessung | PASS |
| G1 | G1a/G1b/G1c: gesperrter Forschungszugriff, Rejection-Grenzen, n=1, 4096-Limit, unabhängige neutrale Rezepte/Quoten | PASS |
| G2 | G2a/G2b: Quellen-/Manifestmanipulation und alle 64 Quellen vor erstem Policy-Aufruf | PASS |
| G3 | statistics/G3b: Intervallrichtungen und Nullränder, Paarzuordnung, Schichtung, vollständige Partitionen und Mittelwerte | PASS |
| G4 | U_and_reference_corruption: elf U-Untertests, injizierte U-/F-Referenzabweichung | PASS |
| G5 | supervisor_and_export/G5b: Exportgrenzen, Start/Crash/Cancel/Timeout, Speicherablehnung, Freigabe-/Codeprüfung, Roundtrip/Korruption | PASS |
| G6 | analytical_vectors: ungeordnete Vektoren, 3:1/1:3, Persistenz innerhalb/außerhalb des Medianintervalls | PASS |

Die Negativkontrollen endeten erwartungsgemäß NOT_EVALUABLE ohne lebenden Worker.
Ein absichtlicher 600-MiB-Allokationsantrag wurde vom Windows-Job abgewiesen;
ein entsprechender Roh-Peak wurde nicht als bestandener Größenablauf bewertet.
Bestehender Zielordner wurde ohne Überschreiben abgewiesen.

## F-Bank, transiente Numerik und Eigenheap getrennt

| Größe | Nachweis | Grenze |
| --- | ---: | ---: |
| Persistente F-Bank | 4304 Byte, fester einziger gespeicherter Bankzustand | 4304 Byte |
| Lebende temporäre numerische Nutzdaten in fokussierten Pfaden | 96 Byte | 408 Byte Scratchreserve |
| Zusätzliche Reserve für skalare C-Aufrufergebnisse | 32 Byte | in Scratch enthalten |
| Beobachtet plus Reserve | 128 Byte | 408 Byte |
| Bank plus beobachtete Transienten und Reserve | 4432 Byte | 5120 Byte |
| Vertragsweites konservatives numerisches Maximum | 4712 Byte | 5120 Byte |
| F-Eigenheap im Größenablauf | 4839 Byte | 32768 Byte |
| F-Eigenheap bei injizierten Schreib-/Kopierfehlern | 6753 Byte | 32768 Byte |
| F-Eigenheap beim dritten Fortsetzungswert | 6257 Byte | 32768 Byte |

Die Numerikmessung ist eine externe Zeilen-/Exception-Inventur der lebenden
Baseline-Stackwerte über 173340 Trace-Ereignisse:
Erstaufnahme, bekannte Werte, Gleichstand, Vollbelegung, Hinweisersatz, Abort und
dritter Wert. Geliehener Eingangsvektor und Bank werden separat gerechnet;
geteilte Objekte nicht mehrfach gezählt. 32 Byte decken zusätzliche skalare
C-Ergebnisse zwischen Trace-Ereignissen konservativ ab. Der vollständige
Größenablauf misst zusätzlich den Python-Eigenheap bei jedem F-Aufruf.
Keine Verwechslung von numerischem Payload, Python-Heap und Prozessspeicher.

Der Quellcode hält nur die feste Bank, vergleicht direkt in ihr und erzeugt
keine vollständigen zusätzlichen Schlüssel-/Vektorkopien als versteckte Historie.
Geliehener aktueller Eingang: 384 Rohbytes / 1584 Objektbytes, kein behaltenes
Inputobjekt nach accept. F-Ausgabeslots 1, Receipts 0. Externe Referenzen und
Archive bleiben für F unerreichbar und zählen zum Prozessbudget.

## Genau ein neutraler Größenablauf und Ressourcen

64 Geschichten × 1024 Frames, 128 frische U/F-Armläufe, 65.536 Quellframes,
131.072 Armverarbeitungen und 131.072 unabhängige Referenzfortschritte. Je Arm
32.704 beobachtete Ziele, davon 16.384 Q-Ziele. Festes Achtblockmuster gemäß
Vertrag; keine Forschungsquellen. Status COMPLETE, Worker beendet, Exitcode 0.
Ergebniskennzeichnung NEUTRAL_TECHNICAL_ONLY, keine Nutzeninterpretation.

| Ressource | Beobachtet | Grenze |
| --- | ---: | ---: |
| Workerzeit | 486.123812 s | 3540 s |
| Supervisorzeit | 487.257743 s | 3600 s |
| Gemeinsamer privater Windows-Job-Peak | 126853120 Byte | 536870912 Byte |
| U-Zusatzheap | 5371 Byte | 16384 Byte |
| Quellen gesamt | 391936 Byte | 2097152 Byte |
| Fallarchive gesamt | 9083531 Byte | 33554432 Byte |
| Größter Fall gzip / expandiert | 147445 / 1647079 Byte | 524288 / 4194304 Byte |
| Verwaltung | 405949 Byte | 2097152 Byte |
| Terminaler Abschluss | 15953 Byte | 1048576 Byte |
| Export plus konservativ volle 8 MiB Vorbereitung | 18285977 Byte | 67108864 Byte |

U-Bank 416 Byte; konservative Original-/Kombinationsbelegung 16/18 unter 18/20,
Ausgabeslots U/F 2/1. U-Receipt 751 Byte / UTF-8-Obergrenze 1502 Byte.
Deaktivierte Rohframe-Traces mit Wert 0 sind kein Nullbelegungsnachweis.
U-Zusatzheap und F-Eigenheap sind unterschiedliche Messgrößen. Referenz-,
Beobachter- und Berichtsobjekte zählen zum gemeinsamen Prozesslimit.

## Unabhängige Archivrekonstruktion und Vorstartbindung

133 Dateien des Größenablaufs längen-/hashgeprüft. **65.536 F-Zustände**
aus XOR/zlib-Deltas einschließlich der initialen Sentinels rekonstruiert.
**32.704 F- und 32.704 U-Ausgaben** unabhängig aus eingefrorenen Zuständen bzw.
Original-/Persistenzzuordnungen bewertet. F-Klassen, Vorzielzähler, ausgewählte
Werteplätze, Belegung, Stempel und erste/letzte Feedbackpositionen nachgerechnet.
Primärintervall, 30 ergänzende Intervalle, Interaktion, 704 Diagnosezeilen,
640 armweise Geschichtenmittelwerte, Gewinne/Schäden, Maximalpositionen und
kumulierte Zielverläufe aus den Archiven unabhängig geprüft. Kein Policy-Replay
und keine Quellenmaterialisierung bei dieser Archivprüfung.

Qualifikationspaket mit 173 Dateien, Größe 2976721 Byte:
Jede Datei unabhängig bytegenau rekonstruiert, einschließlich deterministischer
gzip-Wiederherstellung aus dem LZMA-Paket. Kanonische operative Vorbereitung
inklusive zukünftiger Autorisierungsbytes **4690185 Byte**, unter 8388608 Byte.
Lose Qualifikationsdateien bleiben Auditbelege, keine zusätzlichen versteckten
operativen Eingangspakete. Forschungsquellen und Forschungsexport wären später
zusätzlich zu belasten.

Bootstrapmatrix: 320000 Byte, 10.000 Zeilen mit 16+16 geschichteten
Paarindices, unabhängig gegen UF1-Ziehungsregel geprüft.
SHA256: `4d38373dacffbdc2970d1c50ec061f94f3b1e615cea06e4b23cd465b704eadfb`.

Codebindung SHA256: `32a61bfa36d3cfaa400154c9ad839ea5f3a6fffcb83d5a6404c2508c7b388f06`.

**Vorstart-SHA256:** `1a2c3bcab967eeed4d6fa422693216f8ba2853bac7aaab389ecc54aa606eb6d7`.

Abschließender Aufruf `C:/Python314/python.exe -m tools.s2uc_uf1 check`:
**PASS_UF1_PRESTART_NO_RESEARCH**. Alle gebundenen Dateien und Runtimewerte passen.
Forschungszielordner und operative Autorisierungsdatei wurden nicht angelegt.

[Vorstartbindung](../../../docs/S2UC_UF1_V1_20261005_VORSTARTBINDUNG.json),
[Codebindung](../../../docs/S2UC_UF1_V1_20261005_CODEBINDUNG.json),
[exakter späterer Aufruf](../../../docs/S2UC_UF1_V1_20261005_START.md),
[vollständige Prüfbilanz](verification.json),
[formale Qualifikation](../uf1-neutral-20261005-01/closure.json),
[Archivprüfung](../uf1-neutral-20261005-01/archive-verification.json),
[Numerik- und Heapnachweis](../uf1-neutral-20261005-01/N7-resources.json).

## Fachlicher Anschluss

Empfehlung: Das Umsetzungspaket anhand dieser Belege abnehmen und anschließend
separat über genau einen UF1-Forschungsversuch mit dem genannten Vorstart-SHA256
entscheiden. Kein erneuter neutraler Größenablauf erforderlich oder durch diesen
Abschluss freigegeben. Aufgabenfamilie und U bleiben unverändert; die Ergebnisse
wären später getrennt von UH1/UHR1 zu beurteilen. Die technische Qualifikation
belegt keine allgemeine Lernfähigkeit der begrenzten Häufigkeitsbaseline.
