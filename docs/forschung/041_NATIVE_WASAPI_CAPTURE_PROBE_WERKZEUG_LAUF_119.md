# Forschung 041: Natives WASAPI-Capture-Probe-Werkzeug

## Lauf und Status

```text
Workflow-Lauf:                    119
Dokumentart:                      technischer Implementierungsbefund
Native Werkzeugerweiterung:       implementiert
Synthetische Vertragspruefung:    bestanden
Hardwarelauf:                     nicht ausgefuehrt
Rezeptor- oder Feldanbindung:     nicht vorhanden
Quellenstuetze nachgewiesen:      nein
```

## Forschungsfrage und Auftrag

Kann der in Forschung 040 vorregistrierte Rohwertvertrag als isoliertes
Windows-Werkzeug umgesetzt und ohne Hardwarezugriff gegen synthetische
Paketfolgen geprueft werden?

Freigegeben waren genau ein Tool unter `tools/` und fokussierte Tests unter
`tests/`. Ein realer Endpoint durfte nicht geoeffnet werden.

## Implementierte Grenze

`tools/run_native_wasapi_capture_probe.py` besitzt nur einen variablen
Pflichtparameter:

```text
--endpoint-id VOLLSTAENDIGE_NATIVE_WASAPI_ENDPOINT_ID
```

Rate, Kanalzahl, Sampleformat, Share-Mode, Paketlimit und Timeout sind nicht
ueber die Kommandozeile veraenderbar:

```text
48000 Hz
1 Kanal
IEEE float32
Shared Mode
kein Loopback
keine Formatkonversion
100 nichtleere Pakete
10 Sekunden
```

Die native Schicht verwendet direkt Windows COM und WASAPI ueber Python
`ctypes`. Es wurde keine neue Paket- oder COM-Abhaengigkeit installiert.

## Native Schnittstellen

Das Werkzeug verwendet ausschliesslich technische Windows-Schnittstellen:

- `IMMDeviceEnumerator::GetDevice` mit der expliziten Endpoint-ID;
- `IMMDevice::GetId` zur exakten Rueckpruefung derselben ID;
- `IMMEndpoint::GetDataFlow` und `IMMDevice::GetState`;
- `IPropertyStore::GetValue(PKEY_Device_FriendlyName)`;
- `IAudioClient::IsFormatSupported` und `IAudioClient::Initialize`;
- `IAudioClient::GetService`, `Start` und `Stop`;
- `IAudioCaptureClient::GetNextPacketSize`, `GetBuffer` und `ReleaseBuffer`.

Audiodaten werden nicht kopiert, gespeichert oder ausgewertet. Ausgegeben
werden nur Endpoint-Metadaten, festes Format, Rohpaketfelder, HRESULTs,
Entscheidung und Abbruchgrund.

## Synthetisch gepruefter Vertrag

`tests/test_native_wasapi_capture_probe_tool.py` prueft ohne Hardware:

- exakte lueckenlose Device-Position;
- Ablehnung jeder Positionsluecke ohne Toleranz;
- strikt monotone QPC-Position;
- Abbruch bei `DATA_DISCONTINUITY` und `TIMESTAMP_ERROR`;
- unveraenderte Zulassung des `SILENT`-Flags;
- Abbruch bei null Frames und fehlerhaftem `ReleaseBuffer`-HRESULT;
- festes Paketlimit und sicheres Schliessen des Backends;
- Erhalt bereits erfasster Rohpakete bei einem spaeteren Abbruch;
- passive JSON-Metadaten ohne Quellenstuetzen- oder Feldabbildung;
- verpflichtende explizite Endpoint-ID;
- nicht veraenderbare vorregistrierte Laufkonfiguration.

## Messergebnisse und Gegenbaselines

```text
Neue synthetische Tests:          11 bestanden
Unterpruefungen der Fehlerflags:   2 bestanden
Python-Kompilierung:              bestanden
CLI-Hilfe ohne Hardwarezugriff:   bestanden
git diff --check:                 bestanden
Reale Pakete erfasst:             0
Realer Endpoint geoeffnet:        nein
```

- **B0, PortAudio-/sounddevice-Audit:** bleibt unveraendert und besitzt keine
  native Paketposition.
- **B1, synthetische Schemakontrolle:** ist jetzt implementiert und prueft nur
  die Ablehnungs- und Rohwerterhaltungslogik.
- **B2, nativer Rohprobe:** ist technisch implementiert, aber nicht
  ausgefuehrt und daher ohne Messbefund.

B1 ist keine reale positive Quellenbaseline. Die Existenz des nativen Codes
beweist nicht, dass ein lokaler C920-Endpoint das feste Format oder eine
kontinuierliche Paketposition liefert.

## Beobachtetes Ergebnis

Die Vertragslogik ist getrennt von der nativen COM-Schicht importierbar und
mit synthetischen Backends pruefbar. Fehlerflags, Positionsluecken,
nichtmonotone Folgen, fehlerhafte HRESULTs und unvollstaendige Laeufe werden
ohne Glattung oder Toleranz abgelehnt. Ein Abbruch behaelt die bis dahin
erfassten Rohpakete in der technischen Fehlerausgabe.

## Technische Interpretation

Die vorhandene PortAudio-Mechanik musste nicht veraendert werden. Die neue
Schicht ist ein isolierter Diagnosepfad fuer Felder, die PortAudio und
`sounddevice` nicht exponieren. Sie ist weder Audioadapter noch Rezeptor und
besitzt keine Verbindung zur Feldruntime.

Die synthetischen Tests belegen nur die Umsetzung des vorregistrierten
Vertrags. Sie belegen weder die Korrektheit des lokalen Treibers noch die
Kontinuitaet einer realen WASAPI-Paketposition.

## Grenzen und nicht gepruefte Annahmen

- Die native COM-Schicht wurde nicht gegen einen realen Endpoint ausgefuehrt.
- Die Zuordnung des bisherigen `sounddevice`-Geraets `5` zu einer nativen
  Endpoint-ID fehlt weiterhin.
- 48-kHz-Mono-`float32`-Unterstuetzung der C920 ist ungeprueft.
- Reset-, Treiber- und Langzeitverhalten sind ungeprueft.
- Eine Paketposition ist noch keine Quellenstuetze oder Organismuszeit.
- Forschung 030 bleibt gesperrt.
- Memory, Organisation, Semantik und Topologie wurden nicht untersucht.

## Konkrete Schlussfolgerung

Lauf 119 stellt die minimale technische Anschlussstelle und die synthetische
Negativbaseline bereit. Ein positiver realer Paketpositionskandidat liegt
nicht vor. Die Implementierung programmiert kein Messergebnis vor und nimmt
keine Zeitreparatur oder Felddeutung vor.

## Naechster begrenzter Forschungslauf

Vor einem Capture-Lauf sollte ein separater Lauf ausschliesslich die native
Endpoint-Inventarisierung und eindeutige Zuordnung zum bisherigen Audiogeraet
`5` pruefen. Dieser Inventarlauf darf keinen Stream initialisieren und keine
Pakete erfassen. Erst nach eindeutiger, prueferbestaetigter Endpoint-ID darf
ein eigener realer 100-Paket-Lauf freigegeben werden.

## Tatsaechlich verwendete Quellen

- Prueferfreigabe zu Lauf 119;
- `docs/forschung/040_VORREGISTRIERUNG_NATIVE_WASAPI_CAPTURE_PROBE_LAUF_118.md`;
- `docs/architektur/031_FELDZEITUEBERGABE.md`;
- `docs/architektur/036_BEOBACHTUNGSGRENZE_STATT_FELDTAKT.md`;
- `mcm_field_organism/adapter_timing_capability.py`;
- `tools/run_live_adapter_timing_capability_audit.py`;
- Microsoft, `IAudioCaptureClient::GetBuffer`:
  <https://learn.microsoft.com/en-us/windows/win32/api/audioclient/nf-audioclient-iaudiocaptureclient-getbuffer>;
- Microsoft, `IAudioClient::Initialize`:
  <https://learn.microsoft.com/en-us/windows/win32/api/audioclient/nf-audioclient-iaudioclient-initialize>;
- Microsoft, `IAudioCaptureClient::ReleaseBuffer`:
  <https://learn.microsoft.com/en-us/windows/win32/api/audioclient/nf-audioclient-iaudiocaptureclient-releasebuffer>.

MINI_DIO- und externe MCM-Mechanikquellen wurden nicht verwendet.
