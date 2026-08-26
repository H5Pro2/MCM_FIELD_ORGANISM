# S1-XO: Private numerische Margin-Fixture und Validator

## Implementierter Umfang

S1-XO implementiert eine private reine Fixture fuer kuenftige technische
PPB-1-Regressionstests. Sie enthaelt:

- eine auditive Fixture mit 12 synthetischen Traegern;
- eine visuelle Fixture mit 72 synthetischen Traegern;
- je fuenf schwellenferne Verhaltensproben;
- je drei getrennte Operatorfaelle unmittelbar unter, auf und ueber der
  Schwelle;
- Digestbindung fuer Modalitaetsfixtures, Operatorfaelle und Gesamtbundle.

Der Builder berechnet jede erwartete Verhaltensdistanz mit der bestehenden
`normalized_mean_l1_distance`. Vor Rueckgabe muss die berechnete Distanz
exakt dem binaer gebundenen Wert entsprechen, auf der erwarteten
Schwellenseite liegen und den Mindestabstand einhalten.

## Fail-closed-Regeln

Unbekannte Modalitaet, falsche Dimension, geaenderte Werte oder Masken,
abweichende Produktionsmetrik, falsche Klassenseite, zu kleiner Abstand,
eine Verhaltensprobe exakt auf der Schwelle sowie jeder Digestfehler stoppen
die Fixturebildung.

Der separate Operatorfall verwendet `math.nextafter` und prueft nur die
Semantik von `distance <= threshold`. Er ist kein Bestandteil einer
Verhaltensmatrix und erzeugt keine Kandidaten- oder Baselineentscheidung.

## Projektgrenze

Das Modul importiert keine Zustandsbildung, Probe, Registry oder Runner. Es
besitzt keinen Datei-, Feld-, API-, Snapshot- oder Produktionspfad. S1-XC
und S1-XI bleiben byteidentisch und historisch geschlossen.

S1-XO ist ausschliesslich eine technische Testgrundlage. Es entsteht kein
Memory-Faehigkeits- oder MCM-spezifischer Forschungsbefund.

## Naechster Schritt

S1-XP soll die Implementierung rein statisch auf Quellbindung, Rollen,
Digestanatomie, Numerikregeln, Privatheit und historische Trennung pruefen.
Keine Fixtureausfuehrung, keine Zustandsfunktion und kein Matrixlauf.
