# S1-BC: Browser-Testwelt-Rezeptorbruecke an der Kerngrenze

## Status

Technische Architekturabsicherung. Keine Browserausfuehrung, keine neue
Feldmechanik, kein Forschungslauf und kein Memory-, Substrat- oder KI-Befund.

## Frage

Verwendet der bestehende kontrollierte Browserpayload-Consumer
`tests/test_current_api_browser_payload_consumer.py` ausschliesslich aktive
Rollen aus `CURRENT_CONTROLLED_FIELD_EXPORTS`?

## Befund

Der Consumer besitzt genau einen lokalen Projektimport aus:

```text
mcm_field_organism.current_api
```

Seine 13 Projektnamen liegen vollstaendig in der aktiven Kernmenge. Er
importiert keine Rolle aus:

```text
PASSIVE_COMPARISON_EXPORTS
CI_REFERENCE_EXPORTS
F3_REFERENCE_EXPORTS
S1B_REFERENCE_EXPORTS
```

Der abgesicherte technische Pfad bleibt:

```text
kontrollierte PNG- und PCM-Nutzlasten
-> BrowserReceptorBridge
-> reduzierte auditive und visuelle Rezeptorsequenzen
-> gemeinsames neutrales S/H-Feld
-> Snapshot / Restore
```

Die Rohpayloads werden nach der Reduktion nicht im Batch oder in der Bruecke
gehalten.

## Dauerhafte Absicherung

Der AST-Vertrag aus S1-BB wurde auf beide aktiven Consumer verallgemeinert.
Fuer jeden Consumer gilt:

1. genau ein lokaler Projektimport;
2. Import ausschliesslich aus `mcm_field_organism.current_api`;
3. alle importierten Namen sind Teil von
   `CURRENT_CONTROLLED_FIELD_EXPORTS`.

Eine spaetere Referenz- oder Altpfadaufnahme bricht damit die
Architekturpruefung, selbst wenn der Name aus Kompatibilitaetsgruenden in
`current_api.__all__` erhalten bleibt.

## Aussagegrenze

Die Pruefung startet keinen Browser und verwendet keine Kamera, kein
Live-Mikrofon und keine physische Sensorik. Sie belegt nur die technische
Importgrenze und den bestehenden kontrollierten Payloadpfad. Sie belegt kein
Lernen, keine Praegung, keine Feldzeit und kein MCM-Memory.

## Bester naechster Schritt

Beide aktiven Weltzufuhren sind nun gegen die Kernmenge abgesichert. Als
naechstes wird geprueft, ob ihre erzeugten Rezeptorsequenzen an derselben
neutralen Zeit- und Handoffgrenze enden, ohne quellenspezifische Sonderpfade
im gemeinsamen Feld zu erzeugen.

