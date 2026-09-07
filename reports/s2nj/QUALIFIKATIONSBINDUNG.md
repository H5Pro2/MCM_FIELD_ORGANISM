# S2-NJ: private Ausgangshalbierung, neutrale Qualifikationsbindung

Nur Umsetzung des privat freigegebenen Kandidaten aus
[S2-NI](../../docs/S2NI_STATISCHER_AUDITIVER_REZEPTOR_KONTAKT_SKALIERUNGSVERTRAG.md).
Keine Produktionsumstellung, keine Wiedereroeffnung von S2-NH.

## Produktgrenze

`tools/_s2nj_private_auditory_output_projection.py` unterstuetzt ausschliesslich
das unveraenderte `LogSpectralConfig` mit 48000 Hz, 4800 Samples, 480 Hop,
50..18000 Hz und 48 Baendern. Hann-/FFT-Rezeptorcode ist per SHA-256 gebunden.
Die Projektion selbst fuehrt keine FFT oder PCM-Verarbeitung aus.

`project_auditory_half_v1` verlangt den alten `AuditoryReceptorState`, die
explizite unskalierte Profilbindung und unveraenderte Geometrie. Sie validiert
native Samplezeit, Carrier, Werte und Aktivitaetsform, multipliziert jedes der
48 Elemente genau einmal mit `0.5` und prueft danach endlich und `0<=z<=1`.
Kein Fehler veroeffentlicht einen Teilvektor. Negative Rohenergien werden vor
der Multiplikation abgewiesen, auch wenn sie zu minus Null unterlaufen koennten.

`HalfScaleAuditory48V1` ist ein eigener gefrorener Typ, kein alter Rezeptorzustand.
Profil-ID `s2nj.auditory.hann48.output-half.v1`, neue Geometrie mit `.half.v1`,
Quellzustands-/Quellwert-/Profil-/Projektionsdigests verhindern Verwechslung
im vorgesehenen typisierten Pfad. Erneute Projektion des neuen Typs wird
abgewiesen. Keine automatische Konvertierung in alte Adapter; diese bleiben
unveraendert. Digests sind Integritaetsbindungen, keine Herkunftsbeweise gegen
absichtlich neu konstruierte und falsch deklarierte Eingangsobjekte.

## Arithmetik und Grenzen

Binary64, qualifizierte Round-to-nearest/ties-to-even-Umgebung. Keine
dynamische Normalisierung, Saettigung, Flush-to-zero oder Korpusabhaengigkeit.
Subnormalzahlen behalten das native gerundete Multiplikationsergebnis.
Kleinste positive Subnormalzahl mal 0.5 darf zu Null runden; doppelte kleinste
Subnormalzahl bleibt nach Halbierung subnormal. Unterlauf und subnormale
Ausgaenge werden mit Bandindizes gebunden. Negative Null bleibt negative Null.
Eine Umkehrbarkeit fuer jeden Binary64-Wert wird nicht behauptet.

Vorab: 48 Ausgabewerte, maximal 16.384 kanonische Ausgabebytes je Projektion;
acht reale neutrale Fenster/Analysen und 384 reale Rezeptorwerte. Hoechstens
ein PCM-Fenster gleichzeitig; keine PCM-Ablage. Synthetische Vektoren pruefen
nur Fehler-/Grenzverhalten, nicht die Realisierbarkeit durch einen Rezeptor.
Insbesondere ist Rohwert 2 eine inklusive Validatorpruefung, kein erreichbares
Maximum aus der analytischen Hann-Schranke.

## Feste Quellen vor dem Testaufruf

Alle Fenster enthalten 4800 Mono-Samples bei 48000 Hz, als PCM_F32LE:

| ID | Literale Bildung |
| --- | --- |
| zero | konstant 0 |
| positive-full | konstant +1 |
| negative-full | konstant -1 |
| alternating-full | +1, -1 im Wechsel, beginnend mit +1 |
| impulse-edge | +1 an Index 0, sonst 0 |
| impulse-center | -1 an Index 2400, sonst 0 |
| mixture-one | (300 Hz, 0.25, 0.0), (1100 Hz, 0.25, 0.5), (6000 Hz, 0.25, 1.0) |
| mixture-two | (440 Hz, 0.4, 0.125), (3000 Hz, 0.2, 0.75), (11000 Hz, 0.1, -0.25) |

Mischungsparameter: Frequenz, Amplitude, Phase in Radiant. Je Sample in
angegebener Reihenfolge `sum(amplitude*sin(((2*pi*frequency*n)/48000)+phase))`,
danach einmal `struct.pack_into('<f', ...)`. Keine Suche und kein Zufallsseed.
Die Amplitudensummen liegen bereits unter Eins; kein Clip oder Normalize.
Der bestehende Rezeptor analysiert jeden dieser acht Faelle genau einmal.
Die direkte Skalierungsreferenz verwendet `float(Fraction.from_float(E)/2)`.
Keine NH-Quelle, keine Quellenmaterialisierung aus historischen Plandateien.

## Einmalqualifikation

`reports/s2nj/qualify_once.py` uebernimmt nur das vorhandene kleine
Subprozess-/Dateihash-Muster. Genau ein `unittest`-Aufruf mit 16 Testkoerpern
und Fail-fast, keine Wiederholung. Vorab werden AST-Testinventar, obiges
Quellenliteral, Kommando, Interpreter-/NumPy-Identitaet und Quellhashes
gebunden. Pro JSON-Artefakt maximal 131.072 Byte. Keine neue Laufplattform.

Abgedeckt: reale acht Quellen, Profilverwechslung, Typ-/Dimensions-/Carrier-
und Zeitbindung, NaN/Inf, negative Rohwerte, inklusive Grenze und Verletzung,
Unterlauf, Subnormale, signed zero, Unveraenderlichkeit, manipulierte
Ausgaben/Digests, Ausgabegrenze und fehlende Integrationsimporte.

Drei Aussagen bleiben getrennt: (1) analytische Schranke in exakter
Arithmetik aus S2-NI; (2) erst danach beobachtete lokale Testresultate;
(3) weiterhin kein universeller Fehlernachweis der gesamten Gleitkommakette.
Auch ein Bestehen erlaubt weder Memory-/Feld-/Runtimeintegration noch eine
unveraenderte Uebernahme von 0.2 und 0.02. Deren Bedeutung bleibt separat
zu entscheiden. Beide Hauptgates bleiben False, historische Belege erhalten.
