# S1-BA: Restaudit des aktiven Engineeringmanifests

## Status

Statischer Rollen- und API-Audit mit kompatibler Manifestbereinigung. Keine
neue Mechanik, kein Forschungslauf und kein Memory-, Substrat- oder KI-Befund.

## Auftrag

Nach der C_i-Ausgliederung aus S1-AZ wurde jeder Name in
`CURRENT_CONTROLLED_FIELD_EXPORTS` erneut gegen die aktive technische Linie
geprueft:

```text
kontrollierte Audio-/Video-/Browserquelle
-> Rezeptorreduktion und gemeinsame Zeit
-> Verteilung, Docks und transiente Eingabe
-> gemeinsames neutrales S/H-Feld
-> Sitzung, Snapshot und Restore
```

Abgeschlossene Substratkandidaten, Referenzarme, passive Auswertung und
historische Versuchswerkzeuge gehoeren nicht in dieses Kernmanifest.

## Befund

Vor dem Audit enthielt der aktive Kern 131 Rollen. Vier Rollen aus
`controlled_probe_baseline_comparison` vergleichen ausschliesslich bereits
erzeugte Snapshots und schreiben keinen Feldzustand fort:

```text
ControlledProbeComparisonError
ControlledProbeSnapshotComparison
compare_controlled_probe_baseline_set
compare_controlled_probe_snapshots
```

Sie sind passive technische Auswertung, keine aktive Feldoperation. Die vier
Rollen stehen nun getrennt in:

```text
PASSIVE_COMPARISON_EXPORTS
```

`current_api.__all__` enthaelt sie weiterhin. Bestehende Importe bleiben
kompatibel.

## Gepruefte Grenzfaelle

`NeutralLocalFieldSubstrateConfig`, `NeutralLocalFieldSubstrateError` und
`NeutralFastAfterimageConfig` bleiben im aktiven Kern. Trotz des historischen
Namens `substrate` konfigurieren sie den gegenwaertigen neutralen S/H-
Feldschritt und werden von den aktiven AV-Runtimes direkt benoetigt. Sie sind
kein entwickelbares Memorysubstrat.

Kontrollierte Audio-Gates, logarithmische Audiorezeptoren,
Browserpayloadquellen und Browser-Runtimebindungen bleiben ebenfalls im
Kern. Sie erzeugen oder uebergeben kontrollierten Weltkontakt und sind keine
Substrat- oder Auswertungsrollen.

## Ergebnis

```text
aktive Kernrollen vor Audit:          131
passive Vergleiche ausgegliedert:       4
aktive Kernrollen nach Audit:         127
weitere Fehlklassifikationen:           0
entfernte oeffentliche Namen:            0
```

Die vier Referenzbereiche sind jetzt sichtbar getrennt:

```text
PASSIVE_COMPARISON_EXPORTS
CI_REFERENCE_EXPORTS
F3_REFERENCE_EXPORTS
S1B_REFERENCE_EXPORTS
```

Manifesttests sichern die paarweise Trennung vom aktiven Kern und die
fortbestehende Importierbarkeit.

## Aussagegrenze

Der Audit bewertet nur API-Rollen. Er bestaetigt keine Wahrnehmung im
psychologischen Sinn, keine Praegung, kein Lernen, keine Feldzeit und kein
MCM-Memory.

## Bester naechster Schritt

Die aktive Oberflaeche ist nach diesem Audit sauber klassifiziert. Als
naechstes wird die kleinste aktuelle End-to-End-AV-Kette ausschliesslich aus
`CURRENT_CONTROLLED_FIELD_EXPORTS` erneut als Architekturgrenze gebunden.
Dabei wird kein neuer Versuch ausgefuehrt; zuerst wird geprueft, ob der
bestehende Consumer diese engere Kernmenge bereits einhaelt.

