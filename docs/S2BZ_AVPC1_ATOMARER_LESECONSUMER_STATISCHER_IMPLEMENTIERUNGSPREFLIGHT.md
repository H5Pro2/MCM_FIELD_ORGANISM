# S2-BZ: Statischer Implementierungspreflight des AVPC-1-Leseconsumers

## Ergebnis

Der in S2-BY gebundene private atomare Leseconsumer ist ohne neue fachliche
Regel materialisierbar. Alle Eingabe-, Kindausgabe- und Digesttypen sind im
privaten PPB-1-/AVPC-1-Pfad vorhanden. Es verbleiben keine offenen
Implementierungsblocker.

## Vorpruefung

Vor dem ersten Kindaufruf kann der Consumer alle erforderlichen
Quellbeziehungen aus vorhandenen eingefrorenen Feldern pruefen:

- Profil und Probehuelle muessen denselben Relationszustand binden.
- Der auditive Befund muss erkannt, auditiv und an die Projektion der
  Probehuelle gebunden sein.
- Konfiguration, Bankidentitaet, Bankzustand und ausgewaehlter auditiver
  Prototyp muessen zum Relationszustand passen.
- Visuelle Konfiguration, Bankidentitaet und Bankzustand muessen Profil und
  Relationszustand entsprechen.

Diese Vergleiche treffen keine neue Erkennungs- oder Relationsentscheidung.
Die eigentliche Relationsrolle bleibt beim vorhandenen Relations-Lookup.

## Geplanter Minimalumfang

Eine spaetere Implementierung darf genau einen privaten Fehlertyp, einen
eingefrorenen Ergebnistyp, lokale Digest- und Vorpruefhelfer sowie die reine
Funktion `consume_avpc1_auditory_cued_visual_readout` enthalten.

Der Relations-Lookup wird nach bestandener Vorpruefung genau einmal
aufgerufen. Negative Rollen erzeugen ohne Resolveraufruf ein vollstaendiges
negatives Ergebnis. Nur `MATCH` ruft den vorhandenen visuellen Resolver genau
einmal auf. Fehler der Kindfunktionen werden ursachenerhaltend in die
gebundenen privaten Consumerfehler ueberfuehrt und liefern kein Ergebnis.

## Testgrenze

Neun synthetische Rollen decken positiven Abruf, beide negativen Rollen,
Nullaufrufe bei ungueltiger Vorpruefung, Fehler beider Kindfunktionen,
substituierte Kindausgaben, Eingabeunveraenderlichkeit und die private
Systemgrenze ab.

S2-BZ selbst importiert oder startet keine Projektfunktion und fuehrt keine
Tests aus. S2-CA darf erst als eigener Schritt den privaten Consumer und genau
diese synthetischen Vertragstests implementieren.
