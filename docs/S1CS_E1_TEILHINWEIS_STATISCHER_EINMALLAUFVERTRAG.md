# S1-CS: E1 Teilhinweis statischer Einmallaufvertrag

## Status

Der spaetere 36er-Teilhinweislauf ist als genau ein Versuch statisch
registriert. S1-CS hat keinen Runner aufgerufen, keine Matrix komponiert,
keine Entscheidung erzeugt und keine Ergebnis- oder Markierungsdatei
angelegt.

## Digestbindung

```text
S1-CS Einmallaufvertrag: 7dbba163fbf9898f4b1a4a13ab54f79338b86d61ba28864882a33127343d040a
S1-CO Cue-Vertrag:       a69eb30b91fb3cb69bb319b8a514be761eb4c2700e3ad720b2042dc7c63a7528
S1-CR Runnerinventar:    e91148ff48e289a7fcf6b3dbe8f8832a25907f496e24bc73fdce5950f0d34925
```

## Einmalpfade

```text
Ergebnis: reports/e1_partial_cue_s1ct_once_v1.json
Versuch:  reports/e1_partial_cue_s1ct_once_v1.attempt.json
Sperre:   reports/e1_partial_cue_s1ct_once_v1.lock
```

Alle drei Pfade muessen vor dem Start fehlen. Der Versuchsnachweis wird
unmittelbar vor dem ersten Callable exklusiv angelegt. Nach einem gestarteten
Fehler bleibt er bestehen und sperrt eine automatische Wiederholung. Nach
vollstaendig erfolgreicher Komposition wird nur das komplette Ergebnis ueber
einen exklusiven Same-Directory-Link atomar sichtbar.

## Ergebnisfelder

```text
execution_id
one_shot_contract_digest
cue_contract_digest
runner_inventory_digest
result_digest
technical_decision
result
```

Der Ergebnisdigest ist SHA-256 ueber kanonisches JSON des reinen
S1-CP-Ergebniscontainers. Die Entscheidung bleibt ausserhalb des Containers
und muss einer der vier bereits in S1-CO registrierten technischen
Entscheidungen entsprechen.

## Technische Abnahme

Sieben fokussierte Vertragstests und 66 relevante Verbundtests bestehen.
Geprueft wurden Pfade, Digests, Feldreihenfolge, Nebenwirkungsfreiheit,
Wiederholungsschutz, private API und die Abwesenheit von Runner-, Kompositor-
und Evaluatorreferenzen in der Vorbereitung.

## Aussagegrenze

S1-CS ist nur ein Ausfuehrungs- und Persistenzvertrag. Es existiert weiterhin
kein vollstaendiger Teilhinweislauf und kein Historyinteraktions-,
Rekonstruktions- oder Memorybefund.

## Bester naechster Schritt

S1-CT implementiert den gebundenen Executor und prueft dessen Erfolgs-,
Fehler- und Wiederholungspfad zuerst vollstaendig synthetisch. Erst nach
erneuter realer Pfad- und Digestpruefung darf er die 36 Callables genau
einmal auswerten, komponieren, extern entscheiden und atomar speichern.
