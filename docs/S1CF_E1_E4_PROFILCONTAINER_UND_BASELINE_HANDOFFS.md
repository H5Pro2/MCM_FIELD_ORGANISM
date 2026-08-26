# S1-CF: E1 E4-Profilcontainer und Baseline-Handoffs

## Status

Der in S1-CE geforderte Profilcontainer sowie die privaten S2-B2- und
CONST-V-Handoffs sind implementiert und technisch abgenommen. Es wurde kein
E4-Gesamtlauf ausgefuehrt und keine Baselineentscheidung erzeugt. Kein
Memory-, Lern-, Organismus-, Semantik- oder KI-Befund.

## Implementierung

```text
mcm_field_organism/e1_e4_baseline_handoffs.py
tests/test_e1_e4_baseline_handoffs.py
```

Alle Rollen bleiben privat und fehlen sowohl im Paketexport als auch in
`current_api`.

## Beobachtbarer Profilcontainer

`E1E4ObservableProfile` erzwingt die kanonische Checkpointfolge:

```text
H8, G1, G4, G8, C1, C2, C3, C4, C5, C6, C7, C8
```

Jeder Checkpoint enthaelt genau drei vorzeichenbehaftete S- und drei
vorzeichenbehaftete H-Komponenten. Dadurch entstehen unveraenderlich:

```text
12 * 3 * 2 = 72 Komponenten
```

Fehlende, doppelte oder umgeordnete Checkpoints werden abgelehnt. Ein
deterministischer SHA-256-Digest bindet Modellkennung, Reihenfolge und Werte.

## Profilvergleich

`compare_e1_e4_profiles(...)` vergleicht ausschliesslich eine E1-Referenz
gegen genau eine registrierte Baseline. Gebildet werden:

```text
profile_linf_residual
profile_l1_residual
candidate_profile_linf
relative_profile_linf_residual
release_segment_linf_residual
competition_segment_linf_residual
```

Das Freigabesegment umfasst H8, G1, G4 und G8. Das Konkurrenzsegment umfasst
C1 bis C8. Vorzeichen und Knotenlagen bleiben erhalten. Eine E1-Referenz
ohne messbaren Effekt wird abgelehnt, statt durch Division zu einem
scheinbaren Vergleich zu werden.

## S2-B2-Handoff

Der Handoff bindet unveraendert `S2ReferenceModelConfig()` an die aktuelle
Drei-Knoten-Geometrie:

```text
capacity_ratio              = 8.0
coupling_rate_per_second    = 0.25
afterimage_time_seconds     = 0.5
leak_rate_per_second        = 0.0
gain_reference_seconds      = 1.0
rk4_substeps                = 16
```

Die dynamische Zuordnung ist keine neue Gleichung:

```text
Rueckwirkung an   -> vorhandenes S2-Modell B2
Rueckwirkung aus  -> vorhandenes S2-Modell B1
```

B1 besitzt dieselbe lokale L-Entwicklung ohne L-zu-S-Rueckwirkung und ist
damit die gebundene Ablation fuer Phase C.

Fuer spaetere identische Proben wird L objektiv festgehalten. Der aktive
Reader integriert nur die bereits definierte lineare B2-S/H-Gleichung mit
festem L. Der ablatierte Reader verwendet B0 und behaelt dasselbe L
unveraendert. Es gibt keine Zustandsentwicklung waehrend der Probe.

## CONST-V-Handoff

Der Handoff liest genau den kanonischen `const-v`-Spec aus W7-M:

```text
eta        = 1.0
kappa      = 0.5
lambda_sm  = 0.5
```

Er erzeugt lediglich ein uniformes M-Inventar mit Gesamtmasse `1.0` auf der
aktuellen Drei-Knoten-Geometrie. Die Ableitung wird unveraendert an
`compute_w7n_coupling_baseline(...)` delegiert. Der alte W7-BD-Feld- und
Trajektoriendigest wird nicht uebernommen und alte Ergebnisse werden nicht
gekreuzt.

## Technische Abnahme

Fokussiert:

```text
python -m unittest -v tests.test_e1_e4_baseline_handoffs

10 tests
OK
```

Gemeinsam mit dem bisherigen Verbund, jedoch ohne Wiederholung der
S1-BZ- und S1-CD-Einmallaufe:

```text
98 tests
OK
```

Geprueft wurden:

- feste Checkpointordnung und exakt 72 Komponenten;
- getrennte Freigabe- und Konkurrenzresiduen;
- deterministischer Profildigest;
- exakte Zuordnung der S2-Pfade zu B2 und B1;
- eingefrorenes L waehrend aktiver und ablatierter S2-Probe;
- unveraenderte S2-Parameter;
- unveraenderte CONST-V-Parameter und uniforme Gesamtmasse;
- exakte Delegation an den bestehenden W7-N-CONST-V-Kern;
- Ablehnung fremder Geometrie;
- private API-Grenze.

## Aussagegrenze

S1-CF zeigt nur, dass die Modelle in einen gemeinsamen Daten- und
Geometrievertrag ueberfuehrt werden koennen. Es wurde weder geprueft, welche
Baseline den E1-Verlauf erklaert, noch ob alle Modelle den vollstaendigen
12-Checkpoint-Zeitplan numerisch gueltig durchlaufen.

## Anschluss

S1-CG bindet nun vor jeder Ausfuehrung den vollstaendigen
E4-Ausfuehrungsplan: Modellreihenfolge, Zustandsbildung, Checkpoint-Proben,
Refinements, Invarianten, Ergebniscontainer und Abbruchreihenfolge. Es wurde
weiterhin kein E4-Lauf ausgefuehrt.

## Bester naechster Schritt

S1-CH hat F3-Wrapper, Executorkern und Ergebnisrollen synthetisch abgenommen.
S1-CI bindet als naechstes die konkreten Modellrunner isoliert an Weltfolge
und Probe. Noch kein E4-Einmallauf.
