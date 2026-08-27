# S2-DZ-Korrektur und statischer S2-DX-Wiederholungsaudit

## Quellen und Grenze

Korrekturcommit: `a2819b854d381f8923b18b9313474da0b56389f4`.
Vorgaenger: `9218edab54756a42be10998492cbbe3d7c25a260`.
Vorgaengeraudit: S2-DX nach S2-DY, Artefaktdigest
`200a8f2db75395176475e8233c58fcbe89be4eea9c46301021583f98395ea3fd`.

Die S2-DZ-Freigabe umfasst nur die vollstaendige R0-Projektion und den
verrutschten Rueckgabeblock. Anschliessend ist S2-DX rein statisch zu
wiederholen. Der Audit verwendet Quelltext, AST, Git-Differenzen und
Dokumentdigests; keine Projektimporte, Zustandsfunktionen, Tests,
Comparatoren oder Vergleichszellen. Keine Laufnummer wurde vergeben.

## S2-DZ: Umgesetzte Korrekturen

Es wurden genau die zwei privaten Dateien geaendert:

- `mcm_field_organism/_tspm1_s2dr_private_comparison.py`
- `tests/test_tspm1_s2dr_private_comparison_contract.py`

### DX-RB01: Zustandsidentitaet der R0-Projektion

`_ppb_projection` uebernimmt jetzt alle Felder des unveraenderten
PPB-Bankzustands: Schema, Bank-ID, Konfigurationsdigest, Schrittzahl,
Quelluhr, Endtick und vollstaendige Slotdaten einschliesslich Slot-ID.
Die Reihenfolge der auditiven und visuellen Baenke bleibt erhalten.

`_two_level_payload` erhaelt die vier Fast-Quelluhr-/Endtick-Rollen aus
beiden Armen. Fast-Slot-IDs werden vor der positionsgleichen Normalisierung
gegen die drei erwarteten IDs des jeweiligen Arms geprueft. Es wird keine
TSPM-spezifische Zustandsklasse im generischen Helper verwendet.

Der registrierte Initialdeskriptor bleibt unveraendert. Er wird bei
Generation null nicht mehr allein anhand der Generation zurueckgegeben:
vorher werden die leeren Slots, Quellrollen und vollstaendigen PPB-Baenke
gegen die bestehende Profilkonfiguration geprueft. Diese Pruefung erzeugt
keine zusaetzlichen funktionalen Bankzustaende.

`_exact_reduction_projection` erhaelt zusaetzlich die ausgewaehlten
PPB-Slot-IDs. Nicht-Mapping-Eintraege oder fehlende Projektionsfelder
werden mit `S2DR_RESULT_RELATION_MISMATCH` abgelehnt. Es gibt keine
Filterung mehr, die Ereignis- oder Findingpositionen verschwinden laesst.

### DX-RB02: Rueckgabe des mutierten Testergebnisses

Der vorhandene `S2DRCellResult`-Aufbau steht wieder unmittelbar nach dem
Receiptaufbau in `rebuilt_result`. Der unerreichbare zweite Rueckgabeblock
in `synthetic_comparison` ist entfernt. Beide Helper besitzen genau einen
erreichbaren abschliessenden Rueckgabeblock.

Die AST-Differenz bestaetigt: keine neue Definition, keine entfernte
Definition und keine geaenderte Testmethode. Es bleiben 51 Definitionen
T01-T51 einschliesslich zwoelf Fail-Closed-Faellen. T35-T39 und T51 verwenden
weiterhin den echten Comparator-Aufrufpfad. T44 und die S1WU-Quellbindung
sind unveraendert.

## S2-DX: Statische Abnahme und verbleibender Blocker

DX-RB01 und DX-RB02 sind im geprueften Korrekturumfang geschlossen.
R0 besitzt weiterhin eigene generische Zustaende und Operatoren; seine
Initialisierung, Fortschreibung und Probe wurden nicht geaendert.
Die neuen Projektionshelper enthalten keine TSPM-Typen oder -Operatoren.
TSPM-1-Grundkern, PPB-1, oeffentliche API, Snapshot und Feldpfad sind
gegenueber dem Vorgaenger unveraendert.

T48 und T49 erhalten aus `rebuilt_result` wieder den vorgesehenen
Ergebnistyp. Bei gueltiger Vorbereitung fuehrt die vertauschte Budgetquelle
zum Relationsfehler und die erhoehte Ressourcennutzung zum Budgetfehler.
Dies ist eine Quellpfadableitung, kein ausgefuehrter Testbefund.

### DX-ZB01: T50 scheitert bereits in seiner Quellenvorbereitung

Die vollstaendige statische Aufrufkette von T50 lautet:

`test_t50_operation_limit_exceeded_fails_closed`
-> `valid_cell("H1", "TSPM1")`
-> `S2DRCellOwner.consume_once`
-> `advance_s2dr_arm`
-> `_bound_pair`
-> `_sequence`
-> `ReceptorContactFrame.__post_init__`.

Die Testdatei bindet `H1` in Zeile 481. Das Vergleichsmodul setzt diesen
Wert in Zeile 932 unveraendert in `snapshot_id` ein, etwa
`s2dr.H1.formation.001.auditory`. Der unveraenderte Rezeptorvertrag erlaubt
in `technical_identifier` jedoch ausschliesslich
`^[a-z][a-z0-9_.-]*$` und validiert auch `snapshot_id`.

Damit wuerde die Vorbereitung mit `ReceptorContractError` abbrechen,
bevor T50 seinen Operationszaehler auf 294 setzt und den relationalen
Budgetvalidator aufruft. Der reparierte Rueckgabeblock kann diesen
vorgelagerten Fehler nicht beheben. Auch die privaten Frame-ID-Formate
der Registry und die Envelope-Bindungs-ID verwenden die unveraenderten
Grossbuchstaben; eine spaetere Korrektur muss diese Quellen konsistent
behandeln, statt die Rezeptorvalidierung aufzuweichen.

Quellstellen im Korrekturcommit:

- Testdatei: Zeilen 51-58 und 480-491.
- Vergleichsmodul: Zeilen 565-566 und 927-951.
- `mcm_field_organism/receptor_contract.py`: Zeilen 18-27 und 61-66.

Dieser Fehler bestand bereits vor S2-DZ und wurde im vorherigen Audit
nicht als Blocker erfasst. Er wird hier statisch dokumentiert, nicht
ausgefuehrt oder repariert. Eine Quellen-ID-Korrektur gehoert nicht zu den
zwei freigegebenen S2-DZ-Aenderungen.

## Entscheidung

S2-DZ: `SCOPED_CORRECTIONS_COMPLETE`.
S2-DX: `BLOCK_TEST_EXECUTION_T50_SOURCE_IDENTIFIER_PREFLIGHT`.

Die beiden Korrekturen sind abgeschlossen, der Gesamtaudit ist nicht
bestanden. Die 51 Vertragstests und alle 56 Vergleichszellen bleiben
gesperrt. Es entsteht kein Funktions-, Vergleichs- oder Memory-Befund.

Naechster vorgeschlagener Schritt: S2-EA als eng begrenzte Korrektur der
privaten technischen Quellen-ID-Bindung fuer Registry, Frame und Envelope.
Die fachlichen H1-H7-Geschichtsrollen bleiben unveraendert; der
Rezeptorvertrag wird nicht gelockert. Diese Korrektur benoetigt eine eigene
Freigabe. Danach erneut S2-DX, weiterhin ohne Test- oder Zellenausfuehrung.
