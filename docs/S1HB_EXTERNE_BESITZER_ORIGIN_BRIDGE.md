# S1-HB: Externe Besitzer-Origin-Bridge

Stand: 2026-08-15

Status: `INGRESS_BRIDGE_IMPLEMENTIERT_PRODUKTIVER_HOST_VERIFIER_FEHLT`

## Umsetzung

S1-HB implementiert die lokale Eingangsseite der externen
Besitzer-Autorisierungs-Bridge. Sie bindet einen vom Host gelieferten
Nachrichtenbeleg an das exakte S1-GY-Ziel und erzeugt daraus erst nach einem
positiven injizierten Origin-Verifier eine typisierte S1-GW-Autorisierung.

Geprueft werden unter anderem:

- authentifizierter Besitzer-Principal-Digest;
- Task-/Session-Bindung;
- frischer Einmal-Nonce;
- Host-Attestierungs- und Nachrichtendigest;
- exakter Run-, Gate-, Binding-, Batch- und Carrier-Bezug;
- maximal ein Adapteraufruf und ein Feldschritt;
- nicht persistent, kein Retry, keine Nachparametrierung und keine Claims;
- Verfall nach Erfolg oder Fehler.

`ok weiter` und die bekannten Fortsetzungsformulierungen werden ausdruecklich
abgelehnt.

## Verbleibende Grenze

Das Repository besitzt laut EC115 keinen authentifizierten Host-
Nachrichtenkanal. S1-HB erfindet diesen nicht. Der Produktions-Verifier muss
spaeter von der Codex-/Orchestrator-Hostgrenze injiziert werden. Die Tests
verwenden nur einen synthetischen Verifier und beweisen daher ausschliesslich
die lokale Bindungslogik, nicht die Identitaet eines realen Besitzers.

Entscheidung:

```text
EXTERNAL_OWNER_ORIGIN_INGRESS_IMPLEMENTED_HOST_ATTESTOR_NOT_CONNECTED
```

Es wurde keine aktuelle Freigabe erzeugt, kein Token erstellt und nichts
ausgefuehrt oder persistiert.

## Bester naechster Schritt

S1-HC implementiert die reale prozesslokale Einmaltoken-Factory gegen eine
bereits durch S1-HB gebundene Autorisierung. Ihre Tests verwenden nur eine
synthetisch verifizierte HB-Autorisierung; der reale Hostpfad bleibt zu.
