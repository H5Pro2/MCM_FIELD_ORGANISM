# S2-JL - S2-IG-End-to-End-Integration und Qualifikation

## Status

`PRIVATE_S2IG_END_TO_END_CONTEXT_USE_INTEGRATION_VALID`

Qualifikations-ID:

`s2jl-s2ig-end-to-end-integration-qualification-20260901-02`

Die vorhandene private S2-IG-Laufhuelle ist minimal um die bereits
qualifizierte S2-JH-Zulassung und die S2-JK-Verbrauchsarme erweitert. Es wurde
keine neue Runner-, Recorder-, Registry- oder Plattformarchitektur angelegt.
Der Hauptlauf wurde nicht ausgefuehrt und das Gate blieb geschlossen.

## Gebundene Laufanatomie

Die sechs Geschichten, 38 Formationen und acht S2-IE-Faelle bleiben
unveraendert. Nach den bisherigen 170 Ausfuehrungsoperationen folgen pro Fall
genau diese fuenf Operationen:

1. `CONTEXT_ADMISSION_INVOKE`;
2. `CURRENT_PERCEPTION_ONLY_PROJECT`;
3. `ADMITTED_CONTEXT_USE_INVOKE`;
4. `DIRECT_CONTEXT_USE_BASELINE_INVOKE`;
5. `CONTEXT_USE_CASE_EVIDENCE_SEAL`.

Damit gelten fuer den spaeteren Hauptlauf:

```text
Erfolgsoperationen       = 223
START-/RESULT-Ereignisse = 446
Erfolgsbudget            = 1.283.226 Byte
maximaler Fehlerpfad     = 1.290.394 Byte
Mehr-Eltern-Operationen  = 116
Mehr-Eltern-Referenzen   = 294
interne Elternreferenzen = 400
```

Das Ausfuehrungspaket bindet direkt die acht Kontext-Fallbelege. Diese binden
transitiv die zugehoerigen bisherigen Fall- und Geschichtenbelege. Seine
`ParentSetV1`-Vorform umfasst damit 1.698 Byte und bleibt innerhalb der
unveraenderten Grenze von 2.816 Byte.

Die zusaetzlichen Einzelgrenzen sind:

| Belegrolle | Grenze | neutral gemessene Huelle |
| --- | ---: | ---: |
| S2-JH-Zulassung | 3.072 Byte | 1.796 Byte |
| Current-only | 1.536 Byte | 1.171 Byte |
| S2-JK-Plus-Arm | 3.584 Byte | 1.884 Byte |
| direkte S2-JK-Baseline | 3.584 Byte | 1.893 Byte |
| Kontext-Fallbeleg | 3.584 Byte | 2.450 Byte |

Alle drei Funktionsarme erhalten exakt dieselbe maskierte Probe. Status und
Anwendbarkeit werden nicht erneut berechnet. Der Runner materialisiert die
qualifizierten S2-IC-Findings einmal und reicht sie unveraendert an S2-JH und
S2-JK weiter. Enthaltungsstatus rufen weder die Adapterfuellung noch die
direkte Baselinefuellung auf.

## Auswertungstrennung

Der Ausfuehrungspfad versiegelt nur Signal-, Zulassungs-, Current-only-, Plus-
und Direktbaselinebefunde. Zielwerte bleiben in der unabhaengigen
Evaluationswurzel. Erst nach `EXECUTION_EVIDENCE_SEAL` bindet
`EvaluationRunBinding` beide Wurzeln.

Die Auswertung prueft getrennt:

- den erwarteten Fuenf-Status-Befund;
- den erwarteten S2-JK-Abschlussstatus;
- unveraendertes Current-only;
- ausschliesslich maskierte Ergaenzungen bei `c01`, `c04` und `c05`;
- unveraenderte Probe bei `c02`, `c03`, `c06`, `c07` und `c08`;
- Gleichheit von Plus-Arm und direkter Kompositionsbaseline;
- vollstaendige Read-only-Zustandsidentitaet.

## Qualifikationsbefund

Vor dem Testlauf bestanden Syntax-, Registry-, DAG-, Budget-, Gate-, Quellen-
und Evaluationswurzelpruefung. Danach wurde genau ein Testaufruf ausgefuehrt:

```text
python -m unittest tests.test_s2jl_s2ig_end_to_end_integration -v
Ran 12 tests in 0.151s
OK
Exit-Code 0
```

Ein vorangegangener Lauf unter der ID
`s2jl-s2ig-end-to-end-integration-qualification-20260901-01` erreichte zwar
ebenfalls `12/12`, war aber nicht qualifizierend: Ein anschliessender statischer
Nachcheck fand eine zu grosse direkte Elternliste am Ausfuehrungspaket. Der
Graph wurde ohne Aenderung der Funktionslogik auf die acht transitiv
vollstaendigen Kontext-Fallbelege korrigiert. Erst der oben dokumentierte neue
Lauf unter eigener ID qualifiziert diesen Stand.

Die Tests deckten alle fuenf Statuswerte, A/B-Spiegelung, symmetrisches
`CONSISTENT`, unterbliebene Fuellung bei Enthaltung, manipulierte
Zulassungsbelege, Baselinegleichheit, Receiptgrenzen, Verifikatorbindungen und
vollstaendige Zustandsunveraendertheit ab. Es wurden keine Geschichten,
Formationen, Memory-, Rezeptor- oder Feldzustandsfunktionen ausgefuehrt.

## Quellbindung

| Datei | SHA-256 vor und nach dem Lauf |
| --- | --- |
| `tools/_s2ig_private_fixture_registry.py` | `8ad973f3d5ea68f8ebdf097a6915c5f3bee39a8aabb3979bbd0f8009e6d329f8` |
| `tools/_s2ig_private_runner.py` | `8170508adedce49ae06ab22f0ab3be9d80d270ac547b347633ef6e2b34246402` |
| `tools/_s2ig_private_append_only_recorder.py` | `457c159bf9b062ccdbab5609b666e1a3fed0c8f1b156ec4896326624024a7402` |
| `tools/_s2ig_private_result_verifier.py` | `90baf077fa0a4298105b1043a42bd9d9ebbd668653dcc1dc958f9504da32a002` |
| `tests/test_s2jl_s2ig_end_to_end_integration.py` | `6966f78ec07df3727acabcd99df53e5600c20a6947db0ffcc539b38cbc993dfc` |

Die Hashes waren vor und nach dem Testlauf identisch. Der Recorderquellstand
blieb unveraendert.

## Freigabegrenze

Der Befund qualifiziert nur die erweiterte private Laufhuelle. Er ist kein
realer Kontextfunktionsbefund. `MAIN_EXECUTION_ENABLED` bleibt `False`.

Genau ein realer Acht-Faelle-Lauf benoetigt eine separate Freigabe. Danach
wird der Kontextzweig unabhaengig vom Ergebnis geschlossen. Der anschliessende
Hauptabschnitt bleibt die quellenunabhaengige Pixel-/Audio-Wahrnehmungsgrenze.
