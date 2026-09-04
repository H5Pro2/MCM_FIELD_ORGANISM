# S2-LS Presealed AV Corpus Plan 2026-09-04-01

Status: `S2LS_PRESEALED_AV_CORPUS_PLAN_MATERIALIZED`

Das konkrete Korpusinventar wurde vor jeder Rezeptoranalyse erzeugt und
versiegelt. Es erfolgten keine Rezeptor-, Memory-, Feld- oder Kontextaufrufe.

## Inventar

- zwei Wahrnehmungsfamilien;
- je vier Trainingsvarianten;
- je zwei vollstaendig zurueckgehaltene Holdouts;
- neun unabhaengige Druckinhalte;
- 17 vollstaendige AV-Formationsevents;
- acht spaetere modalitaetsspezifische Teilhinweise;
- 25 neutrale Ereignisse insgesamt.

Die Trainingsereignisse sind familienweise interleaved. Danach folgen die
neun Druckereignisse und erst anschliessend die acht Hinweise. Kein Holdout
erscheint in einer Formation.

## Quellenbindung

Alle 21 visuellen und auditiven Inhaltsvarianten besitzen vorab feste
Generatorrezepte, Seeds beziehungsweise ganzzahlige Perioden und kanonische
Byte-Digests. Die Generatorwurzel importiert oder verwendet keine
Rezeptoren, Memory, Felder, Kontexte oder Schwellen.

Die RGB8-Payloads besitzen jeweils `6.220.800` Bytes. Die mono
PCM_F32LE-Payloads besitzen jeweils `4.800` Samples beziehungsweise `19.200`
Bytes. Rohpayloads wurden nur transient zur Digestbildung erzeugt und nicht
im Plan oder Ergebnis gespeichert.

Train/Holdout-Zuordnung und Familienrollen stehen ausschliesslich in der
getrennten Evaluationswurzel. Die Ausfuehrungswurzel enthaelt nur neutrale
Content-, Event-, Source-, Owner-, Zeit-, Payload- und Maskenbindungen.

## Digests

- Plan:
  `1ad42964295cce44b87f6c3d02479983878ca7c403eee21440783fe3326e661a`;
- Generatorwurzel:
  `ab293ddcbd9b2adf9dc9d2a28e05a8a203ec9eaab7b3a07dba59c5a668161d16`;
- Ausfuehrungswurzel:
  `36ff715234dd8fd879b8e548b218505b1c216da217c8dc41638e81349f9ecca8`;
- Evaluationswurzel:
  `35e877d2529534c0bb1ce0708f057ff94866cf0edacac28c97e6529e0cbfa4eb`;
- Plan-Datei:
  `d1453b4abefdccb6425e4faf5b2d434cfda842f608d75bed585f5b12dd7338ae`.

Die getrennt freizugebende Rezeptormaterialisierung muss genau diesen Plan
unveraendert konsumieren. Sie besitzt kein Distanz-Erfolgsgate und darf keine
Variante ersetzen oder nachtraeglich anpassen.
