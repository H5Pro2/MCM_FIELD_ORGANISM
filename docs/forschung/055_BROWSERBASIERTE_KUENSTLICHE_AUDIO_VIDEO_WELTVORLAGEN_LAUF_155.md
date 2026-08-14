# Browserbasierte kuenstliche Audio-Video-Weltvorlagen (Lauf 155)

## Forschungsfrage und Auftrag

Welche kuenstlichen Audio-Video-Weltvorlagen eignen sich fuer kontrollierte
Browserdarstellung, waehrend der reale Kameraraum dunkel und unbewegt ist, und
wie soll die weitere Entwicklung erfolgen, ohne Browserwiedergabe mit einem
tatsaechlichen Rezeptoranschluss gleichzusetzen?

Der Auftrag umfasst Materialsuche, Bestandsabgleich und Entwicklungsplanung.
Er umfasst keinen realen Kamera-Abnahmeversuch und keine neue Feldmechanik.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- aktueller Benutzerauftrag und die Praeferenz fuer kuenstliche Audio-Video-Welten,
- `mcm_field_organism/browser_world_contract.py`,
- `tools/controlled_browser_world/index.html`,
- `tools/controlled_browser_world/stimulus.js`,
- `tools/controlled_browser_world/server.py`,
- `mcm_field_organism/controlled_audio_video_test_world.py`,
- `tools/run_controlled_audio_video_test_world.py`,
- `tests/test_browser_world_contract.py`,
- `tests/test_controlled_browser_world_assets.py`,
- `tests/test_controlled_browser_world_server.py`,
- `tests/test_controlled_audio_video_test_world.py`,
- `docs/forschung/030_KONZEPT_BESTANDSLUECKE_ASYNCHRONER_AUDIO_VIDEO_WELTKONTAKT.md`,
- MDN, Canvas basic animations:
  https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Basic_animations
- MDN, Web Audio API:
  https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- MDN, `createOscillator()`:
  https://developer.mozilla.org/en-US/docs/Web/API/BaseAudioContext/createOscillator
- MDN, Advanced audio scheduling:
  https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Advanced_techniques
- Tone.js, offizielle Projektseite: https://tonejs.github.io/
- p5.js, offizielle Beispiele: https://p5js.org/examples/
- Three.js, offizielle Beispiele: https://threejs.org/examples/

Es wurde keine Medienquelle heruntergeladen, lokal kopiert oder transkodiert.
Die direkte Browserinspektion von MDN wurde durch die vorhandene
Browser-Sicherheitsrichtlinie abgewiesen. Diese Grenze wurde nicht umgangen.

## Verwendete Dateien und Schnittstellen

Die bestehende Browserwelt verwendet `canvas`, `requestAnimationFrame`,
`AudioContext`, einen Oszillator und einen Gain-Knoten. Ihr Vertrag beschreibt
eine externe, passive und nicht speichernde Darstellung mit drei Phasen. Der
Vertrag setzt `direct_sensor_feed=False`.

Die prozedurale Testwelt erzeugt dagegen kontrollierte Audio- und Videowerte
direkt fuer die bereits vorhandenen Rezeptorschnittstellen und das gemeinsame
Feld. Sie ist daher die geeignete technische Basis fuer synthetische
Feldversuche. Browserwelt und prozedurale Rezeptorwelt sind zwei getrennte
Schnittstellen und duerfen nicht als identisch behandelt werden.

## Durchgefuehrte Schritte

1. Bestehende Browser-, Audio-, Video-, Rezeptor- und Feldschnittstellen wurden
   lokal inventarisiert.
2. Externe Browserbausteine wurden nach Determinismus, Zeitsteuerung,
   Abhaengigkeiten und Medienfreiheit bewertet.
3. Die vorhandene Browserwelt wurde gegen die prozedurale Rezeptorwelt
   abgegrenzt.
4. Die vier fokussierten Testsammlungen wurden gemeinsam ausgefuehrt.
5. Ein begrenzter Entwicklungsverlauf wurde zusammengestellt.

## Messergebnisse und Gegenbaselines

Testaufruf:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_browser_world_contract.py tests/test_controlled_browser_world_assets.py tests/test_controlled_browser_world_server.py tests/test_controlled_audio_video_test_world.py
```

Ergebnis:

```text
18 passed in 1.96s
```

Beobachtet:

- Die bestehende Browserwelt ist lokal vorhanden und gegen Kamera-, Mikrofon-,
  Speicher- und direkten Sensorzugriff begrenzt.
- Die bestehende prozedurale Audio-Video-Welt ist wiederholbar und erreicht den
  vorhandenen synthetischen Rezeptor-/Feldpfad ohne Rohdatenspeicherung.
- Native Canvas- und Web-Audio-Bausteine reichen fuer bewegte Geometrie,
  periodische Toene und zeitgesteuerte Phasen aus.

Gegenbaselines fuer die weitere Weltmatrix:

- `W0`: statisches Bild, Stille,
- `WV`: bewegtes Bild, Stille,
- `WA`: statisches Bild, periodischer Ton,
- `WAV`: bewegtes Bild, periodischer Ton.

Diese Bezeichnungen sind ausschliesslich technische Versuchskennungen. Sie
tragen keine Bedeutung und definieren kein Zielverhalten.

## Materialbewertung

### 1. Native Canvas und Web Audio

Bevorzugte Vorlage. Sie entspricht dem bestehenden Projekt, benoetigt keine
externe Medienbibliothek und erlaubt kontrollierte Geometrie, Frequenz,
Amplitude, Phasendauer und Ereignisfolge. Audio muss durch eine menschliche
Browseraktion gestartet werden. `requestAnimationFrame` kann in inaktiven Tabs
gedrosselt werden; deshalb ist es keine verlaessliche Organismuszeit.

### 2. MDN Audio-Scheduling-Beispiel

Geeignet als technische Vorlage fuer Zeitplanung mit
`AudioContext.currentTime`. Nicht uebernommen werden zufaellige Quellen,
Dateisamples oder musikalische Semantik.

### 3. p5.js

Geeignet fuer schnelle, sichtbare Skizzen. Wegen zusaetzlicher Abhaengigkeit und
leicht verfuegbarer Zufalls-, Mikrofon- und Dateifunktionen nur zweite Wahl fuer
kontrollierte Laeufe.

### 4. Tone.js

Geeignet, falls die native Web-Audio-Zeitplanung nachweislich nicht ausreicht.
Fuer den aktuellen Umfang ist die zusaetzliche Abhaengigkeit nicht erforderlich.

### 5. Three.js

Erst sinnvoll, wenn Tiefe, Verdeckung oder Kameraperspektive als begrenzte
Versuchsvariable vorregistriert werden. Fuer die aktuelle 2D Audio-Video-Frage
ist es unnoetig komplex.

Nicht bevorzugt sind Stockvideos, Videostreams, zufaellige generative Welten,
Mikrofon-/Webcam-Demos und dateigeladene Audiosamples. Sie erschweren
Quellengleichheit, Zeitkontrolle und reproduzierbare Gegenbaselines.

## Grenzen und nicht gepruefte Annahmen

- Browserwiedergabe speist nicht automatisch den visuellen oder auditiven
  Rezeptorpfad. Im aktuellen Vertrag ist ein direkter Sensorfeed ausdruecklich
  ausgeschlossen.
- Es wurde in Lauf 155 keine Browserausgabe ueber Kamera oder Mikrofon erfasst.
- Es wurde keine neue Feldtransition ausgefuehrt und keine Feldwirkung gemessen.
- Die reale Stabilitaet von Audio-/Videotiming bei Hintergrundtab, Fensterfokus,
  Bildwiederholrate und Betriebssystemlast ist noch nicht gemessen.
- Aus den 18 bestandenen Tests folgt nur technische Vertrags- und
  Implementierungsbereitschaft, keine Memory-, Organisations-, Semantik- oder
  Topologiewirkung.
- Der dunkle, unbewegte Kameraraum ist eine aktuelle Umweltbedingung und kein
  Befund ueber den Kamerapfad.

## Konkrete Schlussfolgerung

Die beste unmittelbare kuenstliche Welt ist keine externe Video- oder
Audiodatei, sondern die bereits vorhandene native Canvas-/Web-Audio-Welt mit
prozedural erzeugten, kontrollierbaren Reizen. Fuer Feldversuche muss parallel
die bestehende prozedurale Audio-Video-Testwelt verwendet werden, weil nur sie
einen nachgewiesenen synthetischen Rezeptoranschluss besitzt.

Browserdarstellung dient damit als kontrollierbare externe Weltvorlage;
prozedurale Rezeptorwerte dienen als reproduzierbare technische Versuchseingabe.
Eine Gleichsetzung beider Pfade ist nicht zulaessig. Eine Zielabweichung ist
nicht erkennbar.

## Weiterer Entwicklungsverlauf

1. Die vier technische Weltzustaende `W0`, `WV`, `WA` und `WAV` mit identischer
   Gesamtdauer und festem Startzeitpunkt vorregistrieren.
2. Dieselben Quellen einmal mit feiner und einmal mit grober Audio-/Video-
   Ereignisteilung in der bestehenden prozeduralen Welt ausfuehren.
3. Als Gegenbaselines Audio-allein, Video-allein, neutral sowie vertauschte
   Ereignisreihenfolge verwenden; Quellen, Gesamtenergie und Dauer konstant
   halten.
4. Nur Feldzustandsdifferenzen, Zeitkontinuitaet, Ereignisanzahl und
   Reproduzierbarkeit messen. Keine Memoryvariable oder Bedeutung ergaenzen.
5. Erst nach stabiler synthetischer Asynchronitaetspruefung die Browserwelt in
   einem separaten realen Kamera-/Mikrofonlauf untersuchen. Dafuer ist eine neue
   Freigabe und menschliche Startbestaetigung erforderlich.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Lauf 156 sollte die offene Frage aus Forschung 030 als parametrisierten
synthetischen Asynchronitaetslauf pruefen: identische prozedurale Audio- und
Videoquellen, identische Gesamtdauer und identische Feldmechanik, aber feine
gegen grobe Ereignisteilung sowie vertauschte Reihenfolge. Der Lauf soll nur
feststellen, ob die resultierende Feldwirkung gleich bleibt oder von der
Ereignisorganisation abhaengt. Ein Browser-, Kamera- oder Mikrofonzugriff ist
dabei nicht erforderlich.
