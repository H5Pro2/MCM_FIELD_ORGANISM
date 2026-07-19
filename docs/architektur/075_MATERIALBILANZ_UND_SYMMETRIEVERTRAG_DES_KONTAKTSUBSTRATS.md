# Materialbilanz und Symmetrievertrag des Kontaktsubstrats

## Entscheidung

Bevor eine Materialdynamik entsteht, werden nur ihre unverletzbaren
physikalischen Grenzen festgelegt.

Diese Grenzen sollen verhindern, dass eine spätere Regel:

- Material aus dem Nichts erzeugt;
- Beziehungen direkt speichert;
- eine bevorzugte Richtung oder Sinnesart erhält;
- über einen globalen Gewinner organisiert wird;
- Lösung und Wiederbindung als Befehle ausführt.

Der Vertrag bestimmt noch nicht, wann oder wohin sich Material bewegt.

## Lokale Materialbilanz

Für jedes MCM-Neuron `i` gilt:

```text
M_i = u_i + Summe_r s_i,r
```

Dabei sind:

- `M_i`: die feste gesamte Materialmenge des Neurons;
- `u_i`: sein gegenwärtig ungebundenes Material;
- `s_i,r`: Material an seiner Oberfläche in lokaler Richtung `r`.

Für jeden atomaren Übergang muss gelten:

```text
Delta u_i + Summe_r Delta s_i,r = 0
```

Zusätzlich:

```text
u_i >= 0
s_i,r >= 0
```

Eine Oberfläche kann deshalb nur Material erhalten, das beim selben Neuron
an anderer Stelle nicht mehr gleichzeitig verfügbar ist.

## Keine Übertragung zwischen Eigentümern

Kontaktmaterial wechselt nicht von einem Neuron zu einem anderen.

```text
M_i(t+1) = M_i(t)
```

Eine spätere Berührung zweier Neuronen wäre die räumliche Begegnung ihrer
jeweils eigenen Oberflächen. Sie wäre kein gemeinsamer Materialtopf und keine
Übertragung eines Gewichts.

Diese Grenze erhält:

- lokale Eigentümerschaft;
- endliche Konkurrenz innerhalb eines Neurons;
- unabhängige Lösbarkeit beider Seiten;
- erneute Verfügbarkeit nach Rückzug.

## Atomare Zeit

Alle Materialvorschläge eines Taktes müssen aus demselben abgeschlossenen
Vorzustand entstehen.

```text
Material(t)
+ Feldursachen(t)
-> vollständiger Vorschlag für t+1
-> gemeinsame Prüfung
-> atomarer Materialzustand(t+1)
```

Eine früh berechnete Oberfläche darf keine später berechnete Oberfläche
desselben Taktes beeinflussen. Iterationsreihenfolge darf daher kein
Ergebnis verändern.

## Symmetrie der Naturregel

Jedes MCM-Neuron muss derselben lokalen Materialregel folgen.

Die Regel darf nicht lesen:

- Neuronennummer;
- absolute Position als Rang;
- Modalität;
- Kamera- oder Mikrofonherkunft;
- Bedeutung oder Klasse;
- Zieltopologie;
- gewünschte Bewegungsrichtung.

Wird eine vollständige lokale Situation gespiegelt, gedreht oder in anderer
technischer Reihenfolge dargestellt, muss sich die Materialantwort
entsprechend mittransformieren.

```text
F(Transformation(Zustand, Ursache))
=
Transformation(F(Zustand, Ursache))
```

Das ist **Äquivarianz**, nicht Gleichförmigkeit.

Die Außenwelt darf asymmetrische Ursachen erzeugen. Eine Bewegung von links
nach rechts kann deshalb eine andere räumliche Materiallage tragen als die
umgekehrte Bewegung. Verboten ist nur eine im Code bevorzugte Richtung.

## Gegenseitigkeit ohne erzwungene Gleichheit

Zwei benachbarte Neuronen besitzen gegenüberliegende lokale Oberflächen.

```text
Oberfläche von i in Richtung r
Oberfläche von j in Richtung -r
```

Der Vertrag erzwingt nicht:

- gleiche Materialmengen;
- gleichzeitiges Wachstum;
- automatische Kopplung;
- Sender- und Empfängerrollen;
- einen gespeicherten Paarzustand.

Eine spätere funktionale Berührung darf erst beobachtet werden, wenn beide
lokalen Seiten aufgrund ihrer eigenen Geschichte räumlich wirksam sind.
Wie diese gemeinsame Wirksamkeit gelesen wird, bleibt offen.

## Neutraler Nullzustand

Im vollständig neutralen Anfangszustand gilt:

```text
u_i = M_i
s_i,r = 0
```

Wenn zugleich keine lokale Feldursache vorliegt, muss dieser Zustand neutral
bleiben. Sonst würde die technische Initialisierung ohne Weltgeschichte
bereits Struktur erzeugen.

Diese Nullinvarianz bedeutet nicht, dass jede später entwickelte Lage ohne
Weltkontakt unverändert bleiben muss. Relaxation, Stabilisierung und Lösung
sind spätere offene Fragen.

## Reale Zeit statt Schrittzahl

Eine spätere Materialregel muss auf der gemeinsamen Organismuszeit beruhen.
Sie darf nicht davon abhängen, wie oft ein technischer Runner denselben
physischen Zeitraum unterteilt.

Vor Freigabe muss deshalb gelten:

```text
gleiche Weltwirkung über gleiche reale Dauer
+ feinere oder gröbere zulässige Taktung
-> physikalisch vergleichbare Materialentwicklung
```

Eine feste Anzahl von Wiederholungen ist kein biologischer oder organischer
Entwicklungsgrund.

## Lösung und Wiederbindung

Der Bilanzvertrag definiert keine Löschfunktion.

Er verlangt nur:

- zurückgezogenes Oberflächenmaterial wird wieder lokal verfügbar;
- keine alte Oberfläche besitzt reserviertes Material;
- keine Partneridentität bleibt nach vollständiger Lösung bestehen;
- dieselbe endliche Materialmenge kann später andere lokale Form tragen.

Lösung darf später nicht durch Reset, Datenbanklöschung oder globales
Freigabesignal erzeugt werden.

## Fest programmierbare Physik

Fest sein dürfen:

- lokale Eigentümerschaft;
- endliche Gesamtmenge;
- Nichtnegativität;
- lokale Materialerhaltung;
- atomare Zeit;
- geometrische Äquivarianz;
- neutraler Nullzustand;
- Snapshotfähigkeit.

Diese Regeln bestimmen den digitalen Stoff, nicht seine spätere Organisation.

## Nicht fest programmierbare Organisation

Nicht vorgegeben werden dürfen:

- welche Oberfläche gewinnt;
- welche Feldform wichtig ist;
- wie viele Wiederholungen genügen;
- welche Nachbarn sich verbinden;
- welche Beziehung stabil bleibt;
- wann etwas vergessen werden soll;
- welche neue Bindung richtig ist;
- welche Bedeutung entsteht.

## Zulassungsgrenze für eine spätere Dynamik

Eine Materialdynamik darf erst passiv untersucht werden, wenn sie:

1. ausschließlich den vorhandenen lokalen Zustands- und Ursachenvertrag liest;
2. für jedes Neuron die Materialbilanz exakt erhält;
3. keine negativen Materialmengen erzeugt;
4. keine Partner-, Beziehungs- oder Gewinneridentität ergänzt;
5. unter geometrischer Transformation äquivariant bleibt;
6. unabhängig von Neuronen- und Oberflächeniteration ist;
7. den neutralen Nullzustand ohne Feldursache erhält;
8. reale Dauer statt bloßer Schrittzahl berücksichtigt;
9. noch keine Feldrückwirkung besitzt.

Diese Punkte sind notwendige Grenzen, aber kein Nachweis organischer
Entwicklung.

## Status

```text
lokale Materialbilanz definiert:             ja
Eigentümererhaltung definiert:                ja
Nichtnegativität definiert:                   ja
atomare Fortschreibung gefordert:             ja
geometrische Äquivarianz gefordert:            ja
neutraler Nullzustand gefordert:               ja
konkrete Materialdynamik bestimmt:             nein
Berührungsleser bestimmt:                      nein
Runtime-Rückwirkung freigegeben:               nein
organisches Memory gezeigt:                    nein
```

## Nächster technischer Schritt

Als Nächstes wird ein passiver Zulassungsrahmen für
Materialfortschreibungen gebaut.

Er darf eine von außen eingesetzte Kandidatenregel nur gegen Bilanz,
Nichtnegativität, Zeitgrenze und Symmetrie prüfen. Er darf selbst:

- keine Materialbewegung vorschlagen;
- keine Standarddynamik besitzen;
- keinen Kandidaten an die Runtime anschließen;
- keine Kontaktwirkung erzeugen.

Erst innerhalb dieses Rahmens kann später die kleinste neutrale
Umverteilungsdynamik geprüft und bei Verletzung der Grenzen sofort verworfen
werden.

Dieser
[passive Zulassungsrahmen](076_PASSIVER_ZULASSUNGSRAHMEN_FUER_MATERIALFORTSCHREIBUNGEN.md)
ist inzwischen umgesetzt. Er prüft vollständige Kandidatenvorschläge, wendet
sie aber nicht an und gewährt keine Runtime-Freigabe.
