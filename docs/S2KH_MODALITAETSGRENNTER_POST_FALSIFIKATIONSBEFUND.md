# S2-KH - Modalitaetsgetrennter Post-Falsifikationsbefund

## Status und Grundlage

`S2KH_STATIC_MODALITY_SEPARATED_POST_FALSIFICATION_FINDING_COMPLETE`

S2-KH ist eine rein statische Auswertung des unveraenderten Primaerbelegs
`reports/s2kg/s2kg-auditory-holdout-20260903-01/result.json` mit
Record-Digest:

```text
5035530fa5a89a071f8ded35904ba372a8c23fbeb4cbe6d5823892b6cc076554
```

Der formale Gesamtstatus bleibt dauerhaft:

```text
S2KC_AUDITORY_HOLDOUT_GENERALIZATION_FALSIFIED
```

S2-KH aendert weder diesen Status noch Ergebnisdatei, Fixture, Schwelle,
Memoryzustand oder Auswertungsregel. Es findet keine Wiederholung statt.

## Bereichs- und Modalitaetsrollen

Die Befunde werden fortan fuer diese Untersuchung getrennt bezeichnet:

```text
A_RECENT_AV
  gemeinsame audiovisuelle B4-/Fast-Sicht
  auditive und visuelle Fast-Schwelle jeweils 0,2

B_STABLE_AUDITORY
  stabilisierte auditive PPB-1-Sicht
  auditive Slow-Schwelle 0,02

B_STABLE_VISUAL
  stabilisierte visuelle PPB-1-Sicht
  getrennte visuelle Slow-Entscheidung
```

`A_RECENT_AV` ist keine rein auditive Entscheidung. Eine Auswahl dort darf
nicht als auditiver Slow-Treffer und ihre Abwesenheit nicht als vollstaendige
Kontextabwesenheit ausgegeben werden.

## Begriffe

`AUDITORY_NO_MATCH` bedeutet in S2-KH ausschliesslich: Fuer die benannte
Probe existiert in `B_STABLE_AUDITORY` kein gueltiger auditiver Slow-Treffer.
Der Status macht keine Aussage ueber `A_RECENT_AV` oder
`B_STABLE_VISUAL`.

`NO_CONTEXT` waere nur zulaessig, wenn in keiner der drei benannten Rollen
ein gueltiger Kontextbefund vorhanden ist. Aus `AUDITORY_NO_MATCH` folgt
daher niemals automatisch `NO_CONTEXT`.

## Rekonstruktion der Checkpoints

| Checkpoint | Probe | A_RECENT_AV | B_STABLE_AUDITORY | B_STABLE_VISUAL |
| --- | --- | --- | --- | --- |
| C0 | H_AUDIO | absent | absent | absent |
| C0 | N_AUDIO | absent | absent | absent |
| C1 | H_AUDIO | B4 und Fast | absent | absent |
| C1 | N_AUDIO | B4 und Fast | absent | absent |
| C2 | H_AUDIO | B4 und Fast | stabil, Support 3 | stabil, Support 3 |
| C2 | N_AUDIO | B4 und Fast | absent | stabil, Support 3 |
| C3 | H_AUDIO | absent | stabil, Support 3 | stabil, Support 3 |
| C3 | N_AUDIO | absent | absent | stabil, Support 3 |

Die C1-/C2-Auswahl von `N_AUDIO` in B4 und Fast ist mechanisch zulaessig.
Ihre auditiven Distanzen `0.03023999967450985` beziehungsweise
`0.020639999975482805` liegen oberhalb der Slow-Schwelle `0,02`, aber
unterhalb der Fast-Schwelle `0,2`. Der visuelle Abstand ist jeweils `0,0`.

Die falsifizierte Auswerterannahme setzte dadurch unzulaessig
`AUDITORY_NO_SLOW_MATCH` mit `NO_AV_MEMORY_MATCH` gleich. Diese
Fehlgleichsetzung bleibt Bestandteil des gueltigen S2-KG-Ergebnisses und
wird nicht nachtraeglich repariert.

## Finaler modalitaetsgetrennter Befund

### H_AUDIO

Am finalen Checkpoint C3 gilt:

```text
A_RECENT_AV:       absent
B_STABLE_AUDITORY: stabil, Support 3, Distanz 0.018096882417946113
B_STABLE_VISUAL:   stabil, Support 3, Distanz 0.0
```

`H_AUDIO` ist damit final bimodal stabil. Der auditive Befund beruht nicht
auf einem trainierten Holdout: `H_AUDIO` kam in keinem Trainingspfad vor,
Frozen und Replay lehnten es ab, und ausschliesslich der adaptive auditive
Prototyp nahm es an.

### N_AUDIO

Am finalen Checkpoint C3 gilt:

```text
A_RECENT_AV:       absent
B_STABLE_AUDITORY: AUDITORY_NO_MATCH
B_STABLE_VISUAL:   stabil, Support 3, Distanz 0.0
```

Der korrekte zusammenfassende Status lautet:

```text
VISUAL_STABLE_ONLY
```

Er ist weder `NO_CONTEXT` noch ein auditiver Treffer. Frozen, Replay und
adaptiver auditiver Prototyp lehnten `N_AUDIO` ebenfalls ab.

## Komponentenbefund

Folgender enger Teilbefund ist durch S2-KG bestaetigt:

```text
S2KG_ADAPTIVE_AUDITORY_HOLDOUT_COMPONENT_CONFIRMED
```

Er bindet ausschliesslich:

- `H_AUDIO` war nie Trainingsinput;
- Frozen und Replay wiesen `H_AUDIO` ab;
- der adaptive auditive Prototyp nahm `H_AUDIO` an;
- nach Verlust aus `A_RECENT_AV` blieb `H_AUDIO` in
  `B_STABLE_AUDITORY` mit Support `3` erhalten;
- `N_AUDIO` wurde von `B_STABLE_AUDITORY` abgewiesen;
- alle acht Proben waren read-only.

Dieser Komponentenbefund ist kein bestandener S2-KG-Gesamtvertrag und
keine allgemeine auditive Identitaets- oder Lernbehauptung.

## Naechste Funktionsgrenze

Ein weiterer nahezu identischer Holdout-Lauf ist nicht begruendet. Der
naechste getrennt zu kontrahierende Schritt ist eine read-only
modalitaetsgetrennte 336-Werte-Kontextdarstellung. Sie darf auditive und
visuelle Befunde separat bereitstellen, aber weder automatisch zu einer
gemeinsamen Erinnerung verschmelzen noch eine Auswahl oder Entscheidung
erzeugen.
