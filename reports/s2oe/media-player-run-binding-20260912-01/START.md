# Gebundener UHD-Videoversuch

Lauf-ID: `media-memory-video-20260911-02`. Noch nicht ausgeführt.
Dieselbe MP4, zwei Durchläufe, 20 Formationen und vier read-only Hinweise.
Eine Sitzung; Medienzeit beginnt im zweiten Durchlauf erneut, Runtimezeit nicht.
Privates UHD-Profil mit jeweils 1024 MiB Prozess-/Job-Commit, keine globale Erhöhung.

## Bedienseite vorbereiten

Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.
Der folgende Befehl startet ausschließlich die gesperrte Bedienseite.
Er wurde vom Entwickler nicht ausgeführt.

```powershell
C:/Python314/python.exe -m reports.start_bound_media_player --binding reports/s2oe/media-player-run-binding-20260912-01/start-settings.json --binding-sha256 2eebcb9bc95a477f11c7a80140a3ed364b914c2216bbc7526d7cd71ae7370f42 --port 43824
```

Bedienadresse nach Serverstart: `http://127.0.0.1:43824/`.
Ist der Port belegt, nicht automatisch auf eine andere Bindung ausweichen.

Ohne separate Einmallauffreigabe und deren dateigebundene Autorisierung bleibt
der Status `AUTHORIZATION_REQUIRED`. `start-authorization-template.json`
enthält absichtlich `authorized:false` und ist keine wirksame Freigabe.
Nach Freigabe muss eine neue Autorisierungsdatei mit ihrem SHA-256 über die
vorhandenen Argumente `--authorization` und `--authorization-sha256` gebunden
werden. Keine alte Autorisierung oder Verbrauchsdatei wiederverwenden.

Start verarbeitet ausschließlich die gebundene Folge; Status zeigt Fortschritt
und technische Rückgaben, Stopp beendet kontrolliert. Der Player übernimmt
genau eine Verifikation. Keine zusätzliche Verifikationsschleife starten.

## Verbindliche Dateien

- `start-settings.json`: finale Startbindung, nicht die frühere `settings.json`.
- `common.json`: Quelle, Ereignisse, Profile und aktive Referenzen.
- `budget-closure.json`: vollständige Budgethülle einschließlich physischer Budgetdatei.
- `budget.json`: alle 50 Fortschritts-/Abschlussalternativen.

Maxima: Quellen 283.802 / 327.680; Metadaten 107.407 / 131.072;
Zusatzhülle 367.770 / 393.216; Laufgesamt 3.849.686 / 4.194.304 Byte.
Einschließlich vollständiger zusätzlicher Qualifikationsreserve: 3.898.838 Byte.
Der erste volle Wahrnehmungs-/Memorybefund dieser Videozuführung bleibt offen.

Historischer Fehlversuch bleibt `NOT_EVALUABLE`. Keine automatische Wiederholung.
