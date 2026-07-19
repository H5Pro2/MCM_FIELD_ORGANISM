# Anatomischer Zustandsvertrag des Kontaktsubstrats

## Umgesetzte Grenze

Die in Architektur 071 gewählte Hypothese besitzt jetzt einen technischen
Anatomievertrag außerhalb der Organismus-Runtime.

Der Vertrag besteht aus:

```text
ContactMaterialLayerState
└── NeuronContactMaterialState
    ├── Eigentümer: genau ein MCM-Neuron
    ├── ungebundenes Kontaktmaterial
    └── LocalContactSurface je lokaler Raumrichtung
```

Eine Oberfläche kennt nur ihre relative Position und ihre Materialmenge. Sie
kennt keinen Partner, keine Kante und keine Bedeutung.

## Ableitung aus der bestehenden MCM-Anatomie

Die vorhandene MCM-Neuronenschicht besitzt bereits lokale räumliche
`sample_offsets`. Diese Richtungen werden wiederverwendet, ohne daraus
Verbindungen abzuleiten.

In der kontrollierten Audio-Video-Welt gilt:

```text
MCM-Neuronen                         84
lokale Richtungen pro Neuron         4
neutrale Oberflächenplätze         336
gespeicherte Beziehungen             0
```

Die `336` Oberflächenplätze sind keine Kanten. Auch eine Richtung, an der
gegenwärtig kein anderes Neuron liegt, bleibt nur eine lokale anatomische
Möglichkeit des Eigentümers.

## Neutralzustand

Beim Aufbau gilt für jedes Neuron:

```text
gesamtes endliches Material = ungebundenes Material
Material an jeder Oberfläche = 0
```

Der Vertrag prüft die vollständige Materialbilanz:

```text
ungebunden
+ Summe aller Oberflächenmengen
= Gesamtmaterial
```

Damit ist Material endlich und vollständig snapshotfähig. Der Neutralzustand
erzeugt keine Feldwirkung.

## Was bewusst fehlt

Nicht implementiert sind:

- Materialtransport;
- Wachstum oder Rückzug;
- Kopplung zweier Oberflächen;
- Partner- oder Beziehungsidentität;
- Gewichte;
- zeitliche Prägung;
- Stabilisierung;
- Lösung oder Wiederbindung;
- Runtime-Rückwirkung;
- Semantik und Sprache.

Der Vertrag besitzt keine `advance`-, `couple`- oder `field_effect`-Funktion.
Das bestehende gemeinsame MCM-Feld wird beim Aufbau weder verändert noch
erweitert.

## Unterschied zum verworfenen Kandidaten

Der frühere passive Synapsenkandidat erzeugte sofort Zustände für alle 290
gerichteten lokalen Beziehungen.

Der neue Anatomievertrag erzeugt:

```text
84 Eigentümerzustände
+ je 4 partnerlose lokale Oberflächen
+ vollständig ungebundenes Material
```

Es existiert damit noch keine Beziehung, die nur verstärkt werden müsste.

## Evidenzgrenze

Der Vertrag zeigt:

- strukturelles Kontaktmaterial kann technisch einem Neuron gehören;
- räumliche Lokalisation benötigt keine Partner-ID;
- endliche Materialbilanz ist ohne globalen Gewinner darstellbar;
- der neutrale Aufbau verändert die Feldruntime nicht.

Er zeigt nicht:

- dass Material sich organisch umverteilt;
- dass eine Berührung entsteht;
- dass eine Berührung Feldwirkung trägt;
- dass Struktur stabilisiert, gelöst oder neu gebunden wird;
- dass organisches Memory vorliegt.

## Status

```text
anatomischer Zustandsvertrag umgesetzt:       ja
neutrale Initialisierung umgesetzt:           ja
Materialbilanz geprüft:                       ja
Partner- oder Kantenidentität vorhanden:      nein
Materialdynamik vorhanden:                    nein
Feldwirkung vorhanden:                        nein
Runtime-Integration vorhanden:                nein
```

## Nächster Schritt

Vor einer Dynamik muss die lokale Schreibursache exakt zugeordnet werden.

Zu trennen sind mindestens:

```text
gegenwärtige Eigenaktivität
lokale Nachbarwirkung
gerichtete zeitliche Feldänderung
reale Rezeptorwirkung
```

Gesucht wird nicht die Kombination, die gewünschte Beziehungen erzeugt.
Geprüft wird, welche dieser Ursachen bereits am einzelnen Neuron lokal und
kausal vorliegt, ohne erst durch einen nachträglichen Observer konstruiert zu
werden.
