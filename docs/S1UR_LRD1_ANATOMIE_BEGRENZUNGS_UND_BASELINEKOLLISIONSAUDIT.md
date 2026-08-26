# S1-UR: LRD-1-Anatomie-, Begrenzungs- und Baselinekollisionsaudit

> **Abschlussstatus nach S1-UW:** Historische Auditstufe. Der hier
> ausgewaehlte Engineeringtraeger wurde in S1-UV mangels zusaetzlichen
> technischen Nutzens geschlossen und in S1-UW konsolidiert.

## Auftrag und Grenze

S1-UR prueft statisch, welche minimale lokale Zustandsanatomie die in S1-UQ
gebundene Rueckfuehrungsdisposition tragen koennte. Der Audit darf keine
bekannte Baseline als neue Ursache umbenennen.

Es werden keine Gleichung, Parameter, Implementierung, Runtime, Matrix oder
Feldlaeufe eingefuehrt.

## Gebundene Funktion

LRD-1 soll nach verschiedenen lokalen Rueckfuehrungsgeschichten bei
angeglichener schneller Feldlage unter derselben neuen Fortsetzung B eine
unterschiedliche lokale Rueckfuehrungstrajektorie ermoeglichen.

Die Anatomie muss dazu eine Geschichte tragen, die:

- nicht bereits in `S`, `H` oder aktuellem Rezeptorkontakt liegt;
- nicht nur spaeter von einem festen Leser ausgegeben wird;
- die Feldtransition waehrend B beeinflusst;
- lokal begrenzt und ohne Sonderloeschung abschwaechbar ist.

## Gepruefte Anatomieklassen

### A1: Ein lokaler skalarer Dispositionswert

Ein begrenzter skalarer Wert pro Feldort koennte die Staerke der spaeteren
Rueckwirkung in Richtung neutralerer Feldlage veraendern.

```text
Anatomierolle:    lokaler Rueckfuehrungsfaktor
Funktionsnutzen:  direkt und minimal
Kollision:        zustandsabhaengige Mobilitaet / adaptiver Gain
```

Diese Form ist als neue Mechanik geschlossen. Sie bleibt jedoch der kleinste
transparente Engineeringtraeger fuer die in S1-UQ gebundene Funktion.

### A2: Disposition plus lokale freie Kapazitaet

Eine zweite Rolle koennte begrenzen, wie weit sich die Disposition veraendert
und wann sie erneut beanspruchbar wird.

```text
Anatomierolle:    verfuegbar / konfiguriert oder frei / gebunden
Funktionsnutzen:  explizite Kapazitaet und Wiederbeanspruchung
Kollision:        DTS-1/T1, Capacity-Clamp und G2/D3
```

Die zusaetzliche Rolle erzeugt keine eigene Gegenprognose. Sie fuegt dem
skalaren Gain lediglich ein bekanntes Ressourcenledger hinzu.

### A3: Disposition auf Kanten oder Kantenmotiven

Eine relationale Disposition koennte bevorzugte lokale Rueckfuehrungswege
zwischen Nachbarn tragen.

```text
Anatomierolle:    adaptives Kantengewicht oder ueberlappendes Kantenmotiv
Funktionsnutzen:  gerichtete beziehungsweise relationale Rueckwirkung
Kollision:        adaptive Kante, RFM-1, ACM-1H und CGR-1
```

Ohne eine weitere nichtrelationale Ursache wird nur die bekannte
Transportdarstellung veraendert.

### A4: Gekoppeltes Dispositions- und Umformbarkeitspaar

Ein erster Zustand koennte die aktuelle Rueckfuehrung tragen, waehrend ein
zweiter Zustand beeinflusst, wie sich der erste unter Geschichte veraendert.

```text
Anatomierolle:    Rueckfuehrungsdisposition plus Aenderungsdisposition
Funktionsnutzen:  explizite Regulation zweiter Ordnung
Kollision:        F3, gekoppelte Zweizustandsrekurrenz, Materialhysterese
```

Diese Form beschreibt die S1-UO-Funktionsidee am deutlichsten, besitzt aber
ohne weitere Ursache keine von den Baselines getrennte Anatomie. Der zweite
Zustand verschiebt die Reduktionsfrage nur um eine Ebene.

### A5: Veraenderliche lokale Topologie

Eine Geschichte koennte Nachbarschaften erzeugen, loesen oder umordnen.

```text
Anatomierolle:    erzeugter oder geloester lokaler Freiheitsgrad
Funktionsnutzen:  echte Aenderung des Wirkungsinventars
Kollision:        keine unmittelbare einfache Gain-Darstellung
Blocker:          keine lokale Erzeugungs-, Loesungs- oder Bilanzursache
```

A5 waere strukturell am ehesten von A1 bis A4 verschieden. Die Abhandlungen,
der aktive Feldkern und die bisherigen Substrataudits liefern aber keine
Ursache, aus der ein neuer Freiheitsgrad lokal entstehen oder verschwinden
duerfte. Eine Topologieaenderung waere deshalb derzeit frei erfunden und wird
nicht ausgewaehlt.

## Kollisionsmatrix

| Klasse | traegt S1-UQ-Funktion prinzipiell | endliche Begrenzung moeglich | engste Erklaerung | neue Anatomie |
|---|---:|---:|---|---:|
| A1 skalar | ja | ja | Mobilitaet / Gain | nein |
| A2 skalar plus Kapazitaet | ja | ja | DTS/G2/Clamp | nein |
| A3 Kante/Motiv | ja | ja | adaptive Kante / ACM/CGR | nein |
| A4 gekoppeltes Paar | ja | ja | F3 / Zweizustandsrekurrenz | nein |
| A5 veraenderliche Topologie | theoretisch | ungeklaert | noch nicht eng reduziert | nicht begruendet |

Keine Klasse liefert derzeit gleichzeitig eine begruendete lokale Ursache,
eine Bilanz und eine eigene nichtreduzierte Gegenprognose.

## Engineeringentscheidung

S1-UQ hat festgelegt, dass Baselinegleichheit technische Entwicklung nicht
automatisch beendet. Fuer eine bewusst konstruierte MCM-kompatible Funktion
ist deshalb A1 die konservative Auswahl:

```text
LRD-E1 = privater begrenzter lokaler Rueckfuehrungsfaktor
Klasse  = zustandsabhaengige Mobilitaet / adaptiver Rueckfuehrungs-Gain
Status  = transparentes Engineeringreferenzmodell
```

LRD-E1 wird **nicht** als neue Naturursache oder nichtreduzierbare
Mechanikklasse bezeichnet. Die Auswahl erfolgt, weil A1:

- die S1-UQ-Funktion mit der kleinsten Zustandsdimension darstellen kann;
- keine Rollen-, Episoden-, Objekt- oder Pfadidentitaet benoetigt;
- lokal und opt-in vom produktiven Feldkern getrennt werden kann;
- einen exakten neutralen Nullfall erlaubt;
- gegen Fixed, Leaky, Integrator und F3 technisch vergleichbar bleibt;
- weniger unbegruendete Anatomie als A2 bis A5 einfuehrt.

## Vorlaeufige Anatomie von LRD-E1

Noch ohne Zahlen oder Fortschreibungsregel werden genau drei Rollen gebunden:

1. **Neutralreferenz:** feste inhaltsfreie technische Grunddisposition eines
   gleichartigen Feldortes; kein dynamischer Zustand.
2. **Lokale Disposition:** genau ein privater begrenzter skalarer Zustand pro
   teilnehmendem Feldort.
3. **Passive Bilanzdiagnose:** prueft Wertebereich, lokale Aenderung und
   Rueckkehr zur Neutralreferenz, ist aber kein Feldzustand.

Die lokale Disposition darf spaeter nur aus abgeschlossener lokaler
Feldgeschichte fortgeschrieben werden. Sie darf weder aktuelle Diagnosewerte
noch Versuchsphasen, Labels, Wiederholungszaehler oder Ergebnisrollen lesen.

## Begrenzungsidentitaet

LRD-E1 besitzt keine konservierte Masse und kein frei/gebunden-Ledger. Seine
Begrenzung muss dissipativ sein:

- die Disposition bleibt in einem endlichen Intervall um die
  Neutralreferenz;
- ohne tragende Feldgeschichte darf sie nicht unbegrenzt von der
  Neutralreferenz wegdriften;
- kontaktfreie Fortsetzung muss eine pruefbare funktionale Abschwaechung
  erlauben;
- jede Bereichsverletzung bricht fail-closed ab;
- Clipping darf keine normale Zustandsdynamik ersetzen.

Die konkrete Intervallbreite, Dissipationsform und sichere Diskretisierung
bleiben ungebunden und duerfen erst nach einem eigenen mathematischen Vertrag
festgelegt werden.

## Funktions- und Claimgrenze

LRD-E1 kann spaeter hoechstens zeigen, ob ein einfacher lokaler adaptiver
Rueckfuehrungsfaktor die gewuenschte Engineeringfunktion im MCM-Feld stabil
bereitstellt. Bereits vor jeder Ausfuehrung gilt:

- ein positiver Effekt ist erwartungsgemaess mit adaptivem Gain oder
  zustandsabhaengiger Mobilitaet vereinbar;
- daraus folgt keine neue Mechanikklasse;
- daraus folgt kein Befund einer vorhandenen technischen MCM-Memory;
- Nutzen, Stabilitaet und Feldkompatibilitaet bleiben legitime technische
  Prueffragen.

## Stoppregeln

Die LRD-E1-Engineeringlinie wird gestoppt, wenn:

1. die Funktion bereits durch den unveraenderten `S/H`-Pfad entsteht;
2. ein zustandsloser Fixed Adapter dieselbe A/B-Wirkung erzeugt;
3. eine einzelne Leaky-Spur bei gleichem Zustandsbudget exakt genuegt und
   LRD-E1 keinen zusaetzlichen technischen Nutzen bietet;
4. der Zustand nur eine Probeausgabe veraendert und nicht die Feldtransition;
5. lokale Begrenzung oder dissipative Abschwaechung nicht gleichzeitig
   formulierbar sind;
6. Labels, Sonderphasen, Zielwerte oder Observerrueckwirkung erforderlich
   werden;
7. eine Integration den produktiven Feldkern im LRD-OFF-Fall veraendert.

## Verbindliche Entscheidung

```text
S1_UR_NO_NON_BASELINE_COLLIDING_LRD1_ANATOMY_IDENTIFIED
S1_UR_VARIABLE_TOPOLOGY_NOT_CAUSALLY_JUSTIFIED
S1_UR_LRD_E1_SCALAR_DISPOSITION_SELECTED_AS_ENGINEERING_REFERENCE
S1_UR_LRD_E1_OPENLY_CLASSIFIED_AS_STATE_DEPENDENT_MOBILITY_OR_GAIN
S1_UR_DISSIPATIVE_BOUNDARY_REQUIRED_NO_RESOURCE_LEDGER
S1_UR_NO_EQUATION_NO_PARAMETERS_NO_RUNTIME_NO_EXECUTION
```

## Bester naechster Schritt

S1-US darf ausschliesslich den statischen lokalen Kausal- und
Lebenszyklusvertrag fuer LRD-E1 binden: welche inhaltsfreie lokale Feldgroesse
die Disposition belastet, welche Gegenrichtung sie abschwaecht, wie
Interferenz und Wiederbeanspruchung ohne Sonderphasen definiert werden und
welcher exakte LRD-OFF-Nullfall gilt. Noch keine Gleichung, Parameter,
Implementierung oder Ausfuehrung.

## Projektgrundlagen

- [S1-UQ Funktions- und Falsifikationsvertrag](S1UQ_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_LOKALE_RUECKFUEHRUNGSDISPOSITION.md)
- [S1-D Mobilitaetskollision](S1D_AUDIT_FELDSPANNUNGSABHAENGIGE_REZIPROKE_MOBILITAET.md)
- [F3 Existenz- und Reduzierbarkeitsaudit](F3_EXISTENZ_UND_REDUZIERBARKEITSAUDIT.md)
- [S1-Z Umformbarkeits-Bestandssichtung](S1Z_BESTANDSSICHTUNG_LOKAL_MITENTWICKELTE_UMFORMBARKEIT.md)
- [S1-UM Feldkern-Lueckenaudit](S1UM_STATISCHER_RUECKKEHR_UND_LUECKENAUDIT_PRIMAERER_MCM_FELDKERN.md)
