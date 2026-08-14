# Forschung 042: Native WASAPI-Endpoint-Inventarisierung (Lauf 120)

## Forschungsfrage und Auftrag

Kann das bisherige `sounddevice`-Eingabegeraet mit Index `5` anhand einer reinen
Metadateninventarisierung einem vollstaendigen nativen WASAPI-Capture-Endpoint
zugeordnet werden?

Freigegeben waren eine kleine isolierte Werkzeugergaenzung, synthetische Tests
und die Inventarisierung aktiver Capture-Endpoints. Nicht freigegeben waren
Streaminitialisierung, Streamstart, Paketerfassung sowie Rezeptor- oder
Feldruntime.

## Verwendete Dateien und Schnittstellen

- `docs/forschung/040_VORREGISTRIERUNG_NATIVE_WASAPI_CAPTURE_PROBE_LAUF_118.md`
- `tools/run_native_wasapi_capture_probe.py`
- `tools/run_native_wasapi_endpoint_inventory.py`
- `tests/test_native_wasapi_endpoint_inventory_tool.py`
- `IMMDeviceEnumerator::EnumAudioEndpoints`
- `IMMDeviceEnumerator::GetDefaultAudioEndpoint`
- `IMMDeviceCollection::GetCount` und `IMMDeviceCollection::Item`
- `IMMDevice::GetId`, `IMMDevice::GetState` und `IMMDevice::OpenPropertyStore`
- `IMMEndpoint::GetDataFlow`
- `IAudioClient::GetMixFormat` als passive Formatmetadatenabfrage
- `sounddevice.query_devices(5)` und `sounddevice.query_hostapis(...)`

## Durchgefuehrte Schritte

1. Ein separates Inventarwerkzeug fuer aktive native Capture-Endpoints erstellt.
2. Vollstaendige Endpoint-ID, Anzeigename, Datenfluss, Zustand, Defaultrollen und
   Mixformat-Metadaten erfasst.
3. Die unveraenderten lokalen `sounddevice`-Metadaten fuer Index `5` daneben
   ausgegeben.
4. Automatische oder unscharfe Auswahl, Default-Fallback und Mappingentscheidung
   im Werkzeug ausgeschlossen.
5. Synthetisch geprueft, dass das Ergebnis keine Stream-, Paket-, Quellenstuetzen-
   oder Feldhandlung behauptet.
6. Die native Metadateninventarisierung einmal lokal ausgefuehrt.

Der erste Aufruf brach vor der Endpoint-Enumeration mit
`RPC_E_CHANGED_MODE` ab, weil `sounddevice` den Hauptthread bereits in einem
anderen COM-Apartment initialisiert hatte. Die COM-Behandlung wurde daraufhin
eng begrenzt korrigiert: Ein vorhandenes Apartment wird weiterverwendet und nur
eine durch das Werkzeug selbst erfolgreiche COM-Initialisierung wird durch das
Werkzeug wieder beendet. Andere COM-Fehler bleiben harte Abbrueche.

## Messergebnisse und Gegenbaselines

### Native aktive Capture-Endpoints

Es wurde genau ein aktiver Capture-Endpoint beobachtet:

| Feld | Rohwert |
| --- | --- |
| Anzeigename | `Mikrofon (HD Pro Webcam C920)` |
| Endpoint-ID | `{0.0.1.00000000}.{544f2b37-f907-4a1f-b716-b967d9c058d3}` |
| Datenfluss | `capture` |
| Zustand | `1` (`DEVICE_STATE_ACTIVE`) |
| Defaultrollen | `console`, `multimedia`, `communications` |
| Mixformat-Kanaele | `2` |
| Mixformat-Rate | `16000 Hz` |
| Mixformat-Bittiefe | `32` |

### Vergleichsbaseline `sounddevice`-Index 5

| Feld | Rohwert |
| --- | --- |
| Name | `Mikrofon (HD Pro Webcam C920)` |
| Host-API | `Windows DirectSound` (Index `1`) |
| Eingangskanaele | `2` |
| Ausgangskanaele | `0` |
| Default-Rate | `44100 Hz` |
| niedrige Eingangslatenz | `0.12 s` |
| hohe Eingangslatenz | `0.24 s` |

### Technische Pruefungen

- Neue synthetische Inventartests: `4` bestanden.
- `py_compile`: bestanden.
- `git diff --check`: keine Whitespace-Fehler; nur bestehende LF/CRLF-Hinweise
  in anderen Arbeitsbaumdateien.
- Initialisierte Audiostreams: `0`.
- Gestartete Audiostreams: `0`.
- Erfasste Audiopakete: `0`.

Die bestehende PortAudio-/`sounddevice`-Sicht bleibt die Vergleichsbaseline. Sie
enthaelt keine vollstaendige native Endpoint-ID und keine native Paketposition.

## Beobachtetes Ergebnis

Im aktuellen lokalen Zustand gibt es nur einen aktiven nativen Capture-Endpoint.
Sein Anzeigename stimmt exakt mit dem Namen von `sounddevice`-Index `5` ueberein;
beide Sichten melden zwei Eingangskanaele. Dadurch ist die oben genannte native
Endpoint-ID unter dem aktuellen Inventar der einzige Zuordnungskandidat fuer
Geraet `5`.

Die Formatmetadaten stimmen nicht ueberein: Der native Shared-Mode-Mix meldet
`16000 Hz`, waehrend die DirectSound-Sicht `44100 Hz` als Default-Rate meldet.

## Technische Interpretation

Die lokale Kandidatenzuordnung ist durch Einzigkeit, exakte Namensgleichheit und
gleiche Eingangskanalzahl eindeutig. Sie ist dennoch kein API-seitiger
Identitaetsnachweis zwischen einem DirectSound-Index und einer WASAPI-ID, weil
der vorhandene `sounddevice`-Datensatz keinen gemeinsamen stabilen
Identifikator exponiert.

Die Mixformat-Differenz ist kein Beweis gegen 48-kHz-Unterstuetzung. Das native
Mixformat beschreibt das aktuelle Shared-Mode-Mixformat; die Unterstuetzung des
vorregistrierten festen 48-kHz-Mono-`float32`-Formats wurde in diesem Lauf
absichtlich nicht mit `IsFormatSupported` oder `Initialize` geprueft.

## Grenzen und nicht gepruefte Annahmen

- Kein Stream wurde initialisiert oder gestartet.
- Keine Paketgroesse, Device-Position, QPC-Position oder Statusflagfolge wurde
  erfasst.
- Die 48-kHz-Unterstuetzung des Endpoint-Kandidaten ist ungeprueft.
- Die Zuordnung gilt fuer das beobachtete aktuelle Inventar; ein geaenderter
  Geraetebestand erfordert eine neue Inventarisierung.
- Die gemeinsame physische Identitaet hinter DirectSound-Index und WASAPI-ID ist
  mangels gemeinsamem API-Identifier nicht formal bewiesen.
- Eine native Paketposition waere selbst bei spaeterer Beobachtung nur ein
  technischer Kandidat, keine Quellenstuetze, Organismuszeit oder MCM-Feldzeit.
- Forschung 030 bleibt gesperrt.
- Memory, Organisation, Semantik und Topologie wurden nicht untersucht oder
  nachgewiesen.
- Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Lauf 120 ermittelt fuer `sounddevice`-Geraet `5` genau einen aktuellen nativen
WASAPI-Zuordnungskandidaten:
`{0.0.1.00000000}.{544f2b37-f907-4a1f-b716-b967d9c058d3}`.

Die Zuordnung ist lokal eindeutig, bleibt aber wegen der getrennten Host-APIs
methodisch eine Metadatenzuordnung. Sie rechtfertigt weder eine Aussage zur
48-kHz-Faehigkeit noch zu Paketkontinuitaet oder MCM-Feldzeit.

## Naechster begrenzter Forschungslauf

Lauf 121 sollte den bereits implementierten nativen Probe einmal auf exakt dieser
Endpoint-ID ausfuehren, sofern der Forschungspruefer den realen Hardwarelauf
gesondert freigibt. Der Lauf bleibt auf das vorregistrierte feste Format,
hoechstens 100 nichtleere Pakete oder 10 Sekunden und die rohen Paketfelder
begrenzt. Formatablehnung, Fehlerflags, Positionsluecke, Ruecksprung oder Bedarf
an Ersatzzeit fuehren zum harten Abbruch. Eine positive Entscheidung darf nur
`PAKETPOSITION_KANDIDAT` lauten.

## Tatsaechlich verwendete Quellen

- `docs/forschung/040_VORREGISTRIERUNG_NATIVE_WASAPI_CAPTURE_PROBE_LAUF_118.md`
- `tools/run_native_wasapi_capture_probe.py`
- lokales `sounddevice`-Inventar fuer Index `5`
- lokale native Windows-MMDevice-/WASAPI-Metadaten

