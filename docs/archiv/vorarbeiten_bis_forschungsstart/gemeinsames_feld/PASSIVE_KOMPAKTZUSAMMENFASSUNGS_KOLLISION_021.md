# Passive Kompaktzusammenfassungs-Kollision 021

## Status

Diese Untersuchung ist ein passiver Observerlauf vor `GF_001`. Sie ergänzt
keine Feldgleichung, keinen Zustand und keine Runtime-Schnittstelle.

Ausgangspunkt ist die
[Passive Zeitrepräsentations-Scheiterkarte 020](PASSIVE_ZEITREPRAESENTATIONS_SCHEITERKARTE_020.md):
Einfache skalare Nullrepräsentationen verlieren zeitliche Ordnung, während die
vollständige bekannte Stützbahn variabel breit bleibt.

## Frage

Reicht ein deutlich breiteres, aber fest großes Bündel üblicher
Verlaufskennwerte aus, um verschieden geordnete Kontaktbahnen zu unterscheiden?

## Adversarielle Kontrolle

Die beiden vollständig gestützten Wege lauten:

```text
A: 0,5 -> 0,2 -> 0,8 -> 0,3 -> 0,7 -> 0,5
B: 0,5 -> 0,7 -> 0,3 -> 0,8 -> 0,2 -> 0,5
```

`B` ist die exakte Zeitumkehr von `A`. Beide Wege besitzen:

- dieselbe Dauer,
- dieselbe Segmentanzahl,
- denselben Anfang und Endpunkt,
- dieselben Kontaktwerte,
- dieselben Einzeldauern.

Die Wege sind dennoch als geordnete Stützbahnen verschieden.

## Geprüfte feste Zusammenfassung

Nach der synthetischen Ground-Truth-Normalisierung werden 13 Kennwerte
beobachtet:

1. Segmentanzahl,
2. Gesamtdauer,
3. erster Kontakt,
4. letzter Kontakt,
5. zeitgewichteter Mittelwert,
6. zeitgewichtetes zweites Moment,
7. Minimum,
8. Maximum,
9. Gesamtvariation,
10. positive Variation,
11. negative Variation,
12. Summe benachbarter Kontaktprodukte,
13. Anzahl der Richtungswechsel.

Diese Zusammenfassung hat eine feste Breite. Sie ist nur eine Nullbaseline und
keine vorgeschlagene MCM-Repräsentation.

## Ergebnis

Beide Wege erzeugen exakt dieselbe Zusammenfassung:

```text
Segmentanzahl             = 6
Gesamtdauer               = 6
Anfang / Ende             = 0,5 / 0,5
Mittelwert                = 0,5
zweites Moment            = 0,293333...
Minimum / Maximum         = 0,2 / 0,8
Gesamtvariation           = 2,0
positive / negative Var.  = 1,0 / 1,0
Nachbarproduktsumme       = 1,06
Richtungswechsel          = 4
```

Die Darstellungsinvarianz aus Vertrag 019 wurde zusätzlich mit der dichten und
groben konstanten Kontaktbahn erneut geprüft und bleibt für dieses Bündel
erfüllt.

## Tragfähiger Befund

Ein festes Bündel aus üblichen Lage-, Moment-, Extrema-, Änderungs- und
Nachbarschaftskennwerten kann zwei verschieden geordnete Bahnen trotz gleicher
Weltstütze vollständig kollidieren lassen.

Der Grund ist enger als eine allgemeine Unmöglichkeit:

> Die geprüften Kennwerte tragen keine eindeutige gerichtete Zeitordnung.

Nicht gezeigt ist:

- dass jede feste oder kompakte Darstellung scheitert,
- dass 13 Kennwerte eine minimale oder vollständige Baseline bilden,
- dass Zeitumkehr immer eine andere Feldwirkung haben muss,
- dass eine Sequenz gespeichert werden muss,
- dass eine bestimmte ordnungssensitive Kennzahl organisch ist.

Insbesondere wäre die Aussage „kompakte Zeitrepräsentation ist unmöglich“
durch diesen einzelnen Kollisionsbau nicht gedeckt.

## Stopplinie

`GF_001` bleibt geschlossen. Nicht freigegeben sind:

- die 13 Kennwerte als Runtime-Nutzlast,
- vollständige Sequenzspeicherung,
- ein gerichteter Zeitoperator,
- ein lokaler Zeitwirkzustand,
- Feldkopplung, Memory, Topologie oder Lernen.

## Nächster Prüfpunkt

Der nächste passive Lauf muss die nun isolierte Eigenschaft prüfen:

```text
Kann eine feste, stützbasierte und gerichtete Zeitbeobachtung
Zeitumkehr unterscheiden,
ohne Darstellungsdichte mit Feldwirkung zu verwechseln?
```

Dazu dürfen einfache gerichtete Zeitmomente als Nullbaselines verglichen und
sofort gegen weitere Kollisionspaare geprüft werden. Auch ein positiver
Observerbefund wäre noch keine Freigabe für die Feldruntime.

Der [Passive gerichtete Zeitmoment-Abgleich 022](PASSIVER_GERICHTETER_ZEITMOMENT_ABGLEICH_022.md)
zeigt genau diese Grenze: Das erste zentrierte Zeitmoment unterscheidet die
Zeitumkehr und bleibt gegen Segmentverfeinerung invariant, kollidiert aber bei
einem anderen Paar verschieden geordneter Bahnen.
