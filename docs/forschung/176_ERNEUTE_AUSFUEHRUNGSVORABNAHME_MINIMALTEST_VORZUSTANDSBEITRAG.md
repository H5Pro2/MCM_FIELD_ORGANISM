# Erneute Ausfuehrungsvorabnahme Minimaltest Vorzustandsbeitrag

Stand: 2026-07-30

## 1. Gegenstand und Grenze

Diese Vorabnahme prueft die Dokumente 172 bis 175 und die dort fixierten
Eingaben gegen die vorhandenen technischen Wertobjekte. Sie konstruiert kein
gemeinsames Feld, implementiert keinen Runner, startet keinen Testlauf und
berechnet kein Feldergebnis.

## 2. Konstruktor-Kompatibilitaet

Die sieben in Dokument 175 fixierten Ereignisse wurden direkt aus den
eingebetteten kanonischen JSON-Daten als `ReceptorContactFrame` validiert.
Fuer jedes Ereignis wurden die korrespondierenden Werte fuer
`CommonFieldTime` und `MCMFieldStepTime` gegen deren Konstruktorvertraege
geprueft.

Zusaetzlich wurden folgende fixierte Werte erfolgreich gegen ihre bestehenden
Konstruktoren validiert:

- `ReceptorDock`;
- `ReceptorDockAnatomy`;
- `NeutralLocalFieldSubstrateConfig`;
- `NeutralFastAfterimageConfig`.

`dissipation_config` ist exakt `None`; eine `NeutralFieldDissipationConfig`
wurde nicht konstruiert.

Ergebnis: kompatibel mit den bestehenden Wertobjekt- und
Konfigurationsschnittstellen.

## 3. Unabhaengige Digest-Reproduktion

Die vier kanonischen JSON-Bloecke wurden aus Dokument 175 neu eingelesen und
mit den dort festgelegten Regeln serialisiert:

```text
allow_nan:    false
sort_keys:    true
separators:   [",", ":"]
ensure_ascii: true
encoding:     UTF-8
hash:         SHA-256
```

Reproduzierte Digests:

```text
A:      2d435c4331f083939796920ec2ae3e5864992d2cf11f447f9cab8f75e17e9998
B:      66ffdb19bdb743d5fb86a7e65dbb7c8c7f8e2045087aee74999bb5fa5d62da31
C:      81a6cf62a13cbdf246f8309c99eea564c64e035ca8ca094bb391c129036d3be3
config: fa13c44abcfaf7e80aa396b217eeea7ed28c50a3021bbccd62c59a15ecfd0e6a
bundle: 2b3286d2ca5a5a815e2002674736c828e9ae30ba12de5f60ac7fbca0bf1bdbd0
```

Alle reproduzierten Werte sind bitgleich zu Dokument 175.

## 4. Arm- und Replikatpruefung

Die Laufmatrix aus Dokument 173 enthaelt:

- genau 24 eindeutige Lauf-IDs;
- genau `.r1` und `.r2` fuer jeden der 12 Arme;
- A fuer `history_a.*`, `equalized_a.none`, `equalized_b.none` und
  `permuted_b.*`;
- B fuer `history_b.*` und `permuted_a.*`;
- C als aktuellen Kontakt in allen 24 Laufzeilen.

Die equalized Arme verwenden beide A. Die permutierten Arme vertauschen A und
B entsprechend Dokument 172 und 175. Die Replikatsuffixe aendern keine
Eingabebytes.

Ergebnis: Arm-, Permutations-, Equalized- und Replikatzuordnung vollstaendig.

## 5. Bytegleichheit von C

Dokument 175 definiert genau einen kanonischen C-Block und einen festen
C-Digest. Dokument 173 verweist in jeder der 24 Laufzeilen auf C. Es existiert
keine arm- oder replikatspezifische C-Definition.

Ergebnis: C ist vertraglich in allen Armen und Replikaten bytegleich gebunden.

## 6. Gleichheitsbedingungen A und B

Unabhaengig bestaetigt:

```text
event_count:                 3 == 3
total_duration_ticks:       30 == 30
absolute_contact_sum:       1.5 == 1.5
geometry_id:                identisch
modality_sequence:          identisch
time_windows:               identisch
carrier_sequences:          identisch
event_absolute_strengths:   [0.75, 0.5, 0.25] == [0.75, 0.5, 0.25]
```

A und B unterscheiden sich in den Kontaktwerten ausschliesslich durch die
fixierte raeumliche Vertauschung von `carrier.0` und `carrier.2`.

## 7. Sperrenpruefung

Die Dokumente 172 bis 175 sperren weiterhin:

- Feldkonstruktion und Feldlauf;
- Runner-Ausfuehrung;
- Test- und Effektlauf;
- Public-AV-Lauf;
- Produktionsschalter;
- Aenderung der Organismus- oder Felddynamik;
- neue Hypothesen, Messpunkte, Metriken oder Schwellen.

Waehrend dieser Vorabnahme wurde kein gemeinsames Feld konstruiert und kein
Integrator- oder Feldpfad aufgerufen.

## 8. Vorabentscheidung

```text
constructor_compatibility_verified:       true
canonical_digests_reproduced:             true
arm_mapping_verified:                     true
replicate_mapping_verified:               true
equalized_mapping_verified:               true
permutation_mapping_verified:             true
c_byte_identity_contract_verified:        true
a_b_equality_conditions_verified:         true
dissipation_config_is_none:               true
field_constructed:                        false
runner_implemented:                       false
test_or_effect_run_started:               false
limited_runner_implementation_permitted:  true
runner_execution_permitted:               false
effect_measurement_permitted:             false
```

Ein eng begrenzter Runner-Implementierungsauftrag darf formuliert werden. Die
Freigabe betrifft ausschliesslich nicht ausgefuehrten Code zur mechanischen
Abbildung der bereits fixierten Vertraege. Sie ist keine Freigabe fuer einen
Feldlauf oder eine Effektmessung.

## 9. Freigegebener naechster Auftrag

Implementiere einen privaten Forschungsrunner mit zugehoerigen Strukturtests
unter folgenden harten Grenzen:

- A, B, C, Konfiguration und Digests werden unveraendert aus Dokument 175
  abgebildet;
- exakt die 24 Lauf-IDs aus Dokument 173 werden verdrahtet;
- `dissipation_config` wird vor jeder Feldkonstruktion hart auf `None`
  validiert;
- der Runner besitzt eine standardmaessig aktive Ausfuehrungssperre;
- die Implementierungs- und Strukturtests duerfen keine Felder konstruieren,
  keine Rezeptorverteilung erzeugen und keinen Integrator aufrufen;
- die Tests pruefen nur Manifest, Digests, Armzuordnung, Replikate,
  Messpunktdeklarationen, Abbruchregeln und Sperren;
- der private Vorzustands-Hook bleibt nicht oeffentlich exportiert;
- keine Aenderung an Feld-, Organismus-, Projektions-, Diffusions-,
  Daempfungs- oder Afterimage-Dynamik;
- keine neuen Hypothesen, Messpunkte, Messmetriken oder Schwellen;
- kein Testlauf des Forschungsgegenstands und keine Effektberechnung.

Nach der Implementierung ist eine separate technische Review-Abnahme
erforderlich. Erst eine weitere ausdrueckliche Vorabnahme darf spaeter die
Ausfuehrung eines Feldlaufs beurteilen.

## 10. Aussagegrenze

Diese Vorabnahme erzeugt keinen Befund zu Feldwirkung, Kontaktgeschichte,
Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder
KI.
