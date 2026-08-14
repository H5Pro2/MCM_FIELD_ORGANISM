# S1-EB28: Statischer kanonischer Datenflussvertrag

## Status

S1-EB28 bindet die konkreten Artefakttypen, Parameteruebergaben,
Digestkontinuitaeten und Sperrfelder zwischen den sechs in S1-EB27
registrierten kanonischen Funktionen.

Es wurden keine kanonischen Artefakte konstruiert und keine Funktion
aufgerufen.

## Implementierung

```text
mcm_field_organism/e1_confirmation_canonical_dataflow_contract.py
tests/test_e1_confirmation_canonical_dataflow_contract.py
```

Normalisierter Implementierungsdigest:

```text
b6e483e4a0aaecb0eb584318e454ade19c11b0d09e378753c0f27f7162556b78
```

Vertrags-Payloaddigest:

```text
f14f301c5391c6f5052d486dcf0473d7e07caf7b070cfdc84e2038cef8c53ba6
```

## Gebundene Artefakttypen

```text
E1ConfirmationCanonicalFormationProduction
E1ConfirmationCanonicalProbeHandoff
E1ConfirmationProbeResult
E1ConfirmationCanonicalResultHandoff
E1ConfirmationChainResult
E1ConfirmationCanonicalReportHandoff
```

Fuer jeden Typ sind Feldinventar, primaeres Digestfeld und
Verfeinerungsbezug gebunden. Die externen Definitionen von Probe-Resultat und
Chain-Resultat sind zusaetzlich ueber ihre Modulhashes fixiert.

## Digestkontinuitaet

```text
formation.production_digest
  -> probe_handoff.formation_production_digest
  -> result_handoff.formation_production_digest

formation.refinements[*].result_digest
  -> probe_handoff.formation_result_digests

probe_handoff.handoff_digest
  -> result_handoff.probe_handoff_digest

probe_results[*].result_digest
  -> result_handoff.probe_result_digests

probe_results[*].field_digests
  -> result_handoff.probe_field_digests

result_handoff.handoff_digest
  -> report_handoff.result_handoff_digest

chain_result.result_digest
  -> report_handoff.result_digest
```

Genau drei Probe-Resultate in der Reihenfolge `r2`, `r4`, `r8` sind Pflicht.

## Geschlossene Gates

Zwoelf bestehende Sperren bleiben gebunden:

```text
Probe-Handoff:
  probe_execution_permitted       = false
  decision_permitted              = false
  persistence_permitted           = false
  claims_permitted                = false

Result-Handoff:
  result_composition_permitted    = false
  decision_permitted              = false
  persistence_permitted           = false
  claims_permitted                = false

Report-Handoff:
  execution_permitted             = false
  persistence_permitted           = false
  retry_permitted                 = false
  claims_permitted                = false
```

## Technische Abnahme

```text
9 fokussierte S1-EB28-Tests
605 Tests im vollstaendigen E1-Verbund
OK
```

Geprueft wurden sechs Typschemata, zwoelf Parameterkanten, acht
Digestkanten, `r2/r4/r8`, externe Typquellen, alle Sperrfelder,
Manipulationsabwehr, Wiederholbarkeit, fehlende Konstruktor-/Runtime-/Writer-
Aufrufe, private API und freie kanonische Zielpfade.

Der S1-EA6-Bericht blieb unter
`adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47`
unveraendert. Alle drei S1-EB-Zielpfade bleiben frei.

## Aussagegrenze

Der Datenflussvertrag ist kein Feldlauf und kein Forschungsbefund. Er
erlaubt keine Memory-, Feldzeit-, Bedeutungs-, Organisations-, Topologie-
oder KI-Aussage.

## Bester naechster Schritt

S1-EB29 bindet statisch den minimalen Freischaltungsadapter fuer den spaeteren
autorisierten Workerprozess. Dieser Vertrag muss exakt festlegen, welche
Probe-, Kompositions-, Ausfuehrungs- und Persistenzsperren wann geoeffnet
werden duerfen und welche Sperren, insbesondere Retry und Claims, dauerhaft
geschlossen bleiben. S1-EB29 darf noch kein Gate oeffnen, kein Objekt
erzeugen und keinen Lauf starten.
