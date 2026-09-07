# S2-NO: begrenzter read-only Gegenvergleich e25 / e27

Stand: 2026-09-07. Ausschliesslich lesende Gegenueberstellung des bestehenden
Laufs `s2no-half-runtime-20260907-01`, keine neue Laufnummer oder Messung.
S2-NO bleibt unveraendert ein technisch gueltiger, **gemischter** Funktionsbefund.
Keine Wiedereroeffnung des historischen NH-Abbruchs.

## Grundlage und Grenze

Gelesen wurden `recording.json`, `evaluation.json`, `verification.json` und
`BEFUND.md` im Verzeichnis `reports/s2no/s2no-half-runtime-20260907-01/`.
Die Scanbelege stehen unter `comparison.scans`, selektiert nach `ordinal`
25/27, `arm` 0/1 und `role` PRIMARY bzw. DIRECT_BASELINE; der Abrufbeleg ist
jeweils `value.evidence`. Herkunft: vorhandene `formation_inventories`,
`final_lineages` und `source_receipts`. Die Implementierung wurde nur gelesen.

Gespeicherte Identitaeten, hier nicht erneut verifiziert:

- Gesamtbelegdigest: `c4095c283efa12cdfb28f650c625f1850e2ae619946f2d7bbdbfd097b0a30aad`.
- Recording-Dateihash laut vorhandener Verifikation:
  `f55d0273189a57d5111fe521fe3dd932bb759134be999a3aa22ba259613d39c5`.
- Auswertungsdigest: `be8ec235d881b4e7ce4953f690984bac7d86f802f7e697b0a21ba18e9f99fa18`.
- Gemeinsamer Memory-Pre-/Postdigest beider Hinweise und Arme:
  `552c5ce2e458ee6e4c02e574721c8fbaf73c874ebc1af15c29d3e366fc44c0d9`.

Keine Distanz, Banddifferenz oder neue Statistik wurde berechnet. Keine
48-Band-Erweiterung, Rezeptor-, Abruf-, Verifikator-, Test- oder Runtimeausfuehrung.
Alle Zahlen unten sind vorhandene Scanstatistiken, nicht neue Nachrechnungen.
Die gespeicherte Verifikation meldet Direktbaselinegleichheit und Read-only;
dieser Bericht ersetzt oder wiederholt diese Verifikation nicht.

## Hinweise und Rollen

| Ereignis | Technische Audioquelle | Einordnung ausschliesslich im Auswerter |
| --- | --- | --- |
| e25 | nh-a14 | Frequenzvariante des Inhalts B / p01 |
| e27 | nh-a12 | unbekannter Inhalt, ohne eigenes gespeichertes Ziel |

Beide sind `PARTIAL_AUDITORY_CUE`, ohne visuellen Quellenbeleg. Die Cue-Digests
lauten `36a38593f0036caa4985e0c4b24c0924988f535d97181dcbaef41de76a405f06`
(e25) und `48b653324c0ebf95fd766b70ab974a8830e35201882851db7d712e943f3c9f88`
(e27). Unterschiedliche Quellen-/Cueidentitaeten sind keine Kennzeichnung
von Bekanntheit. Der Auswerter kennt fuer e25 einen Zielkandidaten, fuer e27
keinen; dieses Wissen steht der rangfreien Abrufentscheidung nicht zur Verfuegung.

## Konkrete A-Kandidaten und gespeicherte Statistiken

H = historisches `sum(terms)/24`, K = groesste absolute Banddifferenz unter
`ALL_BANDS_24`. Beide verwenden nur Bandindizes 0..23 und die A-Grenze 0.1.
`observed_distance` bezeichnet bei K also ein Maximum, keinen Mittelwert.
Alle neun B4-Eintraege sind belegt. H trifft jeden Eintrag bei beiden Hinweisen.
Die letzte Spalte gilt fuer K bei **beiden** Hinweisen.

| B4-Slot | Herkunft: Quelle / Ereignis / Formationsindex | H e25 | H e27 | K e25 | K e27 | K trifft |
| --- | --- | --- | --- | --- | --- | --- |
| 000 | nh-a10 / e21 / 19 | 0.02371742337525321 | 0.023717450976276592 | 0.39343542984250435 | 0.39343544650153434 | nein |
| 001 | nh-a11 / e22 / 20 | 4.385375417638931E-07 | 4.6613856514780614E-07 | 6.071668602726218E-06 | 6.2010102325378425E-06 | ja |
| 002 | nh-a03 / e14 / 12 | 0.02768659397739961 | 0.027686621578422995 | 0.2900186402318249 | 0.2900186478444209 | nein |
| 003 | nh-a04 / e15 / 13 | 0.02582442375405192 | 0.02582445135507531 | 0.3318772775231127 | 0.33187728739784766 | nein |
| 004 | nh-a05 / e16 / 14 | 1.2911917714503378E-08 | 4.051294109841648E-08 | 1.4864103754871992E-07 | 2.779826673603447E-07 | ja |
| 005 | nh-a06 / e17 / 15 | 3.504810211761401E-08 | 6.264912550152711E-08 | 2.1891727889736804E-07 | 3.482589087089928E-07 | ja |
| 006 | nh-a07 / e18 / 16 | 0.02348945508583716 | 0.023489482686860547 | 0.4289670582679445 | 0.4289670749269745 | nein |
| 007 | nh-a08 / e19 / 17 | 1.0229253526844294E-08 | 2.0255558344050083E-08 | 3.460546184377533E-08 | 1.639470916554001E-07 | ja |
| 008 | nh-a09 / e20 / 18 | 7.66649471734715E-08 | 1.042659705573846E-07 | 3.605293349718264E-07 | 4.898709647834512E-07 | ja |

Die drei Fast-Slots haben jeweils Support 1 und reine Herkunft aus genau der
genannten Druckquelle. Ihre vier gespeicherten Statistiken sind jeweils
identisch mit der angegebenen B4-Zeile:

| Fast-Slot | Herkunft | Statistikzeile oben | H trifft e25/e27 | K trifft e25/e27 |
| --- | --- | --- | --- | --- |
| 000 | p10 / nh-a10 / e21 | B4-000 | ja / ja | nein / nein |
| 001 | p11 / nh-a11 / e22 | B4-001 | ja / ja | ja / ja |
| 002 | p09 / nh-a09 / e20 | B4-008 | ja / ja | ja / ja |

Dies ist eine kompakte Tabellenreferenz, keine Deduplication im Abruf.
B4 und Fast bleiben getrennte interne Scans. Die Historie weist final
ausschliesslich p03..p11 in B4 und p10/p11/p09 in Fast aus, nicht p01.
Es gibt keine durch diese Druckformationen mitaktualisierte Slow-Herkunft.

## Derselbe auditive B-Slot 001

Vollstaendige Slot-ID: `ppb1.auditory.default-live-half.v2.slot.001`.
Support 3; reine p01-Herkunft: e07 CREATED(1), e10 MATCHED(2),
e13 MATCHED(3). Derselbe bereits gebildete Prototyp liegt beiden Hinweisen vor.

| Vorhandener Slow-Scanwert | e25 | e27 |
| --- | --- | --- |
| Historisches Mittel ueber 24 beobachtete Baender | 1.265757144409128E-08 | 4.025859482800438E-08 |
| Unveraenderte Slow-Grenze | 0.01 | 0.01 |
| Beobachteter Treffer | true | true |
| eligible / stable_support / observed_comparison_count | true / 3 / 24 | true / 3 / 24 |
| distance_terms_digest | 570c5fd09187499fb289d6710c7b9084aaadd4dba61741b36ff7ca99ddde37f2 | 8582e711fbda299d1a7bda11e8176faa7de4172fd26889a73a876245c5c86739 |

Diese Slow-Statistik ist in beiden Regelarmen gleich; auch der alternative
Arm wendet **kein** Bandmaximum auf Slow an. Slotdigest:
`e736797fa2c562ab28e0e1f2efc627dac3681d6215f5117eec175094197c7a8f`;
Kandidatenwertdigest:
`bd345a2f0eeb38ee93d0a0f0a45888df72d417784b4215814597781f5c7a8817`.

Der andere stabile auditive Slot 000 trifft keinen der beiden Hinweise:
gespeichert sind 0.021664078231643232 (e25) und 0.02166410583266662 (e27)
gegen 0.01. Slot 002 ist instabil, 003..007 sind frei; deren fehlende
Scanstatistiken sind **keine Nullabstaende**.

**Fehlende Evidenz:** Die 24 einzelnen numerischen Differenzen gegen Slot 001
sind nicht als Bandtabelle gespeichert, sondern nur durch
`distance_terms_digest` gebunden. Der Scanrecord enthaelt kein Array dieser
Terme. Auch Bandindex/Maximum der groessten Slow-Abweichung fehlen.
Die verschiedenen Digests ersetzen diese Werte nicht. Die A-Maxima oben
benennen ebenfalls keinen verursachenden Bandindex. Eine Rekonstruktion aus
Kandidaten- und Cuewerten waere eine neue Differenzberechnung und unterblieb.

## Welche Mehrdeutigkeit liegt vor?

Die folgenden gespeicherten Befunde gelten fuer e25 und e27 sowie die
jeweiligen Direktbaselines:

| Befund | Historischer Arm | ALL_BANDS_24 |
| --- | --- | --- |
| B4-Treffer | 9 | 5 |
| Fast-Treffer | 3 | 2 |
| Slow-Treffer | 1, Slot 001 | 1, Slot 001 |
| A-Status | A_RECENT_INTERNAL_AMBIGUITY | A_RECENT_INTERNAL_AMBIGUITY |
| Oeffentliche A-Kandidaten | 0 | 0 |
| B-Status | B_STABLE_AUDITORY_APPLICABLE | B_STABLE_AUDITORY_APPLICABLE |
| Oeffentliche B-Kandidaten | 1 | 1 |
| Gesamtentscheidung | ABSTAIN_INTERNAL_AMBIGUITY | ABSTAIN_INTERNAL_AMBIGUITY |
| Endhypothese | null | null |

Die interne A-Mehrdeutigkeit ist in **beiden A-Banken** bereits vorhanden.
`_resolve_a` erzeugt deshalb keinen oeffentlichen A-Kandidaten; eine
B4-/Fast-Vollvektorgleichheitspruefung wird hier nicht erreicht
(`internal_equality_comparison_count = 0`). Dies ist kein nachgewiesener
paarweiser `A_RECENT_INTERNAL_CONFLICT`.

Es liegt **keine zusaetzlich aufgezeichnete oeffentliche A/B-Mehrdeutigkeit**
mit zwei Bereichskandidaten vor: `public_candidate_count` ist 1, nicht 2.
Dennoch existieren gleichzeitig interne A-Treffer und ein gueltiger B-Befund.
`_decide` enthaelt sich bereits wegen der internen Mehrdeutigkeit. B wurde
vollstaendig gescannt und nicht durch einen vorzeitigen Scanabbruch verdeckt.

## Zugaengliche Evidenz und Schluss

Dem bestehenden Abrufpfad zugaenglich sind die 24 beobachteten Cuewerte,
entsprechende Kandidatenwerte, ihre daraus im urspruenglichen Lauf gebildeten
Terme/Statistiken, Bankzugehoerigkeit, Stabilitaet sowie technische Quellen-,
Zeit-, Profil- und Slotbindungen. Die restlichen Kandidatenwerte dienen der
bestehenden Kandidatengleichheit, nicht dem Zugriff auf verdeckte Cuewerte.
Die zugelassenen Regeln bilden Treffer und Kardinalitaeten, keine Rangfolge.

Die vorhandenen Zahlen sind **nicht identisch**: e25 hat zum B-Prototyp einen
kleineren gespeicherten Mittelabstand als e27. Damit ist numerischer
Unterschied in beobachteter Evidenz belegt, nicht deren semantische Identitaet.
Beide Hinweise liegen zugleich innerhalb derselben gebundenen Radien und
erzeugen identische Treffermengen. Die kleinen positiven Werte werden nicht
als exakte Gleichheit behandelt.

Die Herkunft der gespeicherten Slots ist fuer die Auswertung nachvollziehbar;
sie belegt aber nicht, dass ein neuer Cue diese Herkunft teilt. Die Rollen
"bekannte Frequenzvariante" und "unbekannt" sind kein Eingang der
Abrufentscheidung. Eine Auswahl ueber diese Rollen, die Quellen-ID oder
verdeckte Cuewerte waere kein Wahrnehmungsnachweis.

**Antwort:** Es gibt beobachtbare numerische Unterschiede, aber aus diesen
vorhandenen zwei Faellen keinen belegten, zielwissensfreien Ansatz fuer eine
zuverlaessige bekannte/unbekannte Unterscheidung. Die bestehende Anwendbarkeit
unterscheidet sie nicht. Insbesondere waere die Zulassung desselben B-Slots
bei beiden Hinweisen fuer e27 falsch; dessen Enthaltung bleibt notwendig.
Weder eine auf diese Zahlen zugeschnittene Grenze noch B-Vorrang oder eine
neue Rangregel wird daraus vorgeschlagen. Die fehlende Einzelbandtabelle
begrenzt zusaetzlich jede Aussage ueber die spektrale Ursache des Unterschieds.

S2-NO wird unveraendert geschlossen. Der teilweise untersuchte Korpus,
die S2-NM-Profilabweichung und die eingeschraenkte Offline-Nachpruefbarkeit
bleiben Grenzen des Ursprungsbefunds. Keine neue Normalform-, Erhaltungs-
oder Generalisierungsaussage entsteht durch diese Lesearbeit.

Produktcode, Quellen und historische Belege wurden nicht geaendert. Kein
Gate wurde geoeffnet; die beteiligten Hauptgates bleiben `False`.
Fremde Aenderungen und Bootstrap bleiben ausgeschlossen. Dieser neue Bericht
ist das einzige eigene Aenderungsartefakt.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung ueber die
Aussagegrenze dieser vorhandenen 24-Band-Evidenz weiter, nicht mit einer
auf e25/e27 zugeschnittenen Abrufregel.
