# S2-NV: statischer Plan einer prospektiven auditiven Verlaufsvorhersage

Nur Plan, keine Laufnummer oder Ausfuehrungsfreigabe. S2-NU ist unveraendert
geschlossen: keine weiteren Permutationen, kein T als Memory-, Identitaets-,
Praegungs- oder Zulassungsmass. ME/MI bleiben gesperrt.

## Frage und genau eine Vorschrift

Hilft ein verfuegbares Praefix bei der Vorhersage eines noch nicht erzeugten
naechsten Rezeptorhalbzustands besser als der letzte Zustand allein?
Unveraenderter LogSpectralReceptor und NJ-Halbprofil, 48 Originalbaender,
direkte Fensteranalyse bei fester 100-ms-Kadenz. Kein Training und keine Suche.

Zwei fest gebundene Arme, fuer Ursprung k=1,2,3 und Ziel k+1:

```text
LINEAR_TWO_STATE:
    d[i] = z[k,i] - z[k-1,i]
    prediction[i] = z[k,i] + d[i]
PERSIST_LAST:
    prediction[i] = z[k,i]
error[i] = abs(prediction[i] - z[k+1,i])
MAE = sum(error[i] for i=0..47)/48
gain = MAE_PERSIST_LAST - MAE_LINEAR_TWO_STATE
```

Binary64, Subtraktion vor Addition; keine Umformung zu `2*z[k]-z[k-1]`.
Python-Builtin `sum` in aufsteigender Originalindexfolge. Keine Gewichte,
Toleranz, Glaettung, Koeffizientenwahl oder weitere Prognose. Persistenz
kopiert die letzten gespeicherten Floatwerte bitgetreu. Positive gain-Werte
bedeuten Verbesserung, negative Verschlechterung; Null ist Gleichstand.

Lineare Prognosen duerfen endlich in `[-1,2]` liegen, auch ausserhalb der
Rezeptornormalform `[0,1]`. Kein Clipping, Fallback oder Ausschluss solcher
Faelle. Sie sind Vorhersagen, keine veroeffentlichten Wahrnehmungszustaende;
ihr voller Fehler zaehlt. Nichtendliche/ungueltige Formen sind technische
Fehler. Alle 48 Prognose- und Fehlerwerte beider Arme bleiben erhalten.

## Vier neue, vollstaendig feste Fuenferfolgen

20 mono PCM_F32LE-Fenster mit je 4.800 Samples bei 48.000 Hz. Neue
Quellen, keine NU-/NT-Wiederverwendung. Feste Gruppen in Partialreihenfolge:

| Gruppe | Frequenzen Hz | Amplituden | Phasenseed |
| --- | --- | --- | --- |
| g0 | 470, 1410, 4230 | 4/20, 2/20, 1/20 | s2nv-pcm-001 |
| g1 | 830, 2490, 7470 | 4/20, 2/20, 1/20 | s2nv-pcm-002 |

Frequenzen/Amplituden als Floatdivision ganzzahliger Zaehler/Nenner.
Partialphase ab Position p=0: `u=unsigned_LE(SHA256(seed+':'+str(p))[:4])`,
`phase=(float(u)/4294967296.0)*math.tau`. Fuer j=0..4799 lokale Synthesezeit
`t=float(j)/48000.0`; Gruppe ab `0.0` in Partialfolge akkumulieren:
`a*math.sin(((math.tau*f)*t)+phase)`. Sample danach `gain*g(t)`, erst dann
genau einmal `<f` runden. Gain ist Floatdivision des Tabellenzaehlers durch
`10.0`. Keine weitere Rundung, Quellenabschwaechung oder Normalisierung.

| Strom | k=0 | k=1 | k=2 | k=3 | k=4 |
| --- | --- | --- | --- | --- | --- |
| s01 | 4/10*g0 | 5/10*g0 | 6/10*g0 | 7/10*g0 | 8/10*g0 |
| s02 | 4/10*g0 | 5/10*g0 | 6/10*g0 | 5/10*g0 | 4/10*g0 |
| s03 | 4/10*g0 | 5/10*g0 | 6/10*g0 | 6/10*g0 | 6/10*g0 |
| s04 | 4/10*g0 | 5/10*g0 | 6/10*g0 | 6/10*g1 | 6/10*g1 |

Die Pegel sind je Fenster konstant; dies ist keine Behauptung sampleweise
stetiger Pegelveraenderung. Ganze Periodenzahlen erlauben lokal wiederholte
Oszillatorzeit. Alle Quellenidentitaeten bleiben getrennt, auch bei
beabsichtigten oder weiteren zufaelligen Bytegleichheiten. Keine Deduplikation.

Nur die Evaluationswurzel bezeichnet s01 als Fortsetzung, s02 als Umkehr,
s03 als Stillstand nach Anstieg und s04 als unerwarteten Gruppenwechsel.
Das sind Erzeugungsbedingungen, keine vom System erkannten Klangidentitaeten.
Vier Stroeme mit gleichem Anfang sind keine vier unabhaengigen Familienreplikate.

Native Quellen-ID `nv-sSS-wKK`, s=1..4, k=0..4, Uhr `audio.sample`:
`start=(s-1)*24000+k*4800`, `end=start+4800`, `snapshot_index=start//480`
nach Ganzzahligkeits-/Teilbarkeitspruefung. Reihenfolge s01..s04, je k=0..4.
Hann-/FFT-/48-Band-Profil 50..18.000 Hz, window=4800, hop=480 und NJ
unveraendert; keine rollende Pipeline. Genau eine direkte Analyse und NJ
je Fenster. Roh-/Halbwerte, Zeiten, Profile, Hex-/Byte- und Rundungsmarker binden.

## Prospektive Grenze und Quellenversiegelung

Vor jeder Rezeptoranalyse alle 20 Rezepte/Payloadhashes, Reihenfolge, native
Zeiten, Profile, Generator-/Interpreter-/Codeidentitaeten und zwoelf feste
Pruefstellen (jeder Strom: k=1->2, 2->3, 3->4) versiegeln. Getrennte
Ausfuehrungs- und Evaluationswurzeln; keine Auswahl nach Rezeptordistanzen.
Hoechstens ein PCM-Fenster, keine Rohpayloadablage. Hashpruefung vor Analyse.

Spaetere Ausfuehrung strikt praefixweise: z0, z1 verarbeiten; beide
Vorhersagen fuer z2 unveraenderlich binden; erst danach Fenster 2 regenerieren
und analysieren. Entsprechend nach z2 vor z3 und nach z3 vor z4 vorgehen.
Kein Vorabmaterialisat der Zielvektoren, keine Nutzung zukuenftiger Fenster
aus einem anderen Strom und keine Rekursion auf vorhergesagte Werte.

Der LINEAR-Vorhersager erhaelt funktional nur Halbprofilbindung und die
letzten zwei zeitlich geordneten 48er-Vektoren; PERSIST nur Profilbindung
und den letzten. Keine Quelle, Stream-ID, absolute Zeit, Zielordinalzahl,
Rezepte, Seeds, Gainparameter, Kategorien, Zukunftswerte oder Evaluationswurzel.
Zeit-/Herkunftspruefung findet ausserhalb dieser geschlossenen Eingaben statt.
Die gemeinsame Historie erlaubt keine Beobachtung, welcher Zweig folgen wird.

Vorhersagebeleg jeweils vor dem naechsten Rezeptoraufruf erzeugen: Praefix-
und Prognosedigest, verfuegbare Fensterzahl, abgeschlossene Analysezahl.
Die spaetere Zielbindung darf die Prognose nicht aendern. Bestehender atomarer
Gesamtbeleg genuegt, kein neues Laufjournal. Neutral spaeter insbesondere
Zukunftszugriff und nachtraegliche Prognoseaenderung fail-closed pruefen.
Ein finaler Digest allein beweist diese zeitliche Ausfuehrungsgrenze nicht;
sie benoetigt auch den kontrollierten Aufrufpfad. Offline pruefbar bleiben
Berechnung und Belegkette, nicht unabhaengig die historische CPU-Reihenfolge.

## Vorhersagen, Verluste und Falsifikation

Primaere begrenzte Gegenprognose: Auf s01 ist LINEAR an allen drei festen
Pruefstellen strikt fehleraermer als Persistenz. Jeder Gleichstand oder
Verlust widerlegt diese vollstaendige Primaerprognose; Einzelgewinne werden
dennoch unverrechnet ausgewiesen. Kein Erfolgskriterium ist ein Startgate.

Getrennte Belastungsprognose: Am ersten nicht angekuendigten Wechselziel
k=3 wird LINEAR in s02, s03 und s04 schlechter als Persistenz. Alle drei
Beziehungen gesondert berichten, auch wenn diese Prognose scheitert. Gerade
ein gleiches verfuegbares Praefix rechtfertigt keine sichere Fortsetzung.
Fuer k=4 keine zusaetzliche Erfolgsforderung: Erholung, Gleichstand oder
weiterer Verlust werden als regulaere Ergebnisse erfasst.

Je Strom und Zielstelle beide MAE, signed gain sowie WIN/TIE/LOSS angeben;
je Verlaufstyp N=3 und absolute Anzahl Gewinne/Gleichstaende/Verluste.
Gemeinsames Anstiegsziel k=2, erstes Zweigziel k=3 und Folgefenster k=4
getrennt ausweisen. Jeder Verlust bleibt sichtbar. Kein Gesamtmittel,
Summengewinn oder 12-Faelle-Pool darf Wechselverluste kompensieren oder
die wiederholte gemeinsame Anfangsbedingung als unabhaengigen Gewinn zaehlen.

## Endliche Arbeit und Aussagegrenze

- 20 Analysen, 20 NJ-Projektionen, je 960 Roh-/Halbwerte; kein Vorlauf.
- 12 Prognosestellen x zwei Arme = 24 Prognosevektoren je Implementierung.
- LINEAR je Implementierung 576 Subtraktionen und 576 Additionen; PERSIST
  nur 576 Wertkopien. Unabhaengige Direktnachrechnung ohne Prognosehelfer.
- Fehler je Implementierung 1.152 Banddifferenzen/Absolutbetraege und
  24 MAE-Summen; beide zusammen 2.304 Fehlerdifferenzen und 48 Summen.
- Je Implementierung 12 gain-Subtraktionen. Alle drei Arbeitsarten getrennt
  zaehlen; keine versteckten Prognosedifferenzen im Fehlerbudget.
- Eine read-only Verifikation separat maximal 960 Vorwaertshalbierungen,
  1.152 Prognosesubtraktionen/-additionen je Operationsart, 2.304 Fehlerterme,
  48 Summen und 24 gain-Pruefungen; danach 12 WIN/TIE/LOSS-Befunde und sechs
  vorgebundene strikte Prognosebedingungen. Keine weiteren Quellpaare.
- Metadaten 65.536 Byte, Gesamtbeleg 2.097.152 Byte, Verifikations- und
  Auswertungsbeleg je 262.144 Byte; ein PCM-Payload 19.200 Byte. Die
  vollstaendige Belegform einschliesslich Praefixbindung spaeter neutral pruefen.

Technische Fehler stoppen phasengenau; kein Retry, Ersatzseed, Clipping,
Parameterwechsel oder Auswahl besserer Verlaeufe. Negative Funktionsbefunde
sind auswertbar. Auch primaeres Bestehen belegt nur Nutzen dieser festen
Zwei-Zustands-Extrapolation fuer diese synthetische Fortsetzung, kein Lernen,
Quellenidentitaet, Bedeutung oder universell vorhersagbare Dynamik. Eine
spaetere Memoryanbindung benoetigt eigene beobachtbare Evidenz und Begruendung.
Jetzt keine Implementierung, Quellenproduktion, Tests oder Ausfuehrung;
alle Gates `False`, ME/MI gesperrt, NU unveraendert geschlossen.
