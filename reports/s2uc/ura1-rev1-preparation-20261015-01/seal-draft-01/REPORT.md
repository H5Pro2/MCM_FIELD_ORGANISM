# URA1-REV1: Implementierung und neutrale Vorbereitung

2026-10-15. **NEUTRAL_QUALIFIED – Forschungsstart nicht autorisiert.** Der angenommene [Konzeptvertrag](../../../docs/S2UC_URA1_REV1_TRANSFER_KONZEPTVERTRAG_20261015.md) ist in getrennten REV1-Modulen umgesetzt. Keine Forschungsquelle erzeugt, kein 1024-Frame-Policyfall und keine Forschungsserie ausgeführt. Die V4-Freigabe und ihre Startmarker bleiben verbraucht und unverändert.

## Umsetzung

- `tools/_s2uc_ura1_rev1_sources.py` und `tools/_s2uc_ura1_rev1_source_reference.py`: getrennte deterministische Erzeugung und unabhängige Rekonstruktion. Zwei Phasen mit 128 Blöcken, je 64 A/B und 64 X/Y; 48/16↔16/48 Kontingenzumkehr. Forschungsnamespace `MCM-URA1-REV1/source/v1`, Testnamespace ausschließlich `MCM-URA1-REV1/neutral/v1`. Kein Parameter für einen verkürzten Forschungswechsel. Ein Forschungspermit setzt eine eigene gültige Vorstartbindung, Berechtigung, START und verifizierten Worker voraus.
- `tools/_s2uc_ura1_rev1_stats.py` und `tools/_s2uc_ura1_rev1_stats_reference.py`: genau ein Primärkontrast Q129–160, Geschichte als statistische Einheit, unveränderte Bootstrapmatrix. Unabhängige Referenz verwendet explizite Framegrenzen statt der Blockformel der Produktion. Übrige Fenster und Diagnosen sind deskriptiv. Kein Herausfiltern kalter, leerer, Ein-Kandidaten- oder schädlicher Ziele.
- `tools/s2uc_ura1_prepare_rev1.py`: eigener Ziel-/Zulassungsbereich, sonst übernommene V4-Integration mit unverändertem Policyexecutor, Archivvergleich, Dateibilanzierung, Terminalabschluss und Budgets. Neue Quelle wird vor dem ersten Arm vollständig unabhängig geprüft und versiegelt. Statistik und Statistikreferenz werden nach vollständiger Serie aufgerufen. Forschung kann ausschließlich das feste 1024-Frame-Rezept verwenden.
- `tools/_s2uc_ura1_rev1_neutral.py`: zwei explizite 32-Frame-Handfälle, Wechsel nach Frame 16, jeweils gespiegelte Hinweise. Die Grenze gehört nur zum Beobachter und wird nicht als Arm-Eingang übergeben. Diese Fixtures werden ausschließlich im neutralen Zweig des Einstiegs benutzt.
- `tools/s2uc_ura1_rev1_qualify.py`, `tools/s2uc_ura1_rev1_seal.py` und `tests/test_s2uc_ura1_rev1.py`: fokussierte Prüfungen und Bindung bestehender Belege. Der Sealer erzeugt keine Forschungsberechtigung.

## Konkrete Tests und Referenzvergleiche

[Unit-Protokoll](unit-tests.json): **18/18 bestanden**, keine übersprungenen Tests. Dauer 30,259 s, Jobpeak 44.716.032 Byte, harte 512-MiB-Jobgrenze.

| IDs | Prüfung und Ergebnis |
| --- | --- |
| S01 | Forschungs-Erzeugung und Quellenreferenz ohne Permit vor dem ersten Quellenhash gesperrt. |
| S02 | Alle 32 neutralen Kennungen zweimal deterministisch erzeugt und unabhängig rekonstruiert; jeweils 1024 Datenframes, korrekte Phasenkontingenzen und konstante Randhäufigkeiten, Quellenformat unter 32 KiB. Diese Daten wurden keinem Policyarm zugeführt und nicht als Forschungsquellen gespeichert. |
| S03 | Manipulierte Wechselposition, Katalogwerte, Ziehungszähler, Zusatzsignal, Neutralflag und Orientierung werden zurückgewiesen. |
| S04 | Rejection Sampling zählt verworfene Ziehungen; 4096-Grenze im Generator und in der unabhängigen Rekonstruktion geprüft. |
| S05–S06 | Ungültige Eingaben, fehlende Kurzwechseloption und ausschließlich neutrale Hashkennungen beider Phasen geprüft. |
| T01 | Kopierte 320000-Byte-Matrix gegen gebundenen Hash und unabhängige Herleitung geprüft; jede Ziehung 16+16 Geschichten gemäß Orientierung; Mutation abgewiesen. |
| T02 | Q128/129 = Frames 511/515 und Q160/161 = 639/643 geprüft. Genau 32 Primärziele je Geschichte; Vorphase 32, späte Nachphase 96, gesamte Nachphase 128. |
| T03 | Künstliche primäre Differenzen +1/4, −1/4 und 0 mit stark abweichenden Fehlern außerhalb des Fensters. Vollständiger Produktions-/Referenzvergleich einschließlich deskriptiver Fenster und Diagnosen bestanden; 1024 Primärziele insgesamt. |
| T04 | Nichtkonstante Bootstrapwerte und unabhängige Quantile; Interpolation 7,5 für das 25%-Quantil von 0/10/20/30. Gegensätzliche Orientierungen +1/4/−1/4 ergeben geschichtet exakt [0,0]. |
| T05 | Positive, negative, nullüberschreitende und nullberührende Intervalle sowie ungültige Reihenfolge. Nullberührung bleibt unentschieden. |
| T06–T07 | Fehlende Geschichte/Ziele, falsche Orientierung, unvollständiger Status, NaN, falscher Hinweis und manipuliertes Statistikergebnis werden zurückgewiesen. |
| T08 | Vollständiger unabhängiger Vergleich zweier nichttrivialer Bootstrapintervalle, die null nur am unteren bzw. oberen Ende berühren; beide unentschieden. |
| E01–E04 | Neues exklusives Ziel und fehlende Berechtigung, kein Resume, Identität übernommener Schutzkomponenten, abgeschaltete neutrale Fehlerhaken im Forschungsmodus und getrennte Forschungsquelle geprüft. |
| G01 | Integrierter Normalabschluss: zwei Geschichten × zwei Arme × 32 Frames = 128 Policyframes, 4 unterschiedliche Arme, `TERMINAL_COMPLETE`, unabhängiger Zustands-/Bestands-/Ticket-/Feedback-/Archivvergleich bestanden. |
| G02 | Integrierter neutraler Admin-Grenzfehler: 2.097.153 > 2.097.152 Byte bei Eintritt in Fall 2. Erwarteter `TECHNICAL_ABORT`, Fall 1 quittiert, kein Fortsetzen oder Ersatz, Worker beendet und Cleanup bestätigt. |

G01/G02 sind in [integration-verification.json](integration-verification.json) überprüft. G01 benötigte 10,120 s, Jobpeak 54.026.240 Byte. G02 benötigte 5,175 s, Jobpeak 51.191.808 Byte; der Workerexit 1 ist Teil des absichtlich ausgelösten Abbruchs. Der Grenzfehler wird im Terminal trotz erschöpften Administrationsbudgets erhalten.

G01 prüfte je Arm und Geschichte 96 äußere und 372 interne Zustandsereignisse, 16 Prognosen und 15 beobachtete Zielrückmeldungen. Bei beiden Fällen lagen am neutralen Wechsel je zwei gültige Fehlerzellen vor. Der Zustand unmittelbar nach Frame 16 und vor Frame 17 war bytegleich; Arm- und Bankidentität blieben erhalten. Auch U/R-Zustände waren dort identisch. Rückmeldungen nach der Grenze wurden weiterhin gegen die bestehende unabhängige Policyreferenz geprüft. Siehe [Fall 1](integration-complete/case-01-continuity.json), [Fall 2](integration-complete/case-02-continuity.json) und [Integrität](integration-complete/neutral-integrity.json).

Der erste Unit-Durchgang hatte einen Fehler in der Testbehauptung: Umkehr einer symmetrischen Vierer-Kontingenztabelle wurde irrtümlich mit Umkehr ihrer Listenreihenfolge gleichgesetzt. Generator und Referenz stimmten überein. Die Prüfung verlangt nun korrekte komplementäre Zellzahlen; der vollständige Test wurde nach dieser Korrektur und Ergänzung von T08 wiederholt. [Erster Durchgang](unit-tests-attempt-01.json) und dessen Log bleiben erhalten. Keine Quelle oder Policy wurde wegen eines Forschungsergebnisses angepasst.

## Übernommene Nachweise und Ressourcen

[inheritance.json](inheritance.json) bindet die vorhandenen Nachweise über den V4-Vorstart `deaae277655ecf078de791190e840d42b2f42fb113288fc903b54b49342ccee3`: alle 891 dort gebundenen Dateien sind unverändert. Die Dateibilanzierungskorrektur bleibt an `a1bdca305b43ceba1e5755cd70557d1eec7b4b0b31352c0425d87902004face4` gebunden. Keine Wiederholung der großen Qualifikationsserie. Die übernommene Bootstrapmatrix hat SHA-256 `0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965`.

[resource-plan.json](resource-plan.json) dokumentiert unveränderte Grenzen: global 57600 s, Worker 54000 s, 3600 s Abschlussreserve, 512 MiB Job, zwei Prozesse; Vorbereitung 8 MiB, Quellen 2 MiB gesamt/32 KiB je Fall, Archive 32 MiB gesamt/512 KiB je gzip, Administration 2 MiB, Closure 1 MiB. Temporäre Dateien und gesamter Export einschließlich Vorbereitung jeweils höchstens 64 MiB; temporäre Dateien zählen zusätzlich im Gesamtexport. Alle übrigen Record-/Dictionary-/Graphgrenzen bleiben unverändert.

Die maximalen endgültigen Kategorien summieren sich auf 45 MiB; die 32 einzelnen Quellencaps auf 1 MiB, die 32 gzip-Caps auf 16 MiB. Alte Belege werden über Dateihashes referenziert, nicht erneut kopiert oder als neue Ausgaben verbucht. Das neue Vorbereitungspaket einschließlich des absichtlichen Admin-Testartefakts bleibt unter 8 MiB; die exakte finale Bytezahl und Bindungsprüfung stehen im [Abschlussbeleg](seal-verification.json).

Die historische V4-Zeitplanung von 50531,048 s und V4-Istdauer von 6727,411 s werden nur als bestehende Orientierung referenziert. Für REV1 wurde keine Vollserienzeit gemessen. Neue Bestandspfade, Archivgrößen und Laufzeiten können weiterhin einen begrenzten technischen Abbruch verursachen. Kurze neutrale Tests sind keine Garantie für einen vollständigen Forschungslauf.

## Vorstart und zukünftiger Einstieg

Neues exklusives Ziel: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-rev1-comparison-16h-01`. Es ist nicht angelegt. `authorization.json` ist nicht vorhanden. Die [Vorstartbindung](prestart.json) und [SHA-256-Datei](prestart.sha256) binden aktuelle Implementierung, Vertrag, Tests und vorhandene Nachweise. Veränderliche Projektübersichten und der nachträgliche Bindungsprüfbeleg bleiben ausdrücklich außerhalb dieser Bindung, um zirkuläre Hashes zu vermeiden.

Exakter **zukünftiger**, erst nach gesonderter Forschungsfreigabe zulässiger Aufruf im Projektverzeichnis:

```powershell
& 'C:\Python314\python.exe' -m tools.s2uc_ura1_prepare_rev1 run 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-rev1-preparation-20261015-01\prestart.json' 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-rev1-preparation-20261015-01\authorization.json'
```

Der Aufruf wurde nicht ausgeführt. Die spätere Berechtigung muss genau die neue Vorstart-SHA referenzieren; eine alte V4-Berechtigung ist nicht verwendbar. Der Einstieg legt das Ziel exklusiv an und verbraucht START vor Materialisierung. Kein Resume und kein automatischer Retry.

## Aussagegrenze und empfohlener nächster Schritt

Belegt sind die neutrale Rezept-/Fensterkorrektheit, unabhängige Statistikvergleiche und der unveränderte Zustandsübergang in kurzen echten U/R-Handfällen. Nicht belegt sind ein REV1-Forschungsergebnis, ein früher R-Vorteil oder eine verzögerte Anpassung durch EMA. Die mechanistische Einschränkung des angenommenen Vertrags bleibt erhalten.

Der Projektleiter prüft dieses Vorbereitungspaket samt Vorstartbindung und entscheidet über den gesonderten Forschungseinstieg. Bis dahin keine Forschungsberechtigung erstellen, keine Forschungsquellen erzeugen und keine Serie starten.
