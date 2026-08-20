# S1-MZ KFS-1 Validator- und Fixturevertrag

## Status

S1-MZ bindet ausschliesslich den statischen Validator- und Fixturevertrag
fuer das in S1-MY festgelegte KFS-1-Schema. Der Schritt implementiert keinen
Validator, fuehrt keine Kandidatendynamik aus und enthaelt keine Gleichung,
keine Dynamikparameter, keine Runtime und keinen Feldlauf.

Die Fixtures pruefen nur Schema, Anatomie, Bilanz, kausale Vergleichbarkeit,
Digeststabilitaet und Fail-Closed-Verhalten. Sie pruefen keine Wirkung und
keinen Befund zur hypothetischen MCM-Memory.

## Validatorgrenze

Der spaetere Validator ist eine reine Pruefkomponente ausserhalb des
MCM-Feldzustands. Er darf:

- unveraenderte Eingabebytes lesen;
- kanonische Serialisierung pruefen;
- registrierte Digests neu berechnen;
- Anatomie- und Bilanzregeln pruefen;
- Messrollen und Expositionsreferenzen vergleichen;
- einen getrennten Validierungsbeleg ausgeben.

Er darf weder Felder ergaenzen noch Werte normalisieren, sortieren,
korrigieren oder in das MCM-Feld beziehungsweise Ressourcenledger schreiben.

## Mehrstufige Pruefung

Die Pruefung erfolgt in fester Reihenfolge:

1. `byte_intake`: Die unveraenderten Eingabebytes erhalten einen
   `input_bytes_digest`.
2. `schema_validation`: Schema-ID, Version, Pflichtfelder, Zusatzfelder und
   kanonische Byteform werden geprueft.
3. `anatomy_validation`: Traeger, Kanten, Geometrie und Feldreferenzen werden
   geprueft.
4. `ledger_validation`: Endlichkeit, Nichtnegativitaet, Erhaltungsidentitaet
   und Doppelzaehlung werden geprueft.
5. `causal_validation`: Messrolle, passiver Lesebereich und relevante
   Expositionshistorie werden geprueft.
6. `digest_validation`: Erst nach den strukturellen Pruefungen werden die
   jeweils berechenbaren Record-Digests verglichen.
7. `validation_receipt`: Status und kanonisch geordnete Fehlergruende werden
   ausserhalb des geprueften Records ausgegeben.

Ein frueher Fehler beendet nicht die sichere Suche nach weiteren unabhaengig
feststellbaren Fehlern. Eine Pruefung, die wegen fehlender Voraussetzung nicht
ausgefuehrt werden kann, erzeugt aber keinen erfundenen Folgedefekt.

## Validierungsbeleg

Der `kfs1_validation_receipt` besitzt genau folgende Felder:

| Feld | Bindung |
|---|---|
| `receipt_schema_id` | exakt `kfs1_validation_receipt` |
| `receipt_schema_version` | registrierte S1-MZ-Version |
| `input_bytes_digest` | SHA-256 der unveraenderten Eingabebytes |
| `declared_record_schema_id` | gelesene Schema-ID oder explizit `unreadable` |
| `validation_status` | exakt `valid` oder `invalid` |
| `completed_checks` | kanonisch geordnete, tatsaechlich ausgefuehrte Checks |
| `failure_reasons` | lexikographisch geordnete S1-MY-Fehlercodes |
| `computed_record_digest` | berechneter Record-Digest oder `not_computable` |
| `validator_contract_digest` | Identitaet des gebundenen Validatorvertrags |
| `validation_receipt_digest` | Digest ueber alle vorstehenden Felder |

`validation_status` und `failure_reasons` im S1-MY-Messrollenrecord sind
abgeleitete Exportfelder. Der Validator darf sie nicht als vertrauenswuerdige
Eingabe fuer sein Urteil verwenden. Bei einem ungueltigen Eingaberecord bleibt
der `input_bytes_digest` stets erhalten, auch wenn kein normaler Record-Digest
berechenbar ist.

## Gueltige Minimalfixtures

S1-MZ bindet zwei positive Referenzklassen ohne dynamische Zahlenfestlegung:

| Fixture-ID | Inhalt | Erwartung |
|---|---|---|
| `V_ANATOMY_MIN_01` | zwei eindeutige Traeger, eine Kante, genau ein endliches `free/bound/blocked`-Ledger, stimmige Geometrie- und Feldreferenz | `valid`, keine Fehlergruende |
| `V_MEASUREMENT_MIN_01` | eine registrierte passive Messrolle mit passendem Anatomie-, Feldreferenz- und Expositionsdigest | `valid`, keine Fehlergruende |

Die konkreten statischen Fixturewerte und ihre erwarteten SHA-256-Digests
duerfen erst bei der spaeteren Implementierungsbindung materialisiert werden.
Sie sind Testdaten und keine Dynamikparameter.

## Einzeldefekt-Fixtures

Jedes negative Fixture wird aus genau einer positiven Referenz durch genau
eine registrierte Mutation erzeugt. Dadurch bleibt der erwartete primaere
Ablehnungsgrund eindeutig.

| Fixture-ID | Einzige Mutation | Erwarteter Grund |
|---|---|---|
| `I_SCHEMA_VERSION_01` | unbekannte Schemaversion | `UNKNOWN_SCHEMA_OR_VERSION` |
| `I_FIELD_MISSING_01` | ein Pflichtfeld entfernt | `MISSING_OR_UNKNOWN_FIELD` |
| `I_FIELD_EXTRA_01` | unbekanntes Zusatzfeld eingefuegt | `MISSING_OR_UNKNOWN_FIELD` |
| `I_SERIALIZATION_01` | nichtkanonische Objektfeldfolge | `NONCANONICAL_SERIALIZATION` |
| `I_CARRIER_DUPLICATE_01` | Traeger-ID dupliziert | `DUPLICATE_CARRIER_OR_EDGE_ID` |
| `I_EDGE_GEOMETRY_01` | Kanten-ID passt nicht zum Traegerpaar | `EDGE_ID_GEOMETRY_MISMATCH` |
| `I_RESOURCE_NEGATIVE_01` | genau eine Ressourcenrolle negativ | `NEGATIVE_OR_NONFINITE_RESOURCE_ROLE` |
| `I_RESOURCE_NONFINITE_01` | genau eine Ressourcenrolle nicht endlich | `NEGATIVE_OR_NONFINITE_RESOURCE_ROLE` |
| `I_CAPACITY_SUM_01` | Ledger-Summe weicht von Kapazitaet ab | `RESOURCE_CAPACITY_MISMATCH` |
| `I_RESOURCE_DUPLICATE_01` | dasselbe Ressourcenkonto zwei Kanten zugeordnet | `RESOURCE_DOUBLE_COUNTING` |
| `I_FIELD_REFERENCE_01` | Mess- und Anatomiereferenz unterscheiden sich | `FIELD_REFERENCE_MISMATCH` |
| `I_ANATOMY_DIGEST_01` | Messrecord verweist auf anderen Anatomiedigest | `ANATOMY_DIGEST_MISMATCH` |
| `I_EXPOSURE_MISSING_01` | Expositionshistorie fehlt | `EXPOSURE_HISTORY_MISSING_OR_MISMATCHED` |
| `I_EXPOSURE_MISMATCH_01` | Baseline besitzt nicht aequivalente Vorgeschichte | `EXPOSURE_HISTORY_MISSING_OR_MISMATCHED` |
| `I_MEASUREMENT_ROLE_01` | nicht registrierte Messrolle | `UNREGISTERED_MEASUREMENT_ROLE` |
| `I_READ_SCOPE_01` | Messrolle fordert Schreibzugriff | `READ_SCOPE_NOT_PASSIVE` |
| `I_FORBIDDEN_PAYLOAD_01` | Rohdaten, Label, Ziel oder Sequenzpuffer eingefuegt | `RAW_DATA_LABEL_TARGET_OR_SEQUENCE_BUFFER_PRESENT` |
| `I_DIGEST_01` | deklarierter Digest gegen unveraenderten Inhalt ausgetauscht | `DIGEST_MISMATCH` |

## Mehrfachdefekt-Fixtures

Mehrfachdefekte pruefen nur die deterministische Sammlung und Sortierung der
Fehlergruende:

| Fixture-ID | Mutationen | Erwartung |
|---|---|---|
| `I_MULTI_SCHEMA_LEDGER_01` | unbekanntes Zusatzfeld und falsche Kapazitaet | beide unabhaengig feststellbaren Codes, lexikographisch sortiert |
| `I_MULTI_CAUSAL_READ_01` | unpassiver Lesebereich und unpassende Expositionshistorie | beide Codes, lexikographisch sortiert |
| `I_MULTI_UNREADABLE_01` | Byteform verhindert Schemaauswertung | nur sicher feststellbare Intake-/Schemafehler, keine erfundenen Folgefehler |

## Digeststabilitaets-Fixtures

Folgende Relationen muessen spaeter bitgenau geprueft werden:

- identische kanonische Bytes erzeugen denselben `input_bytes_digest`;
- erneute Validierung erzeugt denselben Validierungsbeleg;
- eine Inhaltsaenderung ohne Digestanpassung scheitert mit `DIGEST_MISMATCH`;
- eine Aenderung der Expositionshistorie veraendert nur die dafuer
  registrierten abhaengigen Digests;
- Geometrie-, Ressourcen-, Expositions- und Messrollendigests bleiben
  getrennte Identitaeten;
- ein ungueltiger Record wird niemals durch Neuordnung oder Normalisierung in
  ein positives Fixture ueberfuehrt.

Digestunterschiede bleiben technische Identitaetsunterschiede. Sie sind kein
Messwert fuer Kohaerenz, Wirkung oder spaetere Aufnahmeaenderung.

## Abnahmekriterien

S1-MZ ist statisch erfuellt, wenn:

- jede Validatorphase und ihre Eingabegrenze eindeutig ist;
- positive und negative Fixtureklassen vollstaendig gebunden sind;
- jeder Einzeldefekt genau einen primaeren erwarteten Fehlercode besitzt;
- Mehrfachfehler deterministisch und ohne erfundene Folgedefekte erscheinen;
- der unveraenderte Eingabebyte-Digest auch bei ungueltigen Records erhalten
  bleibt;
- keine Reparatur, Dynamik, Feldrueckwirkung oder Funktionswertung zugelassen
  wird.

## Ergebnis von S1-MZ

S1-MZ macht das S1-MY-Schema implementierbar und pruefbar, ohne KFS-1 bereits
auszufuehren. Die Forschungsrichtung bleibt damit methodisch offen, weil ein
spaeterer Kandidat nur auf vorab akzeptierten, kausal fairen Records aufbauen
darf.

## Naechster erlaubter Schritt

Der naechste Schritt ist S1-NA, ausschliesslich als Implementierungsvertrag
fuer einen isolierten statischen KFS-1-Schema-Validator und die in S1-MZ
gebundenen Fixtures. Er darf Dateigrenzen, reine Funktionen, Testumfang und
ein endliches Ausfuehrungsbudget festlegen. Kandidatengleichung,
Dynamikparameter, Runtimeintegration, Feldlauf und Funktionsentscheidung
bleiben gesperrt.
