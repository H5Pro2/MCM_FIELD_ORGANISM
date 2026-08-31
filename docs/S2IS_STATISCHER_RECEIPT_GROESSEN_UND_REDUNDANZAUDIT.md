# S2-IS: Statischer Receipt-Groessen- und Redundanzaudit

Status: `S2IS_STATIC_AUDIT_PASSED_COMPACT_RECEIPT_CORRECTION_ELIGIBLE`

## Grenze

S2-IS ist ausschliesslich ein statischer Audit. Es wurden keine Projektmodule
importiert, keine Tests ausgefuehrt und keine Rezeptor-, Speicher-, Signal-,
Baseline- oder Runnerfunktion aufgerufen. Es wurden weder Produktivcode noch
Registry, Validatoren, Grenzen oder Gates geaendert.

S2-IQ bleibt dauerhaft `NOT_EVALUABLE`. Der fehlgeschlagene S2-IR-Lauf bleibt
`QUALIFICATION_FAILED_RECORDING_BOUND` und wurde nicht wiederholt.

Die kanonische Groessenform ist unveraendert:

- ASCII-JSON;
- sortierte Schluessel;
- Trenner `,` und `:` ohne Leerzeichen;
- genau ein abschliessendes LF;
- vollstaendige Recorderhuelle;
- maximal 96 Zeichen lange gueltige Run-, Invocation- und Owner-IDs.

## Ursache bei `ie-op-117`

Das aktuelle `DUAL_PROBE_AND_ARM_INPUTS_BIND`-Receipt serialisiert:

1. den vollstaendigen `DualProbeCaseBinding`;
2. den vollstaendigen `DualProbeOwnerSnapshot` im Zustand `READY`;
3. Signal- und Baseline-Inputdigest erneut;
4. den vollstaendigen Quellenledger;
5. den Quellenledgerdigest erneut.

Der Owner-Vorzustand wiederholt Case-Plan, Dual-Binding, Kontextprobe,
Signalprobe, Two-Area-Bundle sowie beide Inputdigests. Die beiden Inputdigests
und der Ledgerdigest werden anschliessend auf der obersten Ebene nochmals
gespeichert.

| Form | Nutzpayload | vollstaendige Huelle | Grenze |
| --- | ---: | ---: | ---: |
| S2-IR, konkrete IDs | 3.095 | 3.416 | 2.048 |
| zulaessiger 96-Zeichen-Worst-Case | 3.167 | 3.552 | 2.048 |

`IG-E008` ist damit statisch reproduziert. Eine Erhoehung der 2.048-Byte-Grenze
ist weder erforderlich noch begruendet.

## Belegte kompakte Projektion

Eine `CompactDualProbeBindingReceiptV1`-Aufzeichnung kann auf folgende
unveraenderliche Felder begrenzt werden:

- `schema`;
- `case_plan_digest`;
- `context_retrieval_probe_digest`;
- `masked_signal_probe_digest`;
- `dual_probe_binding_digest`;
- `signal_input_digest`;
- `baseline_input_digest`;
- `source_ledger_digest`;
- `dual_owner_id`;
- `dual_owner_prestate_digest`.

Die vollstaendigen In-Memory-Objekte bleiben bestehen und werden an Signal und
Baseline weitergereicht. Die Projektion ist ausschliesslich eine
Aufzeichnungsform.

Im 96-Zeichen-Worst-Case misst die kanonische Vollhuelle **1.299 Byte**. Die
Reserve zur unveraenderten 2.048-Byte-Grenze betraegt **749 Byte**.

Der Offline-Verifikator kann den vollstaendigen Binding-Preimage aus bereits
aufgezeichneten Quellen rekonstruieren:

- Case-Plan und typisierte Fallrolle aus Registry und Fixture;
- Kontextquelle aus dem zugeordneten Context-Receptor-Receipt;
- Kontext- und Bundledigests aus dem History-Evidence-Pfad;
- Signalquelle und maskierte Probe aus `SIGNAL_PROBE_RECEPTOR` und
  `MASKED_SIGNAL_PROBE_PROJECT`;
- beide Inputdigests aus dem kompakten Receipt;
- der feste Quellenledger aus dem quellhashgebundenen Vertrag.

Der rekonstruierte Bindingdigest muss mit `dual_probe_binding_digest`
uebereinstimmen. Aus diesem Binding, `dual_owner_id`, dem fest gebundenen
Vorzustand `READY` und den vier leeren Terminalfeldern wird der
Owner-Vorzustandsdigest unabhaengig rekonstruiert. Ein Digest ersetzt dabei
keinen fehlenden Elternbeleg.

## Signal- und Baseline-Receipts

Die bestehenden Armprojektionen liegen klar innerhalb ihrer 3.584-Byte-Grenze,
enthalten aber drei Werte nicht, die fuer die unabhaengige Rekonstruktion des
nativen Result- und Receipt-Digests erforderlich sind:

- `invocation_id`;
- `input_digest`;
- `owner_prestate_digest`.

Diese Werte existieren bereits vor dem Armaufruf. Ihre Aufnahme erzeugt keine
neue Provenienz und veraendert kein In-Memory-Ergebnis.

| Fall | Signal aktuell / korrigiert | Baseline aktuell / korrigiert |
| --- | ---: | ---: |
| `c01` | 1.683 / 1.971 | 1.692 / 1.980 |
| `c02` | 1.702 / 1.990 | 1.711 / 1.999 |
| `c03` | 1.702 / 1.990 | 1.711 / 1.999 |
| `c04` | 1.664 / 1.952 | 1.673 / 1.961 |
| `c05` | 1.664 / 1.952 | 1.673 / 1.961 |
| `c06` | 1.641 / 1.929 | 1.650 / 1.938 |
| `c07` | 1.673 / 1.961 | 1.682 / 1.970 |
| `c08` | 1.673 / 1.961 | 1.682 / 1.970 |

Das korrigierte Maximum betraegt 1.999 Byte. Die kleinste Armreserve betraegt
1.585 Byte. Eine Grenzaenderung ist ausgeschlossen.

## Vollstaendige Huellenprognose `ie-op-115` bis `ie-op-170`

Alle Werte verwenden eine 96-Zeichen-Run-ID und, wo vorhanden, eine
96-Zeichen-Invocation- beziehungsweise Owner-ID.

| Fall | Receptor | Masked | Dual aktuell -> kompakt | Signal korrigiert | Baseline korrigiert | Owner | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c01`, `115..121` | 1.195 | 1.650 | 3.552 -> 1.299 | 1.971 | 1.980 | 1.648 | 2.934 |
| `c02`, `122..128` | 1.195 | 1.650 | 3.552 -> 1.299 | 1.990 | 1.999 | 1.648 | 2.930 |
| `c03`, `129..135` | 1.195 | 1.650 | 3.552 -> 1.299 | 1.990 | 1.999 | 1.648 | 2.930 |
| `c04`, `136..142` | 1.197 | 1.650 | 3.552 -> 1.299 | 1.952 | 1.961 | 1.648 | 2.940 |
| `c05`, `143..149` | 1.197 | 1.652 | 3.552 -> 1.299 | 1.952 | 1.961 | 1.648 | 2.940 |
| `c06`, `150..156` | 1.199 | 1.652 | 3.552 -> 1.299 | 1.929 | 1.938 | 1.648 | 2.934 |
| `c07`, `157..163` | 1.195 | 1.650 | 3.552 -> 1.299 | 1.961 | 1.970 | 1.648 | 2.956 |
| `c08`, `164..170` | 1.195 | 1.650 | 3.552 -> 1.299 | 1.961 | 1.970 | 1.648 | 2.956 |

Die kleinsten verbleibenden Reserven in diesem Abschnitt sind 140 Byte fuer
ein Masked-Probe-Receipt und 144 Byte fuer einen Owner-Commit. Beide Formen
sind durch literale IDs, feste Felder und die 96-Zeichen-Obergrenze endlich
materialisiert. Kein weiterer Blocker ist sichtbar.

## Huellen `ie-op-171` bis `ie-op-183`

| Operation | Rolle | Worst Case | Grenze | Reserve |
| --- | --- | ---: | ---: | ---: |
| `171` | Execution evidence | 1.692 | 3.072 | 1.380 |
| `172` | Evaluation binding | 708 | 1.024 | 316 |
| `173` | Evaluation `c01` | 687 | 1.536 | 849 |
| `174` | Evaluation `c02` | 683 | 1.536 | 853 |
| `175` | Evaluation `c03` | 683 | 1.536 | 853 |
| `176` | Evaluation `c04` | 693 | 1.536 | 843 |
| `177` | Evaluation `c05` | 693 | 1.536 | 843 |
| `178` | Evaluation `c06` | 687 | 1.536 | 849 |
| `179` | Evaluation `c07` | 709 | 1.536 | 827 |
| `180` | Evaluation `c08` | 709 | 1.536 | 827 |
| `181` | Aggregate | 1.064 | 1.280 | 216 |
| `182` | Terminal | 630 | 1.024 | 394 |
| `183` | Completion marker | 578 | 1.024 | 446 |

Alle START-/RESULT-Ereignisse von `ie-op-115` bis `ie-op-183` wurden ebenfalls
mit 96-Zeichen-Run-ID vorausberechnet. Das Maximum ist der START-Beleg von
`ie-op-117` mit 1.068 Byte bei einer Grenze von 1.536 Byte. RESULT-Belege
enthalten nur Artefaktdigest und Bytegrenze. Es besteht kein Ereignisblocker.

## ParentSetV1 und Digestgraph

`ParentSetV1` bleibt unveraendert:

- 76 Mehr-Eltern-Operationen;
- 188 kompakte Elternreferenzen;
- maximale Preimage-Grenze 2.816 Byte;
- Eltern werden ausschliesslich aus bereits aufgezeichneten Artefakten
  rekonstruiert;
- Runtime-Invocation- und Owner-IDs sind nicht Teil des Parent-Set-Preimages.

Der korrigierte Graph bleibt vorwaertsgerichtet:

```text
vorhandene History-/Probe-Artefakte
  -> CompactDualProbeBindingReceiptV1
  -> Signal- und Baseline-Receipt
  -> Dual-Owner-Commit
  -> Case-Evidence
  -> Execution-Evidence
  -> getrennte Evaluation
  -> exklusiver Abschluss
```

Der Artefaktdigest des kompakten `ie-op-117`-Receipts bleibt der unmittelbare
Elter fuer Signal und Baseline. Keine Projektion bindet einen eigenen oder
zukuenftigen Digest.

## Ledger und Gesamtbudgets

Die Operations- und Ereigniszahlen bleiben `183/366`. Keine Einzelgrenze wird
geaendert. Daher bleiben die statisch neu addierten Registrybudgets exakt:

```text
Artifact-Grenzsumme       475.290 Byte
Event-Grenzsumme          562.176 Byte
MAX_SUCCESS_PATH_BYTES  1.037.466 Byte
MAX_FAILURE_PATH_BYTES  1.044.634 Byte
```

Die konkrete 96-Zeichen-Prognose fuer die Artefakthuellen `115..183` sinkt
trotz der drei zusaetzlichen Armfelder von 124.984 auf 111.568 Byte. Der
funktionale Quellenledger und alle Memory-/Signal-Operationszaehler bleiben
unveraendert; die kompakte Aufzeichnung verbraucht lediglich weniger vom
bestehenden Dateibudget.

## Entscheidung

S2-IS ist bestanden. Belegt und fuer eine spaeter separat freizugebende
Implementierung geeignet sind ausschliesslich:

1. `CompactDualProbeBindingReceiptV1` fuer die acht Dual-Bindings;
2. Ergaenzung von `invocation_id`, `input_digest` und
   `owner_prestate_digest` in den acht Signal- und acht Baseline-Receipts;
3. entsprechende strikte Offline-Rekonstruktion im Verifikator.

Nicht freigegeben sind Implementierung, Tests, Runnerausfuehrung,
Hauptgeschichten, Validatorlockerung oder Grenzerhoehung. Nach einer separaten
Korrekturimplementierung muss die vollstaendige achtteilige
ID-/Aufrufstellenregression unter neuer Qualifikations-ID einmalig bestanden
werden.

