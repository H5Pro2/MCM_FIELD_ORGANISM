# ULZ1: Bedeutung der beobachteten Entscheidungen

Diese Einordnung gehört zur abschließenden, nachträglichen Archivdiagnose.
Sie enthält keine neuen bestätigenden Untergruppenurteile. Positive Nettowerte
bezeichnen eingesparte Fehlersumme von U gegenüber L, nicht mittlere Fehler.

## Woher kommt der beobachtete Vorteil?

| Fenster | Kategorie | Anzahl | Gewinn | Schaden | Netto |
| --- | --- | ---: | ---: | ---: | ---: |
| S primär Y33–128 | gleiche Ausgabe | 2832 | 0 | 0 | 0 |
| S primär Y33–128 | Kontext/Persistenz | 195 | 27,5 | 12,625 | 14,875 |
| S primär Y33–128 | verschiedene Kontexte | 45 | 2,875 | 2,75 | 0,125 |
| W primär Y129–160 | gleiche Ausgabe | 942 | 0 | 0 | 0 |
| W primär Y129–160 | Kontext/Persistenz | 72 | 8,125 | 5,625 | 2,5 |
| W primär Y129–160 | verschiedene Kontexte | 10 | 0,875 | 0,375 | 0,5 |
| S gesamtes Y | gleiche Ausgabe | 7580 | 0 | 0 | 0 |
| S gesamtes Y | Kontext/Persistenz | 508 | 71,625 | 35,5 | 36,125 |
| S gesamtes Y | verschiedene Kontexte | 104 | 7,25 | 5,75 | 1,5 |
| W gesamtes Y | gleiche Ausgabe | 7597 | 0 | 0 | 0 |
| W gesamtes Y | Kontext/Persistenz | 496 | 67,625 | 35 | 32,625 |
| W gesamtes Y | verschiedene Kontexte | 99 | 6,75 | 5,625 | 1,125 |

Der beobachtete Vorteil entsteht überwiegend beim Unterschied zwischen
Kontextwahl und Persistenz. Im stabilen Primärfenster liefert U=P/L=B allein
Netto 10: 58 Gewinne von je 0,25 gegenüber 18 Schäden von je 0,25.
U=A/L=P liefert Netto 2,5, U=P/L=Z 1,375 und U=P/L=A 1.
A/Z und Z/A tragen zusammen nur 0,125 bei. Im frühen Wechselfenster liefert
P/B Netto 2 der insgesamt 3 Einheiten; A/P und P/A gleichen sich jeweils aus.
Das ändert den fehlenden Primärnachweis für den frühen Wechsel nicht.

Gleiche Fehler bedeuten nicht zwingend gleiche Ausgaben: Bei tatsächlichem Z
sind A und P jeweils 0,125 entfernt. Im stabilen Primärfenster sind deshalb
2.854 Fehler gleich, aber nur 2.832 Ausgaben gleich. Die entsprechende
Differenz beträgt im frühen Wechselfenster 12, im gesamten S 48 und W 53.
Die vollständige Aufteilung steht in [categories.csv](categories.csv).

## Ältere Erfahrung erhält A trotz letzter neutraler Rückmeldung

**ULZ1-01-S, Ziel 327 (Y78), A/P, tatsächliches A:** Das letzte Feedback an
Ziel 323 stammt von Z. Für A gilt ec=ep=0,125; L erkennt deshalb keinen
strikten Vorteil und gibt P aus. U hat nach 21 gültigen Rückmeldungen
EC=0,12891149520874023 und EP=0,18749475479125977. Der negative Abstand
erhält A als eindeutige Wahl; U erzielt Fehler 0 statt 0,25.
Die älteren A-Beobachtungen sind im geglätteten Vorzustand noch wirksam.
Die neue Z-Zelle ist kalt und kann noch nicht konkurrieren.

**Derselbe Mechanismus kann maximal schaden:** ULZ1-01-S und ULZ1-01-W,
jeweils Ziel 103 (Y22), wählen U=A/L=P nach zuletzt Z. U bewertet A mit
EC=0,12621015310287476 gegenüber EP=0,18734526634216309 nach 24 gültigen
Rückmeldungen weiterhin günstig. Tatsächlich folgt B: Fehler U=0,5,
L=0,25, Schaden 0,25. Im stabilen Primärfenster zeigt ULZ1-03-S, Ziel 363,
denselben Maximalschaden. Eine erhaltene frühere Präferenz ist somit weder
pauschal gut noch pauschal schädlich.

Belege: [examples.json](examples.json), Einträge 4, 0, 6 und 14;
jeweils decisions.U/L.hypotheses mit vollständiger Vorgeschichte.

## Ältere Erfahrung verhindert eine sofortige B-Wahl

**ULZ1-01-S, Ziel 175 (Y40), P/B, tatsächliches A:** L sieht aus Ziel 171
für B ec=0 und ep=0,25 und wählt B. In U beträgt B nach elf Rückmeldungen
EC=EP=0,2493896484375; für A ist EC sogar geringfügig größer als EP.
U enthält sich daher und gibt P aus. Fehler U=0,25 statt L=0,5: Gewinn 0,25.
Die älteren Fehler von B verhindern, dass seine letzte richtige Vorhersage
allein die Wahl bestimmt.

**ULZ1-04-S, Ziel 255 (Y60), P/B, tatsächliches B:** Die junge B-Zelle hat
drei frühere Feedbacks: (ec,ep)=(0,375;0,125), nochmals (0,375;0,125),
danach (0;0,25). Daraus folgt in U exakt (EC,EP)=(0,1875;0,1875), in L
(0;0,25). U gibt P aus, L B; B wiederholt sich und U erleidet Schaden 0,25.
Hier verhindert dieselbe Art der Glättung eine diesmal richtige Reaktion.

Im frühen Primärfenster ist die Mechanik besonders kurz nachvollziehbar:
ULZ1-02-W, Ziel 551, hat für B zwei Feedbacks (0,5;0,25), (0;0,25).
U steht bei (0,25;0,25), L bei (0;0,25). Folgendes A bringt U Gewinn 0,25.
ULZ1-14-W, Ziel 655, hat dieselbe Zweierfolge für B; folgendes B erzeugt
stattdessen Schaden 0,25. Das beobachtete Netto ist keine sichere
Vorhersage, welches Ereignis nach derselben Bewertungsmechanik folgt.

Belege: examples.json, Einträge 1, 17, 12 und 22.

## Junge Z-Zellen, verschiedene Kontexte und Gleichstände

**ULZ1-01-S, Ziel 207 (Y48), Z/A, tatsächliches A:** Z hat erst eine
Rückmeldung und deshalb in beiden Armen EC=0,125, EP=0,25, Abstand −0,125.
A hat 23 Rückmeldungen. Sein U-Abstand ist ungefähr −0,12011236 und damit
weniger günstig als Z. L bewertet A nach seinem letzten Treffer dagegen
mit Abstand −0,25. U wählt Z, L A; Schaden 0,125. Der Wechsel zu Z ist
vollständig aus den verschiedenen Vorzuständen erklärbar, ohne einen
anderen Speicherbestand vorauszusetzen.

**ULZ1-01-W, Ziel 655 (Y160)** zeigt die umgekehrte Ergebniswirkung: U
bewertet A nach acht Feedbacks mit Abstand −0,109375, das einmal bewertete
Z mit −0,125. U wählt Z, L A. Tatsächlich folgt Z: Gewinn 0,125.

**ULZ1-01-W, Ziel 591 (Y144)** erklärt eine echte Gleichstands-Enthaltung:
A hat in U (0,09375;0,21875), Z (0,125;0,25). Beide Abstände sind exakt
−0,125, also gibt U P aus. L hat für A (0;0,25) und wählt A. Tatsächliches
B bringt U Gewinn 0,25. Ein negativer Einzelabstand reicht nicht aus,
wenn das beste Ergebnis nicht eindeutig ist.

Auch A statt Z ist durch unterschiedliche ältere Fehlerverläufe erklärbar:
ULZ1-17-S, Ziel 263, hat für A nach zwei Feedbacks (0,0625;0,1875),
Abstand −0,125. Das ältere Z steht nach sieben Feedbacks bei
(0,052734375;0,173828125), Abstand −0,12109375. U wählt A, während L
nach dem letzten Z Z wählt. Tatsächliches A bringt Gewinn 0,125.

Belege: examples.json, Einträge 2, 9, 7 und 23. In allen Beispielen ist
EP hypotheseneigen; wegen unterschiedlicher Zellalter darf es nicht durch
einen gemeinsamen geglätteten Persistenzwert ersetzt werden.

## Größte Schäden und tatsächlicher Speicherlebenszyklus

Der maximale Einzelschaden beträgt in beiden Primärfenstern und beiden
Gesamtbedingungen **0,25**. Im gesamten S gibt es 128 solche Ziele:
51 A/P, 28 P/A und 49 P/B. Im gesamten W sind es 129:
54 A/P, 29 P/A und 46 P/B. Alle 257 stehen in
[maximum-harms.csv](maximum-harms.csv). Die identischen frühen S/W-Verläufe
sind dabei keine unabhängigen Wiederholungen.

P/A ist die dritte maximale Schadensart: ULZ1-01-S, Ziel 375 (Y90), hat
für A zwei frühere Feedbacks (0,5;0,25) und (0;0,25). U bewertet A mit
(0,25;0,25) und enthält sich; L wählt nach dem letzten Treffer A. Folgendes
A verursacht U-Schaden 0,25. Das ist dieselbe Verzögerungsmechanik wie bei
P/B, mit vertauschtem Endpunkt (examples.json, Eintrag 5).

Promotion hat diese Zellen nicht gelöscht: Vor Ziel 175 wurde B bei
Ereignis 172 promoviert, vor Ziel 375 A bei Ereignis 372. Die vorhandenen
Fehlerpaare wurden unverändert übernommen. In beiden Ereignissen wurde Z
verdrängt. Der erste nachfolgende Fall bringt U Gewinn, der zweite Schaden.
Das illustriert, warum bloße Nachbarschaft zu Z-Verdrängung keine
eigenständige Schadensursache belegt. Welches Resultat ohne Verdrängung
entstanden wäre, wurde nicht untersucht.

Über alle Archive wurden **3.978 Zellübernahmen** bei Promotion in beiden
Armen an der nächsten gespeicherten Grenze unverändert wiedergefunden.
Alle 16.384 Y-Ziele enthalten Hypothesen mit ungleichen Zahlen gültiger
früherer Rückmeldungen. In S sind an 966 Zielen, in W an 936 Zielen
zusätzlich kalte Zellen vorhanden. Vollständige Werte und Belegketten:
[Prüfbilanz](verification.json), [Lebenszyklus](lifecycle.json), examples.json.

## Schlussfolgerung und nächster fachlicher Schritt

Der begrenzte Stabilitätsnutzen von U bleibt belegt. Die Diagnose lokalisiert
den beobachteten Nutzen überwiegend bei Kontextwahl gegenüber Enthaltung;
sie zeigt zugleich die entsprechende Verzögerung als Quelle einzelner
Schäden. Der frühe Wechselvorteil von L bleibt nicht nachgewiesen, ebenso
ein gegenläufiger U-Vorteil in diesem Primärfenster.

ULZ1 ist wissenschaftlich abgeschlossen. U bleibt unverändert. Der nächste
sinnvolle Schritt beim Projektleiter ist, eine eigenständige offene
MCM-Forschungsfrage zu priorisieren und ihren Bezug zur bestehenden
Wirkungsgrenze festzulegen. Eine weitere Variante dieser Glättungsstudie
ergibt sich aus den nachträglichen Kategorien allein nicht. Dieser Bericht
startet keine neue Studie und ändert keine Regel.
