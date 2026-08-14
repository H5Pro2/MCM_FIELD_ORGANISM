# W7-BQ: Anschlussvertrag fuer die transparente F3-Baseline

Stand: 2026-08-10

Status: `ENGINEERING_VERTRAG_KEIN_MEMORYBEFUND`

## Zweck

Dieser Vertrag beschreibt den naechsten technischen Anschluss der aktiven
kontrollierten Testwelt an die bereits vorhandene F3-Referenz. Er fuehrt
keine neue Substratnatur und keine Memory-Implementierung ein.

## Zulaessiger Pfad

```text
kontrollierte Video-/Audio-/Browser-Testwelt
-> Rezeptorfolge
-> gemeinsames MCM-Feld
-> optionaler F3-Referenzarm
-> Snapshot / Restore
-> passive technische Auswertung
```

Der F3-Arm bleibt ein Vergleichsmechanismus. Eine geschichtsabhaengige
Feldreaktion darf nur als technische Zustandsdifferenz bezeichnet werden.

## Verbindliche API-Grenze

Der Anschluss verwendet den kuratierten Einstiegspunkt
`mcm_field_organism.current_api`.

Zulaessige Referenzexports sind ausschliesslich die dort als
`F3_REFERENCE_EXPORTS` gebundenen Funktionen und Datentypen:

- `build_uniform_mcm_substrate` und `attach_uniform_mcm_substrate`;
- `compute_mcm_f3_coupling`;
- `activate_mcm_f3_field`;
- `advance_mcm_f3_shared_field`;
- `advance_mcm_f3_shared_field_transient`.

Historische Root-Exports, Live-Adapter und geparkte Memorykandidaten werden
nicht in diesen Anschluss importiert.

## Zulassige technische Fragen

Der Anschluss darf ausschliesslich pruefen:

1. ob identische Rezeptorfolgen identische F3-Snapshots erzeugen;
2. ob Snapshot und Restore bitgenau fortsetzbar sind;
3. ob unterschiedliche kontrollierte Vorgeschichten technisch
   unterscheidbar bleiben;
4. ob die spaetere Feldbahn durch den F3-Zustand beeinflusst wird;
5. ob diese Wirkung durch die festgelegten linearen und leaky Baselines
   erklaert wird.

Diese Fragen sind technische Kausal- und Reproduzierbarkeitsfragen. Sie sind
kein Nachweis von Lernen, Praegung, Vergessen, Feldzeit oder Memory.

## Gegenbaselines

Jede spaetere Auswertung muss mindestens benennen:

- den schnellen Nullpfad;
- die lineare beziehungsweise leaky Referenz;
- eine gleich budgetierte unabhaengige lokale Spur;
- den F3-Referenzarm;
- eine Snapshot-/Restore-Kontrolle.

Ein Unterschied zum Nullpfad ist allein kein positiver Substratbefund.

## Gesperrte Erweiterungen

Dieser Vertrag erlaubt nicht:

- neue langsame Variablen;
- Episoden-, Cluster- oder Label-Speicher;
- externe Speicherkommandos;
- Reward, Zielregeln oder Bedeutungszuweisung;
- adaptive Topologie oder neue Kanten;
- kamerabasierte oder physische Sensorik;
- einen Memory- oder KI-Claim.

## Entscheidung

```text
F3 als technische Baseline:       zulaessig
neue Substratnatur:               nicht hergeleitet
Memory-Lebenszyklus:              nicht geprueft
Forschungslauf:                   nein
Runtime-Erweiterung:              nein
```

## Bester naechster Schritt

Vor jedem Lauf wird ein einzelner kontrollierter Baseline-Vertrag mit festen
Rezeptorfolgen, Snapshot-Punkten, Gegenbaselines und Abbruchkriterien
festgelegt. Erst nach dieser statischen Bindung darf ein technischer Lauf
beauftragt werden.
