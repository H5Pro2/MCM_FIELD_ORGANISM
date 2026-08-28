# Visuelle L1-Kalibrierung: Bestaetigung und getrennte Grenzdiagnose

## Ergebnis

**Die einfache Kalibrierung genuegt fuer den vorab definierten endlichen
Aufgabenumfang.** L1-KAL mit exakt `44/765` beantwortet alle 36 Pflichtproben
auf K1-K3 richtig: 18 Wiedererkennungen und 18 Abweisungen. Keine falsche
Ablehnung, keine Fehlgleichsetzung und keine falschen Rueckgabewerte.
Die Schwelle wurde technisch aus Entwicklungsdaten und Aufgabengrenze
vorgegeben, nicht von MCM erlernt.

L1-ALT mit unveraendertem `0.2` hat im selben Pflichtumfang zwoelf
Fehlgleichsetzungen. Beide Regeln erhielten dieselben gespeicherten
Zustaende und Probeinputs. Nur die visuelle Annahmeschwelle unterscheidet sich.

## Tatsaechlicher Umfang und Abnahme

- Acht von acht fokussierten Tests bestanden, Exit-Code 0. Keine Bildanalyse,
  B4-Bildung oder Matrixausfuehrung innerhalb dieser Qualifikation.
- Genau ein Hauptversuch: **56 Bildanalysen, acht echte B4-Bildungen,
  48 Probeinputs und 96 read-only Regelabrufe**, Exit-Code 0.
- 320 vollstaendige verkettete Start-/Ergebnisrecords. Alle acht Episoden
  beginnen mit einer frischen Bank und genau einer tatsaechlichen Bildung.
- Quellen, Entwicklungsbelege, Bruchwert, Konfiguration und neue Bildpaare
  waren vor der ersten Bildanalyse gebunden. Keine Schwellenanpassung.
- Gespeicherte Zellwerte entsprechen den Rezeptorausgaben. Alle Proben
  lassen die Bank unveraendert; bei Annahme werden die gespeicherten Werte
  zurueckgegeben, nicht die verschobenen Probeinputs.
- Die gesonderte Pruefung las ausschliesslich gespeicherte Belege. Guards
  protokollieren null weitere Rezeptor-, Bildungs-, Abruf- oder Matrixaufrufe.
- Keine Wiederholung oder Teilfortsetzung. Der private Einstieg ist nach
  Abschluss wieder gesperrt. Seine aktive Quellfassung bleibt im Manifest erhalten.

## Pflichtfaelle K1-K3

Je Satz und Regel: beide Speicherrichtungen, Original und Tausch jeweils
mit Delta 0, -8 und +8. Jede Zeile umfasst zwoelf Entscheidungen.

| Satz | Regel | Richtige Wiedererkennung | Richtige Abweisung | Fehlgleichsetzung | Falsche Ablehnung |
|---|---|---:|---:|---:|---:|
| K1, Kontrast 64 | L1-ALT | 6 | 0 | 6 | 0 |
| K1, Kontrast 64 | L1-KAL | 6 | 6 | 0 | 0 |
| K2, Kontrast 96 | L1-ALT | 6 | 0 | 6 | 0 |
| K2, Kontrast 96 | L1-KAL | 6 | 6 | 0 | 0 |
| K3, Kontrast 160 | L1-ALT | 6 | 6 | 0 | 0 |
| K3, Kontrast 160 | L1-KAL | 6 | 6 | 0 | 0 |
| Gesamt | L1-ALT | 18 | 6 | 12 | 0 |
| Gesamt | L1-KAL | 18 | 18 | 0 | 0 |

Rueckgabefehler: null in beiden Regeln. Alle auditiven Distanzen sind null.
Die folgenden visuellen Distanzen wurden in beiden Richtungen gemessen:

| Eingang | K1 | K2 | K3 | G1 |
|---|---:|---:|---:|---:|
| Original, Delta 0 | 0 | 0 | 0 | 0 |
| Original, Delta -8 oder +8 | 0.0313725490 | 0.0313725490 | 0.0313725490 | 0.0313725490 |
| Tausch, Delta 0 | 0.0836601307 | 0.1254901961 | 0.2091503268 | 0.0313725490 |
| Tausch, Delta -8 oder +8 | 0.1045751634 | 0.1464052288 | 0.2300653595 | 0.0522875817 |

Die Tabelle rundet nur die Anzeige. Alle Rohdistanzen stehen vollstaendig
in `events.jsonl` und `verification.json`; ausgefuehrt wurde mit `44/765`.
Die rein diagnostische zulaessige Schwellenluecke der Pflichtfaelle ist
`[0.03137254901960784, 0.08366013071895424)`. Es wurde daraus keine neue
Schwelle ausgewaehlt. Der zuvor gebundene Wert liegt innerhalb der Luecke.

## G1: vollstaendig getrennte Grenzdiagnose

G1 hat Kontrast 24 und liegt damit unter der verpflichtenden Mindestgrenze 64.
Seine zwoelf Entscheidungen pro Regel werden nicht in den Primaerwert aufgenommen:

| Regel | Original erkannt | Tausch abgewiesen | Tausch gleichgesetzt | Falsche Ablehnung | Rueckgabefehler |
|---|---:|---:|---:|---:|---:|
| L1-ALT | 6 | 0 | 6 | 0 | 0 |
| L1-KAL | 6 | 0 | 6 | 0 | 0 |

In jeder Richtung sind alle drei Originalproben und alle drei Tauschproben
angenommen worden. Die diagnostischen Fehlgleichsetzungen werden weder
ausgeblendet noch dem primaeren Erfolg zugerechnet.

Der unveraenderte G1-Tausch und eine erlaubte globale +/-8-Verschiebung
haben **denselben gemessenen Abstand `0.03137254901960784`**. Eine einzige
L1-Schwelle kann diese beiden Faelle nicht verschieden entscheiden.
Dies bestaetigt die vorregistrierte Grenze einer Aufgabenerweiterung auf
solche schwachen Tausche. Eine weitere Absenkung allein loest sie nicht:
Sie wuerde zugleich die geforderte Intensitaetstoleranz verletzen.

Die Ortsinformation bleibt auch fuer G1 im Rezeptor und Speicher erhalten.
Die Gleichsetzung ist eine Grenze der skalaren Abrufentscheidung, kein
Informationsverlust und kein Grund, vorsorglich den Speicher umzubauen.
Erst wenn Tausche unterhalb der festgelegten Mindestgrenze zwingend zu
unterscheiden sein sollen, ist eine getrennte Helligkeits-/Ortsbewertung
als neue, gesondert zu entscheidende Aufgabe begruendet.

## Kosten und technische Grenzen

- Acht Bildungen: 232 funktionale Schreibwoerter; Proben schreiben nichts.
- Pro Regel 48 Abrufe und 1248 funktionale L1-Terme, insgesamt 2496.
  Zusaetzlich insgesamt 2496 live L1-Validierungsterme.
- Pro Abruf 26 funktionale plus 26 Validierungsterme, unter Grenze 234.
  Pro Bildung 29 funktionale Schreibwoerter, unter Grenze 293.
- Unveraendert neun Plaetze und Ressourcenmaximum 255 logische Woerter je
  Bank; ein belegter Platz in jeder Episode.
- Jede Bildanalyse verarbeitet 28800 Kanalwerte. Globale Mittelwert- und
  Histogrammkontrolle haben jeweils weitere 28800 Kanalwerte je Bild;
  diese Kontrollarbeit zaehlt nicht als Speicher- oder Abrufleistung.
- Laufinterne Zeit etwa 0.82 Sekunden. Prozessspeicherspitze nicht gemessen.
  Recordpruefung, Quellhashes und IO sind von funktionalen Kosten getrennt;
  logische Woerter sind kein RAM-Messwert.

Rezeptor, B4-Kern, urspruengliche Abruffunktion, PPB-1, TSPM-1, API, Snapshot
und Feldpfad blieben unveraendert. A/B/C wurden nur als aufgezeichnete
Entwicklungsdaten gelesen, nicht erneut ausgefuehrt. S2-FC, alte Matrix-
und Plattformpfade bleiben gesperrt.

## Einordnung und naechster Schritt

**Beobachtung:** Die technisch vorgegebene Schwelle trennt in den neuen,
vorregistrierten Pflichtfaellen tolerierte Intensitaetsabweichung und
verlangte Ortsaenderung ohne neue Fehlablehnung.

**Engineeringfolgerung:** Fuer diese Aufgabe genuegen vorhandene ortsgebundene
Werte, B4 und eine passende read-only Annahmeschwelle. Keine komplexere
Abrufregel oder neue Speichermechanik ist hier notwendig.

**Nicht geprueft:** zufaellige oder externe Bildverteilungen, beliebige Farben,
Zellinnenstruktur, Ansichtsunabhaengigkeit, Objekte, selbststaendiges Lernen,
laengerfristige Verdichtung und zeitliche Reihenfolge. Die neuen Paare sind
prospektiv registrierte technische Beispiele, keine verblindete Stichprobe.

Empfehlung: Die begrenzte Kalibrierung als private Arbeitsreferenz fuer
diese Aufgabe behalten. Als getrennte naechste Repraesentationsfrage bietet
sich zeitliche Reihenfolge bei gleichen Einzelzustaenden an, zunaechst als
kleiner Aufgabenplan. G1 begruendet keine automatische Erweiterung der Aufgabe.
Keine weitere Ausfuehrung oder Integration ist durch diesen Befund freigegeben.

## Pruefbelege

- [Qualifikation](../calibration-qualification-20260828-01/result.json) und
  [vollstaendiges Testprotokoll](../calibration-qualification-20260828-01/output.txt)
- [Startmanifest mit Quellbytes](manifest.json), [alle Ereignisse](events.jsonl),
  [Ergebnis](result.json), [Abschluss](terminal.json), [read-only Nachpruefung](verification.json),
  [dokumentierte Einstiegssperre](closure.json)
- [Freigabe](../calibration-20260828-01.authorization.txt) und
  [Ausfuehrungsstand](../calibration-20260828-01.prestart.md)

Ergebnisdigest: `f51bf35e381813c767430e453260e9cf93651be42331e659705195f3b919c93a`.
Nachpruefdigest: `f098111574ae2dce3ba16f66036437e428109612a086e1493757f38e91ef7e56`.
