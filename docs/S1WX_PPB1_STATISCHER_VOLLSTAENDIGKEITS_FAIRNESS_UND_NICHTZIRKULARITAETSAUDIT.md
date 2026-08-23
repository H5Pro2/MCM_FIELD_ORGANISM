# S1-WX: Statischer Vollstaendigkeits-, Fairness- und Nichtzirkularitaetsaudit

## Auftrag und Grenze

S1-WX auditiert ausschliesslich den maschinenlesbaren S1-WW-Vertrag. Weder
Projektmodule noch Bildung, Probe, Baseline oder Matrix wurden importiert
oder ausgefuehrt. Feldwirkung und Ergebnisentscheidung bleiben null.

## Bestaetigter Bestand

`12 von 16` Strukturpruefungen bestehen. Bestaetigt sind insbesondere:

- kanonischer S1-WW-Digest und gebundene Elternkette;
- Audio und Video sowie die vollstaendige Phasenreihenfolge;
- Bildung, Stabilisierung und Belegrollen;
- exakt eingefrorener Probevorzustand;
- drei vorab positive und zwei vorab negative Probearten;
- Kandidat und fuenf geforderte Baselines;
- gleiche Bildungsgeschichte, Gap, Probe und Informationsgrenzen;
- Probe- und Bankunveraenderlichkeit;
- symmetrische Pass-/Fail-Regeln;
- Vorrang der Methodenungueltigkeit;
- gesperrte Ergebnis- und MCM-spezifische Claims.

## Vier Korrekturblocker

### 1. Erreichbarkeit der Probeabstaende

Die PPB-1-Konfiguration erlaubt Matchschwellen null und zwei. Bei null kann
kein nahes Positiv echt zwischen null und Schwelle liegen; bei zwei bleibt
kein Raum fuer negative Proben oberhalb der Schwelle. Vor einer endlichen
Matrix muss daher eine Schwelle echt innerhalb des Bereichs sowie eine
positive Nah- und Ferndistanzmarge gebunden werden.

### 2. Nichtzirkulaere Baselineerklaerung

S1-WW fordert derzeit, dass eine erklaerende Baseline alle Funktionsausgaben
trifft. Zu den gemeinsamen Ausgaben gehoeren aber auch private
Zustandsdigests und Speicherzaehler. Eine einfachere Baseline kann dieselben
Erkennungsentscheidungen und Distanzen liefern, muss aber gerade bei diesen
Metadaten abweichen. Ein Vergleich aller Rollen wuerde sie kuenstlich als
nicht erklaerend ausschliessen.

Die Korrektur muss Erkennungsentscheidung und naechste Distanz als
verhaltensbezogenen Erklaerungssatz definieren. Zustands-, Herkunfts- und
Ressourcenrollen werden getrennt berichtet, aber nicht fuer funktionale
Gleichheit verlangt.

### 3. No-Memory ohne Zustandsdigest

Das gemeinsame Ausgabeschema verlangt beobachtete Vor-/Nachzustandsdigests.
No-Memory besitzt definitionsgemaess keinen aus der Bildung abgeleiteten
Zustand. Es fehlt eine kanonische Nullrolle oder eine ausdruecklich nullable
Rolle.

### 4. Gemeinsame Modalitaetsentscheidung

Audio und Video sind vorhanden, aber der Gesamtpass verlangt noch nicht
ausdruecklich alle fuenf Probearten in beiden Modalitaeten. Diese
All-of-Aggregation muss vor Materialisierung gebunden werden.

## Entscheidung

Vier Pruefungen stoppen fail-closed. Die Entscheidung lautet:

```text
BLOCKED_STATIC_CONTRACT_CORRECTION_REQUIRED_NO_EXECUTION
```

Auditdigest:

```text
604b9b52d32dcd5b0bf5e00c91d043f459c22e122eb1f52300826fd33bbed0fd
```

`8 von 8` statische Auditstrukturtests bestehen. Es gibt keinen technischen
Funktions- oder MCM-Memory-Befund. Die vier Blocker betreffen den
Versuchsvertrag, nicht die implementierte private Zustands- oder Probegrenze.

## Naechster Schritt

S1-WY ist ausschliesslich als statischer Korrekturvertrag fuer diese vier
Punkte vorgesehen: erreichbarer innerer Schwellenkorridor, getrennte
Verhaltens- und Metadatenrollen, kanonische No-Memory-Nullrolle und
All-of-Aggregation ueber beide Modalitaeten. Noch keine Fixture-, Matrix-,
Probe-, Baseline- oder Feldausfuehrung.

## Grundlage

- [S1-WW vollstaendiger Bildungs-/Probevertrag](S1WW_PPB1_STATISCHER_BILDUNGS_UND_PROBE_FUNKTIONSVERTRAG.md)
- [Maschinenlesbarer S1-WX-Audit](S1WX_PPB1_STATISCHER_VOLLSTAENDIGKEITS_FAIRNESS_UND_NICHTZIRKULARITAETSAUDIT_V1.json)
