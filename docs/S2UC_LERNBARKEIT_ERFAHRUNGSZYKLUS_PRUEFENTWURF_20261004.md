# Begrenzter Prüfentwurf: Lernbarkeit des vollständigen Erfahrungszyklus

Stand:2026-10-04. **KORRIGIERTER VERTRAG – IMPLEMENTIERUNG UND NEUTRALE QUALIFIKATION BEAUFTRAGT; FORSCHUNGSSTART GESPERRT.**
A1-Diagnose abgenommen; A1-Teilzweig abgeschlossen und deaktiviert. Historische
T1/F-Urteile und Kriterien bleiben unverändert. Dieser Entwurf fragt nach
Lernen unter Unsicherheit, nicht nach fehlerfreier Trennung aller Fortsetzungen.

## 1. Zwei getrennte Fragen und falsifizierbare Erwartungen

**Informationsfrage:** Kann ein ausschließlich aus vergangenen Beobachtungen
lernendes, einfaches Verfahren den durchschnittlichen Fehler gegenüber
Persistenz senken? Erwartung: ja bei stabiler verzerrter Fortsetzungsverteilung;
auch nach dem festgelegten Wechsel wieder, nach einer Übergangszeit. In der
unabhängigen fairen Kontrollbedingung ist auf G_Y kein systematischer Vorteil
zu erwarten. Das deterministische Gerüst darf auch dort vorhersagbar sein.

**Mechanismusfrage:** Nutzt das unveränderte U-System mit bestehender
Mehrhypothesen-Fehlerrückmeldung diese Lerngelegenheit nach Aufnahme,
Bestätigung, Feedback und Wiederabruf? Erwartung: positiver mittlerer Vorteil
gegenüber Persistenz in den beiden informativen Bedingungen, jedoch nicht
notwendig Gleichstand mit dem datenreicheren Häufigkeitsvergleich. Diese
Erwartung kann scheitern, obwohl die Quelle nachweislich lernbar ist.

Ein Vorteil nur gegenüber Persistenz belegt begrenzte Informationsnutzung.
Ein Vorteil gegenüber der einfachen lernenden Vergleichsmethode ist ein
separater, strengerer Befund; er wird nicht aus mehr warmen Abrufen abgeleitet.
Der Entwurf optimiert keine Quelle anhand künftiger Ergebnisse.

## 2. Kontrollierte Quellenfamilie

Vier feste48-dimensionale Wahrnehmungsvektoren, j=0,…,47:

- H1[j]=1/8+j/4096;
- H2[j]=1/2+j/4096;
- L[j]=1/4+j/4096;
- R[j]=3/4+j/4096.

Ein Block besteht aus **[H1,H2,Y,H1]**, Y∈{L,R}.
Der wiederkehrende Hinweis ist H1,H2; seine Fortsetzung Y ist stochastisch.
L und R liegen symmetrisch um die Persistenzvorhersage H2. Der gemeinsame
Koordinatenanstieg verhindert unbeabsichtigte exakte Halb-/Doppelfaktormatches
zwischen unterschiedlichen Vektoren. Alle Werte bleiben im Bereich[0,1].
Die Buchstaben sind nur Entwurfs-/Beobachternotation, keine Eingangstoken.

**Festes Aufnahmepräfix:** vier Blöcke, entweder LL RR oder RR LL, also jede
vollständige Viererspur zweimal unmittelbar nacheinander. Die Reihenfolge wird
vorab zwischen Wiederholungen ausgeglichen. Das sind16 reguläre Frames, kein
Schreiben in Speicherplätze und kein Setzen von Fehlerzellen durch den Beobachter.

Danach genau256 Blöcke pro Geschichte, ohne Reset oder Phasenmeldung:

| Bedingung | Blöcke1–128 nach Präfix | Blöcke129–256 |
| --- | --- | --- |
| S: stabil | P(Y=bevorzugte Fortsetzung)=0,8 | 0,8 |
| W: Wechsel | 0,8 | 0,2 |
| N: Nullkontrolle | 0,5 | 0,5 |

Ziehungen sind innerhalb einer Bedingung unabhängig; der Wechsel erfolgt
unbedingt an derselben vorab bestimmten Blockgrenze. Bevorzugte Fortsetzung
L/R und Präfixreihenfolge werden unabhängig ausgewogen, siehe Wiederholungen.

N besitzt keinen aus dem bisherigen Verlauf vorhersagbaren Zusammenhang zur
nächsten **Y-Fortsetzung**. Das gemeinsame Blockgerüst bleibt auch hier
vorhersagbar. Es wird deshalb niemals behauptet, die gesamte N-Quelle sei
strukturlos. Ein einzelner Hinweis prüft zunächst das Lernen seiner
Fortsetzungsverteilung, nicht einen Zusatznutzen verschiedener Hinweisidentitäten
gegenüber einer unbedingten Häufigkeitsschätzung. Das ist eine bewusste Grenze.

**Analytische Referenz, keine Messung und kein ausführbarer Arm:** Bei p=0,8
beträgt der erwartete Y-MAE einer stets gewählten Mehrheitsfortsetzung0,1,
der Persistenz-MAE0,25. Nach dem Wechsel gilt das spiegelbildlich. Bei p=0,5
beträgt der erwartete Y-MAE jeder Wahl zwischen L und R, auch H2,0,25.
Die ideale0,1 setzt die wahre Verteilung voraus und wird keinem System gegeben.
Ein endlicher lernender Vergleich wird diesen Wert nicht zwingend erreichen.

## 3. Ergebnisunabhängige Gelegenheit für den vollständigen Zyklus

Das feste Präfix bietet U zwei vollständige Wiederholungen. Nach bisherigem
Vertrag sollen beide Originalspuren in den zwei Retained-Plätzen liegen.
Spätere Blöcke sind ausschließlich Wiederkehr einer dieser beiden Spuren:
kein dritter Spurtyp, keine Kapazitätsüberlastung und keine A1-Teilzulassung.
Vor jedem Y treffen genau die beiden Hinweisframes ein. Die Originalnachfolger
liegen an Offset0 vor; Feedback folgt am tatsächlichen Y-Frame. Danach existiert
unabhängig vom gezogenen Wert beim nächsten Block eine erneute Abrufgelegenheit.
Das Verfahren darf weder seltene Ziehungen überspringen noch bis zum gewünschten
Speicher-/Auswahlergebnis zusätzliche Trainingsblöcke anfügen.

Aufnahme, volle Bestätigung, lebende Tickets, Feedbackübernahme und späterer
Abruf derselben Original-Offset-Linie werden getrennt protokolliert. Ein fehlender
Schritt wird als Befund erhalten, nicht durch Nachtraining korrigiert.
Die strukturelle Erwartung ist vor jeder Forschungsausführung neutral zu prüfen.

Dies ist eine **Lerngelegenheitsprüfung innerhalb vorhandener Kapazität**.
Sie prüft nicht Festigung unter vielen konkurrierenden Spuren, Verdrängungsrobustheit,
Transfer oder zusätzliche Speicherorganisation. Ein positives Ergebnis wäre nur
für diesen begrenzten Erfahrungszyklus aussagekräftig.

## 4. Unveränderte Arme und offengelegte Vergleichsspeicher

Alle drei Arme sehen dieselben Frames einmal, in derselben Reihenfolge, und
geben vor dem Ziel ihren Wert ab. Rückmeldungen erfolgen erst mit dem Ziel.

| Arm | Vorhersage / Lernen | Speichergrenze |
| --- | --- | --- |
| P | Letzten beobachteten Frame fortsetzen | Ein48-Float64-Vektor,384Byte Nutzdaten; Verwaltungsheap separat messen |
| U | Bestehender FactorRecencyArm + MultiErrorAdapter, multi_error_exact_v1; beide EMA-Zellen und Auswahl unverändert | Zwei Retained-Spuren, ein Kandidat;18 Originalframes, zwei Outputs,20 kombiniert,416Byte Bank,16.384Byte Zusatzheap;Receipt16.384/UTF-8 32.768Byte |
| H64 | Exakte Häufigkeit vergangener Fortsetzungen zum aktuellen Zweiframehinweis, beschrieben unten | Fester Ring der letzten64 beobachteten Hinweis-Ziel-Tripel, ausdrücklich größer als U |

A1 und K1 bleiben deaktiviert. Keine weitere Armvariante und keine veränderte
Speicher-, Fehler- oder Auswahlregel im MCM-Pfad.

**H64, ausschließlich Vergleichsverfahren:** Vor jeder regulären Prognose die
Einträge des Rings mit exakt demselben Zweiframehinweis zählen. Unter deren
bereits beobachteten Zielvektoren die eindeutig häufigste Fortsetzung vorhersagen;
bei leerer Menge oder Häufigkeitsgleichstand Persistenz. Erst nach Eingang des
Ziels das echte Tripel in den Ring schreiben und nötigenfalls den ältesten Eintrag
überschreiben. Alle regulären Prognosen zählen, auch Gerüst-/Präfixziele. Kein
Zugriff auf L/R-Katalog, Phasen, Ziehparameter oder bevorzugte Fortsetzung.
Kein Reset beim Wechsel.64 ist vorab festgelegt; kein Fenstertuning.

H64 speichert64×3×48×8=73.728Byte Tripel-Nutzdaten. Zusätzlich vorgesehen:
16Byte Ringverwaltung, höchstens drei Vektorpuffer=1.152Byte und64
64-Bit-Zähler=512Byte, zusammen75.408Byte vor Laufzeit-/Objektverwaltung.
Gesamter zusätzlicher Python-Heap einschließlich dieser Daten darf128KiB nicht
überschreiten und ist später tatsächlich zu messen. Keine wachsende Historie.
Dieser Arm ist **kein kapazitätsgleicher Konkurrent**, sondern ein einfacher
Informationsnachweis mit offengelegtem Mehraufwand. Ein Rückstand von U belegt
nicht automatisch die Ursache „zu wenig Speicher“.

## 5. Wiederholungen, Zufall und Informationsabschottung

32 vorab nummerierte Wiederholungen je Bedingung; insgesamt96 Geschichten mit
je1.040 Frames und drei Armen. Alle drei Bedingungen einer Wiederholung werden
als gemeinsame Auswertungseinheit behandelt. Bit0 von r−1 bestimmt die bevorzugte
Fortsetzung L/R, Bit1 die Präfixreihenfolge; jede Kombination kommt achtmal vor.

Konkrete reproduzierbare Ziehfestlegung für eine spätere Implementierung:
Für r=1,…,32 und b=1,…,256 ergibt sich u aus den ersten acht Bytes, big-endian,
von SHA256 des UTF-8-Texts `MCM-LZ1/v1/r={r}/b={b}`. Die bevorzugte Fortsetzung
wird gewählt, falls u/2^64 unter dem jeweiligen p liegt. Es werden dieselben u
innerhalb eines Wiederholungstripels S/W/N verwendet; das koppelt die Bedingungen,
nicht die Arme an deren Ergebnisse. Endliche64-Bit-Auflösung wird dokumentiert.
Keine Seed-Suche, kein Austausch von Wiederholungen und kein vorzeitiges Stoppen
bei günstiger Signifikanz. Diese Festlegung erzeugt hier noch keine Daten.

Nur numerische Wahrnehmungsframes und die bereits erforderlichen monotonen
Index-/Zeit-/Scopefelder erreichen die Arme. Identifikatoren sind inhaltsneutrale
Scope-IDs; keine Fallnamen, Zufallswerte, Phasen, Blocklabels, Verteilungen,
Modalwerte oder zukünftigen Ziele im Policy-Eingang. Quellen erzeugen ihre Folge
ohne Zugriff auf Vorhersagen. Der Beobachter besitzt Parameter/Masken, hat aber
keinen schreibenden Rückkanal in die Arme. H64 erhält dieselbe Sicht wie U.

## 6. Vollständige Bewertungsmengen und Fehlermaß

Unverändert MAE über48 Komponenten pro prognostiziertem Frame.
Für Gesamtlänge1.040 entstehen reguläre Ziele G={3,5,…,1039}; alle519 werden
exportiert. Ziel1041 bleibt bei allen Armen ausdrücklich rechtszensiert.
Keine Bewertung von Frames, für die der bestehende Adapter keine Prognose abgibt.

Vorab feste Teilmengen, jeweils vollständig und in jedem Ergebnis sichtbar:

- G_init={3,5,…,15}: sieben Ziele des festen Aufnahmepräfixes;
- G_post={17,19,…,1039}: alle512 Ziele nach dem Präfix, sekundäre Gesamtmenge;
- G_Y={4b+15 | b=1,…,256}: alle256 stochastischen Fortsetzungen, **primäre Nutzenmenge**;
- G_Gerüst=G_post ohne G_Y: alle256 übrigen Prognosen;
- G_Y zusätzlich disjunkt nach Blöcken1–32,33–128,129–160,161–256.
  Das erste und dritte Fenster zeigen Anlernen beziehungsweise Wechselkosten,
  das letzte den vorab bestimmten späten Nachwechselbereich. Identische Fenster
  gelten für S und N; keine nachträglich gewählten stabilen Abschnitte.

G_post mittelt Y und Gerüst zu gleichen Anteilen. Der triviale Gerüstanteil muss
separat gezeigt werden, damit seine Vorhersagbarkeit nicht als Lernen von Y gilt.
Zusätzlich das Gesamtmittel über G einschließlich Präfix berichten. Keine
Auswertung nur warmer oder ausgewählter Ziele als Ersatz für G_Y. G_post und G einschließlich Präfix bleiben sekundär.

## 7. Unsicherheit, Urteile und Schäden

Für jede Wiederholung und Bedingung die gepaarten G_Y-Mittelunterschiede
H64−P und U−P bilden. Alle Wiederholungen gleich gewichten.
**Vier primäre Kontraste:** beide Unterschiede jeweils in S und W.
Negative Unterschiede bedeuten Vorteil.32 Wiederholungstripel als Cluster
resampeln, dabei alle Bedingungen/Arme eines Tripels zusammenhalten;
10.000 Bootstrap-Ziehungen. Für Ziehung z=1,…,10000 und Position k=1,…,32
kommt der Wiederholungsindex aus den ersten acht SHA256-Bytes (big-endian) des
UTF-8-Texts `MCM-LZ1/uncertainty/v1/z={z}/k={k}`, modulo32 plus1. Damit ist
auch diese Zufallsabbildung vorab festgelegt; keine Stichprobensuche.
Perzentilintervalle mit Grenzen0,625% und99,375% (98,75%-Intervalle) für eine
vorab Bonferroni-aufgeteilte nominale5%-Familie der vier Kontraste. Für ein Quantil p die10.000 sortierten Bootstrap-Mittel mit nullbasiertem
Index h=9999·p linear zwischen floor(h) und ceil(h) interpolieren. Für95%-
Intervalle gelten entsprechend p=0,025 und0,975. Diese finite Bootstrap-
Auswertung ist eine Unsicherheitsabschätzung, keine garantierte exakte Abdeckung.

Ein primärer mittlerer Vorteil ist nur belegt, wenn die obere Intervallgrenze
unter0 liegt. Andernfalls **nicht nachgewiesen**, nicht automatisch widerlegt.
Die Wiederholung ist die Einheit;256 korrelierte Y-Ziele gelten nicht als256
unabhängige Replikate. Mittel, Median, Streuung und sämtliche32 Einzelwerte
bleiben sichtbar; keine Wiederholungsselektion.

U−H64 für S/W sowie N-Kontraste und alle Zeitfenster mit95%-Clusterintervallen
als vorab benannte sekundäre Befunde berichten. Daraus keine zusätzlichen
primären Erfolgserklärungen durch günstige Fensterauswahl. In N wird auf G_Y ein
Intervall um0 erwartet; bloß fehlende Signifikanz beweist keine Gleichwertigkeit.
Ein systematischer N-Vorteil auf G_Y erfordert Prüfung von Zufall, Eingangsleck
oder Maskenfehler. Ein Vorteil im deterministischen N-Gerüst allein ist kein
Hinweis auf ein Informationsleck und kein Nachweis einer gelernten Y-Beziehung.

Getrennte Urteile: (a) technisch auswertbar, (b) Information durch H64 gegenüber P
nachgewiesen, (c) U nutzt sie gegenüber P, (d) relativer Abstand U zu H64.
Wenn U P schlägt, aber H64 unterliegt: begrenzte Lernnutzung, **kein belegter
Vorteil gegenüber der einfachen lernenden Methode**. Wechselanpassung nur als
belegt bezeichnen, soweit die vorher festgelegten Nachwechselwerte dies tragen;
ein günstiges Gesamtmittel allein belegt keine Wiederanpassung.

Schäden für U−P und U−H64 jeweils vollständig darstellen: positive/negative/
gleiche Zielunterschiede, getrennte Schadens- und Gewinnsummen, größter Einzelschaden,
schlechteste mittlere Wiederholung und kumulierte Differenz über alle Blöcke.
Phasen-/Fensterwerte und Streuung ergänzen das Gesamtmittel. Kein Wegmitteln von
Wechselkosten. Es wird keine historische A1-Schadensschwelle auf diesen neuen
Entwurf übertragen und kein Urteil „schadensfrei“ aus einem Mittelwert abgeleitet.

## 8. Was ein negatives Ergebnis bedeutet

| Befund | Zulässige Schlussfolgerung | Nicht daraus ableiten |
| --- | --- | --- |
| Technischer Ablauf verletzt Bindung/Budgets/Kausalität | Nicht auswertbar; Fehlerabschluss, keine automatische Wiederholung | Negative Lernfähigkeit |
| H64 zeigt in S keinen Vorteil gegen P | Empirischer Informationsnachweis misslungen; Quelle, Vergleich oder statistische Trennschärfe prüfen | U habe vorhandene Information sicher ignoriert |
| H64 zeigt Vorteil, U hat keine lebende bestätigte Linie/kein Feedback/keinen späteren Abruf | Erfahrungszyklus bricht an dokumentierter Stufe; gegen strukturelle Gelegenheit prüfen | Reiner Auswahlfehler oder allgemeines Kapazitätsproblem |
| H64 zeigt Vorteil, U hält beide Linien und verarbeitet Feedback, gewinnt aber nicht | Vorhandene Informationsgelegenheit wird im begrenzten Bewertungs-/Auswahlpfad nicht hinreichend genutzt | Quelle sei unlernbar; beliebige Zusatzspeicherung löse es |
| U gewinnt stationär, scheitert nach Wechsel | Begrenzte Anpassung unter Drift; Verlauf der Fehlerzellen und Auswahl relevant | Stationärer Vorteil widerlegt |
| U gewinnt gegen P, verliert gegen H64 | Nutzung ist vorhanden, einfache lernende Methode nutzt sie besser | MCM-spezifischer Mehrwert |
| Beide ohne Vorteil in N | Mit Nullannahme vereinbar | Unmöglichkeit beliebiger Vorhersage bewiesen |

Die Diagnose beobachtet Originalidentitäten, Zellwerte vor der Auswahl,
Ticketlebendigkeit und Feedback nach dem Ziel. Sie benötigt keine nachträgliche
Umschreibung von Erfolgskriterien. Speicher und Auswahl sind anhand fehlender
beziehungsweise vorhandener Stufen zu unterscheiden; bei vorhandenen Stufen
beweist ein negativer Vergleich noch nicht, ob EMA-Verdichtung oder Entscheidung
allein verantwortlich ist. Dafür wäre ein späterer eigener Auftrag nötig.

## 9. Abnahme und erlaubter nächster Schritt

Der Projektleiter hat die Quellenfamilie und das Präfix abgenommen und die
Implementierung samt neutraler Qualifikation beauftragt. Nur G_Y ist primär.
Forschungsfolgen werden dabei weder materialisiert noch abgespielt. Historische
T1/F-Fälle werden nicht neu bewertet.

Empfohlener nächster Schritt beim Projektleiter: Quellenfamilie, feste
Aufnahmephase, H64-Mehraufwand und getrennte Urteile fachlich abnehmen oder ändern.
Erst danach wäre ein eng begrenzter Implementierungsauftrag mit unabhängigen
Referenzen und neutraler Qualifikation sinnvoll. Dabei unveränderte U-Grenzen
prüfen; für die spätere Hülle3.600s Gesamtzeit einschließlich60s Abschlussreserve,
64MiB Gesamtexport einschließlich8MiB Vorbereitung und1MiB Abschluss als
Planungsobergrenzen vorsehen. Vollständige kompakte Ereignistabellen statt
wiederholt ausgeschriebener Feedbackhistorien budgetieren. Machbarkeit ist noch
ungeprüft; bei Überschreitung kein stilles Kürzen von Fällen oder Belegen.
Ein Forschungsstart benötigt anschließend eine eigene gebundene Einmalbeauftragung.
