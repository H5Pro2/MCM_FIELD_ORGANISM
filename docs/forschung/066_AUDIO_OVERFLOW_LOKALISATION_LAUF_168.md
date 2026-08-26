# Lauf 168: Lokalisation der Audio ueberlaeufe

## Forschungsfrage und Auftrag

Geprueft wurde, ob die 1094 zusammengefassten Audio ueberlaeufe aus Lauf 167
vom Audiotreiber oder von einer vollen internen Transportwarteschlange stammen
und unter welcher vorhandenen Verarbeitungslast sie auftreten.

Dafuer wurden drei vorab begrenzte 30-Sekunden-Arme mit demselben Audiogeraet
und derselben Audiokonfiguration verglichen: Audioadapter allein, gemeinsame
Audio-Video-Rezeptorerfassung ohne Feld und gemeinsame Erfassung mit
unveraenderter Feldfortsetzung.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- der aktuelle freigegebene Uebergabeeingang
- `AGENTS.md`
- `docs/forschung/065_REALE_AUDIO_VIDEO_LANGZEITSTABILITAET_LAUF_167.md`
- `mcm_field_organism/live_audio_adapter.py`
- `mcm_field_organism/live_audio_video_field.py`
- `mcm_field_organism/receptor_time_alignment.py`
- `tools/run_live_adapter_timing_capability_audit.py`
- vorhandene Adapter-, Zeit- und Feldruntimetests

Externe Quellen und projektweite Wissensdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Geaendert wurden:

- `mcm_field_organism/live_audio_adapter.py`
- `mcm_field_organism/live_audio_video_field.py`
- `mcm_field_organism/__init__.py`
- `tests/test_finite_audio_adapter.py`

Neu erstellt wurden:

- `tools/run_live_audio_overflow_localization.py`
- `tests/test_run_live_audio_overflow_localization.py`
- dieser Bericht

`SoundDeviceInputSource` fuehrt nun getrennte additive technische Zaehler fuer
PortAudio-Input-Overflow und volle interne Transportwarteschlange. Der bisherige
`overflow_count` bleibt kompatibel die Summe beider Werte. Optionale
Diagnosebeobachter lesen nur diese Zaehler. Feld- und Rezeptormechanik wurden
nicht veraendert.

Verwendet wurden OpenCV-Kameraindex 0 und sounddevice-Audioindex 1, das
Mikrofon der HD Pro Webcam C920.

## Durchgefuehrte Schritte

1. Die beiden bisher zusammengefassten Overflow-Ursachen wurden im vorhandenen
   Audioadapter getrennt instrumentiert.
2. Gesamtzaehler, getrennte Zaehler und unveraendertes Standardverhalten wurden
   mit Regressionstests abgesichert.
3. Der Audioadapter wurde 30 Sekunden direkt und ohne Rezeptorverarbeitung
   verbraucht.
4. Audio und Video wurden 30 Sekunden gemeinsam in die vorhandenen reduzierten
   Rezeptoren aufgenommen, ohne Feldfortsetzung.
5. Dieselbe gemeinsame Erfassung wurde 30 Sekunden mit unveraenderter
   Feldfortsetzung und exakter Fenstergegenbaseline ausgefuehrt.

## Messergebnisse und Gegenbaselines

```text
Arm                         Audio  Video  Treiber  Transport  Gesamt
Audioadapter allein          3000      0        0          0       0
Audio+Video-Rezeptoren       2997    645        0          0       0
Audio+Video+Feld             2997    379        0         94      94
```

```text
Audioadapter-Erfassungsspann:        29.9801342 s
Feldfenster mit Baseline-Abweichung: 0
Feld-Checkpoints:                   29
Rohsensorpayload gespeichert:       nein
Regressionstests:                   47 passed, 9 subtests passed
```

Der Audioadapter-Arm ist die Geraete- und Treibergegenbaseline. Der
Rezeptorarm kontrolliert gemeinsame Kamera-, Audio- und Rezeptorlast ohne
Feldberechnung. Nur der Feldarm erzeugte Verluste, und alle 94 Verluste wurden
dem internen Transportpuffer zugeordnet.

## Einordnung

**Beobachtet:** PortAudio meldete in keinem Arm einen Input-Overflow. Die
interne Audiowarteschlange lief ausschliesslich im Feldarm 94-mal voll.

**Technische Interpretation:** Die in diesem Lauf beobachteten Audioverluste
entstehen durch internen Konsumentenrueckstand unter der vorhandenen
Feldverarbeitung, nicht durch einen gemeldeten Hardware- oder
PortAudio-Input-Overflow. Die fehlerfreie Feldgegenbaseline zeigt weiterhin
nur die korrekte Verarbeitung der angekommenen Rezeptorzustaende.

**Hypothese:** Die CPU- und Scheduling-Last der synchron zur laufenden
Erfassung ausgefuehrten Feld- und Gegenbaselineberechnung verhindert zeitweise
das schnelle Leeren des auf etwa eine Sekunde begrenzten Audiotransports.

**Offene Frage:** Warteschlangenbelegung und Feldrechenzeit pro Fenster wurden
nicht gemessen. Daher ist noch nicht geklaert, ob eine groessere begrenzte
Warteschlange ausreicht oder Erfassung und Feldberechnung zeitlich staerker
entkoppelt werden muessen.

## Grenzen und nicht gepruefte Annahmen

Die drei Arme wurden nacheinander und nicht gleichzeitig ausgefuehrt.
Kameraautomatik, Weltinhalt und allgemeine Betriebssystemlast waren nicht
kontrolliert. Die unterschiedlichen Videozahlen sind ein technischer
Lastindikator, aber kein kalibrierter Leistungsvergleich.

Es wurden keine Rohbilder oder Audiodaten gespeichert. Memory, Bedeutung,
Organisation und Topologie wurden nicht untersucht. Eine Zielabweichung ist
nicht erkennbar.

## Konkrete Schlussfolgerung

Die Audioverluste aus dem realen Langzeitpfad sind fuer Lauf 168 auf die volle
interne Transportwarteschlange unter Feldlast lokalisiert. Ein Treiber- oder
Mikrofonoverflow wurde in keinem der drei 30-Sekunden-Arme beobachtet. Die
reale Wahrnehmungsruntime bleibt damit technisch instabil, aber die konkrete
Verluststelle ist nun nachgewiesen.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Als naechster Lauf sollte ohne Aenderung der Feldmechanik die notwendige
Transportreserve bestimmt werden. Dazu werden Warteschlangenkapazitaet,
maximale Belegung und Feldrechenzeit pro Fenster technisch instrumentiert.
Anschliessend werden 30-Sekunden-Feldarme mit vorab festgelegten begrenzten
Pufferhorizonten von einer, zwei und vier Sekunden verglichen.

Primaeres Kriterium ist null Transportverlust bei weiterhin null
Treiberoverflow. Zusaetzlich muessen Zeitstempel fortschreiten, alle reduzierten
Zustaende innerhalb des Erfassungshorizonts liegen und die exakte
Feldgegenbaseline erhalten bleiben. Falls auch vier Sekunden nicht ausreichen
oder der Rueckstand monoton waechst, ist keine weitere Puffervergroesserung
gerechtfertigt; dann muss Erfassung von Feld- und Baselineberechnung technisch
entkoppelt werden. Memory-, Bedeutungs- und Organisationsauswertungen bleiben
ausgeschlossen.
