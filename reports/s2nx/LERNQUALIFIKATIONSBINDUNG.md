# S2-NX: einmalige neutrale Zwei-Lerner-Qualifikation

Vor Aufruf gebunden: `s2nx-learning-qualification-20260909-01`.
Genau ein `python -m reports.s2nx.qualify_learning_once`, darin
`unittest tests.test_s2nx_private_learning -v -f` mit 32 Testkoerpern.
Kein Retry. Testinventar, Quellenhashes, Interpreter und Budgets werden
zuvor in `preregistration.json` festgeschrieben. Historische Tests werden
nicht erneut ausgefuehrt. Keine versiegelten NX-Payloads.

## Anschluss

NW-LearningState, Update, Freeze/Close, AudioReader, atomare IO sowie
historische LINEAR/PERSIST-Arithmetik bleiben unveraendert. Eigene
NX-Komposition mit zwei administrativ gebundenen Historien und je einem
primaeren und unabhaengigen direkten Nullzustand. Keine Uebernahme primaerer
Fits durch die Direktlerner. FIXED_HALF verwendet ausschliesslich das
Literal 0.5. Baselines je Stelle nur einmal je Implementierung.

Der kontrollierte Aufrufpfad prueft beide Ownerbindungen und unveraenderliche
Quellenketten, bindet alle aktiven Prognosen vor Zielgenerierung/-analyse,
bindet nach Beobachtung beide Fehlerbelege und aktualisiert erst danach.
Beide Freezes vor dem ersten Testreaderzugriff; kein Update im Pruefteil.
Die Rechenfunktionen erhalten keine Quellen-, Historien- oder Rollenfelder.
Vier Lernzustaende, gemeinsam hoechstens drei aktuelle Praefix-/Zielvektoren;
aeltere Werte nur in serialisierten Belegen. Kein neues Memorygebiet.

Ein Offline-Digest beweist nicht die historische CPU-Aufrufordnung.
Die Sperren sind Grenzen des privaten kontrollierten Aufrufpfads, keine
Sandbox gegen beliebige Manipulation seiner internen Pythonattribute.

## Testinventar

| Tests | Verbindlicher neutraler Bereich |
| --- | --- |
| 01-04 | Vier eigene Nullzustaende, fremde Historie, vertauschte Owner/Bindungen, NW-Rechenfolge |
| 05-09 | Vorzeitiger Zielzugriff, fehlende/geaenderte Prognose, Updates erst nach Ziel und beiden Fehlerbindungen |
| 10-12 | Zwei Freezes vor Test, zwoelf gemeinsame Pruefeingaben, Praefixreset, Testupdate-/Freeze-Manipulation |
| 13-17 | Metadatenabschottung, unveraenderliche 0.5, historische Kontrollen, Direktunabhaengigkeit, Null/Subnormal/Inf/NaN, ungeclippte Prognosen |
| 18-24 | Gesamtverifikation, Historien-/Freeze-Ketten, 28 Einzelkriterien, gueltige gleiche/initiale Fits, Wechselverluste, Auswertungssperre |
| 25-27 | Vollstaendige Gesamtbelege und Grenzen; Quellenhash-/Zeitfehler; sechs echte neutrale Adapteranalysen |
| 28-32 | Fehlerabschluss und Freigabe beider Owner, Lifecycle, neutraler Einmaleinstieg, Schreibkonflikt, derselbe Zielzustand |

Die synthetische Hauptfixture hat 32 reduzierte neutrale Fenster, keine
NX-PCM-Erzeugung. Zwei weitere synthetische Folgen pruefen Null- und gleiche
informative Fits; eine vierte den neutralen Einmaleinstieg. Ein kontrollierter
Abbruch erfolgt in der zweiten Historie. Kleine einzelne Praefixpruefungen
ersetzen keine reale NX-Geschichte. Nur der Adaptertest analysiert sechs
neutrale konstante PCM-Fenster; zusaetzlich sechs Hashvorbereitungen und ein
ungueltiger Hashfall, insgesamt maximal 13 neutral erzeugte Fenster.
Alle Corpusgeneratoren und der reale NX-Planladeweg sind im Test gesperrt.

## Endliche Grenzen

Spaeter unveraendert 32 Analysen/NJ-Projektionen, acht Updates, 20 Stellen;
je Implementierung 92 Prognosen, 4.416 Fehlerterme, 108 Gewinndifferenzen.
Je Art 3.456 Prognosesubtraktionen/-additionen, 2.496 Multiplikationen,
960 Persistenzkopien, je 768 Updateoperationen, hoechstens acht Divisionen.
Offline separat: 1.536 Halbierungen, je 6.912 Prognosesubtraktionen/-additionen,
4.992 Multiplikationen, 1.920 Kopien, je 1.536 Updateoperationen,
16 Updates/hoechstens 16 Divisionen, 8.832 Fehlerterme, 184 MAE-Summen,
216 Gewinnpruefungen. Divisionen duerfen bei Nullnenner ausbleiben.

Zustand 4.096 Byte; Prognose/Metadaten 65.536 Byte; Gesamtbeleg einschliesslich
Code-/Siegelbindung 2.097.152 Byte; Verifikation/Auswertung je 262.144 Byte.
Vollstaendige synthetische Huelle wird gespeichert und geprueft.
Gesamte neutrale Suite separat im Qualifikationscaller begrenzt: vier
vollstaendige synthetische Ausfuehrungen, ein Abbruch, maximal 24 einzelne
Praefixpruefungen, sechs echte neutrale Analysen/NJ, maximal 249.600 erzeugte
PCM-Byte mit einem Fenster gleichzeitig. Produktions-/Offline-Arbeit und
die 112 Kriterienauswertungen der vier neutralen Evaluationen separat.
Keine Grenzerhoehung nach dem Aufruf.

Der synthetische IO-Test verwendet ausschliesslich temporaere Dateien,
synthetische Quellen und einen neutralen Reader; dort oeffnet er seinen
isolierten Testgate-Kontext kurz und schliesst ihn im finally. Keine
reale Hauptfreigabe. Ansonsten alle Gates False; anschliessend saemtliche
Gates False. ME/MI gesperrt. Kein Nachweis automatischer Historienauswahl.
