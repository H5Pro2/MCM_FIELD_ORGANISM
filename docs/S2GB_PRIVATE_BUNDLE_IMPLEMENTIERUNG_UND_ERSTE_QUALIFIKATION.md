# S2-GB: Private Bundleimplementierung und erste Qualifikation

## Umgesetzter Umfang

S2-GB implementiert ausschliesslich private, unveraenderliche Datenrollen und
eine reine Projektion bereits validierter read-only Befunde in ein
`PerceptualContextBundle`.

Die Implementierung:

- fuehrt keine Speicher-, Probe- oder Lernoperation aus;
- bildet die Rollen `B4_RECENT`, `TSPM_FAST` und `TSPM_SLOW` kanonisch, aber
  ohne Rangfolge ab;
- erhaelt gleiche Inhalte aus verschiedenen Quellen als getrennte Kandidaten;
- trennt gueltige Abwesenheit von beschaedigter Evidenz;
- behaelt auditive und visuelle Slow-Komponenten ohne Relationsbehauptung
  getrennt;
- bindet Quelle, Probe, Zustand, Zeitfenster, Komponenten, Folgebeleg und
  Ressourcen kanonisch per Digest;
- begrenzt das Ergebnis auf drei Kandidaten, vier Komponenten, 78 Werte und
  neun B4-Folgenreferenzen;
- enthaelt keine automatische Auswahl und keine Feldintegration.

## Erste einmalige Qualifikation

Der erste und in diesem Schritt einzige Aufruf der zwoelf neutralen Tests
endete mit:

```text
Ran 12 tests
10 passed
2 errors
exit code 1
```

Die Fehler lagen in den neutralen Testvorgaben 08 und 09. Deren Helper wollte
bei leerem B4-Bestand eine Folgenreferenz aus dem ersten B4-Kandidaten bilden,
bevor die beabsichtigte fremde Probe beziehungsweise der widerspruechliche
Zustandsdigest die Projektion erreichen konnte. Die beiden Fehler sind daher
ein Test-Fixture-Fehler und kein funktionaler Befund ueber die
Bundleprojektion.

Die Testaufrufe wurden anschliessend eng auf `NOT_REQUESTED` ohne
Folgenreferenz korrigiert. Es erfolgte kein zweiter Testaufruf. Der erste Lauf
bleibt dauerhaft fehlgeschlagen und darf nicht als bestandene Qualifikation
ausgegeben werden.

## Status und Grenze

Implementierungsstatus:

`S2GB_PRIVATE_IMPLEMENTATION_PRESENT`

Qualifikationsstatus:

`S2GB_FIRST_QUALIFICATION_FAILED_TEST_FIXTURE`

Der Status `PRIVATE_READ_ONLY_PERCEPTUAL_CONTEXT_BUNDLE_VALID` ist noch nicht
erreicht. Eine neue einmalige Qualifikation der unveraenderten zwoelf Tests
benoetigt eine getrennte Freigabe. Kontextverwendung, Feldrueckwirkung, API,
Snapshot und Produktionsintegration bleiben gesperrt.
