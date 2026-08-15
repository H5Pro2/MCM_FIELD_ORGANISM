# S1-GT: Synthetischer Einmaltoken-Lebenszyklus

Stand: 2026-08-15

Status: `SYNTHETISCHE_TOKEN_FIXTURE_REAL_GATE_GESCHLOSSEN`

## Umsetzung

S1-GT implementiert einen prozesslokalen Token ausschliesslich fuer eine
synthetische Fixture. Die Fixture ist ausdruecklich keine externe
Besitzerfreigabe und kann weder einen realen Token noch eine Ausfuehrung
autorisieren.

Der Token besitzt folgende Lebenswege:

```text
synthetischer Erfolg: issued -> consumed -> retired
synthetischer Fehler: issued -> retired
synthetischer Fehler: issued -> consumed -> retired
```

Wiederholter Verbrauch, erneute Stilllegung und Erfolg ohne vorherigen
Verbrauch brechen fail-closed ab. Der Token kann nicht kopiert, tief kopiert
oder serialisiert werden. Eine globale Tokenregistrierung oder Persistenz gibt
es nicht.

## Abnahme

- Erfolgs- und beide Fehlerpfade enden stillgelegt;
- Replay nach Verbrauch und Stilllegung wird abgewiesen;
- Kopie, Deepcopy und Serialisierung werden abgewiesen;
- null Adapteraufrufe;
- null Feldschritte;
- keine Besitzerfreigabe und kein realer Token.

Entscheidung:

```text
SYNTHETIC_SINGLE_USE_TOKEN_LIFECYCLE_VALIDATED_REAL_GATE_CLOSED
```

Dies ist eine technische Gate-Fixture, kein Feld-, Substrat- oder
Memory-Befund.

## Bester naechster Schritt

S1-GU bindet statisch den spaeteren Real-Transition-Builder zwischen dem
einzigen Kernelrueckgabefeld und dem S1-GQ-Real-Transition-Schema. Es werden
nur Eingaben, Nachbedingungen und Fehlergrenzen festgelegt; kein Feldkernel
und keine Besitzerfreigabe werden ausgefuehrt.
