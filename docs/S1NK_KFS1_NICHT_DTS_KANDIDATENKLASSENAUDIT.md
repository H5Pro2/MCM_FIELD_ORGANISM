# S1-NK KFS-1-Nicht-DTS-Kandidatenklassenaudit

## Status

S1-NK auditiert die in S1-NJ gebundenen Klassen G1, G2 und G3 gegen das
Nicht-DTS-Mindestgate. Der Schritt waehlt hoechstens eine darstellungsoffene
Klasse. Er bindet keine konkrete Variable, Gleichung, Zahlenwerte, Runtime
oder Feldrueckwirkung.

Entscheidung:

```text
SELECT_G2_BOUNDED_LOCAL_CONFIGURATION_STATE_CLASS_ONLY
```

## Auditkriterien

Jede Klasse wird gegen dieselben sechs Bedingungen geprueft:

1. Ein kontrolliertes Interventionspaar mit identischem S/H und identischem
   vollstaendigem DTS-1-Ledger ist formulierbar.
2. Die eigene Prognose ist nicht aus DTS-1-Rollen oder geschalteten
   DTS-1-Transfers rekonstruierbar.
3. Der benoetigte Zustand ist lokal, endlich und ohne Rohdaten- oder
   Sequenzpuffer formulierbar.
4. Fixed Adapter, Leaky, Integrator, Replay und Readout bleiben als getrennte
   Gegenbaselines pruefbar.
5. Die Klasse fuegt nur die kleinste fuer eine eigene Prognose notwendige
   Struktur hinzu.
6. Labels, Reward, Zieltopologie, globale Normalisierung und Ergebniswissen
   sind keine Kausalquellen.

Ein Kandidatenname oder ein anderes Transfergesetz ersetzt keines dieser
Kriterien.

## G1: anderes atomares Transfernetz

### Audit

G1 kann eine andere atomare Verbindung zwischen `free`, `bound` und
`blocked` festlegen. Bei identischem vollstaendigem Vorzustand, identischer
Regel und identischer Probe folgt daraus jedoch weiterhin genau ein gleicher
Nachzustand. Ein Interventionspaar kann nur entstehen, wenn die Regelkennung
selbst zwischen den Armen gewechselt oder eine weitere getragene lokale Rolle
eingefuehrt wird.

Der Wechsel der Regelkennung waere ein externer Armparameter und keine
getragene lokale Ursache. Eine zusaetzliche Rolle waere bereits G2. Zudem
kann ein vereinfachter Transferpfad leicht auf Leck, Gain oder einen
refraktaerfreien Integrator kollabieren.

### Entscheidung

```text
STOP_G1_NO_INDEPENDENT_STATE_INTERVENTION
```

G1 bleibt als moegliche Dynamikeigenschaft eines spaeteren Kandidaten offen,
ist aber allein keine ausreichende Kandidatenklasse.

## G2: zusaetzliche endliche lokale Zustandskoordinate

### Audit

G2 kann zwei lokale Vorzustaende tragen, bei denen Geometrie, aktuelles S/H
und das vollstaendige `free/bound/blocked`-Ledger identisch sind, waehrend
eine weitere lokale Konfiguration verschieden bleibt. Unter derselben Probe
kann daraus eine gerichtete Differenz der zulaessigen lokalen Umordnung
prognostiziert werden.

Diese Klasse besteht das Mindestgate nur unter folgenden Sperren:

- Der Zustand ist endlich oder hart begrenzt.
- Er ist nicht aus aktuellem S/H, DTS-1-Ledger, Adapter oder deren Summen
  berechenbar.
- Er speichert keine Rohdaten, Ereignisliste, Sequenz oder Zeitreihe.
- Er wird nicht aus Labels, Reward, Zielwerten oder Readoutergebnissen
  geschrieben.
- Seine Ablation entfernt die eigene Prognose.
- Ein Leaky- oder Integratorarm mit derselben relevanten Vorgeschichte bleibt
  verpflichtende Gegenbaseline.

S1-NK benennt absichtlich weder physische Bedeutung noch Darstellung dieser
Koordinate. Begriffe wie `continuity`, `allocation`, Relationsalter,
Richtung oder Polaritaet werden nicht als fertige Zustandsrollen uebernommen.

### Entscheidung

```text
PASS_G2_TO_FUNCTION_AND_FALSIFICATION_CONTRACT
```

Das ist nur eine Klassenauswahl. Es ist kein Kandidaten-, Anatomie- oder
Funktionsbefund.

## G3: nicht faktorisierbare lokale Ressourcenverteilung

### Audit

Eine Verteilung ueber Kanten ist keine eigene Klasse, wenn ihre vollstaendigen
Anteile bereits als DTS-1-Kantenledger gespeichert sind. Dann kann DTS-1 die
spaetere Konkurrenz aus genau diesem Vorzustand berechnen.

Wird stattdessen eine zusaetzliche Beziehung zwischen Kanten benoetigt, die
nicht in den Einzelledgern oder dem gemeinsamen Knotenbudget enthalten ist,
ist diese Beziehung eine weitere lokale Zustandskoordinate. Der fachlich
pruefbare Rest von G3 faellt damit unter G2. Eine feste Nachbarschaftsliste,
Rangfolge oder globale Normalisierung waere unzulaessig.

### Entscheidung

```text
STOP_G3_AS_STANDALONE_RECLASSIFY_RELATIONAL_REMAINDER_TO_G2
```

G3 wird nicht parallel zu G2 weitergefuehrt.

## Ausgewaehlte Klasse

Der einzige weitergefuehrte Klassenraum lautet:

```text
G2_BOUNDED_LOCAL_CONFIGURATION_STATE
```

Gemeint ist ausschliesslich:

```text
eine minimale lokale, endliche und nicht aus S/H oder dem
free/bound/blocked-Ledger rekonstruierbare Konfigurationsrolle
```

Nicht ausgewaehlt sind:

- Name oder physische Interpretation der Rolle;
- Anzahl ihrer Komponenten;
- Wertebereich oder Einheit;
- Bildungs-, Abschwaechungs- oder Freigabegleichung;
- Einfluss auf Ressourcenledger oder Feld;
- Runtime- oder Speicherformat.

## Vorlaeufige Gegenprognose

Der spaetere Funktionsvertrag muss mindestens dieses Paar binden:

```text
Arm A und Arm B:
    gleiche Geometrie
    gleiches aktuelles S/H
    gleiches vollstaendiges free/bound/blocked-Ledger
    verschiedene gueltige lokale G2-Konfiguration

identische naechste lokale Probe
-> verschiedene vorab gerichtete lokale Umordnungsprognose
```

DTS-1, Fixed Adapter und zustandslose Baselines erhalten in beiden Armen
denselben fuer sie vollstaendigen Vorzustand. Zustandsbehaftete Leaky- und
Integratorbaselines muessen spaeter dieselbe relevante Bildungsgeschichte
sehen; sie duerfen nicht nur am Endreadout zugeschaltet werden.

## Verwerfungsbedingungen fuer den naechsten Vertrag

Die G2-Klasse wird vor jeder Anatomie verworfen, wenn:

- keine gerichtete Interventionsprognose ohne Gleichung formulierbar ist;
- die neue Rolle nur ein zweiter Name fuer S, H, `bound` oder `blocked` ist;
- ein skalarer Leaky- oder Integratorzustand die Prognose vollstaendig traegt;
- die Rolle nur aus gespeicherter Ereignisgeschichte gelesen werden kann;
- ihre Endlichkeit oder lokale Zugehoerigkeit nicht definierbar ist;
- die erwartete Differenz erst im Readout erzeugt wird;
- bereits zur Begriffsbildung eine Feldintegration erforderlich ist.

## Aussagegrenze

S1-NK waehlt nur eine darstellungsoffene Kandidatenklasse. Es gibt keine neue
Anatomie, keine Dynamik, keine Feldwirkung, keine Lernfunktion und keinen
Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NL darf ausschliesslich einen Funktions- und Falsifikationsvertrag fuer
`G2_BOUNDED_LOCAL_CONFIGURATION_STATE` binden. Zuerst muessen eigene
Interventionsprognose, Leaky-/Integratorgegenprognosen, Ablation und
Verwerfungsbedingungen feststehen.

S1-NL darf noch keine Zustandsdarstellung, Gleichung, Parameter, Runtime oder
Feldrueckwirkung waehlen.
