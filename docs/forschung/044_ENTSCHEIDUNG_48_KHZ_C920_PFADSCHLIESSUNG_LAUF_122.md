# Forschung 044: Entscheidung 48 kHz und C920-Pfadschliessung (Lauf 122)

## Forschungsfrage und Auftrag

Soll nach dem negativen nativen Hardwarebefund aus Lauf 121 die bestehende
48-kHz-Anforderung beibehalten und der aktuelle C920-Audioquellenzeitpfad
geschlossen werden, oder laesst sich bereits jetzt ein einzelnes anderes
natives Format unabhaengig und methodisch begruendet vorregistrieren?

Freigegeben war ausschliesslich eine technische Entscheidungsvorregistrierung
auf Grundlage vorhandener Dokumente, Schnittstellen und Befunde. Ein
Hardwarelauf, eine Ratensuche, die Uebernahme eines vorgeschlagenen
Alternativformats und eine Rezeptor- oder Feldanbindung waren nicht
freigegeben.

## Verwendete Dateien und Schnittstellen

- `docs/architektur/031_FELDZEITUEBERGABE.md`
- `docs/architektur/036_BEOBACHTUNGSGRENZE_STATT_FELDTAKT.md`
- `docs/forschung/030_KONZEPT_BESTANDSLUECKE_ASYNCHRONER_AUDIO_VIDEO_WELTKONTAKT.md`
- `docs/forschung/040_VORREGISTRIERUNG_NATIVE_WASAPI_CAPTURE_PROBE_LAUF_118.md`
- `docs/forschung/041_NATIVE_WASAPI_CAPTURE_PROBE_WERKZEUG_LAUF_119.md`
- `docs/forschung/042_NATIVE_WASAPI_ENDPOINT_INVENTAR_LAUF_120.md`
- `docs/forschung/043_NATIVE_WASAPI_100_PAKET_PROBE_LAUF_121.md`
- `mcm_field_organism/log_spectral_receptor.py`
- `mcm_field_organism/live_audio_adapter.py`
- `tools/controlled_browser_world/server.py`
- `tools/run_native_wasapi_capture_probe.py`

Es wurde keine Audio-, Kamera-, Rezeptor- oder Feldschnittstelle ausgefuehrt.

## Durchgefuehrte Schritte

1. Geprueft, ob Architektur 031 oder 036 eine bestimmte Abtastrate als
   Organismuszeit, Feldzeit oder Feldtakt verlangt.
2. Die vorhandenen Audio-Konfigurationen und den Livepfad auf ihre tatsaechlich
   verwendeten Raten und Frequenzgrenzen untersucht.
3. Den negativen Befund aus Lauf 121 gegen die vorhandene technische
   Anschlussbedingung abgegrenzt.
4. Geprueft, ob aus den vorhandenen Metadaten bereits ein einzelnes anderes
   vollstaendiges natives Format ohne nachtraegliche Erfolgsauswahl begruendet
   werden kann.
5. Eine der zwei fuer Lauf 122 zulaessigen Entscheidungen festgelegt.

Es wurde keine Codeaenderung vorgenommen. Der statische Wert
`workflow_run: 119` im Diagnosewerkzeug bleibt als bekannter Metadatenmangel
dokumentiert und wird nicht als Laufnummernbeleg verwendet.

## Befunde und Gegenbaselines

### Architekturgrenze

Architektur 031 verlangt lokale Quellenstuetze, getrennte Rezeptorabschluesse
und eine unabhaengige Organismuszeit. Architektur 036 verbietet, eine
Sensorfrequenz oder frei gewaehlt feste Periode als organischen Feldtakt zu
bezeichnen. Keine der beiden Architekturen fordert 48 kHz als Feld- oder
Organismuseigenschaft.

### Vorhandener technischer 48-kHz-Vertrag

Der produktnahe auditive Rezeptor besitzt in `LogSpectralConfig` aktuell:

```text
sample_rate:    48000 Hz
window_size:    4800 Samples
hop_size:       480 Samples
min_frequency:  50 Hz
max_frequency:  18000 Hz
band_count:     48
```

Der kontrollierte Browser-Weltpfad erzeugt ebenfalls explizit eine
Audio-Konfiguration mit `sample_rate=48000` und `frame_size=480`. Der
`SoundDeviceInputSource` reicht die konfigurierte Rate unveraendert an
`sounddevice.check_input_settings` und `sounddevice.InputStream` weiter.

Damit ist 48 kHz eine vorhandene technische Anschlussbedingung des aktuellen
hochaufloesenden auditiven Pfades. Sie ist kein natuerlicher Feldtakt und keine
MCM-Eigenschaft.

### Reale Hardwarebaseline

Lauf 121 ergab fuer den lokal zugeordneten C920-WASAPI-Endpoint:

```text
exakt 48000 Hz, Mono, float32, Shared Mode: nicht unterstuetzt
Pakete:                                         0
Entscheidung:                                   TECHNISCH_NEGATIV
```

### Alternative Formatbaseline

Das Endpoint-Inventar meldete nur Teilmetadaten eines nativen Mixformats:
16 kHz, zwei Kanaele und 32 Bit. Es wies den vollstaendigen Formattyp und die
fuer eine exakte neue Vorregistrierung erforderlichen
`WAVEFORMATEXTENSIBLE`-Eigenschaften nicht aus. Die DirectSound-Sicht meldete
daneben 44,1 kHz als Default-Rate.

Diese voneinander abweichenden Metadaten begruenden kein einzelnes neues
natives Format. Eine Wahl von 16 oder 44,1 kHz waere zum jetzigen Zeitpunkt
eine nachtraegliche Parameterauswahl ohne vollstaendigen Schnittstellenvertrag.

## Beobachtetes Ergebnis

48 kHz ist nicht architektonisch als Feldrate vorgeschrieben, aber im aktuellen
produktnahen Audiorezeptor und Livepfad konkret implementiert. Der C920-Endpoint
kann den exakt vorregistrierten nativen 48-kHz-Vertrag nicht erfuellen.

Aus den vorhandenen Metadaten kann kein einzelnes alternatives natives Format
vollstaendig und unabhaengig begruendet werden.

## Technische Interpretation

Die saubere Entscheidung ist, den bestehenden 48-kHz-Vertrag fuer den
aktuellen produktnahen Auditivrezeptor beizubehalten und den nativen
C920-Audioquellenzeitpfad fuer genau diesen Vertrag zu schliessen.

Diese Pfadschliessung betrifft nicht:

- WASAPI allgemein;
- jede moegliche C920-Aufnahme;
- synthetische Audioschnittstellen;
- andere, spaeter eindeutig inventarisierte Aufnahmegeraete;
- die allgemeine Frage nach lokaler Quellenstuetze.

Sie verhindert lediglich, dass nach dem negativen Ergebnis durch Ratensuche,
Konversion oder nachtraegliche Auswahl ein positiver Kandidat erzeugt wird.

## Entscheidung

```text
48_KHZ_TECHNISCHER_VERTRAG:       BESTAETIGT
C920_NATIVE_48_KHZ_QUELLENZEIT:   GESCHLOSSEN
ALTERNATIVFORMAT_VORREGISTRIERT:   NEIN
HARDWARELAUF_DURCHGEFUEHRT:        NEIN
QUELLENSTUETZE_NACHGEWIESEN:       NEIN
FELDANBINDUNG:                     NEIN
```

## Messergebnisse

Lauf 122 war kein Messlauf. Es wurden keine neuen Hardwarewerte, Pakete,
Device-Positionen, QPC-Positionen oder Statusflags erhoben. Die verwendeten
Zahlen sind bereits vorhandene Konfigurationswerte und Befunde aus den Laeufen
120 und 121.

## Grenzen und nicht gepruefte Annahmen

- Es wurde nicht geprueft, welches vollstaendige native Mixformat die C920
  exponiert.
- Andere Raten, Kanalzahlen, Sampleformate und Share Modes wurden nicht
  getestet oder vorregistriert.
- Es wurde kein alternatives Aufnahmegeraet inventarisiert.
- Die Zweckmaessigkeit von 48 kHz fuer jede spaetere Projektphase ist keine
  naturgegebene Annahme; die Entscheidung bewahrt nur den aktuellen
  technischen Vertrag.
- Paketposition, Quellenstuetze, Organismuszeit und MCM-Feldzeit sind nicht
  nachgewiesen.
- Forschung 030 bleibt gesperrt.
- Memory, Organisation, Semantik und Topologie wurden nicht untersucht oder
  nachgewiesen.
- Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Lauf 122 bestaetigt 48 kHz als vorhandene technische Anschlussbedingung des
aktuellen produktnahen auditiven Rezeptor- und Livepfads, nicht als Feldtakt
oder Organismuszeit. Der native C920-Audioquellenzeitpfad wird fuer diesen
Vertrag geschlossen. Ein alternatives Format wird nicht vorregistriert.

Die klare Stopplinie bleibt erhalten: kein weiterer C920-Probe mit veraenderten
Parametern und keine Quellenstuetzenableitung aus Callback-, Latenz- oder
Defaultformatdaten.

## Naechster begrenzter Forschungslauf

Aus jetziger Sicht sollte Lauf 123 den geschlossenen C920-Zweig nicht erneut
oeffnen. Als naechster begrenzter technischer Schritt ist eine reine
Anschlussstellenentscheidung sinnvoll:

- pruefen, ob ein anderes bereits vorhandenes oder ausdruecklich
  bereitgestelltes Capture-Geraet den unveraenderten 48-kHz-Mono-`float32`-
  Vertrag nativ erfuellen kann;
- zunaechst nur Endpoint-Inventar und exakte Formatmetadaten, ohne Streamstart
  und ohne Paketerfassung;
- falls kein solches Geraet vorhanden ist, den nativen Audioquellenzeit-Zweig
  vorerst als technische Projektgrenze ruhen lassen und den unabhaengigen
  physischen Feld-Welt-Feld-Grundlagenzweig priorisieren.

Ein weiterer Hardware-Capture-Lauf bedarf erneut einer separaten
Vorregistrierung und Freigabe.

## Tatsaechlich verwendete Quellen

- `docs/architektur/031_FELDZEITUEBERGABE.md`
- `docs/architektur/036_BEOBACHTUNGSGRENZE_STATT_FELDTAKT.md`
- `docs/forschung/030_KONZEPT_BESTANDSLUECKE_ASYNCHRONER_AUDIO_VIDEO_WELTKONTAKT.md`
- `docs/forschung/040_VORREGISTRIERUNG_NATIVE_WASAPI_CAPTURE_PROBE_LAUF_118.md`
- `docs/forschung/042_NATIVE_WASAPI_ENDPOINT_INVENTAR_LAUF_120.md`
- `docs/forschung/043_NATIVE_WASAPI_100_PAKET_PROBE_LAUF_121.md`
- `mcm_field_organism/log_spectral_receptor.py`
- `mcm_field_organism/live_audio_adapter.py`
- `tools/controlled_browser_world/server.py`
- `tools/run_native_wasapi_capture_probe.py`

MINI_DIO und externe MCM-Mechaniken wurden nicht verwendet.
