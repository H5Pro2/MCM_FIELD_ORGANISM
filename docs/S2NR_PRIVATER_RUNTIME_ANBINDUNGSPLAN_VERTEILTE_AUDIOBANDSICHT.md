# S2-NR: verteilte auditive Sicht im privaten Halbprofil-Runtimepfad

Stand 2026-09-08, Ausgangscommit `3ee2f63`. Ausschliesslich statischer Plan;
keine Laufnummer, Quellenproduktion, Versiegelung, Implementierung oder Tests.
S2-NQ bleibt unveraendert abgeschlossen: vier richtige A- und vier richtige
B-Abrufe erhalten, davon jeweils drei variierte Hinweise; zwei verhinderte
Fehlzulassungen derselben Kontrollquelle in zwei Geschichten. Das ist keine
unabhaengige Robustheitsbestaetigung und keine verbesserte Lernregel.

## Zwei fest gebundene Arme

Bestehender NJ/NL/NN-Halbprofilpfad, MR-Lifecycle und LM-Geschwisterzweige.
Gemeinsame unveraenderliche Rezeptormaterialisate, aber zwei frische,
getrennte Runtime-, Feld-, Memory- und Ownerinstanzen. Vor Ereignis 1:

| Arm | Beobachtete Originalindizes |
| --- | --- |
| CONTIGUOUS_24 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23 |
| DISTRIBUTED_24 | 0,3,4,7,8,11,12,15,16,19,20,23,24,27,28,31,32,35,36,39,40,43,44,47 |

Beide verwenden NQ-Scan und NQ-Direktbaseline: A `max(terms) <= 0.1`,
Slow historisches `sum(terms)/24 <= 0.01`, Binary64 in aufsteigender
Originalindexfolge. Vollstaendiger 9/3/8-Scan, unveraenderte A/B-Aufloesung,
kein Ranking, Fallback, B-Vorrang oder Maskenwechsel. Hypothesen enthalten
nur 24 Kandidatenwerte im jeweiligen Komplement, keine Anwendung.

Formation unveraendert: Fast Audio 0.1 UND Video 0.2; Rang
`(max(2*d_audio,d_visual),2*d_audio+d_visual,slot_id)`. PPB Audio/Video
je 0.01; Kapazitaeten, Support, Updates und Zeitparameter unveraendert.
NJ genau einmal mit 0.5 vor jedem normalformgebundenen Audiokontakt.
Feld und Memory erhalten dieselben skalierten Audio- und originalen
Visualwerte. Keine Rueckverstaerkung und keine Alt-/Neu-Feldgleichheit.

## Kleinster notwendiger Anschluss

Der existierende NG/NN-Aufruf ist nicht unveraendert maskenfaehig:
NN.bind_event, NG.pack_input, NG.AudioAdapter und AudioRuleBindingV1 binden
den historischen KZ-Bandplan. MR._validate_hypothesis akzeptiert exakt den
historischen AuditoryPartialCueHypothesis48V1; NQ.Hypothesis hat weder dessen
Typ noch dessen Digestoberflaeche. Ein Umbenennen oder Umordnen waere falsch.

Erforderlich sind nur folgende ausdruecklich versionierte Anschluesse:

- Private Bindung `(Halbprofil, ALL_BANDS_24, NQ-Bandplan, Komponentenhashes)`
  vor Beginn, genau zwei erlaubte Sichten. Keine frei konfigurierbare Maske.
- Eigene maskengebundene Cueoperation und Eingabepackung: gemeinsamer
  Wahrnehmungs-/Quellenelternbeleg und identischer Feldpayload; je Arm eigene
  indexgebundene Cue-/Operationsbindung. Die drei LM-Projektionsdigests
  bleiben derselbe gemeinsame Wahrnehmungsbeleg. Die private Packpruefung
  belegt zusaetzlich dessen Beziehung zum jeweiligen Cue, statt historisch
  `cue_digest == perception_digest` vorauszusetzen. Alte Validatoren bleiben.
- Schlanker Audioadapter uebergibt NQ.retrieve bzw. NQ.direct nur den
  vorab gebundenen 24-Werte-Cue und Zustand. Keine verborgenen Cuewerte oder
  andere Sicht gelangen in diese Funktionen. Der Quellen-/Feldbinder darf
  die 48 echten Werte besitzen; er darf keine Trefferentscheidung vorgeben.
- Neue exakte Runtime-Hypothesenform um den validierten NQ-Beleg mit
  Bandplan, Komplement, Herkunft und eigenem Digest. Notwendig ist eine
  geschlossene, versionierte Erweiterung der MR-Hypothesenunion samt
  Pruefung gegen die vorab gebundene Runtimekonfiguration. Historische
  Konfiguration, kanonische Payloads, Defaults und Typakzeptanz bleiben
  unveraendert; kein `object`, Duck-Typing oder gefaelschter KZ-Typ als Ersatz.
- Private Komposition/Offline-Pruefung nach NG: zwei Sichten statt zwei
  A-Regeln, armweise Operationsbelege, NQ-Scanverifikation. LM-Prozessor,
  LO-Feldadapter, atomarer Koordinator und Memorykerne bleiben unveraendert.
  Native Gegenpruefung der zusammenhaengenden Sicht bleibt Referenzkontrolle.

Dies benennt eine notwendige Runtime-Typanbindung, keine neue Memory- oder
Entscheidungsmechanik. Historische NG/NO-Haupteinstiege nicht umetikettieren;
keine globalen Konstanten austauschen. Ein kleiner privater Aufrufer und
ein atomarer Gesamtbeleg genuegen, keine neue Recorderplattform.

## Neuer Quellenstrom, jetzt literal festgelegt

Neue synthetische Quellen, keine alten NP/NQ-Payloads. Spaeter vor jeder
Rezeptor- oder Distanzanalyse alle Rezepte, Payloadhashes, Ereignisse,
Python-/math-/Generator-/Profil-/Codeidentitaeten und diesen Dokumenthash
in getrennten Ausfuehrungs- und Evaluationswurzeln versiegeln. Der Plan
behauptet heute keine schon erzeugten Hashes. Keine Auswahl nach Messung,
kein Ersatzseed, Clipping, Eingangsabschwaechung oder Nachnormalisieren.

Sechs Mono-PCM_F32LE-Rezepte, 48.000 Hz, 4.800 Samples. Reiner vorhandener
NC-pcm_bytes-Baustein mit einer Partialgruppe, ohne historischen Einstieg.
Partialfolge 0/1/2. Form a0=(8/20,2/20,1/20), a1=(6/20,3/40,3/80).

| Quelle | Frequenzen in ganzzahligen mHz | Amplituden | Phasenseed |
| --- | --- | --- | --- |
| nr-a01 | 1837000,3674000,5511000 | a0 | s2nr-pcm-001 |
| nr-a02 | 443000,886000,1329000 | a0 | s2nr-pcm-002 |
| nr-a03 | 1837000,3674000,5511000 | a0 | s2nr-pcm-001 |
| nr-a04 | 1837000,3674000,5511000 | a1 | s2nr-pcm-001 |
| nr-a05 | 1892110,3784220,5676330 | a0 | s2nr-pcm-001 |
| nr-a06 | 739000,3181000,9473000 | a0 | s2nr-pcm-003 |

Phase: erste vier SHA-256-Bytes von `seed+':'+str(i)`, unsigned LE u;
`(float(u)/4294967296.0)*math.tau`. Je j: `t=float(j)/48000.0`,
`f=float(millihz)/1000.0`, `a=float(zaehler)/float(nenner)`;
`angle=((math.tau*f)*t)+phase`; Summe ab 0.0 in Partialfolge, einmal
`struct.pack_into('<f',...)` am Ende. Keine Zwischen-Float32-Rundung.
a01/a03 bleiben getrennte Quellenidentitaeten bei beabsichtigter Bytegleichheit.
Andere Kollisionen werden berichtet, nicht entfernt.

Elf neue volle RGB8-Rezepte nr-v01..nr-v11, 1920x1080, Raster 8x12x3,
Seed jeweils `s2nr-independent-av-20260908-v1:visual:vNN` (NN=01..11).
Bestehende reine NH-rgb_payload-Rechenfolge mit partial=False: SHA-256 von
`seed+':'+block_3stellig`, Bytefolge und Bits 0..7 auf 0/255 abbilden;
erste 288 Werte in Zeile/Spalte/RGB-Reihenfolge, Zellen 135x160 Pixel.
Keine nachtraegliche Wahl besonders trennender Bilder. Keine visuellen Cues.

Neutrale literale Folge; `AV`=vollstaendige Formation, `A`=read-only Audiohinweis:

| Ereignis | Typ | Audio | Video |
| --- | --- | --- | --- |
| e01 | AV | nr-a02 | nr-v02 |
| e02 | A | nr-a03 | keines |
| e03 | AV | nr-a01 | nr-v01 |
| e04 | A | nr-a04 | keines |
| e05 | AV | nr-a01 | nr-v01 |
| e06 | AV | nr-a01 | nr-v01 |
| e07 | AV | nr-a01 | nr-v01 |
| e08 | AV | nr-a02 | nr-v03 |
| e09 | AV | nr-a02 | nr-v04 |
| e10 | AV | nr-a02 | nr-v05 |
| e11 | AV | nr-a02 | nr-v06 |
| e12 | AV | nr-a02 | nr-v07 |
| e13 | AV | nr-a02 | nr-v08 |
| e14 | AV | nr-a02 | nr-v09 |
| e15 | AV | nr-a02 | nr-v10 |
| e16 | AV | nr-a02 | nr-v11 |
| e17 | A | nr-a05 | keines |
| e18 | A | nr-a06 | keines |

18 Ereignisse, 14 Formationen, vier Hinweise pro Arm, kein Neustart.
Der erste AV-Kontakt erhaelt die bestehende NG/LO-Initialisierungsform.
Ein fortgefuehrter HearingPath verarbeitet je Ereignis zehn neue Hops:
Audio n=1..18 auf audio.sample, [(n-1)*4800,n*4800), Endpunktindex
10*(n-1). 180 Hops, 171 rollende Abschluesse; nur 18 Endpunkte an NJ.
Keine zweite Analyse pro Sicht. Rohpayloadhash jeweils vor Verarbeitung.

Explizite Felduhr `s2nr-transfer-field-clock`, E=n*100000000 ns.
Bestehende NO-Zeitabbildung: Audio-Endpunkt gemeinsam [E-10000000,E),
Video nur AV, native video.frame [3*(n-1)+2,3*n), gemeinsam
[floor((3*(n-1)+2)*1000000000/30),E). Feldschritt [(n-1)*100000000,E).
Native 100-ms-Audiohistorie, 10-ms-Abschlusskontakt und visuelles Fenster
bleiben unterschiedliche Begriffe. Keine Fensterstreckung oder neue Uhr.

## Vorhersage, Erreichbarkeit und Bewertung

Nur Evaluationswurzel: nr-a01 ist Ziel, nr-a02 Konkurrenz/Druckaudio;
a03 Exaktkontrolle vor Zielbildung, a04 Pegelvariante frueh, a05
Frequenzvariante spaet, a06 unabhaengige Kontrolle ohne Ziel. Keine Sollrolle
oder Zielwerte im Laufpfad. Frequenzvariation ist eine Pruefannahme, kein
vorausgesetzter Nachweis gleicher akustischer Identitaet.

Vorhersage: e02 Enthaltung trotz vorhandenem Konkurrenten; e04 richtige
A-Hypothese unter Konkurrenz; e17 richtige B-Hypothese nach Zielverlust
aus A; e18 Enthaltung. Die verteilte Sicht soll richtige Referenzabrufe
erhalten und darf keine neue Fehlzulassung erzeugen. Ein Gewinn wird nicht
vorausgesetzt; Gleichstand, Verlust und vollstaendige Enthaltung sind auswertbar.

Statisch sicher: neun spaetere Formationen verdraengen fruehere B4-Eintraege.
Fast-Trennung und PPB-Herkunft sind bei diesen neuen RGB-Werten dagegen
ungeprueft. Falls die AV-Matches wie vorhergesagt trennen, erhaelt nr-a01
durch vier Expositionen CREATED/MATCHED/MATCHED, Support 3, dann LRU-Verlust
aus Fast; die neun Druckformationen konsolidieren nicht. Falls neue Quellen
Fast verschmelzen, Druckaudio Slow veraendert oder das Ziel nicht stabilisiert,
ist genau dieser Verlauf zu berichten. Keine passenden Distanzen, Sollsupports,
Slotinventare oder Treffer als technisches Startgate voraussetzen.

Je Sicht tatsaechliche Formationseingaenge, Fast-Auswahl, PPB-Generation,
Support, Updates, Vermischung und Verdraengung protokollieren. NQ-Auswertung
wiederverwenden: Quellenherkunft statt blosser Wertegleichheit; Rezeptorvariation
gegen vorherige quellengebundene Formationseingaenge auf denselben Indizes.
Cue-/Slotabweichung separat, insbesondere PPB-Drift; fehlende/uneindeutige
Referenz null. Keine Referenzbildung ueber Geschichten, Prototypen oder Digests.

Oeffentliches N/D/R/L getrennt A/frueh und B/spaet: N bekannte Hinweise mit
berechtigtem Ziel, D richtige eindeutige C-Abrufe, R auch D-richtig im selben
Bereich, L verloren. Beziehungserhaltung separat je B4/Fast/Slow-Zielslot,
auch wenn C mehrdeutig war. D=R+L; D=0 bedeutet ERHALTUNG_NICHT_GEPRUEFT.
Jeden Gewinn, Verlust, verworfenen Zielkandidaten, Nichtzieltreffer,
Fehlzulassung und interne/oeffentliche Mehrdeutigkeit einzeln mit Nennern
ausweisen. e02 und e18 nicht als Erhaltungserfolge rechnen.

Begrenzter Zusatznutzen erfordert weniger Fehlzulassungen oder mehr richtige
Hypothesen ohne neue Fehlzulassung oder Beziehungs-/Abrufverlust und mit
positivem Varianten-Erhaltungsnenner. A- und B-Anspruch nur fuer den jeweils
positiven Nenner. Ein Verlust widerlegt verlustfreien Transfer in diesem
Strom. Zwei unterschiedliche Varianten, je nur ein positiver A-/B-Prueffall,
und eine unbekannte Quelle sind eine kleine Stichprobe; Exaktcue wird hier
nur bei Zielabwesenheit geprueft. Keine allgemeine Robustheitsbehauptung.

## Technische Kontrollen und endliche Grenzen

Nach jedem Ereignis identische korrespondierende Feld-/Memorywerte und
Zustandsdigests, getrennte Instanzen. Gemeinsame Quellen-/Feldprojektion;
Masken-, Runtimegesamt- und Receiptdigests duerfen armgebunden verschieden
sein. Alle Hinweise bleiben read-only bezogen auf Memory; Feldkontakt
bleibt unabhaengig auch bei Scanfehler. close() beider Runtimes nach Ablauf
oder Fehler. Keine Hypothesenanwendung und keine Memoryrueckkopplung.

- Vorversiegelung spaeter: 6 PCM-, 11 RGB-Quellen; je hoechstens ein
  PCM-Fenster (19.200 Byte) und RGB-Frame (6.220.800 Byte), keine Rohablage.
- Gemeinsame Materialisierung spaeter: 18 Audiofenster, 180 Hops,
  171 Abschluesse, 18 NJ-Endpunkte, 14 visuelle Analysen.
- Zwei Arme: je 18 Runtimeereignisse/14 Formationen, insgesamt 28
  Formationen, 9.792 Feldkontakte und 16 Abrufbelege inklusive Baselines.
- Abruf: maximal 320 Slotinspektionen, 7.680 Banddifferenzen plus 768
  Gleichheitsvergleiche, 224 logische Operationen. Formation separat
  99.456 konservativ belastete L1-Terme fuer beide Arme.
- Offline-Verifikation separat: 16 Armpruefungen mit denselben oberen
  320/7.680/768 Scanzaehlern; maximal 28 Formationspruefungen, 28.224
  Fast-Rangterme, 43.008 PPB-Auswahlterme, 18.816 Updatekomponenten.
  Zustands-/Quellen-/Typvalidierungen vor dem spaeteren neutralen Aufruf
  separat konkret zaehlen und binden, nicht dem Scanbudget unterschieben.
- Bestehende NG-Limits unveraendert: 98.304 Byte je Zustand, 16.384 je
  gepacktem Eingang/Ereignispaar, 32.768 je Scan, 65.536 Metadaten;
  Gesamtbeleg maximal 4.194.304 Byte. Gleichheit erlaubt kanonische
  Zustandsreferenzen, nicht gemeinsam mutable Runtimezustaende. Bei 15
  eindeutigen Zustaenden, 18 Eingangs-/Ereignispaaren und 16 Scans ergibt
  das 2.654.208 Byte Teilbudget vor JSON-Huelle und Quellen-/NJ-Belegen.
  Diese muessen im unveraenderten Gesamtlimit Platz finden; konkret neutral
  pruefen, keine spaetere Grenzerhoehung. Kein neuer Prozesspeaknachweis.

Spaeter genau ein atomarer Beleg, eine unabhaengige read-only Verifikation,
erst dann getrennte Bewertung. Technisch gueltige Enthaltungen akzeptieren.
NJ-Herkunftsbindung und gerundete Werte pruefen; ohne gespeicherte Rohspektren
keine numerische Rueckrekonstruktion behaupten. Quellen-/Profil-/Zeit-/
Normalform-/Ressourcenfehler: NOT_EVALUABLE, kein Retry oder Quellenersatz.

Jetzt bleibt es bei diesem Plan. Quellenbindung/Vorversiegelung, neutrale
Anschlussqualifikation und realer Einmallauf benoetigen spaetere Freigaben.
Alle Gates False; historische Defaults, Belege, fremde Aenderungen und
Bootstrap unveraendert. Keine Wiederholung von NQ.

WEITER: Am besten geht es jetzt mit der Analystenpruefung des minimalen
versionierten Masken-/Hypothesenanschlusses und des neuen festen Stroms weiter.
