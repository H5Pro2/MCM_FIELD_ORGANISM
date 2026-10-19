# Vollständiger Videoversuch mit korrigierter Bedienung

Neue Lauf-ID: `media-memory-video-20260912-01`. Noch nicht freigegeben oder gestartet.
Der Entwickler übernimmt nach separater Freigabe Start und Überwachung;
kein wiederholtes manuelles Play durch den Benutzer erforderlich.

Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.
Dateigebundener Starter, neue Bedienadresse `http://127.0.0.1:43825/`:

```powershell
C:/Python314/python.exe -m reports.start_bound_media_player --binding reports/s2oe/media-player-run-binding-20260912-03/settings.json --binding-sha256 ae606ab454bd50ebf347e2b0cb94ba4e744992c8dc83ecce2622d1f37624b90e --port 43825
```

Ohne wirksame Autorisierung öffnet dieser Befehl nur die gesperrte Bedienseite.
Vor tatsächlichem Start ist eine separate Einmalautorisierung auf Grundlage
von `authorization-template.json` zu binden und über `--authorization` sowie
`--authorization-sha256` zu übergeben. Vorlage false lassen, bis die Freigabe
erteilt ist. Keine alte Verbrauchsdatei oder alte Autorisierung verwenden.

Vorschau optional und unsynchron. Bei MCM-Start ist sie inaktiv; die
Betriebsanzeige zeigt abgeschlossene Ereignisse, Durchlauf und tatsächlich
verarbeitetes Medienfenster. Unvollständiger Abschluss und Stoppauslöser
werden getrennt vom Erfolg dargestellt. Unbekannte Ursachen bleiben unbekannt.

Der Player verifiziert den Abschluss einmal. Keine zweite Verifikation,
kein Retry und keine automatische Wiederaufnahme. Fachliche Auswertung nur
nach technisch gültigem vollständigem Abschluss; ein neuer Betriebserfolg
ist durch die neutrale Bedienprüfung noch nicht behauptet.

Quelle/Ereignisse/Profil unverändert: zwei Durchläufe, 20 Formationen,
vier vorgelagerte read-only Hinweise; privates 1024-MiB-UHD-Profil.
Metadatenmaximum 112.406, Quellen 298.213, Zusatzhülle 382.181 Byte;
Gesamt mit vollständiger zusätzlicher Qualifikationsreserve 3.934.632 Byte.
Alle bisherigen übergeordneten Grenzen bleiben bestehen.

Der alte Port 43824 und `media-memory-video-20260911-02` gehören zum
unverändert geschlossenen historischen Versuch, nicht zum neuen Startweg.
