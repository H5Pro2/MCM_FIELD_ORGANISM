# S2-DA: CBPC-1 Audit und konstruktiver Zweigstopp

## Auftrag und Grenze

S2-DA auditiert ausschliesslich statisch den S2-CZ-Vertrag fuer CBPC-1.
Geprueft wurden Vollstaendigkeit, Budgetfairness, Teilhinweise,
Prueffamilien, Materialisierbarkeit und konstruktive Reduzierbarkeit.

Es wurden keine Projektmodule importiert, keine Zustands-, Probe-, Baseline-
oder Runnerfunktion ausgefuehrt und keine Implementierung geaendert.

## Vollstaendiger Funktions- und Falsifikationsrahmen

S2-CZ bindet die Forschungsfrage strukturell vollstaendig:

- getrennte Rollen fuer Kontext, Teilhinweis und audiovisuelles Ziel;
- zwei begrenzte Inhaltsbanken und vier Relationsslots;
- eine balancierte Vier-Beziehungen-Tafel mit gleichen Marginalen;
- sieben Prueffamilien fuer Vollhinweis, Teilhinweis, Rauschen,
  Kontexttausch, Interferenz, Kapazitaet und Relationsablation;
- getrennte Verhaltens-, Fehler-, Zustands- und Budgetmessungen;
- No-Memory, Budget-Replay, statische und adaptive Prototypbanken, AVPC-1
  und eine begrenzte assoziative/Attraktorbaseline;
- Erfolgs-, Stopp-, Methoden- und Claimgrenzen.

Ein neuer Digest, Zaehler oder Slotwechsel ist korrekt als unzureichende
Erfolgsmetrik ausgeschlossen. Rollenlabels, Rohhistorie und semantische
Information bleiben fuer alle Consumer verboten.

## Budgetaudit

Die Kapazitaetsrollen sind endlich gebunden: hoechstens drei auditive und
drei visuelle Inhaltsprototypen sowie genau vier Relationsslots. Alle
funktionalen Vektoren, Indizes, Masken und entscheidungswirksamen Zaehler
muessen fuer Kandidat und Baselines in dasselbe Bitbudget eingehen.

Eine exakte Materialisierung ist dennoch noch nicht moeglich. Nicht gebunden
sind:

1. Bitbreiten und kanonische Kodierung der Prototypwerte und Indizes;
2. Bitbreiten der Support-, Konflikt- und Reihenfolgerollen;
3. exakte Aufteilung des Gesamtbudgets auf gemeinsame AOPB-, Replay- und
   assoziative Baselinezustaende.

Damit ist die geforderte Budgetgleichheit als Regel vorhanden, aber noch
nicht numerisch beweisbar.

## Teilhinweis- und Prueffallaudit

Die 50-Prozent-Maskierung trennt unbekannte Werte korrekt von Nullwerten.
Fuer eine eindeutige Fixture fehlen jedoch das verbindliche Rezeptorprofil,
die geradzahlige Traegerdimension und die exakten sichtbaren Maskenindizes.

Weitere offene Materialisierungsrollen sind:

- der konkrete Rauschvektor und seine feste Staerke;
- genau eine statt zwei zugelassener Interferenzpolitiken;
- die vorregistrierte Opfer- und Gleichstandsrolle beim fuenften Eintrag;
- exakte Kontext-Mismatch- und `NO_COMPLETION`-Regeln;
- Comparatorprioritaet, Distanzgrenzen und All-of-Aggregation.

Diese Punkte wuerden eine Implementierung fail-closed blockieren. Sie werden
in S2-DA nicht korrigiert, weil die konstruktive Reduktion den Kandidaten
bereits vorher stoppt.

## Baselinevergleich

### No-Memory und getrennte Prototypbanken

No-Memory und getrennte statische beziehungsweise adaptive
Einzelprototypbanken besitzen keine Kontext-Hinweis-Ziel-Bindung. Sie koennen
die balancierte Tafel ohne zusaetzliche Relationsinformation nicht
reproduzieren.

### AVPC-1

AVPC-1 bindet einen auditiven Schluessel an ein visuelles Ziel, besitzt aber
keine getrennte Kontextrolle. Es kann den identischen Hinweis fuer zwei
Kontexte nicht ohne Erweiterung zu einem gemeinsamen Schluessel
disambiguieren. In unveraenderter Form reproduziert AVPC-1 CBPC-1 nicht.

### AOPB-Joint und Budget-Replay

Eine gemeinsame adaptive Prototypbank oder reduziertes Replay kann die vier
vollstaendigen Kontext-Hinweis-Ziel-Kombinationen direkt halten und bei
Teilhinweisen vervollstaendigen. Ob alle Interferenz- und Kapazitaetsarme in
dem exakt gleichen Bitbudget liegen, bleibt wegen der offenen Bitkodierung
noch unentscheidbar. Diese beiden Baselines sind deshalb statisch plausible,
aber nicht die entscheidende Reduktion.

### BAM-1: konstruktiv vollstaendige Reduktion

CBPC-1 definiert pro Relationsslot funktional:

```text
Schluessel = (Kontextidentitaet, Hinweisidentitaet)
Wert        = (auditive Zielidentitaet, visuelle Zielidentitaet)
Metadaten   = (Support, Konflikt, Reihenfolge)
```

BAM-1 ist im S2-CZ-Vertrag als begrenzte assoziative Key-Value- oder
Attraktorbaseline mit derselben Inhaltsinformation, derselben
Relationskapazitaet und demselben read-only Ausgabeformat zugelassen.

Damit existiert eine direkte isomorphe Abbildung:

- jeder der vier CBPC-1-Relationsslots wird auf genau einen BAM-1-Eintrag
  abgebildet;
- beide verwenden dieselben sechs begrenzten Inhaltsprototypplaetze;
- Kontexttausch liest denselben zusammengesetzten Schluessel;
- Teilhinweis und Rauschen verwenden dieselbe vorab gebundene
  Schluesselzuordnung;
- Interferenz verwendet dieselbe Konfliktrolle;
- Kapazitaetsdruck verwendet dieselbe Vier-Slot-Grenze und Opferregel;
- Relationsablation entfernt in beiden Armen exakt die vier Zuordnungen;
- der read-only Abruf liefert dasselbe Zielpaar und veraendert keinen Zustand.

BAM-1 benoetigt weder mehr Relationsslots noch mehr Inhaltsprototypen,
Expositionen oder Proben. Die Darstellung kann bitidentisch zur
CBPC-1-Tabelle gewaehlt werden. Sie reproduziert daher F1 bis F7
konstruktiv mit denselben Ressourcen.

## Entscheidung

Die im S2-CZ-Vertrag gebundene Stoppregel greift vor jeder Materialisierung:

`STOP_CBPC1_CONSTRUCTIVELY_REDUCED_TO_BAM1_ASSOCIATIVE_KEY_VALUE_BASELINE`

CBPC-1 ist als eigenstaendiger Forschungskandidat terminal geschlossen. Eine
Implementierung, Fixturekorrektur oder synthetische Ausfuehrung wuerde nur
eine bekannte begrenzte assoziative Engineeringfunktion materialisieren und
keine nicht reduzierbare Gegenprognose pruefen.

Die technische Idee kann spaeter als normale private assoziative
Engineeringkomponente neu bewertet werden, falls ein konkreter
Produktnutzen freigegeben wird. Sie ist jedoch kein MCM-spezifischer
Memory-Mechanismus und kein Feldwirkungsbefund.

## Naechste Grenze

Es gibt keinen automatisch freigegebenen CBPC-1-Folgeschritt. Eine neue
Forschungsrichtung muss eine Funktion benennen, die nicht bereits durch
adaptive Prototypbildung, gemeinsame Prototypen, Replay, AVPC-1 oder eine
begrenzte assoziative/Attraktordarstellung konstruktiv reproduziert wird.
