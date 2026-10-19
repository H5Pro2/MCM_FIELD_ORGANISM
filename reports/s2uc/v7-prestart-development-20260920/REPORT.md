# V7-Inventar und Vorstartvalidierung: Entwicklungsabschluss

Umgesetzt im freigegebenen Paket. Der echte Starter bleibt auch nach vollstaendig passender V7-Vorpruefung geschlossen. Keine Defaultumschaltung, finale Hauptlaufbindung, Quellenproduktion, reale Ausfuehrung oder neue formale Qualifikation. Historische Belege, wissenschaftliche Grenzen und Workflow unveraendert. Unabhaengige Abnahme bleibt offen.

## Umsetzung

- `_s2uc_inventory_v7.py`: feste Vereinigung von Starter und allen fuenf gebundenen Testsuiten, einschliesslich S2-UB, transitiver/verzoegerter/literaler dynamischer Importe, Paketinitialisierer und registrierter Lazy-Exports. Groessen und SHA256 stammen aus Dateien. Kanonische Schreibweise, fehlende Module und Datei-Aliase werden geprueft.
- `_s2uc_prestart_v7.py`: eigenes Format `s2uc.prestart-binding.v7`, fester Ressourcenvertrag, fest zugeordnete Pflichtbelege und Teilobergrenzen. Unbekannte Rollen, Zusatzdateien, Resultatplatzhalter und V6/V7-Mischungen scheitern. NU-Plan und Ressourcenvertrag zaehlen mit.
- `_s2uc_run_binding.py`: getrennte V7-Pruefung mit anschliessendem bedingungslosem Stopp, ohne Rueckgabe in den V6-Publikationspfad.
- `s2uc_run_bound_once.py`: Gate vor autorisierter Vorpruefung schliessen. Defaultbindung unveraendert.
- `test_s2uc_prestart_v7.py`: 16 neue neutrale Integrationstests. Der synthetische Bindungswriter existiert ausschliesslich im Testmodul.

## Geaenderte Dateien und SHA256

| Datei | Byte | SHA256 nach Aenderung |
|---|---:|---|
| `tests/test_s2uc_prestart_v7.py` | 17571 | `d0daf7d33e5cfe3fd9a8ec090724282ac82990c14d5854ea9cfb554b543feaf9` |
| `tools/_s2uc_inventory_v7.py` | 8841 | `1cfcdfc64e4db353584a4a5a8c9b9aeee58499958ffc0cbb039fce405ddef1ce` |
| `tools/_s2uc_prestart_v7.py` | 9367 | `3615ce07c10912e2c0c044e4c50eaaaa2c7851c511a5ac2436f77bb4c93a41e0` |
| `tools/_s2uc_run_binding.py` | 34951 | `138cc9b15589c38dc16e3be670503850cd593fc2d5191414ff589fcabe46d33c` |
| `tools/s2uc_run_bound_once.py` | 1309 | `25210fb3f76b632842abbf4b387fd7f89c78209d60e97a291c597aa408ee123f` |

Vorher-/Nachherwerte: [changed-files.json](changed-files.json). Vollstaendige Ausgangs-/Endhashes der erfassten Projektquellen: [before.json](before.json), [after.json](after.json). Andere erfasste Projektquellen unveraendert, insbesondere alte Ledger und beide bisherigen S2-UC-Suiten.

## Testbeleg

**98/98 bestanden, Exitcode 0.** Keine uebersprungenen Tests.

| Suite | Tests |
|---|---:|
| `test_s2ub_candidate_confirmation` | 11 |
| `test_s2uc_materialization_connection` | 46 |
| `test_s2uc_neutral_connection` | 11 |
| `test_s2uc_prestart_v7` | 16 |
| `test_s2uc_resource_contract_v7` | 14 |

Vollstaendige konkrete Test-IDs, Einzelergebnisse, Befehl und Codehashbindung: [test-result.json](test-result.json). Vollstaendige Ausgaben: [tests.stderr.txt](tests.stderr.txt), [tests.stdout.txt](tests.stdout.txt). Die Dateien mit `intermediate-` dokumentieren den vorherigen erfolgreichen Entwicklungsstand und sind nicht der Endnachweis.

Gegenproben umfassen unter anderem fehlende transitive Testdateien trotz neu berechneter Inventar-/Belegdigests, physisch verschwundene Module bei normalen und dynamischen Importen, geaenderte Hashes und Dateien, konsistente Unterzaehlung, falsche Kategorien, doppelte/fehlende/unbekannte Posten, unkanonische Pfade und Hardlinks, externe Laufzeitmanipulation, statische Teilbudgets, gemeinsames Metadatenbudget, echte Codegrenze und Grenze+1 sowie Vermischung von Istwerten/Reserven und V6/V7.

## Vollstaendige Inventar- und Budgetzuordnung

**38 Projektdateien, 621439 / 655360 Byte; Rest 33921 Byte.** Die Vereinigung und alle Dateihashes stehen in [dependency-inventory.json](dependency-inventory.json). Die zusaetzlich vorhandene S2-UB-Testsuite ist ausdruecklich mitgezaehlt und ebenfalls ausgefuehrt.

Externe Identitaeten sind separat gebunden: Interpreterpfad, Executable-Hash, Version, Implementierung, Cachekennung und Plattform; Modulversionen; fuer NumPy ein neu berechneter Hash ueber die tatsaechlichen registrierten Installationsdateien ohne generierte `.pyc`-Caches. Diese Installationsbytes sind ausserhalb der Projektcodegrenze, nicht Null. Dies versiegelt nicht die gesamte Hostumgebung und ist keine Prozessspeichergrenze.

Die folgende Istmessung stammt aus einer **synthetischen, temporaeren Vorstart-Beleghuelle**. Sie belegt die technische Zuordnung und wurde nach der Pruefung entfernt. Sie ist keine neue Hauptlaufbindung oder Qualifikation. Vollstaendige Referenzen, Groessen, Hashes und Abschlussreservierungen: [prestart-measurement-synthetic.json](prestart-measurement-synthetic.json).

| Pflichtbeleg | Namespace / fester Pfad | Konto | Istbyte | Teilgrenze |
|---|---|---|---:|---:|
| manifest | `bundle:manifest.json` | metadata | 24546 | 65536 |
| nu_plan | `project:reports/s2nu/s2nu-source-preseal-20260909-01/execution-plan.json` | static_shared | 44937 | 65536 |
| source_binding | `bundle:source-binding.json` | static_shared | 19210 | 24576 |
| inventory | `bundle:dependency-inventory.json` | static_shared | 7969 | 16384 |
| qualification_summary | `bundle:qualification-summary.json` | static_shared | 285 | 16384 |
| qualification_protocol | `bundle:qualification-protocol.json` | static_shared | 13353 | 32768 |
| qualification_budget | `bundle:qualification-budget.json` | static_shared | 266 | 8192 |
| qualification_result | `bundle:qualification-result.json` | static_shared | 291 | 4096 |
| resource_ledger | `bundle:resource-ledger.json` | static_shared | 3545 | 8192 |
| resource_contract | `bundle:resource-contract.json` | static_shared | 2082 | 8192 |
| Vorstartbindung | `bundle:prestart-binding.json` | metadata | 2105 | gemeinsames M-Limit |

Feste Zuordnungen und Grenzen: [resource-contract.json](resource-contract.json). Die Belegdatei wird gegen die implementierte Vertragsdefinition geprueft; Angaben einer Bindungsdatei koennen weder Rollen noch Grenzen ersetzen.

| Konto | Istbyte | Grenze |
|---|---:|---:|
| code | 621439 | 655360 |
| metadata | 26651 | 65536 |
| static_shared | 91938 | 196608 |
| record | 0 | 262144 |
| verification | 0 | 262144 |
| error | 0 | 16384 |
| terminal | 0 | 16384 |
| minimal | 0 | 16384 |
| staging | 0 | 245760 |
| shared = B + E + T + Tmin | 91938 | 262144 |
| Gesamt, ohne Doppelzaehlung | 740028 | 4194304 |

Vorstart-Istwerte fuer Record, Verifikation, Fehler, Terminal, Minimalabschluss und Staging sind null, weil diese Dateien fehlen; es werden keine leeren Platzhalter erzeugt. Das Ergebnisinventar ist getrennt und leer. Die folgenden Werte sind **Reservierungen**, einschliesslich voller Stagingreserve und gleichzeitig vorhandener Fehler-/Abschlussbelege:

| Alternative | Gesamtbyte |
|---|---:|
| success | 1379004 |
| failure_before_publication | 1018556 |
| failure_after_publication | 1395388 |
| minimal_with_terminal | 1411772 |

## Nachgewiesener Ausfuehrungsstopp

[`starter-stop.json`](starter-stop.json) protokolliert einen strukturell gueltigen synthetischen V7-Beleg am echten Starter:

```text
V7_EXECUTION_NOT_CONNECTED: V7-Ausführung noch nicht angebunden
Supplier=0; Adapter=0; Laufeinstieg=0
Gate offen=False; USED=False; Ergebnisablage vorhanden=False
```

Es gibt keinen Rueckfall von V7 in V6. Ein positives isoliertes Validierungsergebnis enthaelt ausdruecklich `execution_authorized=false`. Die Pruefung bindet Entwicklungsbelege, behauptet aber keine unabhaengige oder formale Qualifikation. Dateiidentitaeten werden vor und nach Einzeldateilesungen verglichen; ein atomarer Snapshot aller Projekt-/Installationsdateien bei konkurrierenden Aenderungen ist damit nicht nachgewiesen. Vor einer spaeteren Ausfuehrung waere der dann aktuelle Stand erneut zu binden.

## Naechster vorgeschlagener Schritt

Nach Abnahme dieses Pakets die V7-Publikation mit getrenntem Verifikationsbeleg und vollstaendiger Fehler-/Stagingbilanz neutral entwickeln. Die bestehende V7-Ausfuehrungssperre dabei zunaechst beibehalten. Eine Hauptlaufbindung oder reale Quellenfreigabe folgt daraus nicht.
