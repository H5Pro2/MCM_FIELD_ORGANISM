# Forschung 043: Nativer WASAPI-100-Paket-Probe (Lauf 121)

## Forschungsfrage und Auftrag

Liefert der in Lauf 120 lokal eindeutig zugeordnete native Capture-Endpoint
bei exakt 48.000 Hz, Mono, IEEE `float32` und Shared Mode innerhalb von
hoechstens 100 nichtleeren Paketen oder 10 Sekunden eine rohe, lueckenlose
Folge aus Paketgroesse, Device-Position, QPC-Position und Statusflags?

Freigegeben war genau ein realer Lauf mit der festen Endpoint-ID
`{0.0.1.00000000}.{544f2b37-f907-4a1f-b716-b967d9c058d3}`. Wiederholungen,
Parameterwechsel, Formatkonversion, Ratensuche, Ersatzzeit sowie Rezeptor- oder
Feldanbindung waren ausgeschlossen.

## Verwendete Dateien und Schnittstellen

- `docs/forschung/040_VORREGISTRIERUNG_NATIVE_WASAPI_CAPTURE_PROBE_LAUF_118.md`
- `docs/forschung/042_NATIVE_WASAPI_ENDPOINT_INVENTAR_LAUF_120.md`
- `tools/run_native_wasapi_capture_probe.py`
- `IMMDeviceEnumerator::GetDevice`
- `IMMDevice::GetId`, `IMMDevice::GetState` und `IMMDevice::Activate`
- `IMMEndpoint::GetDataFlow`
- `IAudioClient::IsFormatSupported`

`IAudioClient::Initialize`, `IAudioClient::Start` und
`IAudioCaptureClient::GetBuffer` wurden wegen des vorangehenden harten
Formatabbruchs nicht erreicht.

## Durchgefuehrte Schritte

1. Vorregistrierung, feste Konstanten und Abbruchlogik des vorhandenen Tools
   vor dem Hardwareaufruf kontrolliert.
2. Das Werkzeug genau einmal mit der freigegebenen vollstaendigen Endpoint-ID
   aufgerufen.
3. Endpoint-ID, Anzeigename, Capture-Datenfluss und aktiven Zustand bestaetigt.
4. Das exakt vorregistrierte Format mit `IsFormatSupported` abgefragt.
5. Nach der Formatverweigerung ohne Wiederholung und ohne Alternativformat
   beendet.

Das bestehende Werkzeug schreibt im JSON statisch `run_number: 119`, weil es
in Lauf 119 implementiert wurde. Der tatsaechlich freigegebene und hier
dokumentierte Hardwareversuch ist Lauf 121. Dieses Metadatenproblem wurde vor
dem einmaligen Lauf nicht durch eine Codeaenderung beeinflusst und ist kein
Messwert.

## Messergebnisse und Gegenbaselines

### B2: realer nativer Probe

```text
Entscheidung:                 TECHNISCH_NEGATIV
Endgrund:                     exact 48-kHz mono float32 shared format is unsupported
Endpoint-ID:                  {0.0.1.00000000}.{544f2b37-f907-4a1f-b716-b967d9c058d3}
Anzeigename:                  Mikrofon (HD Pro Webcam C920)
Datenfluss:                   capture
Geraetezustand:               1 (DEVICE_STATE_ACTIVE)
Angeforderte Rate:            48000 Hz
Angeforderte Kanaele:         1
Angefordertes Sampleformat:   float32
Share Mode:                   shared
Formatkonversion:             nein
Erfasste Pakete:              0
Audiodaten gespeichert:       nein
Quellenstuetze abgebildet:    nein
Feldfortschritt ausgefuehrt:  nein
```

Die Paketgrenze von 100 und die Zeitgrenze von 10 Sekunden wurden nicht
erreicht, weil der harte Formatabbruch vor der Streaminitialisierung eintrat.

### Gegenbaselines

- **B0:** Der bestehende PortAudio-/`sounddevice`-Audit exponiert weiterhin
  keine native Paketposition oder paketbezogene QPC-Position.
- **B1:** Die synthetischen Vertragspruefungen belegen nur die strikte
  Ablehnung fehlerhafter Paketfolgen; sie sind kein Hardwarebefund.
- **B2:** Der reale Probe ist fuer diesen Endpoint und dieses feste Format
  technisch negativ.

Es existiert keine reale positive Paketbaseline, weil kein Paket gelesen wurde.

## Beobachtetes Ergebnis

Der Endpoint war unter seiner exakten ID erreichbar, aktiv und als
Capture-Endpoint bestaetigt. `IAudioClient::IsFormatSupported` bestaetigte das
vorregistrierte 48-kHz-Mono-`float32`-Format im Shared Mode nicht. Der Lauf
endete deshalb vertragsgemaess vor Streaminitialisierung und Paketerfassung.

## Technische Interpretation

Der native 48-kHz-Paketpositionspfad ist fuer diesen Endpoint unter dem exakt
vorregistrierten Format nicht ausfuehrbar. Der Befund betrifft nur diese
Kombination aus Endpoint, Rate, Kanalzahl, Sampleformat und Share Mode.

Aus dem Formatabbruch folgt weder, dass WASAPI allgemein keine nativen
Paketpositionen liefert, noch dass der Endpoint unter anderen Formaten keine
Audiodaten erfassen koennte. Solche Alternativen waren nicht Bestandteil des
Laufs und wurden nicht getestet.

## Grenzen und nicht gepruefte Annahmen

- `Initialize`, `Start`, `GetBuffer` und `ReleaseBuffer` wurden nicht erreicht.
- Paketgroesse, Device-Position, QPC-Position und Statusflags wurden nicht
  beobachtet.
- Es wurde kein vorgeschlagenes Alternativformat uebernommen oder untersucht.
- Es gab keine Wiederholung mit anderer Rate, Kanalzahl oder anderem Format.
- Der Befund ist kein Nachweis allgemeiner WASAPI-Unfaehigkeit.
- Eine Paketposition, Quellenstuetze, Organismuszeit oder MCM-Feldzeit ist
  nicht nachgewiesen.
- Forschung 030 bleibt gesperrt.
- Memory, Organisation, Semantik und Topologie wurden nicht untersucht oder
  nachgewiesen.
- Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Lauf 121 endet gemaess Vorregistrierung mit `TECHNISCH_NEGATIV`. Der lokal
zugeordnete C920-Capture-Endpoint unterstuetzt das geforderte feste
48-kHz-Mono-`float32`-Format im Shared Mode nicht in der fuer den Probe
verlangten exakten Form. Es liegt kein `PAKETPOSITION_KANDIDAT` vor.

Die klare Stopplinie greift: Es wird keine Ersatzzeit berechnet, kein anderes
Format nachtraeglich gewaehlt und keine Quellenstuetzen- oder Feldfunktion
behauptet.

## Naechster begrenzter Forschungslauf

Aus jetziger Sicht sollte Lauf 122 keine Wiederholung dieses Hardwareprobes und
keine nachtraegliche Ratensuche sein. Sinnvoll ist eine reine technische
Entscheidungsvorregistrierung fuer den Audiozweig:

- entweder den 48-kHz-Vertrag als unveraenderliche Projektanforderung
  bestaetigen und den aktuellen C920-Pfad als technische Grenze schliessen;
- oder, nur nach neuer methodischer Begruendung, einen getrennten Probe fuer
  ein vorab festgelegtes nativ unterstuetztes Format spezifizieren.

Der Lauf sollte zunaechst nur Architektur-, Quellen- und Schnittstellenpruefung
sein. Keine Hardwareausfuehrung, kein Alternativformat und keine Feldanbindung
darf ohne erneute Vorregistrierung erfolgen.

## Tatsaechlich verwendete Quellen

- `docs/forschung/040_VORREGISTRIERUNG_NATIVE_WASAPI_CAPTURE_PROBE_LAUF_118.md`
- `docs/forschung/042_NATIVE_WASAPI_ENDPOINT_INVENTAR_LAUF_120.md`
- `tools/run_native_wasapi_capture_probe.py`
- lokale native Windows-MMDevice-/WASAPI-Ausgabe des einmaligen Laufs

