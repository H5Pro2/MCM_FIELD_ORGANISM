# W1-L: Statische und synthetische Invariantendiagnose

Stand: 2026-08-07

Entscheidung: `W1L_REAL_INVARIANT_CAUSE_NARROWED_NOT_IDENTIFIED`

Forschungslauf: nein

Realer Browser gestartet: nein

W1-K wiederholt: nein

## Auftrag

W1-L grenzt den in W1-K nur als Sammelfehler protokollierten
Eingangsinvariantenfehler statisch und unter synthetischen Daten ein. Die
Scheibe darf weder W1-K wiederholen noch reale Browserpayloads erzeugen.

## Logische Eingrenzung des alten Fehlers

Folgende Ursachen koennen den in W1-K beobachteten Fehlertext nicht erzeugt
haben:

1. **Runtimeabweichung:** Sie besitzt vor dem Paar-Comparator einen eigenen
   Abbruchtext.
2. **Auditive, visuelle oder Ereignisinventare:** Jeder Arm konstruiert vor
   dem Paarvergleich einen `BrowserPayloadTimingArmReceipt`, der exakt
   `111`, `36` und `147` verlangt. Eine Abweichung haette bereits dort mit
   `timing arm inventory changed` abgebrochen.
3. **Engineversion:** Eine Abweichung besitzt vor den Invarianten einen
   eigenen Abbruchtext.
4. **Afterimage:** W1-K uebergibt keine `afterimage_config`.
   `advance_neutral_shared_field_transient()` uebernimmt deshalb fuer jedes
   Neuron unveraendert `neuron.afterimage`. Beide frisch aufgebauten Felder
   beginnen exakt bei null.

Damit verbleiben fuer den historischen W1-K-Sammelfehler nur:

```text
visual_sequence
audio_total_energy
```

Eine eindeutige rueckwirkende Auswahl zwischen diesen Rollen ist ohne neue
reale Payloaddiagnose nicht zulaessig.

## Statische visuelle Gleichheit

W1-L projiziert A0 und C0 auf alle Werte, die `renderVisualFrame()` liest:

- `movement_cycles`;
- Phasendauern und `visual_mode`;
- Canvasgeometrie und Device-Scale;
- visuelle Rate;
- Bewegungsachse und Amplitude;
- Vordergrundgroesse;
- Hintergrund- und Vordergrundfarben.

Die zwei Projektionen sind exakt gleich. `renderVisualFrame()` liest weder
`tone_gain`, `tone_frequency_hz`, `contract_id` noch `source_id`. Auf Ebene
der programmierten Renderfunktion ist daher keine visuelle A0/C0-Variation
vorhanden.

Dieser statische Befund schliesst eine reale Capture- oder PNG-
Nichtdeterministik zwischen zwei getrennten Browserkontexten nicht aus.

## Statische Audiointervalle

Bei 8000 Samples/s umfasst jede 300-ms-Phase genau 2400 Samples:

```text
A0 active support: [2400, 4800)
C0 active support: [4800, 7200)
support length:     2400 samples each
shift:              2400 samples / 300 ms
oscillator cycles:  132 at 440 Hz
```

Die beabsichtigte Verschiebung aendert deshalb weder nominelle Tondauer noch
Sinusphase.

## Synthetische Energiesensitivitaet

Eine reine NumPy-Sonde ohne Browser ergab:

```text
Float64 ideal relative error:   3.700743415417177e-15
Float32 ideal relative error:   0.0
bound tolerance:                1e-12
one missing boundary sample:    9.561948346570113e-05
```

Die ideale Zeitverschiebung besteht die gebundene Toleranz. Bereits ein
anders behandeltes nichtnulles Grenzsample ueberschreitet sie jedoch um viele
Groessenordnungen. Web-Audio-Automationsgrenzen bleiben deshalb eine
plausible, aber nicht nachgewiesene Ursache des W1-K-Abbruchs.

## Diagnosehaertung

`BrowserPayloadTimingInvariantDiagnostics` haelt kuenftig auch fuer ein
ungueltiges Paar ausschliesslich folgende skalare Rollen:

- visuelle Sequenzgleichheit;
- beide Audioenergien, relativen Fehler und Toleranz;
- beide Rezeptor- und Ereignisinventare;
- beide maximalen Afterimagebetraege;
- die exakt fehlgeschlagenen Invariantenrollen;
- `raw_payloads_retained=False`.

`BrowserPayloadTimingPairError` kann diesen Diagnosebeleg tragen. Die JSON-
Projektion enthaelt keine Samples, Bilder, Rezeptorfolgen oder Feldwerte.

Zusaetzlich stellen zwei statische Hilfen die visuellen Rendersignaturen und
die halb offenen Audio-Sampleintervalle bereit. Sie starten keinen Browser.

## Synthetische Abnahme

Die fokussierte Suite bestaetigt:

- exakte Gleichheit der visuellen A0/C0-Rendersignaturen;
- Sampleintervalle `[2400, 4800)` und `[4800, 7200)`;
- gleiche ideale Float32-Audioenergie innerhalb `1e-12`;
- Erkennung eines fehlenden Grenzsamples oberhalb der Toleranz;
- skalaren Diagnosebeleg bei absichtlich ungleicher Fake-Audioenergie;
- keine Samplehaltung in der Diagnoseprojektion;
- weiterhin vollstaendigen Ressourcenabschluss unter Fakes;
- weiterhin keine reale Factory im Paarmodul.

Der fokussierte Verbund besteht mit `21 passed`. Die bekannte
Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen Cachepfad.

## Aussagegrenze

W1-L lokalisiert die historische W1-K-Ursache nicht abschliessend. Der Befund
lautet ausschliesslich:

```text
programmed visual inputs:        statically equal
ideal audio energy:              synthetically equal
real W1-K failing role:          visual_sequence or audio_total_energy
most sensitive known boundary:   audio automation boundary sample
confirmed real cause:            no
```

Es gibt weiterhin keinen realen Feldvergleich und keinen Befund zu
Wahrnehmung, Nachhall, Feldzeit, Praegung, Memory, Organisation, Semantik,
Selbstregulation oder KI.

## W1-L-Entscheidung

```text
historische Ursache eingegrenzt: ja, auf zwei Rollen
historische Ursache identifiziert: nein
statische visuelle Signatur:     exakt gleich
synthetische ideale Energie:     innerhalb Toleranz
Grenzsampleempfindlichkeit:      nachgewiesen unter Synthese
skalare Fehlerdiagnose:          implementiert
realer Browserstart:             nein
W1-K-Wiederholung:               nein
Forschungslauf:                  nein
```

## Bester naechster Schritt

W1-M bindet zuerst einen diagnostischen realen Quellenpaar-Smoke ohne
Feldhandoff. Er darf genau einmal A0/C0 capturen und nur den neuen skalaren
Invariantenbeleg ausgeben. Er bewertet weder Feldzustand noch Wirkung und ist
keine Wiederholung von W1-K. Vor einer Ausfuehrung muessen Werkzeug,
Fehlerausgabe, Prozessschluss und Einmalgrenze statisch dokumentiert werden.
