# S2-OA: einmalige neutrale Quellenqualifikation

Qualifikations-ID `s2oa-source-binding-qualification-20260909-01`.
Ein Aufruf `C:/Python314/python.exe -m reports.s2oa.qualify_once` aus workspace.
Genau 18 unabhaengig benannte Testkoerper, kein Retry. Das Testinventar und
saemtliche Quellhashes werden vor dem unittest-Unterprozess gebunden.

Umfang: historische Rezepte; 28-Ereignisfolge; Modalitaetsanwesenheit;
native Indizes und unzulaessige Indexformen; Audio-/Video-/Felduhr;
fortgesetzte Feldfenster; RGB-Okklusion vor Rezeptoranalyse; neutrales PCM;
getrennte Quellenidentitaeten; historische Payloadablehnung; getrennte
Planwurzeln; Manipulationsabwehr; Budgets; Built-in-math; Unveraenderlichkeit.

Neutrale Payloadgrenze: ein 16-Sample-Nullamplitudenrezept mit eigenem Seed
(64 Byte) sowie genau ein JX-Bild ordinal1, das nicht zu OA gehoert
(6.220.800 Byte). Okklusion erfolgt darauf in-place. Keine OA-Payloads,
Rezeptor-, NJ-, Memory-, Feld- oder Runtimeaufrufe. Systemimporte gesperrt.
OA-Planmetadaten und historische Quellenbelege duerfen gelesen werden.

Nur bei Bestehen folgt separat genau ein Aufruf
`C:/Python314/python.exe -m reports.s2oa.preseal_once`, ID
`s2oa-source-preseal-20260909-01`, mit einer unabhaengigen read-only Pruefung.
Jedes Modalitaetsvorkommen wird einmal erzeugt: 22 PCM-/26 RGB-Payloads,
48 Quellenidentitaeten an 28 Ereignissen. Acht Rezept-/Transformationsformen
(ein PCM-, fuenf volle RGB-, zwei okkludierte RGB-Rezepte), keine Deduplizierung.
Historische Vollpayloads muessen uebereinstimmen; neue Cuehashes werden nur
gemessen, nicht auf eine gewuenschte Rezeptorausgabe angepasst.

Maximal ein PCM-Fenster und ein RGB-Frame gleichzeitig; keine Rohdatenablage.
Je Plan-/Belegdatei maximal 262.144 Byte, gesamte Quellenhulle maximal
4.194.304 Byte. Hash-, Profil-, Generator- oder Ausfuehrungsfehler: dokumentierter
Stopp. Keine Ersatzquelle, keine technische Lockerung. Systemgates False;
nur das lokale Quellenfreigabegate wird im einmaligen Sealeraufruf temporaer
geoeffnet und im finally geschlossen. Keine Runtime-/Generationsimplementierung.

Spaeter verbindlich: eine Runtime ohne Reset; visuelle Generationen aus echten
Transaktionen; q05 kein aktueller Verfuegbarkeitsbeleg bei q07; gueltige negative
Inventare und Enthaltungen auswertbar; auditive Slow-Ersetzung und allgemeiner
Dauerbetrieb nicht abgedeckt. Prognosezweig ruht; ME/MI bleiben gesperrt.
