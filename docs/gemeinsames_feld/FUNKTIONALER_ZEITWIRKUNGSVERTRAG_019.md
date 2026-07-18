# Funktionaler Zeitwirkungsvertrag 019

## Status

Vorregistrierter Funktionsvertrag vor `GF_001`.

Audit 019 ergänzt keine Feldmechanik. Er definiert erstmals, welche zeitliche
Information ein späterer Feldeffekt mindestens korrekt behandeln muss, ohne
bereits seine Gleichung oder Architektur festzulegen.

Die Prüfung bleibt synthetisch, weil nur dort die zeitliche Weltstütze jedes
Kontakts vollständig bekannt ist.

## Vorhandener Zeitträger

Der Vertrag verwendet die bereits in Audit 004 eingeführten
`TimedContactSegment`- und `ContactRateRepresentation`-Strukturen. Es entsteht
keine zweite Zeitdatenstruktur.

Ein passiver Ground-Truth-Observer fasst ausschließlich unmittelbar
aufeinanderfolgende Segmente mit exakt gleichem Kontaktwert zusammen:

```text
(0..1, 0,5) + (1..2, 0,5)
-> (0..2, 0,5)
```

Eine tatsächliche Wertänderung wird nicht zusammengelegt. Diese
Normalisierung dient nur dem synthetischen Sollvergleich und ist keine
Feldverdichtung oder Runtimefunktion.

## F1: Darstellungsinvarianz

Derselbe bekannte konstante Kontakt über denselben Horizont wird verschieden
dicht dargestellt:

```text
dicht:  10 Segmente mit Kontakt 0,5
dünn:    2 Segmente mit Kontakt 0,5
```

Beide normalisieren auf dieselbe gestützte Bahn:

```text
(0..10, 0,5)
```

Verbindliche Anforderung an einen späteren Kandidaten:

```text
gleiche gestützte Kontaktbahn
-> gleiche Feldkonsequenz
```

Die technische Segmentanzahl darf keine Wahrnehmungsintensität oder innere
Zeit erzeugen.

## F2: Ordnungszugänglichkeit

Zwei bekannte Kontaktbahnen werden kontrolliert:

```text
Bahn A: 0,2 -> 0,8 -> 0,5
Bahn B: 0,8 -> 0,2 -> 0,5
```

Jeder Abschnitt dauert drei Ticks. Beide Bahnen besitzen:

- denselben Endpunkt `0,5`,
- denselben zeitgewichteten Kontakt `0,5`,
- dieselbe Gesamtdauer.

Ihre geordnete Stützbahn bleibt dennoch verschieden.

Verbindliche Anforderung:

```text
unterschiedliche gestützte Ordnung
-> muss für einen Kandidaten zugänglich bleiben
```

Das fordert nicht, dass jede Reihenfolge zwangsläufig einen anderen späteren
Feldzustand erzeugt. Es verbietet nur, die Reihenfolge bereits an der
Eingangsgrenze durch Endpunkt oder Mittelwert unwiederbringlich zu löschen.

## Nullbaselines

| Baseline | F1 | F2 |
|---|---|---|
| bloße Segmentanzahl | scheitert | keine ausreichende Bahn |
| letzter Endpunkt | kann F1 tragen | kollidiert |
| zeitgewichteter Mittelwert | kann F1 tragen | kollidiert |
| vollständige bekannte Stützbahn | trägt Sollinformation | noch keine Feldwirkung |

Die vollständige Stützbahn ist damit nur Ground Truth, nicht automatisch die
gesuchte Runtime-Repräsentation.

## Kritische Begrenzung

Der Vertrag gilt zunächst nur für exakt bekannte synthetische Stützen. Er legt
nicht fest:

- welche Toleranz bei realem Rauschen gelten darf,
- wann zwei ähnliche Kontakte organisch als gleich wirken,
- welche Unterschiede relevant werden,
- wie lange zeitliche Information nachwirkt,
- wie eine Bahn energetisch auf das Feld wirkt.

Für reale visuelle Frames fehlt weiterhin eine belegte Weltstützdauer. Der
synthetische Observer darf daher nicht auf Live-Video übertragen werden.

## Stopplinie

`GF_001` bleibt geschlossen.

Nicht freigegeben sind:

- die Ground-Truth-Normalisierung als Runtime,
- Endpunkt-, Mittelwert- oder Integrationsmechanik,
- Sequenzspeicherung im Neuron,
- ein asynchroner lokaler Wirkzustand,
- Zeitkonstanten, Schwellen oder Toleranzen,
- Feldkopplung, Memory, Topologie oder Lernen.

## Nächste Untersuchung

Als nächstes dürfen ausschließlich passive Nullrepräsentationen gegen F1 und
F2 geprüft werden. Ziel ist nicht, sofort einen Gewinner zu bauen, sondern die
kleinste notwendige Zeitinformation zu bestimmen:

```text
Wie wenig darf ein späterer Feldträger bewahren,
ohne Darstellungsinvarianz oder Ordnungszugänglichkeit zu verlieren?
```

Die [Passive Zeitrepräsentations-Scheiterkarte 020](PASSIVE_ZEITREPRAESENTATIONS_SCHEITERKARTE_020.md)
führt diese Prüfung aus. Segmentanzahl scheitert an beiden Achsen; Endpunkt und
zeitgewichteter Mittelwert verlieren die geordnete Bahn. Nur die vollständige
bekannte Stützbahn trägt in den kontrollierten Welten beide Sollinformationen,
ist aber variabel breit und weder als minimal noch als Runtime freigegeben.

Semantik, Reflexion, Offline-Erholung und Selbstregulation bleiben geschlossen.
