# S2-CZ: CBPC-1 Funktions- und Falsifikationsvertrag

## Gegenstand

`CBPC-1` bezeichnet den statischen Kandidaten einer **kontextgebundenen
perzeptiven Mustervervollstaendigung unter Interferenz**. Geprueft werden soll
spaeter, ob ein unvollstaendiger oder begrenzt verrauschter audiovisueller
Wahrnehmungshinweis zusammen mit einem getrennten technischen Kontext einen
gebundenen vollstaendigeren Wahrnehmungszustand auswaehlen kann.

S2-CZ fuehrt keine Gleichung, Parameter, Implementierung, Tests oder
Ausfuehrung ein. Es wurden keine Projektmodule importiert und keine
Zustands-, Probe-, Baseline- oder Feldfunktionen aufgerufen.

CBPC-1 ist eine private Engineeringhypothese. Der Vertrag behauptet weder
eine MCM-spezifische Memory-Mechanik noch Feldwirkung oder Semantik.

## Abgrenzung zum Projektbestand

Der geschlossene E1-Teilhinweiszweig wird nicht wieder aufgenommen. Dort war
die Antwort exakt linear zur Hinweisamplitude; eine nichtlineare
Mustervervollstaendigung blieb aus.

AVPC-1 besitzt bereits eine einfache auditive Schluessel-zu-visuelle-Ziel-
Beziehung. Sie ist generisch erklaert und kann denselben Schluessel bei
konkurrierenden Zielen nicht durch einen getrennten Kontext disambiguieren.

CBPC-1 ist nur dann nicht dupliziert, wenn bei gleichen Einzelprototypen und
gleichen Einzelabstaenden ein getrennt gebundener Kontext die Auswahl des
Vervollstaendigungsziels aendert. Eine einfache Paarzuordnung, lineare
Hinweisverstaerkung oder adaptive Einzelprototypverschiebung stoppt den Zweig.

## Funktionsanatomie

CBPC-1 besitzt drei technische Eingangsrollen:

- `context`: ein stabilisierter, verdichteter PPB-1-Zustand ohne Label;
- `partial_cue`: eine gebundene Teilprojektion eines auditiven oder visuellen
  Prototyps mit expliziter Fehlstellenmaske;
- `target`: ein bereits in den begrenzten Inhaltsbanken vorhandenes
  auditiv-visuelles Prototyppaar.

Eine private Relationsbank darf ausschliesslich technische
Prototypidentitaeten und begrenzte Auditmetadaten verbinden. Sie speichert
keine Audio- oder Bildrohdaten, Woerter, Objektklassen, semantischen Labels
oder vollstaendige Expositionshistorien.

Der spaetere Abruf ist read-only. Er darf hoechstens einen
Vervollstaendigungsvorschlag aus bereits vorhandenen verdichteten
Prototypwerten, eine Konfidenzrolle und ein Receipt zurueckgeben. Inhaltsbank,
Relationsbank, Feldzustand und Eingabe bleiben unveraendert.

## Endliches Speicherbudget

Der erste pruefbare Korridor ist fest begrenzt auf:

- zwei getrennte PPB-1-Inhaltsbanken mit jeweils hoechstens drei belegten
  Prototypslots;
- genau vier private Relationsslots;
- je Relationsslot genau eine Kontextidentitaet, eine Hinweisidentitaet,
  eine auditive Zielidentitaet, eine visuelle Zielidentitaet sowie feste
  Support-, Konflikt- und Reihenfolgerollen;
- keine Rohhistorie und keine zusaetzlichen verdeckten Vektoren in der
  Relationsbank.

Das funktionale Speicherbudget umfasst alle gespeicherten Prototypwerte,
Identitaeten, Relationsindizes, Masken und entscheidungswirksamen Zaehler.
Auditdigests werden separat berichtet, duerfen aber keine funktionale
Information tragen.

Jede Baseline erhaelt hoechstens dieselbe Gesamtzahl funktionaler Bits. Kann
das Budget vor einer Materialisierung nicht fuer alle Arme eindeutig und
gleich bilanziert werden, ist der Vergleich methodisch ungueltig.

## Balancierte Gegenprognose

Die kleinste relationale Fixture besitzt zwei Kontexte `C0/C1`, zwei
Teilhinweisquellen `Q0/Q1` und zwei audiovisuelle Ziele `T0/T1`. Die vier
Bildungsbeziehungen sind balanciert:

```text
C0 + Q0 -> T0
C1 + Q0 -> T1
C0 + Q1 -> T1
C1 + Q1 -> T0
```

`C0/C1`, `Q0/Q1` und `T0/T1` treten jeweils gleich oft auf. Kandidat und
Baselines sehen dieselben reduzierten Eingaben in derselben Reihenfolge.
Rollenbezeichner dienen nur der Fixturepruefung und duerfen keinem
Kandidaten- oder Baselineconsumer als Labels uebergeben werden.

Die zentrale Gegenprognose lautet:

> Bei gleichen marginalen Prototypinventaren, Haeufigkeiten und
> Einzelabstaenden liefert derselbe Teilhinweis mit `C0` ein anderes korrektes
> Ziel als mit `C1`, weil nur die gebundene Relationsstruktur verschieden ist.

Eine Baseline, die Kontext und Hinweis nachtraeglich zu einem neuen
Schluessellabel verbindet, muss diesen zusaetzlichen Speicher vollstaendig
bilanzieren und gilt als gemeinsame beziehungsweise assoziative Baseline.

## Verpflichtende Prueffamilien

### F1: Vollstaendiger Kontrollhinweis

Alle vier Beziehungen werden mit vollstaendig sichtbarem Hinweis geprueft.
Dieser Arm kontrolliert Quellen, Zielinventar und prinzipielle Lesbarkeit,
ist aber kein Vervollstaendigungsbefund.

### F2: Gebundener Teilhinweis

Je Hinweis bleibt exakt die Haelfte der Traegerwerte sichtbar; die andere
Haelfte ist durch eine explizite Fehlstellenmaske unbekannt und darf nicht als
Nullwert fehlinterpretiert werden. Alle vier Kontext-Hinweis-Kombinationen
muessen das vorregistrierte Ziel liefern.

### F3: Begrenztes Rauschen

Die sichtbare Hinweisprojektion wird durch eine vor Materialisierung
gebundene, budgetgleiche Stoerung veraendert. Zielauswahl und Fehlstellenmaske
bleiben getrennt messbar. Ein staerkerer oder anders verteilter Stoerarm darf
nicht nach Beobachtung ausgewaehlt werden.

### F4: Kontexttausch und Negativkontrolle

Bei identischem Teilhinweis wird nur der Kontext getauscht. Das Ziel muss
gemaess der balancierten Tafel wechseln. Ein unbekannter oder unvollstaendiger
Kontext muss einen expliziten `NO_COMPLETION`-Befund liefern, nicht das
haeufigste oder naechste Ziel.

### F5: Interferenz

Nach gueltiger Bildung wird eine konkurrierende Zuordnung fuer eine bereits
belegte Kontext-Hinweis-Kombination angeboten. Vor der Implementierung muss
genau eine Politik gebunden werden: expliziter Konflikt ohne Vervollstaendigung
oder deterministisch bilanzierte Aktualisierung. Stille Mittelung oder ein
unregistrierter Zielwechsel ist Fehlverhalten.

### F6: Kapazitaetsdruck

Nach vier belegten Relationsslots wird genau eine neue, nicht kollidierende
Beziehung angeboten. Opferrolle, Erhaltungsrollen und Ergebnis nach
Freigabe muessen vorab feststehen. Ueberkapazitaet, Doppelbelegung oder
nichtdeterministischer Gleichstand sind ungueltig.

### F7: Relationsablation

Bei unveraenderten Inhaltsbanken, Prototypabstaenden und Teilhinweisen wird
nur die Relationsbank entfernt. Die kontextabhaengige Zieldifferenz muss
verschwinden. Bleibt sie bestehen, stammt die Wirkung nicht aus der
gebundenen Relationsstruktur.

## Messgroessen

Getrennt zu berichten sind:

- exakte Zielidentitaetsentscheidung je Kontext-Hinweis-Paar;
- normalisierte Distanz des ausgegebenen verdichteten Zielvektors zum
  vorregistrierten Ziel;
- Abdeckung der maskierten Traegerwerte;
- Kontextselektivitaet zwischen passendem und getauschtem Kontext;
- falsche Vervollstaendigung und `NO_COMPLETION`-Rate;
- Konfliktstatus und stille Fehlzuordnung unter Interferenz;
- belegte Slots, Opferidentitaet und Erhaltung unter Kapazitaetsdruck;
- Unveraenderlichkeit aller Inhalts- und Relationszustaende waehrend Abruf;
- funktionale Speicherbits und Eingabe-/Probebudget je Arm.

Ein Ergebnisdigest, eine geaenderte Slotzahl oder eine andere technische
Identitaet ist keine Erfolgsmetrik.

## Faire Gegenbaselines

Alle Baselines erhalten dieselben Bildungs- und Probeinhalte, Reihenfolgen,
Masken, Stoerungen, Kapazitaets- und funktionalen Bitbudgets.

1. `No-Memory`: kein fortgesetzter Zustand und nur direkter Teilhinweis.
2. `Budget-Replay`: reduzierte gemeinsame Expositionen, jedoch keine Rohdaten
   und nur so viele vollstaendige Eintraege, wie in dasselbe Bitbudget passen.
3. `Static-Prototype`: nach Bildung eingefrorene getrennte Prototypbanken.
4. `AOPB-Independent`: kapazitaetsgleiche adaptive auditive und visuelle
   Einzelprototypbanken ohne Relationszustand.
5. `AOPB-Joint`: staerkste adaptive Online-Prototypbaseline; sie darf
   gemeinsame Kontext-Hinweis-Ziel-Prototypen bilden, muss deren gesamten
   gemeinsamen Vektor- und Indexspeicher aber im selben Bitbudget fuehren.
6. `AVPC-1`: vorhandene begrenzte Paarzuordnung ohne getrennte Kontextrolle.
7. `BAM-1`: begrenzte assoziative Key-Value- beziehungsweise
   Attraktorbaseline mit gleicher Inhaltsinformation, Relationskapazitaet und
   demselben read-only Ausgabeformat.

`BAM-1` ist die staerkste funktionale Gegenbaseline. Wird CBPC-1 nur gegen
Einzelprototypbanken besser, aber durch `AOPB-Joint`, Budget-Replay oder
`BAM-1` reproduziert, ist die technische Vervollstaendigungsfunktion generisch
erklaert.

## Erfolgs-, Stopp- und Ungueltigkeitsregeln

CBPC-1 besteht die technische Funktion nur, wenn alle F1- bis F7-Arme aus
getrennten Frischzustaenden vollstaendig sind, alle vier F2-Ziele korrekt
sind, unbekannte Kontexte keine falsche Vervollstaendigung erzeugen,
Interferenz und Kapazitaet die vorregistrierten Rollen einhalten, die
Relationsablation die Kontextselektivitaet entfernt und keine read-only Probe
Zustand veraendert.

Der Forschungszweig wird gestoppt, wenn:

- E1-artige lineare Teilhinweisskalierung die Ausgabe erklaert;
- AVPC-1 oder eine Paarzuordnung ohne getrennten Kontext alle Pflichtarme
  reproduziert;
- eine budgetgleiche adaptive gemeinsame Prototypbank alle Pflichtarme
  reproduziert;
- Budget-Replay oder BAM-1 die Gesamtfunktion reproduziert;
- der Vorteil aus mehr Speicherbits, mehr Expositionen, zusaetzlichen Proben,
  Labels oder Rohhistorie entsteht;
- keine eindeutige Interferenz- oder Kapazitaetspolitik materialisierbar ist.

Der Vergleich ist methodisch ungueltig bei ungleichen Eingaben, Masken,
Stoerungen, Reihenfolgen, funktionalen Bitbudgets oder Probeanzahlen, bei
Rollenlabels im Consumer, Carry zwischen Geschichten, Teilreceipts, Retry
oder nachtraeglich geaenderten Sollausgaben.

Die spaetere Entscheidungsmenge ist vollstaendig:

```text
METHOD_INVALID
TECHNICAL_COMPLETION_FUNCTION_FAILED
FUNCTION_VALID_BASELINE_EXPLAINS
FUNCTION_VALID_ASSOCIATIVE_REST
```

Auch `FUNCTION_VALID_ASSOCIATIVE_REST` waere zunaechst nur ein begrenzter
technischer Gegenbaselinebefund. Er belegt keine MCM-spezifische Memory-
Mechanik und keine Feldwirkung.

## Freigabegrenze und naechster Schritt

Nicht freigegeben sind Gleichung, Parameter, Fixturewerte, Implementierung,
Tests, Runner, API, Snapshot, Produktion, Live-Sensorik, Feldintegration und
Semantik.

S2-DA darf ausschliesslich statisch Vollstaendigkeit, Nichtduplikation,
Bitbudgetfairness und eindeutige Materialisierbarkeit dieses Vertrags
pruefen. Insbesondere muss geklaert werden, ob `AOPB-Joint`, Budget-Replay
oder `BAM-1` die Gegenprognose bereits konstruktiv schliessen. Erst ein
bestandener S2-DA-Audit duerfte eine Materialisierung vorbereiten.
