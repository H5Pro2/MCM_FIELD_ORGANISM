# S2-NQ: realer Masken-/Memorytransfer

## Technischer Abschluss

Lauf-ID `s2nq-real-mask-memory-transfer-20260908-01`, 2026-09-08,
qualifizierter Quellenstand `7945a4cd2d73d2f2613fb785e11b570c06a9d666`.
Genau ein `run_main_once`, eine unabhaengige read-only Gesamtverifikation
und danach eine getrennte Auswertung. Kein Test, Vorlauf oder Retry.

Aufruf aus dem workspace-Root:
`C:/Python314/python.exe -m reports.s2nq.run_transfer_once`.
Exit-Code **0**. Aufzeichnung und Verifikation: **RECORDING_COMPLETE**;
Auswertung: **EVALUATED**. Diese technischen Status bedeuten fuer sich
noch keinen fachlichen Erfolg. Gate vor/nach Ausfuehrung **False**;
Oeffnung nur im Speicher fuer den einen Hauptaufruf. Qualifizierte
Dateihashes vor/nach identisch, kein Produktcode geaendert.

| Arbeit | Tatsaechlich | Gebundene Obergrenze |
| --- | ---: | ---: |
| Ereignisse / Formationen / Hinweise | 36 / 16 / 20 | 36 / 16 / 20 |
| Direkte Audioanalysen / NJ-Projektionen / visuelle Analysen | 36 / 36 / 16 | 36 / 36 / 16 |
| Abrufbelege inklusive Direktbaselines | 80 | 80 |
| Slotinspektionen | 1.600 | 1.600 |
| Beobachtete Banddifferenzen | 10.944 | 38.400 |
| Kandidatengleichheitsvergleiche | 864 | 3.840 |
| Logische Abrufoperationen | 1.120 | 1.120 |
| Formations-L1-Budget, konservative Ledgerzaehlung | 56.832 | 71.040 |
| Atomarer Gesamtbeleg, Byte | 1.565.773 | 4.194.304 |

Die **zusaetzliche** Offline-Verifikation ist nicht im Abrufbudget enthalten:
80 Armpruefungen, 1.600 Slotinspektionen, 10.944 Banddifferenzen,
864 Gleichheitsvergleiche, 9.408 Fast-Rangterme, 672 PPB-Auswahlterme,
10.752 konservativ belastete Updatekomponenten und 16 Formationspruefungen.
17 Zustandsdekodierungen, 113 Zustandsvalidierungen mit 629.184 belasteten
Wertpruefungen, 36 Quellenbindungen, 108 Projektionsvalidierungen und
6.336 Eingangswertpruefungen. Alle separaten Grenzen eingehalten.
`verification.json`: 24.707 Byte; `evaluation.json`: 57.009 Byte.

Alle 20 Hinweise lesen denselben jeweiligen Vor-/Nachzustand in beiden
Sichten und beiden Direktbaselines. Semantische Baselinegleichheit ist fuer
alle 40 Primaer-/Direktpaare bestaetigt. Nur die 16 Formationen schreiben.
Keine Feld-, Runtime-, Vollprobe- oder Hypothesenanwendung.

## Tatsaechliche Bildung und Herkunft

T = np-a02 + visuelle Ordinale 0, Ei = np-a01 + Ordinale i+1.
Diese Kurzrollen dienen hier nur der Darstellung der gespeicherten
Quellenereignisse. Kein manueller Slot und kein alter Memoryzustand geladen.

| Geschichte | Formationen | Finales B4 / Fast / Audio-Slow / Visual-Slow |
| --- | ---: | --- |
| h01 | 2 | 2 / 2 / 0 / 0; T und E1 getrennte A-Slots, Fast jeweils Support 1 |
| h02 | 1 | 1 / 1 / 0 / 0; nur E1, T nie gebildet |
| h03 | 13 | 9 / 3 / 1 / 1; A nur Ei, beide Slow-Slots aus T mit Support 3 |
| h04 | 0 | 0 / 0 / 0 / 0; frischer Nullzustand |

Die drei Bildungsgeschichten und der Nullzustand sind getrennt initialisiert.
Identische leere Zustandsdigests duerfen im atomaren Beleg dieselbe
unveraenderliche Darstellung referenzieren; die Geschichten wurden nicht
fortsetzungsseitig zusammengelegt.

Vollstaendige Formationenspur, Fast-Slotnummern ohne gemeinsamen Praefix:

| Ereignis | Geschichte / Schritt | Quelle | Fast-Slot | Support / Konsolidierungen | PPB Audio und Video |
| --- | --- | --- | --- | --- | --- |
| e01 | h01 / 1 | T | 000 | 1 / 0 | NO_UPDATE |
| e02 | h01 / 2 | E1 | 001 | 1 / 0 | NO_UPDATE |
| e09 | h02 / 1 | E1 | 000 | 1 / 0 | NO_UPDATE |
| e16 | h03 / 1 | T | 000 | 1 / 0 | NO_UPDATE |
| e17 | h03 / 2 | T | 000 | 2 / 1 | CREATED, Support 1 |
| e18 | h03 / 3 | T | 000 | 2 / 2 | MATCHED, Support 2 |
| e19 | h03 / 4 | T | 000 | 2 / 3 | MATCHED, Support 3 |
| e20 | h03 / 5 | E1 | 001 | 1 / 0 | NO_UPDATE |
| e21 | h03 / 6 | E2 | 002 | 1 / 0 | NO_UPDATE |
| e22 | h03 / 7 | E3 | 000 | 1 / 0 | NO_UPDATE |
| e23 | h03 / 8 | E4 | 001 | 1 / 0 | NO_UPDATE |
| e24 | h03 / 9 | E5 | 002 | 1 / 0 | NO_UPDATE |
| e25 | h03 / 10 | E6 | 000 | 1 / 0 | NO_UPDATE |
| e26 | h03 / 11 | E7 | 001 | 1 / 0 | NO_UPDATE |
| e27 | h03 / 12 | E8 | 002 | 1 / 0 | NO_UPDATE |
| e28 | h03 / 13 | E9 | 000 | 1 / 0 | NO_UPDATE |

h03-B4 physisch: [E6,E7,E8,E9,E1,E2,E3,E4,E5], Formationsindizes
[10,11,12,13,5,6,7,8,9]. Fast physisch: [E9,E7,E8], letzte Schritte
[13,11,12]. T ist aus A vollstaendig verdraengt. Kein Ei erreicht eine
Konsolidierung; keine Vermischung oder weitere Slow-Generation entsteht.

Auditive Slow-Generation: e17, Slot
`ppb1.auditory.default-live-half.v2.slot.000`.
Die drei vollstaendigen Prototypdigests sind:

- CREATED: `e29376b1d10c5317760d1f50c601eef10c21403cf1e2db82944a1ed569945c28`
- MATCHED/s2: `04b5b8b9edcbbf884199e10acc752a72ec2fbc6d8f53a378661afb96c3fd17f7`
- MATCHED/s3: `22e240c84b924926b0e63b7c04c8d9a73b275588055ecdbdbb0c6359d646424f`

Visual-Slot `ppb1.visual.default-live.v1.slot.000` folgt derselben
Supportkette; sein voller Prototypdigest bleibt in den drei Uebergaengen
`46ee578128cfde13f300b2d03bcbd2df7a57d278174abb2d3a2a22c2c6d5855b`.
Alle Auswahl-, Update- und Slotbindungen stehen in der Verifikation.

## Alle 20 Hinweisentscheidungen

C = CONTIGUOUS_24, D = DISTRIBUTED_24. A/B nennen den oeffentlichen Bereich
der unangewandten Hypothese. NA = ABSTAIN_NO_APPLICABLE_CONTEXT;
NC = ABSTAIN_NO_CONTEXT. A/B sind jeweils ADMIT_SINGLE_CONTEXT.
Beide Direktbaselines stimmen mit ihrem Primaerarm ueberein.

| Ereignis | Geschichte | Quelle / Typ | C | D | Einordnung |
| --- | --- | --- | --- | --- | --- |
| e03 | h01 | a07 Exakt | A | A | richtig erhalten |
| e04 | h01 | a08 Pegel | A | A | richtig erhalten |
| e05 | h01 | a09 Frequenz | A | A | richtig erhalten |
| e06 | h01 | a10 Spektral | A | A | richtig erhalten |
| e07 | h01 | a11 Kontrolle | NA | NA | korrekte Enthaltung |
| e08 | h01 | a12 Kontrolle | A | NA | falsche Zulassung verhindert |
| e10 | h02 | a07 Exakt | NA | NA | Zielentfernung |
| e11 | h02 | a08 Pegel | NA | NA | Zielentfernung |
| e12 | h02 | a09 Frequenz | NA | NA | Zielentfernung |
| e13 | h02 | a10 Spektral | NA | NA | Zielentfernung |
| e14 | h02 | a11 Kontrolle | NA | NA | korrekte Enthaltung |
| e15 | h02 | a12 Kontrolle | NA | NA | korrekte Enthaltung |
| e29 | h03 | a07 Exakt | B | B | richtig erhalten |
| e30 | h03 | a08 Pegel | B | B | richtig erhalten |
| e31 | h03 | a09 Frequenz | B | B | richtig erhalten |
| e32 | h03 | a10 Spektral | B | B | richtig erhalten |
| e33 | h03 | a11 Kontrolle | NA | NA | korrekte Enthaltung |
| e34 | h03 | a12 Kontrolle | B | NA | falsche Zulassung verhindert |
| e35 | h04 | a07 Exakt | NC | NC | Nullzustand |
| e36 | h04 | a12 Kontrolle | NC | NC | Nullzustand |

Der Erfolg besteht **nicht** in neuen richtigen Hypothesen: davon gibt es
0. Beide Sichten liefern 8 richtige Hypothesen unter 20 Hinweisen.
Oeffentliche Fehlzulassungen sinken von **2/20 auf 0/20**, beziehungsweise
bei den sieben unabhaengigen Kontrollfaellen von **2/7 auf 0/7**.
Korrekte Enthaltungen steigen von 10/12 auf 12/12 in den Faellen, in denen
kein evaluativ richtiger Zielinhalt vorhanden ist. Interne und oeffentliche
Mehrdeutigkeiten: jeweils **0/20** in beiden Sichten.

## Erhaltung mit getrennten Nennern

N = berechtigte bekannte Faelle mit Ziel, D = bisher richtig eindeutig,
R = richtig im selben Bereich erhalten, L = verloren. Beziehungstabellen
zaehlen dagegen einzelne Zielslotbeziehungen. Keine Vermengung beider Nenner.

| Oeffentliche Erhaltung | Rezeptorvariation je Sicht | N | D | R | L | neue richtige Abrufe |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A / Exakt | false / false | 1 | 1 | 1 | 0 | 0 |
| A / Pegel | true / true | 1 | 1 | 1 | 0 | 0 |
| A / Frequenz | true / true | 1 | 1 | 1 | 0 | 0 |
| A / Spektral | true / true | 1 | 1 | 1 | 0 | 0 |
| B / Exakt | false / false | 1 | 1 | 1 | 0 | 0 |
| B / Pegel | true / true | 1 | 1 | 1 | 0 | 0 |
| B / Frequenz | true / true | 1 | 1 | 1 | 0 | 0 |
| B / Spektral | true / true | 1 | 1 | 1 | 0 | 0 |

A insgesamt **4/4/4/0**, davon Varianten **3/3/3/0**. B separat ebenfalls
**4/4/4/0**, davon Varianten **3/3/3/0**. In beiden Geschichten ist
tatsaechliche A-Konkurrenz gespeichert. Diese wurde vollstaendig gescannt,
ohne einen automatischen Vorrang fuer B.

Beziehungserhaltung: B4 in h01 **4/4/4/0**, Fast in h01 separat
**4/4/4/0**, Audio-Slow in h03 **4/4/4/0**. Je Bank entfallen 1/1/1/0 auf
Exakt und 3/3/3/0 auf die drei Varianten. **Keine verlorene Zielbeziehung,
kein verworfener richtiger Zielkandidat und kein richtiger Abrufverlust.**
Die doppelten B4-/Fast-Beziehungen sind keine acht oeffentlichen A-Abrufe.

Alle uebrigen bank-/geschichtsbezogenen Erhaltungsnenner mit D=0 bleiben
**ERHALTUNG_NICHT_GEPRUEFT**, insbesondere A nach Zielverdraengung in h03,
B ohne stabile Spur in h01/h02 sowie h02/h04 insgesamt. Die vier
Zielentfernungsfaelle h02 und der bekannte Nullzustandsfall h04 bleiben
ausdruecklich als fuenf Faelle ohne Ziel im Bericht, nicht als Erhaltungserfolge.

Falsche Slotanwendbarkeit: **3/102 -> 0/102** Nichtzielbeziehungen.
Konkret e08: je eine falsche B4- und Fast-Beziehung zu np-a02;
e34: eine falsche Slow-Beziehung zu np-a02. Dies sind **drei Beziehungen,
aber nur zwei oeffentliche Fehlzulassungen**. Keine neue falsche Beziehung.
Gewinne verrechnen keine Verluste; die zwei verhinderten Fehlzulassungen
werden nicht als neue richtige Hypothesen gezaehlt.

## Rezeptorvariation und Drift

Die Exaktfaelle e03 und e29 sind gegen ihre gebundenen urspruenglichen
Formationseingaenge in beiden Sichten unveraendert. Bei e29 ist die
Cue-/Kandidatenabweichung trotzdem true/true: der auditive PPB-Prototyp
wurde gerundet fortgeschrieben. Dies zaehlt **nicht** als Rezeptorvariation.
Pegel-, Frequenz- und Spektralhinweise in h01/h03 sind dagegen in beiden
Sichten tatsaechlich variiert, belegt durch die Formationseingangswerte.

Zehn andere Hinweise in h01/h02/h03 sowie die zwei Nullzustandshinweise
haben mangels eindeutiger vorheriger Zielreferenz der jeweiligen Geschichte
`null/null`, Status MISSING_REFERENCE. Keine Ersatzreferenz aus anderer
Geschichte, Prototyp, Digestrekonstruktion oder Quellenlabel.

## Fachlicher Befund und Grenzen

Das vorgebundene Kriterium eines **begrenzten Transfervorteils** ist erfuellt:
weniger Fehlzulassungen, kein gepruefter Beziehungs-/Abrufverlust, keine
neue Fehlzulassung und positive echte Varianten-Erhaltungsnenner getrennt
fuer A und B. Das verbessert auf diesen Quellen die Abrufselektivitaet,
nicht die Lernregel, Kapazitaet oder Objekt-/Klangidentitaetserkennung.

Der NP-Korpus ist bereits untersucht, kein unberuehrter Bestaetigungskorpus.
Die gleiche Kontrollquelle a12 liefert die beiden verhinderten Fehler in
unterschiedlichen Memorygeschichten; das sind nicht zwei unabhaengige
neue Kontrollquellen. Allgemeine Verlustfreiheit und offene Bekanntheits-
erkennung sind nicht nachgewiesen. Beide Direktbaselines erklaeren den Effekt.

Offline wurden Quellen-, Profil-, Zeit-, NJ-Projektions- und gespeicherte
Wertebindungen sowie Memory-/Scanrelationen geprueft. Die Verifikation
rekonstruiert weder urspruengliche Rohspektren aus Halbwerten noch den
nativen TSPM-Receipt numerisch. Diese historische Offline-Grenze bleibt
ausdruecklich bestehen. Keine Aussage universeller Gleitkommagleichheit;
S2-NM bleibt unveraenderte Halbprofilgrenze.

## Artefaktbindungen

- Recorddigest: `ae567c707c833a71f871d9ee7fdffc9b5723e92190b3089b6dd1326d35d2707e`
- Verifikationsdigest: `309e849ccff7563b82d6c678375686f62f468e7cec87d8416716e19e0c4311c2`
- Reportdigest: `52ebe3919ebd133f0e6dce6cfb2d0132cb9d900685d2742407a3a733d82c5164`
- SHA-256 recording.json: `9f5a228e0360e70ed09efe02f6aac8cf8c0d3088973b11cc5b2be4eda0d37f37`
- SHA-256 verification.json: `687d415373cdbb72ea927ac72c74cf7fc1d2101fed6899e2e48aedf036570889`
- SHA-256 evaluation.json: `a4f15b3cf1f90bf26b7d63ea752e86929f133780ecfbb3e160bcb6cfc0918ad0`

Die Einmalbindung und der Abschlussbeleg liegen im uebergeordneten
Verzeichnis unter der Lauf-ID mit `.authorization.json` beziehungsweise
`.completion.json`. Sie binden Aufrufdatei, Qualifikation, Interpreter,
Quellhashes, Budgets und Aufrufzaehler 1/1/1. Keine erneuten Distanzen,
Abrufe oder Auswertungsaufrufe fuer diesen lesend zusammengestellten Bericht.
Historische Belege, fremde Aenderungen und Bootstrap blieben unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenbewertung dieses begrenzten
Transferbefunds und seiner getrennten A-/B-Erhaltung weiter. Eine etwaige
Runtime-Anbindung der verteilten Sicht benoetigt einen eigenen Auftrag;
dieser Lauf autorisiert keine Produktumstellung oder Wiederholung.
