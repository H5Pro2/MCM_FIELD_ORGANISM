# UH1 Implementierung und neutrale Qualifikation

2026-10-05. Status **NEUTRAL_QUALIFIED_PENDING_SEPARATE_RESEARCH_AUTHORIZATION**.
Genau U/H implementiert; U unverändert, H mit zwei begrenzten Hinweisslots.
N1–N7 bestanden. Genau ein vollständiger neutraler Größenablauf COMPLETE.
Keine archivierte Forschungsquelle durch U/H abgespielt, keine Forschungsquelle
neu erzeugt, keine operative Forschungsautorisierung und kein Forschungszielordner.
HX1 bleibt abgenommen; seine Einmalfreigabe bleibt verbraucht.

## Umsetzung

Neue Dateien: `tools/_s2uc_uh1_h.py`, `_s2uc_uh1_reference.py`,
`_s2uc_uh1_sources.py`, `_s2uc_uh1_engine.py`, `_s2uc_uh1_stats.py`,
`tools/s2uc_uh1.py` und `tests/test_s2uc_uh1.py`.
Alle 139 ursprünglich gebundenen HX1-Dateien sind unverändert.

H besitzt eine 3.520-Byte-Bank mit zwei vollständigen Schlüsseln, zwei Mittelwerten,
Zählern/Stempeln, Zweiframe-Puffer, eigener Ausgabe und Prognosesteuerung.
Kein Tabellenwachstum, keine Beobachterhistorie. Schlüsselkopien erfolgen
byteweise innerhalb der festen Bank; keine zusätzliche temporäre 768-Byte-Kopie.
Die Referenz verwendet eigene Objekte, eigene Schlüssel-/Slotentscheidungen und
rationale Einzeloperationen mit expliziter binary64-Rundung. Der externe Beobachter
prüft Zustand und Fehler pro Frame. H-Deltas werden verlustfrei kodiert, separat
dekodiert und mit der unabhängig erzeugten Referenz verglichen.

U nutzt den unveränderten HX1-Replay mit dessen unabhängiger U-Referenz und dem
unveränderten Profil `4309cfc91eb99fc2a999fdac99c5a7f1807ee654996e019ec0d94e3900bcbd4b`.
Die freigegebene Profilkorrektur ist übernommen. Alter Vertrag und alte
Spezifikationsbindung bleiben unter `docs/archiv/uh1-profil-vor-korrektur-20261005`.

Der Forschungsloader validiert ausschließlich die 64 gebundenen Archivdateien.
Ohne expliziten Zulassungsparameter ist Laden für Replay gesperrt. Der öffentliche
Starter prüft zusätzlich die exakte neue Einmalautorisierung und Vorstartbindung.
Neutrale Quellen stammen ausschließlich aus der festen neutralen Blockliste.

## Prüfungen

| Prüfung | Ergebnis und Belegumfang |
| --- | --- |
| N1 | PASS: Eingangsform, Index, NaN/Inf, Einbitänderung, +0/−0, Forschungsgate und Quellenhashes |
| N2 | PASS: unbekannt zunächst Persistenz, Aufnahme erst nach Ziel, bekannte Ausgabe vor Update eingefroren |
| N3 | PASS: a,b,a,c verdrängt b; erneutes b unbekannt und erst bei Feedback aufgenommen |
| N4 | PASS: Rundung gegen unabhängige Referenz, falsche Tickets/Slots und injizierte H-/U-Abweichungen erkannt |
| N5 | PASS: Zählerende 256, Überlauf, Teilabschluss, doppelte Beendigung, Stempelgleichstand, Cleanup bei Schreib-/Allokationsfehlern |
| N6 | PASS: 11 unveränderte U-Untertests; unabhängige Matrix, rationale Mittel/Quantile, positive/negative/Nullgrenzen, vollständige Gewinn-/Schadenspartition |
| N7 | PASS: Dritt-Hinweis-Heap, Exportgrenzen, Code-/Quellenabweichungen, fehlende Autorisierung, bestehender Zielordner, Zeitgrenze, Crash/Abbruch und native Speicherablehnung |

Formale Tests: 7/7 bestanden, zusätzlich 11 U-Untertests. Zehn ergänzende kleine
Fehlerinjektionen über die vier Eingangsphasen bestanden, inklusive vollständiger
Nullung. Vier weitere Randprüfungen bestätigen vertauschte Framefolge, doppelte
Slot-Schlüssel, Überlauf eines bekannten Slotzählers und doppelte Eingangsindices.
Diese kleinen Prüfungen sind keine weiteren vollständigen Größenabläufe.

Alle 320.000 Bytes der 10.000×32-Bootstrapmatrix wurden mit einem getrennten
Indexberechnungspfad verglichen. SHA256 `5a5c86f6e74413f09c553d00a47aa33569bb752fd689c6284559dbd73ffc5b29`.
Nur ein primärer Kontrast D:U−H, nominales 95%-Intervall. Alle 30 ergänzenden
Masken-/Orientierungsbilanzen sowie Interaktion und 512 Diagnosezeilen werden
vollständig rational ausgewertet. Unabhängige Mittel- und Quantilpfade stimmen.
Neutrale Ergebnisurteile sind ausschließlich NEUTRAL_TECHNICAL_ONLY.

## Einziger vollständiger neutraler Größenablauf

64 Geschichten, 128 Armläufe, 65.536 Quellframes, 131.072 Armverarbeitungen und
131.072 Referenzfortschritte. Je Arm 32.704 beobachtete Ziele, davon 16.384 Q.
Alle 65.536 H-Zustände unabhängig geprüft und aus dem Export rekonstruiert.
133 Abschlussdateien hash- und längengeprüft. Worker beendet, Exitcode 0,
Cleanup bestätigt; letzte Prognose 1.025 jeweils rechtszensiert.

U-V0/V1/V2/V3 je neutralem D und N: 108/72/2.008/6.004.
H je neutraler Bedingung: 64 unbekannte und 8.128 bekannte Q-Prognosen.
Diese Zahlen sind technische Vollständigkeitsbelege, kein Forschungsnutzenbefund.

## Ressourcenbilanz

| Größe | Gemessen bzw. konservativ ausgewiesen | Grenze |
| --- | ---: | ---: |
| H feste Bank | 3.520 Byte | numerisch insgesamt 4.096 Byte |
| H konservative Numerik inkl. Scratch | 3.928 Byte | 4.096 Byte |
| H eigener Heap im Größenablauf | 3.991 Byte | 32.768 Byte |
| H eigener Heap bei formalen Fehlerprüfungen | höchstens 5.953 Byte | 32.768 Byte |
| H ergänzende Phasenfehlerprüfungen | höchstens 5.535 Byte | 32.768 Byte |
| H Konstruktion | 3.617 Byte | 32.768 Byte |
| H geliehener aktueller Frame | 384 Rohbytes / 1.584 Objektbytes | höchstens ein Frame |
| H Ausgabe / Receipt | ein Slot / 0 Byte | ein Slot / kein Receipt |
| U Zusatzheap | 5.263 Byte | 16.384 Byte |
| U Bank | 416 Byte | 416 Byte |
| U konservative Original-/kombinierte Belegung | 16 / 18 | 18 / 20 |
| U Ausgaben | zwei Slots | zwei Slots |
| U Receipt / transiente UTF-8-Obergrenze | 751 / 1.502 Byte | 16.384 / 32.768 Byte |
| Gemeinsamer Job-Peak | 132.976.640 Byte | 536.870.912 Byte |
| Workerzeit | 484,547654 s | spätestens 3.540 s ab Supervisorstart |
| Supervisorzeit | 485,471999 s | 3.600 s |
| Größter Fall komprimiert / expandiert | 226.495 / 1.677.606 Byte | 524.288 / 4.194.304 Byte |
| Neutrale Quellen zusammen | 391.936 Byte | 2.097.152 Byte |
| Neutrale Fallarchive zusammen | 14.241.858 Byte | 33.554.432 Byte |
| Neutrale Verwaltung | 159.051 Byte | 2.097.152 Byte |
| Neutraler terminaler Abschluss | 15.952 Byte | 1.048.576 Byte |
| Vollständiger neutraler Export | 14.808.797 Byte | 67.108.864 Byte inkl. Vorbereitung |
| Kanonische Vorbereitung inkl. vorgesehener Autorisierung | 7,803,824 Byte | 8.388.608 Byte |

Der neutrale Supervisor belastete konservativ zusätzlich volle 8 MiB Vorbereitung:
zusammen 23.197.405 Byte unter 64 MiB. Beim späteren Forschungsstart werden die
396.416 Byte unveränderter Archivquellen zusätzlich zur Vorbereitung belastet.
Keine kostenlose Eingangsdateikopie; es werden keine neuen Forschungsquellen exportiert.

U-Grenzstellenmaxima: Basisobjekt 17.151 Byte, Originalobjekte 15.891 Byte,
Originalpayload 5.760 Byte, erreichbarer Systemgraph 20.790 Byte, Ausgabepayload-
Äquivalent 768 Byte. Dies sind Grenzstelleninventare, keine kontinuierlichen Peaks.
H zählt gesamten eigenen Heap, U Zusatzheap: keine Ressourcengleichheit behauptet.

Externe Kosten separat: Eingangsobjekte 458.136 Byte, U-Beobachterbelege maximal
12.164.480 Byte und H-Trace maximal 631.962 Byte je Fall. Kleine unabhängige
H-Referenz-Grenzstellenzählung maximal 7.696 Byte; der im Fallabschluss gespeicherte
Wert 798 Byte ist der Referenzzustand NACH Cleanup, kein laufender Höchststand.
Referenzen/Beobachter sind für Arme unerreichbar und zählen zum gemeinsamen Job.
Rohfelder original_frames_peak/combined_peak=0 bedeuten deaktiviertes Rohframe-
Tracing; maßgeblich sind die genannten konservativen Obergrenzen und Zählungen.

## Offen gelegte Korrekturen

1. Die freigegebene Profilklarstellung korrigiert nur die Beschreibung der
   ursprünglichen HX1-Hashserialisierung; keine Änderung von U oder Profilbytes.
2. Beim ersten Entwicklungsdurchlauf scheiterte N7 am direkten Vergleich von
   Python-Tupeln mit aus JSON gelesenen Listen. Der Test vergleicht nun die
   kanonischen serialisierten Inhalte; gezielte N7-Nachprüfung und formale N1–N7 PASS.
3. Nach dem einzigen Größenablauf wurde ausschließlich die Vorbereitungspackung
   korrigiert: ein gemeinsamer LZMA-Stream in ZIP statt eigener LZMA-Wörterbücher
   je Datei. Größe 6.183.981 Byte. Die originalen gzip-Fallarchive, alle Laufdaten
   und Vertragsparameter bleiben unverändert. Geändert wurden nur `seal` und
   `verify_archive`; sämtliche anderen AST-Knoten sind identisch. Alter Runner
   und Codebindung bleiben unter `docs/archiv/uh1-packaging-20261005` erhalten.
   Gezielte Prüfungen: genaue gzip-Rekonstruktion, Trunkierung, fehlende Datei,
   falscher Hash, Duplikat, übergroßer Eintrag. PASS. Eine anfangs unvollständige
   Testfixture wurde um ihre erforderliche tests.json ergänzt; kein Produktfehler.
   Kein zweiter vollständiger Größenablauf. Vorstartbindung verknüpft ursprüngliche
   Qualifikationsbindung, endgültige Codebindung und Verpackungsnachqualifikation.

## Bindung und noch gesperrter Start

Vorstart-SHA256: `49c8118f34cd4b7e13f0de720d3521e164ac3a35cca761d023ca830fe55becc7`.
Endgültige Codebindung: `be97c28b0c26facd4b22eef3f351b1d07c46d115709260b4eb717a36cd88778e`; 150 Dateien gebunden.
Alle 139 historischen HX1-Dateien unverändert. Vorstartcheck:
`C:/Python314/python.exe -m tools.s2uc_uh1 check` → PASS_UH1_PRESTART_NO_RESEARCH.

Ausführbarer Befehl, ausschließlich NACH neuer separater Einmalbeauftragung:

```powershell
C:/Python314/python.exe -m tools.s2uc_uh1 run --authorization docs/S2UC_UH1_V1_20261005_AUTORISIERUNG.json
```

Arbeitsverzeichnis `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.
Aus der gebundenen Vorlage darf erst nach separater Beauftragung durch alleinige
Statusänderung auf AUTHORIZED_ONCE die operative Datei entstehen. Sie existiert
jetzt nicht. Exklusiver Zielordner `reports/s2uc/uh1-comparison-20261004-01`
existiert ebenfalls nicht. Fehler verbraucht einen gestarteten Versuch; kein Retry.

Nächster Vorschlag an den Projektleiter: technische Abnahme des vorliegenden
Pakets einschließlich offen gelegter Verpackungskorrektur; danach gegebenenfalls
separate Einmalbeauftragung des Vergleichs auf bekannten Quellen. Kein
Leistungsurteil U/H aus dieser neutralen Qualifikation und kein Wiederöffnen von HX1.

Belege: [Prüfbilanz](verification.json), [Verpackungsnachprüfung](packaging-qualification.json),
[Fehlerpfade](supplemental-error-resources.json), [Randprüfungen](supplemental-edge-tests.json),
[Referenzinventar](reference-census.json), [formale Tests](../uh1-neutral-20261005-01/tests.json),
[Qualifikationsabschluss](../uh1-neutral-20261005-01/closure.json),
[neutraler Laufabschluss](../uh1-neutral-20261005-01/integration/closure.json).
