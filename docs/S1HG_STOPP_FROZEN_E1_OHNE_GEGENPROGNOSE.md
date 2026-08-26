# S1-HG: STOPP Frozen-E1 ohne Gegenprognose

## Ausgangspunkt

Lauf 198 misst eine reale, nichtnullige und ueber r2/r4/r8 konvergierende
AB/BA-Wirkung der aus den E1-Endzustaenden abgeleiteten festen Adapter. Vor
der geplanten aktiven Frozen-E1-Probe ist deshalb zu pruefen, ob dieser Zweig
ueberhaupt eine andere Vorhersage besitzt.

## Quellbefund

`advance_frozen_e1_fast_shared_field_transient` fuehrt bei jedem Schritt
genau folgende Operationen aus:

1. denselben eingefrorenen E1-Zustand validieren;
2. daraus deterministisch `compute_e1_weighted_edge_rates` berechnen;
3. `_advance_with_fixed_adapter` aufrufen;
4. denselben unveraenderten E1-Zustand zurueckgeben.

`advance_fixed_e1_adapter_fast_shared_field_transient` ruft mit dem zuvor aus
demselben Zustand berechneten Adapter ebenfalls direkt
`_advance_with_fixed_adapter` auf. Feld, Probe, Adapter und Integrator sind
damit gleich. Die bestehende kanonische Komposition fordert folgerichtig
`fixed_adapter_residual == 0.0` und bitgenaue aktive/feste Gleichheit.

## Entscheidung

`STOPP_ACTIVE_FROZEN_E1_VS_FIXED_ADAPTER_NO_DISTINCT_PREDICTION`

Der aktive Frozen-E1-Teilzweig besitzt in der aktuellen Architektur keine
unterscheidbare Gegenprognose gegen Lauf 198. Die geplante 45-Aufruf-Kette mit
28.000 Feldschritten darf in dieser Form nicht ausgefuehrt werden, weil sie
eine konstruktiv erzwungene Gleichheit lediglich erneut messen wuerde.

Dies ist ein STOPP des Frozen-E1-Probezweigs, nicht des Gesamtprojekts.

## Erforderliches Umdenken

Ein neuer Substratkandidat muss waehrend oder zwischen Weltkontakten eine
lokale, begrenzte Dynamik besitzen, die nicht bei jedem Zeitpunkt vollstaendig
auf einen zustandsabgeleiteten festen Adapter reduzierbar ist. Vor einer
Gleichung sind mindestens eine unterscheidbare Funktionsprognose, endliche
Ressourcen, Abschwaechung, Interferenz, Freigabe und Gegenbaselines neu zu
binden. Diese Richtungswahl erfordert eine ausfuehrliche Besitzerentscheidung.

S1-HG fuehrt keinen weiteren Feldschritt aus und erzeugt keinen Memoryclaim.
