# S2-OA: einmalige neutrale Eininstanz-/Generationsqualifikation

Vor Ausfuehrung festgelegt, 2026-09-10. Keine OA-Payloads oder Hauptgeschichte.
ID `s2oa-single-runtime-qualification-20260910-01`, genau ein unittest-Aufruf
mit 20 Testgruppen. Kein Retry. Historische Tests werden nicht wiederholt.

## Anschluss und neutrale Folge

Eine MR-Instanz pro neutralem Testfall, kein Reset innerhalb ihrer Geschichte.
ALL_BANDS_24, Halbprofil, unveraenderte Memory-, Slow-, Visual- und Feldregeln.
Lokaler OA-Nullfeldaufbau aus beiden bekannten Dockanatomien ohne Wahrnehmungs-
inhalt; dadurch kann der erste reale Kontakt spaeter rein visuell sein.
Eigene OA-Zeitbindung: Audiofenster [9600*g,9600*g+4800), native Indizes 20*g;
Visual [6*g+2,6*g+3), gemeinsame Uhr s2oa-continuous-field-clock. Die
Modalitaetsfenster bleiben verschieden; die Pairing-Schnittmenge ist explizit.

Neutrale Hauptfixture: 21 Ereignisse, 16 Formationen, ein auditiver und vier
visuelle Hinweise. Rohzustand Audio konstant 0.5; NJ erzeugt real 0.25.
Keine FFT/Quellenproduktion. Fuenf konstante visuelle Vektoren 0/0.25/0.5/0.75/1,
bei Hinweisen Werte 32..287 bereits null. Nicht die JX/OA-Bildrezepte.
Literale Folge: visueller Nullzustandshinweis; erste Formation 0; visueller
Hinweis; drei weitere Formationen 0; auditiver Hinweis; je vier Formationen
0.25 und 0.5; eine Formation 0.75; visueller Hinweis 0; zweite Formation 0.75;
zwei Formationen 1; abschliessender visueller Hinweis 0.
Damit werden reale Fast-Freigabe, B4-Verlust, visueller stabiler Abruf und
spaetere visuelle Slow-Ersetzung geprueft, ohne 28 OA-Ereignisse auszufuehren.

Drei eigene neutrale Fehlerfixtures: ein AV-Ereignis mit Fehler nach dem
B4-Kandidaten, ein AV-Ereignis mit Feldfehler und AV plus auditiver Hinweis
mit Primaerscanfehler. Erfolgreiche Geschwisterzweige laufen unabhaengig.
Gesamtdeckel Qualifikation: 25 Runtimeereignisse, 19 Formationsversuche,
21 NJ-Projektionen aus synthetischen Rohzustaenden, null Rezeptoranalysen;
keine OA-/PCM-/RGB-Payloadproduktion. Eine weitere leere Eingabe prueft nur
den vorgelagerten phasengenauen Abbruch, ohne Runtimeerzeugung.

## Vollstaendige Belegformen

NJ-Beleg: tatsaechliche Rohzustands-/Rohwert- und Projektionsdigests, Marker,
PCM-/RGB-Herkunft und gemeinsame Quellenbindung; die Halbwerte stehen nur
im gemeinsamen Eingang. Offline wird die NJ-Projektionsbindung ueber diese
gespeicherten Werte geprueft, nicht die Halbierung aus rekonstruierten Rohwerten.

Formation: verlustfreie positionale Kodierung der tatsaechlichen Receipt-,
Ledger- und Ownerfelder. Wiederholte Felder referenzieren bereits gebundene
Konfiguration, Pre-/Postzustand und Ereignis. Vollstaendiger Roundtrip gegen
die nativen Objekte vor Publikation; keinerlei fingierter Ownerabschluss.

Generation: 24 Slotpositionen mit konkreten Geburtsereignisreferenzen oder
null, Transaktionsdigest, vorherigem Kettendigest und 24 Aktionsformen je
Formation. Generationen sind aus diesen tatsaechlichen Transaktionen,
Konfiguration, Slot, Ereignis sowie Pre-/Postzustand eindeutig ableitbar.
MATCHED erhaelt die Geburt; Ablauf/Freiheit entfernt die aktuelle Bindung.
Unabhaengige Ableitung nutzt die direkt nachgerechnete Fast-/PPB-Auswahl,
nicht die primaeren Generationsangaben. Historische Belege sind keine
aktuellen Verfuegbarkeitsbelege fuer einen anderen Zustand.

## Arbeit, Ausgabe und Pruefgrenzen

Unveraenderte administrative Reserven: NJ 22*1024, Formation 20*1536,
Generation 20*1536 Byte. Historische Quellenherkunft 162321 Byte und
administrative Metadaten 25438 Byte werden weiter voll gezaehlt.
Zustaende <=98304, Eingaben/Schritte <=16384, Scans <32768,
Gesamt <=4194304; neue Verwaltungsrahmen zaehlen zu den 65536 Metadaten.
Alle tatsaechlichen Einzelgroessen sowie der volle Beleg werden gespeichert.
Die zusaetzlichen maschinenlesbaren Qualifikationsmetadaten werden ebenfalls
gegen den verbleibenden Metadatenplatz und die Gesamthuelle bilanziert.

Je unabhaengiger Belegpruefung gelten die OA-Deckel: 20 Formationspruefungen,
20160 Fast-Rangterme, 30720 PPB-Auswahlterme, 13440 Updatekomponenten,
116 konservativ belastete Zustandsvalidierungspassagen; 11712 Scanvergleiche,
28 Quellenbindungen und 480 Slot-Generationskontrollen. Keine neuen
Formationen/Abrufe/Feldfortschreibungen durch den Offline-Pruefer.
Qualifikation: vier regulaere Belegpruefungen (Hauptfixture und drei
Fehlerfixtures), ein manipulierter Generationsbeleg bis zur ersten Formation,
ein manipulierter Initialzustand sowie ein reiner Bindungsfehlerbeleg.
Keine Vollwiederholung des Hauptfalls. Verifikationsdateien gemeinsam <=262144.

Testinventar vor Aufruf: Folge, Lifecycle, Zeiten, NJ-Projektion,
Read-only/Enthaltung, Scans, MATCHED, visuelle Ersetzung, Fast-Freigabe,
historisch/aktuell, Generationsmanipulation, Zustandsmanipulation,
Quellenmanipulation, reale Zusatzbeleggroessen, Gesamthuelle, atomarer Fehler,
Feldfehler, Scanfehler, phasengenauer Abbruch, Hauptgates/Ereignisordnung.

Gates False. Der Anschluss verarbeitet nur bereits gebundene neutrale
Inputobjekte; kein OA-Quellenlade-/Materialisierungseinstieg wird ausgefuehrt.
Funktionale Sollausgaenge beeinflussen nicht die technische Verifikation.
Eininstanzanschluss ist keine allgemeine Dauerbetriebsqualifikation und
deckt keine auditive Slow-Ersetzung ab. ME/MI gesperrt, Prognosezweig ruht.
