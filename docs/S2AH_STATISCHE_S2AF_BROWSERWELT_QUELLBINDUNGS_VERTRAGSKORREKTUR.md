# S2-AH: Statische S2-AF-Browserwelt-Quellbindungskorrektur

## Ergebnis

S2-AH schliesst die in S2-AG gefundene Provenienzluecke auf Vertragsniveau.
Die geplante private Bindefunktion erhaelt kuenftig neben `binding_id`, Batch
und PPB-1-Profilbindung auch das validierte, unveraenderliche
`BrowserWorldContract`-Objekt.

Das historische S2-AF-Artefakt bleibt unveraendert. S2-AH ersetzt nur dessen
Funktionskopf und verschaerft die Pruefreihenfolge fuer die Vertragsquelle.
Alle sonstigen S2-AF-Grenzen bleiben verbindlich.

## Quellbindung

`source_contract_id` darf ausschliesslich aus
`browser_world_contract.contract_id` stammen. Der Vertragsdigest wird aus dem
kanonischen Inhalt des uebergebenen Quellobjekts neu berechnet. ID und Digest
muessen exakt den entsprechenden Batchwerten entsprechen.

Ein externer Soll-Digest, eine separat uebergebene Vertrags-ID, das blosse
Vertrauen in den Digeststring des Batches oder eine Rekonstruktion des
Vertrags aus Rezeptorframes sind nicht zulaessig.

Der kanonische Vertragsinhalt wird nicht in der spaeteren Huelle gespeichert.
Die Huelle traegt nur die nachgepruefte Vertrags-ID und den neu berechneten
Digest. Vertrag, Batch, Profil und Frames muessen vor und nach der Bindung
unveraendert sein.

## Atomare Pruefreihenfolge

Zuerst werden Typ und Digest des Browserweltvertrags geprueft. Danach folgen
Batchdigest sowie die exakte Uebereinstimmung von Vertrags-ID und
Vertragsdigest. Erst anschliessend duerfen Profil-, Geometrie-, Traeger-,
Snapshot- und Zeitrollen geprueft werden.

Bei jeder Abweichung entsteht weder eine Teilhuelle noch ein Receipt. PPB-1-
Zustandsbildung, Probe, Baseline und Feldpfad werden von der Bindung nicht
aufgerufen.

## Grenze und naechster Schritt

S2-AH implementiert und fuehrt nichts aus. Neue Parameter, Wertetransformation,
API-, Snapshot-, Produktions-, Live- oder Feldintegration bleiben gesperrt.
Der Blocker ist nur auf Vertragsniveau geschlossen.

S2-AI soll die korrigierte Gesamtbindung statisch abnehmen und entscheiden,
ob danach eine getrennt freizugebende private Implementierung methodisch
zulaessig ist.

Maschinenlesbare Vertragskorrektur:
[S2AH_STATISCHE_S2AF_BROWSERWELT_QUELLBINDUNGS_VERTRAGSKORREKTUR_V1.json](S2AH_STATISCHE_S2AF_BROWSERWELT_QUELLBINDUNGS_VERTRAGSKORREKTUR_V1.json).
