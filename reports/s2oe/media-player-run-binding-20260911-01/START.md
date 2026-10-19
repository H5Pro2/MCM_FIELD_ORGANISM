# Vorbereiteter Einstieg: noch nicht startbereit

Lauf-ID: `media-memory-video-20260911-01`, unverbraucht.
Die administrative Playerzulassung ist gültig. Die vollständige reale
Laufbilanz überschreitet aber die Sitzungsmetadatengrenze um 3.703 Byte.
`budget.json` enthält die Verletzungen; der Starter muss daher ablehnen.
Keine Freigabe zum Medien- oder Lernlauf und keine wirksame Autorisierungsdatei.

Arbeitsverzeichnis:
`C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`

Vorbereiteter Befehl, derzeit **nicht ausführen**:

```powershell
C:/Python314/python.exe -m reports.start_bound_media_player --binding reports/s2oe/media-player-run-binding-20260911-01/settings.json --binding-sha256 50c1220e6edaf6424d82acd2daf23678699915e1a8bf1da9149c93281167b18d --port 43823
```

Ohne separate Autorisierung öffnet dieser Einstieg auch nach einer späteren
Budgetfreigabe kein Memorygate. Die Oberfläche würde unter
`http://127.0.0.1:43823/` ausschließlich die gebundene Datei anbieten.
Start bleibt ohne passende Einmalautorisierung gesperrt.

Bedienung nach gültiger vollständiger Laufbindung und separater Freigabe:

- **Start:** Vorschau anhalten; eine Sitzung, zwei abgetastete Durchläufe.
- **Status:** Fortschritt, gewähltes Fenster, Runtimezeit, Memory und
  Hypothese beziehungsweise Enthaltung aus vorhandenen Rückgaben anzeigen.
- **Stopp:** kontrollierter vorzeitiger Abschluss, kein vollständiger Erfolg.
- Die einmalige Verifikation übernimmt der Player, nicht eine äußere Hülle.
- Browser-Vorschau und Decoder sind nicht synchronisiert. Kein anderer Tab,
  keine Kamera und kein Mikrofon werden aufgenommen.

`authorization-template.json` enthält ausdrücklich `authorized: false` und
ist keine Startfreigabe. Nicht zum Umgehen der noch ungültigen Bilanz ändern.
Die ausgewählte MP4 wurde für diese Vorbereitung nicht geöffnet. Die alte
Quellenbindung ist unverändert als Herkunft referenziert.
