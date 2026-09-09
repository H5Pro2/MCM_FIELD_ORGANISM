# S2-NY: praefixgebundene Empfehlung einer eingefrorenen Historie

Status: ausschliesslich statischer Plan, keine Lauf-ID. S2-NX bleibt
unveraendert geschlossen, ohne Wiederholung oder Integration. Keine
Quellenproduktion, Berechnung, Implementierung oder Tests mit diesem Auftrag.
Gates `False`, ME/MI gesperrt; keine Memory-, Feld- oder Runtimekopplung.

## Frage und bereits erworbene Zustaende

Hilft der Fehler einer eingefrorenen Erwartung am letzten beobachteten
Uebergang, sie fuer den naechsten unbeobachteten Zustand zu empfehlen?
Genau eine Vorschrift: strikt kleineren vergangenen MAE bevorzugen.
Dies ist eine neue private Empfehlungspruefung, keine bestaetigte
Anwendbarkeitsregel, Quellenidentitaet oder sichere Wechseldetektion.

Die zwei tatsaechlich erworbenen NX-Freeze-Zustaende werden read-only
uebernommen, nicht neu trainiert, gerundet oder durch Sollkoeffizienten ersetzt.
Grundlage: [NX-Einmallauf](../reports/s2nx/s2nx-crossed-learning-20260909-01/BEFUND.md)
mit `result.json` und `verification.json` im selben Verzeichnis.

| Bindung | Kanonischer Digest |
| --- | --- |
| NX-Ergebnis | `c8b478c00ce4a83ecd7e8be138a8ba0aada0c52687a4845c7bc086272d71afd4` |
| NX-Verifikation | `4fe83068ab7382a60730f6dfe987fca271c8d64bd98f8bdfa845d9dc0ffabed9` |
| H1 FROZEN | `e2ac7055d38dfbda06dbd0073506df8251e4b8a7fd997e6253f78e3077483e45` |
| H2 FROZEN | `3ce3c6471d5bd71910cd59ca95e39d7e95de05822ee6a82b6e8236138f190205` |

H1 alpha `0.2500000003063012`, H2 `0.7500000008868464`; massgeblich sind
die gespeicherten Binary64-Werte mit vollstaendiger Zustands-/Profilbindung.
Keine Wiedereroeffnung der geschlossenen NX-Owner, keine erneute NX-Pruefung
oder Lernkettenrechnung. Die spaetere NY-Eingangspruefung bindet die
historischen Ergebnis-/Pruefbelege und beide enthaltenen Freeze-Payloads.
Die Herkunft stammt aus dem qualifizierten NX-Lauf, nicht aus NY-Neulernen.

## Genau eine Empfehlung und eine lokale Kontrolle

Alle Vektoren sind tatsaechliche 48er-Halbprofilwerte. Fuer Ziel k sind
nur z[0] bis z[k-1] verfuegbar. Immer H1, H2 und PERSIST vorhersagen:

```text
Hj[i] = last[i] + (alpha_j * (last[i] - previous[i]))
PERSIST[i] = bitcopy(last[i])
MAE(h, target) = sum(abs(h[i] - target[i]) for i=0..47)/48
```

An der ersten Pruefstelle k=2 fehlt ein beobachtetes Ziel einer solchen
Zwei-Zustands-Prognose: `ABSTAIN_INSUFFICIENT_PREFIX`. Keine Empfehlung,
kein lokaler Koeffizient und kein impliziter PERSIST-Ersatz fuer Enthaltung.
Die drei festen Kontrollen liefern trotzdem ihre gebundenen Prognosen.

Fuer k=3,4 sind die H1-/H2-Prognosen fuer k-1 bereits vor dessen Erzeugung
gebunden und danach bewertet worden. Genau diese beiden Fehler verwenden:
`E1 < E2 -> H1`, `E2 < E1 -> H2`, sonst `ABSTAIN_TIE`.
Keine absolute Fehlerschwelle, Mindestmarge, geglaettete Fehlerhistorie oder
Rolleninformation. Auch zwei schlechte vergangene Prognosen koennen somit
eine eindeutige, aber ungeeignete Empfehlung erzeugen. Fehler duerfen nicht
aus einer anderen Stelle, Folge oder anderen Freeze-Bindung stammen.

LOCAL schaetzt allein aus denselben drei verfuegbaren Zustaenden, pro Stelle
frisch, ohne gespeicherte Historie. NW-Akkumulationsfolge aus Null verwenden:

```text
xx = +0.0; xy = +0.0
for i in 0..47:
    x = z[k-2][i] - z[k-3][i]
    y = z[k-1][i] - z[k-2][i]
    xx = xx + (x*x); xy = xy + (x*y)
beta = xy/xx if xx > 0.0 else +0.0
LOCAL[i] = z[k-1][i] + (beta * (z[k-1][i] - z[k-2][i]))
```

Das ist genau eine lokale Schaetzung, keine weitere fortgeschriebene
Lernhistorie. Nullnenner, Subnormale und Produktunterlauf getrennt markieren.
H1/H2 bleiben unveraendert. Empfehlung referenziert die bereits gebundene
naechste Prognose des gewaehlten Arms, keine Mischung oder neue Rechnung.
LOCAL ist Kontrolle, niemals Fallback oder zusaetzliche Wahlmoeglichkeit.

Binary64, getrennte Subtraktion/Multiplikation/Addition, aufsteigende Indizes,
historisches Python-`sum` fuer MAE; keine FMA, Toleranz oder Umformung.
Endliche Prognosen ausserhalb `[0,1]` ungeclippt bewerten. Nichtendliche
Werte sind technische Fehler; negative Gewinne oder gleiche Fits nicht.

## Informationsgrenze und kausaler Ablauf

Pro Folge frisches Praefix und leerer Fehlerbeleg. z0/z1 analysieren;
H1/H2/PERSIST samt Direktprognosen fuer z2 binden; erst dann z2 erzeugen
und analysieren, Fehler binden. Fuer z3 aus diesen Fehlern empfehlen und
LOCAL aus z0/z1/z2 bestimmen; alle Prognosen und Empfehlung binden, erst
danach z3 erzeugen/analysieren. Fuer z4 entsprechend fortsetzen, dann leeren.
Keine Uebernahme von Prognosen als Wahrnehmung oder von Fehlern anderer Folgen.

Funktionale Eingaben: Profil, verfuegbare Vektoren, feste Koeffizienten;
Empfehlungsfunktion nur die zwei korrekt gebundenen vergangenen Fehler.
Quellen-/Zeit-/Ordinalkennungen prueft die administrative Huelle, sie werden
nicht als Features an die Rechenfunktionen gegeben. Rezepte, Kategorien,
Zukunftsfenster und Sollzuordnungen bleiben draussen. Beide Historien sowie
alle Kontrollen erhalten dieselben einmal analysierten Zielwerte.

Direktnachrechnung bildet Prognosen, lokale Schaetzung, Fehler und Empfehlung
mit eigener Arithmetik; keine primaeren Fehler, beta oder Entscheidungen
uebernehmen. Beide Gegenrechner verwenden dieselben historisch verifizierten
Freeze-Eingaben. Kein erneuter Direktlernerlauf auf NX-Quellen.

## Neue literale Quellen und Pruefstellen

Sechs Fuenferfolgen, 30 mono PCM_F32LE-Fenster mit je 4.800 Samples bei
48.000 Hz. Unveraenderter Hann-/FFT-/48-Band-Rezeptor (50..18000 Hz,
window=4800, hop=480) und NJ-Halbprofil wie NW/NX; direkte Analyse,
keine rollende Pipeline. Keine NX-Payloads als neue Testquellen.

| Gruppe | Frequenzen Hz in Partialfolge | Amplituden | Phasenseed |
| --- | --- | --- | --- |
| g0 | 670, 2010, 6030 | 4/20, 2/20, 1/20 | s2ny-pcm-001 |
| g1 | 890, 2670, 8010 | 4/20, 2/20, 1/20 | s2ny-pcm-002 |

Partial p=0..2: `u=unsigned_LE(SHA256(seed+':'+str(p))[:4])`,
`phase=(float(u)/4294967296.0)*math.tau`. Lokale Synthesezeit
`t=float(j)/48000.0`, j=0..4799. Ab `0.0` in Partialfolge
`a*math.sin(((math.tau*f)*t)+phase)` addieren, dann genau einmal mit
`float(Tabellenzaehler)/1024.0` multiplizieren und als `<f` runden.
Keine Pegelrampe innerhalb eines Fensters oder nachtraegliche Normalisierung.

| Folge | k=0 | k=1 | k=2 | k=3 | k=4 |
| --- | --- | --- | --- | --- | --- |
| s01 | 128*g0 | 320*g0 | 368*g0 | 380*g0 | 383*g0 |
| s02 | 128*g0 | 320*g0 | 464*g0 | 572*g0 | 653*g0 |
| s03 | 128*g0 | 192*g0 | 320*g0 | 576*g0 | 960*g0 |
| s04 | 320*g0 | 320*g0 | 320*g0 | 320*g0 | 320*g0 |
| s05 | 128*g0 | 320*g0 | 368*g0 | 320*g0 | 308*g0 |
| s06 | 128*g0 | 320*g0 | 464*g0 | 464*g1 | 464*g1 |

Reihenfolge s01..s06, je k=0..4; Quellen `ny-sSS-wKK`, globale Ordinalzahl
q=0..29. start=q*4800, end=start+4800, Uhr `audio.sample`, nativer Index
start//480 nur nach Ganzzahligkeit, Nichtnegativitaet und exakter Teilbarkeit.
Je Folge Ziele k=2,3,4: 18 Stellen, davon 12 mit ausreichendem Praefix.

Spaeter vor erster Analyse Rezepte, Payloadhashes, native Fenster, Profile,
Generator-/Interpreter-/Codeidentitaeten, Freeze-Import und Rechenvorschriften
versiegeln. Ausfuehrungswurzel enthaelt keine Sollhistorie. Nur Evaluation:
s01/s02 passende Fortsetzung fuer H1/H2, s03 beschleunigte unpassende
Fortsetzung, s04 Stillstand, s05 Umkehr, s06 Gruppenwechsel.
Dies sind Erzeugungsrollen, keine beobachteten Identitaeten oder garantierten
Rezeptordynamiken. Gleiche Praefixe sind keine unabhaengigen Replikate.
Alle Bytegleichheiten dokumentieren; getrennt analysieren, nicht deduplizieren.
Keine Quellenwahl nach Fit, Empfehlungsquote oder Gewinn, kein Ersatzkorpus.

## Getrennte Bewertung und Falsifikation

Empfehlung hat N=18, ausreichendes Praefix N=12; je Folge N=3 bzw. 2.
Unzureichendes Praefix und Gleichstand separat zaehlen. Nur nach Zielbeobachtung
beurteilen: empfohlene Historie strikt besser als andere = `NEXT_BEST`,
strikt schlechter = `NEXT_WRONG`, gleiche Fehler = `NEXT_TIE`.
Bei Enthaltung keine fiktive Prognose und kein Fehlerwert Null. Zahl D der
ausgegebenen Empfehlungen ist ein eigener Nenner; D=0 bedeutet Nutzen der
Empfehlung nicht geprueft. Alle Nichtempfehlungen bleiben im Abdeckungsnenner.
Eine Empfehlung kann `NEXT_BEST` sein und trotzdem beide Kontrollen verlieren.

Alle MAE und `gain=MAE_Kontrolle-MAE_Empfehlung` einzeln; WIN/TIE/LOSS
gegen H1, H2, PERSIST und LOCAL getrennt, LOCAL nur k=3,4.
Zusaetzlich H1/H2 gegen PERSIST an allen 18 Stellen und LOCAL gegen PERSIST
an den 12 verfuegbaren Stellen berichten. Kein Gesamtmittel als Ersatz.

| Block | Vorab festgelegte Kriterien |
| --- | --- |
| R01-R04 | s01 dann s02, je k=3,4: eindeutige Empfehlung und `NEXT_BEST` |
| L01-L04 | dieselben vier Stellen: Empfehlung vorhanden und MAE < MAE_LOCAL |
| P01-P04 | dieselben vier Stellen: Empfehlung vorhanden und MAE < MAE_PERSIST |
| W01-W08 | s05 dann s06, je k=3,4, je PERSIST dann LOCAL: Empfehlung vorhanden und MAE > MAE_Kontrolle |

R nur bei 4/4 bestaetigt; lokaler Zusatznutzen L separat nur bei 4/4.
Gleichstand oder Enthaltung bestehen diese strikten Bedingungen nicht.
P ist getrennte Persistenzkontrolle, kein Ersatz fuer L. W sind explizite
Verlustprognosen; nicht eingetretene Verluste und Enthaltungen getrennt zeigen.
Erstes Wechselziel k=3 und Folgefenster k=4 nicht zusammenfassen. s03/s04
vollstaendig beschreibend mit identischen Einzelmetriken, ohne Ersatzrolle
fuer gescheiterte R/L. Alle 20 Kriterien separat, keine Bestarmwahl im Auswerter.

Fehlt L, ist Nutzen ueber kurzfristige Schaetzung in dieser strikten Pruefung
nicht bestaetigt, auch bei richtigen Historienempfehlungen. Scheitert R, ist
die volle Fortsetzungsprognose widerlegt. Wechselverluste begrenzen selbst
positive R/L; vergangener Fit garantiert keine naechste Fortsetzung.

## Kleinster Anschluss und feste Budgets

NW/NX-Praediktor, kausale Fensterbindung, reine 1024-Quellensynthese und
atomare Belegwege wiederverwenden. Spaeter nur private NY-Freeze-Import-,
Praefixfehler-/LOCAL- und Auswertungsbindung ergaenzen; historische
Haupteinstiege, Zaehler und Defaults nicht umwidmen. Keine weitere Plattform.

| Arbeit | Obergrenze je Implementierung |
| --- | --- |
| Prognosen | 66 Vektoren: 6 Stellen mit 3, 12 mit 4 Armen |
| Prognosesubtraktionen / Multiplikationen / Additionen | je 2.304 |
| Persistenzkomponenten | 864 |
| Lokale Schaetzungen / Divisionen | 12 / hoechstens 12 |
| Lokale Differenzen / Produkte / Akkumulatoradditionen | je 1.152 |
| Fehlerterme / MAE-Summen samt Division | 3.168 / 66 |
| Empfehlungen | 18, davon 6 ohne Uebergangsevidenz |
| Gewinndifferenzen | hoechstens 96: 48 Empfehlungskontrollen, 48 gegen PERSIST |

Vergangene MAE werden aus dem unmittelbar vorangehenden gebundenen Beleg
gelesen, nicht erneut berechnet. Empfehlung referenziert einen vorhandenen
Prognose-/Fehlerbeleg. Hauptarm plus unabhaengige Direktnachrechnung: zweimal
obige Grenzen, keine dritten Rechnungen im Lauf.
Genau 30 Analysen und 30 NJ-Projektionen, je 1.440 Roh-/Halbwerte;
maximal ein PCM-Fenster mit 19.200 Byte, keine Rohpayloadablage.

Eine spaetere read-only Verifikation separat: 1.440 Halbierungen,
je 4.608 Prognosesubtraktionen/-multiplikationen/-additionen, 1.728 Kopien,
je 2.304 lokale Differenzen/-produkte/-additionen, hoechstens 24 Divisionen,
6.336 Fehlerterme, 132 MAE-Summen/-Divisionen, 36 Empfehlungspruefungen und
192 Gewinnpruefungen. Danach maximal 96 WIN/TIE/LOSS, 18 Empfehlungsurteile
und die 20 Kriterien einmal auswerten. Keine Rezeptor- oder NX-Wiederholung.

Je Freeze-Payload maximal 4.096 Byte; zwei gemeinsame unveraenderliche
Eingaenge, keine operativen Lerner. Maximal drei operative Praefixvektoren:
aeltesten erst nach vollstaendiger Prognosebindung, vor Zielerzeugung freigeben.
Je Stelle Metadaten/Prognosebindung 65.536 Byte; atomarer Gesamtbeleg
2.097.152 Byte; Verifikation und Auswertung je 262.144 Byte. Vollstaendige
Huelle einschliesslich Quellen-, Roh-/Halb-, Freeze- und Fehlerbelegen spaeter
neutral pruefen. Bei Bindungs-, Werte- oder Ressourcenfehler typisierter
Abschluss ohne fachliche Teilauswertung; kein Retry oder Grenzwechsel.

Die kausale Zukunftssperre muss spaeter am Aufrufpfad qualifiziert werden;
ein Offline-Digest allein beweist sie nicht. Zunaechst Analystenentscheidung
ueber diesen Plan, keine Ausfuehrungsfreigabe. Auch ein Erfolg waere nur
begrenzte beobachtungsbasierte Empfehlung, keine Loesung der ME/MI-Bindung.
