# S1-BB: End-to-End-Consumer an der aktiven Kerngrenze

## Status

Technische Architekturabsicherung. Keine neue Feldmechanik, kein
Forschungslauf und kein Memory-, Substrat- oder KI-Befund.

## Frage

Verwendet der bestehende kontrollierte AV-End-to-End-Consumer nach den
Manifestbereinigungen S1-AZ und S1-BA ausschliesslich Rollen aus
`CURRENT_CONTROLLED_FIELD_EXPORTS`?

## Statischer Befund

`tests/test_current_api_end_to_end_consumer.py` besitzt genau einen lokalen
Projektimport:

```text
mcm_field_organism.current_api
```

Die 13 importierten Projektnamen liegen vollstaendig in der aktiven
Kernmenge. Der Consumer importiert nichts aus:

```text
PASSIVE_COMPARISON_EXPORTS
CI_REFERENCE_EXPORTS
F3_REFERENCE_EXPORTS
S1B_REFERENCE_EXPORTS
```

Sein Pfad bleibt damit:

```text
synthetische kontrollierte Audio-/Videofolgen
-> Audio- und Videorezeptoren
-> gemeinsame Rezeptorzeit
-> neutrales gemeinsames S/H-Feld
-> Snapshot / Restore / identische Fortsetzung
```

## Dauerhafte Absicherung

Ein neuer AST-basierter Vertragstest liest die Importanweisung des Consumers,
fordert genau einen Projektimport aus `mcm_field_organism.current_api` und
prueft dessen Namen als echte Teilmenge von
`CURRENT_CONTROLLED_FIELD_EXPORTS`.

Die Pruefung verwendet keinen frei gepflegten zweiten Namenskatalog. Eine
spaetere Aufnahme einer Referenzrolle in den Consumer bricht deshalb den Test,
auch wenn die Rolle weiterhin Teil von `current_api.__all__` ist.

## Aussagegrenze

Die Absicherung belegt eine technische Import- und Ausfuehrungsgrenze. Sie
belegt keine Wahrnehmung im psychologischen Sinn, keine Praegung, kein Lernen,
keine Feldzeit und kein MCM-Memory. Snapshot/Restore bleibt technische
Serialisierung.

## Bester naechster Schritt

Der synthetische End-to-End-Kernpfad ist jetzt manifestgenau abgesichert. Als
naechstes wird dieselbe Grenze fuer den kontrollierten Browserpayload-
Consumer geprueft, weil dieser die zweite aktive Weltzufuhr in das gemeinsame
Feld bildet.

