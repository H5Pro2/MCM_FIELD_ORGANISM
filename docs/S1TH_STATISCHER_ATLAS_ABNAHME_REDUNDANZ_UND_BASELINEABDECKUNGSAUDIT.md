# S1-TH: Statischer Atlas-Abnahme-, Redundanz- und Baselineabdeckungsaudit

## Umfang

S1-TH liest ausschliesslich das in S1-TG publizierte kanonische Artefakt und
die vorab gebundenen Comparator- und Zweiggrenzen. Es wurde kein Comparator,
Test, Modellproducer oder Feldlauf gestartet und kein Parameter veraendert.

Geprueft wurden:

- Identitaet und Vollstaendigkeit des Ergebnisartefakts;
- die vollstaendige 15/76-Paartopologie;
- die Lage der Paare relativ zur festen Grenze `D_rel = 0.05`;
- die Bedeutung der Profilredundanz fuer spaetere faire Baselinevergleiche;
- der fortbestehende Infrastrukturstatus geschlossener Zweige.

## Artefaktabnahme

```text
file_sha256
  b8df5c0cb010169432b93b1af42b3e5720edc8299060a994298e996bfcbefe3a
artifact_digest
  b63c12967fbab69740341af2f011839652762efcd71c8b29c851511ce0c20a9f
result_digest
  dd38f95829e04934ffd678956d52e380729042fe5d7710e99d672a92885b3a56
source_inventory_digest
  c202cd042cc20ce2efedb55d7dada447c211050538ab5c67a67f4649bd30a620

profiles  = 14
contrasts = 322
pairs     = 91
failures  = 0
```

Alle 14 Rollen besitzen genau 40 Checkpoints. Die einzige nullable
Rezeptorlage bleibt je Profil `C_GAP/POST_COMPETITION` mit vier
`None`-Markern. Das Artefakt ist damit fuer diesen Audit vollstaendig und
technisch abgenommen.

## Paarstruktur

Die 15 als `PROFILE_EQUIVALENT` klassifizierten Paare bilden im gebundenen
Atlas eine vollstaendige Sechsergruppe:

```text
A1_FAST_SH
A2_B1_FIXED_ADAPTER
A2_B4_LINEAR_COUPLED
A2_B5_F3_FULL
A2_B6_CONST_V
M4_DTS1_T1
```

Jede dieser Rollen besitzt exakt fuenf aequivalente Nachbarn. Die restlichen
acht Rollen besitzen jeweils keinen aequivalenten Partner:

```text
A0_CURRENT_CONTACT
A2_B2_INTEGRATOR
A2_B3_LOCAL_LEAKY
A3_NORM
M1_PARALLEL_LEAK
M2_DELAY
M2_REPLAY
M5_DIRECT
```

Damit bestehen unter genau dieser Metrik neun beschreibende
Atlas-Komponenten: eine Sechsergruppe und acht Einzelprofile. Dies ist keine
allgemeine mechanistische Aequivalenzrelation ausserhalb des gebundenen
Versuchs.

## Abstand zur Entscheidungsgrenze

```text
groesstes aequivalentes D_rel
  0.02896203737648974
  A1_FAST_SH <> A2_B4_LINEAR_COUPLED

kleinstes verschiedenes D_rel
  0.06464451123986609
  A1_FAST_SH <> A2_B3_LOCAL_LEAKY

gebundene Grenze
  0.05
```

Im vorliegenden Atlas beruehrt kein Paar die Entscheidungsgrenze. Der Audit
veraendert daraus weder Grenze noch Messachse und leitet keine statistische
Sicherheit fuer andere Expositionen ab.

## Entscheidung zur Baselineabdeckung

Keine der 14 registrierten Rollen wird aus einem spaeteren fairen
Kandidatenvergleich entfernt. Die sechs Profile sind nur unter der
festgelegten 320-Komponenten-Achse dieser Exposition nah. Ihre technischen
Updateformen und Kontrollrollen bleiben verschieden.

Eine Reduktion auf einen Vertreter waere derzeit methodisch unzulaessig:

- sie wuerde eine Baselinepraezedenz nach dem Ergebnis einfuehren;
- sie koennte Unterschiede unter einer spaeteren Kandidatenexposition
  verdecken;
- sie wuerde die vorregistrierte Regel abschwaechen, nach der bereits die
  Reproduktion durch eine einzige faire Pflichtbaseline zur
  Kandidatenreduktion ausreicht.

Die Sechsergruppe darf fuer Berichte als atlasinterne Redundanzstruktur
genannt werden. Operativ bleiben jedoch alle 14 Profile erhalten.

## Geschlossene Zweige

`M4_DTS1_T1` bleibt technische Baseline. Seine Zugehoerigkeit zur
Sechsergruppe reaktiviert weder DTS-1/T1 noch G2/D3 als Kandidatenzweig.
Free/Blocked, Ressourcenledger, Validatoren und Adapter bleiben
Infrastruktur. Frozen-E1, G2/D3 und weitere abgeschlossene Kandidatenzweige
bleiben beendet.

## Aussagegrenze

Der Atlas zeigt ausschliesslich, welche vorhandenen Baselineprofile unter
einer fest gebundenen Exposition und Metrik nah oder verschieden sind. Er
zeigt keine Bildung, Abschwaechung, Interferenz, Kapazitaetsfreigabe oder
Wiederverwendung und bestaetigt keine hypothetische MCM-Memory.

## Abschluss und naechster Schritt

```text
S1_TH_STATIC_ATLAS_ACCEPTED
ONE_SIX_ROLE_EQUIVALENCE_GROUP_AND_EIGHT_SINGLETONS_BOUND
ALL_14_REGISTERED_BASELINES_RETAINED_FOR_FUTURE_FAIR_COMPARISON
NO_RUN_NO_PARAMETER_CHANGE_NO_CANDIDATE_DECISION
```

Der einzige naechste Schritt ist S1-TI als statischer
Kandidatenanschluss-Lueckenaudit. Er soll pruefen, welche formal gebundene
S1-PX-Lebenszyklusinformation einem spaeteren Kandidatenprofil noch fehlt,
damit es ohne Sonderpfad gegen alle 14 Atlasprofile gestellt werden kann.
S1-TI darf keinen Kandidaten waehlen, keine Gleichung oder Parameter binden,
keine Runtime implementieren und keinen Lauf ausfuehren.
