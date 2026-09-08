# S2-NT: Vergleichsanbindung neutral qualifiziert

## Beobachteter Abschluss

- Qualifikations-ID: `s2nt-comparison-qualification-20260908-01`.
- Genau ein vorregistrierter Testaufruf, **18/18**, Exit-Code `0`, kein Retry.
- Status: `S2NT_COMPARISON_QUALIFIED`.
- Ergebnisdigest: `39451836dd23d9e659d4489ab531c16d1a41e0d803ffbd23873b6581d162ced4`.
- Testprotokoll-SHA-256: `293d09d16978f3ea189b9cda7c347dc5922a55efb3736a13ae741f165ba63d86`.
- Alle vorab gebundenen Quellhashes vor/nach dem Aufruf identisch.
- Keine realen NT-Vektoren gelesen oder verglichen, keine PCM-Erzeugung,
  Rezeptor-/NJ-Wiederholung oder Systemaufrufe. Haupt- und Quellgate `False`.

Das vollstaendige Inventar, die Interpreter-/Umgebungsbindung und Quellhashes
stehen in `preregistration.json`; Ergebnis und Hashvergleich in `result.json`.
`stderr.txt` enthaelt alle 18 unabhaengig erreichten Testkoerper und `OK`.
Die bisherige NT-Vorversiegelung und Materialisierung wurden nicht veraendert.

## Kleine private Anbindung

`tools/_s2nt_private_comparison.py` bindet Quellen, Zeitfenster, Profile,
Roh-/Projektionsdigests und die bereits bestehende Materialisierungspruefung.
Es verarbeitet exakt die 25 literalen Paare. Einzelterme behalten ihre
Originalindizes 0..47. Die Rechnung lautet unveraendert
`sum(abs(q[i]-r[i]) for i in range(48))/48`, mit dem gebundenen Python-Builtin.
Weder `statistics.mean` noch eine andere Akkumulationsregel wird eingefuehrt.

`tools/_s2nt_private_comparison_verification.py` enthaelt eine eigene direkte
Termrechnung ohne produktiven Distanzhelfer. Die anschliessende Offline-Pruefung
prueft gespeicherte Quellen, Halbierungen, Originalindizes, Terme, Summen und
Roh-/Halbgleichheit; sie erzeugt keine neuen Quellpaare oder Rezeptorwerte.

`tools/_s2nt_private_order_evaluation.py` wertet erst nach erfolgreicher
technischer Verifikation aus: acht primaere, vier Zuordnungs- und zwoelf
Kontrollbedingungen. LT, EQ und GT bleiben getrennt. Addition, Ersetzung,
unabhaengige Kontrollen und Referenzkontrollen werden getrennt aufgefuehrt;
Pegel-/Frequenzvarianten und Exaktkopien bleiben einzeln identifizierbar.

`tools/_s2nt_private_comparison_run.py` bindet den vorhandenen NT-Dateipfad
an feste Vertrauenswurzeln, geschlossenen Einmaleinstieg, atomare Publikation
und getrennte Verifikations-/Auswertungseintritte. Keine neue Recorderplattform.
Der reale Lader und Haupteinstieg wurden nicht ausgefuehrt; die Gateablehnung
vor dem ersten Dateizugriff ist neutral geprueft.

## Nachgewiesene neutrale Kontrollen

Vollstaendige Quellen-/Paarbindung; manipulierte Quellen, Zeitformen,
Profile und Digests; endliche Werteformen; historische Summation; unabhaengige
Direktbaseline; strikte Ordnung, Gleichstand und Umkehrung; nominale Variante
ohne geaenderte Werte; Roh-/Halbkollision; manipulierte Gleichheit und Terme;
Halbierungsfehler; Auswertungssperre; Unveraenderlichkeit; vollstaendige
Artefakthuelle samt Quellhash-/Laufabschlussfeldern; Groessen- und Schreibkonflikte.

Der synthetische Kollisionsfall bindet einen kleinsten positiven Subnormalwert
gegen null an Position 47. Unterschiedliche Rohwerte werden nach Halbierung
bitgleich und bleiben als Halbierungskollision ausgewiesen. Dies ist kein
NT-Korpusbefund. Ein nominaler Pegelfall ohne Wertewechsel zaehlt trotz gueltiger
Metadaten nicht als Variationsnachweis. Exaktkontrollen fuellen diesen Nachweis
nicht auf. Gemaess Plan werden keine Zulassungsentscheidungen daraus abgeleitet.

## Arbeit und Artefaktgrenzen

Pro spaeterem Realvergleich bleiben 1.200 primaere und 1.200 direkte
Banddifferenzen sowie separat 2.400 Roh-/Halbgleichheitskomponenten gebunden.
Die unabhaengige Offline-Pruefung ist zusaetzliche Arbeit: maximal 672
Vorwaertshalbierungen, 2.400 Termpruefungen, 2.400 Gleichheitskomponenten und
50 Summen. Die 24 fachlichen Ordnungskriterien folgen getrennt aus gespeicherten
Distanzen; sie verursachen keine neuen Banddifferenzen.

Gesamtbeleg maximal 2.097.152 Byte, Verifikationsbeleg maximal 262.144 Byte.
Die neutralen Suite-Obergrenzen wurden separat vorregistriert; sie veraendern
keine Grenzen des kuenftigen Einmallaufs. Die vollstaendige neutrale Huelle
liegt innerhalb der Grenze; ein uebergrosses Artefakt wird abgewiesen.

## Grenzen und naechste Entscheidung

Dies ist ausschliesslich ein technischer Anschlussbefund. Die echten 25
NT-Distanzen, Vektorpaarvergleiche und 24 Ordnungskriterien bleiben unausgewertet.
Keine Trennleistung, Bestandteilserkennung, semantische Identitaet oder
Zulassungsschwelle ist nachgewiesen. Fehlende L1-Ordnungsseparation und konkrete
Repraesentationskollisionen werden ausdruecklich nicht gleichgesetzt.

Die reale Verarbeitung der gespeicherten NT-Werte bleibt separat freizugeben.
Historische Belege, fremde Aenderungen und Bootstrap bleiben ausgeschlossen.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser neutralen
Qualifikation und der separaten Entscheidung ueber die einmalige NT-Auswertung weiter.
