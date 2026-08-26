# W7-AP: Roher R1/R2- und R2/R4-Distanzkompositor

## Status

W7-AP ist als privater, entscheidungsfreier Kompositor implementiert. Der
kanonische reale W7-AN-Container wurde dabei nicht erneut ausgefuehrt. Daher
liegt noch kein numerisches W7-AP-Ergebnis fuer die reale R1/R2/R4-
Materialisierung vor.

## Gebundene Eingaben

Der Kompositor akzeptiert ausschliesslich:

- den kanonischen W7-AN-Containerdigest
  `4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5`;
- den W7-AO-Vertragsdigest
  `14455f15e6f3d0f96106aa766ae544ec76f19b5c94308329ec45fd0cd12067dc`;
- die Aufloesungen R1, R2 und R4 in dieser Rollenbindung;
- genau 35 Pfad-/Checkpoint-Rollen je Aufloesung;
- unausgewertete W7-AN-Aufloesungs- und Paarcontainer.

## Materialisierung

Fuer jede der 35 Rollen werden zwei gerichtete Residualvergleiche gebildet:

1. R1 minus R2;
2. R2 minus R4.

Verglichen werden die bereits vorhandenen CAP-minus-P0-S/H-Residualproben.
Pfad, Checkpoint, Plan-Checkpoint-Digest, Beobachtungsticks, Probenzahl und
S/H-Geometrie muessen exakt uebereinstimmen. Pro Probe werden nur die
gerichteten S- und H-Differenzen gebunden. Pro Rolle werden daraus
`S_linf`, `H_linf` und diagnostisch `SH_l2` berechnet.

Damit umfasst ein vollstaendiges Ergebnis genau 70 Rollenvergleiche. Es
enthaelt zusaetzlich 105 Same-Resolution-Identitaetskontrollen fuer R1, R2
und R4. Diese muessen exakt `(0, 0, 0)` ergeben. Eine umgekehrte
Konstruktionsreihenfolge muss dieselben rollenspezifischen Digests liefern.
Die bereits bestandene Primaer-/Gegenlaufgleichheit wird nur ueber den
kanonischen W7-AN-Status gebunden; W7-AP erzeugt keine Ersatz-
Wiederholungsdaten.

## Harte Sperren

W7-AP berechnet und entscheidet ausdruecklich nicht:

- keine rollenweise Konvergenz;
- kein `epsilon_num`;
- keinen Effektboden;
- keine Pfad- oder Feldfunktion;
- keinen Memory-, Feldzeit-, Organisations-, Semantik- oder KI-Befund.

Die Ergebnisflags `convergence_evaluated`, `epsilon_num_ready`,
`effect_floor_ready` und `field_function_decision_allowed` bleiben alle
`false`.

## Verifikation

Der schnelle W7-AN/AO/AP-Verbund besteht mit `54 tests, OK`. Die acht neuen
W7-AP-Tests pruefen die 70 Rollen, die gerichteten Rohdifferenzen, alle 105
exakten Identitaetsnullen, die Digestbindung, Geometrieabweisung,
Manipulationsabweisung und die private API-Grenze. Sie verwenden kleine
synthetische Residualverlaeufe und ersetzen keinen realen W7-AP-Lauf.

## Naechste Grenze

Vor einer W7-AQ-Auswertung muss der kanonische W7-AN-Container erneut rein
im Arbeitsspeicher materialisiert und unmittelbar an W7-AP uebergeben werden.
Dieser Lauf ist wegen der nachgewiesenen W7-AN-Laufzeit von rund 76 Minuten
gesondert zu planen. Erst sein W7-AP-Ergebnis darf Gegenstand einer spaeteren,
vorab statisch gebundenen Auswertung sein.
