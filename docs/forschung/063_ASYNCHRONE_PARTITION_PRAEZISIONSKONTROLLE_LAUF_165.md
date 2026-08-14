# Lauf 165: Praezisionskontrolle der asynchronen Zeitpartition

## Forschungsfrage und Auftrag

Geprueft wurde, ob die in Lauf 164 beobachtete Grob-/Fein-Abweichung bis
`1.1e-14` durch die vorhandenen Gleitkommaoperationen an den Grenzen der
Zeitpartition erklaert wird. Dazu wurden aktive Audio-Video-Arme gegen
wertneutrale Arme und die tatsaechlich verwendete Spektralbasis gegen eine
komponentenweise `math.fsum`-Baseline verglichen.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- aktueller freigegebener Uebergabeeingang zu Lauf 164
- `AGENTS.md`
- `docs/forschung/030_KONZEPT_BESTANDSLUECKE_ASYNCHRONER_AUDIO_VIDEO_WELTKONTAKT.md`
- `docs/forschung/062_ASYNCHRONE_AUDIO_VIDEO_RATEN_PARTITION_LAUF_164.md`
- `mcm_field_organism/asynchronous_audio_video_partition_probe.py`
- `mcm_field_organism/asynchronous_audio_video_rate_probe.py`
- `mcm_field_organism/neutral_local_field_substrate.py`

Externe Quellen und Projektdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu erstellt wurden:

- `mcm_field_organism/asynchronous_audio_video_precision_probe.py`
- `tests/test_asynchronous_audio_video_precision_probe.py`
- `tools/run_asynchronous_audio_video_precision_probe.py`
- dieses Forschungsdokument

Verwendete Schnittstellen waren `run_asynchronous_partition_arm`,
`build_shared_mcm_field`, `_diffusion_generator` und `numpy.linalg.eigh`.
Die vorhandene Feld-, Rezeptor- und Integrationsmechanik wurde nicht geaendert.

## Durchgefuehrte Schritte

1. Die Ratepaare `50/5`, `100/10` und `200/20 Hz` wurden erneut aus frischen
   Zustaenden als grobe und feine Partition ausgefuehrt.
2. Fuer jedes Ratepaar wurde derselbe Vergleich mit dem wertneutralen
   Weltarm `w0` ausgefuehrt. Ereigniszeiten und Partitionsgrenzen blieben
   erhalten, Audio- und Videowerte trugen aber keinen aktiven Inhalt.
3. Fuer den unveraenderten Diffusionsgenerator wurde die Eigenbasis bestimmt.
4. Der maximale Rest von `Q.T Q - I` wurde einmal mit NumPy und einmal durch
   komponentenweise Produkte mit `math.fsum` berechnet.
5. Der hoechste neutrale Feinarm wurde frisch wiederholt.
6. Die neuen Tests wurden zusammen mit den vorhandenen Partitions- und
   Ratenproben ausgefuehrt.

## Messergebnisse und Gegenbaselines

```text
Audio/Video  Schritte  Signal activation  Signal afterimage  Null activation  Null afterimage
50/5 Hz           46       2.0903e-15          2.4156e-15       1.2299e-15       1.3487e-15
100/10 Hz         91       4.6352e-15          4.6144e-15       2.7235e-15       3.1381e-15
200/20 Hz        182       9.7145e-15          1.0976e-14       5.6309e-15       6.5286e-15
```

```text
Neuronen:                              84
NumPy-Orthogonalitaetsrest L-inf:      1.556971382730197e-15
fsum-Orthogonalitaetsrest L-inf:       1.5543122344752192e-15
frische Nullwiederholung exakt:        ja
Tests:                                 8 passed
```

## Einordnung

**Beobachtetes Ergebnis:** Auch der wertneutrale Arm zeigt eine nicht
bitgleiche Grob-/Fein-Abweichung. Sie waechst mit der Zahl der feinen Schritte.
Die mit `math.fsum` kontrollierte Eigenbasis ist in Float64 nicht exakt
orthogonal; ihr maximaler Rest liegt bei `1.55e-15`.

**Technische Interpretation:** Jeder feine Lauf schreibt nach einem Schritt
aus der Spektralbasis in den Feldvektor zurueck und projiziert beim naechsten
Schritt erneut hinein. Der grobe Lauf hat nur einen solchen aeusseren
Basiswechsel. Der neutrale Befund schliesst aktive Audio-/Video-Werte als
notwendige Ursache aus. Der `fsum`-Befund zeigt, dass der Rest nicht allein aus
der NumPy-Reduktionsreihenfolge bei der Kontrollmessung entsteht, sondern
bereits in der endlichen Float64-Darstellung der numerischen Eigenbasis liegt.

**Hypothese:** Die verbleibende Differenz zwischen Signal- und Nullarm entsteht
aus denselben Rundungen zusaetzlich zu den punktweisen Kontaktaktualisierungen.

**Offene Frage:** Die einzelnen Rundungsbeitraege von Matrixprodukt,
Exponentialauswertung und Kontaktaktualisierung wurden nicht separat in
beliebiger Praezision nachgerechnet.

## Grenzen und nicht gepruefte Annahmen

- `math.fsum` verbessert die komponentenweise Summation, ersetzt aber keine
  vollstaendige hochpraezise Wiederimplementierung des Integrators.
- Die Diagnose lokalisiert die Abweichung auf die technische Partition und
  ihre Float64-Basiswechsel; sie weist keinen einzelnen Maschinenbefehl als
  alleinige Ursache nach.
- Digests bleiben absichtlich exakt und reagieren daher auf kleinste
  Floatunterschiede.
- Es gab keine Geraete-, Kamera-, Mikrofon-, Browser-, Medien- oder
  Streamzugriffe.
- Memory, Bedeutung, Organisation und Topologie wurden nicht untersucht.
- Die Laufartefakte sind lokal und unversioniert.

Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Die Grob-/Fein-Abweichung aus Lauf 164 ist eine reproduzierbare technische
Float64-Partitionswirkung. Sie tritt ohne aktive Audio- oder Videowerte auf,
skaliert mit der Zahl wiederholter Spektralbasiswechsel und liegt in derselben
Groessenordnung wie der komponentenweise nachgewiesene Orthogonalitaetsrest.
Damit liefert sie keinen Hinweis auf eine neue Feld-, Memory- oder
Organismusfunktion.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Der synthetische asynchrone Grundlagenpfad ist ausreichend kontrolliert. Als
naechster Lauf sollte die reale Wahrnehmung stabilisiert werden: eine vorab
begrenzte gemeinsame Kamera-/Mikrofon-Laufzeit mit Messung von Zeitkontinuitaet,
Aussetzern, Dock-Herkunft, effektiver Rate und Audio-Video-Versatz. Dabei sind
nur unverfaelschte Rezeptoruebergabe und Runtime-Stabilitaet zu pruefen; eine
Memory-, Bedeutungs- oder Organisationsauswertung bleibt ausgeschlossen.
