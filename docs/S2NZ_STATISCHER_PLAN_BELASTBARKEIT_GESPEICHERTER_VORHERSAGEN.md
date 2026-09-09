# S2-NZ: diagnostischer Stoerungsvergleich gespeicherter Vorhersagen

Status: ein statischer diagnostischer Plan, keine Lauf-ID. Kein praktischer
Nutzen- oder Robustheitstest. Die fehlende Nutzungsanforderung bleibt offen,
ist aber keine Voraussetzung fuer diesen begrenzten Diagnosevergleich.
Jetzt nur Dokumentation; Vorversiegelung und alle operativen Schritte bleiben
separat freizugeben. Keine Berechnung, Quellenproduktion, Implementierung oder
Tests. Gates False, ME/MI und Systemintegration gesperrt.

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
Absolute Fehler sowie Gewinne und Verluste gegen LOCAL sauber und gestoert
getrennt ausweisen. Die festen Historienbefunde bleiben auch bei Enthaltung
sichtbar; sie duerfen nicht als tatsaechlich ausgegebene Empfehlung gelten.
NEXT_BEST/WRONG/TIE, fehlende Evidenz und Fehlergleichstand separat. N=18,
ausreichendes Praefix N=12, D tatsaechlich empfohlene Stellen; je Folge N=3
und LOCAL-N=2. D=0 bleibt NUTZEN_NICHT_GEPRUEFT, kein positiver Nutzenbeleg.

Sauber/gestoert, beide Fortsetzungen sowie erstes Wechselziel k3 und
Folgefenster k4 separat berichten. Die vier gestoerten Fortsetzungsstellen
s02/k3,k4 und s04/k3,k4 bilden den festen diagnostischen Schwerpunkt mit N=4.
Alle vier Stellen erhalten eine eigene Ergebniszeile, auch bei Enthaltung.
Geringere Empfehlungsabdeckung darf den Vierer-Nenner nicht verkleinern;
D ausgegebener Empfehlungen wird daneben separat berichtet. Kein Erfolg
durch Auswahl nur der empfohlenen Stellen. Feste Historiengewinne ersetzen
keinen Empfehlungsnutzen.
Wechselverluste bleiben einzeln sichtbar, auch bei NEXT_BEST oder Vorteilen
gegen LOCAL. Kontrollpaare beschreibend gegenueberstellen, nicht als
unabhaengige Replikate oder nachtraegliche Wahl des guenstigeren Arms werten.

## Diagnostische Aussage statt praktischer Mindestverbesserung

Der bisher vorgesehene Anspruch einer praktisch relevanten Mindestverbesserung
entfaellt. **Keine Ersatzschwelle, kein delta_praktisch und keine Toleranz.**
Es fehlt weiterhin eine unabhaengige Zuordnung von Halbprofil-MAE zu
tolerierbarem Fehler, Entscheidungskosten oder konkretem Anwendungsnutzen.
Diese offene Nutzungsanforderung wird nicht aus NZ-Ergebnissen abgeleitet.

Weder NY-Gewinne noch die geplante PCM-Stoeramplitude liefern diese Grenze:
PCM- und Rezeptorskala sind verschieden. Auch Matchinggrenzen 0.1/0.01,
Float32-Aufloesung oder ein Abstand zum Rundungsrauschen begruenden keinen
Nutzen der Prognose. Eine allein aus solchen Zahlen gesetzte Schwelle
wuerde die offene fachliche Frage nur umbenennen.

NZ beschreibt ausschliesslich Unterschiede auf diesem festen Bestand:
absolute MAE, vorzeichenbehaftete Gewinndifferenzen, Verluste und Abdeckung.
Strikte WIN/TIE/LOSS bleiben numerische Beschreibungen, keine praktische
Relevanzentscheidung. Auch durchgehend positive Differenzen begruenden nur
einen Vorteil auf dieser einen Stoerart/-staerke und diesen Quellen.

Kein Gesamtstatus "praktischer Nutzen bestaetigt" oder "robust" und kein
Gesamtmittel, das Verluste oder Enthaltungen mit Gewinnen verrechnet.
Ein spaeterer praktischer Nutzenbeleg benoetigt erst eine reale Systemaufgabe
mit unabhaengig begruendeter Fehleranforderung; NZ ersetzt diese nicht.

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
Auswertung maximal 96 WIN/TIE/LOSS und 18 Empfehlungsurteile. Die bisher fuer
maximal 12 Relevanzvergleiche reservierte Obergrenze wird nicht erhoeht;
ohne Relevanzschwelle bleiben diese Vergleiche ungenutzt. Keine neuen
Distanz- oder Suchpaare und keine zusaetzliche Arbeit aus der Eingrenzung.
Gesamtbeleg 2.097.152 Byte, Stelle 65.536 Byte, Freeze je 4.096 Byte,
Verifikation/Auswertung je 262.144 Byte; ein PCM-Fenster, drei operative
Praefixvektoren. Keine Grenzerhoehung bei spaeterer Ueberschreitung.

Vorab festgelegte Entscheidungsfolge: Nach separater operativer Freigabe und
technisch gueltigem Abschluss zunaechst nur die vollstaendigen diagnostischen
Einzelbefunde vorlegen. Danach entscheidet der Analyst anhand absoluter
Differenzen, Verlusten und Abdeckung, ob eine spaetere anwendungsbezogene
Pruefung ueberhaupt begruendet erscheint. Dies ist kein automatisches Gate
und keine nachtraegliche Umdeutung der Diagnose in einen praktischen Erfolg.

Ein fehlender ueberzeugender Vorteil wird als Grenze akzeptiert, nicht durch
weitere Stoerparameter, Seeds, Quellen oder Wiederholungen passend gemacht.
Weder positive noch gemischte Befunde autorisieren Integration oder eine
Stoerparametersuche. Praktische Anforderungen stammen spaeter aus einer
tatsaechlichen Systemaufgabe, nicht aus gewuenschten Versuchsergebnissen.
Keine operative Freigabe aus dieser Dokumentaenderung. S2-NY geschlossen;
Gates False, ME/MI und Systemintegration unveraendert gesperrt.
