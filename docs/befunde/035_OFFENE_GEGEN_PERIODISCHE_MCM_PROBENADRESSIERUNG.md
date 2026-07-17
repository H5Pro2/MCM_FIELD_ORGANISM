# Befund 035: Offene gegen periodische MCM-Probenadressierung

## Ergebnis

Methodik 032 wurde als isolierter passiver Referenzprüfer ausgeführt.

Geprüft wurden:

```text
7 Zielpositionen
42 vollständige Welt-Rezeptor-MCM-Zweige
21 äußere Ursachenpaare
14 starre Ringtransformationen
2 vorhandene technische Baselines
1 mehrdeutige Negativgeometrie
```

Der kanonische Gesamtdigest lautet:

```text
1c717cd79cb0a571cfe4e32439c8ba2484b0672da6555765855a5ef811ebbdc5
```

Die bestehende `MCMNeuronLayer` wurde nicht verändert.

## Offene Referenz

Die aktuelle Schicht erzeugte exakt die vorregistrierte offene Probenmatrix:

```text
Position 0: Quelle 1
Position 1: Quellen 0 und 2
Position 2: Quellen 1 und 3
Position 3: Quellen 2 und 4
Position 4: Quellen 3 und 5
Position 5: Quellen 4 und 6
Position 6: Quelle 5
```

Technische Identität, Position, Aktivierung und Nachhall des eingefrorenen
Ausgangszustands blieben unverändert. Nur die neu abgeschlossene
`perception` enthielt erwartungsgemäß die beobachteten offenen Feldproben.

## Periodische Referenz

Die isolierte Modulo-Adressierung ergänzte genau:

```text
Ziel 0, offset -1, Quelle 6
Ziel 6, offset +1, Quelle 0
```

Für die Signaturlage wurden dabei exakt erhalten:

```text
Quelle 6 → Aktivierung 0.6, Nachhall 0.0
Quelle 0 → Aktivierung 0.0, Nachhall 0.6
```

An den Positionen 1 bis 5 waren offene und periodische lokale Proben
vollständig identisch. Weitere Differenzen traten nicht auf.

## Symmetrie

Alle sieben zyklischen Rotationen wurden in beiden technischen
Ringorientierungen geprüft:

```text
7 Rotationen x 2 Orientierungen = 14 Transformationen
```

Nach kanonischer Rückabbildung waren alle Ergebnisse exakt gleich. Kein
numerischer Ort wurde dadurch zum Zentrum, Anfang oder bevorzugten Rand.

Die Richtungsumkehr tauschte ausschließlich die Vorzeichen der technischen
Offsets. Sie erzeugte keine Rollen- oder Wirkungspräferenz.

## Mehrdeutigkeitskontrolle

Eine periodische Achse mit zwei Positionen und den Offsets `-1` und `+1`
adressiert für ein Ziel zweimal dieselbe Quelle.

Diese Geometrie wurde wie vorregistriert abgelehnt. Die Referenz:

- fasste die Proben nicht zusammen,
- zählte sie nicht doppelt,
- führte kein Gewicht ein,
- nutzte keine Iterationsreihenfolge zur Unterscheidung.

Der Ring mit sieben Positionen blieb eindeutig.

## Vollständiger Weltpfad

Jeder der 42 Zweige durchlief erneut:

```text
simulierte Weltintervention
→ abgeschlossener Weltzustand
→ Weltrezeptor
→ allgemeiner Rezeptorrahmen
→ sieben gedockte MCM-Neuronen
→ abgeschlossenes MCM-Feldfenster
→ offene und periodische lokale Probenadressierung
```

Die lokalen Proben wurden damit aus den tatsächlich abgeschlossenen
Feldfenstern gebildet, nicht aus nachträglich rekonstruierten Zielwerten.

In allen 21 Ursachenpaaren galt:

```text
external gegen effector
→ Provenienzdigest verschieden
→ offene Probenlage gleich
→ periodische Probenlage gleich
```

Ursache, `delta`, Effort und Provenienz wurden nicht Bestandteil einer
Feldprobe.

## Baseline-Ablationen

Unter `hold_state_baseline` erzeugten offene und periodische Wahrnehmung exakt
dieselben Aktivierungs- und Nachhallwerte.

Unter `receptor_projection_baseline` galt ebenfalls:

```text
Aktivierung = identischer aktueller Rezeptorkontakt
Nachhall    = 0.0
```

Die unterschiedlichen Randproben blieben in der abgeschlossenen Wahrnehmung
sichtbar, hatten aber unter beiden Baselines keine Wirkung auf den schnellen
Zustand.

Das ist der erwartete Nullbefund. Er zeigt keine Feldkopplung.

## Neutralitätskontrollen

Exakt neutral blieben:

- kein Observer gegen leeren Observer gegen sammelnden Observer,
- normale gegen umgekehrte Zielreihenfolge,
- normale gegen umgekehrte Offsetreihenfolge,
- unabhängige Wiederholung,
- vollständiger Neuaufbau aller Zustände.

Es entstanden keine gespeicherte Wrap-Kante, Nutzungszahl, Kontinuität oder
Restspur.

## Getragener Befund

Für die explizit ringförmige simulierte Rezeptorgeometrie ist periodische
lokale Adressierung technisch geeignet:

```text
Sie erhält die zwei lokalen Weltkontakte über den Darstellungsrand,
ohne weitere Feldproben oder schnelle Zustandsänderungen einzuführen.
```

Damit ist die in Befund 034 ausgewiesene technische Geometrielücke auf Ebene
einer isolierten Referenz geschlossen.

## Stärkstes Gegenargument

Der positive Befund folgt aus einer gewöhnlichen Modulo-Adressierung. Die
Ringstruktur stammt vollständig aus der vom Entwickler vorgegebenen
Simulationswelt.

Der Versuch zeigt deshalb weder:

- dass das MCM-Feld selbst eine Topologie entwickelt,
- dass die zusätzlichen Proben kausal wirken,
- dass Beziehungen entstehen,
- noch dass irgendeine Form von Feldintelligenz vorliegt.

Er zeigt nur, dass eine technische Sensoranatomie die vorgegebene lokale
Weltgeometrie verlustfrei abbilden kann.

## Evidenz

```text
periodische Referenzadressierung:           E1
technische Eignung für den Ringrezeptor:    E1
Ursachenneutralität der lokalen Proben:     E1
Integration in die MCMNeuronLayer-Runtime:  E0
kausale Wirkung lokaler Ringproben:         E0
entwickelte Beziehung oder Topologie:       E0
Eigenwirkung und Handlung:                  E0
Feldintelligenz:                            E0
```

## Stopplinie

Der Befund gibt nicht frei:

- eine allgemeine periodische Standardgeometrie,
- Periodizität für Audio, Video oder spätere Sensoren,
- Änderung der schnellen Neuronenfunktion,
- Feldkopplung, Ausbreitung oder Gewichtung,
- gespeicherte Kanten oder Beziehungen,
- Verbindung einer Ringprobe mit `delta`,
- Effektorwahl, Reward, Ziel oder Handlung.

## Bester nächster Schritt

Vor einer Runtime-Änderung wird Methodik 033 registriert.

Sie darf ausschließlich eine optionale Randart in der technischen
`MCMNeuronLayer` prüfen:

```text
open bleibt unveränderter Standard
periodic muss pro passender Sensorachse explizit gesetzt werden
```

Die Integration muss Befund 035 exakt reproduzieren, bestehende offene
Geometrien unverändert lassen und unter beiden Baselines weiterhin ohne
Wirkung auf Aktivierung und Nachhall bleiben.
