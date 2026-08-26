# W7-AU: Statischer Bestands- und Anschlussaudit der W7-L-Baselines

## Entscheidung

`W7AU_ALL_EQUATIONS_EXIST_NO_TERMINAL_BASELINE_RESULT_CONNECTED`

Auditdigest:

```text
d4093b1109dfd563bdd7e1c2d3359d09fddab3707d3501d301ed25078a3adaa1
```

W7-AU ist ein statischer Code- und Vertragsaudit. Es wurden keine
Ergebniswerte gelesen, keine Integration ausgefuehrt und kein Reportlauf
gestartet.

## Zentrale Korrektur

Die bisherige Kurzform, im W7-AT-Container fehlten zehn Baselines, war
missverstaendlich. Korrekt ist:

- alle zehn Baselinegleichungen oder Interventionsmechaniken existieren;
- alle zehn sind bereits durch W7-M registriert und parametrisch gebunden;
- im terminalen W7-AT-Ergebnis fehlen ihre einheitlich materialisierten und
  digestgebundenen Vergleichsergebnisse;
- deshalb ist derzeit keine der zehn Baselines terminal W7-AT-vergleichbar.

## Inventar

| Baseline | Vorhandener Provider | Aktueller Stand | Fehlende Grenze |
| --- | --- | --- | --- |
| LEAK | `w7n.advance_w7n_local_baseline` | sieben Pfade in W7-AC materialisiert | W7-AC-Ergebnis und Lifecycleprofil terminal binden |
| SAT | `w7n.advance_w7n_local_baseline` | sieben Pfade in W7-AC materialisiert | W7-AC-Ergebnis und Lifecycleprofil terminal binden |
| NORM | `w7n.advance_w7n_local_baseline` | sieben Pfade in W7-AC materialisiert | W7-AC-Ergebnis und Lifecycleprofil terminal binden |
| LIN | `w7n.compute_w7n_coupling_baseline` | lokale Ableitung implementiert | R1/R2/R4-Siebenpfad-Trajektorienverbraucher |
| F3 | `w7n.compute_w7n_coupling_baseline` | lokale Ableitung implementiert | R1/R2/R4-Siebenpfad-Trajektorienverbraucher |
| CONST-V | `w7n.compute_w7n_coupling_baseline` | lokale Ableitung implementiert | R1/R2/R4-Siebenpfad-Trajektorienverbraucher zuerst |
| MOB | `w7n.compute_w7n_coupling_baseline` | lokale Ableitung implementiert | R1/R2/R4-Siebenpfad-Trajektorienverbraucher |
| ETA0 | `w7m.ablate_w7m_eta` | Interventionskonstruktor implementiert | parametrisierter CAP-Trajektorienverbraucher |
| KAPPA0 | `w7m.ablate_w7m_kappa` | Interventionskonstruktor implementiert | parametrisierter CAP-Trajektorienverbraucher |
| SIGN | `w7m.invert_w7m_kappa` | Interventionskonstruktor implementiert | parametrisierter CAP-Trajektorienverbraucher |

## Gruppe 1: vorhandene Observermaterialisierung

LEAK, SAT und NORM sind technisch am weitesten. W7-AC erzeugt bereits fuer
alle sieben Pfade je drei getrennte Modellketten, insgesamt 21 Hauptketten
und 105 gleichpfadige Probeaeste. Die Modelle lesen denselben abgeschlossenen
P0-S-Treiber und veraendern weder P0 noch CAP.

Diese Ergebnisse koennen ohne neue Feldintegration wiederverwendet werden.
Sie sind aber im W7-AS-Terminalobjekt nicht enthalten und wurden noch nicht
mit dem W7-AT-Numerikboden in gebundene Lifecycleprofile ueberfuehrt.

## Gruppe 2: lokale Kopplungsableitungen

LIN, F3, CONST-V und MOB besitzen in W7-N gepruefte lokale
Kopplungsableitungen. W7-P kennt ihre Feldmessrollen. Es fehlt jedoch ein
Verbraucher, der jede Gleichung mit denselben sieben Quellenpfaden,
Checkpointproben, R1/R2/R4-Aufloesungen, Gegenlaeufen und Integrationszeugen
wie CAP zu vollstaendigen Trajektorien materialisiert.

CONST-V bleibt gemaess W7-L die primaere enge Feldbaseline. Sie startet am
homogenen Zustand mit derselben Rate wie CAP und trennt zielseitige freie
Kapazitaet von einer bloss konstant halbierten F3-Rate. Ihre Priorisierung
erlaubt noch keine Funktionsentscheidung ohne die weiteren Baselines.

## Gruppe 3: CAP-Interventionen

ETA0, KAPPA0 und SIGN koennen bereits aus einem gebundenen CAP-Feld erzeugt
werden. Die Konstruktoren bewahren Geometrie, Masse und
Fortsetzungsbindung. W7-AE akzeptiert derzeit aber ausschliesslich den
kanonischen CAP-Arm mit `eta=1`, `kappa=0.5` und `lambda_sm=1`. Daher fehlen
separate siebenpfadige Interventionsverlaeufe und Probeausgaben.

## Evidenzgrenze

```text
equation_implementation_count = 10
terminally_comparable_count = 0
field_function_decision_allowed = false
memory_claim_allowed = false
```

W7-AU veraendert den positiven W7-AT-Numerikbefund nicht. Es zeigt nur, dass
der naechste Engpass Integration und Ergebnisbindung ist, nicht die Erfindung
weiterer Mechaniken.

## Verwendete Projektquellen

- `mcm_field_organism/w7m_capacity_function_matrix.py`
- `mcm_field_organism/w7n_capacity_function_baselines.py`
- `mcm_field_organism/w7p_measurement_compositor.py`
- `mcm_field_organism/w7t_observer_continuation.py`
- `mcm_field_organism/w7ac_observer_seven_path_consumer.py`
- `mcm_field_organism/w7ae_cap_seven_path_consumer.py`
- `mcm_field_organism/w7an_r124_resolution_container.py`

## Naechster Schritt

W7-AV sollte zuerst einen privaten, rein additiven Ergebnisbinder fuer die
bereits vorhandenen LEAK-/SAT-/NORM-Siebenpfadverlaeufe und den gebundenen
W7-AT-Numerikboden implementieren. Dafuer ist keine neue Feldintegration
noetig. Danach muss ein gemeinsamer statischer R1/R2/R4-
Feldtrajektorienvertrag fuer CONST-V, LIN, F3 und MOB folgen.
