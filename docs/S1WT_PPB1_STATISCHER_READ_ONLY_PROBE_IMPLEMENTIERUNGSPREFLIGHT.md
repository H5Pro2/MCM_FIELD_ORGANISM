# S1-WT: Statischer read-only Probe-Implementierungspreflight

## Auftrag und Grenze

S1-WT prueft ausschliesslich per Quelltext, AST und Digestbindung, ob die
vorhandenen PPB-1-Rollen fuer eine spaetere private read-only Probe
wiederverwendbar sind. Es wurde kein Probe-Code implementiert und keine
Probe-, Zustands- oder Advance-Funktion ausgefuehrt.

Neue Matchregeln, Parameter, Zustandsaenderungen, Feldwirkung, Semantik und
Produktionsintegration sind nicht Bestandteil des Preflights.

## Wiederverwendbare Rollen

Der Bestand stellt alle benoetigten reinen Grundrollen bereit:

- `_validate_state` fuer Konfiguration, Bank, Kapazitaet, Platzanatomie und
  Zaehlergrenzen;
- `_validate_frame` fuer Modalitaet, Geometrie, Traegerordnung, Wertebereich
  und gueltiges Kontaktfenster;
- `normalized_mean_l1_distance` als vorhandene dimensionsnormalisierte
  Distanz;
- `_input_projection` zusammen mit `_digest` fuer den kanonischen
  Probeinputdigest;
- `PPB1BankState.digest` und `PPB1BankConfig.digest`;
- `_state_identity_payload` zusammen mit `_digest` fuer die bereits
  gebundene Bank-/Konfigurations-/Platzidentitaet.

Keine dieser statisch untersuchten Rollen ruft `advance_ppb1_bank` oder den
S1-WQ-Lebenszyklus auf.

## Reine Kompositionsrollen

Drei Regeln liegen nicht als einzelne Helferfunktion vor, sind aber durch
vorhandene Felder und den S1-WS-Vertrag vollstaendig bestimmt:

1. gleiche Clock und Probeende groesser als das letzte gebundene Kontaktende;
2. nur belegte Plaetze mit `support_count >= stable_after`;
3. kleinste Distanz, danach lexikographische Platz-ID.

Diese spaetere Komposition benoetigt weder eine neue Distanz noch eine neue
Schwelle oder einen Parameter. Die Gleichstandsreihenfolge entspricht der
bereits im Referenzkern verwendeten Tupelordnung.

## Statische Entscheidung

Alle `14 von 14` Strukturpruefungen bestehen. Null negative Pruefungen und
folgende Nullzaehler sind gebunden:

```text
probe_function_execution_count = 0
state_function_execution_count = 0
advance_call_count              = 0
new_match_rule_count            = 0
new_parameter_count             = 0
field_effect_count              = 0
```

Die Entscheidung lautet:

```text
PASS_REUSE_COMPLETE_PRIVATE_PROBE_IMPLEMENTATION_ADMISSIBLE
```

Preflightdigest:

```text
1e27f509ab37b785334da34ff833d4dc4184d908bbde7eea694cf29549aa43ae
```

`8 von 8` statische Dokumentstrukturtests bestehen. Sie importieren keine
Projektmodule und fuehren keine Probe aus.

## Verbindliche Implementierungsgrenze

Eine spaetere Implementierung darf nur privat, rein und im Arbeitsspeicher
arbeiten. `advance_ppb1_bank`, Nachzustand, Mutation, oeffentlicher Export,
Snapshotfeld, Produktionseinstieg sowie Datei-, Feld-, Semantik- und
Medienruntime bleiben ausgeschlossen.

Der Preflight bestaetigt die technische Implementierbarkeit dieser Grenze.
Er bestaetigt keine Abruffunktion und keine Memory-Faehigkeit.

## Naechster Schritt

S1-WU kann als private reine In-Memory-Implementierung der S1-WS-Probe mit
ausschliesslich synthetischen Vertragstests freigegeben werden. Sie muss die
gebundenen Rollen direkt wiederverwenden, darf keinen Nachzustand liefern und
muss Vor- und Nachdigest des beobachteten Bankzustands als identisch
nachweisen.

## Grundlagen

- [S1-WS statischer read-only Probevertrag](S1WS_PPB1_STATISCHER_READ_ONLY_PERZEPTIVER_PROBEVERTRAG.md)
- [Maschinenlesbarer S1-WT-Preflight](S1WT_PPB1_STATISCHER_READ_ONLY_PROBE_IMPLEMENTIERUNGSPREFLIGHT_V1.json)
