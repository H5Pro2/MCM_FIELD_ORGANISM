# S2-OA: vorab gebundene Quellen-/Haupteinstiegsqualifikation

Neue Qualifikations-ID: `s2oa-main-binding-qualification-20260910-01`.
Genau ein Aufruf mit 14 neuen neutralen Testgruppen. Kein Retry und keine
Wiederholung der historischen 20 Tests. Historische Quellen, administrative
Bindung und die bisherigen Anschlussmodule bleiben bytegleich.

## Neuer Anschluss

`tools/_s2oa_private_main_binding.py`: expliziter Modus OA fuer exakt
28 Ereignisse, 20 Formationen, zwei auditive und sechs visuelle Hinweise.
Eigene Initialisierung einer einzigen MR-Instanz; unveraenderte geerbte
Ereignis-/Transaktions-/Generationsverarbeitung. NEUTRAL bleibt 21/16.

`load_bound()` liest den administrativen v2-Beleg, historische Planwurzeln,
Quellhashes, Umgebung, Profile und beide Qualifikationen. Historische
Budgetabweichung bleibt dokumentiert. Qualifikationsbelege werden ueber
Preregistrierungs-, Ergebnis- und Protokollhashes mitgezaehlt.

Materialisierung: je vorkommender Quelle neu erzeugen, gegebenenfalls bereits
im RGB-Frame okkludieren, Payloadhash pruefen, genau einmal direkt analysieren.
Native Audiofenster mit Index start/480; kein rollender HearingPath.
NJ erfolgt genau einmal vor dem ersten Audiokontakt. 22 Audio- und
26 visuelle Analysen, 22 NJ-Projektionen im spaeteren OA-Lauf. Keine
Deduplizierung. Maximal ein PCM-Payload und ein RGB-Payload gleichzeitig,
keine Rohpayloadablage. Modalitaetsfenster bleiben unterschiedlich.

`run_main_once(run_id)` verlangt ein offenes lokales Gate, eine unbenutzte
ID und ein nicht vorhandenes Verzeichnis. Gate im finally False. Keine
selbstaendige Freigabe; kein historischer Haupteinstieg wird umetikettiert.
Ein atomarer Gesamtbeleg, phasengebundene Fehler, keine fachliche Teilauswertung.
Eine separat beanspruchte `verify_once(out)` prueft ausschliesslich gespeicherte
Belege. `evaluate_once(out)` ist nur nach gueltiger Verifikation zulaessig.
Erwartete Treffer, Supports und Inventare sind ausschliesslich Funktionskriterien.

## Einmaliger neutraler Umfang

Eine vollstaendige **andere** neutrale 28-Ereignis-Folge mit 20 Formationen,
zwei Audio- und sechs Visualhinweisen. Nur synthetische Nullpayloads, nicht
die OA-Rezepte oder die reale Ereignisgeschichte. Neu erzeugte direkte
Rezeptor- und NJ-Ergebnisse je Vorkommen. Ein weiterer neutraler RGB-Payload
fuer die gezielte Hashabwehr, ohne Analyse. Hashfixture: ein Null-RGB-Frame
und ein Null-PCM-Fenster zur unabhaengigen Sollhashbildung.

Die drei isolierten Fehlerfixtures nutzen nur bereits gebundene neutrale
Testeingaben: keine weiteren Rezeptoraufrufe und keine Behauptung, dies
seien reale Materialisierungen. Fehler vor Materialisierung, bei erster
Formation und beim ersten Hinweis. Insgesamt maximal 31 verarbeitete
Runtimeereignisse und 21 Formationsversuche in drei frischen neutralen
Runtimeinstanzen; die vollstaendige Hauptfixture selbst hat genau eine.
Keine OA-Payloads und kein OA-Hauptlauf.

14 Gruppen: volle 28er-Anbindung/Instanzzahl; reale Zusatzgroessen;
native Rezeptor-NJ-Kontaktkette; exakte Zeit-/Quellen-/Maskenabwehr;
unveraenderte NEUTRAL-Grenze/OA-Gate; Hash vor Analyse;
Fehler vor Materialisierung; Formationsfehler/Progress;
Hinweisfehler/unabhaengiges Feld; exklusive Publikation/Verifikation/close;
manipulierte Quellenwurzel; gueltige Enthaltung und falsches Inventar;
Huellenueberschreitungen; falsche Qualifikation/geschlossenes Hauptgate.

Historische/adminstrative Dateien werden zu Beginn nur fuer Referenzbindung
gelesen. Danach Lesesperre fuer reale JSON-Korpora. Generatoranschluss im
neutralen Test durch feste Nullgeneratoren ersetzt; keine historischen
Generator-Haupteinstiege. Die laufende Qualifikation besitzt vor dem Test
noch keinen Ergebnisbeleg: nur diese Resultatpruefung wird im neutralen
historischen Ladecheck durch ihre bereits geschriebene Vorregistrierung
ersetzt. Die reale Ladefunktion verlangt spaeter das bestandene Resultat.

## Unveraenderte Budgets

- Pro vollstaendiger Geschichte: 8.544 Feldkontakte, 16 Scanbelege,
  272 Slotinspektionen, maximal 11.712 Wertvergleiche inkl. Direktbaseline.
- Verifikation separat: 20 Formationspruefungen, 116 Zustandsvalidierungen,
  20.160 Fast-Rangterme, 30.720 PPB-Auswahlterme, 13.440 Updatekomponenten,
  nochmals maximal 11.712 Scanvergleiche und 480 Generationspositionen.
- Neutrale Fehlerpruefungen zusaetzlich separat: maximal sechs
  Zustandsdekodierungen, 16 Scanvalidierungspassagen, 1.408 Scanvergleiche;
  keine erfolgreiche Zusatzformation. Manipulationen werden vor Scans abgewehrt.
- NJ: 22 x 1.024; Formationen: 20 x 1.536; Generationen: 20 x 1.536 Byte.
- Historische Quellenartefakte vollstaendig: 162.321 Byte. Volle gemeinsame
  Reservierung unveraendert 246.289/262.144 Byte, keine getrennten Vollbudgets
  fuer ihre Bestandteile. Metadaten zusammen maximal 65.536 Byte.
- 21 States je 98.304, 28 Inputs und Steps je 16.384, 16 Scans je <32.768.
- Gesamtbeleg samt Referenzen maximal 4.194.304 Byte. Verifikation und
  Auswertung je maximal 262.144 Byte, separat bilanziert. Neutrale Vollhulle
  beinhaltet alle tatsaechlichen NJ-, Formations- und Generationsbelege.
- Neue Qualifikationsmetadaten samt Protokollen und Abschluss: verbleibender
  Metadatenraum, keine Grenzerhoehung. Gesamte neutrale Belegablage einschliesslich
  Fehlerfixtures und referenzierter Vorarbeiten ebenfalls unter 4.194.304 Byte.

Offline-NJ-Pruefung bleibt Herkunfts-/Projektionsbindung, keine Rekonstruktion
ungespeicherter Rohspektren. Feldreceipts sind kein numerischer Feldreplay.
Gueltige negative Funktionsbefunde bleiben auswertbar. Hauptgate False;
ME/MI gesperrt, Prognosezweig ruhend. Reale Ausfuehrung separat freizugeben.
