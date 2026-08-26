# S1-HO: DTS-1 Einzelschritt-Implementierungsvertrag

## Status

S1-HO bindet die spaetere Implementierung genau eines reinen,
zustandsfreien DTS-1-Einzelschritts und seine technische Testmatrix. Es wird
noch kein ausfuehrbarer Schritt implementiert. Keine Materialparameterwerte,
keine Feldrueckwirkung, keine Runtimeintegration und kein Lauf.

Entscheidung:

```text
DTS1_PURE_STEP_IMPLEMENTATION_CONTRACT_AND_TEST_MATRIX_BOUND
```

## Private Modulgrenze

Die spaetere Implementierung darf ausschliesslich in folgendem privaten,
direkt importierten Modul liegen:

```text
mcm_field_organism.dynamic_substrate_dts1_step
```

Sie definiert einen eigenen technischen Fehler `DTS1StepError(ValueError)`
und genau einen Recheneinstieg:

```text
compute_dts1_closed_prestate_step(
    anatomy,
    edge_participations,
    elapsed_time,
    rates,
) -> DTS1StepResult
```

Das Modul bleibt ausserhalb von `mcm_field_organism.__init__`, `current_api`,
Snapshot-, Restore-, Runner-, Browser-, Audio- und Videopfaden.

## Eingabevertrag

`anatomy` ist genau eine gueltige unveraenderliche `DTS1ResourceAnatomy` aus
S1-HI. Die Implementierung verwendet deren feste Knotenkapazitaeten und
vollstaendiges Kantenressourceninventar; freie Ressource wird abgeleitet und
nicht gespeichert.

`edge_participations` enthaelt fuer jede Anatomiekante genau ein
unveraenderliches kanonisches `DTS1EdgeParticipation` mit `p_e` in `[0,1]`.
Fehlende, doppelte, zusaetzliche, selbstbezogene oder nichtkanonische Kanten
werden vor jeder Rechnung abgelehnt. Ein S/H-Feld oder Feldlayer ist kein
Eingabeargument.

`elapsed_time` ist explizit, endlich, nichtnegativ und nicht boolesch. Es gibt
keinen Default, keine implizite Uhr und keinen Aufrufzaehler.

`rates` enthaelt genau `k_bind`, `k_turn` und `k_rec` als endliche,
nichtnegative, globale und inhaltsfreie Werte. S1-HO waehlt keine Werte und
keinen Parameterkorridor.

## Ausgabe und Reinheit

`DTS1StepResult` enthaelt ausschliesslich:

- eine neue vollstaendig validierte `DTS1ResourceAnatomy`;
- ein kanonisches unveraenderliches Kantenledger aus Bindung `x_e`, Umsatz
  `y_e` und Erholung `z_e`;
- technische SHA-256-Identitaeten von Eingabe- und Ausgabeanatomie;
- maximalen lokalen und globalen Bilanzrest als passive Diagnosen.

Diagnosen duerfen weder Zustand noch eine spaetere Rechnung beeinflussen.
Eingabeobjekte bleiben unveraendert. Gleiche Werteingaben muessen denselben
Wertausgang und dieselben Digests erzeugen.

## Verbindliche Rechenphasen

1. Vollstaendige Eingaben validieren und kanonisch ordnen.
2. Freie Knotenressource aus genau einem abgeschlossenen Vorzustand ableiten.
3. Intervallanteile numerisch stabil mit `-expm1(-k*elapsed_time)` berechnen.
4. Alle Bindungsangebote aus diesem Vorzustand berechnen.
5. Alle gemeinsamen Knotennachfragen mit `math.fsum` bilden.
6. Alle lokalen Vorabzulassungen bestimmen, bevor ein Transfer gebucht wird.
7. Bindung, Umsatz und Erholung fuer alle Kanten berechnen.
8. Genau eine neue vollstaendige Anatomie atomar aufbauen.
9. Ausgabeidentitaeten und passive Bilanzdiagnosen pruefen.

Neu gebundene oder neu refraktaere Ressource darf innerhalb desselben
Schritts nicht erneut als Quelle dienen. Kantenweise Teilzulassung in
Aufrufreihenfolge ist verboten.

## Fehlergrenze

Fehler werden vor einer Ausgabe ausgeliefert. Unzulaessig sind insbesondere:

- Mutation einer Eingabe;
- gespeicherte freie Ressource oder versteckter Verlauf;
- implizite Zeit, Zufall oder umgebungsabhaengige Werte;
- Feldzustand, Adapter oder Rueckwirkung als Eingabe;
- Clipping, Nachnormierung oder Reparatur;
- Datei-, Netzwerk-, Prozess- oder Umgebungszugriff;
- unvollstaendige oder reihenfolgeabhaengige Kantenverarbeitung.

Kanonisches Sortieren bereits gueltiger Eingabeobjekte ist erlaubt. Es
repariert keine ungueltige Kante.

## Technische Testmatrix

Die spaetere Implementierung muss alle 17 Faelle bestehen:

| ID | Verpflichtender Nachweis |
|---|---|
| T01 | Nullintervall ergibt exakte Identitaet und Nulltransferledger |
| T02 | drei Nullraten ergeben exakte Identitaet |
| T03 | `p_e=0` sperrt nur Bindung, nicht Umsatz oder Erholung |
| T04 | ein freier Nullendpunkt sperrt Bindung |
| T05 | Einkantenbindung entspricht dem analytischen Intervallanteil |
| T06 | Einkantenumsatz entspricht dem analytischen Intervallanteil |
| T07 | Einkantenerholung entspricht dem analytischen Intervallanteil |
| T08 | gemeinsame Knotenkonkurrenz ist simultan und ueberzieht kein Budget |
| T09 | Kantendeklarationsreihenfolge aendert weder Ergebnis noch Digest |
| T10 | lokale und globale Ressourcenidentitaeten bleiben gewahrt |
| T11 | neu gebundene und neu refraktaere Ressource wird nicht im selben Schritt wiederverwendet |
| T12 | Eingaben bleiben unveraendert; Wiederholung ist deterministisch |
| T13 | ungueltige Skalare und Beteiligungswerte brechen ab |
| T14 | fehlende, doppelte, zusaetzliche oder nichtkanonische Kanten brechen ab |
| T15 | ungueltige oder ueberbelegte Anatomie bricht vor der Rechnung ab |
| T16 | Schrittverfeinerung naehert sich der kontinuierlichen S1-HM-Familie |
| T17 | kein Feld-, Runtime-, I/O- oder oeffentlicher API-Pfad entsteht |

Synthetische Testwerte dienen nur dem Algebra- und Grenztest. Sie sind keine
Auswahl von Materialparametern und duerfen nicht aus einem gewuenschten
Feldprofil bestimmt werden.

## Erfolgs- und Aussagegrenze

Ein spaeter bestandener Verbund belegt nur die korrekte reine
Einzelschrittalgebra. Er belegt weder ein Feldverhalten noch Abschwaechung,
Interferenz, Kapazitaetsfreigabe, Wiederbeanspruchung oder eine Funktion des
MCM-Wahrnehmungsfeldes.

## Bester naechster Schritt

S1-HP darf nach dem naechsten `ok weiter` genau das private reine Schrittmodul
und die 17 technischen Matrixfaelle implementieren. Noch keine
Materialparameterauswahl, keine Feldrueckwirkung, keine Runtimeintegration
und kein Forschungs- oder Feldlauf.
