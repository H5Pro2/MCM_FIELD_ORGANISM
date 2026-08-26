# Lauf 189

## Forschungsfrage und Vorregistrierung

Geprueft wurde, ob zwei unterschiedliche kontrollierte AV-Vorgeschichten bei
exakt angeglichenem schnellen S/H-Zustand und anschliessend identischer,
einmal reduzierter AV-Probe eine kausal der entstandenen M-Konfiguration
zuordenbare spaetere S/H-Wirkung erzeugen.

Verbindliche Vorregistrierung:

- `docs/K2_F3_P2_GESCHICHTSTRAEGER_VORREGISTRIERUNG.md`;
- drei Sekunden Geschichte, danach eine Sekunde gemeinsame Probe;
- unveraenderte Parameter aus Lauf 188;
- aktive Integration mit 4n;
- natural, M-neutral, eta-null, M-swap und P0;
- keine Wiederholung oder ergebnisabhaengige Parameterkorrektur.

## Eingangs- und Kausalkontrollen

```text
same history supports:       321
changed history supports:    321
shared probe supports:       101
shared probe digest:         dba4ae9b51af783ec4abe195eacaac98be94380f1e7125d6cf56f154a15cc927
fast S/H alignment exact:    true
```

Die Probe wurde mit frischen Audio- und Videorezeptoren genau einmal
reduziert und unveraendert in allen zehn Probe-Armen verwendet. Damit wurde
die bekannte Rezeptorvermischung aus Lauf 187 ausgeschlossen.

## Beobachtete Messung

Unterschied der nach den beiden Geschichten entstandenen M-Vektoren vor der
Probe:

```text
M Linf: 0.00122577694223913
M L2:   0.0026468355527541607
```

Nach exakter S/H-Nullangleichung und derselben Probe:

```text
natural S Linf:       0.00010544892805826322
natural H Linf:       0.0001709433621777806
M-neutral S Linf:     0.0
M-neutral H Linf:     0.0
eta-null S Linf:      0.0
eta-null H Linf:      0.0
P0 S Linf:            0.0
P0 H Linf:            0.0
```

Vollstaendiger M-Tausch:

```text
swapped.same == natural.changed: true
swapped.changed == natural.same: true
```

Die Gleichheit umfasst jeweils Activation-, Afterimage- und M-Vektor sowie
den gesamten Snapshotdigest. Die spaetere Wirkung wanderte somit bitgenau
mit der getauschten M-Konfiguration.

Invarianten:

```text
groesster M-Gesamtmassenfehler: 1.1179945857975326e-13
erlaubter Fehler:               1e-12
kleinstes beobachtetes M:       0.011540680468493155
negative M-Werte:               keine
S/H-Bereichsverletzung:         keine
```

## Vorregistrierte Entscheidung

Alle neun Kontrollen waren positiv:

```text
history_m_differs:                 true
fast_alignment_exact:              true
natural_probe_effect:              true
m_neutral_effect_removed:          true
eta_null_effect_removed:           true
m_swap_same_matches_changed:       true
m_swap_changed_matches_same:       true
p0_histories_collapse:             true
state_invariants_hold:             true

decision: CAUSAL_M_HISTORY_CARRIER
```

## Technische Interpretation

Unter der festen K2/F3-Kandidatenform ist M damit erstmals als langsamer
kausaler Geschichtstraeger isoliert:

1. Unterschiedliche normale Weltgeschichte erzeugte unterschiedliches M.
2. Der schnelle Zustand S/H wurde vor der Probe exakt gleichgesetzt.
3. Dasselbe aktuelle Rezeptorereignis erzeugte danach unterschiedliche S/H-
   Fortsetzungen.
4. Die Differenz verschwand bei gleichfoermigem M und bei ausgeschalteter
   M-zu-S-Rueckarbeit.
5. Die vollstaendige Wirkung wanderte beim M-Tausch bitgenau mit.

Damit ist Evidenzstufe E1 des bestehenden Vertrags fuer diesen Kandidaten
technisch erfuellt. Der Befund laesst sich nicht durch verbliebenes schnelles
S/H-Nachhallen oder unterschiedliche aktuelle Rezeptorfolgen erklaeren.

## Grenzen und Nichtnachweise

- M ist in diesem Versuch eine deklarierte konservative Drift-
  Diffusionsvariable der K2/F3-Form.
- Geometrische Verteilung gegen Werteverteilung oder globale Momente wurde
  noch nicht getrennt.
- Wiederholte Teilnahme, Verdichtung, funktionale Loesung und andere
  Wiederpraegung wurden nicht untersucht.
- Lokale Spur-, Hysterese- und Reaktions-Diffusionsbaselines wurden in diesem
  Lauf nicht ausgefuehrt.
- Der Befund belegt keinen inneren Kontext im weitergehenden Sinn und kein
  MCM-Memory, keine Organisation, Topologie, Semantik oder KI.

## Ergebnisartefakt

```text
reports/mcm_f3_history_lauf_189.json
```

Der Einmal-Runner verweigert eine zweite Ausfuehrung, solange das Artefakt
vorhanden ist.

## Bester naechster Schritt

Als naechstes muss Evidenzstufe E2 vorregistriert werden: Eine feste
geometrische M-Permutation und eine massenbilanzierte lokale
M-Neutralisierung muessen bei weiterhin identischem S/H-Start und derselben
Probe testen, ob die Wirkung von der konkreten raeumlichen Zuordnung des M-
Vektors abhaengt und nicht nur von seiner Werteverteilung oder einem globalen
Moment. Erst danach ist eine Untersuchung wiederholter Teilnahme und
Feldzeitverdichtung methodisch sinnvoll.
