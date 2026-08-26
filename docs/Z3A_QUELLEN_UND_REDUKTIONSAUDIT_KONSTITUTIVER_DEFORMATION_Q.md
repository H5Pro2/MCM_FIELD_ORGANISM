# Z3-A: Quellen- und Reduktionsaudit konstitutiver Deformation Q

Stand: 2026-08-06

Entscheidung: `Q_ROLE_BASELINE_EQUIVALENT`

Status:

- statischer Vergleich von drei etablierten Materialklassen;
- primaere Fachquellen und bestehende Projektbefunde verwendet;
- keine Q-Variable, Gleichung oder Parametrisierung zugelassen;
- keine Implementierung, Ausfuehrung oder neuer Forschungslauf;
- Z3 ist abgeschlossen.

## Forschungsfrage

Liefert eine etablierte lokale interne Materialvariable eine physikalisch
eigenstaendige Deformationsrolle mit konjugierter Wirkung, Bilanz und
natuerlicher Funktionsloesung, die fuer MCM nicht auf feste Relaxation,
Fliessgrenze, Hysterese oder Pfadintegration reduziert?

Geprueft werden:

1. viskoelastische interne Variablen;
2. elastoplastische interne Variablen;
3. energetisch rateunabhaengige interne Zustaende.

## Gemeinsamer thermodynamischer Rahmen

Die Theorie interner Zustandsvariablen zeigt, dass ein Materialzustand mehr
als die augenblicklich von aussen sichtbare Deformation enthalten kann.
Freie Energie, interne Variable, zugeordnete thermodynamische Kraft und
Dissipationsbedingung koennen eine konsistente konstitutive Beschreibung
bilden.

Dieser Rahmen liefert eine wichtige positive Grenze:

```text
ein interner materieller Freiheitsgrad ist physikalisch moeglich
```

Er liefert aber nicht automatisch:

```text
welcher Freiheitsgrad fuer MCM gilt
welche Feldgroesse seine konjugierte Kraft ist
welche Energie- und Dissipationsform richtig ist
wie alte Funktion geloest und anders neu gebildet wird
```

Thermodynamische Zulaessigkeit prueft ein konstitutives Gesetz. Sie waehlt
das Gesetz nicht aus.

## Klasse V: viskoelastische interne Variable

### Physische Rolle

Lineare Viskoelastizitaet kann durch innere Deformationsanteile dargestellt
werden. Eine freie Energie bindet aeussere und innere Deformation; ein
viskoser Dissipationsanteil bestimmt die zeitliche Relaxation.

In kleinster lokaler Form entsteht sinngemaess:

```text
eta * dQ/dt = konjugierte Kraft aus aktueller Deformation und Q
```

Bei linearer Energie und Dissipation folgt eine feste exponentielle
Relaxationsmode. Mehrere interne Variablen erzeugen eine Bank solcher Moden.

### MCM-Reduktion

- Q traegt Geschichte und kann spaetere Antwort beeinflussen.
- Die Entwicklung ist jedoch durch Materialzeitkonstanten an Weltsekunden
  gebunden.
- Entlastung loest die Wirkung durch dieselbe feste Relaxation.
- Digital entspricht die Form einer linearen Rekurrenz beziehungsweise einer
  oder mehreren Leaky-Spuren.

### Entscheidung

```text
physische interne Rolle:          ja
konjugierte Bilanz:               ja
weltzeitunabhaengige Entwicklung: nein
oberhalb Leaky-/K1-C1-Baseline:   nein
Q-Kandidat fuer MCM:              nein
```

## Klasse P: elastoplastische interne Variable

### Physische Rolle

Elastoplastische Theorien verwenden innere Variablen, um irreversible
mikrostrukturelle Umlagerung und Verfestigung zu beschreiben. Die
thermodynamische Kraft folgt aus der freien Energie. Ein Fliesspotential,
eine Fliessflaeche oder eine aequivalente Normalitaetsstruktur bestimmt, wann
und in welche Richtung plastische Aenderung erfolgt.

Im rateunabhaengigen Grenzfall haengt die Zustandsbahn von der
Belastungsreihenfolge, aber nicht von einer gleichfoermigen zeitlichen
Umparametrisierung ab.

### MCM-Reduktion

- Q ist hier physikalisch eigenstaendiger als eine Leaky-Spur.
- Die entscheidende Geschichtsschreibung liegt jedoch bereits in
  Fliessflaeche, Flussregel, Verfestigung und Dissipationspotential.
- Diese Strukturen legen Schwelle, Richtung und moegliche Zustandswege vor.
- Vollstaendige Wirkungslosigkeit und andere Wiederpraegung folgen nicht
  allgemein. Rueckbelastung verwendet erneut die festgelegte plastische
  Konstitution und kann irreversible Restdeformation tragen.

Eine Uebertragung auf MCM muesste eine Feld-Fliessflaeche und eine
Feld-Flussregel frei waehlen. Das waere genau die vorprogrammierte
Hysterese- beziehungsweise Schwellenphysik, gegen die Q abgegrenzt werden
muss.

### Entscheidung

```text
physische interne Rolle:              ja
rateunabhaengige Pfadwirkung:          ja
Fliessrichtung ohne Vorgabe bestimmt: nein
natuerliche Funktionsloesung:          nein
oberhalb Plastizitaets-/Hysteresebaseline: nein
Q-Kandidat fuer MCM:                  nein
```

## Klasse E: energetisch rateunabhaengiges System

### Physische Rolle

Energetische Modelle rateunabhaengiger Materialien werden durch eine
zeitabhaengige Speicherenergie `I(t,z)` und eine Dissipationsdistanz
`D(z1,z2)` definiert. Zulaessige Verlaeufe erfuellen Stabilitaet und eine
Energiebilanz. Die Entwicklung kann dadurch unter monotoner
Zeitumparametrisierung invariant sein.

Der interne Zustand `z` kann beispielsweise Phase, plastische Konfiguration
oder Schaedigung beschreiben.

### MCM-Reduktion

- Die Klasse liefert eine saubere mathematische Form fuer
  rateunabhaengige Pfadentwicklung.
- Energie, Dissipationsdistanz, zulaessige Zustandsmenge und Stabilitaetsform
  legen jedoch die gesamte Organisationslandschaft fest.
- Die uebliche energetische Stabilitaet vergleicht den aktuellen Zustand mit
  Alternativzustaenden und wird in inkrementellen Verfahren durch
  Minimierung bestimmt. Das ist nicht automatisch eine rein lokale atomare
  MCM-Naturwirkung.
- Bei lokaler Reduktion bleibt eine feste rateunabhaengige Hysterese- oder
  Play-/Stop-Klasse.
- Eine Funktionsloesung entsteht nur, wenn Energie- und Dissipationsform sie
  bereits erlauben; sie folgt nicht aus Rateunabhaengigkeit allein.

### Entscheidung

```text
rateunabhaengige Entwicklungsordnung: ja
Energie- und Dissipationsbilanz:       ja
Organisationslandschaft unbestimmt:    nein
rein lokale MCM-Konjugation gegeben:   nein
oberhalb Hysterese-/Attraktorbaseline: nein
Q-Kandidat fuer MCM:                   nein
```

## Vergleichsmatrix

| Kriterium | Viskoelastik V | Elastoplastik P | energetisch rateunabhaengig E |
| --- | ---: | ---: | ---: |
| reale interne Materialrolle | ja | ja | ja |
| konjugierte Kraft und Bilanz formulierbar | ja | ja | ja |
| unabhaengig von Weltzeitskalierung | nein | im idealen Grenzfall ja | ja |
| Pfadabhaengigkeit | fading | ja | ja |
| lokale Richtung ohne konstitutive Vorgabe | nein | nein | nein |
| natuerliche vollstaendige Funktionsloesung | feste Relaxation | nicht allgemein | nicht allgemein |
| andere Wiederpraegung ohne Zusatzstruktur | erneute Filteranregung | nicht allgemein | nur gemaess Energielandschaft |
| staerkste MCM-Baseline | Leaky/Rekurrenz | Schwelle/Hysterese | Hysterese/Attraktor |
| als Q weiter zulaessig | nein | nein | nein |

## Entscheidender Unterschied zwischen realem Material und MCM-Uebertragung

Bei einem realen Material koennen innere Variablen durch eine unabhaengig
beobachtete Mikrostruktur, Stoffklasse und experimentelle Kraft-
Deformations-Beziehung begruendet werden. Im aktuellen digitalen MCM-System
fehlen diese unabhaengigen Messbedingungen.

Eine mathematisch konsistente Q-Variable waere daher technisch leicht zu
bauen. Ihre konkrete Beanspruchung, Energie, Dissipation, Fliessrichtung und
Rueckwirkung muessten aber aus dem gewuenschten Entwicklungsverhalten
ausgewaehlt werden. Genau das verbietet der Z3-Vertrag.

## Entscheidung

`Q_ROLE_BASELINE_EQUIVALENT`

Alle drei Klassen belegen, dass interne Deformationszustaende physikalisch
real und thermodynamisch konsistent sein koennen. Keine Klasse liefert jedoch
eine auf MCM uebertragbare Q-Rolle, die zugleich:

- ihre konjugierte Feldwirkung aus der vorhandenen MCM-Physik erhaelt;
- keine feste Relaxation, Fliessgrenze oder Hystereselandschaft vorgibt;
- funktionale Loesung und andere Wiederpraegung aus derselben offenen
  Naturform traegt;
- oberhalb der bereits gebundenen Pflichtbaselines liegt.

Q wird deshalb nicht mathematisch praezisiert und nicht implementiert. Z3
ist abgeschlossen.

Die Entscheidung ist kein allgemeiner Unmoeglichkeitsbeweis. Sie bedeutet,
dass ein solches digitales Material nur als offen gesetzte Standardmaterial-
Hypothese untersucht werden koennte, nicht als aus MCM hergeleitete neue
Physik oder als organisches Memory.

## Primaerquellen

- B. D. Coleman und M. E. Gurtin,
  [Thermodynamics with Internal State Variables](https://doi.org/10.1063/1.1711937),
  1967. Allgemeiner thermodynamischer Rahmen interner Zustandsvariablen.
- J. R. Rice,
  [Inelastic constitutive relations for solids: an internal-variable theory and its application to metal plasticity](https://doi.org/10.1016/0022-5096(71)90010-X),
  1971. Interne Mikrostrukturvariablen, thermodynamische Kraefte,
  Fliesspotential und Normalitaetsstruktur der Plastizitaet.
- B. Halphen und Q. S. Nguyen,
  [Sur les materiaux standards generalises](https://www.researchgate.net/publication/279887925_On_Generalized_Standard_MaterialsSUR_LES_MATERIAUX_STANDARDS_GENERALISES),
  1975. Normale Dissipativitaet und Entwicklungsgesetze fuer
  elastoviskoplastische und elastoplastische interne Parameter.
- A. Morro und M. Vianello,
  [Free energy and internal variables in linear viscoelasticity](https://eudml.org/doc/287373),
  1989. Freie Energie fuer lineare Viskoelastizitaet in Darstellung durch
  interne Variablen.
- A. Mielke, F. Theil und V. I. Levitas,
  [A Variational Formulation of Rate-Independent Phase Transformations Using an Extremum Principle](https://doi.org/10.1007/s002050200194),
  2002. Rateunabhaengige hysteretische Entwicklung durch Energie- und
  Dissipationsfunktionale.
- A. Mielke,
  [Analysis of energetic models for rate-independent materials](https://arxiv.org/abs/math/0305014),
  2003. Stabilitaet, Energiebilanz und interne Zustaende im energetischen
  rateunabhaengigen Rahmen.

## Verwendete Projektquellen

- [Z3-Hypothesenvertrag](Z3_HYPOTHESENVERTRAG_LOKALE_KONSTITUTIVE_DEFORMATION.md)
- [Z2-B-Kollisionsaudit](Z2B_KOLLISIONSAUDIT_LOKALE_FELDARBEIT_UND_FLUSSDURCHGANG.md)
- [H2-B-Materialklassenvergleich](H2B_VERGLEICH_PASSIVER_MATERIALKLASSEN.md)
- [K1-Konstitutiver Schliessungsaudit](K1_KONSTITUTIVER_SCHLIESSUNGSAUDIT.md)
- [Zulassungsvertrag strukturveraendernder MCM-Physik](ZULASSUNGSVERTRAG_STRUKTURVERAENDERNDE_LOKALE_MCM_PHYSIK.md)
- [Vergleich strukturveraendernder K1-Familien](VERGLEICH_STRUKTURVERAENDERNDER_K1_FAMILIEN.md)

## Aussagegrenze

Der Audit bewertet Materialklassen, nicht menschliches Erleben oder
biologische Gedaechtnisbildung. Er weist weder relative Feldzeit noch Memory,
inneren Kontext, Organisation, Topologie, Semantik, Selbstregulation oder KI
nach.

## Bester naechster Schritt

Keine vierte abstrakte Zustandsrolle ableiten. Der
[Z4-Richtungsentscheid](Z4_RICHTUNGSENTSCHEID_STRENGE_FELDLINIE.md) hat die
strenge Feldlinie verbindlich gewaehlt. Als Naechstes wird nur eine statische
Mehrwelt-Feldencoder-Vorregistrierung fuer P0, F3 und B3 erstellt.
