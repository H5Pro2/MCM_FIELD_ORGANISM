# S1-ZP: W1-F statischer Asset- und Erwartungsbindungsaudit

## Auftrag und Grenze

S1-ZP untersucht den in S1-ZN und S1-ZO abgegrenzten W1-F-Assetfehler. Der
Audit startet keinen Browser, importiert keine Projektmodule und fuehrt weder
Smoke-, Capture-, Rezeptor- noch Feldfunktionen aus. Dateien und Erwartungen
werden in diesem Schritt nicht korrigiert.

## Befund

W1-F erwartet fuer `index.html`, `styles.css` und `world.js` die SHA-256-Werte
der im Repository gespeicherten Git-Blobs. Alle drei Git-Blobs verwenden LF
und stimmen exakt mit den gebundenen W1-F-Werten ueberein.

Im aktuellen Windows-Arbeitsbaum gilt zugleich:

```text
core.autocrlf: true
.gitattributes: nicht vorhanden
explizite EOL-Regel fuer die drei Assets: nicht vorhanden
```

Dadurch liegen die drei Dateien lokal mit CRLF vor. Ihre rohen
Arbeitsbaumdigests weichen deshalb von W1-F ab. Nach ausschliesslichem Ersetzen
von CRLF durch LF stimmen alle Bytes wieder exakt mit den Git-Blobs und den
W1-F-Erwartungen ueberein.

| Asset | W1-F und Git-Blob | aktueller Windows-Arbeitsbaum |
|---|---|---|
| `index.html` | `74fc372a3eff08ac38e803689e562ce5acbb39d56d3351db475c768457e32af8` | `2e06a62b439fdf204955217d4950d1b9866c259b7bad231d206f8efc6f7a2d15` |
| `styles.css` | `f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594` | `084930c9e7dfc94a3e6dfd7df12d03c6e2e7cc6d5b20a97592040253610223ec` |
| `world.js` | `fda8c774708af883eb97625b7064ec288c06e2819619fb2eb93e281212d32158` | `b98523962254e78ba70c2d5a3bcf2b99765e18d96bad94f4bef220b83d1b92c7` |

## Ursache und Einordnung

Der Assetpruefer bildet SHA-256 direkt ueber `path.read_bytes()`. Seine
Erwartung ist daher bytegenau, der Checkout ist ohne EOL-Vertrag jedoch
plattformabhaengig. Die W1-F-Werte sind nicht veraltet und die Assets wurden
inhaltlich nicht veraendert. Die fehlende Repositoryregel fuer unveraenderte
Assetbytes ist die alleinige nachgewiesene Ursache.

Der Fehler liegt vor jedem Browserstart. Er betrifft technische
Reproduzierbarkeit, nicht Browser-Lifecycle, Rezeptoren, Feldkern oder eine
Forschungsmechanik.

## Entscheidung

```text
inhaltliche Assetdrift: nein
veraltete W1-F-Erwartungswerte: nein
reine LF/CRLF-Arbeitsbaumabweichung: ja
Browserausfuehrung: 0
Asset- oder Codekorrektur: 0
```

## Naechster Schritt

S1-ZQ soll einen statischen Korrekturvertrag binden. Fachlich vorzuziehen ist
eine enge `.gitattributes`-Regel `text eol=lf` nur fuer die drei kontrollierten
Browser-Assets. Die W1-F-Digests bleiben dabei unveraendert. Erst nach
separater Abnahme darf die Arbeitsbaumdarstellung kontrolliert normalisiert
und der fokussierte synthetische Smoke-Test erneut ausgefuehrt werden.

Maschinenlesbarer Audit:
[S1ZP_W1F_STATISCHER_ASSET_UND_ERWARTUNGSBINDUNGSAUDIT_V1.json](S1ZP_W1F_STATISCHER_ASSET_UND_ERWARTUNGSBINDUNGSAUDIT_V1.json).

