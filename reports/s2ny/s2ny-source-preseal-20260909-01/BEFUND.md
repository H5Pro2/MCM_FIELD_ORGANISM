# S2-NY: einmalige rezeptorfreie Vorversiegelung

ID: `s2ny-source-preseal-20260909-01`.
Status: **S2NY_SOURCES_PRESEALED**, anschliessend **S2NY_PRESEAL_VERIFIED**.
Ein Vorversiegelungsaufruf und genau eine unabhaengige read-only
Bindungspruefung; Exit-Code 0. Kein Retry oder Ersatzreiz.

## Erzeugung und Bindung

Nach [24/24 neutralen Quellenpruefungen](../s2ny-source-binding-qualification-20260909-01/BEFUND.md)
wurden alle 30 PCM-Fenster des unveraenderten
[NY-Plans](../../../docs/S2NY_STATISCHER_PLAN_PRAEFIXGEBUNDENE_ANWENDBARKEIT.md)
einmal in versiegelter Reihenfolge erzeugt: sechs Fuenferfolgen, jeweils
4.800 Samples, PCM_F32LE mono, 48.000 Hz. Insgesamt 576.000 erzeugte Byte,
maximal ein 19.200-Byte-Payload gleichzeitig; nach Hashbildung freigegeben.
Keine Rohpayloadablage und keine Deduplizierung.

Die getrennte [Ausfuehrungswurzel](execution-plan.json) bindet alle Rezepte,
Payload-/Rezept-/Quelldigests, native Fenster/Indizes, 18 Prognosestellen,
zwoelf LOCAL-Stellen, Formeln, Ressourcen und zwei historische Freeze-Payloads.
Die [Evaluationswurzel](evaluation-plan.json) allein traegt Sollhistorien,
Verlaufskategorien und die 20 Kriterien R/L/P/W. W01-W08 sind zu pruefende
Verlustprognosen, weder garantiert noch technische Startgates.

Die [Vorregistrierung](preregistration.json) wurde vor der ersten NY-Erzeugung
publiziert. Lokale Synthesezeit, Gruppen-/Phasenfolge, Nenner 1024 und einmalige
Float32-Rundung nach dem Gain bleiben unveraendert. Keine Eingangsabschwachung,
Clipping, Quellenanpassung oder ergebnisabhaengige Auswahl.

## Historische Freeze-Herkunft

H1/H2 stammen unveraendert aus dem bereits abgeschlossenen NX-Lauf;
beide FROZEN-Payloads, ihre CLOSED-Nachfolgebindungen, Quellkettenbezeichner,
Ergebnis-/Verifikations-/Dateidigests und das Halbprofil sind gebunden.
Keine Koeffizienten aus NY-Rezepten, keine NX-Wiederholung, kein Owneraufruf.
Die gespeicherten alpha-Werte wurden nur gelesen und in Binary64-Hex gebunden,
nicht neu geschaetzt oder funktional angewendet.

| Bindung | Digest |
| --- | --- |
| Historisches NX-Ergebnis | `c8b478c00ce4a83ecd7e8be138a8ba0aada0c52687a4845c7bc086272d71afd4` |
| Historische NX-Verifikation | `4fe83068ab7382a60730f6dfe987fca271c8d64bd98f8bdfa845d9dc0ffabed9` |
| H1 FROZEN | `e2ac7055d38dfbda06dbd0073506df8251e4b8a7fd997e6253f78e3077483e45` |
| H2 FROZEN | `3ce3c6471d5bd71910cd59ca95e39d7e95de05822ee6a82b6e8236138f190205` |
| NY-Freeze-Import | `a897b32ef204947af6e08ef5770e23c921b422da73b06b92d9bf08189c77c07f` |
| Halbprofil | `4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f` |

CPython 3.14.4 Windows x64, `C:/Python314/python.exe`; Interpreterhash
`7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a`.
Built-in-`math` ist durch Herkunft und Built-in-Mitgliedschaft bestaetigt.
Vollstaendige Generator-AST-/Datei-, Interpreter-/DLL- und Profilbindungen
stehen in der Ausfuehrungswurzel. NumPy wurde nicht importiert.

## Vollstaendige Bytegleichheitsgruppen

Alle folgenden Quellen bleiben trotz Bytegleichheit getrennt gebunden.
Keine Gleichheitsgruppe wurde entfernt oder durch neue Quellen ersetzt.

| PCM-SHA-256 | Quellen (jeweils Praefix `ny-`) |
| --- | --- |
| `64a6bea65f22e38bc82eed466b993691bbc7e94a188a8a8723fbd7f417f111a2` | s06-w03, s06-w04 |
| `6dda74c2c4f5dfe640f3df45544e8bcf1e11537689549143693814ce6f39a545` | s01-w01, s02-w01, s03-w02, s04-w00, s04-w01, s04-w02, s04-w03, s04-w04, s05-w01, s05-w03, s06-w01 |
| `77661c14870f56073e6bf8b2633c64a564127d31043e1099e9ccacf71565f063` | s01-w00, s02-w00, s03-w00, s05-w00, s06-w00 |
| `a54f2bcb88997542663c24742c1f1f298d77829461f763ee08f40e9738fa9fb9` | s02-w02, s06-w02 |
| `ffaafa322e3c67950332eeccae76a161f242970c7c6a68127df35bbd7b855580` | s01-w02, s05-w02 |

## Unabhaengige lesende Pruefung

Der [Pruefbeleg](verification.json) bestaetigt einmalig Vollstaendigkeit,
Quellen-/Rezept-/Zeit-/Indexformen, getrennte Wurzelbindung, Qualifikation,
Code-/Umgebungs-/Profilidentitaet, Freeze-Import und Kollisionstabellen.
Quellen und Prognosestellen werden unabhaengig aus den literalen Bindungen
rekonstruiert. Formeln/Budgets sind geteilte feste Metadaten, keine hier
ausgefuehrten Funktionsberechnungen. Die drei Artefaktdateien sind vor/nach
dieser Pruefung bytegleich; alle gebundenen Quellhashes unveraendert.

Keine PCM-Regeneration, FFT, Rezeptor- oder NJ-Wiederholung. Payloadhashes
werden lesend gebunden, nicht durch zweite Synthese numerisch nachgerechnet.
Die historische NX-Lernarithmetik wird ebenfalls nicht wiederholt.
Diese Bindungspruefung beweist keine historische CPU-Aufrufordnung eines
kuenftigen NY-Praediktors und keine geeignete Historienempfehlung.

| Artefakt | Byte | Kanonischer Digest |
| --- | --- | --- |
| execution-plan.json | 50.379 | `17ecbda94c20fdc30cf49007fef12d326cbe628e3d78cb49d8dc5c7d341e43da` |
| evaluation-plan.json | 3.252 | `d1ade159373765a083b83eaf427db56aa939afe23324ab6803db713bf836cd16` |
| seal.json | 5.712 | `7c3fc3c302d1be1fec16e688c7c8d5c53956132ec939aeac56f7b41706e36cc3` |
| verification.json | 2.417 | `4a387ba5ae260d099859e4c174ba8e355cf21d9efd949beaf34802752cdb43b6` |

Vorregistrierung: 46.676 Byte. Alle Metadatenhuellen unter 65.536 Byte,
Pruefbeleg unter 262.144 Byte; keine Grenzerhoehung.

## Aussagegrenze

Bestaetigt ist ausschliesslich die rezeptorfreie Quellen-/Freeze-Bindung.
Alle Rezeptor-, NJ-, Lern-, Empfehlungs-, LOCAL-, Prognose-/Fehler-, Memory-,
Feld-, Kontext- und Runtimeaufrufe bleiben **0**. Kein Funktionsbefund.

Kleine spaetere Unterschiede zu LOCAL muessen als absolute MAE- und
Gewinndifferenzen berichtet werden. Binary64-Vorteile allein belegen keine
allgemeine Robustheit; keine Toleranz ergaenzen. W-Nichteintreten ist ein
regulaerer Befund, nicht Grund fuer einen Abbruch oder Nachjustierung.

Gates durchgehend `False`; ME/MI und Systemintegration gesperrt. Historische
Belege, Versiegelungen, fremde Aenderungen und Bootstrap unveraendert.
Keine separate Rezeptormaterialisierung oder reale Prognose freigegeben.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser Bindungsbelege
und der separaten Entscheidung ueber den kausalen Empfehlungsanschluss weiter.
