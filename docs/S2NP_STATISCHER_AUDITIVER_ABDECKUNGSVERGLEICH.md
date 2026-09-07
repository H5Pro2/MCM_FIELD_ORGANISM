# S2-NP: statischer auditiver Abdeckungsvergleich

## Auftrag und Abschlussgrenze

Stand 2026-09-07, Ausgangscommit `cb5f950`. Nur dieser Plan; keine
Implementierung, Payloaderzeugung, Vorversiegelung, Rezeptoranalyse, Tests
oder Auswertung. Keine neue Laufnummer. S2-NO bleibt als gueltiger gemischter
Funktionsbefund geschlossen, ebenso dessen read-only e25/e27-Diagnosezweig.
Keine weiteren Berechnungen zu diesen Hinweisen und keine Optimierung am
NO-/NH-Korpus. Die bestehenden Abrufregeln und Enthaltungen bleiben erhalten.

Frage: Traegt eine vorab verteilte Sicht auf 24 der 48 Audiobaender mehr
unterscheidende Evidenz als die zusammenhaengende Sicht, ohne bislang
anwendbare bekannte Varianten zu verlieren? Untersucht werden feste
Quellenbeziehungen, **kein Memoryabruf und keine Bekanntheitserkennung**.

## Drei feste Sichten

Indizes folgen der unveraenderten, aufsteigend frequenzgeordneten
Log-Filterbank. Auswahl ausschliesslich durch Indexarithmetik, ohne Seed,
Bild-/Audiowerte, Rollen, Filterbankenergie oder spaetere Ergebnisse:

| Sicht | Literal gebundene Indizes | Verwendung |
| --- | --- | --- |
| CONTIGUOUS_24 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23 | bestehende Abdeckung |
| DISTRIBUTED_24 | 0,3,4,7,8,11,12,15,16,19,20,23,24,27,28,31,32,35,36,39,40,43,44,47 | pro Viererblock Position 0 und 3, ueber alle 48 Baender |
| FULL_48_DIAGNOSTIC | 0..47, aufsteigend, vollstaendig | getrennte diagnostische Referenz |

Die verteilte Sicht ist gleichmaessig nach **Bandindex**, nicht nach linearen
Hz-Abstaenden. Sie ist nicht als optimale oder repraesentative Bandwahl
behauptet. Spaeter die unveraenderten Bandgrenzen als Geometriebeleg mitfuehren.
Keine zweite verteilte Maske, kein Maskensweep oder ergebnisabhaengiger Wechsel.

Je Sicht wird dieselbe Indexmenge auf Hinweis und Vergleichsquelle angewandt.
24-Band-Vergleicher erhalten ausschliesslich 24 indexgebundene Werte beider
Seiten, nicht den Vollvektor. Verdeckte Positionen werden weder aufgefuellt
noch als Null interpretiert. FULL_48_DIAGNOSTIC erhaelt eine eigene
Diagnoseeingabe; seine Werte, Treffer und Entscheidungen duerfen nicht in
einen 24-Band-Vergleich zurueckfliessen. Keine Vereinigung der Teilmasken.

## Profil und feste Vergleichsbedeutung

Unveraenderter `LogSpectralReceptor`, Konfiguration
`48000/4800/480/50.0/18000.0/48`, symmetrisches Hann-Fenster und bestehende
FFT-/Filterbankreduktion. Spaeter genau ein direkter `analyze`-Aufruf je
Quelle, keine rollende Pipeline. Dessen reale Ausgabe als korrekt
quellen-/zeitgebundenen `AuditoryReceptorState` an die vorhandene
`project_auditory_half_v1` uebergeben: genau einmal Faktor `0.5`.
Profil `s2nj.auditory.hann48.output-half.v1`, Geometrie
`auditory.log48.50-18000.w4800.h480.half.v1`; Originalprofil, NJ-Profil,
Codehashes und gerundete Werte getrennt binden. Keine Audiokontakt-,
Memory-, Feld- oder Runtimekonstruktion erforderlich.

Je geordnetem Hinweis-/Referenzpaar und Sicht I:

```text
terms = tuple(abs(reference[i] - cue[i]) for i in I)  # Binary64, Indexfolge
m = sum(terms) / len(I)                             # historisch, nicht mean/fsum
k = max(terms)
```

| Bestehende Bedingung, hier nur Diagnose | Pruefung |
| --- | --- |
| A_HISTORICAL_SUM | m <= 0.1 |
| A_ALL_BANDS | k <= 0.1 |
| SLOW_HISTORICAL_SUM | m <= 0.01 |

Keine neue Regel, Gewichtung, Toleranz oder Schwelle. Die Slow-Bedingung
bleibt Mittelwert, niemals Maximum; die drei Bedingungen werden getrennt
berichtet und nicht kombiniert. Bei 24 Werten bleibt die jeweilige
Rechenfolge `sum(...)/24` bzw. `max(...)`. Bei der Vollreferenz wird durch
48 geteilt, nicht durch 24. Das ist eine gekennzeichnete Vollsichtdiagnose,
keine native PPB-/Fast-Formation: deren `fsum/48` wird hier nicht ausgefuehrt.
FULL_48 ist kein garantierter oberer Leistungswert; Mittelwertverduennung
und die strengere Vollmenge eines Maximumtests bleiben interpretierbar.

Die Halbprofilgrenze aus S2-NM bleibt bestehen: Gleichheit meint tatsaechlich
gerundete Werte, keine verlustfreie historische Migration. Endlichkeit und
NJ-Normalform sind technische Anforderungen, Trennung/Treffer keine Gates.
Keine Ausgangsskalierung ausser NJ, kein Clipping, kein Flush-to-zero.

## Neue Quellen, vor jeder Analyse festgelegt

Zwoelf Quellen, jeweils mono PCM_F32LE, 48.000 Hz, 4.800 Samples, 19.200 Byte.
Zwei Referenzen, je Exaktkontrolle und drei feste Varianten, zwei unabhaengige
Kontrollquellen. Synthetische Partialtonmischungen, keine natuerlichen
Objekt-/Klangidentitaeten. Quellenrelationen sind vorgegebene Pruefannahmen.
Insbesondere ist die spektrale Umgewichtung ein Belastungsfall.

Amplitudenformen in Partialfolge 0/1/2:

- a0: `(8/20, 2/20, 1/20)`.
- a1: `(6/20, 3/40, 3/80)`, Pegelvariante 3/4 von a0.
- a2: `(6/20, 4/20, 1/20)`, feste Umgewichtung vom ersten zum zweiten Partial.

Frequenzen werden als die folgenden **ganzzahligen Millihertz** gespeichert,
ohne spaetere Multiplikation durch einen Variationsfaktor:

| ID | Frequenzen mHz, Partialfolge | Form | Phasenseed |
| --- | --- | --- | --- |
| np-a01 | 310000,620000,930000 | a0 | s2np-pcm-001 |
| np-a02 | 2710000,5420000,8130000 | a0 | s2np-pcm-002 |
| np-a03 | 310000,620000,930000 | a0 | s2np-pcm-001 |
| np-a04 | 310000,620000,930000 | a1 | s2np-pcm-001 |
| np-a05 | 319300,638600,957900 | a0 | s2np-pcm-001 |
| np-a06 | 310000,620000,930000 | a2 | s2np-pcm-001 |
| np-a07 | 2710000,5420000,8130000 | a0 | s2np-pcm-002 |
| np-a08 | 2710000,5420000,8130000 | a1 | s2np-pcm-002 |
| np-a09 | 2791300,5582600,8373900 | a0 | s2np-pcm-002 |
| np-a10 | 2710000,5420000,8130000 | a2 | s2np-pcm-002 |
| np-a11 | 415000,1127000,2761000 | a0 | s2np-pcm-003 |
| np-a12 | 2471000,5323000,11537000 | a0 | s2np-pcm-004 |

Generatorreihenfolge wie im bestehenden reinen `pcm_bytes`-Baustein in
`tools/_s2nc_private_receptor_materialization.py`, nur eine Partialgruppe:
Phase aus den ersten vier SHA-256-Bytes von `seed + ':' + str(i)`, unsigned
Little-Endian u, dann `(float(u)/4294967296.0)*math.tau`. Pro Sample j:
`t=float(j)/48000.0`; `f=float(millihz)/1000.0`;
`a=float(numerator)/float(denominator)`;
`angle=((math.tau*f)*t)+phase`; Summe ab `0.0` in Partialfolge 0,1,2;
abschliessend einmal `struct.pack_into('<f', ...)`. Keine Zwischen-Binary32-
Rundung, Eingangsabschwachung, quellseitige Hannung oder Normalisierung.
Historische Haupteinstiege bleiben unaufgerufen und unveraendert.

Die Exaktkopien a01/a03 und a02/a07 behalten getrennte Identitaeten und Zeiten.
Alle sonstigen Payload-/Rezeptorkollisionen werden berichtet, nicht beseitigt.
Quellenordinal n=1..12: Uhr `audio.sample`, Fenster
`[(n-1)*4800,n*4800)`, gebundener Snapshotindex `10*(n-1)` passend zur
480er-Hopgeometrie. Dies sind direkte Fensteranalysen, keine behaupteten
rollenden Abschluesse. Lokaler Generator-Sampleindex beginnt je Quelle bei 0.

## Feste Vergleichsbelegungen, keine Memoryslots

Referenzkatalog ausschliesslich a01/a02. Hinweise in fester Reihenfolge
a03,a04,a05,a06,a07,a08,a09,a10,a11,a12, niemals als Referenzen einsetzen.
Vier literale Panels, je alle zehn Hinweise in dieser Reihenfolge:

| Panel | Referenz-IDs |
| --- | --- |
| p01 | np-a01,np-a02 |
| p02 | np-a01 |
| p03 | np-a02 |
| p04 | leer |

Keine manuell eingesetzten Rezeptorvektoren, keine behaupteten B4-/Fast-/Slow-
Bestaende. Vollstaendiger Vergleich aller belegten Referenzen, ohne Ranking,
Deduplication oder vorzeitigen Abbruch. Leeres Panel: leere Treffermenge,
kein `sum`/`max` eines leeren Wertevektors. Trefferzahl 0/1/2 liefert lediglich
KEINE/EINDEUTIGE/MEHRDEUTIGE_ANWENDBARKEIT, keine zugelassene Kontexthypothese.
Keine A/B-Aufloesung oder automatische Erinnerungsauswahl.

Ausfuehrungswurzel bindet neutrale IDs, Rezepte, Sichten, Panels, Reihenfolge
und Regeln. Nur Evaluationswurzel bindet a03..a06 an a01, a07..a10 an a02,
Subtypen Exakt/Pegel/Frequenz/Spektral sowie a11/a12 als unabhaengige
Negativkontrollen ohne Ziel. Zielentfernung: p01 -> p02/p03 und
p02/p03 -> p04. Rollen und Ergebnisse beeinflussen keine Materialisierung.

## Auswertung und Widerlegung

Hauptgegenueberstellung DISTRIBUTED_24 gegen CONTIGUOUS_24, **je Bedingung**:

- Beziehungserhaltung: N = bekannte Hinweis-/Panel-Faelle mit vorhandenem
  Ziel; D = davon unter CONTIGUOUS_24 anwendbare Zielbeziehungen;
  R = auch verteilt anwendbar; L = verteilt nicht mehr anwendbar. D=R+L.
  Auch ein Verlust bei vorheriger Mehrdeutigkeit wird als Beziehungsverlust
  gezaehlt, nicht nur der Verlust einer eindeutigen Anwendbarkeit.
- Separat eindeutige richtige Anwendbarkeit: einziges anwendbares Mitglied
  hat vorgebundene Zielherkunft. Eigene N/D/R/L-Tabelle; nicht mit dem
  Beziehungsnenner vermischen. Kein Anspruch eines funktionalen Abrufs.
- Falsche Anwendbarkeit je Nichtziel-Beziehung mit Nenner aller pruefbaren
  Nichtziel-Beziehungen; zusaetzlich falsch eindeutige Panelbefunde,
  Mehrdeutigkeiten und leere Treffermengen je Hinweis-/Panel-Fall berichten.
- Gewinne, jeder Verlust und neu falsche Anwendbarkeit einzeln erhalten;
  getrennt nach Familie, Variantentyp, Konkurrenz/Zielentfernung und
  tatsaechlicher Aenderung der gerundeten Werte je Sicht. Eine quellseitige
  Variante ohne Werteveraenderung ist kein Nachweis variierter Erhaltung.
- D=0 bleibt `ERHALTUNG_NICHT_GEPRUEFT`. Exaktkontrollen ersetzen keine
  Variantenpruefung. Enthaltung bei Mehrdeutigkeit ist keine erkannte
  Unbekanntheit. Unabhaengige Kontrollen und Zielentfernung getrennt ausweisen.

Die identischen Tabellen fuer FULL_48 werden nur diagnostisch daneben
gestellt, niemals zur nachtraeglichen Sichtwahl oder zur Fallauswahl benutzt.
Alle technisch gueltigen Ergebnisse bleiben auswertbar, auch vollstaendige
Untrennbarkeit oder fehlende positive Nenner.

Eine Behauptung verlustfreier Abdeckungsverbesserung ist je Bedingung bereits
durch einen Beziehungsverlust oder eine neue falsche Anwendbarkeit widerlegt.
Ein begrenzter Vorteil verlangt zugleich weniger falsche Anwendbarkeit oder
mehr richtige Eindeutigkeit, ohne solche Verluste und mit D>0 bei tatsaechlich
veraenderten bekannten Hinweisen. Sonst gemischter Befund, kein Vorteil oder
Erhaltung nicht geprueft; kein Verrechnen von Gewinnen und Verlusten.
Kein globales Siegel, das eine schlechte Teilgruppe durch andere verdeckt.

## Spaetere Bindungen, Umfang und Stopps

Vor jeder Rezeptoranalyse separat freizugebende rezeptorfreie Versiegelung:
Dokument, beide Planwurzeln, Literalrezepte, Payloadhashes, Exaktkopien,
Zeit-/Band-/Profilbindungen sowie Interpreter, math-Herkunft, NumPy und
Generator-/Rezeptor-/NJ-Codeidentitaeten. Built-in-math nur mit bestaetigter
Modulherkunft und Python-Build, keine erfundene Moduldatei. Noch keine
Payloadhashes behaupten; sie entstehen erst bei dieser spaeteren Versiegelung.

Danach separat freizugebende Materialisierung: 12 direkte Analysen,
576 rohe Rezeptorwerte, 12 NJ-Projektionen, 576 halbierte Werte. Jeweils
Payloadhash vor Analyse, Rohpayload danach verwerfen, hoechstens ein
19.200-Byte-PCM-Fenster gleichzeitig. Rohzustands-/Projektionsdigests und
Unterlaufmarker getrennt; keine Rohwertrekonstruktion aus halbierten Werten.

Spaeterer Vergleich ausschliesslich aus diesem eingefrorenen Materialisat:
40 Hinweis-/Panel-Faelle pro Sicht/Bedingung, 3 Sichten und 3 bestehende
Bedingungen, also 360 Panelbefunde. Je Sicht 40 belegte Paarbeziehungen
(10 Hinweise mal 2+1+1+0 Referenzen). Pro Paar/Sicht ein geordnetes Termtupel,
geteilt nur zwischen den drei Bedingungen derselben Sicht: 3.840 numerische
Banddifferenzen insgesamt, 360 regelgebundene Beziehungszeilen. Wiederholte
Referenzen in anderen Panels bleiben eigene Zeilen, keine Ergebnisdeduplication.

Unabhaengige direkte Nachrechnung spaeter mit gleichem festem Umfang:
weitere 3.840 Banddifferenzen, 360 Beziehungszeilen und 360 Panelbefunde.
Damit Obergrenze 7.680 Differenzen und je 720 Zeilen/Befunde fuer beide
Implementierungen; keine Such- oder Zusatzpaare. Eine anschliessende
read-only Belegpruefung wiederholt weder Quellen noch Rezeptoren oder
Differenzen; fachliche Auswertung danach getrennt.

Numerische Termtabellen mit Originalindizes mitbinden, nicht nur ihre Digests.
Kompakte bestehende kanonische JSON-/Digest-/atomare Dateiwege genuegen;
kein Recorder oder Runtime. Ein NJ-Beleg hoechstens 16.384 Byte wie bisher,
Plan-/Identitaetsmetadaten hoechstens 65.536 Byte; gesamter spaeterer
Ergebnisbeleg einschliesslich Materialisat, Termen und Direktnachrechnung
hoechstens 2.097.152 Byte. Dies ist ein Artefaktlimit, kein Prozesspeaknachweis.

Technische Quellen-, Zeit-, Profil-, Normalform-, Digest-, Typ- oder
Ressourcenfehler: dokumentierter Stopp `NOT_EVALUABLE`, keine Ersatzquelle,
Skalierung, Grenzerhoehung, Nachbesserung des Korpus oder Retry. Phase,
Quellen-ID und erreichte Zaehler erhalten. Es gibt kein Distanz-Erfolgsgate.

Jetzt endet der Auftrag mit diesem einen Plan. Kein bestehender Scanner,
Rezeptor, Defaultadapter oder Memorykern wird geaendert. Memory-, Feld-,
Kontext- und Runtimeaufrufe bleiben ausgeschlossen, alle Gates `False`.
Historische Belege, fremde Aenderungen und Bootstrap bleiben unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses festen
Abdeckungsplans weiter; Quellenbindung und Ausfuehrung bleiben separat
freizugeben.
