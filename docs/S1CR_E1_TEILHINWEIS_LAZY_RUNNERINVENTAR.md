# S1-CR: E1 Teilhinweis Lazy-Runnerinventar

## Status

Alle 36 S1-CO-Beobachtungsrollen sind als lazy, schreibgeschuetztes und
streng geordnetes Inventar gebunden. Beim Inventaraufbau wurde kein
Cue-Runner, kein Kompositor und keine Entscheidung aufgerufen.

## Implementierung

```text
mcm_field_organism/e1_partial_cue_runner_inventory.py
tests/test_e1_partial_cue_runner_inventory.py
```

Die Rollen bleiben privat.

## Reihenfolge

Die Ordnung ist das kartesische Produkt:

```text
Modelle:     e1, p0, b1-static-h8
Geschichten: left-g4, right-g4, neutral
Hinweise:    left-full, right-full, left-partial, right-partial
```

Damit entstehen exakt 36 eindeutige Schluessel. Jeder Wert ist ein Callable,
das erst bei einem spaeteren expliziten Aufruf genau eine bereits isoliert
abgenommene Beobachtung erzeugt.

## Digestbindung

```text
e91148ff48e289a7fcf6b3dbe8f8832a25907f496e24bc73fdce5950f0d34925
```

Der Digest bindet:

- den S1-CO-Vertragsdigest;
- alle 36 Schluessel in fester Reihenfolge;
- die frische Feldgeometrie;
- linke und rechte G4-Bindungen sowie Neutralzustand;
- den einen statischen H8-Kantenratenadapter;
- S- und H-Zeitparameter;
- die unveraenderte isolierte Runnerfactory.

Eine Aenderung dieser Werte macht eine spaetere Ausfuehrungsfreigabe
ungueltig.

## Technische Abnahme

Sieben fokussierte Inventartests und 59 relevante Verbundtests bestehen.
Geprueft wurden Vollstaendigkeit, Reihenfolge, Schreibschutz,
Nebenwirkungsfreiheit des Aufbaus, deterministischer Digest, Zeit- und
Geometriegrenzen, private API und genau eine isolierte Identitaetsprobe.

Die Identitaetsprobe hat nur einen bereits in S1-CQ abgenommenen Runner
aufgerufen. Eine 36er-Matrix, Interaktionskomposition oder Entscheidung
wurde nicht erzeugt.

## Aussagegrenze

S1-CR bestaetigt ausschliesslich statische Matrixbereitschaft. Es existiert
weiterhin kein vollstaendiges Teilhinweisergebnis und kein
Historyinteraktions-, Rekonstruktions- oder Memorybefund.

## Bester naechster Schritt

S1-CS registriert vor jeder Gesamtmatrixausfuehrung einen atomaren
Einmallaufvertrag. Er bindet Inventardigest, Ergebnisfelder,
Ergebnisdigest, Versuchsnachweis, Fehlerverhalten und Wiederholungsverbot,
ohne einen der 36 Runner aufzurufen.
