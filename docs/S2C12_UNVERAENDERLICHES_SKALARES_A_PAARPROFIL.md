# S2-C12: Unveraenderliches skalares A-Paarprofil

Stand: 2026-08-07

Status: `S2C12_IMMUTABLE_SCALAR_A_PAIR_PROFILE_BOUND`

Forschungsentscheidung: nein

Forschungslauf: nein

Persistiertes Ergebnisprofil: nein

## Zweck

S2-C12 bindet eine reine In-Memory-Zusammenfuehrung der bereits typisierten
A-Paarergebnisse fuer n=1, 2, 4 und 8. Es werden keine Welten erzeugt, keine
Feldtrajektorien neu berechnet und keine Skalarwerte interpretiert.

## Profilvertrag

`S2APairProfile` enthaelt ausschliesslich:

- Modellarm B0 oder B2;
- Kopplungswert;
- gemeinsame Probe- und Probeplan-Digests;
- gemeinsamen Supportumfang;
- vier `S2APairProfileEntry` in fester Reihenfolge `(1, 2, 4, 8)`;
- je Eintrag einen Quellpaar-Digest und genau eine `d_pair`-Metrik.

`assemble_s2c12_a_pair_profile` akzeptiert nur:

```text
S2C1IdentityControl
S2R2C2PairResult
S2R4C4PairResult
S2R8C8PairResult
```

Alle vier Ergebnisse muessen denselben Modellarm und denselben Probe-Support
tragen. B0 muss `(0,0,0,0)` bleiben. `D_pair(1)` muss auch fuer B2 exakt null
bleiben, weil n=1 die Identitaetskontrolle ist.

## Bewusst fehlende Funktionen

Das Profil besitzt keine Felder oder Methoden fuer:

- Trend;
- Steigung oder Fit;
- Entscheidung;
- Wiederholungsnachweis;
- Memory-, Feldzeit- oder Organisationsinterpretation;
- Persistenz oder Ergebnisdatei.

Die unterschiedlichen n-Stufen tragen unterschiedliche Kontaktbudgets. Eine
spaetere Betrachtung ueber n waere daher hoechstens Dosischarakterisierung.

## Technische Pruefung

`tests/test_s2c12_a_pair_profile.py` prueft:

1. exaktes B0-Nullprofil und fehlende Trend-/Entscheidungsfelder;
2. geordnete, deterministische B2-Skalaruebernahme;
3. Abweisung gemischter Modellarme;
4. Abweisung unterschiedlichen Probe-Supports;
5. Abweisung vertauschter Paartypen;
6. Abweisung eines nichtnulligen direkten B0-Profils.

```text
neue S2-C12-Suite:                 6 passed
direkter S1-B/S2-Testverbund:     91 passed
Python-Kompilation:               bestanden
```

Die Tests verwenden typisierte technische Skalarobjekte. Sie erzeugen kein
persistiertes Profil mit Forschungswerten. Die bekannte Pytest-Cachewarnung
hat keinen Einfluss auf die Ergebnisse.

## Aussagegrenze

C12 zeigt nur, dass vier bereits gebundene Paarergebnisse konsistent und
unveraenderlich zusammengefuehrt werden koennen. Daraus folgt kein
empirischer Verlauf und keine Aussage ueber Praegung, organisches Memory,
relative Feldzeit, innere Organisation oder KI.

## Bester naechster Schritt

S2-C16 bindet ausschliesslich die kanonische A8/B8-End-to-End-Komposition.
Keine Schwelle, Weltspezifitaets-, Bedeutungs- oder Semantikbehauptung,
Intervention, Vollmatrix, Persistenz oder Laufnummer.
