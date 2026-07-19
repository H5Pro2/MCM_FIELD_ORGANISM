# Grenze eines homogen verteilten Skalarsubstrats

## Fragestellung

Der Audit des isolierten lokalen Substratzustands ließ eine räumlich verteilte
Klasse offen. Dieser Audit prüft, ob bereits die Vervielfachung desselben
skalaren Zustandstyps über das gemeinsame MCM-Feld eine neue organische
Memory-Form ermöglicht.

Geprüft wird die enge Klasse:

```text
ein skalarer Substratzustand m_i an jedem MCM-Ort i
+ überall dieselbe zeitinvariante lokale Regel
+ symmetrische lokale Nachbarschaft
+ positive gewöhnliche Diffusion
+ keine Kantenidentität
+ keine Zieltopologie
```

Eine konkrete Runtime-Erweiterung ist nicht Bestandteil dieses Audits.

## Das heutige Feld ist bereits verteilt

Die vorhandene Runtime besitzt an jedem Neuronenort Aktivierung und schnellen
Nachhall. Die Aktivierung ist über eine symmetrische Nachbarschaft gekoppelt.
Kontaktfrei gilt für die schnelle Lage in Matrixform:

```text
dx/dt = L x
```

`L` ist der feste Diffusionsgenerator. Seine nichtkonstanten räumlichen Modi
haben nichtpositive Eigenwerte und werden durch

```text
x(t) = exp(L t) x(0)
```

nicht verstärkt. Die konstante Lage bleibt erhalten, Unterschiede werden
geglättet.

Damit ist bereits praktisch belegt:

> Viele lokale Träger und lokale Kopplung allein ergeben noch keine
> entwickelbare Feldtopologie.

## Fall A - Reine positive Diffusion

Für einen hypothetischen verteilten Skalar ohne eigene Reaktionsdynamik gilt
entsprechend:

```text
dm_i/dt = D * Sum_j A_ij (m_j - m_i),  D > 0
```

Diese Regel:

- verteilt vorhandene Unterschiede;
- reduziert räumliche Gradienten;
- erhält je nach Randbedingung eine Gesamtmenge;
- erzeugt keinen neuen geschichtlichen Freiheitsgrad;
- verändert keine lokale Übertragungsbedingung.

Sie ist ein räumlicher Glätter, kein organisches Memory.

## Fall B - Lokal stabile Skalarreaktion plus Diffusion

Mit einer homogenen lokalen Reaktion lautet die Klasse:

```text
dm_i/dt = f(m_i, u_i) + D * Sum_j A_ij (m_j - m_i)
```

Sei `m*` ohne neue Weltwirkung ein lokal stabiler homogener Zustand. Für eine
kleine räumliche Störung hat jeder Graphmodus die lineare Wachstumsrate:

```text
lambda_k = f'(m*) - D * mu_k
```

Dabei ist `mu_k >= 0` der jeweilige Modus des positiven Graph-Laplacians. Wenn
schon der homogene Modus mit `f'(m*) < 0` stabil ist, sind alle nichtkonstanten
Modi noch stärker gedämpft.

Positive Diffusion kann einen lokal stabilen homogenen Skalar deshalb nicht
durch eine klassische diffusionsgetriebene Instabilität in eine räumliche
Organisation überführen.

## Fall C - Bistabile oder mehrdeutige Lokalreaktion

Eine skalare Reaktion kann Domänen und Fronten tragen, wenn `f` mehrere stabile
Lagen besitzt. Dann sind jedoch bereits vorgegeben:

- die möglichen Materiallagen;
- ihre Anziehungsbereiche;
- die Umschaltgrenzen;
- die Art der Frontbewegung.

Eine Weltgeschichte könnte auswählen, wo welche Lage entsteht. Die Menge der
zulässigen Lagen und ihre Lösung sind aber schon in der Materialgleichung
enthalten.

Das kann ein physikalisches Modell sein, begründet im Projekt aber noch keine
darstellungsoffene Memory-Organisation. Es fällt zunächst auf den bereits
geprüften Attraktor- oder Zustandsautomaten zurück.

## Fall D - Antidiffusion oder zustandsabhängiger Transport

Räumliche Unterschiede lassen sich durch negative Diffusion, Cross-Diffusion,
nichtlokale Kopplung oder zustandsabhängige Leitfähigkeit verstärken. Damit
wird aber eine neue Struktur eingeführt:

- negative Diffusion benötigt Stabilisierung gegen unbegrenzte Verstärkung;
- zustandsabhängige Leitfähigkeit ist bereits eine lokale veränderliche
  Übertragungsbedingung;
- Cross-Diffusion benötigt mindestens eine weitere Zustandsrolle;
- nichtlokale Kopplung überschreitet die geprüfte lokale Klasse.

Diese Wege widerlegen die Grenze der positiven Skalar-Diffusion nicht. Sie
verlassen ihre Voraussetzungen.

## Fall E - Erhaltener Skalar und Phasentrennung

Ein erhaltener Skalar kann in einer Phasenfeldmechanik räumliche Domänen bilden
und umordnen. Dafür werden typischerweise benötigt:

- eine vorgegebene freie Energielandschaft;
- ein Gradiententerm oder eine höherordentliche räumliche Wirkung;
- eine Erhaltungsbedingung;
- eine festgelegte Mobilität.

Damit ist räumliche Selbstorganisation grundsätzlich möglich. Ihre bevorzugten
Materiallagen und Grenzflächenkosten sind jedoch in der Physik vorgegeben.

Für das MCM-Projekt wäre zusätzlich ungeklärt:

```text
Domänenbildung
!=
geschichtsabhängige funktionale Feldorganisation
```

Eine sichtbare räumliche Form ist noch kein Beleg für Memory, Beziehung,
Semantik oder Wiederbindung.

## Fall F - Zelluläre und neuronale Automaten

Homogene lokale Automaten können komplexe globale Formen hervorbringen.
Neuronale zelluläre Automaten verwenden dafür jedoch gewöhnlich:

- einen lokalen Zustandsvektor statt eines einzelnen Skalars;
- eine gelernte lokale Update-Regel;
- ein Zielbild oder eine Zielfunktion;
- zusätzliche Lebens-, Masken- oder Aktualisierungsregeln.

Sie belegen, dass lokale homogene Regeln globale Organisation tragen können.
Sie sind aber kein Gegenbeispiel für die Projektgrenze, weil die gewünschte
Form über Training oder Zielvorgabe in die Regel gelangt.

## Räumliche Form ist noch keine Topologie

Für dieses Projekt darf eine räumlich inhomogene Lage erst dann als
Memory-Organisation gelten, wenn sie gemeinsam zeigt:

1. **Geschichtsabhängigkeit:** Verschiedene Weltgeschichten erzeugen bei
   kontrollierter Gegenwart verschiedene innere Lagen.
2. **Kausale Feldwirkung:** Diese Lagen verändern dieselbe spätere Feldprobe.
3. **Nichtredundanz:** Aktivierung und schneller Nachhall erklären den Effekt
   nicht vollständig.
4. **Lösung:** Alte funktionale Wirkung kann ohne globalen Löschbefehl enden.
5. **Wiederprägung:** Neue Weltgeschichte kann dieselbe lokale Materie anders
   funktional einbinden.
6. **Offenheit:** Keine Klasse, Beziehung oder Zielordnung ist vorgegeben.

Ohne diese sechs Punkte wäre ein Muster nur eine dynamische Feldform.

## Enger Negativnachweis

Unter den geprüften Bedingungen gilt:

```text
homogen verteilter Skalar
+ lokal stabile Reaktion
+ positive symmetrische Diffusion
-> Glättung räumlicher Unterschiede
-> keine diffusionsgetriebene Entstehung neuer Organisationsmodi
```

Die Verteilung vervielfacht Zustandsorte, beseitigt aber nicht die Grenze des
isolierten Skalars. Gewöhnliche positive Diffusion koppelt bekannte Spuren,
ohne eine neue Lösungs- oder Wiederbindungsfunktion zu erzeugen.

## Aussagegrenze

Dies ist kein allgemeiner Unmöglichkeitsbeweis gegen skalare räumliche Systeme.
Nichtlineare, konservierte, verzögerte, stochastische oder nichtlokale Regeln
können Muster bilden.

Der Audit zeigt enger:

> Die bloße räumliche Verteilung eines neutralen Skalars über die vorhandene
> positive MCM-Diffusion ist kein neuer Memory-Kandidat.

Jede bekannte Umgehung führt eine zusätzliche physische Struktur ein. Diese
muss einzeln begründet werden und darf nicht als versteckte Semantik oder
gewünschte Topologie eingebaut werden.

## Verbleibende minimale Prüfklasse

Das gemeinsame Feld besitzt bereits eine schnelle Zustandsrolle `x`. Deshalb
ist der nächste zulässige Gedanke nicht ein beliebiges Mehrvariablensystem,
sondern ausschließlich:

```text
vorhandene schnelle Feldlage x_i
<-> noch unbestimmte lokale Materialdisposition m_i
```

Dabei müsste `m_i`:

- überall dieselbe neutrale Rolle besitzen;
- nur reale lokale Feldwirkung und lokale Nachbarschaft lesen;
- keine Partner- oder Objektkennung tragen;
- die lokale Feldantwort mitprägen, ohne eine Zielantwort festzulegen;
- begrenzt, lösbar und erneut prägbar sein.

Diese Kopplung ist noch nicht freigegeben. Vor jeder Gleichung muss geprüft
werden, ob sie eine echte Materialrückwirkung darstellen kann oder nur eine
zweite Leaky-Spur, einen Aktivator-Inhibitor-Automaten oder eine versteckte
adaptive Kante erzeugt.

## Primäre Vergleichsquellen

- A. M. Turing beschreibt Reaktion und Diffusion mehrerer Morphogene als
  Ausgangspunkt diffusionsgetriebener Musterbildung:
  [The Chemical Basis of Morphogenesis](https://academic.oup.com/book/42030/chapter-abstract/355747318)
- B. Ermentrout und M. Lewis zeigen für räumliche Muster mit nur einer
  räumlich beweglichen Spezies, dass zusätzliche nichtdiffundierende Rollen
  entscheidend bleiben:
  [Pattern Formation in Systems with One Spatially Distributed Species](https://www.math.ualberta.ca/~mlewis/publications/24Ermentrout1997BMB.pdf)
- J. W. Cahn und J. E. Hilliard formulieren Phasenorganisation über eine
  vorgegebene freie Energie eines inhomogenen Systems:
  [Free Energy of a Nonuniform System I](https://doi.org/10.1063/1.1744102)
- A. Mordvintsev, E. Randazzo und C. Fouts zeigen zugleich die Leistungsfähigkeit
  und Zielabhängigkeit gelernter homogener lokaler Automaten:
  [Growing Isotropic Neural Cellular Automata](https://arxiv.org/abs/2205.01681)

Diese Quellen werden als Mechanikvergleiche verwendet. Sie belegen keine
MCM-spezifische Organisation.

## Freigabegrenze

```text
Verteilung allein als neuer Memory-Träger:       nein
positive Skalar-Diffusion als Organisation:      nein
räumliche Muster grundsätzlich möglich:          ja
räumliche Muster gleich organisches Memory:       nein
lokale Materialdisposition ausgewählt:            nein
zweite Zustandsrolle freigegeben:                 nein
konstitutive Gleichung freigegeben:               nein
Runtime-Erweiterung freigegeben:                  nein
```

## Nächster Schritt

Als Nächstes wird ausschließlich die minimale reziproke Rollenklasse geprüft:

```text
vorhandene schnelle Feldlage
<-> lokale homogene Materialdisposition
```

Zu klären ist, ob eine solche Rückwirkung überhaupt mehr leisten kann als
gekoppelter Leaky-Nachhall oder fest programmierte Attraktordynamik. Noch wird
weder ein Zustand ergänzt noch eine Gleichung implementiert.
