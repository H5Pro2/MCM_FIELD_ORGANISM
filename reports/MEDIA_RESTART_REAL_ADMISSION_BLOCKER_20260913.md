# Reale Checkpoint-Zulassung: Vorstartblocker

Auftrag: DATEIBETRIEB-CHECKPOINT-BEDIENUNG, realer Referenzvergleich mit
Suspend nach Ereignis 19 und einer Wiederaufnahme. Quellenwahl ist geklärt:
die lokale MP4, keine YouTube-Verarbeitung und keine Wiederholung des
historischen 24-Ereignis-Versuchs.

Repository-HEAD: `537109994cf777f8d36cda617aafe12226806c25`, Arbeitsbaum mit
vorhandenen Änderungen. Rein statische Prüfung; kein Lauf gestartet,
keine Lauf-ID verbraucht, keine Medienpayloads gelesen, keine Tests ausgeführt.

## Konkrete Anschlusslücke

- `tools/_media_restart_player.py`, `Player._authorize()`, Zeilen 22–25:
  verlangt `NEUTRAL_CONNECTION` und einen Quellenpfad unter
  `sources/media-restart-neutral`. Andernfalls typisierte Abweisung.
- `tools/_media_restart_checkpoint.py`, `Session.__init__()`, Zeilen 136–138:
  prüft unabhängig denselben neutralen Quellenpfad und weist die gewählte
  Downloads-Datei mit `REAL_MEDIA_RESTART_BLOCKED` ab.
- Die gefundenen dateigebundenen Restart-Aufrufer unter `reports` sind
  Qualifikations-/Vorbereitungsaufrufer, kein realer Zulassungseinstieg.

Aktuelle SHA-256:

| Datei | SHA-256 |
| --- | --- |
| `_media_restart_player.py` | `26cf0afc3c8f7ba7f97a49e9a98add71634adbb11edded11f429a84141222318` |
| `_media_restart_checkpoint.py` | `475851a60e6a3b3f33fca30d7332f8c0888a8cda366ec17f3e70d2c0183541b0` |

Die bestandene neutrale Qualifikation -05 bleibt gültig. Sie ist kein
Nachweis einer bislang fehlenden realen Quellenzulassung. Eine Gateöffnung
allein reicht nicht. Umdeklarieren als neutral, Verschieben der realen Datei
in den Fixturepfad oder Umgehen der Prüfungen ist keine zulässige Lösung.

## Kleinste Korrekturrichtung

Eine explizite, versionierte reale Zulassungsbindung für genau den bereits
gebundenen Dateihash, FULL-Modus, 20 Ereignisse und einen Restore ergänzen;
beide genannten Prüforte konsistent daran anschließen. Ein dateigebundener
Aufrufer muss Referenz, Suspend-19-Prozess und frischen Restore steuern sowie
Code-/Quellenbindung und gemeinsame Bilanz vor Start prüfen. Die neue
Zulassungsgrenze benötigt gezielte Prüfdeckung, keine Wiederholung der
historischen acht Tests. Memory, Decoderregeln und Limits bleiben unverändert.

Diese Änderung wurde nicht implementiert und nicht als bereits qualifiziert
ausgegeben. Die reale Einmallauffreigabe ist verstanden, ihre technische
Startvorbedingung mit qualifiziertem Anschluss ist derzeit nicht erfüllt.
Gates wurden nicht geöffnet. Kein Funktionsbefund und kein Retry.
