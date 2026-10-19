# Neustartvergleich: gebunden, noch nicht autorisiert

Lauf-ID: `memory-restart-transfer-20260912-01`.
Ergebnis: `reports/memory-restart-transfer-20260912-01`, derzeit nicht vorhanden.
Die historische Vorbereitungs-/Fehlerkette bleibt unverändert.

## Gebundener Ablauf

Referenz: sieben Ereignisse ohne Unterbrechung; nach vier Formationen nur
Vergleichszustand erfassen. Zweiter Arm: vier Formationen, vollständiger
Checkpoint, reguläres Prozessende, frischer Restoreprozess, zwei read-only
Hinweise und eine weitere Formation. Kein Reset der fortgesetzten Zähler.

Je Arm: fünf Formationen, zwei Hinweise, sechs Audio-/NJ-Verarbeitungen,
sechs visuelle Analysen, 2.016 Feldkontakte und vier Scans einschließlich
Direktbaseline. Gemeinsam: 14 Ereignisse, zehn Formationen, 4.032 Kontakte,
acht Scans. Drei vorhandene OB-Dateien werden wiederverwendet; kein neuer
Bestätigungskorpus. Geplante Lesemenge: 37.440.000 Byte je Arm. Das sind keine
gemessenen Lesemengen; die tatsächlichen Konten entstehen erst im Hauptlauf.

Manifest und Quellen bleiben aus der ursprünglichen Aufgabenbindung erhalten.
Der neue Aufrufer ist zusätzlich über das aktuelle Codeinventar gebunden.
Seine Qualifikationsreferenzen sind einzeln verfügbar und hashgebunden;
historische Archive bleiben erhalten, werden aber nicht vollständig zu
operativen Laufabhängigkeiten erklärt. Die verarbeitungsrelevanten Referenzen
werden im Lauf-Ledger mitgezählt.

## Zulassung

Settings-SHA-256:
`f089d57448c0a762ed13cc10d9460e5cc53d9ab81b2008dcd9b2f39376e1a8c3`.
Bindungsdigest:
`d2cda8bd763a691e3980e702292da11aec9844ab6483e014bcec1e7a1509b509`.

Die Datei `authorization.json` wurde **nicht erstellt**. Nach separater
Freigabe muss sie exakt die von `expected_authorization()` bestimmte
kanonische Form enthalten: Lauf-/Manifest-/Profil-/Codebindung, Settingshash
und drei einmalige Rollenabschnitte. Der Hauptaufrufer verbraucht sie vor dem
Start; jeder Worker prüft sie selbst vor der Gateöffnung und verbraucht seine
Rollenmarke. Ein Dispatch allein genügt nicht.

## Späterer Dateieinstieg

**Nicht jetzt ausführen.** Arbeitsverzeichnis:
`C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`

```powershell
C:/Python314/python.exe -m tools._checkpoint_transfer_entry run reports/memory-restart-transfer-final/settings.json reports/memory-restart-transfer-final/authorization.json
```

Keine direkte Workerbedienung und kein Retry. Der Aufrufer wartet auf das
Prozessende, verifiziert den Gesamtbeleg genau einmal und wertet erst danach
getrennt aus. Feld-/Memory-/Generations- und Entscheidungsvergleiche sowie
Lesekonten bleiben einzeln sichtbar. Gültige Enthaltung ist kein Fehler.
Bei Schreibproblemen wird kein gesicherter Abschluss behauptet.

Private Grenzen: Metadaten/Quellen je 196.608 Byte, Zusatzhülle 262.144 Byte,
Verifikation 262.144 Byte, Feldcheckpoint 524.288 Byte, Gesamt 5.242.880 Byte.
Die tatsächliche Laufbilanz wird zusätzlich geprüft; kein Schutzwert ist ein
bereits gemessener Laufwert. Keine allgemeine Crash-Recovery oder Quellenidentität.
