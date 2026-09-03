# S2-KD - Auditive PCM-Koeffizienten und Messgrenze

## Status und Geltung

`S2KD_STATIC_NARROW_CORRECTION_COMPLETE`

S2-KD korrigiert ausschliesslich die PCM-Koeffizienten- und
Unterstuetzungsbindung von S2-KC. Grundlage ist der unveraenderte Vertrag
`S2KC_AUDITIVE_HOLDOUT_GENERALISATION_VERTRAG.md` mit SHA-256
`497469d40b0e9eea05ea78fe8582a29cde5cbda7923277b2d81974828c718e38`.

Normativ ersetzt S2-KD in S2-KC:

1. die direkte Verwendung der Rezeptorbeitraege `c`, `h` und `b` als
   PCM-Koeffizienten;
2. die Forderung nach exakt disjunkten Rezeptorkanalunterstuetzungen;
3. die daraus abgeleiteten exakten Distanzgleichungen als Startbeweis.

Alle anderen S2-KC-Bindungen bleiben unveraendert, insbesondere Schwelle
`0,02`, Formation und Proben, Holdout-Ausschluss, Baselines, Read-only-
Regeln, Stoppstatus und Umfang `17/8/157`.

Dieser Vertrag implementiert oder startet nichts.

## Feste Basen und Zahlenformate

Die beiden S2-KC-Basissignale bleiben unveraendert:

```text
U[n] = sin(2*pi*100*n/48000),  n = 0..4799
V[n] = sin(2*pi*8000*n/48000), n = 0..4799
```

Fuer jede Basis gilt genau diese Bildung:

1. `n`, Frequenz und Samplefrequenz werden als die oben gebundenen Integer
   verwendet.
2. Der Sinus wird mit der vorab digestgebundenen CPython-/libm-/NumPy-
   Runtime in binary64 berechnet.
3. Jeder einzelne Sinuswert wird sofort mit
   `unpack('<f', pack('<f', value))[0]` auf IEEE-754 binary32 kanonisiert.
4. Genau diese 4.800 Werte werden little-endian als `PCM_F32LE` serialisiert
   und digestgebunden.
5. Jede Basis wird in einem frischen unveraenderten
   `BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))` ueber
   zehn Hops analysiert.

Runtime-, Modul-, Konfigurations-, PCM- und Rezeptorwertedigests muessen vor
jeder weiteren Ableitung feststehen. Eine andere Runtime oder
Auswertungsreihenfolge ist keine gleichwertige Fixture.

## Einmalige Normableitung

Aus den tatsaechlichen 48-Werte-Abschluessen der beiden Einheitsbasen werden
einmalig in binary64 berechnet:

```text
zero48 = (0.0, ..., 0.0)
mU = normalized_mean_l1_distance(R(U), zero48)
mV = normalized_mean_l1_distance(R(V), zero48)
```

`mU` und `mV` muessen endlich und strikt positiv sein. Sie werden mit ihren
48er-Quelldigests in einem unveraenderlichen `BasisNormBindingV1` gebunden.
Es gibt keine zweite Normmessung und keine Auswahl zwischen mehreren Basen.

Die gewuenschten Rezeptorbeitraege bleiben die exakten rationalen
Vertragswerte:

```text
c = 33/2000 = 0,0165
h =  1/100  = 0,0100
b =  1/200  = 0,0050
```

Sie sind keine PCM-Koeffizienten. Die PCM-Koeffizienten werden genau einmal
in folgender Reihenfolge abgeleitet:

```text
f32(x) = unpack('<f', pack('<f', x))[0]

c64 = binary64(33.0 / 2000.0)
h64 = binary64( 1.0 /  100.0)
b64 = binary64( 1.0 /  200.0)

alpha_U  = f32(binary64(c64 / mU))
alpha_HV = f32(binary64(h64 / mV))
alpha_BV = f32(binary64(b64 / mV))

alpha_PLUS_V  = f32(binary64(alpha_HV + alpha_BV))
alpha_MINUS_V = f32(binary64(alpha_HV - alpha_BV))
```

Alle Zwischenwerte, ihre binary64-Bitformen und die fuenf resultierenden
binary32-Bitformen werden gebunden. Erforderlich ist:

```text
alpha_U > 0
alpha_HV > alpha_BV > 0
alpha_PLUS_V > alpha_HV > alpha_MINUS_V > 0
```

Ein nicht endlicher, nicht positiver oder falsch geordneter Wert stoppt mit
`S2KC_AUDIO_GEOMETRY_NOT_MATERIALIZABLE`.

## Exakte Samplebildungsreihenfolge

Fuer jedes `n = 0..4799` werden ausschliesslich die bereits kanonisierten
`U32[n]` und `V32[n]` verwendet:

```text
u_term[n]       = f32(binary64(alpha_U       * U32[n]))
h_term[n]       = f32(binary64(alpha_HV      * V32[n]))
plus_v_term[n]  = f32(binary64(alpha_PLUS_V  * V32[n]))
minus_v_term[n] = f32(binary64(alpha_MINUS_V * V32[n]))

H_AUDIO[n] = h_term[n]
T_PLUS[n]  = f32(binary64(u_term[n] + plus_v_term[n]))
T_MINUS[n] = f32(binary64(u_term[n] + minus_v_term[n]))
N_AUDIO[n] = f32(0.0)
```

Es gibt kein FMA, keine alternative Klammerung, kein Zwischenrunden auf ein
anderes Format, kein Clipping und keine Normalisierung. Vor der
Serialisierung muss jeder Wert endlich und innerhalb `[-1.0,1.0]` liegen.
Die vier resultierenden PCM-Payloads werden genau einmal serialisiert und
digestgebunden.

Eine Grenzverletzung fuehrt unmittelbar zu
`S2KC_AUDIO_GEOMETRY_NOT_MATERIALIZABLE`. Koeffizienten, Frequenzen,
Phasen oder Zielbeitraege duerfen danach nicht iterativ angepasst werden.

## Hann- und Filterbankueberlappung

S2-KD behauptet keine exakt disjunkte Rezeptorunterstuetzung. Das
Hann-Fenster, die FFT-Betragsbildung und die dreieckigen Filterbankgewichte
duerfen in beiden Basen numerisch kleine Beitraege ausserhalb ihrer
Hauptbaender erzeugen.

Fuer jeden der 48 Kanaele werden vor Memorybeginn rein diagnostisch
aufgezeichnet:

- `R(U)[i]` und `R(V)[i]`;
- die jeweilige Hauptbandzuordnung;
- Kanaele, auf denen beide Werte ungleich null sind;
- Summe und Maximum der ausserhalb der Hauptbaender liegenden Energien;
- paarweiser L1-Ueberlappungsbeitrag.

Diese Werte duerfen weder Koeffizienten aendern noch eine Toleranz oder
einen neuen Matchweg erzeugen. Es gibt keine Nullheitsforderung und keinen
Ausweichpfad bei Ueberlappung.

## Verbindliches reales Startgate

Nach der einmaligen Samplebildung werden `T_PLUS`, `T_MINUS`, `H_AUDIO` und
`N_AUDIO` jeweils in einem frischen Rezeptorpfad materialisiert. Der
adaptive Referenzprototyp wird ausschliesslich aus den tatsaechlichen
48-Werte-Vektoren und mit der bestehenden PPB-1-Ausdrucksreihenfolge
gebildet:

```text
P0 = R(T_PLUS)
Pk[i] = (1.0 - 0.05) * P(k-1)[i] + 0.05 * R(T_MINUS)[i]
k = 1..6, i = 0..47
```

Die beiden Multiplikationen, deren anschliessende Addition und die
Carrierreihenfolge entsprechen exakt
`mcm_field_organism/_ppb1_reference.py`. Es erfolgt keine zusaetzliche
binary32-Rundung im Prototyp. Die entstehenden Prototyp- und Distanzdigests
werden vor dem ersten Memoryaufruf versiegelt.

Nur die direkt gemessenen Werte entscheiden das Startgate:

```text
0,0205 <= d(R(H_AUDIO), R(T_PLUS))  <= 0,0225
0,0205 <= d(R(H_AUDIO), R(T_MINUS)) <= 0,0225
d(R(T_PLUS), R(T_MINUS)) <= 0,0120
d(R(H_AUDIO), P6) <= 0,0195

d(R(N_AUDIO), R(T_PLUS))  >= 0,0205
d(R(N_AUDIO), R(T_MINUS)) >= 0,0205
d(R(N_AUDIO), P6)         >= 0,0205
```

Zusaetzlich muessen alle sechs Aktualisierungen `R(T_MINUS)` gegen ihren
jeweiligen Prototypvorzustand innerhalb der unveraenderten auditiven
Schwelle `0,02` liegen. Alle D1-D9-Abstaende und die getrennte
Fast-/Slow-Zuordnung werden wie in S2-KC vorab validiert.

Die idealisierten S2-KC-Werte `0,0215`, `0,0100` und
`0,01885091890625` bleiben lediglich analytische Konstruktionsziele. Sie
sind weder Ersatz fuer gemessene Rezeptorausgaben noch Abnahmetoleranz.

Verfehlt eine reale Distanz, ein Aktualisierungsschritt oder ein Sample die
gebundene Grenze, endet die Materialisierung vor dem ersten Memoryaufruf als
`S2KC_AUDIO_GEOMETRY_NOT_MATERIALIZABLE`. Es gibt keine iterative Suche,
keinen zweiten Koeffizientensatz und keine Schwellenanpassung.

## Unveraenderte Versuchsgrenze

Unveraendert bleiben:

- `H_AUDIO` und `N_AUDIO` vollstaendig ausserhalb aller Formation- und
  Baselinetrainingspfade;
- identische visuelle Begleitung fuer Training und beide Holdouts;
- 17 Formationen, acht read-only Proben und 157 funktionale Operationen;
- Frozen-, Replay- und adaptive Prototypbaseline als getrennte Arme;
- ausschliesslich der auditive Slow-Befund als Generalisationsentscheidung;
- keine Memory-, Kontext-, Feld-, API- oder Schwellenaenderung.

Nach bestandenem Startgate darf unmittelbar die private Materialisierung
und neutrale Qualifikation folgen. Eine weitere allgemeine Vertragsstufe ist
nicht erforderlich.
