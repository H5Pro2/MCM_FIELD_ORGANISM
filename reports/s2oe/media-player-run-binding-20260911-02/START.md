# Startbereitschaft: technisch gebunden, Einmallauffreigabe ausstehend

Lauf-ID: `media-memory-video-20260911-01` (unverbraucht).
Bedienadresse nach Start: `http://127.0.0.1:43823/`.
Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.

## Konkreter Befehl nach separater Freigabe

```powershell
C:/Python314/python.exe -m reports.start_bound_media_player `
  --binding reports/s2oe/media-player-run-binding-20260911-02/settings.json `
  --binding-sha256 18d6c1799b26a98869bb93d500d0a7779eaa282dde217b317bea6644db2de696 `
  --authorization reports/s2oe/media-player-run-binding-20260911-02/authorization.json `
  --authorization-sha256 830b7141f39a7dc50fa2ef3e0ad4aa57d25718ea1f414c5c639ac2f0ba294624 `
  --port 43823
```

`authorization.json` wird erst nach ausdrücklicher Einmallauffreigabe
bereitgestellt. Sein vorgebundener Inhalt entspricht exakt der kanonischen
`authorization-template.json`, ausschließlich mit `authorized: true`.
Bis dahin liegt nur die unwirksame Vorlage mit `authorized: false` vor.
Nicht selbst umschalten, starten oder die Freigabe durch einen Inline-Aufruf ersetzen.

## Bedienung

- **Vorschau:** nur die ausgewählte lokale Datei, keine Aufnahme anderer Tabs
  oder Geräte. Vorschau und Decoder sind nicht synchronisiert.
- **Start:** erster autorisierter Klick verbraucht die Einmalfreigabe und
  startet eine Sitzung. Die Vorschau wird angehalten. Kein automatischer Retry.
- **Status:** Ereigniszahl, Durchlauf, Medienfenster, Runtimezeit, Wahrnehmung,
  Memory und Hypothese beziehungsweise Enthaltung. Keine Bedeutungszuordnung.
- **Stopp:** kontrolliert beenden; vorzeitiger Abschluss ist kein voller Erfolg.
  Der Player verifiziert einmal. Kein zweiter äußerer Verifikatoraufruf.
- Nach Abschluss kein Neustart derselben ID. Server mit Strg+C schließen.

## Gebundener Umfang und Grenzen

Ausgewählt: `C:\Users\TV\Downloads\17138816-uhd_3840_2160_30fps.mp4`.
Zwei Durchläufe über 0 bis 5 Sekunden: 24 Ereignisse, 20 Formationen,
vier read-only Hinweise, 22 Audio-/NJ- und 22 visuelle Verarbeitungen,
7.392 Feldkontakte, acht Scans. Memory bleibt erhalten, Runtimezeit steigt.
Audiofenster und Frameauswahl sind abgetastet, keine vollständige Medienaufnahme.

Maxima: Metadaten 100.017 / 131.072, Quellen 259.828 / 262.144,
Zusatzhülle 343.796 / 393.216, Laufgesamt 3.818.322 / 4.194.304 Byte.
Inklusive vollständiger Qualifikation, gemeinsamer Dateien einmal gezählt:
3.948.265 Byte. Einzelbeiträge und Reserven stehen vollständig in `budget.json`.

Noch kein Medienlauf gestartet. Dateihash, Decoderfähigkeit und Ressourcen
werden im später freigegebenen Lauf überprüft; dafür besteht keine Erfolgsgarantie.
Browser und Betriebssystem gehören nicht zum 512-MiB-Decoderjob.
