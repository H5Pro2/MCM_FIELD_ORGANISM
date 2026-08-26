# S1-CD: E1 E3-Einmallauf Freigabe und Ressourcenwiederverwendung

## Status

Die in S1-CC vorregistrierte E3-Probe wurde ohne Parameter- oder
Schwellenanpassung implementiert und genau einmal kanonisch ausgefuehrt. Der
Lauf ist gueltig. Die begrenzte technische Entscheidung lautet:

```text
E3_RELEASE_AND_RESOURCE_REUSE
```

Dies ist kein Memory-, Vergessens-, Lern-, Organismus-, Semantik- oder
KI-Befund.

## Implementierung

```text
mcm_field_organism/e1_e3_probe_run.py
tests/test_e1_e3_probe_run.py
```

Der private Kompositor erzeugt S1-BX-Geschichte, S1-CB-Zustandsarme,
frisches Probefeld, zehn Hauptarme und sechs n=2/n=4-Verfeinerungsarme in
einem gebundenen Ergebnis. Keine Rolle wird ueber das Paket oder
`current_api` exportiert.

## Einmalige Ausfuehrung

Nach bestandener reiner Syntax- und Strukturpruefung wurde genau einmal
ausgefuehrt:

```text
python -m unittest -v tests.test_e1_e3_probe_run

9 tests
OK
```

Der kanonische S1-CD-Lauf wurde danach nicht wiederholt.

## Rohe Zustandsmetriken

```text
release_analytic_linf:             1.734723475976807e-18
resource_budget_linf:              4.440892098500626e-16
release_total_binding_drop:        0.10364242805542052
compete_release_binding_linf:      0.14702684233585644
compete_total_binding_rebound:     0.11840875933358301
compete_neutral_binding_linf:      0.006954809076442525
```

Die programmierte Nullkontaktfreigabe folgt damit der analytischen
Exponentialkurve innerhalb der vorregistrierten Toleranz. Nach der
Gegengeschichte liegt erneut positive Nettobindung vor und COMPETE bleibt
von einer neutralen Neuinitialisierung unterscheidbar.

## Rohe Probemetriken

Kontrollen:

```text
pre_probe_s_linf:                  0.0
pre_probe_h_linf:                  0.0
ablation_p0_s_linf:                0.0
ablation_p0_h_linf:                0.0
fixed_gain_s_linf:                 0.0
fixed_gain_h_linf:                 0.0
refinement_s_linf:                 5.551115123125783e-17
refinement_h_linf:                 1.2490009027033011e-15
```

Aktive Arme gegen P0:

```text
hold_p0_s_linf:                    0.005960779905044511
hold_p0_h_linf:                    0.0037253303212222977
release_p0_s_linf:                 0.002240107629682464
release_p0_h_linf:                 0.0013957395800104355
compete_p0_s_linf:                 0.0026902423795267943
compete_p0_h_linf:                 0.00238212405542311
```

Vorregistrierte Paarvergleiche:

```text
release_hold_s_linf:               0.003720672275362047
release_hold_h_linf:               0.002329590741211862
compete_release_s_linf:            0.0029908008917126083
compete_release_h_linf:            0.0025335555912394947
compete_hold_s_linf:               0.005826613784857659
compete_hold_h_linf:               0.0036957132968034045
```

Alle entscheidenden Paarunterschiede liegen deutlich oberhalb des festen
Effektbodens `1e-12` und des kleineren Numerikrests.

## Kontrollbefund

- Alle zehn Hauptarme starten vom identischen frischen Probefeld.
- P0, H0, R0 und C0 sind im Felddigest exakt identisch.
- H1, R1 und C1 entsprechen jeweils exakt ihrem festen Gainarm.
- RELEASE unterscheidet sich unter identischer Probe von HOLD.
- COMPETE unterscheidet sich unter identischer Probe zusaetzlich von RELEASE.
- Analytische Freigabe, Ressourcenbilanz und erneute Nettobindung bestehen.
- Die eingefrorenen E1-Zustaende bleiben unveraendert.

## Regression

Der bestehende Verbund wurde ohne S1-BZ- oder S1-CD-Wiederholung separat
geprueft:

```text
88 tests
OK
```

## Technische Einordnung

Im ersten Korridor ist nun ein vollstaendiger konstruierter technischer
Lebenszyklus gezeigt:

```text
lokale Geschichte
-> begrenzte E1-Kantenbindung
-> spaetere kausale Feldwirkung
-> analytische Nullkontaktfreigabe
-> konkurrierende erneute Bindung
-> erneut veraenderte spaetere Feldwirkung
```

Der exakte Fixed-Gain-Befund begrenzt die Aussage: Ein eingefrorener
E1-Zustand wirkt in der Einzelprobe wie eine feste raeumliche
Kopplungskonfiguration. Der technische Mehrwert von E1 liegt daher nur in
der programmierten Entwicklung, Freigabe und Wiederverwendung dieser
Konfiguration, nicht in einer neuen Wirkung waehrend der eingefrorenen Probe.

## Aussagegrenze

E3 bestaetigt die spezifizierte Engineeringmechanik, weil genau diese
Freigabe- und Bindungsdynamik implementiert wurde. Noch nicht gezeigt sind:

```text
Vorteil oder Nichtreduzierbarkeit gegen bekannte adaptive Baselines
Rekonstruktion durch einen Teilhinweis
selektive Stabilisierung durch Wiederholung
mehrere konkurrierende Muster bei festem Kapazitaetsbudget
Uebertragung auf die kontrollierte Audio-/Video-Testwelt
```

Die Bezeichnungen MCM-Memory, organisches Vergessen oder feldbasierte KI
bleiben deshalb unzulaessig.

## Bester naechster Schritt

S1-CE registriert den kleinsten E4-Vergleich des gesamten
Geschichte-Freigabe-Konkurrenz-Probe-Verlaufs gegen transparente leaky-,
Integrator-, Fixed-Gain-, F3- und CONST-V-Baselines. S1-CF implementiert als
naechsten Schritt nur die noch fehlenden Profil- und Baselinehandoffs. Es
wird keine neue E1-Gleichung entwickelt.
