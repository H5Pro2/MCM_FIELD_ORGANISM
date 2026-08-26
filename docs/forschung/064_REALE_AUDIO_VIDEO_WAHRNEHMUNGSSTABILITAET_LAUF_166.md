# Lauf 166: Reale Audio-Video-Wahrnehmungsstabilitaet

## Forschungsfrage und Auftrag

Geprueft wurde, ob Kamera und Mikrofon ueber begrenzte gemeinsame Laufzeiten
kontinuierlich in die vorhandenen reduzierten Rezeptor- und Feldschnittstellen
uebergeben werden. Gemessen wurden Zeitkontinuitaet, Aussetzer, Modalitaets- und
Dock-Herkunft, native Raten, zeitliche Ueberlappung und unverfaelschte
Felduebergabe. Memory, Bedeutung und Organisation waren ausgeschlossen.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- aktueller freigegebener Uebergabeeingang zu Lauf 165
- `AGENTS.md`
- `docs/forschung/030_KONZEPT_BESTANDSLUECKE_ASYNCHRONER_AUDIO_VIDEO_WELTKONTAKT.md`
- `docs/forschung/063_ASYNCHRONE_PARTITION_PRAEZISIONSKONTROLLE_LAUF_165.md`
- `mcm_field_organism/live_audio_video_field.py`
- `mcm_field_organism/audio_video_neutral_field_runtime.py`
- `mcm_field_organism/receptor_time_alignment.py`
- `mcm_field_organism/common_receptor_window.py`
- vorhandene Live-Runner und zugehoerige Tests

Externe Quellen und Projektdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Ausgefuehrt wurden:

- `tools/run_live_receptor_time_audit.py`
- `tools/run_live_field_a_stability.py`
- `tools/run_live_common_receptor_window_audit.py`

Verwendete Geraete:

- Kamera: expliziter OpenCV-Index `0`
- Audio: expliziter `sounddevice`-Index `1`,
  `Mikrofon (HD Pro Webcam C920)`, 44.1 kHz Standardrate

Die bestehenden Schnittstellen `capture_live_audio_video_time_audit`,
`capture_live_audio_video_neutral_session` und
`capture_live_common_receptor_window_audit` wurden unveraendert verwendet.
Es wurden keine Codeaenderungen vorgenommen.

## Durchgefuehrte Schritte

1. Die vorhandenen Live-Module, Runner und Tests wurden inventarisiert.
2. Die verfuegbaren Audioeingabegeraete wurden abgefragt. Kamera `0` und das
   Webcam-Mikrofon `1` wurden explizit gewaehlt.
3. Ein gemeinsamer Zeit-Audit ueber nominal fuenf Sekunden wurde ausgefuehrt.
4. Eine fortlaufende neutrale Feld-Session ueber sechs Einsekundenfenster wurde
   mit Checkpoint-Fortsetzung und exakter Gegenbaseline ausgefuehrt.
5. Ein unabhaengiger Common-Window-Audit ueber sechs Einsekundenfenster wurde
   ohne Auswahl, Mittelung, Interpolation oder Hold ausgefuehrt.
6. Die relevanten Live-, Zeit- und Fenstervertraege wurden getestet.

## Messergebnisse und Gegenbaselines

### Zeit-Audit, nominal 5 Sekunden

```text
Organismustakt:                         organism.monotonic_ns
auditive Zustaende:                     491
auditiver Erfassungsspann:              4.9197681 s
effektive auditive Rate:                ca. 99.8 Hz
visuelle Zustaende:                     80
visueller Erfassungsspann:              4.9650275 s
effektive visuelle Rate:                ca. 16.1 Hz
native Ueberlappungen:                  561
eindeutige Eins-zu-eins-Ueberlappungen: 0
mehrdeutige auditive Snapshots:         562
unzugeordnete auditive Snapshots:       9
Auswahl oder Interpolation:             nein
```

### Fortlaufende neutrale Feld-Session, 6 x 1 Sekunde

```text
abgeschlossene Fenster:                 6
auditive Rezeptorzustaende:             597
visuelle Rezeptorzustaende:             87
Kamera-Capture-Frames insgesamt:        88
Audio-Ueberlaeufe:                      0
Checkpoint-Fortsetzungen:               5
exakte Baseline-Digesttreffer:           6 von 6
max. Aktivierungsfehler zur Baseline:   0.0
max. afterimage-Fehler zur Baseline:    0.0
Rohdaten gespeichert:                   nein
Rueckschreiben in die Welt:             nein
```

Die Modalitaetsprofile blieben getrennt und vollstaendig:

```text
auditive Carrier je Profil:             48
visuelle Carrier je Profil:             288
gemeinsame Quellenstuetzungen:           684
```

### Common-Window-Gegenbaseline, 6 x 1 Sekunde

```text
Fenster   auditiv   visuell
0         111       16
1          98       15
2         101       14
3          98       15
4          98       15
5         101       15
```

```text
Zustaende ausserhalb des Horizonts:     0
Fenstergrenzen kreuzende Zustaende:     12
Auswahl/Mittelung/Interpolation/Hold:   nein
Rohdaten gespeichert:                   nein
Tests:                                  28 passed, 12 subtests passed
```

## Einordnung

**Beobachtetes Ergebnis:** Kamera und Mikrofon lieferten in allen geprueften
Einsekundenfenstern reduzierte Rezeptorzustaende. Es trat kein Audioueberlauf
und kein leeres Modalitaetsfenster auf. Die gemeinsame Feld-Session blieb ueber
fuenf Wiederaufnahmen exakt zur unabhaengigen Gegenbaseline.

**Technische Interpretation:** Die vorhandene Runtime traegt beide nativen
Raten auf einem gemeinsamen monotonen Organismustakt, ohne sie auf eine
kuenstliche Eins-zu-eins-Paarung zu reduzieren. Modalitaet, Geometrie und
Carrier-Identitaet bleiben getrennt und bilden die technische Dock-Herkunft.

**Negativer Befund:** Eine eindeutige Eins-zu-eins-Synchronisierung liegt nicht
vor. Das ist bei etwa 100 Hz Audio gegen 16 Hz Video erwartbar und wurde von der
Runtime weder erzwungen noch kaschiert. Zwoelf native Zustandsintervalle
kreuzten die vorab definierten Einsekundenfenster.

**Hypothese:** Die neun im Fuenfsekunden-Audit nicht ueberlappten auditiven
Snapshots liegen an den unterschiedlichen Start- und Endrandausdehnungen der
beiden Erfassungs-Threads. Dieser Randbeitrag wurde nicht separat variiert.

**Offene Frage:** Ob dieselben Raten und Randbeitraege ueber Minuten statt
Sekunden stabil bleiben, wurde nicht untersucht.

## Grenzen und nicht gepruefte Annahmen

- Die drei Messungen waren unabhaengige kurze Geraetelaeufe und zusammen kein
  Langzeitversuch.
- Die Kamera meldete in der Feld-Session keine akzeptierten manuellen
  Akquisitionskontrollen; automatische Kameraeffekte wurden nicht getrennt.
- Es wurde kein externer Hardware-Zeitstempel oder kalibrierter
  Audio-Video-Latenzmarker eingesetzt. Gemessen wurde der gemeinsame lokale
  `monotonic_ns`-Takt der vorhandenen Adapter.
- Dock-Herkunft wurde anhand vorhandener Modalitaets-, Geometrie- und
  Carriervertraege geprueft, nicht durch einen externen physischen Marker.
- Es wurden keine Rohbilder, Audiodateien, Downloads oder Medienartefakte
  erzeugt.
- Memory, Bedeutung, Semantik, Organisation und Topologie wurden nicht
  untersucht.

Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Der reale gemeinsame Kamera-/Mikrofonpfad war in den begrenzten Laeufen
technisch kontinuierlich: Jedes Fenster enthielt beide Modalitaeten, es gab
keine Audioueberlaeufe, keine Zustandsverluste ausserhalb des Horizonts und die
Feldfortsetzung entsprach in allen sechs Fenstern exakt der Gegenbaseline.

Die Runtime bewahrt unterschiedliche native Raten und deren viele-zu-viele
Zeitueberlappung unverfaelscht. Dieser Befund weist nur die technische
Weltkontakt- und Felduebergabe nach; er ist kein Memory- oder
Organismusfunktionsnachweis.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Als naechster Lauf sollte dieselbe unveraenderte gemeinsame Runtime ueber eine
vorab begrenzte Dauer von 60 Sekunden in zehn Sechssekundenbloecken geprueft
werden. Vorab festzulegen sind ausschliesslich Ausfallkriterien fuer leere
Modalitaetsfenster, Audioueberlaeufe, nicht fortschreitende Zeitstempel,
veraenderte Carrier-Identitaeten und Abweichungen von der exakten
Feldgegenbaseline. Kamera-Automatik, Weltinhalt und Feldwerte sind offen zu
berichten und duerfen nicht auf ein gewuenschtes Ergebnis geregelt werden.
