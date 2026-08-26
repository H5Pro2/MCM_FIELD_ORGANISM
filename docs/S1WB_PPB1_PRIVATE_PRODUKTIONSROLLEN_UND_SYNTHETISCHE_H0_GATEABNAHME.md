# S1-WB: Private PPB-1-Produktionsrollen und synthetische H0-Gateabnahme

## Auftrag und Grenze

S1-WB implementiert ausschliesslich die privaten S1-WA-Ressourcen-, Gate-
und Autorisierungsrollen sowie reine H0-Validatoren mit injizierten
synthetischen Werten.

Nicht Bestandteil sind:

- Betriebssystem-, Speicher- oder Datentraegerabfrage;
- Dateisystem- oder atomarer Replace-Aufruf;
- Produktionsartefakt, Lock oder Terminalobjekt;
- Bindung oder Aufruf des privaten S1-VQ-Producers;
- instanziierbare Produktionsautorisierung;
- Produktionsentry, Matrix-, Feld- oder Medienlauf.

## Implementierte private Rollen

Das Modul
[`_ppb1_s1wb_private_production_h0_types.py`](../mcm_field_organism/_ppb1_s1wb_private_production_h0_types.py)
implementiert:

```text
S1WAProductionResourceObservation
S1WAProductionResourceGate
S1WBAuthorizationCandidate
S1WAProductionAuthorization       (vorhanden, aber hart gesperrt)
S1WBH0CandidateResult
```

Alle Rollen bleiben ausserhalb von Paket-Root, `current_api`, Feldsnapshot
und Medienruntime.

## Injizierte Ressourcenbeobachtung

Die Beobachtung akzeptiert nur typisierte Testwerte und bindet:

- Plattform- und kalibrierte Quellcodedigests;
- freien physischen Speicher und freien Artefaktvolume-Speicher;
- getrennte Artefakt- und Temporaervolume-Identitaeten;
- Same-Volume-, atomaren Replace- und freie-Pfade-Rollen;
- kanonischen Beobachtungsdigest;
- Modus `SYNTHETIC_INJECTED_H0_ONLY`.

Es gibt keinen Import fuer Betriebssystem-, Pfad-, Datentraeger- oder
Prozessmessung. Die Rolle kann daher keine reale H0-Beobachtung erzeugen.

## Deterministisches Ressourcengate

Das reine Gate prueft separat:

```text
freier physischer Speicher >= 2.147.483.648 Bytes
freies Artefaktvolume      >= 1.073.741.824 Bytes
Plattform                  bitgleich zu S1-VZ
Quellcodedigests           bitgleich zu S1-VZ
Artefakt-/Temporaervolume  identisch
Same-Volume-Rolle          wahr
atomarer Replace           wahr
Artefaktpfade              frei
```

Die Grenzwerte sind inklusiv. Speicher und Datentraeger, Plattform und
Quelle sowie Volume, Replace und Pfade besitzen jeweils getrennte
Fail-Closed-Tests.

Fuer die kanonische positive Fixture mit `3 GiB` injiziertem Speicher und
`2 GiB` injiziertem Datentraegerplatz gelten:

```text
Beobachtungsdigest:
bbad80105e915c3c7cb1758a65f9a1bfbec030c1144720016d2c5506a07aad0e

Ressourcengatedigest:
42f87bba351984502d96228f7a85fcdb10f90db5908cd3265646d3a52157bde2
```

## Autorisierungskandidat und harte Sperre

Ein vollstaendig bestandenes synthetisches Gate darf nur einen
`S1WBAuthorizationCandidate` erzeugen. Dieser traegt ausdruecklich:

```text
mode = SYNTHETIC_CANDIDATE_NOT_AUTHORIZATION
authorization_instantiation_enabled = false
```

Sein Text entspricht der S1-WA-Vorlage fuer synthetische Ausfuehrungs-IDs,
ist aber kein Autorisierungsobjekt und kann keinen Entry oeffnen.

Der vertraglich vorgesehene Typ `S1WAProductionAuthorization` besitzt alle
gebundenen Felder, verweigert jedoch jede Instanziierung mit
`S1WB_PRODUCTION_AUTHORIZATION_BLOCKED`. Auch der Produktionsentry ist
bedingungslos gesperrt.

## Synthetischer H0-Befund

Die positive Fixture besteht H0A, H0B, H0C und H0E. Exakt H0D bleibt falsch:

```text
H0A_CONTRACT_PLAN_PLATFORM_SOURCE                 PASS
H0B_SAME_VOLUME_ATOMIC_REPLACE                    PASS
H0C_MEMORY_DISK_RESOURCE_GATE                     PASS
H0D_PRODUCTION_AUTHORIZATION_INSTANTIABLE         FAIL
H0E_ARTIFACT_PATHS_FREE                           PASS
```

Entscheidung:

```text
BLOCKED_PRODUCTION_AUTHORIZATION_AND_PRODUCER_BINDING
```

Der H0-Kandidat meldet `producer_call_count = 0`,
`production_artifact_count = 0` und `ready_for_h1 = false`.

Kanonische Kandidatendigests:

```text
Autorisierungskandidat:
55a04e8510a82f2f3d9ea945b432cffb9364603aeb13b29d81314c3fc6ae457f

H0-Kandidatenresultat:
cbb4b70ee56a013af1efc327d49528c10fd089f4d60608338837bcd6716412a6
```

## Tests

`12 von 12` neue Tests pruefen Vertrag, Digests, inklusive Grenzwerte,
getrennte Drift- und Ressourcenrollen, Autorisierungssperre, H0-Stopp sowie
API-, Snapshot-, Dateisystem- und Runnergrenzen. Zusammen mit dem
fokussierten Bestand bestehen `186 von 186` Tests.

## Entscheidung

```text
S1_WB_PRIVATE_INJECTED_RESOURCE_OBSERVATION_IMPLEMENTED
S1_WB_DETERMINISTIC_PRODUCTION_RESOURCE_GATE_IMPLEMENTED
S1_WB_MEMORY_DISK_PLATFORM_SOURCE_VOLUME_AND_PATH_GATES_TESTED
S1_WB_AUTHORIZATION_CANDIDATE_EXPLICITLY_NON_AUTHORIZING
S1_WB_PRODUCTION_AUTHORIZATION_TYPE_PRESENT_BUT_HARD_BLOCKED
S1_WB_POSITIVE_SYNTHETIC_H0_STOPS_ONLY_AT_H0D
S1_WB_ZERO_RESOURCE_PROBES_EXECUTED
S1_WB_ZERO_PRODUCER_CALLS_AND_PRODUCTION_ARTIFACTS
S1_WB_PRODUCTION_ENTRYPOINT_HARD_BLOCKED
S1_WB_12_OF_12_NEW_TESTS_PASS
S1_WB_186_OF_186_COMBINED_FOCUSED_TESTS_PASS
```

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-WC - statischer Post-Implementierungs-Preflight der Produktionsrollen
```

S1-WC darf nur Quelltext, Typen, Vertrags- und Kalibrierungsdigests sowie
die noch offenen Produktionsrollen pruefen. Es darf keine Ressource
abfragen, keine Autorisierung instanziieren, keinen Producer binden oder
aufrufen und kein Artefakt erzeugen. Erst der Audit darf festlegen, welcher
einzelne Implementierungsschritt danach methodisch zulaessig ist.

## Grundlagen

- [S1-WA Produktionsbindungs- und Autorisierungsvertrag](S1WA_PPB1_STATISCHER_PRODUKTIONSBINDUNGS_RESSOURCEN_UND_AUTORISIERUNGSVERTRAG.md)
- [S1-VZ synthetische Ressourcenkalibrierung](S1VZ_PPB1_PRIVATE_SYNTHETISCHE_RESSOURCENKALIBRIERUNG_UND_GATEABNAHME.md)
- [S1-VW synthetische Einmallaufhuelle](S1VW_PPB1_PRIVATE_SYNTHETISCHE_EINMALLAUF_HANDOFF_UND_TERMINALHUELLEN_ABNAHME.md)
