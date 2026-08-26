# S1-BU: E1 synchrone gekoppelte Runtime und Abnahme

## Status

Synchroner atomarer E1/S/H-Schritt implementiert und fokussiert abgenommen.
Keine transiente AV-Kopplung, kein Snapshot-Schema, kein `current_api`-Export
und kein Memory-, Lern-, Organismus- oder KI-Befund.

## Implementierte Dateien

```text
mcm_field_organism/e1_coupled_fast_field.py
tests/test_e1_coupled_fast_field.py
```

Bestehende neutrale Runtime- und API-Dateien wurden nicht veraendert.

## Implementierte Rollen

```text
E1CoupledFastFieldError
E1CoupledFastFieldStepResult
advance_e1_coupled_fast_shared_field(...)
```

Das Ergebnis enthaelt das abgeschlossene Feld, den abgeschlossenen
E1-Endzustand und genau den E1-Mitteladapter, der den Feldgenerator des
Intervalls gebildet hat.

## Implementierte atomare Ordnung

```text
b_(t+1/2) = E1_advance(S_t, b_t, dt/2)
r_(t+1/2) = E1_adapter(b_(t+1/2))
(S_(t+1),H_(t+1)) = exact_fast_field(r_(t+1/2), dt)
b_(t+1) = E1_advance(S_(t+1), b_(t+1/2), dt/2)
```

Der aktive nichtneutrale Arm verwendet den gewichteten internen Generator.
A0 und jeder exakt neutrale Adapterzustand verwenden den bestehenden
neutralen Generatorpfad, damit P0-Gleichheit nicht durch unterschiedliche
Matrixaufbau-Reihenfolgen beeintraechtigt wird.

## Harte Grenze des Weltkontakts

Nur interne vorhandene MCM-Kanten werden durch E1 gewichtet. Gemappte
Rezeptorkontakte treten weiterhin mit der neutralen Basisrate ein. Die
vorhandene exakte S/H-Spektralintegration und optionale Felddissipation werden
unveraendert wiederverwendet.

## Fokussierte Abnahme

Ausgefuehrt mit:

```text
python -m unittest -v tests.test_e1_coupled_fast_field
```

Ergebnis:

```text
8 tests
OK
```

Geprueft wurden:

- bitgenaue P0-/A0-Feldidentitaet bei nichtuniformem E1-Zustand;
- aktive A1-Abweichung in Aktivierung und Nachhall;
- identische Feld-, E1- und Ratenwerte fuer `gamma = 0`;
- Verwendung des ersten halben E1-Zustands als angewendeter Adapter;
- zwei korrekte halbe E1-Schritte bei uniformem kontaktfreiem Feld;
- normierter Feldbereich, E1-Bilanz und Eingabeunveraenderlichkeit;
- abnehmende Abweichung bei Zeitverfeinerung;
- Fehler- und API-Isolation.

Im ersten Testlauf waren zwei Testannahmen unzutreffend: Ein Initialfeld ohne
abgeschlossenen Rezeptorschritt besitzt noch keinen Snapshot, und der
technische Armbeleg bleibt bei `gamma=0` trotz identischer numerischer Werte
absichtlich als an beziehungsweise aus markiert. Nur diese Tests wurden
korrigiert; die Runtimegleichung blieb unveraendert. Danach bestanden alle
acht Tests.

## Gemeinsamer Regressionstest

Gemeinsam ausgefuehrt:

```text
tests.test_e1_coupled_fast_field
tests.test_e1_weighted_field_adapter
tests.test_e1_local_edge_plasticity
tests.test_mcm_substrate_state
tests.test_neutral_local_field_substrate
tests.test_neutral_fast_afterimage
tests.test_current_api_end_to_end_consumer
tests.test_current_api_browser_payload_consumer
```

Ergebnis:

```text
62 tests
OK
```

## Technisches Urteil

```text
atomare Kopplungsordnung:          bestanden
P0-/A0-Feldidentitaet:            bestanden
aktive A1-Feldwirkung:            bestanden
Gamma-Nullkontrolle:              bestanden
E1-Mittelzustandsbindung:         bestanden
Zeitverfeinerung:                 bestanden
S/H-Bereich und E1-Bilanz:        bestanden
neutrale Runtime-Regression:       bestanden
current_api-Isolation:             bestanden
```

Damit ist erstmals technisch gezeigt, dass ein entwickelbarer E1-Zustand
kausal die spaetere interne S/H-Feldfortsetzung veraendern kann. Diese Wirkung
ist im kontrollierten A0-Arm vollstaendig ablatierbar.

## Warum E2 noch nicht erreicht ist

S1-BU vergleicht gekoppelte Schritte, deren Feld- und E1-Endzustaende sich
gemeinsam entwickeln duerfen. Fuer E2 fehlt weiterhin der strengere
Kausaltest:

```text
verschiedene E1-Geschichte
+ vor Probe identisches S und H
+ vor Probe identischer Weltkontakt
+ waehrend Probe eingefrorener E1-Zustand
-> unterschiedliche spaetere Feldfortsetzung nur bei Rueckwirkung an
```

Erst diese Intervention trennt gespeicherte Kantenkonfiguration von aktueller
S/H-Amplitude und laufender E1-Weiterentwicklung.

## Aussagegrenze

Die technische Rueckwirkung ist eine notwendige, aber keine hinreichende
Bedingung fuer MCM-Memory. S1-BU weist weder Praegung, Vergessen,
Wiederverwendung, Rekonstruktion noch eine neue MCM-Natur nach.

## Bester naechster Schritt

S1-BV hat den eingefrorenen identischen Probevertrag fuer E2 gebunden. Zwei
kontrolliert erzeugte gespiegelte E1-Zustaende werden auf exakt angeglichene
S/H-Feldkopien angewendet; aktive Rueckwirkung, Ablation und eingefrorener
fester Gain bleiben getrennt. Als naechstes implementiert S1-BW nur den
eingefrorenen Probeoperator und seine technischen Identitaetstests.
