# MCM-KI: einmalige Bestands-Gegenprobe abgeschlossen

2026-10-02. Genau ein gebundener synthetischer Lauf, Exit 0. Keine Wiederholung.
192 Versuchsarm-Aufnahmen und separat 192 interne Referenzfortschreibungen; kein Zwischenreset.

**Bestand/Kausalität: PASS. Erfahrungsauswahl: PASS. Nettonutzen auf V: SCHADEN.**
Keine technischen Fehler, keine Abweichung von den vorab erwarteten Speicherübergängen.
V besitzt an allen 7 Zielen verfügbaren Kontext. E ist dort besser als P, aber schlechter als K.
Die bessere Diagnose D ersetzt den Vergleich auf V einschließlich Kaltstarts nicht.

## Alle fünf Zielmengen

| Menge | Anzahl | Summe E | Summe K | Summe P | MAE E | MAE K | MAE P |
|---|---:|---:|---:|---:|---:|---:|---:|
| V | 7 | 1.5 | 1.125 | 2.5 | 0.214285714286 | 0.160714285714 | 0.357142857143 |
| D | 3 | 0 | 0.5625 | 1 | 0 | 0.1875 | 0.333333333333 |
| M | 9 | 2 | 1.625 | 3 | 0.222222222222 | 0.180555555556 | 0.333333333333 |
| N | 22 | 11.4375 | 10.25 | 11.4375 | 0.519886363636 | 0.465909090909 | 0.519886363636 |
| Gesamt | 31 | 13.4375 | 11.875 | 14.4375 | 0.433467741935 | 0.383064516129 | 0.465725806452 |

## Einzelentscheidungen aller 31 eingetroffenen Ziele

C = Kontext, P = Persistenz. Positive Differenz bedeutet Mehrfehler von E.

| Ziel | E/K/P-Wahl | Fehler E | Fehler K | Fehler P | E−K | E−P |
|---:|---|---:|---:|---:|---:|---:|
| 3 | P/P/P | 0.5 | 0.5 | 0.5 | 0 | 0 |
| 5 | P/P/P | 0.75 | 0.75 | 0.75 | 0 | 0 |
| 7 | P/C/P | 0.5 | 0 | 0.5 | 0.5 | 0 |
| 9 | P/P/P | 0.5 | 0.5 | 0.5 | 0 | 0 |
| 11 | P/P/P | 0.5625 | 0.5625 | 0.5625 | 0 | 0 |
| 13 | P/P/P | 0.4375 | 0.4375 | 0.4375 | 0 | 0 |
| 15 | P/C/P | 0.5625 | 0 | 0.5625 | 0.5625 | 0 |
| 17 | P/P/P | 0.4375 | 0.4375 | 0.4375 | 0 | 0 |
| 19 | P/C/P | 0 | 0.5625 | 0 | -0.5625 | 0 |
| 21 | P/P/P | 0.6875 | 0.6875 | 0.6875 | 0 | 0 |
| 23 | P/C/P | 0.5 | 0 | 0.5 | 0.5 | 0 |
| 25 | P/P/P | 0.4375 | 0.4375 | 0.4375 | 0 | 0 |
| 27 | P/P/P | 0.125 | 0.125 | 0.125 | 0 | 0 |
| 29 | P/P/P | 0.5625 | 0.5625 | 0.5625 | 0 | 0 |
| 31 | P/C/P | 0 | 0.5625 | 0 | -0.5625 | 0 |
| 33 | P/P/P | 0.6875 | 0.6875 | 0.6875 | 0 | 0 |
| 35 | C/C/P | 0 | 0 | 0.5 | 0 | -0.5 |
| 37 | P/P/P | 0.5 | 0.5 | 0.5 | 0 | 0 |
| 39 | P/P/P | 0 | 0 | 0 | 0 | 0 |
| 41 | P/P/P | 0.375 | 0.375 | 0.375 | 0 | 0 |
| 43 | P/P/P | 0.125 | 0.125 | 0.125 | 0 | 0 |
| 45 | P/P/P | 0.5 | 0.5 | 0.5 | 0 | 0 |
| 47 | P/C/P | 0.125 | 0 | 0.125 | 0.125 | 0 |
| 49 | P/P/P | 0.8125 | 0.8125 | 0.8125 | 0 | 0 |
| 51 | P/P/P | 0.5 | 0.5 | 0.5 | 0 | 0 |
| 53 | P/P/P | 0.75 | 0.75 | 0.75 | 0 | 0 |
| 55 | P/C/P | 0.5 | 0 | 0.5 | 0.5 | 0 |
| 57 | P/P/P | 0.75 | 0.75 | 0.75 | 0 | 0 |
| 59 | P/C/P | 0.5 | 0 | 0.5 | 0.5 | 0 |
| 61 | P/P/P | 0.75 | 0.75 | 0.75 | 0 | 0 |
| 63 | C/C/P | 0 | 0 | 0.5 | 0 | -0.5 |

## Sämtliche Gewinne und Schäden

Gegen K: Gewinne [{"target": 19, "gain": 0.5625}, {"target": 31, "gain": 0.5625}]; Schäden [{"target": 7, "harm": 0.5}, {"target": 15, "harm": 0.5625}, {"target": 23, "harm": 0.5}, {"target": 47, "harm": 0.125}, {"target": 55, "harm": 0.5}, {"target": 59, "harm": 0.5}].
Gewinnsumme 1.125, Schadenssumme 2.6875, Netto-Fehlerdifferenz E−K = 1.5625.
Gegen P: Gewinne [{"target": 35, "gain": 0.5}, {"target": 63, "gain": 0.5}]; Schäden [].
Gewinnsumme 1.0, Schadenssumme 0, Netto-Fehlerdifferenz E−P = -1.0.

## Fehlererfahrung, Verlust und Wiederkehr

- Ziel19: B:r2 startet kalt mit P und lernt (EC,EP)=(0.5625,0). Ziel23: A:r1 startet kalt mit P und lernt (0,0.5).
- Ziel31: beide Bewertungen gleichzeitig erhalten; E wählt für B P. Die A-Zelle bleibt unverändert. Ziel35: E wählt für A C; die B-Zelle bleibt unverändert.
- Ziel39: B:r2 und Bp:c5 sind mehrdeutig. Kein gültiges Ticket, kein Kontext und kein Fehlerupdate; die vollständige Fehlertabelle bleibt vor/nach Zielkonsum gleich.
- Aufnahme40: Bp wird normal promoviert, B:r2 verdrängt und dessen Zelle (0.5625,0) gelöscht. Dies ist ein späteres Aufnahmeereignis, kein Update aus Ziel39.
- Aufnahme48: A:r1 wird verdrängt; seine letzte Fehlerzelle (0,0.5) verschwindet. Auch C:c6 verliert bei Promotion seine Kandidatenzelle (0,0.125).
- Ziel51: kein A-Treffer, keine alte A-Zelle, E/K/P wählen P und haben jeweils Fehler0.5. Der Verlust der Verfügbarkeit bleibt in M und Gesamt enthalten.
- Ziel55: gleicher A-Werteverlauf als neuer Kandidat c7, leere Fehlererfahrung und P-Wahl; danach (0,0.5). Aufnahme56 löscht diese Kandidatenzelle bei Promotion.
- Ziel59: neue retained-Generation r5 beginnt erneut leer und wählt P; danach eigene Erfahrung (0,0.5). Ziel63 wählt C ausschließlich aus dieser neuen Erfahrung.
- Auch die Kandidatenzellen c1/c2 wurden bei Promotion8/16 gelöscht. Alle Aufnahmeereignisse und sämtliche Fehlerzellen vor/nach Zielkonsum stehen in error-cell-trajectories.json.
- V enthält die drei kostentragenden kalten A-Starts23/55/59: zusammen1.5 Mehrfehler gegen K. Die B-Persistenzgewinne19/31 betragen zusammen1.125. Somit bleibt auf V ein Mehrfehler von0.375 (MAE-Differenz0.0535714285714).

## Ressourcen und Abschluss

Endziel65 ist zensiert, ohne Zielkonsum/Fehlerupdate; Vorschläge und EMA-Zellen nach Ende freigegeben.
Memoryzustände nach jedem Frame und Matchreceipts sind zwischen E/K/P identisch. Der Replay prüfte zusätzlich seine interne Referenz.
46 gebundene Dateien unverändert; alle42 bisherigen EMA-Dateien weiterhin hashidentisch. Plan und Laufzeit ebenfalls vor/nach bestätigt.
Frame-Peak16/18, Vorschläge2/2, gemeinsamer Peak17/20. EMA-Zusatz4281/16384 Byte inklusive gemessener temporärer Allokation; Beobachter ausgeschlossen.
Receipt457/16384 Byte, transiente UTF8-Obergrenze914/32768 Byte. Gepackter EMA-Kern416 Byte; keine Gesamtprozess-RAM-Aussage.
Originalexport einschließlich Quelle und Abschluss: 287396 Byte. Er bleibt unverändert.
Dieser ergänzende Bericht und seine Tabellen teilen mit dem Originalexport dasselbe4MiB-Budget. Die exakte gemeinsame Schlussbilanz steht in closure.json;256KiB bleiben bis zum Schreiben des Abschlusses reserviert.
Einzelausgaben und Abschluss des Laufs: ../ema-stock-counterprobe-20261001-01/. Autorisierung ist durch den exklusiv beanspruchten Zielordner verbraucht; kein Neustart.

## Einordnung und nächster Vorschlag an den Projektleiter

Der Mechanismus erfüllt die geprüfte Generationstrennung und kausale Auswahl. Für diese gebundene Bestandsfolge trägt er gegenüber sofortiger Kontextnutzung jedoch zusätzliche Fehler. Kein Nettonutzenbeleg, keine allgemeine Lern- oder Clusterorganisationsaussage. EMA bleibt standardmäßig deaktiviert.
Empfehlung: den technisch korrekten, wirtschaftlich negativen Befund abnehmen. Als nächsten begrenzten Konzeptschritt die kalte Persistenzwahl anhand dieser gespeicherten Kosten den Kontext-Risiken gegenüberstellen und vor einem weiteren Versuch eine prüfbare Alternative begründen. Keine generationenübergreifende Fehlerübernahme, Parameteränderung oder erneute Ausführung aus diesem Bericht ableiten.
