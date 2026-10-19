# V8: begrenzte neutrale Prozessspeichermessung, 20.09.2026

**Drei vorab festgelegte Faelle, jeweils genau einmal in einem frischen Prozess gemessen. Alle drei Messungen technisch gueltig; keine Wiederholung.** Keine Produktdatei oder bestehende Pruefpflicht geaendert. Der reale Starter bleibt gesperrt. Dies ist ein beobachteter Speicherbedarf, keine garantierte RAM-Obergrenze und keine unabhaengige Abnahme.

## Festlegung und Umgebung

[Vorabplan](plan.json), vor dem ersten Kindprozess gespeichert. Erfolg mit 58 Endpunkten; Supplierabbruch bei Versuch 58; bestehende Fehlerstelle nach Terminal-Rename bei bereits publizierter Verifikation. Letzterer Fall schliesst ueber Fehler- und Minimalterminal ab. Nur bestehende Null-PCM-Fixtures, kein NU-Supplier.

Interpreter: `3.14.4 (tags/v3.14.4:23116f9, Apr  7 2026, 14:10:54) [MSC v.1944 64 bit (AMD64)]`. NumPy `2.4.4`. Betriebssystem `Windows-10-10.0.19045-SP0`, Architektur `AMD64`. Interpreterpfad, SHA256, NumPy-Buildkonfiguration und relevante Thread-/Allocator-Umgebungsvariablen: [environment.json](environment.json). Weitere native Dateihashes: [native-runtime-files.json](native-runtime-files.json). Vollstaendige Produkt- und externe Laufzeitbindung: [product-inventory.json](product-inventory.json).

Vorbereitung erzeugte die drei Fixtures in einem separaten, danach beendeten Prozess. Sie gehoert nicht zur gemessenen V8-Ausfuehrung. Ein Selbsttest der Windows-Messschnittstelle und eine Syntaxpruefung des Messskripts starteten keinen Produktpfad. Anschliessend wurden nur die drei registrierten Prozesse gestartet; ihre PID, Startmarken und Exitcodes sind gespeichert.

## Messverfahren und Grenzen

Der externe Beobachter (PID 14688) fragt mit `ctypes` und `GetProcessMemoryInfo` die Windows-Struktur `PROCESS_MEMORY_COUNTERS_EX` ab. `WorkingSetSize` ist das aktuelle residente Working Set (RSS-nahe Windows-Metrik, inklusive gemeinsam nutzbarer Seiten); `PrivateUsage` ist privater Commit, also kein Mass ausschliesslich physisch belegten RAMs. `PeakWorkingSetSize` und `PeakPagefileUsage` sind die vom Betriebssystem gefuehrten bisherigen Prozesshoechststaende. [Microsoft-Definitionen](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters_ex).

Sollintervall 10 ms; jeder Datensatz enthaelt Querybeginn, Ablesezeitpunkt sowie getrennte Ziel-/Beobachterwerte. Beide Prozesse verwenden denselben Windows-Performance-Counter. Die Kindprozesse schreiben verschachtelte Beginn-/Endmarken fuer Import, Vorstart, Verbindung, jede Materialisierung, Quellen-/Ownerabschluss, Codec, Einlesen, Verifikation, Auswertung und Publikation. Originalfunktionen werden im Messprozess durch protokollierende Wrapper aufgerufen; Produktquelldateien bleiben unveraendert. Nur die vorab bestimmten Fehler werden injiziert.

Je 100 ms explizite Haltezeit machen die Interpreterbasis und die Basis nach Importen abtastbar. Die Basis enthaelt bereits Standardbibliothek, Messskript und Marker-I/O; sie ist kein nackter Interpreter. Am Ende wartet das Kind auf die Freigabe des Beobachters fuer einen letzten nativen Snapshot. OS-Peaks gelten bis zu diesem Snapshot, nicht fuer einen behaupteten Peak nach beendetem Prozess. Import/Instrumentierung, Ergebnisexport und Markeraufwand sind enthalten und wurden nicht rechnerisch abgezogen.

Kurze Spitzen zwischen Stichproben koennen fehlen. OS-Hoechststaende sind kumulativ und lassen sich nicht exakt einer kurzen Phase zuweisen. Phasenmaxima unten sind ausschliesslich abgetastete Werte; fehlende Stichproben werden nicht zu Nullwerten. Verschachtelte Phasendauern sind inklusive ihrer Unterphasen und duerfen nicht addiert werden. Hostlast, Paging, Allokator, NumPy-Build und andere Threadkonfigurationen wurden nicht variiert. Drei unterschiedliche Einzelfaelle sind keine statistische Wiederholungsreihe.

## Gemessene Prozesswerte

Alle Speicherwerte in MiB (=1048576 Byte); exakte Bytewerte stehen in [summary.json](summary.json).

| Fall / PID | Abgetastetes WS-Maximum | OS-WS-Peak | Abgetastetes Commit-Maximum | OS-Commit-Peak | Stichproben |
|---|---:|---:|---:|---:|---:|
| Voller Erfolg / 16028 | 67.238 | 67.789 | 441.676 | 442.270 | 779 |
| Abbruch Versuch 58 / 8324 | 66.238 | 66.578 | 441.109 | 441.145 | 826 |
| Fehler nach Verifikationspublikation / 20088 | 67.566 | 68.121 | 441.926 | 442.699 | 930 |

| Fall | Ist-Abstand min / Median / max (ms) | Laengste Messabfrage (ms) | Beobachter WS-Max / Commit-Max (MiB) |
|---|---|---:|---|
| Voller Erfolg | 9.818 / 10.327 / 18.022 | 0.290 | 18.566 / 12.367 |
| Abbruch Versuch 58 | 9.962 / 10.331 / 18.157 | 0.281 | 18.441 / 12.434 |
| Fehler nach Verifikationspublikation | 9.978 / 10.345 / 17.635 | 0.147 | 19.055 / 13.297 |

Die Beobachterwerte sind nicht in Zielprozesswerte eingerechnet. Es gab keine fehlgeschlagene Prozessabfrage und keinen Abstand ueber 20 ms. Die jeweils ersten Samples koennen nach Prozessinitialisierung liegen; kumulative OS-Peaks erfassen auch fruehere, nicht einzeln abgetastete Spitzen bis zum letzten Snapshot.

## Zeitliche Phasenzuordnung

Pro Phase: inklusive Dauer, Zahl der Intervalle mit mindestens einer Stichprobe / Gesamtintervalle, abgetastetes WS-/Commit-Maximum. Die vollstaendige Zeitachse mit relativen Millisekunden steht je Fall in `timeline.csv`; absolute Zaehler und verschachtelte Grenzen in `phases.jsonl` und `phase-intervals.json`.

| Fall | Phase | Dauer ms | Erfasste Intervalle | WS-Max MiB | Commit-Max MiB |
|---|---|---:|---:|---:|---:|
| success | INTERPRETER_BASE | 100.248 | 1/1 | 15.410 | 10.375 |
| success | IMPORTS | 238.221 | 1/1 | 31.832 | 408.988 |
| success | IMPORTED_BASE | 100.463 | 1/1 | 32.102 | 408.988 |
| success | PRESTART_VALIDATION | 4897.089 | 1/1 | 67.238 | 441.676 |
| success | MATERIALIZATION | 421.118 | 41/58 | 51.184 | 425.996 |
| success | CODEC_ENCODE | 9.878 | 1/1 | 46.988 | 421.828 |
| success | CODEC_DECODE | 9.910 | 0/2 | nicht abgetastet | nicht abgetastet |
| success | REREAD_record.json | 0.553 | 0/3 | nicht abgetastet | nicht abgetastet |
| success | TECHNICAL_VERIFICATION | 32.240 | 1/1 | 48.066 | 423.445 |
| success | PUBLISH_verification.json | 307.573 | 1/1 | 48.074 | 423.445 |
| success | REREAD_verification.json | 0.283 | 0/2 | nicht abgetastet | nicht abgetastet |
| success | PUBLICATION_FINISH | 614.559 | 1/1 | 48.355 | 424.621 |
| success | RUN | 7544.799 | 1/1 | 67.238 | 441.676 |
| abort_58 | INTERPRETER_BASE | 100.275 | 1/1 | 15.754 | 10.637 |
| abort_58 | IMPORTS | 231.440 | 1/1 | 31.898 | 408.941 |
| abort_58 | IMPORTED_BASE | 100.123 | 1/1 | 31.980 | 408.941 |
| abort_58 | PRESTART_VALIDATION | 4878.249 | 1/1 | 66.238 | 441.109 |
| abort_58 | MATERIALIZATION | 392.115 | 37/58 | 50.086 | 424.453 |
| abort_58 | CODEC_ENCODE | 9.707 | 1/1 | 47.230 | 421.449 |
| abort_58 | CODEC_DECODE | 11.663 | 1/2 | 48.242 | 422.648 |
| abort_58 | REREAD_record.json | 0.329 | 0/2 | nicht abgetastet | nicht abgetastet |
| abort_58 | TECHNICAL_VERIFICATION | 29.861 | 1/1 | 48.438 | 422.648 |
| abort_58 | PUBLISH_verification.json | 328.335 | 1/1 | 48.484 | 422.648 |
| abort_58 | REREAD_verification.json | 0.395 | 0/2 | nicht abgetastet | nicht abgetastet |
| abort_58 | PUBLICATION_FINISH | 596.749 | 1/1 | 48.512 | 423.156 |
| abort_58 | ERROR_CLOSURE | 1800.337 | 1/1 | 48.512 | 423.156 |
| abort_58 | RUN | 8075.131 | 1/1 | 66.238 | 441.109 |
| post_verification | INTERPRETER_BASE | 100.853 | 1/1 | 15.688 | 10.461 |
| post_verification | IMPORTS | 243.715 | 1/1 | 31.934 | 408.871 |
| post_verification | IMPORTED_BASE | 100.449 | 1/1 | 32.012 | 408.871 |
| post_verification | PRESTART_VALIDATION | 5087.745 | 1/1 | 67.566 | 441.926 |
| post_verification | MATERIALIZATION | 409.858 | 40/58 | 50.164 | 424.809 |
| post_verification | CODEC_ENCODE | 8.528 | 0/1 | nicht abgetastet | nicht abgetastet |
| post_verification | CODEC_DECODE | 10.045 | 1/2 | 48.316 | 422.352 |
| post_verification | REREAD_record.json | 0.748 | 1/3 | 48.793 | 422.617 |
| post_verification | TECHNICAL_VERIFICATION | 33.239 | 1/1 | 48.852 | 422.617 |
| post_verification | PUBLISH_verification.json | 330.636 | 1/1 | 49.031 | 422.949 |
| post_verification | REREAD_verification.json | 0.341 | 0/2 | nicht abgetastet | nicht abgetastet |
| post_verification | PUBLICATION_FINISH | 589.588 | 1/1 | 49.070 | 422.949 |
| post_verification | ERROR_CLOSURE | 2159.484 | 1/1 | 49.113 | 422.949 |
| post_verification | RUN | 9229.621 | 1/1 | 67.566 | 441.926 |

**Beobachtung:** Die hoechsten abgetasteten Werte aller drei Faelle liegen in der Vorstartpruefung. Bereits nach den gemeinsamen Produkt-/NumPy-Imports liegt der private Commit bei rund 409 MiB. Die Materialisierungsphasen liegen abgetastet bei rund 424–426 MiB Commit. **Interpretation:** Der hier beobachtete Bedarf wird wesentlich von der geladenen Laufzeit und der Vorstartpruefung gepraegt. Eine Ursache allein in NumPy, einzelnen Threads oder konkreten Allokationen ist nicht isoliert nachgewiesen.

**Messluecken:** Von 58 Materialisierungsintervallen wurden 41, 37 beziehungsweise 40 getroffen. Beide Codec-Decodes des Erfolgsfalls und das Codec-Encoding des dritten Falls hatten keine Stichprobe. Weitere kurze Einleseintervalle sind in den Rohdaten mit 0 Samples ausgewiesen. Dafuer liegen Zeitmarken, aber keine belastbaren lokalen Speicherspitzen vor. Eine nachtraegliche Wiederholung zur Verbesserung dieser Werte wurde nicht vorgenommen.

## Funktions- und Artefaktpruefung

[analyze.py](analyze.py) liest ausschliesslich erhaltene Daten. Geprueft: Prozessstatus, erwartete Fehlerstelle, Supplier-/Quellenzaehler, sechs geschlossene Owner, beide Gates=false, Status/Auswertbarkeit, Hashbindung von Record und Verifikation sowie alle tatsaechlichen Eingabe- und Ergebnisdateigroessen/-hashes. Alle drei Faelle PASS, alle Artefaktbilanzen vollstaendig und innerhalb der unveraenderten Grenzen, keine fehlenden dauerhaften Abschlussbelege.

| Fall | Versuche / Erfolge | Hash / Rezeptor / NJ | Status / Primaerfehler | Produkt-Artefaktbilanz inkl. Code (Byte) |
|---|---:|---|---|---:|
| Voller Erfolg | 58 / 58 | 58/58/58 | CLOSED_NEUTRAL_VERIFIED / keiner | 1011798 |
| Abbruch Versuch 58 | 58 / 57 | 57/57/57 | NOT_EVALUABLE / LAST_ENDPOINT_FAILURE | 1007683 |
| Fehler nach Verifikationspublikation | 58 / 58 | 58/58/58 | NOT_EVALUABLE / TERMINAL_AFTER_RENAME | 1015305 |

Beim dritten Fall bleiben Record und separate Verifikation erhalten; Fehlerdatei, bereits geschriebenes Terminal und Minimalterminal werden gemeinsam bilanziert. Die Auswertung bleibt trotz zuvor erzeugten Kandidatenbelegs gesperrt. Das ist der vorab festgelegte Fehler nach Verifikationspublikation, kein zweiter Versuch.

## Werkzeugumfang und Hashbindung

Unveraenderter Produktcode einschliesslich aller 138 gebundenen Pruefpflichten: **699053 Byte**. Messskript plus reine Offlineauswertung: **17684 Byte**. Konservativ gemeinsam: **716737 / 720896 Byte**, **4159 Byte frei**. Keine zusaetzliche Projektabhaengigkeit ausser den zwei ausgewiesenen Skripten; keine Paketinstallation. Die bereits gebundene Testfixture wird nur in der Vorbereitung verwendet. Der Beobachter verwendet Standardbibliothek und Windows-API. [Vollstaendiger Werkzeugumfang](complete-tool-scope.json), [Importvereinigung der Messung](tool-code-inventory.json).

| Werkzeug | Byte | SHA256 |
|---|---:|---|
| [measure.py](measure.py) | 10811 | `6dcbed6abb4d79d107dab55b2809119b4d9f34f4f5ccc942030723bfcd0238e6` |
| [analyze.py](analyze.py) | 6873 | `8732c6dae511db39d4a4e77ade3dc51176615207a6170790889a1ac3e6162b5d` |

Die unveraenderte Produktbilanz zaehlt 699053 Codebyte; sie wird nicht nachtraeglich umklassifiziert. Selbst die konservative Zusatzrechnung, die beide externen Werkzeuge jedem einzelnen Abschluss zusaetzlich anlastet, bleibt innerhalb Code- und Gesamtgrenze: success=1029482 Byte, abort_58=1025367 Byte, post_verification=1032989 Byte. Rohmessdaten, Marker und Auswertungsdateien liegen ausserhalb der besitzgebundenen Produkt-Ausgabeordner; ihr eigener Archivumfang wird separat in `archive-footprint.json` ausgewiesen. Quellbyteumfang, Archiv-Diskbedarf, Working Set und Commit sind unterschiedliche Messgroessen.

Produktinventar vor der Messung gegen den angenommenen V8-Stand identisch; danach alle gebundenen Quellhashes erneut gleich. Keine Produkt-/Testaenderung, deshalb keine erneute Gesamtsuite. Die Offlineauswertung wurde fuer die CSV-Zeitachse erweitert und erneut auf denselben Rohdaten ausgefuehrt; kein zusaetzlicher Kindlauf. Alle Rohdaten und Exitprotokolle bleiben erhalten.

## Rohdaten und Reproduzierbarkeit

| Fall | Prozesssamples | Phasenmarken | Zeitachse | Funktionsergebnis |
|---|---|---|---|
| success | [samples.jsonl](success/samples.jsonl) | [phases.jsonl](success/phases.jsonl) | [timeline.csv](success/timeline.csv) | [result.json](success/result.json) |
| abort_58 | [samples.jsonl](abort_58/samples.jsonl) | [phases.jsonl](abort_58/phases.jsonl) | [timeline.csv](abort_58/timeline.csv) | [result.json](abort_58/result.json) |
| post_verification | [samples.jsonl](post_verification/samples.jsonl) | [phases.jsonl](post_verification/phases.jsonl) | [timeline.csv](post_verification/timeline.csv) | [result.json](post_verification/result.json) |

Rohdaten erneut auswerten (startet keine Messung): `python reports/s2uc/v8-process-memory-20260920/analyze.py`.

Fuer eine spaeter gesondert beauftragte Reproduktion die beiden Skripte in einen neuen leeren Geschwister-Berichtsordner unter `reports/s2uc/` kopieren; dann `measure.py prepare` und anschliessend genau einmal `measure.py observe` ausfuehren. `prepare` bindet den angenommenen Produktstand und erzeugt vorab die drei Fallbindungen. `observe` prueft Werkzeug-/Codehashes und verweigert bereits gestartete Faelle durch exklusive Startdateien. Vorhandene Plan-, Start- oder Rohdateien nicht loeschen, um Wiederholungen zu erzwingen. Danach `analyze.py` aufrufen. Fuer diese Uebergabe ist keine weitere Messung erforderlich.

## Konkrete Empfehlung

Als **Startwerte fuer ein spaeter separat zu pruefendes Begrenzungspaket** schlage ich 640 MiB privaten Commit pro Kindprozess und 96 MiB Working Set als Beobachtungs-/Warnschwelle vor. Das liegt rund 45 % beziehungsweise 41 % ueber den groessten hier beobachteten OS-Peaks (442.699 / 68.121 MiB). Dieser Abstand ist ein vorsichtiger Planungsaufschlag, keine statistisch oder funktional abgesicherte Reserve.

Eine spaetere Windows-Job-Object-Grenze fuer Prozess-Commit kann bereits vor Produkt-/NumPy-Importen gelten; `ProcessMemoryLimit` begrenzt committed memory. [Microsoft-Dokumentation](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information). Zuerst neutral pruefen, wie der vorhandene Fehlerabschluss bei tatsaechlichem Allokationsversagen reagiert; ein OOM kann auch Abschlussbelege verhindern. Working Set separat beobachten, nicht als austauschbare Commitgrenze behandeln. Die Werte werden hier weder implementiert noch als neuer Ressourcenvertrag eingefuehrt.

Naechster vorgeschlagener Schritt an den Projektleiter: Messbericht und weiterhin offene unabhaengige V8-Abnahme beurteilen, danach ein begrenztes neutrales Paket fuer durchgesetzte Prozessbegrenzung samt Fehlerabschluss festlegen. Keine garantierte RAM-Obergrenze, keine Aussage ueber andere Hosts oder reale Quellen und kein Erinnerungsvorteil aus diesen drei Messungen.
