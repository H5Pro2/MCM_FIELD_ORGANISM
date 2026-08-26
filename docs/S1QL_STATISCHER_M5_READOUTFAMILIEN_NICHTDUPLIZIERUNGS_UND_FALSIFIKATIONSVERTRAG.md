# S1-QL: Statischer M5-Readoutfamilien-, Nichtduplizierungs- und Falsifikationsvertrag

## Status und Umfang

S1-QL bindet die kleinste endliche ausfuehrbare Readoutrolle fuer M5 nach
dem Bestandsaudit S1-QK. Der Vertrag trennt:

- M5 als breite strukturelle Klasse lokaler Einzustandsmodelle;
- genau einen endlichen ausfuehrbaren technischen Vertreter;
- bereits vorhandene oder gestoppte Unterklassen;
- eigene Gegenprognosen gegen B3, SAT, NORM, M1 und M4;
- Verwerfungs- und Aussagegrenzen.

S1-QL fuegt keine Gleichung, Parameter, Werte oder neue Readoutfunktion ein.
Es gibt keine Implementierung, Fixture, Testausfuehrung, Runtimeintegration
oder Ergebnisentscheidung.

Verbindliche Entscheidung:

```text
M5_EXECUTABLE_READOUT_FAMILY_BOUND_TO_SINGLETON_DIRECT_LOCAL_STATE
EXISTING_W7N_LEAK_ACCEPTED_AS_THE_ONLY_M5_STATE_AND_OUTPUT_KERNEL
DIRECT_REPLACE_S_WITH_SHARED_A1_H_BOUND_AS_FUNCTIONAL_FIELD_ROLE
SAT_REMAINS_STOPPED_OBSERVER_ONLY_SUBCLASS
M5_STRUCTURAL_CLASS_NOT_CLAIMED_EXHAUSTIVELY_EXECUTED
NO_EQUATIONS_NO_VALUES_NO_IMPLEMENTATION_NO_EXECUTION
```

## Zwei getrennte M5-Bedeutungen

### Strukturelle Klasse

Die strukturelle M5-Klasse bezeichnet weiterhin Modelle mit:

- genau einem lokalen Zustand pro Feldort;
- ortsseparabler Zustandsfortschreibung;
- einem vorab festen lokalen Readout;
- keinem globalen Nenner, Ressourcenledger, Puffer oder Replay;
- keiner zweiten privaten Zustandsrolle.

Diese Klasse dient der Nichtduplizierungs- und Reduktionspruefung. Sie ist
keine Behauptung, dass jede mathematisch denkbare lokale Readoutfunktion
ausgefuehrt oder ausgeschlossen wird.

### Ausfuehrbarer Vertreter

Das Pflichtbaselinepaket darf fuer M5 genau einen konkreten Vertreter
vorbereiten:

```text
M5_DIRECT_LOCAL_STATE
```

Dieser Vertreter verwendet unveraendert:

- den W7-N-Frischzustand der Modellrolle `leak`;
- die vorhandene W7-N-`LEAK`-Zustandsfortschreibung;
- den vorhandenen vollstaendigen lokalen `LEAK`-Output;
- den direkten lokalen Output als finales S;
- H aus demselben kandidatenfreien A1-Fast-Vorschlag.

Die spaetere Ausfuehrung dieses Vertreters prueft nur die minimale Erklaerung
`direkte lokale Einzustandsretention`. Sie repraesentiert nicht alle
moeglichen festen nichtlinearen Readouts.

## Gepruefte Readoutfamilien

| Readoutfamilie | Bestand | Entscheidung | Grund |
|---|---|---|---|
| `DIRECT_LOCAL_STATE` | W7-N `LEAK` | ausgewaehlt | lokal, signed, parameterfrei am Readout und bereits vorhanden |
| `FIXED_BOUNDED_LOCAL_STATE` | W7-N `SAT` | nicht ausfuehrbar | gestoppte M5-Unterklasse, nur Observerdiagnostik |
| `GLOBAL_NORMALIZED_STATE` | W7-N `NORM` | ausgeschlossen | eigene A3-Rolle mit geometrieweiter Kopplung |
| lokaler Gain oder Schwellenreadout | kein gebundener M5-Kern | ausgeschlossen | neue Parameter- und Funktionsfamilie |
| Polynom-, Spline- oder Fitreadout | kein gebundener Kern | ausgeschlossen | offene nachtraegliche Modellwahl |
| Mischung mehrerer Readouts | kein gebundener Kern | ausgeschlossen | mehrdeutige oder armweise Funktionswahl |

Die Singletonfamilie ist die kleinste endliche Wahl mit einem vorhandenen
Zustands- und Outputkern. Ein zusaetzlicher Readout ist nur zulaessig, wenn
spaeter eine neue, von M5_DIRECT, SAT und NORM unabhaengige Gegenprognose vor
jeder Ergebniskenntnis begruendet wird. S1-QL oeffnet dafuer keinen Zweig.

## Direkte M5-Funktionsprognose

M5_DIRECT sagt voraus:

1. Eine lokale A1-S-Geschichte kann nach ihrem aktuellen Kontaktende als
   genau ein lokaler privater Zustand in finales S fortwirken.
2. Bei identischer lokaler Evidence und identischem lokalen Vorzustand
   aendert eine nur entfernte M5-Zustandslast den lokalen Output nicht.
3. Der lokale Output bleibt der vorhandene signed W7-N-`LEAK`-Output ohne
   Begrenzungs-, Gain- oder Normalisierungsschritt.
4. Alle Expositionsrollen verwenden denselben Frischzustand, denselben Kern,
   dieselbe Konfiguration und denselben Readout.
5. Die vollstaendige Feldgeschichte entsteht mit genau einer
   Feldzeitfortschreibung pro Intervall.

Diese Prognosen muessen vor einem spaeteren Vergleich als technische
Kontraste materialisierbar sein. Ein lediglich vorhandener lokaler Zustand
ohne vollstaendiges Feld ist kein M5-Ergebnis.

## Feldrollenbindung

Die einzige funktional zulaessige Feldordnung lautet:

```text
Feldvorzustand + Rezeptorinput + Intervall
    -> interner kandidatenfreier A1-Fast-Vorschlag S_fast/H_fast
    -> W7-N-LEAK-Fortschreibung aus M5-Vorzustand und vollstaendigem S_fast
    -> M5-Folgezustand + vollstaendiger signed direkter LEAK-Output
    -> finales Feld: S aus M5_DIRECT, H aus A1-Fast
```

Das finale S darf erst im naechsten Intervall wieder Eingabe sein. Der
A1-Vorschlag bleibt interner Evidence- und H-Beleg und darf nicht separat
veroeffentlicht werden.

Die Kompositionsfamilie ist funktional `REPLACE_S`, weil der vorhandene
vollstaendige lokale Output direkt verwendet wird. Nicht zulaessig sind:

- Mischung mit A1-S;
- Multiplikation oder Gain;
- Ausgabe als zusaetzliche Quelle;
- zweite Feldintegration;
- Veraenderung von H, Perzeption, Dockrollen oder Feldzeit;
- Uebernahme eines NORM-Skalierungsrecords.

S1-QL bindet nur diese Funktionsrolle. Modulgrenze, Receipt, Fehlercodes und
Testbudget bleiben dem naechsten Vertrag vorbehalten.

## Gegenprognose gegen B3

### Passive B3-H-Rolle

Die passive B3-Feldkontrolle traegt ihre Retention in H, waehrend S aus dem
lokalen Feldinput stammt. M5_DIRECT traegt dagegen einen getrennten privaten
lokalen Zustand und setzt daraus finales S; H bleibt die gemeinsame A1-Rolle.

Eigene Gegenprognose:

```text
Bei identischem A1-Vorschlag und angeglichenem H kann M5_DIRECT ein
privatzustandsabhaengiges finales S liefern, waehrend die passive B3-H-Rolle
keinen getrennten privaten S-Retentionszustand besitzt.
```

Wird M5 nur als zweite H-Spur materialisiert, ist es B3-dupliziert und zu
stoppen.

### A2/B3-M/F3-Rolle

Die A2/B3-Feldbaseline traegt einen M-Zustand und wirkt ueber den vorhandenen
F3-Feld- und Geometriepfad. M5_DIRECT besitzt weder M noch Edge- oder
Substratrollen.

Eigene Gegenprognose:

```text
Bei identischer lokaler A1-S-Evidence und identischem lokalen M5-Vorzustand
bleibt M5_DIRECT invariant gegen reine Aenderungen eines entfernten
M-/Edge-Inventars, das die A2/B3-Feldwirkung veraendern darf.
```

Liest M5 ein M-Ledger, einen Laplacepfad, eine Kante oder eine
Substratkonfiguration, ist die Abgrenzung gescheitert.

## Gegenprognose gegen gestopptes SAT

SAT besitzt denselben lokalen Zustandsumfang, aber einen festen begrenzenden
Readout. M5_DIRECT verwendet ausschliesslich den vorhandenen direkten
`LEAK`-Output.

Die technische Unterscheidung lautet:

- M5_DIRECT fuegt nach dem lokalen Folgezustand keine Ausgangsbegrenzung ein;
- SAT kann als passive Observerdiagnostik eine Abweichung zwischen lokalem
  Zustand und begrenztem Output zeigen;
- SAT wird weder Feldarm noch alternatives M5-Fitmodell.

Erklaert M5_DIRECT spaeter das vollstaendige Feldprofil, ist eine zusaetzliche
SAT-Erklaerung nicht erforderlich. Scheitert M5_DIRECT, folgt daraus weder
eine SAT-Freigabe noch eine positive Kandidatenaussage.

## Gegenprognose gegen NORM

M5_DIRECT ist strikt ortsseparabel. NORM besitzt die bereits gebundene
globale aktuelle Skalierungsgrundlage.

Eigene Gegenprognose:

```text
Eine isolierte entfernte Zustandslastaenderung bei konstantem lokalem
Vorzustand und lokaler Evidence veraendert NORMs lokalen Output, aber nicht
M5_DIRECT.
```

Jede entfernte direkte Outputabhaengigkeit, globale Norm oder gemeinsamer
Nenner verwirft M5_DIRECT.

## Gegenprognose gegen M1

M1 traegt mehrere gleichzeitig vorhandene feste passive Spurkomponenten pro
Ort. M5_DIRECT traegt genau eine.

Eigene Gegenprognose:

```text
M5_DIRECT kann keine zwei getrennten gleichzeitig fortbestehenden lokalen
Zeitkomponenten mit unabhaengigen Zerfallsrollen erzeugen.
```

Reproduziert M5_DIRECT dennoch den vollstaendigen Verlauf, ist fuer diesen
Vergleich keine Mehrspurrolle erforderlich. Benoetigt M5 eine zweite
Komponente, wird es verworfen und nicht zu M1 erweitert.

## Gegenprognose gegen M4

M4 traegt ein konservatives `free/bound/blocked`-Ressourcenledger und kann
lokale Konkurrenz, Blockierung und Freigabe abbilden. M5_DIRECT besitzt nur
einen lokalen Skalar ohne Erhaltungsledger.

Eigene Gegenprognose:

```text
M5_DIRECT sagt keine gesonderte Kapazitaetsbindung, Blockierung oder
Freigabetrajektorie voraus; jeder Verlauf muss allein aus seinem einen
lokalen Retentionszustand folgen.
```

Erscheint eine Ressourcenbilanz oder Rollenunterteilung, ist der Pfad nicht
mehr M5.

## Endliche Falsifikationskriterien

M5_DIRECT wird als technischer Vertreter verworfen, wenn mindestens eine der
folgenden Bedingungen eintritt:

- mehr oder weniger als eine private Koordinate pro Feldort wird getragen;
- der lokale W7-N-`LEAK`-Output wird nachtraeglich transformiert;
- der Readout oder seine Konfiguration wechselt zwischen Armen;
- ein entfernter M5-Zustand beeinflusst lokalen Output ohne Feldpfad;
- H wird aus M5 statt aus dem gemeinsamen A1-Vorschlag gebildet;
- ein M-, Edge-, Ressourcen-, Puffer- oder Replayzustand wird gelesen;
- der interne A1-Vorschlag wird als zweites Feld publiziert;
- mehr als eine Feldzeitfortschreibung entsteht;
- ein unvollstaendiges Feld oder ein Teilzustand wird ausgegeben;
- der Vertreter erst nach Ergebniskenntnis gegen einen anderen Readout
  ausgetauscht wird.

Ein spaeteres Nichtbestehen der Profilvergleiche ist ein normales negatives
Baselineergebnis, kein Implementierungsfehler und keine positive Evidenz fuer
eine hypothetische MCM-Memory.

## Aussagegrenze der Singletonfamilie

Ein gueltiger M5_DIRECT-Lauf darf spaeter nur folgende Schliessung tragen:

```text
PROFILE_REDUCIBLE_TO_DIRECT_LOCAL_SINGLE_STATE_RETENTION
```

Er darf nicht behaupten:

- alle lokalen Einzustandsmodelle seien geprueft;
- alle festen nichtlinearen Readouts seien ausgeschlossen;
- SAT oder eine offene Fitfamilie sei ausgefuehrt worden;
- eine nicht erklaerte Abweichung beweise eine neue Funktion.

Diese Aussagegrenze verhindert, dass die breite strukturelle M5-Klasse durch
einen einzelnen Vertreter ueberinterpretiert wird.

## Paketstatus

Nach S1-QL gilt:

```text
M5_DIRECT_LOCAL_STATE_FUNCTION_AND_COUNTERPREDICTIONS_BOUND
EXISTING_W7N_LEAK_KERNEL_REUSABLE
M5_COMPOSITOR_AND_ATOMIC_OUTPUT_STILL_UNBOUND
M5_EXECUTION_NOT_AUTHORIZED
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

## Aussagegrenze

S1-QL ist ein statischer Funktions- und Falsifikationsvertrag. Er bestaetigt
keine M5-Ausfuehrung, keinen Kandidaten und keinen Befund zu einer
hypothetischen MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern bleibt
unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QM - statischer M5_DIRECT-Zustands-, Kompositor-, Fehlercode- und
        Testbudgetvertrag
```

S1-QM soll ausschliesslich die vorhandene W7-N-`LEAK`-Konfiguration, den
vollstaendigen lokalen Zustand, die private A1-M5-REPLACE_S-Modulgrenze,
atomare Digests und Outputs, endliche Fehlercodes sowie ein kleines
technisches Testbudget binden. Keine neue Gleichung, Parameterwerte,
Implementierung, Fixture, Testausfuehrung, Runtimeintegration oder
Ergebnisentscheidung.
