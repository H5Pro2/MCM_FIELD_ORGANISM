# Abgrenzung direkter radialer Flussursachen

## Status

Passiver Rollenbefund auf Evidenzstufe E1. Keine Materialbewegung und keine
Runtime-Freigabe.

## Frage

Welche bereits vorhandene Feldgröße besitzt überhaupt die räumliche Rolle,
einen radialen Fluss später kausal zu begründen, ohne dass der Code zuerst
eine Oberflächenrichtung erfinden muss?

Geprüft werden die tatsächlichen Zustandsrollen von MCM-Neuron,
Feldwahrnehmung und `StructuralContactDriveMap`.

## Rezeptorkontakt

Der aktuelle Rezeptorkontakt liegt am gesamten Dock-Neuron:

```text
receptor_contact -> NeuronContactDrive
```

Er liegt nicht an einer einzelnen Kontaktoberfläche. Aus seinem Wert folgt
weder:

- welche radiale Richtung beansprucht wird;
- ob Material nach außen oder innen fließen soll;
- wie mehrere Richtungen um begrenztes Material konkurrieren.

Eine direkte Regel wie:

```text
positiver Rezeptorkontakt -> Material nach außen
```

würde Annäherung bereits programmieren. Eine gleichmäßige Verteilung auf alle
Oberflächen würde isotrope Expansion programmieren.

Direkter Rezeptorkontakt wird deshalb als unmittelbare radiale Flussursache
verworfen. Das gilt gleichermaßen für äußeren und endogenen Kontakt.

## Eigenaktivierung

Die Eigenaktivierung wird im passiven Drive-Vertrag an jeder Oberfläche nur
als derselbe neuronlokale Wert wiederholt. Diese Wiederholung erzeugt keine
Richtungsinformation.

Auch Eigenaktivierung müsste durch eine zusätzliche Regel in Außen- oder
Innenbewegung übersetzt werden und wird als direkte Ursache verworfen.

## Eigener schneller Nachhall

Der eigene Nachhall ist:

- neuronlokal;
- geschichtsabhängig;
- durch eine feste Zeitkonstante leaky;
- nicht oberflächenwählend.

Würde er direkt Material bewegen, erhielte das Kontaktmaterial lediglich eine
räumliche Verlängerung derselben festen Nachhallspur. Zusätzlich müsste eine
Außen-/Innenrichtung programmiert werden.

Der eigene schnelle Nachhall wird deshalb als direkte Flussursache verworfen.

## Lokal abgetasteter Nachhall

Lokale Feldproben enthalten technisch auch den Nachhall benachbarter
Positionen. Dieser Wert gehört jedoch nicht zum bestehenden
`LocalContactSurfaceDrive`.

Seine nachträgliche Aufnahme wäre eine neue Schreibursachenrolle. Sie ist
außerdem weiterhin eine feste Leaky-Spur und wird nicht stillschweigend
zugelassen.

## Momentaner lokaler Feldfluss

Der vorhandene signierte lokale Feldfluss besitzt bereits:

- eine konkrete Oberflächenrichtung;
- ein geometrisch begründetes Vorzeichen;
- eine kausale Vortaktgrenze;
- keine eigene gespeicherte Geschichte.

Er ist deshalb die einzige aktuell vorhandene Rolle, die ohne erfundene
Oberflächenwahl für eine passive Isolation offen bleibt.

Das bedeutet ausdrücklich nicht, dass er als Materialgeschwindigkeit gewählt
ist. Eine direkte Gleichsetzung:

```text
radiale Geschwindigkeit = lokaler Feldfluss
```

könnte lediglich den momentanen Diffusionsfluss räumlich integrieren. Dann
wäre die Morphologie eine neue Darstellung bereits bekannter schneller
Feldgeschichte, nicht organisches Memory.

## Technischer Befund

`audit_radial_transport_cause_roles` bestätigt am bestehenden Vertrag:

```text
direkter Rezeptorkontakt:      verworfen
Eigenaktivierung:              verworfen
eigener schneller Nachhall:    verworfen
lokal abgetasteter Nachhall:   nicht im Drive-Vertrag
signierter lokaler Feldfluss:  offen für passive Isolation
```

Der Audit verändert weder Feld, Drive-Map noch Kontaktmaterial.

## Nächster Schritt

Als Nächstes wird ausschließlich der signierte lokale Feldfluss als
kontrafaktischer passiver Flussvorschlag untersucht.

Dabei muss geprüft werden:

1. ob Nullfeldfluss exakt Nulltransport ergibt;
2. ob Vorzeichenumkehr den Transport geometrisch umkehrt;
3. ob der Vorschlag lediglich Feldfluss über Zeit integriert;
4. ob unterschiedliche radiale Auflösungen denselben physikalischen Weg
   tragen;
5. ob nach Ende des Feldflusses nur eingefrorene Lage oder natürliche Lösung
   möglich ist;
6. ob irgendein Befund über einen gewöhnlichen räumlichen Integrator
   hinausgeht.

Es erfolgt weiterhin keine Runtime-Freigabe.
