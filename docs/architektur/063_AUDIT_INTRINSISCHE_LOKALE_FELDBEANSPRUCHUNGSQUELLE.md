# Audit der intrinsischen lokalen Feldbeanspruchungsquelle

## Zweck

Der Kandidatenfamilienaudit ließ ausschließlich die Frage offen, ob die
heutige atomare Feldtransition bereits eine intrinsische lokale
Beanspruchungs- oder Flussgröße bereitstellt. Dieser Audit liest die
vorhandene Mechanik. Er ergänzt weder Zustand noch Gleichung.

## Geprüfter Übergangspfad

Ein `MCMNeuronDrive` enthält:

- den abgeschlossenen vorherigen Neuronenzustand;
- den nächsten lokalen Rezeptorkontakt;
- lokale Aktivierungs- und Nachhallproben aus dem abgeschlossenen Vortakt;
- die gemeinsame Schrittzeit und gegebenenfalls transiente Rezeptoreingänge.

Ein `MCMNeuronOutput` enthält ausschließlich:

- `activation`;
- `afterimage`.

Die nächste Schicht wird atomar aus demselben abgeschlossenen Vortakt
gebildet. Es existiert kein öffentlicher Zustand für Gradient, Kantenfluss,
Divergenz, Übergangsarbeit oder Feldspannung.

## Bereits vorhandene lokale Feldwirkung

Das neutrale Substrat bildet aus der festen symmetrischen Nachbarschaft die
lokale Diffusionswirkung. Für benachbarte Neuronen kann ihr momentaner
gerichteter Anteil geschrieben werden als:

```text
J(j -> i, t) = r * (activation(j, t) - activation(i, t))
```

mit der technisch vorgegebenen Reaktionsrate `r`. Die Summe dieser Anteile am
Neuron ist genau der bereits verwendete lokale Diffusionsterm:

```text
D(i, t) = Summe_j J(j -> i, t)
```

Rezeptorkontakt ergänzt eine feste Randwirkung. Die exakte Integration
schreibt daraus die nächste Aktivierung. Der Nachhall bleibt eine feste
schnelle Spur dieser Aktivierung.

Damit besitzt das Feld bereits einen realen momentanen lokalen Fluss. Dieser
Fluss ist keine nachträgliche Bezeichnung durch einen Observer.

## Informationsgrenze

Der momentane Fluss trägt jedoch keine zusätzliche Information. Er ist
vollständig bestimmt durch:

```text
aktuelle Aktivierung
+ feste Nachbarschaft
+ feste Reaktionszeit
```

Gradient, gerichteter Fluss, Knotendivergenz und jede punktweise daraus
gebildete Größe sind deshalb nur verschiedene Darstellungen desselben
schnellen Feldzustands.

Werden `activation` und `afterimage` zweier Zweige angeglichen, stimmen bei
gleicher Anatomie auch alle momentanen Fluss- und Gradientengrößen überein.
Eine frühere unterschiedliche Feldbeanspruchung bleibt darin nicht erhalten.

## Warum daraus noch kein Mediumzustand folgt

Eine über Zeit integrierte Beanspruchung könnte Geschichte tragen. Ihre
Einführung würde aber mindestens drei neue Festlegungen verlangen:

1. welche Flussform integriert wird, etwa Vorzeichen, Betrag oder Quadrat;
2. wie sie erhalten, begrenzt und gelöst wird;
3. wie sie die spätere Feldtransition wieder beeinflusst.

Das wäre bereits eine neue Spur samt Leserfunktion. Ohne vorher nachgewiesenen
Funktionsmangel wäre sie nur ein anders benannter Integrator und fiele in die
bereits verworfenen Familien F1 oder F5 zurück.

## Ergebnis für F8

Die für F8 benötigte Beanspruchungsquelle ist nur teilweise vorhanden:

```text
momentane lokale Feldwirkung:                 vorhanden
vor Observer kausal wirksam:                  ja
aus lokalem Welt- und Feldkontakt entstanden: ja
eigenständiger Informationsgehalt:            nein
geschichtlich fortbestehende Beanspruchung:   nein
natürliche Lösung und erneute Prägung:         nicht prüfbar
```

Der momentane Fluss rechtfertigt daher keinen hysteretischen Mediumzustand.
F8 bleibt geschlossen.

## Passive Nullprüfung vor jeder weiteren Öffnung

Zulässig ist ausschließlich eine passive Redundanzprüfung ohne Akkumulation
und ohne Rückwirkung. Sie soll:

1. gerichtete Nachbarflüsse aus einem abgeschlossenen Feldzustand ableiten;
2. ihre Summe gegen den vorhandenen Diffusionsterm prüfen;
3. die Rekonstruktion aus den öffentlichen lokalen Feldproben prüfen;
4. zeigen, dass angeglichene schnelle Zustände identische Flussgrößen liefern;
5. Observer-Reihenfolge und fehlende Rückschreibung kontrollieren.

Ein positiver Identitätsbefund bestätigt nur die Redundanzgrenze. Er gibt
weder Memory noch Hysterese frei.

## Aussagegrenze

Dieser Audit trägt:

- den Nachweis einer bereits vorhandenen momentanen lokalen Diffusionswirkung;
- ihre vollständige Ableitbarkeit aus schnellem Zustand und fester Anatomie;
- die fehlende geschichtliche Fortdauer nach Zustandsangleichung;
- die geschlossene F8- und Runtime-Grenze.

Er trägt nicht:

- ein neues Feldsubstrat;
- organisches Memory;
- natürliche Lösung oder Wiederbindung;
- semantische Resonanz;
- Feldintelligenz.

## Freigabegrenze

```text
intrinsischer momentaner Fluss bestätigt: ja
unabhängige Beanspruchungsrolle bestätigt: nein
F8-Kandidat zugelassen:                   nein
neue Zustandsrolle freigegeben:           nein
Runtime-Erweiterung freigegeben:          nein
passive Redundanz-Nullprüfung zulässig:    ja
```

## Ergebnis der passiven Nullprüfung

Der
[Redundanzbefund des instantanen Feldflusses](../forschung/009_INSTANTANER_FELDFLUSS_REDUNDANZBEFUND.md)
bestätigt alle vorregistrierten Identitäten. Kantenfluss, lokale Divergenz und
vorhandener Diffusionsgenerator sind bis auf numerisches Rundungsrauschen
identisch. Der Observer ist reihenfolgeinvariant und verändert den Quelldigest
nicht.

## Nächster Schritt

Als Nächstes wird keine Flussspur ergänzt. Zuerst wird konzeptionell geprüft,
ob die feste Diffusionsanatomie selbst natürliche Lösung und Wiederbindung
ausschließt. Feldruntime und Zustandsrollen bleiben geschlossen.
