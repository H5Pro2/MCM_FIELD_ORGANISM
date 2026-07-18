# Weltbegründete Relevanzgrenze

## Status

Darstellungsoffener Forschungsvertrag auf `E1 / RELEVANCE_BOUNDARY`.

```text
Weltursache der Relevanz:          definiert
Trennung von Wirkung und Relevanz: definiert
passive Holdout-Grenze:            definiert
Observerrolle:                     begrenzt
konkrete Weltfamilie:              noch offen
Memory-Darstellung:                offen
Runtime-Erweiterung:               gesperrt
```

Dieser Vertrag folgt aus der
[kausalen Zustandsäquivalenz](053_KAUSALE_ZUSTANDSAEQUIVALENZ.md).
Er verhindert, dass ein beliebig gespeicherter Geschichtsunterschied allein
durch einen fest programmierten Leser als Memory-Erfolg erscheint.

## Grundproblem

Ein innerer Zustand kann frühere Geschichten unterscheiden und dadurch
spätere Feldantworten verändern, obwohl diese Unterscheidung für die
Fortsetzung der Welt keine Information trägt.

```text
beliebiges Geschichtsbit
-> fest programmierter Leser
-> unterschiedliche Feldantwort
```

Damit wäre kausale Wirkung gezeigt, aber keine weltbegründete Relevanz.

Die umgekehrte Verkürzung ist ebenfalls unzulässig:

```text
Weltgeschichte korreliert mit Zukunft
-> äußerer Observer kann sie unterscheiden
```

Damit wäre Struktur der Welt gezeigt, aber noch kein inneres Memory.

Beides muss getrennt und anschließend kausal verbunden werden.

## 1. Vergangene Weltgeschichte

`H` bezeichnet ausschließlich bereits abgeschlossene lokale Weltkontakte bis
zu einer Grenze `t`.

Zulässig sind:

- lokale Rezeptorwerte;
- ihre räumliche und zeitliche Folge;
- kontaktfreie Zwischenzeiten;
- die daraus entstandene kausale Feldgeschichte.

Nicht zu `H` gehören:

- Objekt-, Personen- oder Episodenlabels;
- ein vom Versuchsleiter vergebener Zweigname;
- zukünftige Kontakte;
- eine gewünschte Antwort;
- Reward, Erfolg oder Handlungsergebnis.

## 2. Angeglichene Gegenwart

Vor der Relevanzprüfung wird der bekannte schnelle Organismuszustand `S(t)`
zwischen den Geschichtszweigen angeglichen.

```text
gleiche Anatomie und Parameter
gleiche Organismuszeitgrenze
gleiche activation
gleicher afterimage
keine offenen transienten Rezeptorabschlüsse
gleiche gegenwärtige kausal gelesene Rezeptorlage
```

Eine spätere Memory-Rolle bliebe für ihre Isolation unangetastet. Ohne eine
solche Rolle gilt die vorhandene Runtime-Null.

Damit darf zukünftige Unterscheidbarkeit nicht aus einer noch sichtbaren
schnellen Spur oder aus unterschiedlicher technischer Zeit stammen.

## 3. Noch unbekannte Weltfortsetzung

`W+` bezeichnet die reale Rezeptorfortsetzung nach `t`.

Sie muss:

- beim Aufbau des inneren Zustands noch unbekannt sein;
- aus demselben vorregistrierten Weltprozess hervorgehen wie `H`;
- ohne Rückschreibung des Forschungsobservers entstehen;
- für Bildungs- und Holdoutläufe nach derselben Regel erzeugt werden;
- vor der Ergebnisanalyse in ihrer Prüfform feststehen.

Die Runtime erhält keine Zukunftsdaten. Nur der passive Forschungsobserver
darf nach Abschluss prüfen, ob `H` Information über `W+` trug.

## 4. Weltbegründete Relevanz

Eine vergangene Unterscheidung ist weltbegründet relevant, wenn nach
Angleichung von `S(t)` die mögliche spätere Rezeptorfortsetzung noch von der
vergangenen Weltgeschichte abhängt.

In probabilistischer Schreibweise:

```text
P(W+ | H1, S(t)) != P(W+ | H2, S(t))
```

Gleichbedeutend kann geprüft werden, ob die vergangene Geschichte zusätzliche
Information über die spätere Rezeptorfortsetzung trägt:

```text
I(H ; W+ | S(t)) > 0
```

Diese Formeln sind Forschungsdefinitionen. Sie werden nicht als Zielwert,
Reward oder Updategleichung in die Runtime eingebaut.

Für deterministische Weltfamilien genügt eine engere operative Form:

```text
gleicher schneller Gegenwartszustand
+ verschiedene abgeschlossene Weltgeschichte
-> unter derselben Weltregel verschiedene mögliche Fortsetzungen
```

## 5. Keine semantische Zukunftsklasse

`W+` wird nicht als `Stuhl`, `Gefahr`, `richtig` oder `erwartet` bezeichnet.

Die kleinste zulässige Beobachtung ist die tatsächlich eintreffende
Rezeptorfortsetzung:

- neue lokale Rezeptorwerte;
- ihre zeitliche Folge;
- ihre räumliche Lage an den Docks;
- die daraus kausal entstehende Feldtrajektorie.

Der Forschungsobserver darf diese Fortsetzungen technisch vergleichen. Er
darf keine Bedeutung oder Wichtigkeit in das Feld zurückschreiben.

## 6. Drei getrennte Nachweise

### A. Weltstruktur

Nach Angleichung von `S(t)` trägt `H` auf unabhängigen Holdoutläufen
Information über `W+`.

Dieser Nachweis betrifft zunächst nur die Welt, nicht das Memory.

### B. Innere Trägerspur

Eine innere Zustandsdifferenz `M(t)` entsteht ausschließlich aus `H` und bleibt
nach Angleichung der schnellen Rollen unterscheidbar.

```text
H -> M(t)
```

Dieser Nachweis betrifft zunächst nur die Prägung, nicht ihre Wirkung.

### C. Kausale Feldvermittlung

`M(t)` verändert vor Kenntnis von `W+` die Aufnahme oder Weiterleitung der
später tatsächlich eintreffenden Rezeptorfortsetzung.

```text
H -> M(t) -> spätere Feldaufnahme von W+
```

Erst A, B und C gemeinsam tragen eine weltbegründet relevante Memory-Funktion.

## 7. Relevanz ist kein Optimierungsziel

Das Feld erhält keinen Vorhersagefehler und wird nicht auf richtige Antworten
trainiert.

Nicht eingebaut werden:

- Verlustfunktion;
- Reward;
- Sollantwort;
- globale Auswahl der besten Spur;
- Label der zukünftigen Fortsetzung;
- feste semantische Klasse;
- Rückmeldung des Holdout-Ergebnisses.

Der Forschungsobserver stellt nur nachträglich fest, ob eine aus realem
Weltkontakt entstandene innere Differenz mit der späteren Weltstruktur
zusammenhing und kausal im Feld wirkte.

## 8. Holdout statt Wiederholung desselben Ausschnitts

Eine exakt wiederholte Audio- oder Bilddatei kann durch Templatevergleich
getragen werden. Das genügt nicht.

Eine zulässige Holdoutfamilie muss:

1. dieselbe lokale Weltregel in Bildung und Probe tragen;
2. neue konkrete Rezeptorfolgen enthalten;
3. vor dem Lauf in Bildungs- und Holdoutanteil getrennt sein;
4. mehrere Weltstarts oder unabhängige Fortsetzungen enthalten;
5. den schnellen Zustand vor der Probe angleichen;
6. ohne Auswahl nach dem Ergebnis ausgewertet werden.

Damit wird nicht die exakte Vergangenheit wiedererkannt. Geprüft wird, ob eine
vergangene Feldgeschichte eine noch nicht erlebte konkrete Fortsetzung des
gleichen Weltzusammenhangs relevant unterscheidet.

## 9. Interventionslogik

Ist später eine konkrete Memory-Rolle vorhanden, sind mindestens folgende
Eingriffe nötig:

```text
M tauschen                 -> vermittelte Feldbereitschaft wandert mit
M gleichsetzen             -> vermittelte Differenz verschwindet
M nullsetzen               -> heutige Runtime-Null erscheint
Geschichtsquelle entfernen -> M-Differenz entsteht nicht
Weltstruktur permutieren   -> Relevanzbezug bricht oder wandert kanonisch mit
Wirkpfad trennen           -> M bleibt, Feldvermittlung verschwindet
Observer entfernen         -> Runtime bleibt identisch
```

Eine Wirkung, die nicht mit `M` wandert, wird nicht durch `M` vermittelt.
Eine Wirkung, die trotz zerstörter Weltstruktur unverändert bleibt, ist nicht
durch diese Weltstruktur begründet.

## 10. Notwendige Gegenmodelle

Mindestens abzugrenzen sind:

```text
B0  vollständiger heutiger schneller MCM-Zustand
B1  aktuelle Rezeptorlage
B2  Organismuszeit oder Weltphase
B3  feste Leaky-Spuren mehrerer Zeitkonstanten
B4  lokaler Übergangszähler
B5  fester endlicher Fortsetzungsautomat
B6  exakter Sequenz- oder Templatevergleich
B7  beliebiges Geschichtsbit mit festem Leser
```

B2 bis B7 können als starke Forschungsbaselines zulässig sein, ohne als
Organismusmechanik freigegeben zu sein.

Erklärt eine dieser Baselines den vollständigen Befund, ist die behauptete
offene Memory-Funktion nicht getragen.

## 11. Technische Leckgrenzen

Ein positiver Befund ist ungültig, wenn die spätere Fortsetzung bereits durch
eine technische Nebeninformation erkennbar war:

- Zweig-ID oder Dateiname;
- Weltseed ohne reale Rezeptorwirkung;
- unterschiedliche Schrittzahl oder Uhrzeit;
- nicht angeglichener schneller Zustand;
- offene Puffer oder Decoderzustände;
- Auswahl der Probe nach Sichtung der Ergebnisse;
- Observer- oder Debugrückwirkung;
- gemeinsame mutable Zustände zwischen Forschungszweigen.

## 12. Funktionale Lösung

Weltbegründete Relevanz verlangt nicht, jede frühere Unterscheidung dauerhaft
zu erhalten.

Eine innere Differenz darf funktional verschwinden, wenn weitere reale
Weltgeschichte die zuvor verschiedenen Fortsetzungslagen wieder
unterscheidungslos macht:

```text
zuvor: I(H ; W+ | S(t)) > 0

nach weiterer Weltgeschichte:
I(H ; W+ | S(t2)) = 0
```

Operativ muss dann auch die alte kausale Feldvermittlung verschwinden. Ein
verstecktes Archiv, das nur aktuell nicht gelesen wird, gilt nicht als Lösung.

## 13. Erneute Prägbarkeit

Nach funktionaler Lösung muss neue Weltgeschichte wieder eine andere
weltbegründete Unterscheidung tragen können.

Dabei darf keine feste Gewinnerkante, freie Slot-ID oder globale
Wiederbindungsregel vorgeben, wo diese neue Prägung entsteht.

Diese Bedingung bleibt Teil des späteren Memory-Lebenszyklus. Sie wird durch
die Relevanzgrenze noch nicht mechanisch gelöst.

## 14. Was dieser Vertrag trägt

Der Vertrag trägt:

- eine nicht semantische Definition weltbegründeter Relevanz;
- die Trennung von Weltstruktur, innerer Spur und kausaler Feldwirkung;
- eine passive Holdout- und Interventionsgrenze;
- die Abgrenzung gegen willkürliche Geschichtsbits;
- Lösung als mögliches funktionales Zusammenfallen.

Er trägt nicht:

- eine konkrete Memory-Variable;
- eine Updategleichung;
- eine Neuronenzahl oder Kapazität;
- einen Lernalgorithmus;
- eine semantische Bezeichnung;
- natürliche Feldtopologie;
- Reflexion, Sprache oder Handlung;
- Feldintelligenz.

## 15. Stärkstes Gegenargument

Auch eine weltstrukturierte Holdoutaufgabe kann von einem passenden festen
Automaten gelöst werden.

```text
strukturierte Welt
-> feste endliche Zustandsmaschine
-> richtige Fortsetzungsunterscheidung
```

Ein positiver Relevanzbefund beweist deshalb noch keine organische
Organisation. Er begründet nur, **welche vergangene Unterscheidung überhaupt
eine Funktion in dieser Welt haben kann**.

Die spätere Darstellungsfamilie muss zusätzlich zeigen, dass Bildung, Wirkung,
Lösung und erneute Prägung nicht bereits durch einen passenden festen
Automaten oder adressierte Speicherplätze vorgegeben sind.

## Freigabegrenze

```text
weltbegründete Relevanz definiert:          ja
Weltstruktur und Feldwirkung getrennt:      ja
passive Holdoutgrenze definiert:            ja
Reward und Semantik ausgeschlossen:         ja
aktuelle Runtime erweitert:                 nein
konkrete Weltfamilie vorregistriert:        nein
Darstellungsfamilie freigegeben:            nein
Memory-Mechanik freigegeben:                nein
```

## Nächster Schritt

Als Nächstes wird eine **minimale passive Weltfamilie** vorregistriert.

Sie muss:

- nach Angleichung des schnellen Feldzustands eine echte Abhängigkeit zwischen
  vergangener Kontaktgeschichte und späterer Rezeptorfortsetzung tragen;
- neue konkrete Holdoutfortsetzungen statt exakter Replays verwenden;
- gegen Zeit, Leaky-Spur, Übergangszähler, festen Automaten und Template
  geprüft werden;
- zunächst ausschließlich die Welt- und Beobachtungsgrenze prüfen;
- noch keine Memory-Rolle und keine Runtime-Änderung benötigen.

Erst wenn diese Weltfamilie selbst nicht tautologisch ist, darf geprüft werden,
welche kleinste offene Zustandsfamilie ihre relevante Unterscheidung lokal
tragen könnte.
