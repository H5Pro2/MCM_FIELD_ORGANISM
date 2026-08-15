# S1-JZ: Endlicher Orchestrator-API-, Initialisierungs- und Outputvertrag

## Ergebnis

S1-JZ schliesst die acht in S1-JY gefundenen Schemaluecken, ohne einen Runner
zu implementieren oder ein Intervall auszufuehren.

Die spaetere private Runner-API erhaelt nur `schema_id` und eine exakte
S1-JX-Replik-ID. Felder, private Zustaende, Kandidatendaten, Schwellenwerte
und Retrysignale sind als Aufrufargumente ausgeschlossen.

## Frischzustandsregistry

Fuer sechs Rollen und zwei Geometrien sind zwoelf vollstaendige Records
gebunden. Jeder Record enthaelt:

- die vollstaendige S1-JN-Feld-, Layer-, Geometrie-, Knoten- und Dockidentitaet;
- S/H, Wahrnehmungstick und Rezeptorkontakt im exakten Nullzustand;
- keinen vorherigen Distributionsabschluss und keinen L-Zustand im Feld;
- fuer B1 den geometriegebundenen festen Adapter mit internem Kantendigest;
- fuer B2 vollstaendiges knotengebundenes Null-L;
- fuer B3 bis B6 den rolleneigenen Arm und uniforme Gesamtmasse eins;
- kanonische Feld- und Privatzustandsdigests.

## Checkpoints und Komponenten

Das Checkpointrecord bindet Replik, Sequenz, Ordinal, Intervall, Knotenfolge,
vollstaendiges S/H sowie Feld-, Privatzustands- und Adapteroutputdigest.

Alle 28 Komponenten sind einzeln indexiert. Die Ordnung ist je Vergleich:
Checkpointvergleich, dann `activation`, dann `afterimage`, jeweils in
kanonischer Knotenfolge. Das Vorzeichen ist immer links minus rechts. Die
Blockgroessen bleiben 8/8/6/6.

## Ausgabe und Fehler

Das versionierte Replikausgabeschema enthaelt nur die vollstaendige
Replikidentitaet, Sequenzdigests, Checkpoints, signed Komponenten,
Adapterdiagnostik und den kanonischen Outputdigest. Die einzige spaetere
Fehlerfamilie ist `DTS1OneReplicaOrchestratorError`; Retry, Reparatur und
Teilausgabe sind gesperrt.

## Technisches Exemplar

Als einziges naechstes Implementierungs- und Testexemplar ist
`B1:P_IE_CAUSAL_TWO_SUBSTEP:r2` gebunden. Eine Wiederholung umfasst vier
Intervalle und vier Checkpoints. Zwei deterministische Wiederholungen duerfen
zusammen hoechstens acht technische Intervallaufrufe ausloesen und muessen
dieselben acht signed Komponenten liefern.

Entscheidung:

`FINITE_ONE_REPLICA_RUNNER_API_INITIALIZERS_COMPONENT_INDEX_OUTPUT_AND_ERROR_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`afc1c2d752aca9e5dd62a5f8ceb08859669e105108c6b23138d67d19aa3d508d`

## Naechster zulaessiger Schritt

S1-KA darf ausschliesslich Frischzustandsfactory und privaten reinen Runner
fuer das eine gebundene B1/P_IE/r2-Exemplar implementieren und zweimal mit
hoechstens acht technischen Intervallaufrufen pruefen. Keine andere Replik,
kein vollstaendiger Matrixfall, keine Runtime und keine Forschungsprobe.
