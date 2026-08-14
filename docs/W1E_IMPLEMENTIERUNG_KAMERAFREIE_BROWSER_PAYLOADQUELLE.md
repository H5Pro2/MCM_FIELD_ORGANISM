# W1-E: Implementierung der kamerafreien Browser-Payloadquelle

Stand: 2026-08-07

Entscheidung: `W1E_CAMERA_FREE_BROWSER_PAYLOAD_SOURCE_IMPLEMENTED`

Forschungslauf: nein

Browser gestartet: nein

## Ergebnis

Der in W1-D gebundene allgemeine Quellenrand ist implementiert. Eine lokale,
parametrierte Browserseite kann kontrollierte Canvasbilder und
Offline-Audiosamples bereitstellen. Der Pythonhandoff uebergibt diese
Payloads unmittelbar an die fertige W1-C-Bruecke und gibt nur reduzierte
Rezeptorsequenzen sowie einen skalaren technischen Receipt zurueck.

## Neue Assets

Unter `tools/controlled_browser_payload_world/` bestehen jetzt:

- `index.html` mit streng lokaler Content-Security-Policy und genau einem
  Canvas;
- `styles.css` ohne dynamische Layoutlogik;
- `world.js` mit `configureWorld()`, `renderVisualFrame()`, `renderAudio()`,
  `readAudioChunk()` und `releaseAudio()`.

Die Seite besitzt keine Wanduhr, keinen Animationsloop, keine Timersteuerung,
keinen Live-Audioausgang, keine Sensor-API, kein Netzwerk, keinen lokalen
Speicher und keine Interaktion. Weltprogramm, Rendergeometrie und native
Raten werden vollstaendig von Python uebergeben.

## Neue Pythonrollen

`mcm_field_organism/browser_payload_source.py` implementiert:

- `BrowserPayloadSourceConfig` mit validierter Canvas-, Bewegungs-, Farb- und
  Audioquellenkonfiguration sowie kanonischem Digest;
- `BrowserPayloadCapturePreflight` fuer frischen isolierten Kontext,
  Viewport, Device-Scale und JavaScriptgrenze;
- `BrowserPayloadCaptureReceipt` als rein skalare Abnahme ohne Rohpayload;
- `browser_payload_asset_digests()` fuer das exakte lokale Assetinventar;
- `capture_browser_payload_page()` fuer eine bereits erstellte Seite.

Die Capture-Funktion startet selbst keinen Browser. Sie erlaubt genau die
drei lokalen Assets, konfiguriert die Seite einmal, uebergibt jedes Canvas-PNG
und jeden PCM-Hop unmittelbar an `BrowserReceptorBridge`, gibt den
Browser-Audiopuffer auch bei Fehlern frei und finalisiert danach den
reduzierten Batch.

## Durchgaengiger technischer Pfad

Die Fake-Seiten-Abnahme prueft die echte Kette:

```text
BrowserWorldContract + BrowserPayloadSourceConfig
-> kontrollierte Fake-Seite mit derselben Page-API
-> capture_browser_payload_page
-> BrowserReceptorBridge
-> auditory + visual ReceptorTimeSequence
-> advance_audio_video_receptor_sequences
-> gemeinsames neutrales S/H-Feld
```

Die Fake-Seite ersetzt nur Browserengine und JavaScriptausfuehrung. Alle
Pythonvertraege, PNG-Dekodierung, PCM-Reduktion, Zeitbindung, Batchbildung und
Felduebergabe sind die realen W1-Komponenten.

## Geschlossene Grenzen

Technisch getestet sind:

- deterministische Quellenkonfiguration und Assetdigests;
- vollstaendiges und ausschliesslich lokales Assetinventar;
- statische Abwesenheit verbotener Browser- und Sensor-APIs;
- Abbruch bei einem fremden Request vor jeder Payloaduebergabe;
- exakte Konfigurationsgleichheit zwischen Quelle und W1-C-Rezeptoren;
- geordnete PNG- und PCM-Inventare;
- unmittelbare Reduktion und atomare Batchfinalisierung;
- Audiopufferfreigabe nach Erfolg und Adapterfehler;
- Receipt ohne Rohpayload, Rezeptorwerte oder semantische Rollen;
- End-to-End-Handoff des Fake-Seiten-Batches in das vorhandene S/H-Feld;
- Paketexport der neuen allgemeinen Rollen;
- statische Freiheit von Z4-, Kamera-, Mikrofon- und F3-Importen.

## Technische Verifikation

Die isolierte W1-E-, W1-C- und Architektur-API-Suite bestand mit
`14 passed`.

Der relevante Gesamtverbund aus Browserquelle, Browserbruecke, Audio, Video,
AV, Rezeptorzeit, kontrollierter AV-Testwelt, neutraler Runtime, Verteiler,
gemeinsamem Feld, bestehenden Browservertraegen, Live-Handoff-Mocks und
vorherigem Zustandsbeitrag bestand mit `126 passed` und 9 Subtests.

Die bekannte Pytest-Cachewarnung `WinError 183` betrifft nur den vorhandenen
lokalen Cachepfad. Es wurde kein Browser, keine Kamera, kein Mikrofon, kein
Runner und kein Forschungslauf gestartet.

## Abgrenzung

Die neuen Assets und das neue Modul referenzieren keine Z4-Assets,
Z4-Module, P0-, F3- oder B3-Pfade. Lauf 197 und seine reservierten Dateien
bleiben unangetastet.

W1-E weist keine Wahrnehmung, Wiedererkennung, Praegung, Feldzeit, Memory,
Organisation, Semantik oder KI nach. Er schliesst ausschliesslich den
technischen Quellen- und Uebergabepfad bis zur Browserprozessgrenze.

## W1-E-Entscheidung

```text
allgemeine lokale Browserassets:         implementiert
parametrierte Quellenkonfiguration:      implementiert
lokale Requestgrenze:                    implementiert
unmittelbarer W1-C-Capture-Handoff:      implementiert
skalare technische Abnahme:              implementiert
Fake-Seiten-End-to-End-S/H-Pfad:         bestanden
Rohdatenhaltung:                         nein
Z4-/Kamera-/Mikrofonpfad:                nein
realer Browserstart:                     nein
Forschungslauf:                          nein
```

## Bester naechster Schritt

W1-F bindet vor jeder Ausfuehrung einen minimalen realen technischen
Browser-Smoke: gepinnte lokale Runtime, frischer isolierter Kontext, nur die
drei W1-Assets, kurze kontrollierte Welt, vollstaendige PNG-/PCM-Uebergabe,
Batch- und S/H-Handoff sowie garantiertes Schliessen von Seite, Kontext und
Browser. Noch keine Ausfuehrung, bis dieser Smokevertrag statisch geschlossen
ist.
