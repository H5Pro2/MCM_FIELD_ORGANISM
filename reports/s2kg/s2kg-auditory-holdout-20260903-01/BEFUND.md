# S2-KG - Auditive Holdout-Generalisation

## Abschluss

Der Lauf `s2kg-auditory-holdout-20260903-01` wurde genau einmal ausgefuehrt
und danach genau einmal unabhaengig read-only verifiziert.

```text
Aufzeichnung:   RECORDING_COMPLETE
Operationen:    157
Funktionsstatus: S2KC_AUDITORY_HOLDOUT_GENERALIZATION_FALSIFIED
```

Der Lauf ist technisch vollstaendig und damit fachlich auswertbar. Sein
abweichendes Ergebnis ist eine echte Falsifikation der gesamten vorab
gebundenen Hypothese, kein Infrastrukturfehler. Es gab keinen Retry und
keine Parameter-, Fixture- oder Schwellenaenderung.

## Bestaetigte Teilbefunde

- `H_AUDIO` und `N_AUDIO` erschienen weder im Memory- noch im
  Baselinetraining.
- Nach D1-D9 war `H_AUDIO` weder in B4 noch in Fast vorhanden.
- `H_AUDIO` wurde final ausschliesslich in der auditiven Slow-Bank mit
  Support `3` und Distanz `0.018096882417946113` erkannt.
- Frozen und Replay wiesen `H_AUDIO` ab; der adaptive Prototyp nahm es an.
- `N_AUDIO` hatte final keinen B4-, Fast- oder auditiven Slow-Treffer.
- Die visuelle Slow-Spur war fuer beide Holdouts identisch und damit nicht
  diskriminierend.
- Alle acht Memory- und Baselineproben waren read-only.

## Falsifizierte Bindung

Die vorab gebundene Aussage `negative_has_no_auditory_match` verlangte,
dass `N_AUDIO` an keinem Checkpoint einen der kombinierten B4-, Fast- oder
auditiven Slow-Befunde ausloest. Sie ist falsch:

| Checkpoint | B4 | Fast | Auditory Slow | Auditive Distanz |
| --- | --- | --- | --- | ---: |
| C1 | ausgewaehlt | ausgewaehlt | keiner | `0.03023999967450985` |
| C2 | ausgewaehlt | ausgewaehlt | keiner | `0.020639999975482805` |
| C3 | keiner | keiner | keiner | - |

An C1 und C2 liegen die auditiven Distanzen zwar oberhalb der Schwelle
`0,02`; der identische visuelle Zustand fuehrt dennoch zu kombinierten
B4-/Fast-Auswahlen. Dadurch ist der globale Negativclaim nicht erfuellt.
Der final isolierte auditive Slow-Befund und die adaptiven Baselines bestehen,
duerfen aber die falsifizierte Gesamthypothese nicht in einen Erfolg
umdeuten.

## Aussagegrenze

S2-KG bestaetigt den adaptiven auditiven Slow-Teilbefund innerhalb dieser
Fixture, aber nicht die vollstaendige vorregistrierte auditive
Holdout-Generalisation. Insbesondere zeigt der Lauf, dass ein identischer
visueller Begleiter bei fruehen kombinierten B4-/Fast-Proben nicht als
neutraler Negativkontext behandelt werden kann.

`result.json` bleibt das unveraenderte Primaerartefakt;
`verification.json` enthaelt den einmalig erzeugten Verifikationsbefund.
