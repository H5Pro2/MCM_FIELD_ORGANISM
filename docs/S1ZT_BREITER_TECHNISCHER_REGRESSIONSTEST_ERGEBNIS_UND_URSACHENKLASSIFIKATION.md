# S1-ZT: Breiter technischer Regressionstest und Ursachenklassifikation

## Ausfuehrung

Der vorregistrierte Lauf wurde genau einmal und ohne Fail-Fast ausgefuehrt:

```text
python -m unittest discover -s tests -p test_*.py
Python: 3.14.4
Testmodule im Preflight: 914
ausgefuehrte Tests: 8884
Laufzeit: 7444.725 s
Fehlschlaege: 13
Fehler: 376
Exitcode: 1
Retry: 0
Reparaturen waehrend des Laufs: 0
```

Der breite Projektteststatus ist damit nicht gruen. Der konkrete, zuvor
geschlossene W1-F-Smoke-Assetrest ist im fokussierten Pfad weiterhin behoben;
der Gesamtverbund deckte weitere unabhaengige technische Altlasten auf.

## Ursachenklassen

### C1 - Plattformabhaengige Rohbyte-Digests

Mehrere historische E1- und Folgeketten hashen publizierte JSON-Reports direkt
ueber `read_bytes()`. Unter `core.autocrlf=true` besitzen diese Reports im
Windows-Arbeitsbaum ein abschliessendes CRLF statt LF. Fuer die geprueften
Repraesentanten S1-DI, S1-DQ und S1-EA6 gilt jeweils:

- Arbeitsbaumdigest weicht vom gebundenen Digest ab;
- reine CRLF-zu-LF-Normalisierung ergibt exakt den Git-Blob;
- Git-Blobdigest entspricht exakt der im Code gebundenen Erwartung.

Die gleiche Ursache betrifft die drei Assets unter
`tools/controlled_av_canonical_audio_world/`. Ihre LF-normalisierten Bytes und
Git-Blobs entsprechen exakt den kanonischen W1-M-Erwartungen; die rohen
Windows-Arbeitsbaumbytes nicht.

Diese Klasse erzeugt viele Kaskadenfehler: Ein frueher Reportdigest-Abbruch
verhindert nachfolgende Contracts, Adapter und erwartete Fehlerpfade. Die 376
Fehler duerfen deshalb nicht als 376 unabhaengige Mechanismusdefekte gelesen
werden.

### C2 - Fehlende optionale Test- und Decoderabhaengigkeiten

Im aktiven Python 3.14.4 fehlen `pytest` und `av`:

- `test_contact_reproduction_probe` kann wegen `ModuleNotFoundError: pytest`
  nicht importiert werden;
- der positive PyAV-Containerpfad erwartet einen vorhandenen Decoder, findet
  aber keinen.

Das sind Umgebungs- beziehungsweise Suite-Vertragsfehler, keine
Feldkernregressionen.

### C3 - Historische Erwartungs- und Zustandsisolation

Einige Tests erwarten fruehere Oberflaechen oder einen unbenutzten
Projektzustand, obwohl spaetere historische Schritte diese Grenzen erweitert
oder Marker verbraucht haben. Sichtbare Beispiele sind:

- G2/D3 erwartet das Fehlen einer spaeter hinzugekommenen Commitfunktion;
- E1-One-Shot-Tests treffen vor ihrer eigentlichen Zielpruefung auf bereits
  veraenderte Report- oder Markerbedingungen;
- der W6-I-Test erreicht wegen eines nicht mehr `READY` gebundenen statischen
  Vertrags nicht den erwarteten synthetischen Versionsfehler.

Diese Tests muessen als historische Regressionen eingeordnet oder vollstaendig
isoliert werden. Geschlossene Forschungszweige werden dadurch nicht
reaktiviert.

### C4 - Numerische Plattformtoleranz

Ein raeumlicher Lasttest scheitert unter Python 3.14.4 an einer Differenz von
`5.551115123125783e-16` bei `places=15`. Das ist eine zu enge numerische
Testtoleranz und kein fachlich relevanter Feldunterschied.

### C5 - Fehlende Regressionstier-Aufteilung

Der ungeteilte Verbund benoetigte mehr als zwei Stunden und mischt:

- aktiven Feldkern;
- schnelle statische Verträge;
- optionale Abhaengigkeiten;
- geschlossene historische Kandidatenketten;
- rechenintensive Simulationsregressionen.

Er ist damit kein geeigneter schneller Standard-Gate. Die hohe Laufzeit ist
ein technischer Strukturmangel des Testbestands, kein positives oder negatives
Forschungssignal.

## Fachliche Grenze

S1-ZT stellt keinen neuen Fehler des primaeren MCM-Wahrnehmungsfeldkerns fest.
Der Lauf ist als Gesamtgate fehlgeschlagen, aber die dominanten Ursachen liegen
in Portabilitaet, historischen Kaskaden, optionalen Abhaengigkeiten und
Testorganisation. Es entsteht kein Feld-, Wahrnehmungs- oder Memory-Befund.

## Naechster Schritt

S1-ZU soll als statischer Regressionspartitions- und Portabilitaetsvertrag
genau festlegen:

1. schnelles aktives Feldkern-Gate;
2. optionale Abhaengigkeitsgates;
3. geschlossene historische Regressionen;
4. langsame Simulationsregressionen;
5. Inventar aller bytegenau gehashten, plattformabhaengigen Textartefakte;
6. enge EOL-Regeln ohne globale oder inhaltliche Dateiaenderung.

Vor S1-ZU erfolgen keine weitere Gesamtausfuehrung und keine Reparatur.

Maschinenlesbarer Befund:
[S1ZT_BREITER_TECHNISCHER_REGRESSIONSTEST_ERGEBNIS_UND_URSACHENKLASSIFIKATION_V1.json](S1ZT_BREITER_TECHNISCHER_REGRESSIONSTEST_ERGEBNIS_UND_URSACHENKLASSIFIKATION_V1.json).

