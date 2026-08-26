# S1-CE: E1 E4-Baseline-Bestandsaudit und Vergleichsvertrag

## Status

Statischer Bestandsaudit und Vorvertrag fuer den E4-Vergleich nach dem
gueltigen S1-CD-Befund. Die hier bestimmten Profil-, S2-B2- und CONST-V-
Handoffs sind spaeter in S1-CF implementiert und technisch abgenommen. Keine
Baselineentscheidung wurde erzeugt. Kein E4-, Memory-, Lern-, Organismus-,
Semantik- oder KI-Befund.

## Ausgangslage

S1-CD zeigt fuer E1 einen konstruierten technischen Lebenszyklus aus
Bindung, spaeterer Feldwirkung, Freigabe, konkurrierender Wiederbindung und
erneut veraenderter Feldwirkung. Zugleich ist jeder eingefrorene
E1-Probezustand exakt durch seinen festen Gain erklaert.

E4 fragt deshalb nicht, ob ein einzelner E1-Zustand wie eine feste
Kopplungskonfiguration wirkt. Das ist bereits bestaetigt. E4 fragt:

> Kann eine transparente engere Baseline den gesamten beobachtbaren
> Geschichte-Freigabe-Konkurrenz-Probe-Verlauf von E1 mit einem vorab
> festgelegten Parametervertrag erklaeren?

## Bestandsaudit

### Direkt anschliessbar

```text
P0 / Ablation
E1 Fixed Gain pro eingefrorenem Zustand
mcm_f3_runtime
mcm_f3_coupling
mcm_f3_baseline_coupling.local-leaky
mcm_f3_baseline_coupling.linear-coupled-field
```

P0, Ablation und Fixed Gain sind bereits auf derselben Drei-Knoten-Geometrie
technisch gebunden. Die F3-Runtime und ihre Kopplungsrechner arbeiten
grundsaetzlich auf dem vorhandenen Feld- und Kanteninventar, benoetigen aber
einen M-Zustand und einen E4-spezifischen Handoff.

### Vorhanden, aber nicht direkt anschliessbar

```text
W7-N LEAK
W7-N CONST-V
W7-BD CONST-V-Runtimeadapter
S2 B1/B2-Referenzfamilie
```

W7-N LEAK ist in seiner bestehenden Form ein observer-only lokaler Zustand
ohne Feldrueckwirkung. Er kann den kausalen E1-Probeeffekt nicht direkt
erklaeren und ist nur als Null-Rueckwirkungsbaseline zulaessig.

Der W7-BD-CONST-V-Adapter ist an W7-Matrix- und Trajektoriendigests sowie ein
anderes Anfangsfeld gebunden. Er darf nicht unveraendert als Drei-Knoten-
E1-Baseline ausgegeben werden. Der reine W7-N-CONST-V-Kopplungskern kann erst
nach einem neuen privaten Geometrie- und Zustandsadapter verwendet werden;
seine eingefrorenen Gleichungsparameter bleiben dabei unveraendert.

S2 B1/B2 besitzt eine lineare lokale Entwicklungsvariable. B2 ist die
engste vorhandene kausal rueckwirkende Integratorfamilie. Sie verwendet
jedoch einen Knoten- statt Kantenzustand und eine eigene Referenzruntime. Ein
privater E4-Handoff ist vor einem fairen Vergleich erforderlich.

### Nicht als neue Baseline zu erfinden

Ein ungebundener "Integrator" mit nach Ergebnis gewaehltem Reader, Gain oder
Zeitparameter ist unzulaessig. E4 darf keine neue Gleichung nur deshalb
konstruieren, um E1 nachtraeglich besser oder schlechter zu erklaeren.

## Verbindliches Baseline-Inventar

Der erste E4-Korridor enthaelt genau:

```text
B0  P0 / keine langsame Zustandsrueckwirkung
B1  ein einziger statischer E1-HOLD-Gain ueber alle Phasen
B2  S2 B2 lineare gekoppelte Integratorfamilie
B3  F3 local-leaky mit festem direktem Reader
B4  F3 linear-coupled-field
B5  F3 candidate
B6  W7-N CONST-V mit neuem reinem Drei-Knoten-Handoff
E1  unveraenderter E1-Referenzkandidat
```

Der pro Checkpoint neu aus dem Kandidaten abgeleitete Fixed Gain ist keine
eigenstaendige dynamische Baseline. Er bleibt als Oracle-Obergrenze
erhalten:

```text
ORACLE-G  je Checkpoint exakt passender eingefrorener Gain
```

ORACLE-G muss E1 an jedem einzelnen Probecheckpoint exakt reproduzieren,
kann aber keine autonome Zustandsentwicklung erklaeren. Er wird deshalb
nicht in die E4-Erklaerungsentscheidung aufgenommen.

## Keine Parameteranpassung

Alle Baselines verwenden ausschliesslich ihre bereits dokumentierten
Parameterbindungen:

```text
S/H response_time_seconds      = 1.0
H time_constant_seconds        = 0.5
E1-Vertrag                     = unveraendert aus S1-CD
S2-B2-Vertrag                  = unveraendert aus s2_reference_baselines
F3-Vertraege                   = unveraendert aus mcm_substrate_state
CONST-V-Parameter              = unveraendert aus W7-M/W7-N
```

Es gibt keinen Fit gegen S1-CD-Werte. Ein Adapter darf Identitaet, Geometrie,
Zeit und Datenform uebersetzen, aber keine Gleichung und keinen Parameter
veraendern.

## Gemeinsame Weltfolge

Jedes dynamische Modell erhaelt dieselbe wertidentische Folge:

```text
Phase H:  8 linke Kontakte, je 1.0 s
Phase G:  uniforme Nullkontaktentwicklung bis 1 s, 4 s und 8 s
Phase C:  8 rechte Kontakte, je 1.0 s, beginnend am Zustand G4
```

Die E1-Rueckwirkung bleibt waehrend Phase H wie in S1-BX aktiv. Fuer den
isolierten Konkurrenzvergleich ab G4 bleibt sie waehrend Phase C wie in
S1-CB aus. Jede Baseline muss dieselbe Interventionslogik abbilden:
Zustandsentwicklung bleibt aktiv, Rueckwirkung auf S/H ist in Phase C
abgeschaltet. Kann ein Modell diese Trennung nicht ausdruecken, ist es fuer
diesen Korridor technisch inkompatibel und der Gesamtlauf darf nicht als
vollstaendig gewertet werden.

## Gemeinsame Probecheckpoints

An folgenden unveraenderlichen Zustaenden wird jeweils eine eingefrorene
identische S1-CC-Probe auf einer frischen Kopie von `F*` ausgefuehrt:

```text
H8
G1
G4
G8
C1
C2
C3
C4
C5
C6
C7
C8
```

Die dynamischen Historienfelder werden nicht als Probeanfang verwendet. Nur
der jeweilige langsame Zustand wird geometriegleich auf das frische
Probefeld uebertragen. P0, Ablation, Fixed Reader und n=2/n=4 bleiben
Pflichtkontrollen.

## Vergleichsebene

E1 besitzt Kantenbindungen, F3/CONST-V einen Knotenzustand und S2-B2 eine
lokale Entwicklungsvariable. Diese internen Werte sind nicht
dimensionsgleich und werden nicht direkt voneinander subtrahiert.

Verglichen wird ausschliesslich der beobachtbare Probeeffekt:

```text
Delta_S(checkpoint) = S_active - S_P0
Delta_H(checkpoint) = H_active - H_P0
```

Die kanonische Profilreihenfolge ist:

```text
12 Checkpoints
* 3 Knoten
* S danach H
= 72 vorzeichenbehaftete Komponenten
```

Vorzeichen, Knotenordnung und Checkpointordnung bleiben erhalten. Es werden
nicht nur Betraege oder Endpunkte verglichen.

## Rohmetriken pro Baseline

```text
profile_linf_residual
profile_l1_residual
candidate_profile_linf
relative_profile_linf_residual
release_segment_linf_residual
competition_segment_linf_residual
maximum_mass_or_budget_error
minimum_internal_resource
refinement_linf
observation_schedule_matches
ablation_controls_hold
fixed_reader_controls_hold
invariants_hold
```

Wenn eine Baseline keinen erhaltenen Ressourcenbegriff besitzt, werden
`maximum_mass_or_budget_error` und `minimum_internal_resource` nur gegen
ihren eigenen vorbestehenden Zustandsvertrag geprueft und nicht mit E1
gleichgesetzt.

## Vorregistrierte Grenze

Der bestehende enge F3-Baselinewert wird unveraendert uebernommen:

```text
relative_profile_linf_limit = 0.05
absolute_control_tolerance  = 1e-12
relative_control_tolerance  = 0
```

Eine Baseline erklaert den E1-Lebenszyklus nur, wenn:

1. Zeitplan, Geometrie und Probeinventar exakt uebereinstimmen;
2. alle eigenen Invarianten bestehen;
3. Ablation und fester Reader kontrolliert bestehen;
4. E1 und Baseline an allen 72 Profilkomponenten einen messbaren Effekt
   besitzen, wo die Entscheidung ihn benoetigt;
5. `relative_profile_linf_residual <= 0.05` gilt;
6. Release- und Konkurrenzsegment nicht durch fehlende Ausgabe oder einen
   Reset uebersprungen werden.

## Entscheidungsreihenfolge

```text
INVALID_E4_RUN
TECHNICALLY_INCOMPATIBLE_BASELINE_SET
E4_EXPLAINED_BY_NARROW_BASELINE
E4_RESIDUAL_AFTER_REGISTERED_BASELINES
```

`E4_EXPLAINED_BY_NARROW_BASELINE` gilt, sobald mindestens eine der Baselines
B1 bis B6 alle Kontrollen besteht und das 72-Komponenten-Profil innerhalb
`0.05` erklaert.

`E4_RESIDUAL_AFTER_REGISTERED_BASELINES` gilt nur, wenn alle Baselines
technisch lauffaehig und gueltig sind, aber keine die Grenze erreicht.

Ein Residualbefund waere kein Memorynachweis. Er wuerde nur zeigen, dass die
registrierten engen Baselines den technischen E1-Lebenszyklus in diesem
Korridor nicht hinreichend reproduzieren.

## Implementierungsgrenze

Vor einem E4-Lauf fehlen genau drei private Adapter:

```text
1. gemeinsamer 12-Checkpoint-Profilcontainer
2. S2-B2-Handoff auf dieselbe Drei-Knoten-Welt- und Probezeit
3. W7-N-CONST-V-Handoff ohne W7-Matrixfeld, aber mit unveraendertem Spec
```

F3, local-leaky und linear-coupled duerfen ueber die vorhandene generische
F3-Runtime angeschlossen werden. Es ist nicht zulaessig, alte W7- oder
F3-Ergebnisdateien mit den neuen E1-Werten nachtraeglich zu kreuzen.

## Aussagegrenze

E4 vergleicht konstruierte technische Dynamiken. Kein Ergebnis begruendet
MCM-Memory, organisches Vergessen, Rekonstruktion, Bedeutung,
Selbstwahrnehmung oder feldbasierte KI. Ein spaeterer Memorytest benoetigt
zusaetzlich mindestens Teilhinweis-Rekonstruktion und Kapazitaetskonkurrenz
ohne vorprogrammierte Musteridentitaet.

## Bester naechster Schritt

S1-CF implementiert und testet den privaten 12-Checkpoint-Profilcontainer
sowie die S2-B2- und CONST-V-Handoffs. S1-CG bindet als naechsten Schritt den
vollstaendigen E4-Ausfuehrungs- und Ergebnisvertrag. Noch kein E4-Gesamtlauf
und keine Baselineentscheidung.
