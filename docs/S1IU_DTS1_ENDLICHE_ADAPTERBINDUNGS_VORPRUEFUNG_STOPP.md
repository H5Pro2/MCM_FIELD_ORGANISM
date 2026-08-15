# S1-IU: Endliche DTS-1-Adapterbindungs-Vorpruefung mit STOPP

## Status

S1-IU sollte vorhandene Konfigurationswerte und Digests sowie eine endliche
Fallmatrix fuer sechs Baselines und vier Profilbloecke binden. Vor dieser
Wertbindung wurde geprueft, ob jeder Block eine gemeinsame kausale Exposition
fuer Kandidat und Baselines besitzt. Zwei Bloecke bestehen diese Vorpruefung
nicht. Der Schritt stoppt daher ohne Werte oder Ausfuehrung.

Entscheidung:

```text
STOPP_P_IK_P_IN_COMMON_CAUSAL_BASELINE_EXPOSURE_UNBOUND
```

Auditdigest:

```text
e9323eab702148e4fc82262e2974e73696206c8614c7b80216d44f9b56901e65
```

## Expositionspruefung

| Profilblock | vorhandene Vorgeschichte | Status |
| --- | --- | --- |
| P_IE | zwei gekoppelte S/H-Feldintervalle mit explizitem Nullkontakt | gebunden |
| P_IH | drei gekoppelte S/H-Feldintervalle mit explizitem Nullkontakt | gebunden |
| P_IK | direkte A-B/Gap-A-Kantenbeteiligung, danach frischer Nullkontakt-Readout | blockiert |
| P_IN | direkte A-Last/Nullfenster/B-Probe-Kantenbeteiligung, danach frischer Nullkontakt-Readout | blockiert |

In P_IK und P_IN wird die ressourcenwirksame Vorgeschichte direkt als
DTS-1-Kantenbeteiligung eingespeist. Der Feldreadout beginnt erst danach aus
einem frisch aufgebauten gemeinsamen S/H-Zustand und enthaelt nur ein
Nullkontaktintervall. Damit ist die A/B/Gap-Vorgeschichte nicht als
modellneutrale Feld- oder Rezeptorsequenz registriert.

DTS-1-Beteiligung und Ressourcenhistorie sind fuer Baselines durch S1-IR und
S1-IT gesperrt. Sie dennoch zu uebergeben waere ein Informationsleck. Nur die
frische Endprobe an B2 bis B6 zu geben, waere fuer zustandsbehaftete Baselines
aber ebenfalls kein kausal gleicher Vergleich.

## Fallmatrix

Die geplante Matrix umfasst `6 x 4 = 24` Rollen-Block-Faelle:

- 12 Faelle fuer P_IE und P_IH sind hinsichtlich gemeinsamer Exposition
  formal erreichbar.
- 12 Faelle fuer P_IK und P_IN bleiben blockiert.

Die Matrix ist deshalb insgesamt nicht gebunden. Es wurden keine
Konfigurationswerte, Digests, Refinements oder Schwellen festgelegt und kein
Adapter oder Modell ausgefuehrt.

## Aussagegrenze

Der STOPP ist keine Kernelinkompatibilitaet und keine Baselineverwerfung. Er
entwertet auch nicht die bestehenden direkten Interferenz-, Freigabe- oder
Wiederverwendungsledger. Er verhindert nur, deren nachgelagerten Feldreadout
ohne gemeinsame kausale Exposition als dynamischen Baselinevergleich zu
verwenden.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1iu_finite_binding_precheck.py
tests/test_dynamic_substrate_s1iu_finite_binding_precheck.py
```

Neun Tests pruefen Quellenbindung, vier Expositionsklassen, den exakten
12/12-Matrixsplit, verbotene nachtraegliche Abbildungen, offene Werte und
Digests, Ausfuehrungsfreiheit und Manipulationsschutz.

## Bester naechster Schritt

S1-IV darf ausschliesslich einen statischen gemeinsamen
Kausalexpositionsvertrag fuer P_IK und P_IN binden. A, B, Gap, Dauer,
Reihenfolge, S/H-Trage- oder Resetregeln und die kandidatenspezifische
Recovery-Intervention muessen modellneutral getrennt werden, bevor ein neues
Fixture oder eine Baselinekonfiguration gewaehlt wird. Noch keine Gleichung,
Wertwahl, Fixtureimplementierung, Modellausfuehrung, Runtime oder
Forschungsprobe.
