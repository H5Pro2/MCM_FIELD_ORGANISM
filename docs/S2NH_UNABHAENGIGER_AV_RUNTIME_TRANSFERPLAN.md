# S2-NH: kleiner unabhaengiger AV-Runtime-Transferplan

## Status und Frage

Statischer Plan auf Quellenstand `26f256a`, keine neue Lauf-ID. Keine
Implementierung, Vorversiegelung, Quellenerzeugung, Rezeptoranalyse, Tests
oder Ausfuehrung. S2-NG bleibt unveraendert abgeschlossen.

Frage: Erhaelt die vorab gebundene strengere auditive A-Regel richtige Abrufe
unter Konkurrenz und verbessert sie spaetere Abrufe auch auf unabhaengig
festgelegten Quellen, ohne neue Fehlzulassungen zu erzeugen?
Das ist ein neuer Quellenvergleich mit bekannter Generatorart, keine offene
Welt, natuerliche Klangidentitaet oder neue Memorymechanik. Positive
Erhaltungsnenner und Rezeptorabstaende werden nicht vorausgesetzt.

## Unveraenderte Systemarme

Wiederverwendung von S2-MR, S2-NG `RuntimeComparison`, Verifikator und
getrenntem Auswerter, S2-NE-Audioarmen sowie S2-KQ-Visualpfad/Baseline.
Zwei frische getrennte Runtime-, Feld-, Memory- und Ownerobjekte; genau
dieselben einmal gemeinsam materialisierten unveraenderlichen Eingaben.

- Referenz: `HISTORICAL_SUM_L1_24`, Binary64-`sum` in Bandfolge 0..23 / 24,
  inklusive `<= 0.2`, nicht `statistics.mean`.
- Bevorzugter privater Forschungsarm: `ALL_BANDS_24`, maximale absolute
  Banddifferenz auf 0..23 `<= 0.2`, nur fuer B4/Fast.
- Auditory-Slow unveraendert `sum(...)/24 <= 0.02`; vollstaendige 9/3/8-Scans,
  volle 48-Werte-Kandidatengleichheit, A-Aufloesung und A/B-Enthaltung gleich.
- Visualscan, Masken, Feld, Rezeptoren, Schwellen, Slotzahlen und Formation
  bleiben gleich. Keine Umschaltung, Mischung, Rangfolge oder B-Bevorzugung.

Die Runtimekomposition akzeptiert zeitlich eingeschobene Hinweise innerhalb
ihrer bestehenden Grenzen. Historische MT-Quellenhelfer und Haupteinstiege
sind korpusspezifisch; sie werden nicht umetikettiert, gepatcht oder erneut
aufgerufen. Spaeter ist nur eine kleine eigene Quellen-/Ereignisbindung an
die bestehenden Komponententypen erforderlich, keine neue Laufplattform.

## Vorab bestimmte neue Quellen

Die folgenden Regeln sind jetzt fest, ihre Auswertung findet noch nicht
statt. Masterseed: ASCII `s2nh-independent-av-20260906-v1`.
Keine Seedliste, Auswahlrunde oder Ersatzquelle.

13 Grundrezepte `p00` bis `p12`, jeweils gleichberechtigt:

1. `H_i = SHA256(ASCII(masterseed + ':audio:' + pNN))`.
2. Frequenz `f_i = 60 + int.from_bytes(H_i[0:4], 'big') % 2741` Hz.
3. Phase `phi_i = (2.0 * math.pi * int.from_bytes(H_i[4:8], 'big')) / 2**32`.
4. Mono PCM_F32LE, 48000 Hz, 4800 Samples. `f32` ist genau eine Rundung
   nach IEEE Binary32. `a = f32(0.8500000238418579)`.
5. Fuer j=0..4799, in dieser Reihenfolge:
   `theta = ((2.0 * math.pi * f_i * j) / 48000) + phi_i`;
   `u_j = f32(a * math.sin(theta))`;
   `x_j = f32(u_j * f32(0.989912331104279))`.

Der letzte Faktor uebernimmt unveraendert die bereits verwendete
Eingangs-Rechenfolge. Er wird nicht anhand neuer Maxima bestimmt und ist
keine Garantie fuer gueltige neue Rezeptorenergien. Keine Ausgangsnormierung,
Clipping oder Anpassung bei Normalformfehlern. Auch zufaellig gleiche
Frequenzen oder unpassende Geometrie bleiben erhalten.

Zwei zusaetzliche nie trainierte Audiorezepte:

- `p13`: p00 mit `f32(x_j * f32(0.9))`, sonst identisch.
- `p14`: p01 mit `f_1 + 7` Hz anstelle von f_1, derselben Phase und
  unveraenderter obiger Rechenfolge. Kein nachtraegliches Verschieben.

Die Veraenderungen sind vorgegebene technische Belastungen; sie behaupten
keine akustische Identitaet und werden nicht auf `0.02` oder `0.2` abgestimmt.

Visuell dieselbe reine Generatorart wie MT, neue Seeds:
`masterseed + ':visual:' + pNN`. Je 288 RGB-Zellwerte werden aus
`SHA256(ASCII(visual_seed + ':' + block_ordinal_as_3_digits))` ab Block 000
gebildet: Bytes in Reihenfolge, Bits 0..7 jeweils 0/255, erste 288 Werte,
row-major 8x12x3. Jeder Zellwert wird ohne Interpolation auf 135x160 Pixel
expandiert: kanonisches 1920x1080 RGB8. Keine generatorseitigen Rezeptor-,
Memory- oder Schwellenimporte. Keine gezielte Form-/Texturidentitaetsbehauptung.

Visuelle Begleitung von p13 ist p00, von p14 ist p01: die Audioveraenderung
erhaelt eine unveraenderte visuelle Kontrolle. Jeder visuelle Hinweis wird
aus dem erzeugten RGB-Raster vor der Analyse okkludiert: nur skalare
Zell-/Kanalpositionen 0..31 bleiben sichtbar, alle anderen werden null.
Die unabhaengige feste Positionsmaske wird nicht aus Nullwerten abgeleitet.
Kein vorheriges Analysieren des unmaskierten Hinweisbilds und keine
Vervollstaendigung. Die bekannte Begrenzung dieser Maske bleibt bestehen.

## Literale Folge und Zeitbindung

Nur neutrale IDs und technische Ereignistypen gelangen in den Laufpfad.
Die vierte Spalte unten gehoert ausschliesslich zur Evaluationswurzel.
AV = COMPLETE_AV_PERCEPTION, A = PARTIAL_AUDITORY_CUE,
V = PARTIAL_VISUAL_CUE.

| Ereignisse | Typ | Rezept(e) in Reihenfolge | Nur Auswerter |
| --- | --- | --- | --- |
| e01 e02 | AV AV | p00 p01 | A/B erste Erfahrung |
| e03 e04 | A V | p00 p00 | A-Exaktkontrolle unter frueher Konkurrenz |
| e05 e06 e07 e08 e09 e10 e11 e12 e13 | alle AV | p02 p00 p01 p02 p00 p01 p02 p00 p01 | C/A/B interleaved |
| e14 e15 e16 e17 e18 e19 e20 e21 e22 | alle AV | p03 p04 p05 p06 p07 p08 p09 p10 p11 | neun einmalige Druckreize |
| e23 e24 | A V | p13 p13 | A-Pegelvariante / visuelle Exaktkontrolle |
| e25 e26 | A V | p14 p14 | B-Frequenzvariante / visuelle Exaktkontrolle |
| e27 e28 | A V | p12 p12 | nie trainierte unbekannte Kontrolle |

Je Arm eine fortgesetzte Geschichte: die fruehen Hinweise starten keinen
Zustand neu. Genau 20 Formationen, vier auditive und vier visuelle Hinweise.
Keine Vollprobe. A/B je vier, C drei Formationen; Sollsupport 3/3/2 in beiden
Slow-Banken und spaetere A-Verdraengung sind Vorhersagen, keine Startgates.
Die tatsaechlichen Fast-Zuordnungen und PPB-Uebergaenge entscheiden.

Feste Ereignistaktung wie bisher: Ereignis k endet gemeinsam bei k*100 ms,
neue gebundene Feldclock `s2nh-transfer-field-clock`. Audioereignisse erhalten
je zehn neue 480-Sample-Hops in genau einem fortgefuehrten HearingPath;
native Samplezeit schreitet nur bei vorhandener Audiomodalitaet fort.
Visueller Frameindex `(k-1)*3+2`, native Uhr `video.frame`. Gemeinsame Audio-
Abschlussprojektion `[k*100ms-10ms, k*100ms]`, visuelle Projektion vom nativen
Framestart bis k*100ms. Native Rezeptorzeit und gemeinsame Feldzeit bleiben
getrennt. Jedes Auftreten hat eine eigene Quellen-/Fensterbindung, auch bei
identischen Bytes. Keine erfundenen Zwischenframes oder Audiohops.

## Spaetere Vorversiegelung und Ausfuehrungsgrenze

Vor jeder Rezeptoranalyse: Ausfuehrungswurzel mit obigen Rezepten, Seed,
literalem Ereignistupel, Quellfenstern, Regeln, Profil-/Konfigurations- und
Generator-/Interpreterbindungen versiegeln; separate Evaluationswurzel mit
Zielzuordnung und Bewertung. Byte-Digests fuer 15 PCM-Rezepte, 13 volle
RGB-Grundrezepte und die vier getrennten visuellen Cuequellen binden.
Exaktkopien bleiben eigene Quellenidentitaeten. Built-in-math nur bei
bestaetigter spec.origin/sys.builtin_module_names-Herkunft, sonst reale
Moduldatei binden. Keine behaupteten Digests im jetzigen Plan.

Spaeter nur ein gemeinsam materialisiertes Ereignistupel; 24 Audiofenster
und 24 visuelle Frames gemaess Folge. Jeder Rohpayload wird vor Verarbeitung
gegen das Siegel geprueft, hoechstens ein PCM-Fenster und ein RGB-Frame
gleichzeitig; nach Reduktion verwerfen. Keine Rezeptor-Distanzannahme oder
Kandidatentreffermenge als Quellen-Auswahlgate. Keine Ersatzsuche bei D=0,
Quellenkollision, Interferenz oder funktionalem Scheitern.

## Bewertung und Falsifikationskriterien

Technik separat: ein atomarer Gesamtbeleg, eine unabhaengige read-only
Gesamtverifikation ohne erneute Formation, Rezeptoranalyse oder Runtimeaufruf;
danach einmal getrennt auswerten. Gueltige Enthaltung ist technisch gueltig.
Korrespondierende Feld-/Memoryzustaende muessen gleich bleiben, alle Hinweise
read-only; jede Primaerentscheidung muss ihrer unabhaengigen Direktbaseline
entsprechen. Regelabhaengige Runtime-/Receiptdigests duerfen verschieden sein.
Form-, Quellen-, Zeit-, Digest-, Ausfuehrungs- oder Ressourcenfehler bedeuten
NOT_EVALUABLE, keine fachliche Umdeutung. Kein Retry, beide Runtimes schliessen,
Gate False. Keine aktuelle Freigabe dieser Schritte.

Fachlich alle acht Hinweise und beide Modalitaeten vollstaendig berichten:

- Erwartet richtige Kandidaten fuer p00/p13/p14, Enthaltung fuer p12.
  A/B/C, Variantensubtyp und unbekannt existieren nur im Auswerter.
- Zielkandidatenbindung aus eigenen tatsaechlichen Formationswerten und
  vollstaendigen Slotgenerationen/PPB-Uebergaengen, nie aus Hinweiszielwerten.
  Gemischte oder verlorene Zielspuren sichtbar ausweisen, nicht als technische
  Quellenfehler oder saubere Zielstabilisierung klassifizieren.
- Alle Fast-Auswahlen, PPB-Updates, Inventare und vollen Scans erhalten.
  Beobachtete Konkurrenz belegen: andere nicht wertgleiche Kandidaten neben
  Zielspuren. Ohne solche Konkurrenz keine Behauptung gepruefter Erhaltung
  unter Konkurrenz; Fall trotzdem auswerten und separat gruppieren.
- N/D/R/L je Modalitaet, Zeitpunkt, Exakt-/Pegel-/Frequenzfall und tatsaechlicher
  Konkurrenz; `D=R+L`. D sind richtige Referenzzulassungen, nicht bloss
  anwendbare Zielkandidaten. D=0 bleibt ERHALTUNG_NICHT_GEPRUEFT.
- PCM-, volle Rezeptor- und beobachtete Wertegleichheit getrennt ausweisen.
  Eine PCM-Variante mit identischen Rezeptorwerten prueft keine Erhaltung
  nicht bitidentischer Rezeptorhinweise. Visuelle Kontrollen fuellen keine
  auditiven Nenner auf.
- Jeder verlorene richtige Abruf, neue Fehlzulassung, neu richtige Abruf und
  ausgeschlossene Zielkandidat bleibt einzeln sichtbar. Gewinne und vermiedene
  Fehlzulassungen nicht gegen Verluste saldieren. Alle Enthaltungsgruende
  berichten; Mehrdeutigkeit nicht zu Unbekanntheitserkennung umdeuten.

Ein Verlust bei D>0 widerlegt verlustfreie Erhaltung in dieser Pruefmenge;
eine neue Fehlzulassung widerlegt den entsprechenden Sicherheitsanspruch.
Kein neuer richtiger Abruf und keine vermiedene Fehlzulassung bedeutet
keinen nachgewiesenen Selektivitaetsgewinn. Ein Gewinn mit Verlusten ist
gemischt, kein uneingeschraenkter Fortschritt. Auch verfehlte Stabilisierung
oder Verdraengung bleiben regulaere negative Funktionsbefunde. Keine globale
Erfolgsaussage allein aus weniger Treffern oder technisch korrektem Abschluss.

## Unveraenderte Obergrenzen

Je Arm 28 Ereignisse/20 Formationen/8064 Feldkontakte; insgesamt 40
Formationen, 16128 Kontakte, 32 Scanbelege einschliesslich Direktbaselines
(16 auditiv/16 visuell). Maximal 576 Slotbesuche, 7680 auditive
Banddifferenzen, 8192 visuelle Vergleiche, 5376 interne Gleichheitsvergleiche,
zusammen 21248; gleiche getrennte read-only Verifikationsreserve.
416 logische Scanoperationen, Formations-L1-Limit 142080.
Audio je Scan maximal 528, Visual maximal 800 Wertvergleiche.

Bestehende kanonische Teilbudgets: 21 Zustaende zu maximal 98304 Byte,
28 Inputs und 28 Schrittpaare zu je maximal 16384 Byte, 32 Scanbelege jeweils
unter 32768 Byte, Metadaten maximal 65536 Byte; Teilbudgetsumme 4096000 Byte,
gesamter atomarer Beleg hoechstens 4194304 Byte. Keine Grenzerhoehung.

STOPP fuer weitere S2-NG-Ausfuehrungen. Keine Livequellen, Sequenz-/Praegungs-
mechanismen, Produktumstellung, Hypothesenanwendung oder Feldrueckwirkung.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses einen Plans
und gegebenenfalls einer gesondert freigegebenen rezeptorfreien
Vorversiegelung weiter.
