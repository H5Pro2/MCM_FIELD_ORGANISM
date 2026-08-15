# Lauf 157 - Reale Kamera-Mikrofon-Stabilitaet

## Forschungsfrage und Auftrag

Kann die vorhandene reale Kamera- und Mikrofonaufnahme ueber einen laengeren,
gemeinsamen Lauf technisch stabil betrieben und hinsichtlich
Zeitkontinuitaet, Aussetzern, Dock-Herkunft, nativen Raten, Synchronisierung
und unverfaelschter Uebergabe vermessen werden?

Der Auftrag ist auf Sensor-, Rezeptor- und Timingtechnik begrenzt. Feldadvance,
Memory, Bedeutung, Zielzustand, Reward und physische Feld-Welt-Feld-Wirkung
sind nicht Bestandteil.

## Verwendete Quellen

- aktueller Benutzerfreigabe und Freigabe fuer Lauf 157
- `docs/forschung/044_ENTSCHEIDUNG_48_KHZ_C920_PFADSCHLIESSUNG_LAUF_122.md`
- `docs/forschung/045_ANDERE_48_KHZ_CAPTURE_ENDPOINTS_LAUF_123.md`
- `docs/forschung/056_ASYNCHRONE_AUDIO_VIDEO_ZEITTEILUNG_LAUF_156.md`
- `mcm_field_organism/live_audio_video_field.py`
- `mcm_field_organism/live_audio_adapter.py`
- `mcm_field_organism/live_video_adapter.py`
- `mcm_field_organism/common_receptor_window.py`
- `mcm_field_organism/adapter_timing_capability.py`
- `tools/run_live_common_receptor_window_audit.py`
- `tools/run_live_adapter_timing_capability_audit.py`
- `tools/run_native_wasapi_endpoint_inventory.py`

Externe Webquellen und MINI_DIO wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Der gemeinsame Pfad war:

```text
SoundDeviceInputSource + OpenCVVideoFrameSource
-> BroadbandHearingPath + LocalChannelGridReceptor
-> vorregistrierte gemeinsame Organismuszeitfenster
-> reduzierte ReceptorTimeSequence je Dockmodalitaet
```

Die Kamera wurde explizit als Geraet `0` angesprochen. Fuer Audio wurden nur
die vom lokalen PortAudio-Inventar als 48-kHz-kompatibel gemeldeten, vom
geschlossenen C920-Zweig verschiedenen WDM-KS-Geraete `11` und `12` geprueft.
Der C920-Audioendpoint wurde nicht erneut geoeffnet.

## Durchgefuehrte Schritte

1. Bestehende gemeinsame Liveaufnahme, Zeitfenster, Adapteraudit und
   Dockuebergabe untersucht.
2. Das aktuelle PortAudio-Inventar und die 48-kHz-Mono-`float32`-Faehigkeit
   anderer lokaler Eingangsansichten geprueft.
3. Einen gemeinsamen Lauf mit Kamera `0`, Audio `12`, fuenf Fenstern zu je
   zwei Sekunden und 20 Kamera-Startframes gestartet.
4. Audio `12` separat mit 100 Callback-Bloecken zu je 480 Samples geprueft.
5. Audio `11` als technische Geraetebaseline gleichartig geprueft.
6. Kamera `0` separat ueber zehn Frames und drei Startframes vermessen.
7. Nach den reproduzierten Adapterabbruechen keine Feld-, Dock- oder
   Runtimeaenderung vorgenommen.

## Messergebnisse und Gegenbaselines

### Gemeinsamer Lauf

Der gemeinsame geplante Zehn-Sekunden-Lauf brach nach rund 22 Sekunden ab:

```text
AudioCaptureError: input stream did not deliver its next frame
```

Damit entstanden keine vollstaendigen gemeinsamen Rezeptorsequenzen. Folglich
konnten gemeinsame Zeitkontinuitaet, Completion-Synchronisierung,
Dock-Herkunft und verlustfreie Handoff-Zaehlung nicht positiv abgenommen
werden.

### Audio-Gegenbaselines

PortAudio meldete fuer `11` und `12` die Annahme von 48 kHz, Mono und
`float32`. Beide separaten 100-Callback-Laeufe endeten jedoch nach jeweils
rund sechs Sekunden mit:

```text
RuntimeError: audio callback timing probe timed out
```

Die blosse Formatannahme ist daher keine ausreichende Baseline fuer eine
kontinuierlich liefernde reale Audioquelle.

Die native MMDevice-/WASAPI-Inventarisierung ergab weiterhin genau einen
aktiven Capture-Endpoint:

```text
Mikrofon (HD Pro Webcam C920)
Mixsicht: 16000 Hz, 2 Kanaele, 32 Bit
```

Dieser Endpoint bleibt gemaess Lauf 122 fuer den festen nativen
48-kHz-Quellenzeitvertrag geschlossen.

### Kamera-Gegenbaseline

Die Kamera lieferte zehn Frames ueber DSHOW:

```text
read minimum: 0,1850556000 s
read median:  0,2038594499 s
read maximum: 0,2091114001 s
```

Das entspricht fuer diesen kurzen Lauf etwa 4,9 gelesenen Frames pro Sekunde.
DSHOW stellte weder eine nutzbare Positionszeit noch einen monotonen
Presentation-Timestamp bereit. Belichtet wurde mit einer verfuegbaren
Einstellung, aber ohne ausgewiesene Belichtungsdauer. Eine Organismusstuetze
wurde durch diesen reinen Adapteraudit nicht gemappt.

## Einordnung

**Beobachtet:** Die Kamera kann einzeln Frames liefern. Die beiden vom
PortAudio-Formatcheck akzeptierten alternativen Audioansichten liefern in der
vorhandenen Callbackprobe nicht die geforderte kontinuierliche Folge. Der
gemeinsame Lauf scheitert am ausbleibenden Audioblock.

**Technische Interpretation:** Die aktuelle Projektumgebung besitzt keine
freigegebene und praktisch kontinuierlich liefernde 48-kHz-Audioquelle fuer
den gemeinsamen Livepfad. Formatkompatibilitaet allein reicht fuer die
Laufzeitfaehigkeit nicht aus. Die Kamera besitzt zudem keine native
Quellenzeitmetadaten im verwendeten DSHOW-Pfad; vorhanden ist nur gemessene
Organismus-Lesezeit.

**Hypothese:** Ein ausdruecklich bereitgestellter aktiver 48-kHz-Capture-
Endpoint koennte den unveraenderten gemeinsamen Pfad lauffaehig machen. Das
ist nicht beobachtet.

## Grenzen und nicht gepruefte Annahmen

- Der geplante laengere gemeinsame Lauf wurde technisch nicht abgeschlossen.
- Es liegt keine positive gemeinsame Rate, Synchronisierung oder
  Aussetzerstatistik vor.
- Dock-Herkunft und unverfaelschte Uebergabe sind im Code vertraglich
  vorhanden, konnten aber mangels vollstaendiger gemeinsamer Sequenzen nicht
  als reale Laufmessung bestaetigt werden.
- Die WDM-KS-Ansichten `11` und `12` erscheinen nicht als eigene aktive
  native MMDevice-Capture-Endpoints.
- Der geschlossene C920-Audiozweig wurde nicht umgangen oder erneut getestet.
- Es wurden keine Rohdaten gespeichert, keine Medien erzeugt und kein Feld
  fortgeschrieben.
- Memory, Organisation, Topologie, Semantik und Feld-Welt-Feld-Kausalitaet
  wurden nicht untersucht.

## Konkrete Schlussfolgerung

Lauf 157 kann die gemeinsame reale Kamera- und Mikrofonaufnahme nicht als
stabil bestaetigen. Der begrenzende Befund ist eine fehlende freigegebene,
kontinuierlich liefernde 48-kHz-Audioquelle; der visuelle Pfad allein ist
lesbar, besitzt im aktuellen Backend aber keine native Quellenzeit. Eine
Runtimeaenderung waere ohne geeignete Hardware keine Stabilisierung und wurde
daher nicht vorgenommen. Eine Zielabweichung ist nicht erkennbar.

## Naechster begrenzter Forschungslauf

Lauf 158 sollte ausschliesslich die reale Audioanschlussstelle wieder
herstellen: einen ausdruecklich bereitgestellten aktiven 48-kHz-Capture-
Endpoint inventarisieren, dessen exaktes Format pruefen und danach einen
kurzen Callback-Kontinuitaetslauf ohne Kamera ausfuehren. Erst bei
kontinuierlicher Audioabnahme darf derselbe unveraenderte Endpoint zusammen
mit Kamera `0` in einem vorregistrierten Zehn-Sekunden-Lauf fuer Rate,
Aussetzer, gemeinsame Organismuszeit und einmalige Dockuebergabe geprueft
werden. Bis dahin bleiben Feldadvance, Memory und der physische
Effektor-Zielflaeche-Kamera-Zweig getrennt.
