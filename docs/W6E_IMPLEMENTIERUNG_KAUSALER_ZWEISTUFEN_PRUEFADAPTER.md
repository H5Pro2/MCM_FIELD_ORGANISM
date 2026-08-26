# W6-E: Implementierung des kausalen Zweistufen-Pruefadapters

Stand: 2026-08-09

Entscheidung: `W6E_CAUSAL_CHECK_ADAPTER_AND_WORLD_CONTRACT_TECHNICALLY_ACCEPTED`

Arbeitsart: technische Implementierung und Akzeptanztests

Runtimeaenderung: ja, additive S1-B-Referenzoberflaeche

Browserausfuehrung: nein

Formaler Forschungslauf: nein

## Entwicklungsfrage

Kann der unveraenderte W6-D-Vertrag als deterministischer technischer Adapter
umgesetzt werden, bevor eine kontrollierte Browserwelt gestartet wird?

## Implementierte Komponenten

### Passiver S/H/L-Observer

`run_s1b_asynchronous_field(...)` akzeptiert nun optional einen passiven
Observer. Der transiente S1-B-Integrator uebergibt ihm ausschliesslich Kopien
von S, H und L sowie den Abschluss-Tick. Der Observer besitzt keinen
Rueckschreibepfad.

### Kausaler Zweistufenadapter

`mcm_field_organism/s1b_causal_two_stage.py` implementiert:

- `run_s1b_causal_two_stage(...)`;
- immutable `S1BCausalProbeSample`- und `S1BCausalProbeTrace`-Objekte;
- den skalaren `S1BCausalTwoStageResult`;
- die festen W6-D-Entscheidungen und die Toleranz `1e-12`.

Der Adapter:

1. startet F_A, F_B, den S1-B-Nullarm und die neutrale Runtime vom selben
   unangetasteten Feld;
2. prueft H_A/H_B auf gleiche Geometrie und Zeitstuetzen;
3. stoppt vor P, wenn L_A null oder L_A/L_B nicht unterscheidbar sind;
4. erzeugt R, N und X nur durch vollstaendige L-Neutralisierung oder
   vollstaendigen L-Tausch;
5. prueft vor P die exakte S/H-Gleichheit von R/N/X;
6. fuehrt jeden Probe-Arm genau einmal aus;
7. vergleicht den Nullarm nach Formation und Probe digestgenau mit der
   neutralen Runtime;
8. berechnet nur die vorregistrierten Linf-Differenzen.

Rohframes, PCM, Browserpayloads, Labels, Phasen-IDs und Weltbedeutungen
gelangen nicht in den Adapter oder seinen Ergebniscontainer.

## Neuer statischer Browserweltvertrag

`mcm_field_organism/s1b_causal_browser_world.py` bindet drei passive Teile:

```text
H_A: horizontale Bewegung, 330-Hz-Ton
H_B: vertikale Bewegung, 660-Hz-Ton
P:   horizontale Bewegung, 440-Hz-Ton
```

H_A und H_B besitzen gleiche Dauer, Phasenfolge, Tonverlauf und
Rezeptorquellgeometrie. Sie unterscheiden sich in genau zwei externen
Eingangsdimensionen: Bewegungsachse und Tonfrequenz. P ist ein einzelner
Vertrag, der spaeter unveraendert auf alle Arme angewandt werden muss.

Gemeinsame Parameter:

```text
Canvas:             120 x 80
visuelle Rate:      30 Hz
Audio:              8000 Hz, Hop 80
Phase:              3 x 300 ms
Rohdatenhaltung:    aus
direkte Sensorik:   aus
Rueckschreibung:    aus
```

Gebundene Digests:

```text
Weltset:      66168de571819b71e68ce6605781d3d65224cc1663294924fce788ad2a821920
H_A Welt:     595c8bb0016e0425dc9ab27e7ebc8e4110a0950b1dd001dced7d2ea8fb8929dc
H_A Quelle:   a4968487961556c4f061bb7dfe47ccab610c99d55fb1c26af1d70170274b3095
H_B Welt:     e85714f51fb3fd11081e4c5919fa4033c566679216a65fa2f5c47ee65db55018
H_B Quelle:   8705c1ecc10fb3df7e0f72300c732ecab09bfac6fe07f2d20275cc83225816e7
P Welt:       dad8cac570e58010f2e66886ab7464a277b06367bf21567ab9f6a56ca544fcdc
P Quelle:     3e38be43de466ed71f205b3d1758fb3c7144881b59de541d0ea24cb65efbdb18
```

Keiner dieser Vertrage wurde im Browser ausgefuehrt.

## API-Trennung

Observer, Pruefadapter, Ergebnisrollen und Weltvertrag liegen ausschliesslich
in `S1B_REFERENCE_EXPORTS`. Die neutrale Kernoberflaeche und
`advance_audio_video_receptor_sequences()` bleiben unveraendert.

## Technische Abnahme

Direkt konstruierte reduzierte Audio-/Video-Sequenzen pruefen:

- vollstaendigen Vierarmablauf R/N/X/Z;
- exakte schnelle Gleichheit vor P;
- Nullarmgleichheit mit der neutralen Runtime;
- technisch aufgeloeste, durch S1-B konstruierte L-nach-S-Rueckwirkung;
- Stopp vor P bei identischer Donorformation;
- deterministische und immutable Ergebnisse;
- Abweisung abweichender H_A/H_B-Zeitstuetzen;
- passive, kamera- und rueckschreibungsfreie Weltvertraege;
- gleiche H_A/H_B-Stuetzen bei zwei externen Eingangsunterschieden;
- festen Weltset-Digest und gemeinsame Rezeptorquellgeometrie.

Mit allen betroffenen S1-B-, neutralen Runtime-, API- und AV-
Regressionstests bestehen 60 Tests. Alle neuen Module kompilieren fehlerfrei.

## Technisches Ergebnis

Der Direktsequenztest erreicht
`LOCAL_L_STATE_CAUSALLY_ALTERS_LATER_S_TRAJECTORY_IN_S1B_REFERENCE`. Das ist
kein Forschungsbefund: Die Eingaben wurden direkt konstruiert und die
L-nach-S-Rueckwirkung ist Bestandteil der implementierten S1-B-Gleichung.
Der Test bestaetigt ausschliesslich, dass Intervention, Observer, Metrik und
Entscheidungslogik korrekt verbunden sind.

## Aussagegrenze

W6-E belegt keine Praegung, Wiedererkennung, Rekonstruktion, Loesung,
Wiederverwendung, Feldzeit, innere Wahrnehmung, Organisation, Topologie,
Semantik, Selbstregulation, Memory oder KI. Es wurde kein Browser gestartet
und kein formaler Forschungslauf erzeugt. Lauf 197 bleibt reserviert und
unberuehrt.

## Bester naechster Schritt

W6-F implementiert ohne Browserstart die dreiteilige Capture- und
Zeituebergabe fuer H_A, H_B und P unter deterministischen Browser-Fakes. Sie
muss die drei relativen Weltzeiten auf disjunkte, fortlaufende
Organismuszeitfenster abbilden, P als identisches unveraendertes
Rezeptorobjekt an alle Arme uebergeben und jeden Rohpayload vor dem Feldpfad
verwerfen. Erst danach darf ein realer kontrollierter Browserlauf separat
vorregistriert werden.
