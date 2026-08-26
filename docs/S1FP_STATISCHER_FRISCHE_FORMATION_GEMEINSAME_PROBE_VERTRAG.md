# S1-FP: Statischer Frische-Formation-zu-Gemeinsame-Probe-Vertrag

## Forschungsfrage

Fuehrt ein frisch im selben Prozess gebildeter, numerisch konvergierter
AB/BA-E1-Ordnungszustand unter einer anschliessenden identischen neutralen
AV-Probe zu unterschiedlichen Aktivierungs- oder Nachhallfeldern?

S1-FP verbindet damit zwei bereits getrennt gezeigte technische Teile:

```text
kontrollierte AV-Reihenfolge
-> frisch gebildeter E1-Zustand
-> identischer Feldreset und identische spaetere Probe
-> moegliche zustandsabhaengige Feldantwort
```

Der fruehere S1-DQ-Befund zeigte eine spaetere Feldantwort fuer als gegeben
behandelte Zustaende. S1-FO zeigte die numerisch verfeinerte frische Bildung.
S1-FP darf alte Zustaende, Laufidentitaeten oder Autorisierungen nicht
wiederverwenden. Ein spaeterer Versuch muesste beide Teile in einem neuen
nicht persistenten Prozess verbinden.

## Inventar

Formation:

```text
r2, r4, r8
x
active-ab, active-ba, identity-ab,
formation-ablated-ab, formation-ablated-ba
= 15 E1-Endzustaende
```

Gemeinsame Probe pro Verfeinerung:

```text
p0-reset-ab, p0-reset-ba
e1-active-ab, e1-active-ba
e1-probe-feedback-ablated-ab, e1-probe-feedback-ablated-ba
e1-formation-ablated-ab, e1-formation-ablated-ba
fixed-adapter-ab, fixed-adapter-ba
= 10 Rollen x 3 Verfeinerungen = 30 Probearme
```

Jeder Probearm beginnt mit einem wertidentischen, objektgetrennten frischen
Feld. Probequelle, Supports, Neuronenreihenfolge und Probetakte sind innerhalb
einer Verfeinerung identisch. Der gebildete E1-Zustand bleibt waehrend der
Probe eingefroren.

## Feste Adapterbaseline

S1-DQ zeigte, dass die zustandsabhaengige Feldantwort bitgenau durch den aus
dem E1-Zustand konstruierten festen Kantenadapter erklaert wurde. Diese
Baseline bleibt deshalb verpflichtend. Ein positiver S1-FP-Ausgang darf nicht
als neue Substratnatur bezeichnet werden, wenn aktive und feste Adapterarme
gleich sind.

Die Baseline entwertet den technischen Zustandstraeger nicht. Sie begrenzt
seine Bedeutung: Der E1-Zustand liefert dann eine gebildete Konfiguration fuer
einen bekannten Feldleser, aber noch keine eigenstaendige Memorydynamik.

## Numerische Grenzen

Unveraendert uebernommen werden:

- absolute Kontrollgrenze `1e-12`;
- strikte Signalmarge `8 * r4/r8-Rest`;
- relative Verfeinerungsgrenze `0.01`;
- getrennte Auswertung von Aktivierung und Nachhall.

## Entscheidungen

- `INVALID_FRESH_FORMATION_COMMON_PROBE_CONTROLS`
- `NO_MEASURABLE_FRESH_FORMATION_COMMON_PROBE_DIFFERENCE`
- `NUMERICALLY_UNDECIDABLE_FRESH_FORMATION_COMMON_PROBE_DIFFERENCE`
- `FRESH_FORMATION_COMMON_PROBE_DIFFERENCE_FIXED_ADAPTER_EXPLAINED`
- `FRESH_FORMATION_COMMON_PROBE_DIFFERENCE_NOT_FIXED_ADAPTER_EXPLAINED`

Auch der letzte Ausgang waere zunaechst nur eine technische Abweichung und
muesste gegen Implementierungsfehler sowie weitere Baselines geprueft werden.

## Status und Grenzen

Entscheidung:
`FRESH_FORMATION_COMMON_PROBE_BOUND_IMPLEMENTATION_MISSING`.

Der Vertrag fuehrt keinen Feldschritt aus. Besitzerautorisierung, Ausfuehrung,
Persistenz, Retry und Nachparametrierung fehlen. Er weist weder Memory,
Feldzeit, inneren Kontext, Reaktivierung, Organisation noch KI nach.

## Bester naechster Schritt

S1-FQ soll die 30 Probewege mit bereits typisierten synthetischen
Formationsergebnissen integrieren und Aufrufzahl, Objekttrennung,
Zustandsunveraenderlichkeit, Kontraste und atomare Rueckgabe pruefen. Noch
keine frische reale Formation und keine reale Probe.
