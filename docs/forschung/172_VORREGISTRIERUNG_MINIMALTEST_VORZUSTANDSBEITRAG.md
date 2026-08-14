# Vorregistrierung Minimaltest Vorzustandsbeitrag

## Entscheidung und Grenze

Diese Vorregistrierung beschreibt einen spaeteren synthetischen Minimaltest des
isolierten Vorzustands-Hooks. Sie implementiert keinen Runner und fuehrt keinen
Effektlauf aus. `H0`, `H1` und `H2` sind Hypothesen; `P` ist ein technischer
Permutationsarm und keine vierte Hypothese.

Der Test betrifft ausschliesslich die Frage, ob ein Unterschied in einer
spaeteren gemeinsamen Feldaufnahme technisch vom schnellen Vorzustandsbeitrag
abhaengt. Er prueft kein Memory, keine Organisation, Bedeutung, Semantik,
Eigenstaendigkeit oder KI.

## Fixierter Untersuchungsgegenstand

```text
runtime_path:          advance_neutral_fast_shared_field
research_control:      advance_with_previous_state_operator
state_components:      activation, afterimage
operators:             None, identity, zero
dissipation_config:    None
public_av_allowed:     false
production_switch:     false
field_parameters:      identical_between_all_arms
```

Die vorhandenen Dissipationsaenderungen sind nicht Teil dieses Tests. Vor einer
Ausfuehrung muss ein Quellstand festgeschrieben werden, in dem Hook-Patch und
Dissipationspatch getrennt identifizierbar sind. Jeder Lauf mit einer
`dissipation_config` ungleich `None` ist fuer diesen Minimaltest ungueltig.

## Hypothesenstruktur

### H0 - kein nachweisbarer Vorzustandsbeitrag

Bei identischer spaeterer Rezeptorverteilung, identischem Zeitschritt und
identischen Feldparametern sind die spaeteren Aktivierungs- und
Nachhallvektoren der beiden unterschiedlichen Vorgeschichten im `None`-Arm
exakt gleich. Der Nulloperator erzeugt dann keine zwischen den Vorgeschichten
liegende Differenz, die kausal dem Vorzustand zugeordnet werden kann.

### H1 - technische Geschichtsabhaengigkeit im Vollzustand

Die beiden unterschiedlichen Vorgeschichten erzeugen bei identischer spaeterer
Rezeptorverteilung im `None`-Arm unterschiedliche spaetere Aktivierungs- oder
Nachhallvektoren. Die Differenz muss bei Wiederholung deterministisch sein und
darf nicht durch ungleiche aktuelle Kontakte, Zeiten, Geometrien oder Parameter
erklaert werden.

H1 allein belegt nur Zustandsabhaengigkeit. Sie belegt weder Memory noch eine
neue Organismusfunktion.

### H2 - kausale Zuordnung zum isolierten Vorzustandsbeitrag

Die unter H1 beobachtete zwischenhistorische Differenz verschwindet im
`zero`-Arm bis zur vorab festgelegten numerischen Gleichheitstoleranz, waehrend
`identity` bitgleich zu `None` bleibt. Generator, Boundary-Term, Zeitschritt,
Rezeptorverteilung und Fortschreibung muessen dabei identisch bleiben.

H2 ist nur interpretierbar, wenn H1 erfuellt ist und alle Isolationspruefungen
bestehen.

### P - Permutationsgegenbaseline

Die beiden Vorgeschichten werden zwischen neutral benannten Zweigen vertauscht,
ohne Ereignisse, Zeiten oder Werte innerhalb einer Geschichte zu aendern. Die
spaeteren Vollzustandsausgaben muessen mit der Vorgeschichte mitwandern. Im
`zero`-Arm muessen die Ausgaben weiterhin zwischen den Zweigbezeichnungen
gleich sein.

P prueft Zweig-, Reihenfolge- und Aufbauartefakte. P darf nicht zur Auswahl
einer guenstigen Geschichte nach Sichtung der Ergebnisse verwendet werden.

## Arme und Gegenbaselines

| Arm | Vorgeschichte | Spaeterer Kontakt | Operator | Zweck |
| --- | --- | --- | --- | --- |
| `history_a.none` | A | C | `None` | Vollzustand A |
| `history_b.none` | B | C | `None` | Vollzustand B |
| `history_a.identity` | A | C | `identity` | Hook-Aequivalenz A |
| `history_b.identity` | B | C | `identity` | Hook-Aequivalenz B |
| `history_a.zero` | A | C | `zero` | Vorzustand neutralisiert A |
| `history_b.zero` | B | C | `zero` | Vorzustand neutralisiert B |
| `equalized_a.none` | A | C | `None` | identische Wiederholung A |
| `equalized_b.none` | A | C | `None` | Zweigbaseline ohne Geschichtsdifferenz |
| `permuted_a.none` | B | C | `None` | P: Geschichte B unter Zweig A |
| `permuted_b.none` | A | C | `None` | P: Geschichte A unter Zweig B |
| `permuted_a.zero` | B | C | `zero` | P: neutralisierter Vorzustand unter Zweig A |
| `permuted_b.zero` | A | C | `zero` | P: neutralisierter Vorzustand unter Zweig B |

A und B muessen vorab als inhaltsneutrale synthetische Kontaktfolgen fixiert
werden. Sie muessen dieselbe Ereignisanzahl, Dauer, Kontaktstaerkensumme,
Geometrie und Modalitaetsbelegung besitzen. Nur die zeitlich-raeumliche Folge
darf verschieden sein. C ist in allen Armen bytegleich.

Jeder Arm beginnt mit einem frisch konstruierten Feld. Snapshots duerfen nicht
zwischen Armen weiterverwendet werden.

### Determinismus-Replikationsregel

Jeder in der Tabelle aufgefuehrte Arm wird genau zweimal als unabhaengiges
Replikat ausgefuehrt. Die kanonischen Lauf-IDs entstehen ausschliesslich durch
die Suffixe `.r1` und `.r2`, zum Beispiel `history_a.none.r1` und
`history_a.none.r2`. Beide Replikate verwenden bytegleiche Kontaktfolgen,
Konfigurationen, Geometrien und Zeitvertraege, beginnen aber jeweils mit einem
neu konstruierten Feld. Es gibt keine Seedvariation und keine
Ergebnisabhaengigkeit der Ausfuehrungsreihenfolge.

Fuer jeden Arm muessen die Snapshot-Digests an M0, M1, M2 und M3 zwischen
`.r1` und `.r2` bitgleich sein. Ein einzelner Replikationsfehler macht den
gesamten Minimaltest technisch unentscheidbar.

## Messpunkte

```text
M0: nach frischer Feldkonstruktion
M1: nach Abschluss der Vorgeschichte, vor C
M2: unmittelbar vor dem Integrator fuer C
M3: unmittelbar nach der Feldfortschreibung fuer C
```

An jedem Messpunkt werden nur technische Rollen erfasst:

- Snapshot- und Layer-Digest;
- Aktivierungsvektor und Nachhallvektor;
- Feldtick und gemeinsames Zeitfenster;
- Digest der Rezeptorverteilung;
- Generator-, Boundary- und Geometrie-Digest, sofern bereits als neutrale
  Messrolle vorhanden;
- paarweise `L-inf`-Differenzen fuer Aktivierung und Nachhall;
- exakte Digest-Gleichheit fuer Wiederholung, `None` und `identity`.

Es werden keine Labels, Klassen, Rewards, Bedeutungsmetriken, Memory-Scores,
Organisation-Scores oder Zieltopologien eingefuehrt.

## Vorab festgelegte Auswertung

```text
identity_equivalence:
  snapshot_digest(identity) == snapshot_digest(None)

determinism:
  for every arm and M0..M3:
    snapshot_digest(arm.r1) == snapshot_digest(arm.r2)

history_difference:
  activation_linf(A.none, B.none) > numeric_zero
  or afterimage_linf(A.none, B.none) > numeric_zero

zero_isolation:
  activation_linf(A.zero, B.zero) <= numeric_zero
  and afterimage_linf(A.zero, B.zero) <= numeric_zero

permutation:
  digest(permuted_a.none) == digest(history_b.none)
  and digest(permuted_b.none) == digest(history_a.none)
  and activation_linf(permuted_a.zero, history_b.zero) <= numeric_zero
  and afterimage_linf(permuted_a.zero, history_b.zero) <= numeric_zero
  and activation_linf(permuted_b.zero, history_a.zero) <= numeric_zero
  and afterimage_linf(permuted_b.zero, history_a.zero) <= numeric_zero
```

`numeric_zero` ist verbindlich auf `1e-12` festgelegt, bei `rtol = 0.0`.
Dieser Wert entspricht der bereits verwendeten technischen Gleichheitsgrenze
der synchronen Feldvorregistrierung 027 und liegt oberhalb der dort und in den
aktuellen Invariantentests beobachteten Float64-Rundungsreste. Er darf nach
einem Ergebnis nicht veraendert werden. Digest-Gleichheit bleibt bitgenau.

Entscheidungslogik:

- H0 wird nicht verworfen, wenn im `None`-Arm keine zwischenhistorische
  Differenz oberhalb `numeric_zero` vorliegt.
- H1 ist technisch gestuetzt, wenn die Vollzustandsdifferenz deterministisch
  vorliegt und alle Gleichheitsbaselines bestehen.
- H2 ist technisch gestuetzt, wenn zusaetzlich die zwischenhistorische
  Differenz im `zero`-Arm verschwindet und P exakt mitwandert.
- Ein Fehlschlag von `identity_equivalence`, Determinismus, Equalized-Baseline
  oder P macht den gesamten Test unentscheidbar.

## Abbruch- und Ungueltigkeitskriterien

Der spaetere Lauf ist vor Auswertung abzubrechen und als technisch ungueltig zu
markieren, wenn mindestens eines gilt:

- Hook oder Hook-Test ist nicht derselbe festgeschriebene Quellstand;
- Dissipation ist aktiviert oder Hook- und Dissipationspatch sind nicht
  getrennt identifizierbar;
- `None` und `identity` sind nicht bitgleich;
- eine deterministische Wiederholung weicht im Snapshot-Digest ab;
- ein Arm besitzt nicht genau die beiden vorgeschriebenen Replikate `.r1` und
  `.r2` oder ein Replikat beginnt nicht mit einem frisch konstruierten Feld;
- A und B unterscheiden sich in Budget, Dauer, Geometrie, Modalitaeten oder
  aktuellem Kontakt C;
- Generator, Boundary-Term, Feldzeit oder Rezeptorverteilung unterscheiden
  sich zwischen Operatorarmen;
- ein Arm verwendet Reset, veraenderte Projektion, Diffusion, Daempfung,
  Nachhallparameter, Zustandsfortschreibung oder Messpfad;
- nicht-finite Werte oder Verletzungen des normalisierten Feldbereichs treten
  auf;
- die Equalized-Baseline erzeugt eine zwischen Zweigen liegende Differenz;
- ein Ergebnis wird vor Abschluss aller Arme eingesehen und zur Anpassung von
  A, B, C, `numeric_zero` oder Messpunkten verwendet.

## Sperren

```text
runner_implementation_allowed: false
effect_run_allowed:            false
public_av_run_allowed:         false
production_switch_allowed:     false
dynamics_change_allowed:       false
positive_effect_required:      false
memory_claim_allowed:          false
meaning_claim_allowed:         false
organization_claim_allowed:    false
ai_claim_allowed:              false
```

## Naechster ausfuehrbarer Auftrag

Pruefe diese Vorregistrierung auf logische Vollstaendigkeit, eindeutige
Armzuordnung, Konfundierungsfreiheit und Vereinbarkeit mit dem isolierten Hook.
Noch keinen Runner implementieren und keinen Effektlauf ausfuehren.
