# S1-EC46: Statischer Common-Probe-Akzeptanzvertrag

## Ziel

EC46 registriert die numerische Entscheidung fuer den in EC45 definierten
gemeinsamen spaeteren Probe-Beobachtungsraum. Es wird keine Schwelle aus dem
EC44-Ergebnis abgeleitet und kein Feld ausgefuehrt.

## Uebernommene Regeln

EC46 verwendet ausschliesslich bereits im Projekt gebundene Grenzen:

- absolute Null- und Kontrollgrenze `1e-12` aus dem E1-E3-Probevertrag;
- strikte Signalmarge `8 * r4/r8-Rest` aus S1-EC24;
- relative Verfeinerungsgrenze `0.01` aus dem E1-E4-Vertrag.

Die Regeln gelten getrennt fuer Aktivierung und Nachhall. Eine nachtraegliche
Aenderung anhand eines spaeteren Ergebnisses ist gesperrt.

## Kontrollen

Vor jeder positiven technischen Entscheidung muessen alle folgenden
Reihenfolgekontraste hoechstens `1e-12` betragen:

1. P0 nach identischem Feldreset;
2. E1 mit waehrend der Probe deaktivierter Rueckwirkung;
3. E1 mit deaktivierter Bildung.

Eine verletzte Kontrolle macht den Lauf technisch ungueltig.

## Signal und Konvergenz

Fuer Aktivierung und Nachhall muss jeweils gelten:

```text
r8 > max(1e-12, 8 * r4/r8-Rest)
r4/r8-Rest <= r2/r4-Rest
r4/r8-Rest / max(r8, 1e-12) <= 0.01
```

Alle Ungleichungen fuer das Signal sind strikt. Beide Feldkomponenten muessen
die Regel bestehen.

## Technische Entscheidungen

- `INVALID_COMMON_PROBE_CONTROLS`
- `NO_MEASURABLE_COMMON_PROBE_DIFFERENCE`
- `NUMERICALLY_UNDECIDABLE_COMMON_PROBE_DIFFERENCE`
- `NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE`

Auch die letzte Entscheidung bezeichnet nur eine kontrollierte,
zustandsabhaengige spaetere Feldantwort. Sie ist kein Memory-, Feldzeit-,
Organisations- oder KI-Nachweis.

## Ergebnis

Entscheidung:
`ACCEPTANCE_BOUND_REGISTERED_IMPLEMENTATION_MISSING`

Elf fokussierte Tests bestehen. Die Implementierung eines synthetischen
Common-Probe-Runners ist erlaubt. Reale Feldschritte, Persistenz und Claims
bleiben gesperrt.

Vertragsdigest:
`672239cddf2a1e8a8856a5bd2570ebaf0a9bdda5f52fb45aa0306e2570dd144b`

## Naechster Schritt

Am besten geht es mit S1-EC47 weiter: die acht EC45-Rollen und die EC46-
Auswertung nur mit synthetischen, typisierten Probevektoren integrieren.
Dabei werden null reale Feldschritte ausgefuehrt.
