# S1-HL: DTS-1 Transferdimensionen und Ressourcenobergrenzen

## Status

Statischer Dimensions- und Bilanzvertrag hinter S1-HK. Keine Transferformel,
keine Parameterwerte, keine Rate, kein Zeitgesetz, kein Integrator, keine
Konfliktloesung, keine Feldrueckwirkung, keine Runtime und kein Lauf.

Entscheidung:

```text
DTS1_TRANSFER_DIMENSIONS_AND_RESOURCE_CEILINGS_BOUND_NO_LAW
```

## Dimensionsrollen

```text
q_i, f_i, b_e, u_e                Einheit Ressource
spaeterer Transferbetrag          Einheit Ressource
p_e                               dimensionslos
physisches Intervall              Einheit Zeit
spaetere Intervallantwort         dimensionslos
```

S1-HL waehlt weder eine Zeitskala noch einen Ratenwert. Es bindet nur, dass
eine spaetere zeitabhaengige Transferform dimensionskonsistent einen
Ressourcenbetrag liefern muss.

## Harte Quellobergrenzen

Aus der S1-HI-Halbbilanz folgen fuer einen abgeschlossenen Vorzustand:

```text
Bindungsbetrag  <= 2 * min(f_i, f_j)
Umsatzbetrag    <= b_e
Erholungsbetrag <= u_e
```

Der Faktor zwei im Bindungsmaximum ist keine Modellwahl. Eine auf Kante
`e={i,j}` gebuchte Ressourceneinheit beansprucht nach S1-HI je eine halbe
Einheit an beiden Endpunkten.

Fuer mehrere gleichzeitig an Knoten `i` bindende Kanten gilt gemeinsam:

```text
0.5 * Summe(aller inzidenten Bindungsbetraege) <= f_i
```

Alle Betraege muessen aus demselben abgeschlossenen Vorzustand beurteilt
werden. Ressource, die innerhalb derselben spaeteren Aktualisierung frei oder
gebunden wuerde, darf nicht sofort als neue Quelle weitergereicht werden.

## Notwendige Nullgrenzen

Eine spaetere Transferform muss mindestens folgende Nullen besitzen:

- Bindung ist null bei `p_e = 0`;
- Bindung ist null bei `f_i = 0` oder `f_j = 0`;
- Umsatz ist null bei `b_e = 0`;
- Erholung ist null bei `u_e = 0`;
- jeder Transfer ist null bei einem physischen Intervall der Laenge null.

Diese Nullbedingungen legen keine Produktform fest. Sie sagen nur, wann ein
Transferbetrag zwingend verschwinden muss.

## Fail-Closed-Grenze

Verboten bleiben:

- nachtraegliches Clipping eines zu grossen Transferbetrags;
- Nachnormierung konkurrierender Kantenbetraege;
- direkte Verwendung refraktaerer Ressource fuer neue Bindung;
- Nutzung einer im selben Update erzeugten Rolle als neue Quelle;
- globales Ausleihen zwischen nicht inzidenten Knoten;
- teilweise Annahme nach Aufrufreihenfolge;
- Auswahl eines Parameterwerts, einer Rate oder Zeitkonstante in S1-HL.

Kann eine spaetere Kandidatenform alle gleichzeitigen Quellgrenzen nicht vor
der Zustandsbildung einhalten, muss sie ohne Teilzustand abbrechen.

## Keine Transferaussage

Die berechneten Obergrenzen sind keine vorgeschlagenen Transferbetraege. S1-HL
legt nicht fest, ob eine Quelle vollstaendig, teilweise oder gar nicht genutzt
wird. Es entsteht kein Ressourcenwechsel und kein Nachweis von Abschwaechung,
Interferenz, Freigabe, Wiederbeanspruchung oder Feldwirkung.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1hl_transfer_dimension_budget_contract.py
tests/test_dynamic_substrate_s1hl_transfer_dimension_budget_contract.py
```

Die Tests pruefen nur Einheitenrollen, Obergrenzen, Nullquellen,
Konkurrenzbilanz, Eingabevalidierung und die geschlossene Dynamikgrenze.

## Bester naechster Schritt

S1-HM darf nach dem naechsten `ok weiter` genau eine minimale
Transfergesetzfamilie statisch gegen S1-HH bis S1-HL und die bekannten
Baseline-Reduktionen auditieren. Das Ergebnis ist `ZULASSEN` oder `STOPP`;
noch keine Runtime und kein Lauf.
