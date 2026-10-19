# S2-UC V8: neutraler Gesamtanschluss, Entwicklerabschluss 2026-09-20

**Umgesetzt und neutral nachgewiesen: 138/138 Tests bestanden, Exitcode 0.** Davon 117 unveraenderte Regressionstests und 21 neue V8-Tests. Keine offenen Implementierungs- oder Testfehler im beauftragten neutralen Umfang. Der oeffentliche reale Starter bleibt unbedingt gesperrt. Unabhaengige Abnahme, RAM-Nachweis und eine reale Hauptlaufbindung sind nicht Bestandteil dieses Nachweises.

Der aktuelle direkte V8-Auftrag des Projektleiters ist die Grundlage. Die aelteren Standseinordnungen in Forschungsweg und README werden dadurch nicht als heutige Realfreigabe interpretiert. Historische Befunde wurden nicht umgeschrieben.

## Implementierung

- `_s2uc_resources_v8.py`: eigener prospektiver Ressourcenvertrag `s2uc.resources.separate-code-artifacts.v8`, Codegrenze 720896 Byte. Alle anderen V7-Grenzen, Kategorien und Reserven bleiben gleich; der V7-Vertrag bleibt bytegleich.
- `_s2uc_binding_v8.py`: feste Rollen, Dateinamen, Hashes, vollstaendige Importvereinigung einschliesslich aller gebundenen Tests, Quellen-/Manifestbindung sowie exakt typisierte neutrale Einmalauthorisierung. Lauf-ID und kanonische Ausgabe sind gebunden. Entwicklungsbindung und V7-Mischung werden verworfen. Die in Tests erzeugten Belege sind ausdruecklich neutral und keine formale Qualifikation.
- `_s2uc_execution_v8.py`: isolierter Einstieg mit explizitem Supplier ohne NU-Default. Ausschliesslich gebundene Null-PCM-Fixture. Einmalige Materialisierung pro Endpunkt ueber den vorhandenen Adapter; dasselbe unveraenderliche Wertetupel geht an beide Arme. Receiptpflicht, Rekonstruktion der NJ-Projektion einschliesslich Digest, Profil, Zeit, Werten und Querbindungen; Abgleich mit dem unmittelbar beobachteten Materialisierungsdigest.
- Vollstaendiger oder partieller Quellenabschluss bewahrt Versuche, Erfolge und Hash-/Rezeptor-/NJ-Zaehler. Fehler im 58. Versuch behalten 57 Erfolge. Ein Fehler zwischen beiden Armen behaelt das noch nicht im Ereignisrecord stehende Receipt. Quellenabschluss und Laufabschluss werden getrennt beurteilt.
- Gemeinsamer Lebenszyklus reserviert einen neuen Ausgabeordner vor Supplierarbeit und verbraucht die Lauf-ID vor Ausfuehrung. Beide Owner werden vor ihrer Initialisierung registriert und im Abschluss behandelt; auch Konstruktor- und Closefehler sind getestet. Gate-Ruecksetzung erfolgt im finally. Ursprungsfehler bleiben vorrangig; nachgelagerte Fehler werden sekundaer dokumentiert.
- `_s2uc_publication_v7.py`: gemeinsamer interner Publikationsabschluss mit versionsgebundener Bilanz und Verifikation. Kein zweiter Publisher. Die bestehende V7-Neutralhuelle behaelt ihre Schranke gegen materialisierte Records. Record und separater Verifikationsbeleg werden erneut gelesen und durch das Terminal per Hash gebunden.
- `_s2uc_inventory_v7.py` teilt nur die vorhandene Inventarisierung; `_s2uc_neutral_connection.py` ergaenzt die Ownerfactory. `_s2uc_run_binding.py` verwirft V8 am realen Einstieg; `s2uc_run_bound_once.py` oeffnet auch nach anderweitig erfolgreicher historischer Zulassungspruefung keinen Lauf. Wissenschaftlicher Armcode, Hypothesen und Grenzwerte bleiben unveraendert.

## Dateien und SHA256

Alle neun neuen/geaenderten Pythondateien, abgeglichen gegen den vor Arbeitsbeginn gesicherten Stand. Keine Pythondatei entfernt. Vollstaendige Vorher-/Nachherhashes: [changed-files.json](changed-files.json).

| Datei | Byte | SHA256 |
|---|---:|---|
| [tools/s2uc_run_bound_once.py](../../../tools/s2uc_run_bound_once.py) | 1072 | `f3250dba8334b41858dece27f9a77e8e517cf1c1461c6960ef95883f523865dc` |
| [tools/_s2uc_binding_v8.py](../../../tools/_s2uc_binding_v8.py) | 7347 | `f10554a0b7d598d24a5f2cbfcfbf4e146b33e74989861e0c4be80cd328a65b90` |
| [tools/_s2uc_execution_v8.py](../../../tools/_s2uc_execution_v8.py) | 11226 | `bf2f0ec2d91ec2afaa299a4ff7ce3aa15656bc24d49be2304fa6c59d12dba179` |
| [tools/_s2uc_inventory_v7.py](../../../tools/_s2uc_inventory_v7.py) | 8982 | `c070fea8fe154b14f6c4a96ea0171d2dcb5dc8a2c41120544e76e8665705901e` |
| [tools/_s2uc_neutral_connection.py](../../../tools/_s2uc_neutral_connection.py) | 8836 | `27fa0812e8da3b84e585d785ad687be8fcc480ef328503457f4803f6c9d05a3b` |
| [tools/_s2uc_publication_v7.py](../../../tools/_s2uc_publication_v7.py) | 14606 | `21c79a6346f6534c2262d964fe230b7256e19c1bad1768de366b5a05f67795db` |
| [tools/_s2uc_resources_v8.py](../../../tools/_s2uc_resources_v8.py) | 911 | `62d000968c604abd735e9fdf9592969f203b3beda2bd42bb4c8c90c07b05b17e` |
| [tools/_s2uc_run_binding.py](../../../tools/_s2uc_run_binding.py) | 35066 | `459e6049a1fe975f986abca0a9943afba868aab5edf23f45c1777eda247a8b78` |
| [tests/test_s2uc_execution_v8.py](../../../tests/test_s2uc_execution_v8.py) | 24620 | `9a30da7e42bf930f249aed3d29cf24316f20ecce3b1b0ff90f25e37765fc0fcc` |

## Ausgefuehrte Tests

Gemeinsamer Enddurchgang: **138 Tests, 0 Fehler, 0 Fehlschlaege, 0 uebersprungen**, 556.543 Sekunden, Exitcode 0. Alle erwarteten IDs stimmen exakt mit den ausgefuehrten IDs ueberein. Codehashes vor/nach Durchgang identisch.

Jede vollstaendige Test-ID mit Ergebnis steht in [TESTS.md](TESTS.md) und [test-result.json](final/test-result.json); Originalprotokoll: [tests.log](final/tests.log).

| Suite | Bestanden |
|---|---:|
| `tests.test_s2ub_candidate_confirmation` | 11/11 |
| `tests.test_s2uc_neutral_connection` | 11/11 |
| `tests.test_s2uc_materialization_connection` | 46/46 |
| `tests.test_s2uc_resource_contract_v7` | 14/14 |
| `tests.test_s2uc_prestart_v7` | 16/16 |
| `tests.test_s2uc_publication_v7` | 19/19 |
| `tests.test_s2uc_execution_v8` | 21/21 |

**Keine Versionsanpassung an alten Tests:** Alle sechs bisherigen Suite-Dateien sind bytegleich zum Vorzustand; alle 117 alten IDs sind erhalten. Nachweis: [regression-scope.json](regression-scope.json). Die V7-Codevereinigung bleibt mit 654949 Byte unter ihrer unveraenderten Grenze von 655360 Byte.

Der erste V8-Durchgang hatte 17/18 bestandene Tests. Ein Test verwechselte die im Python-Traceback abgedruckte Supplierdefinition mit einem Supplieraufruf. Korrigiert wurde die Messung im neuen Test: strukturierte Ausgabe des zweiten Prozesses mit Supplierzaehler 0, geschlossenem Gate und erwarteter Ablehnung. Die anschliessenden fuenf fokussierten Tests bestanden; der obige Gesamtdurchgang prueft den Endstand. [Korrekturbeleg](development-correction.json).

## Codeumfang und Abschlussbilanzen

Gebundene Vereinigung: **44 Dateien, 699053 Byte; Grenze 720896 Byte; frei 21843 Byte**. Keine gebundene Testdatei ausgeschlossen. [Inventar mit Einzelhashes](final/dependency-inventory.json). Gegenueber dem V7-Ausgangsstand 654068 Byte sind 44985 Byte hinzugekommen. Der fruehere Grobansatz von maximal 14500 Zusatzbyte war somit zu niedrig; die genehmigte V8-Grenze wird dennoch eingehalten.

Das separate Berichtshilfsskript `measure_tests.py` misst und archiviert Entwicklungstests; es ist kein Bestandteil des gebundenen Laufpfads. Es umfasst 4523 Byte. Auch die zusaetzliche Kontrollsumme aus gebundenem Code und diesem Beobachter liegt mit 703576 Byte unter 720896 Byte. Archivkopien werden nicht als gleichzeitig aktive Laufdateien doppelt gezaehlt. Externe Laufzeitinstallationen sind separat im Inventar identifiziert; diese Quellbytebilanz ist kein Prozessspeicher- oder Gesamtdisknachweis.

Gemessene Einzelabschluesse; jede Gesamtsumme enthaelt C=699053 Byte sowie die angegebenen Nicht-Code-Posten. B bezeichnet statische Shared-Dateien; E/T/Tmin werden im Shared-Konto und in der Gesamtsumme genau einmal erfasst. Alle Werte sind Byte.

| Fall / Beleg | M | B | R | V | E | T | Tmin | Staging | Gesamt inkl. C |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Erfolg, 58/58](final/closures/011/measurement.json) | 26866 | 96872 | 184874 | 2433 | 0 | 1644 | 0 | 0 | 1011742 |
| [Abbruch Versuch 58, 57 Erfolge](final/closures/008/measurement.json) | 26866 | 96872 | 181124 | 385 | 1663 | 1663 | 0 | 0 | 1007626 |
| [Fehler zwischen Armen](final/closures/010/measurement.json) | 26866 | 96872 | 6450 | 382 | 1336 | 1336 | 0 | 0 | 832295 |
| [Konstruktorfehler](final/closures/002/measurement.json) | 26866 | 96872 | 0 | 0 | 877 | 877 | 0 | 0 | 824545 |
| [Konstruktorfehler nach erster Geschichte](final/closures/019/measurement.json) | 26866 | 96872 | 0 | 0 | 1035 | 1035 | 0 | 0 | 824861 |
| [Letzter Ownerfehler, Quelle vollstaendig](final/closures/013/measurement.json) | 26866 | 96872 | 185339 | 393 | 1659 | 1659 | 0 | 0 | 1011841 |
| [Codecfehler nach Quellenabbruch](final/closures/001/measurement.json) | 26866 | 96872 | 0 | 0 | 850 | 850 | 0 | 0 | 824491 |
| [Fehler nach Terminal-Rename](final/closures/018/measurement.json) | 26866 | 96872 | 184874 | 2433 | 1718 | 1644 | 1779 | 0 | 1015239 |
| [Partielles Schreiben, Cleanup blockiert](final/closures/020/measurement.json) | 26866 | 96872 | 0 | 0 | 0 | 0 | 0 | 73 | 822864 |

Alle **20 Abschlussmessungen** stehen in [closure-measurements.json](final/closure-measurements.json). Je Fall sind die tatsaechlichen Eingaben und Ergebnisbytes archiviert; der Code liegt einmalig unter `final/code/`. Nachrechnung: **329 unterschiedliche archivierte Dateien** erneut per Groesse/SHA256 geprueft, alle 20 Kategoriensummen und Gesamtsummen stimmen, alle Bilanzen innerhalb der Grenzen, alle beobachteten Owner und Gates geschlossen. [Archivpruefung](final/archive-verification.json). Reservierungen sind separat: [prestart-reservations.json](final/prestart-reservations.json).

Beim absichtlich blockierten Staging-Cleanup verbleiben 73 Byte; dauerhafter Fehler- und Terminalbeleg fehlen. Das Ergebnis meldet diesen Mangel und bleibt NOT_EVALUABLE. Ein Konstruktorfehler vor Rueckgabe des Verbindungsrecords liefert einen Fehlerabschluss mit beobachtetem Quellenpraefix und Ownerstatus, keinen erfundenen vollstaendigen Record.

## Realsperre und historische Erhaltung

[Separat gemessener Starterstopp](final/starter-stop.json): `V8_REAL_EXECUTION_DISABLED`; Supplier=0, Adapter=0, Laufeinstieg=0, oeffentliches Gate=false, neutrales Gate=false, Ausgabeordner nicht vorhanden. Auch nach vorgetaeuschter erfolgreicher Legacy-Zulassung stoppt der gebundene Test unbedingt vor Ausfuehrung.

598 Dateien des frueheren Publikationsarchivs wurden auf Groesse und SHA256 kontrolliert: keine Abweichung. V7-Ressourcenvertrag bytegleich. [Erhaltungsbeleg](historical-preservation.json). Keine reale Quelle erzeugt, kein realer Lauf gestartet, keine finale Hauptlaufbindung erstellt. Archivierte V8-Bindungen sind ausschliesslich temporaere neutrale Testfixtures.

## Verbleibende Grenzen und vorgeschlagener naechster Schritt

- Unabhaengige Abnahme und RAM-Nachweis bleiben offen. Die Null-PCM-Fixtures belegen technische Integration, keinen wissenschaftlichen Quellenvergleich oder Memoryvorteil.
- Einmaligkeit gilt fuer den besitzgebundenen Ausgabeordner ueber normale Prozessneustarts; manuelles Loeschen/Wiederherstellen dieser Ablage liegt ausserhalb des Vertrags. Keine manipulationssichere Autorisierungsdatenbank und keine Recoverygarantie bei Stromausfall.
- Der explizite Python-Supplier ist keine Sandbox fuer fremden Code. Der getestete neutrale Pfad akzeptiert nur die gebundenen Null-PCM-Bytes.
- Dateisystemfehler koennen dauerhafte Abschlussbelege verhindern. Diese Faelle bleiben sichtbar gesperrt; sie gelten nicht als erfolgreich publiziert.

**Vorschlag an den Projektleiter:** unabhaengige Abnahme dieses eingefrorenen V8-Endstands anhand der 138 Test-IDs, der 20 archivierten Abschluesse und der vollstaendigen Codehashbindung. Dabei besonders Receipt-Manipulation, 57/58-Praefix, Konstruktor-/Ownerfehler und erneuten Start pruefen. Danach den noch fehlenden RAM-Nachweis als getrenntes Paket festlegen. Der reale Starter bleibt bis zu einer gesonderten Entscheidung geschlossen.
