# S1-ZV: Enge Rohbyte-Portabilitaetsimplementierung und fokussierter Abnahmebefund

## Umsetzung

S1-ZV setzt den S1-ZU-Vertrag ohne Erweiterung um. Zu den drei bereits
gebundenen W1-F-Regeln kamen genau vier `text eol=lf`-Regeln hinzu: drei fuer
die kanonischen Audio-World-Assets und eine fuer die 60 versionierten
JSON-Reports unter `reports/`.

Es gibt weiterhin keine globale EOL-Regel. Die 63 Zielpfade wurden
ausschliesslich von CRLF auf die bereits in Git gespeicherten LF-Bytes
materialisiert. Ihr Git-Inhalt und ihre gebundenen Digests blieben
unveraendert.

## Abnahme

Alle 60 Reports und alle drei kanonischen Assets sind im Arbeitsbaum
rohbytegleich zu ihren jeweiligen Git-Blobs. Fuer keinen Zielpfad besteht ein
Git-Inhaltsdiff. Die drei Assetdigests und drei repraesentativen historischen
Reportdigests entsprechen den vorhandenen Quellbindungen.

Die Abnahme bleibt fokussiert:

- 10 statische Vertrags- und Receipt-Tests;
- 2 synthetische kanonische Fake-Pair-Tests;
- 16 schreibgeschuetzte repraesentative Report-Audittests.

Alle 28 Tests bestanden. Es wurden weder ein reales Browserbinary noch eine
Feldfunktion gestartet. Abhaengigkeiten wurden nicht installiert und der
breite Regressionstest wurde nicht wiederholt.

## Einordnung

S1-ZV beseitigt ausschließlich einen Windows-abhaengigen Rohbytefehler in
gebundenen technischen Artefakten. Der MCM-Feldkern, die Reportinhalte und die
Forschungsentscheidungen bleiben unveraendert. Der Befund ist kein Feld- oder
Memory-Ergebnis.

## Naechster Schritt

S1-ZW soll die Portabilitaetskorrektur statisch abschliessen und den bereits
definierten aktiven T0-Schnelltest als naechstes enges Ausfuehrungstor
vorbereiten. Der breite, historische und optionale Bestand bleibt dabei
gesperrt.

Maschinenlesbarer Befund:
[S1ZV_ENGE_ROHBYTE_PORTABILITAETSIMPLEMENTIERUNG_UND_FOKUSSIERTER_ABNAHMEBEFUND_V1.json](S1ZV_ENGE_ROHBYTE_PORTABILITAETSIMPLEMENTIERUNG_UND_FOKUSSIERTER_ABNAHMEBEFUND_V1.json).
