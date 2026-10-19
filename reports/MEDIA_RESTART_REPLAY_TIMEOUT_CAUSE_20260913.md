# Statische Einordnung des Restore-Timeouts

Bezug: `media-restart-real-20260913-02`, unverändert `NOT_EVALUABLE`.
HEAD `537109994cf777f8d36cda617aafe12226806c25` plus laufgebundene lokale
Quellen. Keine Projektimporte, Medienverarbeitung, Tests, Nachsimulation oder
erneute Gesamtverifikation. Historische Laufdateien und deren Bilanz unverändert.

## Belegte Aufrufgrenze

`tools/_s2oe_decoder_worker.py:357` übergibt `select` als einen RPC.
`_rpc():292` bindet eine Sequenznummer und setzt nach Schreiben/Flush eine
Deadline von 30 Sekunden (`:302`). Nur eine Abschlussantwort beendet das
Warten. Phasenmeldungen werden in `_read():278` separat abgefangen; sie
aktualisieren lediglich `last_confirmed_phase`, nicht die Deadline.

`tools/_media_restart_work.py:184`, `Decoder.select()`, bündelt beim ersten
Restoreaufruf alle `window` früheren Auswahlen über `super().select()` und
`release()` in derselben Anfrage. Hier: `select(repeat=1, window=19)`,
Replay der Fenster 0 bis 18, danach Auswahl von Fenster 19 für Ereignis 20.
Es gibt dazwischen keine RPC-Antwort. Die Grenze gilt nicht je Packetdecode
oder Replayfenster und auch nicht für den gesamten mehrphasigen Versuch.

Zum ersten select gehören außerdem Quellenprüfung und Öffnen beider
Container (`_media_restart_work.py:155`, `begin`; `CountedFile:73`).
Die normale Auswahl führt Video- und Audioverarbeitung durch
(`tools/_s2oe_media_decoder.py:149`). Auch im Replay wird für die
durchlaufenen Videoframes RGB konvertiert (`:184`), danach freigegeben.
Das ist reale Decoderarbeit, aber keine MCM-Formation oder Rezeptorerfahrung.

## Historische Evidenz und fehlende Zeitauflösung

`restore20/failure.json`: `DECODER_TIMEOUT`, MATERIALIZATION, completed=19;
letzte bestätigte Meldung `sequence=2`, VIDEO / packet_decode. Im Code ist
Sequenz 1 init, Sequenz 2 hier der erste select. Die Meldung wird unmittelbar
vor `packet.decode()` gesendet (`_media_restart_work.py:143`), nicht danach.
Sie enthält keinen Packetindex, Medien-PTS, Replayfensterindex, Zählerstand
oder Zeitstempel. Gleiche Meldungen überschreiben einander.

Vorhandene Dateisystemzeiten (UTC, nur Publikationsmetadaten):
Restore-Claim 08:29:15, Checkpoint-consumed 08:29:22, Failure und stderr
08:29:53. Sie sind keine gebundenen RPC-Start-/Antwortzeitpunkte und erlauben
keine Zerlegung in Hashprüfung, Replayfenster, Decodieren und Kanalwartezeit.
Insbesondere wird daraus keine genaue Replaydauer nachträglich konstruiert.

Belegt ist das Ablaufen der RPC-Frist ohne rechtzeitig entnommene
Abschlussantwort. Nicht entscheidbar: kontinuierlicher langsamer Fortschritt,
ein langer einzelner Decodierschritt, Stillstand oder verzögerte Kommunikation.
Die letzte Meldung ist keine belegte exakte Hängestelle. Mehr Zeit als Lösung
ist nicht nachgewiesen. Es gab keine Speichergrenzmeldung; dies erklärt den
Timeout ebenfalls nicht.

## Warum die zusätzlichen Zähler fehlen

`worker_main():502` überträgt `counters` und `restart_work` nach abgeschlossener
Operation. Auch sein Exceptionpfad `:507–522` kann aktuelle Zähler übertragen;
die Aussage „nur bei Erfolg“ wäre zu eng. Der Elternprozess übernimmt sie
bei vollständiger Antwort vor der Fehlerauswertung (`_rpc():325–341`).

Bei Timeout ruft `_rpc():310–312` dagegen `cancel()` auf. Dieses beendet den
Job (`:394–399`). Es gibt keine verpflichtende letzte Zählerantwort. Die
Phasenmeldungen enthalten keine Zähler. Der gespeicherte `restart_work` kann
deshalb aus init stammen: `prior` enthält Suspend19, neue Anteile stehen null.
`_rpc():345` markiert die Lesezähler als unvollständig; der Restartadapter
markiert ohne gemeldeten Workerfehler auch die äußere Frameevidenz unvollständig
(`_media_restart_work.py:213–216`). Das innere ältere True hebt das nicht auf.

Zusätzlicher Verbrauch seit der letzten bestätigten Antwort bleibt unbekannt,
nicht null. Eine spätere Reproduktion könnte diese historischen Zahlen nicht
ersetzen. Commit-Peaks und Prozessende belegen keine vollständigen Arbeitszähler.

## Kleinste zusammenhängende Korrekturrichtung, nicht implementiert

Den privaten Restartanschluss in `_media_restart_work.py:184/208` und den
Workerdispatch/-antwortpfad in `_s2oe_decoder_worker.py:428` um explizit
gebundene, endliche Replayabschnitte ergänzen, beispielsweise ein vorhandenes
Auswahlfenster je Anfrage. Kein Aufruf von Materialisierer, NJ oder Memory für
Replayabschnitte, keine Änderung der Auswahlrechnung oder Rohdatenpuffer.
Nach jedem Abschnitt Index, Sequenz, Medienfortschritt und kumulative Konten
bestätigen; prior und Replayverbrauch dürfen nie je Abschnitt zurückgesetzt
oder doppelt addiert werden. Nur das anschließende Zielfenster an MCM liefern.

Für Fehler innerhalb eines Abschnitts begrenzte, sequenzgebundene kumulative
Zwischenstände vorsehen. Letzten bestätigten Stand als Untergrenze samt
unbekanntem Rest erhalten, nicht als vollständigen Verbrauch ausgeben.
Unveränderter Lesemengen-/Frame-/RAM-Rahmen; keine neue unbeschränkte Loghistorie.

Fehlender Fortschritt und gesamte Replayedauer brauchen getrennte endliche
Grenzen. Nur nachgewiesener monotoner Fortschritt darf die erste beeinflussen;
wiederholtes VIDEO/packet_decode ist kein ausreichender Fortschrittsbeleg.
Eine absolute Gesamtdauer darf nicht durch Abschnittsantworten erneuert werden.
Konkrete neue Gesamtzeit und Abschnittsgranularität sind noch zu binden und
neutral zu prüfen; dieser Befund begründet keine pauschale Timeout-Erhöhung
und garantiert nicht, dass ein einzelner Abschnitt rechtzeitig endet.

## Quellenstand

Gelesene Dateien stimmen mit dem laufgebundenen Qualifikationsinventar überein:

- `_media_restart_work.py`: `768f83d11a00b6cc11eec0aaacaf7b8ae4b99335d179b1adb7a81ae615fe4407`
- `_s2oe_decoder_worker.py`: `4a61b9ea41236eb28ac49e959563a2a8248eedb315e4084cffc4db7bdcf10021`
- `_s2oe_media_decoder.py`: `9462319ac6880f5d0d1e21a03c505ef0ebe24b8d75ced4ae7989963b65a2aeca`

Geordnetes Speichern und das Belegbudget funktionieren im erreichten Umfang.
Reale vollständige Wiederaufnahme bleibt offen. Kein Memoryfehler abgeleitet.
Gates unverändert False; weitere Umsetzung und jeder neue Lauf bleiben gesperrt.
