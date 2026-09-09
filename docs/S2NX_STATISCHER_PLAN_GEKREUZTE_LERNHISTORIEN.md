# S2-NX: gekreuzte Lernhistorien gegen eine feste Daempfung

Status: ausschliesslich statischer Plan. Keine Quellenproduktion,
Berechnung, Qualifikation oder Ausfuehrung; keine Lauf-ID. S2-NW bleibt
unveraendert geschlossen, ohne Wiederholung oder Integration. Gates `False`,
ME/MI gesperrt. Kein neuer Memoryzweig und keine Feld-/Runtimekopplung.

## Frage und feste Arme

Veraendern zwei unterschiedliche Lernerfahrungen die spaetere Vorhersage
bei identischer aktueller Wahrnehmung jeweils aufgabengerecht? Zwei getrennte
NW-Lerner H1/H2, jeweils aus eigenem Nullzustand, werden eingefroren und
gegen **alle selben** Pruefstellen gestellt. Keine Auswahl zwischen ihnen.
H1/H2 sind administrative Kettennamen, keine funktionalen Eingangsrollen.

PERSIST und LINEAR bleiben unveraendert. Zusaetzlich genau eine konstante
Kontrolle FIXED_HALF mit `c=0.5` (Binary64 `0x1.0000000000000p-1`).
Diese Wahl ist durch NW motiviert und jetzt vor NX-Analyse festgelegt:
Sie prueft gerade, ob eine feste Daempfung bereits genuegt. Sie wird weder
aus neuen Quellen geschaetzt noch durch den NW-Messwert ersetzt.

Funktionale Eingaben: Profil und letzte zwei tatsaechliche Halbvektoren,
bei H1/H2 zusaetzlich der eigene gelernte alpha-Wert; PERSIST nur der letzte
Vektor. Keine Quellen-, Folgen-, Ziel- oder Zuordnungskennungen, Rezepte oder
Zukunftswerte. Gemeinsame Pruefpraefixe werden an alle Arme identisch gegeben.

```text
Hj:         d[i] = last[i] - previous[i]
            h[i] = last[i] + (alpha_j * d[i])
FIXED_HALF: d[i] = last[i] - previous[i]
            h[i] = last[i] + (0.5 * d[i])
LINEAR:     d[i] = last[i] - previous[i]; h[i] = last[i] + d[i]
PERSIST:    h[i] = bitcopy(last[i])
MAE = sum(abs(h[i] - target[i]) for i=0..47)/48
gain = MAE_baseline - MAE_Hj
```

Binary64, getrennte Subtraktion/Multiplikation/Addition, keine FMA,
Toleranz oder Umformung. Historische Python-sum-Reihenfolge beibehalten.
Endliche Prognosen ausserhalb `[0,1]` bleiben ungeclippt; nichtendliche
Rechenwerte sind technische Fehler, nicht fachliche Verluste.

## Lernen und kausaler Ablauf

Genau die NW-Vorschrift: pro Lerner initial `n=0`, `Sxx=Sxy=alpha=+0.0`.
Nach jedem beobachteten Trainingsziel, erst nach Prognose- und Fehlerbindung:

```text
for i in 0..47:
    x = last[i] - previous[i]; y = target[i] - last[i]
    Sxx = Sxx + (x*x); Sxy = Sxy + (x*y)
n = n + 1
alpha = Sxy/Sxx if Sxx > 0.0 else +0.0
```

Vier Updates je Lerner an Zielen k=2,3,4,5, danach jeweils Freeze. H1 wird
nicht mit H2-Daten aktualisiert. Der direkte Gegenrechner fuehrt fuer jede
Historie einen eigenen Nullzustand und eigene Updates, ohne Uebernahme des
primaeren alpha. Keine Koeffizientenvorgabe aus den Erzeugungsrezepten.
Nullnenner, Unterlauf und Rundung bleiben sichtbar und technisch auswertbar.

Reihenfolge: l01 vollstaendig lernen/frieren, l02 frisch lernen/frieren,
danach s01 bis s04 mit beiden unveraenderten Freeze-Bindungen pruefen.
Im Training werden der jeweils aktive Lerner, FIXED_HALF, LINEAR und
PERSIST vorhergesagt; der andere Lerner wird dort nicht mitgeprueft.
Im Test werden immer H1, H2 und alle drei festen Kontrollen ausgegeben.
Alle Arme samt Direktnachrechnung werden vor Erzeugung/Analyse des naechsten
Ziels unveraenderlich gebunden. Keine separate Zielmaterialisierung.
Nach Beobachtung nur echte Rezeptorwerte als Praefix verwenden.

Beide Freeze-Belege muessen vor dem ersten Pruefpayload gebunden sein.
Pro Prueffolge frisches Praefix, keine Testupdates oder Rueckwirkung von
Fehlern. Derselbe einmal analysierte Zielzustand dient allen Armen; kein
separater Quellenlauf je Lernzustand. Bytegleiche Quellenfenster bleiben
trotzdem eigene Analysen, keine Deduplizierung zwischen Folgen. Anschliessend
beide Zustaende schliessen und operative Referenzen verwerfen.

## Literaler neuer Quellenbestand

32 mono PCM_F32LE-Fenster, jeweils 4.800 Samples bei 48.000 Hz. Derselbe
unveraenderte Hann-/48-Band-Rezeptor und NJ-Halbprofil wie NW; direkte
Analyse, keine rollende Pipeline. Keine NW-Payloads oder NW-Messwerte.

| Gruppe | Frequenzen Hz in Partialfolge | Amplituden | Phasenseed |
| --- | --- | --- | --- |
| g0 | 610, 1830, 5490 | 4/20, 2/20, 1/20 | s2nx-pcm-001 |
| g1 | 790, 2370, 7110 | 4/20, 2/20, 1/20 | s2nx-pcm-002 |
| g2 | 970, 2910, 8730 | 4/20, 2/20, 1/20 | s2nx-pcm-003 |

Partial p=0..2: `u=unsigned_LE(SHA256(seed+':'+str(p))[:4])`,
`phase=(float(u)/4294967296.0)*math.tau`. Lokale Synthesezeit
`t=float(j)/48000.0`, j=0..4799. Ab `0.0` in Partialfolge
`a*math.sin(((math.tau*f)*t)+phase)` addieren. Anschliessend genau einmal
mit `float(Tabellenzaehler)/1024.0` multiplizieren und als `<f` runden.
Keine sampleweise Pegelrampe, Maxnormalisierung oder Eingangsabschwachung.

| Folge | k=0 | k=1 | k=2 | k=3 | k=4 | k=5 |
| --- | --- | --- | --- | --- | --- | --- |
| l01 | 128*g0 | 384*g0 | 448*g0 | 464*g0 | 468*g0 | 469*g0 |
| l02 | 128*g0 | 384*g0 | 576*g0 | 720*g0 | 828*g0 | 909*g0 |
| s01 | 192*g1 | 320*g1 | 352*g1 | 360*g1 | 362*g1 | - |
| s02 | 192*g1 | 320*g1 | 416*g1 | 488*g1 | 542*g1 | - |
| s03 | 192*g1 | 320*g1 | 352*g1 | 320*g1 | 312*g1 | - |
| s04 | 192*g1 | 320*g1 | 416*g1 | 416*g2 | 416*g2 | - |

Alle Zahlen sind Pegelzaehler mit Nenner 1024. Die Lernhistorien haben
denselben Klang-/Phasenbestand und Anfang; verschieden ist ihre Folge.
Die vorgegebenen Fortsetzungsverhaeltnisse der Pegelzuwachse sind 1/4 und
3/4. Dies ist die kontrollierte Erzeugungshypothese, kein berechneter oder
einzusetzender Rezeptorkoeffizient. Die tatsaechlichen Fits bleiben offen.
Beide Fortsetzungstests wechseln auf denselben anderen Ton-/Phasenbestand.
Die Aufgabe ist damit kontrolliert konstruiert, keine offene Generalisierung.

Globale Reihenfolge l01 k=0..5, l02 k=0..5, s01..s04 je k=0..4.
Quellen `nx-l01-wKK`, `nx-l02-wKK`, `nx-sSS-wKK`. Fuer globale nullbasierte
Ordinalzahl q=0..31: start=q*4800, end=start+4800, Uhr `audio.sample`,
nativer snapshot_index=start//480 nach ganzzahliger Nichtnegativitaets-
und exakter Teilbarkeitspruefung. Profile: window=4800, hop=480, 48 Baender
50..18000 Hz; NJ genau einmal. NW-Profilidentitaeten unveraendert binden.

Spaeter vor erster Rezeptoranalyse Rezepte, Payloadhashes, Zeiten,
Generator-/Interpreter-/Code-/Profilidentitaeten und alle Bedingungen
versiegeln. Ausfuehrungswurzel bindet Folgen und Lern-/Freeze-Grenzen;
Bewertungswurzel allein bindet passende Historie, Kategorien und Sollurteile.
Alle Bytegleichheiten dokumentieren, nicht entfernen. Keine Auswahl nach
Distanz, Fit, Gewinn oder Normalformbefund; bei Fehler kein Ersatzreiz.

## Auswertung und klare Gegenprognosen

Zwoelf Teststellen: s01..s04 jeweils Ziele k=2,3,4. Pro Stelle fuenf MAE,
je H1/H2 drei separate Gewinne gegen PERSIST/LINEAR/FIXED_HALF sowie ein
gerichteter Kreuzgewinn `MAE_H2-MAE_H1`. Keine nachtraegliche Armwahl.
Training separat: acht Stellen, jeweils vier MAE und drei Gewinne des
aktiven Lerners. Keine Trainingsverbesserung als Transfererfolg ausgeben.

Die Evaluationswurzel bindet H1 fuer s01 und H2 fuer s02, ohne diese
Zuordnung an den Praediktor oder den technischen Verifikator weiterzugeben.

| Kriterien | Vorab festgelegte Bedingung |
| --- | --- |
| K01-K03 | s01 k=2,3,4: MAE_H1 < MAE_H2 |
| K04-K06 | s02 k=2,3,4: MAE_H2 < MAE_H1 |
| F01-F03 | s01 k=2,3,4: MAE_H1 < MAE_FIXED_HALF |
| F04-F06 | s02 k=2,3,4: MAE_H2 < MAE_FIXED_HALF |
| B01-B06 | s01 k=2,3,4, jeweils PERSIST dann LINEAR: MAE_H1 < MAE_Baseline |
| B07-B12 | s02 k=2,3,4, jeweils PERSIST dann LINEAR: MAE_H2 < MAE_Baseline |
| W01-W04 | s03 dann s04, jeweils H1 dann H2, k=3: MAE_Hj > MAE_PERSIST |

Kreuzhistorienprognose nur bei allen sechs K bestaetigt. Zusatznutzen gegen
die feste Daempfung nur bei allen sechs F bestaetigt, nicht aus K ableiten.
Der volle angestrebte Befund verlangt beide K/F-Bloecke, zwei belegte
nichtinitiale Freeze-Zustaende mit n=4 und Sxx>0 sowie tatsaechlich
unterschiedliche alpha-Werte. Diese sind **fachliche Kriterien**, keine
Startgates. Gleichstaende bestehen strikte Bedingungen nicht. Ein einzelnes
Scheitern widerlegt den jeweiligen vollstaendigen Block; alle Einzelwerte
bleiben erhalten. B und W separat berichten, nicht als Ersatz fuer K/F.

Pro Testfolge/Historie/Baseline N=3, pro Zielphase N=1; je Lernfolge N=4.
Anstieg k=2, erstes Zweigziel k=3 und Folgefenster k=4 trennen. Bei s03
wird Umkehr, bei s04 unangekuendigter Gruppenwechsel geprueft; k=4 zeigt
Folgefehler ohne weitere Erfolgsforderung. Alle Wechselverluste auch gegen
FIXED_HALF und LINEAR offenlegen. Gewinne duerfen Verluste nicht verrechnen.

Gleiche Anfangspraefixe von s01/s02 haben verschiedene spaetere Fortsetzungen.
Der jeweilige Historieneffekt ist ein kontrollierter Eingriff bei identischen
aktuellen Eingaben, keine Faehigkeit, aus diesen Eingaben die passende
Historie automatisch auszuwaehlen. Auch Wiederholungen in s03/s04 sind keine
unabhaengigen Replikate. Erzeugungsgruppen bedeuten keine Quellenidentitaet.

## Anschluss und endliche Budgets

NW-Arithmetik, direkte Nachrechnung, AudioReader, kausale Prognosebindung,
atomare IO und Trennung von Verifikation/Auswertung wiederverwenden.
Spaeter nur private NX-Quellen-/Folgenbindung und Komposition zweier
NW-Lernpaare mit dem festen Kontrollarm. Der historische NW-Renderer bindet
Nenner 64; eine eigene explizite 1024-Bindung nutzt dieselben reinen
Partial-/Phasenfunktionen, ohne diesen Validator zu lockern. NW-Haupteinstieg
und feste 26-Fenster-Bindungen nicht umetikettieren oder monkeypatchen.

| Arbeit | Obergrenze je Implementierung |
| --- | --- |
| Prognosestellen | 8 Training mit 4 Armen, 12 Test mit 5 Armen |
| Prognosevektoren | 92; einschliesslich Direktnachrechnung 184 |
| Prognosesubtraktionen / Additionen | je 3.456 |
| Prognosemultiplikationen / Persistenzkopien | 2.496 / 960 |
| Updates | 8; je 4 aus eigenem Nullzustand |
| Updatedifferenzen / Produkte / Akkumulatoradditionen | je 768 |
| Updatezaehler / Divisionen | 8 / hoechstens 8 |
| Fehlerterme / MAE-Summen | 4.416 / 92 |
| Gewinndifferenzen | 108: 24 Training, 72 Test gegen feste Arme, 12 Kreuzgewinne |

Feste Baselines je Stelle nur einmal pro Implementierung, nicht nochmals
pro Lernzustand. Lernarme und direkte Gegenrechner verwenden jeweils eigene
Arithmetik; keine Uebernahme primaerer Fits. Kein Uebergang zwischen Folgen.

Spaeter insgesamt 32 direkte Analysen/NJ-Projektionen und je 1.536 Roh-/
Halbwerte; 614.400 erzeugte PCM-Byte, maximal ein Payload mit 19.200 Byte.
Eine zusaetzliche read-only Verifikation separat: 1.536 Halbierungen,
6.912 Prognosesubtraktionen/-additionen je Art, 4.992 Multiplikationen,
1.920 Kopien; 1.536 Updatedifferenzen/-produkte/-additionen je Art,
16 Zaehlerupdates/hoechstens 16 Divisionen; 8.832 Fehlerterme,
184 MAE-Summen und 216 Gewinnpruefungen. Keine Rezeptorwiederholung.
Danach 108 WIN/TIE/LOSS-Zuordnungen und 28 strikte Kriterien, getrennt.

Zustand maximal 4.096 Byte je Lerner, insgesamt zwei primaere und zwei
direkte Zustaende; maximal drei operative 48er-Praefixvektoren gemeinsam.
Metadaten/Prognosebindung 65.536 Byte, atomarer Gesamtbeleg 2.097.152 Byte,
Pruefung/Auswertung je 262.144 Byte. Vollstaendige Huelle vor einem spaeteren
Hauptlauf neutral absichern, keine Grenzerhoehung bei Ueberschreitung.

Spaeter besonders abzusichern: getrennte Nullzustaende, Updates nach Ziel,
beide Freeze-Bindungen vor Testproduktion, identische Testeingaben fuer alle
Arme, unveraenderte Kontrollkonstante, keine Rollen-/Zukunftsfelder,
vollstaendige Verlustberichte und auswertbare negative Ergebnisse.
Ein Offline-Digest allein beweist weiterhin keine historische Aufrufordnung.

Jetzt ausschliesslich dieser Plan. Noch kein Nachweis eines NX-Lerneffekts,
keine Quellenproduktion oder neue Qualifikation. Ein positives Ergebnis
waere aufgabengerechter Einfluss unterschiedlicher Erfahrungen auf eine
feste Vorhersagefamilie, keine automatische Erinnerungswahl, Objektbindung
oder Loesung von ME/MI. Kein Ersatzkorpus, Koeffizientensuche oder Retry.
