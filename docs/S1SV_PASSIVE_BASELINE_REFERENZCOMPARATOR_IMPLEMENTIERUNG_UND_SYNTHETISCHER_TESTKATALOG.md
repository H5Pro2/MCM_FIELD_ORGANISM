# S1-SV: Passive Baseline-Referenzcomparator-Implementierung und synthetischer Testkatalog

## Ergebnis

S1-SV implementiert den in S1-SU gebundenen Baseline-Referenzvergleich,
ohne das reale S1-SS-Artefakt numerisch auszuwerten. Die Implementierung ist
in zwei Grenzen getrennt:

- `four_node_baseline_reference_input.py` rekonstruiert aus dem bereits
  validierten Artefakt und seinen digestgebundenen Seiteneingaben genau 14
  unveraenderliche Profile;
- `four_node_baseline_reference_comparator.py` verarbeitet nur diese
  Profile und importiert weder Runner noch Modellkern, Fixture oder
  Lifecycle.

Der Adapter liest keine Dateien, ruft kein Modell auf und erzeugt keinen
Feldzustand. Abweichende Artefakt-, Manifest-, Registrierungs-, Fixture-,
Quellinventar- oder Eingabedateiidentitaeten stoppen die Aufbereitung.

## Gebundene Ausgabe

Der reine Comparator verlangt je Rolle 40 geordnete Checkpoints und damit
320 signed S/H-Komponenten. Er bildet vollstaendig:

```text
14 x 23 = 322 vorregistrierte Rohkontraste
14 x 13 / 2 = 91 ungeordnete Profilpaare
```

Paarresiduen bleiben als 320 signed Werte erhalten. `Linf`, die
symmetrische relative Distanz, `1e-12` Kontrolltoleranz und `0,05`
Profilgrenze sind fest. Es gibt keine Rangfolge und keinen vorzeitigen
Abbruch. Ein Eingabefehler publiziert atomar nur
`AUDIT_INVALID_NOT_COMPUTABLE`, ohne Teilkontraste oder Teilpaare.

Ein gueltiges Paket kann ausschliesslich
`BASELINE_REFERENCE_ATLAS_COMPUTABLE` zusammen mit
`S1PX_CANDIDATE_GATES_NOT_APPLICABLE` liefern. Die Implementierung besitzt
keinen Kandidatenpfad und kann daher keinen Funktionsbefund fuer eine
hypothetische MCM-Memory-Entwicklungsrichtung erzeugen.

## Statische Pruefung und Testsperre

19 synthetische Tests sind definiert. Sie pruefen Vertragsidentitaet,
Cardinalitaeten, Determinismus, Profilmetrik, signed Residuen,
Kontrastordnung, U-Kontrollzuordnung, C-Deltabildung, Provenienz,
Angleichung und atomaren Fehlerfall sowie die Importgrenze des reinen
Comparators.

In S1-SV wurden nur Syntax, AST-Testanzahl, Importgrenzen, Diffsauberkeit
und der unveraenderte SHA-256-Digest des realen S1-SS-Artefakts statisch
geprueft. Die 19 Testmethoden wurden nicht ausgefuehrt. Der Artefaktdigest
blieb:

```text
3fdf622a533f0974c93da26591d8d9edccb2fa4bb1fc272f19098015a8e7e066
```

## Verbindliche Grenze und naechster Schritt

```text
PASSIVE_BASELINE_REFERENCE_COMPARATOR_IMPLEMENTED
NINETEEN_SYNTHETIC_TESTS_DEFINED_NOT_EXECUTED
REAL_S1SS_ARTIFACT_NOT_NUMERICALLY_EVALUATED
NO_CANDIDATE_NO_FUNCTIONAL_DECISION
```

Der einzige naechste Schritt ist S1-SW: genau ein unveraenderter Lauf nur
der 19 synthetischen Tests aus
`tests/test_four_node_baseline_reference_comparator.py`. Kein anderer Test,
kein Modellproducer und keine numerische Auswertung des realen
S1-SS-Artefakts sind dabei zulaessig.
