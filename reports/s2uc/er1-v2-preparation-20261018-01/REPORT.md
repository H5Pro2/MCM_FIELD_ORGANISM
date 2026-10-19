# ER1-v2: Vorbereitung und Bindung

2026-10-18. Abschlussauftrag f3ab81be-286c-474c-8b5b-2b6909bd03fc.

## Umsetzung und vorhandene Messungen

Der getrennte Einstieg tools/s2uc_er1_v2_prepare.py verwendet die abgenommene strukturelle Prüfung für ARCHIVE_STOCK sowie verschachtelte Bestände in ARCHIVE_OBSERVER. Alle fachlichen Felder und die Retained-Reihenfolge bleiben geprüft. Quellenrezept, U-Auswahl, E/F-Regeldifferenz und Statistik bleiben unverändert. Historische Module und Abbruchbelege werden nicht überschrieben.

integration-tests.json und integration-tests.log dokumentieren 8/8 bestandene Tests: sieben integrierte Tests sowie die übernommene synthetische Generations-/JSON-Regression einschließlich 99/100. Keine Wiederholung dieser Tests im Abschlussauftrag.

Fünf vorhandene neutrale Integrationsläufe mit je zwei Fällen, zwei Armen und 80 Frames pro Arm ergeben insgesamt 20 kurze Policy-Arme. Der Positivlauf quittiert Fälle 1 und 2 nach unabhängiger Archivprüfung. Endmarken- und Reihenfolgefehler führen zu ARCHIVE_STOCK, die verschachtelte Observer-Reihenfolge zu ARCHIVE_OBSERVER. Passende Testprüfsummen umgehen die semantische Prüfung nicht. Alle vier Negativläufe quittieren nur Fall 1; Fall 2 bleibt unquittiert. Workerende, Armcleanup und Dateicleanup sind in allen fünf terminal.json bestätigt. Im kombinierten Endmarken-/Budgetfall bleibt ARCHIVE_STOCK die erste Ursache; das erschöpfte Administrationsbudget verhindert den normalen Workerbericht, nicht den reservierten Fehlerabschluss.

Belege: integration-complete/terminal.json, integration-endmark/terminal.json, integration-order/terminal.json, integration-observer_order/terminal.json und integration-endmark_budget/terminal.json.

## Ressourcen: Messung, Hochrechnung, Unsicherheit

RESOURCE_PLAN.md und resource-plan.json enthalten die vollständige Planung und sämtliche unveränderten Grenzen. Gemessen wurden zusätzlich 100 reine Strukturvergleiche am neutralen E-Bestand: 0,271765 s und 100733 Bytes Pythonpeak, ohne Policyarme oder Referenzreplay. Der Vergleich ist bereits in den gemessenen Archivprüfzeiten enthalten und wird nicht doppelt addiert.

Lineare Hochrechnung für 32 Geschichten: 1929,2 s gesamte Fallarbeit, darin 1213,8 s Policy/Capture/Live-Referenzen und 378,7 s Archivprüfung. Planungsansatz Faktor 8 plus 600 s ergibt 16034 s, zuzüglich 3600 s Abschlussreserve. Lineare Archivplanung: 9555968 Bytes insgesamt. Dies sind Hochrechnungen, keine Vollgrößenqualifikation. Lange Herkunfts-/Feedbackketten, Kompression und Speicherpeaks bei 1024 Frames bleiben unbewiesen; alle harten Abbruchgrenzen gelten unverändert.

## Reservierter späterer Forschungsumfang

32 Geschichten zu 1024 Frames; genau 64 Policy-Arme, getrennt 64 Live-Referenzen und 64 Archivrekonstruktionen, keine zusätzlichen Messarme. 32 Quellenrekonstruktionen und eine unabhängige Statistikreferenz. Primärvergleich unverändert über alle 511 Ziele je Geschichte.

Neuer Namensraum MCM-ER1/source/v2; exklusives Ziel reports/s2uc/er1-v2-comparison-16h-01. Es wurden keine Forschungsberechtigung, v2-Forschungsquellen oder vollständigen Policyfälle erzeugt. Der alte Versuch bleibt TECHNICAL_ABORT mit verbrauchter Freigabe; kein Retry, Resume oder nachträgliches Freigeben seines Archivs.

## Abschlussprüfung

Die endgültige Bindung wurde erzeugt und mit dem tatsächlichen Validator geprüft. REPORT.md ist vom vorhandenen Binder ausdrücklich ausgenommen; alle übrigen Vorbereitungsartefakte werden gebunden.

Vorstart-SHA256: `0d67e76c14afa1e74a19dd7190857e68a19062abd26fd2af484c85b761a8f2b7`.

Prüfnachweis: tools.s2uc_er1_v2_prepare.validate_binding erfolgreich; vollständige dynamische Codeabdeckung 2979 Dateien, zusätzlich 72 Qualifikationsartefakte mit vollständigem Mengenabgleich. Validator prüft Hashes, Laufzeitumgebung, Grenzen, Ausführungsstruktur, Namensraum, Ziel und Aufruf. Historischer Vorstart-SHA unverändert; alle 2967 historischen Dateibindungen und 43 Qualifikationsbindungen erneut ausschließlich per Hash geprüft. Zusätzlich sämtliche 43 Abbruchbelege und 11 Korrekturbelege einschließlich ihrer Manifest-SHA unverändert. Keine historische Archiv-Neuauswertung.

Forschungsberechtigung authorization.json, Verbrauchsmarker CONSUMED.json und Forschungsziel fehlen. Keine verbleibenden technischen Hindernisse im Vorbereitungsabschluss. Forschungsentscheidung bleibt gesondert offen.

Exakter zukünftiger Aufruf (nur dokumentiert, NICHT ausgeführt; Arbeitsverzeichnis `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`):

```powershell
& 'C:\Python314\python.exe' '-m' 'tools.s2uc_er1_v2_prepare' 'run' 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\er1-v2-preparation-20261018-01\prestart.json' 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\er1-v2-preparation-20261018-01\authorization.json'
```

Erforderliche spätere Berechtigungsart: ER1_V2_RESEARCH_ONCE, gebunden an den obigen SHA; hier nicht erstellt.

Finale Paketgröße einschließlich Bericht und Vorstartdateien: 3179086 Bytes; Grenze 8388608 Bytes.

Anschluss: Projektleiter prüft das gebundene Paket und entscheidet separat über den Forschungseinstieg. Vollgrößenunsicherheit bleibt bestehen.
