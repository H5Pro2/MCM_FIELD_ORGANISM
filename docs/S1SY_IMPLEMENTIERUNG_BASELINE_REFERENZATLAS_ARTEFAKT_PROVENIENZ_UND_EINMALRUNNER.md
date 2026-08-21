# S1-SY: Implementierung von Baseline-Referenzatlas, Provenienz und Einmalrunner

## Ergebnis

S1-SY implementiert den in S1-SX gebundenen passiven Realpfad, ohne ihn
auszufuehren. Die bestehende Comparatorarithmetik und ihre Toleranzen
bleiben unveraendert.

Die zuvor gebundene Ausgabeluecke ist geschlossen:

- jedes gueltige Comparatorresultat enthaelt alle 14 vollstaendigen
  320-Komponenten-S/H-Profile;
- jedes der 91 Paare bindet beidseitig Modellkonfiguration, Profildigest
  und alle 40 Checkpointquelldigests;
- der oeffentliche Resultatvalidator prueft Achsen, Digests, Kontraste,
  Residuen, Distanzen, Statuswerte und atomare Fehlerresultate ohne
  Produceraufruf.

## Kanonisches Artefakt

`four_node_baseline_reference_artifact.py` stellt bereit:

- ein getrenntes transitives AST-Quellinventar des Comparatorpfads;
- SHA-256-Bindung der drei festen Eingabedateien;
- kanonische Compact-JSON-Serialisierung mit ASCII, sortierten Schluesseln,
  verbotenen nichtendlichen Zahlen und abschliessendem LF;
- einen strikten Parser mit Feld-, Achsen-, Digest-, Vertrags-, Laufzeit-
  und Eingabekreuzpruefung;
- vollstaendige Profile, 322 Kontraste und 91 Paarrecords ohne Rangfolge
  oder Ergebnisfilterung.

Der Parser rekonstruiert die typisierten Records und validiert ihre
numerischen Beziehungen erneut. Ein unvollstaendiger oder
`AUDIT_INVALID_NOT_COMPUTABLE`-Befund ist nicht publizierbar.

## Geschuetzter Einmalrunner

`four_node_baseline_reference_single_run.py` besitzt genau eine
lexikalische Comparator-Aufrufstelle. Der Runner:

1. prueft Autorisierung, feste Pfade und drei Eingabedateien;
2. validiert S1-SS-Artefakt, Manifest, Registrierung und Fixture;
3. rekonstruiert passiv genau 14 Comparatorprofile;
4. bindet historisches S1-SS- und aktuelles Comparatorquellinventar
   getrennt;
5. schreibt Sperre und `STARTED`-Versuchsnachweis vor dem Comparator;
6. akzeptiert nur den vollstaendigen computable Atlas;
7. stoppt bei Quell- oder Eingabedrift;
8. publiziert kanonische Bytes exklusiv ueber gleichverzeichnisiges
   Staging und Hardlink.

Bei gestartetem Fehler bleiben Versuchsnachweis und Sperre bestehen; ein
Ergebnis oder Teilatlas fehlt. Es gibt keinen Retry, Resume, alternativen
Pfad, Modellproducer, Feldschritt, Netzwerk- oder Geraetezugriff.

## Definierter synthetischer Testkatalog

Genau 20 Tests sind in
`tests/test_four_node_baseline_reference_artifact_and_single_run.py`
definiert. Sie pruefen:

- vollstaendige Profil- und Paarprovenienz;
- Ablehnung manipulierter Resultatidentitaeten;
- deterministische kanonische Artefaktbytes und strikten Roundtrip;
- unbekannte, fehlende, doppelte und nichtkanonische Felder;
- Erhalt der signed Profile, Residuen und Quelldigests;
- deterministisches lokales Quellinventar und feste Eingabedateiachse;
- Vorstartabbruch, feste Laufpfade und einzige CLI-Autorisierung;
- genau einen synthetisch ersetzten Comparatoraufruf;
- gestartete Fehler, Quelldrift und Linkfehler ohne Teilergebnis;
- fehlende direkte Modellproducerimporte.

Die Tests wurden in S1-SY nicht ausgefuehrt. Es wurden nur Python-Syntax,
AST-Testanzahl, Importgrenzen, Comparator-Aufrufstellen und Diffsauberkeit
statisch geprueft. Der reale S1-SS-Dateidigest blieb:

```text
3fdf622a533f0974c93da26591d8d9edccb2fa4bb1fc272f19098015a8e7e066
```

Keiner der vier S1-TB-Laufpfade wurde angelegt.

## Entscheidung und naechster Schritt

```text
BASELINE_REFERENCE_ATLAS_PROVENANCE_ARTIFACT_AND_ONE_SHOT_RUNNER_IMPLEMENTED
TWENTY_SYNTHETIC_TESTS_DEFINED_NOT_EXECUTED
ONE_COMPARATOR_CALL_SITE_ZERO_MODEL_PRODUCER_CALLS
NO_REAL_COMPARATOR_NO_RESULT_NO_FUNCTIONAL_DECISION
```

Der einzige naechste Schritt ist S1-SZ: genau ein unveraenderter Lauf nur
der 20 synthetischen Tests aus
`tests/test_four_node_baseline_reference_artifact_and_single_run.py`.
Kein anderer Test, kein reales S1-SS-Comparing und kein Modellproducer sind
dabei zulaessig.
