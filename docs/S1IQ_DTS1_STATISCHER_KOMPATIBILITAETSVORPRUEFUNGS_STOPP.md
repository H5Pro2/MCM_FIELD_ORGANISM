# S1-IQ: Statischer DTS-1-Kompatibilitaetsvorpruefungs-STOPP

## Status

S1-IQ sollte die technische Kompatibilitaet der sechs in S1-IP registrierten
Baseline-Oberflaechen pruefen. Die bindende erste Auditstufe fand jedoch vor
jeder Modellklassifikation einen Kardinalitaetsfehler im gemeinsamen
Profilvertrag. Entsprechend der in S1-IP festgelegten atomaren Reihenfolge
wurde die Kompatibilitaetspruefung fail-closed beendet.

Entscheidung:

```text
STOPP_INVALID_S1IP_PROFILE_CARDINALITY_36_NE_28
```

Auditdigest:

```text
b766a456ad1e368701a797bec7a85bf9e442be207c945594d6ed1c0a99712b60
```

## Kardinalitaetsbefund

Die vorhandenen unveraenderten Record-Schemata ergeben:

| Profilblock | Knoten | Differenzen | S/H-Breite | korrekt | S1-IP |
| --- | ---: | ---: | ---: | ---: | ---: |
| P_IE | 2 | 2 | 4 | 8 | 12 |
| P_IH | 2 | 2 | 4 | 8 | 12 |
| P_IK | 3 | 1 | 6 | 6 | 6 |
| P_IN | 3 | 1 | 6 | 6 | 6 |
| Gesamt | | | | 28 | 36 |

S1-IE bindet zwei vollstaendige S/H-Vektoren einer Zweiknotengeometrie und
S1-IH zwei Checkpointdifferenzen derselben Vektorbreite. Beide Bloecke
enthalten daher je acht, nicht je zwoelf Komponenten. S1-IK und S1-IN sind
Dreiknotenfaelle mit je einer vollstaendigen S/H-Differenz und bleiben bei je
sechs Komponenten. Eine Auffuellung, Duplizierung oder Umdeutung der
vorhandenen Records waere mit dem S1-IP-Vertrag unvereinbar.

## Atomarer STOPP

S1-IP setzt `INVALID_JOINT_BASELINE_AUDIT` an die erste Stelle der
Entscheidungsreihenfolge. Deshalb wurden die sechs Baseline-Signaturen nicht
klassifiziert und keine Formadapter spezifiziert. Alle sechs Rollen tragen
den Status `NOT_REACHED_INVALID_PROFILE_CARDINALITY`.

Es wurden keine Parameter oder Schwellen gewaehlt, keine Modellfunktion
ausgefuehrt und keine Runtime- oder Forschungsfeldschritte vollzogen. Der
Befund ist keine Baselineverwerfung und keine Stuetzung oder Ueberlegenheit
des Kandidaten.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1iq_compatibility_precheck.py
tests/test_dynamic_substrate_s1iq_compatibility_precheck.py
```

Neun Tests pruefen Quellenbindung, alle vier Profilkardinalitaeten, den
exakten Fehlbetrag, die atomare STOPP-Reihenfolge, sechs nicht erreichte
Baselineurteile, Ausfuehrungsfreiheit und Manipulationsschutz.

## Bester naechster Schritt

S1-IR darf ausschliesslich einen statischen korrigierten Profilvertrag mit 28
Komponenten binden und S1-IP fuer die weitere Baselinearbeit ersetzen. Die
vier Profildefinitionen, Vorzeichen, Reihenfolge, direkten Ledger-Gates und
sonstigen Informations- und Claimsperren bleiben unveraendert. Noch keine
Baselineklassifikation, Adapterimplementierung, Parameterauswahl,
Modellausfuehrung, Runtime oder Forschungsprobe.
