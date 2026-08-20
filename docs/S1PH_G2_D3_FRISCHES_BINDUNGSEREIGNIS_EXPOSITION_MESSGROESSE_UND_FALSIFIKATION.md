# S1-PH G2/D3 frisches Bindungsereignis: Exposition, Messgroesse und Falsifikation

## Status und Umfang

S1-PH bindet ausschliesslich den statischen Expositions- und Messvertrag fuer
das in S1-PE noch inhaltsfreie frische Bindungsereignis. Der Schritt legt
Payloadrollen, kausale Reihenfolge, direkte Ledger-Messung, faire
Baselineexposition, Gegenprognosen und Falsifikation fest.

S1-PH waehlt keinen Zahlenwert, keine Wirkungsgleichung und keinen Parameter.
Es gibt keine Implementierung, keinen Test, keinen Kandidaten-, Feld- oder
Runtimelauf.

Entscheidung:

```text
G2_D3_IDENTICAL_FRESH_BINDING_EXPOSURE_AND_LEDGER_MEASUREMENT_BOUND
```

## Technische Fragestellung

Nach der gueltigen S1-PE-Intervention besitzen beide Kandidatenarme dieselbe
Gesamtressource und dieselbe leitende Bindung, aber verschiedene Anteile in
`free` und `blocked`. S1-PH fragt ausschliesslich:

> Fuehrt dasselbe frische lokale Bindungsangebot in beiden gueltigen
> D3-Zustaenden zu einer unterschiedlichen tatsaechlich neu gebundenen
> Ressource?

Untersucht wird nicht der unmittelbare O3-Readout. Eine O3-Differenz ist
bereits durch den unterschiedlichen `free`-Wert konstruktiv festgelegt und
bleibt nur eine externe Manipulationskontrolle.

## Modellneutraler Ereignispayload

Ein spaeterer kanonischer Payload muss genau folgende Sachrollen tragen:

```text
schema_id
schema_version
event_identity_digest
event_id
event_role = FRESH_LOCAL_BINDING_OFFER
edge_id
field_reference_digest
source_role = free
target_role = bound_unconfigured
offer_amount
common_exposure_digest
payload_digest
```

`offer_amount` muss spaeter positiv, endlich und dyadisch gebunden werden.
S1-PH waehlt seinen Wert noch nicht.

Der Payload darf nicht enthalten:

- Arm-, Fixture- oder Interventionskennung;
- `free`, `blocked` oder eine andere Kandidatenressource;
- O3-Readout oder Kandidatenresultat;
- Baselinezustand oder Baselineausgabe;
- Zielausgang, Label, Reward oder Ergebnisflag;
- Rohdaten, Rezeptorfolge oder Kontaktarchiv;
- eine fuer die Arme verschiedene Ereignisversion.

Die kanonischen Ereignisbytes und ihr Digest muessen fuer beide
Kandidatenarme und alle registrierten Baselinereplikate identisch sein.

## Ereignisanatomie ohne Wirkungsgleichung

Das Ereignis bietet ausschliesslich eine noch festzulegende Menge fuer eine
lokale Bindung von `free` nach `bound_unconfigured` an. Es gibt in S1-PH
keine Regel, wie viel davon tatsaechlich gebunden wird.

Bei einem spaeter gueltigen Nachzustand duerfen durch dieses Ereignis nur
folgende Rollen gegensinnig veraendert sein:

```text
free
bound_unconfigured
```

Unveraendert bleiben muessen:

```text
capacity
bound_configured
blocked
Kante, Traeger, Geometrie und Feldreferenz
```

Diese Rollenbindung ist eine Bilanzgrenze und noch keine
Bindungsdynamik.

## Primaere direkte Ledger-Messgroesse

Fuer jeden Kandidatenarm wird die tatsaechlich neu gebundene Ressource erst
nach zwei einzeln gueltigen Vor- und Nachrecords passiv bestimmt:

```text
committed_from_free
= pre_event.free - post_event.free

committed_to_bound_unconfigured
= post_event.bound_unconfigured - pre_event.bound_unconfigured
```

Ein gueltiger Commitwert existiert nur, wenn beide Differenzen exakt gleich,
endlich und nichtnegativ sind. Die Identitaet ist eine Messdefinition, keine
Regel fuer die Erzeugung des Nachzustands.

Die primaere Kandidatenmessgroesse ist der gerichtete Kontrast:

```text
candidate_binding_contrast
= committed_FREE_AVAILABLE - committed_BLOCKED_HELD
```

Die vorregistrierte Kandidatenprognose lautet:

```text
candidate_binding_contrast > 0
```

Ein spaeterer exakter Angebotswert muss deshalb so gewaehlt werden, dass er
die niedrigere freie Ressource beansprucht und zugleich innerhalb der
hoeheren freien Ressource liegt. Der genaue Wert bleibt S1-PH gesperrt.

## Kausale Reihenfolge

Eine spaetere Pruefung muss exakt folgende Ordnung einhalten:

1. den gueltigen S1-PG-Interventionsreceipt passiv pruefen;
2. beide postinterventionellen D3-Vorzustaende einzeln validieren;
3. zwei Baselinereplikate aus demselben registrierten Baselinevorgang bilden;
4. allen Kandidatenarmen und Baselinereplikaten byteidentische Ereignisbytes
   zustellen;
5. jeden Kandidatennachzustand separat und fail-closed validieren;
6. erst danach die beiden direkten Commitwerte bestimmen;
7. Baselinereaktionen erst nach zwei vollstaendigen Ergebnissen vergleichen;
8. Kandidaten- und Baselinekontrast passiv zusammensetzen.

Kein Readout, Receipt oder Zwischenresultat darf als Eingang eines anderen
Arms verwendet werden.

## Faire Baselineexposition

Die primaere zustandsbehaftete Gegenbaseline wird in zwei unabhaengigen
Replikaten aus demselben gueltigen Vorzustand erzeugt. Beide Replikate sehen:

- dieselbe kausale Vorgeschichte bis zum gemeinsamen Vorzustand;
- dieselbe modellneutrale Interventionsgrenze ohne Arm- oder
  Ressourceninformation;
- dieselben kanonischen Bytes des frischen Bindungsereignisses;
- keinen O3-Wert und keine Kandidatenzustandsbytes.

Fixed- und Gainbaseline koennen als transparente Zusatzkontrollen dieselbe
Exposition erhalten. Die hier zugelassenen Baselineoperatoren bekommen weder
eine Kandidatenrolle `free`/`blocked` noch die kontrollierte interne
Kandidatenaufteilung als Ersatzeingang.

Fuer die zwei Replikate einer fair exponierten Baseline gilt die
Gegenprognose:

```text
baseline_replica_contrast
= response_replica_FREE_AVAILABLE - response_replica_BLOCKED_HELD
= 0
```

Die Replikatnamen sind nur externe Vergleichsrollen und werden nicht an den
Baselineoperator uebergeben.

## Entscheidungsmuster

Der spaetere technische Vergleich besitzt genau vier atomare Ausgaenge:

```text
CANDIDATE_DIFFERENT_BASELINE_EQUAL
CANDIDATE_EQUAL_BASELINE_EQUAL
BASELINE_DIFFERENT_EXPOSURE_INVALID
INVALID_OR_INCOMPLETE
```

Nur `CANDIDATE_DIFFERENT_BASELINE_EQUAL` entspricht der in S1-PH
vorregistrierten Ressourcenprognose. Auch dieser Ausgang belegt zunaechst nur
eine kontrollierte ressourcenabhaengige Bindungsreaktion.

## Falsifikation und Abbruch

Die Kandidatenprognose ist fuer diese Fixture falsifiziert, wenn beide
Kandidatencommits nach vollstaendiger gueltiger Exposition gleich sind.

Die gesamte Pruefung ist vor einer Ergebnisentscheidung ungueltig oder
abzubrechen, wenn:

- Ereignisbytes oder Ereignisdigests zwischen Armen oder Baselines abweichen;
- der Payload Armkennung, Kandidatenressource oder O3 enthaelt;
- der Angebotswert die niedrigere freie Ressource nicht uebersteigt oder die
  hoehere freie Ressource uebersteigt;
- Vor- oder Nachrecord ungueltig ist;
- mehr als `free` und `bound_unconfigured` veraendert wird;
- die beiden direkten Ledgerdifferenzen nicht exakt uebereinstimmen;
- ein Nachzustand geklemmt, repariert oder normalisiert wird;
- Baselinereplikate verschiedene relevante Vorgeschichten oder Inputs sehen;
- ein Baselinekontrast ungleich null ist;
- nur O3, nicht aber die tatsaechliche Ledgerbindung verglichen wird;
- ein Receipt oder Ergebnis in einen Ausfuehrungspfad zurueckgefuehrt wird.

## Methodische Aussagegrenze

Eine spaetere positive Kandidatendifferenz waere noch kein Befund einer
selbst entstandenen Substratgeschichte. Die `free`/`blocked`-Differenz wurde
hier kontrolliert extern gesetzt. Der Schritt kann daher nur pruefen, ob
diese lokale Ressourcenrolle eine nachfolgende Bindung technisch begrenzt.

Fuer die Entwicklungsrichtung einer hypothetischen MCM-Memory waeren danach
weiterhin eigenstaendige Pruefungen von Bildung, Abschwaechung, Interferenz,
Freigabe und erneuter Nutzbarkeit erforderlich.

## Naechster erlaubter Schritt

S1-PI darf ausschliesslich den endlichen Ereignis- und Messfixturevertrag
binden: exakter dyadischer Angebotswert, kanonische Payloadbytes, Digests,
Baseline-Replikatprovenienz und erwartete rein statische Messgrenzen.
Wirkungsgleichung, Nachzustandswerte, Implementierung, Test und Lauf bleiben
gesperrt.
