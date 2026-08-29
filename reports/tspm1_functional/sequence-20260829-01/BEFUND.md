# Visuelle Reihenfolge: technischer Fehlabschluss

## Verbindlicher Status

**Die einmalige Hauptuntersuchung ist nicht auswertbar.** Sie darf weder als
positiver noch als negativer funktionaler Sequenzbefund verwendet werden.
Die acht fokussierten Qualifikationstests waren erfolgreich. Der danach
bedingte Hauptprozess beendete sich jedoch mit Exit-Code 1, bevor die
verbindlichen Dateien `result.json` und `terminal.json` veroeffentlicht waren.

Ursache ist ein falscher Modulverweis im rein lesenden Abschlussvalidator:

```text
calibration.empty_payload()
```

Die Funktion liegt in `spatial`; korrekt ist `spatial.empty_payload()`.
Der Fehler trat erst nach dem Schliessen des Ereignisjournals auf. Er ist
kein beobachteter fachlicher Abruffehler, aber ein Abschluss- und
Aufzeichnungsfehler. Nach der Vorregistrierung macht das den Versuch
nicht auswertbar. Es gab keine Wiederholung oder Teilfortsetzung.

## Qualifikation

- Acht von acht Tests bestanden, Exit-Code 0.
- Zwei begrenzte synthetische B4-Uebergaenge prueften die Indexableitung.
- Keine Hauptbilder und kein Rezeptoraufruf in der Qualifikation.
- Geprueft wurden Indexherkunft, Slot-/Containerunabhaengigkeit,
  ungueltige Indizes, exakt `44/765`, die reihenfolgeblinde Zuordnung,
  read-only Verhalten sowie Quellen- und Aufzeichnungsgrenzen.
- Qualifikationsdigest:
  `1e960c4cafeccc8a02567e9136f837a85662df32277b24554ce1e1e1b6b1a15b`.

## Vorhandene Hauptaufzeichnung

`events.jsonl` enthaelt 152 verkettete Start-/Ergebnisereignisse. Die
gesonderte Diagnose las diese Datei ohne Rezeptor-, B4-, Abruf- oder
Matrixaufruf. Alle Guards blieben bei null. Sie rekonstruierte deskriptiv:

- 56 Bildanalysen;
- acht B4-Bildungen;
- zwoelf Folgeproben;
- 24 Sichtentscheidungen;
- vier eindeutige Bildungsindizes je Bank;
- unveraenderte Bankzustaende waehrend der Proben.

Die gespeicherten Entscheidungsrecords ergeben deskriptiv fuer GEORDNET
sechs richtige Wiedererkennungen und sechs richtige Abweisungen. Die
reihenfolgeblinde Sicht nahm alle zwoelf inhaltsgleichen Folgen an. Diese
Zahlen entsprechen der erwarteten technischen Trennung, sind aber wegen
des fehlenden regulaeren Abschlusses **kein akzeptierter Funktionsbefund**.
Sie duerfen nicht als nachgewiesener Kurzzeit-Sequenzabruf zitiert werden.

## Korrektur und Sperre

Nach dem Fehlabschluss wurden ausschliesslich zwei statische Quellaenderungen
vorgenommen:

1. der falsche Validatorverweis wurde auf `spatial.empty_payload()` korrigiert;
2. der verbrauchte private Einstieg wurde von `True` auf `False` gesetzt.

Die Quelle wurde danach nur syntaktisch geprueft. Die acht Tests wurden nicht
wiederholt. Der korrigierte Abschlussvalidator las die bestehende Aufzeichnung
rein diagnostisch; er erzeugte bewusst keine nachtraeglichen `result.json`-
oder `terminal.json`-Dateien. `diagnostic.json` traegt daher explizit
`NOT_EVALUABLE` und `accepted_functional_result: false`.

Keine Aenderung an B4, Einzelbildabruf, TSPM-1, PPB-1, API, Snapshot oder
Feldpfad. Alle alten Einstiege bleiben gesperrt. Die Einmalfreigabe ist
verbraucht. Ein neuer Lauf waere eine ausdrueckliche Aenderung der geltenden
Keine-Wiederholung-Regel und benoetigt deshalb eine konkrete neue Entscheidung.

## Belege

- [Qualifikation](../sequence-qualification-20260829-01/result.json) und
  [Testprotokoll](../sequence-qualification-20260829-01/output.txt)
- [Startmanifest](manifest.json), [Ereignisjournal](events.jsonl),
  [Fehlerbeleg](failure.json), [read-only Diagnose](diagnostic.json)
- [Freigabe](../sequence-20260829-01.authorization.txt),
  [Ausfuehrungsstand](../sequence-20260829-01.prestart.md),
  [Standardausgabe](../sequence-20260829-01.stdout.txt) und
  [Fehlerausgabe](../sequence-20260829-01.stderr.txt)

Fehlerdigest: `ef691e2d6e4b7bbbd0320b9007a7c2d61f403e931603d8556d46844a3bc5888f`.
Diagnosedigest: `987de75b005f5f8d47725b55ca9775b5e56b45974fc87ffcb37f8fa53f4f4074`.
