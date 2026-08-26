# S1-FU: Statische Realadapter-Anschlusskartierung

## Ergebnis

S1-FU prueft die vorhandenen Produktionsschnittstellen, ohne sie aufzurufen.
Sechs Bausteine sind unveraendert wiederverwendbar:

- frische S1-FI-Formationseingaben;
- realer Windows-RAM-Snapshot;
- Fuenfarm-Formation fuer r2/r4/r8;
- S1-FF-Capture der 15 Formationsergebnisse;
- S1-FD-Formationskontrolle und Konvergenzauswertung;
- EC46-Entscheidung nach vollstaendiger Rueckgabe.

Drei Bausteine sind technisch nutzbar, brauchen aber eine neue enge Bindung:

- die frische objektgetrennte Feldkopie;
- der bestehende P0-/Frozen-E1-Probe-Wrapper;
- der vorhandene Fixed-Adapter-Feldkern.

## Exakte Luecke

Der alte reale Probevertrag besitzt acht Rollen. S1-FP verlangt zusaetzlich
`fixed-adapter-ab` und `fixed-adapter-ba`. Der alte Wrapper ruft den bereits
vorhandenen Fixed-Adapter-Kern nicht auf.

S1-FL bildet und erfasst die 15 Formationsergebnisse, gibt in seinem
Resultat aber keine lebenden E1-Zustandsobjekte aus. Damit kann eine spaetere
Probe nicht im selben Prozess an genau diese Objekte anschliessen.

Es fehlen deshalb genau:

1. eine zehnrollige S1-FP-Slotbindung ohne alte Kontaktachse;
2. ein typisierter Live-State-Handoff von Formation zu Probe;
3. ein Fixed-Adapter-Probewrapper mit Receipt;
4. eine 45-Aufruf-Koordination mit Schritt-, Zeit- und Abbruchkontrolle;
5. ein atomarer Rohvektor-Kompositor vor EC46.

Entscheidung:
`EXISTING_KERNELS_REUSABLE_LIVE_STATE_HANDOFF_AND_TEN_ROLE_COORDINATION_MISSING`.

## Bedeutung und Grenze

Fuer diesen Anschluss ist keine neue Feldmechanik erforderlich. Das ist ein
technischer Integrationsbefund, kein Nachweis fuer E1 als Memory, Feldzeit,
Reaktivierung, Organisation oder KI. S1-FU implementiert keinen Realrunner,
liest keine Ressourcen, fuehrt keinen Feldschritt aus und autorisiert nichts.

## Bester naechster Schritt

S1-FV sollte einen statischen Vertrag fuer die zehnrollige Slotbindung und
den Live-State-Handoff formulieren. Er muss Objektidentitaet,
Zustandsunveraenderlichkeit, Fixed-Adapter-Ableitung und fail-closed
Vollstaendigkeit binden. Noch keine Adapter- oder Runnerimplementierung,
Besitzerautorisierung oder Ausfuehrung.
