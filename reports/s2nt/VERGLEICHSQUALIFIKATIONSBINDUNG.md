# S2-NT: neutrale Vergleichsqualifikation

Prospektive Bindung fuer `s2nt-comparison-qualification-20260908-01`.
Genau ein Aufruf von `python -m unittest tests.test_s2nt_private_comparison -v -f`.
18 Testkoerper; kein Retry. Das AST-Inventar und alle Quellhashes werden vor dem
Aufruf in `preregistration.json` gebunden. Bei Fehlern wird gestoppt.

## Eingabegrenze

Nur synthetische reduzierte Zahlenwerte. Die literalen Quellen-, Zeit-, Paar-
und Bewertungsmetadaten duerfen verwendet werden. Keine NT-Payloadgenerierung,
kein Lesen oder Vergleichen der realen NT-Vektoren, keine Rezeptor-/NJ-Aufrufe,
keine Memory-, Kontext-, Feld- oder Runtimefunktionen. Der reale Dateilader
prueft zuerst das geschlossene Gate. Historische Komponenten bleiben unveraendert.

Die synthetischen Quellenbelege sind ausdruecklich keine Erzeugungsbelege.
Sie pruefen Form-, Digest- und Zeitvertraege, nicht die Herkunft echter Messwerte.
Der spaetere Dateilader bindet dagegen die drei unveraenderlichen historischen
Plan-/Materialisierungs-/Verifikationsdigests und die versiegelten Dateihashes.

## Rechenbindung und Grenzen

Je spaeterem Vergleich: exakt 25 Paare pro Implementierung, aufsteigende
Originalindizes 0..47; `sum(abs(q[i]-r[i]) for i in range(48))/48`.
Python-Build und Interpreter bleiben aus der Versiegelung gebunden. `sum`
ist der Python-Builtin, weder `statistics.mean` noch eine selbst programmierte
sequentielle Akkumulation. Die unabhaengige Direktnachrechnung bildet eigene
Terme und verwendet ebenfalls den gebundenen Builtin.

- Primaer: 1.200 Differenzen; direkt: 1.200; zusammen 2.400.
- Roh-/Halb-Bitgleichheit separat im Primaerbeleg: 2.400 Komponentenpruefungen.
  Die numerische Direktbaseline berechnet keine zweite Gleichheitstabelle.
- Unabhaengige Offline-Verifikation separat: 672 Vorwaertshalbierungen aus
  gespeicherten Rohwerten, 2.400 Termpruefungen, 2.400 Gleichheitspruefungen,
  50 Summen. Keine Rekonstruktion von Rohwerten aus Halbwerten.
- Nach technischer Verifikation: 24 strikte Ordnungskriterien aus gespeicherten
  Distanzen. Keine zusaetzlichen Banddifferenzen. Gleichstand ist keine Trennung.
- Gesamtbeleg inklusive eingebetteter Quellen-/Roh-/Projektionsbelege und
  beider Termtabellen: maximal 2.097.152 Byte. Verifikationsbeleg: 262.144 Byte.

Die neutrale Suite bindet hoechstens vier komplette Vergleichsrechnungen,
zwei einzelne Paarnachrechnungen, neun Verifikationsversuche (einschliesslich
frueher Abweisungen), vier erfolgreiche Auswertungen und drei direkte
Ordnungspruefungen. Somit maximal 9.696 neutrale Banddifferenzen, 9.696
primaere Gleichheitskomponenten, 6.048 Offline-Halbierungen, je 21.600
Offline-Term-/Gleichheitspruefungen, 450 Offline-Summen und 99 Ordnungstests.
Dies sind Suite-Obergrenzen, keine erhoehten Grenzen eines spaeteren Reallaufs.

## Pruefgruppen

1. Vollstaendige Bindung, 14 synthetische Quellen, 25 Paare je Arm.
2. Falsche Vertrauenswurzel und manipulierter Materialisierungsdigest.
3. Manipulierte Quellenherkunft trotz intern neu gebundener synthetischer Belege.
4. Snapshot, Fenstertyp und fremde Uhr, unabhaengige Unterkontrollen.
5. Profilverwechslung und ungueltige Werte einschliesslich Inf/NaN vor JSON.
6. Fehlende, vertauschte und doppelte Paare.
7. Historische Builtin-Summation und numerische Originalindex-Terme.
8. Direkte Nachrechnung bei gesperrtem primaeren Distanzhelfer.
9. Strikte, gleiche und invertierte Ordnung; 24 getrennte Befunde.
10. Nominale Variante ohne Wertwechsel; Exaktkontrollen getrennt.
11. Konkrete Halbierungskollision bei verschiedenen Rohwerten.
12. Manipulierte Vektorgleichheit.
13. Halbierungsfehler aus gespeicherten Rohwerten unabhaengig erkannt.
14. Manipulierter Originalindex und Einzelterm, frische Kopien.
15. Manipulierte Direktbaseline; Auswertung vor Verifikation gesperrt.
16. Vollstaendige neutrale Artefakthuelle, Groessenabweisung und Schreibkonflikt.
17. Unveraenderlichkeit von Eingaben und Belegen.
18. Geschlossener Reallader und Ausschluss von Sensor-/Systemimporten.

## Aussagegrenze

Eine bestandene Qualifikation erlaubt noch keine NT-Auswertung. Sie zeigt nur
die neutrale Anschlussfunktion. Addition, Ersetzung und unabhaengige Kontrollen
werden getrennt berichtet. Bitkollisionen und fehlende L1-Ordnungsseparation sind
unterschiedliche Aussagen. Keine Zulassungsschwelle, Bestandteilserkennung oder
semantische Identitaet wird daraus abgeleitet. Alle Gates bleiben `False`.
