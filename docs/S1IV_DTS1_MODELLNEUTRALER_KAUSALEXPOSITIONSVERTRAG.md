# S1-IV: Modellneutraler DTS-1-Kausalexpositionsvertrag

## Status

S1-IV bindet fuer P_IK und P_IN eine gemeinsame kausale Vorgeschichte fuer
DTS-1 und alle sechs Baselines. Ziel ist ausschliesslich ein fairer spaeterer
Vergleich. Es wurden keine Ereigniswerte, Dauern oder Konfigurationen gewaehlt
und kein Fixture oder Adapter implementiert oder ausgefuehrt.

Entscheidung:

```text
COMMON_CAUSAL_EXPOSURE_BOUND_P_IK_P_IN_CONTROLLED_REREGISTRATION_REQUIRED
```

Vertragsdigest:

```text
9242aa71d086b7c0cde86aa1327e502b65700383d886eb7d93812a58478ec92c
```

## Gemeinsames Ereignis

Ein Ereignis ist eine modellneutrale exogene Rezeptorsequenz mit kanonischer
Knotenordnung, positiver Dauer und expliziten Grenzen. Sie enthaelt keine
Koordinate eines Modellzustands. Derselbe Ereignispayload wird im jeweiligen
Arm an DTS-1, Fixed Adapter, S2-Integrator, F3 Local Leaky, F3 Linear, F3 Full
und CONST-V uebergeben. Jedes Modell berechnet seine interne Antwort nur aus
diesem Ereignis und seinem eigenen getragenen Vorzustand.

## P_IK

```text
ABA:       A -> B   -> A -> gemeinsamer S/H-Reset -> Nullkontakt-Readout
A-Gap-A:   A -> Gap -> A -> gemeinsamer S/H-Reset -> Nullkontakt-Readout
```

Nur das mittlere exogene B- beziehungsweise Gap-Ereignis unterscheidet die
Arme. Alle Modelle tragen ihren vollstaendigen Zustand durch die drei
Expositionsintervalle.

## P_IN

```text
Recovery-on:  A -> Gap [DTS-1-Recovery an]  -> B -> S/H-Reset -> Readout
Recovery-off: A -> Gap [DTS-1-Recovery aus] -> B -> S/H-Reset -> Readout
```

A, Gap und B sind fuer beide Arme und alle Modelle identisch. Nur innerhalb
von DTS-1 wird der Recoverykanal an- beziehungsweise abgeschaltet. B1 bis B6
erhalten weder eine entsprechende Kennung noch eine Parameterumschaltung und
bleiben zwischen den Armen identisch konfiguriert.

## Zustandsgrenze

Vor dem Nullkontakt-Readout wird der exponierte S/H-Zustand in allen Modellen
auf denselben noch zu registrierenden Probevorzustand gesetzt. Nur S/H wird
zurueckgesetzt. Erhalten bleiben:

- freie, leitend gebundene und refraktaere DTS-1-Ressource,
- der einmal fixierte B1-Adapter,
- der baselineeigene B2-L-Zustand,
- die baselineeigenen M-Zustaende von B3 bis B6.

DTS-1 leitet seine Kantenbeteiligung intern aus seinem aktuellen Feld ueber
die bereits gebundene S1-HK-Observable ab. Keine Baseline erhaelt diese
Beteiligung, Ressourcenledger oder Recoveryzustand als Eingabe.

## Profilentscheidung

P_IE und P_IH behalten ihre vorhandenen Profile und Receipts. Die alten
P_IK- und P_IN-Feldvektoren werden fuer den gemeinsamen Baselinevergleich
gesperrt, weil ihnen die gemeinsame Vorgeschichte fehlt. Ihre direkten
Interferenz-, Freigabe- und Wiederverwendungsledger bleiben als technische
Evidenz erhalten.

Die kuenftige Struktur bleibt `8 + 8 + 6 + 6 = 28` Komponenten. Die letzten
beiden Sechserbloecke benoetigen jedoch neue vorregistrierte Fixtures und neue
Receipts. Alte Zahlen duerfen weder repariert noch umgedeutet werden.

## Aussagegrenze

S1-IV beweist keine Gleichwertigkeit konkreter Ereigniswerte und keine
Baseline- oder Kandidatenaussage. Erst ein endlicher Vertrag muss Werte,
Dauern, Resetvorzustand, Toleranzen und Aufrufbudgets festlegen. Vorher bleibt
jede Ausfuehrung gesperrt.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1iv_common_causal_exposure_contract.py
tests/test_dynamic_substrate_s1iv_common_causal_exposure_contract.py
```

Neun Tests pruefen Quellenbindung, Modellneutralitaet, beide Zeitplaene,
Recoverytrennung, Reset- und Zustandserhaltung, Profilquarantaene,
kontrollierte Neuregistrierung, Ausfuehrungsfreiheit und Manipulationsschutz.

## Bester naechster Schritt

S1-IW darf ausschliesslich einen endlichen statischen Fixturevertrag fuer die
neuen P_IK- und P_IN-Expositionen binden. A/B/Gap-Werte, Dauern,
Probevorzustand, erwartete strukturelle Nullfaelle, Toleranzen und maximales
technisches Aufrufbudget muessen vor jeder Implementierung feststehen. Noch
keine Adapterkonfiguration, Implementierung, Modellausfuehrung, Runtime oder
Forschungsprobe.
