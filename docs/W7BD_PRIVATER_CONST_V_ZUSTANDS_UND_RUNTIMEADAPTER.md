# W7-BD: Privater CONST-V-Zustands- und Runtimeadapter

## Zweck

W7-BD implementiert den kleinsten technischen Anschluss aus W7-BC. Der
Adapter besitzt keine Pfadlogik, keine Messkomposition und keinen Runner. Er
stellt nur sicher, dass ein spaeterer CONST-V-Schritt dieselbe bestehende
SSPRK33-Runtime wie CAP verwendet, aber die registrierte CONST-V-Gleichung.

## Zustandsgrenze

Eine neue CONST-V-Ausgangslage entsteht als tiefe Kopie des kanonischen W7-M-
Ausgangsfeldes. Vor dem ersten Safe-Step wird dessen Substratarm ersetzt durch:

- `arm_id = w7n.const-v`
- `lambda_sm = 0.5`
- `kappa = 0.5`
- `eta = 1.0`

Neuronenschicht, Docks, Geometrie und skalare Anfangsverteilung bleiben
unveraendert. Das W7-M-CAP-Ausgangsfeld selbst wird nicht veraendert.

## Runtimegrenze

Ein transienter Schritt delegiert an
`mcm_f3_runtime.advance_mcm_f3_shared_field_transient` mit:

- `response_time_seconds = 1.0`;
- `afterimage_time_seconds = 0.5`;
- keiner Dissipation;
- expliziter Aufloesung R1, R2 oder R4 durch den spaeteren Verbraucher;
- `w7n.compute_w7n_coupling_baseline` und der unveraenderten CONST-V-Spezifikation
  als Kopplungsrechner.

Der Runtimeeingang verwirft jedes Feld, das nicht bereits den exakten
CONST-V-Arm traegt. Damit wird verhindert, dass die Safe-Step-Berechnung noch
CAP-Parameter liest, waehrend nur die Ableitung ausgetauscht wird.

Der optionale Messobserver erhaelt ausschliesslich nicht schreibbare Kopien
der S-, H- und Skalarvektoren und darf keinen Zustand zurueckgeben. Diese
Passivitaetsregel ist im Adapterdigest `496a7955...58db` gebunden.

## Evidenzgrenze

W7-BD erzeugt keine Siebenpfadtrajektorie und keinen Zahlenbefund. Der
technische Skalar ist weder freie Kapazitaet noch Memory. Der Adapter ist
privat und wird nicht ueber Paketwurzel oder `current_api` exportiert.

## Naechster Anschluss

W7-BE hat die private CONST-V-Zustandsfortsetzung, Checkpointkopie und
Rohmessung fuer AB/R1 umgesetzt. W7-BF bindet als naechstes BA/R1 und die
exakte AB/R1-Wiederholung, bevor weitere Pfade zugelassen werden.
