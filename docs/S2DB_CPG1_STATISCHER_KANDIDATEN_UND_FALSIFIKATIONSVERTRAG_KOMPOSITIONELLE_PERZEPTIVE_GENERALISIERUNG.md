# S2-DB: CPG-1 Kandidaten- und Falsifikationsvertrag

## Gegenstand

`CPG-1` bezeichnet den statischen Kandidaten einer **kompositionellen
perzeptiven Generalisierung**. Die technische Frage lautet, ob getrennt
gebildete auditive, visuelle und relationale Teilzustaende eine bisher nicht
angebotene audiovisuelle Kombination verarbeiten koennen, ohne diese
Kombination oder ihre erwartete Fortsetzung gespeichert zu haben.

S2-DB bindet ausschliesslich Funktion, Quellen, Hold-out, Budgets,
Gegenbaselines und Stoppregeln. Es fuehrt keine Gleichung, Parameter,
Implementierung, Tests oder Ausfuehrung ein. Projektmodule, Zustands-, Probe-,
Baseline-, Runner- und Feldfunktionen wurden nicht importiert oder aufgerufen.

CPG-1 ist eine private Engineeringhypothese. Der Vertrag behauptet keine
MCM-spezifische Memory-Mechanik, Feldwirkung, Semantik oder allgemeine
Intelligenz.

## Warum zwei Beispiele nicht genuegen

Aus den beiden Beobachtungen `A+X` und `B+Y` folgt mathematisch keine
eindeutige korrekte Verarbeitung von `A+Y`. Unendlich viele Regeln stimmen
auf den zwei bekannten Paaren ueberein und unterscheiden sich am Hold-out.

Das Beispiel beschreibt deshalb nur die Zielidee. Eine gueltige Fixture muss
vorab eine identifizierbare Regelfamilie, ausreichend viele
Bildungsbeobachtungen und eine ausschliesslich fuer die Auswertung bekannte
Hold-out-Fortsetzung binden. Ohne getrennten Identifizierbarkeitsnachweis ist
jeder positive oder negative Befund methodisch ungueltig.

## Abgrenzung zu geschlossenen Klassen

CPG-1 speichert keine neue gemeinsame Schluessel-Wert-Tabelle. Der in S2-DA
geschlossene CBPC-1-Zweig bleibt terminal; BAM-1-artige Zuordnung einer
bekannten gemeinsamen Kombination zu einem Ziel ist keine Generalisierung.

PPB-1 darf nur getrennte Komponenten bilden und aktualisieren. AVPC-1 darf
nur als vorhandene Paarrelationsbaseline auftreten. Replay, gemeinsame
Prototypbanken und Attraktoren duerfen keinen Hold-out-Eintrag erhalten.

Die historische offene-Welt-Grenze bleibt relevant: Eine neue Kombination
ist nur dann aussagekraeftig, wenn sie nicht durch einen vorgegebenen
Regimeindex, eine Lookup-Liste oder einen Hold-out-Schluessel markiert wird.
Ebenso muss ein fester allgemeiner Kompositor als Pflichtbaseline zugelassen
werden.

## Technische Funktionsanatomie

Jede Beobachtung besteht aus:

- einem reduzierten auditiven Teilzustand;
- einem reduzierten visuellen Teilzustand;
- einer spaeter beobachtbaren reduzierten sensorischen Fortsetzung;
- einer gemeinsamen kausalen Reihenfolge und Provenienz.

Die Fortsetzung ist ein technischer Wahrnehmungsvektor, kein Label,
Fehlersignal, Reward oder semantisches Ziel. In der Bildungsphase darf sie
den jeweiligen bekannten Komponenten folgen. Im Hold-out muss der Kandidat
seinen transienten Fortsetzungsvorschlag festschreiben, bevor die reale
Fortsetzung dem aeusseren Audit zugaenglich wird.

CPG-1 darf fortgesetzt halten:

- getrennte auditive und visuelle Komponentenprototypen;
- genau einen begrenzten, komponentenunabhaengig adressierbaren
  Relationsregelzustand;
- feste Audit-, Quellen- und Reihenfolgerollen ohne funktionale
  Hold-out-Information.

Nicht zulaessig sind gespeicherte gemeinsame Hold-out-Prototypen,
Kombinations-IDs, Paarlabels, vollstaendige Rohhistorie, Ergebnisrueckschreiben
oder eine pro Hold-out angelegte Zustandsrolle.

## Endliches Budget

Der erste Korridor bindet:

- genau zwei auditive Komponenten `A/B`;
- genau zwei visuelle Komponenten `X/Y`;
- genau zwei reduzierte Fortsetzungsrollen `R0/R1`;
- vier getrennte Leave-one-combination-out-Geschichten;
- je Geschichte genau drei Bildungs- und eine Hold-out-Kombination;
- je Kombination genau eine Bildungsexposition und genau eine spaetere
  read-only Auswertung;
- getrennte Frischzustaende ohne Carry zwischen Geschichten.

Alle funktionalen Prototypwerte, Regelzustaende, Indizes, Zaehler und
Praezisionsbits zaehlen zum Speicherbudget. Kandidat und Baselines erhalten
dieselbe Zahl reduzierter Eingaben, dieselbe Reihenfolge, dieselbe
Fortsetzungsinformation waehrend Bildung und dieselbe Gesamtzahl
funktionaler Bits.

Auditdigests und Provenienz duerfen keine Auswahl- oder Vorhersageinformation
tragen. Kann das Gesamtbudget nicht vor Materialisierung bitgenau bilanziert
werden, ist der Vergleich ungueltig.

## Echte Hold-out-Struktur

Die vier Kombinationen sind:

```text
A + X
A + Y
B + X
B + Y
```

In jeder Geschichte wird genau eine andere Kombination vollstaendig aus der
Bildung entfernt. Beide Einzelkomponenten der Hold-out-Kombination muessen in
den drei uebrigen Bildungsbeobachtungen vorkommen. Die Hold-out-Kombination,
ihre Fortsetzung und ihre Rollen-ID duerfen in keinem Kandidaten- oder
Baselinezustand erscheinen.

Mindestens zwei getrennte, vorab gebundene Relationswelten muessen dieselben
Komponenten und Marginalhaeufigkeiten verwenden, aber unterschiedliche
Fortsetzungstafeln besitzen. Dadurch wird verhindert, dass ein festes
globales `A/B/X/Y`-Lookup als Generalisierung erscheint.

Vor jeder spaeteren Implementierung muss ein passiver
Identifizierbarkeitsobserver fuer jede Welt nachweisen, dass die drei
Bildungsbeobachtungen innerhalb der gewaehlten Regelfamilie genau eine
Hold-out-Fortsetzung bestimmen. Der Observer darf nicht in Kandidat oder
Baseline zurueckschreiben.

## Verpflichtende Prueffamilien

### G1: Komponentenwiedererkennung

Auditive und visuelle Einzelkomponenten muessen getrennt vor und nach der
Bildung read-only erkannt werden. Eine falsche Einzelkomponente macht die
zugehoerige Kompositionsgeschichte ungueltig.

### G2: Bekannte Kombinationen

Die drei Bildungspaare jeder Geschichte muessen ihre beobachteten
Fortsetzungen korrekt tragen. Dieser Arm prueft Anschluss und Regelbildung,
ist aber noch kein Generalisierungsbefund.

### G3: Zurueckgehaltene Kreuzkombination

Der Fortsetzungsvorschlag fuer die nie gemeinsam angebotene Kombination wird
vor Offenlegung der Fortsetzung atomar gebunden. Erfolg erfordert die vorab
bestimmte Hold-out-Fortsetzung ohne gemeinsamen Prototyp-, Replay- oder
Key-Value-Eintrag.

### G4: Komponentenpermutation

Bei unveraenderten Einzelkomponenten wird nur ihre Paarung permutiert. Der
Vorschlag muss der vorab gebundenen Relationsregel folgen und darf nicht
einfach die haeufigste Fortsetzung ausgeben.

### G5: Marginalen- und Reihenfolgekontrolle

Komponenten- und Fortsetzungshaeufigkeiten sowie Expositionszahlen bleiben
gleich, waehrend die relationale Zuordnung wechselt. Eine Wirkung nur aus
Haeufigkeit, letzter Beobachtung oder Phasenposition ist falsifiziert.

### G6: Regelablation

Bei unveraenderten Komponentenbanken wird nur der begrenzte
Relationsregelzustand entfernt. Der systematische Hold-out-Vorteil muss
verschwinden. Bleibt er bestehen, erklaeren direkte Komponenten oder eine
verdeckte gemeinsame Speicherung das Ergebnis.

### G7: Interferenz zwischen Relationswelten

Nach einer ersten Relationswelt folgt eine zweite mit denselben
Einzelkomponenten und anderer Fortsetzungstafel. Vorab muss gebunden werden,
ob der begrenzte Regelzustand die erste Welt ersetzt oder beide Welten durch
einen rein sensorischen Kontext trennt. Labels, Welt-IDs und Reset als
Auswahlhilfe sind verboten.

### G8: Nichtidentifizierbare Negativkontrolle

Eine bewusst unterbestimmte Zwei-Beobachtungs-Geschichte wie `A+X` und
`B+Y` muss `NO_IDENTIFIABLE_COMPOSITION` liefern. Eine konkrete
Hold-out-Vorhersage in diesem Arm ist Fehlverhalten.

## Mess- und Erfolgsrollen

Getrennt zu berichten sind:

- Einzelkomponenten-Erkennung und Distanz;
- bekannte Kombinations-Fortsetzungsdistanz;
- Hold-out-Fortsetzungsdistanz und exakte technische Rollenentscheidung;
- Vorteil gegen die staerkste einzelne Baseline pro Hold-out, ohne
  Baseline-Mischung;
- Permutations- und Marginalenselektivitaet;
- Fehlvorhersage und `NO_IDENTIFIABLE_COMPOSITION`-Rate;
- Regelzustandsablation und Zustandsunveraenderlichkeit beim read-only Abruf;
- Interferenz-, Ersetzungs- und Carryrollen;
- funktionale Speicherbits, Eingabe-, Bildungs- und Probebudgets.

Ein neuer Digest, eine Zustandsidentitaet oder die bloße Ausgabe von `A` und
`Y` nebeneinander ist kein Generalisierungsbefund.

Die technische Funktion besteht nur, wenn alle vier Hold-out-Geschichten in
mindestens zwei identifizierbaren Relationswelten korrekt sind, G1 und G2
bestehen, G4/G5 keine Marginal- oder Reihenfolgeabkuerzung zulassen, G6 den
Hold-out-Vorteil entfernt, G7 die vorregistrierte Interferenzrolle erfuellt
und G8 jede unbestimmte Vorhersage verweigert.

## Gegenbaselines

Alle Baselines erhalten dieselben Bildungsbeobachtungen, Fortsetzungen,
Reihenfolgen, Komponenten- und Bitbudgets. Keine Baseline darf Hold-out-
Fortsetzung oder Hold-out-ID waehrend Bildung erhalten.

1. `No-Memory`: nur aktuelles Komponentenpaar ohne Bildungszustand.
2. `Budget-Replay`: nur die drei reduzierten Bildungstupel je Geschichte.
3. `Joint-AOPB`: gemeinsame adaptive Prototypen der beobachteten
   Kombinationen und Fortsetzungen im gleichen Bitbudget.
4. `BAM-1`: begrenzte Key-Value-/Attraktorspeicherung nur der drei bekannten
   Kombinationen; der Hold-out-Schluessel fehlt zwingend.
5. `AVPC-1`: vorhandene Paarrelation ohne allgemeinen
   Kombinationsregelzustand.
6. `Direct-Feature-Combinator`: fester, nicht lernender Kompositor aus
   Konkatenation, Summe, Differenz und komponentenweisem Produkt mit
   eingefrorenem read-only Auswerter.
7. `Factorized-Rule-Baseline`: staerkste Gegenbaseline; ein
   kapazitaets- und praezisionsgleicher allgemeiner linearer, bilinearer oder
   tensorfaktorisierter Regelschaetzer, der aus denselben drei
   Bildungsbeobachtungen denselben Hold-out vorhersagen darf.
8. `Identifiability-Oracle`: passiver diagnostischer Deckel mit Kenntnis der
   vorregistrierten Regelfamilie, aber ohne Rueckschreiben.

Der direkte Merkmalskombinator kontrolliert eine fest programmierte
Zusammenfuehrung. Die faktoriserte Regelbaseline kontrolliert die eigentliche
kompositionelle Generalisierungsfunktion. Reproduziert sie alle
Pflichtrollen mit demselben Budget, ist CPG-1 generisch erklaert und wird
gestoppt.

## Stopp- und Ungueltigkeitsregeln

CPG-1 wird fail-closed gestoppt, wenn:

- Replay, Joint-AOPB, BAM-1 oder AVPC-1 den Hold-out durch gespeicherte
  gemeinsame Information reproduziert;
- der direkte Merkmalskombinator alle Pflichtrollen reproduziert;
- die faktoriserte Regelbaseline alle Pflichtrollen reproduziert;
- nur Komponenten nebeneinander ausgegeben oder ein bekanntes Gesamtmuster
  abgerufen wird;
- die Hold-out-Fortsetzung nicht eindeutig aus der Bildungsinformation und
  der vorregistrierten Regelfamilie bestimmbar ist;
- mehr Speicherbits, Bildungstupel, Proben, Praezision oder funktionale
  Kontextinformation als einer Baseline verwendet werden;
- ein Welt-, Paar-, Hold-out- oder Ergebnislabel in den Consumer gelangt.

Methodisch ungueltig sind ungleiche Eingaben, Fortsetzungsinformationen,
Reihenfolgen, Budgets oder Hold-out-Splits, Carry zwischen
Leave-one-out-Geschichten, nachtraegliche Regelauswahl, Ergebnisfeedback,
Teilreceipts oder Retry.

Die spaetere Entscheidungsmenge ist:

```text
METHOD_INVALID
COMPOSITIONAL_FUNCTION_FAILED
FUNCTION_VALID_BASELINE_EXPLAINS
FUNCTION_VALID_FACTORIZATION_REST
```

Auch ein `FUNCTION_VALID_FACTORIZATION_REST` waere nur ein begrenzter
technischer Gegenbaselinebefund und noch keine MCM-spezifische Memory- oder
Feldfunktion.

## Freigabegrenze und naechster Schritt

Nicht freigegeben sind Regelfamilie, Gleichung, Parameter, Fixturewerte,
Implementierung, Tests, Runner, API, Snapshot, Produktion, Live-Sensorik,
Feldintegration und Semantik.

S2-DC darf ausschliesslich statisch Vollstaendigkeit, Identifizierbarkeit,
Nichtduplikation, Bitbudgetfairness und eindeutige Materialisierbarkeit
pruefen. Insbesondere muss es entscheiden, ob ein direkter oder
faktorisierter Standardkompositor die gesamte CPG-1-Gegenprognose bereits
konstruktiv schliesst.
