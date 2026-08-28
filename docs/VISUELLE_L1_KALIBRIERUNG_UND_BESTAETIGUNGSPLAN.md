# Visuelle L1-Kalibrierung und getrennte Bestaetigung

**Status: nur Planung, keine Implementierung oder Ausfuehrung.** Grundlage:
Commit `6967659` und der unveraenderte
[Ortsstrukturbefund](../reports/tspm1_functional/spatial-20260828-01/BEFUND.md).
Ziel ist die Nutzbarkeit vorhandener Speicherwerte, nicht ein neuer Speicher.

## 1. Verbindliche Aufgabe

Das bestehende Profil bleibt: 120 x 80 RGB-Pixel, 3 x 2 Zellen zu je 40 x 40
Pixeln, 18 geordnete visuelle Werte; auditiv immer achtmal null. Alle drei
Kanaele einer Zelle haben denselben konstanten Intensitaetswert.

- **Gleiches Muster:** unveraenderte Zellanordnung mit einer einheitlichen
  ganzzahligen Intensitaetsverschiebung von -8 bis +8, ohne Clipping.
  Endlich geprueft werden -8, 0 und +8, in beiden Speicherrichtungen.
- **Zwingend anderes Muster:** Tausch genau zweier ganzer Zellen, deren
  Ausgangswerte sich um **mindestens 64 von 255 Intensitaetsstufen** unterscheiden.
  Auch mit anschliessender globaler Verschiebung -8, 0 oder +8 muss die
  geaenderte Anordnung unterschieden werden. Histogramm und Gesamthelligkeit
  bleiben bei gleichem Delta zwischen den Anordnungen gleich.
- Die Mindestgrenze bedeutet eine Aenderung von mindestens 64/255 in sechs
  der 18 Komponenten vor dem globalen Offset. Sie ist eine ausdrueckliche
  technische Aufgabenspezifikation, keine biologische Wahrnehmungsschwelle.
  Kleinere Ortsaenderungen erhalten **keine automatische Anders-Klassifikation**.
  Unterschiede innerhalb einer Rasterzelle, Farben und beliebige lokale
  Intensitaetsstoerungen sind nicht Gegenstand dieser Aufgabe.

## 2. Kalibrierung vor jeder Bestaetigung festschreiben

A/B/C und die 24 aufgezeichneten Proben des alten Ortsarms sind ausschliesslich
bekannte Entwicklungsdaten. Sie werden spaeter nur gelesen, nicht neu erzeugt.
Der alte Bericht mit sechs Fehlgleichsetzungen bleibt unveraendert; eine
neue Entwicklungsrechnung ist kein nachtraeglicher Erfolg des alten Versuchs.

Verglichen werden genau zwei read-only Regeln:

| Regel | Auditive Schwelle | Visuelle Schwelle | Sonstige Unterschiede |
|---|---:|---:|---|
| L1-ALT | 0,2 | 0,2 | keine |
| L1-KAL | 0,2 | `44/765`, etwa `0,05751634` | keine |

Beide verwenden dieselbe bestehende normalisierte mittlere L1-Distanz,
dieselbe inklusive Annahme `Distanz <= Schwelle`, dieselben Tie-Regeln und
dasselbe gespeicherte Tupel. Es gibt keine Offsetkorrektur, keine neue
Merkmalsgewichtung und keine Helligkeits-/Ortszerlegung im Abruf.

**Einmalig festgelegtes Auswahlverfahren, ohne Suche auf Bestaetigungsdaten:**

1. U ist der groesste bekannte positive Entwicklungsabstand: `8/255`.
2. Der kleinste bekannte negative Entwicklungsabstand ist `128/765`.
   Die vorab verlangte Mindestunterscheidbarkeit begrenzt diesen Wert weiter:
   Bei zwei vertauschten Grauwertzellen mit Kontrast D ist der kleinste
   mittlere Abstand ueber die zulaessigen globalen Offsets `D/(3*255)`.
   Fuer D >= 64 gilt daher die Aufgaben-Untergrenze `64/765`.
3. L ist das Minimum aus negativer Entwicklungsgrenze und Aufgaben-Untergrenze,
   also `64/765`. Zulaessig ist das Intervall **[U,L)**. Nur bei U < L wird
   dessen Mittelpunkt verwendet: `(U+L)/2 = 44/765`. Keine Rundung auf ein
   nachtraeglich ausgewaehltes Schwellenraster.

Diese Auswahl ist **entwicklungsdaten- und aufgabengebunden**, nicht allein
aus A/B/C gelernt. Die Mindestgrenze wird nicht aus den spaeteren Treffern
abgeleitet. Abweichende Entwicklungsbelege oder ein leeres Intervall stoppen
die Vorbereitung; kein automatischer Ersatzwert. Die vorhandene Genauigkeit
`1e-12` dient nur numerischen Beleg-/Intervallpruefungen, nicht als zusaetzliche
Erkennungsregel. Die auditive Schwelle wird mangels Audioaufgabe nicht kalibriert.

Vor der spaeteren Bestaetigung werden Quellen, Entwicklungsbelege,
Mindestgrenze, Bruchwert der Schwelle, Regeln und nachstehende Eingabetabelle
in einem unveraenderlichen Startbeleg gebunden. Keine Auswahl des besten
Wertes nach Sichtung der neuen Abrufe.

## 3. Neue, fest gebundene Eingaben

Alle Zahlen bezeichnen Zellintensitaeten; Koordinaten sind nullbasiert
`(Zeile,Spalte)`. Die zweite Anordnung entsteht ausschliesslich durch den
genannten Tausch. Alle acht Anordnungen sind verschieden von A/B/C und
voneinander. Neue lokale Intensitaetswerte und neue Tauschpaare werden benutzt.

| Satz | Obere Zeile | Untere Zeile | Tausch | Kontrast | Auswertung |
|---|---|---|---|---:|---|
| K1 | 32, 96, 32 | 96, 32, 96 | (0,0) mit (0,1) | 64 | Primaere Bestaetigung an der Mindestgrenze |
| K2 | 52, 148, 148 | 52, 148, 52 | (0,2) mit (1,2) | 96 | Primaere Bestaetigung |
| K3 | 204, 44, 204 | 44, 204, 44 | (0,2) mit (1,0) | 160 | Primaere Bestaetigung |
| G1 | 104, 128, 104 | 128, 128, 104 | (0,2) mit (1,1) | 24 | Getrennte Grenzdiagnose, nicht im primaeren Erfolgswert |

Jedes Paar wird in beiden Speicherrichtungen geprueft. Je Episode ein frischer
B4-Zustand, genau eine Bildung mit Delta 0, anschliessend dieselbe feste Folge:
Original 0, Tausch 0, Original -8, Tausch -8, Original +8, Tausch +8.
Die zwei Regeln erhalten denselben gespeicherten Zustand und dieselben
Probeinputs. Herkunftskennungen und Sollklassen gelangen nicht in den Abruf.

Die Bildpaare sind **prospektiv neu registrierte Bestaetigungsfaelle**, keine
Zufallsstichprobe oder verblindete externe Daten. Es liegen keine neuen
Abrufbefunde vor; spaetere Ergebnisse duerfen die Schwelle nicht aendern.
Ihre geometrische Konstruktion ist bekannt.
Erfolg bestaetigt den endlichen technischen Transfer, keine allgemeine
Wahrnehmungsleistung. Die Tabelle darf nach Ergebnissen weder ausgetauscht
noch durch einfachere Faelle ersetzt werden.

G1 stellt eine Erweiterungsfrage ausserhalb der Mindestanforderung: Bei
Kontrast 24 hat der reine Zweizellentausch theoretisch denselben mittleren
Abstand `8/255` wie eine tolerierte globale Verschiebung um 8. Sollten auch
solche Tausche zwingend abgewiesen werden, koennte keine einzige L1-Schwelle
beide Anforderungen erfuellen. Das ist eine vorab benannte Grenzprognose,
kein bereits gemessener Befund und kein primaerer Fehler von L1-KAL.

## 4. Umfang, Wiederverwendung und Ressourcen

Entwicklung: nur die alten aufgezeichneten Distanzen lesen; **keine** erneuten
A/B/C-Bildungen oder Proben. Bestaetigung einschliesslich Grenzdiagnose:
**56 Bildanalysen, acht B4-Bildungen, 48 Probeinputs, 96 read-only Regelabrufe**.
K1-K3 umfassen je Regel 18 positive und 18 negative Pflichtentscheidungen;
G1 je Regel sechs Original- und sechs Tauschentscheidungen, separat ausgewiesen.

Wiederverwendet werden Rezeptor, Frameuebergabe, B4-Zustand und Bildung,
Distanzfunktion sowie lokale Aufzeichnung: insbesondere `frame_to_b4`,
`_advance_b4`, der unveraenderte 0,2-Abruf `_probe_joint_slots` und
`normalized_mean_l1_distance`. Ein spaeterer privater Evaluator
braucht nur die gebundene visuelle Schwelle als Parameter. Die alte Funktion
mit festem Wert 0,2 und alle alten Einstiegssperren werden nicht geaendert.
Die Vergleichsregeln arbeiten auf demselben Vorzustand; kein erneutes Speichern
fuer die zweite Schwelle und keine Kalibrierung im Bankzustand.

Unveraendert neun Plaetze und hoechstens 255 logische Woerter pro Bank,
ein belegter Platz je Episode. Acht Bildungen ergeben 232 funktionale
Schreibwoerter; Proben schreiben nichts. 96 Abrufe mit einem 26-Werte-Eintrag
ergeben 2496 funktionale L1-Terme, zusaetzliche Validierung separat zaehlen.
Die bisherigen Grenzen 293 Schreibwoerter und 234 Distanzterme je Operation
einschliesslich L1-Validierung bleiben bestehen. Rezeptor-, globale
Histogramm-/Helligkeitskontrolle, Initialisierung und Recorderarbeit sind
getrennte Kosten; logische Woerter sind keine Prozess-RAM-Angabe.

Spaetere fokussierte Pruefungen betreffen nur die neue Schwellenuebergabe:
Ableitung ohne Zugriff auf K/G-Ergebnisse, Uebereinstimmung von L1-ALT mit
dem vorhandenen Abruf, unveraenderte Zustands-/Werteuebergabe und vollstaendige
Quellen-/Ergebnisbindung. Kein pauschaler neuer Rezeptor- oder Gesamtaudit.
Noch ist weder diese Implementierung noch eine Pruefung freigegeben.

## 5. Auswertung und Konsequenz vorab binden

Vor jedem Erfolgsurteil muessen Quelle, Traegerreihenfolge, Rezeptorwerte,
Speicherung und Probe-Unveraenderlichkeit stimmen. Rueckgabewerte muessen
dem gespeicherten Original entsprechen, nicht dem Probeinput. Fehler in
diesen Bindungen bzw. unvollstaendige Aufzeichnung sind methodisch getrennt
und machen den Versuch nicht auswertbar. Fachliche Fehlentscheidungen
werden vollstaendig erfasst, nicht als technischer Abbruch behandelt.

Pro Regel und Satz getrennt berichten: Fehlgleichsetzungen, falsche
Ablehnungen, exakte und +/-8-Treffer, Rueckgabefehler, Distanzen und Kosten.
Primaerer Erfolg verlangt bei K1-K3 **null Fehlgleichsetzungen und null
falsche Ablehnungen** samt korrekter Rueckgabe und unveraenderten Zustaenden.
G1 darf den Primaerwert weder verbessern noch verschlechtern.

Die aufgezeichneten Pflichtabstaende erlauben anschliessend eine reine
Machbarkeitsdiagnose: U_neu = groesster positiver und L_neu = kleinster
negativer Abstand; eine gemeinsame Schwelle ist nur in [U_neu,L_neu) moeglich.
Das ist **keine nachtraegliche Neuwahl** und kein zweiter Bestaetigungslauf.

- L1-KAL erfuellt die Aufgabe: einfache Kalibrierung genuegt im geprueften Umfang.
- L1-KAL verfehlt Faelle, aber ein belastbares Intervall bleibt: Kalibrierung
  uebertraegt sich nicht ausreichend; noch kein Grund fuer komplexere Mechanik.
- Fuer die verbindliche Aufgabe bleibt kein numerisch belastbares Intervall:
  Grenze einer gemeinsamen L1-Schwelle dokumentieren. Erst dann ist eine
  getrennte Helligkeits-/Ortsbewertung als naechste Richtung zu begruenden.
- Nur G1 zeigt die Grenze: primaere Aufgabe bleibt davon getrennt. Erst eine
  ausdrueckliche Erweiterung unterhalb der Mindestgrenze macht dies verbindlich.

Keine automatische Wiederholung, Teilfortsetzung oder Anpassung nach Fehlern.
Die erste endliche Bestaetigung bleibt auch bei Misserfolg erhalten; spaetere
Neukalibrierung braeuchte neue, getrennte Bestaetigungsfaelle. TSPM-1, PPB-1,
Feldpfad, API und Snapshot bleiben unveraendert. Keine Semantik oder neue
Speichermechanik. Naechste Entscheidung ist ausschliesslich die konkrete
private Umsetzung und fokussierte Ausfuehrung dieses Plans, keine weitere
allgemeine Vertragsaudit-Kaskade.
