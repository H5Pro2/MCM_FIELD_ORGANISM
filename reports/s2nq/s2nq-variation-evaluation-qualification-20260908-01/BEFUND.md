# S2-NQ: Rezeptorvariation getrennt von Kandidatenabweichung

## Ausfuehrungsbefund

- Lauf-ID: `s2nq-variation-evaluation-qualification-20260908-01`.
- Status: `S2NQ_VARIATION_EVALUATION_QUALIFIED`.
- Genau ein fokussierter neutraler Testaufruf, **8/8**, Exit-Code **0**.
- Unittest-Zeit: 0,649 Sekunden; keine Wiederholung.
- Einstieg: `C:/Python314/python.exe -m reports.s2nq.qualify_variation_once`.
- Gebundener Testprozess: `C:/Python314/python.exe -m unittest tests.test_s2nq_private_variation_evaluation -v -f`.
- 14 Auswerteraufrufe mit rein synthetischen Belegformen.
- Groesste kanonische Auswertung: **8.029 Byte**, Grenze unveraendert
  4.194.304 Byte. Dies ist keine neue Vollumfangsmessung des Hauptlaufs.
- Inventar, Budgets und Quellhashes wurden vor dem Testprozess in
  `preregistration.json` gebunden. Alle Vor-/Nachhashes sind identisch.
- `MAIN_GATE` blieb `False`.

## Korrektur und neutrale Beobachtung

Nur der Auswerter wurde produktseitig veraendert. N/D/R/L-Gruppen verwenden
jetzt `receptor_variation`: Cuewerte werden auf denselben Originalindizes
mit gespeicherten urspruenglichen Halbprofil-Formationswerten verglichen.
Der Quellen-/Ereignis-/Projektionsbezug wird geprueft. Quellen-IDs dienen
nur der Referenzsuche in bereits vorliegenden Formationen derselben Geschichte;
ein Quellen- oder Variantenlabel bestimmt nicht das numerische Ergebnis.

Die fruehere Cue-/Slotabweichung bleibt als `cue_candidate_deviation`
separat sichtbar. Ein fest synthetisch gebundener benachbarter
Binary64-Prototyp fuehrte im Test zu `[true, true]` Kandidatenabweichung,
waehrend der Exaktcue `[false, false]` Rezeptorvariation erhielt.
Es wurde dafuer kein neuer PPB-Update ausgefuehrt.

Die sichtbare Aenderung an Index 0 ergibt Variation in beiden Sichten.
Index 1 betrifft nur `CONTIGUOUS_24`, Index 47 nur `DISTRIBUTED_24`.
Fehlende, ungueltige oder mehrdeutige Formationsreferenzen ergeben je Sicht
`null` mit explizitem Status. Unterschiede nur ausserhalb einer Sicht
machen deren Referenz nicht mehrdeutig. Keine Ersatzbildung oder Toleranz.

Die synthetische Folge aus Erhaltung, Verlust und Gewinn ergibt getrennt
`N=3, D=2, R=1, L=1, gains=1`. Das gilt fuer die gepruefte oeffentliche
Erhaltung und die Slow-Beziehungsgruppe. Fehlende Referenzwerte aendern
diese Nenner und gespeicherten Entscheidungen nicht. Ein leerer Nenner
bleibt `ERHALTUNG_NICHT_GEPRUEFT`.

## Bindungsbelege

Ergebnisdigest:
`a7c9e4895ff09867dbbbb6367962238914af50de4e9656fefe8db3232be45525`

SHA-256 des korrigierten Auswerters:
`1f67ef8e55c33399fe5e3e5efab39ee63d6cf86dc5560d8d4d1d0d5c130214b1`

SHA-256 der fokussierten Testdatei:
`b594be1763438835df33d6c1ca8fc44df88a0a7a6e6cfa1f63f3d8ebfeb75d64`

SHA-256 des neuen Qualifikationseinstiegs:
`b777f48db55a9570611fc74ae319c9871f5e40b08114c4e5831e72ca4b39d545`

SHA-256 der Vorabbindung:
`f9f69e9c293bc30646b4099c5e30493081801d0115e8b69b22c477d367528880`

Die vollstaendigen Vor-/Nachhashes sowie Protokollhashes stehen in
`result.json`. `stdout.txt` und `stderr.txt` bleiben unveraenderte
Originalausgaben. Die historische 24/24-Qualifikation wurde weder
wiederholt noch ersetzt; ihre Dateien sind ebenfalls unveraendert gebunden.

## Aussagegrenze

Dies qualifiziert nur die Gruppierung synthetischer Auswertungsevidenz.
Die neutralen Verifikationsformen sind keine behaupteten technisch
verifizierten Memorygeschichten. Die bestehende unabhaengige technische
Gesamtpruefung bleibt Voraussetzung einer spaeteren realen Auswertung.

Keine Scans, Direktbaselineaufrufe, Memoryformationen, Rezeptoranalysen,
NJ-Projektionen, Feld-, Kontext- oder Runtimeaufrufe. Keine NP-Payloads,
keine NP-Rezeptorwerte, keine reale NQ-Geschichte oder Hauptauswertung.
Scan, Baselines, Memorykerne, Quellen und historische Belege blieben
unveraendert. Fremde Aenderungen und Bootstrap bleiben ausgeschlossen.

Der Hauptlauf ist weiterhin gesperrt und benoetigt eine separate Freigabe.
Der Befund behauptet keinen realen Erhaltungs- oder Transfergewinn.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser getrennten
Variationsauswertung und danach der Entscheidung ueber den einmaligen
realen NQ-Transferlauf weiter.
