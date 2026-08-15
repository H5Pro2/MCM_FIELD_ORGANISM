# S1-JH: Endlicher gemeinsamer Intervallhuellen-Fixturevertrag

## Ergebnis

S1-JH bindet die endlichen Werte und kanonischen Digests fuer die in S1-JG
festgelegte gemeinsame Intervallhuelle. Gebunden sind sieben
Orchestrierungssequenzen mit insgesamt 23 Intervallen pro Modell und
Refinement. Es wird noch kein Laufzeitobjekt konstruiert und kein Feld- oder
Modellschritt ausgefuehrt.

## Gemeinsame Zeit- und Kontaktwerte

Jedes Intervall verwendet denselben modellneutralen Zeitwert:

`MCMFieldStepTime("mcm.s1jh.common.interval", 0, 1, 2.0)`

Das entspricht `0.5` synthetischen Zeiteinheiten. Die identischen Ticks
verhindern, dass ein Modell aus dem Zeitobjekt Profil, Sequenz oder Ordinal
ablesen kann. Zweiknotenintervalle erhalten immer `(0,0)`,
Dreiknotenintervalle immer `(0,0,0)`. Auch Quelltakt, Quellfenster und
Kontaktidentitaeten sind pro Geometrie fest und wertgleich.

## Vorzustandsquellen

- P_IE beginnt mit dem weiterhin gueltigen synthetischen Zustand
  `S=(-1,1)`, `H=(-0.2,0.2)` und traegt nach Intervall 1 den vollstaendigen
  S/H-Zustand in Intervall 2.
- P_IH verwendet vor jedem seiner drei Intervalle ausschliesslich
  `A_BOUNDARY_2N` mit `S=(-0.5,0.5)` und `H=(0,0)`.
- P_IK und P_IN verwenden ausschliesslich die in S1-IY/S1-IZ registrierten
  A-, B-, Gap- und Probe-Grenzen der offenen Dreiknotenlinie.
- Der Carry-Quellverweis ist exakt der Digest des unmittelbar vorherigen
  Intervalls. Grenzverweise sind Digests der jeweiligen Fixturewerte.

Alte P_IH-, P_IK- oder P_IN-Feldergebnisse werden weder kopiert noch
skaliert, angepasst oder uminterpretiert.

## Sequenzen

- P_IE: F_HIGH und R_HIGH mit je zwei Intervallen und zwei Checkpoints.
- P_IH: A-A-A mit drei Intervallen und drei Checkpoints.
- P_IK: A-B-A-Probe und A-Gap-A-Probe mit je vier Intervallen und nur dem
  abschliessenden Checkpoint.
- P_IN: Recovery-on und Recovery-off mit jeweils wertgleichem
  A-Gap-B-Probe-Aussenablauf und nur dem abschliessenden Checkpoint.

Die beiden aeusserlich identischen P_IE- und P_IN-Paare besitzen getrennte
orchestratorinterne Sequenzdigests. Diese Digests sind keine Modellfelder.
Damit bleiben Sidecar-Zuordnung und Digestpruefung eindeutig, ohne die
Modellsicht zu erweitern.

## Kandidatenseitige Sidecars

Nur DTS-1 erhaelt getrennt von der Huelle die bereits registrierten
P_IE-Anatomien F_HIGH beziehungsweise R_HIGH und im P_IN-Gap die
Recoveryrate `0.2` beziehungsweise `0.0`. B1 bis B6 erhalten weder Sidecar,
Platzhalter, Label noch einen daraus abgeleiteten Wert.

## Begrenztes Pruefbudget

Fuer sieben Modelle und die Refinements 2/4/8 bindet eine spaetere einfache
Fixturepruefung maximal 483 Intervallaufrufe, 399 Grenzanwendungen und 231
Checkpointaufnahmen. Die deterministische Doppelpruefung ist auf 966, 798
und 462 begrenzt. Das sind technische Obergrenzen und keine ausgefuehrten
Feldschritte.

## Entscheidung

`FINITE_COMMON_INTERVAL_FIXTURE_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`740bcc9fe1f29258d68278ba78a58005ff46c1da548dcf3b465eb8b5f1ed9e56`

S1-JH zeigt keine numerische Zulaessigkeit, Baselinepassung oder
Kandidatenueberlegenheit. Speicher-, Lern- und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JI darf ausschliesslich die privaten unveraenderlichen Fixture- und
Intervallhuellenobjekte sowie deren reine Materialisierung implementieren und
technisch gegen S1-JG/S1-JH pruefen. Noch kein Baselineadapter, Modellaufruf,
Profilvergleich, keine Runtime und keine Forschungsprobe.
