# Bedienkorrektur neutral qualifiziert

`media-player-usability-20260912-01`: genau einmal **8/8 bestanden**.
Neue Player-Version `s2oe.local-player.v2-explicit-closure`. Keine Änderung
an Rezeptoren, Memory, Decoderprofil oder Ereignisauswahl. Der alte Lauf
bleibt unverändert `CLOSE / INCOMPLETE`; kein Stoppauslöser wird ergänzt.

## Bedienung und Abschluss

- Vorschau ausdrücklich optional und nicht synchron. Während und nach der
  Verarbeitung wird sie pausiert; ihre Play-Bedienelemente sind inaktiv.
  MCM benötigt kein wiederholtes manuelles Play.
- Die Betriebsanzeige verwendet `last_processed`, gesetzt erst nach einer
  erfolgreichen Ereignisrückgabe. Das bereits angeforderte nächste Fenster
  wird nicht als verarbeitet ausgegeben. Durchlauf und Runtimezeit bleiben sichtbar.
- Ein unvollständiger Abschluss zeigt **„Unvollständig: 8/24 Ereignisse“**
  beziehungsweise die tatsächlich erreichte Anzahl. Der gespeicherte
  `INCOMPLETE`-Grund bleibt sichtbar, auch bei leerem Player-Exceptionfeld.
- Künftige Abschlussgründe: `USER_STOP`, `SERVER_SHUTDOWN`, `SOURCE_END`,
  `TECHNICAL_ERROR`, `UNKNOWN` und vollständiger Abschluss `COMPLETED`.
  Ein ausdrücklich angeforderter Stoppauslöser bleibt zusätzlich getrennt
  als `stop_trigger` erhalten. Ursprüngliche Fehlercodes werden nicht ersetzt.
- Der Dateistarter meldet seine Serverbeendigung ausdrücklich. Nicht
  aufgezeichnete Ursachen bleiben unbekannt. Nach geschlossenem Lauf darf
  ein weiterer Stop-Aufruf keinen ursprünglichen Grund umdeuten.

## Tatsächlich geprüft

1. Benutzer-Stopp nach acht neutralen Rückgaben: Anzahl, Grund und letztes Fenster.
2. Serverbeendigung getrennt vom Benutzer-Stopp.
3. Quellenende mit erhaltenem `FRAME_COVERAGE_MISSING`.
4. Technischer Fehler mit erhaltenem Fehlercode.
5. Unbekannter Auslöser bleibt UNKNOWN, nicht rückwirkend USER_STOP.
6. Vollständiger neutraler Abschluss.
7. Tatsächliches HTML-Skript in einer neutralen DOM-Umgebung: Beschriftungen,
   deaktivierte Vorschau, unveränderte Eingabestatusobjekte und kein Start-POST.
8. Typisierte Ablehnung eines unzulässigen Stoppauslösers.

Die sechs Abschlussfälle prüfen jeweils nur eine Belegpublikation und einen
Verifikatoraufruf trotz wiederholter Abschlussanfrage. Abschlussdateien bleiben
unter 1.024 Byte. Der DOM-Test ist keine neue reale Browser-/Videoqualifikation.
Es wurden weder echte Medien gelesen noch eine native Runtime instanziiert.
Keine historische Decoder-, Browser- oder Memorysuite wiederholt.

## Bindungen und Grenzen

Code und Testinventar vor dem einzigen Testaufruf gebunden. Vollständige
neutrale Qualifikationsablage einschließlich Fixtures, Log und Bericht:
65.536 Byte reserviert. Gesamte Qualifikationsmetadaten einschließlich
aktiver Referenzen: 107.518 / 131.072 Byte; Qualifikationsgesamt 405.731 Byte.

Die vorbereitete reale Folge bleibt unverändert: 24 Ereignisse, 20 Formationen,
vier read-only Hinweise vor ihren Formationen. Beide Durchläufe derselben MP4,
ein fortgesetzter Memoryzustand. Verarbeitung und Rückgaben bleiben technisch;
keine semantischen Objektlabels oder Hypothesenanwendung.

| Vollständige reale Vorbilanz | Byte | Grenze |
| --- | ---: | ---: |
| Quellen | 298.213 | 327.680 |
| Metadaten | 112.406 | 131.072 |
| gemeinsame Zusatzhülle | 382.181 | 393.216 |
| Laufgesamt | 3.869.096 | 4.194.304 |
| mit vollständiger zusätzlicher Qualifikationsreserve | 3.934.632 | 4.194.304 |

Alle 50 Fortschritts-/Abschlussalternativen geprüft; Erfolgs- und Fehlerformen
werden nicht addiert. Die physische Budgetdatei ist mitgezählt. Der endgültige
Startlader akzeptiert die Bindung, ohne Server oder Sitzung zu starten.

Neue, unbenutzte Lauf-ID: **media-memory-video-20260912-01**.
Startbindung unter `reports/s2oe/media-player-run-binding-20260912-03`.
Autorisierungsvorlage absichtlich false. Kein neuer Starter oder Lauf gestartet.
Der Entwickler soll den später freigegebenen Lauf selbst starten und überwachen.

Ergebnis-SHA-256:
`d966f8cbb593284340d15f9d212e11cb3dda1168b4ca5649fc27a7d32421156c`.

**RÜCKMELDUNG ERFORDERLICH:** separate Freigabe ausschließlich des neuen
gebundenen Einmalversuchs. Acht echte AV-Ereignisse des alten Laufs bleiben
erreichter Fortschritt; der zweite Durchlauf und Wiederabruf sind weiterhin offen.
