# S1-CI: E1 E4 F3-Familienrunner und isolierte Bereitschaft

## Status

Die vier konkreten F3-Familienrunner B3 bis B6 sind an die gemeinsame
H/G/C-Welt, die Rueckwirkungsintervention und die identische eingefrorene
Probe gebunden und isoliert technisch abgenommen.

Es wurde keine vollstaendige E4-Matrix komponiert, kein F3-Profil gegen E1
ausgewertet und keine E4-Entscheidung erzeugt. Die S1-BZ- und
S1-CD-Einmallaufe wurden nicht wiederholt.

## Implementierung

```text
mcm_field_organism/e1_e4_f3_runners.py
tests/test_e1_e4_f3_runners.py
```

Die Runner bleiben private Forschungsrollen und sind weder im Paketexport
noch in `current_api` enthalten.

## Gebundene Modelle

```text
B3  compute_mcm_f3_local_leaky_baseline
B4  compute_mcm_f3_linear_coupled_baseline
B5  compute_mcm_f3_coupling
B6  compute_e1_e4_const_v_coupling ueber den S1-CF-Handoff
```

B3 bis B5 verwenden unveraendert:

```text
lambda_sm_per_second = 1.0
kappa                = 0.5
eta                  = 1.0
initial_total_mass   = 1.0
```

B6 verwendet unveraendert den kanonischen CONST-V-Wert
`lambda_sm_per_second = 0.5` bei denselben uebrigen Parametern.

## Gemeinsamer Runnerpfad

Jedes Modell durchlaeuft isoliert und aus demselben frischen neutralen
Drei-Knoten-Feld:

```text
H: 8 linke Kontakte zu je 1.0 s
G: Nullkontakt bis G1, G4 und G8
C: tiefe G4-Kopie, 8 rechte Kontakte zu je 1.0 s
```

In C bleibt die vorhandene M-Zustandsrate aktiv und nur die Rueckwirkung auf
S/H wird durch den S1-CH-Wrapper ausgeschaltet.

An `H8, G1, G4, G8, C1 ... C8` wird M auf dem vorbereiteten frischen
Probefeld fixiert. Der vorhandene Modellreader wirkt weiterhin auf das
aktuelle S; die M-Rate ist waehrend der Probe null. Das Ergebnis ist das
kanonische signierte 72-Komponenten-Profil.

## Kontrollen

Jeder Runner wird vollstaendig mit `n=2` und `n=4` erzeugt. Gebunden sind:

- unveraenderte Checkpointreihenfolge;
- exakter P0-Pfad fuer vollstaendige Zustands- und Rueckwirkungsablation;
- unveraenderte M-Geometrie und M-Werte waehrend der Frozen-Probe bis
  `1e-12`;
- eigene Massenbilanz und Nichtnegativitaet;
- relativer n=2/n=4-Profilrest bis `0.01`;
- deterministischer Parameterdigest je Modell;
- unveraenderter frischer Eingabefeldzustand.

Die Ablation wird bewusst ueber den vorhandenen exakten P0-Pfad ausgefuehrt.
Ein aktiver M-Container mit einem Nullrechner wuerde den numerischen
SSPRK-Pfad beibehalten und damit einen Integratorrest statt einer reinen
P0-Kontrolle messen.

## Technische Abnahme

Fokussiert:

```text
python -m unittest -v tests.test_e1_e4_f3_runners

9 tests
OK
```

Gemeinsam mit S1-CH, S1-CF sowie den vorhandenen F3-Kopplungs-, Baseline-
und Runtimevertraegen:

```text
57 tests
OK
```

Alle vier Modelle liefern ein vollstaendiges, messbares und ueber die
Checkpoints nicht konstantes Profil. Ablation, Frozen Reader, Invarianten
und die registrierte Refinementgrenze bestehen.

## Aussagegrenze

Die isolierte Lauffaehigkeit zeigt weder, dass eine F3-Baseline E1 erklaert,
noch dass E1 nach den Pflichtbaselines einen Rest besitzt. Die Profile
wurden nicht miteinander verglichen. Es folgt insbesondere kein
Memory-, Lern-, Organisations-, Semantik- oder KI-Befund.

## Anschluss

S1-CJ bindet E1, B0 und den einzigen statischen H8-Gain B1 an denselben
Checkpoint- und Probevertrag. Alle 15 neu gebildeten Kontinuitaetswerte
passen innerhalb `1e-12` zu den gespeicherten S1-CD-Ankern, ohne den
S1-CD-Einmallauf erneut auszufuehren.

## Bester naechster Schritt

S1-CK bindet S2-B2 und ORACLE-G. S1-CL prueft als naechstes das vollstaendige
Runnerinventar statisch. Die E4-Gesamtmatrix und ihre Entscheidung bleiben
gesperrt.
