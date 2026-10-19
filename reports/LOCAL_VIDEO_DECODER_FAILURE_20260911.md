# Videoeingang: statische Einordnung des Decoderabbruchs

Repository: `537109994cf777f8d36cda617aafe12226806c25`, mit bestehenden
uncommitteten Änderungen. Nur vorhandene Belege und Code gelesen; keine
Medienzugriffe, Projektimporte, Tests, erneute Verifikation oder Wiederholung.

## Nachgewiesener Stand

`media-memory-video-20260911-01` bleibt `NOT_EVALUABLE`. Grundlage ist dessen
unveränderter `record.json`, ergänzt durch `verification.json` und
`player-close.json`. Die Sitzung und der Worker sind geschlossen, Gates False.
Ein Videoframe und vier Pakete sind gezählt, aber kein ausgewähltes AV-Fenster,
keine Rezeptor-/NJ-Verarbeitung, Formation, Feldwirkung oder Scan.

| Gespeicherte Größe | Byte |
| --- | ---: |
| Prozess- und Job-Commitgrenze, jeweils | 536.870.912 |
| Peak Process Commit | 536.408.064 |
| Peak Job Commit | 542.973.952 |
| Eingangsbestand | 83.498.438 |
| Geplante maximale Lesemenge | 1.001.981.256 |
| Zuletzt übermittelte Lesemenge | 171.256.136 |

`job_confirmed_before_media=true` und `memory_limit_notification=true` sprechen
gegen einen Einrichtungsfehler. Der gemeldete Jobpeak liegt über der Grenze;
der Prozesspeak liegt darunter. Das sind Commitwerte, keine RSS-Messung.
Die Belege stützen eine tatsächlich ausgelöste Speicherbegrenzung, benennen
aber weder den auslösenden Allokator noch dessen angeforderte Größe.

Die finale Kennung `read_counters_complete=false` macht die Lesemenge zu
einem zuletzt bestätigten Stand, nicht zu einer garantiert vollständigen
Messung. Das frühere `true` in `failure.balance` stammt aus der Kopie vor
dem Fehlerhandler (`_s2oe_decoder_worker.py:290`, `:293`). Exitcode 1 ist
wegen des kontrollierten `TerminateJobObject(..., 1)` kein eigener Crashnachweis.

## Fehlergrenze und Puffer

- `_s2oe_decoder_worker.py:103–117` setzt und prüft beide Commitlimits;
  `:136–151` liest Peaks und fasst Meldungen 9/10 zu einem Boolean zusammen.
  Die konkrete Meldungsart wird nicht erhalten.
- `_rpc()` (`:278`, `:289`) ersetzt bei gesetztem Limitflag den eigentlichen
  Workerfehler durch `DECODER_MEMORY_LIMIT`. Der Worker liefert zwar
  `error` und `exception_type` (`:401–409`), diese gelangen nicht in den
  endgültigen Fehlerbeleg. Worker-stderr wird verworfen (`:225`). Deshalb
  bleibt offen, ob die erste RGB-Konvertierung, ein weiterer Decodeaufruf
  oder eine andere Operation konkret scheiterte. `PAYLOAD_READ` ist nur
  die äußere Phase.
- `Decoder.begin()` (`_s2oe_media_decoder.py:109–136`) hält zwei Container
  und Dateihandles gleichzeitig. Die Hashprüfung liest in 65.536-Byte-Blöcken;
  keine vollständige Dateikopie ist im Pythoncode sichtbar. Video hat bereits
  `thread_count=1`; eine weitere Threadreduktion ist keine belegte Lösung.
- `_frames()` (`:85–95`) kann während eines `yield` die vom Paketdecoder
  gelieferte Frameliste halten. Dazu kommen native Codec-/Containerpuffer,
  deren tatsächliche Größen im vorhandenen Beleg fehlen.
- `select()` (`:146–168`) konvertiert jeden Frame bis zum Mittelpunkt in
  1.920 × 1.080 RGB, auch später verworfene Zwischenframes. Bei Ersetzung
  können alter RGB-Puffer, neues Konvertierungsergebnis und nativer Frame
  gleichzeitig leben. Der nächste Frame bleibt als Zeitbeleg erhalten.
  Die konkrete native Konvertierungsspitze ist nicht gemessen.
- Der gemeinsame Ausgabeslot umfasst 6.240.000 Byte. Zusätzliche Kopien im
  Elternprozess entstehen erst nach erfolgreicher Antwort (`worker:304–315`),
  also nicht als bereits erfolgte Ausgabe dieses fehlgeschlagenen Fensters.
  Die Audio-Konvertierung wurde laut Zählern noch nicht erreicht.

## Kleinster Vorschlag zur Freigabe

Zunächst die bestehende Workerfehlerantwort vollständig, aber endlich
weiterreichen: ursprünglicher Fehlercode und Ausnahmetyp, konkrete Phase
vor Decode/Konvertierung/Audio/Slotübergabe, Zähler und getrennte Limitmeldung.
Keine rekursive Diagnosehülle, keine neue Plattform und keine Grenzerhöhung.
Das schließt die belegte Diagnoseverluststelle, nicht bereits die Speicherursache.

Als eng begrenzte Optimierung ist eine RGB-Konvertierung erst nach endgültiger
PTS-Auswahl prüfbar. Zwischenframes würden nur zeitlich geprüft. Dies lässt
Auswahl und Bildformat unverändert, kann aber einen zusätzlichen nativen
Frame gleichzeitig halten und ist daher keine bewiesene Peakreduktion.
Ohne Allokationsphase und native Pufferbelegung lässt sich kein ausreichend
sicherer Speicherfix behaupten; insbesondere ist ein bisheriger RGB-Puffer
beim allerersten Fenster noch kein belegter Auslöser.

Vorgeschlagene begrenzte Prüfung nach Freigabe: neutrale Fehlerweitergabe
für Decode und Konvertierung, Erhalt ursprünglicher Fehler und Lesemengen,
danach höchstens ein erster realer AV-Endpunkt unter neuer Diagnose-ID und
unverändertem 512-MiB-Joblimit, ohne Rezeptoren oder Memory. Kein voller
Lernlauf. Eine eventuelle Optimierung benötigt zusätzlich eine neutrale
PTS-/Pixelgleichheits- und Pufferprüfung. Dieser Vorschlag ist nicht ausgeführt.

Aktuelle SHA-256:

- Decoder: `7376f0e6929644f87cbc199ec3122796657c5518b49096a8f86ce432cea63129`
- Worker: `3328b576194dab08b8b4bf1db0541799e02b5913cfa6aa855033cf865078d1e8`

**RÜCKMELDUNG ERFORDERLICH:** enge Diagnosekorrektur und begrenzte Prüfung
freigeben. Historischer Lauf bleibt verbraucht; kein automatischer Folgeaufruf.
