# S2-SP: Statischer Plan zur Positionsvariation durch Speicherung und Abruf

**Status:** Der öffentliche Positionsabruf bleibt gesperrt. Der aktuelle
Forschungsweg erlaubt ausschließlich einen privaten read-only Vergleich des
S2-SP-Teilstrukturhinweises mit tatsächlich gebildeten Memorykandidaten.
Quellen, Folge, Ressourcen und neutraler Anschluss werden vor dessen einem
gebundenen Vergleich festgeschrieben. Gates bleiben außerhalb der neutralen
Qualifikation und des separat gebundenen Vergleichs `False`.

## Frage und Aussagegrenze

Prüffrage: Bleibt ein visuelles Muster, das im Bild horizontal verschoben ist,
nach Bildung und festen konkurrierenden Eindrücken über den unveränderten
Memory- und Teilhinweispfad nutzbar?

Geprüft werden ausschließlich lokale RGB-Rezeptorwerte, bestehende
Memorytransaktionen und die bestehende visuelle Teilhinweisregel. Ein positiver
Befund wäre eine begrenzte Nutzbarkeit dieser gebundenen Positionsvariation;
er wäre weder Objektidentität noch Invarianz gegenüber Perspektive, Beleuchtung
oder Verdeckung.

## Vorhandener Ausgangspunkt und Quellenstatus

Der abgeschlossene S2-SFA-Methodenversuch enthält bereits einen direkten,
sequenzweisen Rohvergleich: `QA` (Muster A an verschobenen Positionen) wurde
gegen `RA` und `RB` korrekt A zugeordnet. Er verwendet vier Frames pro Folge
und den Mittelwert über 288 Rezeptorwerte je Frame. Dieser Beleg bleibt
unverändert und zeigt begrenzte direkte Unterscheidbarkeit im Rezeptorraum.
Er zeigt **nicht**, dass ein einzelnes MCM-Formationsereignis dieselbe
Einzelbildbeziehung trägt oder dass der Memoryabruf sie verwendet.

Der spätere Bestand verwendet deshalb nur die bereits festgelegte
Farbmuster-Rezeptfamilie, nicht die historischen SFA-Payloads. Die
Rezeptentscheidung ist vor jeder Materialisierung fest: Das Rechteck liegt in
der obersten Rasterzeile und überdeckt exakt eine Rasterzelle (`160 × 135`,
`y=0`). Damit erhält die unveränderte Maske `0…31` tatsächlich
Vordergrundinformation.

| Technische Rolle außerhalb der Runtime | Rezept | Zweck |
| --- | --- | --- |
| `A0` | Muster A, Hintergrund `(24,32,48)`, Rechteck `160 × 135`, `y=0`, `x=0` | unveränderte Referenzposition |
| `A1` | dasselbe Muster A und dieselbe Geometrie, nur `x=160` | feste horizontale Positionsvariation |
| `B1` | Muster B, gleiche Geometrie wie A1 | anderes Muster an der Variantenposition |

Muster A und B entsprechen den bestehenden SFA-Farben A `(224,64,64)` und B
`(64,224,64)`. Die Palette und die reine Rasterrezeptform werden damit
wiederverwendet; die konkrete Geometrie, alle Quellenidentitäten, Zeiten und
Payloadbindungen wären neu. Historische SFA-Payloads und Rezeptorwerte werden
nicht übernommen. Die drei Rollen gehören ausschließlich in die spätere
Evaluationswurzel. Ein gemeinsames, bereits qualifiziertes Audiofenster kann
für alle vollständigen AV-Formationen unverändert bleiben; es trägt keine
Rolleninformation.

## Unveränderte technische Regeln

- Halbprofil, Rezeptoren, Feld-/Memorytrennung, B4/Fast/PPB-Kapazitäten,
  Schwellen, Rangschlüssel und Updates bleiben unverändert.
- Die direkte Wahrnehmungsbaseline verwendet ausschließlich den gebundenen
  vollen visuellen Rezeptorvektor und die historische Reihenfolge
  `sum(abs(q[i] - r[i])) / 288` über Originalindizes `0…287`.
- Der Teilhinweis bleibt der bestehende visuelle KQ-Exaktvergleich auf den
  Originalpositionen `0…31`; sein Komplement bleibt verdeckt. Es gibt keine
  Positionsnormalisierung, keine neue Maske und keine Vollvektor-Umgehung im
  produktiven Scan.
- Hinweise lesen Memory nur vor einer Formation und schreiben weder Support,
  Prototyp noch Generation fort. Öffentliche Hypothesen bleiben unangewandt.

## Gebundene Folge

Die folgende Folge ist nur eine hypothetische Ablaufhülle. Sie bleibt innerhalb
des vorhandenen privaten Eininstanzrahmens: 19 Ereignisse, 13 vollständige
AV-Formationen und sechs visuelle Hinweise.
Damit unterschreitet sie die bestehenden Obergrenzen von 28 Ereignissen,
20 Formationen und sechs visuellen Hinweisen. Die konkreten Feldkontakt-,
Zeit- und Belegbudgets müssen vor einer späteren Umsetzung aus den tatsächlichen
Modalitätsfenstern und der gewählten Eininstanzhülle gebunden werden; sie sind
durch diese Zählung nicht bereits nachgewiesen.

| Ereignisse | Eingang | Zweck außerhalb der Runtime |
| --- | --- | --- |
| e01 | vollständiges AV `A0` | erste Zielbildung |
| e02 | visueller Teilhinweis `A0` | unmittelbare Referenzkontrolle, read-only |
| e03–e05 | je vollständiges AV `A0` | drei weitere, gleiche Bildungen; Prüfung der bestehenden Stabilisierung |
| e06 | visueller Teilhinweis `A0` | Abruf nach Stabilisierung, read-only |
| e07 | visueller Teilhinweis `A1` | unmittelbare Positionskontrolle vor Konkurrenz, read-only |
| e08–e16 | je vollständiges AV `B1` | feste Konkurrenzfolge; kann A0 verdrängen oder B1-Prototypen fortschreiben |
| e17 | visueller Teilhinweis `A0` | Erhaltung nach B4-/Fast-Druck, read-only |
| e18 | visueller Teilhinweis `A1` | positionsveränderte Prüfung nach Konkurrenz, read-only |
| e19 | visueller Teilhinweis `B1` | Konkurrenzkontrolle, read-only |

Nach e16 liegen die letzten neun B4-Formationen ausschließlich bei `B1`; die
A0-B4-Einträge sind damit nicht mehr aktuell. A0 und B1 belegen nur zwei der
vier visuellen Slow-Slots, **falls** die bestehende Regel B1 als getrennte
PPB-Spur anlegt. Das ist ebenso wie eine A0-Erhaltung eine Vorhersage, kein
Startgate: B1 kann nach den tatsächlichen Matchregeln auch einen vorhandenen
Prototyp aktualisieren. Der bestehende Fast-Ablauf bleibt eine tatsächliche
Folge der Transaktionen, kein Erfolgsgate. Erwartete Inventare und
Entscheidungen stehen ausschließlich in der Evaluationswurzel.

## Drei getrennte Ebenen

### 1. Direkte Vergleichbarkeit

Vor jedem Memoryurteil würde der spätere Auswerter für die vorgebundenen Paare
`A0/A0`, `A0/A1`, `A0/B1`, `A1/B1`, `B1/B1` nur die volle 288-Werte-Direktbaseline
anwenden. Sie berichtet Gleichheit und die strikte Rangbeziehung von A1 zu A0
gegen B1, ohne daraus eine Abrufschwelle abzuleiten. Der bestehende
SFA-Sequenzbefund bleibt dabei eine historische Ergänzung, keine ersetzende
Einzelbildrechnung.

Zusätzlich prüft eine getrennte, nichtproduktive Kopie der bestehenden
32-Komponenten-Cueform `A1` gegen den originalgebundenen A0-Formationsvektor
und gegen B1. Damit ist vor einem Memoryschluss sichtbar, ob bereits die feste
Teilansicht einen Kandidaten ausschließt. Diese Kontrolle verwendet keine
gespeicherten Rollen und nimmt keine Scan- oder Entscheidungshelfer aus dem
produktiven Pfad. Für die gewählte zellgenaue Geometrie ist bereits statisch
klar: A0 und A1 unterscheiden sich auf beobachteten Maskenpositionen. Der
unveränderte visuelle Exaktvergleich kann A1 daher nicht als A0 zulassen. Die
offene Gegenprognose betrifft nur die Vollvektor-Direktbaseline: Sie kann A1
gegenüber B1 noch näher an A0 oder nicht näher an A0 einordnen. Keine dieser
beiden Möglichkeiten öffnet den unveränderten Exaktabruf für A1.

### 2. Erhaltung

e02, e06 und e17 würden die echten, jeweils vorherigen Zustände vergleichen. Die
Formationseingänge, B4-/Fast-/visuellen-PPB-Generationen, Support, Ersetzung
und die aktuelle Verfügbarkeit werden mit den vorhandenen direkten
Zustands- und Transaktionsbaselines geprüft. e17 trennt insbesondere eine
stabilisierte A0-Spur nach B4-Verdrängung von einem lediglich unmittelbaren
A-Treffer.

### 3. Abruf

Jeder der sechs Hinweise würde den unveränderten vollständigen Scan und
die unabhängige Direktbaseline. Kandidatenanwendbarkeit, interne Konflikte,
öffentliche Hypothese oder Enthaltung bleiben getrennte Ergebnisse. e07 zeigt
vor jeder Konkurrenz, dass die gewählte Ortsveränderung bereits den Exaktabruf
ausschließt. e18 kann daher keinen Positionsgewinn des unveränderten Pfads
belegen; e19 bleibt nur eine Konkurrenzkontrolle.

## Ergebnisentscheidung

| Beobachtung | Einordnung |
| --- | --- |
| Die volle 288-Werte-Baseline trennt A1 nicht von B1. | Die gewählte direkte Wahrnehmungsbewertung trägt die Positionsfrage nicht; aus Memorybefunden folgt dann kein Speicherurteil. |
| Die Vollvektorbaseline trennt, aber die 32-Komponenten-Cuekontrolle verwirft A1 bereits gegen A0. | Die Grenze liegt an Teilansicht oder gebundener Vergleichsregel, nicht an nachfolgender Speicherung. Dies ist für die gewählte Geometrie statisch zu erwarten. |
| e07 verwirft A1 schon vor der Konkurrenz. | Kein offener Positions-Memorytest: Der unveränderte Exaktabruf schließt die Variation konstruktiv aus. Ein späterer e18-Befund wäre keine Aussage über Erhaltung. |
| e02/e06/e17 bestätigen A0. | Begrenzte Erhaltung der unveränderten Position unter Konkurrenz; keine Aussage über Positionstransfer. |
| e19 lässt B1 als A0 zu, oder ein bestätigter A0-Abruf geht verloren. | Fehlzulassung beziehungsweise Verlust; ein möglicher Gewinn wird nicht verrechnet. |

Fehlen Kandidatenherkünfte oder sind sie generationell nicht eindeutig, bleibt
die zugehörige Auswertungszelle `null`; sie wird nicht durch Rollenwissen
ersetzt. Gleichstände und technisch gültige Enthaltungen sind reguläre
Ergebnisse.

## Vorhandene Deckung und kleinster fehlender Anschluss

Vorhanden sind: der rezeptorfreie Farbmusterbeleg, der direkte SFA-Rohvergleich
als Sequenzkontrolle, der private Halbprofil-AV-Pfad, generationstreue
Eininstanzbildung, read-only Hinweise sowie unabhängige Zustands- und
Slotscanbaselines. Nicht vorhanden ist ein unveränderter Abrufanschluss, der
eine auf beobachteten Cuepositionen veränderte Ortslage als denselben Kandidaten
behandeln darf. Genau das schließt die bestehende Exaktregel aus.

**Entscheidung:** Diese Ablaufhülle wird nicht implementiert oder qualifiziert.
Sie würde eine bereits statisch bekannte Masken- und Exaktvergleichsgrenze
wiederholen, nicht den Übergang von direkter Positionsinformation zu
gespeicherter Erfahrung prüfen. Die verbleibende offene Gegenprognose ist die
Vollvektor-Rangbeziehung A1 zu A0 gegenüber B1; sie ist eine reine
Wahrnehmungsfrage und begründet ohne einen späteren, fachlich gerechtfertigten
Variantenvergleich keinen Memoryanschluss.

## Nachtrag: Statischer positionskompensierter visueller Vergleich

Dieser Nachtrag beschreibt nur einen möglichen privaten Vergleich vor jeder
späteren Implementierungsentscheidung. Der bestehende Exaktvergleich bleibt
die unveränderte Baseline. Es entsteht keine Memoryänderung, keine neue
allgemeine Distanzschwelle und keine Vervollständigung verdeckter Werte.

### Tatsächlich sichtbare Information

Die Reihenfolge des visuellen Rezeptors ist Zeile, Spalte, RGB-Kanal. Die
Positionen `0…31` enthalten daher zehn vollständige RGB-Zellen der oberen
Rasterzeile (Spalten 0 bis 9) sowie nur Rot und Grün der Spalte 10. Die
unvollständige Zelle darf nicht als Vergleichsfläche dienen. Die zwölfte
Spalte und alle unteren Rasterzeilen sind verdeckt.

Die 32-Komponenten-Sicht reicht damit allenfalls für eine **ganzzahlige
gemeinsame horizontale Verschiebung einer beobachteten Teilstruktur** innerhalb
dieser zehn vollständigen Zellen. Sie reicht nicht für eine allgemeine
Bildpositions- oder Objektinvarianz. Die zunächst vorgeschlagene Grenze von
drei vollständigen RGB-Zellen und zwei unterschiedlichen Tripeln ist ein
unbegründeter Entwurfsparameter: Sie schließt nur eine vollständig konstante
Überdeckung aus, nicht eine Verwechslung verschiedener Hintergründe oder
Gesamtmuster.

### Feste Vergleichsvorschrift

Für Cue und Kandidat werden ausschließlich die vollständigen beobachteten
Zelltripel der oberen Zeile gelesen. Der Vergleich enumeriert alle ganzzahligen
horizontalen Offsets, für die die gewählte Mindestüberdeckung vollständig
sichtbar ist. Für jeden Offset gilt:

1. Nur die überlappenden vollständigen Tripel werden positionsweise exakt
   verglichen.
2. Es werden keine Werte aus dem maskierten Bereich, aus unvollständigen
   Zellen oder aus dem Kandidaten außerhalb der Überdeckung ergänzt.
3. Eine Teilstrukturübereinstimmung läge nur bei genau einem Offset vor,
   dessen gesamte gewählte Überdeckung exakt gleich ist.
4. Kein Offset ergibt `ABSTAIN_SHIFT_OVERLAP_INSUFFICIENT` oder
   `ABSTAIN_SHIFT_NOT_APPLICABLE`; mehrere gleichwertige Offsets ergeben
   `ABSTAIN_SHIFT_AMBIGUITY`.

Der Offset wird allein aus den sichtbaren Rezeptorwerten bestimmt. Er trägt
keine Quellenrolle, Zielposition oder vorherige Auswertungszuordnung. Er wäre
eine begrenzte geometrische Teilstrukturprüfung, keine gelernte Beziehung und
keine Rekonstruktion einer vollständigen Wahrnehmung.

### Konkreter Gegenfall

Nehmen wir für die zehn vollständig sichtbaren Zellen von Cue und Kandidat
einen Offset von sieben Zellen an. Die Dreizellüberdeckung sei im Cue
`(rot, grün, blau)` in den Spalten 0 bis 2 und im Kandidaten dieselbe Folge in
den Spalten 7 bis 9. Die übrigen sichtbaren Kandidatenzellen 0 bis 6 tragen
jedoch eine andere Folge, etwa `(gelb, cyan, magenta, …)`, die im Cue nicht
entspricht. Der Cue kann zugleich außerhalb seiner Spalten 0 bis 2 weitere,
vom Kandidaten verschiedene sichtbare Zellen haben.

Die vorgeschlagene Dreizellregel würde diesen eindeutigen Offset zulassen,
obwohl Cue und Kandidat als vollständige beobachtete Zeile verschieden sind.
Zwei unterschiedliche Tripel in der Überdeckung ändern daran nichts. Die
Regel kann die außerhalb der verglichenen Fläche sichtbaren Unterschiede nicht
als Gegenbeleg verwenden, ohne ihre Vergleichsfläche zu verändern. Der Treffer
belegt deshalb nur: **Diese beobachtete Teilstruktur passt bei diesem Offset.**
Er belegt nicht, dass der gespeicherte Gesamtinhalt wiedererkannt wurde.

### Gegenfälle und Verwerfungsbedingung

| Fall | Erwartete Behandlung |
| --- | --- |
| Dasselbe mehrfarbige Muster, um eine ganze sichtbare Zelle verschoben | Kann eine eindeutige beobachtete Teilstrukturübereinstimmung liefern; keine Gesamtwiedererkennung. |
| Anderes Muster oder andere Vordergrundfarbe bei gleicher Verschiebung | Wird nur abgewiesen, wenn die Abweichung in der tatsächlich verglichenen Überdeckung liegt. |
| Gleichförmiger Hintergrund, Vordergrund außerhalb der vollständigen Sicht oder geringe gemeinsame Fläche | Kann keine informative Eindeutigkeit begründen; die konkrete Mindestfläche ist noch nicht begründet. |
| Periodische oder spiegelnde sichtbare Struktur mit mehreren exakten Offsets | Enthaltung wegen Offsetmehrdeutigkeit. |
| Unterschiedliche Verschiebungen einzelner Zellen | Kein gemeinsamer Offset kann die sichtbaren Abweichungen als eine gemeinsame Verschiebung erklären; ob er abweist, hängt von der gewählten Überdeckung ab. |
| Verschiebung unterhalb einer Rasterzelle | Kann wegen Blockmittelung unsichtbar bleiben oder sichtbare Mittelwerte verändern. Der reine Ganzzellenvergleich kann beides nicht als Teilzellverschiebung klassifizieren. |

Der Vorschlag wäre als allgemeine Wiedererkennung verworfen: Der Gegenfall
zeigt, dass eine zulässige Teilfläche ein fremdes Gesamtmuster nicht ausschließt.
Mehrere Offsets müssen weiterhin zur Enthaltung führen. Ebenso wäre er nicht
als allgemeine Positionslösung auszugeben: Schon eine vertikale Verschiebung
oder ein Muster außerhalb der zehn vollständigen Zellen liegt außerhalb seiner
Information.

### Entscheidung vor einem Anschluss

Für die eng begrenzte zellweise Aufgabe reicht die vorhandene 32-Komponenten-
Sicht nur für eine **Teilstrukturübereinstimmung**, nicht für die beabsichtigte
Wiedererkennung eines gespeicherten Gesamtinhalts. Die Mindestüberdeckung ist
ohne konkrete Aufgabenanforderung nicht sachlich festlegbar. Für beliebige
horizontale Pixelverschiebungen, vertikale Lageänderungen oder komplexere Muster
reicht sie ebenfalls nicht; dafür wäre zuerst ein Informationsbedarf zu
begründen, keine automatische Maskenerweiterung.

**Entscheidung:** Der positionskompensierte Vergleich wird nicht an die
öffentliche Memoryzulassung angeschlossen. Er kann derzeit höchstens eine
beobachtete Teilstruktur bei einem Offset beschreiben. Bis eine Aufgabe
definiert, welche vollständige sichtbare Fläche für eine relevante Erfahrung
erforderlich ist, gibt es keine begründete Mindestüberdeckung und keine
Implementierungs-, Quellen- oder Testfreigabe.

## Aufgabenentscheidung: Private Teilstrukturhinweise

Das Nutzungsziel ist nachträglich enger bestimmt: Der Vergleich darf passende
frühere **Teilwahrnehmungen als unsichere Hinweise** ausgeben. Er darf weder
eine vollständige Erfahrung zuordnen noch die bestehende öffentliche
A/B-Zulassung oder Memoryzustände ändern.

Für genau eine ganze horizontale Rasterzelle sind bei der bestehenden Sicht
neun vollständige RGB-Zellen auf beiden Seiten gemeinsam sichtbar. Diese neun
Zellen sind keine neue Schwelle, sondern die gesamte verfügbare vollständige
Überdeckung der fest gebundenen Verschiebung. Der private Vergleich prüft die
drei möglichen Offsets `-1`, `0`, `+1` ausschließlich über jeweils ihre
vollständige Überdeckung. Ein Kandidat ist ein Teilstrukturhinweis nur, wenn
genau ein Offset alle zugehörigen vollständigen Tripel exakt erfüllt. Mehrere
Offsets oder mehrere passende Kandidaten werden nicht ausgewählt, sondern als
sichtbare Unsicherheit ausgegeben.

Die spätere Quellenbindung enthält vor jeder Analyse mindestens: eine
unverschobene Referenz, ihre Ein-Zell-Verschiebung, eine Fremdstruktur mit
abweichender Zelle innerhalb jeder zulässigen Überdeckung, eine widersprüchliche
verschobene Struktur und eine gleichförmige Sicht mit Offsetmehrdeutigkeit.
Eine zusätzliche Kandidatenstruktur, die nur auf der unüberdeckten
Randzelle abweicht, muss zu mehreren Hinweisen und damit zu sichtbarer
Kandidatenmehrdeutigkeit führen. Rollen bleiben außerhalb der Vergleichslogik.

Die unveränderte 32-Komponenten-Exaktprüfung bleibt die Baseline. Die spätere
Auswertung trennt zusätzliche richtige Hinweise, zusätzliche Fehlhinweise,
verlorene Baselinehinweise, nicht anwendbare Fälle sowie Offset- und
Kandidatenmehrdeutigkeiten. Ein bestätigter Hinweis trägt ausschließlich die
Aussage, dass die gebundene beobachtete Teilstruktur bei einem Offset passt.

## Abschluss des privaten Memoryvergleichs

Der gebundene Lauf `s2sp-memory-compare-real-20260919-01` bestätigt den
Hinweis vor Konkurrenz nur innerhalb Fast. B4 bleibt dabei mehrdeutig. Nach
der Konkurrenzfolge ist die e01-B4-Generation nicht aktuell verfügbar, aber
die A1-Cue ergibt im B4-Bestand einen eindeutigen Hinweis auf eine
Randvariante. Die Randzelle liegt außerhalb der vollständigen Ein-Zell-
Überlappung; sie wird von der fest gebundenen Teilstrukturregel daher nicht
verglichen. Der Hinweis ist regelkonform eine passende sichtbare Teilstruktur,
aber in der externen Zielbeziehung ein Fehlhinweis. Es wurde keine Abweichung
innerhalb der geprüften Überdeckung übergangen.

Die Annahme, die visuelle Slow-Bank sei bei e06 leer, war eine falsche
Einordnung des historischen Scanreports: Er enthielt bereits einen visuellen
Slow-Kandidaten, aber keinen anwendbaren Exakt- oder Teilstrukturhinweis. Die
separat qualifizierte Präfixdiagnose
`s2sp-slow-prefix-diagnostic-20260919-01` bestätigt dies mit nativen
Übergangsreadouts. e01 erstellt Fast mit Support 1 ohne Konsolidierung; e03
bis e05 matchen denselben Fast-Slot, erreichen bzw. halten den gesättigten
Support 2 und schreiben die visuelle PPB jeweils fort. Bei e06 ist ein
visueller Slow-Slot vorhanden. Seine gespeicherten PPB-Werte unterscheiden
sich jedoch von der Cue, daher ist die bestehende Teilstrukturprüfung nicht
anwendbar. Weder eine fehlende Fast-Voraussetzung noch eine fehlerhafte
Kandidatenextraktion ist belegt. Die Befundgrenze liegt in der unveränderten
Abrufvergleichsregel, nicht in Memorybildung, Maske oder Schwelle.
