# Mediencheckpoint: 11/12, NOT_QUALIFIED

2026-09-13. Genau ein neutraler Testaufruf, zwölf Prüfgruppen, 64,468 s.
Quellhashes während des Aufrufs unverändert. Kein Retry, keine nachträgliche
Produktkorrektur und kein realer Videolauf. Repositorybasis:
537109994cf777f8d36cda617aafe12226806c25 plus vorab gebundener Arbeitsbaum.

## Erreichte Deckung

Elf unabhängige Gruppen bestanden: vollständige Mehrframe-Überlaufzählung
ohne ausgelieferte Frames, verzögerte Flushausgabe, unbekannte Framezahl bei
Ausnahme im Decode-Aufruf, Vorabverfügbarkeit und Grenzgleichstand, erhaltene
Lesebytes bei Hashfehler, verlustfreie gemeinsame Referenzen einschließlich
Unveränderlichkeit, fehlende Referenzen, Digest-/Klassenfehler, fehlgeschlagene
Publikation ohne Erfolgsdatei, historische Workerinitialantwort und echter
Workerprozessabbruch mit unvollständiger Verbrauchsevidenz.

Die neue Semantik ist `media.restart-work.v2-batch-abort`: Framegrenzen sind
Abbruchgrenzen nach dem unteilbaren Decoderaufruf. Ein übergroßer Batch wird
vollständig gezählt und nicht an Rezeptoren/MCM ausgeliefert. Die mögliche
interne Überschreitung ist nicht numerisch gedeckelt. Prozess-/Job-RAM und
Zeitlimits bleiben getrennte Grenzen; sie beweisen keine genaue Framezahl.

## Native Prozessgruppe

Referenz: 20 Ereignisse, RECORDING_COMPLETE, PID 18124.
Früher Speicherstopp: Ereignis 1, SUSPENDED, PID 15532.
Früher Restore: bis Ereignis 20, RECORDING_COMPLETE, PID 14480.
Später Speicherstopp: Ereignis 19, SUSPENDED, PID 30108.
Später Restore: Ereignis 20 mit FORMATION_COMMITTED erreicht, danach
NOT_EVALUABLE mit angezeigtem MEDIA_STORE_BUDGET; Kindprozess Exitcode 1.

Damit wurden echte Rezeptoren, Feld-/Memoryfortschreibung, getrennte Prozesse
und beide Suspendpositionen tatsächlich erreicht. Der Decoder lief als echter
isolierter Worker, seine Container-/Codecquelle war jedoch ausdrücklich
synthetisch (801 Video- und 1.255 Audioframes mit verzögertem letzten Paket).
Das ist kein neuer Nachweis der realen MP4-/H.264-/AAC-Kette.

Die nachgelagerten Gesamtvergleiche beider Arme wurden wegen des Fehlschlags
nicht ausgeführt. Keine Vergleichsverifikation und keine Auswertung erzeugt.
Insbesondere werden Zustands-/Auswahlgleichheit, die anschließend angeordneten
Positions-/Quellenmanipulationen und Checkpoint-Wiederverbrauch NICHT als
bestanden ausgegeben. Die bestandenen Teilgruppen ersetzen diese Lücke nicht.

Gespeicherte Konten: Referenz 18.440 Containerbytes, 2.056 Pakete, 801 Video-
und 1.255 Audioframes. Früher Restore kumulativ 34.832 Bytes, 2.064 Pakete,
804 Video- und 1.260 Audioframes. Sein Vorverbrauch bleibt separat erhalten.
Das späte Abschlusskonto fehlt; keine Rekonstruktion als historische Messung.

## Budget- und Fehlerabschlussbefund

Vorregistrierte gemeinsame Reservierung: 3.782.586 Byte, keine vorgelagerte
Verletzung. Davon 131.072 Metadaten, 222.826 Quellen, 1.507.328 native
Objektablage, 1.706.320 Feld einschließlich temporärer Kopie. Diese lokale
Allokation war KEIN hinreichend formatgebundener Nachweis aller Indizes und
Fehlerhüllen. Die komplette Meta-Ausgabe wurde damit nicht abgesichert.

Ist vor result/balance-Abschluss: Metadaten 109.282, Gesamt 2.471.480 Byte.
Nach result.json und balance-before-report.json, vor diesem Bericht:
Metadaten **131.509 / 131.072**, Gesamt **2.493.707 / 4.194.304** Byte.
Damit bereits **437 Byte Metadatenüberschreitung**. Die 21.834 Byte große
Bilanzdatei ist vollständig erhalten. Bericht und abschließende Summendatei
werden zusätzlich gezählt, nicht aus dieser Bilanz ausgelagert.

Die späte fehlgeschlagene Veröffentlichung meldete MEDIA_STORE_BUDGET.
Der exakte damals angeforderte Summenwert ist NICHT gespeichert:
late-restore/record.json und failure.json fehlen, vorhanden sind der
Playerabschluss und der vollständige Kindprozess-Traceback. Der aktuelle
437-Byte-Überstand darf nicht als damaliger Auslösewert ausgegeben werden.

Statische Erklärung des zusätzlichen Fehlerabschlussproblems:
`Store._write` gibt eine vollständige Dateiliste als Fehlerdetails weiter;
`Session.fail` versucht diese erneut über denselben budgetierten Publisher
zu speichern. Ein erneuter Budgetfehler kann die Publikation des Primärbelegs
verhindern. Der Player speichert danach nur den Fehlercode. Das ist eine
offene Beleg-/Fehlergrenze, kein Memorybefund. Keine Reparatur im Fehllauf.

## Grenzen und nächster Korrekturumfang

Gemeinsame Inhalte werden erst nach tatsächlicher Bytegleichheit dedupliziert;
beide Arme erzeugen ihre Inhalte selbst. Alle vorhandenen Objekte, Indizes,
temporären Dateien und Logs bleiben erhalten. Kein Kürzen oder Umklassifizieren.
Die Quellenliste und der optionale historische Workeranschluss sind noch nicht
als Gesamtanschluss qualifiziert. Reale Zulassung bleibt gesperrt.

Erforderlich ist eine eng begrenzte Korrektur der Meta-Index-/Abschlusshülle
und ein endlich großer, nicht rekursiver Primärfehlerabschluss mit den
ursprünglichen Teilbeträgen. Die unerreichten Kontrollen müssen später
unabhängig erreichbar werden. Keine weitere Testausführung ohne neue Freigabe.
Gates und QUALIFIED bleiben False; kein realer Medienstart.

Der erste direkte Aufruf der Vorbereitungsdatei endete vor Erstellung einer
Bindung mit ModuleNotFoundError (Importpfad). Danach wurde sie korrekt als
Modul gestartet. Beides waren Vorbereitungen, keine Qualifikationsaufrufe;
test.claim bindet genau den einen tatsächlichen Suiteaufruf.
