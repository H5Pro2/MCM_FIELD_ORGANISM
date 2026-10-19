# Realer Checkpointvergleich vom 19.09.2026

**Gesamtstatus NOT_EVALUABLE; einmaliger Aufruf, Exitcode 1.**
Die Lauf-ID `media-restart-real-20260913-03` ist verbraucht. Keine Korrektur,
kein Retry, keine Parameter- oder Grenzanpassung während oder nach dem Lauf.
HEAD `537109994cf777f8d36cda617aafe12226806c25` plus qualifizierte lokale Quellen.
Bindung: SHA-256 `ef2af7f3e21e52b0e241dc2c218f592629b164c7a2c59fce4a9bec4f79f7800f`.
Separate Autorisierung: `../media-restart-real-20260913-03-binding/authorization.json`,
SHA-256 `ddf7a594bece6ad5eedbcf97dc2e040feb6c791e89a7e87bc57462d4b0953447`.
Code, aktive Referenzen, unbenutzte Ausgabe und MP4-Hash wurden vor Start geprüft.

## Erreichte Verarbeitung

| Arm | Prozess | Abschluss | MCM-Ereignisse |
|---|---:|---|---:|
| Referenz | 13784 | RECORDING_COMPLETE | 20 |
| Suspend | 4336 | SUSPENDED | 19 |
| Restore | 15296 | RECORDING_COMPLETE | 20 |

Alle drei Prozessbelege bestätigen closed=true und beide Gates False.
Referenz und fortgesetzter Arm erreichen jeweils beide EOF: letzter
Video-PTS 800800, Audioende Sample 1282048. Je vollständigem Arm 20 Audioanalysen,
20 NJ-Projektionen, 20 visuelle Analysen; Restore übernimmt die 19 bisherigen
Formationen und fügt eine hinzu. Replay erzeugt keine zusätzliche MCM-Erfahrung.

19 Replayfenster und Zielauswahl sind einzeln bestätigt. Gesamtzeit laut
letztem Beleg: 59,116940499981865 Sekunden; längste Anfrage rund 2,44 Sekunden.
30 Sekunden je Anfrage und 600 Sekunden insgesamt wurden nicht geändert.
Initialisierung, EOF und Schließen sind getrennte Schritte.

## Verifikation und fehlende Auswertungsveröffentlichung

Genau eine unabhängige read-only Gesamtverifikation wurde abgeschlossen:
`restore20-verification.json`, RECORDING_COMPLETE, evaluation_allowed=true.
Sie bestätigt core_equal, selections_equal, final_field_equal, alle 20
Ereigniszeilen sowie replay_verified mit 20 Bestätigungen.
Verifikationsdigest:
`3cce614120ab68457f26f67ceff6d54627e76690bea0b4351ca43b7db93ee17e`.
Diese Aussagen sind aus dem gespeicherten Beleg gelesen, nicht neu verifiziert.

Der getrennte Auswerter wurde danach genau einmal aufgerufen. Seine Publikation
scheiterte mit `PUBLICATION_POSITION_MISSING`, Phase EVALUATION, completed=20:
Kategorie native, Rolle `evaluation.json#/rows/0`. `failure.json` bleibt der
maßgebliche Fehlerabschluss. Es wurde weder evaluation.json noch result.json
veröffentlicht. Kein CONFIRMED-Auswertungsstatus wird nachträglich ersetzt.
Die gespeicherte Fortsetzungsgleichheit bleibt ein positiver technischer
Einzelbefund; der vollständige Abschlussvertrag ist nicht erfüllt.
Kein Decoder-, Memory- oder Größenfehler aus dieser Meldung ableitbar.

## Tatsächlicher Decoderverbrauch

| Konto | Gelesene Byte | Pakete | Videoframes | Audioframes |
|---|---:|---:|---:|---:|
| Referenz gesamt | 333.993.752 | 2.057 | 801 | 1.252 |
| Vergleich vor Suspend (prior) | 327.529.918 | 1.948 | 758 | 1.186 |
| Restore-Replay zusätzlich | 327.529.918 | 1.948 | 758 | 1.186 |
| Restore regulär einschließlich EOF | 6.463.834 | 109 | 43 | 66 |
| Vergleich kumulativ | 661.523.670 | 4.005 | 1.559 | 2.438 |

Kumulative Vergleichsgrenzen: 2.003.962.512 Byte, 8.192 Pakete, 2.048 Video-
und 4.096 Audioframes. Vollständige Frameevidenz, kein unbekannter Restverbrauch.
Framegrenzen bleiben Post-Batch-Abbruchgrenzen, keine Garantie interner Codecarbeit.
Separat: einmalige administrative MP4-Hashprüfung vor Start las 83.498.438 Byte;
sie ist nicht Teil der Decoderkonten. Referenz und Vergleich sind getrennte Konten.

Quelle unverändert wiederverwendet: `17138816-uhd_3840_2160_30fps.mp4`,
83.498.438 Byte, SHA-256
`df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
Keine Quellenregeneration oder zusätzliche Rezeptorvorprüfung.

## Bilanz und Aussagegrenze

Die vollständige physische Belegung einschließlich aller aktiven Referenzen,
dieses Berichts, Autorisierung und Abschlussbilanz steht in balance.json.
Restreserven bleiben separat gezählt; keine Belegbudgetverletzung.
Keine zugehörigen Prozesse verblieben, Gates False. Historische Befunde
unverändert. Belegt ist die kontrollierte technische Wiederaufnahme dieser
Videowahrnehmung; keine Objekterkennung, allgemeine Videoerinnerung oder Crash-Recovery.
