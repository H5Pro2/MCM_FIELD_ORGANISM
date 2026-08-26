# S2-AY: Private Probe-Aufrufstellenkonsolidierung

## Korrektur

S2-AY schliesst den S2-AX-Blocker durch eine rein mechanische Aenderung in
`mcm_field_organism._ppb1_active_batch_formation_probe_handoff`.

Die neue private Hilfsfunktion `_probe_modality_read_only` enthaelt die einzige
syntaktische Aufrufstelle von `probe_s1wu_perceptual_state`. Die bestehende
Handofffunktion ruft diesen Helfer weiterhin je einmal fuer Audio und Video
auf. Damit bleiben zwei Laufzeitproben pro gueltigem Handoff erhalten.

Distanz, Matchschwelle, Stabilisierung, Partition, Ergebnisdigest,
Fehlerverhalten und Systemgrenzen wurden nicht veraendert.

## Regression

Das gebundene S2-AW-Testmodul wurde einmal erneut ausgefuehrt. Alle 9 Tests
bestanden in 0,092 Sekunden. Die Regression umfasste erneut authentische
synthetische S2-AR-Bildung, positive und negative spaetere Proben sowie alle
fail-closed Grenzfaelle.

Die Testdatei selbst blieb unveraendert. Baselines, Feld, Produktion,
Live-Eingabe und oeffentliche API wurden nicht aufgerufen oder geaendert.

## Einordnung

Der Quellblocker ist technisch geschlossen. S2-AY erzeugt keinen neuen
funktionalen Befund; es bestaetigt nur, dass der bereits bestandene private
Handoff nach der Konsolidierung unveraendert funktioniert.

Der naechste Schritt ist S2-AZ: ein statischer Abschlussaudit von korrigiertem
Quelldigest, einzelner Probe-Aufrufstelle, Blockerschluss und Grenzen ohne
erneute Ausfuehrung.

Maschinenlesbarer Receipt:
[S2AY_PRIVATE_PROBE_AUFRUFSTELLEN_KONSOLIDIERUNG_UND_SYNTHETISCHE_REGRESSION_V1.json](S2AY_PRIVATE_PROBE_AUFRUFSTELLEN_KONSOLIDIERUNG_UND_SYNTHETISCHE_REGRESSION_V1.json).
