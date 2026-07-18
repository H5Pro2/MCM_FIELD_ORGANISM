# Methodik 015: Räumliche Nachhallorientierung

## Frage

Kann der vorhandene verteilte Nachhall die Orientierung einer lokalen
Kontaktfolge tragen, obwohl aktuelle Aktivierung und eigener Zentrum-Nachhall
am Prüfpunkt identisch sind?

## Kontrollierte Welten

Eine eindimensionale Fläche mit fünf lokalen Trägern erhält zwei
spiegelbildliche Kontaktfolgen:

```text
Vorwärts:  Position 0 -> 1 -> 2
Rückwärts: Position 4 -> 3 -> 2
```

Beide enden mit demselben Kontakt an Position 2. Die Nachhallbildung verwendet
unverändert die bekannte unabhängige B1-Baseline. Es gibt keine
Trägerkopplung und keine MCM-Übergangsregel.

## Baselines

- B0: Die aktuelle Aktivierung beider Endlagen muss identisch sein.
- B1-lokal: Der eigene Nachhall an Position 2 muss identisch sein.
- B1-räumlich: Nur die getrennte linke und rechte Nachhallprobe darf die
  Kontaktorientierung unterscheiden.

Der passive Orientierungsobserver lautet:

```text
rechte Nachhallprobe - linke Nachhallprobe
```

Er verändert das Feld nicht und ist keine neuronale Reaktionsregel.

## Kontrollen

1. Exakte Spiegelung der vollständigen Trägerlagen.
2. Vorzeichenwechsel der Orientierung bei Spiegelung.
3. Parameterfamilie verschiedener fester B1-Zeitkonstanten.
4. Lineare Amplitudenskalierung.
5. Passive Pause ohne neuen Kontakt.
6. Exakter Reset aller schnellen Zustände.

## Entscheidung

Ein positiver Befund trägt nur:

> Die räumliche Nachhalllage enthält lokal lesbare Information über die
> Orientierung der vorangegangenen Kontaktfolge.

Er trägt nicht:

- natürliche Ausbreitung,
- Bewegungserkennung,
- eine neuronale Folgereaktion,
- einen Bedarf oder Nichtbedarf langfristiger Zustände,
- Feldintelligenz.

Eine neue Zustandsvariable bleibt geschlossen, solange die vorhandene
räumliche Feldlage die untersuchte Information bereits trägt.
