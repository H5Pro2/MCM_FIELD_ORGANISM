# S1-DK: E1-Vertrag fuer eingefrorenen Zustandstransfer

## Zweck

S1-DK bindet den nach S1-DJ einzig zulaessigen Anschluss statisch. Die in
S1-DI veroeffentlichten Zustaende `b_AB` und `b_BA` sind feste Eingaben. Ihre
Entstehung wird weder erneut ausgefuehrt noch durch diesen Vertrag erklaert.

Der volle S1-DC-Befund bleibt gestoppt:

```text
FULL_S1_DC_BLOCKED_NARROW_STATE_TRANSFER_ONLY
```

## Gebundene Evidenz

```text
S1-DJ-Audit:
29dfe21e71206bd00210528f30a725c1e9377476209e8933d1391cfab942115b

S1-DI-Report:
831e535b0193d0bce03081545c5bda6bb4cc5655fd8b32cf77daa8a1b2fc9d1a

S1-DI-Ergebnis:
7fe242f667ff77b9c4e79e5800c890ab37d269c68ff6b52fccf12224645348d9

b_AB:
bf93d871f6352f82bf0b4d1a0f2cbdc0a577d0f27d03cbc34cbd57ccc2754f86

b_BA:
354d65d02435c31fcad31b182ae78fb3cce0c88180c3f0d9a847cc8e368eb014
```

## Festgelegte Probequelle

Die spaetere Probe verwendet nur den ersten A-Block der bereits gebundenen
reduzierten AV-Quelle:

```text
Feldzeitfenster       0 bis 1_000_000 Ticks
Taktrate              1_000_000 Ticks pro Sekunde
Audioframes           100
Videoframes           10
Supports gesamt       110
Feldknoten            84
E1-Kanten             145
Probequellendigest    c0a9a59fb93996bdfd95247a1f6feec19723aeb36c84bd8bc8a423e677fbea7d
```

Die grobe Vorschlagspartition `(0, 1_000_000)` und die geteilte Partition
`(0, 500_000, 1_000_000)` verwenden dieselbe Quelle. Damit bekommt die
spaetere Transferpruefung einen eigenen Numerikvergleich; er ersetzt nicht
den fehlenden S1-DC-Verfeinerungsrest.

## Sieben Kontrollarme

```text
p0    neutraler Zustand, Rueckwirkung aus
ab0   b_AB, Kantenadapter ablatiert
ba0   b_BA, Kantenadapter ablatiert
ab1   b_AB, zustandsabhaengiger Kantenadapter
ba1   b_BA, zustandsabhaengiger Kantenadapter
abf   b_AB, identisch eingefrorener Adapter
baf   b_BA, identisch eingefrorener Adapter
```

Verbindliche Identitaeten sind:

```text
P0 == AB0 == BA0              bitgenau
AB1 == ABF                    bitgenau
BA1 == BAF                    bitgenau
b_AB und b_BA                 waehrend der Probe unveraendert
frische Vorfelder             wertidentisch, objektseitig getrennt
alle 110 Supports             genau einmal zugeordnet
```

## Zulaessige Auswertung

Erfasst werden nur technische Distanzen der Vor-, Aktiv- und
Nachhallzustandsanteile, die Ablations- und Adapteridentitaeten, der
Probe-Partitionsrest sowie jede unerlaubte Aenderung der eingefrorenen
Zustaende. Zulaessige Entscheidungen sind:

```text
TECHNICALLY_UNDECIDABLE
NO_REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE
REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE
```

Auch ein spaeter registrierter Unterschied waere nur ein technischer
Transferunterschied der gegebenen Zustaende und des konstruierten Adapters.
Er waere kein Beleg fuer History-Ursache, Memory, Semantik, Organisation,
Topologie, Selbstregulation oder KI.

## Implementierung und Abnahme

Der private Builder
`mcm_field_organism/e1_frozen_state_transfer_contract.py` liest und
auditiert nur den veroeffentlichten S1-DI-Report, bindet Zustands- und
Probequellendigest und erzeugt den unveraenderlichen Vertrag. Er ruft keinen
History-Produzenten, Feldlauf oder Probeoperator auf.

```text
S1-DK-Vertragsdigest:
4574cf1caae3792a3721249dac73b4a589062051bb944fcf2f43f317b4e347f8

6 fokussierte Tests
138 relevante Verbundtests nach Gesamtabnahme
```

## Entscheidung

S1-DK ist statisch abgeschlossen. Die Implementierung des engen
Transferpfads ist freigegeben; seine reale Ausfuehrung ist nicht
freigegeben. Der volle S1-DC-Zweig bleibt gestoppt.

## Bester naechster Schritt

S1-DL implementiert den privaten Loader, die sieben Zustandsarme und den
reinen Ergebniscontainer. Zuerst werden nur synthetische Kontrollen und die
Ausfuehrungssperre abgenommen. Der gebundene reale Probeweg bleibt bis zu
einem gesonderten Einmallaufvertrag unaufgerufen.

## Anschlussstatus

S1-DL hat den Zustandsloader und den siebenarmigen Kompositor implementiert
und ausschliesslich synthetisch abgenommen. Kanonisch geladene Zustaende
bleiben vom Kompositor typseitig getrennt und nicht ausfuehrbar. Die reale
Probe wurde nicht aufgerufen. Der naechste Anschluss S1-DM ist deshalb ein
statischer Einmallaufvertrag, noch keine Ausfuehrung.
