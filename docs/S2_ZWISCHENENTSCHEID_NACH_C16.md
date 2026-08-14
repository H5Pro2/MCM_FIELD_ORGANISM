# S2-Zwischenentscheid nach C16

Stand: 2026-08-07

Status: `S2_REFERENCE_EXTENSION_PAUSED_AFTER_C16`

Forschungslauf: nein

## Entscheidungsfrage

Soll die S2-Referenzlinie nach der kanonischen B0/B2-End-to-End-Komposition
weiter technisch ausgebaut oder soll zuerst ein neuer Substratkandidat
vertraglich definiert werden?

## Gesicherter Stand

S2-C2 bis S2-C16 bilden einen durchgaengigen technischen Referenzpfad fuer:

- kontrollierte A- und B-Weltkontakte;
- B0 als exakten schnellen Nullpfad;
- B2 als feste lineare S-L-S-Referenz;
- externe S/H-Angleichung und identische Probe P;
- getrennte Zeitstruktur-Paarwerte bei n=1, 2, 4 und 8;
- A/B-Container und `D_world_pair(8)`;
- reproduzierbare, rein speicherinterne Komposition ohne Laufdatei.

Dieser Stand charakterisiert eine vorgegebene lineare Referenz. Er ist kein
Praegungs-, Memory- oder Feldzeitbefund.

## Noch gebundene Kontrollen

Die S0/S2-Vertraege verlangen fuer einen spaeteren Kandidaten weiterhin:

- B1 als einseitige Leaky-Spur;
- B3 als begrenzten einseitigen Integrator;
- B4 als zustandsabhaengige nichtlineare Gain-Baseline;
- B5 als Ablation der L-nach-S-Rueckwirkung;
- L-Neutralisierung und L-Tausch;
- Observer-an/aus, Snapshot/Wiederaufnahme und Reproduktion;
- gleiche lokale Zustands-, Parameter- und Ressourcenbudgets.

Diese Kontrollen werden nicht gestrichen. Ohne einen neuen Kandidaten wuerde
ihre Vollausfuehrung jedoch hauptsaechlich die bereits festgelegten
Vergleichsgleichungen bestaetigen und keine offene Substratfrage entscheiden.

## Entscheidung

1. Die S2-Referenzerweiterung endet vorerst mit C16.
2. Die 152-Aufgaben-Vollmatrix bleibt gesperrt.
3. Es wird keine weitere Metrik- oder Containerstufe angelegt.
4. B1, B3, B4, B5 und die Interventionen bleiben verbindliche spaetere
   Gegenbaselines und Kausaltrennungen.
5. Vor weiterer Ausfuehrung wird genau ein neuer Substratkandidat statisch
   definiert und gegen diese Kontrollen falsifizierbar gemacht.

## Gebundener Vertragsrahmen S1-C

S1-C darf zunaechst nur einen Funktions- und Falsifikationsvertrag enthalten.
Der Kandidat muss:

- lokal und observerfrei aus erlaubten Feldvorzustaenden fortschreiben;
- nicht auf ein lineares Integral oder einen festen Leser reduzierbar sein;
- begrenzt und unter ausbleibender Beanspruchung funktional loesbar sein;
- mit gleichem Zustands- und Ressourcenbudget gegen B0 bis B5 antreten;
- eine getrennt pruefbare Kausalrichtung `S -> L` und `L -> S` besitzen;
- Tausch und Neutralisierung erlauben;
- ohne Label, Reward, Welt-ID, Zielmuster, Wiederholungszaehler oder
  programmierte Bedeutung auskommen.

S1-C waehlt noch keine Erfolgsschwelle und behauptet keine Memoryfunktion.
Erst nach dem statischen Vertrag kann eine technische Kandidatenimplementierung
gesondert entschieden werden.

## Bester naechster Schritt

Der [S1-C-Zulassungsvertrag](S1C_ZULASSUNGSVERTRAG_MINIMALER_NICHTLINEARER_LOKALER_SUBSTRATKANDIDAT.md)
ist gebunden. S1-D reduziert die gepruefte MCM-spezifische Naturannahme auf
eine Relaxationsbaseline. S1-E begruendet keine zweite lokale Variable und
bestimmt verteilte kausale Nichtseparierbarkeit als offene Feldanforderung.
Ihr statischer S1-F-Zulassungsvertrag ist gebunden und oeffnet keinen
geschlossenen Traegerzweig. Der S1-G-Richtungsentscheid ist gebunden:
Feldwahrnehmung bleibt technisch aktiv, Substratimplementierung pausiert.
Als naechstes folgt W1-A. Noch keine Substratimplementierung und kein
Forschungslauf.
