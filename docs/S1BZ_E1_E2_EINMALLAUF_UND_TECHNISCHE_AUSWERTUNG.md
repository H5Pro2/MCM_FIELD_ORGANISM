# S1-BZ: E1 E2-Einmallauf und technische Auswertung

## Status

Die in S1-BY vorregistrierte Komposition wurde ohne Parameteranpassung
implementiert und genau einmal als Ergebnislauf ausgefuehrt. Der Lauf ist
gueltig und wird begrenzt als `E2_TECHNICAL_CAUSAL_EFFECT` eingeordnet.

Dies ist kein Memory-, Lern-, Organismus-, Semantik- oder KI-Befund.

## Implementierung

```text
mcm_field_organism/e1_frozen_e2_run.py
tests/test_e1_frozen_e2_run.py
```

Die Rollen bleiben privat und werden weder ueber das Paket noch ueber
`current_api` exportiert. Alle sieben Hauptarme erhalten denselben Probe-
Payload einschliesslich seiner Metadaten, aber objektgetrennte Feldkopien.

## Einmalige Ausfuehrung

Ausgefuehrt wurde genau einmal:

```text
python -m unittest -v tests.test_e1_frozen_e2_run
```

Ergebnis:

```text
8 tests
OK
```

Der Lauf wurde nach der Ergebnisbildung nicht wiederholt und nicht anhand
seiner Werte nachparametriert.

## Rohe Metriken

```text
pre_s_linf:                   0.0
pre_h_linf:                   0.0
state_linf:                   0.12683743507475037
total_binding_difference:     5.551115123125783e-17
mirror_binding_error:         5.551115123125783e-17
active_s_linf:                0.006046298243694848
active_h_linf:                0.0038293104101744246
ablated_s_linf:               0.0
ablated_h_linf:               0.0
p0_a0_s_linf:                 0.0
p0_a0_h_linf:                 0.0
fixed_gain_s_linf:            0.0
fixed_gain_h_linf:            0.0
refinement_s_linf:            4.163336342344337e-17
refinement_h_linf:            3.608224830031759e-16
```

Vorregistrierte Entscheidung:

```text
E2_TECHNICAL_CAUSAL_EFFECT
```

## Kontrollbefund

- Das frische Probefeld ist vor allen Armen identisch.
- P0, L0 und R0 sind bei ablatierter Rueckwirkung exakt identisch.
- L1 und R1 unterscheiden sich unter derselben Probe deutlich oberhalb des
  vorregistrierten Numerikrests.
- L1 entspricht seinem festen Gainarm exakt; dasselbe gilt fuer R1.
- Die historischen E1-Zustaende sind gespiegelt und besitzen bis auf
  Rundung dieselbe Gesamtbindung.

Der spaetere Feldunterschied wird damit kausal durch die verschiedenen,
geschichtserzeugten E1-Kantenkonfigurationen und deren aktivierte
Rueckwirkung vermittelt. Der Fixed-Gain-Befund zeigt zugleich, dass im
eingefrorenen Probeintervall keine zusaetzliche Dynamik benoetigt wird, um
diesen Unterschied zu erklaeren.

## Regression

Die bereits bestehende E1-, S/H-, Nachhall- und Consumer-Strecke wurde ohne
erneuten S1-BZ-Ergebnislauf separat geprueft:

```text
78 tests
OK
```

## Aussagegrenze

E2 bestaetigt nur eine technische, geschichtsabhaengige und spaeter kausal
wirksame lokale Feldplastizitaet. Noch nicht untersucht sind:

```text
Nullkontaktfreigabe ueber einen kontrollierten Verlauf
Wiederbindung freigewordener endlicher Ressource
Konkurrenz zwischen alter und neuer lokaler Bindung
Abnahme einer alten und Aufbau einer neuen technischen Probewirkung
Rekonstruktion aus Teilhinweisen
```

Die implementierte Freigaberate ist konstruiert. Ein spaeterer erfolgreicher
Freigabeversuch belegt daher zunaechst nur die korrekte Funktion dieser
Mechanik und kein organisches Vergessen.

## Bester naechster Schritt

S1-CA registriert vor jeder weiteren Ausfuehrung einen E3-Korridor fuer
analytisch kontrollierte Nullkontaktfreigabe und konkurrierende
Ressourcenwiederverwendung. Erst S1-CB darf diesen Vertrag implementieren.
