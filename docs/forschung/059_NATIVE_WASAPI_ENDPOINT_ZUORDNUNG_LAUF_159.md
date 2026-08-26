# Forschung 059: Native WASAPI-Endpoint-Zuordnung (Lauf 159)

## Forschungsfrage und Auftrag

Welcher vollstaendige native WASAPI-Endpoint ist dem bisherigen lokalen
`sounddevice`-Eingabegeraet mit Index `5` im aktuellen aktiven Inventar
zuzuordnen, und ist diese Zuordnung eindeutig?

Freigegeben waren nur passive native Endpoint-Inventarisierung, eine explizite
Metadaten-Zuordnungspruefung und synthetische Vertragstests. Streamstart,
Paketerfassung, Hardware-Capture, Audioadapter, Rezeptorpfad und Feldruntime
waren ausgeschlossen.

## Ermittlung und Begruendung der Laufnummer

Der uebergebene bekannte Stand `119` wurde nicht uebernommen. Die Dateiliste
unter `docs/forschung/` reicht bis
`058_REALE_AUDIOANSCHLUSS_ABNAHME_LAUF_158.md`. Diese Datei bezeichnet Lauf
158 ausdruecklich als letzten ausgefuehrten Lauf und nennt Lauf 159 als
moeglichen Folgelauf. Eine vorhandene Lauf-159-Forschungsdatei gab es vor
diesem Lauf nicht. Daher ist die naechste Laufnummer `159`; die fortlaufende
Forschungsdateinummer ist `059`.

Zur Laufstandsermittlung wurden verwendet:

- Dateiliste `docs/forschung/`
- `docs/forschung/041_NATIVE_WASAPI_CAPTURE_PROBE_WERKZEUG_LAUF_119.md`
- `docs/forschung/042_NATIVE_WASAPI_ENDPOINT_INVENTAR_LAUF_120.md`
- `docs/forschung/058_REALE_AUDIOANSCHLUSS_ABNAHME_LAUF_158.md`

## Verwendete Quellen

- aktueller Arbeitsauftrag des CEO
- die drei oben genannten lokalen Forschungsdokumente
- lokales natives Windows-MMDevice-/WASAPI-Inventar
- lokales `sounddevice`-Inventar fuer Index `5`

Externe Webquellen, Browsermedien und MINI_DIO wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

- `tools/run_native_wasapi_endpoint_inventory.py`
- `tools/run_native_wasapi_capture_probe.py` nur fuer bestehende COM-Typen und
  Konstanten; keine Capture-Probe wurde ausgefuehrt
- `tests/test_native_wasapi_endpoint_inventory_tool.py`
- `IMMDeviceEnumerator::EnumAudioEndpoints`
- `IMMDeviceEnumerator::GetDefaultAudioEndpoint`
- `IMMDevice::GetId`, `IMMDevice::GetState` und
  `IMMDevice::OpenPropertyStore`
- `IMMEndpoint::GetDataFlow`
- `IAudioClient::GetMixFormat` als passive Metadatenabfrage
- `sounddevice.query_devices(5)` und `sounddevice.query_hostapis(...)`

## Durchgefuehrte Schritte

1. Den Forschungsdateibestand und den Arbeitsbaum rein lesend geprueft.
2. Die historische Lauf-120-Inventarisierung und den aktuellen Lauf-158-Befund
   verglichen.
3. Das bestehende Inventarwerkzeug um optionale Parameter fuer Laufnummer und
   explizite Zuordnungspruefung ergaenzt; das Standardverhalten von Lauf 120
   bleibt erhalten.
4. Die Zuordnungslogik auf exakte Anzeigenamensgleichheit, gleiche
   Eingangskanalzahl und genau einen Treffer begrenzt.
5. Synthetische Tests fuer eindeutigen und mehrdeutigen Treffer ergaenzt.
6. Den passiven Modus mit `--run-number 159 --review-mapping` einmal lokal
   ausgefuehrt.

## Messergebnisse und Gegenbaselines

### Aktive native Capture-Endpoints

Es wurde genau ein aktiver nativer Capture-Endpoint beobachtet:

| Feld | Rohwert |
| --- | --- |
| Endpoint-ID | `{0.0.1.00000000}.{544f2b37-f907-4a1f-b716-b967d9c058d3}` |
| Anzeigename | `Mikrofon (HD Pro Webcam C920)` |
| Datenfluss | `capture` |
| Zustand | `1` (`DEVICE_STATE_ACTIVE`) |
| Rollen | `console`, `multimedia`, `communications` |
| Mixformat-Kanaele | `2` |
| Mixformat-Rate | `16000 Hz` |
| Mixformat-Bittiefe | `32` |

### Unveraenderte `sounddevice`-Vergleichsmetadaten

| Feld | Rohwert |
| --- | --- |
| Index | `5` |
| Name | `Mikrofon (HD Pro Webcam C920)` |
| Host-API | `Windows DirectSound` (Index `1`) |
| Eingangskanaele | `2` |
| Ausgangskanaele | `0` |
| Default-Rate | `44100 Hz` |
| niedrige Eingangslatenz | `0.12 s` |
| hohe Eingangslatenz | `0.24 s` |

### Zuordnungspruefung und Gegenbaseline

- Exakte Namens- und Kanalzahl-Treffer: `1`.
- Entscheidung: `LOCALLY_UNIQUE_METADATA_MATCH_NOT_API_IDENTITY`.
- Zugeordnete Endpoint-ID:
  `{0.0.1.00000000}.{544f2b37-f907-4a1f-b716-b967d9c058d3}`.
- Synthetische Mehrdeutigkeitsbaseline mit zwei gleich passenden Endpoints:
  `NOT_UNIQUELY_MAPPABLE`, keine zugeordnete ID.
- Synthetische Tests: `6` bestanden.
- `py_compile`: bestanden.
- AudioClient-Initialisierungen: `0`.
- Gestartete Streams: `0`.
- Erfasste Pakete: `0`.
- Feld-Advances: `0`.

## Beobachtetes Ergebnis

Im aktuellen aktiven Inventar ist die native Endpoint-ID der C920 durch exakt
gleichen Anzeigenamen, gleiche Eingangskanalzahl und die Einzigkeit des
Treffers lokal eindeutig dem `sounddevice`-Geraet `5` zuordenbar.

## Technische Interpretation

Die Zuordnung ist eine kontrollierte Metadatenzuordnung. Sie ist kein
API-seitiger Identitaetsnachweis, weil die DirectSound-Sicht von `sounddevice`
keine native WASAPI-Endpoint-ID oder einen anderen gemeinsamen stabilen
Identifier bereitstellt. Rollen oder Defaultstatus wurden nicht als
Auswahlregel verwendet.

## Grenzen und nicht gepruefte Annahmen

- Die Zuordnung gilt nur fuer das aktuell beobachtete Inventar.
- Die physische Identitaet ist mangels gemeinsamem API-Identifier nicht formal
  bewiesen.
- Das native Mixformat `16000 Hz`, zwei Kanaele und 32 Bit erfuellt den festen
  Vertrag `48 kHz`, Mono und `float32` nicht.
- Es erfolgte keine automatische Auswahl und kein Default-Fallback.
- Kein Stream wurde initialisiert oder gestartet; Pakete und Callbackzeiten
  wurden nicht gemessen.
- Audioadapter, Rezeptorpfad, Kamera und Feldruntime wurden nicht geaendert oder
  ausgefuehrt.
- Browserwiedergabe, Downloads, lokale Medien und Installationen waren nicht
  Gegenstand des Laufs.
- Quellenstuetze, Organismuszeit, MCM-Feldzeit, Memory, Feldorganisation,
  Semantik und Topologie wurden nicht untersucht oder nachgewiesen.
- Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Lauf 159 ordnet `sounddevice`-Geraet `5` lokal eindeutig der nativen WASAPI-ID
`{0.0.1.00000000}.{544f2b37-f907-4a1f-b716-b967d9c058d3}` zu. Die Aussage ist
auf den aktuellen, einzigen Metadatentreffer begrenzt und kein formaler
API-Identitaetsnachweis. Der bekannte C920-Endpoint bleibt fuer den festen
48-kHz-Mono-`float32`-Vertrag ungeeignet; daraus folgt kein Capture-Lauf.

## Naechster begrenzter Forschungslauf

Der Audiozweig sollte erst nach einer bestaetigten aeusseren Zustandsaenderung
fortgesetzt werden: Ein neuer aktiver physischer Capture-Endpoint muss eindeutig
benannt sein. Dann darf Lauf 160 ausschliesslich das native Inventar gegen Lauf
159 vergleichen und die Endpoint-ID, den Aktivzustand sowie das Mixformat des
neuen Kandidaten erfassen. Nur bei vollstaendig positivem Formatbefund waere
danach ein gesondert freizugebender kurzer Audio-only-Callbacklauf sachlich
begruendet. Bis dahin sind keine weitere Inventarwiederholung und keine
Runtimeaenderung angezeigt.
