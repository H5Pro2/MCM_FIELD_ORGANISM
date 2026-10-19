# Checkpoint-/Restore-Qualifikation: NOT_QUALIFIED

Genau ein Testaufruf, 22 erreichte Prüfgruppen, **21 bestanden, eine Assertion
fehlgeschlagen**. Kein Retry und keine anschließende Code- oder Testkorrektur.
Historischer Vorabstand 01 bleibt erhalten und war kein Testlauf.

Vorbindung: 63.866 / 65.536 Byte Metadaten, 3.043.266 / 4.194.304 Byte gesamt.
Feldformatobergrenze 426.580 / 524.288 Byte für das gebundene schema-1-OB-Feld.
Codeinventardigest:
`8fdefba8a46dc1de7feac14a17a031d087fe5c40819667ace6874a29c659193c`.
Quelleninventar vor/nach dem Aufruf unverändert. Sämtliche ausgegebenen Logs
sowie negative Dateien bleiben erhalten; keine Fehlerausgabe nachträglich gekürzt.

## Erreicht

Drei tatsächlich gestartete Interpreter für Baseline, Speichern und Restore,
jeweils Exitcode 0. Der Speicherprozess war beendet, bevor Restore startete.
Vier neutrale Endpunktereignisse, Speicherpunkt nach Ereignis eins; **kein
realer Sieben-Ereignis-Vergleich** und keine realen Aufruferpayloads.

Baseline und fortgesetzter Arm schließen RECORDING_COMPLETE ab. Vollständige
Laufbelege sind gleich, einschließlich Zuständen, Generationen, Scans und
Entscheidungen; die nativen Felddigests der Fortsetzung stimmen überein.
Der Streamzustand vor der ersten Fortsetzung ist erhalten. Beide Hinweise
bleiben read-only. Die logischen IDs bleiben gleich; Prozess-IDs unterscheiden
sich. Keine verbrauchten Ereignisowner wieder geöffnet.

Weitere bestandene Kontrollen: beschädigte/fehlende Bindungen, Profil- und
Codeabweichung, Generation, unvollständige Datei, Schreib- und Linkfehler,
doppelte Veröffentlichung, verbrauchter Checkpoint, Gate, Größenrand,
Feldform, Materialisiererkonten, Reihenfolge vor Payloadzugriff und unabhängige
Referenzauflösung. Ein neutraler Analysefehler nach echtem Lesen von 19.200 Byte
erhält diese Lesemenge und den Primärfehler; Schließen überschreibt ihn nicht.

## Fehlende Prüfdeckung

Test 05 scheitert in Zeile 141 an Python-Objektgleichheit:
`encode(asdict(stream.memory_state)) == JSON-gelesener Codecbeleg`.
`encode()` erhält über `deepcopy` native Tuple-Container; die JSON-Lesegrenze
liefert Listen. Der Codec akzeptiert beide Formen ausdrücklich. Damit ist
ein Vergleich verschiedener Containerdarstellungen statisch erkennbar.
Der Traceback enthält allerdings keinen vollständigen Einzelpfad-Diff:
unittest meldet seine standardmäßig begrenzte Darstellung mit 22.483 Zeichen
Diffumfang. Der vollständige tatsächlich ausgegebene stderr wurde erhalten.

Die anschließenden Assertions für Feld-Rundlauf und Eingabe-Unveränderlichkeit
in derselben Gruppe wurden nicht erreicht. Die bestandene Fortsetzungsgleichheit
ersetzt diese offenen Kontrollen nicht. Kein Memoryfehler wird aus dieser
Assertion abgeleitet und keine Gesamtqualifikation behauptet.

Kleinste Korrekturrichtung zur Entscheidung: kanonische Codecgleichheit prüfen,
native Binary64-/Digestbindung beibehalten; die nachgelagerten Kontrollen
unabhängig erreichen. Keine Codecänderung, keine Toleranz. Noch nicht umgesetzt.

## Ressourcen und Grenzen

Gespeicherter Checkpoint: 364.231 Byte, darin native Feldwerte 333.145 Byte.
Ist vor result.json und diesem Abschluss: Metadaten 27.978, Quellen 62.242,
gemeinsame Zusatzhülle 74.398, Verifikation 7.014, Gesamt 745.849 Byte.
Die abschließende vollständige Bilanz steht in `final-ledger.json`; sie zählt
auch Ergebnis, Bericht, sich selbst, temporäre Negativdatei und 19.200 Byte
neutralen Eingangsbestand. Eingangsbestand ist keine Metadatenumklassifizierung.

Materialisierer-Konten sind angebunden und separat kontrolliert. Der echte
Prozessvergleich verwendet neutrale Rezeptorendpunkte; ein kompletter
PCM-/RGB-Materialisierungslauf über Restore wurde damit nicht nachgewiesen.
Keine allgemeine Crash-Recovery, dauerhafte Datenträgergarantie oder
Kompatibilität mit beliebigen Feldschemas behauptet. Gates False; native
Sitzungen geschlossen, Kindprozesse beendet. Hauptlauf weiterhin gesperrt.
