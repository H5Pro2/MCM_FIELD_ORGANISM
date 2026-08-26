# S1-IB: Direkter DTS-1 Frei/Refraktaer-Interventionsbefund

## Status

S1-IB implementiert das private, feldfreie Auditharness und vollzieht den in
S1-IA vorregistrierten Doppelaudit genau einmal. Beide Acht-Aufruf-Durchgaenge
liefern denselben Receipt. Insgesamt wurden exakt `16` reine
Ressourcenschrittaufrufe und `0` Feldschritte ausgefuehrt.

Entscheidung:

```text
PASS_DTS1_DIRECT_FREE_REFRACTORY_ENGAGEMENT
```

## Direkte Intervention C01

Beide Arme hielten Kapazitaeten, Kante, leitende Bindung, Referenz-S/H,
Beteiligung, Schritt und Raten wie vorregistriert identisch. Nur die
Frei/Refraktaer-Aufteilung unterschied sich.

```text
F_HIGH engagement = 0.2537769456908254
R_HIGH engagement = 0.14501539753761447
Differenz         = 0.1087615481532109
Rundungsgrenze    = 1.1368683772161603e-13
```

Damit sind beide analytischen Vorhersagen innerhalb der gebundenen Grenze,
die Differenz liegt klar oberhalb der Grenze und
`engagement(F_HIGH)>engagement(R_HIGH)` gilt strikt.

Die Eingangs- und Ausgangsdigests lauten:

```text
F_HIGH input  = abec53cbdc0b43bc4fd1e786e762cf582814ee0dbb933b6373911c9ce239285f
F_HIGH output = a3a6950212cc22555a2077b783b5a73a31ff34d8224bc5f63790f33f8359dcc6
R_HIGH input  = 3a5ea1c416e7a29aa917eaf5e750aeaf15b89d8b1dec364fe8276c5ed4e83b45
R_HIGH output = 65b82f63a36eba9001c6010b971144392a39a5277ba9eb11370d1fb7652222b7
```

Die vollstaendigen Transfertripel `(engagement,turnover,recovery)` sind:

```text
F_HIGH = (0.2537769456908254, 0.05571680942997688, 0.019032516392808087)
R_HIGH = (0.14501539753761447, 0.05571680942997688, 0.07613006557123235)
```

Lokale und globale Bilanzreste sind in beiden Armen exakt `0.0`; globale
Kapazitaet und bilanzierte Ressource bleiben jeweils `2.0`.

## Nullkontrollen

- N01: Zwei wertidentische F_HIGH-Ergebnisse sind einschliesslich Digests
  bitgenau gleich.
- N02: Bei Beteiligung null ist Engagement in beiden Armen exakt `0.0`.
- N03: Bei Bindungsrate null ist Engagement in beiden Armen exakt `0.0`.

Auch in allen Nullkontrollen sind die lokalen und globalen Bilanzreste exakt
null. Jeder Fall verwendete genau zwei reine S1-HP-Aufrufe.

## Gegenbaselines

Fixed Adapter/Frozen-E1, Leaky/Integrator, zweistufiges E1, F3/CONST-V und
schneller Nachhall wurden wie vorregistriert nur als unveraenderte
Zustandsraumrecords gefuehrt. Kein Baselinemodell wurde ausgefuehrt und keine
Baseline erhielt Arm-ID oder Frei/Refraktaer-Koordinate.

Der Befund ist deshalb direkt: Bei identischer leitender Bindung und
identischer Gesamtressource aendert die zusaetzliche refraktaere
Zustandskoordinate die naechste akzeptierte Bindungsmenge. Das zweistufige E1
besitzt dieses Zustandspaar in seiner gebundenen Form nicht. Daraus folgt noch
keine Aussage ueber eine Feldantwort oder die Leistung einer Baseline.

## Reproduzierbarkeit

```text
erster Receipt  = ff02ede38e6c125f4a7dc44014f688758309df0a081cecb1ebd4252e2ee813ed
zweiter Receipt = ff02ede38e6c125f4a7dc44014f688758309df0a081cecb1ebd4252e2ee813ed
Audit-Receipt   = 55159311a95b555900632014d68b3534aeb958787e0e6bcfba4d3e32dfedb217
```

Die acht neuen Strukturtests rufen den Audit-Einstieg nicht auf. Der gesamte
dynamische Substratpfad bestand vor der einmaligen Ausfuehrung mit `188`
Tests.

## Aussagegrenze

PASS bestaetigt genau eine technische Vorhersage des festen synthetischen
Fixtures: Die direkt aus dem lokalen Ledger abgeleitete freie Ressource
begrenzt die naechste akzeptierte Bindung anders als refraktaere Ressource.

Nicht nachgewiesen sind eine Feldwirkung dieses Interventionspaars,
Abschwaechung, Interferenz, Kapazitaetsfreigabe, Wiederbeanspruchung,
Materialeignung oder eine weitergehende Projektfaehigkeit. Es entsteht kein
Memory- oder KI-Claim.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_dts1_free_refractory_audit.py
tests/test_dynamic_substrate_dts1_free_refractory_audit.py
```

## Bester naechster Schritt

S1-IC darf ausschliesslich einen statischen Vertrag fuer den kleinsten
gekoppelten kausalen Feldreadout dieses bestandenen Interventionspaars binden.
Er muss vor jeder Ausfuehrung festlegen, wie der erste Subschritt bei
identischem `S`, `H` und `b` feldseitig exakt gleich bleibt, wie die
unterschiedliche neue Bindung erst im folgenden Subschritt eine gerichtete
Feldtrennung erzeugen darf, welche Fixed-Adapter-, A0-, zweistufige E1- und
Nachhallkontrollen gelten und wann atomar STOPP eintritt. Noch keine Werte,
Implementierung, Runtime oder Ausfuehrung.
