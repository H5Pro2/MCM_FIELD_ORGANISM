# Grenze eines isolierten lokalen Substratzustands

## Fragestellung

Die physische Mindestanforderung verlangt begrenzte, lokal feldgetriebene und
funktional reversible Pfadabhängigkeit. Dieser Audit prüft die kleinste
denkbare digitale Darstellung:

```text
ein begrenzter skalarer Substratzustand m pro lokalem Ort
+ nur eigene lokale Feldursache u
+ zeitinvariante neutrale Fortschreibung F
+ lokale Rückwirkung G auf das Feld
```

Formal:

```text
m(t+1) = F(m(t), u(t))
y(t)   = G(m(t), x(t))
```

`x` ist die aktuelle Feldlage, `u` eine bereits vorhandene lokale
Feldwirkung und `y` die mögliche Mitprägung der nächsten Feldtransition.

Geprüft wird zunächst ein **isolierter** lokaler Zustand. Eine Kopplung
mehrerer Substratorte ist nicht Bestandteil dieser Klasse.

## Was ein einzelner Zustand grundsätzlich kann

Ein Skalar kann ohne Objekt- oder Partnerkennung:

- verschiedene vergangene Beanspruchungen unterscheiden;
- begrenzt bleiben;
- spätere lokale Feldwirkung verändern;
- unter anderer Beanspruchung erneut verändert werden.

Damit ist ein einzelner Zustand nicht grundsätzlich speicherunfähig.

Die strengere Frage lautet jedoch:

> Kann er robuste Prägung, vollständige funktionale Lösung und erneute
> Prägbarkeit tragen, ohne nur eine bekannte Spur oder einen programmierten
> Zustandsautomaten darzustellen?

## Fall A - Glatte kontraktive Fortschreibung

Wenn unterschiedliche Zustände unter fehlender oder veränderter Beanspruchung
nur kontrahieren, gilt typischerweise:

```text
|m1(t+1) - m2(t+1)| < |m1(t) - m2(t)|
```

Die Geschichtsdifferenz wird kleiner, erreicht bei einer glatten injektiven
Fortschreibung aber nicht robust nach endlicher Zeit exakt dieselbe Lage.

Das ergibt:

- graduelle Abschwächung;
- asymptotische Annäherung;
- erneute Prägbarkeit.

Es ergibt keine robuste vollständige funktionale Lösung. Mechanisch ist diese
Klasse eine lineare oder nichtlineare Leaky-Spur.

## Fall B - Nicht injektive Zustandskollision

Exakte Zustandsangleichung in endlicher Zeit wird möglich, wenn verschiedene
alte Zustände durch `F` auf denselben neuen Zustand fallen.

Beispiele sind:

- Clipping;
- Quantisierung;
- Sättigungsrand;
- Projektion auf einen festen Bereich;
- explizite Nullsetzung.

Damit ist vollständige Lösung technisch möglich. Die Kollisionsgrenze ist
jedoch bereits Teil der programmierten Fortschreibung. Ohne eine allgemeine
physische Begründung legt sie fest, wann Unterschiede verschwinden.

Diese Klasse ist ein Sättigungs- oder Löschautomat.

## Fall C - Funktionale Null durch den Leser

Der Zustand kann verschieden bleiben, während `G` seine Wirkung unterdrückt:

```text
m1 != m2
aber
G(m1, x) = G(m2, x)
```

Für robuste vollständige Lösung über die zulässigen späteren Proben muss `G`
einen ganzen Zustandsbereich funktional gleich behandeln.

Das ist möglich durch:

- Totzone;
- Schwelle;
- Gate;
- feste Äquivalenzklasse;
- Multiplikation mit einem externen Nullsignal.

Die Lösung liegt dann in einer programmierten Leserform und nicht in einer
natürlich gelösten Substratwirkung.

## Fall D - Bistabilität oder mehrere Attraktoren

Mehrere stabile Lagen können dauerhafte Prägung tragen. Der Wechsel zwischen
ihnen benötigt aber:

- fest vorgegebene Attraktorlagen;
- eine Separatrix oder Schwelle;
- eine definierte Umschaltbedingung.

Damit werden mögliche Zustandsklassen und ihre Lösungsgrenzen bereits in die
Materialgleichung geschrieben. Zusätzlich drohen absorbierende oder nur
schwer erneut prägbare Lagen.

Diese Klasse kann technisch leistungsfähig sein, bleibt aber ein
vorstrukturierter Zustandsautomat.

## Fall E - Monotoner oder sättigender Integrator

Ein begrenzter Integrator kann wiederholte Beanspruchung akkumulieren und
später zurückwirken. Ohne Gegenwirkung kann er alte Prägung nicht vollständig
lösen. Mit festem Zerfall fällt er auf Fall A zurück. Mit Clip oder Schwelle
fällt er auf Fall B oder C zurück.

Er erfüllt deshalb nicht eigenständig den vollständigen Lebenszyklus.

## Enger Negativnachweis

Unter den geprüften Bedingungen gilt:

```text
ein isolierter begrenzter Skalar
-> kann Pfadabhängigkeit tragen
-> bleibt bei glattem Zerfall nur asymptotisch lösbar
-> erreicht endliche funktionale Lösung nur durch
   Zustandskollision oder Leseräquivalenz
```

Diese drei Wege sind bereits bekannte Gegenmodelle:

```text
asymptotischer Zerfall -> Leaky-Spur ohne vollständige endliche Lösung
Zustandskollision      -> Clip-/Schwellenautomat
Leseräquivalenz        -> feste Leserwirkung
```

Ein isolierter lokaler Skalar kann daher keinen neuen
Memory-Substratbefund oberhalb der bestehenden Baselines begründen.

## Aussagegrenze

Dieser Audit ist kein allgemeiner mathematischer Beweis gegen jeden
eindimensionalen nichtlinearen Filter. Ein passend konstruierter Filter kann
jede gewünschte endliche Prüfsequenz erfüllen.

Genau darin liegt die methodische Grenze: Seine gewünschte Lösung und
Wiederprägung wären dann in `F` oder `G` konstruiert und nicht als offene
Feldorganisation entdeckt.

Der Negativnachweis gilt deshalb für die Projektfrage:

> Ein isolierter skalarer Zustand liefert keine darstellungsoffene Erklärung
> organischen Memorys, die über bekannte Spur- und Automatenbaselines
> hinausgeht.

## Was daraus nicht folgt

Nicht gezeigt ist:

- dass digitales organisches Memory unmöglich ist;
- dass mehrere willkürliche Zustandsvariablen ergänzt werden müssen;
- dass adaptive Kanten nötig sind;
- dass ein neuronaler Gewinnermechanismus nötig ist;
- dass ein räumlich gekoppeltes homogenes Substrat scheitert.

Der letzte Punkt ist entscheidend. Viele gleichartige lokale
Substratfreiheitsgrade können gemeinsam eine verteilte Feldlage bilden, ohne
einzelne Beziehungskanten zu speichern. Diese Gesamtklasse ist nicht mehr
eindimensional, obwohl an jedem Ort derselbe lokale Typ liegt.

## Verhältnis zum gemeinsamen MCM-Feld

Das heutige Feld besitzt bereits viele gleichartige lokale Aktivierungs- und
Nachhallzustände. Ihre Kopplung ist jedoch linear und ihre Zeitrollen bleiben
schnell beziehungsweise fest leaky.

Eine mögliche verteilte Substratklasse müsste deshalb:

- im selben gemeinsamen Feld liegen;
- an jedem Ort denselben neutralen Zustandstyp verwenden;
- nur lokale Feld- und Substratnachbarschaft lesen;
- keine expliziten Beziehungskanten besitzen;
- ihre Organisation als räumliche Gesamtform tragen;
- dennoch vollständige funktionale Lösung und erneute Prägbarkeit erlauben.

Dies ist nur eine neue Prüfklasse, keine Freigabe ihrer Implementierung.

## Freigabegrenze

```text
isolierter lokaler Skalar geprüft:           ja
Pfadabhängigkeit grundsätzlich möglich:      ja
neuer Befund oberhalb Leaky/Automat/Leser:    nein
isolierter Skalarkandidat zugelassen:         nein
verteilte homogene Substratklasse geprüft:    nein
zusätzliche Zustandsrolle freigegeben:        nein
Runtime-Erweiterung freigegeben:               nein
```

## Nächster Schritt

Als Nächstes wird ausschließlich die verteilte homogene Substratklasse
konzeptionell abgegrenzt:

```text
gleicher lokaler Substrattyp an jedem MCM-Ort
+ lokale Kopplung
+ keine Kantenidentität
+ keine Zieltopologie
-> kann eine lösbare räumliche Organisationslage überhaupt entstehen?
```

Noch wird weder Zustandsdimension noch Gleichung gewählt.
