# S1-EC65: Statische reale Aufrufadapter

## Zweck

S1-EC65 verbindet die vorhandenen EC54-Wrapper mit den verlustfreien
EC64-Konvertern. Die Adapter sind implementiert, werden in dieser Stufe aber
nicht aufgerufen. Geprueft werden ausschliesslich Signaturen,
Aufrufreihenfolge und Schreibfreiheit.

## Adapter

### Bildung

`run_e1_common_probe_real_formation_receipt_adapter`

1. ruft genau einen EC54-Bildungswrapper mit aufgeloestem Slot,
   Ausgangsfeld und Ausgangszustand auf;
2. uebergibt dessen Output unmittelbar an den EC64-Bildungskonverter;
3. gibt ein positives EC63-Bildungsreceipt zurueck.

### Fresh Field

`build_e1_common_probe_real_fresh_field_adapter`

- delegiert genau einen Slot und das Ausgangsfeld an den vorhandenen
  EC54-Fresh-Field-Wrapper;
- fuegt keine eigene Feldlogik hinzu.

### Probe

`run_e1_common_probe_real_probe_receipt_adapter`

1. entnimmt den eingefrorenen Zustand ausschliesslich dem zugeordneten
   EC63-Bildungsreceipt oder verwendet fuer P0 `None`;
2. ruft genau einen EC54-Probewrapper auf;
3. uebergibt dessen Output unmittelbar an den EC64-Probekonverter;
4. gibt ein positives EC63-Probereceipt zurueck.

## Statische Abnahme

- alle drei Signaturen sind eng und koordinator-kompatibel;
- Bildung und Probe halten strikt Wrapper vor Konverter ein;
- der Probe-Zustand stammt nur aus dem Bildungsreceipt;
- keine Persistenz- oder Schreibpfade;
- der Audit ruft keinen Adapter auf;
- 19 fokussierte Tests bestanden.

Entscheidung:

`REAL_CALL_ADAPTERS_IMPLEMENTED_STATICALLY_NOT_RELEASED`

Audit-Digest:

`dba7a309bf49dfb57881883a049c80d7c58ea5a98f74ef0744167b2a26d718af`

## Grenze

Die Adapter enthalten reale Aufrufpfade, sind aber nicht zur Ausfuehrung
freigegeben. Es wurden keine Feldschritte ausgefuehrt. Das Ergebnis ist keine
Forschungsevidenz und kein Memory-Nachweis.

Am besten geht es mit S1-EC66 weiter: einen positiven-Schritt-Koordinator
definieren, der exakt vier Bildungsadapter, acht Fresh-Field-Adapter und acht
Probeadapter bindet und ein auf 3.208 Schritte begrenztes Gesamtergebnis
erzeugt. Zunaechst nur mit injizierten positiven synthetischen Receipts
abnehmen; EC65-Adapter nicht aufrufen.
