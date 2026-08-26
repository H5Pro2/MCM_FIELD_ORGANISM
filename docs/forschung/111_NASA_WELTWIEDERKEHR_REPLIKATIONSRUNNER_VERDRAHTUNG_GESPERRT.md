# NASA-Weltwiederkehr: sechsarmige Runner-Verdrahtung (gesperrt)

## Gegenstand

Der sechsarmige Replikationsplan ist als nicht ausführbarer Runnervertrag verdrahtet. Diese Arbeit implementiert keine Medien-Decodierung, keine Rezeptorspeisung und keinen Feldlauf.

## Verdrahtete Arme

| Arm | Laufzeitpfad | Eingriff in Stufe zwei |
|---|---|---|
| `return.continued.full_state` | `two_stage_return.full_state_carry` | vollständiger Feldzustand |
| `return.fresh_stage_two` | `two_stage_return.fresh_stage_two` | frisches Feld |
| `control.activation_only_carry` | `component_intervention.reset_afterimage_preserve_activation` | observerseitige Komponentenintervention |
| `control.afterimage_only_carry` | `component_intervention.reset_activation_preserve_afterimage` | observerseitige Komponentenintervention |
| `control.stage_two_order_permuted` | `permutation_contract.reverse_rank_stage_two` | vollständig spezifizierte Rangumkehr |
| `control.stage_two_sequence_withheld` | `contact_free_field_step.stage_two_horizon` | keine Stufe-zwei-Rezeptorkontakte |

Für alle Arme bleiben die Intervalle `[0, 500000000)`, `[500000000, 600000000)` und `[600000000, 1100000000)` sowie Feldparameter und Messrollen unverändert.

## Konstruktive Sperre

`execute_public_av_return_replication_runner` bricht immer mit einer Freigabefehlermeldung ab. Der Vertrag setzt `executable`, `replication_run_allowed`, `media_decode_allowed` und `receptor_feed_allowed` auf `false`. Memory-, Bedeutungs-, Organisations- und KI-Claims sowie entsprechende Schwellen bleiben ausgeschlossen.

## Aussagegrenze

Die Verdrahtung weist nur strukturelle Darstellbarkeit nach. Sie enthält keinen empirischen Replikationsbefund und keine Aussage über Memory, Bedeutung, Organisation oder KI.
