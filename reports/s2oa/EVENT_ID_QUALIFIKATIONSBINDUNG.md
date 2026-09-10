# OA: lokale technische Ereignis-ID, vorab gebundene Qualifikation

ID: `s2oa-event-id-qualification-20260910-01`. Genau ein Testaufruf,
14 neue Gruppen. Kein OA-Payload, keine Hauptgeschichte, kein Retry.

## Anschlussinventar

Plan-IDs e01..e28 bleiben unveraendert. `s2oa.event-id-binding.v1` bindet
die Tabelle (ordinal, plan_id, technical_id) an execution_digest.
Technische ID: `s2oa-event-` plus kurze Plan-ID. Keine Identitaetsaussage.
Tabellen in der kanonischen BoundOA-Provenienz sind ueber deren immutable
JSON-Zeichenfolge gebunden. Main-Gesamtbeleg bekommt Version v2.

- Materializer -> bind_event -> unveraendertes bind_input -> LM-Builder:
  technische ID; AV-pair_id ebenso. Owner/Consume und Formationskontext
  leiten unveraendert aus dieser ID ab. Generationen bleiben ordinalgebunden.
- check_inputs und die unabhaengige Gesamtverifikation pruefen die
  Plan-/Runtime-Zuordnung, nicht laenger unmittelbare Gleichheit.
- Quellen-/Zeit-/Evaluationswurzeln behalten Plan-IDs. Auswertung bleibt
  ueber versiegelte Ordinalfolge verknuepft; q05/q07-Regeln unveraendert.
- Kein Eingriff in LM, NN, Memory, Feld, historische NEUTRAL-Adapter oder
  Quellensealer. Alte Hauptqualifikation bleibt an die alten zwei Dateihashes
  gebunden. Nur genau diese beiden Nachfolger plus vier neue Anschlussdateien
  werden im neuen Qualifikationsdelta gebunden; jede weitere Abweichung sperrt.

## Neutraler Umfang und Grenzen

Alle 28 IDs, fehlende/vertauschte/kollidierende/fremde Bindungen, Planform,
Digest, e01 -> technische ID -> echter visueller LM-Builder mit synthetischem
288er-Nullkontakt; Offline-Decodierung ohne erneute Analyse. Fremdes Ereignis,
unabhaengiger ID-Verifikator, tatsaechliche Aufrufstellen, Qualifikationsdelta,
Gesamthuelle und geschlossene Gates. Unterfaelle bleiben unabhaengig.

Keine Payloads/Rezeptoren/NJ, Runtimeinstanzen, Formationen oder Scans.
Maximal ein neuer neutraler LM-Eingang, 128 vollstaendige ID-Pruefsweeps
zu 28 Zeilen; keine zusaetzlichen Wahrnehmungswertvergleiche. Spaeterer
Hauptpfad: maximal 1200 administrative ID-Zeilenpruefungen; Offline-Pruefung
separat maximal 224 ID-Zeilenpruefungen, bestehende numerische Budgets bleiben.

ID-Tabelle maximal 2048 Byte, neue referenzierte Qualifikation maximal
4096 Byte (Vorregistrierung, Resultat, beide Logs, Metriken). Neue Felder
und Referenzen zaehlen in der Metadatenhuelle von 65536 Byte; gemeinsame
Zusatzhuelle 262144 und Gesamt 4194304 Byte unveraendert. Berichtreserve
im kuenftigen Lauf 512 Byte, verbleibender Raum wird ausgewiesen.

Die vollstaendige gespeicherte NEUTRAL-Huelle der alten Qualifikation wird
nur als Groessenfixture gelesen, nicht erneut technisch/fachlich verifiziert.
Alte neutrale IDs und neue technische IDs haben beide 13 Zeichen; ebenso
bleiben Owner-/Consume-Suffixlaengen und alle Digestlaengen erhalten.
Alle echten NJ-/Formations-/Generationsformen bleiben in der Groessenbilanz;
neue Mapping-/Qualifikationsfelder werden voll hinzugezaehlt. Dies behauptet
keinen neuen v2-Gesamtlauf. Teilformlimits und Metadatenueberschreitungen
werden geprueft, keine Grenzerhoehung. Alte Fehlbelege bleiben NOT_EVALUABLE.
Die neue Qualifikationsreferenz bindet einmal ihre qualification_id unter
reports/s2oa und je Dateiname [sha256, bytes], ohne wiederholte Pfadpraefixe.
Alle fuenf Dateien bleiben vollstaendig in metadata_bytes enthalten.

Quellhashes/Testinventar werden vor dem einen Aufruf geschrieben und danach
auf Gleichheit geprueft. Hauptgate False; Freigabe eines Hauptlaufs fehlt.
