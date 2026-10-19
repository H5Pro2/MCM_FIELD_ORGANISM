# ER1: Erhaltung bestätigter Erfahrung und ihr Preis

2026-10-17. Status: **KONZEPTARBEIT_ABGESCHLOSSEN_ZUR_ABNAHME**.
Fortsetzung des Konzeptauftrags, Workflow `5c049764-767a-4a43-a359-d08b680b993c`.
Nur Dokumentation und statische Prüfung; keine Implementierung, Quellenmaterialisierung,
Archivneuberechnung oder Ausführung. ER1 ist eine Dokumentkennung, keine Laufnummer.
CR1 ist abgenommen; sämtliche bisherigen Forschungsfreigaben bleiben verbraucht.
K1 und A1 bleiben deaktiviert. Auch CR1 wird nicht stillschweigend zum Default.

## 1. Vorarbeiten weiterverwenden und die offene Frage begrenzen

In den aktuellen Projektübersichten und den einschlägigen Konzept-/Berichtsdateien
liegt kein fertiger aktueller Vertrag zur hier verlangten Erfahrungserhaltung vor.
Vorhandene Grundlage wird ausdrücklich weiterverwendet: der
[Wiederwahrnehmungsvertrag vom 30.09.](S2UC_WIEDERWAHRNEHMUNG_VERGLEICHSVERTRAG_20260930.txt)
und dessen bereits abgeschlossene technische Integration. ER1 erfindet keine neue
Speicherstrategie und wiederholt nicht den alten FIFO-Demonstrationsversuch.

**Offene Frage:** Verbessert die bestehende Bevorzugung vollständig wiederbeobachteter,
bestätigter Originalspuren unter fortlaufender Konkurrenz die spätere Prognose
gegenüber Erhaltung allein nach Promotionsreihenfolge – einschließlich des Preises,
dass andere, auch neuere Erfahrungen früher verloren gehen?

| Vorbefund | Belegt | Daraus nicht ableitbar / widerlegte Erwartung |
|---|---|---|
| T1, vollständiger Transferabschluss [B1] | Wiedererkennung in 11/16 Fällen; Anpassung 0/52; kein G-Gesamtnutzen; U wählt an keinem bewerteten Ziel Kontext | Wiedererkennung genügt nicht als Nachweis nützlicher Anpassung. Keine allgemeine Transferunfähigkeit behaupten. |
| T1-Ursachenanalyse [B2] | 133/324 Diagnoseziele verlieren eine früher gebildete berechtigte Originalspur durch Kandidatenersetzung; nur zwei berechtigte lebende Nachfolger, beide kalt | Historisch passende oder modale Nachfolger sind keine lebenden Hypothesen und kein Nutzennachweis. Die Zahl 133 rechtfertigt keine beliebige Verlängerungsfrist. |
| K1-Konzept und ausgeführter Vergleich [B3–B4] | Eine zusätzliche Blockfrist kostet Neuaufnahme; T1 mit warmem modalem Nachfolger bleibt 80/624 gegen 80/624, T1-Prognosefehler identisch | Der vorab verlangte strikte Mechanismuszuwachs ist in diesem Vergleich widerlegt. Ein besseres Gesamtmittel aus F-Fällen erfüllt den T1-Nutzenvertrag nicht. |
| K1-Feedbackdiagnose [B5] | Alle 31 zusätzlichen T1-Vorkommen zunächst kalt; 27 Rückmeldeschlüssel vorher ersetzt; vier Updates übernommen, aber kein späterer berechtigter Wiederabruf derselben Offsetlinie | Bloß längere Abrufbarkeit oder Feedback zu toten Schlüsseln löst keinen vollständigen Erfahrungszyklus. Eine andere Frist ist damit nicht begründet. |
| K1-Gegenfälle [B4–B5] | F1/Ziel19 belegt Erhaltung → lebendiges Feedback → Promotion → warme spätere Nutzung mit geringerem Fehler. F2/Ziel23 belegt den spiegelbildlichen Preis verworfener neuer Erfahrung. F3/Ziel11 zeigt schädliche alte Erfahrung | Erhaltung kann helfen und schaden. Die grundsätzliche Möglichkeit ist bereits belegt und muss nicht erneut als neue Entdeckung demonstriert werden. |
| Wiederwahrnehmung [B6] | Bereits 31/31 technische Tests; A bleibt durch vollständige Wiederbeobachtung erhalten, D geht stattdessen verloren. Hinweise verändern den Bestand nicht | Der Bestandsunterschied ist bekannt. Offen ist der vollständige Prognosenutzen mit Fehlerlernen über fortlaufende, vorab bestimmte Konkurrenzgeschichten. |
| CR1 [B7] | Ausgabevorteil im festen Primärfenster; gemeinsame Speicher- und Fehlerzustände identisch; 75 Unterschiede mit genau einer kalten Hypothese | Kein Nachweis besserer Erfahrungsbildung oder einer Rangfolge mehrerer kalter Originale. |

Der historische [FIFO-Stopp](S2UC_FIFO_EINDEUTIGKEIT_ABLEITUNG_20260930.txt)
bleibt gültig: dieselben bereits ableitbaren Treffermengen nochmals zu erzeugen
wäre nur Regression. Die neue Gegenprognose betrifft **Netto-Prognoseleistung über
alle Ziele frischer Konkurrenzgeschichten**, nicht das bekannte Verschieben einer
Liste. Sie ist ungeprüft. Der S2TX-Lauf mit unvollständiger Vorqualifikation wird
nicht nachträglich aufgewertet; [B6] liefert den späteren lokalen technischen Beleg.

## 2. Genau ein Vergleich: E gegen F

Beide Arme verwenden dieselbe unveränderte U-Auswahl (`multi_error_exact_v1`),
dieselbe Persistenz, Berechtigung, Fehlerinitialisierung, EMA, Gleichstandsregel,
Wahrnehmungsfolge, Vierersegmentierung und Informationsgrenze. Kein CR1-Kaltzweig.
Jeder Arm beginnt je Geschichte frisch; keine geteilten Speicher oder Fehlerzellen.

**E:** bestehende `FactorRecencyArm`-/`PerceptionRecencyArm`-Erhaltung.
**F:** dieselbe Regel mit genau einer Ablation: eine vollständige bestätigte
Wiederbeobachtung verändert die Reihenfolge der Retained-Liste nicht.

Verbindliche Regel am regulären vollständigen Segmentabschluss:

1. Bestehende Validierung, Vorrang bestätigter Vollgleichheit, Kandidatenprüfung,
   Disjunktheit, Generationen und Fehlerpfade bleiben gleich.
2. Die vorhandene Auffrischungsbedingung wird in **beiden** Armen geprüft: genau
   eine vollständig wertgleiche bestätigte Spur und Beginn des neuen Intervalls
   strikt nach ihrer letzten akzeptierten Beobachtungsendmarke.
3. Bei erfüllter Bedingung aktualisieren beide dieselbe begrenzte Endmarke.
   Nur E entfernt dasselbe Trace-Objekt aus seiner Listenposition und hängt es
   hinten an. F lässt es an seiner Position. Werte, Originalordinale und Generation
   bleiben erhalten. Kein Kopieren neuer Frames in die alte Spur.
4. Bei echter Kandidatenpromotion werden in beiden Armen dieselben ursprünglichen
   Kandidatenframes übernommen. Bei zwei belegten Plätzen wird das jeweilige erste
   Listenelement verdrängt, danach die neue Spur angehängt. F entspricht damit FIFO
   nach Promotion; E einer durch vollständige Wahrnehmungsbestätigung aktualisierten
   Verdrängungsreihenfolge. Keine Auffrischung durch Hinweise, Auswahl oder Feedback.
5. Bei unvollständigem Block, fehlender gültiger Wiederbeobachtung, freien Plätzen,
   Kandidatenersetzung, Fristfreiheit und Abschluss gelten die bestehenden Regeln.
   Insbesondere kein K1-Ablauf und keine zusätzliche Kandidatenfrist.

Die zwei bereits vorhandenen skalaren Endmarken werden in beiden Armen gleich
geführt und gleich bilanziert; F bekommt weder weniger zugängliche Information
noch einen zusätzlichen freien Speicherplatz. Das administrative Ereignisprotokoll
unterscheidet Wiederbeobachtung von tatsächlich geänderter Reihenfolge. Es darf
bei F keine nicht erfolgte Umordnung behaupten. Dies ist Protokollierung derselben
Regeldifferenz, keine weitere Lernregel.

**Vorhersage:** Wiederkehrende vollständig beobachtete Erfahrung kann in E länger
lebend bleiben und später mit früherem Feedback genutzt werden. **Gegenprognose:**
E schützt inzwischen unpassende oder bald nicht mehr benötigte Originale und
verdrängt neuere, später nützliche Spuren; sein mittlerer Fehler kann gleich oder
größer sein. Keine der Regeln kennt zukünftige Wiederkehr, Quellenphase oder Ziele.

## 3. Statische Anschlussfähigkeit und Grenzen

`PerceptionRecencyArm.close_segment` [B8] trennt die gültige Wiederbeobachtung,
`remove`/`append` und die höchstens zwei Endmarken bereits sichtbar.
`CandidateTwoArm.close_segment` [B9] verdrängt bei Promotion mit `pop(0)` und
übernimmt die Kandidatenoriginale. Daher ist die Ablation lokal beschreibbar,
ohne eine neue Kandidatenstrategie oder zusätzliche Spur einzuführen.

`MultiErrorAdapter._promote` [B10] erwartet gerade `previous[0]` als Opfer und
überträgt Kandidatenfehler auf die neue Retained-Generation. Diese Invariante
bleibt pro Arm passend. `consume_feedback` aktualisiert alle eingefrorenen
berechtigten, noch lebenden Schlüssel; Auswahl und gemessener Ausgabefehler
steuern die Aufnahme nicht. Die Prognose wird vor Aufnahme ihrer Hinweisframes
eingefroren [B11]. Kein nachträgliches Umschreiben von Tickets, Wiederbeleben
toter Schlüssel oder Übertragen von Feedback zwischen Offsets.

**Anders als CR1 dürfen die Bestände und später die Fehlerzellen zwischen E/F
auseinanderlaufen.** Deshalb ist der CR1-Gleichheitsvergleich gemeinsamer Zustände
kein passender Abnahmenachweis. Erforderlich sind zwei eigene unabhängige
Referenzfortschreibungen, gemeinsame Eingabebelege und dieselbe Auswahlfunktion
auf dem jeweiligen Bestand. Vor einer ersten abweichenden Umordnung müssen die
Zustände gleich sein; danach muss jede Abweichung aus dem protokollierten
Erhaltungsverlauf erklärbar bleiben. Keine zusätzlichen Bytes wegmaskieren.

Exakte Typprüfungen bestehender Adapterkonstruktoren und der alte Referenzpfad
dürfen nicht umgangen oder durch Armumbenennung als qualifiziert ausgegeben werden.
Ein späteres separates Implementierungspaket benötigt einen ausdrücklich gebundenen
E/F-Einstieg, eine unabhängige F-Referenz und passende Archivprüfung. Heute bleibt
sämtlicher ausführbarer Code unverändert.

## 4. Getrennte Nachweise und vollständige Gegenkosten

Beobachteridentität: Geschichte, Scope, vier Originalordinale und Offset;
Generationen/Rollen zusätzlich. Eine Promotion ist bei erhaltenen Originalen kein
Erfahrungsverlust. Wertegleiche spätere Neuaufnahme ist nicht die alte Originallinie.
Beobachterhistorie bleibt extern und darf keinem Arm als Speicher dienen.

| Stufe | Erforderlicher Beleg | Kein Ersatzbeleg |
|---|---|---|
| Erhaltung | Originalspur bleibt über mindestens einen vollständigen, nicht gleichen Zwischenblock und eine konkrete Konkurrenzpromotion lebend; abweichendes Opfer E/F benennen | Nur Listenumordnung, historische Wiederkehr oder höhere Abrufzahl |
| Nutzbare Fehlererfahrung | Früheres tatsächlich übernommenes Feedback desselben Offsets; durchgehende Original-/Promotionslinie bis vor dem späteren Hinweis | Feedback des aktuellen Ziels, eines anderen Offsets oder eines toten Schlüssels |
| Tatsächliche Nutzung | Berechtigte spätere Hypothese wird tatsächlich von U ausgewählt; eingefrorener Ausgabewert und Herkunft belegt | Nur vorhandener Match, Wärme ohne Wahl oder Beobachtermodalwert |
| Prognoseleistung | Tatsächlich realisierte MAE beider Ausgaben; Gewinn, Schaden und Gleichheit auf allen Zielen | Korrekte Herkunft oder häufigere Auswahl |

Für jede Konkurrenzpromotion beide Vor-/Nachbestände, neue Originale und Opfer
protokollieren. Für jedes Ziel symmetrisch E\\F und F\\E der lebenden Original-
hypothesen, Wärme, gewählte Herkunft, Enthaltung und tatsächlichen Fehler berichten.
Zusätzlich ursprüngliches Aufnahmealter und zuletzt akzeptierte Wiederbeobachtung
festhalten; dadurch werden insbesondere Verluste **neuerer** Originale sichtbar.

Die Regel sperrt die unmittelbar anstehende Promotion nicht: beide nehmen zunächst
die neue bestätigte Spur auf, verdrängen gegebenenfalls unterschiedliche bisherige
Spuren. Abweichende Bestände können später weitere Bestätigungen, Kandidatenaufnahmen
und Verdrängungen verändern. Diese Folgeeffekte gehören zu den Kosten. Für jeden
vollständigen Eingangsblock deshalb Annahme, Bestätigung, Verwerfen oder Ersetzen
in beiden Armen erfassen; nicht auf die erste Opferwahl beschränken. Wenn eine
Neuaufnahme wegen einer schon vorhandenen wertgleichen Spur entfällt, ist das nicht
automatisch Inhaltsverlust: Originalidentität, lebende Nachfolger und spätere Nutzung
müssen den behaupteten Schaden tragen.

Gewinn- und Schadenssummen, Anzahlen, maximaler Einzelschaden, schlechtester
Geschichtenabstand und alle betroffenen Ziele bleiben separat sichtbar. Ihre
Differenz ist das Primärmaß, ersetzt aber nicht die getrennten Nachweise.
Eine Kette kann mehrere Ziele betreffen; Ereignisse, Originallinien und Ziele
bekommen getrennte Nenner. Keine Addition überlappender Diagnosepartitionen.

## 5. Frische Quellenanforderungen und fester Umfang

Vorgeschlagen: 32 unabhängig erzeugte Geschichten, je 256 Viererblöcke/1024 Frames,
zwei frische Arme; keine Startpräfixe oder Speicherresets. Je Block:
`(V(x_i), V(1/2), V(y), V(15/16))`, `V(x)[j]=x+j/4096`, j=0…47.
Vier Hinweise i=0…3 mit x=(1,3,5,7)/16, Fortsetzung y=1/4 oder 3/4.
Alle Bezeichnungen und die folgende Quellenlogik gehören nur zum Generator.

Für Geschichte r ist Orientierung o=(r−1) mod 2. Erster Hinweis gleichverteilt
aus vier Werten. Jeder weitere Block behält mit Wahrscheinlichkeit 1/2 den
vorigen Hinweis; andernfalls wählt er gleichverteilt einen der drei anderen
Hinweise in aufsteigender Indexreihenfolge. Dies erzeugt Wiederholungen und
unbeschränkte zufällige Wiederkehrabstände ohne bevorzugte Zielspur.

Der dominante Nachfolger ist A=1/4, wenn `(i mod 2) XOR o XOR p = 0`, sonst B=3/4.
p=0 für Block1…128 und p=1 für129…256. Pro Block unabhängig: dominanter Nachfolger
mit Wahrscheinlichkeit3/4, der andere mit1/4. Dadurch sind auch wiederbeobachtete
Originale fehlbar; nach dem festen Wechsel können alte Erfahrungen schaden.
Die Hinweisfolge läuft ohne Reset weiter. Vier Hinweisfamilien und bis zu acht
vollständige Blocktypen konkurrieren um zwei Retained-Plätze und einen Kandidaten.
Keine garantierte warme Wiederverwendung oder garantierte Zahl von Umordnungen.

Einziger vorgesehener Forschungsnamensraum `MCM-ER1/source/v1`, neutral getrennt
`MCM-ER1/neutral/v1`. SHA-256-Schlüssel exakt
`{namespace}/r={r}/stream={name}/draw={cursor}`; Streams `cue` und `outcome` mit
je eigenem Cursor ab0. Erste acht Bytes unsigned Big-Endian; für `below(n)`
Werte ab `2^64−(2^64 mod n)` verwerfen, sonst modulo n. Pro Stream höchstens4096
Ziehungen. Cue: einmal below(4), danach je Block below(2), bei1 zusätzlich below(3)
unter Ausschluss des vorigen Hinweises. Outcome: je Block below(4), bei0 der
nichtdominante Nachfolger, sonst der dominante. Keine Kennung ausprobieren.

Generator und unabhängige Rekonstruktion werden erst nach separater Freigabe
implementiert. Alle32 Quellen samt Hashes vor dem ersten Arm versiegeln. Keine
T1-/K1-/CR1-Daten wiederverwenden, keine Nachauswahl nach Treffern, Fehlern oder
Umordnungen. Die alte A-A-D-D-A-Z-Z-Folge bleibt ausschließlich kurze neutrale
Regression für die bekannte Regel und ist kein neuer Forschungsarm.

Beide Systeme erhalten nur identische reguläre 48-dimensionalen Wahrnehmungsframes
und bestehende Scope-/Ordinaldaten. Keine Hinweisnamen, Phase, Wahrscheinlichkeiten,
Wiederkehrtermine, Opferlabels oder Generatorzustände. Die Endlichkeit der Quelle
begründet keinen Zugriff auf zukünftige Werte. Diese Familie ist ein synthetischer
Test der festgelegten Frage, kein natürlicher AV-Transfernachweis.

## 6. Ein Primärmaß und feste Entscheidung

Je Geschichte r sämtliche beobachteten Prognoseziele t=3,5,…,1023 verwenden:
511 Ziele, einschließlich fehlender Hypothesen, kalter Zustände und gleicher
Ausgaben. Letzte Prognose für1025 zensiert. Kein Ausfiltern nach Abruf, Wärme,
Erhaltung oder Quellphase. Primär:

`D_r = (1/511) Σ_t [MAE(E,r,t) − MAE(F,r,t)]`, `D = (1/32) Σ_r D_r`.

Statistische Einheit Geschichte, insgesamt16352 Zielpaare; Geschichte ohne
Erhaltungsunterschied bleibt enthalten. Exakte rationale Auswertung gespeicherter
binary64-Fehler. Unveränderte feste 10000-fache Bootstrapindexmatrix aus dem
bisherigen 32-Geschichten-Verfahren, 16+16 nach Orientierung;
SHA `0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965`.
Keine alten Fehlerwerte übernommen. Nominales zweiseitiges95%-Perzentilintervall,
lineare Interpolation h=9999q. Neue Statistikreferenz muss den Vollnenner511
ausdrücklich prüfen; CR1-Fenstercode ist dafür nicht unverändert qualifiziert.

| Kriterium | Primärurteil |
|---|---|
| Obere Intervallgrenze <0 | E verbessert mittlere Prognoseleistung in dieser Familie |
| Untere Intervallgrenze >0 | E ist im Mittel nachteilig |
| Intervall berührt/enthält0 | Unentschieden, kein Gleichwertigkeitsnachweis |
| Fehlende Geschichte/Ziele, Referenz-, Herkunfts- oder Ressourcenverletzung | Technisch nicht auswertbar; kein Nutzenurteil aus Teilserie |

Zusätzlich getrennte mechanistische Urteile: Erhaltung nur mit konkretem
Erhaltungszeugen; spätere warme Nutzung nur mit vollständiger Feedback-/Originalkette;
lokaler Nutzen nur bei kleinerem tatsächlich gemessenen Fehler desselben Ziels.
Die Aussage „Erhaltung ermöglicht nützliche spätere Wiederverwendung“ erfordert
mindestens einen vollständigen solchen Zeugen **und** das negative Primärintervall
für den Gesamtvorteil. Fehlt eine Stufe, wird sie als nicht nachgewiesen ausgewiesen,
auch bei günstigem Primärmaß. Das ist keine neue Signifikanzprüfung.

Vor-/Nachwechsel, Q-Ziele, kalte/warme Nutzung, Wiederkehrabstände und Kostenklassen
bleiben deskriptiv. Kein zusätzlicher Wirksamkeitstest, kein nachträgliches optimales
Fenster. Nullgruppen: Anzahl0, Mittel undefiniert. Keine lokale Schadensfreiheit
aus einem negativen Gesamtmittel ableiten; kein automatischer Architekturentscheid.

## 7. Ressourcen, spätere Abnahme und heutiger Abschluss

Identische Policygrenzen: zwei bestätigte Viererspuren, ein Viererkandidat,
höchstens vier Bildungsframes; maximal18 verschiedene Originalframes einschließlich
Hints, eingefrorener und abgelöster Referenzen; zwei Ausgabeslots, kombiniert20;
416-Byte-Fehler-/Ticketbank; Zusatzheap16384 Byte, Receipt16384 Byte,
transienter UTF8 32768 Byte im bestehenden Messumfang. Endmarken in beiden Armen
höchstens zwei; keine zusätzliche persistente Metadatenliste oder Archivzugriff.
Heapgrenze ist keine Gesamtprozess-RAM-Aussage; neu zu qualifizieren, nicht behauptet.

Späterer Gesamtrahmen höchstens32 Geschichten/64 Arme, global57600s,
Worker54000s, Abschlussreserve3600s innerhalb Gesamtfrist; gemeinsamer Job512MiB,
höchstens zwei Prozesse. Vorbereitung8MiB, Quellen2MiB/32KiB je Fall,
Archive32MiB/512KiB je gzip, encoded/dictionary je4MiB, record256KiB,
nodes65536/edges262144/indices65536/collections16; temporär und Gesamtexport
je64MiB einschließlich Vorbereitung, Administration2MiB, Closure1MiB.
Neue Beobachterbelege müssen in diese Grenzen passen. Keine Laufzeit- oder
Archivgrößengarantie aus CR1; Grenzenüberschreitung ist technischer Abschluss.

Vor Forschungsfreigabe erforderlich: kurzer unabhängiger E/F-Regelvergleich,
Identität der Auswahlfunktion auf gleichen Beständen, richtige Endmarken in F,
Erhaltung und Opfer beider Richtungen, warme Wiederverwendung und verlorene neuere
Erfahrung, Promotions-/Ticket-Lebendigkeit, Quellenreferenz ohne Zukunftsfluss,
Vollnenner und Vorzeichen, sämtliche Intervallfälle, separate Archive und
Fehlercleanup, Ressourcenmessung. Bestehende technische Belege nur für tatsächlich
unveränderte Komponenten übernehmen. Kein großer Wiederholungstest des bereits
erklärten FIFO-Grundfalls. Eigene Vorstartbindung und exklusives Forschungsziel
erst nach abgenommenem Implementierungspaket; kein Retry, Resume oder Ersatzlauf.

**Übergabe:** Konzeptarbeit abgeschlossen. Empfohlen wird die fachliche Abnahme
dieses einen E/F-Vergleichs, insbesondere seiner neuen Vollleistungsfrage gegenüber
dem bereits bekannten Bestandsmechanismus. Erst danach gegebenenfalls ein getrenntes,
begrenztes Implementierungs-/Neutralprüfpaket. Heute wurden ausschließlich dieser
Vertrag und die drei Projektübersichten geschrieben; keine Befunde neu berechnet.

## Belege

- B1: [T1-Abschluss](../reports/s2uc/t1-transfer-assessment-20261003-02/REPORT.md), getrennte Urteile und feste Nenner.
- B2: [T1-Ursachenanalyse](../reports/s2uc/t1-cause-analysis-20261003-01/REPORT.md), 324 Ziele, Kandidatenverluste und Zeitgrenze.
- B3: [K1-Konzept](S2UC_KANDIDATENERHALTUNG_K1_KONZEPTVERTRAG_20261003.md), Frist, Kosten und damaliger Prüfvertrag; historisch, keine neue Freigabe.
- B4: [K1-Abschluss](../reports/s2uc/k1-comparison-assessment-20261004-01/REPORT.md), 80/624 gegen80/624 und F1/F2/F3.
- B5: [K1-Feedbackdiagnose](../reports/s2uc/k1-feedback-diagnosis-20261004-01/REPORT.md), 27+4 und fehlende weitere Nutzung.
- B6: [Wiederwahrnehmungsintegration](../reports/s2uc/perception-recency-20260930-02/REPORT.txt), bekannte Regel und Verlustseite.
- B7: [CR1-Abschluss](../reports/s2uc/ura1-cr1-comparison-16h-01/REPORT.md), abgenommener Ausgabebefund und Grenzen.
- B8: [Erhaltungsaktualisierung](../tools/_s2uc_perception_recency.py), `close_segment` ab Zeile10, Bedingung15, Umordnung19–20, Endmarken21/24; [aktuelle Integration](../tools/_s2uc_factor_recency.py).
- B9: [Kandidatenpromotion und Verdrängung](../tools/_s2uc_four_arm.py), `CandidateTwoArm.close_segment` ab27, Opfer46/Übernahme47.
- B10: [U-Auswahl und Rückmeldung](../tools/_s2uc_multi_error.py), `_receipt`103, `consume_feedback`179, `_promote`267, `_admit`298.
- B11: [Wahrnehmungsreihenfolge](../tools/_s2uc_pair_context_adapter.py), `accept_perception`; [K1-Default aus](../tools/_s2uc_k1.py), `create`71.
- B12: [Projektorientierung zum Erfahrungsmechanismus](KONZEPTNOTIZ_WAHRNEHMUNGSVERLAEUFE_PRAEGUNG_UND_INNERKONTEXT.md), keine eigenständige Ausführungsfreigabe.
