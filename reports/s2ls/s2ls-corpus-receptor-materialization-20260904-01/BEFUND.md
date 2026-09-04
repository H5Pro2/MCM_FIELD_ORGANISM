# S2-LS Korpus-Rezeptormaterialisierung 2026-09-04-01

Status: `S2LS_RECEPTOR_GEOMETRY_MATERIALIZED`

Der exakt versiegelte Plan
`1ad42964295cce44b87f6c3d02479983878ca7c403eee21440783fe3326e661a`
wurde genau einmal mit den unveraenderten Audio- und Videorezeptoren
materialisiert. Es gab kein Distanz-Annahmegate, keinen Retry und keine
Quellenanpassung.

## Umfang

- 21 kanonische Inhaltsquellen;
- 21 auditive Rezeptorzustaende mit je 48 Werten;
- 21 visuelle Vollzustaende mit je 288 Werten;
- vier tatsaechlich okkludierte visuelle Hinweiszustaende;
- 25 separate Ereignis-, Quellen- und Zeitbindungen;
- 210 vollstaendige paarweise Audio-/Video-Distanzzeilen;
- 168 Teilhinweis-Distanzzeilen;
- 210 auditive Hopaufrufe und 21 auditive Endpunkte;
- 25 visuelle Rezeptoraufrufe.

Alle kanonischen Byte-Digests wurden vor dem jeweiligen Rezeptoraufruf
geprueft. Rohpayloads wurden nach ihrer Reduktion verworfen und erscheinen
nicht im Ergebnis.

## Deskriptive Geometrie

Die folgenden Werte sind Messbefunde und keine Annahme- oder Ausschlussregel.

- Auditive Trainingsabstaende innerhalb Familie 01:
  `0.006747815432211364...0.018143183632148775`;
- auditive Trainingsabstaende innerhalb Familie 02:
  `0.006448210644485422...0.024498533668876273`;
- auditive Trainingsabstaende zwischen den Familien:
  `0.033140214890201226...0.03727860351918235`;
- visuelle Trainingsabstaende innerhalb Familie 01:
  `0.00013293920963447465...0.00014361244755103456`;
- visuelle Trainingsabstaende innerhalb Familie 02:
  `0.00013638684640522784...0.0001426025528524164`;
- visuelle Trainingsabstaende zwischen den Familien:
  `0.002242588431977727...0.002280276037884289`.

Die unabhaengig erzeugten RGB8-Texturen besitzen unterschiedliche
Payloaddigests, werden durch die blockweise Mittelung des bestehenden
Videorezeptors aber auf eng benachbarte visuelle Zustaende reduziert. Dieser
Befund bleibt unveraendert Bestandteil des spaeteren Funktionsvergleichs.

Die vier visuellen und vier auditiven Hinweise besitzen gegenueber ihrem
eigenen Holdout auf den jeweils beobachteten Positionen Distanz `0.0`; bei
den visuellen Hinweisen gibt es dort jeweils null exakte Abweichungen.

## Integritaet

- Distanz-Annahmegate: `False`;
- Quellenersetzungen: `0`;
- Quellneuerzeugungen: `0`;
- Quellskalierungen: `0`;
- Memoryaufrufe: `0`;
- Feldaufrufe: `0`;
- Kontextaufrufe: `0`;
- Gate nach Abschluss: `False`;
- Materialisiererhash vor/nach:
  `ff64b8ba1300d3552a2c673ef305427b2a4061522c8cf66ed4b345677cede76d`;
- Evidenzdigest:
  `0840c261f91f824cd913fb1bc5ccdd9ba21b75d6680e61948561a986e2443f9b`;
- Ergebnisdateihash:
  `e09583f995f75ff4d9454af969133b51d9b4852a404af24befa61fadb8757e8a`.

Der Befund bestaetigt ausschliesslich eine technisch vollstaendige
Rezeptorgeometrie. Er trifft noch keine Aussage ueber Memorybildung,
Generalisation oder den Vergleich von Adaptive, Frozen und Replay.
