# S2-NO: Halbprofil-Funktionsplan mit gebundenen NH-Quellen

## Status und Frage

Statischer Plan auf Stand `5d4c989`, 2026-09-07. Keine neue Lauf-ID,
Implementierung, Vorversiegelung, Quellenmaterialisierung, Tests oder Ausfuehrung.
S2-NN ist neutral qualifiziert. Der historische NH-Abbruch bleibt
`NOT_EVALUABLE`; S2-NM bleibt akzeptierte semantische Profilabweichung.

Frage: Welche Stabilisierung und welche richtigen/falschen Abrufe oder
Enthaltungen entstehen auf der gebundenen NH-Folge innerhalb des neuen
Halbprofils, und was veraendert dessen strengere auditive A-Regel?
Dies ist ein **neuer profilgebundener Versuch**, keine Reparatur des alten Laufs,
keine verlustfreie Migration und kein Nachweis allgemeiner Robustheit.

## Unveraenderte Quellen, neue Versuchskonfiguration

Wiederverwendung von `reports/s2nh/s2nh-source-preseal-20260906-01/`:

| Bindung | Unveraendert uebernommener Digest |
| --- | --- |
| execution-plan.json, Wurzeldigest | `47ac97a175e37d45f576479ba82c906e4b36c47ae3708fca7d8e6ced885298a4` |
| evaluation-plan.json, Wurzeldigest | `03bb9a881d5f03935104788f2a98083d2790c8dc0565c5a9664c5d5ba13e8cb2` |
| seal.json, Wurzeldigest | `c0acb80b6ab88436ee0daaf007cc2abd46ce4409d9a40ed8fdc2c6635bbb2b2b` |
| execution-plan.json, Datei-SHA-256 | `776ddf73bcbd9f61ad64612bc7bfb0ddeaebb6c233026e9831a2bfdd5a607826` |
| evaluation-plan.json, Datei-SHA-256 | `a2b07880702f33bbff6129fdfe11b96897503cef52f7e46f0c9d52b415c9a531` |
| seal.json, Datei-SHA-256 | `65bb79bc8c0e65b433a1a9f5bb84969970e440a51745a85af8883e1dc99838bd` |

Alle 15 PCM-Rezepte, 13 vollen RGB-Grundrezepte, vier getrennten visuellen
Cuequellen und 28 Ereignisse einschliesslich Quellenfenstern, Masken und
Reihenfolge bleiben unveraendert. Exaktkopien behalten getrennte Identitaeten.
Der bereits im PCM-Rezept enthaltene Faktor `0.989912331104279` bleibt mit
derselben Binary32-Rechenfolge erhalten: **keine zusaetzliche Eingangsabschwachung**.
Keine Neuversiegelung, Seedwahl, Ersatzquelle oder Anpassung an Messergebnisse.

Das Siegel enthaelt das historische Default-Live-Profil. Es wird nicht
umgeschrieben oder als Halbprofil ausgegeben. Eine kleine neue Versuchskonfiguration
referenziert beide alten Wurzeln und bindet explizit NJ-/NL-Profil, neue
Komponentenhashes, beide Regeln und diesen Plan. Der neue Koordinatordigest ist
`55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e`;
die vollstaendigen NJ-/NL-Bindungen stammen aus dem qualifizierten Profil.

Historische Dateihashes bleiben Herkunftsbelege. Die spaetere Quellenpruefung
muss Generator, reine Quellfunktionen, Interpreter/math/NumPy und unveraenderte
Rohrezeptoren weiterhin exakt binden. Versionierte Memory-/Profilkomponenten
werden ausdruecklich gegen die neue Bindung geprueft, nicht gegen alte
Kernhashes. Kein pauschales Ignorieren abweichender Hashes: die Trennung zwischen
unveraendertem Quellenpfad und versioniertem Profilanschluss ist explizit.

Der Korpus wurde urspruenglich unabhaengig vorversiegelt, ist inzwischen aber
teilweise untersucht, insbesondere e01/e02 und die diagnostische Reproduktion
des e02-Audioendpunkts. Er ist **kein vollstaendig unberuehrter Bestaetigungskorpus**.
Diese Vorgeschichte wird im neuen Ergebnis genannt, nicht nachtraeglich verdeckt.

## Reale Materialisierung: NJ vor dem Kontakt

Verbindlicher spaeterer Pfad:

```text
versiegelter PCM-Payload -> Hashpruefung -> fortgefuehrter HearingPath
-> gebundener roher AuditoryReceptorState -> genau einmal S2-NJ
-> halbierter Audiokontakt -> gemeinsame AV-/Cue-Bindung
-> identische neue Werte an unabhaengige Feld-/Memoryzweige beider Arme
```

Lesender Befund: `BroadbandHearingPath.push` liefert einen rohen Spektralzustand,
noch keinen normalformgebundenen `ReceptorContactFrame`. Der alte
`_s2nh_private_runtime_binding.Materializer.run_once` ruft danach unmittelbar
`from_auditory_receptor_state(state)` auf. **Dieser Aufruf darf im neuen
Audiopfad nicht vor NJ stattfinden.** Auch zur Zeit-/Digestpruefung kein
vorlaeufiger unskalierter Kontakt. Den alten Materialisierer nicht aufrufen.

Genau ein HearingPath, 24 Audiofenster, 240 Hops und 231 rollende Abschluesse.
Nur die 24 versiegelten Endpunkte gehen in Ereignisse ein und erhalten jeweils
genau eine NJ-Projektion, nicht je Regelarm. Die uebrigen Abschluesse erhalten
keinen Kontakt und werden verworfen. Native Audiozeit schreitet auch ueber
reine Videoereignisse hinweg im selben HearingPath korrekt fort.
24 visuelle Analysen; Cueframes werden bereits okkludiert analysiert, nie
zuerst als volle Zielbilder. Hoechstens ein PCM-Fenster und ein RGB-Frame
gleichzeitig; Payloadhash vor Verarbeitung, Rohpayload nach Reduktion freigeben.

Notwendige kleine Anschlussaenderungen, jetzt **nicht implementiert**:

1. Eigene profilgebundene Materialisierung auf Basis der vorhandenen NH-Schleife
   und reinen Generatoren. Alte `Materializer.__init__`-Profilgleichheit,
   `load_execution`/`source.watched` mit historischen Kernbindungen nicht durch
   Umetikettierung umgehen; Quellenwurzel und neue Profilwurzel separat validieren.
2. NN-Eingangsbindung fuer die echten getrennten gemeinsamen Fenster ergaenzen:
   NH-Visual beginnt bei `(3*k-1)*1e9//30`, Audio bei `k*100ms-10ms`, beide
   enden bei `k*100ms`. NN verlangt bisher `visual.field_time == common_time`.
   Fuer volle AV-Ereignisse stattdessen die exakt versiegelten Modalitaetsfenster,
   gleiche Felduhr und deren Schnittmenge als Pairingzeit pruefen. Kein Zeitwert
   wird verschoben; insbesondere bleibt die volle visuelle Fensterbindung erhalten.
   NL-`bind_pair` und bestehendes Pairing koennen diese Ueberlappung darstellen.
3. NN hat bisher nur einen neutralen Vergleichseinstieg. Spaeter ein kleiner
   geschlossener Einmaleinstieg mit neuer ID/eigenem Verzeichnis und fester
   Halbprofilbindung an vorhandenes NG-`RuntimeComparison(mode="MAIN")`;
   keine 28 Ereignisse als `NEUTRAL` deklarieren oder neutrale Limits lockern.
   Historische NH-Haupteinstiege bleiben unaufgerufen und unveraendert.
4. Quellenreceipt/Verifikator an NJ anpassen: rohen Rezeptorzustandsdigest und
   Rohwerte-Digest, NJ-Profil-/Projektionsdigest, gerundeten Werte-Digest und
   Unterlauf-/Subnormalmarker getrennt binden. Der alte NH-Verifikator darf
   Rohenergien nicht aus halbierten Kontaktwerten rekonstruieren. Kompakte
   Receipts, Profil-Carriers und bereits gespeicherte neue Werte wiederverwenden;
   keine zweite Projektion, keine Rekonstruktion verlorener Bits und keine
   duplizierten Vollbelege pro Arm. Bestehende NG-Gesamtpruefung wiederverwenden.

Ein endlicher NJ-Ausgang ausserhalb `[0,1]`, Nichtendlichkeit, Quellen-, Zeit-,
Form-, Digest-, Ausfuehrungs- oder Ressourcenfehler fuehrt zu dokumentiertem
`NOT_EVALUABLE`. Phase, Ereignis, Quelle und erreichte Zaehler erhalten.
Kein Clipping, Nachnormalisieren, weiterer Faktor oder Retry.

## Zwei Arme innerhalb desselben neuen Profils

- `HISTORICAL_SUM_L1_24`: historische Rechenfolge `sum(...)/24`, jetzt mit
  Audiogrenze `0.1`; keine historische Werte-/Profilreproduktion behaupten.
- `ALL_BANDS_24`: groesste absolute Differenz auf 0..23 `<= 0.1`, nur B4/Fast.
- Auditive Formation/Fast `fsum/48 <= 0.1`, PPB `fsum/48 <= 0.01`,
  Slow-Teilscan `sum(...)/24 <= 0.01`. Interne gemischte Auswahl fest mit
  `r_audio=2.0*d_audio`, dann `(max(r_audio,d_visual), r_audio+d_visual, slot_id)`
  und den bestehenden routenspezifischen Tie-Breaks. Rangfreie Scans bleiben rangfrei.
- Visualwerte/-regeln, Kapazitaeten, Support, Updates und Zeitparameter bleiben
  unveraendert. Keine automatische Regelwahl, B-Bevorzugung oder Hypothesenanwendung.

Beide Arme erhalten dieselben unveraenderlichen Materialisate, aber getrennte
frische Runtime-, Feld-, Memory- und Ownerinstanzen. Vergleich korrespondierender
neuer Feld-/Memoryzustaende; regelgebundene Gesamtdigests duerfen differieren.
Feldkontakte unabhaengig von Memory-/Scanfehlern; nur B4/TSPM atomar.
Keine Alt-/Neu-Feldgleichheit und kein kompensierender Feldgain.
Gerundete Wertegleichheit gilt im neuen Profil; S2-NM verbietet daraus eine
allgemeine semantische Gleichheit oder automatisch richtige Konfliktaufloesung abzuleiten.

## Folge, Bewertung und Falsifikation

Die versiegelte Ereignisliste wird literal uebernommen: e01/e02 erste volle
Erfahrungen, e03/e04 fruehe Audio-/Visualhinweise, e05..e13 weitere interleaved
Formationen, e14..e22 neun Druckereignisse, e23..e28 spaete Hinweise.
Je Arm 20 Formationen und acht read-only Hinweise ohne Zustandsneustart oder
Vollprobe. Felduhr bleibt `s2nh-transfer-field-clock`, getrennt von nativen Uhren.

Erst nach einer technisch gueltigen Gesamtverifikation die unveraenderte
NH-Evaluationswurzel anwenden. Rollen und Zielwerte bleiben ausschliesslich dort.
Sollsupport A/B/C = 3/3/2, Stabilisierung und A-Verdraengung sowie erwartete
Hinweistreffer sind **Vorhersagen, keine technischen Startbedingungen**.

Fuer jede Formation Fast-Auswahl, Slotgeneration, PPB-Uebergang, Support und
Herkunft ausweisen; Ersetzung trennt Generationen, Sattigung bleibt MATCHED.
Reine, gemischte, instabile und verlorene Spuren unterscheiden. Zielbindung
aus tatsaechlichen neuen Formationsketten, nie aus Hinweiszielwerten oder
historischen unskalierten Prototypdigests. Numerische Wertgleichheit und
Herkunft getrennt berichten; kollidierende oder gemischte Herkunft nicht
allein wegen eines gleichen Digests als richtigen Zielabruf zaehlen.

Alle acht Hinweise, volle Treffermengen und beide Direktbaselines ausweisen.
N/D/R/L (`D=R+L`) nach Modalitaet, frueh/spaet, Variante, tatsaechlicher
Rezeptorvariation und belegter Konkurrenz berichten. D zaehlt richtige
Referenzzulassungen, nicht nur anwendbare Zielkandidaten; **D=0 bleibt
ERHALTUNG_NICHT_GEPRUEFT**. Visuelle Treffer fuellen keine auditiven Nenner auf.
Neue richtige Abrufe, jeder Verlust, verworfene Zielkandidaten, Fehlzulassungen
und Enthaltungsgruende einzeln erhalten. Mehrdeutigkeit ist keine erkannte
Unbekanntheit. Gewinne duerfen Verluste nicht verrechnen.

Ein Verlust bei D>0 widerlegt Erhaltung in dieser Pruefmenge; eine neue
Fehlzulassung widerlegt den entsprechenden Sicherheitsanspruch. Ohne neue
richtige Abrufe oder verhinderte Fehlzulassungen kein Selektivitaetsgewinn.
Gemischte Ergebnisse und fehlende Stabilisierung sind regulaere Funktionsbefunde,
keine technischen Fehler. Kein Erfolg allein durch weniger Kandidaten.

## Bestehende Belegwege und Grenzen

Spaeter genau ein Hauptaufruf, ein atomarer Gesamtbeleg, eine unabhaengige
read-only Verifikation ohne Rezeptor-/Runtimewiederholung, danach einmal
getrennt auswerten. Neue Schema-/Profilbindung um die bestehenden NG-Belege;
keine Recorderplattform. Beide Runtimes auch bei Fehlern schliessen, beteiligte
Hauptgates ausschliesslich fuer den autorisierten Aufruf oeffnen und danach False.

Unveraendert je Arm 28 Ereignisse/20 Formationen/8064 Feldkontakte; zusammen
16128 Kontakte und 32 Scanbelege. Maximal 576 Slotbesuche, 21248
Scan-Wertvergleiche plus separate gleich grosse Verifikationsreserve,
416 logische Scanoperationen und Formation-L1-Limit 142080. Audio pro Scan
maximal 528, Visual 800. Rohpayload gleichzeitig maximal 19200 PCM- und
6220800 RGB-Byte, kein behaupteter neuer Prozess-Peaknachweis.

21 Zustandsbelege je maximal 98304 Byte, 28 gepackte Eingaben und 28
Schrittpaare je maximal 16384, 32 Scans strikt unter 32768, Metadaten maximal
65536 Byte. Gesamtbeleg einschliesslich Quellen-/NJ-Anbindung maximal
4194304 Byte; kompakter NH-artiger Aussenbeleg maximal 32768 Byte.
NN-Eingangsbundles bis 65536 Byte bleiben transiente Bindungen, keine weitere
28-fache Kopie im Ergebnis. Bei Ueberschreitung Stopp, keine Grenzerhoehung.

Dieser Auftrag endet mit dem Plan. Anschlussaenderungen und ein realer
Einmallauf benoetigen weitere ausdrueckliche Freigaben. Alle Gates bleiben
jetzt False; historische NH-/NM-/NN-Belege und Bootstrap bleiben unveraendert.
