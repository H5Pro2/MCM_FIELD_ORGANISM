# Lauf 167: Reale Audio-Video-Langzeitstabilitaet

## Forschungsfrage und Auftrag

Geprueft wurde, ob die in Lauf 166 kurzfristig beobachtete technische
Audio-Video-Stabilitaet mit derselben Feldruntime ueber 60 Sekunden bestehen
bleibt. Der Lauf war vorab auf 60 Einsekundenfenster in zehn Bloecken zu je
sechs Fenstern begrenzt.

Vorab festgelegte Ausfallkriterien waren ein leeres Modalitaetsfenster, ein
Audio ueberlauf, ein nicht fortschreitender Zeitstempel, eine veraenderte
Carrier-Identitaet oder eine Abweichung von der exakten Feldgegenbaseline.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- der aktuelle freigegebene Uebergabeeingang
- `AGENTS.md`
- `docs/forschung/064_REALE_AUDIO_VIDEO_WAHRNEHMUNGSSTABILITAET_LAUF_166.md`
- `mcm_field_organism/live_audio_video_field.py`
- `mcm_field_organism/live_audio_adapter.py`
- `mcm_field_organism/audio_video_neutral_field_runtime.py`
- vorhandene Runtime- und Adaptertests

Externe Quellen und projektweite Wissensdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu erstellt wurden:

- `tools/run_live_audio_video_long_stability.py`
- `tests/test_run_live_audio_video_long_stability.py`
- dieser Bericht

Verwendet wurde unveraendert
`capture_live_audio_video_neutral_session` mit OpenCV-Kameraindex 0 und
sounddevice-Audioindex 1, dem Mikrofon der HD Pro Webcam C920 bei 44.1 kHz.
Die Feld- und Rezeptormechanik wurde nicht veraendert. Der Runner bewahrt nur
reduzierte Beobachtungen und Rezeptorprofile auf, keine Rohbilder oder
Audiodaten.

## Durchgefuehrte Schritte

1. Die bestehende Langzeitschnittstelle und ihre Ausfallindikatoren wurden
   untersucht.
2. Ein reproduzierbarer Runner fuer 60 Einsekundenfenster und zehn
   Sechssekundenbloecke wurde ergaenzt.
3. Derselbe neutrale Feldpfad wie in Lauf 166 wurde mit kontinuierlich
   geoeffneten Kamera- und Mikrofonschnittstellen ausgefuehrt.
4. Modalitaetsbelegung, Zeitfortschritt, Carrier-Identitaet und exakte
   Feldgegenbaseline wurden fuer jedes Fenster geprueft.
5. Die vorab festgelegten Kriterien wurden als explizite maschinenlesbare
   Ausfallentscheidung im Runner abgesichert.

## Messergebnisse und Gegenbaselines

```text
Block  Fenster  auditiv  visuell  exakte Baseline
0       0-5       597       81       6/6
1       6-11      596       73       6/6
2      12-17      600       73       6/6
3      18-23      585       70       6/6
4      24-29      601       72       6/6
5      30-35      597       73       6/6
6      36-41      601       71       6/6
7      42-47      600       69       6/6
8      48-53      600       72       6/6
9      54-59      598       72       6/6
```

```text
auditive Rezeptorzustaende:       5975
visuelle Rezeptorzustaende:        726
Kamera-Capture-Frames:             727
Checkpoint-Fortsetzungen:           59
leere Modalitaetsfenster:             0
nicht fortschreitende Fenster:        0
Carrier-Identitaetswechsel:            0
Baseline-Abweichungsfenster:           0
Audio ueberlaeufe:                  1094
Rohsensorpayload gespeichert:      nein
Tests:                              16 passed, 9 subtests passed
```

Die Ausfallentscheidung lautet:

```text
leeres Modalitaetsfenster:       nein
Audio ueberlauf:                 ja
nicht fortschreitender Zeitstempel: nein
veraenderte Carrier-Identitaet:  nein
Feldbaseline-Abweichung:         nein
alle Ausfallkriterien frei:      nein
```

## Einordnung

**Beobachtet:** Alle 60 Fenster enthielten beide Modalitaeten. Zeitstempel und
Carrier-Identitaeten blieben stabil. Die fortgesetzte Feldberechnung traf in
allen Fenstern die exakte Gegenbaseline. Gleichzeitig wurden 1094 Audio
ueberlaeufe gezaehlt.

**Technische Interpretation:** Der reale Langzeitpfad hat das vorab festgelegte
Stabilitaetskriterium nicht bestanden. Vorhandene Rezeptorzustaende wurden
korrekt und reproduzierbar an das Feld uebergeben; die Audioerfassung war aber
nicht verlustfrei.

**Hypothese:** Rechenlast oder Konsumentenrueckstand waehrend der gemeinsamen
Rezeptor- und Feldverarbeitung koennen einen Teil der Verluste verursachen.

**Offene Frage:** `SoundDeviceInputSource.overflow_count` vereinigt zwei
Ursachen: vom Audiotreiber gemeldeten Input-Overflow und eine volle interne
Transportwarteschlange. Lauf 167 kann diese Ursachen nicht getrennt
quantifizieren.

## Grenzen und nicht gepruefte Annahmen

Es wurden keine externen Hardware-Zeitstempel und keine kalibrierten
Audio-Video-Latenzmarker verwendet. Kameraautomatik und Weltinhalt waren
unkontrolliert. Die gemessene visuelle Rate lag unter den kurzen Messungen aus
Lauf 166; deren Ursache wurde nicht isoliert.

Der Lauf pruefte keine Memory-, Bedeutungs-, Organisations- oder
Topologiefunktion. Die vorhandene Feldmechanik wurde nicht als Ursache oder
Loesung der Audioverluste angenommen. Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Die 60-sekuendige gemeinsame reale Wahrnehmung ist nach den vorab festgelegten
Kriterien nicht stabil, weil Audioframes verloren gingen. Die fehlerfreie
Feldgegenbaseline weist nur nach, dass die tatsaechlich angekommenen
Rezeptorzustaende unverfaelscht weitergerechnet wurden. Sie widerlegt den
Erfassungsverlust nicht und ist kein Memory- oder Organismusfunktionsnachweis.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Als naechster Lauf sollte die Herkunft der Audio ueberlaeufe ohne Aenderung der
Feldmechanik getrennt gemessen werden. Dafuer sind zwei technische Zaehler im
Audioadapter vorzusehen: PortAudio-Input-Overflow und volle interne
Transportwarteschlange. Anschliessend werden mit identischem Geraet und
identischer Audiokonfiguration drei vorab begrenzte 30-Sekunden-Arme verglichen:

- Audioadapter allein
- gemeinsame Audio-Video-Rezeptorerfassung ohne Feldfortsetzung
- gemeinsame Audio-Video-Erfassung mit unveraenderter Feldfortsetzung

Gegenbaselines sind die beiden getrennten Verlustzaehler, die gelieferten
Audioframes und der Zeitfortschritt. Erst nach Lokalisation und Beseitigung des
technischen Verlustpfads sollte der 60-Sekunden-Stabilitaetslauf wiederholt
werden. Memory-, Bedeutungs- und Organisationsauswertungen bleiben
ausgeschlossen.
