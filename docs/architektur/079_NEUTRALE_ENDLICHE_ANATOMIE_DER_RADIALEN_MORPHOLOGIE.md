# Neutrale endliche Anatomie der radialen Morphologie

## Umsetzung

Der minimale räumliche Zustandsvertrag besitzt jetzt eine technische
Anatomie außerhalb der Organismus-Runtime.

```text
RadialContactMaterialLayerState
└── NeuronRadialMaterialState
    ├── ungebundenes Eigentümermaterial
    └── RadialContactProfile je lokaler Richtung
        └── RadialMaterialCell je normiertem Raumbereich
```

Eine radiale Zelle ist ein anonymer räumlicher Stützbereich. Sie ist kein
Partikel und besitzt keine dauerhafte Identität.

## Explizite Auflösung

Die radiale Geometrie wird beim Aufbau ausdrücklich über ihre Kanten
angegeben:

```text
(0,0; 0,25; 0,5; 0,75; 1,0)
```

Diese Vier-Zellen-Geometrie dient nur dem technischen Nachweis. Die
Builderfunktion besitzt absichtlich keinen Standardwert für die Auflösung.

Damit wird weder behauptet, dass vier Zellen biologisch richtig sind, noch
dass eine spätere Runtime dieselbe Auflösung verwenden muss.

## Neutralzustand

Beim Aufbau gilt:

```text
ungebundenes Material = gesamte Eigentümermenge
Material jeder radialen Zelle = 0
Grenzflächenmaterial = 0
```

Es entstehen:

- keine Materialausdehnung;
- keine Berührung;
- keine Beziehung;
- keine Feldwirkung;
- keine Materialbewegung.

## Kontrollierte Audio-Video-Anatomie

Für die vorhandene kontrollierte Welt ergibt die gewählte technische
Vier-Zellen-Geometrie:

```text
MCM-Neuronen:                 84
lokale Richtungsprofile:     336
radiale Materialzellen:     1344
Zellen mit Material:           0
Grenzflächen mit Material:     0
gespeicherte Beziehungen:      0
```

Sämtliches Material bleibt in den 84 ungebundenen Eigentümeranteilen.

## Erhaltene alte Bilanz

Die bisherige Oberflächenmenge wird aus jedem radialen Profil rekonstruiert:

```text
surface_material(r)
=
Summe der radialen Zellmengen in Richtung r
```

Im Neutralzustand sind beide Seiten exakt null. Die neue Anatomie ersetzt
nicht die Materialbilanz, sondern verfeinert ausschließlich ihre mögliche
räumliche Darstellung.

## Technische Grenzen

Die Umsetzung enthält keine:

- Partikel-ID;
- Partner- oder Beziehungs-ID;
- Ausdehnungsvariable;
- Materialtransportfunktion;
- Wachstums- oder Rückzugsrate;
- Kontaktstärke;
- Feldwirkung;
- Runtime-Integration.

`build_neutral_radial_contact_morphology` akzeptiert nur einen vollständig
neutralen Kontaktmaterialzustand. Ein bereits verteiltes
`surface_material` kann nicht nachträglich willkürlich in ein räumliches
Profil umgedeutet werden.

## Verifikation

Die fokussierten Prüfungen bestätigen:

- exakte Eigentümer- und Materialbilanz;
- 336 Profile und 1344 leere radiale Zellen;
- identische radiale Geometrie in allen Richtungen;
- leere Grenzflächen;
- exakte Rekonstruktion der alten Oberflächenbilanz;
- Reproduzierbarkeit und Snapshotfähigkeit;
- unveränderte Kontaktanatomie und unverändertes MCM-Feld;
- fehlenden versteckten Auflösungsstandard.

## Status

```text
neutrale radiale Anatomie umgesetzt:       ja
Auflösung explizit erforderlich:           ja
Materialprofile initial leer:              ja
Grenzflächenmaterial vorhanden:            nein
geometrische Berührung vorhanden:          nein
Materialtransport vorhanden:               nein
Feldwirkung vorhanden:                     nein
Runtime-Integration vorhanden:             nein
```

## Nächster Schritt

Vor jeder Transportgleichung muss die räumliche Zeitgrenze geklärt werden:

> Welche Transportklasse kann endliches Eigentümermaterial entlang eines
> radialen Profils bewegen, ohne eine gespeicherte Spur, feste Zielposition,
> Schwelle oder technisch bevorzugte Grenzfläche zu erzeugen?

Zuerst werden konservative Transportklassen abgegrenzt. Noch wird keine
Materialbewegung implementiert.

Diese
[Abgrenzung konservativer radialer Transportklassen](080_ABGRENZUNG_KONSERVATIVER_RADIALER_TRANSPORTKLASSEN.md)
lässt ausschließlich endliche konservative Advektion als ersten passiven
Morphologiekandidaten offen. Eine Geschwindigkeit oder Materialbewegung ist
damit noch nicht freigegeben.
