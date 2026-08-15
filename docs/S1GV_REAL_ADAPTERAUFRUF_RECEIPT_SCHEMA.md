# S1-GV: Real-Adapteraufruf-Receipt-Schema

Stand: 2026-08-15

Status: `UNVERAENDERLICHES_SCHEMA_KEINE_FACTORY_KEINE_AUSFUEHRUNG`

## Umsetzung

S1-GV implementiert das unveraenderliche, typisierte Schema fuer ein spaeteres
einzelnes Real-Adapteraufruf-Receipt. Es bindet strukturell:

- Gate-, Autorisierungs- und verbrauchten Token-Digest;
- Binding, Batchindex und Batchzeit;
- vorherigen Carrier- und Felddigest;
- naechsten Felddigest und Feldobjektwechsel;
- unveraenderte Quellzustands- und Fixed-Adapter-Digests;
- exakten Fixed-Adapter-Kernelnamen;
- genau einen Adapteraufruf und einen Feldschritt;
- geschlossene Persistenz- und Claim-Grenzen.

## Wichtige Trennung

Schema-Integritaet ist noch keine Ausfuehrungs-Authentizitaet. Ein strukturell
gueltiges Objekt beweist fuer sich allein nicht, dass externe Autorisierung,
Tokenverbrauch und Kernelaufruf wirklich atomar stattgefunden haben.

Deshalb besitzt S1-GV keine Receipt-Factory und erzeugt keine Receipt-Instanz.
Der spaetere Authentizitaetspfad muss die typisierten externen Autorisierungs-
und Realtokenobjekte mit dem atomaren Einbatch-Adapter verbinden.

Entscheidung:

```text
REAL_ADAPTER_CALL_RECEIPT_SCHEMA_READY_AUTHENTICITY_PATH_ABSENT
```

Es wurde kein Adapter oder Feldkernel ausgefuehrt. Dies ist kein Feld-,
Substrat- oder Memory-Befund.

## Bester naechster Schritt

S1-GW bindet statisch das externe Besitzer-Autorisierungsobjekt fuer genau
einen spaeteren Real-Batch. Inhalt, Scope, Frische, Laufbindung und
Einmaligkeit werden festgelegt; es wird keine Freigabe aus der aktuellen
Unterhaltung abgeleitet und kein Token erzeugt.
