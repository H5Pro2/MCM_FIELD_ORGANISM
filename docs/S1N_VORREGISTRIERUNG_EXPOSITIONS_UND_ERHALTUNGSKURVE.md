# S1-N: Vorregistrierung Expositions- und Erhaltungskurve

Stand: 2026-08-09

Vertragsstatus: `PREREGISTERED_NOT_IMPLEMENTED_NOT_EXECUTED`

Runtimeaenderung: nein

Forschungslauf: nein

## Ausgangspunkt

S1-M weist auf der aktuellen 26-Neuronen-AV-Geometrie eine reproduzierbare
technische Feldverlaufswirkung nach. Der vollstaendige Effektvektor wird im
geprueften Korridor mit 1.842 Prozent Rest durch die lineare gekoppelte
Feldbaseline erklaert.

S1-N sucht deshalb nicht nach neuer Physik. Der Vertrag charakterisiert die
bekannte transparente Engineeringfunktion entlang von Expositionsdosis,
Ereignissegmentierung und anschliessender Nullkontaktdauer.

## Forschungsfragen

1. Veraendert eine gemeinsame Erhoehung von Kontaktzahl und kumulierter
   Kontaktdauer die spaetere technische Feldwirkung abgestuft?
2. Nimmt diese Wirkung unter laengerem Nullkontakt geordnet ab?
3. Macht es bei gleicher kumulierter Kontaktdauer einen Unterschied, ob der
   Kontakt in mehrere 0.1-Sekunden-Supports oder einen zusammenhaengenden
   Support aufgeteilt wird?
4. Bleibt die gesamte Kurve durch die lineare gekoppelte F3-Baseline
   erklaert?

Die externen Sekundenwerte sind nur Kontrollen des Organismus-Takts. Sie
werden nicht als relative Feldzeit oder Feldzeitverdichtung interpretiert.

## Unveraenderte Mechanik

```text
Feldneuronen:                  26
auditive Feldneuronen:          8
visuelle Feldneuronen:         18
response_time_seconds:        1.0
afterimage_time_constant:     0.5
lambda_sm_per_second:         1.0
kappa:                        0.5
eta aktiver Arm:              1.0
initial_total_mass:           1.0
dissipation:                  keine
Hauptverfeinerung:            4
Konvergenzvergleich:          2 gegen 4
```

Feldgleichung, Rezeptorprojektion, Geometrie, Integrator und Parameter
bleiben unveraendert.

## Feste Expositionsquelle

Jeder aktive Support verwendet dieselbe bedeutungsfreie reduzierte
AV-Quelle:

```text
auditory[0] = 0.8
visual[5]   = 0.6
alle anderen Werte = 0.0
```

Die spaetere Probe P bleibt identisch zu S1-K:

```text
auditory[3] = 0.4
visual[8]   = 0.4
alle anderen Werte = 0.0
```

Es werden keine Objektklassen, Episoden-IDs, Bedeutungen oder Zielantworten
eingefuehrt.

## Expositionsdosen

```text
dose_count = 1, 2, 4, 8
support_duration = 0.1 s
cumulative_contact_duration = 0.1, 0.2, 0.4, 0.8 s
```

Die Dosisreihe veraendert Kontaktzahl und kumulierte Kontaktdauer gemeinsam.
Ein Dosisbefund darf deshalb nicht allein der Wiederholung zugeschrieben
werden.

## Segmentierungsgegenbaseline

Fuer jede Dosis werden zwei Quellenformen mit derselben Quelle und derselben
kumulierten Kontaktdauer verglichen:

| Quellenform | Beschreibung |
|---|---|
| `repeated-supports` | `n` aufeinanderfolgende Supports zu je 0.1 s |
| `continuous-support` | genau ein Support mit Dauer `n * 0.1 s` |

Die Gegenbaseline trennt die Wirkung mehrerer Abschlussereignisse von der
Wirkung derselben gesamten Kontaktdauer. Ereigniszahl bleibt dabei bewusst
verschieden und wird vollstaendig protokolliert.

## Nullkontaktdauern

Nach dem letzten aktiven Kontakt folgt eine der festen technischen
Nullkontaktdauern:

```text
0.0 s
0.2 s
0.8 s
1.6 s
```

Am Ende dieser Dauer werden S und H extern exakt auf den gemeinsamen
Nullzustand angeglichen. M bleibt unveraendert. Danach folgen der identische
Probe-P-Kontakt und ein 0.1-Sekunden-Nullsupport.

## Zeitlich angeglichene Nullreferenz

Jede exponierte Zelle besitzt eine frische Nullreferenz mit exakt demselben
externen Zeithorizont, denselben Probezeiten und derselben Feldgeometrie. In
der Nullreferenz werden alle Expositions- und Erhaltungssupports mit Wert 0.0
belegt.

Vor P muessen exponierter und nullreferenzierter Pfad in S und H exakt gleich
sein. Nur M darf verschieden sein.

## Modellarme

### Vollstaendige Matrix

F3 und die lineare gekoppelte Baseline durchlaufen die gesamte Matrix:

```text
4 Dosen * 2 Quellenformen * 4 Nullkontaktdauern
= 32 Zellen je Modell
```

F3 wird in jeder Zelle mit Verfeinerung 2 und 4 ausgefuehrt. Die lineare
Baseline verwendet Verfeinerung 4.

### Null- und Kausalkontrollen

P0 und `eta=0` werden fuer folgende Sentinelzellen gebunden:

- Dosis 1, `repeated-supports`, Nullkontakt 0.0 s;
- Dosis 8, `repeated-supports`, Nullkontakt 1.6 s;
- Dosis 8, `continuous-support`, Nullkontakt 0.0 s.

Eine uniforme M-Neutralisierung wird fuer F3 bei Dosis 8,
`repeated-supports`, Nullkontakt 0.0 und 1.6 s geprueft.

Alle Sentinelkontrollen muessen nach S/H-Angleichung in der Probe exakt
wirkungsgleich zu ihrer zeitlich angeglichenen Nullreferenz bleiben.

## Messrollen

Fuer Modell `X`, Dosis `n`, Quellenform `q`, Nullkontaktdauer `d` und
Probengrenze `t` gilt:

```text
E_X(n,q,d,t) = max(
  Linf(S_exposed(t) - S_zero(t)),
  Linf(H_exposed(t) - H_zero(t))
)
```

Ausgegeben werden:

- vollstaendiger S/H-Effektvektor ueber beide Probegrenzen;
- maximaler Effekt `E_X(n,q,d)`;
- M-Linf zwischen exponiertem und Nullpfad vor P;
- Gesamtmasse, minimale M-Masse und Feldgrenzen;
- 2/4-Verfeinerungsabweichung je F3-Zelle;
- relativer F3-Rest gegen die lineare Baseline je Zelle;
- Effektvektorrest zwischen `repeated-supports` und
  `continuous-support` gleicher Dosis und Nullkontaktdauer;
- Erhaltungshorizont je Dosis und Quellenform.

Der Erhaltungshorizont ist die groesste gebundene Nullkontaktdauer, bei der
der Effekt noch ueber dem zellbezogenen Nachweisboden liegt. Ein Effekt, der
bei 1.6 s noch besteht, wird als rechtszensiert protokolliert; eine laengere
Erhaltung wird nicht behauptet.

## Numerische Schwellen

Fuer jede F3-Zelle wird vor der Klassifikation gebildet:

```text
absolute_floor = 1e-12
convergence_floor(n,q,d) = 8 * Linf(effect_r4 - effect_r2)
detection_floor(n,q,d) = max(absolute_floor, convergence_floor)
linear_equivalence_limit = 0.05
mass_tolerance = 1e-12
```

Monotonievergleiche besitzen die groessere Nachweisgrenze der beiden
verglichenen Zellen als Toleranz. Ein streng groesserer oder kleinerer Wert
muss diese Toleranz ueberschreiten.

## Pflichtkontrollen

1. Alle aktiven Quellen besitzen die festgelegte Wertemultimenge pro Support.
2. Wiederholte und kontinuierliche Quelle besitzen je Dosis gleiche
   kumulierte Dauer und integrierte L1-/L2-Quelle.
3. Exponierter und zeitlich angeglichener Nullpfad besitzen vor P exakt
   gleiches S und H.
4. P0, `eta=0` und M-neutralisierte Sentinel bleiben exakt wirkungsnull.
5. Gesamtmasse bleibt innerhalb `1e-12` bei 1.0; M bleibt nichtnegativ.
6. Aktivierung und H bleiben im normierten Wertebereich.
7. Quellen- und Modelldigests bleiben ueber Wiederholungen gleich.
8. Kein Observerwert veraendert Quelle, Dauer, Arm oder Runtime.
9. Alle Zellmetriken sind endlich.

Eine Verletzung klassifiziert die gesamte Matrix als
`TECHNICALLY_INVALID`.

## Getrennte technische Klassifikationen

S1-N bindet keine einzige zusammengesetzte Erfolgsbehauptung. Nach bestandenen
Kontrollen werden vier getrennte Rollen ausgegeben.

### Dosisordnung

- `NO_DOSE_CONDITIONED_EFFECT`: Keine Dosis liegt ueber ihrem Nachweisboden.
- `MONOTONIC_DOSE_GRADATION`: Die Effekte bei Nullkontaktdauer 0.0 s sind
  innerhalb Toleranz nicht fallend und mindestens ein Schritt ist streng.
- `TECHNICAL_EFFECT_WITHOUT_DOSE_ORDER`: Effekte bestehen, aber die
  Dosisreihe ist nicht monoton.

### Abnahmeordnung

- `MONOTONIC_NULL_CONTACT_ATTENUATION`: Der Effekt steigt fuer keine Dosis
  mit laengerer Nullkontaktdauer ueber Toleranz an.
- `NONMONOTONIC_NULL_CONTACT_RESPONSE`: Mindestens eine Dosis steigt mit
  laengerem Nullkontakt ueber Toleranz an.
- `NO_DETECTABLE_PRESERVATION`: Bereits bei 0.0 s liegt kein Effekt ueber dem
  Nachweisboden.

### Segmentierung

- `DURATION_EQUIVALENT_WITHIN_FLOOR`: Wiederholte und kontinuierliche Quelle
  bleiben in allen Zellen innerhalb des Verfeinerungsbodens.
- `EVENT_SEGMENTATION_SENSITIVE`: Mindestens eine Zelle unterscheidet sich
  oberhalb des Verfeinerungsbodens.

### Mechanikerlaerung

- `CURVE_LINEARLY_EXPLAINED`: Jede gueltige F3-Zelle bleibt mit hoechstens
  5 Prozent relativem Effektvektorrest bei der linearen Baseline.
- `CURVE_CONTAINS_BASELINE_DIFFERENT_CELL`: Mindestens eine gueltige Zelle
  ueberschreitet 5 Prozent.

Eine baselineverschiedene Zelle waere kein Nachweis neuer Physik. Sie muesste
zuerst unabhaengig repliziert und gegen weitere enge Baselines geprueft
werden.

## Aussagegrenze

S1-N ist eine statische Vorregistrierung. Es wurde nichts implementiert und
nichts ausgefuehrt. Kein moeglicher Ausgang belegt:

- Praegung, Lernen, Vergessen oder Rekonstruktion;
- MCM-Memory oder organisches Memory;
- Clusterverdichtung oder Feldzeitverdichtung;
- relative Feldzeit, inneren Kontext oder Semantik;
- Organisation, Topologie, Selbstregulation oder KI.

Es bleiben ausschliesslich synthetische AV-Fakes erlaubt. Browser, Kamera,
Mikrofon, reale Sensorik, Forschungsrunner, Ergebnisreport und neue
Laufnummer bleiben gesperrt.

## Abgrenzung zu geschlossenen Arbeiten

S1-N wiederholt Lauf 194 nicht. Es prueft weder konkurrierende Verdraengung
noch natuerliche Wiederverwendung. Die Zweige 213ZZR bis 213ZZU, Z4, W1-O,
W1-Q und Lauf 197 bleiben unberuehrt.

## Bester naechster Schritt

S1-O implementiert nur den In-Memory-Quellen- und Matrixadapter mit
technischen Tests fuer Quellenmarginalien, Zeitangleichung, Zellinventar und
Nullkontrollen. Die vier S1-N-Klassifikationen werden in S1-O noch nicht
berechnet; Runner, Report und Laufnummer bleiben gesperrt.

## Spaeterer Umsetzungsstand S1-O

S1-O ist inzwischen im
[`In-Memory-Expositionsmatrixadapter`](S1O_IMPLEMENTIERUNG_IN_MEMORY_EXPOSITIONSMATRIXADAPTER.md)
umgesetzt. Das 32-Zellen-Inventar, exakte Dauer-/L1-/L2-Marginalien,
S/H-Angleichung, Massenbilanz und alle Sentinelnullen bestehen technisch mit
`74 passed` und 36 Subtests. Die Vollmatrix und ihre Klassifikationen bleiben
unausgefuehrt. Naechster Schritt ist der begrenzte S1-P-Kompositor.

## Spaetere Vollmatrixklassifikation S1-P

S1-P hat alle 32 Zellen mit bestandenen Kontrollen ausgewertet. Die vier
vorregistrierten Rollen lauten `MONOTONIC_DOSE_GRADATION`,
`NONMONOTONIC_NULL_CONTACT_RESPONSE`, `EVENT_SEGMENTATION_SENSITIVE` und
`CURVE_LINEARLY_EXPLAINED`. Die nichtmonotone Nullkontaktantwort sperrt eine
Interpretation als reine Erhaltungs- oder Vergessenskurve.
