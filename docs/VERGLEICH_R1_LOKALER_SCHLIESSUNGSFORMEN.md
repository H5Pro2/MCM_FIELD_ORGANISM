# Vergleich lokaler R1-Schliessungsformen

## Status

```text
Pruefart:                           statischer Reduzierbarkeitsaudit
untersuchte Formen:                drei
Form 1:                             geschlossen
Form 2:                             geschlossen
Form 3:                             bedingt offen
konkrete Gleichung:                 nicht zugelassen
Implementierung oder Versuch:       nicht zugelassen
```

## Forschungsfrage

Welche kleinste lokale S-L-Kreuzwirkungsform besitzt innerhalb von R1 eine
eigene konstitutive Rolle, ohne lediglich eine Leaky-Spur, einen Integrator,
Gain, Mobilitaet, Oszillator, eine feste Hysterese oder eine vorbereitete
Musterkinetik zu realisieren?

R1 setzt weiterhin voraus:

- nur S besitzt den bestehenden raeumlichen Feldfluss;
- L bleibt ein skalarer, ortsgebundener Zustand desselben MCM-Feldes;
- S und L werden atomar aus demselben Vorzustand fortgeschrieben;
- die Welt erreicht L nur ueber die normale S-Feldentwicklung;
- L wirkt additiv auf S und skaliert weder Rezeptoren noch Feldfluss;
- keine Schliessung darf Memory, Organisation oder Bedeutung vorgeben.

## Gemeinsamer Pruefmassstab

Eine Form bleibt nur offen, wenn ihre behauptete Funktion nicht schon durch
eine engere bekannte Klasse vollstaendig beschrieben wird. Lange Dauer,
Nichtlinearitaet, Schleifen, unterschiedliche Endzustaende oder raeumliche
Muster sind fuer sich kein ausreichender Rest.

Der spaetere Vergleich muss fuer Kandidat und Baseline jeweils einen festen
vorregistrierten Parametersatz ueber den gesamten Verlauf verwenden. Eine
phasenweise Neuparametrisierung ist unzulaessig.

## Form 1: dissipative reziproke Akkommodation

### Rollenidee

S und L wirken wechselseitig aufeinander, waehrend eine eindeutige neutrale
Region und eine dissipative Rueckkehr alle ungetriebenen Verlaeufe begrenzen.

### Reduktion

Ist die lokale Form monoton, kontraktiv oder durch ein konvexes
Dissipationsgefaelle bestimmt, werden Unterschiede der inneren Zustaende
letztlich abgebaut. L ist dann eine interne Relaxationsvariable. Abhaengig von
der konkreten Parametrisierung entsteht:

- eine einzelne oder zusammengesetzte Leaky-Spur;
- ein viskoelastischer beziehungsweise Fading-Memory-Zustand;
- ein gedaempfter Modenaustausch zwischen S und L;
- eine statische nichtlineare Antwort mit nachgelagerter Relaxation.

Eine eindeutige neutrale Region verhindert zwar vorbereitete Zielmuster, sie
liefert aber keine unabhaengige Funktion fuer Bildung, spaetere kausale
Wirkung, funktionale Loesung und andere Wiederpraegung. Diese Phasen bleiben
Ausdruck derselben vorgegebenen Relaxation.

### Entscheidung

```text
Form 1: STOPP als primaerer R1-Kandidat
Grund:  vollstaendig durch Relaxations-, Fading-Memory- oder
        viskoelastische Baselines erklaerbar
```

Form 1 bleibt eine Pflichtbaseline.

## Form 2: begrenzte nichtgradientige S-L-Kreuzwirkung

### Rollenidee

Die lokale Dynamik besitzt kein einzelnes Potential, dessen Gefaelle die
gesamte Entwicklung bestimmt. S und L koennen dadurch gekruemmte oder
rotierende lokale Verlaeufe bilden.

### Reduktion

`Nichtgradientig` bezeichnet nur das Fehlen einer bestimmten mathematischen
Darstellung. Daraus folgt noch keine eigene physische Funktion. Unter fester
oder angeglichener lokaler Anregung bleiben insbesondere folgende enge
Erklaerungen offen:

- ein stabiler eindeutiger Endzustand mit komplexem Transienten;
- ein gedaempfter oder selbsterhaltender Oszillator;
- ein Grenzzyklus beziehungsweise eine Phasenvariable;
- mehrere vorbereitete Attraktoren oder feste Hysterese;
- eine bekannte Ein-Diffusor-Reaktions-Diffusionskinetik im raeumlichen Feld.

Die Forderung nach Begrenztheit schliesst Divergenz aus, trennt diese Klassen
aber nicht. Ohne zusaetzliche Funktionsannahme ist die Form breiter als die
gesuchte Erklaerung und nicht eigenstaendig falsifizierbar.

### Entscheidung

```text
Form 2: STOPP als primaerer R1-Kandidat
Grund:  Nichtgradientigkeit ist eine Formeigenschaft, keine unabhaengige
        Naturfunktion; die verbleibenden Effekte besitzen engere Baselines
```

Form 2 darf spaeter nur als Oberklasse oder konkrete Oszillator-, Attraktor-
und Musterbaseline auftreten.

## Form 3: lokale zustandsabhaengige additive Gegenwirkung

### Rollenidee

L ist eine lokale interne Feldkonfiguration, deren Beitrag der aktuellen
S-Fortsetzung additiv gegenuebersteht oder sie umlenkt. Gleichzeitig wird L
durch dieselbe lokale S-L-Wechselwirkung weiterentwickelt.

`Gegenwirkung` bedeutet hier keinen Fehler, kein Ziel und keine programmierte
Rueckkehr. Sie benennt ausschliesslich die Vorzeichen- beziehungsweise
Richtungsrolle eines internen konstitutiven Beitrags innerhalb der atomaren
S-L-Fortsetzung.

### Warum diese Form einen Rest behaelt

Im Unterschied zu Gain oder Mobilitaet veraendert L nicht die Staerke eines
Rezeptors, einer Kante oder einer Zeitkonstante. Im Unterschied zur reinen
Spur wird L nicht nur gebildet und spaeter durch einen getrennten Leser
ausgewertet. Sein Beitrag ist Bestandteil derselben lokalen Wechselwirkung,
die den internen Zustand fortsetzt.

Damit ist zumindest eine kausal pruefbare Rollenart vorhanden:

```text
gleicher S-Zustand + unterschiedliches L
-> unterschiedlicher additiver interner S-Beitrag
```

Diese Rollenart belegt noch keine neue Mechanik. Klassische Modelle mit
innerer Gegenvariable, dynamischer Erholung oder glatter Hysterese koennen
dasselbe Verhalten erzeugen.

### Harte Reduktionsgrenze

Form 3 wird geschlossen, wenn ihre Konkretisierung eine der folgenden
Eigenschaften benoetigt:

1. L ist lediglich eine gefilterte, integrierte oder verzoegerte Kopie von S.
2. Ein fester Multiplikator liest L als Gain, Mobilitaet oder Zeitkonstante.
3. Eine Schaltschwelle, Fliessgrenze oder Fallunterscheidung schreibt Bildung
   und Loesung vor.
4. Die Gleichung konstruiert eine feste Hystereseschleife, bekannte
   Rueckstellkurve oder mehrere gewuenschte Lagen.
5. Dynamische Erholung ist nur ein festes Abklingen einer internen
   Gegenvariable.
6. Unter einer zulaessigen Zustands- oder Modentransformation bleibt nur ein
   Relaxator oder Oszillator uebrig.
7. Der raeumliche Effekt besteht nur aus Wellen, Flecken, Symmetriebruch oder
   anderen Ein-Diffusor-Mustern.
8. Die behauptete Funktion benoetigt bereits Begriffe wie Praegung, Memory,
   Erkennen, Bedeutung oder Organisation.

### Entscheidung

```text
Form 3: bedingt offen fuer genau einen engeren statischen Vertrag
Grund:  additive interne Gegenwirkung ist von Gain und reinem Register
        kausal unterscheidbar, aber noch nicht von Hysterese und klassischen
        internen Gegenvariablen getrennt
```

Die offene Form wird vorlaeufig **begrenztes additives konstitutives
Gegenfeld** genannt. Der Name beschreibt eine Rollenannahme, keinen positiven
Befund und kein Memory.

## Vergleichsergebnis

| Form | Eigener funktionaler Rest | Engste Primaererklaerung | Entscheidung |
|---|---|---|---|
| dissipativ reziprok | nein | Relaxation, Fading Memory, Viskoelastik | geschlossen |
| begrenzt nichtgradientig | nein | Transient, Oszillator, Attraktor oder Musterkinetik | geschlossen |
| additive Gegenwirkung | noch ungeprueft | interne Gegenvariable oder glatte Hysterese | bedingt offen |

Es ist damit keine MCM-Memory-Mechanik gefunden. Der Audit reduziert nur den
Suchraum von drei lokalen Formfamilien auf eine engere Rollenart.

## Spaetere Gegenbaselines fuer Form 3

Vor jeder Gleichungswahl muessen mindestens folgende Baselines als
vollstaendige Alternativerklaerungen operationalisiert werden:

- lineare interne Gegenvariable mit fester Relaxation;
- nichtlineare Gegenvariable mit dynamischer Erholung;
- glatte skalare Hysterese mit festem Parametersatz;
- gedaempfter lokaler S-L-Oszillator;
- derselbe S-Pfad ohne L-zu-S-Richtung;
- derselbe L-Zustand mit neutralisiertem additivem Beitrag.

Die letzten beiden Formen sind kausale Ablationen, keine Organismusfunktionen.

## Quellen

- G. M. Eggert und P. R. Dawson,
  [On the use of internal variable constitutive equations in transient forming processes](https://doi.org/10.1016/0020-7403(87)90045-2),
  1987. Dient zur Einordnung eines skalaren inneren konstitutiven Zustands;
  daraus wird keine MCM-Gleichung uebernommen.
- M. Ismail, F. Ikhouane und J. Rodellar,
  [The Hysteresis Bouc-Wen Model, a Survey](https://doi.org/10.1007/s11831-025-10301-z),
  2026. Dient als Gegenbeleg dafuer, dass glatte begrenzte differentielle
  Hysterese bereits vielfaeltige Schleifen- und Erholungseffekte tragen kann.
- H. Miyazako, Y. Hori und S. Hara,
  [Turing Instability in Reaction-Diffusion Systems with a Single Diffuser](https://arxiv.org/abs/1309.0111),
  2013. Dient als Grenze gegen die Umdeutung raeumlicher Muster in eine
  neue lokale Funktion.

## Bester naechster Schritt

Als naechstes wird fuer das **begrenzte additive konstitutive Gegenfeld** ein
enger Minimal- und Reduzierbarkeitsvertrag formuliert. Er muss ohne konkrete
Gleichung entscheiden, welche Symmetrie-, Bilanz- und Kausalbedingungen die
Rollenart von einer linearen Gegenvariable, dynamischer Erholung und glatter
Hysterese unterscheidbar machen koennten. Bleibt danach kein pruefbarer Rest,
wird R1 geschlossen, bevor Code oder Versuche entstehen.
