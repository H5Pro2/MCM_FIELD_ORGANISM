# V8: externe neutrale Prozessbegrenzung, 20.09.2026

**Die drei beauftragten Fachfaelle sind belegt.** Die aktive experimentelle Grenze betraegt 640 MiB privaten Commit pro Zielprozess; 96 MiB Working Set sind ausschliesslich eine Warnschwelle. Die Vorimport-Zulassung wurde im Eltern- und Kindprozess sowie am Ende aus dem Windows Job Object zurueckgelesen. Produktlogik, realer Starter, Artefaktvertrag und alle 138 Pruefpflichten bleiben unveraendert. Keine unabhaengige V8-Abnahme oder reale Hauptlaufbindung.

## Versuchsfolge und erhaltene Fehlversuche

Zuerst wurden drei Faelle im [urspruenglichen Plan](../v8-process-limit-20260920/plan.json) festgelegt. Die isolierte reale Allokationsgegenprobe bestand. Die beiden Produktfaelle scheiterten nach erfolgreicher Limitzulassung beim Import: `-I` blendete die vorhandene NumPy-Installation im User-Site-Verzeichnis aus (`ModuleNotFoundError`). Kein V8-Eintritt, keine Quellenarbeit, kein Produktabschluss. Die Dateien wurden nicht ueberschrieben; der externe Status lautet `EXTERNAL_ABORT_NO_PRODUCT_SUCCESS`.

[Dokumentierte Korrektur](../v8-process-limit-20260920/CORRECTION.md): Nur `-I` entfernt, `-S` und die blockierende Vorimport-Zulassung erhalten. Explizites `site.main()` erfolgt weiterhin erst nach dem Limitnachweis. Der [Korrekturplan](plan.json) wiederholt ausschliesslich die beiden zuvor nicht ausgefuehrten Produktfaelle. Die valide Allokationsgegenprobe wurde nicht wiederholt. Insgesamt fuenf gestartete Zielprozesse: drei valide Fachnachweise und zwei erhaltene Importfehlversuche. Keine Wiederholung der drei frueheren reinen Prozessspeichermessungen.

## Begrenzungsrahmen

1. Elternprozess erzeugt fuer jeden Fall ein eigenes Job Object, setzt `ProcessMemoryLimit=671088640` und die Flags `0x2100` (Prozess-Commitgrenze und Kill-on-job-close). Ein Working-Set-Limit wird nicht gesetzt.
2. Kind startet mit `-S`: keine automatische Site-Initialisierung. Es laedt nur den gehashten Bootstrap mit Standardbibliothek/Messhelfern, bestaetigt fehlende Produkt-/NumPy-Module und blockiert auf der Eingabepipe.
3. Elternprozess ordnet das Kind dem Job zu und prueft per `IsProcessInJob` und `QueryInformationJobObject` Mitgliedschaft, exakte Flags und Grenze. Nur dann sendet er `admit`. Bei Fehlern wird ein bereits gestartetes Kind beendet; kein Import wird freigegeben.
4. Das Kind oeffnet den benannten Job nur zur Abfrage, prueft Mitgliedschaft und Grenze nochmals und schliesst den Abfragehandle. Erst danach folgen `site.main()` und Produkt-/NumPy-Importe. Der Elternprozess behaelt den Jobhandle bis zum Ende.
5. Vor Prozessende werden aktive Grenze und Hoechststaende nochmals ausgelesen. Der Beobachter schreibt ausschliesslich eigene Mess-/Prozessbelege und erzeugt bei Abbruch keine stellvertretenden Produktabschluesse.

Die API begrenzt committed memory pro Prozess; Job- und Prozessgrenzen sind unterschiedliche Konten. Kill-on-job-close beendet zugeordnete Prozesse beim Schliessen des letzten Jobhandles. [Microsoft: Prozess-/Jobgrenzen](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information), [Job-Objekte](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects). Gezielte Fehlerproben jeder einzelnen Verwaltungs-API wurden nicht ausgefuehrt; deren verweigernder Kontrollpfad ist im Rahmen sichtbar. Der Bootstrap ist kein Schutz vor einem administrativen Eingriff in den Host.

## Durchsetzung und Fehlerabschluss

| Fachfall | PID | Ergebnis | OS-Working-Set-Peak MiB | OS-privater-Commit-Peak MiB |
|---|---:|---|---:|---:|
| 58-Endpunkt-Erfolg | 3248 | CLOSED_NEUTRAL_VERIFIED | 67.438 | 442.449 |
| Reale Allokationsablehnung | 18748 | REAL_ALLOCATION_REJECTED | 18.098 | 636.621 |
| Injiziertes MemoryError | 17728 | NOT_EVALUABLE | 67.820 | 442.352 |

**Reale Allokation:** Windows `VirtualAlloc(MEM_RESERVE|MEM_COMMIT)` konnte insgesamt **654311424 Byte (624 MiB)** in 16-MiB-Bloecken zusagen. Die naechste Anforderung von **16777216 Byte** wurde tatsaechlich mit NULL und Windowsfehler **1455** abgewiesen. Zu diesem Zeitpunkt: privater Commit **666845184 Byte**; plus neue Anforderung oberhalb der aktiven 671088640-Byte-Grenze. Gleichzeitig standen systemweit **16715546624 Byte** Commit zur Verfuegung, gemessen mit `GetPerformanceInfo` (CommitLimit minus CommitTotal, mal PageSize). Kein kuenstlich geworfener Fehler. [Allokationsbeleg](../v8-process-limit-20260920/allocation/allocation-rejection.json).

Die zugesagten Seiten wurden nicht beschrieben. Daher prueft dieser Fall Commitdurchsetzung, keinen 624-MiB-Bedarf an residentem RAM. Die Speicherbloecke wurden nach der Ablehnung freigegeben, bevor der Beleg geschrieben wurde. Der Fall hat keinen Produktcode geladen und beansprucht keinen V8-Fehlerabschluss. Windows zaehlt zugesagte Seiten auch vor ihrer physischen Nutzung. [Microsoft: Performance-Zaehlung](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-performance_information).

**Erfolg unter Grenze:** 58 Versuche, 58 Erfolge, Hash/Rezeptor/NJ jeweils 58; sechs Owner geschlossen, beide Gates=false. Record und separate Verifikation hashgebunden, Auswertung erlaubt, keine fehlenden dauerhaften Belege. Tatsaechliche Produktbilanz einschliesslich Code: **1011807 Byte**.

**Injiziertes MemoryError:** Der Supplier wirft im 58. Versuch explizit `MemoryError`. 57 erfolgreiche Materialisierungen, Hash/Rezeptor/NJ jeweils 57, partieller Quellenabschluss, sechs Owner geschlossen, beide Gates=false. Primaerfehler bleibt `MemoryError`, Verifikation des Fehlerpraefixes `VERIFIED_FAILURE`, Ergebnis `NOT_EVALUABLE`, Auswertung gesperrt. Keine fehlenden dauerhaften Belege. Tatsaechliche Produktbilanz einschliesslich Code: **1007665 Byte**. Dieser Fall ist **keine echte Speichererschoepfung**.

Alle vorhandenen Ergebnisdateien sowie Eingaben wurden erneut per Groesse/SHA256 und Gesamtsumme kontrolliert. Beide Produktbilanzen sind vollstaendig und innerhalb aller unveraenderten Artefaktgrenzen. [Zusaetzliche Abschlusspruefung](final-checks.json). Der Prozess-Peak liegt in allen drei gueltigen Faellen unter der Prozessgrenze. `PeakJobMemoryUsed` wird separat roh ausgewiesen und kann hoeher sein; eine 640-MiB-Gesamtgrenze fuer das Jobkonto wurde nicht gesetzt.

## Beobachter und Abtastung

Wiederverwendet wird die native Speicherabfrage aus dem unveraenderten bisherigen `measure.py`. GetProcessMemoryInfo liefert Working Set, privaten Commit und kumulative OS-Hoechststaende. Abtastziel 10 ms; rohe Zeitstempel bleiben erhalten. OS-Peaks werden bis zum letzten Snapshot des noch lebenden Kindes angegeben. Nicht abgetastete Zwischenpeaks und die Zeit nach diesem Snapshot werden nicht als gemessen behauptet. Beobachterwerte sind getrennt und werden nicht vom Zielwert subtrahiert.

| Fall | Abgetastetes Ziel WS / Commit MiB | Beobachter WS / Commit MiB | Max. Sample-Abstand ms | WS-Warnsamples |
|---|---|---|---:|---:|
| success | 66.891 / 441.906 | 18.633 / 13.004 | 17.412 | 0 |
| allocation | 18.094 / 636.621 | 18.574 / 13.121 | 11.038 | 0 |
| memoryerror | 67.270 / 442.352 | 18.426 / 12.922 | 17.935 | 0 |

Keine der drei gueltigen Messungen loeste die 96-MiB-Warnung aus. Das tatsaechliche Ausloesen einer Warnung ist damit nicht getestet; die Schwelle hat keine Allokation verweigert und keine Working-Set-Begrenzung gesetzt. Die reale Commitablehnung ist davon unabhaengig belegt.

## Vollstaendiger verwendeter Codebestand

Alle 44 bisherigen Produkt-/Testdateien mit **699053 Byte** bleiben in beiden versionsgebundenen Inventaren enthalten. Dazu kommen jeweils das komplette wiederverwendete `measure.py` und die komplette jeweilige `limit.py` inklusive Offlinepruefung. Keine Dateiteile herausgerechnet und keine Pruefpflicht entfernt. Die fruehere `analyze.py` wird in diesem Auftrag weder importiert noch ausgefuehrt; sie bleibt im historischen Archiv unveraendert vorhanden.

| Ausfuehrungsbindung | Produkt + Tests | Messhelfer | Begrenzungsrahmen inkl. Auswertung | Vollstaendig | Frei bis 720896 |
|---|---:|---:|---:|---:|---:|
| Erste Revision; gueltiger Allokationsfall | 699053 | 10811 | 10999 | 720863 | 33 |
| Korrigierte Revision; beide Produktfaelle | 699053 | 10811 | 10978 | 720842 | 54 |

Die Inventare sind pro ausgefuehrter Werkzeugrevision gebunden. Archivierte Zwischenversionen sind kein gleichzeitig geladener Codebestand; es wird keine einzige identische Werkzeugversion fuer alle drei Fachnachweise behauptet. Die Korrektur aendert die Startoption und die Liste der zu wiederholenden Faelle, nicht die Jobgrenze, die Allokationsprobe oder die Produktlogik. Aktuelle Inventare: [korrigiert](used-inventory.json), [erste Revision](../v8-process-limit-20260920/used-inventory.json).

| Datei | SHA256 |
|---|---|
| [v8-process-memory-20260920/measure.py](../v8-process-memory-20260920/measure.py) | `6dcbed6abb4d79d107dab55b2809119b4d9f34f4f5ccc942030723bfcd0238e6` |
| [v8-process-limit-20260920/limit.py](../v8-process-limit-20260920/limit.py) | `d72faec9b3573d77617c1f9a11a8c2aea311823c7f552e7c0fdfb18dc1ed649e` |
| [v8-process-limit-corrected-20260920/limit.py](limit.py) | `9c4cb7ebe57dae107b317ffaef45b6522af26d970cd8a6ee2e08d0954d7b5b12` |

Keine zusaetzliche Paketinstallation. Weitere verwendete Module sind Python-Standardbibliothek, insbesondere ctypes, subprocess, runpy und site; die native Jobsteuerung verwendet kernel32. Interpreter, NumPy, Betriebssystem und externe Installationshashes sind im jeweiligen Inventar enthalten. Vorige native DLL-Identitaet: [native-runtime-files.json](../v8-process-memory-20260920/native-runtime-files.json). Die neuen Kindprozesse benutzen denselben Interpreter; deren Startflags stehen in den Bootstrapbelegen. Quellbytevertrag, Commitgrenze und Working-Set-Warnschwelle sind getrennte Konten.

386 Dateien des angenommenen V8-Entwicklungsarchivs und 95 Dateien des bisherigen Speicherberichts unveraendert nachgeprueft. Alle Produkt-/Testquellhashes vor und nach der Arbeit identisch. Keine erneute Gesamtsuite; die neuen externen Faelle und ihre funktionalen Nachbedingungen wurden gezielt geprueft.

## Rohdaten und Nachpruefung

| Fachfall | Zulassung vor Importen | Rohsamples | Ergebnis |
|---|---|---|---|
| Erfolg | [Elternprozess](success/parent-admission.json), [Kind](success/child-admission.json), [Importbeginn](success/before-imports.json) | [samples.jsonl](success/samples.jsonl) | [result.json](success/result.json) |
| Allokation | [Elternprozess](../v8-process-limit-20260920/allocation/parent-admission.json), [Kind](../v8-process-limit-20260920/allocation/child-admission.json) | [samples.jsonl](../v8-process-limit-20260920/allocation/samples.jsonl) | [Ablehnung](../v8-process-limit-20260920/allocation/allocation-rejection.json) |
| MemoryError | [Elternprozess](memoryerror/parent-admission.json), [Kind](memoryerror/child-admission.json), [Importbeginn](memoryerror/before-imports.json) | [samples.jsonl](memoryerror/samples.jsonl) | [result.json](memoryerror/result.json) |

Je Fall liegen ausserdem `bootstrap.json`, `process-exit.json`, `final-native.json`, stdout/stderr und bei Produktfaellen die vollstaendigen Produktartefakte vor. Beide `limit.py analyze`-Aufrufe pruefen ausschliesslich vorhandene Daten und starten keine Prozesse. `prepare` und `observe` sind Startbefehle und verweigern vorhandene Plan-/Startdateien; sie wurden nicht zur stillen Wiederholung verwendet.

## Gewaehrleistet und nicht gewaehrleistet

- Fuer die nachgewiesenen Prozesse: vor Produktimporten aktivierte und zurueckgelesene 640-MiB-Prozess-Commitgrenze; reale verweigerte Commitanforderung im isolierten Fall.
- Fuer den injizierten MemoryError bei weiterhin verfuegbarem Speicher: beobachteter geordneter V8-Fehlerabschluss mit erhaltenem Primaerfehler und gesperrter Auswertung.
- **Nicht gewaehrleistet:** erfolgreicher Record-, Fehler- oder Terminalabschluss bei tatsaechlicher Speichererschoepfung, abruptem Prozessende oder Hostausfall. Die isolierte Allokationsprobe hat nach Freigabe der Bloecke protokolliert; sie beweist keine Produktpublikation unter OOM.
- Bei den beiden unkontrollierten Importabbruechen meldet der Beobachter Exitcode 1 und fehlendes Produktresultat. Er ersetzt keinen Produktabschluss. Ein Beobachter-/Hostausfall kann auch seine eigenen Belege verhindern; aus dem Kill-on-close-Verhalten folgt keine dauerhafte Protokollgarantie.

**Naechster Vorschlag an den Projektleiter:** unabhaengige Abnahme des unveraenderten V8-Pfads zusammen mit diesen begrenzten Durchsetzungsbelegen. Vor einer spaeteren Laufentscheidung ausdruecklich festlegen, dass ein durch Speichergrenze verlorener Produktabschluss als nicht auswertbar gilt. Falls ein dauerhafter externer Abbruchbeleg gefordert wird, diesen als eigenes, kleines Abnahmepaket spezifizieren; er darf keinen erfolgreichen Produktabschluss ersetzen. Kein Hauptlauf und keine reale Quelle freigegeben.
