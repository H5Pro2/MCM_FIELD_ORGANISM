# Abgrenzung konservativer radialer Transportklassen

## Fragestellung

Die neutrale radiale Morphologie stellt Materiallage dar, bewegt aber noch
nichts.

Gesucht ist die kleinste Transportklasse, die:

- Eigentümermaterial exakt erhält;
- räumliche Lage tatsächlich verändert;
- endliche Ausbreitung erlaubt;
- keine Zielposition vorgibt;
- keine Kontaktschwelle benötigt;
- keine Beziehung oder Bedeutung kennt;
- nicht nur eine weitere Leaky-Spur ist.

Noch wird keine Transportgleichung implementiert.

## Klasse A - Positive radiale Diffusion

Eine direkte Möglichkeit wäre:

```text
partielle_Ableitung rho / partielle_Ableitung t
=
D * zweite_radiale_Ableitung rho
```

Positive Diffusion verteilt vorhandenes Material entlang des Profils und
glättet Unterschiede.

Diese Klasse ist lokal, symmetrisch und materialerhaltend formulierbar. Für
die Projektfrage besitzt sie jedoch klare Grenzen:

- ein lokaler Impuls verteilt sich sofort oder numerisch stark
  auflösungsabhängig;
- räumliche Unterschiede werden geglättet;
- ohne weitere Physik entsteht keine gerichtete Annäherung;
- mit festem Rückfluss entsteht eine räumlich verteilte Leaky-Kaskade;
- Grenzflächenmaterial klingt typischerweise asymptotisch statt vollständig
  geometrisch zu verschwinden.

Reine Diffusion wird nicht als erster Morphologiekandidat zugelassen.

## Klasse B - Drift zu einem festen Potential

Ein radiales Potential könnte Material in Richtung bestimmter Lagen treiben:

```text
Materialfluss
=
- Mobilität * rho * Gradient(Potential)
```

Ist das Potential fest, sind bevorzugte Materiallagen bereits Teil der
programmierten Physik.

Ist das Potential eine Funktion der gegenwärtigen Feldursache, folgt die
Materiallage mit Verzögerung einer aktuellen Zielverteilung. Bei konvexer
Dynamik ist dies funktional eine geglättete Gegenwartsprojektion.

Nichtkonvexe Potentiale führen feste Attraktoren und Umschaltgrenzen ein.

Diese Klasse wird ohne unabhängige Materialbegründung nicht zugelassen.

## Klasse C - Reaktion, Wachstum und Zerfall

Eine Reaktionsgleichung könnte Material lokal erzeugen, abbauen oder zwischen
Formen umwandeln.

Für das aktuelle Eigentümermaterial wäre dafür mindestens nötig:

```text
Wachstum an einer Stelle
gegen
Verbrauch oder Rückzug an anderer Stelle
```

Eine feste Wachstums- und Zerfallsrate erzeugt erneut:

- Integrator;
- Leaky-Spur;
- Sättigung;
- Schwellen- oder Attraktordynamik.

Sie bewegt nicht notwendig vorhandene räumliche Unterstützung, sondern
verändert hauptsächlich Amplituden.

Diese Klasse wird nicht zugelassen.

## Klasse D - Phasenfeld und Grenzflächenenergie

Massenerhaltende Phasenfelder können Domänen, Fronten und Umordnung tragen.
Dafür benötigen sie jedoch eine vorgegebene freie Energielandschaft,
Grenzflächenkosten und Mobilität.

Die daraus bevorzugten Materialphasen und Längenskalen wären bereits in der
Gleichung enthalten. Eine sichtbare Front wäre noch kein Nachweis von
Memory, Beziehung oder Wiederbindung.

Diese Klasse ist für den minimalen ersten Kandidaten zu voraussetzungsreich.

## Klasse E - Elastische oder wellenartige Bewegung

Material könnte über Spannung, Trägheit und Rückstellwirkung bewegt werden.
Das erlaubt endliche Ausbreitung, benötigt aber zusätzliche Rollen:

- Geschwindigkeit oder Impuls;
- Ruhelage;
- Elastizität;
- Dämpfung.

Ohne Dämpfung entstehen Oszillationen. Mit Dämpfung entsteht eine
mechanische Nachhallklasse. Die Ruhelage und ihre Rückstellung wären
programmiert.

Diese Klasse wird nicht als erster Kandidat gewählt.

## Klasse F - Konservative Advektion

Advektion bewegt vorhandene Materialunterstützung mit einem lokalen
Geschwindigkeitsfeld:

```text
partielle_Ableitung rho / partielle_Ableitung t
+
partielle_Ableitung (v * rho) / partielle_Ableitung q
=
0
```

Diese Klasse besitzt Eigenschaften, die von einer reinen Amplitudenspur
verschieden sind:

- Material wird räumlich transportiert, nicht erzeugt oder gelöscht;
- Unterstützung kann sich mit endlicher Geschwindigkeit verlagern;
- eine Materialfront kann die geometrische Grenzfläche erreichen;
- umgekehrter Transport kann Material wieder räumlich trennen;
- eine Kontaktgrenze muss nicht als Aktivierungsschwelle erfunden werden;
- es existiert keine feste Zielposition.

Damit ist konservative endliche Advektion die einzige der geprüften
Minimalfamilien, die als **passiver erster Morphologiekandidat** offen bleibt.

## Wichtige Einschränkung

Advektion allein ist noch kein organisches Memory.

Die Materiallage ist das Zeitintegral ihrer Bewegung. Wird die Geschwindigkeit
direkt aus einer Feldursache konstruiert, kann der Kandidat funktional ein
räumlicher Integrator sein.

Offen bleiben insbesondere:

- welche vorhandene Feldursache eine Geschwindigkeit begründen darf;
- welches Vorzeichen nach außen oder innen wirkt;
- ob unterschiedliche Weltgeschichten selektive Unterstützung erzeugen;
- ob Material ohne programmierte Rückstellkraft wieder zurückweicht;
- ob Berührung beidseitig entstehen kann;
- ob numerische Diffusion den Befund erklärt.

Die Transportklasse wird deshalb zugelassen, nicht ihre konkrete Anregung.

## Keine bevorzugte Grenzfläche

Die radiale Außengrenze `q = 1` ist Geometrie, aber kein Ziel.

Eine zulässige Transportregel darf nicht enthalten:

```text
bewege Material grundsätzlich zu q = 1
```

Ebenso unzulässig ist:

```text
bewege Material ohne Feldursache grundsätzlich zu q = 0
```

Beides würde Annäherung beziehungsweise Rückzug bereits als gewünschtes
Verhalten programmieren.

Im neutralen Zustand ohne zugelassene Ursache muss die Geschwindigkeit null
sein.

## Endliche Volumenbilanz

Für die digitale radiale Anatomie ist eine konservative Flussform notwendig.
Zwischen benachbarten radialen Zellen existiert ein Grenzfluss:

```text
F(k + 1/2)
```

Die Zellmenge ändert sich nur durch ein- und austretenden Fluss:

```text
Delta m_k
=
Delta t * (F(k - 1/2) - F(k + 1/2))
```

Innere Flüsse heben sich in der Gesamtbilanz paarweise auf.

Der Fluss am neuronennahen Rand darf nur Material mit dem ungebundenen
Eigentümeranteil austauschen. Am äußeren Rand darf kein Material das Neuron
verlassen.

Damit bleibt:

```text
ungebunden
+ Summe aller radialen Zellmengen
=
Eigentümergesamtmenge
```

## Numerische Gegenkontrollen

Ein späterer passiver Advektionskandidat muss mindestens prüfen:

1. exakte Eigentümerbilanz;
2. Nichtnegativität;
3. endliche Ausbreitung;
4. Nullursache erzeugt keine Bewegung;
5. Spiegelung und Achstausch;
6. umgekehrte Iterationsreihenfolge;
7. feinere und gröbere zulässige Zeitschritte;
8. feinere und gröbere radiale Auflösung;
9. Trennung von physischer Bewegung und numerischer Diffusion;
10. keine Runtime- oder Feldrückwirkung.

Ein Befund, der bei anderer Auflösung verschwindet oder nur durch numerische
Verschmierung Grenzflächenmaterial erzeugt, wird verworfen.

## Noch keine Geschwindigkeitsregel

Nicht freigegeben werden:

- Geschwindigkeit aus Flussbetrag;
- Geschwindigkeit aus Flussvorzeichen;
- Koaktivitätsdruck;
- Rezeptorkontakt als direkte Außenbewegung;
- Rückstellkraft;
- Kontaktanziehung;
- zufällige Bewegung;
- gelernte Transportparameter.

Diese Ursachen müssen einzeln gegen die bisherigen Negativbefunde geprüft
werden.

## Status

```text
positive Diffusion als erster Kandidat:       verworfen
festes oder feldabhängiges Potential:         nicht zugelassen
Wachstum und Zerfall:                         verworfen
Phasenfeld:                                   zu voraussetzungsreich
elastische Bewegung:                          nicht gewählt
konservative endliche Advektion:              passiv zugelassen
konkrete Geschwindigkeit bestimmt:            nein
Materialbewegung implementiert:                nein
Feldwirkung freigegeben:                       nein
Runtime-Integration freigegeben:               nein
```

## Nächster technischer Schritt

Als Nächstes wird nur ein **radialer Flussvertrag** implementiert.

Er darf:

- Grenzflüsse zwischen benachbarten radialen Zellen darstellen;
- den Austausch mit dem ungebundenen Eigentümeranteil bilanzieren;
- Nichtnegativität, Zeit und Auflösung prüfen;
- einen vollständigen passiven Transportvorschlag validieren.

Er darf nicht:

- selbst eine Geschwindigkeit erzeugen;
- Material automatisch nach außen oder innen bewegen;
- Grenzflächenkontakt erzeugen;
- den Vorschlag in die Runtime übernehmen.

Erst danach kann eine einzelne Geschwindigkeitsursache isoliert geprüft
werden.
