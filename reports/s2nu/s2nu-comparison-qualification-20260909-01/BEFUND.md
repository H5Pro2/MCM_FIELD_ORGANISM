# S2-NU: Vergleichsanbindung nicht qualifiziert

## Beobachteter Abschluss

- Qualifikations-ID: `s2nu-comparison-qualification-20260909-01`.
- Genau ein vorab gebundener neutraler Testaufruf; Exit-Code `1`.
- Ergebnis: **NOT_QUALIFIED**. Kein Retry, keine nachtraegliche Codekorrektur.
- 20 Testgruppen waren registriert; **0 Testkoerper erreicht**.
- Abbruch in `ComparisonQualification.setUpClass`, beim Binden des
  vollstaendigen synthetischen 30-Fenster-Materialisats.
- Fehlerklasse `S2NUComparisonError`, Code **COUNTERS_INVALID**.

[Vorregistrierung](preregistration.json), [Testprotokoll](stderr.txt),
[Ergebnisbeleg](result.json) und die vorab dokumentierten Grenzen in
[VERGLEICHSQUALIFIKATIONSBINDUNG.md](../VERGLEICHSQUALIFIKATIONSBINDUNG.md)
bleiben unveraendert erhalten.

## Konkrete Ursache

In `tools/_s2nu_private_comparison.py:127` verlangt die neue NU-Anbindung
bei den sieben Materialisierungszaehlern noch `14`, obwohl Plan, neutrale
Fixture und Materialisierung korrekt `30` Fenster binden. Diese erste
deterministisch verletzte Bedingung erklaert den dokumentierten Abbruch.

Die anschliessende lesende Kontrolle zeigt ausserdem in Zeile 129 noch
`proof["materialized_sources"] == 14`. Diese zweite falsche NU-Bindung wurde
im Lauf nicht mehr erreicht. Beide Stellen stammen aus der unvollstaendigen
Uebertragung der historischen NT-Zaehlerbindung. Es handelt sich um einen
Fehler der neuen privaten Eingangsvalidierung, nicht um ungueltige NU-Quellen,
einen Rezeptorfehler oder einen fachlichen Verlaufsbefund.

Die neue Bindung wurde nach dem Abbruch nicht geaendert. Eine spaetere
Korrektur muss ausschliesslich den bereits vorgegebenen 30-Fenster-Umfang
wiedergeben; sie waere keine Erweiterung der Arbeitsgrenzen.

## Implementiert, aber noch nicht qualifiziert

Vorbereitet sind geschlossene unveraenderliche Eingabetypen fuer die
geordnete Folge, die beiden Randvektoren und das profilgebundene sortierte
Multiset. Die Messung verwendet nur Halbwerte; rohe Werte bleiben in den
Herkunftsbelegen und fuer die separat budgetierte Halbierungspruefung.

Primaere Rechnung, unabhaengige Direktrechnung, technische Verifikation
und nachgelagerte fuenf Ordnungskriterien sind getrennt angebunden.
Primaererfolg soll beide Kontrollgleichheiten und `T(s02)<T(s03)` verlangen;
die vier beschreibenden Befunde sollen primaeres Nichtbestehen nicht ersetzen.
Der geschlossene Haupteinstieg fordert einen bestandenen Qualifikationsbeleg.

**Keine dieser Verhaltensaussagen ist durch diesen Testlauf qualifiziert.**
Auch die neutrale Vollausgabehuelle wurde nicht erreicht;
`envelope_sha256` bleibt `null`. Es wurde kein positiver Teilbefund aus einem
nicht erreichten Test abgeleitet. Der reale Vergleich bleibt gesperrt.

## Bindungen und Ausschluesse

Ergebnisdigest:
`69877582c9783cc71dcda806b3cec6919f18e147820ba9ef0fdee1f0ed901a34`.
Testprotokoll-SHA-256:
`e41e189f9fb0025f1acbd2cbd7d6105d9fd5489ba0e340dbe449c02bc3d3ef79`.
Betroffenes Produktmodul-SHA-256:
`2844ad18025c664df71011b50d4c88e3fed49aadf6391b1c11a138dbb49afbfc`.
Testdatei-SHA-256:
`c8e50df2d137594d74a812535c1154841f888b83c1f6db4353950b9b3df06535`.
Alle 18 vorab gebundenen Dokument-/Quellhashes stimmen vor und nach dem
einmaligen Aufruf ueberein; vollstaendige Tabelle im Ergebnisbeleg.

Der Testprozess hatte Lesesperren fuer reale NU-Materialisierungsdateien
und eine Aufrufsperre fuer NU-Payloadgenerierung. Ausschliesslich synthetische
reduzierte Werte wurden fuer das Klassen-Setup erzeugt. Der Abbruch liegt
vor der ersten zeitlichen Differenzberechnung, Direktrechnung oder Bewertung.

Reale NU-Vektoren gelesen/verglichen: `0`. PCM-, Rezeptor-, NJ- und
Systemaufrufe: jeweils `0`. Quellengate und Vergleichshauptgate `False`.
Materialisierung, Versiegelung, historische Belege, ME/MI, fremde Aenderungen
und Bootstrap bleiben unveraendert.

**RUECKMELDUNG ERFORDERLICH:** Vorschlag ist die eng begrenzte Freigabe zur
Korrektur beider 14er-Zaehlerbindungen auf den bereits festgelegten Wert 30
und danach genau einer neuen vollstaendigen neutralen Qualifikation unter
neuer ID. Kein neuer Vertrag und keine reale NU-Auswertung sind damit freigegeben.
