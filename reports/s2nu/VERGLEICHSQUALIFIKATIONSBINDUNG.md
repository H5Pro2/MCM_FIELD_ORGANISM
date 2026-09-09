# S2-NU: vorgebundene neutrale Vergleichsqualifikation

Qualifikations-ID: `s2nu-comparison-qualification-20260909-01`.
Genau ein `unittest`-Aufruf, 20 Gruppen, failfast, kein Retry. Kein Zugriff
auf reale NU-Materialisierungsdateien, keine PCM-/Rezeptor-/NJ-Ausfuehrung.
Quellplanmetadaten sind erlaubt; numerische Eingaben ausschliesslich literal
synthetische reduzierte Vektoren, keine aus NU-Rezepten abgeleiteten Werte.

## Inventar

1. Vollstaendige sechs Stroeme mit 30 gebundenen synthetischen Zustaenden.
2. Konstante Folge.
3. Geaenderte Reihenfolge bei gleichen Raendern und identischem Multiset.
4. Vorzeichen und historische aufsteigende Builtin-Summation.
5. Randarm ohne Zugriff auf Zwischenwerte.
6. Geschlossene ungeordnete Eingabe ohne Herkunfts-/Zeitmetadaten.
7. Multiplizitaet und unvollstaendiges Multiset.
8. Primaererfolg als Konjunktion aller drei erforderlichen Befunde.
9. T-Gleichstand trotz vier bestandener deskriptiver Kontrollen.
10. Inverse primaere Ordnung.
11. Jede fehlende Kontrollgleichheit verhindert den Primarerfolg.
12. Fehlende, vertauschte und duplizierte Fenster.
13. Manipulierte native Zeit-/Uhrbindung.
14. Profilverwechslung und ungueltige Zahlen nur am Wertevalidator.
15. Manipulierte Quellen-/Ankerbindung.
16. Manipulierte Terme, durchgereichte Metadaten und Kontrollbefunde.
17. Unabhaengige Direktnachrechnung und Nachpruefung ohne primaere Helfer.
18. Vollstaendige synthetische Ausgabehuelle und Groessenabweisung.
19. Geschlossener Haupteinstieg, Schreibkonflikt, technischer Fehlerabschluss.
20. Auswertungssperre vor gueltiger Verifikation und Unveraenderlichkeit.

## Funktionale Grenzen

`OrderedView`: nur Halbprofil und fuenf Halbvektoren in gepruefter Reihenfolge.
`EndpointView`: nur Halbprofil und die beiden Randvektoren.
`UnorderedView`: nur Halbprofil und fuenf sortierte `<48d`-Bytevektoren.
Alle drei Typen sind eigene unveraenderliche, geschlossene Datentypen.
Herkunft und Zeiten bleiben ausserhalb ihrer funktionalen Eingaben in der
Gesamtbelegbindung. Raw-Werte dienen dort nur Integritaet und der separat
budgetierten Vorwaertshalbierungspruefung, nicht der Verlaufsmessung.

Kein Kontrollarm erhaelt Erzeugungskategorien. Es werden keine Frequenzspuren,
Quellenidentitaeten oder Lernbindungen ausgegeben. Keine Glaettung, Gewichtung,
Toleranz, Schwelle, Maskenwahl oder Uebergaenge zwischen Stroemen.

## Endlicher Umfang

Je spaeterem Vollvergleich unveraendert: je Implementierung 24 Uebergaenge
und sechs Randvergleiche, also 1.440 Differenzen; gemeinsam 2.880.
Kontrollgleichheit je Implementierung 96 Rand- und 240 Multisetkomponenten,
gemeinsam 672. Unabhaengige read-only Nachpruefung separat maximal 1.440
Vorwaertshalbierungen, 2.880 Termpruefungen, 72 Summen, 672 Kontrollgleichheiten.
Erst danach fuenf Ordnungskriterien.

Die neutrale Suite umfasst hoechstens sechs vollstaendige Vergleiche,
zwei einzelne geordnete Messungen, zwei einzelne Randmessungen und eine
einzelne Direktmessung: maximal 18.000 Banddifferenzen und 4.032
Kontrollgleichheitskomponenten. Maximal zehn numerische Verifikationsversuche:
14.400 Halbierungen, 28.800 Terme, 720 Summen, 6.720 Kontrollgleichheiten.
Sechs erfolgreiche Auswertungen, maximal 30 Ordnungskriterien; ein gesperrter
Auswertungsaufruf erreicht keine Ordnung. Weitere frueh abgewiesene Formen
duerfen diese Arbeit nicht ausloesen. Keine realen NU-Vergleiche.

Ausgabehuellentest: alle 30 synthetischen Quellen, Rohzustaende, Hex-/Byte-
und NJ-Belege, native Zeiten, Profile/Baender, Elternwurzeln sowie je sechs
primaere/direkte Strommessungen und vollstaendige Kontrollbelege. Einschliesslich
Lauf-ID und Quellhashhuelle; kein einfacher Groessenplatzhalter. Die dabei
gemessenen kanonischen Groessen werden als `neutral-envelope.json` gespeichert.
Dies ist ein konkreter Vollformtest, keine mathematische Groessengarantie
fuer beliebige andere Nutzlasten. Produktionspruefungen weisen Ueberschreitungen ab.

Metadaten maximal 65.536 Byte, Gesamtbeleg 2.097.152 Byte, Verifikations- und
Auswertungsbeleg jeweils 262.144 Byte. Keine Grenzerhoehung. Schreibkonflikte
werden vor Publikation abgewiesen. Die neue Laufbindung bleibt `MAIN_GATE=False`;
ein spaeterer realer Vergleich bedarf separater Freigabe und neuer Lauf-ID.
