# S1-EC10: Kleine reale r2/r4/r8-Refinementmatrix

## Status

```text
SMALL_REAL_REFINEMENT_MATRIX_ACCEPTED
RESIDUAL_DECREASE_OBSERVED
NO_CANONICAL_EXECUTION
NO_MEMORY_CLAIM
```

S1-EC10 fuehrt die reale Fuenf-Arm-Formation aus S1-EC9 auf derselben
kleinen Zwei-Dock-In-Memory-Fixture mit echten completion-aligned
Schrittfolgen fuer `r2`, `r4` und `r8` aus. Die Untersuchung persistiert
nichts und beruehrt keine kanonischen Laufpfade.

## Implementierung

```text
mcm_field_organism/e1_confirmation_small_refinement_matrix.py
tests/test_e1_confirmation_small_refinement_matrix.py
```

## Rohwerte

```text
Schrittzahlen:
r2 = 4
r4 = 8
r8 = 16

AB/BA-Zustandsabstand:
r2 = 0.042777145652345056
r4 = 0.04154048303838301
r8 = 0.04319945232129818

Verfeinerungsrest ueber alle fuenf Arme:
r2 -> r4 = 0.039194601584206512
r4 -> r8 = 0.019481843726620207

convergence_nonincreasing = true
result_digest = 688a8fb04911b8982dd7fc2b639812727ca3e43a4c0a0db6c3887070e938d240
```

Der Verfeinerungsrest nimmt in dieser kleinen Matrix um etwa die Haelfte ab.
Der AB/BA-Zustandsabstand bleibt zugleich auf allen drei Stufen von null
getrennt. Seine leichte Nichtmonotonie ist kein Fehler: Vorregistriert war
die Abnahme des stufengleichen numerischen Verfeinerungsrests, nicht eine
monotone Entwicklung der AB/BA-Effektgroesse.

## Bestaetigte Kontrollen

- jede Refinementstufe verwendet die reale Fuenf-Arm-Komposition;
- AB-Identitaetswiederholung und neutrale Ablationen bestehen auf allen
  drei Stufen;
- Ausgangszustaende bleiben objektgetrennt;
- Feldkontrollen ohne History-Rueckwirkung stimmen ueberein;
- das lokale Ressourcenbudget bleibt erhalten;
- die vorbereiteten Eingaben bleiben digestidentisch;
- die gesamte Matrix ist deterministisch wiederholbar;
- kanonische Ausfuehrung und fachliche Claims bleiben explizit gesperrt.

## Verifikation

```text
48 passed
```

Der gemeinsame S1-EC1-bis-S1-EC10-Testverbund besteht. Die einzige Warnung
betrifft den nicht beschreibbaren Pytest-Cache und nicht die Forschungskette.

## Evidenzgrenze

S1-EC10 bestaetigt nur, dass der reale kleine Formationskern bei zunehmender
zeitlicher Aufloesung kontrolliert ausfuehrbar ist und in dieser Fixture einen
sinkenden stufengleichen Verfeinerungsrest zeigt. Die kleine Fixture ersetzt
weder die vollstaendige vorbereitete AV-Eingabe noch eine kanonische
Bestaetigung. Sie belegt kein MCM-Memory, keine Organisation, Semantik,
Topologie, Selbstregulation oder KI.

## Bester naechster Schritt

S1-EC11 sollte den realen kleinen r2/r4/r8-Formationskern hinter den bereits
vorbereiteten S1-EC7-Consumer und den temporaeren S1-EC3-Laufvertrag binden.
Damit wird erstmals der korrigierte Lebenszyklus Ende-zu-Ende mit realer,
aber weiterhin kleiner Formation geprueft. Persistenz, kanonische Pfade,
Probe und fachliche Claims bleiben gesperrt.
