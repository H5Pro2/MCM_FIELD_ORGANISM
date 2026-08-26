# S1-IG: Endlicher DTS-1 Abschwaechungs-Auditvertrag

## Status

S1-IG bindet das endliche synthetische Fixture und den Ausfuehrungsvertrag
fuer S1-IF. Es wird kein Harness implementiert und kein Ressourcen- oder
Feldschritt ausgefuehrt.

Entscheidung:

```text
DTS1_FINITE_REPEATED_CONTACT_ATTENUATION_AUDIT_CONTRACT_BOUND
```

Vertragsdigest:

```text
f807ed35def035d4390602555520fe3df1b19f4066e572a993c18f7aac9af9cd
```

Quelle ist der S1-IF-Vertragsdigest
`bfad62c3da8abf8a7cf6777adb401b33b35135360bd566093631de124cd47f56`.

## Festes Fixture

Gebunden ist eine isolierte offene Zweiknotenkante mit Kapazitaeten `1.0`,
leitender Startbindung `0.4`, refraktaerer Startressource `0.2` und daraus
abgeleiteter freier Ressource `0.7` je Knoten. Drei unmittelbar folgende
Kontakte verwenden jeweils Beteiligung `1.0`, Dauer `0.5` und die bereits
synthetisch verwendeten Raten `0.4/0.3/0.2`.

Die drei getrennten Readouts lesen jeweils denselben Pruefzustand
`S=(-1,1)`, `H=(-0.2,0.2)`, Nullkontakt und Dauer `0.5`. Antwortzeit ist
`1.0`, Nachhallzeit `0.5`, Leckrate null. Die H-Kontrolle setzt denselben
S-Zustand mit `H=(0,0)` ein. Kein Readout-Poststate gelangt in die
Kontaktfolge.

Alle Werte sind synthetische technische Fixturewerte und keine Material- oder
Zeitschaetzung.

## Analytische Ressourcenprognose

Die drei Vorzustandsbindungen lauten:

```text
b = (0.4, 0.5980601362608484, 0.725980129434404)
```

Die direkte akzeptierte Bindung muss strikt sinken:

```text
engagement = (0.2537769456908254,
              0.21122499977283485,
              0.17701921891971492)
```

Die kleinere der beiden aufeinanderfolgenden Differenzen ist
`0.034205780853119926`. Nach Kontakt 3 bleiben `b=0.8018761070500025`,
refraktaer `0.37028143786492795` und frei
`0.4139212275425348` je Knoten. Alle Zustaende liegen im gueltigen Inneren.

## Analytische Feldprognose

Die Readoutadapter steigen vorab gerichtet:

```text
rate = (1.2, 1.299030068130424, 1.362990064717202)
```

Die orientierten S-Kontraste muessen zugleich strikt sinken:

```text
C = (0.3653670481054693,
     0.33091858932072243,
     0.3104157086599864)
```

Die aufeinanderfolgenden Kontrastabnahmen sind
`0.034448458784746894` und `0.020502880660736023`. Die H-Nullkontrolle muss
dieselbe S-Kontrastfolge liefern. Die feste Float64-Grenze ist
`1.1368683772161603e-13`.

## Fallmatrix und Budget

Ein Audit umfasst in fester Reihenfolge:

1. C01: aktive Drei-Kontakt-Folge mit drei gemeinsamen Readouts;
2. N01: wertidentische Ressourcen- und Feldwiederholung;
3. N02: drei A0-Readouts;
4. N03: drei Readouts mit derselben Startanatomie als fixiertem Adapter;
5. N04: drei aktive Readouts bei H null;
6. N05: drei Ressourcenfolgeschritte bei Beteiligung null.

Das ergibt je Audit exakt acht direkte Ressourcenaufrufe und 14 technische
Feldaufrufe. Eine identische Wiederholung begrenzt S1-IH auf hoechstens 16
direkte Ressourcenaufrufe, 28 technische Feldaufrufe und null
Forschungsfeldschritte.

## Gegenbaselines und STOPP

Alle fuenf S1-IF-Gegenbaselinegruppen werden nur als statische Records
gefuehrt. A0, fixierter Startadapter und H null sind technische Kontrollen,
keine angepassten Baselinemodelle. Abschwaechung allein grenzt dynamisches
zweistufiges E1 weiterhin nicht ab.

Jede Abweichung von Fixture, Reihenfolge, Callbudget, analytischem Wert,
strikter Richtung, Kontrolle, Bilanz oder Feldbereich ergibt atomar STOPP.
Das gilt ebenso fuer Baselineausfuehrung oder -erweiterung, Nachwahl, Retry,
Teiloutput, Runtimekopplung oder Forschungsfeldnutzung.

## Aussagegrenze

S1-IG registriert nur einen endlichen synthetischen Doppelaudit. Eine
Abschwaechung wurde noch nicht ausgefuehrt oder nachgewiesen. Interferenz,
Freigabe, Wiederbeanspruchung, Materialeignung und weitergehende Claims
bleiben offen.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1ig_attenuation_audit_contract.py
tests/test_dynamic_substrate_s1ig_attenuation_audit_contract.py
```

Neun Tests pruefen Quellenbindung, Fixture, unabhaengige Ressourcen- und
Feldanalytik, Fallmatrix, Aufrufbudgets, Kontrollen, Baselinegrenze,
Ausfuehrungssperren und Manipulationsschutz.

## Bester naechster Schritt

S1-IH darf genau das private Auditharness implementieren und den
vorregistrierten Doppelaudit einmal mit hoechstens 16 direkten Ressourcen- und
28 technischen Feldaufrufen vollziehen. STOPP beendet den
Abschwaechungspfad; PASS waere nur ein begrenzter synthetischer
Abschwaechungsbefund. Keine Runtime, Baselineausfuehrung oder Forschungsprobe.
