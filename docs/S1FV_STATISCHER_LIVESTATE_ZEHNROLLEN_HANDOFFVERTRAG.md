# S1-FV: Statischer Live-State-Zehnrollen-Handoffvertrag

## Quellzustaende

S1-FV bindet pro Verfeinerung vier lebende E1-Probequellen:

```text
active-ab                 <- Formation-Arm ab
active-ba                 <- Formation-Arm ba
formation-ablated-ab      <- Formation-Arm ab_formation_ablated
formation-ablated-ba      <- Formation-Arm ba_formation_ablated
```

Ueber r2/r4/r8 sind das zwoelf lebende Zustandsobjekte. Die drei
`ab_identity`-Ergebnisse bleiben Formationskontrollen und duerfen keine Probe
speisen.

## Zehn Rollen

Je Verfeinerung werden zehn Rollen gebunden:

- zwei P0-Arme ohne Zustand;
- aktive AB/BA-Arme mit Rueckwirkung;
- AB/BA-Probeablationsarme mit denselben aktiven Zustandsobjekten, aber ohne
  Rueckwirkung;
- zwei Formationsablationsarme mit ihren eigenen abgetragenen Zustaenden;
- zwei Fixed-Adapter-Arme, deren Adapter aus den exakten aktiven
  Zustandsobjekten abgeleitet werden.

Damit verwenden 24 der 30 Probe-Slots einen der zwoelf lebenden Zustaende.
Sechs P0-Slots besitzen keinen Zustand. Sechs Fixed-Adapter werden abgeleitet.

## Identitaetsgrenze

Ein Digest oder ein rekonstruierter Capture-Vektor darf das lebende Objekt
nicht ersetzen. Die exakte Objektidentitaet aus dem aktuellen
Formationsergebnis muss bis zum Probe-Handoff erhalten bleiben. Alle
abhaengigen Proben muessen den Zustand unveraendert lassen. Auch die
Fixed-Adapter-Ableitung darf ihn nicht veraendern.

Die Slotbindung enthaelt keine alte Kontaktachse und keine n1/n2-Wiederholungs-
oder Continuous-Semantik.

## Status

Entscheidung:
`TEN_ROLE_LIVE_STATE_HANDOFF_BOUND_IMPLEMENTATION_MISSING`.

Nur eine synthetische Handoff-Implementierung ist als naechster Schritt
zulaessig. Realadapter, Runner, Besitzerautorisierung, Feldschritte,
Persistenz und Claims bleiben geschlossen.

## Bester naechster Schritt

S1-FW sollte den zwoelfobjektigen Handoff und alle 30 Slotbindungen mit
synthetischen lebenden E1-Zustaenden abnehmen. Zu pruefen sind Objektidentitaet,
Mehrfachrouting, Unveraenderlichkeit und Fixed-Adapter-Ableitung. Noch kein
realer Probeadapter, Runner oder Feldschritt.
