# Lauf 158 - Reale Audioanschluss-Abnahme

## Forschungsfrage und Auftrag

Ist ein ausdruecklich bereitgestellter aktiver Capture-Endpoint vorhanden,
der den unveraenderten technischen Vertrag von 48 kHz, Mono und `float32`
erfuellt und danach in einem kurzen Audio-Callback-Lauf ohne Kamera
kontinuierlich Frames liefert?

Freigegeben sind ausschliesslich Audio-Inventarisierung, Formatpruefung und,
bei positivem Formatbefund, Callback-Kontinuitaet. Kamera, Rezeptor-Feld-
Advance, Memory und physische Weltwirkung sind ausgeschlossen.

## Verwendete Quellen

- aktueller Benutzerfreigabe und Freigabe fuer Lauf 158
- `docs/forschung/044_ENTSCHEIDUNG_48_KHZ_C920_PFADSCHLIESSUNG_LAUF_122.md`
- `docs/forschung/045_ANDERE_48_KHZ_CAPTURE_ENDPOINTS_LAUF_123.md`
- `docs/forschung/057_REALE_KAMERA_MIKROFON_STABILITAET_LAUF_157.md`
- `tools/run_native_wasapi_endpoint_inventory.py`
- `tools/run_native_wasapi_capture_probe.py`
- `tools/run_live_adapter_timing_capability_audit.py`
- `mcm_field_organism/live_audio_adapter.py`
- `mcm_field_organism/adapter_timing_capability.py`

Externe Webquellen und MINI_DIO wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Ausgefuehrt wurde die vorhandene passive native MMDevice-/WASAPI-
Inventarisierung. Sie liest Endpointidentitaet, Zustand und Mixformat, ohne
einen Stream zu initialisieren oder Pakete zu erfassen.

Die Capture-Probe und der Callback-Audit wurden als nachgelagerte
Schnittstellen geprueft, aber mangels eines freigegebenen Kandidaten nicht
aufgerufen.

## Durchgefuehrte Schritte

1. Das aktuelle native Inventar der aktiven Capture-Endpoints neu gelesen.
2. Den einzigen Endpoint ueber seine vollstaendige Endpoint-ID mit dem in
   Lauf 122 geschlossenen C920-Zweig abgeglichen.
3. Geprueft, ob nach diesem Ausschluss ein ausdruecklich bereitgestellter
   aktiver 48-kHz-Kandidat verbleibt.
4. Wegen leerer Kandidatenmenge keine automatische Geraetewahl, keine
   `IAudioClient::Initialize`-Operation, keinen Streamstart, keine
   Paketerfassung und keinen Callback-Lauf ausgefuehrt.
5. Die zugehoerigen Werkzeug- und Vertrags-Tests lokal reproduziert.

## Messergebnisse und Gegenbaselines

### Aktuelles natives Inventar

```text
aktive native Capture-Endpoints:        1
geschlossene C920-Endpoints:             1
andere aktive Capture-Endpoints:         0
freigegebene 48-kHz-Kandidaten:          0
AudioClient-Initialisierungen:           0
gestartete Streams:                      0
erfasste Pakete:                         0
Callback-Kontinuitaetslaeufe:            0
Feld-Advances:                           0
```

Der einzige aktive native Endpoint lautet weiterhin:

```text
ID:          {0.0.1.00000000}.{544f2b37-f907-4a1f-b716-b967d9c058d3}
Name:        Mikrofon (HD Pro Webcam C920)
Zustand:     DEVICE_STATE_ACTIVE
Mixformat:   16000 Hz, 2 Kanaele, 32 Bit
Standard:    console, multimedia, communications
```

Die lokale SoundDevice-Vergleichssicht zeigt denselben C920-Namen als
DirectSound-Geraet `5` mit 44.100 Hz Standardrate. Diese Sicht ist kein neuer
physischer Endpoint und ersetzt keine positive native 48-kHz-Abnahme.

### Gegenbaselines

- Lauf 122 schliesst genau diesen C920-Audioquellenzeitpfad fuer den festen
  48-kHz-Vertrag.
- Lauf 123 fand nach Ausschluss der C920 ebenfalls keinen anderen aktiven
  Endpoint.
- Lauf 157 zeigte, dass formal akzeptierte PortAudio-Geraeteansichten `11`
  und `12` keine kontinuierlichen Callback-Folgen lieferten. Sie erscheinen
  auch jetzt nicht als eigenstaendige aktive native MMDevice-Endpoints.

## Beobachtetes Ergebnis

Es wurde kein neuer oder ausdruecklich bereitgestellter aktiver
48-kHz-Capture-Endpoint gefunden. Nach dem verbindlichen Ausschluss des
C920-Zweigs ist die Kandidatenmenge leer.

## Technische Interpretation

Ohne einen real vorhandenen Kandidaten kann weder ein exakter Formatbefund
noch eine Callback-Kontinuitaet gemessen werden. Eine Wiederholung am C920,
eine automatische PortAudio-Auswahl oder eine Umgehung ueber Geraeteansichten
waere keine Abnahme des freigegebenen Auftrags.

## Hypothese und offene Frage

Ein spaeter physisch angeschlossener und aktiver Endpoint koennte den
48-kHz-Vertrag erfuellen. Offen bleibt seine konkrete Identitaet, sein natives
Format und seine Laufzeitkontinuitaet. Dazu liegt in Lauf 158 kein Messwert
vor.

## Grenzen und nicht gepruefte Annahmen

- Es wurde kein neues Geraet angeschlossen, aktiviert oder installiert.
- Der C920-Audiozweig wurde nicht wiedereroeffnet.
- `IsFormatSupported`, Streaminitialisierung, Paketpositionen, Callbackzeiten
  und Aussetzer konnten an keinem neuen Kandidaten gemessen werden.
- Kamera, Rezeptoren, Docks und MCM-Feld wurden nicht verwendet.
- Es wurden keine Rohdaten oder Medien gespeichert.
- Memory, Organisation, Semantik, Topologie und Feld-Welt-Feld-Kausalitaet
  wurden nicht untersucht.

## Konkrete Schlussfolgerung

Lauf 158 endet an einer realen Anschlussgrenze: Es steht kein freigegebener
aktiver Capture-Endpoint fuer die 48-kHz-Audioabnahme bereit. Deshalb gibt es
weder einen positiven Formatbefund noch einen Callback-Kontinuitaetsbefund.
Die bestehende Runtime benoetigt keine Codeaenderung. Eine Zielabweichung ist
nicht erkennbar.

## Naechster begrenzter Forschungslauf

Der Audiozweig darf erst nach einer aeusseren Zustandsaenderung fortgesetzt
werden: Ein anderer physischer Capture-Endpoint muss angeschlossen, aktiviert
und vom Benutzer eindeutig benannt sein. Der dann folgende Lauf 159 sollte
zunaechst nur das neue native Inventar mit Endpoint-ID und Mixformat gegen das
vorherige Inventar vergleichen. Nur bei einem tatsaechlich neuen aktiven
Endpoint folgen exakte 48-kHz-Formatpruefung und ein kurzer Audio-only-
Callbacklauf. Bis dahin sollte kein weiterer Audio-Wiederholungslauf erfolgen;
Kamera, Feldadvance und physischer Feld-Welt-Feld-Aufbau bleiben getrennt.
