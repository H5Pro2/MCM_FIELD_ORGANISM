# S2-NR: einmaliger realer Masken-Runtimevergleich

## Getrennter Abschluss

Lauf-ID: `s2nr-mask-runtime-transfer-20260908-01`.
Unveraenderter qualifizierter Quellenstand: Commit `57c93b95`.

**Technik: RECORDING_COMPLETE**, unabhaengige read-only Verifikation bestanden.
**Funktion: negativer Transferbefund.** Die vorgebundene Forderung nach
Erhaltung richtiger Abrufe ohne neue Fehlzulassung ist in diesem Strom
widerlegt. Der getrennte Auswerter meldet regulaer `EVALUATED`, nicht
`NOT_EVALUABLE`. Sein gespeicherter Status wird nicht umgeschrieben.

Die zusammenhaengende Sicht erfuellt 4/4 Vorhersagen, die verteilte 1/4.
Die verteilte Sicht gewinnt keinen richtigen Abruf, verliert zwei richtige
Abrufe und erzeugt eine neue Fehlzulassung. Das ist kein technischer Fehler
und kein Anlass fuer einen Retry, eine Masken- oder Quellenanpassung.

## Einmaligkeit und Quellenbindung

Genau ein `run_main_once`-Aufruf, danach genau ein `verify_file_once` und erst
nach dessen Bestehen genau ein `evaluate_file_once`, jeweils Exit-Code 0.
Keine vorgeschalteten Tests oder Rezeptorvorlaeufe. Die Ergebnisdestination
existierte vor dem Hauptaufruf nicht. Die Freigabe steht separat in
`reports/s2nr/NR_HAUPTLAUF_20260908_01_BINDUNG.md`.

Der Haupteinstieg pruefte vor Materialisierung den vollstaendigen
Qualifikationsverbund, den neuen Anschlussbeleg, die historischen Quellenpins
sowie Generator-, Umgebungs- und Profilbindungen. Die versiegelte Folge blieb
unveraendert. Payloadhashes wurden vor der jeweiligen Verarbeitung geprueft;
Rohpayloads wurden nicht abgelegt. Keine nachtraegliche Quellenauswahl.

Das prozesslokale Hauptgate wurde ausschliesslich fuer diesen Aufruf geoeffnet.
Nach `finally` waren Run-, NR-Kompositions-, NN- und NG-Hauptgate `False`.
Beide Runtimes endeten `CLOSED`, jeweils nach 18 Ereignissen, mit
`next_ordinal=19`. Keine Hypothesenanwendung.

## Technischer Umfang

| Messung | Beobachtet |
| --- | ---: |
| Gemeinsame Audiofenster | 18 |
| Fortlaufende Audiohops | 180 |
| Rollende Audioabschluesse | 171 |
| Einmalige NJ-Endpunktprojektionen | 18 |
| Visuelle Analysen | 14 |
| Runtimeereignisse je Arm | 18 |
| Formationen je Arm | 14 |
| Feldkontakte beider Arme | 9792 |
| Abrufbelege einschliesslich Direktbaselines | 16 |
| Offline gepruefte Formationsrelationen | 28 |
| Offline Zustandsdekodierungen | 15 |
| Offline protokollierte Wertevergleiche | 3264 |

Beide Arme erhielten dieselben unveraenderlichen Materialisate, aber getrennte
Runtime-, Feld-, Memory- und Ownerinstanzen. Verifikation:
`baseline_equal=true`, `sibling_states_equal=true`, `read_only=true`.
Alle Hinweise liessen Memory unveraendert; Formationen waren schreibend.
Die Feldkontakte bestanden unabhaengig davon fort. Native Modalitaetsfenster
und explizite NR-Felduhr wurden verifiziert.

Enddigest Feld, beide Arme:
`d996ee7ee2e17a8e492a147c0f2eaefe4b34a7468d1f935004c9ea1e5c8bb612`.
Enddigest Memory, beide Arme:
`4f6f57b8e88f4638ea323812d5903b68a8ac668cbc63863bff410081b5c08678`.
Die maskengebundenen Runtimegesamtdigests sind erwartungsgemaess verschieden.

`recording.json`: **865318 Byte**, unveraenderte Obergrenze **4194304 Byte**.
`verification.json`: 5425 Byte; `evaluation.json`: 57082 Byte.
Scan- und Verifikationsbudgets bleiben getrennt im Gesamtbeleg gebunden;
es erfolgte keine Grenzerhoehung.

## Tatsaechliche Speicherbildung

Beide Arme bilden dieselbe Geschichte:

- e01: Konkurrenzquelle `nr-a02` in B4 und Fast, noch kein Slow-Prototyp.
- e03: Ziel `nr-a01` in eigenem Fast-Slot 001 neben Konkurrent Slot 000.
- e05: Zielkonsolidierung erzeugt je einen auditiven und visuellen PPB-Slot 000,
  Support 1, Generation e05.
- e06/e07: beide Slots `MATCHED`, Support 2/3.
- e08 bis e16: neun Druckformationen, keine weiteren PPB-Updates und keine
  Vermischung des Zielprototyps. Fast legt neue Druckslots mit Support 1 an;
  Zielslot 001 wird bei e10 ersetzt.
- Nach e16: neun B4- und drei Fast-Slots ausschliesslich mit Audioherkunft
  `nr-a02`; Ziel vollstaendig aus A verdrangt. Beide Slow-Slots bleiben stabil
  mit Support 3 und reiner Herkunft `nr-a01` beziehungsweise `nr-v01`.

Die vollstaendigen Inventare und Slot-Uebergaenge stehen in
`evaluation.json/formations`, numerische Zustaende und Receipts im Gesamtbeleg.
Keine Sollsupports oder gewuenschten Inventare wurden als Startgate benutzt.

PPB-Prototypdigests getrennt von Rezeptorvariation:

| Ereignis | Auditiv | Visuell |
| --- | --- | --- |
| e05 / CREATED | `638c625ac47444b011a8cb965a358e9ca9caac7df3018a06b8d3bb4607360351` | `5fbb335eac83d329feaa15c5c4430f1621e540ee1a920097be51988f1ed7aed2` |
| e06 / MATCHED | `fc01d27ae56222fac9628ce42f15ee6b7b31a1da1083dc23169a8951956db0ea` | `5fbb335eac83d329feaa15c5c4430f1621e540ee1a920097be51988f1ed7aed2` |
| e07 / MATCHED | `8d671f8870feebd085d063b57dca93a0d51722ba2fa7a1fa50b868bbc76ebd55` | `5fbb335eac83d329feaa15c5c4430f1621e540ee1a920097be51988f1ed7aed2` |

Die auditive PPB-Fortschreibung aendert somit den gespeicherten Prototyp.
Diese Aenderung wird nicht als neue Rezeptorvariation gerechnet. Die
Variationsmerkmale unten stammen aus den gebundenen Formationseingaengen.
Eine zusaetzliche numerische Zerlegung von Variantenabstand und PPB-Drift
wurde nicht ausgefuehrt.

## Alle vier Hinweise

C = CONTIGUOUS_24; D = DISTRIBUTED_24. Beide verwenden A-Maximum <=0.1
und Slow `sum(terms)/24 <=0.01`, unveraendert. Trefferzahlen sind B4/Fast/Slow
fuer die auditive Bank; es gibt keine visuellen Hinweise in diesem Strom.

| Ereignis | C-Treffer | D-Treffer | C-Entscheidung | D-Entscheidung |
| --- | --- | --- | --- | --- |
| e02 / Exaktkontrolle vor Zielbildung | 0/0/0 | 1/1/0 | `ABSTAIN_NO_APPLICABLE_CONTEXT` | `ADMIT_SINGLE_CONTEXT`, falsches A aus nr-a02 |
| e04 / fruehe Pegelvariante | 1/1/0 | 2/2/0 | richtiges `A_RECENT` aus nr-a01 | `ABSTAIN_INTERNAL_AMBIGUITY` |
| e17 / spaete Frequenzvariante | 0/0/1 | 9/3/1 | richtiges `B_STABLE_AUDITORY` aus nr-a01 | `ABSTAIN_INTERNAL_AMBIGUITY` |
| e18 / unabhaengige Kontrolle | 0/0/0 | 9/3/1 | `ABSTAIN_NO_APPLICABLE_CONTEXT` | `ABSTAIN_INTERNAL_AMBIGUITY` |

e02: Der Zielinhalt wurde noch nicht erfahren. D laesst den Konkurrenten
faelschlich zu; seine B4-/Fast-Belege ergeben einen oeffentlichen A-Kandidaten.
e04/e17: Die Zielbeziehungen bleiben in D erhalten, zusaetzliche
Konkurrententreffer erzwingen jedoch Enthaltung. Es geht keine Erinnerung
verloren, wohl aber die zuvor richtige eindeutige Abrufentscheidung.
e18: Beide Arme enthalten sich; D trifft auch den stabilen Zielslot, wird
aber bereits durch A-interne Mehrdeutigkeit blockiert. Das ist keine
nachgewiesene Erkennung von Unbekanntheit und begruendet keinen B-Vorrang.

## Erhaltung, Verlust und Fehlzulassung

Oeffentliche richtige Abrufe, getrennt nach dem vorgesehenen Bereich:

| Gruppe, jeweils unter Konkurrenz | N | D | R | L |
| --- | ---: | ---: | ---: | ---: |
| Fruehe A-Pegelvariante e04 | 1 | 1 | 0 | 1 |
| Spaete B-Frequenzvariante e17 | 1 | 1 | 0 | 1 |

Beide Verluste betreffen tatsaechliche sichtbare Rezeptorvariation in beiden
Sichten (`true/true`). Cue-/Kandidatenabweichung ist ebenfalls `true/true`,
aber ein getrenntes Merkmal. Bei e02 fehlt eine vorherige Zielformation,
bei e18 fehlt die Zielreferenz: jeweils `null/null`, nicht `False`.

Die uebrigen, im Auswerter getrennt erhaltenen Bereichs-/Kontrollgruppen mit
D=0 bleiben **ERHALTUNG_NICHT_GEPRUEFT**. Exaktkontrollen liefern hier keinen
positiven Erhaltungsnenner; sie pruefen Zielabwesenheit.

Ziel-Beziehungserhaltung ist etwas anderes als richtige Eindeutigkeit:

| Zielbeziehung | N | D | R | L |
| --- | ---: | ---: | ---: | ---: |
| e04 B4 | 1 | 1 | 1 | 0 |
| e04 Fast | 1 | 1 | 1 | 0 |
| e17 Slow | 1 | 1 | 1 | 0 |

Keine verworfenen Zielkandidaten (0/3 geprueften Zielbeziehungen).
Keine Gewinne (0/2 bekannte Hinweise), zwei verlorene richtige Abrufe (2/2).
Gewinne und Verluste werden nicht verrechnet.

| Gesamtergebnis | C | D |
| --- | ---: | ---: |
| Richtige Hypothesen / bekannte Hinweise | 2/2 | 0/2 |
| Fehlzulassungen / alle Hinweise | 0/4 | 1/4 |
| Fehlzulassungen / Zielabwesenheitskontrollen | 0/2 | 1/2 |
| Erfuellte Vorhersagen | 4/4 | 1/4 |
| Mehrdeutigkeitsentscheidungen | 0/4 | 3/4 |
| Enthaltungen insgesamt | 2/4 | 3/4 |
| Enthaltungen auf Zielabwesenheitskontrollen | 2/2 | 1/2 |

Die Fehlzulassung ist e02, beide Abrufverluste sind e04 und e17. Mehr
Enthaltungen sind hier kein Gewinn: Zwei davon ersetzen richtige Abrufe.

## Integritaet und Aussagegrenze

- Aufzeichnungsdigest: `64b222f2eff36c603f60e5fa12a0d49d6c65e6d5e1073603721362a45fe9182a`
- Aufzeichnungsdatei-SHA-256: `26819e869538e91b024915208e7dcb1e20316e2c4c7d6b31920b50698b406275`
- Verifikationsreportdigest: `1ec2bfc43956425919a520b92f2caa69ffefbac334512b98e9bfa418b99765ef`
- Auswertungsdigest: `938a171b0aff54c5ab164a25b1c5c35fed4828700f96f7043f9566dd750f0fcc`

Die einmalige Verifikation bestaetigt die unveraenderte Aufzeichnungsdatei.
Sie prueft gerundete NJ-Projektionswerte, Kontakt-, Scan- und Zustandsrelationen
sowie Herkunftsdigestbindungen. Ungespeicherte Rohspektren werden nicht aus
halbierten Werten rekonstruiert; ein unabhaengiges numerisches Nachrechnen
der urspruenglichen NJ-Halbierung ist offline damit nicht behauptet.
Die bekannte S2-NM-Subnormalgrenze des getrennten Halbprofils bleibt bestehen.

Dieser neue, vor Rezeptoranalyse versiegelte Strom widerlegt den erwarteten
verlustfreien Maskentransfer fuer seine vier Hinweise. Er widerlegt weder die
technische Runtimequalifikation noch die frueheren begrenzten NP-/NQ-Befunde.
Die Memorybildung funktioniert; der untersuchte Sichtwechsel fuehrt hier zu
schlechterer Selektivitaet. Die Direktbaselines reproduzieren den Effekt.
Keine allgemeine Aussage ueber natuerliche akustische Identitaet, keine
Produktumstellung und keine nachtraegliche Wahl einer besseren Maske.

Historische Belege, Versiegelung, Produktcode, fremde Aenderungen und Bootstrap
bleiben unveraendert. Keine Wiederholung oder weitere Messung ausgefuehrt.

**WEITER:** Am besten geht es jetzt mit der Analystenbewertung dieses negativen
Transfers und seiner Abgrenzung zu NP/NQ weiter, ohne erneuten NR-Lauf oder
nachtraegliche Maskenoptimierung.
