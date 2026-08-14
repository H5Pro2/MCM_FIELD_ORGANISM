# W7-AK: Implementierung des CAP/P0-Rohkontrastkompositors

## Entscheidung

`CAP_P0_SAMPLE_ALIGNED_RAW_CONTRASTS_MATERIALIZED`

W7-AK implementiert den statischen Vertrag W7-AJ im Arbeitsspeicher. Die
vorhandenen W7-AG- und W7-AI-Messergebnisse werden nur gelesen; kein
Messzweig wird erneut ausgefuehrt. Es gibt keine Schwellen-, Pfad- oder
Funktionsauswertung.

## 1. Implementierter Umfang

- genau 35 Paare fuer sieben Pfade und Checkpoints 0 bis 4;
- genau 3.185 gerichtete S/H-Residualsamples `CAP - P0`;
- identische W7-Y-Checkpointdigests, Ticks und Neuronenreihenfolgen;
- je Paar drei primaere sampleweise Rohabstaende;
- je Paar drei sekundaere W7-P-Aggregataudits;
- unveraenderte W7-AG- und W7-AI-Eingangsdigests;
- Kennzeichen `evaluated = false` auf Paar- und Gesamtebene.

## 2. Primaere Rohabstaende

Aus den gerichteten Residuen wurden ausschliesslich berechnet:

- `cap_p0_S_linf`;
- `cap_p0_H_linf`;
- `cap_p0_SH_trajectory_l2`.

Die groessten Werte ueber die 35 Rollen lauten:

```text
max cap_p0_S_linf              = 0.00024372674997497068
max cap_p0_H_linf              = 0.0001402313749417905
max cap_p0_SH_trajectory_l2    = 0.0037883232850900745
```

Diese Zahlen sind rohe Modelldistanzen bei der vorhandenen n-Aufloesung. Sie
werden nicht als aufgeloester Effekt oder Feldfunktion bewertet.

## 3. Gegenkontrollen

- CAP/CAP und P0/P0 ergeben fuer alle drei Rohabstaende exakt null;
- CAP/P0 und P0/CAP besitzen gleiche absolute Abstaende und
  vorzeicheninvertierte gerichtete Residuen;
- kanonische und umgekehrte Rollenverarbeitung liefern je Rolle denselben
  Paarresultatdigest;
- alle sechs vorhandenen W7-P-Skalare werden aus den jeweiligen Samples
  exakt rekonstruiert;
- M, regionale Kapazitaet und Observerwerte fliessen nicht in die
  S/H-Rohabstaende ein.

## 4. Gebundener Gesamtdigest

```text
ca047546d37a0ebd5728ee6adcf27d083c2a7fce3aad82f882284f08629f1fc3
```

Der Digest bindet die 35 Paarresultate, beide Eingangsdigests sowie
Identitaets-, Symmetrie- und Reihenfolgegegenkontrollen. Er enthaelt keine
Schwelle oder Entscheidung.

## 5. Verifikation

Die fokussierte W7-AK-Suite besteht mit:

```text
Ran 10 tests in 361.267s
OK
```

Geprueft wurden Rollenbestand, Sampleanzahl, Checkpoint- und Tickbindung,
exakte Residuen, Rohabstaende, Aggregataudits, Rollenreinheit,
Gegenkontrolldigests, Eingangspassivitaet, Digestmanipulationsabwehr und
fehlender Export aus `current_api`.

## 6. Offene numerische Grenze

Die CAP-Runtime besitzt technisch einen `refinement`-Parameter. Der aktuelle
W7-AE/AG-Pfad verwendet jedoch nur dessen Standardwert `1`; es existieren
keine vollstaendig gebundenen 2n/4n-Messketten. Damit koennen `epsilon_num`
und `effect_floor` aus W7-L noch nicht bestimmt werden.

## 7. Aussagegrenze

W7-AK zeigt, dass CAP und P0 technisch sampleweise verglichen werden koennen
und bei n-Aufloesung endliche Rohabstaende liefern. Ohne Verfeinerungsboden,
Pfadkontrast und Intervention folgen daraus keine Feldfunktion,
Ressourcenfreisetzung, Wiederverwendung, Memory, Feldzeit, Organisation,
Topologie, Semantik, Selbstregulation oder KI.

## 8. Verwendete Quellen

- `docs/W7AJ_VERTRAG_CAP_P0_MESSPAARUNG_UND_ROHKONTRASTE.md`
- `mcm_field_organism/w7ag_passive_cap_measurement_handoff.py`
- `mcm_field_organism/w7ai_p0_zero_start_measurement_reference.py`
- `mcm_field_organism/w7ak_cap_p0_raw_contrast_compositor.py`
- `tests/test_w7ak_cap_p0_raw_contrast_compositor.py`

## 9. Naechster Schritt

W7-AL soll statisch auditieren, wie `refinement = 2` und `refinement = 4`
durch den bestehenden CAP-Haupt-, Mess- und Paarungspfad gefuehrt werden
koennen, welche P0-Referenz dabei konstant bleibt und welche Digests neue
Rollen benoetigen. Noch keine Runtimeaenderung, Verfeinerungsausfuehrung,
Schwellenberechnung, Auswertung, kein Browser, Report oder Forschungslauf.
