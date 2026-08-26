# Forschung 045: Andere 48-kHz-Capture-Endpoints (Lauf 123)

## Forschungsfrage und Auftrag

Ist neben dem in Lauf 122 geschlossenen C920-Endpoint ein anderes bereits
vorhandenes oder ausdruecklich bereitgestelltes aktives Capture-Geraet
verfuegbar, das als Kandidat fuer den unveraenderten technischen
48-kHz-Mono-`float32`-Shared-Mode-Vertrag geprueft werden kann?

Freigegeben waren eine reine Anschlussstellenpruefung und hoechstens eine eng
begrenzte Erweiterung fuer vollstaendige Formatmetadaten. Nicht freigegeben
waren eine Wiedereroeffnung des C920-Capture-Zweigs, Streaminitialisierung,
Streamstart, `GetBuffer`, Paketerfassung, Ratensuche, Formatkonversion sowie
Rezeptor- oder Feldanbindung.

## Verwendete Dateien und Schnittstellen

- `docs/forschung/042_NATIVE_WASAPI_ENDPOINT_INVENTAR_LAUF_120.md`
- `docs/forschung/043_NATIVE_WASAPI_100_PAKET_PROBE_LAUF_121.md`
- `docs/forschung/044_ENTSCHEIDUNG_48_KHZ_C920_PFADSCHLIESSUNG_LAUF_122.md`
- `tools/run_native_wasapi_endpoint_inventory.py`
- `tests/test_native_wasapi_endpoint_inventory_tool.py`
- `IMMDeviceEnumerator::EnumAudioEndpoints`
- passive MMDevice-/WASAPI-Endpoint-Metadaten
- unveraenderte lokale `sounddevice`-Metadaten fuer die Vergleichssicht

`IAudioClient::Initialize`, `IAudioClient::Start`,
`IAudioCaptureClient::GetBuffer` und `IAudioCaptureClient::ReleaseBuffer`
wurden nicht aufgerufen.

## Durchgefuehrte Schritte

1. Geprueft, ob der vorhandene Inventarpfad Streams oder Pakete oeffnet. Der
   Pfad liest nur Endpoint- und Mixformat-Metadaten und setzt alle Stream-,
   Paket-, Quellenstuetzen- und Feldhandlungen auf `False`.
2. Eine aktuelle native Inventarisierung der aktiven Capture-Endpoints
   ausgefuehrt.
3. Den in Lauf 122 geschlossenen C920-Endpoint anhand seiner vollstaendigen ID
   aus der Kandidatenmenge ausgeschlossen.
4. Geprueft, ob nach diesem Ausschluss mindestens ein anderer Endpoint fuer
   eine exakte 48-kHz-Formatpruefung verbleibt.
5. Wegen leerer Kandidatenmenge keine `IsFormatSupported`-Pruefung und keine
   Werkzeugerweiterung ausgefuehrt.

## Messergebnisse und Gegenbaselines

### Aktuelles natives Inventar

```text
aktive Capture-Endpoints gesamt:       1
geschlossene C920-Endpoints:            1
andere aktive Capture-Endpoints:        0
48-kHz-Kandidaten nach Ausschluss:       0
IsFormatSupported-Aufrufe fuer Kandidat: 0
initialisierte Streams:                  0
gestartete Streams:                      0
erfasste Pakete:                         0
```

Der einzige beobachtete Endpoint blieb:

```text
ID:          {0.0.1.00000000}.{544f2b37-f907-4a1f-b716-b967d9c058d3}
Name:        Mikrofon (HD Pro Webcam C920)
Datenfluss:  capture
Zustand:     DEVICE_STATE_ACTIVE
Mixsicht:    16000 Hz, 2 Kanaele, 32 Bit
```

Die DirectSound-Vergleichssicht fuer Geraet `5` blieb unveraendert bei
`Mikrofon (HD Pro Webcam C920)`, zwei Eingangskanaelen und 44.100 Hz
Default-Rate.

### Gegenbaselines

- **B0:** Lauf 120 inventarisierte ebenfalls genau diesen einen aktiven
  nativen Capture-Endpoint.
- **B1:** Lauf 121 belegt fuer diesen Endpoint den technischen Negativbefund
  des exakten 48-kHz-Mono-`float32`-Vertrags.
- **B2:** Lauf 122 schliesst den C920-Zweig fuer genau diesen Vertrag und
  verbietet eine Wiederholung mit geaenderten Parametern.

Eine positive andere Endpoint-Baseline existiert nicht.

## Beobachtetes Ergebnis

Es ist aktuell kein anderer aktiver nativer Capture-Endpoint vorhanden. Nach
dem verbindlichen Ausschluss der C920 bleibt keine Anschlussstelle, an der der
unveraenderte 48-kHz-Vertrag ohne Wiedereroeffnung des geschlossenen Zweigs
geprueft werden koennte.

## Technische Interpretation

Die fehlende Kandidatenmenge macht eine vollstaendige Formatmetadaten- oder
`IsFormatSupported`-Erweiterung in diesem Lauf unnoetig. Eine solche
Erweiterung ohne vorhandenen anderen Endpoint wuerde keine neue Beobachtung
ermoeglichen.

Der Befund bedeutet nicht, dass kein geeignetes Geraet existieren kann. Er
besagt nur, dass im aktuellen lokalen Inventar kein anderes aktives
Capture-Geraet bereitsteht.

## Grenzen und nicht gepruefte Annahmen

- Deaktivierte, getrennte oder spaeter angeschlossene Geraete wurden nicht als
  verfuegbare aktive Endpoints behandelt.
- Es wurde kein neues Geraet installiert, aktiviert oder angeschlossen.
- Die C920 wurde nicht erneut auf 48-kHz-Unterstuetzung geprueft.
- Kein anderer Endpoint konnte auf vollstaendige Formatmetadaten untersucht
  werden.
- Paketposition, Quellenstuetze, Organismuszeit und MCM-Feldzeit sind nicht
  nachgewiesen.
- Forschung 030 bleibt gesperrt.
- Memory, Organisation, Semantik und Topologie wurden nicht untersucht oder
  nachgewiesen.
- Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Lauf 123 findet keinen anderen aktiven Capture-Endpoint. Der native
Audioquellenzeit-Zweig ruht damit gemaess Lauf 122 als technische
Projektgrenze. Es erfolgt keine Erweiterung, kein weiterer Formatprobe und
keine Umgehung ueber die C920.

## Naechster begrenzter Forschungslauf

Aus jetziger Sicht sollte Lauf 124 den ruhenden Audioquellenzeit-Zweig nicht
synthetisch oder mit geaenderten C920-Parametern fortsetzen. Der naechste
Grundlagenlauf sollte den unabhaengigen physischen Feld-Welt-Feld-Zweig ordnen:

- vorhandene Effektor-, Kamera-, Rezeptor- und Feldschnittstellen im Workspace
  pruefen;
- eine getrennte passive Zielflaeche und die Sichttrennung zwischen Kamera und
  Effektor als konkreten Aufbauvertrag vorregistrieren;
- zunaechst nur Schnittstellen- und Aufbaupruefung, noch keine Feldwirkung,
  Memory- oder Organisationsauswertung.

Ein spaeter bereitgestelltes anderes 48-kHz-Capture-Geraet kann den nativen
Audiozweig erst nach neuer Inventarisierung und gesonderter Freigabe wieder
oeffnen.

## Tatsaechlich verwendete Quellen

- `docs/forschung/042_NATIVE_WASAPI_ENDPOINT_INVENTAR_LAUF_120.md`
- `docs/forschung/043_NATIVE_WASAPI_100_PAKET_PROBE_LAUF_121.md`
- `docs/forschung/044_ENTSCHEIDUNG_48_KHZ_C920_PFADSCHLIESSUNG_LAUF_122.md`
- `tools/run_native_wasapi_endpoint_inventory.py`
- lokale native Windows-MMDevice-/WASAPI-Inventarausgabe
- lokale `sounddevice`-Vergleichsmetadaten

MINI_DIO und externe MCM-Mechaniken wurden nicht verwendet.

