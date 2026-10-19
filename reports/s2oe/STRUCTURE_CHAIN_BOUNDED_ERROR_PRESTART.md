# Begrenzte Fehlerdiagnostik: erneuter Vorabstopp

Die neue Freigabe hebt ausschließlich die Pflicht zur unbegrenzt vollständigen
Textdiagnostik prospektiv auf. Historische Dateien und Limits unverändert.

Vorbereitet im bestehenden `reports/qualify_structure_chain_once.py`:

- `ppb-chain.bounded-error.v1`: feste primäre Codes oder `UNKNOWN_ERROR`,
  Phase, Fortschritt, Bindungsdigest und Verweis samt Digest auf den letzten
  im Präfix enthaltenen Zustandsbeleg. Keine freie Ausnahmeverkettung.
- Höchstens 512 Unicode-Codepunkte ergänzende Nachricht, höchstens 6.144
  Byte für deren JSON-escaped Inhalt. Überschreitung wird ausdrücklich als
  `DIAGNOSTIC_LIMIT_REACHED` markiert; keine vollständige Tracebackbehauptung.
- Kindprozessausgabe wird während der Erfassung auf 4.096 gespeicherte Bytes
  begrenzt. Ein zusätzlich gelesenes Byte erkennt Überlauf; der Kindprozess
  wird beendet und darf keinen Qualifikationserfolg erhalten. Es wird kein
  vollständiges Log behauptet, wenn Überlauf eintritt.

Die ursprünglichen zwölf Tests bleiben vorbereitet. Drei zusätzliche Gruppen
prüfen primären Fehler samt Fortschritt, überlangen unbekannten Fehlertext
und Ausgabegrenze einschließlich Gleichstand. Keine Gruppe wurde ausgeführt.
Der historische reine Diagnosequelltext bleibt am bisherigen Archivort;
die neue geplante Qualifikations-ID endet auf `20260912-03`.

## Vorbilanz, nicht Qualifikationsaufruf

Ein Aufruf von `prepare` stoppte mit `PRESTART_LIMIT`, vor Veröffentlichung
der Vorregistrierung und vor Anlegen eines Qualifikationsclaims:

| Klasse | Erfolg | Fehleralternative |
| --- | ---: | ---: |
| Quellen | 594.304 | 594.304 |
| Metadaten einschließlich Reserve | 95.824 | 95.824 |
| Evidenz | 2.525.777 | 3.574.353 |
| Verifikation | 35.446 | 35.446 |
| Gesamt | 3.251.351 | 4.299.927 |

Grenze 4.194.304 Byte; Fehleralternative **105.623 Byte zu groß**.
Vorregistrierungsformat: 6.684 Byte. Diese Beträge betreffen den vorbereiteten
Quellenstand vor diesem Bericht; der Bericht liegt innerhalb der bestehenden
Berichtreserve, nicht in einer neu hinzugefügten Reserve.

## Noch nicht abgeschlossen

Die begrenzte Textform beseitigt den zuvor unbeschränkten Textbestandteil,
aber nicht die zu große Evidenzreservierung. Die drei bestehenden vollen
1.048.576-Byte-Reserven wurden nicht willkürlich reduziert. Eine kleinere
aus sämtlichen konkreten Zustands-/Tabellenformaten abgeleitete Reserve
ist noch nicht nachgewiesen. Die Vorbilanz ist daher weiterhin kein
abgesicherter vollständiger Fehlerobergrenzennachweis.

Auch die bereits dokumentierten Dateifehlergrenzen (`save`/temporäre Datei,
Fehler im `finally`) und die unterschiedliche Abschlussrechnung sind nicht
durch die Textbegrenzung gelöst. Die implementierte Änderung ist ausdrücklich
unqualifiziert und kein freigegebener Hauptanschluss. Kein Hauptlauf, keine
PPB-Nachsimulation, keine historischen Tests und keine Grenzerhöhung.
