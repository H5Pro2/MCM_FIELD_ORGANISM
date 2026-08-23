# S1-WJ: Private PPB-1-Root- und Ressourcenadapter

## Auftrag und Grenze

S1-WJ implementiert die erste technische Adapterbruecke aus dem
S1-WG-Integrationsdelta. Die Bruecke bleibt vollstaendig auf einen
dedizierten Temporaerspiegel und injizierte Testwerte begrenzt.

Nicht ausgefuehrt werden:

- Zugriff auf die echte Produktionswurzel;
- Betriebssystem- oder Ressourcenabfrage;
- Atomizitaets- oder Artefaktpfadprobe;
- Dateischreibvorgang;
- Autorisierungsinstanziierung;
- Lock-, Terminal-, Producer- oder Matrixfunktion;
- Feld-, Rezeptor- oder Medienruntime.

## Rootspiegel

Akzeptiert wird nur ein existierendes Verzeichnis namens
`s1wj-production-root-mirror` unter der Betriebssystem-Temporaerwurzel. Ein
gleichnamiges Workspace-Verzeichnis, ein abweichender Name und insbesondere
`data/generated/ppb1/one_shot` werden abgelehnt.

Der kanonische Rootreceipt bindet:

- die vertragliche relative Produktionsrootrolle als Text;
- einen Digest des aufgeloesten Temporaerspiegels;
- injizierte Artefakt- und Temporaervolumeidentitaeten;
- die daraus abgeleitete Same-Volume-Rolle;
- `mirror_only = true`;
- `production_root_accessed = false`;
- null Dateischreibvorgaenge und Produktionsartefakte.

Die vertragliche Produktionsrootrolle wird damit beschrieben, aber nicht
auf dem Dateisystem aufgeloest oder geprueft.

## Injizierte Ressourcen

S1-WJ verlangt vier explizite Testwerte:

```text
available_physical_memory_bytes
artifact_volume_free_bytes
atomic_replace_probe_passed
artifact_paths_free
```

Plattform- und Quellbindung sowie Volumeidentitaeten bleiben ebenfalls
injizierte Vertragsrollen. Daraus werden die bestehenden privaten
S1-WB-Beobachtungs- und Gateobjekte gebildet. `injected_value_count = 4` ist
fest gebunden.

Insbesondere bedeuten `atomic_replace_probe_passed = true` und
`artifact_paths_free = true` nur positive Testeingaben. S1-WJ hat diese
Eigenschaften nicht an der echten Produktionswurzel gemessen.

## Bruecke zur Koordinatorhuelle

Ein gueltiger Rootreceipt erzeugt einen unveraenderlichen H0B-Adapter. Bei
Volumeabweichung ist dessen `passed`-Rolle falsch. Ein Ressourcenreceipt
erzeugt H0C genau nach `all_resource_gates_passed`.

Der positive kombinierte Fixturepfad erreicht in S1-WH weiterhin nur:

```text
H0A -> H0B -> H0C -> H0D -> H0E -> H1 -> H2_BLOCKED
```

Produceraufloesung und Produktionswirkung bleiben null.

## Abnahme

Die zwoelf neuen Tests bestaetigen:

- kanonischen schreibfreien Rootspiegelreceipt;
- harte Ablehnung der echten Produktionswurzel;
- Ablehnung falscher und lokaler Spiegelwurzeln;
- Volumeformatvalidierung;
- sichtbare Same-Volume-Abweichung in H0B;
- positiven vierfach injizierten Ressourcengatepfad;
- getrennte Speicher- und Datentraegergrenzen;
- getrennte Atomizitaets- und Pfadrollen;
- getrennte Plattform- und Quellcodedrift;
- H0B-/H0C-Bruecke mit unveraenderter H2-Sperre;
- gesperrten Produktionsentry und fehlende OS-/Dateischreib-APIs;
- private API- und Snapshotneutralitaet.

S1-WJ-Quellcodedigest:

```text
60cbacf603e2a8d5235fbd3d52bd21fa466a353b9404eb11479926d461c556af
```

Zusammen bestehen `254 von 254` aktuelle fokussierte PPB-1-Tests.

## Entscheidung

```text
S1_WJ_PRIVATE_TEMPORARY_ROOT_MIRROR_RECEIPT_IMPLEMENTED
S1_WJ_FOUR_EXPLICIT_INJECTED_RESOURCE_VALUES_BOUND
S1_WJ_EXISTING_S1WB_RESOURCE_GATE_REUSED
S1_WJ_H0B_AND_H0C_BRIDGE_TO_S1WH_ACCEPTED
S1_WJ_REAL_PRODUCTION_ROOT_OS_PROBES_AND_WRITES_ZERO
S1_WJ_H2_PRODUCER_RESOLUTION_REMAINS_BLOCKED
S1_WJ_12_OF_12_NEW_TESTS_PASS
S1_WJ_254_OF_254_CURRENT_FOCUSED_PPB1_TESTS_PASS
```

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-WK - statischer Root-/Ressourcenadapter- und Produktionsgrenzenaudit
```

S1-WK darf nur S1-WG-Vertrag, S1-WJ-Quelltext, AST und Typfelder lesen. Keine
S1-WJ-, S1-WH-, Ressourcen-, Dateisystem-, Autorisierungs-, Producer-,
Matrix-, Feld- oder Medienfunktion darf ausgefuehrt werden.

## Grundlagen

- [S1-WI statischer Koordinatorpreflight](S1WI_PPB1_STATISCHER_KOORDINATOR_PREFLIGHT.md)
- [S1-WH private In-Memory-Koordinatorhuelle](S1WH_PPB1_PRIVATE_IN_MEMORY_KOORDINATORHUELLE.md)
- [S1-WG statischer Integrationsdelta-Vertrag](S1WG_PPB1_STATISCHER_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG.md)
