# S2-NQ: statischer Memory-Transferplan auditiver Abdeckung

## Grenze und Fragestellung

Stand 2026-09-08, Ausgangscommit `8fdcbe9`. S2-NP bleibt unveraendert als
begrenzter, regelabhaengiger Abdeckungsbefund geschlossen. Jetzt nur dieser
Plan: keine Implementierung, Quellenmaterialisierung, Tests, Nachberechnung
oder Memoryausfuehrung. Keine neue Laufnummer; alle Systemgates bleiben False.

Frage: Bleibt der beobachtete Abdeckungsvorteil an tatsaechlich gebildeten
Halbprofil-Kandidaten unter A-Konkurrenz und nach Zielverdraengung erhalten?
Beide Sichten lesen denselben Zustand. Ein Panelvorteil ist weder ein
Memorybefund noch eine garantierte richtige oeffentliche Hypothese.
Keine Runtime-, Feld- oder Hypothesenanwendung und keine Produktumstellung.

## Unveraenderte Quellen und zwei Sichten

Verbindliche Herkunft sind der S2-NP-Plan, seine Vorversiegelung und das
verifizierte Rezeptor-/NJ-Materialisat. Relevante kanonische Wurzeldigests:

| Bindung | Digest |
| --- | --- |
| NP execution-plan | bae2b0ef565a5117c28984d40753da39cc1ca82b576e59864c72d57212254664 |
| NP evaluation-plan | 0d2849710a4d321cc63ae42b024f46e0ead3579f0d4dfce9dd4139243e4cd96d |
| NP seal | a72aa07c9dc153f29a187470bce76fb918ce8cbbaeb4f2666c700fb719bf307b |
| NP Materialisierung | f548fa82983390465854b1c1b4824c2a32f5b73669cb85c01dc0de853151b9f7 |

Dateien liegen unter `reports/s2np/s2np-source-preseal-20260907-01/`
und `reports/s2np/s2np-receptor-nj-materialization-20260907-01/`.
Der Vergleich unter `reports/s2np/s2np-coverage-corpus-comparison-20260907-01/`
ist bereits ausgewertet. Dieser Transferkorpus ist damit ausdruecklich
**bereits untersucht**, kein neuer unabhaengiger Bestaetigungskorpus.

Der kleine Transfer fokussiert die zweite NP-Referenz: np-a02 als
Bildungsquelle, np-a01 als Konkurrenzquelle; np-a07 (Exaktkopie), np-a08
(Pegel), np-a09 (Frequenz), np-a10 (spektrale Umgewichtung), np-a11 und
np-a12 (unabhaengige Kontrollen) als Hinweise. np-a03..np-a06 werden nicht
nachtraeglich als Ersatz eingesetzt. Dies ist keine Generalisierungsaussage
ueber beide NP-Quellenfamilien. Alle sechs Hinweise bleiben in jeder der
drei belegten Geschichten enthalten, unabhaengig vom Ergebnis.

| Sicht | Beobachtete Originalindizes, aufsteigend |
| --- | --- |
| CONTIGUOUS_24 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23 |
| DISTRIBUTED_24 | 0,3,4,7,8,11,12,15,16,19,20,23,24,27,28,31,32,35,36,39,40,43,44,47 |

Keine Maskenaenderung am Hinweis, keine Vereinigung beider Sichten und keine
Vollsichtdiagnose im Abruf. Pro Arm nur dessen 24 indexgebundene Cuewerte.
Gespeicherte 48-Werte-Vektoren behalten ihre urspruengliche Bandreihenfolge.
Nicht beobachtete Cuewerte sind dem Scanner und seiner Baseline unzugaenglich.

## Profil und unveraenderte Mechanik

Das qualifizierte S2-NL-Halbprofil und sein atomarer S2-JW-Koordinator bleiben
unveraendert. S2-NJ genau einmal vor der ersten Audiokontaktbildung;
Profil `s2nj.auditory.hann48.output-half.v1`. Kein Quellenfaktor, Clipping
oder Normalisieren. Alte und neue Skalen duerfen nicht gemischt werden.

- Formation: auditives Fast-Matching 0.1, visuelles 0.2, gemeinsame AND-Regel.
- Interne Fast-Rangbindung: `(max(2*d_audio,d_visual),2*d_audio+d_visual,slot_id)`.
- Auditive PPB-Zuordnung 0.01, visuelle PPB-Zuordnung 0.01; native
  Vollvektorarithmetik unveraendert. Kapazitaeten B4/Fast/Audio-Slow 9/3/8,
  Visual-Slow 4; Support-, Update-, Zeit- und Ersetzungsregeln unveraendert.
- In BEIDEN Teilscanarmen: A ausschliesslich `max(terms) <= 0.1`;
  Audio-Slow ausschliesslich historisches `sum(terms)/24 <= 0.01`.
  `terms` folgt jeweils den 24 aufsteigenden Originalindizes. Kein mean/fsum
  als Ersatz, keine Toleranz, kein zusaetzlicher historischer A-Mittelwertarm.
- Vollstaendige drei Bankscans vor Aufloesung. Keine Rangfolge oder
  Deduplication, auch nicht bei mehrfach identischen Audiokandidaten.
  B4/Fast bleiben intern A_RECENT, Audio-Slow bleibt B_STABLE.

Mehrere Treffer einer A-Bank erzwingen interne Mehrdeutigkeit. Genau ein
B4- und ein Fast-Treffer werden nur bei Gleichheit aller tatsaechlich
gespeicherten 48 Werte zu einem A-Kandidaten; sonst interner Konflikt.
Diese Kandidatengleichheitspruefung verwendet keine verdeckten Cuewerte.
Oeffentlich zwei anwendbare Bereiche bedeuten Enthaltung, keinen B-Vorrang.
S2-NM bleibt Profilgrenze: gerundete Gleichheit ist keine verlustfreie
historische Gleichheit und kein Beweis richtiger Quellenzuordnung.

## Literale Bildungsgeschichten

AV-Begleitung unveraendert aus dem bereits gebundenen S2-JX-/S2-NE-Weg:
X = visuelle Fixtureordinal 0; D1..D9 = Ordinale 2..10. Keine neuen visuellen
Druckquellen. Die folgenden Kurzrollen dienen ausschliesslich der Darstellung
und Evaluation; der Laufpfad erhaelt neutrale Quellen- und Ereignis-IDs:

```text
T  = np-a02 + X
Ei = np-a01 + Di
Q  = np-a07 np-a08 np-a09 np-a10 np-a11 np-a12

h01: T E1                         -> Q
h02: E1                           -> Q
h03: T T T T E1 E2 E3 E4 E5 E6 E7 E8 E9 -> Q
h04: frischer Nullzustand          -> np-a07 np-a12
```

Drei frische gebildete Zustaende plus Nullzustand, **16 Formationen,
20 auditive Hinweise, 36 Ereignisse**. Pfeile sind read-only Teilhinweise,
keine Vollproben. Beide Sichten und beide Direktbaselines lesen je Hinweis
denselben Zustand; keine zweite Formationgeschichte pro Arm.
h02 ist die Zielentfernungskontrolle zu h01, kein nachtraegliches Slotloeschen.

Eindeutige technische Ereignisfolge e01..e36, global g=0..35:
h01 g=0..7, h02 g=8..14, h03 g=15..33, h04 g=34..35. Innerhalb dieser
Bereiche genau die obige Reihenfolge. Hinweise zaehlen fuer Quellenzeit,
nicht fuer Formationsschritt oder PPB-Support. Fuer jedes Ereignis:

```text
Audio: Uhr audio.sample, [9600*g,9600*g+4800), Snapshotindex 20*g
Video (nur Formation): Uhr video.frame, [6*g+2,6*g+3)
Gemeinsame Uhr: s2nq-pair-clock, Einheit ns
Audio gemeinsam: [200000000*g,200000000*g+100000000)
Video gemeinsam: [floor((6*g+2)*1000000000/30),200000000*g+100000000)
```

Unterschiedliche Modalitaetsfenster bleiben erhalten; sie ueberlappen im
letzten Drittel des Audiofensters. Die gemeinsame Zeit erzeugt keinen
Feldaufruf. Cues pruefen ausschliesslich die native auditive Quellenzeit.
Jedes Ereignis bekommt eine neue Zeit-/Quellenbindung und einen eigenen
Owner; historische NP-Zeitbelege werden nicht umetikettiert.

Spaeter aus unveraenderten Rezepten direkt analysieren: je Ereignis ein
PCM-Payloadhashcheck vor analyze, danach NJ vor Kontakt; bei Formationen
zusaetzlich RGB-Payloadhashcheck gegen die vorhandene JX-Bindung vor Analyse.
Neue Zeit-/Zustandsdigests und alte Rezept-/Payloadbindungen unterscheiden.
Keine gespeicherten NP-Werte als Slots einsetzen, keine alten Memoryzustaende
laden. Reduzierte Werte duerfen mit den bestehenden Quellenwertbindungen
geprueft werden, ohne eine neue Distanz-Erfolgsauswahl einzufuehren.

## Statische Erreichbarkeit, noch kein Ausfuehrungsbefund

h01: B4 enthaelt T,E1; Fast F0=T/Support1, F1=E1/Support1; Slow leer.
h02: B4 und F0 enthalten nur E1/Support1; Slow leer.
Die einfachen B4-/Fast-Paare stammen jeweils aus derselben Formation.
h04 bleibt vollstaendig leer. Fuer h03 gilt dieselbe bereits abgeleitete
visuelle Trennung wie S2-NE: X/Di und verschiedene Di/Dj mindestens
13/24 > 0.2. Deshalb keine gemeinsamen Fast-Matches in der Druckphase,
auch bei gleicher Audioquelle; keine neue Audiogeometrie dafuer erforderlich.

| Formationsschritt h03 | Fast-Aenderung | PPB in beiden Modalitaeten |
| --- | --- | --- |
| 1 | F0=T/s1 | leer |
| 2 | F0=T/s2/c1 | S0 CREATED/s1 |
| 3 | F0=T/s2/c2 | S0 MATCHED/s2 |
| 4 | F0=T/s2/c3 | S0 MATCHED/s3 |
| 5 | F1=E1/s1 | unveraendert |
| 6 | F2=E2/s1 | unveraendert |
| 7 | F0=E3/s1 ersetzt T | unveraendert |
| 8 | F1=E4/s1 ersetzt E1 | unveraendert |
| 9 | F2=E5/s1 ersetzt E2 | unveraendert |
| 10 | F0=E6/s1 ersetzt E3 | unveraendert |
| 11 | F1=E7/s1 ersetzt E4 | unveraendert |
| 12 | F2=E8/s1 ersetzt E5 | unveraendert |
| 13 | F0=E9/s1 ersetzt E6 | unveraendert |

Fast-Support saettigt bei 2; c ist die Konsolidierungszahl, kein Zusatzslot.
Vor jeder LRU-Ersetzung liegt das Slot-Alter unter 8. B4 nach Schritt 13
chronologisch E1..E9, physisch [E6,E7,E8,E9,E1,E2,E3,E4,E5]; Fast
[E9,E7,E8]. Ziel T ist vollstaendig aus A verdraengt. Keine Druckformation
erreicht Fast-Support2; keine weitere PPB-Zuweisung. PPB-Schrittzaehler
werden dadurch nicht fortgeschrieben, S0 bleibt Support3, alle anderen
Slow-Slots leer. Keine stille Erzeugung stabiler Druckprototypen.

Audio- UND Video-Endprototyp folgen den tatsaechlichen PPB-Eingaben:
`p0=x; p1=(1.0-0.05)*p0+0.05*x; p2=(1.0-0.05)*p1+0.05*x`, genau in
Binary64-Kernreihenfolge. x ist die jeweilige reale Formation, bei Audio
bereits halbiert. Nicht Fast-Endwerte als PPB-Eingang einsetzen und nicht
Bitgleichheit von p2 mit x behaupten. CREATED/MATCHED/MATCHED, Support,
Slotgeneration und vollstaendige Prototypdigests sind spaeter zu belegen.

Gespeicherte NP-Termtabellen, nicht neu berechnete Abstaende, liefern die
Transferhypothese: fuer die sechs gewaehlten Cues liegt A_ALL_BANDS gegen
np-a01 in beiden Sichten ausserhalb 0.1. Die bekannten vier Cues passen
gegen np-a02 in beiden Sichten; np-a12 nur zusammenhaengend, np-a11 in
keiner Sicht. Beispiel np-a12/np-a02: gespeichertes Maximum zusammenhaengend
6.756967058597124e-9, verteilt 0.18058917088271517; gespeicherter verteilter
Mittelwert 0.016784432675437295. Das sind Quellenbeziehungen, keine bereits
gemessenen Distanzen zum gerundeten p2 oder oeffentlichen Memoryentscheidungen.

Prognose: h01 bekannte Cues korrekt A, h03 korrekt B; h02 und h04 Enthaltung.
Bei np-a12 moeglicher Rueckgang falscher A-/B-Zulassungen durch DISTRIBUTED_24;
np-a11 soll abgewiesen werden. Alles sind widerlegbare Erwartungen, keine
Startgates. Zielverlust aus A bedeutet nicht automatisch A-Freiheit des Cues:
die neun bzw. drei gleichen Druckaudios bleiben einzeln zu scannen. Ein
Treffer auf sie kann weiterhin A-interne Mehrdeutigkeit erzwingen.

## Kleinster privater Maskenanschluss

S2-KZ und S2-NE binden 0..23 nicht nur im Scan, sondern in Cuevalidierung
und Hypothesenkonstruktion. S2-NL.bind_cue bindet ebenfalls die zusammenhaengende Sicht.
Ein vertauschter Vollvektor oder ein Austausch globaler MASKED_BANDS waere
keine korrekte Anbindung. Historische Typen, Validatoren und Defaults bleiben.

Notwendig ist eine kleine eigene versionierte Bandplan-/Cuebindung fuer
genau die zwei obigen Literale: Profil, Indexfolge, 24 Werte, Quellenzeit,
Elterndigest und Werte-/Plandigest. Kein allgemeiner Maskenbaukasten.
Der neue private Scan projiziert Kandidaten ueber deren Originalindizes;
die unveraenderte A/B-Entscheidungspolitik erhaelt lediglich maskengebundene
Hypothesen-/Bereichsbelege. Historische Helfer mit festem Komplement duerfen
nicht unbemerkt fuer die verteilte Ausgabe verwendet werden.

CONTIGUOUS_24 wird gegen den vorhandenen Halbprofil-ALL-BANDS-Abruf geprueft.
Die verteilte Variante braucht eine eigene unabhaengige Direktnachrechnung
ohne gemeinsame Scan-/Entscheidungshelfer. Gemeinsame technische Validatoren
sind zulaessig. Keine Aenderung an Formationskoordinator oder Rangschluessel.

Eine Hypothese nennt hoechstens 24 Kandidatenwerte mit den **unbeobachteten
Originalindizes** ihrer Sicht, getrennt von Wahrnehmung. Kein Auffuellen oder
Anwenden. Die beiden Hypothesen haben verschiedene Komplementpositionen;
Erhaltung vergleicht Bereich und eindeutige Slot-/Quellenherkunft, nicht
Gleichheit ihrer 24 Ausgabezahlen. Vollstaendige Kandidatengleichheit bleibt
ein interner Memoryvergleich, kein zusaetzlicher Vollsicht-Cuearm.

## Getrennte Bewertung und Widerlegung

Sollquellen, Subtypen und Erwartungen liegen ausschliesslich im getrennten
Auswerter. Reine Wertegleichheit ohne eindeutige Formationsherkunft reicht
nicht fuer einen richtigen Abruf. Je Geschichte, Exakt/Pegel/Frequenz/Spektral,
tatsaechlicher Cuewertvariation je Sicht und Konkurrenzbefund getrennt:

- Beziehungs-N/D/R/L: N sind bekannte Cue-/Zielslot-Paare mit vorhandenem,
  scanberechtigtem Zielslot; getrennt nach B4, Fast und Slow. D sind die
  zusammenhaengend anwendbaren, R auch verteilt anwendbaren, L verloren.
  D=R+L, auch bei vorheriger Mehrdeutigkeit. Mehrfach gespeicherte Belege
  bleiben explizite Slotzeilen; sie sind keine zusaetzlichen richtigen Abrufe.
- Oeffentliches N/D/R/L: N sind bekannte Cue-/Geschichtsfaelle mit
  scanberechtigtem Ziel; D sind korrekte eindeutige CONTIGUOUS-Hypothesen,
  R korrekt erhaltene DISTRIBUTED-Hypothesen, L verlorene. Eigenstaendiger
  Nenner, keine Auffuellung durch Beziehungen oder Kontroll-Enthaltungen.
- Alle bekannten Faelle ohne Ziel bleiben in der Zielentfernungstabelle;
  nicht stillschweigend als Erfolg aus N ausschliessen. Unabhaengige
  Kontrollen und Nullzustand separat. Falsche Anwendbarkeit pro Nichtzielslot
  mit eigenem Nenner; Fehlzulassung pro oeffentlichem Cuefall mit Nenner.
- Gewinne, jeder Beziehungs-/Abrufverlust, verworfene Zielkandidaten,
  interne/oeffentliche Mehrdeutigkeit und korrekte Enthaltung einzeln
  ausweisen. Keine Verrechnung. D=0: ERHALTUNG_NICHT_GEPRUEFT.

Ein verlustfreier Transfer ist bereits durch einen Beziehungs-/Abrufverlust
oder eine neue Fehlzulassung widerlegt. Ein begrenzter Vorteil verlangt
weniger Fehlzulassungen oder mehr richtige Hypothesen ohne solche Verluste,
bei positivem Varianten-Erhaltungsnenner. Exaktkontrollen ersetzen diesen
nicht; A-Erhaltung und B-Erhaltung bleiben getrennt. Gemischte/negative
Ergebnisse sind regulaer, kein Anlass fuer neue Druckquellen oder Masken.

## Endliche Belegwege und spaetere Freigaben

Bestehende S2-NE-Bausteine fuer atomare Formation, kompakte Gesamtaufzeichnung,
read-only Verifikation und getrennte Bewertung wiederverwenden. Keine neue
Registry, Recorderplattform oder allgemeine Runtime. Technische Verifikation
prueft volle Ereignisfolge, Quellen, Profile, Inventare, PPB-Uebergaenge,
Scanvollstaendigkeit und Vor-/Nachzustandsdigests. Gueltige Enthaltung ist
technisch akzeptabel; Erwartungen werden erst danach einmal ausgewertet.

Feste spaetere Obergrenzen:

- 36 direkte Audioanalysen und 36 NJ-Projektionen, 16 visuelle Analysen;
  keine rollende Pipeline, keine Vollprobe. Acht bestehende PCM-Rezepte.
- Je 20 Hinweise in zwei Sichten und je einer Direktbaseline: 80 Abrufbelege.
- Je Arm/Fall 20 Slotinspektionen (9/3/8), hoechstens 480 beobachtete
  Differenzen plus 48 Kandidatengleichheitsvergleiche, zusammen 528;
  maximal 14 logische Abrufoperationen nach bestehender KZ-Zaehlung.
- Insgesamt maximal 1.600 Slotinspektionen, 38.400 beobachtete Differenzen,
  3.840 Gleichheitsvergleiche, zusammen 42.240 Wertvergleiche und 1.120
  logische Abrufoperationen. Formation separat: bestehende NE-Obergrenze
  71.040 L1-Wertvergleiche bleibt Deckel, keine Erhoehung fuer 16 Formationen.
- Einzelabruf hoechstens 32.768 Byte, NJ-Einzelbeleg 16.384 Byte;
  atomarer Gesamtbeleg einschliesslich beider Direktbaselines hoechstens
  bestehende NE-Grenze 4.194.304 Byte. Konkrete maximale Serialisierung vor
  Hauptfreigabe neutral pruefen, keine spaetere Grenzerhoehung.
- Hoechstens ein PCM-Fenster (19.200 Byte) und ein bestehender Original-RGB-
  Frame (6.220.800 Byte) gleichzeitig; Rohpayloads nach Reduktion verwerfen.
  Dies ist keine neue Behauptung eines gemessenen Prozesspeaks.

Quellen-/Profil-/Zeit-/Normalform-/Digest-/Ressourcenfehler: NOT_EVALUABLE,
Phase, Ereignis und erreichte Zaehler dokumentieren; kein Retry, Clipping,
Quellenaustausch oder Schwellenwechsel. Eine vollstaendige, technisch
gueltige Abweichung von der statischen Spur oder Abrufprognose bleibt ein
fachlicher Gegenbefund, kein nachtraegliches Materialisierungs-Erfolgsgate.

Jetzt nur der Plan. Kleine private Anbindung und neutrale Qualifikation
benoetigen Freigabe; der reale Einmallauf danach eine eigene Freigabe.
NP, historische Komponenten/Belege, fremde Aenderungen und Bootstrap bleiben
unveraendert. Keine Implementierung oder weitere Untersuchung in diesem Schritt.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses begrenzten
Memory-Transferplans und des privaten Maskenanschlusses weiter.
