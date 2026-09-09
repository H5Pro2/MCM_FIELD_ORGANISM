# S2-NU: korrigierte Vergleichsanbindung neutral qualifiziert

## Ergebnis

Qualifikations-ID: `s2nu-comparison-qualification-20260909-02`.
**S2NU_COMPARISON_QUALIFIED**, **22/22**, Exit-Code `0`.
Genau ein vollstaendiger vorregistrierter neutraler Testaufruf; kein Retry.
Alle 20 zuvor unerreichten Testkoerper sowie zwei hinzugefuegte
Bindungsregressionen wurden erreicht und bestanden.

[Vorregistrierung](preregistration.json), [Testprotokoll](stderr.txt),
[Ergebnisbeleg](result.json), [Ausgabehuelle](neutral-envelope.json).
Die vorab gebundenen Pruefgruppen und Budgets stehen in
[VERGLEICHSQUALIFIKATIONSBINDUNG.md](../VERGLEICHSQUALIFIKATIONSBINDUNG.md).

## Enger Aenderungsumfang

In `tools/_s2nu_private_comparison.py` wurden ausschliesslich zwei
Zaehleranforderungen von `14` auf den bereits vertraglich gebundenen Wert
`30` korrigiert: Materialisierungszaehler und `proof.materialized_sources`.
Keine allgemeine Lockerung; historische NT-Pruefungen unveraendert.

Die bisherigen 20 Testkoerper bleiben unveraendert. Neu hinzugekommen:

- Test 21: Jeder der sieben falschen Materialisierungszaehler wird mit
  frischer Belegkopie in eigenem `subTest` als `S2NUComparisonError` mit
  exakt `COUNTERS_INVALID` abgewiesen.
- Test 22: Falsches `materialized_sources` wird unabhaengig in eigener
  Testfunktion als `S2NUComparisonError` mit exakt
  `VERIFICATION_BINDING_INVALID` abgewiesen.

Die gueltige 30-Fenster-Bindung wird bereits im vollstaendigen Klassen-Setup
und in Test 01 angenommen. Die neuen Ablehnungen werden nicht durch
unpassende Anker- oder Digestfehler vorzeitig verdeckt.

Qualifikations-ID, Testinventar und die Qualifikationsanforderung des
geschlossenen Haupteinstiegs wurden auf den neuen 22-Test-Beleg gebunden.
Messung, Direktnachrechnung, Kontrollregeln und Auswertung blieben unveraendert.

Der alte Lauf `s2nu-comparison-qualification-20260909-01` bleibt dauerhaft
`NOT_QUALIFIED`; sein Klassen-Setup-Abbruch ist kein bestandener Teiltest.
Historische Ergebnisdateien und Quellversiegelung wurden nicht veraendert.

## Erreichte Pruefdeckung

Bestaetigt sind fuer die neutralen Fixtures: vier vorzeichenbehaftete
Uebergaenge je Fuenferfolge, aufsteigende Builtin-Summation, Konstanz,
Reihenfolgeaenderung bei gleichen Raendern und gleichem Multiset,
Multiplizitaet, Gleichstand und inverse Ordnung. Fehlende, vertauschte und
duplizierte Fenster sowie Profil-/Zeit-/Quellenmanipulationen werden abgewiesen.

Die Randmessung verwendet ausschliesslich zwei Vektoren; der ungeordnete
Arm ausschliesslich Profilbindung und kanonisch sortierte Vektorbytes.
Unerlaubte Herkunfts-/Zeitmetadaten werden abgewiesen. Primaere Messhelfer
wurden waehrend der Direktbaseline-/Verifikationspruefung durch Aufrufsperren
ausgeschlossen. Die numerischen neutralen Belege bleiben baselinegleich.

Primaererfolg verlangt beide tatsaechlich geprueften Kontrollgleichheiten
und striktes `T(s02)<T(s03)`. Ein Gleichstand trotz vier positiver deskriptiver
Kontrollen bleibt primaeres Nichtbestehen. Fehlende Rand- oder Multisetgleichheit
verhindert den Primarerfolg auch bei positiver T-Ordnung.
Auswertung ohne gueltige gebundene Verifikation wird abgewiesen.

Der komplette synthetische 30-Fenster-Gesamtbeleg einschliesslich Quellen,
Roh-/Halbwertbindungen, beider Implementierungen und Kontrollbelege erreicht
**513.889 Byte**, unter **2.097.152 Byte**. Verifikationshuelle: **615 Byte**;
Auswertung: **1.595 Byte**, jeweils unter **262.144 Byte**. Ueberschreitungen
und Schreibkonflikte wurden separat abgewiesen. Dies ist ein konkreter
Vollformtest, keine allgemeine Groessengarantie fuer andere Eingaben.

Die unveraenderten Grenzen des spaeteren Vergleichs sind separat gebunden:
2.880 Differenzen und 672 Kontrollkomponenten fuer beide Implementierungen.
Die zusaetzliche read-only Verifikation darf maximal 1.440 Halbierungen,
2.880 Termpruefungen, 72 Summen und 672 Kontrollkomponenten ausfuehren;
erst danach folgen fuenf Ordnungskriterien. Die neuen Regressionen fuegen
nur acht Bindungsablehnungen hinzu, keine weitere numerische Vergleichsarbeit.

## Digests und Grenzen

Ergebnisdigest:
`10d17e2c6868229fcde914ebbd0d2c3a76f41cd8092144c40e783a816633f360`.
Testprotokoll-SHA-256:
`d6be3be6de049ee5d9695f259e83bd33663f517a3d95597ee4bf48a4b00b7ba0`.
Ausgabehuellenbeleg-SHA-256:
`c70958eb9e5c341bc92797b9e3f03262a7997cd976f478552617af0fbb66e186`.

Alle 18 vorab gebundenen Dokument-/Quellhashes sind vor und nach dem Aufruf
identisch. Vollstaendige Hashliste im Ergebnisbeleg. Insbesondere:

- Korrigiertes Vergleichsmodul: `1a4f555852c3954569da1118b9ca7dba3b22a19c8233c5ecd0e23657cb6a3565`.
- Testdatei: `5f075233aa18fcc8179975c71526638422ca6fcedeb6b3daf8a7670e19132848`.
- Qualifikationseinstieg: `07d0eec46c9b3888c4df0f48d8dee87bc4eb569aada029db7b151a9544d6af4a`.
- Gebundener Haupteinstieg: `3d442f750670e0e7077a5a441c9b06dda2f22500fb9d9839631107873ea79592`.

Reale NU-Materialisierungsdateien waren durch Lesesperren ausgeschlossen.
Keine NU-Payloads, Rezeptor-/NJ-Aufrufe oder Memory-/Feld-/Runtimeausfuehrung.
Nur synthetische reduzierte Werte wurden verglichen. Gates nach dem Aufruf
`False`; fremde Aenderungen und Bootstrap bleiben ausgeschlossen.

**Ein realer NU-Verlaufsbefund liegt weiterhin nicht vor.** Insbesondere
werden reale Kontrollgleichheit, Primaerordnung, Quellenfortsetzung und
Lernbindung nicht behauptet. Naechster Vorschlag an den Analysten: die
vollstaendige neutrale Qualifikation lesen und separat ueber genau eine
Auswertung des bereits gespeicherten NU-Materialisats entscheiden.
