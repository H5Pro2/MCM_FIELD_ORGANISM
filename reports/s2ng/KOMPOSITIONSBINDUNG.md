# S2-NG: gebundene private Komposition und neutrale Qualifikation

Grundlage bleibt der unveraenderte S2-NG-Plan. Keine S2-MT-Quellen werden
erzeugt, analysiert oder verglichen. `MAIN_GATE = False`.

## Private Anbindung

- Unveraenderte S2-MR-Runtime und S2-LM-Prozessoren; pro Arm eigene
  Runtimekonfiguration, Prozessor-, Feld-, Memory- und Ereignisownerobjekte.
- Die zwei eingefrorenen `AudioRuleBindingV1` binden Quellenstand,
  Memorykonfiguration und Bandplan vor dem ersten Ereignis. Referenz:
  `HISTORICAL_SUM_L1_24`, historische `sum(...)/24`-Reihenfolge. Alternative:
  `ALL_BANDS_24`, ausschliesslich auditive B4/Fast-Anwendbarkeit.
- S2-NE-Referenz delegiert weiterhin an S2-KZ. Beide S2-NE-Direktarme und
  der unveraenderte visuelle S2-KQ-/Direktpfad bleiben erhalten. Keine
  Modifikation bestehender Defaultadapter, kein Monkeypatching, kein Fallback.
- Gemeinsames Tupel unveraenderlicher reduzierter Ereignisse, getrennte
  Fortschreibung. Nur bei der Serialisierung identischer Memoryzustaende
  wird ein gemeinsamer Digestpool verwendet. Dieser ist kein Runtime-Memory.
- Pro Ereignis werden die beiden Feld- und Memoryzustaende auf Gleichheit
  geprueft. Runtime- und regelgebundene Receiptdigests muessen nicht gleich sein.
- Die technische Nachpruefung liest Eingaben, Zustandsketten und jeden
  vollstaendigen Scanbeleg. Keine Wiederholung von Formation, Feldschritt,
  Rezeptoranalyse oder Runtimeverarbeitung. Semantische Scankontrolle mit
  bestehender unabhaengiger NE-Verifikation beziehungsweise direkter
  visueller Tabellenrechnung. Geltende Enthaltung ist technisch gueltig.
- Erst der separate Auswerter erhaelt Zielbindungen. Auditive und visuelle
  N/D/R/L, Gewinne, Fehlzulassungen, Enthaltungen und verworfene Zielkandidaten
  bleiben getrennt. `D = 0` ist `ERHALTUNG_NICHT_GEPRUEFT`.

## Vorab feste Ressourcen

Fuer einen spaeter separat freizugebenden 28-Ereignis-Vergleich:

| Grenze fuer beide Runtimearme einschliesslich Direktbaselines | Maximum |
| --- | ---: |
| Formationen | 40 |
| Feldkontakte | 16.128 |
| Audio-/Visualscanbelege | 16 / 16 |
| Vollstaendige Slotbesuche | 576 |
| Auditive beobachtete Banddifferenzen | 7.680 |
| Visuelle beobachtete Wertvergleiche | 8.192 |
| Interne Kandidatengleichheitsvergleiche | 5.376 |
| Gesamte Scan-Wertvergleiche | 21.248 |
| Zusaetzliche read-only Verifikations-Wertvergleiche | 21.248 |
| Logische Scanoperationen | 416 |
| Formations-L1-Obergrenze | 142.080 |

Je Audioarm 20 Slots und hoechstens 528 Wertvergleiche; je visuellem Arm
16 Slots und hoechstens 800 Wertvergleiche. Kein Short-Circuit.

Kanonische ASCII-JSON-Teilbudgets: maximal 21 Memoryzustaende zu 98.304 Byte,
28 Eingabebelege zu 16.384 Byte, 28 Schrittpaare zu 16.384 Byte, 32 Scanbelege
unter 32.768 Byte sowie Metadaten bis 65.536 Byte. Summe: 4.096.000 Byte.
98.304 Byte verbleiben fuer JSON-Einbettung und Digestpool-Schluessel;
der vollstaendige Beleg ist unabhaengig davon auf 4.194.304 Byte begrenzt.
Carrier-IDs werden nach exakter Profilvalidierung nicht redundant in jedem
Eingabebeleg gespeichert, sondern beim Lesen aus demselben gebundenen Profil
bezogen. Werte, Frames und Geometrie bleiben digestgebunden. Jede verletzte
Teil- oder Gesamtgrenze stoppt; keine nachtraegliche Grenzerhoehung.

## Genau ein neutraler Aufruf

Qualifikations-ID: `s2ng-private-runtime-composition-qualification-20260906-01`.
Ein Modulaufruf `python -m reports.s2ng.qualify_once` startet genau einmal
die neue Testsuite mit 22 Testkoerpern. Der Aufruf archiviert vorab
AST-Testinventar, Quellhashes, Kommando, Interpreter und Grenzen, danach
Exit-Code, Protokolle, Belege und Nachherhashes. Alte Tests werden nicht gestartet.

Neutrale reduzierte Fixture, keine PCM-/RGB-Erzeugung: je Vergleich eine
vollstaendige Formation, zwei auditive Hinweise (Treffer und Unvereinbarkeit)
und ein visueller Hinweis. Beide Arme bilden je einmal. Ein zweiter neutraler
Zwei-Ereignis-Fehlerfall verwendet eine fremde native Audiouhr und prueft,
dass beide Scanfehler den unabhaengigen gueltigen Feldkontakt nicht loeschen.
Insgesamt vier reale neutrale Formationen, zwoelf verarbeitete Runtimeereignisse
und 2.208 Feldkontakte; keine Hauptgeschichte. Hinzu kommen rein synthetische
Bankbelege fuer Arithmetik, unveraenderte Slow-Regel und volle Scanbelegung.

22 Gruppen: feste Regelbindung; Instanz-/Ownertrennung; unveraenderliche
Eingaben; native Zeit-/Digestfehler; Geschwistergleichheit; Read-only und
visuelle Gleichheit; Lifecycle; Vollscans; fehlende/zusatzliche Belege;
vertauschte Belege; Quellen-/Zustandsmanipulation; gueltige Enthaltung trotz
abweichender Vorhersage; Feldkontakt trotz Scanfehler; historische Arithmetik
und Slow; Bankmehrdeutigkeit und Kandidatengleichheit; getrennte Gewinne und
Verluste; auditives D=0; explizit verworfene Zielanwendbarkeit; feste Budgets;
Groessen-/Schreibkonflikt; unveraenderliche Nachauswertung; Ausfuehrungsgrenze.

Auswertungstests mit synthetischen Entscheidungen sind kein Memory- oder
Transferbefund. Kein erneuter Versuch bei fehlgeschlagener Qualifikation.
Der reale S2-MT-Vergleich bleibt separat gesperrt.
