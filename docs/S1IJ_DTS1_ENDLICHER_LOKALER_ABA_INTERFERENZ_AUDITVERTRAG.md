# S1-IJ: Endlicher lokaler DTS-1 A-B-A-Interferenz-Auditvertrag

## Status

S1-IJ bindet das endliche synthetische Fixture und den Ausfuehrungsvertrag
fuer S1-II. Es wird kein Harness implementiert und kein Ressourcen- oder
Feldschritt ausgefuehrt.

Entscheidung:

```text
DTS1_FINITE_LOCAL_ABA_INTERFERENCE_AUDIT_CONTRACT_BOUND
```

Vertragsdigest:

```text
b24d7ab337b201e24f14abb6bd6d8735b206b51f912da00481432569ce83cb9c
```

Quelle ist der S1-II-Vertragsdigest
`888c5bfcb525f44439f85f6e9b4664616013552c72ed86e8cd3bb141ddd8a60f`.

## Festes Fixture

Gebunden ist die offene Linie `node-a -- node-b -- node-c`. Kante A verbindet
a mit b, Kante B verbindet b mit c. Alle Knotenkapazitaeten betragen `1.0`.
Beide Kanten starten mit leitender Bindung `0.2` und refraktaerer Ressource
`0.1`. Daraus folgen freie Ressourcen `(0.85,0.7,0.85)`.

A-, B- und Pausenintervalle verwenden die Beteiligungen `(1,0)`, `(0,1)` und
`(0,0)`. Dauer ist jeweils `0.5`; die bereits synthetisch verwendeten Raten
sind `0.4/0.3/0.2`.

Der gemeinsame Feldreadout verwendet `S=(-1,0,1)`,
`H=(-0.2,0,0.2)`, Nullkontakt, Dauer `0.5`, Antwortzeit `1.0`, Nachhallzeit
`0.5` und Leckrate null. Die H-Kontrolle setzt `H=(0,0,0)`.

Alle Werte sind synthetische Fixturewerte und keine Materialparameter.

## Analytische Ressourcenprognose

Nach dem ersten gemeinsamen A-Kontakt ist die Anatomie in beiden Armen:

```text
(bA,uA,bB,uB) =
(0.4259185409758369, 0.11834214651858439,
 0.17214159528501158, 0.11834214651858439)
```

Im mittleren Intervall bindet B im Konkurrenzarm
`0.21122499977283485`, im Pausenarm exakt `0.0`. Vor der finalen A-Probe
lauten die freien Ressourcen am gemeinsamen Knoten:

```text
A-B-A      = 0.4882770296824491
A-Pause-A  = 0.5938895295688666
Defizit    = 0.10561249988641752
```

Die finale akzeptierte A-Bindung ist vorab gerichtet:

```text
A-B-A      = 0.1770192189197149
A-Pause-A  = 0.21530781555964015
Marge      = 0.03828859663992526
```

Die vollstaendigen Endanatomien bleiben gueltige innere Zustaende. Alle
Knotenzulassungsfaktoren der finalen A-Probe sind `1.0`; die Differenz folgt
damit direkt aus der kleineren gemeinsam verfuegbaren Ressource und nicht aus
Clipping.

## Analytische Feldprognose

Die Endadapterraten fuer `(A,B)` lauten:

```text
A-B-A      = (1.246273717300394, 1.1546643362246074)
A-Pause-A  = (1.2654180156203565, 1.0637628151621774)
```

Der gemeinsame Readout sagt fuer den orientierten A-Kantenkontrast voraus:

```text
C_A(A-B-A)     = 0.31965910192609714
C_A(A-Pause-A) = 0.30941727600747576
Marge          = 0.010241825918621383
```

Die vollstaendige S/H-Armtrennung ist fuer Haupt-H und H null jeweils
`0.012414072466544523`. Die feste Float64-Grenze lautet
`1.1368683772161603e-13`.

## Fallmatrix und Budget

Ein Audit umfasst in fester Reihenfolge:

1. C01: aktive Folgen `A-B-A` und `A-Pause-A` mit Haupt-H-Readout;
2. N01: zwei wertidentische vollstaendige `A-B-A`-Wiederholungen;
3. N02: B null gegen den passenden Pausenarm;
4. N03: zwei A0-Feldreadouts aus den aktiven Endanatomien;
5. N04: zwei Readouts aus derselben fixierten Startanatomie;
6. N05: aktive Endanatomien bei H null;
7. N06: beide Folgen mit Beteiligung null in der finalen A-Probe.

Das ergibt je Audit exakt 24 direkte Ressourcen- und zehn technische
Feldaufrufe. Eine identische Wiederholung begrenzt S1-IK auf hoechstens 48
direkte Ressourcenaufrufe, 20 technische Feldaufrufe und null
Forschungsfeldschritte.

## Gegenbaselines und STOPP

Alle fuenf S1-II-Gegenbaselinegruppen werden ausschliesslich als statische
Records gefuehrt. A0, fixierter Startadapter und H null sind technische
Kontrollen, keine angepassten Baselinemodelle. Interferenz allein grenzt
dynamisches zweistufiges E1 weiterhin nicht ab.

Jede Abweichung von Fixture, Reihenfolge, Aufrufbudget, analytischem Wert,
strikter Richtung, Kontrolle, Bilanz oder Feldbereich ergibt atomar STOPP.
Das gilt ebenso fuer Baselineausfuehrung oder -erweiterung, Nachwahl, Retry,
Teiloutput, Runtimekopplung oder Forschungsfeldnutzung.

## Aussagegrenze

S1-IJ registriert nur einen endlichen synthetischen Doppelaudit. Interferenz
wurde noch nicht ausgefuehrt oder nachgewiesen. Freigabe,
Wiederbeanspruchung, Materialeignung und weitergehende Claims bleiben offen.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1ij_interference_audit_contract.py
tests/test_dynamic_substrate_s1ij_interference_audit_contract.py
```

Neun Tests pruefen Quellenbindung, Fixture, unabhaengige Zweiarm-
Ressourcenrekurrenz, unabhaengigen symmetrischen Feldgenerator, Fallmatrix,
Aufrufbudgets, Kontrollen, Baselinegrenze, Ausfuehrungssperren und
Manipulationsschutz.

## Bester naechster Schritt

S1-IK darf genau das private Auditharness implementieren und den
vorregistrierten Doppelaudit einmal mit hoechstens 48 direkten Ressourcen- und
20 technischen Feldaufrufen vollziehen. STOPP beendet den Interferenzpfad;
PASS waere nur ein begrenzter synthetischer Interferenzbefund. Keine Runtime,
Baselineausfuehrung oder Forschungsprobe.
