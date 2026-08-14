# S1-EC48: Statischer Common-Probe-Real-Kernel-Audit

## Forschungsfrage

Besitzt das Projekt bereits die technischen Grundkerne fuer den in EC45
definierten Acht-Rollen-Common-Probe-Vergleich, oder waere dafuer eine neue
Substratmechanik erforderlich?

## Vorhandene Kerne

Der statische Audit bestaetigt:

- Der vorbereitete reale Bildungskern kann aktive und bildungsablatierte
  AB/BA-Zustaende auf getrennten Kopien erzeugen.
- `E1ConfirmationFormationResult` traegt `b_ab`, `b_ba`,
  `b_ab_formation_ablated` und `b_ba_formation_ablated` getrennt.
- Der neutrale transiente Feldkern ist fuer P0 vorhanden.
- Der eingefrorene E1-Probekern ist vorhanden.
- Die E1-Rueckwirkung besitzt einen expliziten booleschen Schalter
  `backreaction_enabled`.
- Der vorhandene kanonische Probeadapter erzeugt objektgetrennte, anfangs
  identische frische Felder.
- Aktive AB/BA- und Rueckwirkungsablationsarme existieren bereits.

Damit sind die benoetigten Grundkerne ausreichend. Es ist keine neue
Substratgleichung erforderlich.

## Adapterluecke

Der vorhandene Sieben-Arm-Probeweg ist nicht identisch mit EC45:

1. Er besitzt nur einen gemeinsamen P0-Slot statt `p0-reset-ab` und
   `p0-reset-ba`.
2. Die vorhandenen bildungsablatierten AB/BA-Zustaende werden nicht als
   eigene Probe-Slots durch den eingefrorenen Rueckwirkungsweg gefuehrt.

Die fehlenden Adapterrollen sind daher exakt:

- `p0-reset-ab`
- `p0-reset-ba`
- `e1-formation-ablated-ab`
- `e1-formation-ablated-ba`

## Entscheidung

`KERNELS_AVAILABLE_NARROW_EIGHT_ROLE_ADAPTER_MISSING`

Ein enger Acht-Rollen-Adapter darf implementiert und zunaechst nur mit
injizierten synthetischen Kernreceipts abgenommen werden. Reale Feldschritte,
Persistenz, Forschungsentscheidungen und Claims bleiben gesperrt.

15 fokussierte gemeinsame Tests bestehen.

Audit-Digest:
`8f7d15694e909c159e5bc8afad313490af1276acfec73b4d79f2af2173c9be7a`

## Naechster Schritt

Am besten geht es mit S1-EC49 weiter: den engen Acht-Rollen-Adapter mit
injizierbaren Bildung-, Reset- und Probe-Kernschnittstellen implementieren
und ausschliesslich synthetisch abnehmen. Noch keine reale Probeausfuehrung.
