# S1-BR: E1 ablatierbarer Kantenratenadapter

## Status

Statischer Adapter- und Generatorvertrag. Noch keine Implementierung, keine
E1-gekoppelte S/H-Runtime, kein Snapshot-Schema, kein `current_api`-Export und
kein Memory-, Lern-, Organismus- oder KI-Befund.

## Technische Frage

Wie wird ein gueltiger isolierter E1-Zustand in die vorhandene schnelle
interne Felddiffusion rueckgekoppelt, ohne Rezeptorgrenzen, Weltkontakt,
Nachhall oder bestehende Runtimepfade implizit zu veraendern?

## Getrennte Adapterdatei

Die spaetere Implementierung liegt ausschliesslich in:

```text
mcm_field_organism/e1_weighted_field_adapter.py
```

Sie importiert den E1-Zustand und die vorhandenen Geometrievertraege. Das
bestehende Modul `neutral_local_field_substrate.py` bleibt in dieser Stufe
unveraendert.

## Basisrate

Die neutrale schnelle Feldantwort besitzt bereits:

```text
r_0 = 1 / response_time_seconds
```

`response_time_seconds` wird aus einem gueltigen
`NeutralLocalFieldSubstrateConfig` gelesen. E1 definiert keine zweite
Basiszeit und keine eigene Weltkontaktgeschwindigkeit.

## Gewichtete Kantenrate

Fuer jede vorhandene kanonische Kante `e` gilt im aktiven Adapterarm:

```text
r_e = r_0 * (1 + gamma * b_e / q_0)
```

mit:

```text
q_0    = state.contract.node_capacity
gamma  = state.contract.backreaction_gain
b_e    = vorhandene Bindung derselben Kante
```

Wegen `0 <= gamma <= 1` und `0 <= b_e/q_0 <= 2` bleibt:

```text
r_0 <= r_e <= 3 * r_0
```

Alle Kantenraten sind endlich, nichtnegativ und fuer beide Richtungen einer
ungerichteten Kante identisch.

## Technische Ablation

Der Adapter besitzt genau einen expliziten Versuchsparameter:

```text
backreaction_enabled: bool
```

Er ist kein Organismuszustand und keine regelbasierte Feldfunktion. Er wird
nur von einem kontrollierten Vergleichsarm gesetzt.

```text
backreaction_enabled = True
-> r_e = r_0 * (1 + gamma * b_e / q_0)

backreaction_enabled = False
-> r_e = r_0 fuer jede Kante
```

Der Ablationsarm behaelt denselben E1-Zustand unveraendert bei und entfernt
nur dessen Wirkung auf den Generator. Damit kann spaeter dieselbe Geschichte
mit Rueckwirkung an und aus verglichen werden.

## Adapterrollen

```text
E1WeightedFieldAdapterError(ValueError)

E1WeightedEdgeRate
    first_neuron_id
    second_neuron_id
    rate_per_second

E1WeightedFieldAdapterResult
    backreaction_enabled
    base_rate_per_second
    edge_rates
    edge_inventory_digest
```

Der Ergebniscontainer speichert keine Aktivierung, keine freie Ressource und
keine Zeitgeschichte. Kanten werden kanonisch sortiert und muessen das
vollstaendige vorhandene Inventar genau einmal abdecken.

## Reine Adapterfunktion

```text
compute_e1_weighted_edge_rates(
    layer,
    state,
    substrate_config,
    *,
    backreaction_enabled,
) -> E1WeightedFieldAdapterResult
```

Die Funktion:

1. validiert Layer und E1-Zustand mit
   `validate_e1_state_for_layer(...)`;
2. validiert `NeutralLocalFieldSubstrateConfig`;
3. akzeptiert fuer `backreaction_enabled` nur einen echten Booleschen Wert;
4. berechnet jede Rate direkt aus derselben Kantenbindung;
5. veraendert weder Layer, E1-Zustand noch Konfiguration;
6. besitzt keine versteckte Standardkonfiguration;
7. fuehrt keinen E1-Entwicklungsschritt aus.

## Gewichteter interner Generator

Eine zweite reine Funktion darf aus dem validierten Adapterergebnis den
internen Graphgenerator bilden:

```text
build_e1_weighted_diffusion_generator(layer, adapter_result)
    -> quadratische float64-Matrix G_E1
```

Fuer jede Kante `e = {i,j}` wird exakt eingetragen:

```text
G_E1[i,j] += r_e
G_E1[j,i] += r_e
G_E1[i,i] -= r_e
G_E1[j,j] -= r_e
```

Daraus folgen konstruktiv:

```text
G_E1 = transpose(G_E1)
G_E1 * 1 = 0
x^T G_E1 x <= 0
```

Der interne E1-Generator ist damit symmetrisch, massenerhaltend und
negativ-semidefinit. Er fuegt keinen externen Antrieb hinzu.

## Harte Rezeptorgrenze

E1 gewichtet ausschliesslich Kanten aus
`mcm_substrate_edge_inventory(layer)`. Rezeptorkontakte sind keine solchen
internen Kanten und bleiben spaeter unveraendert:

```text
interne Nachbarschaft:     G_E1 mit r_e
Rezeptor-Diagonalverlust:  weiterhin -r_0
Rezeptor-Randantrieb:      weiterhin +r_0 * contact
H-Nachhall:                weiterhin aus der resultierenden S-Trajektorie
```

E1 darf daher weder die Rezeptoramplitude multiplizieren noch einen Kontakt
erzeugen, unterdruecken oder nach Modalitaet gewichten.

## Null- und Kontrollfaelle

```text
b_e = 0 fuer alle e
-> aktiver und ablatierter Adapter liefern exakt r_0

gamma = 0
-> aktiver und ablatierter Adapter sind exakt identisch

backreaction_enabled = False
-> Ergebnis ist unabhaengig von der Verteilung von b_e

gleiche b_e-Verteilung auf permutierter Geometrie
-> Raten folgen ausschliesslich den permutierten Kantenidentitaeten
```

## Pflichtbaselines fuer eine spaetere Kopplung

```text
P0: heutiger neutraler S/H-Generator ohne E1-Zustand
A0: E1-Zustand vorhanden, Rueckwirkung aus
A1: E1-Zustand vorhanden, Rueckwirkung an
F0: eingefrorene aktive E1-Kantenraten als fester raeumlicher Gain
U0: uniformer fester Gain mit gleichem maximalen Ratenbereich
```

Der Adapter implementiert nur A0 und A1. P0 bleibt der unveraenderte
bestehende Pfad; F0 und U0 werden erst in einem spaeteren Laufvertrag
bereitgestellt.

## Fokussierte Abnahme vor Runtimekopplung

Die spaetere Adapterimplementierung muss mindestens pruefen:

1. aktive Ratenformel auf jeder vorhandenen Kante;
2. exakte Ablation auf `r_0` bei unveraendertem E1-Zustand;
3. exakte Neutralitaet fuer `b_e = 0` und `gamma = 0`;
4. Ratenbereich `r_0 <= r_e <= 3*r_0`;
5. vollstaendige Geometrie- und Digestbindung;
6. Symmetrie, Nullzeilensumme und Nichtpositivitaet des Generators;
7. Unveraenderlichkeit aller Eingaben;
8. keine Rezeptor-, H-, Snapshot- oder API-Rolle;
9. keine Exporte aus `__init__` oder `current_api`;
10. keine Aenderung am neutralen P0-Testverbund.

## Aussagegrenze

Ein bestandener Adaptertest zeigt nur, dass ein E1-Zustand technisch kausal
auf die spaetere interne Feldleitung wirken kann. Ohne eine gekoppelte
identische Probe nach angeglichenem S/H ist noch nicht einmal E2 erreicht.
Memory oder eine neue MCM-Natur werden nicht behauptet.

## Bester naechster Schritt

S1-BS hat den reinen Kantenratenadapter, den gewichteten internen Generator
und den fokussierten Adaptertest implementiert. Als naechstes spezifiziert
S1-BT die atomare Einbindung in einen neuen opt-in S/H-Schritt, bevor eine
bestehende Feldfunktion veraendert wird.
