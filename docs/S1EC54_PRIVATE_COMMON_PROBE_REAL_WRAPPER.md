# S1-EC54: Private Common-Probe-Real-Wrapper

## Ziel

EC54 implementiert vier private Wrapper fuer den EC53-Adapter:

1. kontakt- und verfeinerungsgebundene Planauflosung;
2. Bildung genau eines benoetigten E1-Zustands;
3. Erzeugung einer tiefen, digest-identischen Fresh-Field-Kopie;
4. Ausfuehrung genau eines neutralen oder Frozen-E1-Probe-Slots.

## Gebundene Eigenschaften

Der Resolver ordnet n1/n2 den vorhandenen EC27-Planpaaren zu und verwendet
fuer AB den Wiederholungsplan sowie fuer BA den Kontinuierlich-Plan. Alle
Slots erhalten denselben festen Common-Probe-Plan der jeweiligen
Verfeinerung.

Der Bildungswrapper ruft ausschliesslich den bereits gebundenen
`run_prepared_real_formation_arm_in_memory`-Kern auf.

Der Fresh-Field-Wrapper erzeugt eine tiefe Objektkopie und verlangt einen
identischen initialen Felddigest.

Der Probe-Wrapper:

- verwendet fuer P0 den neutralen transienten Feldkern;
- verwendet fuer E1 den Frozen-E1-Kern;
- uebernimmt den vorregistrierten Rueckwirkungsschalter des Slots;
- prueft, dass das eingefrorene Zustandsobjekt und sein Digest unveraendert
  bleiben;
- liefert nur terminale Aktivierungs-/Nachhallvektoren und technische
  Zaehler;
- besitzt keinen Schreibpfad und keine Claim-Rolle.

## Entscheidung

`REAL_WRAPPERS_IMPLEMENTED_SMALL_FIXTURE_MISSING`

Elf fokussierte gemeinsame Tests bestehen. Die Tests auditieren Struktur und
Signaturen; kein Wrapper und kein Feldkern wurde ausgefuehrt.

Audit-Digest:
`cc80b40fc7b7c97bcab7135da10a23e45d739572f9b94ff6f7bf45bb836b2bfb`

## Naechster Schritt

Am besten geht es mit S1-EC55 weiter: nur einen kleinen kontrollierten
P0-Slot und ein passendes Frozen-E1-Aktiv/Ablationspaar auf einer vorhandenen
kleinen Fixture ausfuehren. Keine 48-Slot-Matrix, keine Persistenz und keine
Forschungsentscheidung.
