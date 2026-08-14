# S1-EB4: Statischer E1-Bestaetigungskettenvertrag

## Status

Die vollstaendige spaetere S1-EB-Bestaetigungskette ist statisch gebunden.
Der Vertrag erzeugt nur Metadaten und Digests. Er hat keinen Produzenten,
Executor, E1-Zustand, Feld oder Probe ausgefuehrt und keinen Exactly-once-
Pfad angelegt.

## Implementierung

```text
mcm_field_organism/e1_confirmation_chain_contract.py
tests/test_e1_confirmation_chain_contract.py
```

Normalisierter Implementierungsdigest:

```text
6c5da63148d3923acc3c3c87b101c7ca9cace63a97449f50d4c4d3bfa8622a78
```

Vertragsdigest:

```text
acf1136fa9142747729a78dda719bd36086ce2eed9e015dbfbdb58d8302fa650
```

Konfigurationsdigest:

```text
415e0323fe1eafa5c5dfd42d429b2b70dc47d54aaadad52d40b59a41319c714d
```

## Gebundene Kette

S1-EB4 bindet hashgenau:

- den S1-EB-Vertrag;
- den kanonischen S1-EB2-Preflight;
- den getrennten `r2/r4/r8`-Planer;
- den synthetisch abgenommenen S1-EB3-Bildungsrunner;
- den unveraenderten eingefrorenen Transferkern;
- den unveraenderten siebenarmigen Probeweg;
- die kanonischen AB-, BA-, Permutations- und Probequellen;
- die drei kanonischen Planmengen;
- 220 History- und 110 Probe-Supports;
- 200 History- und 100 Probe-Abschlusszeiten;
- 84 Feldknoten und 145 Kanten;
- fuenf Bildungs- und sieben Probearme;
- elf Pflichtkontrollen und die vier vorregistrierten Entscheidungen;
- die unveraenderte strikte Achtfachgrenze.

Kanonischer Preflight-Digest:

```text
e657636e86cea6eabef638597ed22e3e0bc6894bbdc9f9fb96c001d3c31a0372
```

## Ergebnisoberflaeche

Die spaetere Auswertung muss fuer `r2/r4/r8` dieselben Zustands- und
Probensignale liefern und zwei getrennte numerische Reststufen ausweisen:

```text
state_refinement_r2_r4
state_refinement_r4_r8
probe_refinement_r2_r4
probe_refinement_r4_r8
```

Die Entscheidung bleibt exakt die S1-EB-Vorregistrierung. Eine nachtraeglich
weichere Schwelle oder geaenderte Mechanik ist nicht zulaessig.

## Geschlossene Freigaben

```text
canonical_producer_bound             = false
canonical_executor_bound             = false
execution_permitted                  = false
execution_started                    = false
s1_ea6_rerun_permitted               = false
posthoc_threshold_change_permitted   = false
alle starken Claims                  = false
```

Die drei S1-EB-Ergebnis-, Attempt- und Lockpfade bleiben frei.

## Technische Abnahme

```text
8 fokussierte S1-EB4-Tests
447 Tests im vollstaendigen E1-Verbund
OK
```

## Aussagegrenze

S1-EB4 ist ein statischer Ausfuehrungs- und Ergebnisvertrag. Er liefert
keinen kanonischen Zustands-, Transfer-, Memory-, Semantik-, Organisations-,
Topologie-, Selbstregulations- oder KI-Befund.

## Anschluss

S1-EB5 hat den privaten `r2/r4/r8`-Ergebnis- und Entscheidungskern mit
synthetisch konstruierten Resultaten abgenommen. Alle vier Entscheidungen
und die strikte Achtfachgrenze sind kontrolliert; kanonische Ausfuehrung und
S1-EB-Pfade blieben unberuehrt. Siehe
[S1-EB5 Ergebnis- und Entscheidungskern](S1EB5_E1_R2_R4_R8_ERGEBNIS_UND_ENTSCHEIDUNGSKERN.md).
