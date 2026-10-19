# S2-UC / V7: Gesamtanschluss derzeit nicht budgetierbar

**Entscheidung: Budgetkonflikt. Keine Implementierung und keine weitere Verkleinerungsrunde.** Die Quellenkette und der V7-Abschluss sind einzeln vorhanden, aber ihre fachlich vollstaendige Verbindung passt nach der nachfolgenden einmaligen Aufwandsabschaetzung nicht in den verbleibenden Spielraum. Eine blosse Starterumschaltung waere unvollstaendig.

## Messung und Abschaetzung getrennt

Statisch nachgemessen: **40 gebundene Dateien, 654.068 Byte; Grenze 655.360; frei 1.292 Byte.** Alle Dateihashes entsprechen dem angenommenen Publikationsstand. Das bestehende Inventar wurde nachgemessen, nicht durch einen neuen Importgraphen ersetzt: Es gab keine Codeaenderung. Keine Projektmodule importiert, Tests oder Quellen ausgefuehrt.

[STATIC_EVIDENCE.json](STATIC_EVIDENCE.json) enthaelt Dateigroessen, Hashes, gemessene Vergleichsfunktionen, die nachfolgende Schaetzrechnung und die Archivpruefung. Die Zusatzwerte sind **Planansatzbereiche**, keine gemessenen Bytes eines noch nicht geschriebenen Patches und keine mathematische Untergrenze fuer jede denkbare Kodierung. Unter den Vorgaben des Auftrags wird daraus keine Komprimierungs-/Verkleinerungssuche abgeleitet.

## Einziger betrachteter Integrationspfad

Ausfuehrungszulassung -> exklusiv reservierter Lauf/Ausgabeordner -> einmaliger SourceAdapter -> connection.execute -> vollstaendiger oder partieller Quellenabschluss -> strikte Recordpruefung -> V7-Publikation im bereits eigenen Ausgabeordner -> Gate in jedem Fall schliessen.

Dies ist die vollstaendige Lueckenabgrenzung, **kein als budgetkonform freigegebener Bauplan**. Neutrale Entwicklungsbelege bleiben vom Ausfuehrungsvertrag getrennt. Der Default und die derzeitige echte Startersperre bleiben unveraendert.

| Uebergang | Wiederverwendbar | Notwendige Aenderung | Neutrale Gegenproben |
|---|---|---|---|
| Ausfuehrungszulassung | `_s2uc_prestart_v7.validate`, `_s2uc_inventory_v7.current`, `_s2uc_run_binding.validate`/`_run_pair`; bestehende Beleg-/Hashpruefer | Eigenes geschlossenes Ausfuehrungsschema mit Lauf-ID, festem Ausgabepfad, Quellen-/Manifestbindung, qualifikationsgebundenem aktuellem Code und ausdruecklicher Einmallaufautorisierung. Entwicklungsstatus oder `authorize=True` allein darf keine Zulassung ersetzen. Vorstartinventar weiter voll pruefen; keine Uebernahme des V6-Ledgers. | Synthetische/strukturelle Belege bleiben gesperrt; falsche Lauf-ID, Ausgabe, Quelle, veralteter Code oder unpassende Qualifikation: Supplier 0. Isolierte neutrale positive Ausfuehrungszulassung mit fest gebundenem Testlieferanten. |
| Einmalige Materialisierung und beide Arme | `SourceAdapter.__call__`, `materialize`, `connection.execute` | Materialisierung selbst unveraendert wiederverwenden. `execute` ruft den Adapter pro Nicht-CLOSE-Ereignis einmal und verwendet dasselbe Werte-Tupel fuer beide Frames. Keine zweite Materialisierung, keine Deduplizierung wiederholter Quellen. Die Anschlusskontrolle liegt im Ausfuehrungsrahmen. | Durch den neuen Gesamtpfad 58 Endpunktverwendungen; Hash-/Audio-/NJ-Zaehler jeweils 58; identische Werte-Tupel fuer beide Arme, Reihenfolge und keine Deduplizierung; Ausfall zwischen den Armaufrufen. |
| Vollstaendige Materialisierungs-/Quellenabschlusspruefung | `SourceAdapter.complete`, `MaterializationCounters.snapshot`, `verification.verify(..., require_source_completion=True)`, `verify_failure`, `_materialization`, `HalfScaleAuditory48V1`/`validate_projection` | Im Ausfuehrungsmodus Receiptpflicht je erfolgreichem Endpunkt erzwingen. Projektion samt Werten, Digest, Profil, Snapshot und Zeitfenster sowie redundante Receiptangaben konsistent pruefen. Erfolgsabschluss verpflichtend; fuer Abbruch einen oeffentlichen partiellen Adapterabschluss mit Versuchen, Erfolgen, Phasenzaehlern und erreichtem Schritt bereitstellen und gegen Recordpraefix abgleichen. Keine zweite PCM-/Rezeptorausfuehrung zur Verifikation. | Entferntes Receipt trotz korrekter Gesamtzaehler; manipulierte Projektion/Werte/Zeitfenster; fehlender oder gefaelschter Abschluss; Fehler bei Supplier, Hash, Rezeptor, NJ und nach Materialisierung; Versuch 58 mit nur 57 Erfolgen; Ownerfehler nach allen 58 Endpunkten. |
| Erfolgs-/Abbruchrecord zum V7-Abschluss | `codec.dumps/loads`, `_Publication.atomic/snapshot/failure/finish`, `verification.verify/verify_failure`, `evaluation.evaluate` | Geschuetzter Ausfuehrungsabschluss neben unveraendertem neutralem Wrapper. Er nimmt materialisierte Records und den validierten Ausfuehrungskontext an. Der Ausgabeordner muss schon vor dem ersten Supplier exklusiv reserviert sein: `publish_neutral` verlangt dagegen einen noch fehlenden Ordner. Deshalb internen Abschluss an eine bereits besitzgebundene Publikationssitzung anschliessen. Fehler vor Record/Codec ebenfalls an Fehlerabschluss uebergeben. V7-Hashanker und Bilanzregeln unveraendert erhalten. | Vollstaendiger materialisierter Erfolg bis erneut gelesenem V-Beleg; Materialisierungsabbruch, Codecfehler und nachgelagerte Abschlussfehler erhalten Primärfehler und sperren Auswertung; bereits vorhandener Ausgabeordner stoppt vor Supplier. |
| Primaerfehler, Owner, Gate, Einmaligkeit | `connection._close_pair`, Fehlerpraefix von `execute`, Gate-/USED-Muster in `run_once`, V7-Fehlerabschluss | Ein zusammenhaengender Lebenszyklusrahmen: Zulassung und Ausgaberesevierung vor Supplier; Einmaligkeit vor erster Quellenarbeit verbrauchen; keine automatische Freigabe bei Fehler. Gate in `finally` schliessen. Beide erzeugten Owner abschliessen, auch bei zweitem Konstruktorfehler. Partiellen statt vollen Quellenabschluss nach Abbruch verwenden; spaetere Abschlussfehler nur sekundaer erfassen. Einmaligkeit an unveraenderliche Lauf-ID/Ausgabe koppeln, nicht allein an prozesslokales USED. | Zweiter Start, erneuter Versuch nach Abbruch, frischer Prozess mit vorhandener Laufablage; Fehler in Ownerkonstruktion/-abschluss, Quellenabschluss, Codec und Publikation; erster Fehler bleibt erhalten, Gate false, keine nachfolgende Geschichte. |

## Konkrete Anschlussluecken

1. `evidence_expected()` verlangt `STRUCTURAL_EVIDENCE_ONLY` und `execution_authorized=false`; `validate()` akzeptiert nur Entwicklungsarten und liefert keine Ausfuehrungszulassung. Das Ersetzen eines Statusstrings waere keine Qualifikations- oder Laufbindung.
2. `_Publication.__init__` verlangt `synthetic-development`; `publish_neutral` verweigert Materialisierungsreceipts und `source_completion`. Diese Grenzen einfach zu entfernen, ohne eine strengere Ausfuehrungspruefung einzubauen, waere eine Pruefluecke.
3. `_materialization(None, ...)` ist im neutralen Verifier erlaubt. Vorhandene Receipts werden derzeit nur teilweise geprueft; insbesondere wird der Projektionsdigest dort nicht aus rekonstruierten Werten nachgerechnet. `require_source_completion=True` erzwingt den Gesamtabschluss, ersetzt aber keine Receiptpflicht. `verify_failure` prueft den Verbindungspraefix, besitzt jedoch keinen verpflichtenden partiellen Quellenabschluss. Die vorhandene NJ-Projektionsvalidierung ist wiederverwendbar; nicht gespeicherte rohe Rezeptorwerte sind nachtraeglich nicht vollstaendig rekonstruierbar. Deren Ursprung muss durch die bereits gepruefte Materialisierung gebunden bleiben, nicht durch eine erfundene Offline-Nachrechnung.
4. Der alte `run_once` ruft `completion()` auch nach einem abgebrochenen Verbindungsrecord auf. `SourceAdapter.complete()` verlangt alle 58 Verwendungen und wuerde einen weiteren `ENDPOINT_COUNT_INVALID` ausloesen. Der neue Gesamtpfad muss stattdessen den originalen Abbruch samt partiellem Quellenstatus erhalten.
5. `connection.execute` erzeugt die beiden Owner vor seinem Ereignis-try. Ein Fehler beim zweiten Konstruktor ist durch `_close_pair` allein nicht abgedeckt. Gate/USED im alten Einstieg sowie die V7-Ordnererzeugung bilden derzeit ebenfalls keinen gemeinsamen Ausfuehrungsrahmen.

## Einmalige Zusatzbudgetrechnung

Alle Werte sind **zusaetzliche Netto-Planansaetze** nach Wiederverwendung vorhandener Funktionen, inklusive notwendiger Aenderungen/Imports und neutraler Anschlussgegenproben. Vorhandener Code wird nicht ein zweites Mal als Zusatz gerechnet. Keine Testdatei wird aus dem Inventar entfernt; keine Einsparung durch eine nicht beauftragte Verkleinerung angenommen.

| Uebergang | Produktion zusaetzlich | Tests zusaetzlich |
|---|---:|---:|
| Ausfuehrungszulassung | 1.200–2.000 | 900–1.400 |
| Materialisierung / gemeinsame Armwerte | 0 | 800–1.100 |
| Strikte Receipts und voller/partieller Quellenabschluss | 1.400–2.200 | 1.400–2.200 |
| Besitzgebundene Record-/Fehleruebergabe an V7 | 1.100–1.800 | 900–1.400 |
| Lebenszyklus, Primaerfehler, Gate, Einmaligkeit | 600–1.000 | 900–1.400 |
| **Summe** | **4.300–7.000** | **4.900–7.500** |

**Gemeinsam: 9.200–14.500 Byte zusaetzlich.** Gegenueber 1.292 freien Byte ergibt das ein **geschaetztes Defizit von 7.908–13.208 Byte**. Gesamtansatz: **663.268–668.568 Byte** gegen unveraenderte **655.360 Byte**. Bereits der untere Produktionsansatz ueberschreitet den gesamten freien Raum um 3.008 Byte; Tests kommen zwingend hinzu.

Die Groessenordnung stuetzt sich auf statisch gemessene Vergleichsstellen, nicht auf ein bereits geschriebenes Integrationsmodul: bestehender Starterrumpf 540 Byte; struktureller Beleggenerator 1.019 Byte; vorhandene Materialisierungs-Receiptpruefung 894 Byte. Bei Tests beanspruchen allein der vorhandene Quellenabschluss-Manipulationstest 2.000 Byte, ein vollstaendiger Eintritts-/Verifikationstest 1.434 Byte und der V7-Starterstopp-Test 1.170 Byte. Die konkreten Zeilen und Bytebereiche stehen im maschinenlesbaren Beleg. Diese Vergleichsfunktionen bleiben wiederverwendbar; ihre Groessen sind keine behauptete unvermeidbare Kopiermenge.

## Konsequenz

**Kein tragfaehiger Gesamtanschluss innerhalb des aktuellen Restbudgets ausgewiesen. STOPP fuer eine Starteranbindung unter dieser Budgetannahme.** Das ist keine allgemeine Unmoeglichkeitsaussage ueber andere Architekturen, sondern der Budgetkonflikt dieses vorhandenen Aufbaus ohne weitere Verkleinerungsrunde.

Keine Implementierung, keine neuen Tests ausgefuehrt, keine Quellenproduktion und keine Ausfuehrungsfreigabe. Alle 117 bestehenden Pruefpflichten bleiben bestehen. Archivierte Publikationsbelege und gebundene Quelldateien wurden per Groesse/Hash auf Unveraendertheit kontrolliert.

Naechster vorgeschlagener Schritt fuer den Projektleiter: diesen konkreten Konflikt als Architekturentscheidung behandeln. Innerhalb des jetzigen Auftrags wird weder eine Grenze erhoeht noch ein weiterer Umbau begonnen; eine Starteroeffnung ist nicht der naechste zulaessige Schritt.
