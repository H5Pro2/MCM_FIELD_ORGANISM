# W7-AR: Reiner numerischer Einmal-Auswerter

## Status

W7-AR ist als privater, deterministischer Auswerter implementiert. Er nimmt
ein vollstaendiges W7-AP-Ergebnis und den unveraenderten W7-AQ-Vertrag an und
wertet alle 70 vorregistrierten S/H-Komponenten gemeinsam aus.

Es wurde kein realer W7-AN/AP-Lauf ausgefuehrt. Die in den Tests verwendeten
Zahlen sind synthetische Vertragsdaten und kein Forschungsbefund.

## Eingangsgrenze

W7-AR akzeptiert nur:

- den kanonischen W7-AN-Provenienzdigest `4f150aad...f3e5`;
- den W7-AO-Vertragsdigest `14455f15...067dc`;
- den privaten W7-AP-Kompositor in unveraenderter Version;
- den W7-AQ-Vertragsdigest `66717c7b...86ee3`;
- genau 70 Rohdistanzen und 105 exakte Identitaetsnullen;
- bestandene Reihenfolge- und kanonisch gebundene Gegenlaufkontrollen;
- ein noch nicht ausgewertetes W7-AP-Ergebnis.

Fehlende Rollen, abweichende Provenienz, nicht endliche Werte oder eine
nicht exakte Identitaetsnull werden als Eingabefehler abgewiesen.

## Komponentenpruefung

Fuer jede der 35 Rollen werden `S_linf` und `H_linf` getrennt geprueft:

```text
converged = D24 < D12 oder (D12 = 0 und D24 = 0)
```

Jede der 70 Pruefungen erhaelt einen eigenen Digest. `SH_l2` bleibt Diagnose
und wird nicht fuer die Entscheidung gelesen. Es gibt keine Mittelung,
Rundung oder Auswahl guenstiger Rollen.

## Ergebnisbildung

Wenn mindestens eine Komponente nicht konvergiert:

```text
outcome = NUMERICALLY_UNRESOLVED
epsilon_num = None
effect_floor = None
```

Nur wenn alle 70 Komponenten bestehen:

```text
outcome = RESOLUTION_COMPARISON_CONVERGED
epsilon_num = max aller D24-Werte
effect_floor = 10 * epsilon_num
```

Wiederholte reine Auswertung desselben unveraenderten Eingangs liefert
denselben Ergebnisdigest. Der Eingang wird nicht veraendert.

## Evidenzgrenze

`field_function_decision_allowed` und `memory_claim_allowed` bleiben in
beiden Ergebniszustaenden `false`. W7-AR ersetzt keine der fehlenden
Funktionsbaselines LEAK, LIN, F3, CONST-V, SAT, MOB, NORM, ETA0, KAPPA0 und
SIGN. Ein konvergierter Aufloesungsvergleich waere nur ein technischer
Numerikbefund.

## Verifikation

Der schnelle W7-AN/AO/AP/AQ/AR-Verbund besteht mit `70 tests, OK`. Geprueft
sind strikte Konvergenz, Nichtkonvergenz ohne Boden, exakte Doppelnull,
vollstaendige Rollenordnung, Determinismus, Eingabepassivitaet,
Manipulationsabweisung und private API-Grenze.

## Naechster Schritt

Vor dem langen realen Lauf sollte W7-AS einen privaten terminalen In-Memory-
Handoff binden: Der fertige W7-AN-Container muss unmittelbar und ohne
Zwischenpersistenz durch W7-AP und W7-AR gefuehrt werden. Dadurch geht das
erneut teuer materialisierte Objekt nicht wie beim ersten W7-AN-Nachweis
nach der Containerpruefung verloren.
