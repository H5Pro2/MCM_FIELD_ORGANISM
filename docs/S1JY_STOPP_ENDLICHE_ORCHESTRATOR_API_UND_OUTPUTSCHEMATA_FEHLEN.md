# S1-JY: STOPP endliche Orchestrator-API und Outputschemata fehlen

## Ergebnis

S1-JY stoppt vor dem ersten Orchestratorcode. S1-JX bindet Sequenzen,
Carrygrenzen, Repliken, Checkpoints, Komponentenzahlen und Atomaritaet. Diese
Bindungen reichen aber noch nicht aus, um eine konkrete Runner-API ohne
verdeckte neue Entscheidungen zu implementieren.

## Acht fehlende Bindungen

1. Es fehlt eine versionierte Runner-Signatur mit einem vollstaendigen
   unveraenderlichen Inputrecord fuer genau eine Replik.
2. Es fehlen kanonische vollstaendige Frischfeld- und Privatzustandspayloads
   samt Digests fuer sechs Rollen und zwei Geometrien.
3. Die Initialisierungspruefung fuer B1-Fixed-Payload, B2-Null-L und uniforme
   B3-bis-B6-M-Zustaende ist noch nicht an endliche Records gebunden.
4. Es fehlt ein versioniertes Checkpointrecord mit exakten Keys und
   Digestrollen.
5. Die 8/8/6/6-Komponentenzahlen und Vorzeichen sind gebunden, nicht jedoch
   jeder Index als eindeutiges Tupel aus Sequenz, Checkpoint, Kanal, Knoten
   und Vorzeichen.
6. Es fehlt ein versioniertes vollstaendiges Replikausgabeschema samt
   kanonischem Outputdigest.
7. Es fehlt eine einheitliche Runner-Fehlergrenze mit gebundenen
   Ausnahmefamilien und ausdruecklichem Verbot von Teilausgaben.
8. Es fehlt genau eine ausgewaehlte technische Beispielreplik samt endlichem
   Aufrufbudget fuer die Implementierungsabnahme.

Die Auswahl dieser Werte direkt im Runner wuerde die spaetere Profilform,
Initialisierung und Abnahme verdeckt festlegen. Deshalb wurde kein
Materializer oder Adapter aufgerufen.

## Erhaltener Stand

Alle S1-JX-Records fuer sieben Sequenzen, 72 Repliken, 24 Faelle, 414
geplante Intervalle und die Carry-/Checkpoint-/Atomaritaetsregeln bleiben
gueltig. Ebenso bleiben S1-JW, S1-JO, S1-JR und die korrigierten
S1-IR-Profile unveraendert.

Entscheidung:

`STOPP_ONE_REPLICA_ORCHESTRATOR_FINITE_API_INITIALIZERS_AND_OUTPUT_SCHEMAS_MISSING`

Kanonischer Auditdigest:

`e383b88f95ed6f19b8e31cfcaf892f87dc26f642edee326fde70252340750eb7`

Es wurde kein Orchestrator implementiert, keine technische Replik und kein
Profilfall ausgefuehrt und kein Baselineintervall aufgerufen.

## Naechster zulaessiger Schritt

S1-JZ darf ausschliesslich die fehlenden endlichen Input-, Frischzustands-,
Checkpoint-, Komponentenindex-, Output-, Digest- und Fehlerrecords binden und
genau eine technische Beispielreplik samt Aufrufbudget auswaehlen. Noch keine
Implementierung, kein Materializer- oder Adapteraufruf, kein Matrixfall, keine
Runtime und keine Forschungsprobe.
