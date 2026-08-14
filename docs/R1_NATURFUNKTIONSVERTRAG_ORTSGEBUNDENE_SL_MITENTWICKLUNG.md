# R1-Naturfunktionsvertrag: ortsgebundene S-L-Mitentwicklung

## Status

```text
Vertragstyp:                       verbindliche funktionale Zulassungsgrenze
raeumlich mobile Komponente:       nur bestehendes S-Feld
L-Rolle:                           ortsgebundene interne Feldkonfiguration
unabhaengige Naturfunktion:        lokale konstitutive Akkommodation
mathematische Oberklasse:          Ein-Diffusor-Reaktions-Diffusion
konkrete Schliessung:              nicht gewaehlt
Implementierung:                   gesperrt
```

## Zweck

Der raeumliche Familienvergleich behaelt R1 als kleinste offene Familie:
S traegt den vorhandenen Feldfluss, waehrend L am Feldort bleibt und nur lokal
mit S mitentwickelt wird.

Dieser Vertrag bestimmt, welche unabhaengige physische Funktion L besitzen
muss, damit R1 nicht lediglich eine weitere Spur, ein Gain oder ein
Oszillator ist.

## 1. Methodische Korrektur der Baselinegrenze

Jede R1-Form besitzt abstrakt die Struktur:

```text
raeumliche S-Wirkung
+ lokale gemeinsame S-L-Dynamik
```

Damit liegt R1 mathematisch in der Oberklasse von Systemen mit lokal
gekoppelten Zustaenden und nur einer raeumlich mobilen Komponente.

### Oberklasse ist keine einzelne Baseline

`Beliebige Ein-Diffusor-Reaktions-Diffusion` darf nicht als Universalbaseline
verwendet werden. Diese Klasse enthaelt jeden moeglichen R1-Kandidaten und
koennte ihn definitionsgemaess identisch abbilden.

Verglichen werden muessen stattdessen enge vorregistrierte Formen:

- lineare lokale S-L-Relaxation;
- einzelne und mehrfache Leaky-Spuren;
- adaptiver Gain und variable Mobilitaet;
- linearer oder nichtlinearer Standardoszillator;
- feste Bistabilitaet und Hysterese;
- konkrete klassische Ein-Diffusor-Musterkinetiken;
- strukturell reduzierte Ablationen des Kandidaten.

Die mathematische Oberklasse beschreibt die Modellform. Sie widerlegt nicht
automatisch eine konkrete physische Funktion.

## 2. Unabhaengige physische Funktion

Die einzige fuer R1 zulaessige Funktionsbezeichnung lautet:

> lokale konstitutive Akkommodation

Sie bedeutet:

> Eine lokale interne Feldkonfiguration L wird durch die gegenwaertige
> gemeinsame S-L-Wechselwirkung veraendert. Dieselbe Wechselwirkung leistet
> gleichzeitig einen internen Beitrag zur weiteren lokalen S-Entwicklung.

Akkommodation bedeutet weder Lernen noch Angleichungsziel. Der Begriff
behauptet kein Memory.

### Physische Rollen

```text
S = aktuelle schnelle Feldlage und raeumlich transportierte Feldwirkung
L = ortsgebundene interne Konfiguration des lokalen Feldmaterials
```

L ist vergleichbar mit einer internen Zustandsvariablen in einer
konstitutiven Materialbeschreibung: Der aktuelle aeussere beziehungsweise
schnelle Zustand allein reicht nicht aus, um die spaetere Materialantwort zu
bestimmen.

Diese Analogie begruendet nur die Rollenart. Eine bekannte
Materialgleichung wird nicht in MCM uebernommen.

## 3. Unteilbare lokale Kreuzwirkung

Eine spaetere R1-Schliessung muss eine lokale Kreuzwirkung `K` besitzen, die
nur als gemeinsamer Beitrag sinnvoll ist:

```text
K veraendert die L-Fortsetzung
und
K veraendert die S-Fortsetzung
innerhalb derselben atomaren Kausalgrenze
```

`K` ist hier nur ein Funktionsplatzhalter, keine Variable und keine Gleichung.

### Additive interne S-Wirkung

Die L-vermittelte Wirkung auf S muss als interner Beitrag zur lokalen
S-Fortsetzung formulierbar sein. L darf nicht lediglich:

- Rezeptoreingang multiplizieren;
- Nachbarschaftsfluss multiplizieren;
- Antwortzeit einstellen;
- einen Zielwert fuer S liefern;
- S an eine gespeicherte Vorlage angleichen.

Damit werden Gain, Receptivity, Mobilitaet und Template-Leser als primaere
Erklaerungen ausgeschlossen.

### Keine getrennte Bildung und Auslesung

Unzulaessig ist jede Zerlegung der Form:

```text
Bildungsregel schreibt L
+ fester Leser wendet L spaeter auf S an
```

Die gleiche lokale Kreuzwirkung muss waehrend jedes normalen Schritts beide
Richtungen tragen. Es gibt keinen Schreib- oder Lesemodus.

## 4. Kausale Operationalisierung

Die behauptete Funktion existiert nur, wenn spaeter alle folgenden
Interventionen moeglich sind.

### S-zu-L-Richtung

Bei identischem L-Vorzustand muessen kontrolliert unterschiedliche lokale
S-Verlaeufe unterschiedliche L-Fortsetzungen verursachen.

### L-zu-S-Richtung

Bei angeglichenem S-Vorzustand und identischer weiterer S-Feldwirkung muessen
kontrolliert unterschiedliche L-Zustaende unterschiedliche vollstaendige
S-Fortsetzungen verursachen.

### Kreuztausch

Wird L zwischen zwei ansonsten identischen lokalen Gesamtzustaenden
getauscht, muss die spaetere S-Wirkung mitwandern.

### Richtungsablation

Die Entfernung jeweils einer Kreuzrichtung muss deren kausale Folge
entfernen, ohne die andere Richtung oder den technischen S-Nullpfad
unbeabsichtigt zu ersetzen.

Diese Eingriffe sind Forschungsinstrumente, keine Runtimefunktionen.

## 5. Verbotene Reduktionen

Eine konkrete Form ist keine R1-Akkommodation, wenn sie exakt auf eine dieser
Strukturen faellt.

### Spur oder Relaxation

L folgt S oder einer festen Funktion von S mit einer festen Zeitkonstante.

### Integrator

L summiert S, Aktivitaet, Energie, lokale Differenz, Koaktivitaet oder
Feldfluss und wird spaeter ausgelesen.

### Gain oder Mobilitaet

L skaliert nur eine bereits vorhandene S-Wirkung oder deren Geschwindigkeit.

### Oszillator

S und L tauschen nur eine konservierte oder gedaempfte Modenamplitude
beziehungsweise Phase aus.

### Hysterese oder Zielattraktor

Die Naturform enthaelt mehrere vorbereitete Lagen, eine feste
Hystereseschleife oder gewuenschte stabile Zustaende.

### Musterkinetik

Lokale Terme oder Parameter werden so ausgewaehlt, dass eine bekannte
Wellenlaenge, Flecken-, Streifen- oder Clusterform entsteht.

### Universelle nichtlineare Rekurrenz

Eine beliebige nichtlineare Funktion mit derselben Zustandsdimension ist
keine sinnvolle Gegenbaseline. Konkrete reduzierte Funktionsklassen muessen
benannt werden.

## 6. Nichtleerer funktionaler Hypothesenraum

Ein skalarer interner konstitutiver Zustand ist in der Materialmodellierung
eine etablierte Moeglichkeit, um einen sich waehrend Belastung veraendernden
Materialzustand zu beschreiben. Damit ist die Rollenart `interne
Konfiguration` physikalisch nicht leer.

Fuer MCM bleibt jedoch offen, ob eine konkrete skalare Naturform zugleich:

- ohne Ziel und Fehlerbegriff auskommt;
- nicht auf die verbotenen Reduktionen faellt;
- den gesamten geforderten Lebenszyklus tragen kann;
- gegen enge Baselines unterscheidbar bleibt.

Die Entscheidung lautet deshalb:

```text
physische Rollenart vorhanden:       ja
MCM-taugliche skalare Schliessung:   noch nicht nachgewiesen
```

Der Vertrag oeffnet einen Suchraum, keine Implementierung.

## 7. Ein-Diffusor-Effekte, die R1 nicht belegen

Folgende Beobachtungen werden primaer der raeumlichen Oberklasse oder engen
Standardformen zugerechnet:

- spontane Inhomogenitaet;
- gitterabhaengige Hochfrequenzmuster;
- stationaere Flecken oder Streifen;
- wandernde Wellen;
- lokale Oszillation;
- lange Transienten;
- Symmetriebruch;
- empfindliche Abhaengigkeit von Startstoerungen.

Keine dieser Beobachtungen weist fuer sich konstitutive Akkommodation,
Praegung oder Memory nach.

## 8. Unterscheidende spaetere Beobachtung

Ein R1-Kandidat muss nicht beweisen, dass er keine Reaktions-Diffusionsform
ist. Er muss innerhalb dieser Oberklasse einen kontrollierten Funktionszyklus
tragen, den die vorregistrierten engeren Baselines mit ihrem jeweiligen
einheitlichen Parametersatz nicht gemeinsam reproduzieren:

```text
Bildung durch normale Weltgeschichte
-> spaetere L-vermittelte S-Wirkung bei angeglichenem S
-> Mitwandern beim L-Tausch
-> Verschwinden bei L-Neutralisierung
-> funktionaler Verlust unter weiterer normaler Weltgeschichte
-> andere Wiederpraegung derselben lokalen L-Freiheitsgrade
```

Eine Baseline darf nicht fuer jede Phase neu parametrisiert werden. Derselbe
vorregistrierte Parametersatz muss ihren gesamten Vergleichsverlauf tragen.

## 9. Naturregel und entstandene Konfiguration

| Fest programmiert | Muss aus Weltgeschichte entstehen |
|---|---|
| ein skalarer L-Wert pro Ort | konkrete L-Belegung |
| lokale gemeinsame S-L-Form | konkrete lokale Trajektorie |
| bestehender S-Feldfluss | raeumliche Verteilung der L-Wirkung |
| Wertebereich und Symmetrien | Staerke und Dauer |
| technische Atomaritaet | funktionaler Verlust |
| fester Parameterbereich | spaetere andere Konfiguration |

Die Naturform darf keine konkrete Zeile der rechten Spalte vorwegnehmen.

## 10. Stopplinien vor einer Gleichungswahl

Eine vorgeschlagene R1-Schliessungsfamilie erhaelt sofort STOPP, wenn:

1. ihre unabhaengige Funktion nur `Memory erzeugen` lautet;
2. L eine gespeicherte Beobachtung, Vorlage oder Bedeutung ist;
3. S-L-Wechselwirkung als Fehlerkorrektur oder Zielangleichung formuliert
   wird;
4. Bildung und Wirkung in getrennte Regeln zerfallen;
5. L nur Eingang, Feldfluss oder Zeitkonstante skaliert;
6. L nur eine Groesse integriert oder exponentiell verfolgt;
7. mehrere gewuenschte Ruhelagen oder eine Hysteresekurve eingebaut werden;
8. das Resultat nur Oszillation oder Musterbildung ist;
9. Loesung eine Schwelle, feste Dauer, Phase oder Reset benoetigt;
10. keine konkrete engere Baseline mit demselben Zustandsbudget formulierbar
    ist.

## Zulassungsentscheidung

R1 besitzt mit der lokalen konstitutiven Akkommodation eine physisch
benennbare unabhaengige Rollenart. Diese Rollenart ist fuer genau einen
statischen Schliessungsformen-Audit zugelassen.

```text
R1-Naturfunktion als Forschungsrahmen: zugelassen
generische Ein-Diffusor-Klasse als Baseline: verboten
enge Ein-Diffusor-Baselines:          erforderlich
konkrete Kreuzwirkung:                nicht gewaehlt
konkrete Gleichung:                   nicht zugelassen
Schema, Runtime oder Test:            nicht zugelassen
```

## Quellen

- G. M. Eggert und P. R. Dawson,
  [On the use of internal variable constitutive equations in transient forming processes](https://doi.org/10.1016/0020-7403(87)90045-2),
  1987. Belegt die physikalische Rollenart einer einzelnen skalaren internen
  Zustandsvariablen in einer sich unter Belastung veraendernden
  Materialbeschreibung.
- H. Miyazako, Y. Hori und S. Hara,
  [Turing Instability in Reaction-Diffusion Systems with a Single Diffuser](https://arxiv.org/abs/1309.0111),
  2013. Dient als Grenze fuer kollektive Effekte mit nur einer raeumlich
  mobilen Komponente.

Die R1-Akkommodation ist eine MCM-Forschungshypothese und keine aus diesen
Quellen uebernommene Materialgleichung.

## Bester naechster Schritt

Als naechstes wird ein **R1-Schliessungsformen-Audit** durchgefuehrt. Er
vergleicht hoechstens drei kleinste lokale Kreuzwirkungsformen:

1. dissipative reziproke Akkommodation mit eindeutigem neutralem Bereich;
2. begrenzte nichtgradientige S-L-Kreuzwirkung ohne Zielattraktor;
3. lokale zustandsabhaengige Gegenwirkung ohne multiplikativen Gain.

Der Audit muss jede Form algebraisch gegen Leaky-Spur, Integrator, Gain,
Mobilitaet, Oszillator, Hysterese und konkrete Ein-Diffusor-Standardkinetiken
reduzieren. Danach darf hoechstens eine Form fuer eine konkrete mathematische
Schliessung offen bleiben.
