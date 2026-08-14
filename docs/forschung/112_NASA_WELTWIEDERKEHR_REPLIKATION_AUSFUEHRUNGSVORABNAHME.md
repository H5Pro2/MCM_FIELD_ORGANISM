# NASA-Weltwiederkehr: Replikations-Ausfuehrungsvorabnahme

## Entscheidung

Die technische Vorabnahme fuer genau einen begrenzten sechsarmigen NASA-Weltwiederkehr-Replikationslauf ist als separates Gate umgesetzt.

Die Vorabnahme startet keinen Replikationslauf. Sie decodiert kein Medium, speist keine Rezeptoren und fuehrt keinen Feldlauf aus.

## Gepruefte Bindungen

- Quellenvertrag und lokale Dateiintegritaet.
- Vorregistrierungsidentitaet `public.av.nasa-earthrise.return-replication.v1`.
- Kompatibilitaetsaudit `public.av.nasa-earthrise.return-replication.compatibility.v2`.
- Runnerverdrahtung `public.av.nasa-earthrise.return-replication.runner.wiring.v1`.
- Permutationsvertrag `public.av.nasa-earthrise.return-replication.permutation-contract.v1`.
- Vollstaendigkeit aller sechs Arme.
- Feste Intervalle:
  - Stufe eins `[0, 500000000)`.
  - Aufloesungsphase `[500000000, 600000000)`.
  - Stufe zwei `[600000000, 1100000000)`.
- Unveraenderte Feldparameterrollen.
- Weiter bestehende Run-Sperre im Runner und im Kompatibilitaetsaudit.

## Freigabegrenze

```text
arm_count:                                      6
arm_ids_complete:                              true
all_arms_wired:                                true
all_arms_structurally_supported:               true
fixed_field_parameters_match_preregistration:  true
runner_wiring_non_executable:                  true
runner_run_lock_engaged:                       true
compatibility_run_lock_engaged:                true
media_decode_allowed:                          false
receptor_feed_allowed:                         false
single_bounded_replication_run_release_granted: true
repeat_count_authorized:                       1
field_run_started:                             false
```

Die positive Vorabnahme erlaubt nur einem nachfolgenden Ausfuehrungspfad, genau einen begrenzten sechsarmigen Replikationslauf zu starten, sofern alle Gate-Bedingungen unveraendert bleiben.

## Claim-Grenze

Die Vorabnahme definiert keine Memory-, Bedeutungs- oder Organisationsschwelle. Sie erlaubt keine Memory-, Bedeutungs-, Organisations- oder KI-Claims.
