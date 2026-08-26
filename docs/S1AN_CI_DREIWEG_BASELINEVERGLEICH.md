# S1-AN: Dreiwegvergleich `C_i`, leaky und F3

Stand: 2026-08-11

Status: `TECHNISCHER_BASELINEVERGLEICH_KEIN_MEMORYBEFUND`

## Umfang

Die gekoppelte `C_i`-Engineeringbaseline wurde mit leaky und F3 ueber die
identischen vier synthetischen AV-Phasen verglichen:

```text
contact.0 -> gap.0 -> contact.1 -> probe.0
```

Die `C_i`-Rueckwirkung wurde zwischen den Phasen in den technischen
Feldzustand projiziert. Leaky und F3 wurden mit demselben transienten
Rezeptorbatchpfad ausgefuehrt.

## Ergebnisse

```text
world.history.same
ci    = e657cb03f900a6fef87f91520da17954c83d9c6f6e873f2ccb4e7785bab1f46d
leaky = 72c7343ff0d76b34552c2e4fb36658770d5a8c682db9f8661b8525ad84671d56
f3    = 13311b4f7048c6ace79a0e1b0b1879aee5d9b6ea035e1d643cdf74d6047a456d

ci_vs_leaky = 0.013002853092802719
ci_vs_f3    = 0.012423582827629315
leaky_vs_f3 = 0.0005792702651734039

world.history.changed
ci    = 5c84edb93b24b5f74943cdf709f799eb969d6971e1f40c7208735d076d9cfca7
leaky = bebb5e2c04d361e5c234602f5f5ab19b554870ae51944cb8ca70c34cb42599ca
f3    = 02ceb46be533d1e0ba5f4eac7717fe39f65a44b195b3320022ae9e2aec711f04

ci_vs_leaky = 0.01368948173896195
ci_vs_f3    = 0.013248770208198424
leaky_vs_f3 = 0.0006914457616601366
```

## Einordnung

Die `C_i`-Baseline erzeugt in diesem technischen Pfad andere spaetere
Aktivierungszustaende als leaky und F3. Leaky und F3 sind in diesem Vergleich
nahe beieinander.

Das Ergebnis zeigt nur eine numerische Modell- und Trajektoriendifferenz. Es
zeigt nicht:

- dass `C_i` besser oder biologischer ist;
- dass `C_i` Memory, Lernen oder Vergessen besitzt;
- dass die MCM als Naturwirkprinzip bestaetigt ist;
- dass eine feldbasierte KI entstanden ist.

## Offene technische Fragen

1. Ist die `C_i`-Differenz stabil gegen Parameter- und Zeitschrittvariation?
2. Bleibt sie bei gleichen Budgets und gleicher Anfangsgeometrie erhalten?
3. Welche Differenz bleibt nach strenger Angleichung von S/H uebrig?
4. Ist die Differenz durch die Form des Austauschterms oder nur durch seine
   staerkere Rueckwirkung erklaert?
5. Welche gleich budgetierte leaky-, Integrator- und F3-Parameterwahl ist
   als faire Gegenbaseline verbindlich?

## Entscheidung

```text
C_i technisch unterscheidbar:   ja
C_i als neue Substratnatur:     nein
C_i als Engineeringbaseline:   ja
Memory-Claim:                   nein
```

## Bester naechster Schritt

Eine Parameter- und Zeitschrittrobustheitspruefung mit unveraenderten
Gegenbaselines durchfuehren. Erst danach darf beurteilt werden, ob die
Differenz eine stabile Materialeigenschaft oder nur eine
Konfigurationswirkung ist.
