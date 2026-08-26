# S1-IH: DTS-1 Abschwaechungsbefund bei wiederholtem Kontakt

## Status

S1-IH implementiert das private Auditharness und vollzieht den in S1-IG
vorregistrierten Doppelaudit genau einmal. Beide Durchgaenge liefern denselben
Receipt. Insgesamt wurden exakt `16` direkte Ressourcenaufrufe, `28`
technische Feldaufrufe und `0` Forschungsfeldschritte ausgefuehrt.

Entscheidung:

```text
PASS_DTS1_REPEATED_EQUAL_CONTACT_ATTENUATION
```

## Direkte Ressourcenfolge

Die drei identischen Kontakte erzeugen die vorregistrierte strikt sinkende
akzeptierte Bindung:

```text
Kontakt 1 = 0.2537769456908254
Kontakt 2 = 0.21122499977283485
Kontakt 3 = 0.17701921891971492

Abnahme 1 -> 2 = 0.042551945917990525
Abnahme 2 -> 3 = 0.03420578085311993
```

Die vorbestehende leitende Bindung steigt dabei kontrolliert von `0.4` ueber
`0.5980601362608484` auf `0.725980129434404`. Nach Kontakt 3 betraegt sie
`0.8018761070500025`; refraktaere Ressource ist
`0.37028143786492795`, freie Ressource `0.4139212275425348` je Knoten.
Alle lokalen und globalen Bilanzreste sind exakt null.

## Gemeinsamer Feldreadout

Die getrennten wertidentischen S/H-Pruefvorzustaende lesen ausschliesslich die
jeweilige Voranatomie. Ihre Adapterraten und orientierten S-Kontraste lauten:

```text
Adapter = (1.2, 1.299030068130424, 1.362990064717202)
Kontrast = (0.36536704810546916,
            0.3309185893207224,
            0.3104157086599863)

Abnahme 1 -> 2 = 0.03444845878474678
Abnahme 2 -> 3 = 0.020502880660736078
```

Beide direkten Bindungsabnahmen und beide Feldkontrastabnahmen liegen klar
ueber der festen Float64-Grenze `1.1368683772161603e-13`. Kein
Readout-Poststate wurde in die Kontaktfolge zurueckgeschrieben.

## Kontrollen

- N01: Wertidentische Ressourcen- und Feldvorschlaege sind vollstaendig
  bitgenau.
- N02: A0 liefert an allen drei Checkpoints denselben neutralen Adapter `1.0`
  und denselben Kontrast `0.4462603202968595`.
- N03: Die fixierte Startanatomie liefert dreimal Adapter `1.2` und Kontrast
  `0.36536704810546916`; sie erzeugt keine Abschwaechungsfolge.
- N04: Bei `H=(0,0)` bleibt die aktive S-Kontrastfolge innerhalb der festen
  Grenze identisch und strikt gerichtet.
- N05: Beteiligung null liefert an allen drei Kontakten exakt null Engagement.

Alle Kontrollanatomien und Feldbereiche sind gueltig. Saemtliche
Ressourcenbilanzreste sind null.

## Gegenbaselines

Fixed Adapter/Frozen-E1, Leaky/Integrator, F3/CONST-V und schneller Nachhall
wurden nur als statische Gegenprognoserecords gefuehrt. Kein Baselinemodell
wurde ausgefuehrt oder je Checkpoint angepasst.

Fuer dynamisches zweistufiges E1 lautet der Record ausdruecklich
`ATTENUATION_ALONE_NOT_DISTINCT_NO_EXECUTION`. Die beobachtete Abschwaechung
allein ist daher kein Abgrenzungsbefund gegen E1. Der bestandene S1-IB-Eingriff
frei gegen refraktaer und der S1-IE-Feldreadout bleiben gemeinsam erforderlich.

## Reproduzierbarkeit

```text
erster Receipt  = 045b8f1d165cb9f4a69d5e38c55bca298a51290611fb25d7912e82ea481f7b54
zweiter Receipt = 045b8f1d165cb9f4a69d5e38c55bca298a51290611fb25d7912e82ea481f7b54
Audit-Receipt   = 2fd24fd7ccdee690ea5610440e2d76f85e6a5ca0b8bc4b9045ff7c12a34d0c36
```

Die Strukturtests rufen den offiziellen Audit-Einstieg nicht auf.

## Aussagegrenze

PASS bestaetigt fuer das feste synthetische Fixture eine gemeinsame direkte
Ressourcen- und Feldreadoutabschwaechung unter drei identischen lokalen
Kontakten. Er bestaetigt keine Interferenz, Kapazitaetsfreigabe,
Wiederbeanspruchung, Materialeignung, E1-Nichtreduzierbarkeit oder
weitergehende Projektfaehigkeit. Es entsteht kein Memory- oder KI-Claim.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_dts1_attenuation_audit.py
tests/test_dynamic_substrate_dts1_attenuation_audit.py
```

## Bester naechster Schritt

S1-II darf ausschliesslich einen statischen Interferenzvertrag fuer eine
kleine lokale `A-B-A`-Folge gegen eine belastungsabgeglichene
`A-Pause-A`-Kontrolle binden. A und B muessen benachbarte Kanten mit genau
einem gemeinsamen endlichen Endpunktbudget sein. Vor jeder Gleichung,
Fixturewahl oder Ausfuehrung muessen direkte Ledger-Messgroesse,
Folgecheckpoint, Gegenrichtung, H-Angleichung, A0, fixierter Adapter,
Leaky/Integrator und zweistufiges E1 sowie atomare Verwerfungsregeln
feststehen. Noch keine Werte, Implementierung, Runtime oder Ausfuehrung.
