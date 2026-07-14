# Befund 007: Breite logarithmische Audiorezeptorfläche

## 1. Bezug

Ausgeführt wurde
[Methodik 007](../methodik/007_BREITE_LOGARITHMISCHE_AUDIOREZEPTORFLAECHE.md).

Geprüft wurde ausschließlich die synthetische passive Rezeptorfläche. Es fand
in diesem Versuch kein neuer Mikrofonlauf statt.

## 2. Implementierte Rezeptorbaseline

```text
48000-Hz-Audiosamples
-> 100-ms-Rollfenster mit 10-ms-Fortschritt
-> Hann-Fenster
-> reelle FFT
-> überlappende logarithmische Dreiecksbänder
-> verteilte lokale Bandenergien
```

Der Bereich reicht von `50 Hz` bis `18 kHz`. Verglichen wurden 24, 48 und 64
Bänder. Die Implementierung enthält keine Schwelle, Spikemechanik, Kopplung,
Verstärkungsanpassung oder semantische Analyse.

## 3. Ausführung

```text
python -m unittest -v tests.test_log_spectral_receptor
```

Gültiges Ergebnis nach Korrektur einer fehlerhaften Testindizierung:

```text
17 Tests
17 bestanden
0 Fehler
0 Fehlschläge
```

Die Korrektur betraf ausschließlich die Bildung benachbarter Paare in der
Prüfschleife. Die Rezeptormechanik wurde dadurch nicht verändert.

Anschließend bestand die vollständige Projektsuite:

```text
python -m unittest discover

110 Tests
110 bestanden
```

## 4. Frequenzlokalität

Alle vorregistrierten Einzeltonlagen wurden lokal sichtbar:

```text
50 / 80 / 125 / 250 / 440 / 1000 / 2000 / 4000 /
8000 / 12000 / 16000 / 18000 Hz
```

Größte relative Abweichung zwischen Reizfrequenz und Mitte des dominanten
Bandes:

```text
24 Bänder: 13.59 Prozent
48 Bänder:  6.13 Prozent
64 Bänder:  4.61 Prozent
```

Alle drei Geometrien tragen denselben groben Frequenzort. Mehr Bänder erhöhen
erwartungsgemäß die technische Ortsauflösung. Das beweist nicht, dass 64 Bänder
biologisch oder für eine spätere Feldentwicklung richtiger wären.

## 5. Stille, Amplitude und Phase

- Stille blieb bei 24, 48 und 64 Bändern exakt null.
- Eine Verdopplung der Tonamplitude verdoppelte jede Bandenergie innerhalb der
  numerischen Prüfung exakt.
- Bei den geprüften Phasenlagen blieb das dominante Band identisch.
- Der größte relative Unterschied der gesamten Bandlage durch Phase betrug
  ungefähr `0.000572 Prozent`.

Die Bandenergie darf trotzdem nicht als direkte Tonamplitude gelesen werden.
Ein Band fasst durch Hann-Fensterung und überlappende Gewichte mehrere
Spektralanteile zusammen. Dadurch kann sein Zahlenwert die eingespeiste
Einzelamplitude übersteigen.

## 6. Mehrklang

Ein gleichzeitiger kontrollierter Kontakt bei `250`, `4000` und `12000 Hz`
erzeugte drei lokale aktive Regionen. Die Energien der jeweils nächstliegenden
Bänder betrugen ungefähr:

```text
250 Hz:    0.1954
4000 Hz:   0.2416
12000 Hz:  0.1840
```

Die Frequenzen kollabierten nicht in eine globale Summenklasse. Benachbarte
Bänder dürfen durch die überlappende Geometrie gleichzeitig aktiv sein.

## 7. Randwirkung

Die Grenzen `50 Hz` und `18 kHz` sind Filterübergänge, keine harten Mauern.

Bei gleicher Amplitude ergab die 48-Band-Fläche:

```text
50 Hz:     0.499999
40 Hz:     0.250079
20 Hz:     0.0000109
19000 Hz:  0.000000050
```

Der 40-Hz-Reiz wirkt wegen FFT-Auflösung und Hann-Leckage noch mit etwa der
halben 50-Hz-Spitzenantwort in den unteren Rand. Das ist ausgewiesener
Informationsübertritt der Rezeptortransformation und darf nicht als Aktivität
eines tatsächlich gemessenen 50-Hz-Tons interpretiert werden.

## 8. Technische Zeitreichweite

Das Rollfenster erzeugt erst nach zehn 10-ms-Chunks den ersten Zustand. Eine
direkte 100-ms-Analyse und dieselben zehn kausal geordneten Chunks ergeben exakt
dieselbe Bandlage.

Nach einem vollständigen 100-ms-Fenster Stille ist ein früherer Ton exakt aus
dem Rezeptorzustand entfernt. Reset löscht Puffer, Füllstand und Ausgabezähler
und reproduziert danach dieselbe Folge exakt.

Damit trägt die Baseline technische Fensterzeit, aber keinen Nachhall über
`100 ms` hinaus.

## 9. Kritische Grenzen

- Der Bereich ist technisch festgelegt und nicht biologisch nachgewiesen.
- Die logarithmische Geometrie ist ein offener Induktionsbias.
- 24, 48 und 64 Bänder sind Kandidaten, keine natürliche Anatomie.
- Das 100-ms-Fenster verbessert tiefe Frequenzauflösung, erzeugt aber
  Einlaufzeit und zeitliche Glättung.
- Überlappende Bänder duplizieren Anteile zwischen Nachbarn.
- Hann-Fensterung erzeugt Rand- und Leckageeffekte.
- Synthetische stationäre Töne bilden keine reale Hörwelt ab.
- Es existiert keine Wirkung zwischen den Frequenzträgern.

## 10. Evidenz

**E1 für eine breite passive logarithmische Audiorezeptorfläche von 50 Hz bis
18 kHz unter synthetischen Kontrollen.**

Weiterhin **E0** für:

- menschliches oder semantisches Hören,
- MCM-Neuronen,
- ein gekoppeltes auditives MCM-Feld,
- organische Entwicklung,
- Feldintelligenz.

## 11. Architekturentscheidung

Die 48-Band-Fläche darf als mittlere passive Forschungskonfiguration in einen
endlichen realen Mikrofonlauf gehen. 24 und 64 Bänder bleiben obligatorische
Observer-Gegenreferenzen. Keine Variante wird als endgültige Feldgeometrie
festgeschrieben.

Die bisherigen drei Einzelsonden bleiben nur als historische Minimalreferenz
für Methodik 006 bestehen. Sie werden nicht als vollständiges Gehör ausgegeben.

## 12. Bester nächster Schritt

Als nächstes wird ein endlicher realer Mikrofonlauf parallel durch 24, 48 und
64 Bänder geführt. Zu prüfen sind vollständige Bandbelegung, Randdominanz,
Bandzahlstabilität und Rechenzeit. Es werden weiterhin keine Schwellen oder
Spikes verwendet.

Erst wenn reale Audioabschnitte in allen drei Geometrien dieselbe grobe
Spektrallandschaft tragen, darf eine mittlere Rezeptorfläche an eine spätere
auditive MCM-Feldprüfung übergeben werden.
