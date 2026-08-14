# S1-GN: Typisierter Live-Field-Carrier

Stand: 2026-08-15

Status: `SYNTHETISCHE_CARRIER_ABNAHME_KEIN_FELDLAUF`

## Umsetzung

S1-GN implementiert den in S1-GM geforderten expliziten Traeger des
fortlaufenden Feldobjekts:

```text
Fresh-Field-Binding
-> LiveFieldCarrier(current_field = exaktes frisches SharedMCMField)
-> Batch + Carrier
-> LiveFieldCarrierTransition
-> naechster Carrier
```

Der Carrier bindet Feldobjekt, Binding, Anfangs- und aktuellen Felddigest,
Neuronenreihenfolge, abgeschlossene Batchanzahl, Supportbilanz und
tatsaechliche Feldschritte.

## Synthetische Transition

Die S1-GN-Transition fuehrt keinen Feldkernel aus. Sie erzeugt ein neues
Carrierobjekt, traegt aber dasselbe explizite `SharedMCMField` weiter. Dadurch
werden Batchreihenfolge und Supportbilanz fortgeschrieben, waehrend
Felddigest und Feldobjekt unveraendert bleiben und reale Feldschritte null
sind.

Die sechs Plaene erreichen gemeinsam:

- 2.800 abgeschlossene Batches;
- 660 Supportereignisse;
- null reale Feldschritte.

Kreuzbindung, falsche Batchreihenfolge und manipulierte Schrittbilanz brechen
fail-closed ab. Es gibt keinen globalen, Closure- oder anderweitig versteckten
Feldzustand.

Entscheidung:

```text
EXPLICIT_LIVE_FIELD_CARRIER_SYNTHETIC_TRANSITION_VALIDATED_REAL_ADAPTER_CLOSED
```

Dies ist eine technische Zustandsweitergabe, kein Feld-, Substrat- oder
Memory-Befund.

## Bester naechster Schritt

S1-GO revidiert den privaten S1-GL-Wrapper auf die Carrier-Schnittstelle und
nimmt den vollstaendigen Sechsarmablauf erneut mit der synthetischen S1-GN-
Transition ab. Der Tokenpfad bleibt als historische Kontrollflussfixture
erhalten; der reale Batch-Adapter bleibt geschlossen.
