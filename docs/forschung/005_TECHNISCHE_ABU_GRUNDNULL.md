# Technische Grundnull der A-B-U-Interaktionsmatrix

## Status

`E2` für den technischen Nullbefund der vorregistrierten Matrix.

`E0` für eine neue Organisationsmechanik, natürliche Lösung oder
Wiederbindung.

Der Lauf verändert weder die Runtime noch das MCM-Neuron. Er verwendet die
bestehende neutrale Feldintegration mit Aktivierung und schnellem Nachhall.

## Geprüfte Frage

Die in
[Architektur 042](../architektur/042_VORREGISTRIERUNG_PASSIVE_ABU_INTERAKTIONSMATRIX.md)
festgelegten Bereiche wurden unverändert verwendet:

```text
A = Positionen 1 und 2
B = Positionen 2 und 3
U = Positionen 5 und 6
```

A und B überlappen lokal. U ist gleich geformt, aber räumlich getrennt. Die
acht Zweige `Y00` bis `Y11` und `Z00` bis `Z11` wurden unabhängig aufgebaut.

Nach jeder Vorgeschichtsphase wurden ausschließlich `activation` und
`afterimage` konstruktiv angeglichen. Die anschließende Probe war eine
kontaktfreie passive Lesung aus dem angeglichenen schnellen Feldzustand.

## Ergebnis

Vor der Angleichung erzeugten A und U verschiedene reale Feldzustände. Die
U-Geschichte erreichte durch die kontinuierliche neutrale Diffusion auch den
B-Bereich:

```text
maximale U-Wirkung im B-Bereich vor Angleichung = 0,08343498474450703
```

U war damit ausdrücklich keine wirkungslose Nullkontrolle.

Nach der Angleichung ergaben die vollständigen Feldvektoren:

```text
max |I_AB| = 0,0
max |I_UB| = 0,0
```

Die heutige Runtime besitzt außerhalb von Aktivierung, Nachhall und den
technischen Wahrnehmungsschnappschüssen keinen Zustand, der A nach der
Angleichung funktional in die spätere Probe tragen könnte.

## Lösung und erneute B-Evidenz

Beide vorregistrierten Weltchallenges wurden ausgeführt:

```text
D0 = 16 Sekunden vollständige Kontaktabwesenheit
D1 = zweimal H(3,4)
```

Für beide galt nach der konstruktiven Angleichung:

```text
L0 = L1, maximale Abweichung 0,0
R0 = R1, maximale Abweichung 0,0
```

Das ist keine natürliche Lösung und keine natürliche Wiederbindung. Es zeigt
nur, dass die bestehende Runtime nach Entfernung ihrer schnellen Unterschiede
keine zusätzliche A-Wirkung bewahrt, die B später beeinflusst.

## Kontrollen

Die Kontrollen schlossen mit folgenden maximalen Abweichungen:

```text
grobe gegen feine Zeitteilung = 4,440892098500626e-16
räumliche Spiegelung          = 2,3592239273284576e-16
räumliche Übersetzung         = 1,214306433183765e-16
umgekehrte Neuronenfolge      = 0,0
```

Zusätzlich waren exakt gleich:

- umgekehrte Zweigausführung,
- unabhängiger Neuaufbau der neutralen B0-Runtime,
- Snapshot und Wiederaufnahme nach den Hauptphasen,
- zwei vollständige Wiederholungen des Ergebnislaufs.

Der kanonische Ergebnisdigest lautet:

```text
1c24ff931aa3cf53452612b2895602acd5f615a2a84403237c9f58d8bc5da249
```

## Technische Umsetzung

Der passive Lauf liegt in:

```text
mcm_field_organism/abu_interaction_ground_null.py
tests/test_abu_interaction_ground_null.py
```

Das Modul führt keine der folgenden Rollen ein:

- Kapazität,
- Kante oder Partnerliste,
- Gewicht oder Lernrate,
- Gewinner oder Schwelle,
- Semantik oder Bedeutung,
- persistenter Organisationszustand.

## Interpretation

Der Lauf bestätigt die Eignung der A-B-U-Matrix als technische
Forschungsanordnung. Er bestätigt zugleich die erwartete Grenze der heutigen
Runtime:

> Reale lokale Feldwirkung und kontinuierliche Diffusion sind vorhanden. Nach
> Angleichung der schnellen Zustände bleibt jedoch keine zusätzliche
> geschichtsabhängige Organisationswirkung zurück.

Damit ist weder Feldintelligenz gesucht noch gefunden. Eine solche Möglichkeit
bleibt lediglich eine offene Fernhypothese und ist kein Entwicklungsziel dieses
Laufs.

## Stopplinie

Der Nullbefund gibt keine Organisationsgleichung frei. Vor einer weiteren
Implementierung muss ein passiver Kandidat vorregistriert werden, der:

- nur lokale gegenwärtige Feldrollen liest,
- keine A-, B-, U- oder Phasenkennung erhält,
- mit denselben Zustands- und Leserbudgets gegen B1 bis B9 geprüft wird,
- Lösung durch gewöhnliche Weltgeschichte statt Reset erlaubt,
- und bei Scheitern vollständig entfernbar bleibt.

## Nächster Schritt

Als Nächstes wird ausschließlich der Zulassungsvertrag für einen zweiten
passiven Organisationskandidaten formuliert. Noch wird keine neue Gleichung und
kein persistenter Zustand implementiert.
