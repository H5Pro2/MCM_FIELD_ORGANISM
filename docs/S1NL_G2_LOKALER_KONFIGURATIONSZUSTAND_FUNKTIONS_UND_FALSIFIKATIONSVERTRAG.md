# S1-NL G2-Funktions- und Falsifikationsvertrag

## Status

S1-NL bindet ausschliesslich die Funktions- und Falsifikationsgrenze fuer die
in S1-NK ausgewaehlte Klasse
`G2_BOUNDED_LOCAL_CONFIGURATION_STATE`. Der Schritt waehlt noch keine
Zustandsdarstellung, Gleichung, Parameter, Runtime oder Feldrueckwirkung.

Entscheidung:

```text
G2_LOCAL_CONFIGURATION_FUNCTION_AND_FALSIFICATION_CONTRACT_BOUND
```

## Zweck

G2 darf nicht allein deshalb weitergefuehrt werden, weil eine zusaetzliche
Variable denkbar ist. Vor jeder Anatomie muss feststehen:

- welche eigene lokale Kausalprognose die Klasse traegt;
- wie diese Prognose von DTS-1, Fixed Adapter, Leaky und Integrator getrennt
  wird;
- wie die neue Rolle ablatiert wird;
- wann die Klasse ohne Implementierung verworfen wird.

Der Vertrag trennt deshalb eine direkte Zustandsintervention von einer
spaeteren lokalen Bildungsgeschichte. Die Intervention prueft Kausalitaet;
die Bildungsgeschichte prueft, ob die Rolle ohne manuelles Setzen technisch
entstehen koennte.

## Vollstaendig kontrollierter Vorzustand

Beide Interventionsarme muessen unmittelbar vor derselben lokalen Probe
bitgleich besitzen:

```text
Geometrie und Kantenidentitaet
aktuelle S- und H-Werte
aktuellen Rezeptorkontakt
vollstaendiges free/bound/blocked-Ledger
DTS-1-Knoten- und Kantenledger
Feldzeitgrenze
Adapter-, Leaky- und Integratorzustand der Gegenbaselines
```

Der einzige erlaubte Unterschied ist eine gueltige lokale G2-Konfiguration.
Die G2-Konfiguration selbst ist nicht Teil von DTS-1 oder der Baselines.

## F1: direkte Zustandsintervention

Zwei vorregistrierte gueltige Konfigurationszustaende werden vorlaeufig nur
als Rollen bezeichnet:

```text
G2_C0 = neutrale Konfigurationsrolle
G2_C1 = nichtneutrale Konfigurationsrolle
```

Diese Rollen sind noch keine Zahlen und besitzen noch keine physische oder
semantische Interpretation.

Unter derselben lokalen Probe muss ein spaeterer Kandidat vor der
Implementierung genau eine gerichtete technische Prognose binden:

```text
candidate_local_admissibility(G2_C1)
!= candidate_local_admissibility(G2_C0)
```

`candidate_local_admissibility` bezeichnet nur den spaeter zu bindenden
lokalen Einfluss auf eine erlaubte Ressourcen- oder Kopplungsumordnung. Es
ist kein Readoutscore. Richtung, Messkomponente und Vorzeichen muessen im
naechsten endlichen Interventionsvertrag festgelegt werden, bevor eine
Gleichung gewaehlt wird.

Wenn keine einzelne lokale Messkomponente fuer diese Differenz benannt werden
kann, wird G2 gestoppt.

## F2: endogene Bildungsprognose

Eine direkte Intervention reicht nicht als Kandidatenfunktion. Eine spaetere
lokale Bildungsgeschichte muss G2 ohne externes Setzen erzeugen koennen.

Erforderliche Form:

```text
lokale Geschichte H1 -> gueltige G2-Konfiguration C1
lokale Geschichte H0 -> gueltige G2-Konfiguration C0

danach kontrollierte Angleichung von S/H und Ressourcenledger
+ identische lokale Probe
-> dieselbe gerichtete F1-Differenz
```

H1 und H0 muessen aus kontrollierten lokalen Feldkontakten bestehen. Sie
duerfen keine Labels, Zielwerte, Reward, Ergebnisdaten oder manuell gesetzte
Topologie enthalten. Welche konkreten Geschichten verwendet werden, bleibt
bis zu einem spaeteren Expositionsvertrag offen.

Die Angleichung darf G2 nicht aus Ergebniskenntnis reparieren. Sie dient nur
der kausalen Trennung von schnellem Feldzustand, Dreirollenledger und der
zusaetzlichen Konfigurationsrolle.

## F3: Abschwaechung und Loesung

G2 darf keine permanente versteckte Struktur sein. Eine vorab festgelegte
lokale Loesungsgeschichte muss die F1-Differenz reduzieren und schliesslich
einen neutralen oder wieder frei definierbaren Konfigurationszustand
ermoeglichen.

Dabei muessen gleichzeitig gelten:

- alle endlichen Ressourcenbilanzen bleiben erhalten;
- die Reduktion entsteht im Kandidatenzustand und nicht erst im Readout;
- dieselbe Loesungsgeschichte wird zustandsbehafteten Baselines zugefuehrt;
- eine geloeschte Rohdaten- oder Sequenzkopie ist keine Loesung.

Ohne messbare Abschwaechung und erneute Bildbarkeit wird G2 verworfen.

## F4: lokale Interferenz

Eine konkurrierende lokale Geschichte muss die spaetere F1-Prognose gerichtet
veraendern koennen. Die Interferenz muss lokal bleiben und darf weder durch
globale Normalisierung noch durch Austausch eines Konfigurationslabels
erzeugt werden.

Ein spaeterer Vertrag muss mindestens drei Arme enthalten:

```text
Bildung
Bildung + neutrale Zwischenphase
Bildung + konkurrierende Zwischenphase
```

Die Differenz zwischen neutraler und konkurrierender Zwischenphase muss vor
Ausfuehrung gerichtet gebunden werden.

## Gegenprognosen

### DTS-1 und geschaltetes T1

Bei identischem S/H und identischem vollstaendigem Ressourcenledger besitzen
DTS-1 und T1 keine G2-Koordinate. Ihre direkte Interventionsprognose ist
daher bitgleiche lokale Ressourcenfortschreibung in C0 und C1.

Wenn die Kandidatendifferenz durch feste oder ereignisgeschaltete DTS-1-
Transfers rekonstruiert werden kann, wird G2 verworfen.

### Fixed Adapter

Bei identischem Feld- und Adaptervorzustand sagt der Fixed Adapter bitgleiche
Fortschreibung voraus. Ein armweise verschiedener Adapter ist unzulaessig.

### Leaky und Integrator

Im direkten Interventionsarm muessen ihre vollstaendigen eigenen Zustaende
bitgleich sein; ihre Prognose ist daher ebenfalls bitgleich.

Im endogenen Bildungsarm erhalten sie dagegen dieselbe relevante H1-/H0-
Vorgeschichte wie G2. Reproduziert ein einzelner vorregistrierter Leaky- oder
Integratorarm Bildung, Spaetwirkung, Abschwaechung, Interferenz und Loesung
vollstaendig, besitzt G2 keine eigene Funktionsachse und wird gestoppt.

### Replay und Readout

Replay ist keine Kandidatenbaseline mit Laufrecht, sondern eine
Ausschlusskontrolle: G2 darf keine Folge erneut ausgeben oder Ereignisse
indizieren. Der Readout bleibt passiv und darf die Armdifferenz nicht
erzeugen.

## Ablationsvertrag

Die spaetere Kandidatenablation entfernt oder neutralisiert ausschliesslich
die G2-Konfigurationsrolle. Geometrie, S/H, Ressourcenledger, Probe,
Schrittordnung und alle uebrigen Kandidatenbestandteile bleiben identisch.

Verbindliche Prognose:

```text
G2 aktiv:    gerichtete F1-Differenz vorhanden
G2 ablatiert: F1-Differenz kollabiert auf die registrierte Nullgrenze
```

Bleibt die Differenz nach Ablation bestehen, stammt sie nicht kausal aus G2.
Veraendert die Ablation weitere Zustandsrollen, ist der Vergleich ungueltig.

## Mindestmessungen vor Gleichung

Vor einer Kandidatengleichung muessen spaeter mindestens gebunden sein:

- Identitaet der lokalen Interventionseinheit;
- vollstaendiger Kontrollvorzustand beider Arme;
- eine einzelne primaere lokale Admissibilitaetskomponente;
- Richtung und Nullgrenze der F1-Differenz;
- H1/H0-Bildungsgeschichten;
- neutrale und konkurrierende Zwischenphase;
- Loesungs- und erneute Bildungsgrenze;
- DTS-1-, T1-, Fixed-, Leaky- und Integratorprofile;
- Ablationsarm und Fail-Closed-Codes.

Keine Messrolle darf nach Kenntnis eines Ergebnisses gewechselt werden.

## Verwerfungsbedingungen

Die G2-Klasse wird vor Implementierung verworfen, wenn:

- C0 und C1 nicht bei sonst vollstaendig identischem Vorzustand gueltig sind;
- keine gerichtete lokale F1-Komponente formulierbar ist;
- G2 aus S/H, Dreirollenledger oder Adapter rekonstruierbar ist;
- die direkte Differenz durch DTS-1 oder geschaltetes T1 entsteht;
- ein einzelner fair exponierter Leaky- oder Integratorarm alle gebundenen
  Funktionsrollen reproduziert;
- Ablation die Differenz nicht entfernt;
- Bildung eine manuelle Zustandssetzung, Labels, Reward oder Zieltopologie
  benoetigt;
- Abschwaechung, Interferenz, Loesung oder erneute Bildung nicht getrennt
  messbar sind;
- Rohdaten, Sequenzen oder Ergebniswissen gespeichert werden muessen;
- eine Feldintegration noetig ist, bevor die lokale Kausalprognose steht.

## Aussagegrenze

S1-NL bindet nur notwendige Funktions- und Falsifikationsrollen. Es gibt noch
keine G2-Anatomie, keine Dynamik, keine Feldwirkung, keine Lernfunktion und
keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NM darf ausschliesslich einen endlichen, darstellungsneutralen
Interventions- und Messvertrag fuer F1 binden. Er muss die zwei Arme, den
vollstaendigen Kontrollvorzustand, genau eine primaere lokale Messkomponente,
Richtung, Nullgrenze, Baselineprognosen und Abbruchbedingungen festlegen.

S1-NM darf noch keine G2-Zustandsdarstellung, Bildungsgleichung, Parameter,
Runtime oder Feldrueckwirkung waehlen.
