# Ergänzung der drei offenen Diagnosegrenzen

Ein ergänzender Qualifikationsaufruf, nicht die früheren zwölf Tests.
Aktuelle Dateien und beide Teststände getrennt über Inventare binden.
Keine ausgewählte MP4 öffnen. Neue neutrale Datei: 124 konstante yuv420p-
Frames, alle aktiven Plane-Bytes 128, 3840x2160, 30000/1001 fps, BT.709,
begrenzter Bereich; libx264 ultrafast/zerolatency CRF 30. Kein Ersatzcodec.
Die Datei wird in der Qualifikation einmal erzeugt und getrennt gehasht.

## Nativer Weg

VideoWorker startet unverändert worker_main im echten begrenzten Job.
Vier unabhängige Worker erhalten dieselbe neutrale Datei für Punkte 2,2,8,8;
vor jedem Öffnen wird das gemeinsame Restbudget geprüft. Native PTS,
Framebindung, RGB-Hash, Null-Audiozähler und geschlossene Worker werden
aufgezeichnet. Eine eigene negative Hashbindung prüft die Fehlerweitergabe
vor Dekodierung im echten Prozess. Keine Rezeptor- oder Memoryausführung.

## Gemeinsames Budget

FourWorkers hält Zähler und Reihenfolge über die vier Worker. Verbleibende
Frames werden im video_point-Befehl gebunden und im Kind vor dem nächsten
Frameabruf geprüft. Alle tatsächlich gemeldeten Frames zählen auch bei
Fehlern. Vorzeitiges close sperrt weitere Öffnungen; kein Reset/Fallback.
400 ausgegebene Decoderframes insgesamt, maximal vier Worker der eigentlichen
Folge. Das sind vom Decoder zurückgegebene Frames, nicht interne Codecoperationen.
Worker-Paket-, Lese-, Zeit- und UHD-Speichergrenzen bleiben unverändert.
Die zusätzliche negative neutrale Fehlerprobe gehört nur zur Qualifikation.

## Vollständige Ausgabeform

Alle acht Vektoren bleiben vollständig: je 288 Binary64-Werte als
Big-Endian-IEEE-Hex, 16 Zeichen pro Wert. Keine Änderung oder Rundung;
Subnormale und negatives Null bleiben erhalten. Das ist keine zusätzliche
Kompression. Die sechs festen Vergleichspaare referenzieren diese Werte
mit ihren Originalindizes; 704 explizite Gleichheitszeichen 0/1.
Keine doppelte Ablage derselben Zahlen in den Vergleichszeilen erforderlich.
Bei noch fehlenden Vektoren bleibt der Vergleich null, nicht falsch.

Pro vollständiger Tabelle einschließlich Fehleralternative:
36.864 Zeichen Vektoren + vier Workerbelege zu maximal 3.072 Byte
+ 2.048 Bindungen + 4.096 ursprünglicher Fehler + 704 Gleichheitszeichen
+ 1.024 Strukturreserve = 57.024 Byte, Grenze 57.344.
Jede Serialisierung prüft zusätzlich die tatsächliche Gesamtgröße.
Restore prüft vollständige Rekonstruktion und kanonische Gleichheit.
Die Qualifikation serialisiert Gleichheit, Abweichung und Fehler getrennt
im Speicher; protokolliert Größe und Digest, ohne drei weitere Pflichtarchive.
Vollständige native Workerbelege bleiben separat in der Qualifikationsablage.

## Gesamthülle

Alle aktuellen Quell-/Prüfdateien sowie historische Teilqualifikation zählen
im Quelleninventar. Zusätzlich 196.608 Byte für das neue neutrale Video.
Metadatenreserve 114.688: vollständiges Log 32.768, Ergebnis 8.192,
Bindungen/Bericht/native Belege 16.384 und Tabelle 57.344.
Grenzen bleiben 327.680 Quellen, 131.072 Metadaten, 393.216 gemeinsame
Zusatzhülle, 4.194.304 Gesamt. Vorab bei Überschreitung stoppen.
Fehlerlog niemals kürzen; bei Überschreitung Befund nicht qualifiziert.

## Späterer Realvergleich, weiterhin gesperrt

Quelle, historische PTS und acht Analysen wie im Diagnoseanschluss gebunden.
FourWorkers.next ist der verpflichtende gemeinsame Aufrufpfad; kein direkter
VideoWorker-Aufruf außerhalb dieses Budgets im späteren Versuch. Aktuelle
Profilbindung nach Quellen-/Codeprüfung, Gate nur nach separater Freigabe.
Zwischen den vier Öffnungen kein Framecache. Kein neuer Quellenbestand,
keine Schwelle und keine Memory-/Feldfunktion. Noch kein realer Lauf.
