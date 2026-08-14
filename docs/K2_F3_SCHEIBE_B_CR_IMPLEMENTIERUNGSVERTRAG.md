# K2/F3 Scheibe B: C/R-Implementierungsvertrag

Stand: 2026-08-06

Status:

- reine F3-C/R-Funktion implementiert;
- algebraische Vertrags- und Invariantentests bestanden;
- kein Integrator und kein AV-Forschungslauf in Scheibe B;
- keine Memory-, Organisations-, Topologie-, Semantik- oder KI-Behauptung.

## 1. Implementierter Umfang

Modul:

```text
mcm_field_organism/mcm_f3_coupling.py
```

Oeffentliche API:

```text
MCMF3LocalRate
MCMF3CouplingResult
MCMF3CouplingError
compute_mcm_f3_coupling(layer, substrate)
mcm_f3_coupling_public_roles
```

Die Funktion erhaelt nur den aktuellen `MCMNeuronLayer` und den aktuellen
`MCMSubstrateState`. Sie erhaelt keinen Weltkontakt, keine Phase, keinen
Snapshotverlauf, keine Labels und keine Ergebnisinformation.

## 2. Atomare Berechnung

Jede vorhandene ungerichtete Feldkante wird genau einmal verarbeitet:

```text
q_i_to_j = lambda_sm * M_i * (1 + kappa * (S_j - S_i))
q_j_to_i = lambda_sm * M_j * (1 - kappa * (S_j - S_i))
```

Der eine berechnete Nettofluss wird mit entgegengesetztem Vorzeichen auf
beide Endpunkte gebucht. Danach wird R ausschliesslich aus demselben fertigen
C berechnet:

```text
R_i = -eta * (1 - S_i^2) * C_i / M_total
```

Es gibt keine Reihenfolge `erst M, dann S`, keinen zweiten C-Lauf und keine
Zustandsaenderung innerhalb der Funktion.

## 3. Harte Eingangsgrenzen

Vor der Berechnung werden geprueft:

- vollstaendige Identitaet zwischen Feldneuronen und M-Massen;
- kanonische vorhandene Feldkanten;
- Uebereinstimmung mit dem gespeicherten Kanten-Digest;
- gueltiger fester Armvertrag;
- normalisierte S-Werte aus dem bestehenden Neuronenvertrag;
- nichtnegative M-Werte und feste Gesamtmasse aus Scheibe A.

Die Funktion lernt oder veraendert keine Kante und liest M nicht ueber die
allgemeine Wahrnehmung.

## 4. Nachgewiesene technische Invarianten

Die Tests bestaetigen:

- P0 liefert C und R exakt Null;
- gleichfoermiges M und ein S-Gradient erzeugen gerichteten M-Transport;
- `sum(C)` bleibt im Mehrknotenfall auf Gleitkomma-Rundungsniveau Null;
- `eta = 0` entfernt nur R, nicht C;
- `kappa = 0` laesst nur neutrale M-Diffusion;
- Vorzeichenwechsel von `kappa` kehrt beim gleichfoermigen M-Gradienten die
  Transportrichtung um;
- konstantes S und gleichfoermiges M bilden einen exakten Ruhezustand;
- an `S = -1` und `S = 1` ist R exakt Null, waehrend C bestehen kann;
- Deklarationsreihenfolge aendert das kanonische Ergebnis nicht;
- falsche Neuronenidentitaeten und Kanten-Digests werden abgelehnt;
- Eingabe-Layer und Substrat bleiben unveraendert.

## 5. Nicht implementiert

Scheibe B enthaelt weiterhin nicht:

- eine Zeitschrittweite;
- Euler, SSPRK oder einen anderen Integrator;
- Aenderung von S, H oder M;
- Rezeptorereignisverarbeitung;
- Snapshotfortschreibung;
- AV-Weltkontakt;
- Praegung, Memory oder Organisation.

## 6. Ergebnis

Scheibe B stellt die lokal konservative C/R-Ableitung getrennt von jeder
Numerik bereit. Damit kann Scheibe C die Funktion als unveraenderte atomare
Rechte-Seite verwenden und gegen Zeitverfeinerung pruefen.

Der naechste Implementierungsschritt ist Scheibe C: der fest
ereignisausgerichtete SSPRK(3,3)-Pfad mit gemeinsamer S/H/M-Fortschreibung,
P0-Bypass, Invariantendiagnose und Restore-Pruefung. Ein AV-Forschungslauf
bleibt davon getrennt.
