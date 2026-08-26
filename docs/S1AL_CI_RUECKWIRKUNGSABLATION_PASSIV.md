# S1-AL: Passive `C_i -> S`-Rueckwirkungsablation

Stand: 2026-08-11

Status: `TECHNISCHE_PROJEKTION_KEINE_FELDRUECKSCHREIBUNG`

## Umfang

Die passive `C_i`-Baseline wurde ueber die vier Phasen der synthetischen
Weltfamilie gefuehrt. Fuer jeden Snapshot wurden zwei Auswertungen gebildet:

```text
Rueckwirkung aus:  originale S-Aktivierung
Rueckwirkung an:   originale S-Aktivierung + dt * C_i-Backreaction
```

Die projizierte Aktivierung wurde nicht in den naechsten gemeinsamen
MCM-Feldschritt zurueckgeschrieben. Es handelt sich daher um eine getrennte
technische Ablation und nicht um eine vollstaendige gekoppelte Runtime.

Konfiguration:

```text
alpha = 0.5
beta  = 1.0
dt    = 0.1
```

## Ergebnisse

```text
world.history.same
feedback_digest = 0bf9c7df0acce21dcba800f0cd3f72aa5699c01dfa7121d528406831845f16a9
max_projection_linf = 0.010967644104282137

world.history.changed
feedback_digest = cb7922aaebbab05cddfe4c7261c6abab37ad4d01c86faf2ccea4ef46123cc687
max_projection_linf = 0.013446040948330462
```

## Einordnung

Der Test zeigt nur, dass der definierte technische `C_i`-Rueckwirkungsvektor
die aktuelle Aktivierung numerisch veraendert. Er zeigt noch nicht, dass die
veraenderte Aktivierung die naechste Feldaufnahme veraendert, weil keine
Rueckschreibung in die folgende Feldphase erfolgte.

Damit ist noch kein Nachweis von:

- Memory oder Lernen;
- spaeterer selbststaendiger Anpassung;
- Feldzeit, innerem Kontext oder Organisation;
- einer neuen MCM-Natur.

## Entscheidung

```text
passive Rueckwirkungsprojektion:  technisch reproduzierbar
Rueckschreibung in S-Runtime:    noch nicht ausgefuehrt
Memory-Claim:                     nein
```

## Bester naechster Schritt

Eine isolierte End-to-End-Ablation vorbereiten, in der Rueckwirkung an und
Rueckwirkung aus dieselbe naechste synthetische Probe erhalten und die beiden
Folgesnapshots verglichen werden. Dieser Schritt benoetigt eine eigene
technische Freigabe fuer die gekoppelte `C_i -> S`-Runtime.
