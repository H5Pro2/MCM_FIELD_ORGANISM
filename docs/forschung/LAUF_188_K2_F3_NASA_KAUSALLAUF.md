# Lauf 188

## Forschungsfrage und Vorregistrierung

Geprueft wurde unter der vorab gebundenen NASA-Audio-Video-Folge, ob die
aktive K2/F3-Kopplung eine kausal getrennte M-Umverteilung, eine an `eta`
gebundene S/H-Rueckwirkung und eine abnehmende n/2n/4n-Abweichung erzeugt.

Verbindliche Vorregistrierung:

- `docs/K2_F3_ERSTER_NASA_KAUSALLAUF_VORREGISTRIERUNG.md`
- Intervall `[0, 500000000)` auf `public.media.pts_ns`;
- `lambda_sm = 1.0`, `kappa = 0.5`, `eta = 1.0`;
- keine Dissipation;
- P0, P1 n/2n/4n, eta-null, kappa-null und kappa-invertiert;
- keine ergebnisabhaengige Parameterkorrektur oder Wiederholung.

## Verwendete Quelle und Eingangspruefung

```text
source_id: public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20
auditory frames: 41
visual frames: 15
source supports: 56
proposal steps: 55
receptor reduction repeatable: true
```

Groesse, SHA-1, Rezeptordigests und Framezahlen entsprachen der
Vorregistrierung. Kamera, Live-Mikrofon, Netzwerk und physische Sensorik
wurden nicht verwendet. Rohsamples und Pixel wurden nicht im Ergebnis
gespeichert.

## Beobachtete Messung

Aktiver P1-Arm bei 4n:

```text
M Linf gegen gleichfoermigen Start: 1.0564203236067098e-05
M L2 gegen gleichfoermigen Start:   5.438111955971377e-05
P1 vs P0 S Linf:                    7.6464396306479e-06
P1 vs P0 H Linf:                    1.2343011256774755e-06
P1 vs eta-null S Linf:              7.646388394923903e-06
P1 vs eta-null H Linf:              1.234380122933261e-06
P1 vs kappa-null M Linf:            1.0564203236067098e-05
P1 vs kappa-invertiert M Linf:      2.1127133020970666e-05
```

`kappa-null` blieb exakt in der gleichfoermigen M-Verteilung. Die
Vorzeicheninversion erzeugte einen getrennten M-Endzustand.

Zeitverfeinerung des vollstaendigen S/H/M-Zustands:

```text
n zu 2n L2:  3.437008637419801e-08
2n zu 4n L2: 4.2090677451738585e-09
Quotient:    0.1224631122
Abnahme:     true
```

Invarianten:

```text
groesster M-Gesamtmassenfehler: 9.547918011776346e-15
kleinstes M aller aktiven Arme: 0.0034616592924373185
erlaubter M-Fehler:             1e-12
negative M-Werte:               keine
S/H-Bereichsverletzung:         keine
```

## Technische Interpretation

Unter genau dieser kontrollierten AV-Folge ist die implementierte
K2/F3-Kausalstruktur technisch wirksam:

1. Die weltbedingte S-Inhomogenitaet fuehrt bei aktivem `kappa` aus dem
   gleichfoermigen M-Start zu konservativer M-Umverteilung.
2. `kappa = 0` entfernt diese gerichtete Umverteilung unter dem
   gleichfoermigen Start exakt.
3. Das invertierte `kappa` trennt die Transportrichtung wie vorregistriert.
4. Die S/H-Differenz zwischen P1 und eta-null ist mit der an denselben
   M-Fluss gebundenen Rueckarbeit vereinbar.
5. Die feinere Verfeinerungsabweichung ist rund achtmal kleiner als die
   groebere. Der beobachtete P1/eta-null-S-Kontrast liegt zudem weit ueber der
   P1-2n/4n-Gesamtzustandsabweichung.

Damit ist die erste technische Voraussetzung fuer eine spaetere
Feld-Substrat-Geschichtspruefung vorhanden. Der Befund ist auf diese
Kandidatenform, Parameter und AV-Folge begrenzt.

## Nichtnachweise und offene Grenzen

- Es wurde nur ein frischer 0,5-Sekunden-Kontakt untersucht.
- Es gab keine getrennten Vorgeschichten und keinen identischen spaeteren
  Holdout.
- Persistenz, funktionale Loesung, Neutralisierung und Wiederpraegung wurden
  nicht untersucht.
- Enge klassische Vergleichsformen ausser den ausgefuehrten Ablationen sind
  noch offen.
- Es gibt keinen Nachweis von Feldzeitverdichtung, innerem Kontext,
  MCM-Memory, Organisation, Topologie, Semantik oder KI.

## Ergebnisartefakt

```text
reports/mcm_f3_nasa_causal_lauf_188.json
```

Der Einmal-Runner verweigert eine zweite Ausfuehrung, solange dieses Artefakt
vorhanden ist.

## Bester naechster Schritt

Als naechstes wird ein P2-Geschichtsvertrag formuliert. Zwei kontrollierte,
unterschiedliche AV-Vorgeschichten muessen in getrennten frischen P1-Feldern
M entwickeln. Danach erhalten beide Arme exakt dieselbe einmal reduzierte
Holdoutfolge. P0, M-Neutralisierung, M-Tausch und eta-null muessen vorab
gebunden werden. Erst dieser Schritt kann untersuchen, ob die entstandene
M-Verteilung einen spaeteren identischen Weltkontakt kausal veraendert.
