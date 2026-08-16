# S1-LN: B3/P_IH-C10 Anatomie- und Konservationsvertrag (statisch)

S1-LN bindet den statischen Strukturrahmen für den Kandidaten auf dem bereits
ausgeloesten Lauf- und Fallkontext `C10` (`B3` / `P_IH_ATTENUATION`) vollständig
an, ohne Gleichung, Parameter, Runtime oder Ausfuehrung zu waehlen.

Ziel ist ein reiner Ressourcenanker fuer weitere Messungen:

- lokale Rollen je Kante (`free`, `conductive-bound`, `refractory`) werden je Endpunkt
  und insgesamt gebunden;
- lokale Ledgers werden aus der Knotenkapazitaet und den Kantenrollen abgeleitet;
- lokale und globale Konservationsgleichung bleibt statisch kontrolliert;
- Start-, Ablauf- und Ausfuehrungsentscheidungen bleiben explizit `false`;
- keine neue Funktionsebene oder neue Kandidatsaussage wird hier gesetzt.

## Gebundene Quellen

- `S1-LM` als statische Fallauswahl fuer `C10` (`B3_P_IH_ATTENUATION`)
- `S1-HH` als reiner Drei-Rollen-Kandidatensaldo (nicht als dynamische
  Funktionalitaet implementiert)

## Geometrie und Endpunkte

- Geometrie: `TWO_NODE_OPEN_LINE`
- Endpunkte: `node-a`, `node-b`
- Knotenkapazitaeten je Ende: `0.5`
- Kantenrolle (`node-a`,`node-b`): `conductive-bound=0.20`, `refractory=0.10`

## Lokale und globale Identität

- Lokale Rollen werden für jeden Knoten mit der halben Kantenbelastung
  der inzidenten Kanten geführt.
- `free` ist **abgeleitet**, nicht separat gespeichert.
- Lokale Identität ist gebunden; globale Identität ist gebunden.
- Globaler Rest ist Null innerhalb der Toleranz; damit ist die Konservationsgleichung
  als statische Vorbedingung erfüllt.

## Abgrenzungen gegen Baselines und Basiskomponenten

S1-LN unterscheidet strukturell:

- `fixed-adapter`: feste Koeffizienten, kein finite Rollenledger;
- `gain`: reine Skalierung ohne lokale Rollenquelle;
- `fast-afterimage`: Residuum statt lokaler Endpunkte-Ressource;
- `integrator`: Aggregation ohne abgeleitete lokale Rollenquelle;
- `replay`: Wiederholung der Eingabe bei leerem Strukturledger.

## Gesperrte Claims (klarer sprachlicher Rahmen)

`memory`, `learning`, `organism`, `consciousness`, `understanding`, `feeling`
bleiben gesperrt.

## Verbotene Zustandsformen

- unvollstaendige oder doppelte Endpunktinventare;
- nicht-kanonische oder Selbstkanten;
- nicht-finite oder negative Rollen/Kapazitaeten;
- lokale Überbelegung pro Endpunkt;
- fehlende Ableitung zwischen Speicher- und Leitungsrollen;
- nicht identische Baseline-Vergleichspfade im Anatomieverbund;
- nicht-finiter globaler Saldo.

## Nächster Schritt

S1-LN ist eine statische Bindung. Erforderlich ist erst eine separate Freigabe
für die naechste Dynamik-/Vergleichsstufe mit eigener Gegenprognose, Mess- und
Falsifikationsstruktur.
