# W7-AO: Statischer Aufloesungsvergleichsvertrag

## Entscheidung

`W7AO_R1_R2_R4_RAW_RESIDUAL_COMPARISON_CONTRACT_BOUND`

W7-AO bindet vor jeder Auswertung den kleinsten zulaessigen Vergleich des
realen W7-AN-Containers. Es wurden keine R1/R2- oder R2/R4-Distanzen gelesen
oder berechnet.

## Gebundener Eingang

Zulaessig ist ausschliesslich der nicht ausgewertete W7-AN-Container:

```text
4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5
```

Er muss `convergence_compared = false` und `effect_floor_ready = false`
tragen. Alle drei Aufloesungen muessen dieselbe einmalige W7-AI-P0-Referenz
lesen.

## Vergleichseinheit

Verglichen werden ausschliesslich die gerichteten CAP-minus-P0-
Rohresiduals der 35 identisch ausgerichteten Pfad-/Checkpointrollen. Fuer
jeden Tick und jeden Feldort gilt:

```text
Delta12_S = residual_R1_S - residual_R2_S
Delta12_H = residual_R1_H - residual_R2_H

Delta24_S = residual_R2_S - residual_R4_S
Delta24_H = residual_R2_H - residual_R4_H
```

Pfad, Checkpoint, Plandigest, Tickfolge, Neuronenordnung sowie S/H-Geometrie
muessen exakt uebereinstimmen. Aggregierte Skalarwerte duerfen keine
abweichende Rohtrajektorie verdecken.

## Metriken

Primaer und entscheidend sind je Rolle:

- `S_linf` der rohen S-Differenzen;
- `H_linf` der rohen H-Differenzen.

`SH_l2` ueber alle rohen S/H-Differenzen einer Rolle ist nur Diagnose und
darf keine gegenteilige Linf-Entscheidung ueberstimmen.

## Konvergenzregel

Fuer jede der 35 Rollen und fuer S sowie H muss gelten:

```text
D24 < D12
```

Zulaessige exakte Ausnahme:

```text
D12 = 0 und D24 = 0
```

Ein einzelnes `D24 >= D12` ausserhalb der exakten Null macht den aktuellen
Vergleich numerisch unentschieden. Es gibt keine Mittelung ueber Pfade und
keine nachtraegliche Auswahl nur guenstiger Rollen.

## Numerischer Boden

Unveraendert aus W7-L:

```text
epsilon_num = Maximum aller 35 R2/R4-S_linf- und H_linf-Abstaende
effect_floor = 10 * epsilon_num
```

Der Faktor 10 darf nach Sichtung der Werte nicht geaendert werden. Der
numerische Boden ist nur bei bestandener rollenweiser Konvergenz verwendbar.

## Gegenbaselines

Vor einer technischen Kontrastauflosung muessen gelten:

- Primaer gegen Gegenlauf ist fuer jede Aufloesung digest- und rohgleich;
- dieselbe Aufloesung gegen sich selbst hat exakt Abstand null;
- alle Rollen lesen dieselbe analytisch exakte P0-Referenz;
- R1 reproduziert die kanonischen W7-AE/AG/AK-Digests;
- Reihenfolge-, Passivitaets-, Starttrennungs- und Invariantenkontrollen des
  W7-AN-Containers bleiben bestanden.

Diese Kontrollen bestimmen keine Feldfunktion. LEAK, LIN, F3, CONST-V, SAT,
MOB, NORM, ETA0, KAPPA0 und SIGN aus W7-L sind im aktuellen Container nicht
enthalten. Deshalb darf W7-AO selbst bei geordneter Konvergenz hoechstens
einen technisch aufgeloesten CAP/P0-Rohkontrast feststellen.

## Stopplinien

Sofortiger Stopp gilt bei:

- einem anderen W7-AN-Containerdigest;
- fehlender Rollen-, Tick- oder Vektorausrichtung;
- veraenderten P0-, Quellen-, Plan- oder Autorisierungsbindungen;
- nicht endlichen oder nachtraeglich gerundeten Rohwerten;
- fehlender rollenweiser Konvergenz;
- nach Sichtung veraenderter Metrik, Faktor oder Rollenauswahl;
- einer Feldfunktions-, Memory- oder KI-Interpretation.

## Naechster Schritt

W7-AP darf ausschliesslich den rohen R1/R2- und R2/R4-
Distanzkompositor implementieren. Er materialisiert alle 70 Rollenvergleiche
und technischen Gegenkontrollen, setzt aber noch keine Konvergenz- oder
Effektentscheidung.
