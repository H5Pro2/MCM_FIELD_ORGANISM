# Methodik 009: MCM-Verteiler und multimodale Musterprüfung

## 1. Forschungsfrage

Können sensorspezifische MCM-Module über offene Docks verlustfrei und
reihenfolgeneutral an einen Verteiler angeschlossen werden, und kann ein
passiver Prüfer ihre Feldlagen als unterscheidbare zeitliche Konstellation
erhalten?

## 2. Teil A: Verteiler

Pflichtfälle:

- auditives MCM allein,
- synthetisches visuelles MCM allein,
- auditive und visuelle MCM-Feldlage in beiden Ankunftsreihenfolgen,
- Ergänzung eines taktilen Docks ohne Änderung bestehender Docks,
- identische Zahlen in verschiedenen Modalitäten,
- unbekannter Dock und falsche Modalität am Dock,
- doppelte Feld- oder Schnappschussidentität,
- verschiedene Uhrkennungen,
- ungültige Zeitfenster,
- falsche Feldgeometrie,
- unveränderte Feldlage im Verteilerausgang.

## 3. Teil B: Musterprüfer

Pflichtfälle:

- auditives Feld allein,
- visuelles Feld allein,
- zeitlich überlappende Felder,
- zeitlich getrennte Felder,
- gleiche Felder in jeder Reihenfolge,
- Änderung nur eines Feldes,
- gleiche Zahlen in verschiedenen Modalitäten,
- ungültige oder doppelte Modalität,
- unterschiedliche Uhrkennungen,
- Observer an und aus,
- exakte Wiederholung.

## 4. Baselines

- **B0:** vollständig getrennte Zustände.
- **B1:** kanonisch geordnete verlustfreie Konstellation.
- **B2:** globale Summe als absichtliche Kollisionsbaseline.

Der neue Stand trägt zunächst nur B1. Er behauptet noch keine gemeinsame
Feldwirkung.

## 5. Erfolgskriterien

1. Reihenfolge verändert weder Routing noch Konstellationsdigest.
2. Modalitäten bleiben trotz gleicher Zahlen unterscheidbar.
3. Nur tatsächlich überlappende Feldlagen werden als gemeinsam markiert.
4. Änderung eines Feldes verändert den Gesamtdigest kausal.
5. Rohsensorik und Semantik erscheinen in keinem öffentlichen Zustand.
6. Der Verteiler verändert keine angedockte Feldlage.
7. Der Prüfer schreibt auf keinen Feldzustand zurück.

## 6. Evidenzgrenze

Ein positiver synthetischer Lauf trägt E1 für Verteilung und passive
multimodale Mustererhaltung. Er zeigt keine multimodale Feldwirkung, kein
Lernen, keine innere Bezeichnung und keine Feldintelligenz.

## 7. Bester nächster Schritt

Nach der synthetischen Prüfung wird Video-In aufgebaut. Erst danach können
reale Audio- und Videofeldlagen gemeinsam verteilt werden.
