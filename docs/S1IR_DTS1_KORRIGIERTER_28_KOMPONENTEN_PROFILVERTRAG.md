# S1-IR: Korrigierter DTS-1-Profilvertrag mit 28 Komponenten

## Status

S1-IR ersetzt den in S1-IQ gestoppten S1-IP-Vertrag fuer jede weitere
Baselinearbeit. Der Schritt korrigiert ausschliesslich die fehlerhafte
Kardinalitaet. Es wurden keine Profile neu definiert, keine Werte gewaehlt,
keine Adapter implementiert und keine Modelle oder Feldschritte ausgefuehrt.

Entscheidung:

```text
DTS1_CORRECTED_28_COMPONENT_JOINT_BASELINE_CONTRACT_BOUND_NO_EXECUTION
```

Vertragsdigest:

```text
350de2e0abbd05d03544567b3e7aae81ef387c75c739b924deea5f726410123e
```

## Korrekturumfang

| Profilblock | Geometrie und Differenzen | S1-IP | S1-IR |
| --- | --- | ---: | ---: |
| P_IE | zwei Knoten, zwei vollstaendige S/H-Differenzen | 12 | 8 |
| P_IH | zwei Knoten, zwei vollstaendige S/H-Differenzen | 12 | 8 |
| P_IK | drei Knoten, eine vollstaendige S/H-Differenz | 6 | 6 |
| P_IN | drei Knoten, eine vollstaendige S/H-Differenz | 6 | 6 |
| Gesamt | | 36 | 28 |

Die globalen L-infinity- und L1-Metrikbezeichnungen beziehen sich nun auf 28
statt 36 Komponenten. Dies fuegt keine Messgroesse hinzu und entfernt keine
vorhandene Messgroesse.

## Unveraenderte Bindungen

Aus S1-IP bleiben unveraendert erhalten:

- die vier Profilinhalte, ihre Vorzeichen und ihre Reihenfolge,
- sechs ausfuehrbare Baseline-Rollen und zwei strukturelle Gegenrollen,
- alle direkten Ressourcen-, Kausal- und Nullkontrollledger,
- erlaubte und verbotene Baselineeingaben,
- eine unveraenderliche Konfigurationsquelle je dynamischer Baseline,
- Vergleichsreihenfolge, STOPP-Bedingungen und Claimsperren.

Der S1-IP-Digest
`685d4d90c894d441f69d558fa91de110e51124b84442df31949b45e4de8d6625`
bleibt als supersedierter historischer Beleg gebunden und ist fuer weitere
Baselinearbeit nicht mehr gueltig. S1-IR bindet unmittelbar den
S1-IQ-Auditdigest
`b766a456ad1e368701a797bec7a85bf9e442be207c945594d6ed1c0a99712b60`.

## Aussagegrenze

S1-IR stellt nur einen formal konsistenten Vergleichsvertrag wieder her. Die
sechs Baseline-Signaturen sind weiterhin nicht klassifiziert. Der Schritt
belegt keine Baselinekompatibilitaet, Baselineschliessung oder
Kandidatenueberlegenheit und autorisiert keine Runtime oder Forschungsprobe.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1ir_corrected_profile_contract.py
tests/test_dynamic_substrate_s1ir_corrected_profile_contract.py
```

Sieben Tests pruefen die exakte Quellenkette, den begrenzten
Korrekturumfang, unveraenderte Rollen und Sperren, Ausfuehrungsfreiheit und
Manipulationsschutz.

## Bester naechster Schritt

S1-IS darf die in S1-IQ abgebrochene statische Kompatibilitaetspruefung gegen
den korrigierten 28-Komponenten-Vertrag neu beginnen. Geprueft werden nur
Signaturen, Zustandsdimensionen, Zwei-/Dreiknotengeometrien und notwendige
private Formadapter. Noch keine Adapterimplementierung, Parameterauswahl,
Modellausfuehrung, Runtime oder Forschungsprobe.
