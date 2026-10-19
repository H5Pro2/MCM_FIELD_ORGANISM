# MCM-KI: gebundener S/W/L-Vergleich abgeschlossen

2026-10-03. S16,W16,L64 jeweils in M/E/K/P genau einmal; Exit0.
96 Quellpositionen,384 Arm-Aufnahmen und384 separat ausgewiesene interne Referenzfortschreibungen.
Kein Zwischenreset,keine Zusatzfolge,Wiederholung oder Parameteränderung.

**Korrekte Zuordnung: PASS in S/W/L. Begrenzter Stabilitätsvorteil mit Wechselschaden. Robuster Auswahlvorteil: NICHT_NACHGEWIESEN.**
Keine technischen Fehler und keine Erwartungsabweichungen. Alle vorgegebenen Ziele vorhanden.
L bleibt Entwicklungsregression; unabhängiger Evaluationsnutzen bleibt NICHT_GEPRUEFT (Maschinenstatus NOT_TESTED).
EMA und Promotionsmitnahme bleiben standardmäßig deaktiviert.

## Festgelegte Zielmengen und sämtliche Armvergleiche

Je Feld Fehlersumme / MAE. M=Mitnahme,E=Reset,K=Kontext-sonst-Persistenz,P=Persistenz.
H/N partitionieren G. V,D,J überlappen; sie werden nicht addiert oder nachträglich umgewichtet.

### S

| Menge | Ziele | M Summe / MAE | E Summe / MAE | K Summe / MAE | P Summe / MAE |
|---|---|---:|---:|---:|---:|
| H | 7,11,15 | 0.5 / 0.166666666667 | 1 / 0.333333333333 | 0 / 0 | 1.5 / 0.5 |
| N | 3,5,9,13 | 2.75 / 0.6875 | 2.75 / 0.6875 | 2.75 / 0.6875 | 2.75 / 0.6875 |
| G | 3,5,7,9,11,13,15 | 3.25 / 0.464285714286 | 3.75 / 0.535714285714 | 2.75 / 0.392857142857 | 4.25 / 0.607142857143 |
| V | 7,11 | 0.5 / 0.25 | 1 / 0.5 | 0 / 0 | 1 / 0.5 |
| D | 11 | 0 / 0 | 0.5 / 0.5 | 0 / 0 | 0.5 / 0.5 |
| J | 11 | 0 / 0 | 0.5 / 0.5 | 0 / 0 | 0.5 / 0.5 |

V-Kontextverfügbarkeit: True; Baseline-Nettonutzen auf V: SCHADEN.

### W

| Menge | Ziele | M Summe / MAE | E Summe / MAE | K Summe / MAE | P Summe / MAE |
|---|---|---:|---:|---:|---:|
| H | 7,11,15 | 1 / 0.333333333333 | 0.5 / 0.166666666667 | 0.5 / 0.166666666667 | 0.5 / 0.166666666667 |
| N | 3,5,9,13 | 2.75 / 0.6875 | 2.75 / 0.6875 | 2.75 / 0.6875 | 2.75 / 0.6875 |
| G | 3,5,7,9,11,13,15 | 3.75 / 0.535714285714 | 3.25 / 0.464285714286 | 3.25 / 0.464285714286 | 3.25 / 0.464285714286 |
| V | 7,11 | 1 / 0.5 | 0.5 / 0.25 | 0.5 / 0.25 | 0.5 / 0.25 |
| D | 11 | 0.5 / 0.5 | 0 / 0 | 0.5 / 0.5 | 0 / 0 |
| J | 11 | 0.5 / 0.5 | 0 / 0 | 0.5 / 0.5 | 0 / 0 |

V-Kontextverfügbarkeit: True; Baseline-Nettonutzen auf V: SCHADEN.

### L

| Menge | Ziele | M Summe / MAE | E Summe / MAE | K Summe / MAE | P Summe / MAE |
|---|---|---:|---:|---:|---:|
| H | 19,23,31,35,39,51,55,59,63 | 1.5625 / 0.173611111111 | 2 / 0.222222222222 | 1.625 / 0.180555555556 | 3 / 0.333333333333 |
| N | 3,5,7,9,11,13,15,17,21,25,27,29,33,37,41,43,45,47,49,53,57,61 | 11.4375 / 0.519886363636 | 11.4375 / 0.519886363636 | 10.25 / 0.465909090909 | 11.4375 / 0.519886363636 |
| G | 3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53,55,57,59,61,63 | 13 / 0.41935483871 | 13.4375 / 0.433467741935 | 11.875 / 0.383064516129 | 14.4375 / 0.465725806452 |
| V | 19,23,31,35,55,59,63 | 1.0625 / 0.151785714286 | 1.5 / 0.214285714286 | 1.125 / 0.160714285714 | 2.5 / 0.357142857143 |
| D | 31,35,63 | 0 / 0 | 0 / 0 | 0.5625 / 0.1875 | 1 / 0.333333333333 |
| J | 19,23,59 | 0.5625 / 0.1875 | 1 / 0.333333333333 | 0.5625 / 0.1875 | 1 / 0.333333333333 |

V-Kontextverfügbarkeit: True; Baseline-Nettonutzen auf V: BELEGT.

## Vollständige Gewinne und Schäden

Alle folgenden Werte sind einzelne Fehlerdifferenzen von M gegen die jeweilige Baseline; keine Verrechnung zwischen Geschichten.
- S gegen E: Gewinne [{"target": 11, "gain": 0.5}]; Schäden [].
- S gegen K: Gewinne []; Schäden [{"target": 7, "harm": 0.5}].
- S gegen P: Gewinne [{"target": 11, "gain": 0.5}, {"target": 15, "gain": 0.5}]; Schäden [].
- W gegen E: Gewinne []; Schäden [{"target": 11, "harm": 0.5}].
- W gegen K: Gewinne []; Schäden [{"target": 7, "harm": 0.5}].
- W gegen P: Gewinne []; Schäden [{"target": 11, "harm": 0.5}].
- L gegen E: Gewinne [{"target": 23, "gain": 0.5}, {"target": 59, "gain": 0.5}]; Schäden [{"target": 19, "harm": 0.5625}].
- L gegen K: Gewinne [{"target": 31, "gain": 0.5625}]; Schäden [{"target": 7, "harm": 0.5}, {"target": 15, "harm": 0.5625}, {"target": 47, "harm": 0.125}, {"target": 55, "harm": 0.5}].
- L gegen P: Gewinne [{"target": 23, "gain": 0.5}, {"target": 35, "gain": 0.5}, {"target": 59, "gain": 0.5}, {"target": 63, "gain": 0.5}]; Schäden [{"target": 19, "harm": 0.5625}].

## Alle Einzelentscheidungen und Herkunft der Erfahrung

C=Kontext,P=Persistenz. Ohne auswählbaren Kontext ist P eine Enthaltung vom Kontext, kein gelernter Erfolg.
MITGENOMMEN_DANACH_AKTUALISIERT enthält beide Anteile; die Mitnahme wird nicht als neue Beobachtung gezählt.

### S

| Ziel | Wahl M/E/K/P | Fehler M/E/K/P | Grundlage M | Grundlage E |
|---:|---|---|---|---|
| 3 | P/P/P/P | 0.5/0.5/0.5/0.5 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 5 | P/P/P/P | 0.75/0.75/0.75/0.75 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 7 | P/P/C/P | 0.5/0.5/0/0.5 | KALTER_STANDARD | KALTER_STANDARD |
| 9 | P/P/P/P | 0.75/0.75/0.75/0.75 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 11 | C/P/C/P | 0/0.5/0/0.5 | MITGENOMMENE_ERFAHRUNG | KALTER_STANDARD |
| 13 | P/P/P/P | 0.75/0.75/0.75/0.75 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 15 | C/C/C/P | 0/0/0/0.5 | MITGENOMMEN_DANACH_AKTUALISIERT | NEU_ERWORBENE_ERFAHRUNG |

### W

| Ziel | Wahl M/E/K/P | Fehler M/E/K/P | Grundlage M | Grundlage E |
|---:|---|---|---|---|
| 3 | P/P/P/P | 0.5/0.5/0.5/0.5 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 5 | P/P/P/P | 0.75/0.75/0.75/0.75 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 7 | P/P/C/P | 0.5/0.5/0/0.5 | KALTER_STANDARD | KALTER_STANDARD |
| 9 | P/P/P/P | 0.75/0.75/0.75/0.75 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 11 | C/P/C/P | 0.5/0/0.5/0 | MITGENOMMENE_ERFAHRUNG | KALTER_STANDARD |
| 13 | P/P/P/P | 0.75/0.75/0.75/0.75 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 15 | P/P/P/P | 0/0/0/0 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |

### L

| Ziel | Wahl M/E/K/P | Fehler M/E/K/P | Grundlage M | Grundlage E |
|---:|---|---|---|---|
| 3 | P/P/P/P | 0.5/0.5/0.5/0.5 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 5 | P/P/P/P | 0.75/0.75/0.75/0.75 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 7 | P/P/C/P | 0.5/0.5/0/0.5 | KALTER_STANDARD | KALTER_STANDARD |
| 9 | P/P/P/P | 0.5/0.5/0.5/0.5 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 11 | P/P/P/P | 0.5625/0.5625/0.5625/0.5625 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 13 | P/P/P/P | 0.4375/0.4375/0.4375/0.4375 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 15 | P/P/C/P | 0.5625/0.5625/0/0.5625 | KALTER_STANDARD | KALTER_STANDARD |
| 17 | P/P/P/P | 0.4375/0.4375/0.4375/0.4375 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 19 | C/P/C/P | 0.5625/0/0.5625/0 | MITGENOMMENE_ERFAHRUNG | KALTER_STANDARD |
| 21 | P/P/P/P | 0.6875/0.6875/0.6875/0.6875 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 23 | C/P/C/P | 0/0.5/0/0.5 | MITGENOMMENE_ERFAHRUNG | KALTER_STANDARD |
| 25 | P/P/P/P | 0.4375/0.4375/0.4375/0.4375 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 27 | P/P/P/P | 0.125/0.125/0.125/0.125 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 29 | P/P/P/P | 0.5625/0.5625/0.5625/0.5625 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 31 | P/P/C/P | 0/0/0.5625/0 | MITGENOMMEN_DANACH_AKTUALISIERT | NEU_ERWORBENE_ERFAHRUNG |
| 33 | P/P/P/P | 0.6875/0.6875/0.6875/0.6875 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 35 | C/C/C/P | 0/0/0/0.5 | MITGENOMMEN_DANACH_AKTUALISIERT | NEU_ERWORBENE_ERFAHRUNG |
| 37 | P/P/P/P | 0.5/0.5/0.5/0.5 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 39 | P/P/P/P | 0/0/0/0 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 41 | P/P/P/P | 0.375/0.375/0.375/0.375 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 43 | P/P/P/P | 0.125/0.125/0.125/0.125 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 45 | P/P/P/P | 0.5/0.5/0.5/0.5 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 47 | P/P/C/P | 0.125/0.125/0/0.125 | KALTER_STANDARD | KALTER_STANDARD |
| 49 | P/P/P/P | 0.8125/0.8125/0.8125/0.8125 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 51 | P/P/P/P | 0.5/0.5/0.5/0.5 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 53 | P/P/P/P | 0.75/0.75/0.75/0.75 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 55 | P/P/C/P | 0.5/0.5/0/0.5 | KALTER_STANDARD | KALTER_STANDARD |
| 57 | P/P/P/P | 0.75/0.75/0.75/0.75 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 59 | C/P/C/P | 0/0.5/0/0.5 | MITGENOMMENE_ERFAHRUNG | KALTER_STANDARD |
| 61 | P/P/P/P | 0.75/0.75/0.75/0.75 | KEIN_AUSWAEHLBARER_KONTEXT | KEIN_AUSWAEHLBARER_KONTEXT |
| 63 | C/C/C/P | 0/0/0/0.5 | MITGENOMMEN_DANACH_AKTUALISIERT | NEU_ERWORBENE_ERFAHRUNG |

## Fehlerzellen unmittelbar vor und nach jeder Promotion

Die Zeilen enthalten die vollständige jeweilige Tabelle, einschließlich fremder oder gleichzeitig verdrängter Zellen.

- S Aufnahme8: c1→r1, Originalordinalen[1, 2, 3, 4].
  M vorher: c1/o0/q0:(0.0,0.5); nachher: r1/o0/q0:(0.0,0.5).
  E vorher: c1/o0/q0:(0.0,0.5); nachher: leer.
- W Aufnahme8: c1→r1, Originalordinalen[1, 2, 3, 4].
  M vorher: c1/o0/q0:(0.0,0.5); nachher: r1/o0/q0:(0.0,0.5).
  E vorher: c1/o0/q0:(0.0,0.5); nachher: leer.
- W Aufnahme16: c2→r2, Originalordinalen[9, 10, 11, 12].
  M vorher: r1/o0/q0:(0.25,0.25); nachher: r1/o0/q0:(0.25,0.25).
  E vorher: r1/o0/q0:(0.5,0.0); nachher: r1/o0/q0:(0.5,0.0).
- L Aufnahme8: c1→r1, Originalordinalen[1, 2, 3, 4].
  M vorher: c1/o0/q0:(0.0,0.5); nachher: r1/o0/q0:(0.0,0.5).
  E vorher: c1/o0/q0:(0.0,0.5); nachher: leer.
- L Aufnahme16: c2→r2, Originalordinalen[9, 10, 11, 12].
  M vorher: r1/o0/q0:(0.0,0.5); c2/o0/q0:(0.0,0.5625); nachher: r1/o0/q0:(0.0,0.5); r2/o0/q0:(0.0,0.5625).
  E vorher: c2/o0/q0:(0.0,0.5625); nachher: leer.
- L Aufnahme40: c5→r3, Originalordinalen[29, 30, 31, 32].
  M vorher: r1/o0/q0:(0.0,0.5); r2/o0/q0:(0.421875,0.140625); nachher: r1/o0/q0:(0.0,0.5).
  E vorher: r2/o0/q0:(0.5625,0.0); r1/o0/q0:(0.0,0.5); nachher: r1/o0/q0:(0.0,0.5).
- L Aufnahme48: c6→r4, Originalordinalen[41, 42, 43, 44].
  M vorher: r1/o0/q0:(0.0,0.5); c6/o0/q0:(0.0,0.125); nachher: r4/o0/q0:(0.0,0.125).
  E vorher: c6/o0/q0:(0.0,0.125); r1/o0/q0:(0.0,0.5); nachher: leer.
- L Aufnahme56: c7→r5, Originalordinalen[49, 50, 51, 52].
  M vorher: c7/o0/q0:(0.0,0.5); r4/o0/q0:(0.0,0.125); nachher: r5/o0/q0:(0.0,0.5); r4/o0/q0:(0.0,0.125).
  E vorher: c7/o0/q0:(0.0,0.5); nachher: leer.

## Fachliche Auswertung

S: An7 lernen M/E aus demselben kalten P-Start das Paar(0,0.5). M erhält es bei8. An11 wählt M daraus C und spart0.5 gegen E; an15 haben beide neue retained-Erfahrung. M erfüllt den Stabilitätsvergleich auf H und G. Gegen K bleibt der kalte Verlust an7 bestehen; deshalb kein V-Nettonutzen gegen alle Baselines.
W: Derselbe Transfer bei8 bewahrt dieselbe Bewertung, die an11 nun unpassend ist. M wählt C und verliert0.5 gegen E/P. Danach steht M auf(0.25,0.25),E auf(0.5,0). An15 verhindert Mehrdeutigkeit eine Kontextwahl; die dortige P-Wahl belegt daher keine erneute eindeutige erfahrungsabhängige Anpassung. Promotion16 erzeugt mangels Kandidatenzelle keine Fehlererfahrung.
L: M verliert an19 gegenüber E/P0.5625 aus mitgenommener B-Kontexterfahrung; E gewinnt dort durch seinen kalten Default, nicht durch Lernen. M spart an23 und59 je0.5 gegen E. An31 wählt M nach neuer Beobachtung19 bei Gleichstand P, E nach eigener B-Bewertung ebenfalls P. Dieser Gewinn gegen K ist kein zusätzlicher M-Gewinn gegen E oder kalte Persistenz.
An39 kein Fehlerupdate bei Mehrdeutigkeit; spätere reguläre B-Löschung bei40 bleibt getrennt. Bei48 wird alte A-Erfahrung gelöscht, während C-Erfahrung mitgenommen wird. An51 fehlt A-Kontext. An55 sind M/E für den neuen Kandidaten c7 kalt; nur dessen neue Erfahrung wird bei56 nach r5 verschoben. M nutzt sie an59; an63 ist sie zusätzlich durch das neue Ziel59 aktualisiert. Keine Übernahme vom alten r1 nach Wiederkehr.
Auf L-V ist M strikt besser als E,K,P und erfüllt das vorab definierte lokale Nutzenkriterium. Über alle31 L-Ziele ist M jedoch weiterhin schlechter als K. L ist bekanntes Entwicklungsmaterial; daraus folgt kein unabhängiger Evaluationsnutzen. Das positive L-V-Ergebnis und der S-Gewinn heben den W-Schaden nicht auf.

## Ressourcen, Abweichungen und Abschluss

51 gebundene Dateien sowie Plan,Vertrag und Python-Laufzeit vor/nach unverändert. Die Autorisierung unterscheidet sich nur im Status von der Vorlage.
Memoryzustände und Matchreceipts zwischen allen Armen identisch. Zielzahlen je Arm S7/W7/L31. Endziele17/17/65 zensiert ohne Zielkonsum; Vorschläge und EMA-Zellen freigegeben.
Gemessene Spitzen über alle Arme: {"additional_python_peak": 4420, "frame_peak": 16, "proposal_peak": 2, "combined_peak": 17, "receipt_bytes": 457, "transient_utf8_upper": 914, "packed_bytes": 416}. Grenzen:16384 Zusatzbyte,18 Frames,2 Vorschläge,20 gemeinsam,16384 Receiptbyte,32768 transiente UTF8-Byte. Keine Gesamtprozess-RAM-Aussage.
Originalexport einschließlich Abschluss:493440 Byte. Die frühere technische Qualifikation mit sämtlichen Fixtures/Snapshots wird mit weiteren495076 Byte konservativ in die gemeinsame4MiB-Bilanz einbezogen.
Auch dieser Bericht und seine Tabellen sind enthalten. Exakte gemeinsame Endsumme: closure.json.256KiB Abschlussreserve vorab eingehalten. Keine ursprüngliche Exportdatei geändert. Nachauswertung ausschließlich gespeicherter Daten; keine weiteren Replays.
Keine Ausführungs-/Erwartungsabweichungen. Das Ausbleiben eines robusten Vorteils ist ein fachlicher Gegenbefund, kein technischer Fehler. Die Einmalfreigabe ist verbraucht.

## Genau ein nächster fachlicher Vorschlag

Den Mischbefund abnehmen und die Variante unverändert experimentell/default disabled belassen. Als nächsten begrenzten Konzeptschritt prüfen, welche vor dem Ziel tatsächlich verfügbaren Informationen stabile und veränderte Fortsetzungen überhaupt unterscheiden könnten. S/W besitzen bis zur ersten unterschiedlichen Fortsetzung denselben beobachteten Präfix; ohne zusätzliche Information kann eine kausale Auswahl diesen Wechsel nicht im Voraus erkennen. Deshalb keine bloße Neuabstimmung von Alpha oder Kaltstartdefault als allgemeine Lösung.
Abnahmekriterium dieses Konzeptschritts: ein klar benanntes,vor Ziel verfügbares Informationssignal mit Gegenfall und Informationsgrenze oder die begründete Feststellung,dass mit dem bisherigen Eingang nur nachträgliche Anpassung möglich ist. Keine neue Implementierung,Quelle oder Wiederholung aus diesem Bericht ableiten.
