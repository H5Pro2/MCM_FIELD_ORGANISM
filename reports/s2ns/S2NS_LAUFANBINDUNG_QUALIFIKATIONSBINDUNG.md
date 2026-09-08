# S2-NS: einmalige neutrale Anschlussqualifikation

## Auftrag und unveraenderte Grenzen

Neue Qualifikations-ID: `s2ns-run-binding-qualification-20260908-01`.
Genau ein `unittest`-Aufruf mit 20 neuen Testkoerpern und Fail-Fast.
Kein Retry. Die bestehenden 24 Logiktests werden nur ueber ihren unveraenderten
Ergebnisbeleg und Quellhashes referenziert, nicht erneut ausgefuehrt.
Die spaetere Hauptausfuehrung bleibt separat gesperrt.

Historische Versiegelung, Profile, Quellen, Reihenfolge, Regeln und Budgets
bleiben bytegleich. Neue Quellenanbindung:
`s2ns.direct-endpoint-native-index.v2`; Gesamtbeleg:
`s2ns.formation-chain-recording.v2`.

## Explizit autorisierte Indexkorrektur

Die historische Ausfuehrungswurzel
`bd21e9e5f564e3a11dc2bb0a3dcb40d92a6a5336e863fa10a57c2eb86aa92816`
enthaelt weiterhin `endpoint_snapshot_index`. Dieser wird unveraendert
mitgefuehrt, nicht als NJ-Index interpretiert.

Der Anschluss prueft echte Integer ohne Bool, Nichtnegativitaet und
`window_start_sample % 480 == 0`, bevor er
`nj_snapshot_index = window_start_sample // 480` berechnet.
Fensterlaenge bleibt 4800; Ereignis und Planwurzel binden beide Indizes.
e01: historisch 0 / nativ 0; e02: historisch 1 / nativ 10;
spaetere Fenster entsprechend. Keine zusaetzlichen Hops.

`LogSpectralReceptor.analyze(samples)` hat keinen Indexparameter.
Der private Endpunktadapter prueft die korrigierte Zeitbindung **vor** diesem
Aufruf und konstruiert den Rohzustand danach genau einmal mit dem nativen
Index. Es gibt keine nachtraegliche Umetikettierung eines Rohzustands.
NJ-Zeitvalidierung unveraendert. Spaeter 31 direkte Analysen und 31 NJ-Aufrufe.

## Neutrales Inventar vor dem Aufruf

Die genaue Testliste und alle Quellenhashes werden vor dem einen Testprozess
aus dem statischen AST festgeschrieben. Die 20 Gruppen:

1. Historischer/native Index, spaetere Fenster, Unveraenderlichkeit.
2. Nichtteilbarkeit, negativer Start, Float und Bool.
3. Falscher Index vor jeglicher Analyse abgewiesen.
4. Manipulierte Ereignis-, Plan- und Fensterbindung.
5. Zwei echte neutrale Null-PCM-Endpunkte und ein Null-RGB-Frame,
   Analyse/NJ/Kontakt-Reihenfolge und lesende Quellenrestauration.
6. Fortgesetzte neutrale Geschichte ueber read-only Hinweise.
7. Reale CREATED/MATCHED/REPLACED-Generationen und deren Erhaltung/Loeschung.
8. Manipulierte Generationsherkunft.
9. Manipulierter Formationsbeleg.
10. Fehlendes Ereignis.
11. Vertauschte Ereignisse.
12. Manipulierte PCM-Quellenbindung.
13. Visueller Formationsbeleg in einem auditiven Hinweis.
14. Phasengenauer terminaler Materialisierungsfehler.
15. Auswertungssperre vor erfolgreicher Verifikation.
16. Technisch gueltige Enthaltung trotz fachlicher Hypothesenvorhersage.
17. Variation aus Originalformationen; fehlende Referenz null, D=0 offen.
18. Vollstaendige Gesamtbelegform und getrennte Abschnittsgrenzen.
19. Vorhandenes Zielverzeichnis und bereits vorhandene Verifikation.
20. Geschlossene Gates und gemessene Arbeitszaehler.

Eine einzige neutrale reduzierte Folge (keine NS-Quellen): viermal (0,0),
Hinweis 0; acht Formationen mit Audio .025/.05/.075/.1/.125/.15/.175/.2
und Visual 0; Hinweis .2; (.9,0), (.9,1), (.9,.5), (.9,.5);
Hinweise .9 und 0. Genau 16 echte atomare Formationen und vier Hinweise.
Die konstanten reduzierten Werte sind **synthetische Adapterfixtures**, keine
behaupteten Rezeptormessungen. Jeder reduzierte Rohzustand durchlaeuft NJ.
Zwei weitere echte neutrale Audioanalysen/Projektionen und eine Videoanalyse
pruefen den direkten Materialisierer; keine NS-Generatoren werden verwendet.

Qualifikationsobergrenzen: 16 Memoryformationen; 2 Audioanalysen;
22 NJ-Projektionen; 1 Videoanalyse; 16 Ausfuehrungsscans / 7680 Bandterme;
8 lesende Scans / 3840 Bandterme; 40 lesende Formationskontrollen;
0 NS-Payloads, 0 Feld-/Kontext-/Runtimeaufrufe und 0 Hauptlaeufe.
Wiederholte Manipulationspruefungen verwenden nur Kopien des einen neutralen
Belegs. Keine erneute Memorybildung. Auswertungstests erzeugen keine Scans.

## Gesamthuelle statt Platzhalter

Vor dem Test gilt diese additive Grenze fuer **alle** serialisierten Abschnitte:

| Abschnitt | Anzahl | Byte je Abschnitt |
| --- | ---: | ---: |
| Vollstaendiger nativer Zustand | 17 | 98304 |
| AV-Quellenbeleg inkl. Raw/NJ/Visual/Zeit/Identitaeten | 16 | 16384 |
| Cue-Quellenbeleg inkl. Raw/NJ/Zeit/Identitaeten | 15 | 8192 |
| Formationsresultat, Receipt, Ledger und beide Ownerformen | 16 | 8192 |
| Vollstaendiges Generationsinventar | 15 | 24576 |
| Vollstaendige Zwei-Scan-/Drei-Entscheidungsresultate | 30 | 49152 |
| Ereignisrahmen und Delimiterreserve | 31 | 1024 |
| Gesamtrahmen, Hashlisten, Zaehler, State-Keys und Reserve | 1 | 65536 |

Summe: **4127744 Byte**, unter unveraendert 4194304 Byte.
Die einzelnen Abschnitte werden am tatsaechlichen Beleg geprueft; keine
Grenzerhoehung bei Ueberschreitung. Die wiederholten visuellen Carrier-IDs
stehen einmal in der gebundenen Konfiguration, nicht in jedem Quellenbeleg;
deren exakte Wiederherstellung ist verlustfrei und profilgeprueft. Saemtliche
numerischen Roh-, NJ- und visuellen Werte bleiben explizit gespeichert.

Der neutrale Groessentest verwendet **echte vollstaendige Belegformen** aus
der neutralen Folge, expandiert nur fuer die Serialisierung auf 31/16/15,
17 native Zustandsformen und voll belegte Termtabellen. Dies ist kein
ausgefuehrter 31-Ereignis-Strom und kein fachlich gueltiger Ersatzbeleg.
Es gibt keine leere oder gepolsterte Ersatzhuelle.

## Unabhaengige lesende Arbeit

Spaeter maximal 16 Formationskontrollen, 16128 Fast-Rangterme,
24576 PPB-Auswahlterme und 10752 Updatekomponenten;
17 Zustandsdekodierungen, 31 Quellenbindungen, 1488 Halbierungspruefungen,
48 native Zustandsvalidierungspassagen.
Scans separat: maximal 60 Scans, 1200 Zeilen, 28800 Banddifferenzen,
4320 Kandidatengleichheitsvergleiche. Tatsaechlich prueft ein unabhaengiges
Zwei-Sichten-Rescanpaar beide gespeicherten Implementierungen gemeinsam.
Formations- und Generationsbelege werden dabei nicht durch einen erneuten
Memoryaufruf hergestellt.

Die Gesamtverifikation leitet Generationen erst nach unabhaengiger Pruefung
von Auswahl, Owner, atomarem Resultat, B4 und beiden PPB-Uebergaengen ab.
CREATED/REPLACED binden eine Geburt; MATCHED erhaelt diese; freie/ersetzte
Slots fuehren keine alte Generation im aktuellen Inventar weiter.
Historische Geburtsbelege bleiben als Historie vorhanden, nicht als aktuelle
Bindung. Zielrollen fliessen erst danach in die getrennte Auswertung ein.

Numerisch nachpruefbar: gespeicherte Raw-zu-NJ-Halbierungen, Auswahl/Updates,
Scandifferenzen und Aufloesung. Nicht offline rekonstruiert: PCM/RGB-Payloads,
FFT/Rezeptorreduktion und die interne native TSPM-Receipterzeugung; diese
Herkunft bleibt hashgebunden. Kein Ersatz der historischen Fehlbelege.
