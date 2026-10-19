# V9 Entwicklerpaket: Umfang und Versionsgrenzen

Grundlage ist der aktuelle direkte Auftrag des Projektleiters: Quellenanschluss, gemeinsamer Kern, begrenzter Prozesseinstieg, neutrale Gegenproben und Regression; Codegrenze 851968 Byte. Keine Quellenproduktion, keine finale reale Laufbindung, keine Hauptlauffreigabe.

## Standabgleich

Die oberste Standseinordnung in AKTUELLER_FORSCHUNGSWEG.md beschreibt noch den abgeschlossenen V6-Modultrennungszweig und keinen Umsetzungsauftrag. Der neuere direkte V9-Auftrag sowie der statische Anschlussplan sind die operative Grundlage dieses Pakets. Die alte Standseinordnung wird nicht als reale Freigabe gelesen und nicht umgeschrieben.

## Gemeinsamer Kern

V8-Vertrag, V8-Binder und historische Bindungen bleiben unveraendert. In tools/_s2uc_execution_v8.py wird lediglich die vorhandene Funktion als privater gemeinsamer _run-Kern mit Validator- und Publisherparametern verfuegbar. Der bisherige run_neutral-Einstieg uebergibt weiterhin ausschliesslich den V8-Validator und V8-Publisher. Der V9-Einstieg uebergibt seinen getrennten Validator und eine Publisher-Unterklasse. Keine zweite Materialisierung, kein zweiter Lebenszyklus, kein zweiter Publikationsalgorithmus. Der gemeinsame Quelltext aendert seinen Hash; alte archivierte Inventare werden nicht nachtraeglich angepasst. Alle alten Testdateien bleiben bytegleich.

## Evidenzgrenze

Fuenf synthetische Nichtnull-PCM-Fixtures haben eigene neutral-v9-IDs. NU-Erzeugung wird im Test ersetzt bzw. gegen versehentliche Aufrufe gesperrt. Das Vorbereiten des NU-Suppliers erzeugt keine Payloads; sein Aufruf wird ausschliesslich mit einem Mock des Generators auf feste Fensterwahl, fehlenden Cache und Objektidentitaet geprueft.

Fixturebelege tragen SYNTHETIC_FIXTURE_NOT_EXECUTED/FIXTURE_ONLY. Der Belegleser prueft Hash-, Test-ID- und Protokollkonsistenz ausgefuehrter neutraler Entwicklungstests; er ist keine unabhaengige Zertifizierungsinstanz. Auch ein konsistent gefaelschtes neutrales Protokoll kann niemals eine reale Zulassung erzeugen. Der oeffentliche Realeinstieg stoppt unbedingt nach der Strukturpruefung.

candidate_gains und candidate_losses bleiben wissenschaftlich unveraendert leer; V9 kennzeichnet sie als NOT_MEASURED. Keine Nullgewinn-/Nullverlustmessung und keine neue Bewertungsregel.

640 MiB Prozess-Commit bleibt ein neutraler Testparameter. Ein fehlender Produktabschluss ist NOT_EVALUABLE; ein externer Prozessbeleg ist kein Produktabschluss. Keine Wiederholung der historischen Allokationsmessung vorgesehen.

## Begrenzte Qualifikationsbelege

Der ausfuehrliche test-result.json-Entwicklerbericht ist kein aktives Zulassungsartefakt. Der Leser verwendet qualification-summary.json (urspruengliche 16384-Byte-Grenze), tests.log mit allen Test-IDs und Ergebnissen (32768 Byte) sowie dependency-inventory.json (16384 Byte). Hash und exakter Inhalt werden gegen den aktuellen Code-, Werkzeug- und Runtimebestand geprueft. Der Quellen-Vorbereitungsleser zaehlt die tatsaechlichen Bytes dieser drei Belege, des unveraenderten NU-Plans und des separat begrenzten Quellenkontexts. Die daraus erzeugte Bilanz ist eine vorbereitende Lesebilanz, keine finale reale Ausfuehrungsbindung.

Der erste gemeinsame Durchgang unter final wurde fuer diese Ergaenzung kontrolliert unterbrochen und ist keine Endqualifikation. Ausschliesslich final-02 bezeichnet den abschliessenden gemeinsamen Teststand.
