# S1-SX: Statischer Realpfad-, Ergebnisartefakt- und Einmalpublikationsvertrag des Baseline-Referenzatlas

## Status und Zweck

S1-SX bindet den spaeteren rein passiven Realpfad oberhalb des in S1-SW
synthetisch abgenommenen Comparators. Der Pfad darf das bereits publizierte
S1-SS-Artefakt nur lesen, rekonstruieren und genau einmal vergleichen.

S1-SX implementiert keinen Serializer oder Runner, definiert und startet
keinen Test, ruft keinen Comparator auf und erzeugt keine Laufdatei. Es
erfolgt keine numerische Auswertung.

## Pflichtkorrektur vor einem Reallauf

Der aktuelle Comparator berechnet die gebundenen Kontraste und
320-Komponenten-Paarresiduen. Sein In-Memory-Resultat traegt aber noch
nicht alle in S1-SU geforderten Herkunftsidentitaeten je Paar und keinen
vollstaendigen 14-Profil-Ausgabeblock.

S1-SY muss deshalb vor jeder Realfreigabe ergaenzen:

- 14 geordnete vollstaendige 320-Komponenten-S/H-Profile;
- Modellposition, Modellrolle, Konfigurationsdigest, Profildigest und die
  40 geordneten Quelldigests je Profil;
- linke und rechte Konfigurations-, Profil- und Quelldigestidentitaet in
  jedem der 91 Paarrecords;
- eine oeffentliche strenge Resultat- und Artefaktvalidierung.

Diese Ergaenzung veraendert keine Metrik und kein numerisches Ergebnis. Sie
schliesst nur die bereits gebundene Nachweisstruktur. Ohne diese Felder ist
der reale Pfad nicht publikationsfaehig.

## Feste Eingaben

Der spaetere Lauf darf ausschliesslich diese drei Projektdateien lesen:

```text
reports/s1ss_four_node_matrix_once_v1.json
  file_sha256 = 3fdf622a533f0974c93da26591d8d9edccb2fa4bb1fc272f19098015a8e7e066
  artifact_digest = 69a3c11613d2d83660a870dfdb288b98b23e7af9934463d7836ccd77340618bb
  matrix_result_digest = 1188e83b4ebfb8327e8fed22e85c8a17751f9b2eaf846632091ac01c1499dde5

reports/s1rk_four_node_fresh_manifest.json
  file_sha256 = 19cc753c110b64d1d48cabe46be190a01247995053da442dd4cefcd344ea8bfc

reports/s1sd_four_node_fresh_matrix_registration.json
  file_sha256 = dc5c42d2dab2b9d3f373e5601b3d170c4f081c46df5b3eb4e8f3a242454ab663
```

Das Fixture wird ausschliesslich kanonisch aus der Registrierung erzeugt.
Der Adapter muss Manifest, Registrierung, Fixture, historische
S1-SS-Quellinventarbindung, Matrixidentitaet, 238 Summarys und 560
Checkpointrecords erneut fail-closed pruefen.

## Ausfuehrungsidentitaet

```text
schema_id       = mcm.s1sx.baseline-reference-atlas-artifact.v1
source_contract = S1-SX
execution_id    = mcm.s1tb.baseline-reference-atlas.once.v1
canonicalizer   = compact-json-ascii-sort-keys-no-nan-sha256-v1
authorization   = S1-TB_REAL_BASELINE_REFERENCE_ATLAS_ONCE
contract_id     = mcm.s1su.baseline-reference-comparator.v1
contract_digest = 639cf70ab24892fb0e59e5baaba6c952b99b8ad16c498acf2a399841d44c5a50
```

Die Kennungen sind ausschliesslich technische Provenienz. Sie enthalten
keine erwartete Paarbeziehung und kein Modellurteil.

## Feste Laufpfade

```text
Ergebnis:
reports/s1tb_baseline_reference_atlas_once_v1.json

Versuchsnachweis:
reports/s1tb_baseline_reference_atlas_once_v1.attempt.json

Sperre:
reports/s1tb_baseline_reference_atlas_once_v1.lock

gleichverzeichnisige Ergebnisstufe:
reports/.s1tb_baseline_reference_atlas_once_v1.json.staging
```

Vorstart muessen alle vier Pfade fehlen. Reale Verzeichnisse, aufgeloeste
Projektgrenzen, exakte Schreibweise und fehlende Links sind Pflicht. Es
gibt keinen alternativen Ausgabe-, Resume-, Retry- oder Reparaturpfad.

## Getrenntes Comparator-Quellinventar

Das historische Quellinventar im S1-SS-Artefakt bleibt unveraendert und
wird gegen seine eigenen gebundenen Digests geprueft. Zusaetzlich muss der
spaetere Comparatorlauf seine tatsaechlich erreichbaren aktuellen
Produktionsbytes separat belegen.

Inventarwurzeln sind:

```text
mcm_field_organism/four_node_baseline_reference_single_run.py
mcm_field_organism/four_node_baseline_reference_artifact.py
mcm_field_organism/four_node_baseline_reference_input.py
mcm_field_organism/four_node_baseline_reference_comparator.py
```

Ausgehend davon wird per Python-AST die transitive lokale Importmenge samt
Paket-Bootstrap gebildet. Sortierte projektrelative POSIX-Pfade und
SHA-256-Dateidigest ergeben einen eigenen
`comparator_source_inventory_digest`. Dynamische oder unaufloesbare lokale
Imports, Links, Pfade ausserhalb des Projektroots und Quelldrift zwischen
Vor- und Nachpruefung stoppen ohne Ergebnisartefakt.

## Kanonisches Ergebnisartefakt

Das Rootobjekt enthaelt exakt:

```text
schema_id
source_contract_id
execution_id
canonicalization_id
authorization_digest
comparator_contract_identity
comparator_source_inventory
comparator_source_inventory_digest
input_file_digests
validated_input_identity
runtime_identity
baseline_reference_result
artifact_digest
```

`validated_input_identity` bindet Datei-, Artefakt-, Matrix-, Manifest-,
Registrierungs-, Fixture-, Achsen- und Comparatorinputdigests.

`baseline_reference_result` enthaelt bei Erfolg exakt:

```text
status = BASELINE_REFERENCE_ATLAS_COMPUTABLE
candidate_gate_status = S1PX_CANDIDATE_GATES_NOT_APPLICABLE
ordered_14_complete_profiles
ordered_322_contrasts
ordered_91_pair_comparisons
failure_codes = []
result_digest
```

Jedes Profil behaelt alle 320 signed Komponenten in kanonischer Ordnung.
Jeder Kontrast behaelt beide signed Vierervektoren. Jedes Paar behaelt das
vollstaendige signed 320-Komponenten-Residuum, `D_abs`, `scale`, `D_rel`,
Status und die beidseitigen Konfigurations-, Profil- und Quelldigests.

Es gibt keine Rundung, Filterung, Rangfolge, Gewinnerrolle,
Ergebniszusammenfassung oder Kandidatenprojektion im Artefakt.

## Fehlergrenze und Einmalschutz

Nach bestandenem Vorstart-Preflight werden Sperre und kanonischer
`STARTED`-Versuchsnachweis exklusiv und dauerhaft geschrieben, bevor der
einzige Comparatoraufruf beginnt. Bei jedem danach auftretenden Fehler
bleiben beide Belege bestehen; Ergebnis und Teilatlas fehlen.

Der Comparator darf intern `AUDIT_INVALID_NOT_COMPUTABLE` liefern. Dieser
Status ist kein publizierbares Ergebnisartefakt. Er stoppt den Runner mit
einem technischen Fehlercode. Es gibt keinen automatischen zweiten Aufruf.

Ein erfolgreiches Artefakt wird vollstaendig in Memory gebaut, kanonisch
serialisiert, im selben Verzeichnis exklusiv gestuft, geflusht, per
`fsync` bestaetigt, erneut streng geparst und nur per exklusivem
Same-Directory-Hardlink am fehlenden Ziel sichtbar gemacht. Erst danach
duerfen Versuchsnachweis und Sperre entfernt werden.

## Spaeterer Prozessweg und Budget

Nach Implementierung, synthetischer Abnahme und finalem statischem
Preflight ist nur dieser Prozessweg zulaessig:

```text
python -B -m mcm_field_organism.four_node_baseline_reference_single_run \
  --authorization S1-TB_REAL_BASELINE_REFERENCE_ATLAS_ONCE
```

Festes Budget:

```text
3 Eingabedateien
1 passive Adapterrekonstruktion
14 vollstaendige Profile
1 Comparatoraufruf
322 Rohkontraste
91 Profilpaare
0 Modellproducer
0 Feldschritte
0 Geraete- oder Netzwerkzugriffe
0 automatische Wiederholungen
```

Der Runner akzeptiert keine Rollen-, Paar-, Toleranz-, Pfad-, Filter-,
Ranking-, Parallel-, Retry- oder Kandidatenparameter.

## Implementierungsgrenze fuer S1-SY

S1-SY darf ausschliesslich bearbeiten oder neu anlegen:

```text
mcm_field_organism/four_node_baseline_reference_comparator.py
mcm_field_organism/four_node_baseline_reference_input.py
mcm_field_organism/four_node_baseline_reference_artifact.py
mcm_field_organism/four_node_baseline_reference_single_run.py
tests/test_four_node_baseline_reference_artifact_and_single_run.py
```

Es duerfen hoechstens 20 synthetische Tests definiert, aber noch nicht
ausgefuehrt werden. Sie muessen insbesondere Profil- und Paarprovenienz,
strikte Resultatdigests, kanonischen Roundtrip, Quellinventar,
Eingabedrift, Vorstartschutz, atomare Publikation, gestarteten Fehler ohne
Teilergebnis und genau einen synthetischen Comparatoraufruf pruefen.

Kein Test darf das reale S1-SS-Artefakt numerisch vergleichen oder einen
Modellproducer aufrufen.

## Entscheidung und naechster Schritt

```text
STATIC_BASELINE_REFERENCE_ATLAS_REAL_PATH_AND_ONE_SHOT_CONTRACT_BOUND
CURRENT_OUTPUT_PROVENANCE_GAP_BOUND_FOR_CORRECTION
NO_IMPLEMENTATION_NO_TEST_NO_COMPARATOR_NO_REAL_RESULT
```

Der einzige naechste Schritt ist S1-SY fuer die begrenzte Implementierung
und hoechstens 20 nur definierte synthetische Tests. Eine reale Auswertung
bleibt bis nach separater Testabnahme und finalem Preflight gesperrt.
