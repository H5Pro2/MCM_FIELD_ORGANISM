# S1-Q: Vorregistrierung Phasentrennung Feldverlauf

Stand: 2026-08-09

Vertragsstatus: `PREREGISTERED_NOT_IMPLEMENTED_NOT_EXECUTED`

Runtimeaenderung: nein

Forschungslauf: nein

## Ausgangspunkt

S1-P zeigt eine technisch nachweisbare, aber nichtmonotone Antwort auf die
gebundene Nullkontaktdauer. Deshalb darf die bisherige Kurve weder als reine
Erhaltung noch als Abschwaechung oder Vergessen gelesen werden.

S1-Q prueft enger, ob der Verlauf mit zwei zeitlich getrennten technischen
Phasen vereinbar ist: einer fruehen Aenderung der internen M-Lage nach Ende
des Aussenkontakts und einer spaeteren Aenderung dieser Lage. Die Phasengrenze
wird vor Implementierung und Ergebnissicht festgelegt.

## Forschungsfrage

Laesst sich die nichtmonotone S1-P-Antwort bei festen fruehen Messgrenzen in
eine fruehe Bildungsantwort und eine davon getrennte spaetere
Abschwaechungsantwort zerlegen, und bleiben beide durch die lineare gekoppelte
F3-Baseline erklaert?

Dies ist eine technische Ursachenfrage. Selbst ein positiver Ausgang belegt
keine Feldzeit, Praegung, Konsolidierung, Erhaltung oder Memory.

## Unveraenderte Mechanik

Feldgleichung, 26-Neuronen-Geometrie, Rezeptorprojektion, Probe P,
Integrator, Parameter, S/H-Angleichung und Nullreferenz bleiben identisch zu
S1-N bis S1-P. F3 wird mit Verfeinerung 2 und 4 berechnet; die lineare
gekoppelte Baseline mit Verfeinerung 4.

Es werden keine zusaetzlichen Zustandsrollen, Lernregeln, Schwellen in der
Runtime oder Rueckschreibungen eingefuehrt.

## Gebundene Teilmatrix

S1-Q verwendet ausschliesslich die beiden Randdosen und beide bereits
kontrollierten Quellenformen:

```text
dose_count = 1, 8
source_form = repeated-supports, continuous-support
```

Die festen Nullkontaktgrenzen lauten:

```text
0.000 s
0.025 s
0.050 s
0.100 s
0.200 s
0.400 s
0.800 s
1.600 s
```

Damit entstehen 32 Zellen je Modellarm. Die externen Sekunden sind nur
Takt- und Vergleichsgrenzen, keine interne Feldzeit.

Nullkontakt wird in Supports von hoechstens 0.100 Sekunden zerlegt. Ist die
gesamte Grenze kuerzer, besteht sie aus genau einem Support; andernfalls ist
nur der letzte Support gegebenenfalls kuerzer. Damit bleiben 0.200, 0.800
und 1.600 Sekunden ereignisgleich zum bestehenden S1-P-Pfad, waehrend die
neuen Grenzen exakt erreichbar sind.

## Vorab gebundene Phasen

Die Phasengrenze liegt fest bei 0.200 Sekunden:

```text
fruehes Fenster: 0.000 bis 0.200 s
spaetes Fenster: 0.200 bis 1.600 s
```

Sie wird nach Kenntnis der Ergebnisse weder verschoben noch durch eine
geschaetzte Peakzeit ersetzt. Es wird kein Kurvenmaximum als neue Grenze
ausgewaehlt. Die Einzelwerte bleiben vollstaendig sichtbar.

## Messrollen

Je Zelle werden getrennt ausgegeben:

- der vollstaendige Vorproben-M-Differenzvektor gegen die zeitgleiche
  Nullreferenz;
- dessen `Linf`-Norm `M_pre(d)`;
- der vollstaendige spaetere S/H-Probeeffektvektor;
- dessen `Linf`-Norm `E_probe(d)`;
- die F3-Abweichung zwischen Verfeinerung 2 und 4;
- der relative Effektvektorrest gegen die lineare gekoppelte Baseline;
- Gesamtmasse, minimale M-Masse und S/H-Angleichung vor P.

Vorproben-M- und Probeeffektvektor erhalten getrennte zellbezogene
Nachweisboeden:

```text
m_detection_floor = max(1e-12, 8 * M_vector_refinement_2_4_linf)
probe_detection_floor = max(1e-12, 8 * probe_vector_refinement_2_4_linf)
linear_equivalence_limit = 0.05
```

Fuer einen Paarvergleich gilt die groessere Nachweisgrenze beider Zellen als
Toleranz. Vorproben-M und Probeeffekt werden getrennt klassifiziert. Auch der
relative lineare Vektorrest wird fuer beide Rollen separat berechnet; die
Mechanikrolle verwendet den groesseren Rest aller jeweils nachweisbaren
M- und Probevektoren.

## Pflichtkontrollen und Gegenbaselines

1. Quellenwerte, Gesamtdauer und integrierte L1-/L2-Marginalien bleiben
   unveraendert zu S1-N.
2. Exponierter Pfad und Nullreferenz besitzen vor P exakt gleiches S und H.
3. P0 und `eta=0` bleiben fuer `repeated-supports` an Dosis 1 und 8 bei
   0.000, 0.200 und 1.600 Sekunden wirkungsnull.
4. Externe uniforme M-Neutralisierung bleibt an denselben sechs
   `repeated-supports`-Rand-/Grenzzellen wirkungsnull.
5. Gesamtmasse bleibt innerhalb `1e-12` bei 1.0; M bleibt nichtnegativ.
6. Eine lange Randzelle wird exakt wiederholt.
7. Alle 32 F3-Zellen besitzen einen eigenen 2/4-Konvergenzboden.
8. Jede nachweisbare F3-Zelle wird gegen die lineare gekoppelte Baseline
   geprueft.
9. Kein Observerwert darf Quelle, Grenze, Modellarm oder Runtime veraendern.

Eine verletzte Pflichtkontrolle klassifiziert S1-Q insgesamt als
`TECHNICALLY_INVALID`.

## Vorregistrierte Fensterklassifikation

Fuer `M_pre` und `E_probe` wird jedes Fenster separat klassifiziert:

- `WINDOW_INCREASE`: kein toleranzueberschreitender Abfall und mindestens
  ein toleranzueberschreitender Anstieg;
- `WINDOW_DECREASE`: kein toleranzueberschreitender Anstieg und mindestens
  ein toleranzueberschreitender Abfall;
- `WINDOW_STABLE_WITHIN_FLOOR`: weder Anstieg noch Abfall oberhalb der
  Paartoleranz;
- `WINDOW_MIXED`: mindestens ein Anstieg und ein Abfall oberhalb der
  Paartoleranz.

Diese Rollen werden fuer jede der vier Dosis-/Quellenform-Kurven ausgegeben.

## Technische Hauptklassifikation

- `NO_EARLY_FORMATION_AT_FIXED_BOUNDARY`: Keine `M_pre`-Kurve zeigt im
  fruehen Fenster einen toleranzueberschreitenden Anstieg.
- `FORMATION_EXTENDS_BEYOND_FIXED_BOUNDARY`: Mindestens eine `M_pre`-Kurve
  zeigt im spaeten Fenster einen toleranzueberschreitenden Anstieg.
- `FIXED_BOUNDARY_FORMATION_THEN_ATTENUATION`: Bei allen vier Kurven zeigt
  `M_pre` im fruehen Fenster `WINDOW_INCREASE` und im spaeten Fenster
  `WINDOW_DECREASE`; `E_probe` widerspricht dieser Reihenfolge in keiner
  Kurve durch die umgekehrte reine Fensterordnung.
- `MIXED_PHASE_RESPONSE`: Die Kontrollen bestehen, aber keine der drei
  engeren Rollen trifft zu.

Die Reihenfolge ist bindend: zuerst fehlende fruehe Bildung, danach Bildung
jenseits der Grenze, danach die vollstaendige Trennung; alle restlichen
gueltigen Muster sind gemischt. Dadurch gibt es keine nachtraegliche
Erfolgsauswahl.

Die Mechanikrolle bleibt separat:

- `PHASE_CURVES_LINEARLY_EXPLAINED`: Alle nachweisbaren Zellen bleiben bei
  hoechstens 5 Prozent relativem Effektvektorrest.
- `PHASE_CURVE_CONTAINS_BASELINE_DIFFERENT_CELL`: Mindestens eine
  nachweisbare Zelle ueberschreitet 5 Prozent.

## Interpretationsgrenze

Eine feste technische Phasentrennung waere nur mit einer internen
Zustandsentwicklung nach Kontaktende vereinbar. Sie waere kein Nachweis von
Vergessen, Konsolidierung, Feldzeitverdichtung oder Memory. Eine lineare
Erklaerung wuerde weiterhin bedeuten, dass dafuer im geprueften Korridor
keine neue Feldphysik benoetigt wird.

Keine Klassifikation erlaubt Aussagen ueber Semantik, inneren Kontext,
Organisation, Topologie, Selbstregulation, Lernen oder KI. S1-Q verwendet
nur synthetische AV-Quellen im Speicher; Browser, Kamera, Mikrofon, reale
Sensorik, Runner, Report und neue Laufnummer bleiben gesperrt.

## Abgrenzung

S1-Q wiederholt Lauf 194 nicht und beruehrt Lauf 197 nicht. Die Zweige
213ZZR bis 213ZZU, Z4, W1-O und W1-Q bleiben geschlossen beziehungsweise
unveraendert. S1-Q erweitert allein die Zeitabtastung der transparenten
S1-P-Engineeringfunktion.

## Bester naechster Schritt

S1-R implementiert nur einen zellweisen In-Memory-Adapter fuer die 32 fest
gebundenen S1-Q-Zellen. Zunaechst werden Inventar, feste Grenzen,
Vorproben-M-Ausgabe, S/H-Angleichung, Quellenmarginalien und Sentinelnullen
technisch getestet. Die Vollmatrix und die S1-Q-Klassifikationen bleiben in
S1-R noch unausgefuehrt.

## Spaeterer Auswertungsstand S1-S

S1-S hat die unveraenderte Matrix inzwischen reproduziert ausgewertet. Die
Hauptrolle lautet `FORMATION_EXTENDS_BEYOND_FIXED_BOUNDARY`, weil drei der
vier Vorproben-M-Kurven im spaeten Fenster gemischt bleiben. Alle
nachweisbaren M- und Probevektoren bleiben innerhalb der linearen
5-Prozent-Grenze. Daraus folgt kein Memory- oder Feldzeitbefund.
