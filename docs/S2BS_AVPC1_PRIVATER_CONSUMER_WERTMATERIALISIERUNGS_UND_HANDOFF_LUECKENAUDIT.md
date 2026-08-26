# S2-BS: Privater Consumer- und Wertuebergabe-Lueckenaudit

## Fragestellung

S2-BS prueft ausschliesslich, ob der bestehende private PPB-1-/AVPC-1-Pfad
bereits eine gebundene visuelle Prototypidentitaet auf den zugehoerigen
verdichteten visuellen Prototypzustand zurueckfuehren kann.

Die benoetigte Funktion ist keine neue Speicherung. Sie soll nur einen bereits
vorhandenen stabilisierten Prototyp in einem exakt eingefrorenen visuellen
Bankzustand eindeutig und read-only bereitstellen.

## Bestandsbefund

Der Bestand deckt Teilrollen ab, aber nicht die vollstaendige Uebergabe:

- `S1WUReadOnlyPerceptualFinding` liefert einen Prototypdigest, jedoch keine
  Prototypwerte.
- `AVPC1ReadOnlyRelationFinding` liefert bei `MATCH` den gebundenen visuellen
  Zieldigest, jedoch keine Prototypwerte.
- `PPB1Readout` kann Werte enthalten, ist aber an einen zustandsfortschreibenden
  PPB-1-Schritt und dessen Nachzustand gebunden. Es ist kein read-only Resolver
  fuer einen Relationsbefund.
- `PPB1ActiveBatchFormationResult` enthaelt ganze Banknachzustaende, loest aber
  keinen Relations-Zieldigest auf.
- Der Formation-/Probe-Handoff transportiert wiederum nur Probenbefunde.

Damit fehlt genau eine kleine Engineeringfunktion. Es fehlt keine neue
Feldursache und kein neues Speicherverfahren.

## Ausgewaehlter Anschluss

Als einziger naechster Baustein wird ein privater read-only Resolververtrag
ausgewaehlt. Er muss einen positiven Relationsbefund, den exakten
Relationszustand sowie die validierte eingefrorene visuelle Bank gemeinsam
binden. Der Zieldigest muss genau einen stabilisierten Slot identifizieren.

Die Ausgabe darf nur vorhandene normalisierte Prototypwerte, Carrier- und
Slotidentitaet, Support sowie alle Quell- und Zustandsdigests enthalten. Es
darf keine Distanzsuche, Aktualisierung, Konvertierung, aktuelle visuelle
Eingabe oder Feldwirkung stattfinden.

## Naechster Schritt

S2-BT soll diesen Resolver ausschliesslich statisch vertraglich binden. Vor
einer Implementierung sind exakte Eingaben, Digestidentitaeten,
Eindeutigkeitsregel, Ausgabeform und Fail-Closed-Faelle festzulegen.

Implementierung, Ausfuehrung, oeffentliche API, Feldsnapshot, Produktion und
Feldwirkung bleiben gesperrt.
