# K2/F3 Scheibe A: API- und Schema-2-Vertrag

Stand: 2026-08-06

Status:

- Scheibe A implementiert;
- technische Vertrags- und Regressionstests bestanden;
- aktive F3-Kopplung weiterhin gesperrt;
- kein AV-Forschungslauf;
- kein Memory-, Organisations-, Topologie-, Semantik- oder KI-Nachweis.

## 1. Implementierter Umfang

Scheibe A fuegt dem bestehenden gemeinsamen Feld eine optionale,
unveraenderliche M-Substratkomponente hinzu. Sie implementiert noch keinen
M-Transport und keine S-Rueckwirkung.

Implementiert sind:

1. fester F3-Armvertrag;
2. nichtnegative, kanonisch nach `neuron_id` geordnete M-Massen;
3. kanonischer Digest der vorhandenen symmetrischen Feldkanten;
4. gleichfoermige M-Initialreferenz mit Gesamtmasse 1;
5. Snapshot-Schema 2;
6. ausdrueckliche Migration von Schema 1 nach Schema 2;
7. vollstaendiger historischer S/H-Projektionsdigest;
8. unveraenderte P0-Fortsetzung fuer synchrone und asynchrone Feldpfade;
9. harte Sperre gegen aktive Kopplung im allgemeinen Scheibe-A-Advancepfad.

## 2. Zustands-API

Modul:

```text
mcm_field_organism/mcm_substrate_state.py
```

Oeffentliche Vertraege:

```text
MCMSubstrateArmContract
MCMSubstrateMass
MCMSubstrateState
MCMSubstrateStateError
build_uniform_mcm_substrate
mcm_substrate_edge_inventory
mcm_substrate_edge_inventory_digest
mcm_substrate_state_public_roles
```

Der Armvertrag enthaelt ausschliesslich:

```text
arm_id
lambda_sm_per_second
kappa
eta
initial_total_mass
```

Fuer den ersten Korridor gilt:

```text
lambda_sm_per_second >= 0
-0.5 <= kappa <= 0.5
eta >= 0
initial_total_mass == 1
```

Parameter sind endlich, boolesche Werte sind unzulaessig. Der Armvertrag ist
unveraenderlich und besitzt keine zustandsabhaengige Umschaltung.

## 3. Eigentumsgrenze

`SharedMCMField` besitzt jetzt optional:

```text
substrate: MCMSubstrateState | None
```

M wurde nicht aufgenommen in:

- `MCMNeuron`;
- `MCMNeuronOutput`;
- `MCMFieldPerception`;
- `MCMFieldSample`;
- Rezeptorframes;
- Observer oder Sessionhistorien.

Jeder M-Wert ist ueber `neuron_id` genau einem vorhandenen Feldort
zugeordnet. Der Substratzustand muss dieselbe vollstaendige Neuronenmenge und
dieselbe bestehende Kantenidentitaet wie das Feld besitzen.

## 4. Kanteninventar

Das Inventar wird ausschliesslich aus `MCMNeuronLayer.sample_offsets`, den
vorhandenen Feldpositionen und den vorhandenen periodischen Achsen gebildet.

Verlangt werden:

- mindestens eine Kante;
- keine Selbstkante;
- symmetrische Nachbarschaft;
- jede ungerichtete Kante genau einmal;
- ein zusammenhaengender Graph im ersten Korridor;
- kanonische Sortierung und SHA-256-Digest.

Es werden keine Kanten gelernt, gewichtet oder semantisch klassifiziert.

## 5. Snapshot-Schema 1

Schema 1 bleibt unveraendert und enthaelt exakt:

```text
schema_version
layer
docks
last_distribution
```

Ein Feld ohne Substrat erzeugt weiterhin Schema 1. Seine kanonische
Serialisierung und sein Digest verwenden denselben bisherigen Codepfad.
Schema 1 darf kein `substrate`-Feld enthalten.

## 6. Snapshot-Schema 2

Schema 2 enthaelt zusaetzlich:

```text
substrate:
  arm
  masses
  edge_inventory_digest
```

Schema 2 ist nur gueltig, wenn der komplette M-Zustand vorhanden ist. Der
Parser lehnt fehlende, unbekannte, doppelte, negative, nichtendliche oder zur
Gesamtmasse beziehungsweise Feldgeometrie unpassende Daten ab.

Restore serialisiert und parst eine unabhaengige Kopie. Danach muessen der
vollstaendige Schema-2-Digest, S/H/M, Armvertrag, Kantenidentitaet und letzte
Zeitgrenze identisch sein.

## 7. Explizite Migration

Oeffentliche Funktion:

```text
migrate_shared_mcm_field_snapshot_to_schema2(snapshot, arm)
```

Die Migration akzeptiert nur:

- einen validierten Schema-1-Snapshot;
- einen ausdruecklich uebergebenen P0-Nullarm;
- die gleichfoermige Initialreferenz `M_i = 1/N`.

Es gibt keine automatische Migration beim Lesen oder Wiederaufnehmen. Eine
zweite Migration und eine Migration mit aktivem Arm werden abgelehnt.

## 8. P0-Projektionsvertrag

Ein Schema-2-Snapshot bietet:

```text
fast_state_projection_payload()
fast_state_projection_digest()
```

Die Projektion entfernt ausschliesslich den neuen Substratzustand und setzt
die Schemaidentitaet auf 1. Sie behaelt Layer, S, H, Wahrnehmung, Docks,
Verteilung und Zeitgrenze vollstaendig bei.

Bei P0 gilt:

```text
lambda_sm_per_second == 0
M bleibt unveraendert
der vorhandene S/H-Advancepfad wird direkt verwendet
```

Der P0-Pfad wurde nicht durch einen neuen Integrator nachgebildet.

## 9. Aktive Sperre

`attach_uniform_mcm_substrate(field, arm)` akzeptiert in Scheibe A nur einen
Nullarm. Ein manuell geladener Schema-2-Zustand mit aktivem Arm kann zwar als
vollstaendiger technischer Zustand validiert werden, aber `SharedMCMField.advance`
bricht vor jeder Fortentwicklung mit einer Scheibe-A-Sperre ab.

Damit existiert noch kein halb implementierter aktiver Organismuspfad.

## 10. Technische Pruefung

Am 2026-08-06 wurden ausschliesslich technische Tests ausgefuehrt:

```text
erste Scheibe-A-Suite:
38 Tests bestanden
9 Untertests bestanden

angrenzende Feldregression:
60 Tests bestanden
14 Untertests bestanden
```

Geprueft wurden unter anderem:

- Substratvalidierung und Kanteninventar;
- Schema-1-Roundtrip und Digestvertrag;
- Schema-2-Migration, Roundtrip und Restore;
- unbekannte und ungueltige Substratdaten;
- synchrone P0-Projektionsgleichheit;
- asynchrone P0-Projektionsgleichheit;
- Session-Restore und Fortsetzung;
- bisheriger Exaktintegrator, Fast-Afterimage und Resume;
- oeffentliche API- und transiente Feldgrenzen.

Pytest meldete nur, dass der bereits vorhandene `.pytest_cache`-Pfad nicht
neu angelegt werden konnte. Alle ausgewaehlten Tests selbst bestanden.

Diese Tests sind Softwareverifikation und keine Laufnummer oder
Forschungsevidenz fuer MCM-Memory.

## 11. Nicht implementiert

Weiterhin nicht vorhanden sind:

- F3-Kantenraten q;
- C- und R-Berechnung;
- M-Transport;
- aktive S-Rueckwirkung;
- SSPRK(3,3);
- AV-Kausallauf;
- Praegung, Verdichtung, Loesung oder Vergessen;
- Memory, Organisation, Topologie, Semantik oder KI.

## 12. Ergebnis und naechste Grenze

Scheibe A stellt jetzt eine vollstaendige, rueckwaertskompatible und
serialisierbare technische M-Zustandsgrenze bereit. Sie veraendert den
bisherigen P0-S/H-Pfad nicht und eroeffnet keinen allgemeinen M-Leser.

Der naechste zulaessige Implementierungsschritt ist Scheibe B: eine reine,
weltfreie und zustandslose F3-C/R-Funktion mit algebraischen Invariantentests.
Sie darf noch keinen Integrator und keinen AV-Lauf enthalten.
