# Visuelle Ortsstruktur: Implementierungs- und Einmalbefund

## Ergebnis

Der freigegebene Versuch `spatial-20260828-01` ist vollstaendig abgeschlossen:
**28 Bildanalysen, acht Speicherbildungen, 48 read-only Proben, Exit-Code 0.**
Es gab keinen technischen Abbruch, keine Wiederholung und keine Anpassung
von Bildrezepten, Speicherkern, Kapazitaet, Distanzfunktion oder Schwelle.

**Im Ortsarm bleibt die unterschiedliche Anordnung der Zellwerte im Rezeptor
und im Speicher erhalten. Die vorhandene Abrufbewertung unterscheidet den
grossen Ortstausch, setzt den kleinen aber faelschlich gleich.** Die Grenze
liegt fuer diese Aufgabe damit beim Abruf, nicht bei der Speicherung.

## Was umgesetzt und geprueft wurde

Genau zwei neue private Dateien:

- `tools/_visual_spatial_memory_probe.py`: Bild-/Frame-zu-B4-Adapter,
  deklarierte Ortsablation, einmaliger Versuch und read-only Ergebnispruefung.
- `tests/test_visual_spatial_memory_probe.py`: sechs kleine Adapter- und
  Aufzeichnungspruefungen sowie die fuenf vorhandenen Regressionen aus dem Plan.

Der fokussierte Lauf bestand **11/11 Tests**, Exit-Code 0, terminales `OK`.
Dabei wurden keine B4-Bildungs-/Probeoperatoren oder alten Matrixoperatoren
ausgefuehrt; die entsprechenden Fehlerguards verzeichnen jeweils null Aufrufe.
Die Bildanalysen der vorhandenen Rezeptorregressionen sind vom Hauptversuch
getrennt. Die Tests wurden nicht wiederholt.

Quellen: [Testprotokoll](../spatial-qualification-20260828-01/output.txt),
[Testbeleg](../spatial-qualification-20260828-01/result.json),
[Ausfuehrungsstand](../spatial-20260828-01.prestart.md),
[Benutzerfreigabe](../spatial-20260828-01.authorization.txt).

## Beobachtete Einzelaufgaben

Die vorhandene 3x2-Rezeptorgeometrie lieferte je Bild 18 geordnete Kanalwerte.
A/B vertauscht alle sechs Zellen; A/C nur zwei. Alle Bilder besitzen bei
gleichem Delta dasselbe Histogramm und dieselbe globale Helligkeit. Der
auditive Eingang blieb immer achtmal null.

Je Bedingung: vier frische Episoden, vier Bildungen und 24 Proben.
Beide Speicherrichtungen und alle Deltas -8, 0 und +8 sind enthalten.

| Pruefung | B4 mit Ortswerten | B4 ohne Ortsinformation |
|---|---:|---:|
| Original, Delta 0 | 4/4 erkannt | 4/4 erkannt |
| Original, Delta -8 oder +8 | 8/8 erkannt | 8/8 erkannt |
| Grosser Ortstausch A/B | 6/6 korrekt abgewiesen | 6/6 falsch gleichgesetzt |
| Kleiner Ortstausch A/C | 6/6 falsch gleichgesetzt | 6/6 falsch gleichgesetzt |
| Korrekte Entscheidungen insgesamt | 18/24 | 12/24 |
| Falsche Ablehnungen | 0 | 0 |
| Falsche Rueckgabewerte bei erkanntem Abruf | 0 | 0 |
| Unveraenderte Probezustaende | 24/24 | 24/24 |

Die ortsblinde Kontrolle entfernt die Ortsinformation absichtlich vor dem
Speichern durch kanalweise Mittelung. Ihre Fehlgleichsetzungen sind der
erwartete diagnostische Kontrollbefund, kein negativer Befund ueber B4.
Sie erhaelt weder Bildnamen noch den urspruenglichen Ortsvektor als Abrufhilfe.

## Getrennte Fehlerzuordnung

**Rezeptor und Uebergabe:** Alle 28 Rezeptorausgaben stimmen positionsweise
mit den vorab definierten Zellmittelwerten ueberein. Der maximale beobachtete
Fehler ist 0,0. Geometrie, Traegerreihenfolge und die Uebernahme in den
Rezeptorframe blieben korrekt. A/C unterscheidet sich in sechs der 18 Werte,
also in zwei Zellen mit jeweils drei Kanaelen.

**Speicherung:** In allen acht Bildungen stimmt der gespeicherte 26-Werte-
Vektor exakt mit dem tatsaechlichen Angebot der jeweiligen Bedingung ueberein.
Es gibt weder eine unbeabsichtigte Mittelung im Ortsarm noch eine Veraenderung
durch Proben. Im Ortsarm wird die urspruengliche Zellfolge zurueckgegeben;
bei tolerierter Intensitaetsaenderung wird nicht der Probeinput als
vermeintlicher Speicherinhalt ausgegeben.

**Abruf:** Die unveraenderte Regel akzeptiert normalisierte mittlere
L1-Distanzen bis einschliesslich 0,2 je Modalitaet. Die auditive Distanz ist
in jeder Probe 0,0. Beobachtete visuelle Distanzen im Ortsarm:

| Probe gegen gespeichertes Original | Distanz | Entscheidung |
|---|---:|---|
| Identisches Original | 0,0 | erkannt |
| Original mit +/-8 | 0,0313725490 | erkannt |
| A/B, alle Deltas | 0,5019607843 | abgewiesen |
| A/C, Delta 0 | 0,1673202614 | erkannt, fachlich falsche Gleichsetzung |
| A/C, Delta -8 oder +8 | 0,1882352941 | erkannt, fachlich falsche Gleichsetzung |

Die Mittelung ueber alle 18 Komponenten macht den kleinen Ortstausch kleiner
als die bestehende Matchschwelle, obwohl seine abweichenden Komponenten
vorhanden sind. Das ist eine **aufgabenspezifische Grenze dieser Abrufregel**.
Es ist kein automatischer Informationsverlust und kein Scheitern des Speichers.
Die zuvor dokumentierte statische Gegenprognose wurde durch den Lauf bestaetigt;
sie wurde nicht als Ersatz fuer die tatsaechlichen Bildungen verwendet.

## Ressourcen und Aufzeichnung

- Unveraendert neun FIFO-Plaetze und maximal 255 logische Woerter pro Bank.
  Jede Episode hat genau einen belegten Platz; Kapazitaetsdruck wurde nicht untersucht.
- 232 funktionale Schreibwoerter: achtmal 29, bei Proben jeweils null.
  Die 29 umfassen 26 Werte, Belegungsmarker, Bildungsindex und globalen Zaehler.
  Der rohe Helper-Kostenteil `(27,0)` ist zusaetzlich unveraendert protokolliert.
- 1248 funktionale L1-Terme und 1248 zusaetzliche L1-Validierungsterme.
  Je Probe sind es 26 plus 26, unter der Grenze 234. Bildungs-Schreibarbeit
  29 bleibt unter 293. Initialisierung: 72 Slotinitialisierungen, separat.
- Rezeptorreduktion und globale Bildkontrolle verarbeiten jeweils 806400
  Kanalwerte. Zusaetzlich 504 positionsweise Rezeptorpruefungen;
  Kontrollprojektion und deren Abnahme verwenden zusammen 1008 Summeneingaenge
  und 168 Mittelwertdivisionen. Diese Nebenarbeiten sind keine Speicherfunktion.
- Ein Eingabebild umfasst 28800 Nutzbytes. Rohbilder gelangen nicht in B4.
  Rezepte, Bildhashes und vollstaendige reduzierte Werte bleiben im Beleg.
- Gemessene innere Versuchsdauer: 0,452797 Sekunden. Aeussere Prozesszeit
  einschliesslich Import und Abschluss etwa 1,327 Sekunden. Es gibt keine
  getrennte Geschwindigkeitsmessung je Bedingung und keine Messung der realen
  Prozessspeicherspitze. Logische Woerter sind keine Python-RAM-Angabe.

Alle 168 Start-/Ergebnisrecords sind vollstaendig verkettet. Jeder Befund
enthaelt Quellenbezug, tatsaechliche Werte, Distanzen, Entscheidung und Kosten;
Bildungen und Proben enthalten die zugehoerigen Zustandsbelege. Die acht
Episoden-/Bedingungs-Owner sind verschieden. Es gibt keine Fehlerdatei und
keinen unvollstaendigen temporaeren Abschluss.

Nach dem Versuch wurden ausschliesslich gespeicherte Ergebnisse und
Quellenbytes gelesen: Journal-/Dateihashes, Quellenbindung, Zaehler,
Owner, unveraenderte Probezustaende und der externe Prozessbeleg stimmen.
Alle 24 im Hauptmanifest archivierten Projektquellen waren vor der
anschliessenden Gatesperrung unveraendert. Keine erneuten Rezeptor-,
Speicher- oder Probeaufrufe fanden zur Auswertung statt.

| Originalbeleg | SHA-256 der Dateibytes |
|---|---|
| [manifest.json](manifest.json) | `4385c5f2b03c22d16803b9e4c59e6d172f7cd6d76f3f3abff96a9885ef33f4a7` |
| [events.jsonl](events.jsonl) | `d1e0c07e3e1fbafc2a0d7ee064fe8fbd7c581af825d2aa49b101c0619eb512fd` |
| [result.json](result.json) | `6b56cf88727698e3c2622d298fbaa6dd1ba2dd1b0bfef6f3e854b4a45017d229` |
| [terminal.json](terminal.json) | `8ccf0db9fde9ca5c6e9f831355058962001e073385e88b1a9d82f29383878e4e` |

Der kanonische Ergebnisdigest lautet
`d68ad96845facc45035f3e99df4d5300f8b5452820d04e78214cee61413bfa8d`.
Der [Prozessbeleg](../spatial-20260828-01.process.json) bindet Exit-Code 0,
Ausgabehashes und den einzigen Aufruf.

## Konsequenz und Grenze

Fuer die Erhaltung dieser Zellmittelwerte ist keine zusaetzliche
Speichermechanik begruendet. Die vorhandene Repraesentation und B4 genuegen
zum Bewahren der geprueften Ortsanordnung. **Fuer die vollstaendige
Unterscheidungsaufgabe genuegt die bisherige Abrufbewertung dagegen nicht.**

Naechste Entscheidung: Soll eine aufgabenspezifische Abrufbewertung kleine
Ortsaenderungen strenger unterscheiden, waehrend die gebundene
Intensitaetstoleranz erhalten bleibt? Eine solche Aenderung ist nicht Teil
dieses Auftrags. Insbesondere wurde die Schwelle nicht nachtraeglich gesenkt.
Es folgt daraus weder ein neuer Speicher noch eine allgemeine Aussage ueber
Objekte, Ansichtsunabhaengigkeit, Zeitfolgen oder langfristige Verdichtung.

Der neue Einstieg wurde nach erfolgreicher Belegpruefung auf gesperrt gesetzt;
die archivierten Ausfuehrungsbytes bleiben erhalten. Ein statischer AST-Abgleich
bestaetigt ausschliesslich diese Gatesperre als Abweichung; die anderen 23
archivierten Quellen sind bytegleich. SHA-256 des gesperrten Adapters:
`11b5a42a7b5e3755bd2f56ec3cf68572f25f8983917883f328cbe64c1182f24b`.
Versuchspfad und
Qualifikationspfad duerfen nicht wiederverwendet werden. Rezeptor, B4-Kern,
TSPM-1, PPB-1, API, Snapshot und Feldpfad wurden nicht veraendert. Alte Matrix-
und Plattformpfade sowie S2-FC bleiben gesperrt.
