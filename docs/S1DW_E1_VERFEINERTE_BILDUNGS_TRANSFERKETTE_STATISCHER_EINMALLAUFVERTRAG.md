# S1-DW: E1 verfeinerte Bildungs-Transferkette statischer Einmallaufvertrag

## Status

Der Ergebnis- und Entscheidungsraum fuer genau einen spaeteren kanonischen
Lauf der verfeinerten Bildungs- und Transferkette ist statisch registriert.
Es wurde kein Produzent, Runner, E1-Zustand, Feld oder Probe ausgefuehrt und
keine Ergebnisdatei angelegt.

## Implementierung

```text
mcm_field_organism/e1_refined_chain_one_shot_contract.py
tests/test_e1_refined_chain_one_shot_contract.py
```

Projektgebundener Vertragsdigest:

```text
63170519c9d0486f4110506be6c4f3fd90cd27c8f58635dab804e9426ce9fb1a
```

Konfigurationsdigest:

```text
542ec0179fd328dc68f12db27968539f748834f4c29f313185a50e9ba026b9b7
```

## Gebundene Grundlage

S1-DW bindet vor weiterer Implementierung:

- den S1-DS-Vertragsdigest;
- den kanonischen S1-DU-Preflight-Digest;
- den aktuellen S1-DV-Bildungsrunner-Digest;
- den bestehenden eingefrorenen S1-DL-Transferkern-Digest;
- AB-, BA-, Permutations- und identischen Probe-Digest;
- History- und Probezeit, 220 und 110 Supports, 84 Knoten und 145 Kanten;
- `r1/r2/r4`;
- fuenf Bildungsarme und sieben Probearme je Verfeinerung;
- alle Metriken, elf Pflichtkontrollen, vier Entscheidungen und ihre
  Reihenfolge;
- den vorregistrierten Signalfaktor acht.

Der S1-DV-Digest bindet nur die synthetisch abgenommene Runnermechanik. Der
Runner selbst lehnt kanonische Quellen weiterhin ab. S1-DW gibt deshalb
nicht vor, dass bereits ein kanonischer Produzent existiert.

## Ergebnisvertrag

Ein spaeteres Ergebnis muss geordnet enthalten:

```text
execution_id
one_shot_contract_digest
s1_ds_contract_digest
s1_du_preflight_digest
formation_implementation_digest
transfer_implementation_digest
source_digests
probe_digest
refinement_result_digests
result_digest
technical_decision
metrics
controls
result
```

Die Persistenz bleibt atomar. Ein gestarteter Fehler behaelt den
Versuchsmarker und erlaubt keine automatische Wiederholung.

## Einmalpfade

```text
reports/e1_refined_formation_transfer_s1ea_once_v1.json
reports/e1_refined_formation_transfer_s1ea_once_v1.attempt.json
reports/e1_refined_formation_transfer_s1ea_once_v1.lock
```

Alle drei Pfade fehlen zum Abschluss von S1-DW.

## Freigabegrenze

S1-DW setzt ausdruecklich:

```text
execution_permitted = False
execution_started = False
canonical_producer_bound = False
canonical_executor_bound = False
```

Damit ist der Einmallauf registriert, aber nicht freigegeben. Ebenfalls
gesperrt bleiben Wiederholungen von S1-DI und S1-DQ sowie Memory-, Semantik-,
Organisations-, Topologie-, Selbstregulations- und KI-Claims.

## Technische Abnahme

```text
8 fokussierte Tests
351 Tests im vollstaendigen E1-Verbund
OK
```

Geprueft sind Quellen- und Evidenzbindung, freie Pfade, deterministischer
Digest, Berichtsfelder, Entscheidungsgrenze, fehlende Lauf-Freigabe,
Fail-closed-Verhalten, Nichtausfuehrung und private API-Grenze.

## Aussagegrenze

S1-DW ist ein statischer Vertrag. Er enthaelt keine gebildeten E1-Zustaende,
keine Feldantworten und keinen wissenschaftlichen Befund.

## Bester naechster Schritt

S1-DX implementiert den privaten Einmalexecutor und den reinen
Ergebniscontainer fuer diese Kette. Erfolg, Vorstartfehler, gestarteter
Fehler, atomare Veroeffentlichung, Kontrollfehler und Wiederholungsschutz
werden nur mit synthetischen Ergebnisproduzenten geprueft. Der kanonische
Produzent und alle S1-EA-Pfade bleiben dabei unaufgerufen.

## Anschlussstatus nach S1-DX

S1-DX hat Ergebniscontainer und atomare Persistenz inzwischen nur mit
synthetischen Zielordnern abgenommen. Die kanonische Ausfuehrung bleibt
gesperrt und alle S1-EA-Pfade fehlen. Der aktuelle Anschluss steht in
`S1DX_E1_VERFEINERTER_KETTENERGEBNISKERN_UND_SYNTHETISCHER_EINMALEXECUTOR.md`.
