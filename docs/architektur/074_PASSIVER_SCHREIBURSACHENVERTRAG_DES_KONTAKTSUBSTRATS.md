# Passiver Schreibursachenvertrag des Kontaktsubstrats

## Zweck

Der anatomische Zustandsvertrag besitzt neutrale, partnerlose
Kontaktoberflächen. Vor jeder Materialdynamik muss geklärt werden, welche
Ursachen dort bereits kausal vorliegen.

Der neue Vertrag richtet ausschließlich vorhandene Größen an diesen
Oberflächen aus. Er schreibt kein Material und wählt keine Wachstumsregel.

## Kausale Zeitgrenze

Für einen Übergang von `t` nach `t+1` werden nur Größen verwendet, die bereits
im vorhandenen `MCMNeuronDrive` liegen:

```text
Eigenaktivierung des Neurons bei t
lokale Feldprobe aus Richtung r bei t
gerichteter momentaner Feldfluss bei t
realer Rezeptorkontakt für t+1
```

Der gerichtete Fluss wird nicht gespeichert:

```text
J(r -> i, t) =
    (Aktivierung_r(t) - Aktivierung_i(t))
    / Reaktionszeit
```

Er ist dieselbe bereits bestätigte schnelle Diffusionswirkung und keine neue
Memory-Rolle.

## Räumliche Zuordnung

Jede neutrale Kontaktoberfläche erhält genau ihre vorhandene lokale
Vortaktprobe. Wo die Feldgeometrie in dieser Richtung keinen Träger besitzt,
bleibt auch die Ursache leer.

Der Rezeptorkontakt bleibt dagegen eine Ursache des gesamten Neurons. Er wird
nicht künstlich auf eine bestimmte Oberfläche projiziert.

Damit gilt:

```text
Eigenaktivierung:       neuronlokal, nicht richtungswählend
Rezeptorkontakt:        neuronlokal, nicht richtungswählend
lokale Feldprobe:       oberflächenlokal
gerichteter Feldfluss:  oberflächenlokal
```

Diese Zuordnung bestimmt noch nicht, welche Größe später Material verändern
darf.

## Technische Umsetzung

`structural_contact_drive.py` erzeugt einen unveränderlichen
`StructuralContactDriveMap`.

Er enthält:

- keine Partner- oder Beziehungs-ID;
- kein Gewicht;
- keinen Memory- oder Geschichtszustand;
- keine Materialänderung;
- keine Schwelle;
- keine Gewinnerregel;
- keine Rückwirkung auf das MCM-Feld.

Der Quell-Layer und der Kontaktmaterialzustand werden über ihre Digests
referenziert. Wiederholte Abbildung desselben abgeschlossenen Übergangs ist
exakt reproduzierbar.

## Enger technischer Nachweis

Eine dreiteilige eindimensionale Feldanatomie besitzt sechs neutrale
Oberflächen. Vier Richtungen treffen tatsächlich einen lokalen Feldträger,
zwei zeigen aus der endlichen Anatomie heraus.

Die Abbildung zeigt:

```text
neutrale Oberflächen:                6
Oberflächen mit lokaler Feldprobe:   4
Materialänderungen:                  0
Feldänderungen durch den Observer:   0
gespeicherte Beziehungen:            0
```

Die gerichteten Flüsse am mittleren Neuron werden aus den Vortaktwerten exakt
als `+0,8` und `-0,4` rekonstruiert.

## Aussagegrenze

Gezeigt ist:

- vorhandene Feldursachen lassen sich ohne Partner-ID an neutrale
  Kontaktoberflächen ausrichten;
- lokale Feldprobe und momentaner Fluss besitzen eine echte
  Richtungszuordnung;
- Rezeptorkontakt und Eigenaktivierung wählen keine Oberfläche;
- die Abbildung benötigt keinen zusätzlichen Organismuszustand.

Nicht gezeigt ist:

- welche Ursache Material bewegen darf;
- dass Flussbetrag, Flussvorzeichen oder Koaktivität eine organische
  Schreibregel bilden;
- dass Kontaktmaterial wächst, zurückgeht oder sich umverteilt;
- dass zwei Oberflächen eine Berührung bilden;
- dass Memory, Lösung oder Wiederbindung entsteht.

## Entscheidung

Der Vertrag öffnet keine Materialdynamik.

Insbesondere werden nicht eingeführt:

- Flussakkumulation;
- Betrags- oder Quadratintegration;
- zeitliche Schwellen;
- rezeptorgesteuerte Oberflächenwahl;
- feste Sender- und Empfängerrollen;
- adaptive Kanten.

## Nächster Schritt

Die nächste enge Frage lautet:

> Welche lokale Wechselwirkung kann Material räumlich umverteilen, ohne
> lediglich den momentanen Fluss zu integrieren und ohne eine Oberfläche als
> Gewinner auszuwählen?

Vor Code muss dafür ein Materialbilanz- und Symmetrievertrag formuliert
werden. Er muss festlegen, was digitale Materialerhaltung bedeutet, darf aber
noch keine gewünschte Kontaktform erzeugen.
