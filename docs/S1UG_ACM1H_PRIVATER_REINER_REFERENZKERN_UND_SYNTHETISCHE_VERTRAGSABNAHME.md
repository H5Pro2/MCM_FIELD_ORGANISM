# S1-UG: ACM-1H privater reiner Referenzkern und synthetische Vertragsabnahme

## Freigabe und Grenze

S1-UG wurde ausdruecklich freigegeben fuer:

> ausschliesslich den privaten reinen ACM-1H-Referenzkern und synthetische
> Vertragstests; keine SharedMCMField-Integration, kein Snapshotumbau und
> kein Feldlauf.

Diese Grenze wurde eingehalten. Der produktive Feldkern, seine oeffentliche
API, Snapshots, Rezeptorpfade und Laufwerkzeuge wurden nicht veraendert.

## Implementierter Kern

Der private Kern liegt in:

```text
mcm_field_organism/_acm1h_reference.py
```

Er implementiert ausschliesslich den in S1-UE und S1-UF gebundenen
Vier-Knoten-Korridor:

```text
node-a -- node-b -- node-c -- node-d
```

Enthalten sind:

- die sechs vorregistrierten aktiven `(gamma_z, beta)`-Konfigurationen;
- getrennte reine Orakel fuer ACM-OFF, `z = 0`, Readout-OFF und Write-OFF;
- kanonische Kanten- und Motivrollen;
- die Primaerflussabbildung aus Rate und S-Vorzustand;
- donorbegrenzte `z`-Fortschreibung mit beteiligungsfreiem Halten;
- gemeinsamer Motivreadout aus `z_pre`;
- multiplikative, reihenfolgeneutrale Komposition auf `e_bc`;
- nichtnegative symmetrische Kantenraten und ein quellenfreier
  Vier-Knoten-Generator;
- die enge vorzeichenblinde IAG-2-Fortschreibung;
- unveraenderliche Records, kanonische Payloads und SHA-256-Digests;
- atomare Erfolgs- oder Fehlerrecords ohne Teilresultat.

Das Modul wird weder aus dem Paketroot noch aus `current_api` exportiert.

## Implementierte Recordrollen

Die in S1-UF gebundenen Rollen sind als frozen Dataclasses umgesetzt:

1. `ACM1HConfigRecord`
2. `ACM1HPrestateRecord`
3. `ACM1HEdgeFluxRecord`
4. `ACM1HMotifProposalRecord`
5. `ACM1HCompositionRecord`
6. `ACM1HDecisionRecord`

Ein erfolgreicher Decisionrecord enthaelt den vollstaendigen Konfigurations-
und Vorzustandsbezug, alle drei Primaerfluesse, beide Motivvorschlaege und
die vollstaendige Komposition. Ein Fehlerrecord enthaelt ausschliesslich
`FAILED` und genau einen gebundenen Fehlercode.

## Synthetische Vertragsabnahme

Die neue Testdatei lautet:

```text
tests/test_acm1h_reference.py
```

Die 14 fokussierten Tests pruefen:

- alle sechs aktiven Parameterkandidaten;
- alle vier getrennten festen Ablationen;
- Primaerflussgleichung und symmetrischen Generator;
- Wertebereich, Donorbegrenzung und `z_pre`-Readout;
- Halten bei inaktiver Einzelkante;
- einmalige und reihenfolgeneutrale `e_bc`-Komposition;
- gemeinsamen Vorzeichenwechsel;
- Spiegelung der offenen Linie;
- echte zweistufige G/O-Fortschreibung gegen IAG-2;
- atomare Fehlerrecords;
- Konfigurations-, Geometrie-, Kanten- und Ratenvalidatoren;
- Unveraenderlichkeit der Records;
- unveraenderte private und oeffentliche API-Grenzen.

Ergebnis:

```text
14 fokussierte ACM-1H-Tests: bestanden
```

## Direkter Regressionstest

Zusaetzlich wurden gemeinsam ausgefuehrt:

- ACM-1H-Referenztests;
- `MCMFieldStepTime`-Vertrag;
- vorhandener E1-Kantenratenadapter und Generator;
- Architekturvertragsgrenze;
- aktive Engineeringoberflaeche.

Ergebnis:

```text
37 direkt relevante Tests: bestanden
```

Es wurde kein Browser, kein Audio-/Video-Pfad, kein Rezeptorprozess und kein
Feldlauf gestartet.

## Technischer Befund

Die S1-UE-Minimalgleichung ist im isolierten reinen Vier-Knoten-Korridor
implementierbar. Die synthetischen Orakel bestaetigen fuer die registrierten
Eingaben:

- begrenzte Zustandsfortschreibung ohne Clipping;
- exaktes Halten ohne gemeinsame Beteiligung;
- nichtnegative Kantenfaktoren;
- quellenfreie symmetrische Generatorbildung;
- einmalige gemeinsame Kantenkomposition;
- G/O-Trennung bei wertidentischem IAG-2-Endzustand;
- Fail-Closed-Verhalten ohne Teiloutput.

Dies ist eine technische Vertragsabnahme. Sie weist keinen praktischen
Feldnutzen, keine Wirkung in `SharedMCMField` und keine vorhandene
Memory-, Lern- oder KI-Faehigkeit nach.

## Unveraenderte Sperren

Weiterhin nicht zugelassen sind:

- Import oder Export des Referenzkerns ueber die oeffentliche API;
- ACM-1H-Zustand in `SharedMCMField` oder dessen Snapshot;
- Aenderungen an `SharedMCMField.advance` oder `MCMNeuronLayer.advance`;
- Integration in Browser-, Audio-, Video- oder Rezeptorpfade;
- Feldlauf, Parameteroptimierung oder Ergebniswahl;
- Funktionsentscheidung aus den synthetischen Tests;
- Wiedereroeffnung von RFM-1.

## Entscheidung

```text
S1_UG_PRIVATE_PURE_ACM1H_REFERENCE_KERNEL_IMPLEMENTED
SIX_PARAMETER_CANDIDATES_AND_SEVEN_ORACLE_CLASSES_TECHNICALLY_COVERED
FOURTEEN_FOCUSED_AND_THIRTYSEVEN_RELEVANT_TESTS_PASSED
PUBLIC_API_FIELD_RUNTIME_AND_SNAPSHOTS_UNCHANGED
NO_FIELD_RUN_NO_FUNCTION_FINDING
```

## Naechster Schritt

Der naechste methodisch zulaessige Schritt ist S1-UH als ausschliesslich
statischer Zustandscontainer-, Atomaritaets-, Integrationsgrenz- und
Reduktionsaudit. Er darf noch keine Runtime implementieren oder ausfuehren.
Zu klaeren sind:

- kleinster private Feld-/ACM-Zustandspaarcontainer ohne Snapshotaenderung;
- Geschwistervorschlag und atomarer Paarcommit ohne Write-then-read;
- exakter ACM-OFF-Bypass zum unveraenderten neutralen Feldkern;
- Abgrenzung gegen den vorhandenen E1-Gainadapter;
- ob eine spaetere Runtimeintegration einen technischen Mehrwert besitzt,
  der den zusaetzlichen Carry rechtfertigt;
- welche neue ausdrueckliche Freigabe vor jeder Runtimeimplementierung
  erforderlich waere.

Falls kein sauberer atomarer Integrationsweg ohne produktiven Snapshotumbau
verbleibt, bleibt ACM-1H auf den privaten Referenzkern begrenzt.
