# S2-NW: gelernte Verlaufsvorhersage mit eingefrorener Pruefphase

Status: ausschliesslich statischer Plan, keine Laufnummer oder Ausfuehrungsfreigabe.
S2-NV bleibt unveraendert geschlossen. Keine bevorzugte LINEAR-Systemprognose.
ME/MI bleiben gesperrt; alle Gates `False`. Kein eigener Memoryzweig,
Feld-/Runtimeanschluss, Quellenproduktion oder neue Versuchsplattform.

## Frage und ein einziger Lernansatz

Nuetzt eine aus beobachteten Uebergaengen erworbene Fortsetzungsstaerke noch
auf neuen Fenstern, wenn ihr Lernzustand nicht mehr veraendert werden darf?
Genau ein Ansatz: ein globaler skalarer Koeffizient fuer die letzte
48-Band-Aenderung, durch kumulierte quadratische Anpassung ohne Achsenabschnitt.
Keine Bandgewichte, Lernratenwahl, Kandidatenmodelle oder Algorithmussuche.
Unveraenderter direkter LogSpectralReceptor und S2-NJ-Halbprofil wie NV.

Drei immer getrennt ausgegebene Arme, alle mit demselben verfuegbaren Praefix:

```text
LEARNED_DELTA: d[i] = z[k,i] - z[k-1,i]
               h[i] = z[k,i] + (alpha * d[i])
LINEAR:        d[i] = z[k,i] - z[k-1,i]
               h[i] = z[k,i] + d[i]
PERSIST:       h[i] = z[k,i]   # bitgetreue Kopie
MAE = sum(abs(h[i] - z[k+1,i]) for i=0..47)/48
gain_vs_baseline = MAE_baseline - MAE_LEARNED_DELTA
```

Binary64; Subtraktion, Multiplikation, Addition getrennt, keine FMA oder
algebraische Umformung. Historische Python-`sum`-Folge und MAE unveraendert.
Keine Toleranz, kein Clipping, Fallback oder Auswahl des besseren Arms.
Endliche Prognosen ausserhalb `[0,1]` zaehlen ungekuerzt; sie sind keine
Wahrnehmungszustaende. Nichtendliche Rechenwerte sind technische Fehler.

## Lernzustand, Aktualisierung und Freeze

Ein unveraenderlicher, versionierter Zustand traegt Profilbindung, `n`,
`Sxx`, `Sxy`, `alpha` und Phase `TRAIN/FROZEN/CLOSED`, mit Digest und
belegter Vorgaengerbindung. Initial: `n=0`, `Sxx=Sxy=alpha=+0.0`.
Kein gelernter Anfangswert. Alpha ist kein Quellparameter.

Vier Trainingsstellen: nach k=1,2,3,4 wird k+1 vorhergesagt. Erst nachdem
alle drei Prognosen und ihre Direktnachrechnung unveraenderlich gebunden,
das Ziel erzeugt/analysiert und die Fehler festgehalten sind, folgt ein Update:

```text
for i in 0..47:
    x = z[k,i] - z[k-1,i]
    y = z[k+1,i] - z[k,i]
    Sxx = Sxx + (x * x)
    Sxy = Sxy + (x * y)
n = n + 1
alpha = Sxy / Sxx if Sxx > 0.0 else +0.0
```

Die Akkumulation erfolgt in Trainingsstellenfolge und je Stelle in
aufsteigender Bandfolge. Kein Vergessen, Regularisieren, Begrenzen von alpha
oder Nachtrainieren nach Prueffehlern. Die Definition bei `Sxx=0` ist eine
feste Behandlung fehlender beobachteter Aenderung, kein Baseline-Umschalter.
Subnormal-/Unterlauf- und Nullnennerfaelle bleiben sichtbar; negative Sxx,
nichtendliche Werte oder ungueltige Ketten werden typisiert abgewiesen.
Bei Nullnenner liegt kein informativer Fit vor, aber kein fachlich positiver
Startzustand wird erzwungen. Ein solcher gueltiger Versuch bleibt auswertbar.

Nach dem vierten Update wird genau dieser Zustand eingefroren und vor
Erzeugung irgendeines Pruefpayloads gebunden. Numerisch uebertragen wird nur
alpha; n/Summen/Kette sind administrative Lernbelege, keine weiteren
Prognoseeingaben. Jede Prueffolge startet mit leerem Praefix und derselben
unveraenderlichen Freeze-Bindung. Kein Uebergang zwischen Folgen, keine
Trainingsvektoren oder Pruefziele als versteckte Historie. Alle zwoelf
Pruefstellen erhalten denselben alpha-Wert. Danach Zustand schliessen und
operative Referenzen verwerfen; kein Persistieren als A-/B-Memoryinhalt.

Die unabhaengige Direktnachrechnung fuehrt einen eigenen Nullzustand und
dieselben vier Updates ohne produktive Prognose-/Updatehelfer. Sie darf
alpha nicht aus dem primaeren Ergebnis uebernehmen. Beide Freeze-Ergebnisse
und alle Prognosen/Fehler werden exakt, ohne Toleranz verglichen.

## Neue, vor Analyse festgelegte Quellen

26 getrennte mono PCM_F32LE-Fenster, je 4.800 Samples bei 48.000 Hz.
Keine NV-Quellen oder nachtraegliche Auswahl anhand der Rezeptorwerte.

| Gruppe | Frequenzen Hz, in dieser Reihenfolge | Amplituden | Phasenseed |
| --- | --- | --- | --- |
| g0 | 530, 1590, 4770 | 4/20, 2/20, 1/20 | s2nw-pcm-001 |
| g1 | 710, 2130, 6390 | 4/20, 2/20, 1/20 | s2nw-pcm-002 |
| g2 | 890, 2670, 8010 | 4/20, 2/20, 1/20 | s2nw-pcm-003 |

Reine Synthesereihenfolge wie NV: Partialindex p=0..2;
`u=unsigned_LE(SHA256(seed+':'+str(p))[:4])`,
`phase=(float(u)/4294967296.0)*math.tau`. Lokale Zeit
`t=float(j)/48000.0`, j=0..4799; ab `0.0` in Partialfolge
`a*math.sin(((math.tau*f)*t)+phase)` akkumulieren. Erst danach mit
`float(Tabellenzaehler)/64.0` multiplizieren und genau einmal als `<f`
runden. Keine Fenster-Maxnormalisierung oder weitere Abschwaechung.
Pegel sind je Fenster konstant, nicht sampleweise kontinuierlich.

| Folge | k=0 | k=1 | k=2 | k=3 | k=4 | k=5 |
| --- | --- | --- | --- | --- | --- | --- |
| l01 | 16*g0 | 32*g0 | 40*g0 | 44*g0 | 46*g0 | 47*g0 |
| s01 | 20*g1 | 28*g1 | 32*g1 | 34*g1 | 35*g1 | - |
| s02 | 20*g1 | 28*g1 | 32*g1 | 28*g1 | 26*g1 | - |
| s03 | 20*g1 | 28*g1 | 32*g1 | 32*g1 | 32*g1 | - |
| s04 | 20*g1 | 28*g1 | 32*g1 | 32*g2 | 32*g2 | - |

Alle Tabellenfaktoren sind Zaehler mit gemeinsamem Nenner 64, keine
unskalierten PCM-Amplituden. Die Erzeugungsvorschrift ist kontrolliert auf
eine abnehmende Fortsetzungsstaerke angelegt; diese ist eine vorgebundene
Gegenprognose, kein behaupteter Rezeptorbefund und kein vorzubesetzender Fit.
Gruppenwechsel bedeutet ausschliesslich unterschiedliche Syntheseherkunft.
Der Transfer wechselt Ton-/Phasenbestand, prueft aber nur eine kontrollierte
Dynamikklasse, keine breit unabhaengige Generalisierung.

Reihenfolge l01 k=0..5, danach s01..s04 je k=0..4. Quellen-ID
`nw-l01-wKK` beziehungsweise `nw-sSS-wKK`. Fuer die nullbasierte globale
Ordinalzahl q=0..25: `start=q*4800`, `end=start+4800`, Uhr `audio.sample`,
`snapshot_index=start//480` erst nach ganzzahliger Nichtnegativitaets- und
Teilbarkeitspruefung. Unveraenderte NV-Profilparameter: Hann, window=4800,
hop=480, 48 Baender von 50 bis 18.000 Hz, NJ genau einmal nach direkter Analyse.

Alle Rezepte, Fenster, Payloadhashes, Profil-/Generator-/Interpreter- und
Codebindungen werden spaeter vor der ersten Rezeptoranalyse versiegelt.
Beabsichtigte gemeinsame Praefixe und weitere Bytegleichheiten dokumentieren,
nicht deduplizieren. Keine Rohpayloadablage, hoechstens ein PCM-Fenster.
Die Ausfuehrungswurzel bindet nur Quellen, Reihenfolge, Trainings-/Freeze-
Grenze und Pruefstellen. Erzeugungskategorien, Erfolgsbedingungen und
Train-/Transferinterpretation liegen in der getrennten Evaluationswurzel.

## Funktionale Zukunftssperre

LEARNED erhaelt nur Profil, alpha und zwei verfuegbare Halbvektoren;
LINEAR Profil und zwei, PERSIST Profil und einen Halbvektor. Keine Zeit,
Quelle, Kategorie, Rezept, Gain, Pruefstellen-ID oder zukuenftigen Werte.
Der Updatekern erhaelt nur den bisherigen Lernzustand und das bereits
beobachtete Dreierfenster. Trainingsfreigabe kontrolliert der aeussere Ablauf.

Wie NV: erstes Zweierpraefix analysieren; alle Prognosen samt Direktarm
binden; erst dann das naechste Zielpayload erzeugen und analysieren. Das
gilt auch bei bekannten Bytegleichheiten. Nur echte Ziele setzen das
Praefix fort. Trainingsupdates erst danach; in FROZEN sind Updates unzulaessig.
Prognosebelege binden den tatsaechlich verwendeten Vorzustand; Freeze und
Pruefzustand bleiben bytegleich. Kein reaktiver Armwechsel nach einem Fehler.
Ein Offline-Digest allein beweist weiterhin keine historische CPU-Reihenfolge.

## Auswertung und Falsifikation

Vier Trainingsprognosen mit ihren jeweils damaligen alpha-Werten separat
beschreiben, nicht als eingefrorenen Transfererfolg zaehlen. Zwoelf
Pruefprognosen: je s01..s04 die Ziele k=2,3,4. Je Stelle drei MAE und
zwei Gewinne mit je WIN/TIE/LOSS, ohne Wahl einer nachtraeglichen Referenz.

Primaer sechs strikte Bedingungen: LEARNED hat auf s01 an jedem der drei
Ziele kleineren MAE als PERSIST **und** LINEAR. Jeder Gleichstand/Verlust
widerlegt die vollstaendige Primaerprognose, Einzelbefunde bleiben erhalten.
Ein positiver Lernbefund setzt ausserdem einen aus vier tatsaechlichen Updates
belegten, nichtinitialen Freeze-Zustand mit `Sxx>0` voraus. Das ist eine
Bewertungsbedingung, kein technisches Startgate. Der Initialzustand alpha=0
ist rechnerisch Persistenz und benoetigt keinen vierten Vergleichsarm.

Drei unabhaengige Belastungsprognosen: LEARNED ist bei s02/s03/s04 jeweils
am ersten Wechselziel k=3 schlechter als PERSIST. Gegen LINEAR werden die
Gewinne/Verluste dort ohne Erfolgsforderung separat berichtet. Fuer k=4
keine Erfolgsforderung: Erholung, Gleichstand oder weiterer Verlust bleiben
sichtbar. Weder ein Trainingsgewinn noch eine bestaetigte Verlustprognose
kompensiert eine verfehlte primaere Transferbedingung.

Nenner: je Prueffolge und Baseline N=3; je gemeinsamer Anstieg, erstes
Zweigziel und Folgefenster N=1. Die wiederholten gemeinsamen Praefixe sind
keine unabhaengigen Replikate. Kein Gesamtmittel verdeckt Wechselverluste.
Freeze-Identitaet prueft technische Retention; erst Nutzen gegen beide
Baselines prueft die begrenzte funktionale Lernhypothese.

## Endliches Budget und spaetere Pruefgrenzen

- 26 direkte Analysen/NJ-Projektionen, je 1.248 Roh-/Halbwerte; keine rollende
  Pipeline, separate Zielmaterialisierung oder zusaetzliche Quellpaare.
- 16 Prognosestellen (4 Training, 12 Pruefung), drei Arme: 48 Vektoren je
  Implementierung, einschliesslich Direktnachrechnung 96. Je Implementierung
  LEARNED 768 Subtraktionen, Multiplikationen und Additionen; LINEAR je
  768 Subtraktionen/Additionen; PERSIST 768 Kopien. Keine versteckte Wiederverwendung.
- Vier Updates je Implementierung: 384 Differenzen, 384 Multiplikationen,
  384 Akkumulatoradditionen, vier Zaehlerupdates und hoechstens vier Divisionen.
- Fehler je Implementierung 2.304 Einzelterme, 48 MAE-Summen und 32 Gewinne;
  beide Implementierungen zusammen 4.608 Fehlerterme, 96 Summen, 64 Gewinne.
- Eine spaetere read-only Verifikation separat: 1.248 Halbierungen; Prognosen
  hoechstens 3.072 Subtraktionen, 1.536 Multiplikationen, 3.072 Additionen,
  1.536 Kopien; Updates 768 Differenzen/Multiplikationen/Additionen je Art,
  acht Zaehlerupdates/Divisionen; Fehler 4.608 Terme, 96 Summen, 64 Gewinne.
  Kein Rezeptor-/NJ-Aufruf. Danach 32 WIN/TIE/LOSS-Zuordnungen (davon acht
  Training), sechs primaere und drei getrennte Belastungsbedingungen.
- Je kanonischer Lernzustand maximal 4.096 Byte; numerischer Zustand vier
  Skalare (einschliesslich n), operatives Praefix maximal drei 48er-Vektoren
  beim Update. Kein Quellenarchiv im Lerner. Ein PCM-Payload 19.200 Byte.
  Metadaten 65.536, Gesamtbeleg 2.097.152, Pruef-/Auswertungsbeleg je
  262.144 Byte. Vollstaendige Huelle spaeter neutral pruefen, keine Grenzerhoehung.

Bestehende NV-Belegwege wiederverwenden, historische Module nicht umwidmen.
Spaeter neutral insbesondere Update-nach-Ziel, Freeze-Sperre, unabhaengige
Ruecksetzung der Praefixe, manipulierte Lernketten, Nullnenner, Rechenfolge
und Verluste pruefen. Technische Fehler phasengenau stoppen, kein Retry.
Negative Ergebnisse sind auswertbar; keine Ersatzquelle oder Koeffizientensuche.

Zeitliche Nachbarschaft definiert hier nur das naechste beobachtete Fenster,
keine gleiche Quelle oder zulaessige Objektvariation. Vorhersagefehler sind
weder automatisch Quellenwechsel noch Stress. Selbst Erfolg waere nur
erfahrungsabhaengige Vorhersage dieser kontrollierten Dynamik, kein Nachweis
von Identitaet, Bedeutung, Praegung oder Loesung der ME/MI-Lernbindung.
Jetzt nur Plan; jede Qualifikation, Vorversiegelung und Ausfuehrung bleibt
separat freizugeben. Keine Memoryschicht und keine Systemintegration.
