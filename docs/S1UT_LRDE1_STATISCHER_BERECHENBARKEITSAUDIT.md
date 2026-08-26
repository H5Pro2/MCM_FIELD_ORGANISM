# S1-UT: Statischer Berechenbarkeitsaudit fuer LRD-E1

> **Abschlussstatus nach S1-UW:** Historische Auditstufe. Dieser Audit
> stoppte K1/K2/K3; die spaetere reduzierte LRD-E1-Linie wurde in S1-UV
> vollstaendig geschlossen und in S1-UW konsolidiert.

## Auftrag und Grenze

S1-UT prueft ausschliesslich, ob die in S1-US gebundenen Ursachenklassen K1,
K2 und K3 an den vorhandenen atomaren `SharedMCMField`-Schrittgrenzen
eindeutig bestimmbar waeren.

Es werden keine Gleichung, Parameter, Implementierung, Tests, Runtime,
Snapshotaenderung oder Feldlaeufe eingefuehrt oder ausgefuehrt.

## Vorhandene technische Rollen

Der bestehende Feldkern stellt fuer einen privaten atomaren Adapter bereits
folgende abgeschlossene Rollen bereit:

1. den vollstaendigen lokalen `S/H`-Vorzustand im unveraenderlichen Feld;
2. den vollstaendigen lokalen `S/H`-Folgezustand nach genau einem synchronen
   Feldschritt;
3. die dem Schritt zugeordnete Rezeptorverteilung;
4. pro angedocktem Feldknoten eindeutig `receptor_contact` oder `None`;
5. Feldort, Tick, Intervall und feste Feldgeometrie;
6. die technische Neutralreferenz `S = 0`.

Ein privater In-Memory-Carry koennte diese Rollen wie bereits beim
ACM-1H-Integrationsmuster atomar zusammenhalten, ohne `current_api` oder
Feldsnapshot zu erweitern. Diese Feststellung ist nur eine
Darstellbarkeitsaussage und keine Implementierungsfreigabe.

## Audit der Ursachenklassen

### K1: Endpunktseitig berechenbar

Bei eindeutig fehlendem lokalem Rezeptorkontakt kann aus `S_pre` und `S_next`
festgestellt werden, ob die absolute Auslenkung kleiner wird und beide Werte
auf derselben Seite der Neutralreferenz liegen. K1 ist damit als geometrische
Endpunktrelation privat berechenbar.

K1 identifiziert jedoch nicht die einzelne physikalische Ursache der
Bewegung. Der normale Feldschritt mischt lokale Diffusion, Nachbarfluss,
Randkontakt und optionale Dissipation in einer gemeinsamen Transition. Das
ist mit S1-US vereinbar, solange K1 nur als lokale Feldfortsetzung und nicht
als isolierter Selbstruecklauf bezeichnet wird.

### K2: Nicht eindeutig als tragendes Ueberschwingen berechenbar

Aus zwei abgeschlossenen Endpunkten ist ein Vorzeichenwechsel von `S`
erkennbar. Daraus folgt aber nicht eindeutig die in S1-US verlangte
tragende Ueberschwingbewegung:

- ein entgegengesetzter Nachbarfluss kann den lokalen Wert ueber Null ziehen;
- ein Endpunktpaar zeigt weder Zwischenverlauf noch Fortsetzungsrichtung;
- Werte in numerischer Nullnaehe koennen ohne gebundene Toleranz nicht von
  einem belastbaren Vorzeichenwechsel getrennt werden;
- `H` ist im neutralen schnellen Kern eine nachlaufende Spur und liefert
  keine unabhaengige lokale Bewegungsursache fuer diese Trennung.

Die exakte spektrale Schrittintegration verringert Integratorfehler, ersetzt
aber keine kausale Information ueber den Verlauf innerhalb des Schritts.
K2 erfuellt daher die eigene S1-US-Bedingung zur Trennung von numerischem und
tragendem Ueberschwingen nicht.

### K3: Als feldnahe Ruhe nicht eindeutig berechenbar

`Kein K1 und kein K2` ist technisch entscheidbar, aber nicht gleichbedeutend
mit feldnaher Ruhe. Diese Restklasse enthaelt unter anderem gleichseitige
Bewegung weg von Null, unveraenderte von Null entfernte Lagen und durch
Nachbarfluss getragene Plateaus.

Eine echte Naehe- oder Ruheentscheidung benoetigte mindestens eine gebundene
Zustands- oder Bewegungsgrenze. Eine solche Grenze waere ein neuer Parameter
und ist in S1-US bewusst nicht vorhanden. K3 kann deshalb nicht zugleich
parameterfrei, eindeutig und semantisch als feldnahe Ruhe gelten.

## API-, Snapshot- und Atomaritaetsaudit

Die Berechenbarkeitsluecke liegt nicht an der oeffentlichen Architektur:

- Vor- und Folgezustand koennen privat an derselben Schritttransaktion
  gebunden werden.
- Lokaler Rezeptorkontakt ist in der Verteilung und in der erzeugten
  Feldwahrnehmung eindeutig vorhanden.
- Eine neue Disposition koennte erst nach dem normalen Feldfolgezustand
  vorgeschlagen und fruehestens im naechsten Schritt verwendet werden.
- `LRD-OFF` koennte den bestehenden neutralen Feldpfad direkt aufrufen.

Eine oeffentliche API- oder Snapshotaenderung wuerde K2 und K3 nicht
automatisch klaeren. Es fehlt eine fachlich eindeutige Ursachenbeschreibung,
nicht ein Transportkanal.

## Fail-closed-Entscheidung

S1-US verlangt, dass K1, K2 und K3 ausschliesslich aus den zugelassenen
lokalen Rollen entscheidbar sind. Nur K1 besteht diese Pruefung. K2 und K3
bestehen sie in ihrer gebundenen Bedeutung nicht. Damit greift die erste
S1-US-Stoppbedingung vor Mathematik.

```text
S1_UT_EXISTING_PRIVATE_ATOMIC_BOUNDARY_SUFFICIENT
S1_UT_LOCAL_CONTACT_AND_S_H_ENDPOINTS_AVAILABLE
S1_UT_K1_ENDPOINT_RELATION_COMPUTABLE
S1_UT_K2_CAUSAL_OVERSHOOT_NOT_UNAMBIGUOUS
S1_UT_K3_FIELD_NEAR_QUIESCENCE_NOT_UNAMBIGUOUS
S1_UT_K1_K2_K3_LIFECYCLE_STOPPED_BEFORE_MATHEMATICS
S1_UT_NO_API_NO_SNAPSHOT_NO_EQUATION_NO_RUNTIME_NO_EXECUTION
```

Das stoppt die aktuelle diskrete K1/K2/K3-Ursachenfassung. Es widerlegt
weder den allgemeinen S1-UQ-Funktionsvertrag noch die moegliche technische
Nutzbarkeit eines transparenten adaptiven Rueckfuehrungsfaktors.

## Bester naechster Schritt

S1-UU darf ausschliesslich statisch pruefen, ob der Ursachenvertrag ohne
diskrete Ueberschwing- und Ruhelabels auf eine kontinuierliche lokale
Richtungsrelation reduziert werden kann: kontaktfreie Feldbewegung zur
Neutralreferenz, Feldbewegung von ihr weg und allgemeine stetige
Dissipation. Dabei muss vor jeder Mathematik geklaert werden, ob diese Rollen
aus denselben Endpunkten vollstaendig, gegenseitig ausschliessend und ohne
Naehe-Schwelle bestimmbar sind.

Scheitert auch diese reduzierte Ursachenbeschreibung oder wiederholt sie nur
eine engere Leaky-Baseline ohne eigenen technischen Nutzen, wird LRD-E1
vollstaendig geschlossen. Gleichung, Parameter, Implementierung und
Ausfuehrung bleiben bis zu einer gesonderten Freigabe gesperrt.

## Projektgrundlagen

- [S1-US lokaler Kausal- und Lebenszyklusvertrag](S1US_LRDE1_LOKALER_KAUSAL_UND_LEBENSZYKLUSVERTRAG.md)
- [S1-UR Anatomie- und Baselinekollisionsaudit](S1UR_LRD1_ANATOMIE_BEGRENZUNGS_UND_BASELINEKOLLISIONSAUDIT.md)
- [S1-UQ Funktions- und Falsifikationsvertrag](S1UQ_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_LOKALE_RUECKFUEHRUNGSDISPOSITION.md)
