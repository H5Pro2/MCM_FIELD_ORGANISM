# HX1: Entwicklungsprotokoll der neutralen Vorbereitung

2026-10-04. Dokumentation des beauftragten Implementierungs-/Qualifikationspakets.
Kein Forschungsbefund. Der HX1-Vertrag bleibt unverändert.

## Umsetzung

Neue HX1-Module für gesperrte Quellenrezepte, getrennte globale Baselines,
unabhängige Beobachterreferenzen, rationale Auswertung, Windows-Job-Grenze
und exklusive Laufhülle. Der Produktionscode von U wurde nicht geändert.
Die bereits vorhandene unabhängige U-Bestandsreferenz und die neutralen
U-Zell-/Lebenszyklusprüfungen werden verwendet. D/N-Speicherbestände von U
werden nicht künstlich angeglichen; ausschließlich G besitzt die geforderte
positionsweise Gleichheitsinvariante auf Q.

## Kleine Entwicklungsprüfungen vor der gebundenen Qualifikation

- Ein neuer neutraler 32-Frame-Smokecheck für HX1-U/G/P, Abschluss und eigene
  Baseline-Heaps. Kein Forschungsstrom und kein vollständiger Größenablauf.
- Q1–Q7 zunächst als begrenzte Entwicklungsprüfung ausgeführt. Q1–Q6 bestanden;
  Q7 deckte einen Fehler im Abschlussweg des absichtlich übergroßen
  Windows-Speicherabrufs auf.
- Der 600-MiB-Abruf wurde vom Windows-Job abgewiesen. Der Job-Peakzähler war
  danach größer als das Limit; eine zusätzliche Ausnahme beim Auslesen
  verhinderte jedoch den beabsichtigten terminalen Fehlerabschluss.
- Korrektur ausschließlich in der HX1-Hülle: Job-Ablesung bleibt auch im
  Fehlerfall möglich; Grenzüberschreitungen führen zum Fehlerstatus statt
  zum Verlust des Abschlusses. Jeder Supervisorversuch erhält einen frischen
  verschachtelten Job, damit historische Fehlertest-Peaks nicht als Peak eines
  späteren Versuchs erscheinen. Bei erfolgreichem Abschluss darf auch der
  gemeldete Job-Peak das Limit nicht überschreiten.
- Betroffene Q7-Gruppe erneut ausgeführt: bestanden, einschließlich tatsächlicher
  Windows-Abweisung, vollständigem Fehlerabschluss und Neustartsperre.
- Vor der Codebindung außerdem externe Fehlerkontexte, kumulierte Differenzen,
  dominante Verfügbarkeit in D und unabhängige Aggregationskontrolle ergänzt.
  Danach gebundene Q1–Q7 vollständig bestanden. Diese Abschlussqualifikation
  prüft den final gebundenen Code, nicht den früheren Zwischenstand.

Keine Vertragsparameter geändert. Keine Forschungssaaten erzeugt, keine
Forschungsquellen abgespielt, keine Produktionsmemory erweitert. Der einzige
vollständige neutrale Größenablauf gehört zur gebundenen Qualifikation;
seine endgültigen Belege stehen im separaten Vorbereitungsbericht.
