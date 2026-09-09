# S2-NX: einmalige neutrale Quellen-/Bindungsqualifikation

Vor Aufruf gebunden: `s2nx-source-binding-qualification-20260909-01`.
Genau ein Aufruf `python -m reports.s2nx.qualify_once`, darin ein
`unittest -v -f` mit 24 Testkoerpern. Kein Retry. Vorher werden Testinventar,
Quellhashes, Interpreterumgebung und Budgets in `preregistration.json`
festgeschrieben. Historische Tests und Haupteinstiege bleiben unberuehrt.

| Tests | Pruefbereich |
| --- | --- |
| 01-03 | 32 literale Fenster, Reihenfolge, native Indizes, bytegleiche Rezepte mit getrennten Identitaeten und Zeiten |
| 04-07 | Feste Phasen-/Partialfolge einschliesslich Nullamplitude, lokale Synthesezeit, Nenner 1024, einmalige Float32-Rundung |
| 08-12 | Unabhaengige Metadatenpruefung, Quellen-/Zeit-/Praefixmanipulation, geschlossene Funktionsfelder und 28 getrennte Kriterien |
| 13-16 | Vollstaendige Metadatenhuellen, unveraenderliche Rezeptformen, Profil/Digest, Built-in-math, Fail-closed und Importgrenzen |
| 17-20 | Zwei getrennte Lernhistorien, acht Updatepositionen, beide Freezes, kein vorgegebener Fit, Zaehler und getrennte Wurzeln |
| 21-24 | Unveraenderliches 0.5 samt Binary64-Hex, zwoelf gekreuzte Pruefstellen, Fitdifferenz nur Funktionskriterium, historische 64-Bindung nicht gelockert |

NX- und reine historische Corpusgenerator-Einstiege sind in jedem Test
gesperrt. Nur sechs neutrale Samples werden mit frei benannten neutralen
Partials gerendert, insgesamt 24 Byte, maximal 12 Byte Ergebnis je Aufruf.
Eine weitere absichtlich ungueltige Ein-Sample-Anforderung wird vor
Veroeffentlichung abgewiesen. Hoechstens 64 neutrale Sinusaufrufe und
32.768 Metadaten-Digestkontrollen; keine vollstaendigen PCM-Fenster.

Rezept-/Quell-/Planstrukturen duerfen aus den literalen NX-Metadaten
entstehen; synthetische Payloadhash-Tokens sind keine behaupteten
PCM-Ergebnisse. Der Verifikator erzeugt seine erwarteten Bindungen ohne
produktive Plan-/Rezeptbauer und ohne Payloadregeneration. Profil und
Umgebung werden rezeptorfrei gebunden; keine NumPy-/Rezeptor-/NJ-Imports
im Testprozess. Keine Lern-/Prognose-/Fehlerberechnung oder Systemaufrufe.

Je Metadatenartefakt maximal 65.536 Byte; die vollstaendige spaetere
Preregistrierung mit realen Umgebungs-/Generator-/Codebindungen wird neutral
auf Groesse geprueft. Spaetere Gesamtbeleggrenzen und getrennte Arbeitsbudgets
werden nur gebunden, nicht ausgefuehrt.

Nur nach vollstaendigem Bestehen ist einmal
`s2nx-source-preseal-20260909-01` zulaessig: 32 PCM-Fenster, 614.400 Byte
erzeugt, maximal ein Payload mit 19.200 Byte, keine Rohdatenablage; danach
genau eine unabhaengige read-only Bindungspruefung. Alle Kollisionen bleiben
erhalten. Keine Rezeptor-/NJ-, Lern- oder Prognoseausfuehrung.

Das qualifiziert Quellen- und Ablaufmetadaten, nicht die spaetere kausale
Zwei-Lerner-Ausfuehrung. Ein Freeze-Metadatum beweist noch kein wirkliches
Einfrieren. Hauptgates bleiben `False`, ME/MI gesperrt. Die feste Kontrolle
0.5 ist kein Initialwert eines Lerners; beide erwarteten Lernkoeffizienten
bleiben `null`. Keine automatische Auswahl der passenden Historie.
