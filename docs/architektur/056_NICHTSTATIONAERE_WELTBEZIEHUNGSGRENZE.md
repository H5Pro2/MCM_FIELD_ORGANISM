# Nichtstationäre Weltbeziehungsgrenze

## Status

Darstellungsoffener Welt- und Funktionsvertrag auf
`E1 / NONSTATIONARY_WORLD_BOUNDARY`.

```text
nichtstationäre Weltursache:       definiert
Erhaltung ohne starre Zeitlage:    definiert
bedingte Wirkungslosigkeit:        definiert
erneute weltgetragene Relevanz:    definiert
Phasen- und Umschaltlabel:         ausgeschlossen
konkrete Weltfamilie:              vorregistriert
Memory-Darstellung:                offen
Runtime-Erweiterung:               gesperrt
```

Dieser Vertrag folgt aus dem
[Weltbefund der verdeckten Fortsetzung](../forschung/006_VERDECKTE_FORTSETZUNG_WELTBEFUND.md).
Die dortige Weltgeschichte ist relevant, aber eine feste Leaky-Spur, ein
Übergangszähler oder ein Bewegungsautomat kann sie bereits tragen.

Die nächste Weltgrenze muss deshalb nicht nur Bewahrung, sondern auch
Erhaltung, Lösung und erneute Relevanz unter einer real veränderlichen
Außenwelt prüfbar machen.

## 1. Grundproblem

Eine stationäre Welt macht dauerhaft dieselbe innere Unterscheidung relevant.

```text
gleiche Weltbeziehung
-> gleiche historische Information bleibt nützlich
```

Das trennt nicht:

- langlebiges Memory von einer sehr langsamen Leaky-Spur;
- lösbare Organisation von permanenter Speicherung;
- erneute Prägung von fester Rückkehr;
- weltgetragene Anpassung von einem programmierten Bewegungsautomaten.

Eine organische Memory-Funktion benötigt eine Welt, in der frühere
Unterscheidungen tatsächlich relevant werden, später ihre Relevanz verlieren
und andere Erfahrungen neue Relevanz tragen.

## 2. Nichtstationär bedeutet nicht zufällig

Die Weltbeziehung darf sich verändern, aber nicht beliebig rauschen.

Innerhalb einer begrenzten Lebensstrecke muss jeweils eine lokale Beziehung
zwischen abgeschlossener Kontaktgeschichte `H` und späterer
Rezeptorfortsetzung `W+` bestehen:

```text
P(W+ | H, S(t)) unterscheidet sich nach realer Weltgeschichte
```

Zu einem späteren Zeitpunkt darf eine andere lokale Beziehung tragen.

Die Welt bleibt kausal erzeugt. Nur ihre wirksame Fortsetzungsbeziehung ist
nicht für die gesamte Lebensdauer unveränderlich.

## 3. Ein kontinuierliches Weltleben

Die Hauptprüfung ist keine Sammlung unabhängig gestarteter Episoden.

```text
ein Weltstrom
-> wiederholte lokale Kontakte
-> kontaktarme Zwischenräume
-> reale Änderung der Fortsetzungsbeziehung
-> weitere lokale Kontakte
```

Der Organismuszustand wird zwischen diesen Abschnitten nicht zurückgesetzt,
kopiert oder neu erzeugt.

Forschungsbegriffe wie `A`, `B`, `vorher` oder `nachher` dürfen den Strom im
Bericht segmentieren. Sie sind keine Runtimeeingaben.

## 4. Zwei Weltbeziehungen ohne Bedeutungslabel

Die kleinste Grenze benötigt mindestens zwei technisch symmetrische lokale
Fortsetzungsbeziehungen `R0` und `R1`.

Die anschließende konkrete Weltfamilie übernimmt:

```text
R0: lokaler Anflug setzt sich hinter einer Verdeckung fort
R1: derselbe lokale Anflug wird hinter der Verdeckung räumlich umgelenkt
```

`R0` und `R1` sind Namen des Forschungsobservers. Der Organismus erhält weder
Beziehungs-ID noch Richtung, Regel, Umschaltzeit oder erwarteten Austritt.

Die beiden Beziehungen müssen bezüglich Energie, Dauer, Kontaktanzahl und
Geometriebudget fair sein.

## 5. Stationäre Tragephase

Zu Beginn trägt reale wiederholte Weltgeschichte die Beziehung `R0`.

Auf neuen konkreten Holdoutfortsetzungen muss gelten:

```text
I(H_R0 ; W+ | S(t)) > 0
```

Die Aussage betrifft zunächst nur die Welt. Ein späterer innerer Kandidat
müsste zusätzlich zeigen, dass seine aus Weltkontakt entstandene Lage diese
Unterscheidung vor dem Austritt kausal im Feld vermittelt.

## 6. Variable Verdeckungs- und Zwischenzeiten

Die gleiche Weltbeziehung wird über mehrere vorregistrierte physische
Zwischenzeiten geprüft.

Die Zeiten müssen:

- lang genug sein, um die heutige Rezeptionsnull anzugleichen;
- mehr als eine feste kurze Zeitlage beanspruchen;
- in Bildung und Holdout neue konkrete Werte enthalten;
- als reale Dauer und nicht nur als Schrittzahl vorliegen;
- unabhängig von der Beziehungsidentität balanciert sein.

Eine feste Leaky-Spur darf dabei einen Rest tragen. Sie bleibt eine
Pflichtbaseline und wird nicht durch eine künstliche Nullschwelle entfernt.

## 7. Reale unbezeichnete Weltänderung

Die Fortsetzungsbeziehung wechselt von `R0` zu `R1` ausschließlich in der
Außenwelt.

Der Wechsel darf nicht angekündigt werden durch:

- Phasenlabel;
- Umschaltbit;
- besondere Nullframes;
- abweichende Sensorzeit;
- neue Dock- oder Trägeridentität;
- Weltseed in der Runtime;
- Reward, Fehlerwert oder Korrektursignal.

Der Organismus kann den Wechsel erst durch neue reale Kontaktfolgen erfahren.
Eine sofort richtige Reaktion auf den ersten unerwarteten `R1`-Kontakt wird
deshalb ausdrücklich nicht gefordert.

## 8. Neue lokale Evidenz

Nach der Weltänderung treten mehrere konkrete `R1`-Fortsetzungen auf.

Sie verwenden dieselben Rezeptoren, Docks und lokalen Weltursachen wie zuvor.
Nur die tatsächlich erlebte Beziehung zwischen Anflug und späterem Austritt
hat sich verändert.

```text
keine Umschaltinformation
+ neue reale R1-Erfahrung
-> R1 wird für spätere Weltfortsetzung relevant
```

Ohne neue `R1`-Erfahrung darf keine neue innere R1-Wirkung gefordert oder als
Erfolg gewertet werden.

## 9. Bedingte Wirkungslosigkeit der alten Geschichte

Nach ausreichender realer `R1`-Geschichte muss die frühere `R0`-Geschichte für
die spätere Fortsetzung keine zusätzliche Information mehr liefern.

In Forschungsnotation:

```text
P(W+ | H_R0, H_R1, S(t2))
=
P(W+ | H_R1, S(t2))
```

oder:

```text
I(H_R0 ; W+ | H_R1, S(t2)) = 0
```

Diese Gleichheit beschreibt funktionale Lösung auf Ebene der Weltrelevanz.
Sie verlangt weder Löschbefehl noch digitalen Nullwert.

Ein späterer innerer Kandidat müsste zusätzlich zeigen, dass keine zulässige
Intervention noch eine alte `R0`-Feldwirkung freilegt.

## 10. Erneute weltgetragene Relevanz

Während `R0` bedingt wirkungslos wird, muss `R1` auf neuen Holdouts relevante
Information tragen:

```text
I(H_R1 ; W+ | S(t2)) > 0
```

Damit wird die gewünschte Funktion nicht als „Speicherplatz neu binden“
beschrieben, sondern als Änderung derjenigen eigenen Weltgeschichte, die für
spätere Feldbildung noch kausal unterscheidbar sein muss.

## 11. Keine spontane Rückkehr

Nach einer späteren kontaktarmen Zeit darf `R0` nicht allein deshalb wieder
relevant werden, weil eine feste Relaxation einen früheren Zustand
rekonstruiert.

```text
keine neue R0-Welterfahrung
-> keine erneute R0-Wirkung
```

Eine Rückkehr zu `R0` ist zulässig, wenn die Außenwelt tatsächlich wieder
`R0` trägt und neue lokale `R0`-Erfahrung erfolgt. Das wäre erneute Prägung,
nicht passive Rückkehr.

## 12. Beobachtungsprofil statt zweiter Evidenzskala

Die nichtstationäre Weltfamilie wird später über getrennte Merkmale berichtet:

```text
W  Weltabhängigkeit innerhalb R0 und R1
G  exakte schnelle Gegenwartsangleichung
E  Erhaltung über variable Zwischenzeiten
L  bedingte Wirkungslosigkeit von R0 nach R1-Erfahrung
N  neue Relevanz von R1
P  fehlende Phasen- und Metadatenlecks
H  neue konkrete Holdoutfortsetzungen
```

Dieses Profil ersetzt nicht die bestehende Evidenzskala `E0` bis `E6`.

## 13. Unverzichtbare Weltkontrollen

Mindestens erforderlich sind:

### K0: dauerhaft R0

Prüft, ob `R0` ohne Weltänderung relevant bleibt.

### K1: dauerhaft R1

Prüft die symmetrische Grundtragfähigkeit von `R1`.

### K2: R0 zu R1 ohne neue R1-Erfahrung

Nach dem äußeren Wechsel folgt noch keine beobachtbare neue
Fortsetzungsbeziehung. Hier darf keine Anpassung erwartet werden.

### K3: R0 zu R1 mit realer R1-Erfahrung

Dies ist der Hauptzweig für bedingte Wirkungslosigkeit und neue Relevanz.

### K4: permutierte Fortsetzungen

Erhält Randhäufigkeiten und Dauer, zerstört aber die lokale Beziehung.

### K5: sichtbares Umschaltsignal

Ein äußerer Cue bezeichnet den Wechsel. Diese Kontrolle zeigt, wie stark eine
triviale aktuelle Rezeptorinformation wäre. Sie ist keine Memory-Prüfung.

### K6: Rückkehr ohne neue R0-Erfahrung

Prüft passive Relaxation und zeitgesteuerte Wiederkehr.

### K7: Rückkehr mit neuer R0-Erfahrung

Prüft, ob erneute R0-Relevanz grundsätzlich wieder weltgetragen möglich ist.

## 14. Pflichtbaselines

Die spätere Auswertung muss mindestens vergleichen:

```text
B0  heutige Rezeptions- und Feldruntime
B1  mehrere feste Leaky-Spuren
B2  lokale Übergangszähler
B3  begrenzte lokale Produktspuren
B4  letzter beobachteter Austritt
B5  fester Bewegungsautomat
B6  fester Zwei-Regime-Automat
B7  Ereigniszahl oder globale Weltphase
B8  exakter Sequenz- oder Templatevergleich
B9  permanente Speicherung beider Beziehungen
```

B6 ist ein besonders starkes Gegenmodell. Kann ein fest vorregistrierter
Regimeautomat mit fairem Zustandsbudget den vollständigen Lebenszyklus tragen,
ist noch keine offene organische Organisation gezeigt.

B7 bis B9 sind keine zulässigen Runtime-Lösungen, aber notwendige
Alternativerklärungen.

## 15. Zeit- und Budgetfairness

Alle Weltbeziehungen und Baselines erhalten:

- dieselben physischen Dauern;
- dieselben Ereigniszahlen und Randhäufigkeiten;
- dieselben Reizstärken und Geometrien;
- dieselben Holdouttransformationen;
- dieselben Zustands-, Präzisions- und Leserbudgets;
- vor dem Holdout eingefrorene Parameter;
- keine Auswahl anhand späterer Antworten.

Ein Kandidat darf nicht durch mehr Zeitlagen, größere Reichweite oder
zusätzliche Weltmetadaten gewinnen.

## 16. Kausale Trennung eines späteren inneren Trägers

Falls später eine Memory-Rolle existiert, muss ihre Wirkung getrennt werden
durch:

```text
Zustand tauschen             -> Feldwirkung wandert mit
Zustand gleichsetzen         -> Geschichtsdifferenz verschwindet
Zustand nullsetzen           -> heutige Runtime-Null erscheint
R0-Geschichte entfernen      -> R0-Prägung entsteht nicht
R1-Geschichte entfernen      -> keine Lösung oder neue R1-Prägung
lokalen Wirkpfad blockieren  -> Zustand bleibt, Vermittlung verschwindet
Observer entfernen           -> Runtime bleibt identisch
```

Diese Interventionen sind Anforderungen, keine Freigabe einer Zustandsform.

## 17. Scheitergrenzen

Die Weltfamilie oder ein späterer Kandidat scheitert, wenn:

- der Wechselzeitpunkt aus Schrittzahl oder Organismuszeit ablesbar ist;
- `R0` und `R1` unterschiedliche technische Träger erhalten;
- ein Phasenlabel Bildung, Lösung oder Probe umschaltet;
- exakt dieselben Kontaktfolgen wiederholt werden;
- alte Relevanz nur durch einen Reset verschwindet;
- neue Relevanz ohne neue Weltgeschichte entsteht;
- passive Relaxation die alte Wirkung zurückbringt;
- die behauptete Lösung nur eine Leser- oder Schwellenwirkung ist;
- Weltausgang oder Holdout nach Sichtung des Feldes gewählt wird;
- Observer oder Bericht in die Runtime zurückschreibt.

## 18. Stärkstes Gegenargument

Ein fester endlicher Automat kann eine nichtstationäre Zwei-Regime-Welt
prinzipiell nachbilden:

```text
beobachteter Austritt
-> interner Regimezustand
-> erwartete nächste Fortsetzung
```

Dieser Vertrag widerlegt das nicht. Er verhindert nur, dass bereits eine
stationäre Bewegungsregel oder feste Leaky-Zeitkonstante als organisches
Memory ausgegeben wird.

Ein späterer Kandidat muss zusätzlich gegenüber einem fairen festen
Regimeautomaten zeigen, dass seine lokale Bildung, Lösung und erneute Prägung
nicht als vorgegebene Zustandsmaschine codiert wurden.

## 19. Aussagegrenze

Der Vertrag trägt:

- eine kontinuierliche nichtstationäre Weltanforderung;
- Lösung als bedingten Verlust alter Weltrelevanz;
- erneute Prägung als neue weltgetragene Relevanz;
- Schutz gegen Phasenlabel und spontane Rückkehr;
- starke statische und endliche Automatenbaselines.

Er trägt nicht:

- eine konkrete Weltimplementierung;
- eine Memory-Variable oder Updategleichung;
- eine Topologie- oder Ressourcenstruktur;
- semantische Resonanz;
- Reflexion, Sprache oder Handlung;
- Feldintelligenz.

## Freigabegrenze

```text
nichtstationäre Weltfunktion definiert:    ja
bedingte Lösung definiert:                 ja
erneute weltgetragene Relevanz definiert: ja
Phasenlabel ausgeschlossen:               ja
konkrete Weltfamilie vorregistriert:       ja
Memory-Kandidat freigegeben:               nein
Runtime-Erweiterung freigegeben:           nein
```

## Nächster Schritt

Die
[minimale kontinuierliche Zwei-Beziehungs-Weltfamilie](057_MINIMALE_KONTINUIERLICHE_ZWEI_BEZIEHUNGS_WELTFAMILIE.md)
ist vorregistriert. Sie enthält K0 bis K7, variable physische Zwischenzeiten,
verschobene Wechselstellen und B0 bis B9, ohne eine Memory-Rolle festzulegen.

Als Nächstes dürfen ausschließlich der äußere Generator, passive Observer und
die vorregistrierten Baselines umgesetzt werden. Die bestehende Rezeptor- und
Feldruntime bleibt unverändert.
