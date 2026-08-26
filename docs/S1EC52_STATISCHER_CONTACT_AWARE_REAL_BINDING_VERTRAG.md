# S1-EC52: Statischer kontaktbewusster Real-Binding-Vertrag

## Ziel

EC52 bindet die in EC51 korrigierte n1/n2-Common-Probe-Matrix an die
vorhandenen realen Schnittstellen, ohne eine gebundene Funktion aufzurufen.

## Bildungsbindung

Der Vertrag verwendet den bestehenden EC27-Planbestand mit Digest
`b53d1e1c...65ea`. Fuer jeden Kontaktzweig und jede Verfeinerung werden vier
Zustandsrollen gebunden:

- aktiv AB an den Wiederholungsplan;
- aktiv BA an den Kontinuierlich-Plan;
- bildungsablatiert AB an den Wiederholungsplan;
- bildungsablatiert BA an den Kontinuierlich-Plan.

Damit sind 24 Bildungszustands-Slots definiert.

## Probebindung

Alle 48 Probe-Slots verwenden dieselbe feste Probequelle mit Digest
`c0a9a59fb93996bdfd95247a1f6feec19723aeb36c84bd8bc8a423e677fbea7d`.

Jeder Slot verlangt eine eigene tiefe Kopie desselben vorbereiteten frischen
Ausgangsfeldes. Die Kernbindung lautet:

- P0-reset: `advance_neutral_fast_shared_field_transient`;
- alle E1-Rollen: `advance_frozen_e1_fast_shared_field_transient`;
- aktive und bildungsablatierte Rollen: Rueckwirkung an;
- Probe-Rueckwirkungsablation: Rueckwirkung aus.

Aktive Zustandsobjekte duerfen nur zwischen dem passenden aktiven Slot und
seiner Rueckwirkungsablation wiederverwendet werden. Die Probefelder bleiben
immer getrennt.

## Entscheidung

`REAL_INTERFACES_BOUND_ADAPTER_IMPLEMENTATION_MISSING`

Der typisierte Real-Adapter darf als naechster Schritt implementiert werden.
Feldschritte, Persistenz, Forschungsentscheidungen und Claims bleiben
gesperrt.

Zwoelf fokussierte gemeinsame Tests bestehen.

Vertragsdigest:
`291ea70c96ad26b3f6e696588ebd55d3e6f7163967b45de9a689bd731cb7bf7b`

## Naechster Schritt

Am besten geht es mit S1-EC53 weiter: den kontaktbewussten Real-Adapter mit
injizierbaren Plan-, Bildungs-, Fresh-Field- und Probe-Kernen implementieren
und nur durch typisierte Nullschritt-Receipts abnehmen. Noch keine reale
Bildung oder Probe.
