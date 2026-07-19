# Kontrafaktische Feldfluss-Transportgrenze

## Status

Passiver Gegenbefund auf Evidenzstufe E1. Keine Materialbewegung in der
Runtime.

## Frage

Kann der vorhandene signierte lokale Feldfluss ohne zusätzliche
Programmentscheidung als Ursache eines radialen Materialflusses verwendet
werden?

Der lokale Feldfluss ist die einzige bisherige Ursache mit vorhandener
Oberflächenrichtung und geometrischem Vorzeichen. Das genügt jedoch noch
nicht, um sein Vorzeichen als radiale Außen- oder Innenbewegung zu deuten.

## Zwei gleich mögliche Abbildungen

Kontrafaktisch werden zwei globale Polaritäten geprüft:

```text
Variante A:
radiale Geschwindigkeit = + Skala * lokaler Feldfluss

Variante B:
radiale Geschwindigkeit = - Skala * lokaler Feldfluss
```

Material fließt nur von der Seite einer Grenzfläche, auf der im
abgeschlossenen Quellzustand Material vorhanden ist. Im neutralen
Anfangszustand kann daher nur der ungebundene Anteil in die erste radiale
Zelle eintreten. Es wird kein negatives Material erzeugt.

Die Vorschläge werden ausschließlich durch den passiven radialen
Flussvertrag 084 rekonstruiert.

## Befund

Unter derselben kontrollierten dreiteiligen Feldanatomie gilt bei
`Skala = 1` und `dt = 0,1`:

```text
Variante A bilanziell zulässig:  ja
Variante B bilanziell zulässig:  ja

bewegtes Material A:  0,12
bewegtes Material B:  0,12

entstandene Morphologien gleich: nein
```

Beide Varianten erfüllen:

- Eigentümererhaltung;
- Nichtnegativität;
- geschlossene Außengrenzen;
- vollständige radiale Auflösung;
- unveränderte Feld- und Drive-Zustände.

Trotzdem beanspruchen sie unterschiedliche Richtungsprofile.

## Polaritätsproblem

Das Vorzeichen des lokalen Feldflusses beschreibt, wie die vorhandene feste
Felddiffusion zwischen Nachbarpositionen wirkt.

Es beschreibt nicht automatisch:

```text
Material soll sich zur Nachbarposition ausdehnen.
```

Ebenso beschreibt das umgekehrte Vorzeichen nicht automatisch:

```text
Material soll sich von der Nachbarposition zurückziehen.
```

Welche dieser beiden Deutungen gelten soll, wäre eine zusätzliche
konstitutive Annahme über die Bedeutung des Kontaktmaterials. Diese Annahme
liegt weder im MCM-Feld noch im bisherigen Memory-Vertrag.

## Skalenproblem

Der Feldfluss besitzt keine vom Projekt hergeleitete Umrechnung in radiale
Geschwindigkeit. Wird die eingesetzte Skala halbiert, halbiert sich die
bewegte Materialmenge exakt.

Damit gilt in diesem Ein-Schritt-Gegenversuch vollständig:

```text
Materialänderung
=
eingesetzte Skala * Zeit * verfügbare Quelle * ausgewählter Feldfluss
```

Es entsteht kein unerklärter Organisationsrest. Die Morphologie integriert
lediglich die von außen eingesetzte Abbildung.

## Schlussfolgerung

Der signierte lokale Feldfluss ist geometrisch gerichtet, aber keine bereits
begründete radiale Materialursache.

Eine direkte Gleichsetzung mit radialer Geschwindigkeit wird nicht
freigegeben, weil:

- zwei entgegengesetzte Polaritäten gleichermaßen zulässig sind;
- beide unterschiedliche Morphologien erzeugen;
- das Feld keine Polarität auswählt;
- das Feld keine Umrechnungsskala liefert;
- die Materialänderung vollständig aus der eingesetzten Integratorform folgt.

## Stopplinie

Nach den bisherigen Abgrenzungen besitzt keine vorhandene schnelle
Feld- oder Rezeptorgröße eine ausreichend begründete direkte
Materialbewegungsrolle:

```text
Rezeptorkontakt:             keine Oberflächenrichtung
Eigenaktivierung:            keine Oberflächenrichtung
schneller Nachhall:          feste Leaky-Spur ohne Richtung
lokal abgetasteter Nachhall: nicht im Drive-Vertrag
signierter Feldfluss:        Richtung vorhanden,
                             radiale Polarität und Skala unbegründet
```

An dieser Stelle wird keine weitere Bewegungsformel gebaut.

Vor weiterer Implementierung muss konzeptionell geklärt werden:

> Welche physische Rolle besitzt das strukturelle Kontaktmaterial, aus der
> Außenbewegung, Rückzug und begrenzte Wiederbindung folgen können, ohne diese
> Verhaltensweisen als gewünschte Regel einzubauen?

Alternativ muss geprüft werden, ob die angenommene Kontaktmorphologie
überhaupt das geeignete Substrat für organisches Memory ist.
