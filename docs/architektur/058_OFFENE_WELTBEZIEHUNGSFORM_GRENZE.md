# Offene Weltbeziehungsform-Grenze

## Status

Darstellungsoffener Welt- und Funktionsvertrag auf
`E1 / OPEN_RELATION_FORM_BOUNDARY`.

```text
Funktionsmangel der Zwei-Regime-Welt: definiert
nicht enumerierte Beziehungsform:    definiert
neue Beziehungswerte im Holdout:     gefordert
kontinuierliches Weltleben:          gefordert
feste Schätzerbaselines:             gefordert
konkrete Weltfamilie:                noch offen
äußerer Generator:                   gesperrt
Memory-Rolle:                        gesperrt
Runtime-Erweiterung:                 gesperrt
```

Dieser Vertrag folgt aus dem
[kontinuierlichen Zwei-Beziehungs-Baselinebefund](../forschung/007_KONTINUIERLICHE_ZWEI_BEZIEHUNGS_BASELINEBEFUND.md).

Die bisherige Welt ist nicht zu leicht, weil sie zu wenige Kontakte besitzt.
Sie ist strukturell geschlossen, weil ihre gesamte Veränderlichkeit bereits
aus zwei vorgegebenen Beziehungszuständen besteht.

## 1. Präziser Funktionsmangel

Die bisherige Welt verlangt nur:

```text
erkenne, ob zuletzt R0 oder R1 galt
```

Ein fester Zwei-Regime-Automat erfüllt diese Funktion nach einer einzigen
neuen Erfahrung vollständig.

Die offene Funktion lautet stattdessen:

> Kann eine neue lokale Fortsetzungsbeziehung aus Weltkontakt wirksam werden,
> obwohl ihre konkrete Form in keiner zuvor angebotenen Regimeliste enthalten
> war?

Damit wird keine bestimmte innere Darstellung gefordert.

## 2. Nicht „mehr feste Regime“

Unzulässig wäre:

```text
R0, R1
-> R0, R1, R2, R3, R4
```

Eine größere endliche Liste verschiebt nur die Grenze des Automaten.

Erforderlich ist eine Familie, in der konkrete Beziehungen außerhalb aller
zuvor angebotenen Beziehungswerte liegen können.

Forschungsnamen wie `R_alt`, `R_neu` oder `R_holdout` dürfen Abschnitte im
Bericht unterscheiden. Sie sind keine Identitäten, die der Organismus lesen
oder speichern darf.

## 2.1 Operationale Offenheit im digitalen Versuch

Ein endlicher digitaler Lauf enthält immer endlich viele konkrete Werte.
„Offen“ bedeutet deshalb nicht mathematische Unendlichkeit in einer
Ausführung.

Operational bedeutet es:

- Entwicklungs- und Holdoutwerte werden vor dem Lauf getrennt festgelegt;
- Holdoutwerte kommen in keiner Entwicklungsfolge vor;
- Baselineparameter werden vor Öffnung der Holdouts eingefroren;
- kein innerer Zustand wird pro konkretem Holdoutwert vorangelegt;
- ein endlicher Regimeautomat erhält nur das vereinbarte Zustandsbudget;
- Kandidat und Baselines verwenden dieselbe numerische Präzision;
- die Holdouts werden nicht nach Sichtung einer Feldantwort ausgewählt.

Der äußere Forschungsobserver darf die endliche Werteliste kennen. Organismus
und trainierbare Baselineteile dürfen sie vor dem Holdout nicht lesen.

## 3. Minimaler technischer Weltträger

Ein möglicher kleinster Träger ist eine lokale räumliche Fortsetzung:

```text
y = T(x)
```

Dabei ist:

- `x` eine sichtbare lokale Anfluglage;
- `y` eine spätere sichtbare Austrittslage;
- `T` eine Eigenschaft der verdeckten Außenwelt;
- `T` weder Rezeptorwert noch Runtimeparameter.

Eine affine Familie wäre ein zulässiger erster Prüfkandidat:

```text
T(x) = a * x + b
```

`a` und `b` sind ausschließlich Größen des äußeren Weltgenerators und des
passiven Forschungsobservers.

Diese Formel ist keine MCM-Gleichung, kein Memoryzustand und keine
vorweggenommene innere Repräsentation.

## 4. Warum mindestens zwei Freiheitsgrade

Eine reine Verschiebung

```text
y = x + d
```

kann nach einem einzigen vollständigen Kontakt durch den letzten beobachteten
Wert `d` getragen werden.

Eine Beziehung mit mindestens zwei unabhängigen Freiheitsgraden verlangt
mehrere nicht entartete Weltkontakte:

```text
(x1, y1)
(x2, y2)
mit x1 != x2
```

Erst dann ist ihre konkrete Fortsetzungsform bestimmbar.

Das beweist noch kein organisches Memory. Es beseitigt nur die vollständige
Erklärung durch einen einzelnen festen Regimewert.

## 5. Neuheit der Beziehungsform

Die spätere Beziehungsform muss außerhalb aller zuvor angebotenen konkreten
Parameterwerte liegen.

Für eine affine Prüfwelt hieße das:

```text
(a_holdout, b_holdout)
not in
{(a1, b1), ..., (an, bn)}
```

Zusätzlich dürfen weder `a_holdout` noch `b_holdout` nur ein bekanntes
Regimelabel codieren.

Der Holdout muss neue Kombinationen und mindestens einen neuen Einzelwert
enthalten.

## 6. Generalisierung innerhalb derselben neuen Beziehung

Neue Beziehungsform bedeutet nicht, dass derselbe konkrete Kontakt wiederholt
wird.

Nach realen Bildungskontakten folgen neue Anfluglagen:

```text
x_holdout not in {x1, ..., xn}
```

Die spätere Außenweltfortsetzung wird weiterhin durch dieselbe neue
Weltbeziehung erzeugt:

```text
y_holdout = T_neu(x_holdout)
```

Damit werden:

- Beziehungsbildung;
- Wiederholung konkreter Frames;
- reine Austrittsvorlage;
- und lokale Fortsetzung

getrennt.

## 7. Kontinuierliches Leben und unbezeichneter Wechsel

Der Organismus bleibt über alle Kontakte auf derselben Feldinstanz.

```text
alte offene Beziehung
-> gewöhnliche Weltkontakte
-> unbezeichneter äußerer Wechsel
-> neue nicht entartete Kontakte
-> neue Holdoutlagen
```

Verboten bleiben:

- Reset;
- Snapshot als neuer Startzustand;
- Beziehungs-ID;
- Parameterwerte in Rezeptor oder Dock;
- Umschaltbit;
- neue Uhr;
- neue Geometrie-ID;
- Ergebnis- oder Korrektursignal.

Der Wechsel kann erst aus realen neuen Kontaktpaaren erfahren werden.

## 8. Bildung, Lösung und erneute Bildung

Die offene Welt muss drei Funktionen trennen.

### Bildung

Mehrere lokale Kontakte derselben neuen Außenweltbeziehung tragen Information
über neue Holdoutfortsetzungen.

### Bedingte Lösung

Bei festgehaltener ausreichender neuer Geschichte darf die alte
Beziehungsgeschichte keine zusätzliche Information über die neue Fortsetzung
tragen:

```text
P(W+ | H_alt, H_neu, S)
=
P(W+ | H_neu, S)
```

### Erneute Bildung

Eine weitere neue Beziehungsform, deren konkrete Werte weder der alten noch
der ersten neuen Form entsprechen, muss nach eigener realer Erfahrung
Holdoutrelevanz tragen können.

Es wird keine Rückkehr zu einem gespeicherten Regimelabel gefordert.

## 9. Unverzichtbare Identifizierbarkeitskontrolle

Ein negativer Befund ist wertlos, wenn die neue Weltbeziehung aus den
angebotenen Kontakten mathematisch nicht bestimmbar war.

Die Weltfamilie muss deshalb getrennt enthalten:

```text
I0  keine neue Erfahrung
I1  entartete Erfahrung
I2  gerade ausreichend nicht entartete Erfahrung
I3  zusätzliche unabhängige Erfahrung
I4  randgleiche permutierte Paarungen
```

Bei einer affinen Welt ist beispielsweise mehrfach derselbe `x`-Wert
entartet, weil damit Steigung und Verschiebung nicht getrennt werden können.

## 10. Holdouttrennung

Mindestens drei Holdoutachsen sind erforderlich:

```text
H1  neue Anfluglage unter bekannter konkreter Beziehung
H2  neue konkrete Beziehung innerhalb der Weltfamilie
H3  neue Beziehung nach einer vorherigen anderen Lebensphase
```

H2 prüft Offenheit gegenüber nicht angebotenen Beziehungswerten.

H3 prüft, ob alte Geschichte bedingt wirkungslos werden und eine weitere
neue Form Relevanz erhalten kann.

## 11. Pflichtgegenmodelle

Eine spätere konkrete Weltfamilie muss mindestens vergleichen:

```text
A0  heutige unveränderte Feldruntime
A1  letzter beobachteter Transformationswert
A2  mehrere feste Leaky-Schätzer
A3  exakter Zwei-Punkt-Schätzer
A4  feste laufende Ausgleichsrechnung
A5  fester rekursiver Parameterschätzer
A6  endlicher Regimeautomat mit festem Zustandsbudget
A7  nächstes bekanntes Beziehungstemplate
A8  festes lokales Reservoir mit eingefrorenem Leser
A9  vollständiges Kontaktarchiv mit festem Auswertungsalgorithmus
```

Diese Gegenmodelle sind passive Forschungsinstrumente. Keines wird dadurch
als Organismusmechanik freigegeben.

## 12. Die nächste stärkere Stopplinie

Eine offene Welt widerlegt zwar einen endlichen Automaten, wenn neue
Beziehungswerte außerhalb seines Zustandsvorrats liegen.

Sie widerlegt nicht automatisch einen festen allgemeinen Schätzer:

```text
neue Kontaktpaare
-> feste Parameterschätzung
-> neue Holdoutfortsetzung
```

Falls A3, A4 oder A5 die Welt vollständig trägt, ist gezeigt:

> Die Welt verlangt eine entwickelbare Beziehungsinformation, aber noch keine
> organische Feldorganisation.

Das wäre ein wichtiger Fortschritt gegenüber B6, aber noch keine Freigabe
einer MCM-Memory-Mechanik.

## 13. Architekturgrenze eines späteren Kandidaten

Ein späterer innerer Kandidat darf nicht erhalten:

- Parameterplätze mit den Namen `a`, `b` oder `T`;
- eine feste Beziehungs-ID;
- eine bekannte Anzahl möglicher Beziehungen;
- eine vorgegebene Auswahlregel;
- eine Zieltopologie;
- einen Fehler gegen den späteren Austritt;
- einen Observerwert als Rückschreibesignal.

Seine mögliche Wirkung müsste ausschließlich aus lokalen Weltkontakten,
vorhandenem Eigenzustand und lokaler Feldwirkung entstehen.

Diese Forderung wählt noch keine Datenform oder Gleichung.

## 14. Kausale Mindestprüfung eines späteren Trägers

Falls später ein innerer Träger untersucht wird, muss getrennt werden:

```text
Träger tauschen
-> Feldwirkung wandert mit

Träger gleichsetzen
-> Geschichtsdifferenz verschwindet

neue Beziehungsgeschichte entfernen
-> neue Wirkung entsteht nicht

alte Geschichte variieren bei gleicher neuer Geschichte
-> neue Holdoutwirkung bleibt gleich

lokalen Wirkpfad blockieren
-> Träger bleibt, vermittelte Feldwirkung verschwindet
```

Das ist eine spätere Zulässigkeitsgrenze, keine aktuelle
Implementierungsfreigabe.

## 15. Scheitergrenzen

Die offene Weltgrenze scheitert, wenn:

- nur weitere feste Beziehungs-IDs ergänzt werden;
- alle späteren Parameterwerte bereits in Bildungsläufen vorkommen;
- ein einzelner Kontakt die gesamte Beziehung trivial offenlegt;
- Bildung und Holdout dieselben konkreten Anfluglagen verwenden;
- Parameter oder Phasen in die Runtime gelangen;
- ein globaler Takt die Beziehungsform verrät;
- alte Relevanz nur durch Reset verschwindet;
- neue Wirkung ohne neue Weltkontakte entsteht;
- die Welt nach Sichtung des Feldzustands angepasst wird;
- ein fester Schätzer nicht als Gegenmodell zugelassen wird.

## 16. Aussagegrenze

Dieser Vertrag trägt:

- den präzisen Funktionsmangel der Zwei-Regime-Welt;
- Nichtenumerierbarkeit als neue Weltanforderung;
- neue Beziehungswerte und neue Anfluglagen als getrennte Holdouts;
- Identifizierbarkeit als Pflichtkontrolle;
- eine stärkere Baselinegrenze gegenüber allgemeinen Schätzern.

Er trägt nicht:

- eine konkrete affine Weltimplementierung;
- eine MCM-interne Transformationsdarstellung;
- eine Memory-Variable;
- eine Updategleichung;
- organische Feldorganisation;
- semantische Resonanz;
- Reflexion, Sprache oder Handlung;
- Feldintelligenz.

## Freigabegrenze

```text
offene Weltfunktion definiert:          ja
konkrete Weltfamilie vorregistriert:    nein
äußerer Generator freigegeben:          nein
passiver innerer Kandidat freigegeben:  nein
Memory-Rolle freigegeben:               nein
Runtime-Erweiterung freigegeben:        nein
```

## Nächster Schritt

Der
[Audit von affiner und lokaler Deformationswelt](059_AUDIT_AFFINE_UND_LOKALE_DEFORMATIONSWELT.md)
ist abgeschlossen. Die affine Fortsetzung wird als Hauptwelt verworfen, weil
ein exakter Zwei-Punkt-Schätzer ihre globale Form vollständig trägt. Sie
bleibt als Baseline erhalten.

Als nächster Weltträger ist eine lokal stetige, nachweislich nichtaffine
Deformationswelt bedingt zugelassen. Vorregistrierung, Generator und
Feldruntime bleiben noch geschlossen.
