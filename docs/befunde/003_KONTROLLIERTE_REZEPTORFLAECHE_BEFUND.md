# Befund 003: Kontrollierte lokale Rezeptorfläche

## 1. Bezug

Ausgeführt wurde
[Methodik 003](../methodik/003_KONTROLLIERTE_REZEPTORFLAECHE.md).

Geprüft wurde eine kontrollierte 3×3-Fläche mit direkter lokaler
Rezeptor-Träger-Zuordnung. Zwischen den neun Positionen existiert keine
Wechselwirkung.

## 2. Implementierter Umfang

Implementiert wurden:

- neun stabile technische Positionsidentitäten,
- direkte Eins-zu-eins-Abbildung lokaler Kontakte,
- B0 als zustandslose Fläche,
- B1 als neun unabhängige Leaky-Spuren,
- B2 als globale Summenbaseline,
- räumliche Verschiebungsprüfung,
- exakte Zustandsvergleiche ohne Klassifikator.

Nicht implementiert wurden:

- Nachbarschaft oder Diffusion,
- räumliche Faltung,
- Muster- oder Bewegungserkennung,
- globale Feldauslese,
- MCM-Dynamik,
- Handlung oder Lernen.

## 3. Ausführung

```text
python -m unittest -v tests.test_controlled_receptor_surface
```

Ergebnis:

```text
15 Tests
15 bestanden
0 Fehler
0 Fehlschläge
```

Die zeitlichen Prüfungen verwendeten erneut:

```text
tau in {0.25, 1.0, 4.0}
dt  in {1.0, 0.5, 0.25}
```

## 4. Getragene Informationsbefunde

### F1: Positionsidentität getragen

Jeder Einzelkontakt erscheint ausschließlich an seiner zugeordneten Position.
Nie kontaktierte Positionen bleiben auch dann null, wenn eine direkt daneben
liegende Position Kontakt und Nachhall trägt.

### F2: Verteilungserhalt getragen

Benachbarte und getrennte Kontakte mit gleicher Gesamtenergie bleiben im
vollständigen Positionsvektor verschieden.

Die globale B2-Summe lässt dagegen absichtlich verschiedene räumliche
Verteilungen kollidieren. Der Informationsverlust entsteht somit durch die
Summation, nicht durch fehlende Trägerkopplung.

### F3: Richtungsspur im verteilten Nachhall getragen

Horizontale Vorwärts- und Rückwärtsfolgen erzeugen nach Ende des aktuellen
Kontakts über alle neun `tau`/`dt`-Kombinationen verschiedene
Nachhallverteilungen.

Es wurde keine Richtung erkannt. Der passive Observer stellt lediglich fest,
dass die vollständigen Zustandsvektoren verschieden sind.

### F4: Lokale Vorgeschichte im Gesamtzustand getragen

Zwei Folgen erreichen dieselbe mittlere Endposition aus entgegengesetzten
Richtungen. Gegenwartsaktivierung und lokaler Nachhall am Mittelpunkt sind
identisch; die übrige Flächenlage bleibt verschieden.

Damit trägt nicht der einzelne Zielträger, wohl aber die Gesamtheit
unabhängiger lokaler Spuren den Unterschied.

### F5: Translationsentsprechung getragen

Dieselbe Kontaktfolge in einer anderen Zeile erzeugt nach technischer
Rückverschiebung exakt dieselben lokalen Werte. Es wurde keine inhaltliche
Vorzugsposition gefunden.

### F6: Keine Ausbreitung bestätigt

Kontaktwirkung bleibt vollständig auf bereits kontaktierte Positionen
beschränkt. Die Fläche besitzt kein internes Weiterleitungs- oder
Überlagerungsvermögen.

### F7: Geschichtskollision bestätigt

Verschiedene Kontaktgeschichten wurden über alle neun Parameterkombinationen
auf exakt dieselbe vollständige Endlage gebracht:

```text
Geschichte A: Kontakt 1, dann 0, dann 0
Geschichte B: 0, dann Kontakt d, dann 0
d = exp(-dt / tau)
```

Nach der Kollision kann B1 die frühere Differenz nicht mehr tragen. Diese
Grenze ist dieselbe Einspurkompression wie in Befund 002, nun auf der gesamten
Fläche.

## 5. Zentrale Entscheidung

Für die registrierten passiven Funktionen wurde kein Informationsmangel
gefunden, der lokale Wechselwirkung benötigt.

Unabhängige Träger erhalten bereits:

- aktuelle Position,
- vollständige räumliche Verteilung,
- begrenzte lokale Vorgeschichte,
- Vorwärts-/Rückwärtsunterschiede,
- Pausenunterschiede,
- Polarität,
- verschobene Kontaktentsprechung.

Die bindende Aussage lautet:

```text
verteilte räumlich-zeitliche Zustandsunterschiede
!= Trägerwechselwirkung
!= MCM-Feld
```

B3 bleibt geschlossen.

## 6. Kritische Einordnung

Der Verteilungserhalt ist durch die direkte Eins-zu-eins-Zuordnung technisch
angelegt. Ebenso folgt die Richtungsspur aus unterschiedlich alten
unabhängigen Nachhallwerten.

Diese Befunde zeigen keine Emergenz. Sie verhindern vielmehr, dass eine
vorhandene Information fälschlich als Leistung einer Feldkopplung ausgegeben
wird.

Die Fläche besitzt eine räumlich verteilte Lage, aber keine interne kausale
Feldwirkung. Ob eine solche Sammlung unabhängiger Spuren bereits als MCM-Feld
bezeichnet werden soll, ist eine Architekturdefinition und kein Ergebnis
dieses Versuchs.

## 7. Nicht gezeigt

Nicht gezeigt sind:

- ein notwendiger Informationsaustausch zwischen Trägern,
- lokale Überlagerung oder Ausbreitung,
- eine Weltfunktion, die Kopplung benötigt,
- Musterbildung innerhalb der Runtime,
- Wahrnehmung oder Erkennen von Bewegung,
- neuronähnliche Verarbeitung,
- ein gemeinsamer MCM-Strang,
- Lernen oder Feldintelligenz.

## 8. Evidenz

**E1 für die Informationskarte der kontrollierten B0/B1/B2-Fläche.**

Weiterhin **E0** für:

- MCM-Feldmechanik,
- Trägerkopplung,
- Neuron,
- gemeinsamen MCM-Strang,
- Organisationsgeschichte,
- Feldintelligenz.

## 9. Stopplinie

Weitere passive Rezeptorfolgen werden voraussichtlich nur mehr Varianten
desselben Befunds erzeugen. Eine Kopplung würde derzeit eine gewünschte
Feldwirkung programmieren, nicht aus einem nachgewiesenen Mangel folgen.

Deshalb wird keine Methodik 004 für Diffusion, Nachbarschaft oder Neuronen
automatisch eröffnet.

## 10. Notwendige Architekturentscheidung

Vor weiterer Mechanik muss geklärt werden, was das Wort **Feld** funktional
über eine räumlich verteilte Sammlung unabhängiger lokaler Spuren hinaus
bedeutet.

Zwei Richtungen sind derzeit unterscheidbar:

1. Die verteilte lokale Zustandslage selbst ist das schnelle MCM-Feld. Dann ist
   für diese Ebene keine neuronähnliche Kopplung nötig.
2. Das MCM-Feld soll ein kausales Wechselwirkungsmedium sein. Dann muss zuerst
   eine konkrete Weltfunktion benannt werden, die unabhängige Spuren nicht
   tragen und die nicht bereits die gewünschte Kopplung voraussetzt.

## 11. Bester nächster Schritt

An dieser Stelle wird vor weiterer Programmierung gemeinsam die funktionale
MCM-Felddefinition festgelegt. Erst danach kann entschieden werden, ob der
nächste Versuch eine reale Rezeptorwelt, einen minimalen geschlossenen
Weltkreis oder überhaupt eine lokale Wechselwirkung untersuchen darf.
