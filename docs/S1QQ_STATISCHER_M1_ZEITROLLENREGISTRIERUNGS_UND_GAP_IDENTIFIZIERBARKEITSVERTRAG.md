# S1-QQ: Statischer M1-Zeitrollenregistrierungs- und Gap-Identifizierbarkeitsvertrag

## Status und Umfang

S1-QQ registriert fuer die in S1-QP gebundene M1-Zweispurfamilie genau zwei
konkrete Zeitrollen und genau drei kumulative Gap-Messpositionen. Der Vertrag
prueft rein analytisch, ob der gleichgewichtete Zweispurreadout auf dieser
Zeitachse von einer einzelnen festen Exponentialspur unterscheidbar ist.

S1-QQ implementiert keine Spezifikation, keinen Zustand und keinen
Kompositor. Es wird kein Test, keine Runtime und kein Feldlauf ausgefuehrt.
Der primaere Feldkern und alle geschlossenen Zweige bleiben unveraendert.

Vertragsentscheidung:

```text
M1_FAST_TAU_ONE_SECOND_AND_SLOW_TAU_FOUR_SECONDS_REGISTERED
M1_CUMULATIVE_GAP_CHECKPOINTS_ONE_FOUR_EIGHT_SECONDS_REGISTERED
THREE_POINT_SINGLE_EXPONENTIAL_IDENTIFIABILITY_CHECK_PASSED_ANALYTICALLY
CANONICAL_TIME_AXIS_PAYLOAD_AND_DIGEST_BOUND
NO_IMPLEMENTATION_NO_TEST_NO_FIELD_EXECUTION
```

## Herkunft der Zeitachse

Die Auswahl verwendet ausschliesslich bereits vorhandene technische
Zeitrollen des Projekts:

- eine Sekunde ist die vorhandene W7-M-`LEAK`-Zeitkonstante;
- eine Sekunde ist zugleich eine wiederholt verwendete abgeschlossene
  Geschichtsintervalllaenge;
- vier Sekunden sind eine vorhandene technische Gap-Grenze;
- die kumulativen Gap-Punkte eine, vier und acht Sekunden sind im Bestand
  bereits als geordnete technische Messachse verwendet;
- die zugehoerigen inkrementellen Nullkontaktintervalle sind eine, drei und
  vier Sekunden.

Aus diesen Verwendungen werden nur Zahlen und ihre Zeitordnung uebernommen.
Nicht uebernommen werden:

- E1-Zustand, Gleichung, Parameter oder Kandidatenmechanik;
- historische Runner-, Profil- oder Ergebnisdaten;
- Release-, Bindungs-, Ressourcen- oder Entwicklungsrollen;
- alte Digests, Toleranzen oder Befundentscheidungen.

Die Zeitwahl liest keine M1-Ausgabe und kein spaeteres Kandidatenergebnis.

## Registrierte M1-Zeitrollen

Verbindlich gilt:

| Spurrolle | `equation_id` | `time_constant_seconds` |
|---|---|---:|
| `FAST` | `baseline.m1.fast-local-leak.v1` | `1.0` |
| `SLOW` | `baseline.m1.slow-local-leak.v1` | `4.0` |

Beide Rollen verwenden:

```text
model_id = leak
equation_contract = dz_i/dt=(S_i-z_i)/tau;R_i=0
persistent_scalars_per_neuron = 1
organism_runtime_allowed = false
parameter_bindings = nur time_constant_seconds
```

Damit gilt exakt:

```text
tau_FAST = 1.0 s
tau_SLOW = 4.0 s
tau_SLOW / tau_FAST = 4
```

Andere Werte, Bereiche, Fitparameter oder armweise Varianten sind nicht Teil
der registrierten M1-Familie.

## Registrierte Gap-Achse

Die kumulativen Messpositionen ab Beginn des Nullkontakt-Gaps sind:

```text
G1 = 1.0 s
G4 = 4.0 s
G8 = 8.0 s
```

Bei sequenzieller Fortschreibung entstehen daraus:

```text
START -> 1.0 s -> G1
G1    -> 3.0 s -> G4
G4    -> 4.0 s -> G8
```

Jedes Intervall verwendet normalen `GAP_ZERO_CONTACT`, denselben Feldcarry
und denselben privaten M1-Carry. Ein Checkpoint ist passiv und fuehrt weder
A1 noch eine M1-Spur fort.

Ein zulaessiger spaeterer Ablauf darf nicht drei getrennte Frischzustaende
fuer G1, G4 und G8 verwenden. Alle drei Punkte muessen derselben kausalen
Gap-Fortsetzung entstammen.

## Kanonische Registrierung

Die kanonische kompakte UTF-8-JSON-Payload lautet exakt:

```json
{"contract_id":"m1-two-trace-time-axis/s1qq.v1","gap_checkpoints_seconds":[1.0,4.0,8.0],"readout_id":"pointwise-equal-mean/v1","trace_specs":[{"equation_contract":"dz_i/dt=(S_i-z_i)/tau;R_i=0","equation_id":"baseline.m1.fast-local-leak.v1","model_id":"leak","organism_runtime_allowed":false,"parameter_bindings":[["time_constant_seconds",1.0]],"persistent_scalars_per_neuron":1,"role_id":"FAST"},{"equation_contract":"dz_i/dt=(S_i-z_i)/tau;R_i=0","equation_id":"baseline.m1.slow-local-leak.v1","model_id":"leak","organism_runtime_allowed":false,"parameter_bindings":[["time_constant_seconds",4.0]],"persistent_scalars_per_neuron":1,"role_id":"SLOW"}]}
```

Ihr SHA-256-Digest ist:

```text
141b552532f0f43449e2d92c2d09274eae6acb66b224cd287b12b3a6d8d63f3b
```

Jede Aenderung an Zeitwert, Rollenordnung, Gleichungsidentitaet,
Parameterbindung, Readoutidentitaet oder Gap-Punkt erzeugt eine andere
Konfiguration und ist fuer S1-QQ unzulaessig.

## Analytische Identifizierbarkeitsreferenz

Die statische Referenz setzt am Gap-Beginn beide lokalen Spurwerte auf
denselben positiven Einheitswert. Diese Normierung ist nur eine analytische
Strukturprobe. Sie ist keine Initialisierungsregel fuer einen spaeteren
Lebenszyklusarm.

Unter Nullkontakt gilt fuer den gebundenen Mittelwert:

```text
y(t) = (exp(-t / 1.0) + exp(-t / 4.0)) / 2
```

An den registrierten Punkten ergibt sich:

| Punkt | FAST | SLOW | Mittelwert `y(t)` |
|---|---:|---:|---:|
| G1 | `0.36787944117144233` | `0.7788007830714049` | `0.5733401121214237` |
| G4 | `0.01831563888873418` | `0.36787944117144233` | `0.19309754003008825` |
| G8 | `0.00033546262790251185` | `0.1353352832366127` | `0.06783537293225761` |

Eine einzelne positive Exponentialspur, die zwei aufeinanderfolgende
Messabschnitte jeweils exakt erklaeren soll, benoetigte:

```text
tau_single(G1 -> G4) = 2.7566342538378557 s
tau_single(G4 -> G8) = 3.8236835782814316 s
```

Die beiden erforderlichen Werte sind nicht gleich. Ein einziger fester
Einspurparameter kann daher die drei registrierten Referenzpunkte nicht
gemeinsam exakt reproduzieren.

Diese Rechnung zeigt nur strukturelle Identifizierbarkeit der registrierten
M1-Familie. Sie zeigt nicht, dass ein spaeterer Feldverlauf diese Familie
benoetigt oder dass ein Effekt vorhanden ist.

## Gueltigkeitsbedingungen fuer eine spaetere endliche Fixture

Eine spaetere M1-Komponentenfixture muss vor einer Ergebnisentscheidung
belegen:

- beide Spuren starten frisch und werden durch dieselbe einpolige Evidence
  normal fortgeschrieben;
- beide Vor-Gap-Zustaende sind endlich, gleichgerichtet und ungleich null;
- beide Spuren sehen im Gap exakt denselben Nullkontakt und dieselben
  inkrementellen Zeiten `1.0`, `3.0`, `4.0` Sekunden;
- G1, G4 und G8 stammen aus einem lueckenlosen gemeinsamen Carry;
- der Readout bleibt an allen Punkten der gleichgewichtete lokale Mittelwert;
- kein Checkpoint veraendert Feld oder Zustand;
- eine Einspurvergleichsrolle verwendet einen einzigen vorregistrierten
  Zeitparameter fuer alle drei Punkte.

Sind eine Spur oder ihr Readoutbeitrag numerisch null, kann die konkrete
Fixture M1 nicht identifizieren und ist `not_computable`. Sie darf nicht
durch staerkere Exposition, neue Gewichte oder andere Zeitwerte nachgebessert
werden.

## Abgrenzung gegen Einspurbaselines

Die Identifizierbarkeitspruefung richtet sich gegen:

- A1 mit seiner einzelnen festen H-Zeitrolle;
- vorhandene B3-Einspurrollen;
- M5_DIRECT mit genau einem W7-N-`LEAK`-Zustand;
- jeden nachtraeglich vorgeschlagenen einzelnen positiven Exponentialfit.

Eine Einspurbaseline wird nicht getrennt fuer G1-G4 und G4-G8 neu angepasst.
Sie muss dieselbe Spezifikation und denselben Zustand durch die gesamte
Geschichte tragen.

Reproduziert eine zulaessige Einspurrolle spaeter dennoch das vollstaendige
gemeinsame Feldprofil unter der vorab gebundenen Comparatorregel, ist M1 fuer
diesen Vergleich nicht erforderlich. Die analytische Referenz ersetzt diese
spaetere faire Gesamtpruefung nicht.

## Numerische Grenze

S1-QQ bindet die dargestellten Referenzwerte als mathematische Sollwerte,
aber noch keine Implementierungstoleranz. Ein spaeterer Testbudgetvertrag
muss eine einzige feste numerische Toleranz vor Ausfuehrung festlegen.

Unzulaessig sind:

- eine Toleranz aus einem beobachteten M1- oder Kandidatenfehler;
- unterschiedliche Toleranzen je Gap-Punkt oder Modell;
- gerundete Tabellenwerte als Zustandsinput;
- logarithmische Auswertung nicht positiver oder nicht endlicher Werte;
- Akzeptanz nur aufgrund sichtbar verschiedener Kurven ohne formale
  Drei-Punkt-Pruefung.

## Fail-Closed-Regeln

M1 bleibt gesperrt, wenn:

- Zeitwerte oder Gap-Punkte vom kanonischen Payload abweichen;
- FAST und SLOW dieselbe Spezifikation oder denselben Zustand aliasieren;
- Gap-Punkte aus getrennten Frischlaeufen zusammengesetzt werden;
- ein historisches E1-Profil oder ein Kandidatenzustand als M1-Eingabe dient;
- eine Spur eine andere Evidence oder Intervalldauer erhaelt;
- Parameter oder Toleranzen nach Ergebnissicht geaendert werden;
- weniger als drei Gap-Punkte gemeinsam bewertet werden;
- die analytische Referenz als Feldbefund ausgegeben wird;
- ein Teilresultat trotz fehlender Identifizierbarkeit verglichen wird.

## Paketstatus

Nach S1-QQ gilt:

```text
M1_TWO_TRACE_TIME_VALUES_AND_GAP_AXIS_REGISTERED
M1_STATIC_THREE_POINT_IDENTIFIABILITY_PRESENT
M1_STATE_COMPOSITOR_ERRORS_AND_TEST_BUDGET_UNBOUND
M1_IMPLEMENTATION_AND_EXECUTION_NOT_AUTHORIZED
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

## Aussagegrenze

S1-QQ ist eine statische technische Registrierung. Sie bestaetigt keine
Mehrzeitskalenwirkung im Feld, keinen Kandidaten und keinen Befund zu einer
hypothetischen MCM-Memory. Alte E1-Mechaniken und Ergebnisse werden nicht
wiedereroeffnet.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QR - statischer M1-Zustands-, Kompositor-, Fehlercode- und
        Testbudgetvertrag
```

S1-QR soll die private Zwei-Spur-Zustandsoberflaeche, atomare
A1/`REPLACE_S`-Komposition, kanonische Receipts, deterministische Fehlercodes
und genau ein begrenztes Testbudget binden. Keine Implementierung,
Testausfuehrung oder Feldentscheidung.
