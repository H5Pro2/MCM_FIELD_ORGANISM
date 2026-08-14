# Zwei gekoppelte MCM-Substratrollen im gemeinsamen Feld

## Status

```text
Vertragstyp:                       darstellungsoffene Funktionsgrenze
gemeinsames MCM-Feld:              verbindlich eins
schnelle Wahrnehmungsrolle:        technisch vorhanden
langsame Entwicklungsrolle:        funktional offen
digitale Darstellung:              nicht gewaehlt
Kopplungsgleichung:                nicht gewaehlt
zweite Runtime oder zweites Feld:  ausgeschlossen
Implementierung:                   nein
```

## Architekturentscheidung

Das Projekt behaelt genau ein gemeinsames MCM-Feld und eine gemeinsame
Organismusgrenze:

```text
Audio-/Video-/Browserwelt
-> Rezeptoren
-> offene MCM-Docks
-> gemeinsame MCM-Neuronenschicht
-> ein gemeinsamer MCM-Feldzustand
```

Innerhalb dieses Feldes werden zwei **Funktionsrollen** unterschieden:

```text
schnelle MCM-Wahrnehmungsdynamik
<-> langsameres MCM-Entwicklungssubstrat
```

Die Rollen sind noch keine zwei Variablen, Schichten oder Netzwerke. Sie
bezeichnen zwei notwendige kausale Zeitskalen derselben Feldentwicklung.

## Rolle S: schnelle MCM-Wahrnehmungsdynamik

Die schnelle Rolle ist technisch vorhanden. Sie traegt:

- aktuellen lokalen Rezeptorkontakt;
- gemeinsame audiovisuelle Feldueberlagerung;
- lokale Feldweiterleitung;
- Aktivierung und schnellen Nachhall;
- atomare zeitliche Reihenfolge;
- gegenwaertige und kurz vorhergehende Feldlage.

Ihre Funktion ist:

```text
gegenwaertige Weltteilnahme
-> gegenwaertige gemeinsame Feldform
```

Sie ist kein langfristiger Geschichtstraeger. Nach Angleichung von Aktivierung
und Nachhall bleibt in der heutigen Runtime keine zusaetzliche Wirkung.

## Rolle L: langsameres MCM-Entwicklungssubstrat

Die langsame Rolle ist nur funktional bestimmt. Sie muesste:

- durch reale lokale Teilnahme der schnellen Feldentwicklung veraendert
  werden;
- waehrend weiterer Weltteilnahme kontinuierlich mitentwickeln;
- spaetere schnelle Feldaufnahme oder Weiterleitung lokal mitpraegen;
- ueber schnellen Nachhall hinausreichen;
- durch weitere Feldgeschichte vollstaendig funktionslos werden koennen;
- danach unter derselben Naturbedingung anders praegbar bleiben.

Ihre Funktion ist:

```text
lokale Feldgeschichte
-> veraenderte langsame Entwicklungsbedingung
-> veraenderte spaetere schnelle Feldentwicklung
```

Die langsame Rolle speichert keine Bilder, Sequenzen, Objekte, Woerter,
Labels, Rangzyklen oder Episoden.

## Warum Rolle L nicht nur langsamer Nachhall sein darf

Eine zweite Zeitkonstante oder eine Kaskade fester Zeitkonstanten erzeugt:

```text
gleiche Evidenz
-> exponentiell gewichtete Vergangenheit
-> fester Leser
```

Das ist eine physisch brauchbare Baseline, aber noch kein
Entwicklungssubstrat. Rolle L benoetigt eine Funktion oberhalb solcher Spuren:

1. Identische neue Feldgeschichte muss je nach realer Vorgeschichte eine
   unterschiedliche **weitere langsame Entwicklung** erzeugen.
2. Der Unterschied muss bereits vor einer spaeteren Probe im vollstaendigen
   kausalen Zustand liegen.
3. Neue konkurrierende Feldgeschichte muss die alte Funktion nicht nur
   abschwaechen, sondern vollstaendig irrelevant machen koennen.
4. Nach dieser Loesung muss dieselbe lokale Entwicklungsfaehigkeit eine andere
   Geschichte tragen koennen.

Wenn mehrere Leaky-Spuren mit gleichem Budget alle vier Punkte reproduzieren,
ist Rolle L nicht eigenstaendig getragen.

## Warum Rolle L keine zweite Runtime sein darf

Ein separates langsames Netzwerk wuerde eine neue Architektur mit eigener
Anatomie, eigenen Eingaben und einer nachgeschalteten Leserbruecke erzeugen.
Das widerspricht dem Ein-Feld-Prinzip.

Zulaessig ist nur:

- dieselbe gemeinsame Feldgeometrie oder eine noch darstellungsoffene lokale
  Zugehoerigkeit zu ihr;
- dieselbe atomare Kausalgrenze;
- lokale Kopplung ohne globale Zuordnung;
- ein gemeinsamer vollstaendiger Organismuszustand;
- ein gemeinsamer Snapshot und eine gemeinsame Fortsetzung.

Nicht zulaessig sind:

- ein zweites sensorisches Feld;
- ein separates Memory-Netz hinter dem MCM-Feld;
- ein Encoder-Decoder zwischen beiden Rollen;
- eine Datenbankabfrage;
- ein globaler Cross-Attention- oder Routingmechanismus;
- eine LLM- oder Embeddingbruecke.

## Reziproke Kopplungsgrenze

Beide Richtungen muessen kausal real sein.

### S nach L: Entwicklungsursache

```text
abgeschlossene schnelle lokale Feldteilnahme
+ abgeschlossener langsamer Vorzustand
-> naechster langsamer Zustandsvorschlag
```

Die konkrete Schreibursache bleibt offen. Nicht automatisch zulaessig sind
Aktivitaetssumme, Energie, Produkt, Flussbetrag, Rangwechsel oder
Wiederholungszahl.

### L nach S: innerer Kontext

```text
abgeschlossener langsamer lokaler Zustand
+ gegenwaertiger Weltkontakt
+ schnelles lokales Vorfeld
-> naechste schnelle Feldentwicklung
```

Die Wirkung muss waehrend der Feldtransition entstehen. Ein nachgeschalteter
Observer oder Leserwert reicht nicht.

### Atomare Ordnung

Alle schnellen und langsamen Vorschlaege lesen denselben vollstaendig
abgeschlossenen gemeinsamen Vorzustand. Keine neu berechnete Rolle darf im
selben atomaren Schritt erneut als eigene Ursache gelesen werden.

## Relative Feldzeit zwischen den Rollen

Die Rollen erhalten keine getrennten Uhren.

```text
Organismuszeit
= technische Kausal- und Dauerbasis

relative Feldzeit
= innere Reihenfolge tatsaechlicher gekoppelter Zustandsentwicklung
```

Relative Feldzeit waere funktional sichtbar, wenn:

- gleiche Weltzeit nach unterschiedlicher gekoppelter Entwicklung eine andere
  spaetere Feldfortsetzung besitzt;
- unterschiedliche Weltzeit bei kausal entsprechender Entwicklung nach
  Zeitabbildung funktional entsprechen kann;
- technische Segmentdichte und Aufrufzahl keine eigene Wirkung erzeugen;
- Pausen ohne Feldteilnahme nicht automatisch dieselbe Entwicklung wie
  aktive Feldgeschichte erzeugen.

Die langsame Rolle darf deshalb weder mit Sekunden noch mit Tickzahl direkt
gleichgesetzt werden.

## Feldzeitverdichtung als spaetere Prueffunktion

Feldzeitverdichtung wird nicht als Zaehler oder Cluster implementiert. Sie ist
fruehestens dann ein Kandidat, wenn wiederkehrende Feldgeschichte zunehmend
dieselbe lokal entstandene Entwicklungsfaehigkeit beansprucht und dadurch die
spaetere Feldwirkung veraendert.

Notwendig sind:

- Wiederholung ohne Wiederholungszaehler;
- verwandte Verlaeufe ohne Runtime-Aehnlichkeitsmetrik;
- keine Cluster-ID oder gespeicherte Vorlage;
- Wirkungstausch mit dem langsamen Zustand;
- Loesung der alten Wirkung;
- andere Wiederpraegung derselben Faehigkeit.

## Kausale Minimalmatrix

Ein spaeterer Kandidat muss mindestens folgende Zweige tragen:

| Zweig | Langsame Vorgeschichte | Schneller Probeverlauf | Zweck |
|---|---|---|---|
| `N-P` | Nullgeschichte | P | heutige Grundantwort |
| `A-P` | Geschichte A | identisches P | moeglicher innerer Kontext |
| `B-P` | budgetgleiche Geschichte B | identisches P | Geschichtsspezifitaet |
| `A-B` | A, danach B | B waehrend Mitentwicklung | Bildung vor Leser |
| `swap` | L-Zustand zwischen A und B getauscht | identisches P | kausaler Traeger |
| `zero` | L-Wirkung neutralisiert | identisches P | Nullpfad |
| `S-equal` | schnelle Rollen angeglichen | identisches P | Trennung vom Nachhall |
| `solve` | konkurrierende Geschichte | alte Probe | funktionale Loesung |
| `rebind` | neue Geschichte nach Loesung | neue Probe | andere Wiederpraegung |

Die Probe muss als byteidentische reduzierte Rezeptorfolge oder durch einen
gleichwertig strengen Rezeptorzustandsnachweis fixiert sein. Der technisch
unentscheidbare Lauf 187 darf nicht als positive oder negative Evidenz
verwendet werden.

## Pflichtbaselines

Ein Kandidat muss bei gleichem Zustands-, Parameter-, Praezisions-, Radius-,
Zeitpraefix- und Leserbudget verglichen werden mit:

- heutigem schnellen Feld und Nachhall;
- einer und mehreren Leaky-Spuren;
- viskoelastischer Relaxationskaskade;
- Produkt- und Momentenintegratoren;
- fester lokaler Rekurrenz;
- zweiter identischer langsamer Feldkopie;
- statischem adaptivem Gain;
- memristiver oder Duhem-Hysterese;
- konserviertem Phasenfeld mit festgelegter Energielandschaft;
- Sequenz-, Reservoir- und Interpolationsbaseline ausserhalb der Runtime.

Das Scheitern aller Baselines beweist noch kein Memory. Es entfernt nur
bekannte einfachere Erklaerungen.

## Zulaessige feste Naturbedingungen

Fest vorgegeben werden duerfen:

- Lokalitaet und endlicher Radius;
- atomare Kausalitaet;
- gleiche Regel an gleichartigen Orten;
- endliche Wertebereiche und Rechenressourcen;
- reale Organismusdauer;
- Nullzustand und exakte heutige Nullruntime;
- Snapshotfaehigkeit;
- Observerpassivitaet;
- geometrische Aequivarianz.

Diese Bedingungen definieren die digitale Naturgrenze, nicht die entstehende
Organisation.

## Verbotene Vorprogrammierung

Nicht festgelegt werden duerfen:

- welche Geschichte wichtig ist;
- welche Orte oder Modalitaeten sich binden;
- wie viele Wiederholungen genuegen;
- welche langsame Form stabil bleibt;
- wann vergessen werden soll;
- welche Probe richtig beantwortet wird;
- Objekt-, Wort-, Partner-, Episoden- oder Clusteridentitaet;
- Zieltopologie, Reward, Fehlerfunktion oder Gewinner;
- Wenn-X-dann-Y-Regeln als Organismusfunktion.

## Zulassungsfragen fuer eine konkrete Naturhypothese

Vor jeder Implementierung muss ein Kandidat beantworten:

1. Welche lokale Rolle veraendert sich langsam?
2. Warum ist sie MCM-Substrat und kein separates Memory-Modul?
3. Welche schnelle lokale Feldteilnahme veraendert sie?
4. Wie wirkt sie atomar auf dieselbe gemeinsame Feldentwicklung zurueck?
5. Weshalb ist ihre Wirkung nicht faktorisiert in Spur plus festen Leser?
6. Wodurch entsteht vollstaendige Funktionslosigkeit ohne Loeschregel?
7. Wodurch bleibt danach andere Wiederpraegung moeglich?
8. Welche Baseline ist ihr staerkstes gleich budgetiertes Gegenmodell?
9. Welche konkrete Beobachtung wuerde die Hypothese sofort verwerfen?

Ohne vollstaendige Antworten bleibt die Runtime geschlossen.

## Forschungsentscheidung

Der Zwei-MCM-Substratrollen-Weg ist mit der Ein-Feld-Architektur vereinbar und
entspricht der neuen manuellen Forschungsrichtung. Er loest das
konstitutive Problem noch nicht: Auch eine langsame MCM-Rolle benoetigt eine
transparent begruendete Naturhypothese.

Der Vertrag verhindert aber drei Fehlrichtungen:

```text
kein zweites Organismusfeld
kein langsames Leaky-Memory unter neuem Namen
keine nachgeschaltete Datenbank- oder Leserbruecke
```

## Bester naechster Schritt

Der [Vergleich der Kopplungsfamilien S <-> L](VERGLEICH_MCM_KOPPLUNGSFAMILIEN_S_L.md)
ist abgeschlossen. Aufnahme, Weiterleitung und Kapazitaet sind Wirkungsorte,
aber keine eigenstaendigen Entstehungsprinzipien. Nur die gemeinsame lokale
Mitentwicklung bleibt als korrekte Oberklasse offen; auch sie benoetigt vor
jeder Implementierung eine bewusst deklarierte minimale Naturannahme.

Diese Naturannahme ist als S0 des
[Richtungsentscheids `Substrat vor Memorybefund`](RICHTUNGSENTSCHEID_SUBSTRAT_VOR_MEMORYBEFUND.md)
im [Funktions- und Ressourcenvertrag der langsamen Substratrolle L](S0_FUNKTIONS_UND_RESSOURCENVERTRAG_LANGSAME_SUBSTRATROLLE_L.md)
gebunden. S1-A bindet inzwischen die kapazitaetsgewichtete reziproke
S-L-Akkommodation als lineare B2-Referenzgleichung; S1-B implementiert sie als
opt-in Pfad. S2-A ist inzwischen als Referenzcharakterisierung
vorregistriert, S2-B bindet den technischen Runnervertrag und der S2-C-Kern
ist implementiert. S2-C2 bis S2-C8 binden Einzelbatch, r1.a/c1.a,
S/H-Angleichung, Probe P, N8, Observer, Einpaardistanzen und D_pair(1);
S2-C9 bis S2-C16 binden A/B-Pfade, Container, Observermetrik und kanonische
End-to-End-Komposition. Der S2-Zwischenentscheid verweist als naechsten
Schritt auf den statischen S1-C-Kandidatenvertrag. Die Mechanik darf keinen
gewuenschten Memory-Erfolg, keine Clusterbildung und keine Bedeutung als
Ergebnis vorprogrammieren.
