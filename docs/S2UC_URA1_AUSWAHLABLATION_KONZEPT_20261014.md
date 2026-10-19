# URA1 Konzeptentscheidung zur Nutzung gespeicherter Fehler bei gleichem Spurenbestand

Stand 2026-10-14. MCM-KI-Entwickler an MCM KI Projektleiter.
Status: KONZEPT_ZUR_ABNAHME. Ausschließlich Codelektüre und Dokumentation.
URA1 ist eine Dokumentkennung, keine Laufnummer oder Ausführungsfreigabe.

## 1 Entscheidung und Abgrenzung

Die vorhandenen Befunde beantworten die neue Frage noch nicht ausreichend:
**Verbessert die Nutzung gespeicherter Fehlererfahrung zur Auswahl die
Vorhersage gegenüber einer einfachen fehlerunabhängigen Auswahl aus genau
demselben verfügbaren Spurenbestand?**

Empfohlen wird konzeptionell genau eine Ablation U/R. U bleibt unverändert.
R wählt die zeitlich jüngste berechtigte Originalfortsetzung, ohne Fehlerwerte,
Warm/Kalt-Status oder Häufigkeiten für die Auswahl zu benutzen. Beide Arme
behalten dieselbe Aufnahme, Bestätigung, Promotion, Verdrängung, Abrufprüfung
und Feedbackverarbeitung. R führt die gleichen Fehlerzellen als für seine
Auswahl ungenutzten Kontrollzustand fort. Nur die Auswahlfunktion einschließlich
der Entscheidung Kontext/Persistenz wird ersetzt.

Das ist eine Ablation der **Nutzung** der Fehlererfahrung, nicht des Berechnens
oder Speicherns der Fehlerwerte. Ihre Entfernung wäre eine zweite Änderung
und würde die enge Zuschreibung erschweren. Daraus folgt insbesondere keine
Behauptung, R sei bereits eine speichersparende Produktvariante.

UFB1 bleibt eine abgeschlossene Konzeptarbeit. Seine Erkenntnisse zu
Informationszugang, Phasennutzung und vollständiger Speicherzählung bleiben
erhalten; seine Implementierung und Forschungswiederholung sind derzeit
nicht beauftragt. URA1 übernimmt weder die UFB1-Hülle noch dessen
65.536-Byte-Implementierungspaket als stillen Zusatzauftrag.

## 2 Was die vorhandenen Befunde tatsächlich beantworten

Alle Zahlen in diesem Abschnitt sind aus bestehenden Berichten übernommen.
Es wurden keine Archive neu berechnet, keine Policies abgespielt und keine
neuen statistischen Tests ausgeführt.

| Beleg | Beantwortete Frage | Verbleibende Lücke |
| --- | --- | --- |
| [LZ1-analytische Vorprüfung](../reports/s2uc/ul-analytic-precheck-20261004-01/REPORT.md) | Auf der damaligen Zweinachfolgerstruktur mit festem Präfix waren U und Letztfehlerregel nach dem Präfix regulär vorhersageäquivalent; Unterschiede an binary64-Grenzen begründeten keinen großen Versuch. | Keine allgemeine Überlegenheit der Glättung; insbesondere darf erneut keine bloß behauptete Stabilitäts-/Wechselabwägung als Motivation dienen. |
| [ULZ1-Abschluss](../reports/s2uc/ulz1-assessment-20261004-01/REPORT.md) | U gegen L mit jeweils fehlerbasierter Auswahl, L speichert nur letztes gültiges Fehlerpaar. Stabil S/Y33–128: U−L = −0,004882812, 97,5%-Intervall [−0,006591797; −0,003214010]. Früher Wechsel W/Y129–160: −0,002929688, [−0,006713867; 0,000976562]. Erwarteter L-Vorteil im Wechsel nicht nachgewiesen. | Beide Regeln benutzen Fehlererfahrung. Der Vergleich entfernt diese Entscheidungsgrundlage nicht. |
| [ULZ1-Archivdiagnose](../reports/s2uc/ulz1-diagnosis-20261004-01/EINORDNUNG.md) | Stabiler Nettogewinn überwiegend Kontext/Persistenz: 14,875 gegenüber 0,125 zwischen verschiedenen Kontexten. Identische Bestände und Feedbackgelegenheiten sind belegt; alte Erfahrung kann nutzen und schaden. | Nachträgliche Diagnose, kein neuer konfirmatorischer Nachweis gegenüber einer fehlerfreien Auswahlregel. Die Kontext/Persistenz-Entscheidung muss in der Ablation mit enthalten sein. |
| [HX1-Abschluss](../reports/s2uc/hx1-assessment-20261004-01/REPORT.md) | In D U−G = −0,064610281192 und U−P = −0,063659667969; drei vorregistrierte Kontraste inklusive D/N-Interaktion belegt. | Globalmittel G und Persistenz P wählen nicht aus demselben Originalspurenbestand. Das isoliert weder Fehlerauswertung noch Auswahl zwischen vorhandenen Kontexten. |
| [UF1-Abschluss](../reports/s2uc/uf1-assessment-20261005-01/REPORT.md) | F ist in D besser: U−F = 0,057098388672, 95%-Intervall [0,054504394531; 0,059814453125]. In N ergänzend U−F = −0,011047363281. | F hat andere Schlüssel-/Wertrepräsentation, Zähler und Phasennutzung. Kein Vergleich derselben verfügbaren Spuren mit und ohne Fehlerauswahl. |

Der historische [U/L-Konzeptvertrag](S2UC_BEWERTUNGSVERGLEICH_GLEICHES_BUDGET_KONZEPT_20261004.md)
und [LastErrorAdapter](../tools/_s2uc_ulz1_last.py) bestätigen, dass L weiterhin
EC−EP und die strikte Verbesserung gegenüber Persistenz verwendet. R ist weder
L unter anderem Namen noch ein neuer Glättungsfaktor. R kennt für seine Auswahl
überhaupt keinen vergangenen Fehlerwert.

Auch die frühere [ContinuationAdapter-Regel](../tools/_s2uc_continuation_adapter.py)
ist nicht R: Sie enthält sich bei mehreren Treffern, während R berechtigte
Originalfortsetzungen durch deren Originalzeit ordnet. Die hier geprüften
ULZ1-/HX1-/UF1-Belege enthalten keinen kontrollierten U/R-Befund. Die gezielte
Textsuche in Projektberichten und Konzepten ergab ebenfalls keinen belegten
Vergleich dieser Regel; daraus wird keine Vollständigkeitsgarantie über jede
historische Projektdatei abgeleitet.

## 3 Genau eine Vergleichsregel

### 3.1 Unverändertes U

MultiErrorAdapter, multi_error_exact_v1, FactorRecencyArm, exact_v1,
legacy_v1, alpha=1/2; A1/K1 aus. Gleiche Faktorhinweisprüfung wie bisher;
auswahlberechtigt sind ausschließlich Treffer mit factors exakt [1.0] und
offset 0 oder 1, sodass frames[offset+2] als Originalnachfolger existiert.
Ein bloßer Treffer ohne Nachfolger oder mit anderen Faktoren bleibt unberechtigt.

U wählt unter warmen berechtigten Hypothesen das eindeutige Minimum EC−EP,
nur wenn dieses strikt negativ ist. Ohne solchen eindeutigen Gewinner
verwendet U die zweite aktuelle Hinweiswahrnehmung als Persistenz. Kalte
Zellen sind keine Nullfehler. Keine Änderungen an Rundung, Gleichständen,
Initialisierung, Promotionsmitnahme oder Updateberechtigung.

### 3.2 R als jüngste berechtigte Originalfortsetzung

Vor Zugang zum Ziel wird dieselbe vollständige berechtigte Hypothesenmenge H
wie in U gebildet. „Berechtigt“ bedeutet hier strukturell abrufbar und mit
Originalnachfolger; es enthält ausdrücklich auch kalte Hypothesen.

Für jede Hypothese h ist o(h)=frames[h.offset+2].ordinal, also der Index des
tatsächlich gespeicherten Originalnachfolgers, nicht der letzte Abruf-,
Bestätigungs-, Promotions- oder Feedbackzeitpunkt.

1. H leer: R gibt dieselbe Persistenzdefinition wie U aus.
2. H nicht leer: R wählt h mit maximalem o(h), unabhängig von seinen EC/EP-
   Werten, Warm/Kalt-Status und dem jüngsten Ziel.
3. Bei gleichem maximalem o(h): lexikographisch kleinster Schlüssel
   (role, generation, offset), mit retained=0 und candidate=1. Das ist nur
   eine reproduzierbare Identitätsauflösung, keine Fehler-/Wertprüfung.
4. Ausgabe ist bitgleich frames[h.offset+2].values, vor dem Ziel eingefroren.
   Kein Mittelwert, keine Skalierung, kein Fallback nach betrachtetem Ziel.

Alle zum Vergleich dieser Regel nötigen Ordinals und Schlüssel sind bereits
Metadaten der gemeinsamen Hypothesen. Es gibt keine neue Zeitstempeltabelle,
Häufigkeitsbank, zusätzliche Originalspur oder von außen gespeiste Historie.
Ein Wiedersehen kann U-intern Recency für die Verdrängung verändern; es
schreibt aber den Originalindex nicht um. R ist daher bewusst „jüngstes
verfügbares Original“, nicht „zuletzt beobachtete Fortsetzung“. Wenn der
zuletzt beobachtete Wert regulär verloren ist, wird er nicht rekonstruiert.

Die Regel ist fachlich begründet als minimaler zeitbasierter Abruf aus dem
bereits verfügbaren Bestand. Sie erlaubt Kontextauswahl auch bei Konkurrenz,
ohne weitere Lernstatistik. Ihre Festlegung erfolgt jetzt, vor neuen Quellen
und vor R-Ergebniskenntnis. Kein paralleler Vergleich ältestes/zufälliges/
häufigstes Original, keine nachträgliche Wahl der günstigsten Baseline.

Die Auswahlregel gilt für alle regulären Prognosetermine, nicht nur für die
primären Q-Ziele. Sie erhält keine Q-Markierung und keinen Aufgabenphasenfilter.
Auch eine kalte Kontextwahl oder das Ausbleiben von U-Gleichstands-Enthaltung
ist Teil der beabsichtigten Ablation, kein Fehler der Vergleichbarkeit.

## 4 Gemeinsamer Bestand und Prüfung möglicher Rückkopplung

### 4.1 Codepfad und analytische Begründung

Die maßgeblichen vorhandenen Stellen sind:

- [PairContextAdapter.accept_perception](../tools/_s2uc_pair_context_adapter.py):
  nimmt das aktuelle Paar entgegen, fragt Hinweise vor dessen Aufnahme ab und
  führt anschließend genau die ursprünglichen Frameobjekte _admit zu.
- [MultiErrorAdapter._receipt / consume_feedback / _admit / _promote](../tools/_s2uc_multi_error.py):
  friert alle berechtigten Hypothesen und den Persistenzframe ein. Feedback
  berechnet ec für jede eingefrorene, noch lebende Hypothese und ep aus
  _pframe, unabhängig davon, welche Hypothese ausgewählt wurde. choice steuert
  die Ausgabe; es filtert nicht die Feedbackschleife oder Aufnahme.
- [CandidateTwoArm.close_segment](../tools/_s2uc_four_arm.py) und
  [PerceptionRecencyArm.close_segment](../tools/_s2uc_perception_recency.py):
  Bestätigung, Kandidatenersetzung, Promotion und Retained-Recency folgen den
  tatsächlich beobachteten Frames und Originalintervallen, nicht der Güte
  oder Identität der gewählten Vorhersage.
- [FactorHintArm.hint](../tools/_s2uc_factor_hint.py): Treffer aus vorhandenem
  Bestand und aktuellem Paar; kein Lesen der ausgewählten Ausgabe oder EC/EP.
- [equal_lifecycle](../tools/_s2uc_ulz1_engine.py): vorhandenes Beispiel eines
  ereignisweisen Gleichheitsprüfers; es ersetzt nicht die neue U/R-Qualifikation.

Daraus folgt für fehlerfreie Schritte bei identischen Eingaben induktiv:
gleicher Anfangsbestand -> gleiche Treffer/Tickets -> unabhängig von der Wahl
gleiche Aufnahme -> gleiche Bestätigungen/Verdrängungen -> gleiche gültige
Hypothesenfeedbacks -> gleiche Zellen und nächster Bestand.

R soll dazu consume_feedback unverändert verwenden. Es führt die gleichen
EC/EP-Werte mit identischer Numerik fort, liest sie jedoch nicht zur Auswahl.
Diese ungenutzten Fehlerzellen sind ein bewusst erhaltener Kontrollzustand,
kein versteckter Entscheidungszugang. Auch nicht gewählte Hypothesen werden
aktualisiert. Eine Umstellung auf Feedback nur für den Gewinner wäre eine
verbotene zweite Änderung und würde die Bestands-/Zellgleichheit gefährden.

**Ergebnis der Codelektüre:** Keine reguläre Rückkopplung der Auswahl auf den
späteren Spurenbestand erkennbar. Das ist eine statische Begründung, noch kein
technischer Nachweis für einen nicht implementierten R-Arm.

### 4.2 Was später ausdrücklich nachzuweisen ist

Zwei isolierte Instanzen; keine von U gesteuerte Bestandskopie als R-Eingang.
Vor/nach jedem Eingangs-, Feedback-, Promotions- und Cleanup-Ereignis vergleichen:

- geordnete Retained-Originale, Kandidat, forming, Hinweispuffer, Rollen,
  Generationen, Originalindices und bitgleiche Originalwerte;
- Bestätigungen, Beobachtungsendstände, Promotion, Verdrängung und Ersetzungen;
- vollständige Treffer und strukturell berechtigte Hypothesen einschließlich
  Originalnachfolger, eingefrorener Tickets und Kalt/Warm-Belegung;
- Lebensdauer, gültige Updates und Werte aller EC/EP-Zellen.

Objektadressen dürfen zwischen Instanzen verschieden sein; innerhalb jedes
Arms muss die Originalidentität erhalten bleiben. Gewählter Ticketindex,
Ausgabe, Auswahlgrund und ausgewählter Fehler dürfen verschieden sein.
Vorhersagespezifische Felder werden nicht fälschlich als Bestandsabweichung gewertet.

Mögliche technische Kopplungen: unterschiedliche Receipt-/Ausgabehalter können
Ressourcenfehler auslösen; ein fehlerhafter R-Patch könnte Tickets verkürzen,
Updates filtern oder Cleanup verändern. Das sind keine akzeptierten
Mechanismuseffekte. Jede Bestands-/Hypothesen-/Zellabweichung oder einseitige
Ressourcenverletzung macht den gesamten Vergleich NICHT_AUSWERTBAR.
Keine Gleichheit durch künstliches Nachkopieren, Zurücksetzen oder Schutz von Spuren.

## 5 Neue Gegenprognose und begrenzte Aufgabe

Die neue Hypothese lautet: **Bei stabilen hinweisabhängigen, aber nicht
deterministischen Fortsetzungen liefert U über alle Q-Ziele weniger Fehler
als die Auswahl des jüngsten verfügbaren Originalnachfolgers.**

Begründung: Das Alter einer erhaltenen Originalspur ist kein Nachweis ihrer
Vorhersagegüte. U kann eine strukturell verfügbare, aber bisher gegenüber
Persistenz ungünstige Fortsetzung zurückweisen oder zwischen verfügbaren
Nachfolgern anhand ihrer bisherigen Fehler unterscheiden. R kann das nicht.
Gegenmechanismus: U kann durch kalte Zellen, Gleichstands-Enthaltung und
begrenzte Fehlerhistorien eine brauchbare junge Spur zu spät nutzen; dann
kann R gleich gut oder besser sein. Es wird keine allgemeine EMA-
Stabilitätsüberlegenheit behauptet: Die frühere LZ1-Herleitung bleibt gültig.

Die Regeln sind bereits analytisch nicht identisch: Ist H nicht leer und sind
alle Zellen kalt, wählt U Persistenz und R ein Original. Ebenso kann bei zwei
verfügbaren Originalen ein älteres einen strikt günstigen Fehlerabstand haben,
während das jüngere ungünstig ist. Dann können ihre Entscheidungen verschieden
sein. Das sind logische Zustandsfälle, keine heute simulierten oder im neuen
Material beobachteten Verläufe. Ob und wie oft sie regulär erreichbar sind,
muss später ausschließlich neutral vor Forschung geprüft werden. Ergibt diese
Prüfung strukturelle Ausgabenäquivalenz für die festgelegte Familie, STOPP
für URA1 statt einer nachträglich „interessanter“ gemachten Quelle.

### 5.1 Feste Aufgabenstruktur

Nur die D-Familie aus HX1/UF1: zwei Hinweise, je zwei mögliche Fortsetzungen,
stabile 3:1- bzw. 1:3-Zuordnung. Kein neuer Wechselabschnitt, kein dritter
Fortsetzungswert und kein speziell schützendes Aufnahmepräfix. Die neue
Intervention ist die Auswahlregel, nicht eine Erweiterung des Aufgabenkatalogs.

32 neue Geschichten, je 1024 Frames = 256 Vierframeblöcke. Genau zwei Arme,
also 64 Armläufe. Orientierung o=(r−1)%2, je 16 Geschichten.
V(x)[j]=x+j/4096, j=0,…,47. Katalog:
V(1/8), V(7/8), V(1/2), V(1/4), V(3/4), V(1/16).
Hinweise X=(V(1/8),V(1/2)), Y=(V(7/8),V(1/2)); A=V(1/4), B=V(3/4).
Block: erster Hinweisframe, V(1/2), A/B, V(1/16).

Je Geschichte 128 A/128 B und 128 X/128 Y; Kontingenz XA/XB/YA/YB bei
ungeradem r=96/32/32/96, bei geradem r=32/96/96/32. Alle Werte und Beziehungen
werden nur durch die tatsächlichen Frames aufgenommen, nicht im Arm vorgegeben.
Zwei Retained-Spuren plus Kandidat bleiben der regulären Bestandsdynamik
ausgesetzt. Kein Austausch von Folgen nach Anzahl warmer oder verfügbarer Spuren.

Neue geplante Quellenkennung URA1-01-D bis URA1-32-D, Namensraum
MCM-URA1/source/v1/r={r}/stream={s}/draw={d}. Streams continuation,
dependent-A, dependent-B, jeweils unabhängig ab d=0. SHA256 exakter UTF-8-
Zeichenfolge ohne LF, erste acht Bytes big-endian uint64 u. randbelow(n):
u < 2^64−(2^64 mod n) akzeptieren und u mod n, sonst nächste Ziehung;
maximal 4096 Rohziehungen pro Stream, jede Ziehung zählt. Fisher-Yates
i=m−1,…,1. Erst 128 A gefolgt von 128 B mischen, dann aufsteigend aufgeführte
A-/B-Positionen getrennt mischen; erste 96/32 bzw. 32/96 erhalten X, Rest Y.
Keine N-Quelle und kein vierter Stream nötig, da keine N-Frage geplant ist.

Diese Namen werden nur konzeptionell reserviert. Neue Rezept-/Codebindung und
unabhängige Quellenprüfung sind Voraussetzung einer späteren separaten
Einmalfreigabe. Alle 32 Quellen müssen vor erstem Arm versiegelt sein.
Keine Wiederverwendung der UF1-/HX1-Folgen oder nachträgliche Auswahl nach
vorhandenen U-Fehlerreihen. Keine Quellen- oder Matrixerzeugung in diesem Auftrag.

## 6 Ein Primärkontrast und Entwicklungsentscheidung

Q={3,7,…,1023}, alle 256 Q-Ziele einschließlich Kaltstart, fehlender Spuren,
Enthaltungen und zwischenzeitlicher Verluste. Kein bedingtes Auswählen nur
divergierender, warmer oder mehrdeutiger Entscheidungen.

Je Geschichte d[r] = mean_Q(MAE(U)) − mean_Q(MAE(R)); einziger
Primärschätzer theta = mean über alle 32 Geschichten. MAE48 in bisheriger
binary64-Reihenfolge j=0,…,47, abschließend /48, ohne FMA/Umordnung.
Gespeicherte MAE und daraus folgende Aggregate/Quantile exakt rational behandeln.

Nominales 95%-Paarbootstrapintervall, 10.000 nach Orientierung geschichtete
Ziehungen. z=0,…,9999, o=0/1, k=0,…,15; erste acht SHA256-Bytes von
MCM-URA1/bootstrap/v1/z={z}/orientation={o}/k={k}, UTF-8 ohne LF,
big-endian uint64 u; r=2·(u mod 16)+1+o. Je Zeile erst 16 ungerade,
dann 16 gerade Indices; später 320.000 Matrixbytes r−1 vor Forschung binden.
Mittelwert der 32 gezogenen Paarwerte, Quantile 1/40 und 39/40 mit
h=9999q und linearer Interpolation. Keine zweite Primärhypothese.

| Ausgang | Urteil | Daraus folgende Entwicklungsentscheidung |
| --- | --- | --- |
| obere Intervallgrenze <0 | FEHLERAUSWAHL_GEGEN_ORIGINALRECENCY_NUETZLICH | Fehlergestützte Auswahl für diesen begrenzten Anwendungsfall beibehalten; kein Ersatz durch R. Der Schritt zur erfahrungsabhängigen Nutzung erhält einen engen Nutzenbeleg, keine allgemeine Bestätigung. |
| untere Intervallgrenze >0 | ORIGINALRECENCY_GEGEN_FEHLERAUSWAHL_BESSER | U-Auswahl für diese Familie nicht als begründeten Zusatznutzen weiter ausbauen. Eine Vereinfachung zur R-Regel wäre als separater Änderungsauftrag zu prüfen, nicht automatisch in den Standard zu übernehmen. |
| Intervall enthält/berührt 0 | KEIN_EINDEUTIGER_UNTERSCHIED | Kein zusätzlicher Nutzen der Fehlerauswahl belegt, aber auch keine Gleichwertigkeit. Kein Tuning oder unveränderter Wiederholungslauf; diesen Auswahlvergleich abschließen und keine Erweiterung der Fehlerlogik daraus rechtfertigen. |
| technische Abweichung | NICHT_AUSWERTBAR | Keine Auswahlentscheidung aus Leistungszahlen; konkreten Fehler und verbleibende Belege berichten. Verbrauchte Einmalfreigabe wird nicht erneuert. |

Die Gegenprognose eines negativen theta ist widerlegbar: ein eindeutig
positives Intervall spricht dagegen; ein Null einschließendes Intervall
bestätigt sie nicht. Eine praktisch relevante Mindestverbesserung oder
Gleichwertigkeitsmarge wird nicht nach Ergebnis ergänzt. Ein statistisch
eindeutiger Vorteil allein verpflichtet nicht zur Nutzung in anderen Aufgaben.

Sekundär vollständig: U/R-Mittelwerte und Paarwerte für Q, G_all=3,5,…,1023,
S=5,9,…,1021 sowie Q_X/Q_Y; Orientierungen getrennt deskriptiv, keine neuen
Erfolgsregeln. Gewinn/Schaden/Netto, besser/schlechter/gleich, maximaler Schaden
mit Positionen, schlechteste Geschichte und kumulierte Zielunterschiede.
Diagnose: keine/eine/mehrere berechtigte Hypothesen, U-Kalt/Warm-Klasse,
gleiche Ausgabe, Kontext/Persistenz und verschiedene Kontexte. Diese Gruppen
erklären Entscheidungen nachträglich; sie ersetzen nicht den Gesamtprimärwert.
S-Gleichheit wird nicht vorausgesetzt, sondern als Ergebnis dokumentiert.

## 7 Unabhängigkeit, Ressourcen und Abnahmekriterien

Vor Forschung benötigt ein gesonderter Entwicklungsauftrag folgende Belege:

1. U bitgleich zu den gebundenen Kernregeln; R verändert ausschließlich
   Auswahl und notwendige Kennzeichnung des Auswahlgrundes. Freeze-Menge,
   Persistenzdefinition, Aufnahme und Feedback bleiben erhalten.
2. Unabhängige U-Referenz und unabhängig implementierte R-Auswahlreferenz,
   beide aus eigenen Zuständen. R-Referenz bestimmt berechtigte Originale
   und Zeitordnung selbst, nicht aus dem Produktionsgewinner.
3. Neutrale Fälle: kein Treffer, ein kalter/warmer Treffer, mehrere Treffer,
   jüngeres Original mit schlechterem Fehler, ursprüngliches Alter gegenüber
   neuer Bestätigung, Promotion/Verdrängung bei ausstehendem Ticket,
   Metadatengleichstände, fehlender Nachfolger und unzulässige Faktoren.
4. Mutationsprüfung der erlaubten R-Auswahleingaben: Änderung gültiger
   EC/EP-Werte oder Warmstatus bei sonst gleichem Bestand darf R-Ausgabe
   nicht ändern; geänderte Originalzeitordnung darf sie regelgemäß ändern.
   Das erfordert neutral erzeugte gültige Zustände, keine Manipulation
   von Forschungsarchiven. U-Reaktionen bleiben referenzgebunden.
5. Ereignisweise Bestands-, Treffer-, Ticket- und Zellgleichheit nach
   Abschnitt 4; absichtlich injizierte Kopplung muss terminal erkannt werden.
6. Analytische und neutrale Nichtäquivalenzprüfung vor Forschungsfreigabe;
   keine Quellenwahl anhand eines günstigen U/R-Leistungsabstands.
7. Unabhängige Quellen-/Bootstrap-/Statistikprüfung und verlustfreies Archiv
   für Originale, Zustände, Hypothesen, Ausgaben, Fehler und alle Updates.
8. Vollständige Ressourcenbilanz für beide Arme und Test der Abbruchpfade.

Beide Arme behalten dieselbe 416-Byte-Bank, dieselben maximal sechs Zellen und
Tickets, höchstens 18 erreichbare Originalframes, höchstens zwei Ausgabeslots
und kombinierte Grenze 20. Zusatzheap je Arm höchstens 16.384 Byte nach
derselben bisherigen Definition; Receipt <=16.384 Byte, UTF-8-Obergrenze
32.768 Byte. Zusätzlich sind der komplette Armgraph einschließlich Basisarm,
Originalwerte/-metadaten, Eingangsrecord, Puffer, Halter und transiente Kopien
für beide offenzulegen. Der Zusatzheap ist ausdrücklich nicht der Gesamtheap.
Physische Aliase innerhalb eines Arms einmal, echte Kopien mehrfach zählen;
keine künstliche Speicherauffüllung oder Gratis-Historie im Beobachter.

Die identischen Fehlerzellen in R dienen der kausalen Kontrolle. Aus dem
Ablationsergebnis folgt kein Sparpotenzial in Bytes oder CPU-Zeit ohne
separaten Nachweis einer später wirklich reduzierten Implementierung.
Eine neue gemeinsame 64-KiB-Hülle aus UFB1 ist nicht Voraussetzung dieser
schmalen, strukturell identischen U/R-Ablation.

Geplante harte Forschungshülle: Supervisor plus höchstens ein Worker im selben
Windows-Job, privater Commit <=536.870.912 Byte; gesamte Frist 3600 s,
Workerfrist 3540 s. Export insgesamt <=64 MiB einschließlich Vorbereitung
und Abschlussprüfung; Vorbereitung <=8 MiB, Quellen <=2 MiB/32 KiB je Fall,
Fallarchive <=32 MiB/512 KiB gzip und 4 MiB expandiert je Fall,
Verwaltung/Postprüfung <=2 MiB, Abschluss <=1 MiB. Tatsächliche R-Belegung
und Exportmachbarkeit sind heute unbekannt und später neutral nachzuweisen.

Quelle/Code/Runtime/Matrix vorab separat binden, danach ausdrückliche
Einmalfreigabe auf den neuen Vorstart-SHA. Geplantes exklusives Ziel
reports/s2uc/ura1-comparison-v1, heute nicht anlegen. Marker verbraucht
die Freigabe auch bei frühem Fehler. Kein Retry, Resume, Ersatz oder Pooling.
Terminal: Bindungs-, Kausalitäts-, Bestands-, Zell-, Referenz-, Ressourcen-
oder Zielvollständigkeitsabweichung. Keine Teilmengenwertung und kein
nachträgliches Synchronisieren divergierter Bestände.

Postlauf ausschließlich unabhängige Archivprüfung; keine erneuten Policies
oder Forschungsquellen. Primärurteil nur bei vollständigen 32 Geschichten,
64 Armläufen, allen Ausgaben/Referenzen, eingehaltenen Grenzen und Cleanup.

## 8 Aussagegrenze und nächster Schritt

URA1 prüft den Nutzen der fehlergestützten Auswahl **bei festgehaltener
Bestands- und Feedbackdynamik gegenüber genau dieser Originalrecency-Regel**.
Es isoliert nicht allein das EMA-Glätten: Kaltstartbehandlung, Fehlergate
gegen Persistenz, Ranking und Gleichstands-Enthaltung werden gemeinsam als
Auswahlpaket abgetragen. Für ihre Einzelbeiträge wäre eine andere Frage nötig.

Ebenso wenig belegt es den Nutzen des Speicherns von Verlaufsspuren an sich,
einen Vorteil gegenüber F, eine bessere Gedächtnisorganisation oder allgemeine
Kognition. Beide Arme besitzen den vorhandenen strukturellen Phasenzugang und
dieselben Originalspuren. Die Frage nach anderen Aufgaben, Audio/Video,
Semantik oder feldinterner Memory bleibt offen. Alte ULZ1-/HX1-/UF1-Ergebnisse
werden weder gepoolt noch durch diesen Entwurf neu interpretiert.

Die Nichtredundanz ist begründet: U gegen L bleibt abgeschlossen; R benutzt
keinen letzten Fehlerwert. HX1/UF1 verändern mehrere Mechanismen, URA1 hält
den verfügbaren Spurenbestand und die Fehlerfortschreibung konstant. Der
zusätzliche Erkenntnisgewinn wäre eine engere Entwicklungsentscheidung über
die Verwendung der bereits berechneten Fehler zur Auswahl.

**Nächster Vorschlag:** Projektleiter entscheidet über diesen einen
Ablationsvertrag. Bei Abnahme ausschließlich ein begrenztes neutrales
Entwicklungspaket für R-Auswahl, unabhängige Referenz und Bestands-/Zell-
Gleichheitsprüfung beauftragen. Abnahmekriterium: U unverändert, Auswahlregel
exakt wie Abschnitt 3, regulär unterschiedliche Entscheidungen möglich,
keine Bestandsrückkopplung, vollständige Ressourcenbelege. Forschungsquellen,
Matrix und Einmallauf bleiben einer späteren gesonderten Freigabe vorbehalten.
Heute wurden ausschließlich dieser Vertrag und die Projektübersichten geändert.
