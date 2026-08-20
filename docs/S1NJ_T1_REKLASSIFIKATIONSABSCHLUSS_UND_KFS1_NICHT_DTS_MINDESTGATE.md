# S1-NJ T1-Reklassifikationsabschluss und KFS-1-Nicht-DTS-Mindestgate

## Status

S1-NJ schliesst die Reklassifikation von
`KFS1-T1_LOCAL_TARGET_REFRACTORY` ab und bindet die Mindestanforderung an
einen spaeteren KFS-1-Regelkandidaten. Der Schritt waehlt keine neue Regel,
keine Gleichung, keine Parameter und keine Feldrueckwirkung.

Entscheidung:

```text
T1_INDEPENDENT_BRANCH_CLOSED_KFS1_NON_DTS_GATE_BOUND
```

## Abschluss von T1

T1 bleibt im Projekt in genau zwei technischen Rollen erhalten:

- reproduzierbare diskrete DTS-1-Gegenbaseline;
- Testfixture fuer atomare Ereignisgrenzen und Ressourcenbilanz.

T1 ist gesperrt als:

- unabhaengiger KFS-1-Substratkandidat;
- Begruendung einer neuen Feldrueckwirkung;
- Funktionsbefund fuer Spaetaufnahme, Abschwaechung, Interferenz oder
  Wiederbindung;
- Befund zur hypothetischen MCM-Memory.

Die Implementierung wird nicht geloescht oder umgedeutet. Ihre Herkunft,
Abnahme und Reklassifikation bleiben nachvollziehbar.

## Konsequenz fuer die bisherige KFS-1-Anatomie

S1-MX bindet `free`, `bound` und `blocked` als drei disjunkte Rollen eines
endlichen lokalen Ledgers. S1-NI zeigt, dass diese Rollen allein keinen
eigenstaendigen Kandidaten begruenden: DTS-1 besitzt dieselbe
Dreirollenbilanz, und T1 verwendet denselben gerichteten Rollenzyklus in
diskret geschalteter Form.

Die S1-MX-Anatomie bleibt als gueltige Bilanz- und Baselineoberflaeche
erhalten. Sie ist ab S1-NJ aber keine hinreichende Kandidatenabgrenzung mehr.
Eine neue Regel auf demselben Ledger darf nicht allein wegen anderer Raten,
Schwellen, Ereignisnamen oder Schaltbedingungen als neue Substratklasse
bezeichnet werden.

## Nicht-DTS-Mindestgate

Ein spaeterer KFS-1-Regelkandidat muss vor jeder Implementierung mindestens
einen der folgenden strukturellen Wege eindeutig binden.

### G1: anderes atomares Transfernetz

Der Kandidat verwendet eine lokal erhaltene atomare Rollenbeziehung, die
nicht durch den geschlossenen DTS-1-Zyklus
`free -> bound -> blocked -> free` mit beliebigen festen oder
ereignisgeschalteten Transferanteilen reproduziert werden kann.

Ein blosses Auslassen einer Rolle ist nicht ausreichend, wenn die Regel
dadurch auf Gain, Fixed Adapter, Leaky oder Integrator reduziert wird.

### G2: zusaetzliche endliche lokale Zustandskoordinate

Der Kandidat besitzt mindestens eine endliche, bilanziert oder hart begrenzt
definierte lokale Zustandskoordinate, die nicht aus `free/bound/blocked`, S/H,
einem Adapterwert oder deren unmittelbaren Summen rekonstruiert werden kann.

Die Koordinate darf keine Rohdaten, Sequenz, Labels, Reward, Zielwerte oder
Readoutergebnisse speichern.

### G3: nicht faktorisierbare lokale Ressourcenverteilung

Der Kandidat bindet eine endliche lokale Verteilungs- oder Besitzrelation
zwischen konkurrierenden Kanten. Deren spaetere Wirkung darf weder in
unabhaengige Einkanten-DTS-1-Ledger noch in das bereits vorhandene gemeinsame
DTS-1-Knotenbudget zerfallen.

Eine globale Normalisierung oder ein nachtraeglicher Nachbarschaftsvergleich
erfuellt dieses Gate nicht.

Mindestens eines der drei Gates muss vollstaendig erfuellt sein. Eine
Kombination ist zulaessig, aber nicht erforderlich und begruendet fuer sich
keinen Vorteil.

## Verbindliche Interventionsprognose

Vor jeder Kandidatengleichung muss ein Paar gueltiger lokaler Vorzustaende
gebunden werden mit:

```text
identischem aktuellem S/H
identischem aggregiertem free/bound/blocked-Ledger
identischer Geometrie und Feldzeitgrenze
unterschiedlicher kandidatenspezifischer G1-, G2- oder G3-Rolle
```

Unter derselben naechsten lokalen Probe muss der Kandidat daraus zwei
verschiedene, vorab gerichtete Nachzustands- oder Feldaufnahmeprognosen
ableiten. DTS-1 erhaelt in beiden Armen denselben gueltigen Vorzustand und muss
daher dieselbe Prognose liefern.

Wenn kein solches Interventionspaar formulierbar ist, besitzt der Kandidat
keine eigene technische Kausalvariable und wird vor Implementierung
verworfen.

## Rekonstruktionsaudit

Fuer jeden spaeter vorgeschlagenen Kandidaten muss vor Code geprueft werden:

1. Sind alle gespeicherten Werte aus DTS-1-Ledger, S/H oder einem festen
   Adapter rekonstruierbar?
2. Lassen sich alle Transfers als DTS-1-Engagement, -Turnover und -Recovery
   mit festen oder ereignisgeschalteten Anteilen schreiben?
3. Zerfaellt ein Mehrkantenverhalten in unabhaengige DTS-1-Einkantenarme oder
   das vorhandene gemeinsame DTS-1-Knotenbudget?
4. Verschwindet die eigene Prognose bei Ablation der neuen Rolle?
5. Bleibt die Prognose ohne Labels, Reward, Replay, Zieltopologie und
   Ergebniswissen erhalten?

Ein positives Ergebnis in Frage 1, 2 oder 3 ohne eine unabhaengige
Interventionsprognose schliesst den Vorschlag als eigenstaendigen Kandidaten.

## Weiterhin geltender Funktionsvertrag

Der S1-MW-Funktions- und Falsifikationsvertrag bleibt bestehen. Ein spaeterer
Kandidat muss weiterhin lokale Belastung, Spaetaufnahme, Abschwaechung,
Interferenz, Freigabe und Wiederbindung getrennt vorhersagen und gegen Fixed
Adapter, Leaky, Integrator, Replay, globale Normalisierung, F3/CONST-V und
DTS-1 antreten.

Das Nicht-DTS-Gate ist eine zusaetzliche notwendige Bedingung. Es ersetzt
keine Funktionsprognose und keine faire Kausalexposition.

## Fail-Closed-Grenze

Vor Implementierung wird ein Vorschlag gestoppt, wenn:

- er nur neue Namen fuer DTS-1-Rollen oder -Transfers einfuehrt;
- seine neue Variable aus vorhandenen Zustandswerten berechenbar ist;
- seine Prognose erst durch Readout, Fit oder Ergebniswahl entsteht;
- seine Ressource unbeschraenkt, global oder nicht bilanziert ist;
- kein zustandskontrolliertes Interventionspaar formulierbar ist;
- er fuer die eigene Abgrenzung bereits eine Feldintegration benoetigt.

## Aussagegrenze

S1-NJ ist ein statischer Architektur- und Falsifikationsvertrag. Er zeigt
keinen neuen Kandidaten, keine Feldwirkung, keine Lernfunktion und keinen
Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NK darf ausschliesslich einen statischen Kandidatenklassenaudit fuer G1,
G2 und G3 durchfuehren. Dabei darf hoechstens eine minimale Klasse fuer einen
spaeteren Funktionsvertrag ausgewaehlt werden; wenn keine Klasse eine klare
Interventionsprognose traegt, lautet das Ergebnis `STOPP`.

S1-NK bindet noch keine Gleichung, Zahlenwerte, Runtime oder Feldrueckwirkung.
