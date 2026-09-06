# S2-NC: Quelleninventar und Konkurrenzpanels vorversiegelt

Status: `SOURCE_INVENTORY_AND_PANELS_PRESEALED`.

Das neue Inventar wurde genau einmal zur PCM-Hashbindung erzeugt.
Der isolierte Standardbibliotheksaufruf endete mit Exit-Code `0`.
Es gab keinen Retry, keine Parametersuche und keine nachtraegliche
Aenderung an Inventar, Panels oder Auswertungsrelationen.

## Umfang

- 23 Mono-PCM-F32LE-Fenster mit je 4.800 Samples bei 48.000 Hz.
- 20 unterschiedliche Payloads und drei beabsichtigte exakte Wiederholungen.
- Neun Referenzquellen, 14 spaetere Hinweisquellen.
- Drei Panelpaare mit jeweils unveraenderter Konkurrenz nach Entfernung
  der zugeordneten bekannten Referenz aus B4 und Fast.
- 48 Hinweis-/Panelfaelle je Regel, davon neun bekannte Sollzulassungen
  und 39 Sollenthaltungen in getrennt ausgewerteten Kategorien.
- 528 belegte Beziehungen und 12.672 Banddifferenzen je spaeterem Arm;
  25.344 Banddifferenzen fuer beide Regeln zusammen.

Nur der Generator erzeugte PCM-Bytes. Die Rohpayloads wurden nach der
Hashbindung verworfen und nicht gespeichert. Weder historische
Rezeptorvektoren noch historische Distanzmatrizen wurden gelesen.

Die vorab gebundenen Hinweise enthalten exakte Wiederholungen,
Pegelvarianten (-25 Prozent), Frequenzvarianten (+3 Prozent), unbekannte
Rezepte, Stille, eine sehr leise Variante sowie eine gleichgewichtete
Mischung zweier Referenzrezepte. Die Kategorien sind externe Testvorgaben.
Insbesondere beweist die Kategorie der leisen Variante keine gemessene
Informationsarmut, und die Mischung keine gemessene Mehrdeutigkeit.

## Getrennte Wurzeln und Pruefung

`execution-plan.json` bindet ausschliesslich die neutralen Quellen,
Zeitfenster, Positionen, Faelle, Profil-/Regelparameter und Arbeitsbudgets.
`evaluation-plan.json` bindet separat Kategorien, Sollrelationen und Nenner.
Der Ausfuehrungsplan kennt den Evaluationsdigest nicht. `seal.json` bindet
beide Digests, die Dokument-/Quellhashes sowie die Generatorversion.

Eine anschliessende read-only Strukturpruefung bestaetigte:

- alle drei kanonischen Wurzeldigests und alle 23 Rezeptdigests;
- Quellenordinalzahlen, Fenster und Referenz-/Hinweistrennung;
- die sechs vollstaendigen Panels und reine Entfernung ohne Ersatzquelle;
- 48 Faelle, 528 belegte Beziehungen je Arm und alle Budgetadditionen;
- die unveraenderten Quell-, Vertrags- und Skripthashes.

Diese Pruefung erzeugte kein weiteres PCM und berechnete keine Distanz.
Es wurden keine Vergleichs- oder Projektfunktionstests ausgefuehrt.
Rezeptor-, Regel-, Memory-, Feld- und Kontextaufrufe: jeweils `0`.

## Digests

- Ausfuehrungswurzel:
  `00a0f5d177d11702b6ac08056d08b0501f125cefa8f0c0f1e3b651b894c67ae2`.
- Auswertungswurzel:
  `5f81b3e4c2e1f746659a9ef529ad6af91dbe0e890c4043edbd99ebf1ea36e641`.
- Gemeinsames Siegel:
  `ac2ec3e0441fb463c2a1a80d8cb296bbc4934f7555899c5750aa32a0ea56679b`.

## Grenze

Dies ist kein positiver Geometrie-, Anwendbarkeits- oder Memorybefund.
Die strengere Regel ist weiterhin weder implementiert noch qualifiziert.
S2-KZ, Memorykerne, Runtime, README und historische Belege sind unveraendert.
Die bekannte Bootstrap-Datei blieb ausgeschlossen und unberuehrt.

Als naechster enger Schritt ist die einmalige Materialisierung der
23 Rezeptorfenster aus genau diesen Quellen zu entscheiden. Ein
ungueltiger Rezeptorausgabewert darf nicht durch Clipping oder erneute
Skalierung repariert werden. Unguenstige, aber gueltige Geometrie bleibt
ein regulaerer Befund; sie erlaubt keinen Austausch der Quellen.
