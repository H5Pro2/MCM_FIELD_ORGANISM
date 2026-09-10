# S2-OC: Korrigierter Anschluss, Vorbedingung der Neuqualifikation

Diese Vorbereitung übernimmt keine historischen Passzahlen. Vorgesehen bleibt
ein vollständiger neutraler Aufruf mit 24 Prüfgruppen unter einer neuen ID.
Die Ergebnisablage wird erst nach bestandener Vorbilanz erstellt. Vorher liegt
keine Qualifikation vor. Historischer Lauf 01 bleibt NOT_QUALIFIED.

## Lokale Änderungen

- Eine aktuelle Materialisierungsphase wird nicht mehr durch die alte
  EVIDENCE-Phase des vorigen Runtimeereignisses überschrieben. Nur im aktuell
  laufenden EVENT-Teil darf die Runtime ihre EVIDENCE-Phase ergänzen.
- Die Eingangs- und Zustandsvergleiche erfolgen an derselben kanonischen
  Ausgabegrenze. Ein Python-Tupel und die entsprechende JSON-Liste sind dort
  dieselbe Darstellung; numerische Werte, IDs und Profile werden nicht gelockert.
  Die unabhängige bestehende Verifikation rekonstruiert weiterhin native Typen.
- Eingangs- und Quellenassertion, Ereignis- und Zustandsassertion sowie die
  Kontrollen des Payloadfehlers sind durch getrennte subTest-Blöcke unabhängig
  erreichbar. Geprüft werden Fehlercode, Analysezahl, abgeschlossene Ereignisse,
  aktuelle Phase, erhaltene Feld-/Memorydigests, frühe Rückgabe und Auswertungssperre.
- Die neutrale Scanfixture verwendet oc-scan-error statt der ungültigen kurzen ID.
  Keine Änderung des ID-Validators oder der eigentlichen Scan-/Memoryregeln.

## Vollständiges Inventar

Die AST-erfassten 24 Testnamen werden vor einem möglichen Aufruf vollständig
in preflight.json gespeichert und gehasht. Sie umfassen die Gleichheitsfolge,
Einzelergebnisse, Quellenbindung, Reihenfolge, Warteschritte, Wiedereintritt,
unvollständiges und wiederholtes Schließen, Payload-/Memory-/Feld-/Scanfehler,
Manipulationsabwehr, Gate und Gesamtbilanz. Keine alte Passzahl gilt als neu geprüft.

Vorgesehene Arbeit unverändert: ein Stapel und zwölf Sitzungen; 13 Audioanalysen,
13 NJ-Projektionen, 13 visuelle Analysen; 13 unabhängige Verifikationen. Keine
realen Aufruferdateien, OA-/OB-Wiederholung oder gespeicherte Geschichte ausführen.
Die Fehlerfälle behalten eigene frische neutrale Instanzen. Gates außerhalb
dieser noch nicht begonnenen Prüfung False.

## Belegbindung und konkreter Stoppgrund

Die administrative Vorbereitung referenziert ihr vollständiges Quelleninventar
einmal mit Datei, Länge und SHA-256. Test- und Aufrufdatei sind darin enthalten.
Die zwei historischen Diagnoseeingänge stehen einmal im Referenzkatalog mit
ihren tatsächlichen Größen und Digests. Diese Referenzform spart Wiederholungen
in der Vorbereitung; sie beseitigt weder die Laufmetadaten noch die vollständigen
Fehlerprotokolle und wird nicht als entsprechende Einsparung ausgegeben.

Unverändert: 65.536 Byte Metadaten, 262.144 Byte gemeinsame Zusatzhülle,
4.194.304 Byte global; 4.096 Byte Qualifikationsreserve und 512 Byte Berichtreserve.
Das korrigierte Ledger unterscheidet tatsächliche Belegung, ursprüngliche
Reserven und die erforderliche Gesamtbelegung mit max(Ist, Reserve).
Eine Überschreitung bleibt daher auch in der Gesamtsumme sichtbar.

Bereits der vollständig gespeicherte Fehlerlog von Lauf 01 hat 4.643 Byte.
Er überschreitet allein die aktuelle Qualifikationsreserve um 547 Byte, noch
ohne Vorregistrierung, Metriken, Ergebnis und Ledger. Das ist eine nachgewiesene
Untergrenze für einen bereits aufgetretenen Fehlerumfang, keine obere Grenze
aller künftig möglichen Logs und keine Vorhersage eines neuen Fehllaufs.
Ein angenommener kurzer Erfolgslog genügt nicht zur Aufhebung dieses Widerspruchs.

Die ursprüngliche gemeinsame Lauf-/Sitzungsmetadatenbelegung betrug zudem
77.940 statt 57.344 Byte: 20.596 Byte Überschreitung. Die lokalen Code- und
Testkorrekturen liefern keinen Beleg für deren Reduktion. Die notwendige
verlustfreie Kompaktierung dieser Laufbindungen ist weiterhin nicht abgeschlossen.
Die Vorbereitung selbst wird nicht als passend kompaktierte neue Gesamthülle
ausgegeben. Eine bloße Referenzierung ohne Mitbilanz der aufgelösten Inhalte
oder Verlagerung des Logs in eine andere Klasse ist ausgeschlossen.

Der Aufruf muss daher an der administrativen Vorbedingung stoppen, bevor
unittest oder eine neue neutrale Materialisierung gestartet wird. Keine neue
Qualifikationsablage, kein neuer Laufbefund und keine 24/24-Behauptung.
Die Ausgabe enthält die belegten Einzelbeträge und Überschreitungen ausdrücklich.
Weitere kompakte Darstellung der übrigen Bindungen könnte diese eigenständige
Loggrenze nicht allein schließen. Keine allgemeine Unmöglichkeit anderer
verlustfreier Darstellungen behaupten; dafür liegt hier kein qualifizierter
und vollständig bilanzierter Anschluss vor.

ME/MI bleiben gesperrt, Prognosezweig ruhend. Der echte Sitzungsversuch bleibt
gesperrt. Vor einer Neuqualifikation ist eine tragfähige gemeinsame Belegform
einschließlich vollständiger Fehlerdiagnostik erforderlich, keine weitere Reserve.
