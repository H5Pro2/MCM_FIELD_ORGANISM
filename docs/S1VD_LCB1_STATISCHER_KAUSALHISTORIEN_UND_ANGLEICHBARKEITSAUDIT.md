# S1-VD: LCB-1 statischer Kausalhistorien- und Angleichbarkeitsaudit

## Freigabe und Grenze

S1-VD setzt die ausdrueckliche Freigabe fuer ausschliesslich den statischen
Kausalhistorien- und Angleichbarkeitsaudit von `LCB-1` um.

S1-VD fuehrt keine neue LCB-1-Gleichung, keinen Parameter, keine
Zustandsimplementierung, keine Runtime-, API- oder Snapshotaenderung, kein
Fixture, keinen Test und keinen Feldlauf ein.

Geprueft wird nur:

1. ob `H_CW` und `H_CCW` als normale Feldgeschichten eine endogene
   schleifengebundene Ursache tragen koennen;
2. ob danach eine nichtzirkulaere gemeinsame Fortsetzung alle unabhaengigen
   Feld- und Baselinezustaende angleichen kann, ohne den behaupteten
   Kandidatenunterschied synthetisch zu setzen.

## Verbindlicher bestehender Feldfluss

Der aktive neutrale Feldkern besitzt eine feste symmetrische
Diffusionsanatomie. Der momentane gerichtete Fluss einer vorhandenen Kante ist
bereits vollstaendig durch die beiden aktuellen Aktivierungen und die feste
Reaktionsrate bestimmt:

```text
J(j -> i, t) = r * (S_j(t) - S_i(t))
```

Dies ist keine neue S1-VD-Gleichung. Es ist die vorhandene Feldidentitaet aus
dem bereits abgeschlossenen instantanen Feldfluss-Redundanzbefund.

Verbindlich bekannt ist:

- Gegenkantenfluesse sind exakt antisymmetrisch;
- lokale Divergenz ist die Summe dieser Kantenfluesse;
- der Fluss ist vollstaendig aus `S`, fester Anatomie und Reaktionsrate
  rekonstruierbar;
- bei angeglichenem schnellen Feldzustand sind auch alle momentanen Fluesse
  identisch;
- der momentane Fluss besitzt keinen eigenen geschichtlichen Zustand.

## Schleifensummenidentitaet

Fuer die in S1-VC gebundene Rundfolge gilt im bestehenden Feldkern zu jedem
Zeitpunkt:

```text
J(p00 -> p01)
+ J(p01 -> p11)
+ J(p11 -> p10)
+ J(p10 -> p00)

= r * [(S_p00 - S_p01)
     + (S_p01 - S_p11)
     + (S_p11 - S_p10)
     + (S_p10 - S_p00)]

= 0
```

Alle Aktivierungsterme heben sich paarweise auf. Das Ergebnis gilt fuer jede
Aktivierungslage, nicht nur fuer einen besonderen Nullzustand.

Damit besitzt der aktive neutrale Feldkern keine momentane nichtverschwindende
CW- oder CCW-Schleifenzirkulation. Eine echte orientierte Flussquelle, die
gleichzeitig alle vier Kanten in derselben Rundrichtung traegt, ist in der
vorhandenen Gradientenphysik ausgeschlossen.

## Audit der vorgeschlagenen Gegenhistorien

### Variante A: Gleichzeitiger orientierter Schleifenfluss

Eine Geschichte, deren einzelne Feldlage auf allen vier Kanten denselben
CW-Sinn traegt, widerspricht der Schleifensummenidentitaet. Dasselbe gilt fuer
CCW.

```text
Entscheidung: anatomisch und kausal unzulaessig
```

### Variante B: Zeitlich nacheinander aktivierte Kanten

Rezeptorexpositionen koennen zeitlich verschiedene Knotenlagen und damit
nacheinander verschiedene lokale Kantenfluesse erzeugen. Eine aeussere
Versuchsplanung kann diese Ereignisse in einer CW- oder CCW-Reihenfolge
anordnen.

Der vorhandene Feldkern bildet daraus jedoch kein eigenes abgeschlossenes
Schleifenereignis. Zu jedem Zeitpunkt bleiben:

```text
momentaner Fluss = Funktion des aktuellen S-Zustands
Schleifensumme = 0
historische Schleifenphase = nicht vorhanden
```

Damit eine lokale Rolle feststellen koennte, dass erst `e_top`, danach
`e_right`, danach `e_bottom` und danach `e_left` beteiligt war, muesste sie
mindestens zusaetzlich tragen:

- welche Teilkante der Rundfolge bereits erreicht wurde;
- welche Teilfolge als naechstes erwartet wird;
- wann eine unvollstaendige Folge verworfen oder freigegeben wird;
- wie Gegenereignisse die Teilfolge veraendern.

Die S1-VC-Anatomie besitzt nur `Q_free`, `Q_cw` und `Q_ccw`. Keine dieser
Rollen bindet einen Kantenindex, eine Teilphase oder einen endogenen
Rundfolgenfortschritt. Eine solche Zusatzrolle waere eine neue
Sequenzzustands- oder gekoppelte Adaptermechanik und keine bereits vorhandene
Feldursache.

```text
Entscheidung: als aeussere Expositionsreihenfolge konstruierbar,
              als endogene LCB-1-Ursache nicht gebunden
```

### Variante C: Nachtraegliche Gruppierung

Ein Comparator koennte vier beobachtete Kantenereignisse nachtraeglich als
CW oder CCW klassifizieren. Diese Klassifikation waere observerseitig und
wuerde nicht auf den Feldkern zurueckwirken.

S1-VB schliesst einen globalen Observer, Pfadnamen und Versuchsrollen als
Bildungsursache ausdruecklich aus.

```text
Entscheidung: verboten durch FORBIDDEN_CONTROL_ROLE
```

## Angleichbarkeitsaudit

### Schneller Feldzustand

Eine gemeinsame Fortsetzung kann schnelle Unterschiede prinzipiell
abschwaechen. Fuer den methodischen Vertrag reicht eine nur asymptotische
Annaeherung jedoch nicht: `S`, `H` und Probevorzustand muessen vor der Probe
exakt wertgleich sein. Ohne eine konkret vorregistrierte endliche Geschichte
ist diese Gleichheit nicht statisch garantiert.

### Unabhaengige Kantenspuren und Baselines

Zeitlich verschiedene CW-/CCW-Expositionsreihenfolgen sind gerade fuer
zustandsbehaftete Kantenspuren, Leaky-Profile, Integratoren und gekoppelte
Adapter unterschiedliche Eingaben. Ob eine gemeinsame Fortsetzung alle diese
Zustaende exakt angleicht, haengt von ihren jeweiligen Fortschreibungen und
Zeitkonstanten ab.

S1-VD darf diese Werte weder setzen noch durch einen synthetischen
Zustandstransfer angleichen. Eine universelle statische Angleichbarkeit fuer
alle in S1-VB gebundenen Baselines folgt deshalb nicht aus der Anatomie.

### Zirkulaere Begruendung

Man koennte die Historien so auswaehlen, dass eine spaetere, noch unbekannte
LCB-1-Regel unterschiedliche `Q_cw/Q_ccw`-Anteile erzeugt, waehrend bestimmte
Baselineprofile zufaellig gleich enden. Das wuerde die Geschichte jedoch aus
der gewuenschten Kandidatenwirkung rueckwaerts konstruieren.

Ohne eine bereits unabhaengig vorhandene lokale Ursache waere dies genau die
in S1-VB verbotene Vorprogrammierung. Die fehlende Ursache kann daher nicht
durch weitere Matchingprofile repariert werden.

## Ausloesung der S1-VB-Stoppregeln

S1-VD loest zwei gebundene Regeln aus:

### Primaere Stoppregel

```text
NO_ENDOGENOUS_CAUSE
```

Die vorhandene Gradientenphysik traegt keine momentane Schleifenzirkulation.
Eine zeitliche Rundfolge benoetigt eine neue Teilphasen- oder
Sequenzzustandsmechanik, die weder im Feldkern noch in der S1-VC-Anatomie
vorhanden ist.

### Methodische Folge

```text
INVALID_HISTORY_MATCH
```

Es liegt kein zulaessiges `H_CW/H_CCW`-Paar mit endogener LCB-1-Ursache vor,
fuer das die vollstaendige Angleichung aller unabhaengigen Baselines
vorregistriert werden koennte. Ein Matchingaudit ohne gueltige Ursache waere
methodisch gegenstandslos.

`NO_ENDOGENOUS_CAUSE` allein genuegt gemaess S1-VB fuer den unmittelbaren
Stopp. `INVALID_HISTORY_MATCH` ist die daraus folgende Vergleichsgrenze.

## Baselineeinordnung

Es wurde keine Baseline implementiert oder ausgefuehrt. Der statische Befund
zeigt dennoch:

- momentane Kantenfluesse sind bereits durch den schnellen Feldkern
  rekonstruiert;
- getrennte zeitliche Akkumulation waere Integrator-, Leaky- oder
  Retentionsbaseline;
- explizite Kantenfolge waere eine gerichtete Kantenspur oder ein
  Sequenzadapter;
- gekoppelte Mehrkantenklassifikation faellt in die ACM-/CGR-
  Darstellbarkeitsgrenze, solange keine andere lokale Ursache vorliegt.

Damit darf eine spaetere komplexere Folgeerkennung nicht als Reparatur von
LCB-1 eingefuehrt werden.

## Verbindliche Entscheidung

```text
S1_VD_EXISTING_EDGE_FLOW_IS_SCALAR_GRADIENT_DERIVED
S1_VD_INSTANTANEOUS_ELEMENTARY_CYCLE_SUM_EXACTLY_ZERO
S1_VD_NO_SIMULTANEOUS_CW_OR_CCW_FIELD_CIRCULATION
S1_VD_SEQUENTIAL_CYCLE_GROUPING_REQUIRES_UNBOUND_PROGRESS_STATE
S1_VD_NO_ADMISSIBLE_ENDOGENOUS_HCW_HCCW_PAIR
S1_VD_FULL_BASELINE_MATCH_NOT_PREREGISTRABLE
S1_VD_STOP_NO_ENDOGENOUS_CAUSE
S1_VD_INVALID_HISTORY_MATCH
S1_VD_LCB1_BRANCH_TERMINALLY_STOPPED
S1_VD_NO_EQUATION_NO_PARAMETER_NO_IMPLEMENTATION_NO_TEST_NO_RUN
S1_VD_NO_MEMORY_OR_FIELD_CAPABILITY_CLAIM
```

LCB-1 wird an der in S1-VB vorab gebundenen Stopplinie beendet. Es folgen
keine Anatomieerweiterung, Gleichung, Parameterwahl, Runtime, Baselinefixture
oder Ausfuehrung.

S1-VA bleibt ein korrekter Kandidatenraumaudit: LCB-1 besass eine formal
isolierbare Schleifenprognose. S1-VD zeigt nun, dass die dafuer vorausgesetzte
lokale Ursache nicht aus der vorhandenen Feldphysik erreichbar ist. Das ist
ein negativer Forschungsbefund und keine Fehlfunktion des Feldkerns.

## Weiteres Vorgehen

Die Kandidatenforschung pausiert erneut. Ein allgemeines `ok weiter` darf aus
LCB-1 weder einen zeitlichen Chiralitaetszustand noch eine komplexere
Schleifenmechanik ableiten.

Eine neue Forschungsrichtung benoetigt wieder eine ausdrueckliche fachliche
Entscheidung und eine andere lokale Ursache, die nicht erst durch die
gewuenschte historische Wirkung definiert wird. Der konsolidierte aktive
MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Projektgrundlagen

- [S1-VC Anatomie- und Bilanzvollstaendigkeitsaudit](S1VC_LCB1_STATISCHER_ANATOMIE_UND_BILANZVOLLSTAENDIGKEITSAUDIT.md)
- [S1-VB Funktions- und Falsifikationsvertrag](S1VB_LCB1_STATISCHER_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG.md)
- [Instantaner Feldfluss-Redundanzbefund](forschung/009_INSTANTANER_FELDFLUSS_REDUNDANZBEFUND.md)
- [Intrinsische lokale Feldbeanspruchungsquelle](architektur/063_AUDIT_INTRINSISCHE_LOKALE_FELDBEANSPRUCHUNGSQUELLE.md)
- [Feldarbeit- und Flussdurchgang-Kollisionsaudit](Z2B_KOLLISIONSAUDIT_LOKALE_FELDARBEIT_UND_FLUSSDURCHGANG.md)
- [Aktiver neutraler Feldkern](../mcm_field_organism/neutral_local_field_substrate.py)
