# S1-AI: Konjugierte Rueckwirkung des `C_i`-Substrats

Stand: 2026-08-11

Status: `FORMALER_MATERIALENTWURF_KEINE_RUNTIMEFREIGABE`

## Ziel

S1-AI bindet die Rueckwirkung von `C_i` an dieselbe lokale
Akkommodationswirkung, die `C_i` veraendert. Es gibt keinen separaten
Speicherleser.

## Gemeinsamer Austauschterm

Aus der lokalen Feldabweichung

```text
Delta_i = E_i - C_i
```

wird genau ein lokaler Austauschterm gebildet:

```text
J_i = alpha * (1 - C_i^2) * Delta_i
```

Die beiden gekoppelten Rollen lauten:

```text
dC_i/dt =  J_i
dS_i/dt = F_MCM_i - beta * J_i
```

mit `alpha >= 0` und `beta >= 0`.

Der Term `J_i` veraendert also gleichzeitig die Substratdisposition und die
schnelle Feldlage. Das Minuszeichen beschreibt eine technische
Aufnahme-/Rueckgabe-Bilanz: Ein Anteil der lokalen Feldabweichung wird in die
Disposition ueberfuehrt und nicht doppelt als freie Feldaktivierung verbucht.

## Warum dies keine getrennte Speicherregel ist

Unzulaessig waere:

```text
dC_i/dt = eigene Schreibregel
dS_i/dt = fester Leser(C_i)
```

Der vorliegende Entwurf verwendet stattdessen denselben `J_i` fuer Bildung
und Rueckwirkung. Wird `J_i` entfernt, verschwinden beide Rollen gemeinsam.

## Technische Folgerungen

Unter Vernachlaessigung des vorhandenen MCM-Feldterms gilt fuer die lokale
Kombination:

```text
d/dt (S_i / beta + C_i) = 0
```

fuer `beta > 0`. Damit besitzt der Entwurf eine explizite lokale
Austauschbilanz. Diese Bilanz ist eine digitale Materialannahme und kein aus
der bisherigen MCM-Evidenz bewiesenes Naturgesetz.

## Begrenzung

Der Faktor `(1 - C_i^2)` begrenzt die Disposition kontinuierlich auf
`C_i in [-1, 1]`. Es gibt keinen Reset, keinen Speicherbefehl und keinen
festen Zerfallstimer.

Die Begrenzung muss spaeter numerisch invariant bleiben. Clipping,
ereignisabhaengiges Zuruecksetzen oder globale Renormierung waeren keine
zulaessigen Ersatzmechanismen.

## Baseline-Risiko

Der Entwurf ist wahrscheinlich auf bekannte Klassen reduzierbar:

- `beta = 0`: lokaler begrenzter Integrator beziehungsweise leaky Spur;
- konstantes `C_i`: fester Gain oder Leser;
- konstante `alpha`: lineare lokale Austauschkomponente;
- rein lokale unabhaengige `J_i`: Summe lokaler Spuren;
- ortsuebergreifender Austausch: konservierte Transportbaseline;
- feste Kennlinie: Hysterese oder Saettigung.

Der Entwurf erhaelt nur dann eine staerkere Substratrolle, wenn die
gemeinsame lokale Feld-/Substratwirkung trotz dieser Reduktionen ein
reproduzierbares, nichtgleichwertiges Verhalten zeigt.

## Gegenprognosen

Vor einer Implementierung muessen mindestens diese Verlaeufe fest gebunden
werden:

1. `beta = 0` entfernt jede Rueckwirkung auf S.
2. identische Startzustaende und identische Eingaben bleiben digestgleich.
3. homogene `E_i` und passendes `C_i` erzeugen keinen kuenstlichen Drift.
4. bei ausgeschaltetem `J_i` bleibt der bestehende MCM-Nullpfad erhalten.
5. eine reine lokale Wiederholung darf nicht automatisch als Memory gelten.

## Entscheidung

```text
gemeinsamer Term J_i:        formal bestimmt
lokale Austauschbilanz:      formal bestimmt
Baseline-Reduktion:          noch offen
numerische Stabilitaet:      noch nicht geprueft
Runtimeimplementierung:      gesperrt
Memory-Claim:                nein
```

## Bester naechster Schritt

Den Entwurf statisch gegen die vorhandenen leaky-, Integrator-, Gain-,
Hysterese- und F3-Baselines reduzieren. Erst wenn mindestens eine
nichttriviale Gegenprognose uebrig bleibt, darf ein privater technischer
Prototyp vorbereitet werden.
