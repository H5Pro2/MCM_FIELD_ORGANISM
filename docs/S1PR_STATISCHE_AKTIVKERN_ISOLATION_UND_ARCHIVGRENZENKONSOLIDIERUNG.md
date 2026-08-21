# S1-PR: Statische Aktivkern-Isolation und Archivgrenzenkonsolidierung

## Status und Umfang

S1-PR konsolidiert ausschliesslich die technische Oberflaechen- und
Archivgrenze des Projekts. Es waehlt keine Kandidatenmechanik, veraendert
keine Gleichung, keinen Parameter, keine Runtime und keinen Importpfad. Es
wurden keine Tests, Feldlaeufe, Browser oder Sensoren gestartet und keine
Dateien geloescht.

Entscheidung:

```text
ACTIVE_NAMESPACE_CLEAN_PACKAGE_INITIALIZER_BROAD_STATIC_LAZY_SPLIT_CONTRACT_REQUIRED
```

## Gepruefte Quellen

Der Audit bindet den heutigen Stand aus:

- `mcm_field_organism/current_api.py`;
- `mcm_field_organism/__init__.py`;
- W2-A, W2-D und W2-J zur Paketoberflaeche und zum Importgraphen;
- S1-AZ und S1-BA zur Trennung aktiver Rollen und Referenzmanifeste;
- S1-BH bis S1-BJ zum maschinenlesbaren Feldvertrag und AV-Abschluss;
- S1-PP und S1-PQ zu den geschlossenen Kandidatenzweigen und der
  Forschungspause.

## Verbindliche Klassifikationsregel

Jeder direkt angebotene Projektbestand wird mit folgender Vorrangfolge genau
einer operativen Rolle zugeordnet:

1. **`ACTIVE_FIELD_CORE`:** Namen in
   `current_api.CURRENT_CONTROLLED_FIELD_EXPORTS`.
2. **`REFERENCE_BASELINE`:** Namen in
   `PASSIVE_COMPARISON_EXPORTS`, `CI_REFERENCE_EXPORTS`,
   `F3_REFERENCE_EXPORTS` oder `S1B_REFERENCE_EXPORTS`.
3. **`CLOSED_CANDIDATE`:** nur ueber die breite Root-Oberflaeche oder direkte
   Modulimporte erreichbare Artefakte beendeter Kandidatenfamilien,
   insbesondere E1, DTS-1/T1, G2/D3, KFS-1, lokale historische
   Traeger-, Material- und Substratfamilien.
4. **`INACTIVE_SENSOR`:** Live-Audio-, Live-Video-, Kamera-, Mikrofon- und
   physische Effektorpfade ausserhalb der kontrollierten Testwelt.
5. **`HISTORICAL_RUNNER`:** alle uebrigen nur ueber Root-Kompatibilitaet,
   direkte Modulimporte oder `tools/` erreichbaren Runner, Einmallaufpfade,
   Audits, Preflights und historische Hilfsoberflaechen.

Die Reihenfolge ist fail-closed: Ein Name, der im aktiven Manifest steht,
bleibt aktiver Kern, auch wenn ein kompatibler Root-Reexport existiert. Ein
Name in einem Referenzmanifest ist niemals zugleich aktiver Kern. Alles, was
nur in der breiten Root-Oberflaeche verbleibt und keiner engeren Klasse
zugeordnet ist, faellt in `HISTORICAL_RUNNER` und erhaelt dadurch keine
aktive Rolle.

## Bestandsaudit

### ACTIVE_FIELD_CORE

Der maschinenlesbare Vertrag `mcm.active_av_field_state.v1` bindet 129
aktive Rollen. Sie bilden den kontrollierten Pfad aus AV-Quellen,
Rezeptorreduktion, technischer Zeitordnung, Handoff, transienten Docks,
gemeinsamem neutralem S/H-Feld, Sitzungen sowie Snapshot und Restore.

Der statische W2-J-Importgraphaudit fand hinter diesem Kern keine
historischen, pausierten, privaten oder Live-/physisch inaktiven Module. Vier
sichtbare Referenzabhaengigkeiten dienen nur gemeinsamen Validierungsrollen
und optionalen Snapshotfeldern; sie aktivieren keine Referenzmechanik.

### REFERENCE_BASELINE

`current_api.__all__` enthaelt neben den 129 Kernrollen vier explizit
getrennte Referenzmanifeste mit zusammen 57 Rollen:

| Manifest | Rollen | Einordnung |
|---|---:|---|
| `PASSIVE_COMPARISON_EXPORTS` | 4 | passive technische Vergleiche |
| `CI_REFERENCE_EXPORTS` | 8 | abgeschlossene C_i-Referenz |
| `F3_REFERENCE_EXPORTS` | 17 | F3- und lineare Referenzpfade |
| `S1B_REFERENCE_EXPORTS` | 28 | opt-in S1-B- und W7B-Referenzpfade |

Damit besitzt `current_api` insgesamt 186 eindeutige Exporte. Die
Referenzrollen bleiben importierbar, sind aber nicht Teil des aktiven
Feldkerns.

### CLOSED_CANDIDATE

Geschlossene Kandidatenartefakte bleiben im Paket als Quell-, Schema-,
Validator-, Comparator- und Reproduzierbarkeitsbestand erhalten. Dazu
gehoeren insbesondere die umfangreichen `e1_*`- und
`dynamic_substrate_*`-Familien sowie die abgeschlossenen lokalen
Traegerfamilien. S1-PP bindet G2/D3 ausschliesslich als Infrastruktur und
Baselinebestand.

Keiner dieser Namen steht im aktiven Kernmanifest. Direkter Modulimport oder
Root-Kompatibilitaet reaktiviert keinen Zweig.

### INACTIVE_SENSOR

`live_audio_adapter`, `live_video_adapter`, `live_audio_video_field` und
physische Praesentations- oder Effektorpfade bleiben ausserhalb von
`current_api`. Kontrollierte Browserpayloads sind davon getrennt und gehoeren
zur digitalen Testwelt des aktiven Kerns.

### HISTORICAL_RUNNER

Z4-, Einmallauf-, Matrix-, Preflight-, Audit- und zahlreiche weitere
Forschungsrunner bleiben fuer Nachvollziehbarkeit erhalten. Ebenso bleiben
`tools/` und Tests technische Entwicklungsartefakte. Sie sind kein Teil der
aktiven Laufzeitoberflaeche.

## Verbleibende Isolationsluecke

Die Namens- und Vertragsgrenze von `current_api` ist sauber. Die physische
Paketinitialisierung ist jedoch weiterhin breit:

```text
import mcm_field_organism.current_api
-> Python initialisiert zuerst mcm_field_organism/__init__.py
-> __init__.py importiert aktive, historische, geschlossene und inaktive
   Moduloberflaechen fuer Root-Kompatibilitaet
-> danach wird current_api geladen
```

Damit gilt:

- kein geschlossener Name wird durch `current_api` exportiert;
- es ist kein automatischer Feldlauf oder Sensorstart festgestellt;
- dennoch ist der statische Lade- und Abhaengigkeitsumfang des Pakets
  groesser als der aktive Kern;
- W2-J belegt einen sauberen Untermodulgraphen, aber keine schlanke
  Ausfuehrung der Paketinitialisierung selbst.

Diese Luecke ist eine technische Import- und Kompatibilitaetsfrage. Sie ist
kein Feldfehler und keine Grundlage fuer eine neue Forschungsfunktion.

## Konsolidierte operative Grenze

Ab S1-PR gilt verbindlich:

```text
aktiver Entwicklungseinstieg:
    mcm_field_organism.current_api

breite Kompatibilitaetsoberflaeche:
    mcm_field_organism.__init__

Archiv- und Direktimportbestand:
    geschlossene Kandidaten, historische Runner und inaktive Sensorik
```

Neue aktive Technik darf nur ueber ein ausdruecklich klassifiziertes
Manifest in `current_api` aufgenommen werden. Das blosse Vorhandensein oder
der Root-Reexport eines Namens reicht nicht. Bestehende Archivdateien werden
nicht geloescht und nicht in aktive Verzeichnisse verschoben.

## Abschluss

S1-PR schliesst die statische Rollen- und Archivkonsolidierung ab. Der aktive
Feldkern ist auf Namens-, Manifest- und Vertragsniveau isoliert. Offen bleibt
nur die breite Paketinitialisierung aus Kompatibilitaetsgruenden.

## Genau ein naechster Schritt

```text
S1-PS - statischer Vertrag fuer eine kompatible schlanke Paketinitialisierung
```

S1-PS soll noch keine Imports veraendern. Es soll zuerst binden:

- welche Root-Namen dauerhaft kompatibel bleiben muessen;
- welche Root-Namen spaeter lazy aufgeloest werden koennen;
- wie `current_api` ohne eager Laden geschlossener, historischer oder
  inaktiver Module erreichbar wird;
- welche Importidentitaeten und Fehlermodi erhalten bleiben muessen;
- welches statische und spaetere endliche Testgate eine Migration
  fail-closed absichert.

S1-PS bleibt technische Architekturpflege. Die pausierte
Substratforschung wird dadurch nicht wieder geoeffnet.
