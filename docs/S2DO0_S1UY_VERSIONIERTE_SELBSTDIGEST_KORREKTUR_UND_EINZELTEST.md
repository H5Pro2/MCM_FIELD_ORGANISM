# S2-DO0: Versionierte S1-UY-Selbstdigestkorrektur

## Auftrag und Grenze

S2-DO0 korrigiert ausschliesslich den veralteten Selbstdigest des aktiven
S1-UY-Driftaudits. Das historische V1-Artefakt bleibt unveraendert. Eine neue
V2-Fassung bindet die endgueltige Testquelle, und genau die betroffene aktive
Testmethode wurde einmal erneut ausgefuehrt.

Es gab keine Aenderung an TSPM-1, PPB-1, Memory-Funktionen, Feldpfad,
Snapshot, API oder Produktionslogik.

## Ursache

`S1UY_ACTIVE_CORE_DRIFT_CONTRACT_V1.json` band fuer
`tests/test_active_engineering_surface_boundary.py` den Digest
`7ece494d2ee1d2be21188f75b068adcfa9b08a6b85be7c1ef48ccfcc7f573187`.
Dieser Wert gehoerte zu einer Zwischenfassung. Die spaeter eingecheckte
Endfassung besass deshalb keinen reproduzierbaren Ruecklauf gegen V1.

Das ist ein historischer Belegfehler und keine Abweichung des aktiven
Feldkerns.

## Versionierte Korrektur

V1 bleibt mit seinem kanonisch gueltigen Artefaktdigest
`e20980b561645bb7c12d863bdd7589c428a3ad8090df2dfbc1c6d5ba4fc62680`
erhalten.

V2 liegt unter `docs/S1UY_ACTIVE_CORE_DRIFT_CONTRACT_V2.json` und:

- verweist mit `supersedes_artifact_digest` auf V1;
- traegt die Vertragskennung `mcm.s1uy.active-core-drift-contract.v2`;
- bindet den endgueltigen Testdigest
  `77e017d9d481527aac0a085a6fd80c76482fdcd53f9802afde50548fbfdd9a63`;
- behaelt alle vier Produktquellbindungen, Driftgates, geschlossenen Familien
  und Architekturgrenzen unveraendert;
- besitzt den kanonischen Artefaktdigest
  `c1ce338680dcf84689ae958074e0a7218f39761086314a52434a83290ea99ecb`.

Der betroffene Test liest nun ausschliesslich V2. Dadurch ist der
Testquelldigest vor der Artefakterzeugung stabil gebunden und nicht
zirkulaer.

## Einzeltest

Ausgefuehrt wurde genau:

```text
python -m unittest tests.test_active_engineering_surface_boundary.ActiveEngineeringSurfaceBoundaryTests.test_machine_readable_drift_contract_matches_active_boundary -v
```

Ergebnis:

- `1/1` Test bestanden;
- Exit-Code `0`;
- terminales `OK`;
- keine weitere aktive oder historische Testmethode ausgefuehrt.

## Unveraenderte Grenzen

Der Git-Diff gegen den S2-DO0-Vorzustand ist fuer
`_tspm1_private.py`, `_ppb1_reference.py`, `current_api.py` und
`shared_mcm_field.py` leer. Die Korrektur betrifft ausschliesslich die neue
V2-Datei, zwei konstante V1-zu-V2-Testbindungen und diesen Pruefbeleg.

## Entscheidung

`PASS_S2DO0_VERSIONED_S1UY_SELF_DIGEST_CORRECTION_1_OF_1`

S1-UY ist fuer den aktiven Pruefpfad wieder reproduzierbar. Der Befund ist
eine technische Belegkorrektur und weder ein Memory- noch ein
MCM-Feldnachweis.

## Naechster Schritt

S2-DO kann nun als separat freigegebener statischer Funktions- und
Baselinevergleichsvertrag fuer TSPM-1 beginnen. Noch nicht freigegeben sind
Vergleichsimplementierung, Ausfuehrung oder Feldintegration.
