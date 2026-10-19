# MEMORY-SPEICHERN-WIEDERLADEN — PROZESSAUFRUFER-FERTIGSTELLUNG

Status: **NOT_READY**, keine neue Qualifikation und kein Hauptlauf.

## Bearbeitungsnachtrag

Der Aufruferentwurf wurde weiter ergänzt: Prozesslogs werden während der
Erfassung auf zusammen 8.192 Byte je Kindprozess begrenzt; bei Überlauf wird
der Kindprozess beendet und der Log ausdrücklich nicht als vollständig
bezeichnet. Timeout und Logschreibfehler erhalten eigene Fehlercodes.
Außerdem wurden die Ereignis-/Payloadbindungen der Gesamtrecords an das
Manifest und einzeln ausgewiesene Wahrnehmungs-, Memory-, Feld-, Generations-,
Snapshot-, Schritt- und Quellenvergleiche ergänzt.

Aktueller Entwurf: 14.289 Byte, SHA-256
`2b9c95e8bc92910c12de5f6551b96430e2660ff9359f0481ebebf4b63ba74372`.
Die untenstehende erste Hashangabe bezeichnet den vorherigen Bearbeitungsstand.
Die historischen qualifizierten Quellenhashes wurden lesend abgeglichen;
keine Abweichung gefunden. Keine Projektimporte oder Testaufrufe.

**Die Fertigstellung ist damit nicht erreicht.** Die geschlossene Zulassung,
vollständige gemeinsame Vorbilanz und vorgebundene neue Testsuite fehlen
weiterhin. Es ist weder ein Qualifikationsergebnis noch ein nachgewiesener
unlösbarer Budgetkonflikt vorhanden. Diese fehlende Fertigstellung darf nicht
als erforderliche neue Analystenentscheidung ausgegeben werden. Der aktuelle
Auftrag und seine Freigabe bleiben bestehen; keine ausführbare Einmalbindung.

Die weiteren Abschnitte beschreiben den vorherigen statischen Prüfstand;
insbesondere die dort genannten unbeschränkten Prozesslogs und fehlenden
Einzelvergleichsfelder sind inzwischen als unqualifizierter Code ergänzt.
Repository-HEAD: `537109994cf777f8d36cda617aafe12226806c25`.
Der Arbeitsbaum enthält zahlreiche vorbestehende Änderungen; HEAD allein
bezeichnet deshalb nicht den ausführbaren Quellenstand.

Der neue, weiterhin unqualifizierte Entwurf
`tools/_checkpoint_transfer_entry.py` hat 10.933 Byte und SHA-256
`e9afacd0763e7aa6a0331b70328538ae01e46d788cfa0ca677e3fe479e077767`.
Die vorhandene Eingangsbindung unter
`reports/memory-restart-transfer-binding-20260912-01` bleibt unverändert.
Das Ergebnisverzeichnis `reports/memory-restart-transfer-20260912-01`
ist weiterhin nicht vorhanden. Keine Autorisierung wurde erstellt.

## Bereits im Entwurf vorhanden, nicht neu qualifiziert

Der Referenzworker verarbeitet sieben Ereignisse ohne Unterbrechung und
erfasst nach e04 nur einen Vergleichspunkt. Nur der Saveworker suspendiert
nach vier Formationen. Der äußere Aufrufer wartet auf dessen Prozessende,
bevor er den Restoreworker startet. Dieser verwendet den Checkpoint und
setzt bei e05 fort. Kein Rezeptor- oder Memoryaufruf wurde hierzu ausgeführt.

In dieser Bearbeitung ergänzt: Prozessfehler erhalten die abgeschlossenen
Stufen und die aktive Rolle; auch Fehler vor Sitzungserzeugung haben eine
vorgesehene Fehlerform. Savebeleg und Checkpointdigest werden verknüpft.
Ein Fehler beim äußeren Fehlerpublizieren verdrängt nicht mehr die
ursprüngliche Ausnahme. Diese Änderungen sind ausdrücklich **ungetestet**.
Historischer Checkpointcode und historische Qualifikationen wurden nicht geändert.

## Konkrete verbleibende Startblocker

1. **Zulassung, `check_binding()`, Zeile 22:** Der Entwurf verlangt eine noch
   nicht existierende neue Form mit `ready`, `manifest`, `inventory` und
   `qualification_references`. Die vorhandene `binding.json` hat dagegen
   `INPUT_BOUND_NOT_EXECUTABLE` und `active_entry: null`. Hashprüfungen allein
   prüfen zudem nicht die geforderte Verbunddeckung aus den 21 bestandenen
   Gruppen und vier Ergänzungskontrollen. Der historische Fehlstatus darf
   nicht zu einem neuen Gesamterfolg umgedeutet werden.
2. **Gesamte Quellenbindung:** Aktueller Aufrufer, dessen noch fehlende
   fokussierte Test-/Aufrufdateien, Qualifikation und Abschluss sind nicht
   gemeinsam gebunden. `charged_sources` ist im Ledger optional. Der neue
   Einstieg muss seine vollständige aktive Pflichtliste verlangen; die
   vorbereitete Manifest-Codebindung ersetzt diese neue Aufruferbindung nicht.
3. **Vorstart und Fortschritt, `run()`, Zeile 175:** `common.json`,
   Vorregistrierung, Dispatch, Qualifikationskopien und Prozesslogs werden
   außerhalb von `publish_new()` geschrieben. Es gibt noch keine vollständige
   vorausgehende Bilanz dieser Dateien samt Autorisierung und Verbrauchsmarke.
   Der vorhandene Ledger prüft spätere Publikationen, nicht diese gesamte
   Folge vor dem ersten Prozessstart. Die Endbilanz wird noch nicht publiziert.
4. **Fehlergrößen, `run()`/`worker()`:** Kindprozess-stdout und -stderr haben
   im Entwurf keinen endlichen Ausgabedeckel; der Timeout begrenzt Zeit,
   nicht Bytes. Vollständige Fehlerpräfixe, Pending-Dateien und sekundäre
   Publikationsfehler müssen gemeinsam berücksichtigt werden. Eine beliebige
   Erfolgsloggröße ist dafür keine gültige Obergrenze. Die alte Formatvorrechnung
   in `prepare_checkpoint_budget.py` addiert außerdem noch beide fertigen Arme
   während einer Checkpointpublikation; sie ist keine erreichbarkeitsgenaue
   Fortschrittsrechnung dieses Aufrufers.
5. **Fehlerabschluss:** Einrichtungsfehler nach Verbrauch der Autorisierung
   liegen noch vor dem äußeren `try` in `run()`. Bei Budgetablehnung kann die
   Fehlerpublikation selbst am bereits belegten Budget scheitern. Die neue
   Weitergabe des Primärfehlers löst nicht dessen garantierte physische Ablage.
   Dafür fehlt die vorab reservierte, nicht rekursiv bilanzierte Fehlerform.
6. **Gesamtverifikation, `verify_total()`, Zeile 118:** Sie prüft native
   Einzelbelege und Konten, aber bindet die vollständige Referenzfolge noch
   nicht ausdrücklich Ereignis für Ereignis an das Aufrufermanifest. Der
   historische `verify_core()` prüft interne Quellen-/Zeitkonsistenz, nicht
   allein die komplette neue Aufruferzulassung. Die zusätzlichen Prüfungen
   und ihre kumulative Arbeit sind noch separat zu budgetieren. Das Lesen
   derselben Datei ersetzt keine unabhängige Herkunftsprüfung.
7. **Vergleichsumfang, `evaluate()`, Zeile 156:** Gegenwärtig werden
   Gesamtrecordgleichheit und zwei Statusentscheidungen ausgegeben. Die
   geforderten einzelnen Wahrnehmungs-, Memory-, Feld-, Generations- und
   Kontobindungen nach jedem Ereignis sind noch nicht getrennt ausgewiesen.
   Der neue Anschluss besitzt weder das vollständige fokussierte Prüfinventar
   noch dessen vorgebundene Gesamthülle. Ein Teststart wäre verfrüht.

## Tragfähigkeit und kleinste Fertigstellung

Die sieben Ereignisse und die bestehenden Kernregeln benötigen nach diesen
statischen Befunden keine Erweiterung. **Die Artefakttragfähigkeit ist jedoch
noch nicht bewiesen.** Es gibt keinen belastbaren vollständigen Summenwert
des neuen Aufrufers; weder eine Überschreitung noch ein Bestehen wird behauptet.

Unverändert gelten 65.536 Byte Metadaten, 174.080 Byte Quellen,
262.144 Byte gemeinsame Zusatzhülle, 262.144 Byte Verifikation und
4.194.304 Byte gesamt. FIELD_CHECKPOINT.v1 bleibt bei 524.288 Byte,
seine bestehende feste Formatobergrenze bei 426.580 Byte. Diese lokalen
Grenzen sind keine gleichzeitig garantierte Platzreservierung.

Die kleinste zusammenhängende Fertigstellung bleibt im neuen Aufrufer:
geschlossene Zulassungsform und aktive Pflichtliste; derselbe Ledger vor
Einrichtung, an jeder Prozessgrenze und beim alternativen Erfolgs-/Fehlerabschluss;
endlicher Prozessausgabeverbrauch mit erhaltenem Fehler; manifestgebundene
Gesamtprüfung und einzeln ausgewiesene Vergleichsgrößen. Danach sind nur
diese neuen Anschlüsse einmal neutral zu qualifizieren. Keine neue
Entscheidung über Memorymechanik oder Medienauswahl ist erforderlich.

Bis dahin ist **kein ausführbarer Startbefehl freigegeben**. Es wurden keine
Projektimporte, Tests, Payloadzugriffe oder Prozesse ausgeführt. Historische
Belege unverändert; kein Gate geöffnet. Die unbenutzte Lauf-ID bleibt erhalten.
