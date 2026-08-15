# S1-IE: Kausaler DTS-1 Zweischritt-Feldreadoutbefund

## Status

S1-IE implementiert das private Auditharness und vollzieht den in S1-ID
vorregistrierten Doppelaudit genau einmal. Beide 20-Aufruf-Durchgaenge liefern
denselben Receipt. Insgesamt wurden exakt `40` technische Feldaufrufe und `0`
Forschungsfeldschritte ausgefuehrt.

Entscheidung:

```text
PASS_DTS1_TWO_SUBSTEP_CAUSAL_FIELD_READOUT
```

## C01: Kausaler Zweischritt-Readout

Beide Arme starteten mit identischem S/H-Feld, identischer leitender Bindung,
Geometrie, Gesamtressource, Kontakt, Zeit und Konfiguration. Nur die
Frei/Refraktaer-Aufteilung unterschied sich.

Im ersten Subschritt blieben Adapter und vollstaendiger S/H-Feldvorschlag
bitgenau armgleich. Gleichzeitig entstanden die vorregistrierten
unterschiedlichen neuen Bindungen:

```text
b1(F_HIGH) = 0.5980601362608484
b1(R_HIGH) = 0.48929858810763766
Adapter 1  = 1.2 in beiden Armen
Kontrast 1 = 0.36536704810546916 in beiden Armen
```

Erst der zweite Subschritt las diese unterschiedliche vorbestehende Bindung:

```text
Adapter 2 F_HIGH       = 1.299030068130424
Adapter 2 R_HIGH       = 1.2446492940538187
Kontrast 2 F_HIGH      = 0.06045337407166918
Kontrast 2 R_HIGH      = 0.06383190638930976
gerichtete Kontrastmarge = 0.003378532317640577
vollstaendige S/H-Trennung = 0.0016892661588202885
Rundungsgrenze            = 1.1368683772161603e-13
```

Damit gilt die vorregistrierte Richtung `C_F_HIGH<C_R_HIGH`; die
vollstaendige S/H-Trennung liegt klar ueber der gebundenen Grenze. Alle acht
Exaktheits- und Richtungspruefungen sowie alle Ressourcenbilanzen bestehen.

## Kontrollen

- N01: Das wertidentische F_HIGH-Paar ist vollstaendig bitgenau gleich.
- N02: A0 liefert in beiden Subschritten identische Felder und durchgehend den
  Basisadapter.
- N03: Der fixierte b0-Adapter liefert in beiden Armen identische erste und
  zweite Felder. Der groesste Bilanzrest von `2.220446049250313e-16` bleibt
  unter der vorregistrierten Rundungsgrenze.
- N04: Bei `H0=0` bleiben die ersten Felder gleich; die gerichtete Trennung im
  zweiten Subschritt folgt weiterhin dem unterschiedlichen vorbestehenden
  Adapter und liegt oberhalb der Grenze.

## Gegenbaselines

Fixed Adapter/Frozen-E1, Leaky/Integrator, zweistufiges E1, F3/CONST-V und
schneller Nachhall wurden ausschliesslich als vorregistrierte
Zustandsraumrecords gefuehrt. Kein Baselinemodell wurde ausgefuehrt. Die
Frozen-b0-Kontrolle zeigt innerhalb des Fixtures, dass ein armgleich fixierter
Adapter die beobachtete Zweitschritttrennung nicht erzeugt.

## Reproduzierbarkeit

```text
erster Receipt  = 91bec1f34f13da4458c335e8124065d8d6e882cde7f03ade41b01378c4ee9db5
zweiter Receipt = 91bec1f34f13da4458c335e8124065d8d6e882cde7f03ade41b01378c4ee9db5
Audit-Receipt   = dbaa141450f1a00defb71824feb4e61bbef727c0023ea1d1e19cc979581ebcea
```

Die Strukturtests rufen den offiziellen Audit-Einstieg nicht erneut auf.

## Aussagegrenze

PASS bestaetigt fuer das feste synthetische Fixture genau eine technische
Kausalkette: Die Frei/Refraktaer-Intervention aendert die neu gebundene
Ressource, und diese Aenderung beeinflusst ueber den vorbestehenden Adapter
erst den folgenden Feldvorschlag.

Nicht nachgewiesen sind Abschwaechung bei Wiederholung, Interferenz,
Kapazitaetsfreigabe, Wiederbeanspruchung, Materialeignung oder eine
weitergehende Projektfaehigkeit. Es entsteht kein Memory- oder KI-Claim.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_dts1_causal_field_readout_audit.py
tests/test_dynamic_substrate_dts1_causal_field_readout_audit.py
```

## Bester naechster Schritt

S1-IF darf ausschliesslich einen statischen Vertrag fuer die kleinste
Abschwaechungspruefung unter wiederholtem identischem lokalen Kontakt binden.
Vor jeder Gleichung, Wertwahl oder Ausfuehrung muessen direkte Messgroesse,
Kontaktfolge, gerichtete DTS-1-Prognose, A0-, Fixed-Adapter-/Frozen-b0-,
Leaky/Integrator- und H-abgeglichene Kontrollen sowie atomare
Verwerfungsbedingungen feststehen. Noch keine Implementierung, Runtime oder
Ausfuehrung.
