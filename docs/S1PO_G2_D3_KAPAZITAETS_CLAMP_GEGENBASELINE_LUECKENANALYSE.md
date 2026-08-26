# S1-PO G2/D3 Kapazitaets-Clamp-Gegenbaseline und Lueckenanalyse

## Status und Umfang

S1-PO prueft ausschliesslich statisch, ob der mit S1-PN technisch
abgenommene frische Bindungskontrast eine eigene Gegenprognose gegen eine
minimale lokale Kapazitaetsbegrenzung besitzt. Es gibt keine Codeaenderung,
keine neue Gleichung, keine Testausfuehrung und keinen Feldlauf.

Entscheidung:

```text
MINIMAL_CAPACITY_CLAMP_EXACTLY_REPRODUCES_S1PN_STATIC_BINDING_CONTRAST_DISTINCT_FUNCTION_NOT_ESTABLISHED
```

## Gepruefter S1-PN-Befund

Gebunden und technisch abgenommen sind:

```text
offer_amount = 0.375
FREE_AVAILABLE.pre.free = 0.5
BLOCKED_HELD.pre.free = 0.25
candidate commit rule = min(offer_amount, pre.free)
```

Daraus folgen:

| Arm | Angebot | freie Ressource | Kandidatencommit |
|---|---:|---:|---:|
| `FREE_AVAILABLE` | `0.375` | `0.5` | `0.375` |
| `BLOCKED_HELD` | `0.375` | `0.25` | `0.25` |

Der Kandidatenkontrast ist damit `0.375 - 0.25 = 0.125`.

## Minimale Gegenbaseline

Die kleinste faire Kapazitaets-Clamp-Baseline liest genau die fuer den
Commit relevante Vorgabe und denselben lokalen freien Betrag:

```text
clamp_commit(offer, free) = min(offer, free)
```

Sie benoetigt weder `blocked`, eine Substratgeschichte, einen Adapter, O3
noch ein Feld. Fuer die beiden S1-PN-Arme ergibt sie:

| Arm | Clampcommit | Kandidatencommit | Rest |
|---|---:|---:|---:|
| `FREE_AVAILABLE` | `0.375` | `0.375` | `0.0` |
| `BLOCKED_HELD` | `0.25` | `0.25` | `0.0` |

Der Clampkontrast ist ebenfalls `0.125`; sein Rest zum Kandidatenkontrast ist
exakt `0.0`.

## Bewertung der bisherigen Retentionsbaseline

Die in S1-PJ bis S1-PN verwendeten Retentionsreplikate erhalten absichtlich
weder Kandidatenzustand noch freie Ressourcenmenge. Sie liefern deshalb zwei
gleiche erste Antworten `0.25` und Kontrast `0.0`. Diese Replikate pruefen
Reproduzierbarkeit und Informationsisolation, sind aber keine ausreichende
Gegenbaseline gegen eine lokale Kapazitaetsbegrenzung.

Ein Vergleich `Kandidatenkontrast 0.125` gegen `Retentionskontrast 0.0`
belegt daher nur, dass der Kandidatenoperator die vorgegebene freie Ressource
liest. Er grenzt keine eigene Substratfunktion ab.

## Geschlossene Aussage

Die folgende Interpretation wird geschlossen:

```text
Der einmalige frische Bindungscommit besitzt aufgrund seines Kontrasts eine
eigene, nicht durch minimale Kapazitaetsbegrenzung erklaerte Funktion.
```

S1-PN bleibt als technische Abnahme gueltig. Weiterhin nutzbar bleiben:

- die kanonische G2/D3-Ressourcenanatomie;
- die Erhaltungs- und Fail-Closed-Pruefungen;
- der atomare lokale Bindungsoperator als konstruktives Primitiv;
- der informationsisolierte Ereignisadapter;
- der passive Comparator und die reproduzierbaren Fixtures.

Nicht verworfen werden das MCM-Wahrnehmungsfeld oder die offene dynamische
Substrathypothese. Verworfen wird nur der statische Einzelcommit als eigene
Funktionsevidenz.

## Verbleibende technische Gegenprognose

Eine unterscheidende Prognose kann erst aus einer kausal erzeugten
Ereignisfolge entstehen. Dabei muessen mindestens getrennt messbar sein:

1. Belastung einer endlichen lokalen Ressource durch ein erstes Ereignis;
2. anschliessender Rollenwechsel in einen nicht sofort nutzbaren Zustand;
3. Freigabe dieses Zustands waehrend einer gebundenen Nullkontaktphase;
4. erneute Beanspruchung durch ein identisches Folgeangebot;
5. Unterschied gegen Baselines, die dieselbe relevante Vorgeschichte sehen.

Der spaetere Hauptvergleich darf nicht nur den letzten Commit betrachten.
Er muss die vollstaendige Ledgertrajektorie und die kausale Herkunft jedes
freien Betrags pruefen. Eine statische Clamp-Baseline bleibt Pflichtkontrolle
am letzten Bindungsschritt. Zusaetzlich bleiben Fixed Adapter,
Leaky/Integrator, zweistufiges E1, schneller Nachhall und eine explizite
Erholungsbaseline aktive Gegenmodelle.

## Verwerfungsbedingungen fuer die Fortsetzung

Der naechste dynamische Kandidat wird gestoppt, wenn mindestens eine der
folgenden Bedingungen gilt:

- seine Zustandsfolge wird extern eingesetzt statt kausal erzeugt;
- die Baselines erhalten nicht dieselbe relevante Ereignisgeschichte;
- der Unterschied entsteht nur erneut aus `min(offer, free)`;
- Freigabe oder Wiederbeanspruchung ist nicht direkt im Ledger messbar;
- eine registrierte Erholungs-, Leaky- oder Adapterbaseline reproduziert die
  vollstaendige gerichtete Prognose;
- Teilcommit, Clipping, Reparatur oder unbegrenzte Ressource ist erforderlich.

## Aussagegrenze

S1-PO ist eine statische Baseline-Schliessung. Es gibt keinen neuen
Funktionsbefund, keine Feldwirkung und keinen Nachweis hypothetischer
MCM-Memory. Der Befund erzwingt keine Aenderung des MCM-Feldkerns; er
praezisiert die notwendige zeitliche Falsifikation des Substratzweigs.

## Naechster erlaubter Schritt

S1-PP darf ausschliesslich einen Funktions- und Falsifikationsvertrag fuer
eine kausal erzeugte Belastungs-, Freigabe- und Wiederbeanspruchungsfolge
binden. Vor Gleichung, Parametern oder Implementierung muessen Ereignisfolge,
Ledgerobservablen, faire Gegenbaselines, gerichtete Prognose und
Verwerfungsbedingungen feststehen. Kein Test und kein Lauf sind freigegeben.
