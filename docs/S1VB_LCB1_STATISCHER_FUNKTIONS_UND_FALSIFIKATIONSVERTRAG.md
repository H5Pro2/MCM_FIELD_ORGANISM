# S1-VB: LCB-1 statischer Funktions- und Falsifikationsvertrag

> **Abschlussstatus nach S1-VD:** Die hier gebundene Stoppregel
> `NO_ENDOGENOUS_CAUSE` ist eingetreten. LCB-1 ist terminal geschlossen;
> dieser Vertrag darf nicht weiter ausgefuehrt oder implementiert werden.

## Freigabe und Grenze

S1-VB bindet ausschliesslich den ausdruecklich freigegebenen statischen
Funktions- und Falsifikationsvertrag fuer `LCB-1`.

Nicht freigegeben und in S1-VB nicht enthalten sind:

- Fortschreibungs- oder Rueckwirkungsgleichung;
- Parameter, Schwellen, Raten oder Zeitskalen;
- digitale Zustandsdarstellung;
- Runtime, Implementierung oder Testfixture;
- oeffentliche API oder Snapshotaenderung;
- Test-, Matrix- oder Feldlauf.

LCB-1 ist nur ein pruefbarer technischer Kandidat. Der Vertrag behauptet
weder eine MCM-Memory-Funktion noch eine besondere Faehigkeit des Feldes.

## Kandidatenidentitaet

```text
LCB-1 = local cycle balance candidate 1
deutsche Rolle = lokaler schleifengebundener Zirkulationsbilanztraeger
Status = STATIC_FUNCTION_AND_FALSIFICATION_CONTRACT_ONLY
```

Der Name bezeichnet keine Implementierungsform und keinen Befund.

## Genaue Bindung an die vorhandene Feldschleife

### Minimales Pruefmotiv

LCB-1 darf ausschliesslich an ein elementares `2 x 2`-Motiv der bereits
vorhandenen zweidimensionalen Feldgeometrie gebunden werden. Das Motiv
enthaelt vier verschiedene Feldorte:

```text
p00 -- p01
 |      |
p10 -- p11
```

Zulaessige Schleifenkanten sind genau:

```text
p00--p01
p01--p11
p11--p10
p10--p00
```

Diagonalen, zusaetzliche Partnerbeziehungen und durch den Kandidaten erzeugte
Kanten sind ausgeschlossen. Alle vier Kanten muessen bereits aus den festen
symmetrischen orthogonalen Nachbarschaftsoffsets des Feldkerns folgen.

### Kanonische Orientierung

Die zwei technischen Orientierungen werden ausschliesslich aus den festen
Koordinaten und der Achsenreihenfolge der Geometrie abgeleitet:

```text
CW:  p00 -> p01 -> p11 -> p10 -> p00
CCW: p00 -> p10 -> p11 -> p01 -> p00
```

Versuchsrollen, Welt-ID, Modalitaet, Inhalt oder Ergebnis duerfen die
Orientierung nicht bestimmen. Eine Spiegelung der gesamten Geometrie muss
CW und CCW gemeinsam vertauschen; sie darf keinen absoluten Vorzug erzeugen.

### Begrenzung des ersten Korridors

Der erste spaetere Pruefkorridor darf genau eine vorab ausgewaehlte
elementare Schleife enthalten. Ueberlappende Schleifen, ein vollstaendiges
Raster und eine produktive zweidimensionale Integration bleiben geschlossen.
Die Auswahl erfolgt vor jeder Geschichte anhand der festen Geometrie und
nicht anhand eines Ergebnisses.

## Lokale technische Ursache

Eine zulaessige LCB-1-Bildungsursache ist nur ein abgeschlossener, kausal
geordneter lokaler Feldfluss, der alle vier vorhandenen Schleifenkanten in
einer gemeinsamen Orientierung beteiligt.

Nicht als Ursache zulaessig sind:

- Rezeptorwerte ohne vermittelten Feldfluss;
- aktuelle Knotenaktivierung oder schneller Nachhall allein;
- eine einzelne aktive Kante oder ein offener Drei-Kanten-Pfad;
- blosse Reihenfolgekennungen, Zaehler oder Pfadnamen;
- ein globaler Observer, der vier Einzelereignisse nachtraeglich gruppiert;
- eine synthetisch gesetzte LCB-1-Rolle ohne normale Feldgeschichte.

Ob die vorhandene Feldgeschichte diese Ursache tatsaechlich bilden kann, ist
eine spaetere Falsifikationsfrage und keine Annahme dieses Vertrags.

## Endlicher Zirkulationszustand und Bilanzidentitaet

### Ausschliessliche Bilanzrollen

Fuer genau eine elementare Schleife werden nur drei abstrakte
Bilanzanteile zugelassen:

```text
Q_free = unbeanspruchter lokaler Schleifenanteil
Q_cw   = im CW-Sinn beanspruchter Anteil
Q_ccw  = im CCW-Sinn beanspruchter Anteil
```

Diese Rollen legen weder Datentyp noch Aktualisierung fest.

### Lokale Erhaltungsidentitaet

Die einzige in S1-VB zugelassene Identitaet ist eine reine
Buchhaltungsgrenze, keine Entwicklungsgleichung:

```text
Q_cycle = Q_free + Q_cw + Q_ccw
```

Verbindlich gelten:

- `Q_cycle` ist endlich, lokal und waehrend eines Vergleichspfads konstant;
- alle drei Anteile sind nichtnegativ;
- CW-Beanspruchung darf nicht ohne entsprechenden Verlust von `Q_free` oder
  `Q_ccw` entstehen;
- CCW-Beanspruchung darf nicht ohne entsprechenden Verlust von `Q_free` oder
  `Q_cw` entstehen;
- gleichzeitiges unabhaengiges Anwachsen aller drei Rollen ist unzulaessig;
- globale Normierung oder Kapazitaetsausgleich mit anderen Schleifen ist
  ausgeschlossen;
- Entfernung oder Unterbrechung der gebundenen Schleife darf den
  beanspruchten Anteil nicht unveraendert als vier unabhaengige Kantenspuren
  weitertragen.

Wie Beanspruchung, Gegenbeanspruchung oder Freigabe erfolgt, bleibt offen.
Eine spaetere Anatomie muss diese Rollen ohne Reset und ohne unbilanzierte
Loeschung schliessen; andernfalls wird LCB-1 gestoppt.

## Erreichbare Bildung durch zulaessige Feldgeschichte

### Zwei Gegenverlaeufe

Ein spaeterer Vergleich benoetigt zwei getrennte frische Feldgeschichten:

```text
H_CW  = normaler Feldpfad mit vollstaendigem orientiertem CW-Fluss
H_CCW = normaler Feldpfad mit vollstaendigem orientiertem CCW-Fluss
```

Beide Verlaeufe muessen dieselben Rezeptor-, Zeit-, Geometrie-, Feld- und
Praezisionsbudgets besitzen. Keine LCB-1-Rolle darf extern gesetzt,
transplantiert oder nach dem Ergebnis korrigiert werden.

### Verpflichtende Ausgleichsfortsetzung

Nach der orientierten Bildungsphase erhalten beide Verlaeufe eine vorab
festgelegte gemeinsame Ausgleichsfortsetzung. Vor der spaeteren Probe muessen
wertgleich sein:

- aktueller Rezeptorkontakt;
- vollstaendiger schneller `S`- und `H`-Feldzustand;
- alle vier Knotenwerte und Knoteninvarianten;
- jede unabhaengige gerichtete Kantenspur;
- jedes Einzelkantenhistogramm und jede Einzelkantenmarginale;
- Integrator-, Leaky-, Nachhall- und Retentionszustaende;
- F3-, DTS-1/T1-, G2/D3- und Capacity-Clamp-Zustaende, soweit die Baseline
  fuer denselben Korridor definiert ist;
- Feldzeit, Schrittgrenzen und Probevorzustand.

Kann eine vorregistrierte normale Ausgleichsfortsetzung diese Gleichheit
nicht erreichen, lautet das Ergebnis `INVALID_HISTORY_MATCH`. Der Vergleich
darf nicht durch Zustandssetzung oder eine synthetische Probeintervention
repariert werden.

## Eigene spaetere Feldprognose

Nach vollstaendiger Angleichung erhalten beide Verlaeufe dieselbe lokale
Probe `B` auf derselben intakten Schleife.

LCB-1 sagt ausschliesslich folgende technische Gegenprognose voraus:

```text
H_CW  + gemeinsame Ausgleichsfortsetzung + B
H_CCW + gemeinsame Ausgleichsfortsetzung + B

-> entgegengesetzt orientierter lokaler Flussrest auf der Schleife
```

Der Rest muss:

- numerisch in den tatsaechlichen spaeteren Feldfluesen erscheinen;
- mit Vertauschung von CW und CCW sein Vorzeichen beziehungsweise seine
  Orientierung vertauschen;
- bei neutraler Schleifenbilanz verschwinden;
- bei LCB-1-OFF den unveraenderten Feldkern reproduzieren;
- bei gleicher Geschichte und gleichem Gesamtzustand exakt reproduzierbar
  sein;
- von einem Unterschied in `S`, `H`, Rezeptorkontakt oder unabhaengigen
  Kantenspuren vor der Probe getrennt sein.

Ein Digestunterschied, ein nur vom Observer berechneter Zirkulationswert oder
eine groessere Amplitude ohne orientierungsgebundene Feldflusswirkung genuegt
nicht.

## Schleifenschluss-Intervention

Die Gegenprognose muss spaeter einen vorregistrierten offenen Kontrollarm
enthalten. Dort fehlt bereits vor der Bildung genau eine der vier
Schleifenkanten; die verbleibende Anatomie und alle erreichbaren lokalen
Expositionen bleiben so weit wie kausal moeglich identisch.

Verbindliche Prognose:

- auf der intakten Schleife kann der LCB-1-Kontrast prinzipiell auftreten;
- auf dem offenen Drei-Kanten-Pfad darf derselbe schleifengebundene Kontrast
  nicht entstehen;
- vier unabhaengige Kantenspuren duerfen dagegen ihre jeweils lokale Wirkung
  auch ohne geschlossenen Zyklus behalten.

Kann LCB-1 den offenen Kontrollarm nicht von unabhaengigen Kantenspuren
unterscheiden, ist seine Schleifenursache widerlegt.

Eine Unterbrechung nach bereits erfolgter Bildung bleibt fuer S1-VB
geschlossen. Ihre Bilanz- und Freigabefolge muss erst in einer spaeteren
Anatomie ohne unbilanzierte Loeschung eindeutig geklaert werden.

## Gegenbaselines und faire Exposition

Alle zustandsbehafteten Baselines muessen dieselbe vollstaendige
`H_CW`-/`H_CCW`-, Ausgleichs- und Probengeschichte sehen.

### B0: Unveraenderter Feldkern und schneller Nachhall

Der aktive `S/H`-Feldkern, LCB-1-OFF und schneller Nachhall muessen bei
angeglichenem Vorzustand dieselbe neutrale Fortsetzung liefern.

### B1: Unabhaengige gerichtete Kantenspuren

B1 ist die staerkste isolierende Gegenbaseline. Jede der vier gerichteten
Kanten erhaelt eine eigene Spur beziehungsweise einen eigenen Gain. Der
gesamte Satz dieser vier Rollen muss zusammen dasselbe Gesamtzustands-,
Kapazitaets-, Zeit- und Praezisionsbudget wie der LCB-1-Korridor einhalten.
B1 kennt keine Zyklusidentitaet und keine gemeinsame Vier-Kanten-Rolle.

Sind alle B1-Kantenzustaende vor B wertgleich, darf B1 keinen H_CW/H_CCW-
Kontrast erzeugen. Reproduziert eine faire B1-Variante dennoch die gesamte
LCB-1-Trajektorie, wird LCB-1 gestoppt.

### B2: ACM-1H und CGR-1

ACM-1H bleibt als private relationale Kantenmotivdarstellung enthalten.
CGR-1 ist die staerkere gekoppelte Gainreduktion, die ACM-1H bereits exakt
erklaert hat. Beide erhalten die vollstaendige Geschichte; kein vorhandenes
G/O-Ergebnis wird als LCB-1-Befund uminterpretiert.

### B3: Integrator, Leaky, Retention und Nachhall

Ein und mehrere lokale Integratoren, feste Leaky-Zeitskalen,
Retentionsbaseline und schneller Nachhall muessen mit gleichem Verlauf und
gleichem Budget verglichen werden.

### B4: Ressourcen- und Transportmodelle

F3, DTS-1/T1, G2/D3, Capacity-Clamp und ein skalar umverteilbarer
Kopplungstraeger bleiben verpflichtend. Sie duerfen nicht wegen ihres
geschlossenen Kandidatenstatus aus der Baselinepruefung entfernt werden.

### B5: Feste nichtreziproke Kopplung und lokaler Oszillator

Eine feste orientierte Kopplung prueft, ob die Richtung bereits in der
Anatomie steckt. Ein lokaler Oszillator prueft, ob der Rest nur Phase oder
gedaempfte Resonanz ist. Beide muessen mit einem festen Parametersatz alle
Gegenverlaeufe tragen.

## Falsifikations- und Stoppbedingungen

LCB-1 wird unmittelbar und ohne weitere Varianten gestoppt, wenn mindestens
eine Bedingung eintritt:

1. `NO_ELEMENTARY_CYCLE`: Das gebundene Motiv ist keine vollstaendige
   elementare Schleife der vorhandenen Feldgeometrie.
2. `NO_ENDOGENOUS_CAUSE`: H_CW und H_CCW koennen nicht ueber den normalen
   Rezeptor-, Dock- und Feldpfad gebildet werden.
3. `INVALID_HISTORY_MATCH`: Die Ausgleichsfortsetzung gleicht schnellen
   Feldzustand und saemtliche unabhaengigen Baselinezustaende nicht an.
4. `NO_ORIENTATION_ODD_FIELD_EFFECT`: Die identische Probe erzeugt keinen
   numerischen orientierungswechselnden Feldflussrest.
5. `OBSERVER_ONLY_EFFECT`: Der Rest existiert nur als nachtraeglich
   berechnete Metrik und wirkt nicht auf die Feldfortsetzung.
6. `OPEN_PATH_EFFECT_PERSISTS`: Der gleiche Kandidatenkontrast entsteht auf
   dem offenen Drei-Kanten-Kontrollpfad.
7. `EDGE_TRACE_REDUCTION`: B1 reproduziert die vollstaendige Bildungs-,
   Ausgleichs-, Probe- und Kontrolltrajektorie.
8. `ACM_CGR_REDUCTION`: ACM-1H oder CGR-1 reproduziert die vollstaendige
   Gegenprognose.
9. `STANDARD_BASELINE_REDUCTION`: Eine andere Pflichtbaseline reproduziert
   die vollstaendige Gegenprognose mit einem festen Parametersatz.
10. `BALANCE_NOT_CLOSED`: Endlichkeit, Nichtnegativitaet oder lokale
    Erhaltungsidentitaet kann nicht ohne globale Korrektur eingehalten werden.
11. `FORBIDDEN_CONTROL_ROLE`: Welt-ID, Versuchsrolle, Pfadname, Observer,
    adaptive Topologie, Reset oder getrennte Schreib-/Leseregel wird kausal
    benoetigt.
12. `NONFUNCTIONAL_DIFFERENCE`: Der Unterschied ist nur Digest-, Amplituden-,
    Nachhall-, Oszillations-, Instabilitaets- oder Laufzeitunterschied.

Eine Baselinereproduktion beendet den LCB-1-Zweig. Sie wird nicht durch eine
komplexere LCB-1-Variante beantwortet.

## Zulaessige spaetere Ergebniswoerter

Ein spaeterer Vertrag oder Vergleich darf nur zwischen folgenden technischen
Ausgaengen unterscheiden:

```text
LCB1_TECHNICAL_CYCLE_BOUND_RESIDUAL
LCB1_EXPLAINED_BY_BASELINE
LCB1_METHODICALLY_INVALID
```

Der erste Ausgang wuerde nur einen technischen schleifengebundenen
Wirkungsrest bezeichnen. Er waere kein Nachweis einer Memory-Funktion oder
einer besonderen Feldfaehigkeit.

## Verbindlicher Vertragsstand

```text
S1_VB_LCB1_ELEMENTARY_FIXED_CYCLE_BOUND
S1_VB_LOCAL_CAUSE_AND_BALANCE_IDENTITY_BOUND
S1_VB_ENDOGENOUS_HISTORY_AND_FULL_MATCH_REQUIRED
S1_VB_ORIENTATION_ODD_FIELD_PREDICTION_BOUND
S1_VB_OPEN_PATH_CONTROL_BOUND
S1_VB_EDGE_ACM_CGR_INTEGRATOR_AFTERIMAGE_RESOURCE_BASELINES_BOUND
S1_VB_TWELVE_FAIL_CLOSED_STOP_CONDITIONS_BOUND
S1_VB_NO_EQUATION_NO_PARAMETER_NO_RUNTIME_NO_API_NO_SNAPSHOT_NO_EXECUTION
S1_VB_NO_MEMORY_OR_FIELD_CAPABILITY_CLAIM
```

S1-VB laesst LCB-1 ausschliesslich als statisch pruefbaren Kandidaten zu.

## Bester naechster Schritt

S1-VC darf erst nach ausdruecklicher fachlicher Freigabe ausschliesslich die
diskrete LCB-1-Anatomie und lokale Bilanzvollstaendigkeit statisch auditieren.
Zu klaeren waeren nur:

- eindeutige Zuordnung der vier Feldorte und vier vorhandenen Kanten;
- minimale Rollen `Q_free`, `Q_cw`, `Q_ccw` ohne digitale Typfestlegung;
- gemeinsame Kapazitaet und verbotene Bilanzzustaende;
- Spiegelungs-, Rotations- und Open-Path-Invarianten;
- Ueberlappungsverbot des ersten Ein-Schleifen-Korridors;
- Fail-Closed-Anatomietests als spaeterer Vertrag, noch ohne Implementierung.

S1-VC darf keine Fortschreibungs- oder Rueckwirkungsgleichung, Parameter,
Runtime, API, Snapshotintegration, Fixture, Testausfuehrung oder Feldlauf
festlegen.

## Projektgrundlagen

- [S1-VA Kandidatenraumaudit](S1VA_STATISCHER_KANDIDATENRAUMAUDIT_LOKALE_TECHNISCHE_URSACHEN.md)
- [S1-UK ACM-1H/CGR-1-Gegenbaseline](S1UK_ACM1H_PRIVATE_SYNTHETISCHE_33_PFADE_GEGENBASELINE.md)
- [S1-UL ACM-1H-Zweigabschluss](S1UL_ACM1H_STATISCHER_ZWEIGABSCHLUSS_UND_KONSOLIDIERUNGSAUDIT.md)
- [S1-F verteilte kausale Nichtseparierbarkeit](S1F_ZULASSUNGSVERTRAG_VERTEILTE_KAUSALE_NICHTSEPARIERBARKEIT.md)
- [S1-UZ Aktivkern-Konsolidierungsabschluss](S1UZ_STATISCHER_ABSCHLUSSAUDIT_AKTIVKERN_KONSOLIDIERUNG.md)
