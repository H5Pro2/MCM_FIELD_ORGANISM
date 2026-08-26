# S1-SU: Statischer Baseline-Referenz-Comparator-, Metrik-, Toleranz- und Falsifikationsvertrag

## Status und methodische Korrektur

S1-SU bindet ausschliesslich die spaetere passive Auswertung des in S1-SS
publizierten Pflichtbaselineartefakts. Das Artefakt enthaelt 14
Baseline- und Kontrollrollen, aber keinen neuen Kandidaten, keine
Kandidatenbilanz und keine Kandidatenablation.

Deshalb darf der Comparator aus diesem Artefakt keinen S1-PX-Funktionsstatus
und kein Residuum einer hypothetischen MCM-Memory-Entwicklungsrichtung
bilden. Seine zulaessige Aufgabe ist nur:

- vollstaendige technische Referenzprofile je Baseline;
- vorregistrierte rohe F-/T-/I-/C-/R-/U-Kontrastvektoren je Baseline;
- paarweise Baseline-Profilredundanz unter einer festen Regel;
- atomare Fail-Closed-Ausgabe ohne Modellrangfolge.

S1-SU liest keine Ergebniswerte, implementiert keinen Comparator und fuehrt
keine numerische Auswertung aus.

## Kanonische Vertragsidentitaet

```text
contract_id          = mcm.s1su.baseline-reference-comparator.v1
source_artifact      = 69a3c11613d2d83660a870dfdb288b98b23e7af9934463d7836ccd77340618bb
matrix_result_digest = 1188e83b4ebfb8327e8fed22e85c8a17751f9b2eaf846632091ac01c1499dde5
contract_digest      = 639cf70ab24892fb0e59e5baaba6c952b99b8ad16c498acf2a399841d44c5a50
```

Der Vertragsdigest ist SHA-256 der 1.977 Byte langen kanonischen
Compact-JSON-Praeimage mit sortierten Schluesseln, ASCII, ohne NaN und ohne
eigenes Digestfeld. Sie bindet Rollenachsen, Profilordnung, 320 Komponenten,
91 Paare, alle 23 Kontrastrollen, Metriken, Toleranzen und Statusvokabular.

## Eingabepreflight

Vor jeder Zahlenoperation muessen die S1-QA-Gates 1 bis 6 fuer das
Baselinepaket bestehen:

1. Artefaktbytes, Schema, Vertrags- und Ausfuehrungsidentitaet;
2. 14 Modellrollen, 17 Plaene, 238 Summarys und 560 Checkpoints;
3. Manifest-, Registrierungs-, Fixture-, Geometrie-, Zeit- und
   Rezeptorprovenienz;
4. Frischzustands-, Carry-, Konfigurations- und Checkpointidentitaet;
5. belastungsangepasste B/C- und zeitangepasste Gap-/U-Kontrollen;
6. gleicher aktueller Kontakt sowie angeglichenes S und H vor jedem
   vorgesehenen Readoutkontrast.

Der Comparator muss die in S1-ST gebundene Rekonstruktion aus Artefakt,
Manifest, Registrierung und Fixture selbst fail-closed ausfuehren. Ein
fehlendes oder abweichendes Element ergibt ausschliesslich
`AUDIT_INVALID_NOT_COMPUTABLE` und keine Teilmetrik.

## Kanonische Profilachse

Fuer jede Modellrolle wird genau ein vollstaendiges Profil gebildet. Die
Reihenfolge ist:

```text
Planposition 1 bis 17
-> Ereignisreihenfolge der 40 Checkpoints
-> signed_activation_vector S, danach signed_afterimage_vector H
-> node-a, node-b, node-c, node-d
```

Damit besitzt jedes Modellprofil exakt:

```text
40 Checkpoints x 2 Kanaele x 4 Knoten = 320 signed Komponenten
```

Keine Komponente darf ausgewaehlt, betragsgebildet, sortiert oder verworfen
werden. Der vollstaendige signed Profilvektor und jeder signed
Residualvektor bleiben Bestandteil des spaeteren Comparatorresultats.

`signed_activation_vector` ist der primaere S1-PX-Feldreadout.
`signed_afterimage_vector` ist H und bleibt gemeinsame Kontroll- und
Profilkomponente. Feld-, Carry-, Privatstatus- und Distributionsdigests sind
nur Integritaetsbelege und keine numerischen Distanzen.

## Feste Rohkontraste

Jeder Residualvektor wird ausschliesslich als `links - rechts` gebildet.
Die folgenden Rollen sind vollstaendig und unveraenderlich:

```text
F_AC = F_A - F_C
F_AG = F_A - F_G
F_CG = F_C - F_G

T_LE = T_LATER - T_EARLY

I_LR = I_LOCAL - I_REMOTE
I_LG = I_LOCAL - I_GAP
I_RG = I_REMOTE - I_GAP

C_PRE_LR, C_PRE_LG, C_PRE_RG
C_POST_MINUS_PRE_LOCAL
C_POST_MINUS_PRE_REMOTE
C_POST_MINUS_PRE_GAP
C_DELTA_LR, C_DELTA_LG, C_DELTA_RG
C_READOUT_LR, C_READOUT_LG, C_READOUT_RG

R_LE = R_LATE - R_EARLY

U_RELEASED_FRESH = U_RELEASED - U_FRESH_B_LATE
U_EARLY_FRESH    = U_EARLY - U_FRESH_B_EARLY
U_RELEASED_EARLY = U_RELEASED - U_EARLY
```

`C_DELTA` vergleicht die jeweiligen `POST_COMPETITION - PRE_COMPETITION`-
Vektoren. `C_READOUT` verwendet `POST_PROBE_READOUT`.

`U_RELEASED_EARLY` ist wegen verschiedener B-Startzeiten nur Diagnostik.
Die beiden methodisch kontrollierten U-Kontraste verwenden jeweils ihre
eigene zeitangepasste Frischkontrolle. Kein einzelner Kontrast erzeugt eine
Funktionsentscheidung.

## Metriken und feste Toleranzen

Fuer jeden signed Residualvektor `r` wird zusaetzlich rein diagnostisch
berechnet:

```text
Linf(r) = max_i abs(r_i)
```

Die absolute technische Kontrollgrenze lautet projektweit einheitlich:

```text
absolute_control_tolerance = 1e-12
```

Sie gilt nur fuer konstruktive Gleichheits-, Angleichungs-, Null- und
Provenienzkontrollen. Ein Funktionssignal wird nicht allein deshalb
angenommen, weil es `1e-12` ueberschreitet.

Fuer zwei vollstaendige 320-Komponenten-Profile `x` und `y` gilt:

```text
D_abs(x,y) = Linf(x-y)
scale(x,y) = max(Linf(x), Linf(y), 1e-12)
D_rel(x,y) = D_abs(x,y) / scale(x,y)
```

Die vorab uebernommene projektweite Profil-Aequivalenzgrenze lautet:

```text
profile_equivalence_limit = 0.05
```

Zwei Baselineprofile sind nur dann fuer dieses Paket profilredundant, wenn
`D_rel <= 0.05` ueber die gesamte 320-Komponenten-Achse gilt. Die Regel ist
symmetrisch, verwendet keine Modellrolle als bevorzugten Nenner und darf
nicht je Familie, Modell oder Ergebnis angepasst werden.

`D_rel > 0.05` bedeutet nur `BASELINE_PROFILES_DISTINCT_UNDER_BOUND_METRIC`.
Es ist kein Qualitaetsurteil und kein positiver Funktionsbefund.

## Paar- und Ausgabematrix

Alle 14 Modellprofile werden in der registrierten Rollenordnung
vollstaendig paarweise verglichen:

```text
14 x 13 / 2 = 91 ungeordnete Modellpaare
```

Jedes Paarresultat bindet:

- beide Rollen- und Konfigurationsidentitaeten;
- beide Profil- und Quelldigests;
- den vollstaendigen signed 320-Komponenten-Residualvektor;
- `D_abs`, `scale`, `D_rel`;
- exakt einen Status `PROFILE_EQUIVALENT` oder `PROFILE_DISTINCT`;
- einen kanonischen Eigendigest.

Alle F-/T-/I-/C-/R-/U-Rohkontraste bleiben zusaetzlich je Modell erhalten.
Es gibt kein Best-of, keinen Sieger, keine Baselinepraezedenz und keinen
vorzeitigen Stopp nach einem Paar.

## Falsifikations- und Statusgrenze

Der Baseline-Referenzcomparator ist technisch falsifiziert und liefert nur
`AUDIT_INVALID_NOT_COMPUTABLE`, wenn unter anderem:

- Artefakt oder Seiteneingaben nicht exakt den gebundenen Digests
  entsprechen;
- eine Rolle, ein Plan, Checkpoint oder Profilwert fehlt;
- Vor-Readout-Kontakt, S oder H ausserhalb `1e-12` nicht angeglichen ist;
- B/C-Last, Gap-Zeit oder U-Frischzeit nicht konstruktiv kontrolliert ist;
- Konfigurationen zwischen Armen wechseln;
- Vektoren gekuerzt, umgeordnet, betraglich ersetzt oder nach Ergebnis
  skaliert werden;
- eine Toleranz oder Rollenreihenfolge nachtraeglich geaendert wird;
- ein Teilresultat trotz Fehler publiziert wird.

Bei vollstaendiger technischer Gueltigkeit lautet der Paketstatus nur:

```text
BASELINE_REFERENCE_ATLAS_COMPUTABLE
S1PX_CANDIDATE_GATES_NOT_APPLICABLE
```

Weder paarweise Redundanz noch Verschiedenheit bestaetigt endogene Bildung,
Abschwaechung, Interferenz, Kapazitaet, Freigabe oder Wiederverwendung. Die
S1-QA-Gates 7 bis 16 bleiben ohne getrenntes Kandidaten-, Bilanz-, Nullpfad-
und Ablationspaket nicht anwendbar.

Ein spaeterer Kandidat waere unter derselben Profilregel baseline-reduziert,
wenn mindestens eine faire Pflichtbaseline sein vollstaendiges
40-Checkpoint-S/H-Profil mit `D_rel <= 0.05` reproduziert. Eine
kandidateninterne Bilanz darf ein solches Feldprofilfit nicht aufheben.
Diese Zukunftsregel entscheidet am aktuellen Artefakt nichts.

## Verbindliche Entscheidung und naechster Schritt

```text
BASELINE_REFERENCE_COMPARATOR_METRIC_TOLERANCE_AND_STATUS_CONTRACT_BOUND
FULL_320_COMPONENT_PROFILES_AND_91_PAIR_MATRIX_REQUIRED
NO_CANDIDATE_NO_NUMERICAL_EVALUATION_NO_FUNCTIONAL_DECISION
```

Der einzige naechste Schritt ist S1-SV fuer die reine passive
Comparatorimplementierung und hoechstens 20 noch nicht ausgefuehrte
synthetische Tests. S1-SV darf das reale S1-SS-Artefakt nicht numerisch
auswerten, keinen Runner oder Modellkern importieren und keinen
S1-PX-Funktionsstatus erzeugen.
