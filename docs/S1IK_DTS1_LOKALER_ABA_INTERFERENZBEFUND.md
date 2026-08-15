# S1-IK: Lokaler DTS-1 A-B-A-Interferenzbefund

## Status

S1-IK implementiert das private Auditharness und vollzieht den in S1-IJ
vorregistrierten Doppelaudit genau einmal. Beide Durchgaenge liefern denselben
Receipt. Insgesamt wurden exakt `48` direkte Ressourcenaufrufe, `20`
technische Feldaufrufe und `0` Forschungsfeldschritte ausgefuehrt.

Entscheidung: `PASS_DTS1_LOCAL_ABA_INTERFERENCE`.

## Direkter Ressourcenbefund

Im mittleren Intervall bindet B im Konkurrenzarm
`0.21122499977283485`, im Pausenarm exakt `0.0`. Vor der finalen A-Probe
lautet die gemeinsam freie Ressource:

```text
A-B-A      = 0.4882770296824491
A-Pause-A  = 0.5938895295688665
Defizit    = 0.10561249988641741
```

Die finale akzeptierte A-Bindung ist entsprechend kleiner:

```text
A-B-A      = 0.1770192189197149
A-Pause-A  = 0.2153078155596401
Marge      = 0.038288596639925204
```

Damit ist fuer dieses feste synthetische Fixture eine lokale Konkurrenz um
das gemeinsame Endpunktbudget direkt im Ressourcenledger sichtbar.

## Gemeinsamer Feldreadout

Die getrennten Readouts aus den uebernommenen Endanatomien ergeben:

```text
C_A(A-B-A)     = 0.31965910192609714
C_A(A-Pause-A) = 0.30941727600747576
Marge          = 0.010241825918621383
```

Die maximale vollstaendige S/H-Armtrennung betraegt mit Haupt-H und H null
jeweils `0.012414072466544523`. Beide Werte liegen klar ueber der festen
Float64-Grenze `1.1368683772161603e-13`. Kein Feldreadout-Poststate wurde in
die Ressourcenfolge zurueckgeschrieben.

## Kontrollen

- N01: Zwei wertidentische A-B-A-Folgen und Readouts sind bitgenau.
- N02: B mit Beteiligung null ist bitgenau der passenden Pause gleich.
- N03: A0 macht die Feldausgaben beider Endanatomien bitgenau gleich und
  liefert nur den Basisadapter `1.0`.
- N04: Zwei Readouts aus derselben fixierten Startanatomie sind bitgenau.
- N05: Bei H null bleibt die vorregistrierte vollstaendige Trennung erhalten.
- N06: Beteiligung null in der finalen A-Probe liefert exakt null A-Bindung.

Alle lokalen und globalen Bilanzreste bleiben unter der festen
Float64-Grenze. Alle vorregistrierten Richtungen und Werte bestehen.

## Gegenbaselines

Fixed Adapter/Frozen-E1, Leaky/Integrator, F3/CONST-V und schneller Nachhall
wurden nur als statische Gegenprognoserecords gefuehrt. Kein Baselinemodell
wurde ausgefuehrt oder angepasst. Fuer dynamisches zweistufiges E1 lautet der
Record `INTERFERENCE_ALONE_NOT_DISTINCT_NO_EXECUTION`. Der beobachtete
Interferenzbefund allein grenzt DTS-1 daher nicht von E1 ab.

## Reproduzierbarkeit

```text
erster Receipt  = aa8a25da985cdd5af4b2d0725467a1b58f98559b75c1ee5dd985654314c29cbc
zweiter Receipt = aa8a25da985cdd5af4b2d0725467a1b58f98559b75c1ee5dd985654314c29cbc
Audit-Receipt   = 7d0a5bffd19cc7f212392b1d4a9c4d8ea8c79ffb1414d6a9fbc9a936ff9dedfe
```

Die Strukturtests rufen den offiziellen Audit-Einstieg nicht auf.

## Aussagegrenze

PASS bestaetigt nur fuer das feste synthetische Fixture positive lokale
B-Bindung, ein gemeinsames Freidefizit, verringerte folgende A-Bindung und
einen gerichteten gemeinsamen Feldreadout. Er bestaetigt keine
Kapazitaetsfreigabe, konkurrierende Wiederverwendung, Materialeignung,
E1-Nichtreduzierbarkeit oder weitergehende Projektfaehigkeit. Es entsteht
kein Memory- oder KI-Claim.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_dts1_interference_audit.py
tests/test_dynamic_substrate_dts1_interference_audit.py
```

## Bester naechster Schritt

S1-IL darf ausschliesslich einen statischen Funktions- und
Falsifikationsvertrag fuer Kapazitaetsfreigabe und konkurrierende
Wiederverwendung derselben lokalen Ressource binden. Vor jeder Gleichung,
Fixturewahl oder Ausfuehrung muessen Belastungs-, Erholungs- und
Keine-Erholungsarme, direkte Freigabe- und Wiederbindungsledger,
Zeitangleichung, Gegenbaselines, Nullkontrollen und atomare
Verwerfungsbedingungen feststehen. Noch keine Werte, Gleichung, neuen
Parameter, Implementierung, Runtime oder Ausfuehrung.
