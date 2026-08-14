# S2-C14: Unveraenderlicher n=8-A/B-Skalarcontainer

Stand: 2026-08-07

Status: `S2C14_IMMUTABLE_N8_AB_SCALAR_CONTAINER_BOUND`

Differenzmetrik: nein

Forschungsentscheidung: nein

Forschungslauf: nein

## Zweck

S2-C14 fuehrt genau zwei bereits typisierte n=8-Paarergebnisse in einem
unveraenderlichen In-Memory-Container zusammen:

```text
A: S2R8C8PairResult
B: S2R8BC8BPairResult
```

Es werden keine Welten ausgefuehrt, keine Trajektorien neu berechnet und
keine A/B-Differenz gebildet.

## Containervertrag

`S2N8ABScalarContainer` bindet:

- denselben Modellarm B0 oder B2;
- denselben Kopplungswert;
- identische Probe- und Probeplan-Digests;
- identischen Supportumfang;
- getrennte kollisionsfreie Quellpaar-Digests fuer A und B;
- benannte Skalare `a_d_pair` und `b_d_pair`.

Die Quellpaar-Digests enthalten Paartyp, Formationsdigests, Modellarm,
Probe-Provenienz, Support und Skalar. A und B bleiben dadurch auch bei
`D_pair=0` unterscheidbar.

`assemble_s2c14_n8_ab_scalar_container` akzeptiert die Paartypen nur in der
Reihenfolge A8, B8. B0 verlangt fuer beide Skalare exakt null.

## Bewusst fehlende Funktionen

Der Container besitzt keine Felder fuer:

- Differenz oder Delta;
- Weltspezifitaet;
- Entscheidung;
- Bedeutung oder Semantik;
- Memory oder Organisation.

## Technische Pruefung

`tests/test_s2c14_n8_ab_scalar_container.py` prueft sechs Invarianten:

1. zwei exakte B0-Nullskalare und fehlende Auswertungsfelder;
2. benannte deterministische B2-Skalaruebernahme;
3. Abweisung gemischter Modellarme;
4. Abweisung unterschiedlichen Probe-Supports;
5. Abweisung vertauschter Paartypen;
6. Abweisung eines nichtnulligen direkten B0-Containers.

Die C12-Provenienztests wurden wegen der Digest-Erweiterung gemeinsam
ausgefuehrt.

```text
neue S2-C14-Suite:                 6 passed
C12/C14 gemeinsam:               12 passed
direkter S1-B/S2-Testverbund:    104 passed
Python-Kompilation:               bestanden
```

Die bekannte Pytest-Cachewarnung hat keinen Einfluss auf die Ergebnisse.

## Aussagegrenze

C14 zeigt nur, dass zwei getrennte Weltpaar-Skalare mit gemeinsamer
Provenienz technisch nebeneinander gebunden werden koennen. Der Container ist
kein A/B-Befund und keine Evidenz fuer Weltspezifitaet, Praegung, Memory,
Feldzeit, Organisation, Bedeutung oder KI.

## Bester naechster Schritt

S2-C16 bindet die kanonische technische End-to-End-Komposition bis zur
inzwischen implementierten Observermetrik:

```text
D_world_pair(8) = abs(D_pair_A(8) - D_pair_B(8))
```

B0 muss exakt null bleiben. B2 darf nur als lineare
Referenzcharakterisierung ausgegeben werden. Keine Ergebnisdatei, Schwelle, Entscheidung,
Weltspezifitaets- oder Semantikbehauptung, Intervention, Vollmatrix,
Persistenz oder Laufnummer.
