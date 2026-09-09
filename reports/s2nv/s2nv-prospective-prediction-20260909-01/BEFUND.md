# S2-NV: einmalige prospektive Verlaufsvorhersage

## Technischer Abschluss

- Lauf-ID: `s2nv-prospective-prediction-20260909-01`, Datum: 2026-09-09.
- Genau ein `run_main_once`-Aufruf, danach ein `verify_file_once`-Aufruf und erst nach dessen Freigabe ein `evaluate_file_once`-Aufruf. Exit-Code `0`; kein Retry, Test oder zusaetzlicher Vorlauf.
- Ergebnis: `RECORDING_COMPLETE`, Fehlerbeleg `null`; Pruefung: `S2NV_PREDICTION_VERIFIED`, `evaluation_allowed=True`, `baseline_equal=True`.
- Unveraenderte vier Fuenferfolgen: 20 Payloadgenerierungen und vor Analyse bestaetigte Payloadhashes, 20 direkte Analysen, 20 NJ-Projektionen, 20 abgeschlossene Fenster, zwoelf gebundene Prognosestellen. Keine Deduplizierung.
- Je Strom frischer Praefixcontroller. Beide Prognosearme und Direktnachrechnung werden vor Erzeugung/Analyse des jeweiligen Zielpayloads gebunden. Folgepraefixe verwenden ausschliesslich tatsaechliche Rezeptorwerte. Keine Vorabmaterialisierung, Wiederverwendung von Zielwerten zwischen Stroemen oder Prognosekuerzung.
- Das Hauptgate wurde nur im aufrufenden Python-Prozess fuer diesen Aufruf geoeffnet und in `finally` zurueckgesetzt. Prognose- und Quellgate anschliessend explizit `False` bestaetigt. Keine qualifizierte Quelldatei geaendert.
- `rolling_hops`, Rohpayloadablage, Memory-, Feld-, Kontext- und Runtimeaufrufe jeweils `0`.

Aufruf aus dem workspace mit `C:/Python314/python.exe -`: neue ID und nicht vorhandenes Ergebnisverzeichnis pruefen; Gate oeffnen; `run_main_once(run_id)`; Gate in `finally` schliessen; `verify_file_once(out)`; nur bei `RECORDING_COMPLETE` und `evaluation_allowed=True` anschliessend `evaluate_file_once(out)`. Beide Gates abschliessend pruefen. Die Einmal-Claims liegen im Ergebnisverzeichnis.

## Zwoelf Einzelbefunde

Gespeicherte MAE-Werte ohne neue Nachberechnung. WIN bedeutet strikt kleineren LINEAR-Fehler, LOSS strikt groesseren, TIE Gleichheit. Zielordinal `k` ist nullbasiert. Die vier gemeinsamen Praefixe sind keine unabhaengigen Replikate.

| Stelle | Strom | k | Phase | LINEAR-MAE | PERSIST-MAE | Befund |
| --- | --- | --- | --- | --- | --- | --- |
| p01 | s01 Fortsetzung | 2 | gemeinsamer Anstieg | 1.9895970930295746e-11 | 0.0004579810843347019 | WIN |
| p02 | s01 Fortsetzung | 3 | weitere Fortsetzung | 2.0844311811336113e-11 | 0.00045798109553816667 | WIN |
| p03 | s01 Fortsetzung | 4 | Folgefenster | 2.2626718501061796e-11 | 0.00045798109551712366 | WIN |
| p04 | s02 Umkehr | 2 | gemeinsamer Anstieg | 1.9895970930295746e-11 | 0.0004579810843347019 | WIN |
| p05 | s02 Umkehr | 3 | erster Wechsel | 0.0009159621686694037 | 0.0004579810843347019 | LOSS |
| p06 | s02 Umkehr | 4 | Folgefenster | 1.989597080380563e-11 | 0.00045798109204130393 | WIN |
| p07 | s03 Stillstand | 2 | gemeinsamer Anstieg | 1.9895970930295746e-11 | 0.0004579810843347019 | WIN |
| p08 | s03 Stillstand | 3 | erster Wechsel | 0.0004579810843347018 | 0.0 | LOSS |
| p09 | s03 Stillstand | 4 | Folgefenster | 0.0 | 0.0 | TIE |
| p10 | s04 Quellenwechsel | 2 | gemeinsamer Anstieg | 1.9895970930295746e-11 | 0.0004579810843347019 | WIN |
| p11 | s04 Quellenwechsel | 3 | erster Wechsel | 0.005895900745535605 | 0.005437920791175294 | LOSS |
| p12 | s04 Quellenwechsel | 4 | Folgefenster | 0.005437920791175294 | 0.0 | LOSS |

Jeweils Nenner 3: s01 hat 3 WIN / 0 TIE / 0 LOSS; s02 2 / 0 / 1; s03 1 / 1 / 1; s04 1 / 0 / 2. Kein gepoolter Mittelwert; Gewinne kompensieren keine Verluste. Insbesondere bleiben die drei ersten Wechselverluste und der weitere Verlust p12 einzeln bestehen.

## Sechs vorgebundene Prognosebedingungen

| Bedingung | Stelle | Vorhersage | Ergebnis |
| --- | --- | --- | --- |
| o01 | p01 | LINEAR-MAE < PERSIST-MAE | bestaetigt |
| o02 | p02 | LINEAR-MAE < PERSIST-MAE | bestaetigt |
| o03 | p03 | LINEAR-MAE < PERSIST-MAE | bestaetigt |
| o04 | p05 | LINEAR-MAE > PERSIST-MAE | bestaetigt, Wechselverlust |
| o05 | p08 | LINEAR-MAE > PERSIST-MAE | bestaetigt, Wechselverlust |
| o06 | p11 | LINEAR-MAE > PERSIST-MAE | bestaetigt, Wechselverlust |

Primaerprognose `CONFIRMED`: alle drei Fortsetzungsbedingungen bestehen. Die drei getrennten Belastungsbedingungen bestehen ebenfalls, gerade weil LINEAR an diesen Stellen schlechter abschneidet. Dies ist keine allgemeine Ueberlegenheit der Verlaufsvorhersage.

## Arbeit und Beleggrenzen

Die vollstaendigen Zaehler stehen in `result.json`, ihre vorab gebundenen Grenzen in `preregistration.json`; alle Ausfuehrungszaehler entsprechen den gebundenen Werten.

- Je primaerer und direkter Prognose: 576 Subtraktionen, 576 Additionen und 576 Persistenzkopien.
- Je primaerer und direkter Fehlerrechnung: 1.152 Einzelterme, 24 MAE-Summen und zwoelf Gewinne.
- Separat budgetierte einmalige Verifikation: 960 Halbierungen, 1.152 Prognosesubtraktionen, 1.152 Additionen, 1.152 Persistenzkopien, 2.304 Fehlerterme, 48 MAE-Summen, 24 Gewinne; 20 Fenster und zwoelf Stellen.
- Nachgelagerte Auswertung: zwoelf Ergebniszuordnungen und sechs strikte Bedingungen.
- Gesamtbeleg `392826` Byte bei Grenze `2097152`; Vorbindung `4216` bei `65536`; Verifikation `865` und Auswertung `3553` jeweils unter `262144` Byte.

Die read-only Pruefung bestaetigt Quellen-/Zeit-/Profil-/Wertebindungen, gespeicherte Halbierungen, Prognose- und Fehlerarithmetik sowie Direktbaselinegleichheit. Keine PCM-Regeneration, FFT-, Rezeptor- oder NJ-Wiederholung. Sie prueft gespeicherte Rohwerte vorwaerts, rekonstruiert sie nicht aus Halbwerten. Der Ergebnisdateihash bleibt vor/nach Verifikation identisch.

Die historische CPU-Aufrufreihenfolge ist durch den Offline-Beleg allein **nicht unabhaengig bewiesen** (`chronology_independently_proven=False`). Die Zukunftssperre stuetzt sich auf den zuvor neutral qualifizierten kontrollierten Aufrufpfad und dessen unveraenderte Quellenbindung; ein finaler Digest ersetzt diese Grenze nicht.

## Bindungen

- Ausfuehrungswurzel: `37a6a114860f868bda9d7bfbb437ad6f3e8e22820fedc60d49a1622ae209499e`.
- Evaluationswurzel: `85bd55b8c1e40e0ce8f99a285408756f20a152439c842cda48f01c21842c4155`.
- Historisches Siegel: `c927527b71f016e5f359fc2e439c8b58a23672fcb22f8cb959760313ade8507a`.
- Ergebnisdigest: `cc2253a487dded8e3af16bd9f2a4f1ceb8e0e66b7fc8cf56cc8feb7167220aee`.
- Ergebnisdatei SHA-256 vor/nach Pruefung: `be53ea10945305d6448a0c63b615cec846abfc2e3c77c85cb28167f769b2bb6d`.
- Verifikationsdigest: `57517538e3f854efbdb5a6ebbef9f1f7156c008e46d0fbc6d9e7ce53a7b5b812`.
- Auswertungsdigest: `fdae81e05af586e3944a43637975fe07032f2d1af25cc68bbf43c519808401a9`.

Saemtliche qualifizierten Quellhashes vor/nach Ausfuehrung stimmen ueberein und sind in Vorbindung/Gesamtbeleg einzeln erhalten. Versiegelung, Quellenrezepte, Parameter und historische Qualifikationen blieben unveraendert; keine Ersatzquelle oder neue Kalibrierung.

## Aussage und weitere Entscheidung

Auf diesem vorgebundenen Pruefbestand verbessert feste lineare Extrapolation die drei Fortsetzungsprognosen. Bei unangekuendigten Aenderungen ist sie dagegen schlechter als Persistenz; nach Quellenwechsel bleibt dieser Nachteil noch im Folgefenster bestehen. Identische Praefixe erlauben hier keine Vorwegnahme ihrer unterschiedlichen Fortsetzungen.

Dies ist ein begrenzter prospektiver Nutzen mit offen ausgewiesenen Verlusten: **feste Extrapolation, kein Lernen, keine Quellenidentitaet und keine tragfaehige Lernbindung**. Kein Memory-, Feld- oder Runtimeanschluss; ME/MI bleiben gesperrt. Keine weitere Ausfuehrung freigegeben.

WEITER: Am besten geht es jetzt mit der Analystenbewertung der getrennten Fortsetzungsgewinne und Wechselverluste sowie der daraus zulassigen naechsten fachlichen Frage weiter.
