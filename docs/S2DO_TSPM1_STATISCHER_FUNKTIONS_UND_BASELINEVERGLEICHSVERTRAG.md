# S2-DO: Statischer TSPM-1-Funktions- und Baselinevergleichsvertrag

## Auftrag und Grenze

S2-DO bindet ausschliesslich den spaeteren technischen Funktionsvergleich
der privaten Zwei-Zeitskalen-Architektur `TSPM-1`. Verglichen werden schnelle
Aufnahme, begrenzte Haltedauer, Konsolidierung, Verdraengung und read-only
Abruf unter identischen Eingabe-, Zustands-, Schreib-, Zeit- und
Probebudgets.

Es wurde keine Vergleichsfunktion implementiert, keine Zustandsfunktion
aufgerufen und kein Test oder Runner ausgefuehrt. TSPM-1, PPB-1, API,
Snapshot, Feldpfad und Produktion bleiben unveraendert.

## Technische Prueffrage

Die gerichtete Prueffrage lautet:

> Erreicht TSPM-1 bei gleichem Gesamtbudget zugleich frueheren gueltigen
> Abruf neuer audiovisueller Zustaende und spaeteren gueltigen Abruf
> bestaetigter Zustaende nach Ablauf der schnellen Ebene, ohne mehr
> Fehlzuordnungen, unkontrollierte Konsolidierung oder unfaire
> Zusatzinformation als die staerkste einfache Baseline?

Ein Digestwechsel, eine belegte Slotzahl oder ein positiver Einzelabruf
genuegen nicht. Erfolg verlangt eine vorab gerichtete Kombination aus
schneller Aufnahme, selektiver Konsolidierung, Interferenzkontrolle und
spaeterem Abruf.

## Unveraenderter Kandidat

TSPM-1 wird exakt in der durch S2-DE bis S2-DN abgeschlossenen privaten Form
verwendet:

- gemeinsamer kurzlebiger Audio-/Video-Fast-Slot;
- vollstaendiger Match nur bei passender auditiver und visueller Komponente;
- `FAST_CREATED`, `FAST_UPDATED` oder `FAST_REPLACED`;
- Ablauf nach der gebundenen Expositionsgrenze;
- LRU-Ersatz bei voller Kapazitaet;
- Konsolidierung nur aus einem bestaetigten `FAST_UPDATED` und nur mit den
  aktuellen Originalframes;
- zwei unveraenderte PPB-1-Baenke als langsame Ebene;
- read-only Probe mit getrenntem Fast-, Audio-PPB- und Video-PPB-Befund;
- kein Replay, keine Feldrueckwirkung und keine Semantik.

Konfiguration, Gleichungen, Matchregeln und Prioritaeten duerfen fuer den
Vergleich nicht veraendert werden.

## Pflichtbaselines

### B0: No-Memory

B0 besitzt keinen fortgeschriebenen Zustand. Eine spaetere Probe kann nur
den aktuellen Probeinput validieren und muss ansonsten
`NO_COMPLETE_CONTEXT` liefern.

### B1: PPB-1 allein

B1 verwendet ausschliesslich zwei unveraenderte PPB-1-Baenke. Sie erhaelt
dieselben Originalframes und keine Fast-Slotinformation. Zwei Varianten sind
vorab getrennt auszuweisen:

- `PPB_DIRECT`: jeder gueltige Originalframe wird genau einmal angeboten;
- `PPB_BUDGET_MATCHED`: nur eine vorregistrierte, kandidatenunabhaengige
  Teilmenge darf bis zur gleichen langsamen Schreibzahl wie TSPM-1 gelangen.

Die direkte Variante ist die staerkere Funktionsbaseline; die
budgetangepasste Variante isoliert den Einfluss zusaetzlicher Schreibarbeit.

### B2: Gemeinsame adaptive Online-Prototypbank

B2 besitzt gemeinsame audiovisuelle Prototypen mit einer homogenen
Match-, Update-, Ablauf- und Ersatzregel. Sie darf das gesamte
TSPM-1-Zustandsbudget verwenden, aber keine getrennte schnelle und langsame
Lebensdauer, kein Replay und keine TSPM-1-Ergebnisrollen nachbilden.

### B3: Nachhall

B3 traegt genau einen begrenzten gleitenden Audio-/Video-Zustand mit
homogener Abschwaechung. Sie darf keine diskreten Prototypen, keine
Konsolidierung und keine alte Eingabefolge speichern. Der Abruf verwendet
nur den gegenwaertigen Nachhallzustand und dieselbe Distanzmetrik.

### B4: Kurzfristiger Zustand

B4 ist ein endlicher FIFO- oder Ringzustand der zuletzt akzeptierten
verdichteten Audio-/Video-Eingaben. Kapazitaet und Bitbudget duerfen TSPM-1
nicht ueberschreiten. Beim Ueberschreiben ist ein Zustand vollstaendig
verworfen; es gibt keine zweite Stabilisierungsebene und kein Replay in eine
weitere Bank.

### R0: Generische Zwei-Ebenen-Reduktionskontrolle

R0 darf dieselbe Fast-/Slow-Anatomie und dieselben Regeln wie TSPM-1 als
allgemeine technische Speicherkomposition abbilden. Reproduziert R0 den
Kandidaten, ist dies die erwartete Engineeringreduktion und sperrt jede
MCM-spezifische Interpretation. R0 ist keine zusaetzliche Erfolgsbaseline
fuer die Auswahl zwischen einfachen Architekturen, sondern die verbindliche
Claim-Grenze.

## Identische Budgets

Jeder gueltige Vergleich bindet vorab:

1. dieselben auditiven und visuellen Originalframes in derselben kausalen
   Reihenfolge;
2. dieselben Bildungs-, Gap-, Stoer- und Probezeitpunkte;
3. dieselbe Zahl sensorischer Expositionen und read-only Proben;
4. dasselbe Gesamtbudget fuer gespeicherte skalare Werte, Slotmetadaten und
   Zustandsdigests;
5. hoechstens dieselbe Zahl von Zustandsschreibvorgaengen und
   Distanzbewertungen wie TSPM-1;
6. dieselbe numerische Praezision und dieselben Eingabedimensionen;
7. dieselbe Parameterwahl- und Vorpruefmenge, getrennt von den spaeteren
   gehaltenen Vergleichsgeschichten;
8. frische, voneinander unabhaengige Anfangszustaende fuer jeden Arm und jede
   Geschichte.

Kann eine Baseline das TSPM-1-Gesamtbudget nicht vollstaendig nutzen, wird
der ungenutzte Rest dokumentiert und nicht TSPM-1 abgezogen. Benoetigt eine
Baseline mehr Ressourcen, ist der Arm methodisch ungueltig und darf nicht
zugunsten des Kandidaten gewertet werden.

## Endliche Pflichtgeschichten

Die spaetere Fixture muss mit symbolisch aus der gebundenen Konfiguration
abgeleiteten Grenzen arbeiten: Fast-Kapazitaet `K`,
Konsolidierungsgrenze `C` und Ablaufgrenze `E`. S2-DO legt keine neuen
Parameterwerte fest.

### H1: Schnelle Aufnahme

Ein neuer audiovisueller Zustand `A:X` erscheint einmal. Eine kausal spaetere
Probe erfolgt vor `C`. Gemessen werden erste positive Abruflage,
Fehlzuordnung und Zustandsschreibbudget.

### H2: Bestaetigung und Konsolidierung

`A:X` wird bis zur gebundenen Konsolidierungsgrenze wiederholt. Proben liegen
unmittelbar vor und nach der Grenze. Nur ein aktueller Originalframe darf
eine Konsolidierung ausloesen.

### H3: Haltedauer nach schnellem Ablauf

Nach erfolgreicher Bestaetigung folgen mindestens `E` nicht passende
Expositionen. Die Probe fuer `A:X` erfolgt erst, wenn der zugehoerige
Fast-Slot nachweislich nicht mehr verfuegbar ist. Ein positiver TSPM-1-Befund
muss dann aus beiden PPB-1-Baenken stammen.

### H4: Widerspruechliche Teilassoziation

Nach `A:X` folgen die Teilkombinationen `A:Y` und `B:X`. Geprueft wird, ob
die bestehende Paarbindung einseitig umgeschrieben, falsch konsolidiert oder
bei spaeteren getrennten Proben verwechselt wird.

### H5: Kapazitaetsdruck und Verdraengung

Es werden `K + 1` hinreichend getrennte audiovisuelle Zustaende angeboten.
Vorab festgelegte Auswahlzeitpunkte erzwingen einen eindeutigen LRU-Fall.
Geprueft werden vollstaendiger Ersatz, korrekter Verlust des verdraengten
Fast-Zustands und Fortbestand zuvor gueltig konsolidierter langsamer
Zustaende.

### H6: Transiente Stoerfolge

Ein bestaetigter Zustand wird von einer endlichen Folge einmaliger
Stoerzustaende umgeben. Der Vergleich trennt kurzfristige Verfuegbarkeit,
falsche Stabilisierung der Stoerer und spaeteren Abruf des bestaetigten
Zustands.

### H7: Negative und aehnliche Probe

Zu jedem positiven Abruf existieren eine hinreichend verschiedene
Negativprobe und eine nahe, aber ausserhalb mindestens einer gebundenen
Modalitaetsschwelle liegende Probe. Dadurch werden Treffer und
Fehlakzeptanz getrennt bewertet.

## Messgroessen

Fuer jeden Arm werden getrennt erfasst:

- `capture_latency`: Expositionen bis zum ersten gueltigen read-only Abruf;
- `early_recall`: Abruf vor der Konsolidierungsgrenze;
- `fast_retention`: letzter Abruf aus der schnellen Ebene;
- `post_expiry_recall`: Abruf nach nachgewiesenem Fast-Ablauf;
- `consolidation_precision`: Anteil bestaetigter statt einmaliger Zustaende
  in der langsamen Ebene;
- `false_consolidation_count`;
- `partial_conflict_error_count`;
- `eviction_correctness` und `evicted_state_false_recall`;
- positive, negative und nahe-Probe-Trefferraten;
- Zustands-, Schreib-, Distanz- und Probebudget;
- bitgleiche Vor-/Nachzustaende jeder read-only Probe.

Fast- und Slow-Abruf duerfen nicht zu einer gemeinsamen Erfolgszahl
verschmolzen werden. Ebenso duerfen Konsolidierungsstatus und positiver
PPB-1-Abruf nicht gleichgesetzt werden.

## Gerichtete Gegenprognose

TSPM-1 ist gegenueber den einfachen Baselines nur dann funktional weiter
begruendet, wenn es bei identischem Gesamtbudget gleichzeitig:

1. in H1 vor der langsamen Stabilisierung einen gueltigen gemeinsamen Abruf
   liefert;
2. in H3 nach sicherem Fast-Ablauf einen gueltigen langsamen Abruf liefert;
3. in H4 keine einseitige Teilassoziation als vollstaendige Paarbindung
   uebernimmt;
4. in H5 die gebundene schnelle LRU-Verdraengung korrekt ausfuehrt, ohne
   einen bestaetigten langsamen Zustand dadurch zu verlieren;
5. keine hoehere Fehlakzeptanz oder falsche Konsolidierung als die jeweils
   staerkste einfache Baseline erzeugt.

Eine Verbesserung nur in einer Geschichte, ein groesserer interner Zustand
oder eine andere Ergebnisbezeichnung ist kein Funktionsvorteil.

## Auswertungsreihenfolge

1. Quellen-, Konfigurations- und Budgetgleichheit pruefen.
2. Frische und Unabhaengigkeit aller Arme pruefen.
3. Negative und nahe Proben auswerten.
4. Atomaritaet und read-only Unveraenderlichkeit pruefen.
5. H1 bis H7 je Messgroesse auswerten.
6. TSPM-1 zuerst gegen die staerkste einfache Baseline vergleichen.
7. PPB-Direkt- und budgetangepasste Ergebnisse getrennt berichten.
8. R0 zuletzt ausschliesslich zur Engineering- und Claim-Einordnung nutzen.

## Falsifikation und Stopp

Der Vergleich lautet `METHOD_INVALID`, sobald Quellen, Kapazitaet,
Schreibarbeit, Proben, Parameterwahl oder Anfangszustaende nicht fair
gebunden sind.

TSPM-1 besitzt keinen begruendeten Funktionsvorteil, wenn eine der folgenden
Bedingungen eintritt:

- B1 oder B2 reproduziert die kombinierte H1-/H3-/H4-/H5-Prognose mit
  gleichem Budget;
- der spaete Abruf in H3 stammt noch aus einem Fast-Slot oder aus Replay;
- einmalige Stoerzustaende werden unkontrolliert konsolidiert;
- Teilassoziationskonflikte erzeugen falsche vollstaendige Bindungen;
- read-only Proben veraendern irgendeinen Zustand;
- der Vorteil verschwindet bei gleicher Kapazitaet oder gleicher
  Schreibzahl;
- ein Baselinefehler wird als Kandidatenerfolg gewertet.

In diesen Faellen lautet die Entscheidung
`FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS` oder bei einem Kandidatenfehler
`TSPM1_FUNCTION_NOT_VALID`.

Nur wenn alle gerichteten Bedingungen bei gueltigem Vergleich bestehen,
darf der technische Befund
`TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES` lauten.
Auch dann bleibt R0 die generische Erklaerung der Architektur.

## Entscheidung

`PASS_TSPM1_STATIC_FUNCTION_AND_BASELINE_COMPARISON_CONTRACT_BOUND`

S2-DO bindet eine endliche und falsifizierbare technische Vergleichsfrage.
Es belegt weder einen Funktionsvorteil noch eine eigenstaendige
MCM-Memory-Mechanik.

## Naechster Schritt

S2-DP darf nach separater Freigabe ausschliesslich die Materialisierbarkeit,
Budgetgleichheit, Nichtzirkularitaet und eindeutige Auswertbarkeit dieses
Vertrags statisch auditieren. Implementierung, Tests, Runner,
Zustandsaufrufe und Feldintegration bleiben bis zu einem bestandenen S2-DP
gesperrt.
