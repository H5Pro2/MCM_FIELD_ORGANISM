# S1-JG: Gemeinsame modellneutrale Intervallhuelle

## Ergebnis

S1-JG bindet ausschliesslich den statischen Vertrag fuer eine gemeinsame
Intervallhuelle ueber P_IE sowie die korrigierten P_IH-, P_IK- und
P_IN-Expositionen. Die Huelle ist noch nicht implementiert und enthaelt noch
keine konkreten Ticks, Anfangswerte oder Intervalldigests.

## Zweistufige Informationsgrenze

Die Orchestrierung bindet vor jeder Modellwahl genau Geometrie, kanonische
Knotenfolge, Vorzustandsdirektive, Rezeptorkontakt, positive Intervallzeit,
Reihenfolge und Checkpointanweisung. Danach materialisiert sie den gemeinsamen
Feldvorzustand und die passende Rezeptordistribution.

Ein Modell erhaelt erst anschliessend eine informationsarme Sicht aus Feld,
Distribution, Zeit, Geometrie- und Eingabedigest. Profil-, Arm-, Fall-,
Sequenz-, Grenz- und Zielbezeichnungen bleiben verborgen. Dasselbe gilt fuer
Checkpointnummern, Referenzwerte, spaetere Zustaende und Fitinformationen.

## Expositionstopologien

- P_IE: zwei wertgleiche aeussere Sequenzen mit je zwei Intervallen und zwei
  Checkpoints; nur DTS-1 erhaelt getrennt die registrierte F_HIGH- oder
  R_HIGH-Anatomie.
- P_IH: eine Folge aus drei Intervallen mit einer Zweiknoten-A-Grenze vor
  jedem Intervall und drei vollstaendigen Checkpoints.
- P_IK: A-B-A und A-GAP-A mit je vier Intervallen und einer
  Dreiknotengrenze vor jedem Intervall.
- P_IN: zwei aeusserlich wertgleiche A-GAP-B-Probe-Folgen; nur DTS-1 erhaelt
  getrennt die registrierte Recovery-on- oder Recovery-off-Intervention.

Damit entstehen pro Modell und Refinement 23 gemeinsame Intervalle: 4 fuer
P_IE, 3 fuer P_IH, 8 fuer P_IK und 8 fuer P_IN. Die 24
Baseline-Rollen-Block-Faelle und das 28-Komponenten-Profil bleiben
unveraendert.

## Kandidatenseitige Sidecars

P_IE-Anatomie und P_IN-Recovery sind keine Felder der gemeinsamen Huelle oder
der modellseitigen Sicht. Sie werden vor einer spaeteren Ausfuehrung gebunden,
duerfen kein Ergebnis lesen und sind fuer B1 bis B6 ohne Platzhalter oder
abgeleitete Werte unerreichbar. Dadurch bleiben gemeinsame aeussere
Exposition und kandidatenspezifische Intervention getrennt.

## Fail-Closed-Regeln

Fehlende, zusaetzliche, falsch typisierte, nicht endliche oder digestfalsche
Felder brechen ab. Dasselbe gilt fuer Abweichungen bei Geometrie,
Knotenreihenfolge, Kontaktbreite, Zeit, Vorzustandsquelle, Sequenzordnung,
Grenzanwendung, Carry oder Checkpoint. Ein ungueltiges Intervall blockiert
alle 24 spaeteren Baselinefaelle ohne Teilausgabe.

Intervalle duerfen nicht zusammengelegt, geteilt, verzoegert, wiederholt,
umgeordnet oder ausgelassen werden. Modellinterne Refinementsubschritte wenden
keine gemeinsame Grenze erneut an. Checkpointergebnisse duerfen nicht in ein
Modell oder ein spaeteres Intervall zurueckfliessen.

## Entscheidung

`COMMON_MODEL_NEUTRAL_INTERVAL_ENVELOPE_CONTRACT_BOUND_NO_VALUES_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`dfdc0b2a1f8fd280804d3b87e950418de0c6686b6f2af0ec7dfd796f9cc3616d`

S1-JG implementiert oder bestaetigt keine Huelle, keinen Adapter und kein
Modell. Es wurden keine technischen oder forschungsbezogenen Feldschritte
ausgefuehrt. Baselinepassung, Kandidatenueberlegenheit sowie Speicher-, Lern-
und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JH darf ausschliesslich einen endlichen statischen Fixturevertrag fuer die
gemeinsame Intervallhuelle binden: konkrete Anfangszustaende, Kontakte,
Zeiten, Quellenidentitaeten, Sequenz- und Intervalldigests sowie ein begrenztes
technisches Pruefbudget. Noch keine Huelleimplementierung, kein Adapter- oder
Modellaufruf, keine Runtime und keine Forschungsprobe.
