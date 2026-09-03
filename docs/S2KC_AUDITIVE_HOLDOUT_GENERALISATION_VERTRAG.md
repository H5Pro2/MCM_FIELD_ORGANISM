# S2-KC - Auditive Holdout-Generalisation

## Status und Zweck

`S2KC_STATIC_FEASIBILITY_AND_FALSIFICATION_CONTRACT_COMPLETE`

S2-KC bindet einen endlichen prospektiven Versuch fuer die Frage:

> Kann variierte auditive Erfahrung einen stabilen Slow-Prototyp so
> verschieben, dass er eine nie trainierte PCM-Wahrnehmung erkennt, obwohl
> jedes gespeicherte Einzelbeispiel diese Wahrnehmung abweist?

Dieser Vertrag implementiert und startet nichts. Er aendert weder Rezeptor,
Memorykern, Schwelle, Kontext noch Feld. S2-KA bleibt als bestaetigter
visueller Lernbefund unveraendert.

## Gebundene Grundlage

Grundlage ist Commit `d28dc669dc36ec7170e6f5866a5632a8b706d2c9`.

| Quelle | SHA-256 |
| --- | --- |
| `log_spectral_receptor.py` | `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0` |
| `broadband_hearing_path.py` | `a20456b24c04d099ba5ee2da6250e3d83dc657392603c41d816b13ca68a37fb7` |
| PPB-1-Kern | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| TSPM-1-Kern | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| B4-Operator | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |
| Default-Live-Profilmodul | `ad5c8f607bc375daa8d407d4f53fd183cf61919cf0bd6e046c97cf7a976b287c` |
| AV-Paarung | `4ec7d8660bb2269f858db8a025749764b193cd3511934b9ae143bb07359958db` |
| 336-Werte-Koordinator | `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81` |
| Read-only-Adapter | `efd3dad03810811acc3fc124543bf8aa524ad1de4585210f2852f7048dbf93e7` |
| S2-KB-Runnerreferenz | `642f09ed0f391804991e38240b8e7c1819a3c8ca8a7e011253dc1b72b503dc6c` |
| S2-KB-Verifikatorreferenz | `87979f03a1985328c4710fa2d04de412f719fecbf5cdc474cc4cb61eaa405e3f` |

Unveraendert gelten 48 auditive und 288 visuelle Rezeptorwerte, die auditive
PPB-Schwelle `0,02`, PPB-Update `0,05`, Stabilitaet ab Support `3`, die
bestehenden Slotzahlen und alle Fast- und B4-Parameter.

## Reale PCM-Grenze

Jede auditive Rolle besteht aus genau einem kanonischen
`PCM_F32LE`-Fenster mit 4.800 Samples bei 48.000 Hz. Es wird in zehn
geordnete Hops zu je 480 Samples zerlegt und ausschliesslich durch
`BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))` reduziert.

Unzulaessig sind:

- handgeschriebene oder nach dem Rezeptor eingesetzte 48er-Vektoren;
- Resampling, Normalisierung, Clipping oder nachtraegliche
  Spektralbearbeitung;
- Auswahl anhand eines Memory-, Baseline- oder Auswertungsergebnisses;
- Training mit `H_AUDIO` oder `N_AUDIO`.

Rohsamples bleiben fluechtig. Ergebnis und Memory duerfen nur Payload-,
Rezeptorwerte-, Pairing- und Quelldigests enthalten.

## Prospektive PCM-Konstruktion

Die Fixture nutzt zwei vorab festgelegte, FFT-binzentrierte und weit
getrennte Basissignale:

```text
U[n] = sin(2*pi*100*n/48000),  n = 0..4799
V[n] = sin(2*pi*8000*n/48000), n = 0..4799
```

Die Sinuswerte werden in dieser Reihenfolge genau einmal auf IEEE-754
binary32 kanonisiert. Beide Basen besitzen damit exakt 4.800
`PCM_F32LE`-Samples, Phase 0 und einen separat gebundenen PCM-Digest. Ihre
gewichteten FFT-Traeger muessen im unveraenderten Filterbankrezeptor
disjunkte Kanalunterstuetzungen besitzen. Andernfalls stoppt S2-KC vor jeder
Memoryoperation.

Aus den realen Rezeptorausgaben der beiden Einheitsbasen werden

```text
mU = mean_l1(R(U), 0)
mV = mean_l1(R(V), 0)
```

gebildet. Daraus werden vorab die float32-Koeffizienten fuer folgende
Zielbeitraege abgeleitet:

```text
gemeinsamer U-Beitrag c = 0,0165
H_AUDIO-V-Beitrag     h = 0,0100
gegenlaeufiger V-Teil b = 0,0050

H_AUDIO =             h * V
T_PLUS  = c * U + (h + b) * V
T_MINUS = c * U + (h - b) * V
N_AUDIO =             0 * U + 0 * V
```

Die Koeffizienten werden einmal auf `float32` kanonisiert. Jeder erzeugte
Samplewert muss endlich und in `[-1,1]` liegen. Die PCM-Bytes und ihre
Digests werden vor dem ersten Memoryaufruf versiegelt. Eine abweichende
Kanalunterstuetzung, Koeffizientengeometrie oder Samplegrenze darf nicht
durch Suche nach anderen Schwellen repariert werden.

Unter der zwingend zu bestaetigenden disjunkten positiven Homogenitaet gilt
prospektiv:

```text
d(T_PLUS,T_MINUS) = 2b = 0,0100 <= 0,02
d(H_AUDIO,T_PLUS) = c+b = 0,0215 > 0,02
d(H_AUDIO,T_MINUS)= c+b = 0,0215 > 0,02
```

Der erste Slow-Prototyp entsteht bei der zweiten `T_PLUS`-Exposition. Nach
sechs `T_MINUS`-Updates mit Rate `0,05` ist der verbleibende gerichtete
V-Anteil

```text
q = 2 * 0,95^6 - 1 = 0,47018378125
d(H_AUDIO,P_adaptiv)
  = c + q*b
  = 0,01885091890625 <= 0,02
```

Der Nullholdout bleibt getrennt:

```text
d(N_AUDIO,T_MINUS)   = c+h-b   = 0,0215 > 0,02
d(N_AUDIO,T_PLUS)    = c+h+b   = 0,0315 > 0,02
d(N_AUDIO,P_adaptiv) = c+h+q*b = 0,02885091890625 > 0,02
```

Diese Werte sind Zielinvarianten der PCM-Konstruktion, keine
handgeschriebenen Rezeptorwerte. Vor Memorybeginn muessen alle Distanzen aus
den tatsaechlich erzeugten 48er-Rezeptorausgaben neu berechnet werden. Es
gelten zusaetzlich Sicherheitsintervalle:

```text
0,0205 <= d(H_AUDIO,T_PLUS/T_MINUS) <= 0,0225
d(T_PLUS,T_MINUS) <= 0,0120
d(H_AUDIO,P_adaptiv) <= 0,0195
d(N_AUDIO,T_PLUS/T_MINUS/P_adaptiv) >= 0,0205
```

Wird auch nur eine Grenze verfehlt, lautet der Abschluss
`S2KC_AUDIO_GEOMETRY_NOT_MATERIALIZABLE`. Es entsteht kein Memorylauf. Eine
andere PCM-Fixture benoetigt einen neuen prospektiven Vertrag.

## Visuelle Kontrolle

`T_PLUS`, `T_MINUS`, `H_AUDIO` und `N_AUDIO` erhalten bitidentisch dasselbe
reale `1920x1080 RGB8`-Bild und damit denselben 288-Werte-Rezeptorzustand.
Kein visueller Unterschied kann die auditive Entscheidung uebernehmen.

Durch die Wiederholungen entsteht erwartbar auch ein stabiler visueller
Slow-Prototyp. Er ist fuer `H_AUDIO` und `N_AUDIO` identisch und damit nur
eine nicht diskriminierende Kontrolle. Der Lernclaim wird ausschliesslich
aus dem getrennten auditiven `B_STABLE`-Befund abgeleitet. Es wird keine
automatische audiovisuelle Gesamtentscheidung erzeugt.

D1 bis D9 verwenden die bereits qualifizierten realen S2-KB-Distraktor-
Frames und PCM-Fenster. Vor Memorybeginn ist erneut zu bestaetigen, dass sie
den Ziel-Fast-Slot verdraengen und auditiv keinen Ziel-Slow-Prototyp
aktualisieren.

## Formation und Proben

Die S2-KB-Topologie bleibt unveraendert:

```text
Formation:
T_PLUS, T_PLUS,
T_MINUS, T_MINUS, T_MINUS, T_MINUS, T_MINUS, T_MINUS,
D1, D2, D3, D4, D5, D6, D7, D8, D9

Read-only an C0/C1/C2/C3 jeweils:
H_AUDIO, N_AUDIO
```

| Checkpoint | Erwartung fuer die auditive Bank |
| --- | --- |
| `C0` vor Formation | kein Treffer |
| `C1` nach einer Exposition | kein Slow-Prototyp |
| `C2` nach acht Expositionen | `H_AUDIO` stabiler Slow-Treffer, Support `3`; `N_AUDIO` kein Slow-Treffer |
| `C3` nach D1 bis D9 | weder Holdout in B4/Fast; nur `H_AUDIO` auditiv stabil, `N_AUDIO` auditiv abgewiesen |

Alle Quellenfenster sind strikt geordnet. Probequellen sind neue Bloecke mit
neuen Quellen-, Pairing-, Fixture- und Probe-Digests. Jeder Probezugriff
muss identische Memory-Vor- und Nachzustandsdigests besitzen.

## Unabhaengige Baselines

Die drei Baselines konsumieren nur die bereits erzeugten auditiven
Rezeptorwerte und besitzen getrennte unveraenderliche Zustaende:

1. `FROZEN_FIRST`: erster bei Formation 2 erzeugter `T_PLUS`-Prototyp;
2. `REPLAY_NEAREST`: naechstes tatsaechliches Trainingsbeispiel;
3. `ADAPTIVE_PROTOTYPE`: gleiche sechs Updates mit Rate `0,05`, aber ohne
   Aufruf von PPB-1 oder TSPM-1.

`H_AUDIO` und `N_AUDIO` duerfen in keinem Baselinetraining vorkommen. Final
muessen Frozen und Replay `H_AUDIO` abweisen, waehrend der adaptive Prototyp
`H_AUDIO` annehmen darf. Alle drei Baselines muessen `N_AUDIO` abweisen.
Sollstatus und Rollenbedeutung gelangen erst zum getrennten Auswerter.

## Wiederverwendung und Budgets

Wiederverwendet werden S2-KB-Gate, Operationskette, atomare einzelne
Ergebnisdatei, Offline-Verifikation und die Topologie der getrennten
Memory-/Baselinebefunde. Auditive Fixture-, Mess- und Auswertungsregeln
werden privat neu gebunden; die visuelle S2-KA-Auswertung wird nicht
umgedeutet.

| Grenze | Wert |
| --- | ---: |
| Formationen | 17 |
| read-only Proben | 8 |
| funktionale Top-Level-Operationen | 157 |
| Memoryoperationen | 100 |
| Baselineoperationen | 31 |
| Hauptlauf-Rezeptoranalysen | 25 visuell, 250 Audiohops |
| Hauptlauf-Rohbytes | 156.000.000 |
| Vorabmaterialisierung | 13 visuell, 130 Audiohops, 81.120.000 Rohbytes |
| Memory-L1-Obergrenze | 133.344 Terme |
| gesamte L1-Obergrenze | 156.864 Terme |

Vorabmaterialisierung und spaeterer Funktionslauf bleiben getrennte
Ressourcenrollen. Rohpayloads werden einzeln gestreamt und nach der
Rezeptorreduktion verworfen.

## Erfolg, Falsifikation und Stopp

`S2KC_AUDITORY_HOLDOUT_GENERALIZATION_CONFIRMED` ist nur zulaessig, wenn:

- die reale PCM-/Rezeptorgeometrie vor dem ersten Memoryaufruf alle Grenzen
  erfuellt;
- `H_AUDIO` und `N_AUDIO` in keinem Formation- oder Baselinetrainingspfad
  erscheinen;
- nach D1 bis D9 fuer beide Holdouts weder B4 noch Fast einen Treffer liefert;
- ausschliesslich `H_AUDIO` in der auditiven Slow-Bank mit Support `3`
  erkannt wird;
- Frozen und Replay `H_AUDIO` abweisen, die adaptive Baseline es annimmt;
- alle auditiven Memory- und Baselinebefunde bei `N_AUDIO` negativ bleiben;
- alle Proben read-only sind und die Aufzeichnung vollstaendig verifiziert
  wird.

Ein vollstaendiger, technisch gueltiger Lauf mit abweichender Funktion endet
als `S2KC_AUDITORY_HOLDOUT_GENERALIZATION_FALSIFIED`. Er darf weder als
Infrastrukturfehler umgedeutet noch mit geaenderten Schwellen wiederholt
werden.

`NOT_EVALUABLE` bleibt auf Quellen-, Reihenfolge-, Owner-, Digest-,
Receipt-, Ledger-, Read-only- oder Aufzeichnungsbruch begrenzt. Eine nicht
materialisierbare PCM-Geometrie stoppt bereits vor dem Lauf mit
`S2KC_AUDIO_GEOMETRY_NOT_MATERIALIZABLE`.

## Aussagegrenze

Ein positives Ergebnis belegt begrenzte auditive erfahrungsabhaengige
Generalisation einer nie trainierten PCM-Wahrnehmung. Die adaptive
Prototypbank darf den Mechanismus vollstaendig erklaeren. Nicht belegt waeren
Semantik, Kategorien, allgemeines audiovisuelles Lernen, Kontextwahl oder
MCM-spezifische Physik.

Der naechste Schritt ist unmittelbar eine kleine private PCM-Fixture- und
Messimplementierung mit neutraler Qualifikation. Eine weitere allgemeine
Vertrags- oder Infrastrukturkaskade ist nicht erforderlich.
