# ER1: technischer Abbruch im ersten Forschungsfall

2026-10-17. Workflow `261de2b7-68f4-4c2b-996d-d77ebdfb48d8`.
Status **TECHNICAL_ABORT – KEIN NUTZENURTEIL**.

Der freigegebene Aufruf zur Vorstartbindung
`8b00f9a27f958307e41673543ae294e8cffe9d2bf36949d2d71b3886b18b5bde` wurde genau einmal ausgeführt.
Die Freigabe ist verbraucht. Kein Retry, Resume, Ersatzlauf, Tuning oder
nachträgliches Übergehen der fehlgeschlagenen Prüfung.

## Start und erreichte Arbeit

Unmittelbar vor dem Start: 2967 gebundene Dateien, 43 Qualifikationsartefakte,
Laufzeit, Grenzen, Aufruf und Ziel durch den gebundenen Validator bestätigt;
Ziel und Verbrauchsmarker waren nicht vorhanden. Danach wurde ausschließlich
die freigegebene ER1_RESEARCH_ONCE-Berechtigung mit diesem SHA erstellt und der
unveränderte Aufruf aus prestart.json:call einmal gestartet.

[START.json](START.json) und der Verbrauchsmarker in der Vorbereitung belegen
den Verbrauch. Alle 32 Quellen wurden unter MCM-ER1/source/v1 erzeugt,
unabhängig geprüft und vor dem ersten Arm gemeinsam versiegelt.
Manifest-SHA: `e932f00681189d8b1e268b9b9a2ef1f8e56c760e26fe2c3364685f5427a154e3`.
Die Nachprüfung der bestehenden Dateihashes bestätigt alle 32 Quellen und
sämtliche 39 Einträge des unveränderten Abschlussmanifests.

Fall 1 erzeugte zwei verschiedene Policy-Arme, E und F, mit je 1024 Frames.
Beide erreichten ihren Abschluss und bestanden ihre begleitenden unabhängigen
Referenzprüfungen laut Capture. Ein Archiv wurde geschrieben. Seine anschließende
fachliche Archivreferenz scheiterte. Keine zusätzliche Mess- oder Capture-Policy
wurde gestartet. Fälle 2–32 wurden nicht begonnen.

**Quittierte Geschichten: 0/32. Angelegte Policy-Arme: 2/64.**
Die Zahlen bestätigen Fortschritt, keine erfolgreiche Qualifikation von Fall 1.
Der unabhängige Archivprüfschritt ist unvollständig. Primärstatistik und globale
mechanistische Nutzenaussage wurden nicht erzeugt; aus dieser Teilserie werden
keine Fehlervergleiche, Vorteile oder Nachteile als Forschungsresultat berichtet.

## Erste Ursache und belegter Blocker

Erste unverändert gespeicherte Ursache: `ValueError:ARCHIVE_STOCK`.

- [terminal.json](terminal.json), first_diagnostic: Worker, fachliche Archivprüfung.
- `tools/_s2uc_er1_run_archive.py`, Vergleich des archivierten Bestands mit der
  unabhängigen Referenz durch zwei JSON-Zeichenketten.
- [case-01.gz](case-01.gz) und [case-01-capture.json](case-01-capture.json)
  sind erhalten; das Archiv gilt **nicht** als fachlich abgenommen.
- [worker.json](worker.json), [result.json](result.json),
  [closure.json](closure.json) bewahren den technischen Abschluss.

Eine begrenzte Nachsicht ausschließlich vorhandener Archivfelder zeigt einen
konkreten Darstellungsfehler im Prüfpfad: JSON liest die Schlüssel von
observation_end als Strings zurück, die Referenz führt Generationsschlüssel
als Integer. json.dumps(sort_keys=True) sortiert diese unterschiedlich.
Die Abbildung {9:208, 10:224} wird in anderer Reihenfolge serialisiert als
{"9":208, "10":224}, obwohl die normalisierten Abbildungen gleich sind.

Im vorhandenen E-Capture tritt diese Konstellation erstmals bei Frame 224 auf
(Generationen 9 und 10); im F-Capture bei Frame 344. Der reine
Zeichenkettenvergleich kann deshalb ARCHIVE_STOCK auslösen, ohne dass sich die
zugehörigen Endmarkenwerte unterscheiden. [abort-diagnosis.json](abort-diagnosis.json)
belegt diese unterschiedliche Darstellung an den vorhandenen Daten.

Das ist ein nachgewiesener Prüferdefekt und eine konkrete Erklärung für die
Fehlermeldung. Eine vollständige erneute Referenzfortschreibung zur ausschließlichen
Ursachenzuordnung wurde **nicht** durchgeführt. Insbesondere wird das Archiv dadurch
nicht nachträglich für gültig erklärt. Keine Codekorrektur oder Wiederholung im
verbrauchten Forschungsversuch. Die kurzen neutralen Vorprüfungen hatten diesen
Übergang von einstelligen zu mehrstelligen Generationen nicht abgedeckt.

## Ressourcen und getrennte Cleanupzustände

| Befund | Wert |
|---|---:|
| Gesamtdauer laut Terminal | 86.602381 s |
| Gemeinsamer Jobpeak | 147726336 Bytes |
| Größter Prozesspeak im Job | 117764096 Bytes |
| Jobgrenze | 536870912 Bytes |
| Worker-Inventurprüfungen | 4235 |
| Worker-Inventurzeit | 31.586063 s |
| Supervisor-Inventurprüfungen | 4676 |
| Supervisor-Inventurzeit | 35.621905 s |
| Archiv gzip | 180449 Bytes |
| Archiv encoded | 1054538 Bytes |
| Höchster gemessener Policy-Zusatzheap | 5527 Bytes |
| Originalframe-Obergrenze | 16 |
| Frames plus Ausgaben, Obergrenze | 18 |

Inventurzeiten überlappen zwischen Worker und Supervisor und werden nicht zur
Gesamtdauer addiert. Keine Ressourcenüberschreitung ist als Abbruchursache
registriert. Die inaktiven Tracerfelder mit Wert 0 sind keine Nullmessungen;
maßgeblich sind die ausgewiesenen konservativen Frameobergrenzen.

- Armcleanup: CONFIRMED für beide Arme; beide Captures melden cleanup=true.
- Workerende: bestätigt; Workerexitcode 0.
- Dateicleanup: bestätigt; keine Partialdateien verblieben.
- Codecstore: im Fallabschluss freigegeben; Worker meldet Gesamtcleanup CONFIRMED.
- Forschungsstatus: TECHNICAL_ABORT. Der äußere Prozessreturncode 0 ersetzt
  diesen Status nicht und bedeutet hier keinen wissenschaftlichen Erfolg.

Das ursprüngliche closure.json bleibt unverändert. Die ergänzende
Prüfsummenliste delivery-closure.json schließt Terminal, Diagnose und diesen
Bericht ein; sie ist keine neue Vorstartbindung und keine Autorisierung.

## Nächster konkreter Schritt

Empfehlung an den Projektleiter: einen ausschließlich neutralen Fehlerbehebungsauftrag
für den Archiv-Bestandsvergleich erteilen. Ganze Bestände typgleich und strukturell
vergleichen, ohne Werte, Originale oder Endmarken auszublenden; gezielte Regressionen
für Generationsschlüssel 9/10 und 99/100 sowie echte Bestandsabweichungen ergänzen.
Anschließend den korrigierten Prüfpfad separat bewerten. Dieser Vorschlag enthält
weder einen erneuten Forschungsaufruf noch eine Wiederaufnahme des abgebrochenen
Versuchs. Die bestehende Einmalfreigabe bleibt verbraucht.
