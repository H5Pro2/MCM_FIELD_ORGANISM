# S2-BF: Vollstaendige Quellvorpruefung vor Baselinebildung

## Korrektur

S2-BF fuegt einen neuen privaten korrigierten Einstieg hinzu. Der
historische S2-BD-Quellstand bleibt unveraendert und digestgebunden.

Der neue Einstieg prueft vor jeder Ableitung:

1. die exakten Eingabetypen;
2. die vollstaendige Bindung des Kandidatenbefunds an Bildungsumschlag und
   Profil;
3. die vollstaendige Bindung und zeitliche Trennung der spaeteren Probe;
4. erst danach den Eintritt in den vorhandenen atomaren Comparator.

Die beiden Vorpruefungen sind rein. Sie fuehren keine Kandidatenprobe aus,
bilden keine Baseline und veraendern keinen Zustand.

## Adversarialer Nachweis

Der neue Regressionstest kombiniert:

- einen authentischen und stabilisierten, aber fremden Kandidatenbefund;
- einen fuer sich gueltigen Bildungsumschlag, ein gueltiges Profil und eine
  gueltige spaetere Probe.

Die Quellpruefung verwirft diese Kombination. Die instrumentierte
Baselinebildungsfunktion wird dabei exakt `0`-mal aufgerufen und es entsteht
kein Receipt. Damit ist der S2-BE-Reihenfolgeblocker geschlossen.

## Gueltige Pfade

Die positive und negative gueltige Fixture bleiben unveraendert durch die
statische Prototypbaseline erklaert. Der fokussierte Testlauf besteht mit
`4/4` Tests.

## Grenze

Der korrigierte Einstieg bleibt privat. API, Paketexport, Snapshot,
Feldkern und Produktionspfad sind unveraendert. Es entsteht kein
Funktionsvorteil, keine Feldwirkung und kein Befund einer MCM-spezifischen
Memory-Mechanik.

## Naechster Schritt

S2-BG ist der statische Abschlussaudit des korrigierten Einstiegs, seiner
Quellreihenfolge, des adversarialen Null-Aufruf-Befunds und der privaten
Grenzen. Die Tests werden nicht erneut ausgefuehrt.
