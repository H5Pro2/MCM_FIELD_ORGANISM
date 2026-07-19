# Minimaler räumlicher Zustandsvertrag des Kontaktmaterials

## Zweck

Die reine Materialmenge pro Oberfläche kann keine räumliche Berührung
darstellen. Der nächste Vertrag bestimmt deshalb die kleinste zusätzliche
Geometrie, noch ohne Bewegung, Wachstum oder Feldwirkung.

Gesucht wird ein Zustand, der unterscheiden kann:

```text
Material ist ungebunden
Material liegt zurückgezogen in einer lokalen Richtung
Material nähert sich der lokalen Grenzfläche
Material erreicht die Grenzfläche
Material zieht sich wieder zurück
```

## Nicht gewählte Darstellungen

### Nur eine Ausdehnungszahl

Ein einzelner Wert `extent` pro Richtung wäre kompakt, legt aber bereits fest,
dass jede Materialform zusammenhängend und vollständig durch ihre größte
Reichweite beschrieben ist.

Er könnte innere Lücken, getrennte lokale Materiallagen oder eine
Massenverteilung entlang der Richtung nicht unterscheiden. Zusammen mit einer
Kontaktgrenze würde er leicht zu einem neuen Richtungsgewicht.

Diese Darstellung wird nicht gewählt.

### Identifizierte Partikel

Einzelne Partikel mit dauerhafter ID wären räumlich offen, würden aber neue
technische Identitäten und eine potenziell stark wachsende Zustandsmenge
einführen.

Partikelhistorien könnten unbeabsichtigt selbst zum Memory werden.

Diese Darstellung wird nicht gewählt.

### Vollständige mehrdimensionale Dichte

Ein freies Materialfeld um jedes Neuron wäre darstellungsoffen, aber für die
erste notwendige Unterscheidung zu groß. Es würde zusätzliche laterale
Nachbarschaft, Auflösung, Randbedingungen und numerische Transportphysik
erzwingen.

Diese Darstellung wird vorerst nicht gewählt.

## Gewählte minimale Zustandsklasse

Jede bereits vorhandene lokale Oberflächenrichtung erhält ein
**eindimensionales radiales Materialprofil**.

```text
MCM-Neuron i
├── ungebundenes Material u_i
└── Richtung r
    └── radiales Profil rho_i,r(q)
```

`q` ist eine normierte eigentümerlokale Raumkoordinate:

```text
q = 0    neuronennaher Ursprung der Richtung
0 < q < 1    Material innerhalb der lokalen Richtung
q = 1    geometrische Grenzfläche zum vorhandenen Nachbarraum
```

Das Profil beschreibt Materialmenge nach lokaler Reichweite. Es besitzt keine
Partner- oder Beziehungsidentität.

## Materialbilanz

Für jedes Neuron bleibt die bestehende Eigentümerbilanz erhalten:

```text
M_i =
u_i
+ Summe_r Integral rho_i,r(q) dq
```

In einer endlichen digitalen Darstellung wird das Integral durch eine
vollständig ausgewiesene räumliche Diskretisierung ersetzt.

Fest gilt:

- alle Materialmengen sind nichtnegativ;
- die Gesamtmenge `M_i` bleibt unverändert;
- Material wechselt nicht zwischen Neuronen;
- räumliche Profile teilen sich dieselbe endliche Eigentümermenge;
- leere Profile reservieren keine spätere Beziehung.

## Geometrische Grenzfläche

Die Grenze `q = 1` ist keine gelernte Schwelle. Sie ist die normierte
räumliche Außengrenze des Eigentümerbereichs in einer vorhandenen lokalen
Richtung.

Eine Richtung besitzt nur dann eine mögliche Gegenfläche, wenn die bestehende
MCM-Geometrie dort tatsächlich einen lokalen Feldträger enthält.

```text
Neuron i an Position p
+ lokale Richtung r
-> möglicher Nachbarraum bei p + r
```

Die Geometrie kann diesen Raum bestimmen, ohne seine Neuronen-ID im
Materialzustand zu speichern.

## Geometrische Berührung

Eine mögliche Berührung setzt voraus:

```text
Material von i erreicht seine Grenzfläche in Richtung r
und
Material der gegenüberliegenden Seite erreicht deren Grenzfläche -r
```

Der Vertrag speichert daraus keine Kante.

Noch nicht bestimmt werden:

- eine Kontaktstärke;
- ein Kopplungsgewicht;
- eine Feldwirkung;
- ein Sender oder Empfänger;
- eine Stabilisierung;
- eine semantische Bedeutung.

Berührung ist zunächst nur eine aus zwei getrennten Eigentümerprofilen
ableitbare geometrische Beobachtung.

## Rückzug und Lösung

Wenn Grenzflächenmaterial wieder in den eigentümerlokalen Innenraum gelangt,
liegt geometrisch keine Berührung mehr vor.

Damit wird erstmals darstellbar:

```text
Material bleibt vollständig erhalten
aber
lokale Berührung endet durch räumliche Trennung
```

Es wird kein Gewicht gelöscht und kein Beziehungszustand zurückgesetzt.

Ob und wodurch Material tatsächlich zurückweicht, bleibt eine spätere
Materialdynamik.

## Endliche digitale Darstellung

Die Runtime kann keine kontinuierliche Funktion speichern. Eine spätere
technische Umsetzung benötigt deshalb endlich viele normierte Stützbereiche
pro Richtung.

Der Zustandsvertrag legt dafür nur fest:

- die Stützbereiche sind für alle Neuronen gleich;
- ihre räumliche Reihenfolge ist explizit;
- der letzte Bereich liegt an der Grenzfläche;
- die Auflösung ist technische Geometrie, keine Lernstufe;
- die Gesamtmaterialmenge bleibt unabhängig von der Auflösung erhalten;
- keine Zelle besitzt Bedeutung oder Partneridentität;
- jeder Zustand bleibt vollständig snapshotfähig.

Die konkrete Anzahl radialer Bereiche wird noch nicht bestimmt.

## Symmetrie

Unter Spiegelung oder Achstausch müssen:

- Eigentümerposition;
- lokale Richtung;
- radiale Profilwerte;
- mögliche Gegenfläche

gemeinsam transformiert werden.

Die radiale Koordinate selbst bleibt dabei unverändert:

```text
q bleibt q
r wird transformiert
```

Eine bevorzugte Welt- oder Sensorrichtung darf nicht im Profilvertrag liegen.

## Neutralzustand

Der neutrale Zustand lautet:

```text
u_i = M_i
rho_i,r(q) = 0 für alle Richtungen und radialen Bereiche
```

Damit existiert:

- kein Grenzflächenmaterial;
- keine geometrische Berührung;
- keine Kontaktwirkung;
- keine vorgegebene Topologie.

Der Aufbau des räumlichen Zustands darf diesen Neutralzustand nicht verändern.

## Verhältnis zum bisherigen Oberflächenmaterial

Das bisherige `surface_material` entspricht nur der Gesamtmenge eines
radialen Profils:

```text
s_i,r = Integral rho_i,r(q) dq
```

Es bleibt als Bilanzgröße ableitbar, ist aber nicht mehr die vollständige
Morphologie.

Damit wird die vorhandene Arbeit nicht verworfen:

- Eigentümerschaft bleibt bestehen;
- Oberflächenrichtungen bleiben bestehen;
- Materialbilanz bleibt bestehen;
- der passive Ursachenvertrag bleibt nutzbar;
- der Zulassungsrahmen bleibt nutzbar.

## Was weiterhin offen bleibt

Nicht festgelegt sind:

- radiale Auflösung;
- Materialtransport;
- Wachstums- oder Rückzugsgeschwindigkeit;
- Diffusion innerhalb des Profils;
- Reaktion auf Feldfluss;
- Kontaktstabilisierung;
- Kontaktwirkung auf das MCM-Feld;
- Offline-Verhalten;
- Reflexionsrückwirkung.

## Falsifikationsgrenze

Die Zustandsklasse wird zurückgestellt, wenn ihre technische Konkretisierung:

- nur eine Ausdehnungszahl oder ein Gewicht verkleidet;
- dauerhafte Materialelement-IDs benötigt;
- Partneridentitäten speichert;
- Kontakt durch eine frei gewählte Aktivierungsschwelle definiert;
- keine exakte Materialbilanz erlaubt;
- Rückzug nicht von bloßer Amplitudenabschwächung unterscheiden kann;
- bereits beim Aufbau Grenzflächenmaterial erzeugt.

## Status

```text
partnerlose räumliche Zustandsklasse gewählt:       ja
radiales Eigentümerprofil gewählt:                  ja
Materialbilanz erhalten:                            ja
geometrische Grenzfläche definiert:                 ja
Berührung als gespeicherte Kante definiert:         nein
radiale Auflösung bestimmt:                         nein
Materialdynamik bestimmt:                           nein
Feldwirkung freigegeben:                            nein
Runtime-Integration freigegeben:                    nein
```

## Nächster technischer Schritt

Als Nächstes wird ausschließlich die neutrale endliche Anatomie dieses
radialen Profils implementiert.

Sie muss:

- für jede bestehende Oberfläche dieselbe explizite radiale Geometrie tragen;
- sämtliches Material weiterhin ungebunden halten;
- alle Profilbereiche mit null initialisieren;
- keine Berührung, Bewegung oder Feldwirkung erzeugen;
- die alte Oberflächenbilanz exakt rekonstruieren;
- unter Spiegelung äquivalent bleiben.

Erst danach darf eine Transportphysik diskutiert werden.

Diese
[neutrale endliche Profilanatomie](079_NEUTRALE_ENDLICHE_ANATOMIE_DER_RADIALEN_MORPHOLOGIE.md)
ist inzwischen umgesetzt. Die radiale Auflösung bleibt explizit, alle Zellen
beginnen leer und das gesamte Material bleibt ungebunden.
