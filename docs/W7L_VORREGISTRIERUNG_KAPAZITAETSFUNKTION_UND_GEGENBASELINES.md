# W7-L: Vorregistrierung von Kapazitaetsfunktion und Gegenbaselines

Stand: 2026-08-09

Entscheidung: `CAPACITY_FUNCTION_BASELINE_MATRIX_PREREGISTERED`

Arbeitsart: statischer Funktions-, Kausal- und Gegenbaselinevertrag

Implementierung oder Forschungslauf: nein

## Ausgangspunkt

W7-K stellt eine technisch kontrollierte opt-in Runtime fuer den in W7-F
definierten kapazitaetsbegrenzten Kantenaustausch bereit. Nachgewiesen sind
nur Integration, Massenbilanz, lokale Kapazitaetsinvarianz und gebundene
Fortsetzung.

Lauf 194 bleibt die wichtigste Negativreferenz: Im unveraenderten K2/F3-Pfad
sank die alte A-Wirkung unter B und unter gleich langer Unterbrechung fast
identisch. Gleichzeitig entstand eine neue B-Wirkung. Das war passive
Verlust- und Wiederverwendungsfaehigkeit, aber keine konkurrierende
funktionale Loesung und kein Nachweis freigesetzter Kapazitaet.

W7-L bindet deshalb vor jeder neuen Ausfuehrung, welche zusaetzliche Wirkung
der W7-K-Pfad zeigen muesste und wie sie von passiver Relaxation, konstanter
Ratenskalierung, lokaler Saettigung und externer Normalisierung getrennt wird.

## Forschungsfrage

Fuehrt die zustandsabhaengige freie Zielkapazitaet unter demselben lokalen
Regelwerk dazu, dass konkurrierende B-Feldgeschichte eine zuvor durch A
veraenderte lokale M-Verteilung staerker als eine gleich lange passive
Unterbrechung loest, die dabei frei werdende bilanzierte Kapazitaet in einem
anderen vorab bestimmten Feldbereich erneut beansprucht wird und der neue
M-Zustand eine spaetere identische S/H-Probe kausal veraendert?

Ein positiver Ausgang waere weiterhin nur ein Funktionsbefund fuer die offen
konstruierte Engineeringgleichung. Er waere kein Memory-, Feldzeit-,
Organisations- oder KI-Nachweis.

## Unveraenderte kontrollierte Quellen

W7-L verwendet ausschliesslich den bestehenden In-Memory-Quellenvertrag:

```text
mcm_field_organism/mcm_f3_k2b_source.py
build_mcm_f3_k2b_source()
```

Damit bleiben unveraendert:

- A: vier Sekunden wiederholte kontrollierte Audio-/Videowelt;
- B: vier einzelne kontrollierte Audio-/Videoschritte;
- G: vier gleich lange Unterbrechungsschritte;
- P: dieselbe einsekundige technische Probe an Checkpoint 0 bis 4;
- alle bereits hart gebundenen Rezeptorsequenzdigests;
- gemeinsamer Organismustakt mit `1_000_000` Ticks pro Sekunde.

Es gibt keinen Browser, keine Kamera, kein Mikrofon, keine reale Sensorik und
keine neue Medienquelle. Phasenkennungen und Wiederholungszahlen duerfen nur
den Versuchsadapter ordnen; die Runtime erhaelt sie nicht als Zustand.

## Kandidatenparameter ohne Ergebnisanpassung

Fuer N vorhandene Feldorte und `M_total = 1` gilt:

```text
lambda_sm = 1.0
kappa = 0.5
eta = 1.0
C_site = 2 * M_total / N
V_initial = 1 - (M_total / N) / C_site = 0.5
response_time_seconds = 1.0
afterimage_time_constant_seconds = 0.5
dissipation = keine
refinement = n, 2n, 4n mit n = 1
```

`C_site` wird aus dem homogenen Ausgangszustand abgeleitet und nicht an ein
Ergebnis angepasst. Jeder Ort startet bei halber Kapazitaet. Der Wert bleibt
in allen Phasen, Quellen, Tauscharmen und Fortsetzungen identisch.

## Vorab bestimmte Beobachtungsbereiche

Die Regionsrollen werden ausschliesslich aus den eingefrorenen reduzierten
Quellen vor jedem Modelllauf bestimmt. Fuer jeden angedockten Feldort i sind
`E_A,i` und `E_B,i` die zeitintegrierten absoluten Rezeptorkontakte der A-
beziehungsweise B-Quelle bei identischem Zeitbudget.

```text
R_A = {i | E_A,i > E_B,i}
R_B = {i | E_B,i > E_A,i}
R_0 = {i | E_A,i = E_B,i}
```

Die drei Mengen muessen disjunkt und vollstaendig sein; `R_A` und `R_B`
muessen beide nichtleer sein. Es gibt keine Schwelle und keine Auswahl aus
Kandidatenresultaten. Die Mengen sind reine Observerrollen und werden weder
an Feld noch Substrat zurueckgegeben.

Gemessen werden fuer jede Region die M-Summe und die freie Kapazitaet:

```text
M_R = Summe_{i in R} M_i
F_R = |R| * C_site - M_R
```

## Segmentierungskontrolle

Dieselbe A-Rezeptorsequenz wird technisch auf zwei Weisen uebergeben:

- `A-COMB`: ein zusammenhaengendes Viersekundenintervall;
- `A-SEG`: vier aufeinanderfolgende Einsekundenintervalle.

Weltwerte, Ereignisse und Gesamtdauer sind identisch. Der Vergleich prueft
nur, dass keine Episoden- oder Phasenzaehlung wirkt. Abweichungen duerfen
hoechstens den vorab berechneten numerischen Verfeinerungsboden erreichen.
Dieser Kontrollarm ist kein Beleg organischer Wiederholungspraegung.

## Kausale Hauptpfade

`U` bezeichnet das homogene M-Ausgangsfeld. Nach A wird S/H auf Kopien exakt
angeglichen; M bleibt unveraendert. Danach laufen alle Hauptpfade ohne Reset,
Loeschsignal oder Parameterwechsel:

```text
AB_k: A x4 -> B x0..4
AG_k: A x4 -> G x0..4
UB_k: U    -> B x0..4
UG_k: U    -> G x0..4

BA_k: B x4 -> A x0..4
BG_k: B x4 -> G x0..4
UA_k: U    -> A x0..4
UG_k: U    -> G x0..4
```

Der BA-Tausch ist eine Richtungs- und Quellenkontrolle. Er darf keine eigene
Gleichung oder angepasste Kapazitaet erhalten.

An jedem Checkpoint wird nur auf einer Feldkopie S/H erneut angeglichen und
die gebundene Probe P ausgefuehrt. Der weiterlaufende Hauptpfad wird durch die
Probe nicht veraendert.

## Direkte Kausalinterventionen

Fuer jeden Modellarm werden am finalen Checkpoint zusaetzliche Feldkopien
gebildet:

1. `M-NEUTRAL`: M wird extern auf den homogenen U-Zustand gesetzt, S/H und
   die folgende Probe bleiben identisch.
2. `M-TRANSPLANT`: Der vollstaendige lokale M-Vektor wird zwischen zwei
   S/H-angeglichenen Geschichtearmen transplantiert. Gesamtmasse,
   Neuronenordnung und Kapazitaetsgrenze muessen erhalten bleiben.
3. `ETA0`: Dieselbe M-Dynamik laeuft mit `eta = 0`; M darf sich veraendern,
   aber nicht auf S zurueckwirken.
4. `KAPPA0`: Dieselbe Kapazitaet laeuft ohne S-gerichteten Transportanteil.
5. `SIGN`: Das Vorzeichen von kappa wird fuer den gesamten Arm invertiert.

Eine Probe-Wirkung gilt nur als M-kausal, wenn Neutralisierung sie bis zum
numerischen Boden entfernt und Transplantation sie mit dem transplantierten
M-Vektor uebertraegt. `ETA0` muss die M-nach-S-Wirkung entfernen. Observer
duerfen diese Interventionen nicht als Runtimeursache verwenden.

## Pflichtbaselines

Alle Baselines erhalten dieselben Quellen, Feldgeometrie, Beobachtungszeiten,
S/H-Angleichungen, Praezision und hoechstens ein persistentes skalares
Substratbudget je Feldort.

| Kennung | Gebundene Rolle |
| --- | --- |
| P0 | schneller MCM-Pfad ohne aktiven Substrataustausch |
| LEAK | einseitige lineare Leaky-Spur ohne Rueckwirkung |
| LIN | lineare reziproke Spur aus W7-B/Lauf 192 |
| F3 | unveraenderter quellenbegrenzter K2/F3-Transport aus Lauf 194 |
| CONST-V | unveraendertes F3 mit `lambda_sm = 0.5`, exakt gleiche Anfangsraten wie CAP |
| SAT | unabhaengiger begrenzter lokaler Integrator ohne Ressourcenfluss |
| MOB | zustandsabhaengige lokale Mobilitaet oder Gain ohne Zielkapazitaetsledger |
| NORM | externe globale Normalisierung nur als unzulaessige Gegenkontrolle |
| ETA0 | CAP ohne M-nach-S-Rueckwirkung |
| KAPPA0 | CAP ohne gerichteten S-Anteil |
| SIGN | CAP mit global invertiertem kappa |

`CONST-V` ist der primaere enge Vergleich. Bei homogenem M ist seine
Kantenrate exakt gleich der Kandidatenrate, weil `V_initial = 0.5`. Erst eine
veraenderte lokale Belegung kann beide Pfade trennen.

SAT, MOB und NORM duerfen nicht nach Ergebnis fitten. W7-M muss ihre
Gleichungen und Parameter analytisch am homogenen Anfangszustand angleichen
und vor jeder Kandidatenauswertung einfrieren. NORM bleibt eine externe
Erklaerungsbaseline und darf niemals Organismusfunktion werden.

## Messrollen

Pro Checkpoint und Modell werden mindestens erfasst:

- S/H-Linf und Trajektorien-L2 der identischen Probe;
- vollstaendiger M-Vektor nur im Arbeitsspeicher;
- `M_R` und `F_R` fuer `R_A`, `R_B` und `R_0`;
- alte A-Probewirkung unter B und unter G;
- neue B-Probewirkung nach U und nach A;
- Massenfehler, kleinstes M, groesstes M und kleinste freie Kapazitaet;
- n/2n/4n-Abweichung jeder entscheidenden S/H- und M-Rolle;
- Abweichung von CONST-V und allen weiteren Pflichtbaselines;
- Neutralisierungs-, Transplantations-, ETA0-, KAPPA0- und SIGN-Wirkung.

Bilanzierte Freisetzung und Beanspruchung werden nicht aus S abgeleitet:

```text
release_A(k) = M_RA(AG_k) - M_RA(AB_k)
claim_B(k)   = M_RB(AB_k) - M_RB(AG_k)
residual_0(k)= M_R0(AB_k) - M_R0(AG_k)

release_A(k) = claim_B(k) + residual_0(k)
```

Die Gleichung folgt aus identischer Gesamtmasse der verglichenen Pfade. Eine
positive `claim_B` allein genuegt nicht; sie muss mit positiver Freisetzung,
Probe-Kausalitaet und dem Gegenvergleich zur Unterbrechung zusammenfallen.

## Numerische und funktionale Schwellen

Der numerische Boden wird vor der Hauptentscheidung aus dem groessten
entscheidenden 2n/4n-Abstand bestimmt:

```text
epsilon_num = max aller gebundenen 2n/4n-Linf-Abstaende
effect_floor = 10 * epsilon_num
mass_abs_tolerance = 1e-12
baseline_explanation_limit = 0.05
functional_loss_limit = 0.05
competitive_advantage_factor = 0.50
```

Die letzten beiden Funktionsschwellen werden unveraendert aus Lauf 194
uebernommen. Keine Schwelle darf nach Sichtung eines W7-Ergebnisses geaendert
werden.

## Entscheidungsordnung

Die spaetere einmalige Auswertung muss genau eine Entscheidung liefern:

1. `TECHNICALLY_UNDECIDABLE`, wenn Quellen, Regionen, Fortsetzungsbindungen,
   Segmentierungskontrolle, Invarianten oder Verfeinerung scheitern.
2. `NO_CAPACITY_SPECIFIC_EFFECT`, wenn CAP und CONST-V innerhalb von
   `effect_floor` und der 5-Prozent-Erklaerungsgrenze bleiben.
3. `CAPACITY_TRANSPORT_EFFECT_ONLY`, wenn CAP von CONST-V abweicht, aber
   keine konkurrierende bilanzierte Freisetzung und M-kausale Probe-Wirkung
   gemeinsam zeigt.
4. `COMPETITIVE_RELEASE_WITHOUT_REUSE`, wenn B alte A-Wirkung und regionale
   A-Belegung spezifisch gegen G loest, aber keine bilanzierte Beanspruchung
   in `R_B` mit kausaler neuer Probe-Wirkung entsteht.
5. `FUNCTIONAL_RELEASE_AND_REUSE_CANDIDATE`, nur wenn gemeinsam gilt:
   alte A-Retention unter B hoechstens 0.05 und hoechstens halb so gross wie
   unter G; `release_A` und `claim_B` liegen ueber `effect_floor`; die
   Regionsbilanz schliesst; M-Neutralisierung entfernt und M-Transplantation
   uebertraegt die Probe-Wirkung; ETA0 entfernt nur die Rueckwirkung; der
   Effekt bleibt jenseits aller eingefrorenen Pflichtbaselines; der BA-Tausch
   traegt dieselbe Mechanik ohne bevorzugte Quellenrichtung.

Auch Entscheidung 5 ist nur ein Kandidatenbefund. Die Bezeichnung Memory
bleibt gesperrt, bis weitere unabhaengige Weltkontakte, Gegenbaselines und
Rekonstruktionspruefungen bestehen.

## Harte Stopplinien

Der Lauf wird nicht ausgefuehrt oder als Befund gewertet, wenn:

- ein Quellen-, Parameter-, Regions- oder Konfigurationsdigest offen ist;
- eine Region aus Kandidatenresultaten statt aus Quellen bestimmt wird;
- `C_site`, lambda, kappa oder eta nach einem Ergebnis angepasst werden;
- M geclippt, global normalisiert oder zwischen Schritten korrigiert wird;
- die externe Fortsetzungsbindung fehlt oder wechselt;
- Probe oder Observer den Hauptpfad veraendern;
- S/H-Verlust als Kapazitaetsfreisetzung ausgegeben wird;
- ein positiver Flieskommawert unterhalb `effect_floor` interpretiert wird;
- ein Baselinegleichstand sprachlich als Emergenz oder Memory umbenannt wird.

## Verwendete Projektquellen

- [W7-C Funktions- und Ressourcenvertrag](W7C_FUNKTIONS_UND_RESSOURCENVERTRAG_JENSEITS_LINEARER_SPUR.md)
- [W7-E Engineeringentscheid](W7E_ENGINEERINGENTSCHEID_ZIELSEITIGE_FREIE_KAPAZITAET.md)
- [W7-F mathematischer Minimalvertrag](W7F_MATHEMATISCHER_MINIMALVERTRAG_KAPAZITAETSBEGRENZTER_KANTENAUSTAUSCH.md)
- [W7-K Runtimeimplementierung](W7K_IMPLEMENTIERUNG_KAPAZITAETSBEGRENZTER_SHAREDMCMFIELD_ADAPTER.md)
- [K2-B/F3-Vorregistrierung](K2_B_F3_FUNKTIONSVERLUST_UND_WIEDERVERWENDUNG_VORREGISTRIERUNG.md)
- [Lauf 194](forschung/LAUF_194_K2_B_F3_FUNKTIONSVERLUST_UND_WIEDERVERWENDUNG.md)
- [Operationale C2-Baselineklassen](architektur/045_OPERATIONALE_C2_BASELINEKLASSEN.md)

## Naechster Schritt

W7-M darf ausschliesslich den In-Memory-Quellen-, Regions-, Interventions-
und Baseline-Matrixadapter implementieren und mit synthetischen technischen
Vertragstests pruefen. Es darf noch keine Hauptmatrix auswerten, keinen
Browser starten und keinen Report schreiben.
