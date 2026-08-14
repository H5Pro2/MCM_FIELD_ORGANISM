# S1-CX: E1 Cue-Amplituden statischer Einmallaufvertrag

## Status

Die spaetere 72er-Amplitudenkurve ist als genau ein Versuch statisch
registriert. Kein Runner, Kompositor oder Evaluator wurde aufgerufen und
keine Ziel- oder Markierungsdatei angelegt.

## Digestbindung

```text
S1-CX Einmallaufvertrag: ac9ff73915423bde98f9f25e93c540e0345ae236d1d1430f9d9fef0dd81b177f
S1-CU Kurvenvertrag:     88e56327c18c2c39244befff17747e99dbf0110e68a5ecb99c32cb63c625cbe0
S1-CW Runnerinventar:    d3a40cbf9e76bffb6ccab1a1a2a3facedef8ad8af7f0f2198bc876e7ef276cd9
```

## Einmalpfade

```text
Ergebnis: reports/e1_cue_amplitude_s1cy_once_v1.json
Versuch:  reports/e1_cue_amplitude_s1cy_once_v1.attempt.json
Sperre:   reports/e1_cue_amplitude_s1cy_once_v1.lock
```

Vor dem Start muessen alle Pfade fehlen. Der Versuchsnachweis wird direkt
vor dem ersten Callable exklusiv angelegt. Nach einem gestarteten Fehler
bleibt er bestehen. Ein vollstaendiges Ergebnis wird erst nach allen 72
Beobachtungen, Komposition und externer Entscheidung atomar veroeffentlicht.

## Ergebnisfelder

```text
execution_id
one_shot_contract_digest
curve_contract_digest
runner_inventory_digest
result_digest
technical_decision
result
```

Der Ergebnisdigest ist SHA-256 ueber kanonisches JSON des reinen
S1-CV-Ergebniscontainers. Die Entscheidung bleibt ausserhalb des Containers.

## Technische Abnahme

Sieben fokussierte Vertragstests und 98 relevante Verbundtests bestehen.
Pfade, Digests, Entscheidungsliste, Nebenwirkungsfreiheit,
Wiederholungsschutz und private API sind statisch geprueft.

## Aussagegrenze

S1-CX ist nur ein Ausfuehrungs- und Persistenzvertrag. Es existiert noch
kein realer Amplitudenkurvenbefund.

## Bester naechster Schritt

S1-CY implementiert den Executor und prueft Erfolg, gestarteten Fehler,
Digestabweichung und Wiederholung zuerst synthetisch. Erst nach sauberer
finaler Vorpruefung darf die 72er-Matrix genau einmal real ausgefuehrt
werden.
