# S1-IP: Statischer gemeinsamer DTS-1-Baselineschliessungsvertrag

## Status

S1-IP bindet ausschliesslich den gemeinsamen Vergleichsvertrag fuer die in
S1-IO noch offenen Gegenbaselines. Es wurden keine Parameterwerte oder
Schwellen gewaehlt, keine Geometrieadapter oder Profilcontainer implementiert
und keine Baseline, Runtime oder Forschungsprobe ausgefuehrt.

Entscheidung:

```text
DTS1_JOINT_BASELINE_CLOSURE_CONTRACT_BOUND_NO_PARAMETERS_OR_EXECUTION
```

Vertragsdigest:

```text
685d4d90c894d441f69d558fa91de110e51124b84442df31949b45e4de8d6625
```

## Gemeinsame Vergleichsflaeche

Der Vertrag bindet 36 vorzeichenbehaftete S/H-Komponenten in fester Ordnung:

| Block | Inhalt | Komponenten |
| --- | --- | ---: |
| P_IE | Kausaler F_HIGH-minus-R_HIGH-Vergleich an zwei Subschritten | 12 |
| P_IH | Abschwaechung an zwei gebundenen Checkpointdifferenzen | 12 |
| P_IK | A-B-A-minus-A-Pause-A nach der Folge | 6 |
| P_IN | Recovery-on-minus-Recovery-off nach der B-Probe | 6 |

Zwei- und Dreiknotenbloecke bleiben bis zur kanonischen Konkatenation
getrennt. Armweise Skalierung, Betragsbildung, nachtraegliche Auswahl und
checkpointweise Fits sind unzulaessig. Die direkten Ressourcen-, Kausal- und
Nullkontrollledger aus S1-IB, S1-IE, S1-IH, S1-IK und S1-IN bleiben harte
Gates und koennen nicht durch einen guten Feldprofilfit ersetzt werden.

## Gegenrollen

Sechs vorhandene Modellrollen sind fuer eine spaetere technische Ausfuehrung
registriert:

1. vor der Armdivergenz fixierter DTS-1-Adapter,
2. lineare S2-Integratorbaseline,
3. lokale F3-Leaky-Baseline,
4. linear gekoppelte F3-Baseline,
5. vollstaendige F3-Baseline,
6. CONST-V-Baseline.

Das dynamische zweistufige E1 und schneller Nachhall sind als strukturelle
Gegenrollen gebunden. Sie werden in diesem Vertrag nicht ausgefuehrt oder
nachparametriert.

## Parameter- und Informationsgrenze

Jede dynamische Baseline muss ueber alle technisch kompatiblen Profilbloecke
genau eine unveraenderliche Konfigurationsquelle und einen Digest verwenden.
Der feste Adapter darf pro Quellfixture genau einmal aus dem gemeinsamen
Zustand vor der Armdivergenz entstehen. DTS-1-Ressourcenpartitionen,
Armkennungen, Zielrichtungen, Referenzausgaben, Zukunftszustaende und
ergebnisabhaengige Werte sind fuer Baselines gesperrt.

S1-IP waehlt noch keine Zahlen. Insbesondere sind vorhandene
Modellgleichungen, Zustandsdimensionen und veroeffentlichte Defaultquellen
nicht veraenderbar. Ein reiner Geometrie- oder Formadapter darf nur Identitaet,
Reihenfolge und Datenform uebersetzen.

## Entscheidung und STOPP

Die spaetere Entscheidung ist atomar geordnet: ungueltiger Audit, technisch
inkompatibles Inventar, Erklaerung durch eine registrierte Baseline oder
Residuum nach allen registrierten Baselines. Eine inkompatible Baseline darf
nicht still ausgelassen oder als positiver Residualbefund gewertet werden.
Receipt-, Profil-, Vorzeichen-, Gate-, Parameter- oder Kontrollabweichung
bewirkt STOPP.

## Aussagegrenze

S1-IP beweist weder Kompatibilitaet noch Baselineschliessung oder
Kandidatenueberlegenheit. Der Schritt validiert kein Material und autorisiert
keine Runtime oder Forschungsfeldprobe. Memory bleibt eine offene
Forschungsrichtung; Lernen, Semantik, innerer Kontext, Organisation,
Selbstregulation und weitergehende Projektmerkmale werden nicht behauptet.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1ip_joint_baseline_contract.py
tests/test_dynamic_substrate_s1ip_joint_baseline_contract.py
```

Zehn Tests pruefen Quellen, Rollen, Profilumfang, direkte Gates,
Informationsgrenzen, Parameterregeln, Entscheidungsordnung,
Ausfuehrungsfreiheit und Manipulationsschutz.

## Bester naechster Schritt

S1-IQ darf ausschliesslich statisch pruefen, ob die sechs registrierten
ausfuehrbaren Modelloberflaechen die gebundenen Zwei- und Dreiknotenprofile
ohne Gleichungs-, Parameter- oder Zustandsaenderung aufnehmen koennen und
welche privaten Formadapter dafuer erforderlich waeren. Noch keine
Adapterimplementierung, Parameterauswahl, Modellausfuehrung, Runtime oder
Forschungsprobe.
