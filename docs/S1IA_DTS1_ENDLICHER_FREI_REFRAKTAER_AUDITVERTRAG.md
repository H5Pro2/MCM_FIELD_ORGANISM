# S1-IA: Endlicher DTS-1 Frei/Refraktaer-Auditvertrag

## Status

S1-IA bindet das feste synthetische Fixture und den vollstaendigen
Ausfuehrungsvertrag fuer die in S1-HZ vorregistrierte Zustandsintervention.
Der Audit wird noch nicht implementiert oder ausgefuehrt. Es wird keine
Gleichung hinzugefuegt oder geaendert und keine Runtime angebunden.

Entscheidung:

```text
DTS1_FINITE_FREE_REFRACTORY_AUDIT_CONTRACT_BOUND
```

Vertragsdigest:

```text
c59c5d1c05ac5f9fed8d91088a1490e136ad08ed28bfa72cc34f54b6c45dc650
```

## Quellenbindung

S1-IA bindet den S1-HZ-Vertragsdigest
`968a0ed6e033da839fae767cbf2a5ed2129440a6ab9c68c386fe206c606cff57`
und genau das private spaetere Zielmodul
`mcm_field_organism.dynamic_substrate_dts1_free_refractory_audit`.

## Festes synthetisches Fixture

```text
Geometrie:              eine isolierte bestehende Kante node-a -- node-b
Kapazitaeten:           (1.0, 1.0)
Referenz-S:             (-1.0, 1.0)
Referenz-H:             (0.2, -0.2)
Kantenbeteiligung:      1.0
Schrittdauer:           0.5 synthetische Zeiteinheiten
Raten:                  bind=0.4, turn=0.3, rec=0.2
leitende Bindung:       0.4 in beiden Armen
F_HIGH refraktaer:      0.2
R_HIGH refraktaer:      0.8
F_HIGH frei je Knoten:  0.7
R_HIGH frei je Knoten:  0.3999999999999999
```

Die freien Werte werden nicht gespeichert. Sie entstehen exakt aus der
produktiven S1-HI-Reihenfolge:

```text
free = capacity - fsum(0.5 * conductive, 0.5 * refractory)
```

Die sichtbare Float64-Darstellung des R_HIGH-Werts ist deshalb verbindlich.
Beide lokalen Identitaeten und die globale Gesamtressource `2.0` bleiben
erhalten. Die Zahlen sind unveraenderliche synthetische Algebrafixtures und
keine Materialparameter oder physische Zeitskala.

## Analytische Vorpruefung

Ohne Aufruf des S1-HP-Schritts wurden aus seiner bereits gebundenen Abbildung
folgende Float64-Erwartungen vorregistriert:

```text
alpha_bind                   = 0.18126924692201812
F_HIGH engagement            = 0.2537769456908254
R_HIGH engagement            = 0.14501539753761447
F_HIGH Knotennachfrage       = 0.1268884728454127
R_HIGH Knotennachfrage       = 0.07250769876880724
Admission in beiden Armen    = 1.0
erwartete Differenz          = 0.1087615481532109
Float64-Rundungsgrenze       = 1.1368683772161603e-13
```

Beide Nachfragen liegen strikt unter der jeweiligen freien Knotenressource.
Damit ist das Fixture nichtsaturiert; die gerichtete Differenz entsteht nicht
aus Clipping oder gemeinsamer Zulassungsbegrenzung.

## Vier Faelle pro Audit

| Fall | Inhalt | reine S1-HP-Aufrufe |
| --- | --- | ---: |
| C01 | F_HIGH gegen R_HIGH bei positiver Beteiligung und positiver Bindungsrate | 2 |
| N01 | zwei wertidentische F_HIGH-Vorschlaege | 2 |
| N02 | F_HIGH und R_HIGH bei Beteiligung null | 2 |
| N03 | F_HIGH und R_HIGH bei Bindungsrate null | 2 |

Ein Audit umfasst exakt acht reine Ressourcenschrittaufrufe. Derselbe Audit
muss ein zweites Mal ausgefuehrt werden und denselben kanonischen Receipt
liefern. Der gesamte spaetere Doppelaudit ist auf hoechstens `16` reine
Ressourcenschrittaufrufe begrenzt. Feldschritte bleiben exakt null.

## Entscheidung

Die primaere Messgroesse bleibt ausschliesslich `engagement` im passiven
Zielkanten-Transferledger. Fuer C01 muessen die beiden Werte innerhalb der
gebundenen Rundungsgrenze bei ihren Vorhersagen liegen. Zusaetzlich muss ihre
Differenz groesser als die Rundungsgrenze und strikt positiv sein.

N01 verlangt bitgenaue vollstaendige Ergebnisse und Digests. N02 und N03
verlangen in beiden Armen exakt null Engagement. Alle Eingangs- und
Ausgangsanatomien muessen ihre lokalen und globalen Bilanzen innerhalb der
Rundungsgrenze halten.

Die fuenf S1-HZ-Gegenbaselines werden nur als statische, unveraenderte
Zustandsraumrecords gefuehrt. Es wird kein Baselinemodell ausgefuehrt. Keine
Baseline erhaelt Arm-ID, Frei/Refraktaer-Koordinate oder einen armweisen Fit.

## STOPP

Jede einzelne Abweichung ergibt atomar STOPP, insbesondere:

- Fixture-, Arm-, Fallreihenfolge- oder Aufrufzahldrift;
- fehlende Gleichheit einer Kontrollgroesse;
- ungueltige, randstaendige oder saturierte Anatomie;
- Ersatz der direkten Messgroesse durch Netto-Bindung, Feldwert oder Proxy;
- Abweichung der positiven Engagementwerte jenseits der Rundungsgrenze;
- fehlende gerichtete Differenz oder fehlerhafte Nullkontrolle;
- Ressourcenbilanzfehler oder Receipt-Nichtdeterminismus;
- Baseline-Erweiterung, Retry, Nachjustierung, Teilausgabe;
- mehr als 16 Ressourcenaufrufe oder irgendein Feld-, Runtime- oder
  Forschungslauf.

## Aussagegrenze

S1-IA hat nur Fixture, Ausfuehrungsumfang und Entscheidung vorregistriert. Es
liegt noch kein Interventionsbefund vor. Selbst ein spaeterer PASS waere nur
ein direkter technischer Ressourcen-Zustandsbefund des festen synthetischen
Fixtures. Feldfunktion, Abschwaechung, Interferenz, Freigabe,
Wiederbeanspruchung und Materialeignung blieben weiterhin offen.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1ia_free_refractory_audit_contract.py
tests/test_dynamic_substrate_s1ia_free_refractory_audit_contract.py
```

Zehn Tests pruefen Quellenbindung, Fixture, lokale Identitaeten, unabhaengige
Float64-Vorpruefung, Fall- und Aufrufumfang, direkte Entscheidung,
Baselinegrenzen, Atomaritaet, Ausfuehrungssperren und Manipulationsschutz.

## Bester naechster Schritt

S1-IB darf genau das private Auditharness implementieren und den
vorregistrierten Doppelaudit genau einmal mit hoechstens 16 reinen
Ressourcenschrittaufrufen ausfuehren. Es darf keinen Feldschritt, keine
Baselineausfuehrung, Runtimeintegration oder Forschungsprobe geben. STOPP
beendet diesen Interventionspfad; PASS belegt noch keine Feldfunktion.
