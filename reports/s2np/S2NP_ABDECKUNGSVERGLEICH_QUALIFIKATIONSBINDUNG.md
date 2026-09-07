# S2-NP: private Vergleichsbindung und neutrales Testinventar

Stand 2026-09-07, Basis 6910de1. Nur Implementierung und genau ein neutraler
Qualifikationsaufruf. Kein realer NP-Vergleich und keine erneute Materialisierung.
Der vorversiegelte Vertrag sowie Quellen, Masken, Schwellen und Profile bleiben
unveraendert. Die bisherigen Datei-/Ergebnisbindungen werden nur gehasht.

## Kleine Anbindung

- `_s2np_private_coverage_comparison.py`: unveraenderliche indexgebundene
  `ViewValues`, explizite Teil-/Diagnoseeingaenge, vollstaendige Panelvergleiche,
  literale Paneltraversierung und technische Belegpruefung.
- `_s2np_private_coverage_baseline.py`: eigene Differenzbildung, historische
  `sum(...)/len(I)`-Reihenfolge, Maximum und direkte Kardinalitaetstabelle.
  Gemeinsam sind ausschliesslich Eingabevalidierung, Typen und Kanonisierung.
- `_s2np_private_coverage_evaluation.py`: erst nach Verifikation; getrennte
  Beziehungs- und Eindeutigkeitsnenner, Verluste, Gewinne, falsche Anwendbarkeit,
  Leer-/Mehrdeutigkeitsbefunde und Zielentfernung. Keine Auswahl oder Anwendung.

Die Projektion erhaelt bereits gepruefte reduzierte NJ-Werte. Der Aufrufer muss
vor einem spaeteren realen Vergleich das versiegelte Materialisat authentisieren.
`project_values` authentisiert keinen externen Elternbeleg. Vergleicher erhalten
nur die gewaehlten Werte und Herkunftsdigests, keine versteckten Restwerte.
Die Katalogpruefung kontrolliert vor den Scans ihre korrekte Teilwertprojektion;
der getrennte Auswerter darf Wertegleichheit je Sicht und Rollen gegenueberstellen.
Weder Rollen noch Vollsichtbefunde wirken in die Teilvergleiche hinein.

Alle numerischen Einzelterme mit Originalindex werden gespeichert. Die
Offline-Pruefung bildet keine Quelldifferenzen neu. Sie prueft Eingabebindung,
vollstaendige Index-/Panelreihenfolge, gespeicherte Aggregate und Bedingungen
sowie bitgenaue kanonische Gleichheit beider unabhaengig erzeugter Belege.
Sie ist keine dritte numerische Implementierung. Gueltige leere oder mehrdeutige
Treffermengen sind technisch gueltig, unabhaengig von Sollrelationen.

## Vorab festes neutrales Inventar

Genau 22 Testgruppen, AST-Inventar und Quellhashes vor dem einzigen unittest-
Unterprozess in `preregistration.json` binden:

1. Feste Masken, Reihenfolge und Tupelform.
2. Abschottung verdeckter Werte in beiden 24er-Sichten.
3. Separater 48er-Diagnoseeingang.
4. Vollstaendiger Scan, keine Deduplizierung wertgleicher Quellen.
5. Leeres Panel ohne leere numerische Reduktion.
6. Inklusive Grenzen und benachbarte Binary64-Werte.
7. Historische Summationsreihenfolge und Vollsichtdivisor 48.
8. ALL-BANDS-Teilmenge und unveraenderte Slow-Mittelwertbedingung.
9. Quellen-, Profil-, Zeit-, Typ- und Normalformfehler.
10. Unveraenderliche Eingaben und Ergebnisobjekte.
11. Vollstaendiger synthetischer Umfang 360/360 Befunde, 3840/3840 Differenzen.
12. Fehlende/vertauschte Quellen und manipulierte Teilprojektion.
13. Fehlende/vertauschte Ergebnisbelege.
14. Quellen-, Termindex-, Scan- und Statistikmanipulationen einzeln.
15. Selbstkonsistent manipulierte Terme gegen unabhaengige Baseline.
16. Statische Unabhaengigkeit der Baseline von Scan-/Entscheidungshelfern.
17. Beziehungsverlust trotz vorheriger Mehrdeutigkeit und falsch eindeutigem Rest.
18. Erhaltung, Verlust und Gewinn mit D=R+L ohne Verrechnung.
19. Leere Nenner und technisch gueltige Enthaltung.
20. Evaluationsbindung, tatsaechliche Variation je Sicht und Diagnosetrennung.
21. Konkrete Serialisierung und harte Ausgabe-/Panelbegrenzung.
22. Subnormale, ungueltige Werte und numerische statt Digest-only-Termausgabe.

Die synthetischen Quellen verwenden lediglich die literalen neutralen NP-IDs,
nicht deren PCM-Rezepte oder gemessene Rezeptorwerte. Keine NP-Payloads,
Rezeptor-, NJ-, Memory-, Feld-, Kontext- oder Runtimeaufrufe.

## Budgets und Stopps

Spaeter unveraendert: je Implementierung 120 Sicht-/Panel-/Cue-Scans mit drei
Bedingungen = 360 Panelbefunde, 360 regelgebundene Beziehungszeilen und 3840
Banddifferenzen. Beide Implementierungen zusammen 7680, kein Zusatzscan bei
der Verifikation. Vollstaendige leere Panels sind darin enthalten.

Neutrale Qualifikation: ein synthetisches Vollinventar pro Implementierung
plus kleine Einzelkontrollen, insgesamt hoechstens 16384 Banddifferenzen.
Diese separate Testobergrenze vergroessert kein spaeteres Korpusbudget.
Keine Retry-Schleife. Bei Nichtbestehen Ergebnis sichern und stoppen.

Ein einzelner Panelbeleg hoechstens 32768 Byte (enger privater Teilrahmen),
Metadaten 65536 Byte und gesamter spaeterer Ergebnisbeleg 2097152 Byte.
Der konkrete neutrale Groessencheck enthaelt beide vollstaendigen numerischen
Implementierungsbelege, Projektionen, Verifikation und Auswertung sowie
131072 Byte Materialisatreserve und 65536 Byte Metadatenreserve. Das historische
Materialisat hat 125094 Byte. Dies ist keine allgemeine Maximalgroessenbehauptung
fuer beliebige Floatdarstellungen; `bounded_payload` muss die tatsaechliche
Gesamtausgabe vor jeder spaeteren Veroeffentlichung pruefen. Kein Prozesspeakclaim.

Kein neuer Haupteinstieg oder Recorder. `MAIN_GATE=False`. Die reale Auswertung
braucht weiterhin eine eigene Freigabe; diese Qualifikation ist kein Befund zur
auditiven Abdeckung, Beziehungserhaltung oder Unbekanntheitserkennung.
