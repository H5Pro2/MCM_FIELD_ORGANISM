# S2-NS: auditive Zwei-Sichten-Bestaetigung

Stand 2026-09-08. Ausschliesslich statischer Plan, keine Laufnummer und keine
Ausfuehrungsfreigabe. NP/NQ/NR bleiben unveraendert geschlossen. Untersucht
wird eine **neue, strengere Zulassungsregel**, weder eine dritte bessere feste
Maske noch Sequenzgedaechtnis, Objektidentitaet oder eine neue Memoryschicht.

## Evidenz und Entscheidungsregel

Zwei feste, komplementaere Sichten desselben realen Audioendpunkts:
`LOWER_24 = (0..23)`, `UPPER_24 = (24..47)`, jeweils aufsteigend.
Ein Rezeptoraufruf und eine NJ-Halbprojektion pro Endpunkt, danach zwei
getrennte unveraenderliche Index-/Wertebelege. Beide binden dieselbe Quelle,
PCM-Hash, native Uhr und Fenster, Rohzustandsdigest, NJ-Projektionsdigest und
Profilidentitaet; eigene Masken- und Teilwertdigests. Keine zweite Analyse,
automatische Sichtwahl, nachtraegliche Umordnung oder Werteimputation.
Die Sichten sind getrennt geprueft, nicht statistisch unabhaengige Messungen.

Jeder Sichtpruefer erhaelt nur seine 24 Werte mit Originalindizes und denselben
unveraenderlichen Halbprofil-Memoryzustand. Vollstaendiger Scan aller 9 B4-,
3 Fast- und 8 auditiven Slow-Slots, einschliesslich expliziter Nichtbelegung;
kein Short-Circuit. Slow nur bei der bestehenden Stabilitaetsgrenze anwendbar.
Je eligible Slot k und Sicht I bleibt die Rechnung:

```text
terms_I(k) = abs(cue[i] - candidate_k[i]), i in I aufsteigend
A_I(k)    = max(terms_I(k)) <= 0.1
B_I(k)    = sum(terms_I(k))/24 <= 0.01
confirmed(k) = eligible(k) AND match_LOWER(k) AND match_UPPER(k)
```

Historische Binary64-Summationsfolge, inklusive Grenzen, keine Toleranz.
Fuer A ist diese Konjunktion mathematisch gleich einer Maximumpruefung ueber
alle 48 tatsaechlich beobachteten Werte; kein darueber hinausgehender Mechanismus
wird behauptet. Fuer Slow sind **beide 24er-Mittelwerte einzeln** erforderlich.
Ein gemeinsames `sum(...)/48` ist kein Ersatz: Er kann eine einseitige
Grenzverletzung verduennen. Kein weiterer Vollsicht-Vergleichsarm.

Zusammenfuehren nur ueber identische Bindung aus Geschichte, Profil,
Zustandsdigest, Bank, Slot-ID, Generation und aktuellem Slot-/Wertedigest.
Generation kommt aus dem belegten CREATED-/REPLACED-Formationsuebergang;
MATCHED setzt sie fort. Slot-ID oder Wertegleichheit allein reichen nicht.
Diese technische Herkunft wird aus der bestehenden Transaktionskette fuer
den Abrufbeleg gebunden, nicht als neue dauerhafte Memoryablage angelegt.
Keine Zuordnung ueber Zielrollen. Luecken, Ersetzung zwischen den Sichten oder
abweichende Bindungen ergeben typisierten Evidenzfehler, keine Bestaetigung.

Erst auf den bestaetigten Slotmengen erfolgt die bestehende Aufloesung:
mehrere Treffer in B4 oder Fast bedeuten A-interne Mehrdeutigkeit; je ein
B4-/Fast-Treffer wird anhand aller 48 gespeicherten Kandidatenwerte auf
Gleichheit oder Konflikt geprueft. Keine Deduplication mehrerer Banktreffer.
Mehrere stabile Slow-Treffer bedeuten B-interne Mehrdeutigkeit. Intern gueltiger
Konflikt bedeutet Enthaltung; sonst genau ein oeffentlicher Bereich A oder B
zulassen, null enthalten, beide enthalten. Kein B-Vorrang oder Ranking.

Die Einzelarme loesen ihre eigenen Treffermengen mit derselben Tabelle auf.
Der Bestaetigungsarm stimmt **nicht** ueber fertige Einzelhypothesen ab:
beide Sichten duerfen einzeln mehrdeutig sein und dennoch denselben einzigen
Slot gemeinsam bestaetigen. Unterschiedliche eindeutige Slotgenerationen
koennen sich umgekehrt nicht gegenseitig bestaetigen.

Fehlt eine regulaere zweite Sicht, lautet der kombinierte Befund
`ABSTAIN_INSUFFICIENT_EVIDENCE`; kein Fallback. Beschaedigte vorhandene Evidenz
bleibt technischer Fehler. Keine Ergaenzung aus Memory. Zusammen sind alle
48 Baender beobachtet: Ausgabe hier nur Zulassungs-/Enthaltungsbeleg mit
Bereich und Kandidatenherkunft, **keine ergaenzten Wahrnehmungswerte**.

## Neuer, vor Analyse zu versiegelnder Pruefbestand

Sieben neue PCM_F32LE-Rezepte, je 4800 Samples bei 48000 Hz. Bestehender reiner
`pcm_bytes`-Generator: Gruppen-/Partialfolge literal; Phasen aus ersten vier
SHA-256-Bytes von `seed+':'+str(partial_index)`, unsigned LE,
`phase=(float(u)/4294967296.0)*math.tau`. Je Sample j: `t=float(j)/48000.0`,
`f=float(millihz)/1000.0`, `a=float(n)/float(d)`,
`angle=((math.tau*f)*t)+phase`, Summe ab 0.0 in Gruppen-/Partialfolge.
Nur abschliessend `struct.pack_into('<f',...)`; kein Zwischen-Float32,
Clipping, Scalingwechsel oder Normalisieren. Jede Tabellenzeile ist eine
Gruppe, ausser a06 mit den zwei ausdruecklich aufgefuehrten Gruppen.

| Quelle | Frequenzen in mHz | Amplitudenverhaeltnisse | Seed |
| --- | --- | --- | --- |
| ns-a01 | 271000,1084000,6775000 | 6/20,2/20,1/20 | s2ns-pcm-001 |
| ns-a02 | 419000,1676000,10475000 | 6/20,2/20,1/20 | s2ns-pcm-002 |
| ns-a03 | 271000,1084000,6775000 | 6/20,2/20,1/20 | s2ns-pcm-001 |
| ns-a04 | 271000,1084000,6775000 | 9/40,3/40,3/80 | s2ns-pcm-001 |
| ns-a05 | 279130,1116520,6978250 | 6/20,2/20,1/20 | s2ns-pcm-001 |
| ns-a06, Gruppe 0 | 271000,1084000,6775000 | 6/20,2/20,0/1 | s2ns-pcm-001 |
| ns-a06, Gruppe 1 | 419000,1676000,10475000 | 0/1,0/1,1/20 | s2ns-pcm-002 |
| ns-a07 | 593000,2372000,8302000 | 6/20,2/20,1/20 | s2ns-pcm-003 |

Nullamplituden in a06 bleiben explizite Partialpositionen mit ihren Phasen;
keine Deduplizierung oder Auslassung. a01/a03 sind getrennte Exaktquellen.
a06 ist eine physische Partialmischung, kein Zusammensetzen von Rezeptorwerten.
Wegen Filterbankueberlappung ist ein Widerspruch der beiden Teilbefunde eine
Pruefannahme, keine garantierte Geometrie oder Startbedingung. Wird er nicht
beobachtet, bleibt seine reale Pruefdeckung offen; keine Ersatzquelle.

Elf neue RGB8-Begleiter ns-v01..ns-v11, unveraenderter reiner NH-SHA-Grid-
Generator, 1920x1080, 8x12x3 Blockwerte, `partial=False`; Seed
`s2ns-independent-av-20260908-v1:visual:vNN`, NN=01..11. Keine RGB-Optimierung
an Fast-Distanzen. RGB dient nur echter AV-Memorybildung, keinem Feldpfad.

Vor jeder Rezeptoranalyse: alle Rezepte, Seeds, Payloadhashes, Ereignisse,
Zeiten, Python-/math-/Generatoridentitaeten, Profile und diesen Dokumentstand
in getrennten Ausfuehrungs-/Evaluationswurzeln versiegeln. Keine NR-Werte,
keine Quellenauswahl nach Distanzen oder Ergebnissen, kein Ersatzseed.

## Literale Folge und Herkunft

Drei frische Memorygeschichten, kein eingesetzter Slot und kein historischer
Zustandsimport. Die Quellen-IDs sind technische Bindungen, keine Sollrollen.

| Geschichte | Formationseingaenge in Reihenfolge | Danach fuenf read-only Endpunkte |
| --- | --- | --- |
| h01 | (a01,v01), (a02,v02) | a03, a04, a05, a06, a07 |
| h02 | (a02,v02) | a03, a04, a05, a06, a07 |
| h03 | (a01,v01), (a01,v01), (a01,v01), (a01,v01), (a02,v03), (a02,v04), (a02,v05), (a02,v06), (a02,v07), (a02,v08), (a02,v09), (a02,v10), (a02,v11) | a03, a04, a05, a06, a07 |

Vollstaendige Praefixe sind `ns-`. Globale neutrale Ereignisse e01..e31:
h01 e01..e07, h02 e08..e13, h03 e14..e31. Je Ereignis n native Audiozeit
`[(n-1)*4800,n*4800)` auf `audio.sample`; ein direkter analyze-Endpunkt mit
Snapshotindex n-1, keine rollende Pipeline. NJ einmal vor Audiokontaktbildung.
Formationen nutzen Video `video.frame [3*n-1,3*n)`; gemeinsame reine
Zeitprojektion wie NQ, Audiokontakt `[E-10000000,E)`, Video
`[floor((3*n-1)*1000000000/30),E)`, E=n*100000000,
Clock `s2ns-pairing-clock`. Kein Feldaufruf. Hinweise sind strikt spaeter
als die Formationen und lesen denselben Zustand in allen Armen.

Nur Evaluationswurzel: a01 Ziel, a02 Konkurrent, a03 Exaktkontrolle,
a04 Pegel-, a05 Frequenzvariante, a06 Misch-/Widerspruchskontrolle,
a07 unabhaengige Nichtzielkontrolle. a06 besitzt kein autorisiertes eindeutiges
Ziel. Erwartet: h01 richtige A-Abrufe fuer a03..a05, h02 Enthaltung,
h03 richtige B-Abrufe fuer a03..a05, Kontrollen stets Enthaltung.

Erreichbarkeitsgrenze: neun spaetere Formationen verdraengen die alten
B4-Eintraege. Fast-Trennung, Konsolidierung und reines B mit Support 3 haengen
von den noch ungemessenen Quellen ab. Abweichende Bildung, Vermischung oder
fehlendes stabiles B werden regulaer ausgewertet, nicht durch neue Quellen
repariert. Formation, Fast-Rangskala, PPB-Updates und Supportgrenzen bleiben
unveraendert im qualifizierten Halbprofil.

## Vergleich, Verlustkontrollen und Falsifikation

Drei vorab gebundene Arme: LOWER allein, UPPER allein, generationstreue
Konjunktion. Zwei Sichtscans pro Implementierung genuegen: deren unveraenderte
Termbelege tragen Einzel- und Konjunktionsentscheidung, kein dritter Distanzscan.
Unabhaengige Direktnachrechnung scannt beide Sichten selbst und entscheidet
mit eigener Tabelle, ohne produktive Scan-/Entscheidungshelfer.

Je Einzelarm gegen Konjunktion separat N/D/R/L fuer Zielbeziehungen und
richtige oeffentliche Abrufe, A/B, Exakt/Varianten und Konkurrenz trennen.
D=R+L; D=0 bleibt ERHALTUNG_NICHT_GEPRUEFT. Rezeptorvariation gegen belegte
Formationseingaenge auf denselben Indizes, PPB-Drift separat; fehlende oder
uneindeutige Referenzen null. Fehlende Zielbildung nicht als Erhaltungserfolg.

Jeden verworfenen Zielkandidaten, richtigen Abrufverlust, Gewinn, falsche
Anwendbarkeit, Fehlzulassung und Mehrdeutigkeit mit Quelle und Nenner ausweisen.
Die Schnittmenge kann falsche Beziehungen ausschliessen, aber auch richtige.
Weniger Kandidaten garantiert keine richtige Eindeutigkeit: ein verbleibender
Konkurrent kann nach Zielausschluss sogar neu falsch zugelassen werden.
Keine Verrechnung von Gewinnen und Verlusten. Widerspruchstypen separat:
einseitiger Slotmatch, disjunkte Treffermengen, verbleibende Mehrdeutigkeit.

Begrenzter Nutzen gegen einen Einzelarm nur bei mindestens einer verhinderten
Fehlzulassung oder einem neuen richtigen Abruf, ohne neue Fehlzulassung,
ohne Zielbeziehungs-/Abrufverlust und mit positivem echtem Varianten-D.
Ein Verlust widerlegt verlustfreie Uebertragung gegen diesen Arm; D=0 oder
kein realer Widerspruch bleibt Nichtnachweis. Kein Erfolgsgate fuer den Lauf.
Gueltige Enthaltung ist auswertbar; Typ-/Zeit-/Profil-/Digest-/Ressourcenfehler
sind technisch NOT_EVALUABLE. Selbst Uebereinstimmung beweist keine Klangidentitaet.

## Endlicher Rahmen und kleinster Anschluss

Nur private versionierte Zwei-Sichten-Belege und generationstreuer Join vor
der bestehenden A/B-Tabelle. Historische NQ/NR-Typen und Defaults unveraendert;
UPPER_24 nicht durch Umetikettieren einer bestehenden Maske einschleusen.
Keine Runtime-/Feldintegration, Hypothesenanwendung oder neue Memorymechanik.

- Vorversiegelung: 7 PCM- und 11 RGB-Quellen; hoechstens ein PCM-Fenster
  (19200 Byte) und ein RGB-Frame (6220800 Byte) gleichzeitig, keine Rohablage.
- Spaeter 31 Ereignisse: 16 Formationen, 15 Hinweise; 31 Audioanalysen und
  NJ-Projektionen sowie 16 visuelle Analysen, keine Analyse pro Sicht.
- Primaer plus Direkt: 60 vollstaendige Sichtscans, 1200 Slotzeilen,
  maximal 28800 Banddifferenzen. 90 getrennte Entscheidungen einschliesslich
  Einzelarme und Konjunktion, maximal 4320 Kandidatengleichheitsvergleiche.
- Offline separat: maximal dieselben 60/1200/28800/4320; keine Rezeptor- oder
  Memorywiederholung. Formation separat bestehende NQ-Obergrenze 71040
  belastete L1-Terme, 16 Formationspruefungen. Quellen-/Zeit-/Generations-
  Validierungen bleiben im Beleg separat von Distanzarbeit auszuweisen.
- Bestehende Limits: 98304 Byte je Zustand, 32768 je Sichtscan, 65536
  je Metadatenhuelle, 4194304 Byte Gesamtbeleg. Hoechstens 17 verschiedene
  Zustandsdarstellungen; ein gemeinsamer unveraenderlicher Nullbeleg ist
  keine Zusammenlegung der drei Geschichten. Keine Grenzerhoehung bei Platzmangel.

Spaeter notwendige neutrale Kontrollen: fehlende Sicht, fremder Endpunkt,
abweichende Generation trotz gleicher Slot-ID/Werte, inklusive Grenzen,
disjunkte Treffer, gueltige Enthaltung, vollstaendige Scans und Direktgleichheit.
Konkrete kanonische Gesamtgroesse und administrative Validierungszaehler sind
vor einer solchen Qualifikation zu binden, nicht nach einem Hauptlauf.
Bestehende atomare Beleg-/Verifikationswege genuegen; keine neue Plattform.

Jetzt wurden ausschliesslich Dateien gelesen und dieser Plan dokumentiert.
Keine Quellenproduktion, Berechnung, Tests, Implementierung oder Ausfuehrung.
Gates bleiben False. Vorversiegelung, Qualifikation und realer Versuch bleiben
separat freizugeben; historische Belege und Bootstrap unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenpruefung der generationstreuen
Zwei-Sichten-Regel, ihrer Verlustkontrollen und des begrenzten neuen Bestands weiter.
