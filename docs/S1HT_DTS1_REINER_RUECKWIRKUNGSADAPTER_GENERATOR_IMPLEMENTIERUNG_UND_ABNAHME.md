# S1-HT: DTS-1 Rueckwirkungsadapter und Generator

## Status

Der in S1-HS gebundene private reine DTS-1-Kantenratenadapter und der
getrennte symmetrische Generatoraufbau sind implementiert und technisch
abgenommen. Es wurde kein DTS-1-Ressourcenschritt und kein MCM-Feldschritt
ausgefuehrt. Keine Materialratenwerte, keine gekoppelte Runtime und kein
Forschungslauf.

Entscheidung:

```text
DTS1_PURE_BACKREACTION_IMPLEMENTED_TECHNICALLY_ACCEPTED
```

## Implementierter Umfang

Das private Modul

```text
mcm_field_organism/dynamic_substrate_dts1_backreaction.py
```

enthaelt:

- `DTS1BackreactionEdgeRate` fuer eine positive symmetrische Kantenrate;
- `DTS1BackreactionResult` fuer das vollstaendige kanonische Ledger;
- `compute_dts1_edge_rates(...)` als reinen Leser einer Anatomie;
- `build_dts1_diffusion_generator(...)` als reinen Matrixaufbau;
- einen eigenen harten `DTS1BackreactionError`.

Das Modul importiert den DTS-1-Ressourcenschritt nicht und veraendert weder
Anatomie noch Layer oder Konfiguration.

## Geometrie und Adapter

Vor jeder Rate werden Layer und Anatomie gegen dieselben vorhandenen
MCM-Geometriehelfer geprueft. Knoteninventar, Kanteninventar und Kantendigest
muessen vollstaendig uebereinstimmen.

Die aktive Rate folgt exakt S1-HR:

```text
c_e = (0.5 * b_e) / min(q_i, q_j)
r_e = r_0 * (1 + c_e)
```

Die Form fuer `c_e` ist algebraisch identisch zu
`b_e/(2*min(q_i,q_j))`, vermeidet aber einen unnoetigen Ueberlauf bei sehr
grossen endlichen Kapazitaeten. Ablation liefert bitgleich `r_e=r_0`.

Der Ergebniscontainer erzwingt selbst `r_0 <= r_e <= 2*r_0`, eindeutige
kanonische Kanten, einen gueltigen Digest und im Ablationsarm die exakte
Basisrate.

## Generator

Der Generator wird als neue quadratische `float64`-Matrix aufgebaut. Jede
Kante wird einmal symmetrisch und mit negativen Diagonaleintraegen gebucht.
Vor Rueckgabe prueft das Modul:

- nur endliche Werte;
- exakte Symmetrie;
- Nullzeilensumme innerhalb einer rein technischen Gleitkommatoleranz;
- kein positives Eigenwertmaximum oberhalb derselben skalierten Toleranz.

Die Pruefung korrigiert keine Matrix. Bei Verletzung wird abgebrochen.

## Technische Abnahme

Alle 16 S1-HS-Matrixklassen sind umgesetzt:

- heterogene Kapazitaeten, Ablation, Nullbindung und Maximalbelegung;
- identische momentane Raten bei gleichem `b_e` und anderer refraktaerer
  Aufteilung;
- vollstaendige Geometrie- und Digestbindung;
- Fail-Closed fuer Eingaben und Ratenledger;
- Reihenfolgeinvarianz und Eingabeimmutabilitaet;
- Matrixformat, Symmetrie, Nullzeilensumme, Nullraum und Spektrum;
- antisymmetrischer kantenweiser Fluss;
- kein Ressourcenschritt-, Feldwert-, Runtime-, Snapshot-, I/O- oder
  oeffentlicher API-Pfad.

Die verwendeten Zahlen sind nur synthetische Algebrafixtures und keine
Materialparameterauswahl.

## Aussagegrenze

Die Abnahme zeigt ausschließlich korrekte momentane Adapter- und
Generatoralgebra. Diese bleibt Fixed-Adapter-aequivalent. Nicht gezeigt sind
gekoppelte Schrittordnung, numerische Feldstabilitaet, Abschwaechung,
Interferenz, Freigabe, Wiederbeanspruchung oder Baseline-Trennung.

## Bester naechster Schritt

S1-HU darf nach dem naechsten `ok weiter` ausschliesslich die atomare
Kopplungs- und Zeitordnungsfrage zwischen abgeschlossenem S/H-Vorzustand,
S1-HP-Ressourcenschritt und S1-HT-Generator statisch auditieren. Ergebnis nur
`ZULASSEN` oder `STOPP`; noch keine Materialratenwerte, Runtime oder Feldlauf.
