# S1-IM: Endlicher DTS-1 Freigabe- und Wiederverwendungs-Auditvertrag

## Status

S1-IM bindet das endliche synthetische Fixture und den Ausfuehrungsvertrag
fuer S1-IL. Es wird kein Harness implementiert und kein Ressourcen- oder
Feldschritt ausgefuehrt.

Entscheidung:

```text
DTS1_FINITE_LOCAL_CAPACITY_RELEASE_REUSE_AUDIT_CONTRACT_BOUND
```

Vertragsdigest:

```text
f553533b70088766b41c79b95dee070668a4f5a827c1cb67b773c98f56fd68c2
```

Quelle ist der S1-IL-Vertragsdigest
`05582932f13789dab3ff612ea2035ffbfb3180154203ee1574e67b6a86e2c550`.

## Festes Fixture

Gebunden ist die offene Linie `node-a -- node-b -- node-c` mit A zwischen a
und b sowie B zwischen b und c. Alle Knotenkapazitaeten betragen `1.0`.
Beide Kanten starten mit leitender Bindung `0.2` und refraktaerer Ressource
`0.1`.

A-Last, kontaktfreies Fenster und B-Probe verwenden die Beteiligungen
`(1,0)`, `(0,0)` und `(0,1)`. Dauer ist jeweils `0.5`; die synthetischen
Recovery-on-Raten sind `0.4/0.3/0.2`. Recovery-off aendert ausschliesslich
die Recoveryrate auf `0.0`.

Der gemeinsame Feldreadout verwendet `S=(-1,0,1)`,
`H=(-0.2,0,0.2)`, Nullkontakt, Dauer `0.5`, Antwortzeit `1.0`, Nachhallzeit
`0.5` und Leckrate null. Die H-Kontrolle setzt `H=(0,0,0)`.

Alle Werte sind synthetische Fixturewerte und keine Materialparameter.

## Analytische Ressourcenprognose

Nach der gemeinsamen A-Last ist die Anatomie:

```text
(bA,uA,bB,uB) =
(0.4259185409758369, 0.11834214651858439,
 0.17214159528501158, 0.11834214651858439)
```

Im kontaktfreien Fenster betraegt Recovery auf jeder Kante im aktiven Arm
`0.011261744217875269`, im abgetragenen Arm exakt `0.0`. Die leitenden
Bindungen bleiben danach bitgenau armgleich. Direkt vor der B-Probe gilt:

```text
gemeinsame freie Ressource Recovery-on  = 0.5938895295688665
gemeinsame freie Ressource Recovery-off = 0.5826277853509914
Freigabemarge                           = 0.01126174421787518
```

Die identische nichtsaturierende B-Probe sagt voraus:

```text
B-Bindung Recovery-on  = 0.2153078155596401
B-Bindung Recovery-off = 0.21122499977283485
Wiederbindungsmarge    = 0.0040828157868052495
```

Alle Knotenzulassungen bleiben `1.0`; weder Clipping noch Saettigung erzeugt
die Richtung.

## Analytische Feldprognose

Die Postprobe-Adapterraten fuer `(A,B)` lauten:

```text
Recovery-on  = (1.1577641078405365, 1.1714167229419974)
Recovery-off = (1.1577641078405365, 1.1693753150485948)
```

Der gemeinsame Readout sagt fuer den B-Kantenkontrast voraus:

```text
C_B(Recovery-on)  = 0.3367717320392176
C_B(Recovery-off) = 0.33724837238920485
Marge off - on    = 0.00047664034998723404
```

Die vollstaendige S/H-Armtrennung ist fuer Haupt-H und H null jeweils
`0.000273420770841859`. Die feste Float64-Grenze lautet
`1.1368683772161603e-13`. Der Feldreadout bleibt sekundaer; direkte Recovery
und zusaetzliche B-Bindung sind die primaeren getrennten Messungen.

## Fallmatrix und Budget

Ein Audit umfasst in fester Reihenfolge:

1. C01: Recovery-on gegen Recovery-off mit B-Probe und Haupt-H-Readout;
2. N01: zwei wertidentische vollstaendige Recovery-on-Wiederholungen;
3. N02: Recoveryrate null gegen explizit abgetragenen Recoverykanal;
4. N03: Recovery bei null refraktaerer und null Turnoverquelle;
5. N04: B-Beteiligung null aus beiden aktiven Vorprobe-Anatomien;
6. N05: zwei A0-Feldreadouts aus den aktiven Endanatomien;
7. N06: zwei Readouts mit demselben vor Freigabe fixierten Adapter;
8. N07: aktive Endanatomien bei H null.

Das ergibt je Audit exakt 18 direkte Ressourcen- und zehn technische
Feldaufrufe. Eine identische Wiederholung begrenzt S1-IN auf hoechstens 36
direkte Ressourcenaufrufe, 20 technische Feldaufrufe und null
Forschungsfeldschritte.

## Gegenbaselines und STOPP

Alle fuenf S1-IL-Gegenbaselinegruppen werden ausschliesslich als statische
Records gefuehrt. Recovery, gemeinsame Freimenge und zusaetzliche B-Bindung
muessen getrennt bestehen. Freigabe und Wiederverwendung allein grenzen
dynamisches zweistufiges E1 weiterhin nicht ab.

Jede Abweichung von Fixture, Reihenfolge, Aufrufbudget, analytischem Wert,
strikter Richtung, Kontrolle, Bilanz oder Feldbereich ergibt atomar STOPP.
Das gilt ebenso fuer Baselineausfuehrung, Nachwahl, Retry, Teiloutput,
Runtimekopplung oder Forschungsfeldnutzung.

## Aussagegrenze

S1-IM registriert nur einen endlichen synthetischen Doppelaudit. Freigabe und
Wiederverwendung wurden noch nicht ausgefuehrt oder nachgewiesen.
Materialeignung, E1-Nichtreduzierbarkeit und weitergehende Claims bleiben
offen. Es entsteht kein Memory- oder KI-Claim.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1im_release_reuse_audit_contract.py
tests/test_dynamic_substrate_s1im_release_reuse_audit_contract.py
```

Zehn Tests pruefen Quellenbindung, Fixture, unabhaengige Zweiarmrekurrenz,
analytische Margen, unabhaengigen symmetrischen Feldgenerator, Fallmatrix,
Budgets, Gegenbaselinegrenze, Ausfuehrungssperren und Manipulationsschutz.

## Bester naechster Schritt

S1-IN darf genau das private Auditharness implementieren und den
vorregistrierten Doppelaudit einmal mit hoechstens 36 direkten Ressourcen-
und 20 technischen Feldaufrufen vollziehen. STOPP beendet den
Freigabe-/Wiederverwendungspfad; PASS waere nur ein begrenzter synthetischer
Befund. Keine Runtime, Baselineausfuehrung oder Forschungsprobe.
