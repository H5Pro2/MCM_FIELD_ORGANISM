# Realer Dateineustartvergleich: technischer Abbruch

**media-restart-real-20260913-01: NOT_EVALUABLE.**
Genau ein Hauptaufruf; kein Retry, keine Code-, Quellen- oder Grenzänderung.
Die ID ist verbraucht. Quelle: unveränderte lokale MP4, bereits zuvor
untersucht; kein unabhängiger neuer Korpus und keine YouTube-Verarbeitung.

## Tatsächlich erreicht

Der Referenzarm hat 20 Ereignisse verarbeitet. Der gespeicherte Fortschritt
nennt file-event-20 und 20 Feldschritte. Beide Streams erreichten EOF;
20 Medienfenster wurden ausgewählt. Der vollständige Referenz-Gesamtbeleg
wurde jedoch nicht veröffentlicht. Diese Fortschrittsangaben ersetzen
keine unabhängige technische Gesamtverifikation.

Suspend-19 und Restore wurden nicht gestartet. **Null Gesamtverifikationen,
null fachliche Auswertungen. Fortsetzungsgleichheit bleibt ungeprüft.**

## Vollständig erhaltener Primärfehler

Quelle: reference/failure.json, 3.368 Byte. Code MEDIA_STORE_BUDGET,
Phase DRAIN, Ereignis/Fortschritt 20. Nicht als Memoryfehler interpretieren.

| Beitrag der abgewiesenen Publikation | Byte |
| --- | ---: |
| Bereits belegte Metadaten | 102.021 |
| Neuer Metadatenbeleg | 3.872 |
| Zwei Veröffentlichungskopien zusammen | 7.744 |
| Log-/Abschlussreserven | 16.384 |
| Primärfehlerreserve | 8.192 |
| Prospektive Summe | **134.341** |
| Grenze | **131.072** |
| Überschreitung | **3.269** |

Nur die Metadatengrenze wurde hier verletzt. Prospektives Gesamtvolumen:
1.639.305 Byte gegenüber 4.194.304. Der äußere REAL_CHILD_FAILED und der
Kindprozessstatus REAL_STAGE_FAILED sind Folgefehler; sie ersetzen nicht
den gespeicherten Primärfehler. Vollständiges Kindprozesslog: reference.stderr.

## Tatsächlich gezählte Decoderarbeit

- Containerlesemenge einschließlich Hashlesen: **333.993.752 / 2.003.962.512 Byte**.
- Videoframes: **801 / 2.048**; Audioframes: **1.252 / 4.096**.
- Pakete: **2.057 / 8.192**. Replay: in allen Konten null.
- Worker geschlossen; gespeicherter Worker-Exitcode 1. Keine daraus
  abgeleitete zusätzliche numerische Fehlerursache.
- Beide Stream-EOF-Marker sind True. Spitzen-Job-Commit: 604.504.064 Byte.

Der Elternaufruf endete mit Exitcode 1. Eine anschließende Prozessabfrage
fand keinen laufenden Python-Prozess des Dateieinstiegs oder Restartworkers.
Der Fehlerbeleg hält gate=False fest; die Einstieg-finally-Blöcke setzen
beide Gates zurück. Keine erneute Sitzung zum Schließen geöffnet.

## Bindung und Abschluss

Codeinventar und aktive Nachweise vor Start geprüft. 26 neutrale
Fixturedateien verbleiben unverändert im digestgebundenen Archiv und sind
keine realen Eingänge. Alle Pflichtnachweise und die fünf Bindungsdateien
zählen weiterhin vollständig. Anfangsbilanz einschließlich Reserven:
114.548 Byte Metadaten; administrative Publikationsspitze: 122.350 Byte.
Dies war ausdrücklich keine Garantie für die tatsächlichen Laufbelege.

balance.json enthält die vollständige Istbilanz einschließlich dieses
Berichts und ihrer eigenen Größe. Fehlbeleg und historische Nachweise
bleiben unverändert. Keine Korrektur oder neue Laufvorbereitung angeschlossen.
