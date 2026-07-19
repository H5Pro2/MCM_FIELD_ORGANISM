# Minimale lokal stetige Deformationswelt

## Status

Vorregistrierter äußerer Weltträger auf
`E1 / LOCAL_DEFORMATION_WORLD_PREREGISTERED`.

```text
konkrete Weltgeometrie:                 festgelegt
lokal stetige nichtaffine Formen:       festgelegt
Bildungsstufen D0 bis D5:               festgelegt
Lebens- und Kontrollgruppen:            festgelegt
Baselines L0 bis L9:                    bindend
äußerer Generator:                      umgesetzt
passive Observer und L0 bis L9:         umgesetzt
Memory-Rolle und Feldruntime:            gesperrt
```

Diese Vorregistrierung folgt aus dem
[Weltträgeraudit](059_AUDIT_AFFINE_UND_LOKALE_DEFORMATIONSWELT.md).
Sie beschreibt ausschließlich eine äußere Prüfwelt und passive Auswertung.
Sie wählt keine innere Darstellung und keine Lernmechanik.

## 1. Forschungsfrage

Kann eine lokal verteilte, neue Fortsetzungsbeziehung nach realen Kontakten
Holdouts zwischen erfahrenen Lagen tragen, ohne dass ihre konkrete Form als
Regime, Klasse oder Parameter in der Runtime vorliegt?

Die Welt ist bewusst so gewählt, dass eine feste stückweise lineare
Interpolation sie nach vollständiger lokaler Erfahrung voraussichtlich exakt
erklärt. Ein solcher Baselinesieg ist der erwartete Grenzbefund und keine
Freigabe für organisches Memory.

## 2. Äußere Geometrie

Die visuelle Welt besitzt dreizehn diskrete lokale Positionen:

```text
x in {0, 1, ..., 12}
```

Ein vollständiger Weltkontakt besteht aus:

```text
sichtbarer Eintritt x:          20 ms
verdeckter Weltabschnitt:       30, 50 oder 80 ms
sichtbarer Austritt y:          20 ms
kontaktarmer Zwischenraum:      30, 60 oder 90 ms
```

Alle Kontakte laufen im selben fortgesetzten Feldzustand. Es gibt keinen
Reset zwischen Kontakten, Formen oder Holdouts. Die Zeiten werden über die
Gruppen balanciert und bezeichnen weder Form noch Bildungsstufe.

## 3. Lokale Deformationsformen

Jede äußere Form wird für den Forschungsobserver durch vier Stützpaare an den
Positionen `0`, `4`, `8` und `12` definiert:

```text
Form  y(0)  y(4)  y(8)  y(12)
F0      1     3     9      11
F1      0     6     8      12
F2      2     4    10      12
F3      0     4     6      12
```

Zwischen benachbarten Stützstellen ist die äußere Welt linear. Die gesamte
Form ist jedoch nicht affin, weil ihre lokalen Steigungen wechseln.

Stützstellen, Formnamen und Steigungen existieren nur im äußeren Generator
und im passiven Observer. Der Organismus erhält ausschließlich sichtbare
Rezeptorkontakte.

## 4. Holdouts

Die neuen Eintrittslagen liegen zwischen den Stützstellen:

```text
Holdout x:       2   6   10
F0-Austritt:     2   6   10
F1-Austritt:     3   7   10
F2-Austritt:     3   7   11
F3-Austritt:     2   5    9
```

Keines dieser vollständigen Holdoutpaare darf zuvor als Bildungskontakt der
jeweiligen Form vorkommen. Die Austritte werden vor dem Lauf allein aus der
äußeren Form bestimmt, nicht nach Sichtung einer Feldantwort.

## 5. Operationale Offenheit

Ein digitaler Versuch bleibt endlich. Offenheit bedeutet hier:

- `F0` und `F1` dienen Entwicklung und stationären Kontrollen;
- `F2` und `F3` sind davon getrennte Formholdouts;
- `F2` und `F3` werden erst durch eigene reale Kontakte innerhalb ihres
  fortlaufenden Weltlebens erfahrbar;
- Baselinealgorithmen und Parameter werden vor Öffnung ihrer Holdouts
  eingefroren;
- es existiert kein innerer Zustand pro Form, Holdoutwert oder Stützstelle;
- Formnamen und Bildungsstufen erreichen die Runtime nicht.

Damit ist keine mathematische Unendlichkeit behauptet. Geprüft wird eine neue
konkrete lokale Beziehung außerhalb der vorher angebotenen Formen.

## 6. Bildungsstufen D0 bis D5

Die Stufen sind Beobachtungsgrenzen, keine programmierten Lernschwellen.

```text
D0  kein vollständiger Kontakt der neuen Form
D1  ein Stützpaar
D2  zwei nicht entartete Stützpaare bei x = 0 und x = 12
D3  drei Stützpaare bei x = 0, 4 und 8
D4  alle vier Stützpaare
D5  randgleiche Paarungspermutation der vier Stützpaare
```

Für D3 ist die Nichtaffinität bei jeder Form exakt nachweisbar. Die mittlere
Stützstelle liegt nicht auf der Geraden durch die beiden äußeren Punkte.

Die Reihenfolge innerhalb einer Stufe wird balanciert. Ereigniszahl,
Kontaktzeit und Reihenfolge dürfen keine Formkennung liefern.

Holdouts werden nur dort ausgewertet, wo die Identifizierbarkeit fair ist:

```text
D0: keine Anpassungsforderung
D1: nur Punktnähe, keine Formfortsetzung
D2: affine Gegenhypothese zulässig
D3: x = 2 und x = 6 innerhalb erfahrener Intervalle
D4: x = 2, x = 6 und x = 10
D5: keine richtige lokale Fortsetzung erwartet
```

## 7. Lebens- und Kontrollgruppen

```text
G0  stationäre F0- und F1-Leben
G1  stationäre F2- und F3-Leben über D0 bis D4
G2  F0 -> F2 über D0 bis D4
G3  F1 -> F3 über D0 bis D4
G4  F0 -> F2 -> F3; erneute lokale Bildung
G5  verschiedene alte Geschichten, identische neue F2-Geschichte
G6  verschobene Wechselstellen sowie balancierte Kontakt- und Pausenzeiten
G7  D5 mit erhaltenen x- und y-Randverteilungen
```

G5 prüft die Lösung alter funktionaler Relevanz:

```text
gleiche neue lokale Geschichte
+ unterschiedliche alte Geschichte
-> gleiche neue Holdoutfortsetzung
```

G4 prüft nur, ob nach einer weiteren realen Weltänderung erneut lokale
Information getragen werden müsste. Es fordert keine sofortige Umschaltung.

## 8. Randgleiche Paarungspermutation D5

D5 erhält dieselben Mengen der Eintritts- und Austrittslagen, ordnet die
Paare aber so um, dass die lokale stetige Zuordnung zerstört wird.

Damit werden Randhäufigkeit, Positionsenergie, Kontaktzahl und Zeitaufwand von
der tatsächlichen lokalen Paarbeziehung getrennt. Eine D5-Antwort darf nicht
als gelernte Form gedeutet werden.

## 9. Pflichtbaselines

```text
L0  heutige unveränderte Feldruntime
L1  letzter lokaler Verschiebungswert
L2  affine Zwei-Punkt-Fortsetzung
L3  feste lineare Nachbarschaftsinterpolation
L4  feste stückweise lineare Interpolation
L5  feste lokale Polynominterpolation
L6  feste rekursive lokale Ausgleichsrechnung
L7  nächstes bekanntes Deformationstemplate
L8  festes lokales Reservoir mit eingefrorenem Leser
L9  vollständiges Kontaktarchiv mit festem Interpolator
```

Ein endlicher Formautomat mit festem Zustandsbudget bleibt zusätzliche
Kontrolle. L4 wird bei D4 voraussichtlich alle Holdouts exakt tragen. Bei D3
darf L4 nur in bereits durch Nachbarstützstellen begrenzten Intervallen wirken.

## 10. Messungen

Der passive Observer protokolliert getrennt:

- vollständige äußere Kontaktgeschichte;
- bekannte schnelle Feldzustände vor jedem Holdout;
- Holdoutantwort der unveränderten Runtime;
- Antwort und Fehler jeder Baseline;
- alte und neue Weltgeschichte ausschließlich außerhalb der Runtime;
- Gleichheit der Randverteilungen in D5;
- Reproduzierbarkeit bei vertauschter Ausführungsreihenfolge.

Formkenntnis, Sollfehler und Baselineausgabe schreiben niemals in das Feld
zurück.

## 11. Leck- und Kausalitätskontrollen

Unzulässig in Runtime oder Snapshot sind:

- Form-ID oder Phasen-ID;
- Bildungsstufe oder Stützstellen-ID;
- erwarteter Austritt oder Holdoutmarkierung;
- Interpolationsgewicht, lokale Steigung oder `L`;
- Umschaltzeit;
- Fehler-, Reward- oder Gewinnerwert;
- Rohbildarchiv für spätere Suche.

Neue Austrittskontakte dürfen im selben atomaren Schritt keine rückwirkende
Vorhersage erzeugen.

## 12. Vorregistrierte Erwartung

Die stärkste erwartete Erklärung lautet:

```text
vollständige lokale Stützgeschichte
-> feste stückweise lineare Interpolation
-> exakte lokale Holdoutfortsetzung
```

Falls dies eintritt, ist gezeigt, welche lokal verteilte
Beziehungsinformation die Weltfunktion benötigt. Nicht gezeigt ist, dass das
MCM-Feld diese Information organisch bildet oder als eigenes Memory trägt.

## 13. Stopplinie

Kein Memory-Kandidat wird geöffnet, wenn:

- L4 oder L9 die entscheidenden Holdouts vollständig erklärt;
- eine Form-ID, Stützstelle oder Phase in die Runtime gelangt;
- der Effekt nur aus einem expliziten Kontaktarchiv stammt;
- D5 trotz zerstörter Paarbeziehung gleich behandelt wird;
- technische Reihenfolge das Ergebnis verändert;
- alte Wirkung nur durch Reset verschwindet;
- ein Kandidat eine fest programmierte Interpolation nachbildet.

Auch ein Scheitern aller Baselines gibt keine Mechanik automatisch frei. Es
würde zunächst nur eine unvollständige Gegenmodellmenge anzeigen.

## 14. Aussagegrenze

Die Vorregistrierung trägt die konkrete Außenwelt, getrennte Form- und
Positionsholdouts, D0 bis D5, G0 bis G7 und die bindenden Baselines L0 bis L9.

Sie trägt weder organisches Memory noch entwickelte Feldtopologie,
semantische Resonanz, Reflexion, selbstständige Regulation oder
Feldintelligenz.

## Freigabegrenze

```text
konkrete Weltfamilie vorregistriert:    ja
äußerer Generator freigegeben:          ja, nur passiv nach diesem Vertrag
passive Observer und L0 bis L9:         ja
Memory-Kandidat freigegeben:            nein
Runtime-Erweiterung freigegeben:        nein
```

## Nächster Schritt

Generator und Baselines sind inzwischen umgesetzt. Der
[Baselinebefund](../forschung/008_LOKALE_DEFORMATIONSWELT_BASELINEBEFUND.md)
zeigt, dass L4 alle 110 fair identifizierbaren Holdouts exakt trägt.

Als Nächstes wird vor jeder inneren Mechanik ausschließlich der verbleibende
Funktionsmangel gegenüber dieser festen Interpolation bestimmt. Die heutige
Feldruntime bleibt unverändert.
