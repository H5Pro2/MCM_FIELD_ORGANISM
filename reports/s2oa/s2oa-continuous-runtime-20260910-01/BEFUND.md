# S2-OA: einmaliger Hauptlauf technisch abgebrochen

Lauf-ID: `s2oa-continuous-runtime-20260910-01`.
Genau ein `run_main_once`-Aufruf, danach genau eine unabhaengige read-only
Verifikation in einem separaten Python-Prozess. Kein Retry, keine Korrektur,
keine weiteren Tests oder Analysen. Keine Funktionsauswertung.

## Technischer Befund

Status **NOT_EVALUABLE**. Fehler bei `e01`, Quelle `oa-e01-visual`,
Phase `NJ_CONTACT`, Klasse `S2LMStreamError`, Code `OA_TECHNICAL_ERROR`.
Die Phase umfasst hier die Bindung eines visuellen Hinweises; sie belegt
weder eine ausgefuehrte NJ-Projektion noch einen numerischen Normalformfehler.
Der genaue verletzte Vertrag ist durch diesen Beleg nicht lokalisiert.

Vorher wurden Qualifikationen, administrative Referenzen, historische
Versiegelung, Quellen-, Profil-, Code- und Umgebungsbindungen geprueft.
Die Materialisierung erreichte genau einen hashbestaetigten RGB-Payload und
eine zurueckgekehrte visuelle Analyse. Die nachfolgende Ereignisbindung
scheiterte; kein vollstaendiges Ereignismaterialisat wurde veroeffentlicht.

| Zaehler | Erreicht | Gebunden |
| --- | ---: | ---: |
| Payloads hashbestaetigt | 1 | 48 |
| Direkte Audioanalysen | 0 | 22 |
| NJ-Projektionen | 0 | 22 |
| Visuelle Analysen | 1 | 26 |
| Vollstaendig materialisierte Ereignisse | 0 | 28 |
| Runtimeereignisse / Formationen | 0 / 0 | 28 / 20 |
| Feldkontakte / Scanbelege | 0 / 0 | 8544 / 16 |

Keine Runtime initialisiert, kein Memory-/Feldzustand fortgeschrieben.
Letzter Runtime-Snapshot und finaler Snapshot sind null. Deshalb war kein
Runtime-close aufzurufen. Haupt-, Neutral- und Quellengate sind False.
Rohpayload nicht gespeichert; keine Deduplizierung oder Ersatzquelle.
Die beiden Python-Aufrufe endeten mit Exit-Code 0: Das bestaetigt die
Belegerzeugung, nicht einen erfolgreichen Systemlauf.

## Belege und Aussagegrenze

[Gesamt-/Fehlerbeleg](record.json), [Aufrufbeleg](invocation.json),
[read-only Pruefbeleg](verification.json).
Ergebnisdigest:
`143ec9db2643475345ca2b9900151172ffd67ff21bff4b64a30e28b50627f180`.
Verifikationsdigest:
`c948df447ff726842807bb6b94a425977dc56bd7b80cc53e7250c157415e1baf`.
Der Verifikator akzeptiert die Fehlerform, Status bleibt NOT_EVALUABLE,
`evaluation_allowed=false`. Kein zweiter Verifikationsaufruf.

q01 wurde nicht bis zum Abruf erreicht; q02, q03, q04, q05, q06, q07 und
q08 wurden nicht verarbeitet. Es gibt keine Hypothesen oder Enthaltungen
als fachliche Ergebnisse. Saemtliche vorhergesagten Uebergaenge f01..f20,
Stabilisierung, B4-Verdraengung, Fast-Ablauf, visueller B-Abruf und Slow-
Ersetzung sind in diesem Lauf ungeprueft. Insbesondere kein q05-Beleg und
keine aktuelle q07-Verfuegbarkeit; keine Aussage zu gleicher Slot-ID und
neuer Generation aus diesem realen Lauf. Fruehere neutrale Qualifikationen
bleiben mit ihrem eigenen Umfang unveraendert erhalten.

## Tatsaechliche Artefaktbilanz

Bytes kanonischer Dateien bzw. des Abschlussberichts, kein Prozesspeak:

| Klasse / Datei | Byte |
| --- | ---: |
| Referenzierte administrative und Qualifikationsmetadaten | 47135 |
| record.json | 3131 |
| invocation.json | 321 |
| Dieser Abschlussbericht | 4253 |
| Metadaten zusammen, Grenze 65536 | 54840 |
| Vollstaendige historische Quellenartefakte | 162321 |
| NJ-/Formations-/Generationszusatzbelege | 0 |
| Gemeinsame Zusatzhuelle, Grenze 262144 | 162321 |
| Administrative Vorverifikation | 1580 |
| verification.json plus verification.claim | 275 |
| Verifikation zusammen, Grenze 262144 | 1855 |
| Auswertung | 0 |
| Gesamt einschliesslich Referenzen/Abschluss, Grenze 4194304 | 219016 |

Die vollen kuenftigen Reserven bleiben unveraendert. Historische Dateien
werden voll mitgezaehlt, nicht rueckwirkend als budgetkonform umgedeutet.
Keine fachliche Teilauswertung oder Umdeutung des technischen Abbruchs.

RUECKMELDUNG ERFORDERLICH: Analystenentscheidung ueber eine eng begrenzte
statische Klaerung der visuellen Ereignisbindung vor der Runtime. Keine
Korrektur oder weitere Ausfuehrung aus diesem Bericht ableiten.
ME/MI gesperrt, Prognosezweig ruhend; historische Belege und Bootstrap
unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenpruefung des technischen
Abbruchbelegs und der Entscheidung ueber die lokale Vertragsklaerung weiter.
