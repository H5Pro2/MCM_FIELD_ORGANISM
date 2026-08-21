# S1-TK: Statischer Schema-, Kardinalitaets- und Fail-Closed-Validierungsvertrag der Kandidatenhuelle

## Status und Grenze

S1-TK konkretisiert die in S1-TJ gebundene modellneutrale
Kandidaten-Beobachtungshuelle als statischen Record- und Validierungsvertrag.

S1-TK bindet nur:

- Recordfamilien und ihre Referenzrichtung;
- feste Kardinalitaeten der bereits registrierten Expositionsachse;
- kanonische Ordnungen;
- Fail-Closed-Pruefreihenfolge und Fehlerklassen.

Nicht enthalten sind Kandidatenanatomie, Ressourcennamen, Gleichung,
Parameter, konkrete Werte, neue Digests, Implementierung, Tests, Lauf oder
Ergebnisentscheidung.

## Unveraenderliche aeussere Achse

Die Kandidatenhuelle verwendet ohne Erweiterung oder Umordnung:

```text
plan_count                 = 17
field_checkpoint_count     = 40
candidate_interval_count   = 127
node_count                 = 4
signed_field_components    = 320
post_probe_readout_count   = 17
```

Die 127 Intervalle folgen aus dem bereits real abgenommenen
Vier-Knoten-Lebenszyklus mit 1.778 Modellintervallen fuer 14 Rollen. S1-TK
fuehrt daraus keinen neuen Laufbudgetwert ab; es bindet nur dieselbe
vollstaendige Kandidatenachse.

## Planordnung

```text
01 F_A
02 F_C
03 F_G
04 T_EARLY
05 T_LATER
06 I_LOCAL
07 I_REMOTE
08 I_GAP
09 C_LOCAL
10 C_REMOTE
11 C_GAP
12 R_EARLY
13 R_LATE
14 U_RELEASED
15 U_EARLY
16 U_FRESH_B_EARLY
17 U_FRESH_B_LATE
```

Jeder Nicht-C-Plan besitzt in dieser Reihenfolge:

```text
ALIGNED_PRE_PROBE
POST_PROBE_READOUT
```

Jeder C-Plan besitzt:

```text
PRE_COMPETITION
POST_COMPETITION
ALIGNED_PRE_PROBE
POST_PROBE_READOUT
```

Damit entstehen exakt `14 * 2 + 3 * 4 = 40` Checkpointpositionen. Die
Knotenordnung bleibt `node-a, node-b, node-c, node-d` und je Checkpoint die
Komponentenordnung `S[4], H[4]`.

## Exakte Wurzelfamilien

Eine spaetere serialisierte Huelle darf auf oberster Ebene ausschliesslich
folgende logisch getrennte Familien besitzen:

```text
envelope_identity
candidate_field_profile
candidate_internal_evidence
candidate_controls
lifecycle_links
completion
```

Unbekannte, doppelte oder fehlende Wurzelfamilien sind ungueltig. Keine
Familie darf Comparatorresultate oder Baselinepayloads enthalten.

## S1 - EnvelopeIdentityRecord

Kardinalitaet: exakt 1.

Der Identitaetsrecord bindet spaeter typisiert:

- Schema- und Vertragsidentitaet;
- opake, vor Ausfuehrung registrierte Kandidatenrollenidentitaet;
- genau eine Kandidatenkonfigurationsidentitaet;
- Expositions-, Fixture-, Manifest- und Registrierungsidentitaet;
- Geometrie- und Knotenordnungsidentitaet;
- Quelleninventaridentitaet;
- Referenzidentitaet des unveraenderten S1-TG-Atlas;
- Kanonisierungs- und Laufzeitidentitaet.

Der Record enthaelt keine Parameterpayloads, Baselinewerte oder
Kandidatenzustandswerte.

## S2 - CandidatePlanRecord

Kardinalitaet: exakt 17 in Planordnung.

Jeder Planrecord referenziert:

- Planposition und Planrolle;
- gemeinsame Expositionsplanidentitaet;
- Frischzustandsidentitaet;
- unveraenderte Kandidatenkonfiguration;
- geordnete zugehoerige Checkpointrecords;
- ersten und letzten Carrybeleg;
- terminale Ereigniskettenidentitaet;
- planweisen Abschlussstatus.

Ein Planrecord enthaelt keine Feld- oder Bilanzzusammenfassung anstelle der
vollstaendigen Einzelrecords.

## S3 - CandidateFieldCheckpointRecord

Kardinalitaet: exakt 40 in der gebundenen Checkpointordnung.

Jeder Feldcheckpoint traegt spaeter:

- Planposition, Planrolle, Checkpointrolle und Checkpointtick;
- Fixtureereignis- und Ereigniskettenprovenienz;
- Feld-, Carry- und privaten Zustandsbezug;
- Konfigurations- und Abhaengigkeitsidentitaeten;
- Distributions- und Alignbezug, soweit fuer die Position zulaessig;
- vollstaendigen Rezeptorkontaktvektor;
- vollstaendigen signed S-Vektor;
- vollstaendigen signed H-Vektor;
- Feld- und Layertick;
- Eigendigest.

S und H bestehen immer aus vier endlichen Zahlen. R besteht aus vier
endlichen Zahlen oder exakt an `C_GAP/POST_COMPETITION` aus vier
Nullabilitaetsmarkern. Gemischte oder weitere nullable R-Lagen sind
ungueltig.

Aus den 40 Records wird spaeter genau ein 320-Komponenten-Profil in der
gebundenen Reihenfolge materialisiert. Der Profilrecord darf keine
Kandidatenbilanz oder Kontrollrolle enthalten.

## S4 - CandidateStateCheckpointRecord

Kardinalitaet: exakt 40, eins-zu-eins zu S3.

Jeder Record bindet:

- den zugehoerigen Feldcheckpoint;
- vollstaendigen privaten Zustandsdigest;
- Kandidatenkonfigurationsidentitaet;
- Carry- und Ereigniskettenidentitaet;
- die spaeter deklarierte Bilanzschemareferenz;
- den zugehoerigen Bilanzcheckpoint;
- Eigendigest.

Der private Zustandsdigest muss den vollstaendigen Kandidatenzustand binden,
ist aber kein numerischer Bilanzwert und kein Funktionsbeleg.

## S5 - CandidateTransitionRecord

Kardinalitaet: exakt 127 in gemeinsamer Intervallordnung.

Jeder Uebergangsrecord referenziert:

- Intervallordinal, Plan und gemeinsame Ereignisquelle;
- Vor- und Nachzustandsbeleg;
- Vor- und Nachcarry;
- Vor- und Nachbilanz;
- Feldfortschrittsbeleg;
- genau eine klassifizierte Kausalquelle;
- nativen Receipt- oder Diagnostikbezug;
- Eigendigest.

Im Hauptpfad ist als kandidatenbildende Quelle nur normale Feldgeschichte
zulaessig. Observer, Comparator, Armziel, Ergebnis, Reset, Recoverytoggle
oder altes Sidecar sind keine zulaessigen Quellen.

## S6 - CandidateBalanceCheckpointRecord

Kardinalitaet: exakt 40, eins-zu-eins zu S3 und S4.

Der Record ist anatomieneutral und traegt spaeter fuer die vollstaendig
vorregistrierte Kandidatenbilanz:

- Bilanzschemareferenz;
- alle lokalen Zustandskoordinaten je registriertem Ort;
- lokale Summen oder explizite lokale Dissipationsbuchungen;
- globale Summe der endlichen Testgeometrie;
- vollstaendige Zu-, Abfluss- und Transferbuchungen seit dem vorigen
  Bilanzcheckpoint;
- Bilanzrest;
- Zustands-, Checkpoint- und Eigendigestbezug.

S1-TK legt weder Anzahl noch Namen der spaeteren Ressourcenrollen fest. Der
spaetere Kandidatenvertrag muss jedoch eine feste Rollenachse deklarieren;
danach sind fehlende, zusaetzliche oder umgeordnete Rollen ungueltig.

## S7 - CandidateTransitionBalanceRecord

Kardinalitaet: exakt 127, eins-zu-eins zu S5.

Jeder Record bindet Vorbilanz, Nachbilanz, alle waehrend genau dieses
Intervalls deklarierten Transfers, Zu- und Abfluesse, Dissipation sowie den
resultierenden Rest. Er referenziert dieselbe Kausalquelle wie der
zugehoerige Uebergangsrecord.

Nichtendliche Werte, ungebuchte Koordinatenaenderungen, verdeckter globaler
Zustand oder nachtraegliche Normalisierung sind ungueltig. Eine konkrete
Bilanzgleichung und zulaessige Restregel muessen erst mit einer spaeteren
Kandidatenanatomie vorregistriert werden.

## S8 - ReadoutAblationRecord

Kardinalitaet: exakt 17, je einer fuer jeden `POST_PROBE_READOUT`.

Die Vollmenge wird vor einer Ergebniskenntnis verlangt. Ein spaeterer
Comparator darf Ablationen nicht nur fuer auffaellige Readouts auswaehlen.

Jeder Record bindet Original und Ablation mit:

- identischer Plan-, Expositions-, Frisch- und Konfigurationsidentitaet;
- identischem Geschichtspraefix und Ereigniskettenbezug;
- identischem Rezeptorkontakt und angeglichenem S/H-Vorzustand;
- identischem Kandidatenzustand unmittelbar vor dem Readout;
- identischer Geometrie, Zeitlage und Probe;
- vollstaendigen signed Original- und Ablationsreadouts;
- exklusivem Beleg, dass nur Kandidatenrueckwirkung fuer diesen Readout
  deaktiviert war;
- Eigendigest.

Eine Ablation darf keinen Hauptpfadcheckpoint ersetzen und nicht in das
320-Komponenten-Kandidatenprofil eingehen.

## S9 - DisabledFullPathProfile

Kardinalitaet:

```text
1 Kandidat-deaktivierter Vollpfad
1 unabhaengiger Feldkern-Referenzvollpfad
je 17 Planrecords
je 40 Feldcheckpointrecords
40 geordnete Nullpfad-Paarbelege
1 atomarer Nullpfad-Abschlussrecord
```

Der Kandidat ist ab Frischzustand ueber alle 127 gemeinsamen Intervalle
deaktiviert. Ein gesonderter Pfadbeleg muss zeigen, dass keine
Kandidatenfortschreibung und kein verdeckter Kandidatencarry stattfand.

Jeder Nullpfad-Paarbeleg verbindet exakt positionsgleiche Checkpoints beider
Vollpfade. Die konkrete bitgenaue Gleichheitsregel wird nicht aus einem
Ergebnis abgeleitet und darf spaeter keine Toleranz erhalten.

## S10 - ReleaseLifecycleLink

Kardinalitaet: exakt 1 atomarer R-Linkrecord.

Er referenziert vollstaendig:

- `R_EARLY` und `R_LATE` samt beiden Checkpoints;
- zugehoerige Zustands- und Bilanzrecords;
- gleiche Gap-, Probe-, Eingangs- und S/H-Provenienz;
- spaeteren Funktionsverlustbeleg;
- direkt ausgewiesene erneut nutzbare lokale Kapazitaet;
- Ausschluss von Reset, Clipping, Neustart und Recoverytoggle.

Der Link erzeugt selbst keinen Freigabestatus. Die konkrete
Falsifikationsregel bleibt einem spaeteren Kandidatenvertrag vorbehalten.

## S11 - ReuseLifecycleLink

Kardinalitaet: exakt 1 atomarer U-Linkrecord.

Er referenziert vollstaendig:

- `U_RELEASED`, `U_EARLY`, `U_FRESH_B_EARLY` und `U_FRESH_B_LATE`;
- den gueltigen S10-R-Link;
- Bilanzlage vor jeder B-Geschichte;
- erneute lokale Beanspruchung im freigegebenen Arm;
- vollstaendige B-Readouts und zeitangepasste Frischkontrollen;
- lueckenlose Identitaet der freigegebenen und erneut beanspruchten
  Zustandsrolle.

Ohne gueltigen R-Link ist der U-Link strukturell ungueltig.

## S12 - EnvelopeCompletionRecord

Kardinalitaet: exakt 1 und letzter Record der logischen Huelle.

Er bindet:

- Digests aller geordneten Recordfamilien;
- Vollstaendigkeits- und Kardinalitaetsbelege;
- Informationsbarrierenstatus;
- atomaren Huellendigest;
- genau einen technischen Abschlussstatus.

Zulaessig ist auf Huellenebene nur ein technisch vollstaendiger Status oder
`AUDIT_INVALID_NOT_COMPUTABLE`. S1-PX-Funktions- und Baselinereduktionsstatus
gehoeren ausschliesslich zu einem spaeteren getrennten Comparator.

## Referenzrichtung

Referenzen bilden einen gerichteten azyklischen Beleggraphen:

```text
Identity
  -> Plan / Field Checkpoint
  -> State / Balance
  -> Transition / Transition Balance
  -> Ablation / Disabled Full Path
  -> Release
  -> Reuse
  -> Completion
```

Rueckreferenzen duerfen nur Identitaet bestaetigen und keinen spaeteren
Status in einen frueheren Record einspeisen. Ein Record darf nicht sich
selbst oder einen noch nicht abgeschlossenen spaeteren Record als Ursache
verwenden.

## Geordnete Fail-Closed-Pruefung

Ein spaeterer Validator muss ohne Modellaufruf in dieser Reihenfolge pruefen:

1. kanonische Syntax, exakte Wurzelfamilien und Abschlussform;
2. Schema-, Vertrags-, Kandidaten-, Konfigurations- und Atlasidentitaet;
3. Plan-, Checkpoint-, Knoten- und Komponentenordnung;
4. 17 Plan- und 40 Feldcheckpointrecords;
5. 40 Zustands- und 127 Uebergangsrecords;
6. deklarierte Bilanzachse, 40 Bilanz- und 127 Intervallbilanzrecords;
7. Ereignis-, Carry-, Quellen- und Kausalprovenienz;
8. alle 17 Readoutablationen;
9. Kandidat-deaktivierter Vollpfad, Feldkern-Referenzvollpfad und 40
   Nullpfad-Paarbelege;
10. R-Link und direkte Freigabebindung;
11. U-Link nur nach gueltigem R-Link;
12. Informationssperren und atomaren Abschluss.

Der erste Fehler stoppt die Pruefung. Es wird genau eine Fehlerklasse ohne
Teilresultate publiziert.

## Gebundene Fehlerklassen

```text
ENVELOPE_CANONICAL_FORM_INVALID
ENVELOPE_ROOT_SCHEMA_INVALID
ENVELOPE_IDENTITY_INVALID
CANDIDATE_CONFIGURATION_IDENTITY_INVALID
ATLAS_REFERENCE_INVALID
EXPOSURE_REFERENCE_INVALID
PLAN_AXIS_INVALID
CHECKPOINT_AXIS_INVALID
FIELD_VECTOR_INVALID
RECEPTOR_NULLABILITY_INVALID
FIELD_PROFILE_DIGEST_INVALID
STATE_CHECKPOINT_COUNT_INVALID
STATE_CARRY_CHAIN_INVALID
TRANSITION_COUNT_INVALID
TRANSITION_CAUSAL_SOURCE_INVALID
BALANCE_SCHEMA_INVALID
BALANCE_CHECKPOINT_COUNT_INVALID
BALANCE_TRANSITION_COUNT_INVALID
BALANCE_RECORD_INVALID
ABLATION_COUNT_INVALID
ABLATION_PRECONDITION_MISMATCH
ABLATION_SCOPE_INVALID
NULL_PATH_CARDINALITY_INVALID
NULL_PATH_REFERENCE_INVALID
NULL_PATH_MISMATCH
NULL_PATH_CANDIDATE_STATE_LEAK
RELEASE_LINK_INVALID
REUSE_LINK_WITHOUT_RELEASE
REUSE_LINK_INVALID
INFORMATION_BARRIER_VIOLATION
ENVELOPE_COMPLETION_INVALID
PARTIAL_RESULT_FORBIDDEN
```

Jede Klasse kollabiert nach aussen zu:

```text
AUDIT_INVALID_NOT_COMPUTABLE
```

Fehlerdetails duerfen diagnostisch die Klasse und den ersten betroffenen
Recordordinal nennen, aber keine privaten Rohzustaende oder Teilkontraste
veroeffentlichen.

## Aussagegrenze

S1-TK bindet nur eine spaeter implementierbare, fail-closed pruefbare
Beobachtungsstruktur. Es existiert weiterhin kein Kandidat, keine
Ressourcenanatomie, keine Gleichung und kein Befund zu einer hypothetischen
MCM-Memory. Der S1-TG-Atlas und der primaere Feldkern bleiben unveraendert.

## Abschluss und naechster Schritt

```text
S1_TK_CANDIDATE_ENVELOPE_SCHEMA_CARDINALITY_AND_FAILURE_CLASSES_BOUND
17_PLANS_40_CHECKPOINTS_127_TRANSITIONS_AND_ALL_CONTROLS_REQUIRED
FIRST_ERROR_FAIL_CLOSED_WITHOUT_PARTIAL_RESULT
NO_CANDIDATE_NO_VALUES_NO_IMPLEMENTATION_NO_RUN
```

Der einzige naechste Schritt ist S1-TL als statischer
Nichtduplizierungs-, Informationsfluss- und Implementierungsreifeaudit. Er
soll pruefen, welche vorhandenen unveraenderten Recordtypen und
Kanonisierungshelfer S1-TK wiederverwenden kann, welche Kandidatenfelder neu
bleiben muessen und ob ein rein struktureller Validator ohne
Kandidatenmechanik implementierbar ist. Keine Implementierung, Tests,
Kandidatenwahl oder Ausfuehrung ist dabei zulaessig.
