# ZW1: einmaliger gebundener Forschungsversuch abgeschlossen

Workflow 22e3ae79-3fc0-40bf-8c6c-45ed44af47fc · 2026-10-18.
Status: TERMINAL_COMPLETE; kein Retry, Resume, Ersatzlauf, Tuning oder Umfangszuwachs.

## Primärer Befund und Aussagegrenze

Einziger Primärvergleich: (E−F)A − (E−F)B auf allen 511 beobachtbaren Zielen
je Geschichte, vollständige Quellenpaare als statistische Einheit.
16 Paare, 32 Geschichten, 16352 Bedingungs-Zielpaare und 32704 Armfehler.

Mittelwert: **-67/32704 = -0.0020486791**.
95%-Perzentilintervall: **[-123/32704, -11/32704] = [-0.0037610078, -0.0003363503]**.
Gebundenes Urteil: **NEGATIVE_INTERACTION**. Das Intervall liegt vollständig unter null.
Die unabhängige Statistikreferenz stimmt bei allen 16 Paardifferenzen, Mittelwert und
Intervall exakt überein. Die feste 10000×16-Bootstrapmatrix blieb unverändert;
Resampling ganzer Paare, acht je Orientierung, lineare Perzentilinterpolation.
Keine zusätzliche Bootstrapberechnung im Abschlussaudit.

Beobachtet wird eine gerichtete Interaktion zugunsten eines relativ kleineren
E−F-Fehlers in A als in B innerhalb dieser zweiphasigen Quellenfamilie.
Dies ist kein separater Signifikanznachweis für einen absoluten E-Vorteil in A
oder einen Schaden in B. Keine zusätzlichen bedingungsweisen Tests oder Intervalle.
Es ist auch kein isolierter Kausalnachweis einzelner Auffrischungsoperationen:
Wiederkehrlängen, lokale Häufigkeiten, Promotionen, Verdrängungen und mittelbar
Fortsetzungsabhängigkeiten ändern sich gemeinsam mit dem Quellengesetz.
Kein Nachweis allgemeiner Intelligenz, Semantik oder feldinterner Memory.

Nur deskriptive Zerlegung aus den bereits geprüften Fehlerreihen:

| Bedingung | Ziele | mittleres E−F | E besser | F besser | gleich |
|---|---:|---:|---:|---:|---:|
| A | 8176 | -51/32704 = -0.0015594423 | 195 | 144 | 7837 |
| B | 8176 | 1/2044 = 0.0004892368 | 262 | 278 | 7636 |

Paardifferenzen des einzigen Primärvergleichs:

| Paar | Exakt | Dezimal |
|---|---:|---:|
| 1 | 2/511 | 0.0039138943 |
| 2 | 2/511 | 0.0039138943 |
| 3 | -9/1022 | -0.0088062622 |
| 4 | -1/1022 | -0.0009784736 |
| 5 | 1/511 | 0.0019569472 |
| 6 | -9/2044 | -0.0044031311 |
| 7 | -2/511 | -0.0039138943 |
| 8 | -1/2044 | -0.0004892368 |
| 9 | 0 | 0.0000000000 |
| 10 | -15/2044 | -0.0073385519 |
| 11 | -5/1022 | -0.0048923679 |
| 12 | -1/292 | -0.0034246575 |
| 13 | -3/1022 | -0.0029354207 |
| 14 | -9/2044 | -0.0044031311 |
| 15 | -1/2044 | -0.0004892368 |
| 16 | -1/2044 | -0.0004892368 |

## Zulassung und tatsächliche Ausführung

Unmittelbar vor Ausführung bestätigte der tatsächliche validate_binding-Validator
2995 Dateien und 98 Qualifikationsartefakte, einschließlich sämtlicher Dateien
unter experiments/zw1. Berechtigung, Verbrauchsmarker und Ziel fehlten zuvor.
Die Berechtigung wurde exklusiv erstellt mit kind=ZW1_RESEARCH_ONCE,
allow_research=true und Vorstart-SHA:
`28a1b008daaa9663a3f7ce3f403dc631526c0f7f78c2cebe82f8d89962e3dc13`.
Der Supervisor prüfte die Bindung nochmals beim Start. Genau ein Aufruf wurde
unverändert aus prestart.json:call ausgeführt, einschließlich -B:

```powershell
& 'C:\Python314\python.exe' '-B' '-m' 'experiments.zw1.prepare' 'run' 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\zw1-research-preparation-20261018-01\prestart.json' 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\zw1-research-preparation-20261018-01\authorization.json'
```

Arbeitsverzeichnis: C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace.
Exklusives Ziel: reports/s2uc/zw1-comparison-16h-01.
START.json und CONSUMED.json sichern den Verbrauch. Die Berechtigung ist verbraucht;
eine erneute Zustellung erlaubt keinen weiteren Start.

Namensraum MCM-ZW1/source/v1. Alle 32 Bedingungsquellen wurden vor dem ersten Arm
unabhängig rekonstruiert, geprüft und gemeinsam versiegelt. Der aktuelle Hashabgleich
bestätigt alle 32 Quellen und das Quellenmanifest:
`dd7652c3a5f3fb13b1c23feb4df1a9d61a35fc2ede68ba6fb2c3604f5e8de18e`.
Matrix-SHA: `cd452bee76ea2b1b64c920afdd9c70211e5ba7abc7207049f4e7e280e5703f6c`.

Tatsächlich 16 vollständige Quellenpaare, 64 verschiedene frische Policy-Arme,
64 Live-Referenzen und 64 erfolgreiche Archivrekonstruktionen. Keine Zusatzarme.
Die 32 Bedingungs-Archivprüfungen umfassen jeweils E und F. A/B wurden seriell
verarbeitet. Alle 16 Paarquittungen bestätigen vier verschiedene Arme, beide
Bedingungsabschlüsse und Cleanup. Keine Zustandsübertragung zwischen Armen.
Nur kompakte Fehlerreihen wurden paarübergreifend für die Statistik gehalten.

## Prüfbelege und Cleanup

- terminal.json: TERMINAL_COMPLETE; Worker beendet, Exitcode 0; 64/64 Arme geschlossen;
  aktives Paar null, keine erste oder nachfolgende Fehlerursache.
- result.json und worker.json: vollständige Serie, reference_equal=true, retry_allowed=false.
- pair-01-receipt.json bis pair-16-receipt.json: alle Ziele 3,5,...,1023,
  A/B vollständig, PASS_DELTA_INTEGRITY, bestätigtes Cleanup.
- case-01-summary.json bis case-32-summary.json: je zwei Policy-, Live- und
  Archivreferenzen; vollständige Archivprüfung und Ressourcenwerte.
- statistics.json und statistics-reference.json: exakte Übereinstimmung.
- closure.json: 151 ursprüngliche Abschlussdateien per Größe und SHA erneut bestätigt.
- verification.json: abschließender Bindungs-, Mengen-, Quittungs-, Ressourcen- und
  Erhaltungsabgleich PASS. Keine Wiederholung von Policy, Quellen oder Archiven.

Cleanupzustände getrennt: Workerende bestätigt; Arm-/Codec-Cleanup bestätigt;
Dateicleanup bestätigt; keine Partialdateien. Keine Teilserie und kein Teilurteil.
Die früheren 11 Integrationsprüfungen und fünf neutralen Szenarien wurden übernommen,
nicht erneut ausgeführt. Der neue Beleg ist ausschließlich dieser freigegebene Lauf
mit den darin vorgesehenen Live-, Archiv- und Statistikreferenzen.

## Gemessene Ressourcen

Supervisorlauf einschließlich Worker und Abschluss: 4456.266879 s
(74.27 min), unter 54000 s Worker-/57600 s Gesamtgrenze;
3600 s Abschlussreserve unverändert. Gemeinsamer harter Windows-Job mit höchstens
Supervisor und einem Worker. Jobpeak 399138816 Bytes
(380.65 MiB), Prozesspeak
306810880 Bytes, Jobgrenze 536870912 Bytes.
Die Grenzen wurden weder geändert noch umgangen.

Quellen insgesamt 238048 Bytes; Archive insgesamt 5359890 Bytes.
Maxima pro Bedingung: gzip 180215, encoded 1068105, Dictionary 1013464 Bytes;
14758 Knoten, 135464 Kanten, 10303 Indizes, 14 Collections, Record 16845 Bytes.
Observer-Daten 4973015 Bytes, Mechanismen-Daten 77187 Bytes.
Policymaxima: zusätzlicher Pythonheap 5518 Bytes, Receipt 795 Bytes,
UTF8-Obergrenze 1590 Bytes, gepackte Bank 416 Bytes, höchstens zwei Ausgabeslots;
gebundene konservative kombinierte Obergrenze 18. Einzelmessungen sind nicht mit
einem vollständigen Prozesspeak gleichzusetzen; dafür dient die Jobmessung.
Alle gebundenen Grenzen bestanden in genau dieser Serie. Daraus folgt keine
allgemeine Speicherverträglichkeitsgarantie für andere Quellen oder längere Fälle.

## Erhaltung, Lieferung und nächster Schritt

Historische ER1-v2-Forschungslieferung (139 Dateien), ER1-v1-Abbruch (43),
unabhängiger ER1-Zeugenaudit (41) und ZW1-Neutralpaket (53) per Liefermanifest
unverändert bestätigt. Historisches ER1-Urteil bleibt INCONCLUSIVE.
Die Vorstartbindung ist auch nach dem Lauf gültig. Ausführbarer Code unverändert.
Neu sind nur Berechtigung/Verbrauchsmarker, Forschungsartefakte und diese Lieferung;
die drei Projektübersichten erhalten den neuen Stand. delivery-closure.json bindet
zusätzlich Terminal, ursprüngliche Closure, verification.json und diesen Bericht.

Empfohlener Anschluss: Projektleiter bewertet die gerichtete Interaktion mit der
festgelegten Aussagegrenze. Falls eine mechanistische Vertiefung erforderlich ist,
wäre ein eng begrenzter unabhängiger Audit bereits vorhandener ZW1-Archivzeugen
zu Erhaltung, Auffrischung und Verdrängung sinnvoll. Kein neuer Policylauf und keine
Auswahl allein günstiger Zeugen; Vergleich beider Bedingungen und beider Arme.
Dies ist ein Vorschlag, keine neue Freigabe und kein hier ausgeführter Audit.
