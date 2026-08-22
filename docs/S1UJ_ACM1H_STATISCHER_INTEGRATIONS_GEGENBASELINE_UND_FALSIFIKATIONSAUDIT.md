# S1-UJ: ACM-1H statischer Integrations-, Gegenbaseline- und Falsifikationsaudit

## Auftrag und Grenze

S1-UJ legt nach der privaten S1-UI-Integration fest, welcher kleinste faire
synthetische Vergleich die vermittelte ACM-1H-Feldwirkung pruefen koennte.
Der Audit verwendet ausschliesslich bereits gebundene Gleichungen,
Parameterkandidaten, G/O-Geschichten, Feldprimitive und Baselines.

S1-UJ erzeugt keine neue Gleichung, keinen Parameter, keinen Code, keinen
Test und keinen Feldlauf. Es wird keine Ergebnisentscheidung getroffen.

## Praezisierte Entwicklungsfrage

ACM-1H wird nicht als vorhandene Memory-Faehigkeit behandelt. Geprueft
werden soll zunaechst nur:

> Kann ein kontrolliert erzeugter relationaler Kantenmotivzustand bei einem
> identischen spaeteren Feldvorzustand eine eigene, baselinekontrollierte
> Feldfortsetzung vermitteln?

Eine positive Antwort waere ein technischer Zwischenschritt bei der
Bewertung, ob ACM-1H als Baustein der hypothetischen MCM-Memory-
Entwicklungsrichtung geeignet sein koennte. Sie waere weder eine
ausgearbeitete MCM-Memory-Funktion noch ein Nachweis einer solchen Funktion.

## Vorhandene technische Grundlage

Bereits geschlossen sind:

- die offene Linie `node-a -- node-b -- node-c -- node-d`;
- das linke Motiv aus `e_ab` und `e_bc`;
- die G/O-Paarung mit gleichen Einzelkantenmarginalen und verschiedener
  gemeinsamer Paritaet;
- sechs feste ACM-1H-Parameterkandidaten;
- der reine G/O-Zustandsmatch gegen IAG-2;
- der private atomare Feld-/ACM-Carry;
- der bitgenaue ACM-OFF-Bypass;
- die Abgrenzung gegen den vorhandenen vorzeichenblinden E1-Kantengain;
- die akzeptierte Darstellbarkeit durch eine breitere gekoppelte
  Gainbaseline.

Der neue Audit aendert keinen dieser Vertraege.

## Warum ein ununterbrochener G/O-Feldpfad noch nicht fair ist

In einem aktiven ACM-1H-Pfad wirkt `z_pre` bereits waehrend der weiteren
Geschichtsbildung auf die Kantenraten. Nach dem ersten G/O-Intervall koennen
deshalb die anschliessenden Feldzustaende und Primaerfluesse auseinander
laufen. Dann waere bei einer spaeteren Probe nicht mehr eindeutig, ob ein
Unterschied vom relationalen Zustand oder vom bereits verschiedenen
aktuellen Feldvorzustand stammt.

Ein endliches gemeinsames Ruheintervall loest dieses Problem nicht exakt:
Der passive Feldkern kann Unterschiede abschwaechen, muss sie aber in
endlicher Zeit nicht bitgenau beseitigen. Eine nachtraegliche ungepruefte
Angleichung waere ebenfalls unzulaessig.

Die erste Integrationsmatrix darf daher noch keine ununterbrochene
Geschichte-zu-Probe-Kette behaupten. Sie muss die Zustandsbildung und den
gemeinsamen Feldreadout als zwei kontrollierte Stufen trennen.

## Stufe A: vorhandene Zustandsbildung

Stufe A verwendet die bereits in S1-UE und S1-UG gebundene reine G/O-
Konstruktion auf dem linken Motiv:

```text
G: (+Q,+Q) gefolgt von (-Q,-Q)
O: (+Q,-Q) gefolgt von (-Q,+Q)
```

Die bestehende synthetische Fixture realisiert `Q = 0.5` durch die bereits
verwendeten vier Knotenzustaende. `e_cd` bleibt dabei inaktiv. Es wird kein
neuer Expositionswert eingefuehrt.

Aus demselben Nullzustand entstehen fuer jede der sechs registrierten
Konfigurationen:

- `z_G` und `z_O` mit entgegengesetztem Vorzeichen und gleichem Betrag;
- ein neutraler Vergleichszustand `z_0`;
- wertidentische enge IAG-2-Einzelkantenzustaende;
- wertidentische E1-Einzelkantenbindings, weil die quadrierten
  Einzelkantendifferenzen in jedem zugeordneten Intervall gleich sind.

Die ACM- und IAG-2-Rollen von Stufe A sind durch den reinen Kern bereits
technisch abgedeckt. Die E1-Gleichheit ist in S1-UH statisch hergeleitet,
aber noch nicht auf dieser Fixture materialisiert. Sie bleibt deshalb eine
Pflichtvorbedingung der spaeteren Matrix. In S1-UJ wird keine dieser Rollen
ausgefuehrt; Stufe A ist noch kein integrierter Feldvergleich.

## Stufe B: identischer gemeinsamer Feldvorzustand

Alle integrierten Vergleichspfade muessen denselben synthetischen
Vier-Knoten-Feldvorzustand `F_PROBE` erhalten. Er verwendet die bereits in
der G/O-Fixture vorhandene positive linke Motivlage:

```text
S = (1.0, 0.5, 0.0, 0.0)
H = (0.0, 0.0, 0.0, 0.0)
```

Gebunden bleiben ausserdem:

- dieselbe Feld-, Layer-, Geometrie-, Dock- und Knotenidentitaet;
- derselbe Feldtick und Zeitendpunkt;
- dieselbe Nullkontaktverteilung im Probeintervall;
- dieselbe S/H-, Rezeptor- und Dissipationskonfiguration;
- derselbe Schrittzeitvertrag;
- keine A/B/C/D-Versuchsrolle im Feld oder Modellkern.

`F_PROBE` ist eine synthetische Zustandsintervention. Es wird nicht
behauptet, dass die beiden vorausgehenden G/O-Feldpfade diesen Zustand
selbststaendig und bitgenau erreicht haben.

## Vergleichsrollen

### ACM-1H

Je Parameterkonfiguration werden drei private Carries auf dasselbe
`F_PROBE` gebunden:

- `ACM_G` mit dem aus Stufe A stammenden `z_G`;
- `ACM_O` mit dem aus Stufe A stammenden `z_O`;
- `ACM_Z0` mit neutralem `z_0`.

Alle drei erhalten dieselbe spaetere Probe. Nur der private Motivzustand
darf verschieden sein.

### ACM-OFF

`ACM_OFF` erhaelt `F_PROBE` ohne privaten Zustand und muss direkt den
neutralen S/H-Pfad reproduzieren. Dieser Pfad ist parameterunabhaengig und
muss deshalb nicht sechsmal neu berechnet werden.

### Vorhandener E1-Kantengain

`E1_G` und `E1_O` erhalten dieselben G/O-Geschichten auf der vorhandenen
E1-Zustandsoberflaeche. Vor der Probe muessen alle drei E1-Bindings
wertidentisch sein. Beide E1-Pfade werden danach auf dasselbe `F_PROBE`
gebunden und erhalten dieselbe Probe.

Falls bereits die E1-Vorzustaende abweichen, ist der Vergleich ungueltig und
wird nicht durch eine nachtraegliche Bindingsetzung repariert.

### Gekoppelte Reduktionsbaseline CGR-1

`CGR-1` ist keine neue Kandidatenmechanik. Sie ist die ausdrueckliche
Darstellbarkeitskontrolle fuer einen allgemeinen gekoppelten Motivgain mit
denselben zwei signed Motivkoordinaten, demselben Vorzustandsreadout und
demselben symmetrischen Kantenfaktor wie ACM-1H.

`CGR_G` und `CGR_O` muessen fuer jede der sechs Konfigurationen die
vollstaendige ACM-Ausgabe reproduzieren. Diese erwartete Gleichheit
bestaetigt nur die bereits akzeptierte Engineeringreduktion. CGR-1 darf
nicht als unabhaengiger Kandidat oder als neue Feldmechanik interpretiert
werden.

## Kleinste Matrix

Die Matrix besitzt keine Repliken und keine Parametersuche. Deterministische
Kontrollausgaben duerfen wiederverwendet werden.

| Rollenblock | Pfade je Konfiguration | Konfigurationen | Gesamt |
|---|---:|---:|---:|
| ACM-1H: `G`, `O`, `Z0` | 3 | 6 | 18 |
| CGR-1: `G`, `O` | 2 | 6 | 12 |
| ACM-OFF | wiederverwendbar | 1 | 1 |
| E1: `G`, `O` | parameterunabhaengig | 1 | 2 |
| **Gesamt** |  |  | **33** |

IAG-2 wird nicht als weiterer integrierter Pfad dupliziert. Sein exakter
G/O-Zustandsmatch ist bereits algebraisch und im reinen Referenzkern
geschlossen. E1 ist fuer diese Matrix die staerkere vorhandene konkrete
Einzelkantenbaseline.

## Pflichtoutputs

Jeder integrierte Pfad muss vor einer Comparatorentscheidung getrennt
ausgeben:

- vollstaendigen Eingangs-Felddigest;
- privaten Eingangszustandsdigest oder explizite Zustandslosmarkierung;
- drei angewandte Kantenraten;
- vier Aktivierungswerte des Feldfolgezustands;
- vier Nachhallwerte des Feldfolgezustands;
- beide `z_next` nur fuer aktive ACM-/CGR-Pfade;
- vollstaendigen Ausgangs-Felddigest;
- Folgecarry- oder ACM-OFF-Rolle;
- Konfigurations-, Geometrie-, Kanteninventar- und Zeitbindungen.

Ein Digestunterschied ohne einen benannten numerischen Unterschied in
Kantenrate, Aktivierung oder Nachhall ist kein technischer Kontrast.

## Vorab gebundene Vergleiche

### C0: Nullintegration

`ACM_Z0` muss fuer dieselbe Konfiguration wertgleich zu `ACM_OFF` sein.
Andernfalls ist die private Integration nicht neutral am gebundenen
Nullzustand.

### C1: G/O-Feldkontrast

`ACM_G` und `ACM_O` muessen von demselben `F_PROBE` aus unterschiedliche
gemeinsame Motivkantenraten und unterschiedliche numerische
Feldfolgezustaende erzeugen. Die Richtung muss der bereits gebundenen
Verstaerkungs-/Abschwaechungsprognose entsprechen.

### C2: Zustandsvermittlung

Der G/O-Kontrast muss mit dem transplantierten privaten Zustand und nicht
mit Pfadname, Iterationsreihenfolge, Feldpayload oder Rezeptoreingabe
wechseln. `z_G`/`z_O`-Tausch vertauscht daher die zugeordneten Ausgaben;
`z_0` entfernt den Kontrast.

Der Tausch ist eine Comparatorintervention und kein zusaetzlicher
Matrixpfad, weil dieselben 18 ACM-Ausgaben nur anders zugeordnet werden.

### C3: E1-Gegenbaseline

`E1_G` und `E1_O` muessen identische Bindings, Kantenraten und
Feldfolgezustaende liefern. Eine E1-Differenz widerlegt nicht ACM-1H,
sondern die Fairness des angenommenen matched Vergleichs.

### C4: Reduktionskontrolle

`CGR_G` muss `ACM_G` und `CGR_O` muss `ACM_O` fuer alle Pflichtoutputs
reproduzieren. Eine Abweichung kennzeichnet einen fehlerhaften
Baselineadapter oder einen unvollstaendigen Reduktionsvertrag.

### C5: Konfigurationsvollstaendigkeit

Alle sechs vorregistrierten ACM-Konfigurationen muessen ausgewertet werden.
Es gibt keine Auswahl nach Ergebnis und keine gemeinsame
Bestkonfiguration. Die Kontrollpfade duerfen jedoch aufgrund ihrer
Parameterunabhaengigkeit unveraendert wiederverwendet werden.

## Falsifikations- und Stoppregeln

Die integrierte ACM-1H-Richtung wird als praktischer Engineeringpfad
gestoppt oder auf die passende Baseline reduziert, wenn:

- `ACM_Z0` und ACM-OFF nicht wertgleich sind;
- `ACM_G` und `ACM_O` bei identischem `F_PROBE` keinen benannten
  numerischen Feldkontrast erzeugen;
- der Kontrast nicht mit `z_G`/`z_O` getauscht und mit `z_0` entfernt wird;
- E1 bereits vor der Probe verschiedene Bindings traegt;
- E1 trotz identischem Zustand und identischer Probe unterschiedliche
  Fortsetzungen erzeugt;
- CGR-1 die ACM-Ausgaben nicht reproduziert;
- ein Pfad eine andere Geometrie, Probe, Zeit oder S/H-Konfiguration nutzt;
- ein Fehler durch Clipping, Reset, Nachnormalisierung, Fallback oder
  Teilcommit verborgen wird;
- nur Digests, aber keine technischen Feldwerte verschieden sind;
- eine Konfiguration ausgelassen oder nach Ergebnis bevorzugt wird.

Eine erwartete Gleichheit von ACM-1H und CGR-1 ist kein negativer Befund.
Sie bestaetigt die bereits akzeptierte Reduzierbarkeit des Moduls.

## Aussagegrenze eines spaeteren positiven Ergebnisses

Ein bestandener 33-Pfade-Vergleich wuerde zeigen:

- der private relationale Zustand kann bei identischem aktuellem
  Feldvorzustand eine kontrollierte Feldfortsetzung vermitteln;
- diese Wirkung ist gegen ACM-OFF und den vorhandenen E1-Einzelkantengain
  technisch abgrenzbar;
- dieselbe Wirkung bleibt durch eine allgemeinere gekoppelte Gainbaseline
  vollstaendig darstellbar.

Nicht gezeigt waeren:

- eine ununterbrochene kausale Geschichte-zu-Probe-Entwicklung im Feld;
- autonome Bildung eines gemeinsamen Probevorzustands;
- Abschwaechung, Interferenz, Kapazitaetsfreigabe oder Wiederverwendung;
- Eignung fuer eine vollstaendige hypothetische MCM-Memory-Funktion;
- Lernen, Rekonstruktion, Semantik oder eine KI-Faehigkeit.

## Auditentscheidung

```text
S1_UJ_TWO_STAGE_STATE_FORMATION_AND_COMMON_FIELD_READOUT_BOUND
IDENTICAL_F_PROBE_REQUIRED_FOR_ALL_INTEGRATED_COMPARISONS
THIRTY_THREE_PATH_MINIMAL_INTERVENTION_MATRIX_BOUND
CURRENT_E1_MATCHED_EDGE_GAIN_CONTROL_REQUIRED
CGR1_EXACT_REDUCTION_CONTROL_REQUIRED
NO_UNINTERRUPTED_HISTORY_TO_PROBE_CLAIM
NO_ASSESSMENT_OF_COMPLETE_MCM_MEMORY_FUNCTION
NO_CODE_NO_TEST_NO_FIELD_RUN
```

Die 33-Pfade-Matrix ist als synthetischer Zustandsinterventionsvergleich
methodisch zulaessig. Sie bewertet die Feldvermittlung des privaten
relationalen Zustands, nicht bereits dessen ununterbrochene Entwicklung aus
Wahrnehmung.

## Erforderliche naechste Freigabe

S1-UK wuerde erstmals die private synthetische `F_PROBE`-Fixture, den
E1-Matchadapter, die reine CGR-1-Reduktionskontrolle, die 33-Pfade-Matrix und
ihre Comparatoren implementieren und synthetisch ausfuehren.

Dieser Schritt erzeugt neuen Vergleichscode und fuehrt neue synthetische
Integrationsschritte aus. Er benoetigt deshalb eine konkrete Freigabe. Auch
mit dieser Freigabe blieben oeffentliche API, Snapshots, reale Rezeptorpfade,
formale oder reale Feldlaeufe und Funktionsentscheidungen gesperrt.
