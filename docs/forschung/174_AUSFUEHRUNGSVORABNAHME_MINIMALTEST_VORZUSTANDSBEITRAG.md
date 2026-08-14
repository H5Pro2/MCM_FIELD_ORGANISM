# Ausfuehrungsvorabnahme Minimaltest Vorzustandsbeitrag

Stand: 2026-07-30

## 1. Gegenstand und Grenze

Diese Vorabnahme prueft ausschliesslich, ob der in Dokument 172
vorregistrierte und in Dokument 173 spezifizierte Minimaltest bereits eindeutig
genug fuer einen eng begrenzten Runner-Implementierungsauftrag ist.

Sie implementiert keinen Runner, startet keinen Testlauf, konstruiert kein Feld
und berechnet kein Ergebnis.

## 2. Gepruefte Vertragsbestandteile

### 2.1 Laufmatrix und Replikate

Dokument 173 bindet die 12 Tabellenarme aus Dokument 172 vollstaendig auf 24
eindeutige Lauf-IDs ab. Jeder Arm besitzt genau `.r1` und `.r2`; jedes Replikat
muss mit einem frischen Feld beginnen. Die Tabellenreihenfolge ist fest und
nicht ergebnisabhaengig.

Ergebnis: vorab abnahmefaehig.

### 2.2 Messpunkte und Messrollen

`M0` bis `M3` sind eindeutig an Feldkonstruktion, Ende der Vorgeschichte,
Integrator-Eingang fuer C und anschliessende Feldfortschreibung gebunden. Die
Messrollen sind auf die in Dokument 172 festgelegten technischen Zustandsrollen,
Digests, `L-inf`-Differenzen und exakte Gleichheit begrenzt.

Ergebnis: vorab abnahmefaehig.

### 2.3 Dissipations-Gate

Der Vertrag verlangt vor Feldkonstruktion:

- ein explizites Manifestfeld `dissipation_config` mit dem Wert `None`
  beziehungsweise `null` nach Serialisierung;
- keine Konstruktion oder Ableitung einer `NeutralFieldDissipationConfig`;
- getrennte Identifizierbarkeit von Hook- und Dissipationsaenderungen.

Ein abweichender oder nicht eindeutig pruefbarer Zustand sperrt den Lauf vor
Konstruktion des ersten Feldes.

Ergebnis: vorab abnahmefaehig.

### 2.4 Abbruch und Protokollierung

Die Abbruchbedingungen aus Dokument 172 sind in Dokument 173 als harte Gates
gebunden. Bei einem Abbruch duerfen nur technischer Grund, Lauf-ID, Messpunkt
und vorhandene Diagnosedaten protokolliert werden. Teilresultate duerfen nicht
fuer H0, H1, H2 oder P ausgewertet werden.

Ergebnis: vorab abnahmefaehig.

## 3. Vorab-Fixierbarkeit von A, B und C

Die vorhandenen Schnittstellen koennen die synthetischen Eingaben ohne neue
Organismusfunktion und ohne Dynamikaenderung ausdruecken. Insbesondere stehen
bereits technische Strukturen fuer Rezeptorkontakte, gemeinsame Feldzeit,
Feldschrittzeit, Rezeptorverteilung und frische Feldkonstruktion bereit.

A, B und C sind daher technisch vorab fixierbar. In Dokument 172 und 173 sind
sie jedoch noch nicht konkret fixiert. Festgelegt sind bislang nur folgende
Relationen:

- A und B besitzen gleiche Ereignisanzahl, Dauer, Kontaktstaerkensumme,
  Geometrie und Modalitaetsbelegung;
- nur ihre zeitlich-raeumliche Folge darf verschieden sein;
- C ist in allen Armen bytegleich.

Es fehlen weiterhin:

- die vollstaendigen geordneten Ereignislisten von A, B und C;
- alle konkreten Ereigniswerte, Zeitintervalle, Quellen- und Traegerkennungen;
- die konkrete Dock-Anatomie, Sample-Offsets und Feldgeometrie;
- die festen Substrat- und Afterimage-Konfigurationen;
- eine kanonische Serialisierungsregel fuer A, B, C und die gemeinsame
  Laufkonfiguration;
- vorab erzeugte Digests dieser kanonischen Darstellungen.

Ohne diese Fixierung koennte eine Runner-Implementierung die eigentlichen
Untersuchungseingaben erstmals im Code festlegen. Das waere keine rein
mechanische Umsetzung des bereits eingefrorenen Vertrags und liesse
nachtraegliche Freiheitsgrade offen.

## 4. Vorabentscheidung

```text
arm_count:                              12
run_id_count:                           24
replicates_complete:                    true
fresh_field_per_replica_required:       true
measurement_points_m0_m3_fixed:         true
measurement_roles_fixed:                true
dissipation_none_gate_fixed:            true
abort_conditions_fixed:                 true
partial_result_interpretation_forbidden:true
a_b_c_structurally_fixable:             true
a_b_c_concretely_fixed:                 false
canonical_input_serialization_fixed:    false
canonical_input_digests_fixed:          false
runner_implementation_release_granted:  false
effect_run_release_granted:             false
field_run_started:                      false
```

Der Runner-Spezifikationsvertrag ist technisch konsistent, aber die
Ausfuehrungsvorabnahme ist fuer einen Implementierungsauftrag noch negativ.
Grund ist ausschliesslich die fehlende konkrete Vorab-Fixierung von A, B, C und
ihren Konfigurationsbytes. Die Hypothesen-, Mess- und Abbruchlogik wird nicht
beanstandet.

## 5. Korrigierter naechster Auftrag

Vor jeder Runner-Implementierung ist ein reiner Eingabe-Fixierungsvertrag zu
erstellen. Dieser Auftrag umfasst ausschliesslich:

- konkrete, inhaltsneutral benannte und vollstaendig geordnete Ereignislisten
  fuer A, B und C unter Verwendung vorhandener Rezeptor- und Zeitstrukturen;
- maschinell pruefbare Gleichheit von Ereignisanzahl, Dauer,
  Kontaktstaerkensumme, Geometrie und Modalitaetsbelegung zwischen A und B;
- eine bytegleiche einzige Definition von C fuer alle 24 Lauf-IDs;
- feste Dock-Anatomie, Sample-Offsets, Feldgeometrie, Substratkonfiguration und
  Afterimage-Konfiguration;
- eine kanonische Serialisierungsregel und feste Digests fuer A, B, C und die
  gemeinsame Konfiguration;
- explizit `dissipation_config: None`;
- keine Runner-Implementierung, keine Feldkonstruktion, keinen Testlauf und
  keine Ergebnisberechnung.

Der Eingabe-Fixierungsvertrag darf keine neuen Hypothesen, Messpunkte,
Messmetriken, Schwellen, Labels, Bedeutungen, Rewards oder Zieltopologien
einfuehren. Nach seiner Erstellung ist eine erneute, eng begrenzte
Ausfuehrungsvorabnahme erforderlich.

## 6. Aussage- und Projektsperren

Weiterhin nicht freigegeben sind:

- Runner-Implementierung,
- Effekt- oder Hypothesenlauf,
- Public-AV-Lauf,
- Produktionsschalter,
- Aenderung der Organismus- oder Felddynamik,
- Aussagen zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung,
  Semantik, Bewusstsein, Eigenstaendigkeit oder KI.
