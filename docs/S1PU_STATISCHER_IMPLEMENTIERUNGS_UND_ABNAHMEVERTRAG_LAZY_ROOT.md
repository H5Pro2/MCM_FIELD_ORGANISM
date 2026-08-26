# S1-PU: Statischer Implementierungs- und Abnahmevertrag fuer Lazy Root

## Status und Umfang

S1-PU bindet ausschliesslich den spaeteren Implementierungsumfang und das
endliche Abnahmegate fuer die in S1-PS und S1-PT vorbereitete
Lazy-Root-Migration. Es veraendert keinen Importcode, keine Runtime und keine
Feldfunktion. Es wurden keine Tests, Projektimporte, Browser, Sensoren oder
Feldlaeufe gestartet und keine Dateien geloescht.

Entscheidung:

```text
LAZY_ROOT_IMPLEMENTATION_SCOPE_AND_FORTY_ONE_METHOD_ACCEPTANCE_BOUND_NO_IMPLEMENTATION
```

## Gebundene Grundlage

Die Implementierung darf nur auf dem S1-PT-Artefakt aufbauen:

```text
contract_id: mcm.s1pt.root_export_inventory.v1
root_exports: 1267
root_source_modules: 156
root_source_sha256:
f69cc32fbe7a26a4db6355e87a8b09a6456a2d2839c5036415e0d54d395f39ab
root_all_sha256:
4fdf82f4fe480e3180a6447987684093e2336837a329b95ce33b3069beb62639
sorted_records_sha256:
d783c5a0d29782c2b8f10d93ba2d048cef4c83468900e1e553050f0d84196cc1

current_api_source_sha256:
01daabe43dd52766014926f3ee30d55cd390d9d3ed6651a7bd3664997caa0360
current_api_transitive_modules: 57
current_api_local_import_edges: 253
current_api_modules_sha256:
26a6787cb3168074bf48a283dc247e653a8285fc2cba496a263227d50389946b
current_api_edges_sha256:
bcd270da8683c02819cf6db9560eda249c0bed42c3ec4a8b846b51c1b6e5d7f9
```

Vor jeder spaeteren Aenderung muessen diese Werte statisch erneut stimmen.
Eine Abweichung bedeutet `STOPP`; das Inventar darf nicht still neu erzeugt
werden, um eine unerwartete Root-Aenderung zu uebernehmen.

## Spaeter zulaessige Dateien

Ein einziger Implementierungsschritt darf ausschliesslich:

1. `mcm_field_organism/__init__.py` kompatibel auf Lazy-Aufloesung umstellen;
2. `mcm_field_organism/root_lazy_exports.py` als generierte statische
   Laufzeitabbildung neu anlegen;
3. `tools/build_s1pv_lazy_root_exports.py` als fail-closed Generator neu
   anlegen;
4. `tests/test_s1pv_lazy_root_manifest.py` mit exakt acht Testmethoden neu
   anlegen;
5. `tests/test_s1pv_lazy_root_subprocess.py` mit exakt fuenf Testmethoden neu
   anlegen;
6. das spaetere S1-PV-Abschlussdokument und die drei aktiven Statusseiten
   aktualisieren.

Alle anderen Python-Dateien bleiben unveraendert. Insbesondere gesperrt sind:

```text
mcm_field_organism/current_api.py
alle aktiven Feld-, Rezeptor-, Handoff-, Sitzungs- und Snapshotmodule
alle Referenzmodule
alle geschlossenen Kandidatenmodule
alle historischen Runner
alle inaktiven Sensor- und Effektorpfade
docs/S1PT_ROOT_EXPORT_INVENTORY_V1.json
tools/build_s1pt_root_export_inventory.py
```

## Generierte Laufzeitabbildung

`root_lazy_exports.py` muss vollstaendig aus dem unveraenderten S1-PT-
Inventar erzeugt werden. Handpflege einzelner Eintraege ist verboten.

Zulaessiger Inhalt:

```text
ROOT_ALL
ROOT_LAZY_EXPORTS
ROOT_SURFACE_CLASSES
CURRENT_API_ALLOWED_MODULES
S1PT_ROOT_ALL_SHA256
S1PT_SORTED_RECORDS_SHA256
CURRENT_API_SOURCE_SHA256
CURRENT_API_ALLOWED_MODULES_SHA256
CURRENT_API_IMPORT_EDGES_SHA256
```

Dabei gilt:

- `ROOT_ALL` reproduziert die 1.267 Namen in exakt heutiger Reihenfolge;
- `ROOT_LAZY_EXPORTS` bindet jeden Namen an genau ein relatives Modul und
  genau ein Attribut;
- `ROOT_SURFACE_CLASSES` bindet dieselben Namen an genau eine S1-PR-Klasse;
- `CURRENT_API_ALLOWED_MODULES` bindet die 57 statisch transitiv erreichten
  lokalen Module einschliesslich `current_api` selbst;
- keine Funktion des generierten Moduls importiert ein Ursprungsmodul;
- alle drei Namensmengen sind identisch und dublettenfrei;
- der Generator bricht bei jedem Digest-, Schema- oder Mengenfehler ab.

## Gebundene Root-Implementierung

Die spaetere `__init__.py` darf nur folgende operative Rollen enthalten:

1. den bestehenden fachlichen Modulkommentar;
2. Standardbibliotheksimport von `import_module`;
3. Import der statischen Rollen aus `root_lazy_exports`;
4. `__all__ = list(ROOT_ALL)`;
5. eine private unveraenderliche Name-zu-Ursprung-Abbildung;
6. `__getattr__`;
7. `__dir__`.

### `__getattr__`

Fuer einen registrierten Namen muss `__getattr__`:

```text
Name nachschlagen
-> genau das registrierte relative Modul mit import_module laden
-> genau das registrierte Attribut lesen
-> Objekt unter globals()[Name] cachen
-> dasselbe Objekt zurueckgeben
```

Fuer einen nicht registrierten Namen muss es ohne Modulsuche `AttributeError`
im ueblichen Modulformat ausloesen. Import- und Attributfehler eines
registrierten Ursprungs werden unveraendert weitergegeben. Platzhalter,
Fallbackmodule und Fehlerunterdrueckung sind verboten.

### `__dir__`

`__dir__` gibt die sortierte Vereinigung aus statischen Root-Namen und
bereits vorhandenen Modulglobals zurueck. Die Funktion darf kein
Ursprungsmodul laden.

### Identitaet und Caching

Nach erfolgreicher Aufloesung muss gelten:

```text
mcm_field_organism.Name
is
getattr(import_module("mcm_field_organism.<source_module>"), source_attribute)
```

Wiederholter Root-Zugriff darf keinen zweiten Aufloesungspfad erzeugen. Die
Standard-Importlocks und das anschliessende Root-Caching muessen dieselbe
Objektidentitaet auch bei wiederholtem Zugriff erhalten. Eine eigene
Nebenlaeufigkeits- oder Reloadmechanik ist nicht zulaessig.

## Import- und Fehlergrenzen

Nach `import mcm_field_organism` in einem frischen Prozess duerfen aus dem
Projekt nur das Paket selbst und die statische Lazy-Abbildung geladen sein.

Nach `import mcm_field_organism.current_api` duerfen nur:

- das Paket und die statische Lazy-Abbildung;
- `current_api`;
- seine direkten und transitiven aktiven oder expliziten
  Referenzabhaengigkeiten

geladen sein. Der spaetere Generator muss diese erlaubte lokale
Abhaengigkeitsmenge statisch aus dem `current_api`-Importgraphen binden und
gegen Quell-, Modul- und Kantendigest pruefen.
Module, die nur wegen der heutigen Root-Eagerimporte erscheinen, sind nicht
zulaessig.

Die einzige vorab erlaubte Fehlerzeitaenderung bleibt:

```text
Fehler eines nicht angeforderten historischen oder inaktiven Moduls
-> nicht mehr beim Paket- oder Aktivkernimport
-> erst beim ausdruecklichen Root-Zugriff oder direkten Modulimport
```

Fehlertyp und Fehlerinhalt des tatsaechlich angeforderten Ursprungs duerfen
nicht ersetzt werden.

## Neue Testmethoden

`test_s1pv_lazy_root_manifest.py` muss exakt acht Methoden enthalten:

1. generierte Abbildung stimmt mit allen S1-PT-Records ueberein;
2. `ROOT_ALL` stimmt in Inhalt und Reihenfolge mit dem gebundenen Digest;
3. alle drei generierten Namensmengen sind vollstaendig und eindeutig;
4. alle 1.267 Root-Namen liefern das identische Ursprungsobjekt;
5. ein unbekannter Name liefert `AttributeError` ohne Modulladen;
6. `dir()` ist vollstaendig und importfrei;
7. wiederholter Zugriff verwendet das gecachte identische Objekt;
8. die 43 additiven `current_api`-Namen werden nicht zur Root-API erweitert.

`test_s1pv_lazy_root_subprocess.py` muss exakt fuenf Methoden enthalten:

1. reiner Paketimport bleibt auf Paket und Lazy-Abbildung begrenzt;
2. `current_api`-Import entspricht exakt der statisch erlaubten lokalen
   Abhaengigkeitsmenge;
3. einzelner aktiver Root-Zugriff laedt seinen Ursprung und behaelt
   Identitaet;
4. ein geschlossener Root-Name bleibt bis zu seinem ausdruecklichen Zugriff
   ungeladen und behaelt danach Identitaet;
5. ausdruecklicher Sternimport reproduziert den vollstaendigen historischen
   Root-Namensbestand als getrennten Kompatibilitaetsarm.

Jeder Unterprozess startet mit einem frischen Interpreter und gibt nur
kanonisches JSON an den Testprozess zurueck. Ein bereits importierter
Elternprozess darf nicht als Isolationsbeleg dienen.

## Vorhandener Abnahmeverbund

Exakt diese acht vorhandenen Dateien werden einbezogen:

| Datei | Methoden |
|---|---:|
| `tests/test_current_api_manifest.py` | 5 |
| `tests/test_current_architecture_api.py` | 3 |
| `tests/test_active_engineering_surface_boundary.py` | 7 |
| `tests/test_architecture_contract_boundary.py` | 2 |
| `tests/test_audio_video_field_geometry_boundary.py` | 3 |
| `tests/test_receptor_proposal_handoff_boundary.py` | 2 |
| `tests/test_receptor_time_model_boundary.py` | 3 |
| `tests/test_current_api_end_to_end_consumer.py` | 3 |
| **Vorhanden gesamt** | **28** |

Mit den 13 neuen Methoden entsteht genau ein Verbund mit 41 Testmethoden.

## Endliches Ausfuehrungsbudget

Der spaetere S1-PV-Schritt darf nach statisch bestaetigten Ausgangsdigests
genau einen fokussierten 41-Methoden-Verbund starten.

Zulaessig sind:

```text
neue Lazy-Methoden:       13
vorhandene Grenzmethoden: 28
Gesamt:                   41
Testlaeufe:                1
```

Ein Syntax-, Import-, Test- oder Unterprozessfehler beendet den Lauf
fail-closed. Kein zweiter Lauf ist innerhalb derselben Freigabe erlaubt. Eine
Korrektur benoetigt einen neuen statischen Reparaturvertrag.

## Abnahmekriterien

S1-PV ist nur abgenommen, wenn gemeinsam gilt:

- der S1-PT-Ausgangsdigest war vor der Aenderung exakt;
- Quell-, Modul- und Kantendigest des `current_api`-Graphen waren vor der
  Aenderung exakt;
- nur die freigegebenen Dateien wurden veraendert;
- `root_all_sha256` bleibt exakt gleich;
- die semantische Recordabbildung bleibt exakt gleich;
- Root-Objektidentitaet besteht fuer alle 1.267 Namen;
- reiner Paketimport und Aktivkernimport bestehen ihre frischen
  Unterprozessgrenzen;
- der eine Verbund meldet exakt 41 erfolgreiche Testmethoden und keinen
  Fehler;
- keine Feldfunktion und kein Ergebnisartefakt wurde erzeugt.

Bei Nichterfuellung bleibt die Migration nicht abgenommen. Es gibt keine
Teilfreigabe.

## Projektgrenze

S1-PU ist technische Architekturpflege. Die geplante Migration veraendert
keine Feldmechanik und erzeugt keine neue Funktionsprognose. Geschlossene
Zweige und die Forschungspause bleiben unveraendert.

## Genau ein naechster Schritt

```text
S1-PV - einmalige Implementierung und 41-Methoden-Abnahme der Lazy-Root-Migration
```

S1-PV darf ausschliesslich den hier gebundenen Umfang implementieren und den
einen Testverbund ausfuehren. Weitere Bereinigung, Namensentfernung,
Archivverschiebung oder Forschungsarbeit ist nicht freigegeben.
