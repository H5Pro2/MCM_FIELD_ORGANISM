# S1-PT: Statischer Root-Exportinventar- und Eindeutigkeitsaudit

## Status und Umfang

S1-PT wertet `mcm_field_organism/__init__.py` und
`mcm_field_organism/current_api.py` ausschliesslich mit dem Python-AST aus.
Kein Projektmodul wurde importiert. Die Root-Datei, die Runtime und alle
Feldfunktionen bleiben unveraendert. Es wurden keine Tests, Browser,
Sensoren oder Feldlaeufe gestartet und keine Dateien geloescht.

Entscheidung:

```text
ROOT_EXPORT_INVENTORY_COMPLETE_UNAMBIGUOUS_DIGEST_BOUND_LAZY_IMPLEMENTATION_NOT_YET_AUTHORIZED
```

## Auditwerkzeug und Artefakt

Der reproduzierbare statische Builder liegt in:

```text
tools/build_s1pt_root_export_inventory.py
```

Er verwendet nur Standardbibliothek und liest Projektdateien als Syntax. Er
schreibt das kanonische Inventar nach:

```text
docs/S1PT_ROOT_EXPORT_INVENTORY_V1.json
```

Das Artefakt enthaelt fuer jeden Root-Namen:

```text
export_name
source_module
source_attribute
surface_class
```

Zusaetzlich enthaelt es die heutige geordnete `__all__`-Liste, die
Klassifikationsgrundlagen, Zaehler und drei getrennte Digests.

## Fail-Closed-Eindeutigkeitsgate

Der Builder bricht ohne Artefaktabnahme ab, wenn:

- `__all__` nicht statisch als Liste auswertbar ist;
- ein Name mehrfach in `__all__` vorkommt;
- ein exportierter Name keinen relativen Importursprung besitzt;
- ein Root-Import nicht in `__all__` gebunden ist;
- ein Name aus mehreren verschiedenen Urspruengen importiert wird;
- ein `current_api`-Manifest nicht statisch oder nicht eindeutig ist.

Der heutige Bestand erfuellt alle Gates:

| Pruefung | Ergebnis |
|---|---:|
| Root-Namen in `__all__` | 1.267 |
| eindeutige Root-Namen | 1.267 |
| statisch gebundene Importnamen | 1.267 |
| Namen ohne Ursprung | 0 |
| importiert, aber nicht exportiert | 0 |
| Mehrdeutigkeiten | 0 |
| `__all__`-Dubletten | 0 |
| Ursprungsmodule | 156 |

Damit ist die heutige Root-Oberflaeche vollstaendig und eindeutig in eine
spaetere statische Lazy-Abbildung ueberfuehrbar. Dies ist noch keine
Freigabe, `__init__.py` zu veraendern.

## Operative Klassifikation

Die 1.267 Root-Namen verteilen sich nach der S1-PR-Vorrangregel:

| Klasse | Root-Namen | Bedeutung |
|---|---:|---|
| `ACTIVE_FIELD_CORE` | 125 | aktive Kernrollen, die zugleich als Root-Reexport bestehen |
| `REFERENCE_BASELINE` | 18 | explizite Referenzrollen mit Root-Kompatibilitaet |
| `CLOSED_CANDIDATE` | 212 | beendete Kandidaten- und Substratartefakte |
| `INACTIVE_SENSOR` | 75 | Live-, physische Sensor- und Effektorrollen |
| `HISTORICAL_RUNNER` | 837 | uebrige historische Runner, Audits, Preflights und Werkzeuge |
| **Gesamt** | **1.267** | |

Die Zuordnung ist statisch und steuert keine Runtime. Namen aus aktiven oder
Referenzmanifesten werden ausschliesslich durch exakte Manifestmitgliedschaft
klassifiziert. Erst danach greifen die expliziten Modulgruppen fuer inaktive
Sensorik und geschlossene Kandidaten; alle uebrigen Root-Namen fallen
fail-closed in `HISTORICAL_RUNNER`.

## Abgleich mit current_api

`current_api` besitzt 129 aktive und 57 explizite Referenzrollen. Nicht alle
davon sind aus der historischen Root-API reexportiert:

| Bereich | in `current_api` | zugleich Root-Reexport | nur `current_api` |
|---|---:|---:|---:|
| aktiver Feldkern | 129 | 125 | 4 |
| Referenzmanifeste | 57 | 18 | 39 |

Die vier nur in `current_api` vorhandenen aktiven Namen sind:

```text
AudioFrameSource
VideoFrameSource
active_field_state_contract
active_field_state_contract_digest
```

Diese Asymmetrie ist beabsichtigt und kein Vollstaendigkeitsfehler der
Root-Oberflaeche. Die spaetere Lazy-Migration darf keine der 43 additiven
`current_api`-Rollen unkontrolliert zur Root-API hinzufuegen.

## Gebundene Digests

Die kanonische Kodierung verwendet UTF-8, sortierte JSON-Schluessel,
kompakte Separatoren und keine nichtendlichen Zahlen.

```text
root_source_sha256:
f69cc32fbe7a26a4db6355e87a8b09a6456a2d2839c5036415e0d54d395f39ab

root_all_sha256:
4fdf82f4fe480e3180a6447987684093e2336837a329b95ce33b3069beb62639

sorted_records_sha256:
d783c5a0d29782c2b8f10d93ba2d048cef4c83468900e1e553050f0d84196cc1
```

Die drei Rollen sind getrennt:

- `root_source_sha256` bindet die unveraenderten Bytes von `__init__.py`;
- `root_all_sha256` bindet Inhalt und Reihenfolge der `__all__`-Liste;
- `sorted_records_sha256` bindet die sortierte Name-Ursprung-Klasse-Menge.

Eine spaetere Migration darf den Quelldigest erwartungsgemaess veraendern,
muss aber `root_all_sha256` und die semantische Recordabbildung vor und nach
der Umstellung reproduzieren.

## Befund fuer die Lazy-Migration

S1-PT findet keinen statischen Blocker:

- alle Root-Namen sind explizit und vollstaendig;
- jeder Name besitzt genau einen Importursprung;
- es gibt keine Namensdublette und keine konkurrierenden Urspruenge;
- die S1-PR-Klassen decken die gesamte Root-Oberflaeche ab;
- der aktive Feldkern kann anhand exakter Manifestmitgliedschaft erkannt
  werden.

Das Risiko liegt nicht mehr in fehlender Inventarisierbarkeit, sondern in der
spaeteren Wahrung von Importidentitaet, Fehlerzeit, Sternimport und
Unterprozess-Isolation. Diese Punkte muessen vor jeder Codeaenderung endlich
gebunden werden.

## Projektgrenze

S1-PT ist ein technischer Architekturaudit. Er veraendert keine Feldfunktion
und oeffnet keinen geschlossenen Kandidatenzweig. Die Substrat- und technische
Memory-Funktionsforschung bleibt pausiert.

## Genau ein naechster Schritt

```text
S1-PU - statischer Implementierungs- und Abnahmevertrag fuer die Lazy-Root-Migration
```

S1-PU soll exakt binden:

- die spaeter zulaessigen Dateien und unveraenderten Dateien;
- die Uebernahme des S1-PT-Inventars in eine importierbare statische
  Abbildung;
- `__getattr__`, `__dir__`, Caching und Fehlerweitergabe;
- den Umgang mit Sternimport und direkten Root-Importen;
- frische Unterprozessarme fuer die Aktivkern-Isolationspruefung;
- ein endliches einmaliges Testbudget und klare Rueckfallbedingungen.

S1-PU implementiert noch nichts und fuehrt noch keine Tests aus.
