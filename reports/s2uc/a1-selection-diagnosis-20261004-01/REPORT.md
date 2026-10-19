# A1: Archivdiagnose der Auswahlentscheidung – 2026-10-04

**Ergebnis:** Eine frühere relative Fehlerüberlegenheit rechtfertigt im vorhandenen
Vertrag die Auswahl, garantiert aber keine günstige nächste Fortsetzung.
Das Archiv enthält sogar zwei vor der Prognose inhaltlich identische Verläufe
mit entgegengesetztem Nutzen derselben Auswahl. Eine allgemeine Gegenprognose,
die diese Fälle anhand zulässiger Vorhersageinformationen sicher trennt,
ist damit nicht begründbar. Für spätere Wiederverwendungen ist widersprüchliches
Feedback teilweise bereits beobachtet worden; es identifiziert jedoch ebenfalls
nicht zuverlässig den nächsten Schaden.

A1-Primärbefund ist abgenommen und bleibt negativ. A1 bleibt deaktiviert.
Keine neue Auswahlregel, Mindestmarge, Schwelle, Quellenmaterialisierung oder
Replay. Diese Diagnose liest ausschließlich das bestehende Laufarchiv.

## Belege und Kausalgrenze

[decisions.csv](decisions.csv) enthält20 Entscheidungseinträge: T1-1-3/Ziel17,
alle15 Abrufgelegenheiten der Linie1–4/Offset0 in F7 und die vier übrigen
Schadensziele aus F3/F4. [chains.json](chains.json) enthält alle38
Feedbackgelegenheiten der vier untersuchten Linien mit unverdeckter Historie,
Originalnachfolger, konkurrierenden Hypothesen und JSON-Belegstellen.
[t1-extra-five.json](t1-extra-five.json) deckt alle fünf zusätzlichen warmen
T1-Vorkommen ab. Originalidentitäten sind immer falllokal; F7 besitzt eine
entsprechende Linie1–4/Offset0, nicht dieselben Objekte wie T1.

Die Dateien trennen ausdrücklich `before_prediction` und `after_target`.
Vor Ziel t sind aktuelle Hinweise bis t−1, lebende Originalspuren, ihre
Fehlerzellen Ec/Ep und daraus abgeleitete Auswahl tatsächlich verfügbar.
Frühere Rückmeldungen wurden zu ihren Zeitpunkten verarbeitet; ihre vollständige
Liste ist Beobachterarchiv, **kein zusätzlich gespeicherter Produktionszustand**.
Der Adapter hält je Linie die zwei EMA-Werte, keine vollständige Rückmeldungshistorie
und keinen separaten Widerspruchszähler.

Ziel-t-Fehler ec/ep, tatsächliche Richtigkeit, Modalzuordnung und Nutzen gegenüber U
stehen ausschließlich rechts der Kausalgrenze. Die Modalzuordnung ist nur
Auswerterwissen und gehört auch bei früheren Zielen nicht zum Policy-Eingang.
Eine schlechte absolute Kontextvorhersage ec>0 ist von einem relativen
Widerspruch ec>ep zu unterscheiden. In den Tabellen bedeutet „frühere Nachteile“
ausschließlich bereits beobachtetes ec>ep derselben Linie.

Die Auswahl verwendet die eindeutig kleinste negative Differenz Ec−Ep unter
berechtigten warmen Hypothesen; andernfalls Persistenz. Die erste gültige
Rückmeldung setzt beide Zellen, weitere bilden jeweils0,5·alt+0,5·neu.
Diese unveränderte Arithmetik wurde nur gegen archivierte Werte geprüft;
keine Policy wurde erneut ausgeführt. JSON-Pointer in den Dateien beziehen sich
auf [das unveränderte Laufarchiv](../a1-comparison-20261004-01/closure.json).

## T1-1-3/Ziel17: vollständige Vorgeschichte

- Originalspur1–4,Offset0; gewählter Nachfolger ist **Originalframe3**.
- Hinweis5/6 führt bei6 zur Teilzulassung: Kandidat[1,1]→Retained[0,1].
  Die eingefrorene Prognose für7 ist noch kalt und verwendet Persistenz.
- **Einzige frühere Rückmeldung: Ziel7.** ec=0,08672873179117839,
  ep=0,08912928899129231. Beide Werte werden als erste Fehlerzellen gesetzt.
  Der Kontext wäre nicht exakt richtig gewesen, aber relativ etwas besser.
- Zwischen Feedback7 und der Prognose bei16 existiert kein weiteres Feedback
  dieser Originalspur-Offset-Linie. Die Zellen vor Ziel17 sind daher unverändert:
  Ec=0,08672873179117839;Ep=0,08912928899129231.
- Ec−Ep≈−0,002400557200114 bestimmt die Kontextwahl. Es gibt genau eine
  berechtigte Hypothese; kein konkurrierender Gewinner und kein Auswahlgleichstand.
- **Erst bei Ziel17 bekannt:** ec=0,08539581298828125,ep=0.
  Original3 ist weder tatsächlich richtig noch modal; U-Persistenz ist richtig.
  Nach Feedback17 lauten die Zellen[0,08606227238972983;0,04456464449564616].

Vor Ziel17 gibt es **keinen früheren relativen Widerspruch** dieser Linie.
Es gab lediglich eine ungenaue, relativ günstigere Beobachtung. Deren hohe
absolute Fehlerwerte sind vorab sichtbar, belegen aber ohne zusätzliche,
vorab begründete Annahme nicht die Richtigkeit der kommenden Persistenz.
Eine jetzt am Einzelschaden gewählte Mindestmarge wäre eine nachträgliche Anpassung.

Beleg: `chains.json → T1-1-3 → target17 → before_prediction.previous_feedback`;
Originalarchiv `T1-1-3-assessment.json#/rows/2` (Feedback7) und `#/rows/7`
(Ziel17), Receipt `T1-1-3-A1.json#/forecasts/7` (Hinweis15/16).

## F7: jede Entscheidung der entsprechenden Linie

Einheit q=1/128=0,0078125. Vor jedem warmen Abruf ist Ep/q=1.
Nach jedem Ziel ist das rohe Persistenzfeedback ep/q=1.
Ec ist der **vorherige EMA-Wert**; ec rechts ist erst nachträglich bekannt.
Δ ist A1-Fehler minus U-Fehler. Negative Werte sind Verbesserungen.

| Ziel | vorher Ec/q | frühere Nachteile bei | tatsächliche Auswahl | nachher ec/q dieser Linie | nachher Δ/q |
| --- | ---: | --- | --- | ---: | ---: |
| 7 | kalt | keine | Persistenz | 0 | 0 |
| 11 | 0 | keine | Original3 | 0 | -1 |
| 15 | 0 | keine | Original3 | 0 | -1 |
| 19 | 0 | keine | Original3 | 2 | 1 |
| 23 | 1 | 19 | Persistenz | 0 | 0 |
| 27 | 1/2 | 19 | Original3 | 0 | -1 |
| 31 | 1/4 | 19 | andere Linie: Original23 | 0 | -1 |
| 35 | 1/8 | 19 | Original3 | 0 | -1 |
| 39 | 1/16 | 19 | Original3 | 0 | -1 |
| 43 | 1/32 | 19 | Original3 | 2 | 1 |
| 47 | 65/64 | 19,43 | Persistenz | 0 | 0 |
| 51 | 65/128 | 19,43 | Original3 | 0 | -1 |
| 55 | 65/256 | 19,43 | andere Linie: Original47 | 0 | -1 |
| 59 | 65/512 | 19,43 | Original3 | 0 | -1 |
| 63 | 65/1024 | 19,43 | Original3 | 0 | -1 |

Die Linie selbst wird zehnmal gewählt: acht Verbesserungen und zwei Schäden
(19,43), keine wirkungslose Auswahl. Bei7 ist sie kalt, bei23/47 wird Persistenz
gewählt. Bei31/55 gewinnt eine andere, schon warme Originalspur mit günstigerem
Ec; diese Verbesserungen dürfen nicht als Auswahl der Linie1–4 gezählt werden.
Die betrachtete Linie erhält auch ohne eigene Auswahl Feedback, solange ihr
Ticket lebt. Die terminale Prognose65 enthält sie nicht als berechtigte Hypothese.

Vor11,15,19 besitzt die Linie exakt dieselben Fehlerzellen[0;q]. Auch Hinweise,
Originalnachfolger und Persistenzvektor stimmen für diesen Offset überein.
Vor19 wurden drei relative Erfolge7/11/15 beobachtet, kein Nachteil.
Der erste Nachteil entsteht erst19. Nach19 bleibt zunächst ein Gleichstand,
bei23 daher Enthaltung; dessen positives Feedback macht die Linie wieder günstig.
Vor43 sind frühere Nachteile bereits vorhanden, trotzdem ist Ec wieder sehr klein.
Erfolgreiche Auswahlen nach27 haben ebenfalls widersprüchliche Vorgeschichten.
Ein vergangener Widerspruch trennt also nicht einfach spätere Gewinne und Schäden.

## Gegenprüfung F3/F4

| Fall/Ziel | vorher Ec | vorher Ep | bereits beobachtete Nachteile | nachher Mehrfehler |
| --- | ---: | ---: | --- | ---: |
| F3/11 | 0 | 0,0078125 | keine | 0,0078125 |
| F3/35 | 0,0029296875 | 0,0078125 | 11,15 | 0,0078125 |
| F3/59 | 0,00311279296875 | 0,0078125 | 11,15,35,39 | 0,0078125 |
| F4/43 | 0,001953125 | 0,0078125 | 19 | 0,0078125 |

In F3 gewinnt jeweils Original3 aus Spur1–4/Offset0; in F4 gewinnt Original15
aus Spur13–16/Offset0. F4 beobachtet schon beim ersten Feedback19 einen Nachteil,
bei23/27/39 danach relative Vorteile. Bei43 ist die EMA deshalb günstig, obwohl
die Geschichte bereits widersprüchlich war. Die vollständigen Rohpaare und
Aktualisierungszeitpunkte stehen in `chains.json → F3/F4`.

## Stärkster Befund: identische Vergangenheit, verschiedene Fortsetzung

F3/Ziel11 und F7/Ziel11 besitzen **dieselben ersten zehn Wahrnehmungsframes**.
Die3.840 gespeicherten Float64-Bytes des Präfixes sind identisch. Auch sämtliche
bis dahin protokollierten Bestandsereignisse, Feedbackzeilen und Receipts stimmen
überein, bei Receipts abgesehen vom jeweiligen `profile`-Scope-Hash.
Beide wählen Original3 mit Ec=0,Ep=q; beide kennen lediglich Feedback7 mit ec=0,ep=q.
Erst Frame11 unterscheidet sich: F3-Kontextfehler2q, F7-Kontextfehler0,
Persistenzfehler jeweilsq. Entsprechend Schaden+q versus Gewinn−q.

[indistinguishable-prefix.json](indistinguishable-prefix.json) dokumentiert
Bytezahl, Präfixhash und die Gleichheitsprüfungen. Verglichen wurden ausschließlich
bereits archivierte Bytes; keine Forschungsquelle wurde erzeugt oder exportiert.
Die unterschiedlichen Profile sind Gesamtgeschichten-Digests für Scope/Provenienz.
Eine Unterscheidung nach diesen Hashes oder nach Fallnamen wäre keine inhaltliche,
kausale Gegenprognose aus Wahrnehmung und Feedback.

Damit kann weder eine andere Mindestmarge noch eine beliebige deterministische
Auswertung **dieser identischen zulässigen Vergangenheit** den Erfolg in F7/11
bewahren und zugleich den Schaden in F3/11 gezielt verhindern. Eine gemeinsame
Enthaltung wäre eine andere Risikoentscheidung und würde auch den dortigen
Gewinn aufgeben; sie ist keine Unterscheidung der beiden Fortsetzungen.
Das ist kein globaler Unmöglichkeitsnachweis für jede spätere Wahrnehmung oder
jede Forschungswelt. Es ist ein konkreter Gegenbeleg gegen sichere Trennbarkeit
im vorliegenden Informationsstand. Andere spätere Fälle haben unterschiedliche
Historien; aus deren Unterschieden wurde hier keine neue Regel abgeleitet.

## Alle fünf zusätzlichen warmen T1-Vorkommen

| Fall/Ziel | Linie → Original | vorher Ec / Ep | Auswahl | nachträgliche Einordnung und Grund für fehlenden Vorteil |
| --- | --- | --- | --- | --- |
| T1-1-1/69 | 45–48,Offset1 →48 | 0,07457558314 /0,07457558314 | Persistenz | Gleichstand; zusätzlicher Nachfolger tatsächlich falsch und nicht modal; Δ=0 |
| T1-1-3/17 | 1–4,Offset0 →3 | 0,08672873179 /0,08912928899 | Kontext | Falscher, nichtmodaler Nachfolger; Δ=+0,08539581299 |
| T1-1-3/49 | 1–4,Offset0 →3 | 0,08606227239 /0,04456464450 | Persistenz | Kontext nun schlechter geschätzt; tatsächlich falsch/nichtmodal; Persistenz richtig, Δ=0 |
| T1-1-3/51 | 1–4,Offset0 →3 | 0,08572904269 /0,02228232225 | Persistenz | Kontext weiterhin schlechter; tatsächlich falsch/nichtmodal; Persistenz richtig, Δ=0 |
| T1-1-4/73 | 45–48,Offset1 →48 | 0,08086729050 /0,08086729050 | Persistenz | Gleichstand; Kontext wäre tatsächlich richtig, aber nicht modal; Persistenz ebenfalls richtig, Δ=0 |

Zwei Gleichstände, zwei ungünstige Schätzungen, eine schädliche Kontextwahl.
Keines dieser fünf Vorkommen besitzt einen modalen Originalnachfolger.
Bei T1-1-3/51 gibt es zusätzlich eine kalte, tatsächlich richtige Kandidatenhypothese
für Original48; sie ist keine zusätzliche warme Linie und ändert die Wahl nicht.
Rundungen in dieser Tabelle dienen der Lesbarkeit; exakte gespeicherte Werte und
sämtliche vorangegangenen Rückmeldungen stehen in `t1-extra-five.json`.

## Fachliche Schlussfolgerung und nächster Schritt

Technisch erlaubt vergangene Erfahrung eine relative Fehlerprognose. Ihre erneute
Verwendung wäre inhaltlich nur unter einer tragfähigen Annahme gerechtfertigt,
dass diese Vergangenheit die aktuelle Fortsetzung noch unterscheidbar vorhersagt.
Genau das ist hier nicht allgemein belegt. Erstmalige Schäden treten ohne
vorherigen relativen Widerspruch auf; spätere Schäden und Gewinne teilen
widersprüchliche Vorgeschichten. Die zwei EMA-Werte sind weder ein Maß für
Gewissheit noch ein Nachweis stabiler Fortsetzung.

Der vorhandene Zustand trägt **keine belegte, allgemein trennende Gegenprognose**
für die untersuchten Erfolge und Schäden. Er trägt eine enger prüfbare Aussage:
Gleiches kausales Präfix kann verschiedene Fortsetzungen besitzen. Beobachtbare
Unterschiede einzelner anderer Fälle sind noch kein validierter Selektor.
Keine rückwirkend passende Mindestmarge und kein Widerspruchsfilter ist daraus
implementiert oder als geprüft behauptet.

Empfehlung an den Projektleiter: A1 als untersuchten Ansatz zur Erhaltung
abschließen und deaktiviert lassen. Vor einem weiteren Entwicklerauftrag
konzeptionell entscheiden, ob das Projekt einen begrenzten Erwartungsnutzen
unter Fortsetzungsunsicherheit akzeptieren will oder eine unabhängig begründete,
vor dem Ziel verfügbare Zusatzinformation benötigt. Erst eine konkrete
Gegenprognose mit erkennbarem Informationsunterschied rechtfertigt einen neuen
Versuchsauftrag. Keine weitere Archiv- oder Bestätigungsschleife ist erforderlich.

## Integrität und Umfang

Alle149 Dateien des Laufabschlusses wurden auf Länge und SHA256 geprüft.
Laufabschluss-SHA256:
`85ef6239c3e3fc8e161284c9ffbe19ddbdcb06bc1201e73850f04862c807a769`.
[verification.json](verification.json) belegt38 Rückmeldungsschritte,
20 Tabelleneinträge, alle fünf T1-Vorkommen, kausale Zeitgrenzen und die
Präfixgleichheit. Das Diagnoseskript verwendet nur Standardbibliotheken und
importiert weder Policy noch Replay- oder Quellgeneratorcode.
Historische Archive, Kriterien, A1-Regel und Einmallaufbindung bleiben unverändert.
