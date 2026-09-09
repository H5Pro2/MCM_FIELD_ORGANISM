# S2-NZ: Belastbarkeit gespeicherter Vorhersagen unter PCM-Stoerung

Status: ein statischer Plan, keine Lauf-ID. Relevanzkriterium offen;
**noch nicht zur Vorversiegelung oder Ausfuehrung bereit**. Keine Berechnung,
Quellenproduktion, Implementierung oder Tests. Gates False, ME/MI und
Systemintegration gesperrt. Keine neue Memory-, Feld- oder Runtimeanbindung.

## Ausgangspunkt und Frage

[S2-NY](../reports/s2ny/s2ny-prefix-recommendation-20260909-01/BEFUND.md)
bleibt unveraendert als begrenzter Mischbefund geschlossen. NEXT_BEST bezeichnet
nur die bessere der beiden gespeicherten Historien. Die vier formalen Vorteile
gegen LOCAL begruenden keinen ueberzeugenden praktischen Zusatznutzen;
Beschleunigung und Wechsel zeigen eigenstaendige Verluste. Keine bevorzugte
Empfehlung, Wiederholung, nachtraegliche Fehlerschwelle oder Integration.

Neue Hypothese: Fest gespeicherte Erfahrungsparameter koennten gegenueber
einer frischen lokalen Schaetzung helfen, wenn aktuelle PCM-Fenster gestoert
sind. Sie koennen ebenso unpassend bleiben, und die NY-Empfehlung kann trotz
eines nuetzlichen festen Arms den falschen Arm empfehlen. Beides getrennt
pruefen. Keine Aussage zu Klangidentitaet, Sensorrobustheit oder Wechselerkennung.

## Unveraenderliche Arme und Ziel

Beide historischen NX-Freeze-Payloads aus dem NY-Plan read-only uebernehmen,
einschliesslich Ergebnis-, Verifikations-, Profil- und Hexbindung; nicht neu
lernen, runden, rekonstruieren oder Owner oeffnen. Derselbe unveraenderte
48-Band-Hann-/FFT-Rezeptor und NJ-Halbprofil, direkte Analyse je Fenster.

H1, H2, PERSIST, LOCAL und NY-Empfehlung exakt wie im
[NY-Vertrag](S2NY_STATISCHER_PLAN_PRAEFIXGEBUNDENE_ANWENDBARKEIT.md):
getrennte Binary64-Operationen, keine FMA oder Toleranz. LOCAL pro Stelle aus
genau drei tatsaechlichen Vektoren neu; Nullnenner beta=+0.0. Empfehlung nur
aus den unmittelbar vorherigen gebundenen H1-/H2-Fehlern derselben Folge.
k=2 ABSTAIN_INSUFFICIENT_PREFIX; Gleichstand ABSTAIN_TIE. Keine Ersatzprognose.

Ziel ist der **naechste tatsaechlich beobachtete Halbvektor**, auch im
gestoerten Arm, nicht ein verborgenes sauberes Gegenstueck. Somit wird nicht
Entrauschung oder Rekonstruktion eines sauberen Signals bewertet. Alle Arme
erhalten identische Beobachtungen derselben Folge. Saubere Kontrollfolgen
werden separat zurueckgesetzt und liefern keinerlei operative Zusatzinformation.

## Feste neue Quellen, ohne Parametersuche

Sechs Fuenferfolgen, 30 getrennte PCM_F32LE-Fenster, je 4.800 Samples bei
48.000 Hz. Lokale Synthesezeit j/48000, keine rollende Pipeline.
Zwei neue Partialgruppen in fester Reihenfolge p=0,1,2:

| Gruppe | Frequenzen Hz | Amplituden | Phasenseed |
| --- | --- | --- | --- |
| g0 | 730, 2190, 6570 | 4/20, 2/20, 1/20 | s2nz-pcm-001 |
| g1 | 1010, 3030, 9090 | 4/20, 2/20, 1/20 | s2nz-pcm-002 |

Phase wie NY: u = unsigned_LE(SHA256(seed+':'+str(p))[:4]),
phase=(float(u)/4294967296.0)*math.tau. Von +0.0 in Partialfolge
`a*math.sin(((math.tau*f)*t)+phase)` addieren, dann mit
`float(Tabellenzaehler)/1024.0` multiplizieren. Noch nicht Float32 runden.

| Folge | k0 | k1 | k2 | k3 | k4 | rho | Stoerseed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s01 | 128*g0 | 320*g0 | 368*g0 | 380*g0 | 383*g0 | 0 | keiner |
| s02 | 128*g0 | 320*g0 | 368*g0 | 380*g0 | 383*g0 | 1/1024 | s2nz-noise-001 |
| s03 | 128*g0 | 320*g0 | 464*g0 | 572*g0 | 653*g0 | 0 | keiner |
| s04 | 128*g0 | 320*g0 | 464*g0 | 572*g0 | 653*g0 | 1/1024 | s2nz-noise-002 |
| s05 | 128*g0 | 320*g0 | 464*g0 | 464*g1 | 464*g1 | 0 | keiner |
| s06 | 128*g0 | 320*g0 | 464*g0 | 464*g1 | 464*g1 | 1/1024 | s2nz-noise-003 |

Eine einzige Stoerart/-staerke, keine Sweep- oder Nachwahlmoeglichkeit:
fuer jedes j im gestoerten Fenster
`u=unsigned_LE(SHA256(ASCII(seed+':'+str(k)+':'+str(j)))[:4])`,
`v=(float(u)/4294967296.0)*2.0-1.0`, `noise=(1.0/1024.0)*v`.
Noise nach der Pegelmultiplikation addieren. Sauber: keine Noiseaddition.
Erst das fertige Sample genau einmal als little-endian Float32 runden.
Keine Zwischenrundung, datenabhaengige Stoerstaerke, Max-Normierung oder Clipping.
Die Stoerung liegt in allen fuenf Fenstern, also auch im spaeteren Ziel.
Die Seeds geben keine bekannte zeitliche Stoerfortsetzung an den Praediktor.

rho ist eine vorab gewaehlte begrenzte Belastung in PCM-Einheiten, keine
behauptete reale Sensorverteilung oder nachgewiesene Schwierigkeit. Die
Partialamplituden und additive Begrenzung lassen quellenunabhaengig Abstand
zur PCM-Vollaussteuerung; dies ist keine Garantie der Rezeptornormalform.
Technisch ungueltige Quellen/Ausgaenge spaeter abbrechen, nicht reparieren.

Reihenfolge s01..s06, jeweils k0..k4; globale Ordinalzahl q=0..29,
Quellen-ID `nz-sSS-wKK`, start=q*4800, end=start+4800, Uhr audio.sample,
nativer Index start//480 erst nach exakter Teilbarkeitspruefung. Exaktkopien
getrennt binden und spaeter getrennt analysieren, keine Deduplizierung.

Vor jeder Analyse waeren Rezepte, Stoerstaerke/-seeds, Rundungsfolge,
Payloadhashes, Zeiten, Profile und Code-/Umgebungsidentitaeten zu versiegeln.
Nur Evaluation kennt Fortsetzung H1 (s01/s02), H2 (s03/s04), Gruppenwechsel
(s05/s06) sowie Kontrollpaare. Kein Label, Seed, sauberes Gegenstueck oder
Generatorparameter in Prognose oder Empfehlung. Keine weiteren Stoerseeds
oder Quellen suchen, auch bei fehlender Stoerwirkung oder negativem Ergebnis.

## Kausale Pruefung und getrennte Bewertung

Je Folge frisches Praefix und leere Fehlerhistorie. Ziele k=2,3,4: 18 Stellen,
12 LOCAL-Stellen. Prognosen beider Rechnungen und Empfehlung vor Zielerzeugung
binden; erst nach Beobachtung Fehler erfassen. Keine kuenftigen Zielwerte
vorab materialisieren oder Prognosen als naechstes Praefix einsetzen.

Absolutes Fehlermass bleibt eindeutig und profilgebunden:
`MAE=sum(abs(pred[i]-target[i]) for i=0..47)/48` in historischer Reihenfolge.
Es misst mittleren Komponentenfehler auf der Halbprofilskala, keine Lautheit,
Wahrnehmbarkeit oder nachgewiesene Kosten einer Folgeentscheidung.
Gewinn gegen LOCAL/PERSIST ist jeweils deren MAE minus Arm-MAE, nicht Prozent.

Alle 66 Arm-MAE und bis zu 96 bestehenden NY-Gewinndifferenzen einzeln
berichten; Empfehlung hat keinen eigenen Ersatzfehler. Fuer H1/H2, LOCAL,
PERSIST und Empfehlung dieselben festen Vergleiche wie NY, kein Bestarm-Oracle.
NEXT_BEST/WRONG/TIE, fehlende Evidenz und Fehlergleichstand separat. N=18,
ausreichendes Praefix N=12, D tatsaechlich empfohlene Stellen; je Folge N=3
und LOCAL-N=2. D=0 bleibt NUTZEN_NICHT_GEPRUEFT, kein positiver Nutzenbeleg.

Sauber/gestoert, beide Fortsetzungen sowie erstes Wechselziel k3 und
Folgefenster k4 separat berichten. Die vier gestoerten Fortsetzungsstellen
s02/k3,k4 und s04/k3,k4 waeren der vorab bezeichnete primaere Relevanzbereich.
Geringere Empfehlungsabdeckung darf keine verlorenen Faelle aus dessen
Nenner entfernen. Feste Historiengewinne ersetzen keinen Empfehlungsnutzen.
Wechselverluste bleiben einzeln sichtbar, auch bei NEXT_BEST oder Vorteilen
gegen LOCAL. Kontrollpaare beschreibend gegenueberstellen, nicht als
unabhaengige Replikate oder nachtraegliche Wahl des guenstigeren Arms werten.

## Praktische Mindestverbesserung: derzeit unbegruendete Grenze

**delta_praktisch ist nicht festgelegt.** In den vorhandenen Vorhersageplaenen
fehlt eine unabhaengige fachliche Zuordnung von Halbprofil-MAE zu tolerierbarem
Vorhersagefehler, Entscheidungskosten oder einem messbaren Anwendungsnutzen.
Ohne diese Zuordnung waere etwa ein fester Bruchteil von [0,1] nur eine
Konvention, keine begruendete praktische Mindestverbesserung.

Weder NY-Gewinne noch die geplante PCM-Stoeramplitude liefern diese Grenze:
PCM- und Rezeptorskala sind verschieden. Auch Matchinggrenzen 0.1/0.01,
Float32-Aufloesung oder ein Abstand zum Rundungsrauschen begruenden keinen
Nutzen der Prognose. Eine allein aus solchen Zahlen gesetzte Schwelle
wuerde die offene fachliche Frage nur umbenennen. Keine nachtraegliche Toleranz.

Notwendig ist vor Quellenproduktion eine ausserhalb dieser Ergebnisse
begruendete absolute Verbesserung in genau dieser MAE-Einheit, etwa aus
einem konkret benannten tolerierbaren Vorhersagefehler samt Nutzungsfolge.
Der Analyst muss diese Anforderung begruenden oder bestaetigen, dass sie
derzeit nicht verfuegbar ist; eine beliebige Zahl als Freigabe genuegt nicht.

Erst danach koennte ein fester Erfolgsvergleich an allen vier primaeren
Stellen gebunden werden: Empfehlung vorhanden und Gewinn gegen LOCAL
mindestens delta_praktisch, mit unveraendertem Nenner und separaten Verlusten.
Das ist hier **kein bereits vollstaendiges Erfolgskriterium**. Solange delta
unbegruendet bleibt, sind praktische Relevanz und ein entsprechender Erfolg
nicht pruefbar. Auch ein spaeterer positiver Befund waere auf diese eine
Stoerart und Staerke begrenzt, kein allgemeiner Robustheitsnachweis.

## Endlicher Umfang und Entscheidung

Bestehende NY-Arithmetik, kausalen Belegwege und Direktrechnung einplanen,
keine neue Plattform. Derselbe Umfang: 30 Analysen/NJ, je 1.440 Roh-/Halbwerte;
je Implementierung 66 Prognosen, je 2.304 Prognoseoperationen, 864 Kopien,
12 lokale Fits/maximal 12 Divisionen, je 1.152 lokale Operationen,
3.168 Fehlerterme und 66 MAE, 18 Empfehlungen, maximal 96 Gewinndifferenzen.
Eine spaetere read-only Verifikation separat innerhalb der NY-Grenzen:
1.440 Halbierungen, je 4.608 Prognoseoperationen, 1.728 Kopien,
je 2.304 lokale Operationen, maximal 24 Divisionen, 6.336 Fehlerterme,
132 MAE, 36 Empfehlungs- und 192 Gewinnpruefungen. Keine Quellenwiederholung.
Auswertung maximal 96 WIN/TIE/LOSS, 18 Empfehlungsurteile und nach begruendeter
Bindung maximal 12 Relevanzvergleiche; keine neuen Distanz- oder Suchpaare.
Gesamtbeleg 2.097.152 Byte, Stelle 65.536 Byte, Freeze je 4.096 Byte,
Verifikation/Auswertung je 262.144 Byte; ein PCM-Fenster, drei operative
Praefixvektoren. Keine Grenzerhoehung bei spaeterer Ueberschreitung.

Empfehlung: die Relevanzluecke zuerst fachlich entscheiden, nicht durch einen
weiteren formal positiven Lauf ersetzen. Keine operative Freigabe aus diesem
Plan. S2-NY geschlossen; ME/MI unveraendert gesperrt.

RUECKMELDUNG ERFORDERLICH: eine unabhaengig begruendbare absolute
MAE-Mindestverbesserung fehlt. Bis dahin kein NZ-Erfolgstest und keine
Vorversiegelung, Quellenproduktion, Implementierung oder Ausfuehrung.
