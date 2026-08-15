# S1-IC: Statischer kausaler DTS-1 Zweischritt-Feldreadoutvertrag

## Status

S1-IC bindet den kleinsten gekoppelten Kausalreadout des in S1-IB bestandenen
Frei/Refraktaer-Interventionspaars. Es werden noch keine Fixturewerte
ausgewaehlt, keine Gleichung geaendert, kein Harness implementiert und kein
Feldschritt ausgefuehrt.

Entscheidung:

```text
DTS1_TWO_SUBSTEP_CAUSAL_FIELD_READOUT_CONTRACT_BOUND
```

Vertragsdigest:

```text
98a376eee3bb141d4a058202cd8759bd34324b80ecaa19a333491148a18ca5e9
```

Quelle ist der bestandene S1-IB-Audit-Receipt
`55159311a95b555900632014d68b3534aeb958787e0e6bcfba4d3e32dfedb217`.

## Geschlossenes Interventionspaar

F_HIGH und R_HIGH starten aus wertidentischen vollstaendigen Feldzustaenden
`S0/H0`. Identisch bleiben Geometrie, Kapazitaeten, Gesamtressource, leitende
Bindung `b0`, Kontakt, Ereignisgrenzen, Feldkonfigurationen, Schrittzeiten und
DTS-1-Raten. Nur die gueltige ledgerabgeleitete Aufteilung frei/refraktaer
darf sich unterscheiden.

Jeder Subschritt liest genau ein abgeschlossenes Feld-/Anatomiepaar. Feld- und
Ressourcenvorschlag werden erst nach vollstaendiger Validierung atomar
uebernommen. Armname, Ergebniswert und Poststate duerfen keinen Vorschlag
steuern.

## Kausalkette

### Subschritt 1

- `S0` ist identisch, daher ist die Kantenbeteiligung identisch.
- `b0` ist identisch, daher ist der angewandte Adapter bitgenau identisch.
- Der vollstaendige Feldvorschlag `S1/H1` muss bitgenau identisch sein.
- Nach S1-IB ist die akzeptierte Bindung in F_HIGH strikt groesser.
- Bei gleichem vorbestehendem `b0` und gleichem Umsatz folgt deshalb
  `b1(F_HIGH) > b1(R_HIGH)`.

Die neue Bindung darf den Feldvorschlag dieses Subschritts nicht beeinflussen.

### Subschritt 2

- Der vollstaendige Feldvorzustand `S1/H1` bleibt zwischen den Armen bitgenau
  identisch.
- Der Adapter liest nun ausschliesslich das jeweils vorbestehende `b1`.
- Deshalb muss seine Zielkantenrate in F_HIGH strikt groesser sein.
- Erst der Feldvorschlag dieses zweiten Subschritts darf zwischen den Armen
  divergieren.
- Der gleichzeitig gebildete Ressourcenpoststate aus Subschritt 2 darf die
  Feldtrennung nicht erklaeren.

Ein dritter Subschritt gehoert nicht zum minimalen Readout.

## Feldmessung

Gebunden werden:

- vollstaendige kanonische `S`- und `H`-Vektoren nach jedem Subschritt;
- angewandte Kantenraten in beiden Subschritten;
- der orientierte Zielkantenkontrast
  `C = S(second_endpoint) - S(first_endpoint)`;
- die Maximumsnorm der vollstaendigen S/H-Armtrennung nach Subschritt 2;
- Ressourcen- und Bilanzledger nur als kausale Diagnostik.

Das naechste Fixture muss einen positiven Kantenkontrast vor Subschritt 2
binden und vor der Ausfuehrung analytisch Vorzeichen, Nichtnullmarge und
Float64-Grenze festlegen. Fuer dieses Fixture lautet die gerichtete Prognose:

```text
C_F_HIGH(substep 2) < C_R_HIGH(substep 2)
```

Die vollstaendige S/H-Trennung muss zugleich oberhalb der vorregistrierten
Rundungsgrenze liegen. Eine nach dem Ergebnis gewaehlte Richtung oder Schwelle
ist verboten.

## Kontrollen

1. Wertidentische Aufteilungen muessen durch beide Subschritte bitgenau
   identische vollstaendige Paare liefern.
2. A0 muss in beiden Armen und beiden Subschritten bitgenau den neutralen
   Feldpfad liefern.
3. Ein vor der Probe auf `b0` fixierter Adapter muss zwischen den Armen in
   beiden Subschritten bitgenau bleiben.
4. Der gerichtete aktive Readout muss auch fuer ein in beiden Armen exakt
   gleiches `H0=0` vorregistriert werden.

## Gegenbaselines

- Fixed Adapter/Frozen-E1 kann nach identischem ersten Feldzustand mit einem
  einzigen `b0`-Adapter nicht armweise divergieren.
- Leaky/Integrator sieht durch Subschritt 1 dieselbe Feldgeschichte und
  denselben Folgeeingang.
- Das gebundene zweistufige E1 kollabiert die Arme bei gleichem `b0` und
  gleicher Gesamtressource und sagt deshalb gleiches `b1` voraus.
- F3/CONST-V besitzt ohne Transport keine lokale Frei/Refraktaer-Koordinate
  fuer einen armweisen `b1`-Adapter.
- Schneller Nachhall bleibt bis zum zweiten Vorschlag bitgenau gleich; die
  Null-H-Kontrolle sperrt eine H-Erklaerung zusaetzlich.

Keine Baseline darf Arm-ID, Frei/Refraktaer-Koordinate oder einen armweisen Fit
erhalten.

## PASS und STOPP

Ein spaeterer PASS setzt gemeinsam voraus: vollstaendige aktive Arme und alle
vier Kontrollen, exakte Erstschrittidentitaeten, gerichtetes `b1` und
gerichteten Zweitschrittadapter, Zweitschritt-Feldtrennung oberhalb der festen
Grenze mit vorregistrierter Kontrastrichtung, gueltige Feldbereiche und
Ressourcenbilanzen sowie unveraenderte Gegenbaselines.

Jede Abweichung ergibt atomar STOPP. Insbesondere sind Poststateeinfluss im
gleichen Subschritt, ein dritter Erklaerungsschritt, Proxy-Messung,
Baselineerweiterung, Nachjustierung, Retry, Teiloutput, Runtimekopplung und
nicht registrierte Ausfuehrung ausgeschlossen.

## Aussagegrenze

S1-IC hat nur die Kausalprognose und ihre Falsifikation gebunden. Eine
Feldwirkung wurde noch nicht gemessen. Selbst ein spaeterer PASS waere nur ein
begrenzter technischer Feldreadout der bereits bekannten Ressourcenintervention,
kein Befund zu Abschwaechung, Interferenz, Freigabe, Wiederbeanspruchung oder
Materialeignung. Weitergehende Claims bleiben gesperrt.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1ic_causal_field_readout_contract.py
tests/test_dynamic_substrate_s1ic_causal_field_readout_contract.py
```

Neun Tests pruefen Quellenbindung, Paarinvarianten, Kausalkette,
Feldobservablen, vier Kontrollen, alle Gegenbaselinegruppen, Atomaritaet,
Ausfuehrungssperren und Manipulationsschutz.

## Bester naechster Schritt

S1-ID darf ausschliesslich ein endliches synthetisches Fixture und einen
Ausfuehrungsvertrag fuer S1-IC binden. Vor jeder Implementierung muessen
konkrete Feld- und Anatomiewerte, Kontakte, Zeiten, Raten, analytische
Erstschrittidentitaeten, Zweitschritt-Kontrastrichtung, Rundungsgrenze,
Fallmatrix und maximales Feldschrittbudget feststehen. Noch keine
Implementierung, Runtime oder Ausfuehrung.
