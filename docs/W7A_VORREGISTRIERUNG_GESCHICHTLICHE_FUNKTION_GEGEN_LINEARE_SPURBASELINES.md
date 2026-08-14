# W7-A: Geschichtliche Funktion gegen lineare Spurbaselines

Stand: 2026-08-09

Entscheidung: `W7A_MINIMAL_LINEAR_HISTORY_DISCRIMINATION_PREREGISTERED`

Arbeitsart: statische Vorregistrierung

Runtimeaenderung: nein

Browser oder Forschungslauf: nein

## Ausgangspunkt

W6-I hat unter einer real gerenderten kontrollierten Browserwelt gezeigt,
dass der in S1-B gebildete L-Zustand bei identischer spaeterer Probe kausal
auf S zurueckwirkt. Dieser Einmallauf ist abgeschlossen und darf nicht
wiederholt werden.

S1-B und die S2-B2-Referenz sind definitionsgleich. Deshalb kann S1-B B2
nicht uebertreffen. Ein positiver R8/C8-Kontrast in S1-B waere zunaechst die
erwartete Wirkung eines festen linearen reziproken Zweizeitensystems und kein
Memorybefund.

## Forschungsfrage

Laesst sich die spaetere Wirkung von acht getrennten Weltkontakten gegen
einen kontaktzeitgleichen Dauerkontakt vollstaendig durch die bereits
gebundene lineare B2-Spurdynamik erklaeren, und welcher Anteil verschwindet,
wenn die L-nach-S-Rueckwirkung in der einseitigen B1-Spur fehlt?

Die Frage sucht keine Emergenz und keine Bedeutung. Sie prueft, welche
Funktion mit der vorhandenen linearen Mechanik tatsaechlich erreicht ist und
wo eine neue Substratfunktion erforderlich wird.

## Wiederverwendeter Weltvertrag

W7-A erzeugt keine neue Welt. Verwendet wird spaeter ausschliesslich das
bereits gebundene kontrollierte S2-C11-Paar:

```text
R8: acht A-Kontakte zu je 0.4 s mit sieben N-Luecken zu je 0.4 s
C8: ein zusammenhaengender A-Kontakt von 3.2 s
Gesamtdauer je Arm:       8.0 s
aktive Kontaktzeit:       3.2 s
zeitlicher Schwerpunkt:   4.0 s
Quellenstuetzen je Arm:   871
Probeunterstuetzungen:    31
```

R8 und C8 besitzen dieselbe kontrollierte Audio-/Video-Welt, Rezeptorgeometrie,
Gesamtdauer, aktive Kontaktzeit und denselben zeitlichen Schwerpunkt. Nur die
zeitliche Gliederung unterscheidet sich. Kamera, Live-Mikrofon, physische
Sensorik, Browser und oeffentliche Medien bleiben fuer W7-A unbenutzt.

## Modellarme

### B0 - schneller Nullpfad

Kein wirksamer L-Zustand. Nach externer S/H-Angleichung muss die identische
Probe fuer R8 und C8 exakt denselben Verlauf liefern.

### B1 - einseitige lineare Leaky-Spur

```text
dS/dt = vorhandene schnelle MCM-Wirkung
dL/dt = (g/rho) * (S - L)
```

B1 darf unterschiedliche L-Endlagen bilden, besitzt aber keine L-nach-S-
Rueckwirkung. Nach S/H-Angleichung muss die identische Probe deshalb in S/H
zwischen R8 und C8 exakt gleich bleiben.

### B2 - reziproke lineare Referenz

```text
dS/dt = vorhandene schnelle MCM-Wirkung - g * (S - L)
dL/dt = (g/rho) * (S - L)
```

B2 ist mathematisch identisch mit S1-B. Produktionspfad und unabhaengige
Referenzrechnung muessen deshalb innerhalb der vorab gebundenen numerischen
Toleranz uebereinstimmen.

Gemeinsame Parameter bleiben:

```text
rho = 8
g   = 0.25 / s
```

Eine `langsame Feldkopie` mit derselben Gleichung wie B1 wird nicht als
zweite unabhaengige Baseline gezaehlt. Zwei Bezeichnungen fuer dieselbe
exponentielle S-nach-L-Spur wuerden keine zusaetzliche Gegenpruefung liefern.

## Intervention und Probe

Nach der achtsekundigen Formation werden S und H in allen Armen durch die
bereits gebundene externe Testintervention exakt auf denselben Zustand
gesetzt. L bleibt unveraendert. Danach erhalten alle Arme dieselbe Probe P.

Die Intervention ist keine Organismusfunktion. Weder R8, C8, B0, B1, B2 noch
P werden der Runtime als Rolle oder Label mitgeteilt.

## Vorregistrierte Skalare

Vor P:

```text
l_pair_b1 = ||L_R8_B1 - L_C8_B1||_inf
l_pair_b2 = ||L_R8_B2 - L_C8_B2||_inf
```

Unter P:

```text
d_pair_b0 = max_t max(||S_R8-S_C8||_inf, ||H_R8-H_C8||_inf)
d_pair_b1 = max_t max(||S_R8-S_C8||_inf, ||H_R8-H_C8||_inf)
d_pair_b2 = max_t max(||S_R8-S_C8||_inf, ||H_R8-H_C8||_inf)
```

Unabhaengige Referenzkontrolle:

```text
b2_reference_error = maximale S/H/L-Abweichung zwischen
                     Produktions-S1-B und unabhaengiger B2-Rechnung
                     an allen gebundenen Formations- und Probezeitpunkten
```

Zusaetzlich bleiben Quellen-, Plan-, Modell-, Probe- und Implementierungs-
digests, Supportzahlen, S/H-Angleichung, Endlichkeit und Reproduktion
Pflichtkontrollen.

## Toleranz

```text
digestgebundene Identitaet: exakt
lineare Referenzabweichung:  <= 2e-12
aufgeloeste Distanz:         > 2e-12
```

Die Toleranz stammt aus dem bestehenden S2-Vertrag und darf nach Einsicht in
W7-Ergebnisse nicht veraendert werden.

## Entscheidungen

### `STOP_TECHNICAL_INVALID`

Ein Digest, Budget, Support, S/H-Abgleich, Nullpfad, Reproduktions-,
Endlichkeits- oder Rohdatengrenze ist verletzt.

### `NO_R8_C8_EFFECT_IN_LINEAR_REFERENCE`

`l_pair_b2` oder `d_pair_b2` liegt nicht oberhalb `2e-12`. Dann ist das Paar
fuer die gebundene Frage nicht informativ.

### `REFERENCE_IMPLEMENTATION_MISMATCH`

`b2_reference_error > 2e-12`. Dann wird nichts funktional interpretiert.

### `LINEAR_RECIPROCAL_TRACE_SUFFICIENT`

Diese Entscheidung gilt nur, wenn:

1. `d_pair_b0 = 0` exakt;
2. B1 unterschiedliche L-Lagen bilden darf, aber `d_pair_b1 = 0` exakt;
3. `d_pair_b2 > 2e-12`;
4. `b2_reference_error <= 2e-12`;
5. alle technischen Kontrollen bestehen.

Sie bedeutet: Der R8/C8-Unterschied benoetigt L-nach-S-Rueckwirkung, ist aber
vollstaendig durch das feste lineare reziproke Zweizeitensystem erklaert.
Damit bleibt S1-B eine Referenzspur und kein eigenstaendiger Memorykandidat.

W7-A besitzt keine positive Entscheidung fuer Praegung, Memory,
Feldzeitverdichtung, Rekonstruktion, Organisation oder KI.

## Ausfuehrungssperre

W7-A gibt weder Browser- noch Welt- oder Forschungsausfuehrung frei. Vor
einer spaeteren Ausfuehrungsentscheidung muss W7-B:

1. B1 additiv an genau den vorhandenen S2-C11-R8/C8-Pfad anschliessen;
2. die unabhaengige B2-Referenzabweichung implementieren;
3. B0/B1/B2 auf genau dieselben vorbereiteten Sequenzen und Probe binden;
4. ein rein speicherinternes Skalarergebnis ohne Trajektorienpersistenz
   bereitstellen;
5. Fake-/Direktsequenztests fuer Nullpfad, Reproduktion und Modelltrennung
   bestehen.

Die S2-Vollmatrix, W6-I-Wiederholung und Lauf 197 bleiben gesperrt.

## Bester naechster Schritt

W7-B implementiert ausschliesslich den fehlenden B1-R8/C8-Adapter und die
unabhaengige B2-Referenzkontrolle in Memory. Es startet keinen Browser,
schreibt keinen Forschungsreport und veraendert den neutralen Standardpfad
nicht.
