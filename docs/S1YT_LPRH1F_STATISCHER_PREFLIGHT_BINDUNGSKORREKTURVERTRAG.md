# S1-YT: Statischer LPRH-1F-Preflight-Bindungskorrekturvertrag

## Ergebnis

S1-YT schliesst die sechs S1-YS-Luecken statisch. Die Mittelpunktregel hat
nur noch eine zulaessige Operationsreihenfolge: zuerst
`OFF-Aktivierung + Steering-Wert`, danach Multiplikation mit `0.5`.

## Korrigierte private Anatomie

Sechs private Typen tragen jetzt die tatsaechlichen Objekte und Werte:

- vorbereiteter `MCMNeuronDrive` mit seinem OFF-`MCMNeuronOutput`;
- ein vollstaendiger geordneter Vorbereitungssatz;
- ein Steering-Input mit LPRH-1-Handoff oder generischer Quelle und exakten
  Neuron-Dock-Carrier-Werten;
- lokale Ausgaben;
- vollstaendiger Ausgabesatz;
- atomarer Ergebnis- und Feldverbrauchsbeleg.

Fuer alle sechs Typen sind kanonische Digestpayloads festgelegt. Kandidat
und generische Baseline muessen dieselbe geordnete
Neuron-Dock-Carrier-Wert-Anatomie und denselben vorbereiteten OFF-Satz
verwenden.

## Aufruf- und Fehlergrenze

Die OFF-Vorbereitung besitzt alle Base-Transition-Aufrufe. Der Consumer ruft
die Transition nie auf und zaehlt nur seinen einen Aufruf sowie eine
Mittelpunktanwendung je lokalem Wert. Acht Fehlercodes und eine elfstufige
atomare Reihenfolge sind fest gebunden.

## Grenze

Noch wurde nichts implementiert oder ausgefuehrt. S1-YU muss diese
Schliessungen abschliessend statisch auditieren. API, `SharedMCMField`,
`MCMNeuronDrive`, Produktion und Feldlauf bleiben gesperrt.

Maschinenlesbarer Vertrag:
[S1YT_LPRH1F_STATISCHER_PREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json](S1YT_LPRH1F_STATISCHER_PREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json).
