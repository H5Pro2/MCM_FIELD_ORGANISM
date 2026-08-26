# S1-HX: DTS-1 Verfeinerungs- und Kausalitaetsauditvertrag

## Status

S1-HX registriert genau einen endlichen synthetischen Audit der in S1-HW
implementierten Kopplung vor. Es wird noch kein Auditharness implementiert
und kein Audit ausgefuehrt. Keine Materialparameter, Runtimeintegration oder
Forschungsprobe.

Entscheidung:

```text
DTS1_FINITE_SYNTHETIC_REFINEMENT_CAUSALITY_AUDIT_CONTRACT_BOUND
```

## Fester Umfang

Der spaetere Audit darf nur im privaten Modul

```text
mcm_field_organism.dynamic_substrate_dts1_refinement_causality_audit
```

liegen. Er verwendet genau die Partitionszahlen

```text
n=2, 2n=4, 4n=8
```

ueber dasselbe geschlossene physische Intervall von `0` bis `2` synthetischen
Zeiteinheiten. Die Basispartition folgt fuer das feste positive Ratenfixture
aus dem S1-HQ-Korridor. Nur die Anzahl gleichfoermiger Subschritte darf sich
zwischen den Stufen aendern.

## Festes synthetisches Fixture

Verbindlich sind:

```text
Geometrie:       bestehende offene Dreiknotenlinie mit zwei Kanten
S_0:             (-0.8, 0.1, 0.7)
H_0:             (0.2, -0.1, 0.3)
Kontakt:         (0.9, -0.2, 0.4), ueber das ganze Intervall konstant
Kapazitaeten:    (1.0, 1.0, 1.0)
Feldantwortzeit: 1.0
Nachhallzeit:    0.5
Leckrate:        0.0
DTS-1-Raten:     k_bind=0.4, k_turn=0.3, k_rec=0.2
aktive Kanten:   (b=0.2,u=0.1), (b=0.4,u=0.2)
Nullkanten:      (b=0,u=0), (b=0,u=0)
```

Diese Werte sind unveraenderliche synthetische Algebrafixtures. Sie sind
weder Schaetzungen noch Materialparameter und duerfen nach einem Ergebnis
nicht angepasst werden.

Alle Stufen beginnen aus wertidentischen Vorzustaenden, verwenden identische
Kontakte, Konfigurationen und Ereignisgrenzen und enden an derselben
physischen Grenze. Jeder Subschritt liest seinen eigenen abgeschlossenen
Vorzustand neu.

## Drei Szenarien

### C01: P0/A0-Exaktheitskontrolle

P0 und A0 laufen fuer `2`, `4` und `8` Subschritte. Ihre Feldsnapshots muessen
innerhalb jeder Stufe nach jedem korrespondierenden Subschritt bitgenau
identisch sein. DTS-1 darf in A0 fortschreiten, aber den Feldpfad nicht
veraendern.

### C02: Nullbindungs-Kausallatenz

A0 und A1 starten aus exakt null gebundener und null refraktaerer Ressource.
Im ersten Subschritt muessen Feldvorschlag und Ressourcenvorschlag zwischen A0
und A1 exakt gleich sein. Der Ressourcenvorschlag muss positive neue Bindung
enthalten. Diese darf das Feld erst in einem spaeteren Subschritt beeinflussen.

Bis zum gemeinsamen Intervallende muss die A1/A0-Feldtrennung oberhalb ihrer
Gleitkommaauflosung liegen. Die obere Leserlatzenz ist genau eine
Subschrittdauer und halbiert sich daher verbindlich:

```text
2 Schritte -> 1.0
4 Schritte -> 0.5
8 Schritte -> 0.25
```

### C03: Aktive vollstaendige Paarverfeinerung

A1 startet aus dem festen aktiven Ressourcenfixture. Verglichen wird nicht
nur das Feld, sondern das vollstaendige Feld-/Anatomiepaar am gemeinsamen
Intervallende.

## Kanonischer Paarrest

Der Vergleichsvektor enthaelt in kanonischer Reihenfolge:

1. alle `S`-Werte;
2. alle `H`-Werte;
3. fuer jede Kante `b_e/(2*min(q_i,q_j))`;
4. fuer jede Kante `u_e/(2*min(q_i,q_j))`.

Damit liegen Feld- und Ressourcenkomponenten in festen dimensionslosen
Bereichen. Fuer zwei Endpaare gilt die Maximumsnorm:

```text
D(X,Y) = max_k abs(X_k-Y_k)
R_n_2n = D(X_n,X_2n)
R_2n_4n = D(X_2n,X_4n)
```

Die Aufloesungsgrenze lautet vorregistriert:

```text
floor = 512 * float64_epsilon
        * max(1, norm_inf(X_n), norm_inf(X_2n), norm_inf(X_4n))
```

Fuer C03 muss `R_n_2n > floor` und strikt `R_2n_4n < R_n_2n` gelten. Aus nur
drei Stufen wird keine asymptotische Ordnung behauptet.

## PASS und STOPP

PASS setzt gemeinsam voraus:

- drei vollstaendige endliche Szenariorecords;
- gueltige Feldbereiche und Ressourcenbilanzen;
- alle exakten C01-Identitaeten;
- alle C02-Kausalidentitaeten, positive neue Bindung und spaetere Trennung;
- halbierende Leserlatzenz;
- einen nichttrivialen und strikt sinkenden C03-Paarrest;
- denselben kanonischen Receipt-Digest bei einer zweiten identischen
  Gesamtausfuehrung.

Jede einzelne Abweichung ergibt atomar STOPP. Teil-PASS, Fixtureaenderung,
Nachjustierung, alternativer Schwellenwert oder Retry-Tuning sind verboten.
Der gesamte deterministische Doppelaudit ist auf exakt hoechstens 140
technische Feldschrittaufrufe begrenzt.

## Ausgabe

Die spaetere Ausgabe enthaelt nur:

- eine atomare PASS- oder STOPP-Entscheidung;
- drei vollstaendige Szenariorecords;
- Partitionszahlen und Leserlatzenzen;
- beide aktiven Paarreste und die Aufloesungsgrenze;
- Exaktheits- und Ressourcenvaliditaetsflags;
- technische Schrittzahl und kanonischen SHA-256-Receipt.

## Aussagegrenze

Ein spaeterer PASS waere nur ein technischer Befund zu dieser diskreten
Kopplung und diesem festen synthetischen Fixture. Er waere kein
Materialparameter-, Funktions- oder Baselinebefund. Abschwaechung,
Interferenz, Kapazitaetsfreigabe, Wiederbeanspruchung und jede weitergehende
Projektfaehigkeit blieben offen.

## Bester naechster Schritt

S1-HY darf nach dem naechsten `ok weiter` genau das private Auditharness
implementieren und den einmaligen deterministischen Doppelaudit innerhalb von
140 technischen Feldschritten ausfuehren. Bei STOPP endet die gekoppelte
Weiterarbeit; bei PASS folgt erst ein neuer Vertrag. Keine Materialparameter,
Runtimeintegration oder Forschungsprobe.
