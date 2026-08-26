# S2-CQ: Privater gekreuzter AVPC-1-End-to-End-Vertrag

## Vertragsziel

S2-CQ bindet genau einen privaten synthetischen Evaluationsablauf fuer die
bereits geschlossene AVPC-1-Engineeringkomposition. Der Ablauf soll spaeter
pruefen, ob authentisch gebildete, eingefrorene auditive und visuelle
Prototypzustaende ueber eindeutig ueberlappende Expositionen relationiert und
nach einer Luecke durch eine rein auditive Probe kontrolliert gelesen werden
koennen.

Der Vertrag fuegt keine Speicher-, Distanz-, Match-, Support-, Kapazitaets-,
Konflikt- oder Ersetzungsregel hinzu. Er bindet ausschliesslich vorhandene
private Funktionen in einer festen Kausalfolge.

## Quellen und Eigentumsgrenze

Eine spaetere Evaluationsinstanz muss vor dem ersten Kindaufruf alle Profile,
Rezeptorquellen, Bildungsumschlaege, Expositionsumschlaege, Probenquellen,
Initialzustaende, Relationstabellen-IDs, Owner- und Verbrauchs-IDs sowie den
Baselineumfang per Digest autorisieren.

Alle Kindowner und Zwischenresultate bleiben innerhalb der privaten
Evaluationsinstanz. Nach aussen darf erst ein vollstaendiger unveraenderlicher
Gesamtbeleg erscheinen. Ein Fehler in einer beliebigen Phase beendet die
Instanz terminal, ohne Zwischenzustand, Teilergebnis, Retry oder Reparatur
freizugeben.

## Gebundene Kausalfolge

### P0: Gemeinsame Inhaltsbildung

Genau ein authentisches PPB-1-Bildungsergebnis bildet zwei getrennte stabile
auditive und zwei getrennte stabile visuelle Prototypidentitaeten. Dasselbe
Formationsergebnis mit denselben Bankidentitaets- und Zustandsdigests ist die
unveraenderliche Inhaltsquelle fuer `H_LEFT`, `H_RIGHT` und alle fairen
Baselines. Rollenbezeichnungen dienen nur der synthetischen Fixturebindung.

### P1: Einfrieren

Nach P0 werden Profil, auditive Bank und visuelle Bank eingefroren. Von P1
bis zum Abschluss darf keine PPB-1-Zustandsfortschreibung, Stabilisierung,
Abschwaechung, Ersetzung oder Ablaufveraenderung erfolgen.

### P2: Gekreuzte Relationsexposition

Jede Geschichte besitzt vier zeitlich geordnete, positive und vollstaendig
eindeutige audiovisuelle Ueberlappungen:

```text
H_LEFT:  A_KEY-V_LEFT,  B_CONTROL-V_RIGHT,
         A_KEY-V_LEFT,  B_CONTROL-V_RIGHT

H_RIGHT: A_KEY-V_RIGHT, B_CONTROL-V_LEFT,
         A_KEY-V_RIGHT, B_CONTROL-V_LEFT
```

Jeder Beleg wird genau einmal von einem eigenen atomaren
Relationsbildungs-Owner verbraucht. Die vorhandene Relationskapazitaet zwei,
die Bestaetigungsgrenze zwei und das Expositionsbudget vier bleiben
unveraendert. Die erwartete Ereignisfolge je Geschichte lautet zweimal
`PAIR_CREATED_PENDING`, danach fuer dieselben beiden Schluessel jeweils
`PAIR_CONFIRMED_STABLE` in der gebundenen Eingabereihenfolge.

### P3: Luecke

Die Luecke besitzt keine audiovisuelle Exposition, keinen Bankaufruf, keine
Relationsfortschreibung und keinen Abruf. Sie wird ausschliesslich durch eine
vorab gebundene kausale Zeitgrenze zwischen dem letzten Relationsfenster und
der spaeteren Probe repraesentiert.

### P4: Spaetere auditive Probe

Jede Probe liegt auf Quell- und Feldzeit nach allen gebundenen
Relationsexpositionen. Sie enthaelt genau einen auditiven und null visuelle
Inputs. Zulaessige Kernproben sind `A_KEY` und `B_CONTROL`; jede Probe beginnt
vom selben eingefrorenen Inhaltszustand und demselben abgeschlossenen
Relationszustand ihrer Geschichte und bleibt read-only.

### P5: Atomarer Abruf

Der vorhandene atomare Leseconsumer wird pro Kernprobe genau einmal
aufgerufen. Erwartet werden:

```text
H_LEFT  + A_KEY       -> V_LEFT
H_LEFT  + B_CONTROL   -> V_RIGHT
H_RIGHT + A_KEY       -> V_RIGHT
H_RIGHT + B_CONTROL   -> V_LEFT
```

Vor- und Nachdigests aller Inhalts- und Relationszustaende muessen identisch
bleiben. Negative unbekannte oder konfliktbehaftete Schluessel duerfen nur in
separat gebundenen Kontrollzellen mit passender erreichbarer Vorgeschichte
geprueft werden; sie duerfen die vier Kernzellen nicht nachtraeglich aendern.

## Faire Gegenbaseline

Die staerkste Baseline ist eine getrennt identifizierte, aber funktional
gleiche kapazitaetsbegrenzte generische heteroassoziative Prototyptabelle. Sie
erhaelt dieselben eingefrorenen Inhaltszustaende, dieselben vier
Expositionsbelege, dieselbe Reihenfolge, Kapazitaet, Bestaetigungsgrenze,
Expositionsgrenze, Luecke und dieselben spaeteren Proben.

Da Tabellen- und Owner-IDs absichtlich getrennt sind, duerfen rohe
Zustandsdigests nicht als Gleichheits- oder Vorteilsmass dienen. Der
Comparator verwendet ausschliesslich eine vorab definierte funktionale
Projektion aus Ereignisrolle, Slotstatus, auditiver Prototypidentitaet,
visueller Zielidentitaet, Supportrolle, Konfliktrolle und Abrufausgabe.

No-Association, getrennte Prototypbanken und letzter visueller Kontakt bleiben
zusaetzliche schwache Kontrollen. Replay wird getrennt als Kontrolle mit
hoeherem Informationsbudget ausgewiesen.

## Entscheidungsreihenfolge

1. `METHOD_INVALID`, sobald eine Quellen-, Kausal-, Einmaligkeits-,
   Zustands-, Budget- oder Comparatorbindung verletzt ist.
2. `TECHNICAL_FUNCTION_FAILED`, wenn eine gueltige Kernzelle nicht die
   vorregistrierte Ausgabe liefert.
3. `FUNCTION_VALID_BASELINE_EXPLAINS`, wenn Kandidat und staerkste Baseline
   dieselbe funktionale Projektion liefern.
4. `FUNCTION_VALID_BASELINE_DIFFERS_REQUIRES_SEPARATE_AUDIT` nur bei einer
   vorab messbaren Differenz; daraus folgt noch keine besondere Mechanik.

Die bereits gebundene Gleichheit des Relationskerns macht
`FUNCTION_VALID_BASELINE_EXPLAINS` zur fachlich erwarteten Einordnung. Ein
anderes Ergebnis waere zuerst als Integrations- oder Fairnessabweichung zu
auditieren.

## Fail-Closed- und Stoppregeln

Der Gesamtversuch ist ungueltig bei ungleichen Inhaltszustaenden, geaenderter
Phasenfolge, nicht eindeutiger Ueberlappung, wiederverwendetem Beleg oder
Owner, visueller Eingabe waehrend der spaeteren Probe, Zustandsaenderung im
Read-only-Abschnitt, ungleichem Budget, nachtraeglicher Comparatoraenderung,
Kindfehler oder digestkonsistenter falscher Kindausgabe.

Es gibt keinen Teilerfolg. Ein Fehler stoppt die gesamte Evaluationsinstanz.
Oeffentliche API, `SharedMCMField`, Snapshot, Produktion, Livepfade, Semantik
und Feldrueckwirkung bleiben ausgeschlossen.

## Einordnung und naechster Schritt

S2-CQ beschreibt einen technischen Funktions- und Integrationsvertrag. Selbst
ein vollstaendig erfolgreicher spaeterer Ablauf waere kein Nachweis einer
MCM-spezifischen Memory-Mechanik, sondern zunaechst die kontrollierte Funktion
einer generisch erklaerbaren perzeptiven Assoziationskomponente.

S2-CR soll rein statisch pruefen, ob dieser Vertrag mit den vorhandenen
privaten Typen und Funktionen eindeutig materialisierbar ist. Implementierung,
Tests, Runner und jede Zustands- oder Feldausfuehrung bleiben bis dahin
gesperrt.
