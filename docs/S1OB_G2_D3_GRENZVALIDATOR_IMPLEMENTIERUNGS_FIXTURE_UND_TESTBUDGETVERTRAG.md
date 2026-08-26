# S1-OB G2/D3 Grenzvalidator-Implementierungs-, Fixture- und Testbudgetvertrag

## Status

S1-OB bindet ausschliesslich die spaetere isolierte Implementierung und
Abnahme des S1-OA-Grenzvalidators. Dateigrenzen, reine APIs, eine kanonische
Fixture-Fabrik, positive Digests, negative Mutationen und ein endliches
Testbudget werden vorab geschlossen. Der Schritt implementiert und fuehrt
nichts aus.

Entscheidung:

```text
G2_D3_TRANSIENT_BOUNDARY_VALIDATOR_IMPLEMENTATION_FIXTURES_AND_TEST_BUDGET_BOUND
```

## Gebundene Dateigrenze

S1-OC darf genau drei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/g2_d3_transient_boundary_validator.py` | reiner Grenzrecord- und Ereignisvalidator |
| `tests/g2_d3_s1oc_fixtures.py` | kanonische Grenzfixture-Fabrik und gebundene Mutationen |
| `tests/test_g2_d3_s1oc_transient_boundary_validator.py` | fokussierte technische Abnahme |

Alle bestehenden Dateien bleiben unveraendert. Insbesondere duerfen
D3-Validator, D3-Fixtures und O3-Operator weder erweitert noch repariert
werden.

## Erlaubte Produktionsabhaengigkeiten

Das neue Produktionsmodul darf nur importieren:

- Python-Standardbibliothek fuer unveraenderliche Datentypen und reines
  JSON-Lesen;
- `G2D3ValidationRegistry` und
  `validate_g2_d3_anatomy_record` aus dem akzeptierten D3-Validator;
- `canonical_json_bytes` und `sha256_hex` aus dem unveraenderten
  KFS-1-Validator.

Feld-, Transfer-, O3-, Runner-, Medien-, Netzwerk- oder Dateischreibmodule
sind unzulaessig.

## Reine oeffentliche API

Das Modul darf genau bereitstellen:

```text
build_g2_d3_transient_boundary_registry()
-> G2D3TransientBoundaryRegistry

validate_g2_d3_transient_boundary(
    boundary_raw_bytes,
    d3_raw_bytes,
    boundary_registry,
    d3_registry,
) -> G2D3TransientBoundaryValidationReceipt
```

Zusaetzlich sind nur unveraenderliche Registry- und Belegtypen sowie Schema-,
Ereignis- und Fehlercodekonstanten oeffentlich. Parsing, Kontaktdigest,
Grenzdigest und Klassifikation bleiben privat.

## Feste Fixtureidentitaet

Alle positiven Fixtures verwenden unveraendert:

```text
candidate_class_id
= G2_D3_TRANSIENT_LOCAL_CONTINUATION_GATED_REPARTITION

edge_id
= edge:carrier-a:carrier-b

field_reference_digest
= 8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835

source_d3_anatomy_record_digest
= 1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f

d3_raw_bytes
= unveraendertes D3_V_C0
```

## Kanonische Fixture-Fabrik

Die testseitige Fabrik erhaelt nur:

```text
current_orientation in {X,Y}
current_interval_ordinal >= 0
prior_orientation in {X,Y} oder None
```

Sie setzt Kante, Feldreferenz, Klasse und D3-Quelldigest auf die feste
Fixtureidentitaet. Bei `prior_orientation=None` muessen aktuelles Ordinal null
und alle Vorgaengerfelder `null` sein. Andernfalls setzt sie das
Vorgaengerordinal exakt auf `current_interval_ordinal-1` und beide
Abschlussfelder auf `true`.

Kontaktpayloads werden exakt nach S1-OA kanonisch digestiert, danach der
vollstaendige Grenzrecord ohne `boundary_record_digest`, zuletzt die
vollstaendigen Eingabebytes. Die Fabrik enthaelt keine Ereignistabelle und
keinen erwarteten Validatorstatus.

## Sechs positive Tabellenfixtures

| Fixture | Vorgaenger | Aktuell | Prior-Digest | Current-Digest | Boundary-Digest | Input-Digest | Ereignis |
|---|---|---|---|---|---|---|---|
| `OA_V_FIRST_X` | none | X/0 | `null` | `a05eb5a15b939ab088ed4d82d866ee120168c11e27e99cb9ea665ccf8e4c1d18` | `078d6250bee7a51093bde34f00d4faa33ad329f0c21fd103475d168907710027` | `bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228` | `NO_PREDECESSOR` |
| `OA_V_FIRST_Y` | none | Y/0 | `null` | `42d573a7d8340a1496fec9da3fc7bcd9f73c358083eb39cac6be02a24999ae20` | `1f6cdf067d253d0f8fa300f7074ab4ea6bb5568d4b193e0b274a12b104f6f89c` | `3da5f86db0772fb339b25c6e916bf0a13dfde6f5e144a8e48cb7eea62cc43769` | `NO_PREDECESSOR` |
| `OA_V_XX` | X/0 | X/1 | `a05eb5a15b939ab088ed4d82d866ee120168c11e27e99cb9ea665ccf8e4c1d18` | `0df023f42e8be41504bbad49fc8c5d89b7d16e25a2904c773f0845a841ffea15` | `15502f7ba7dedc0046d67cbdd66f0de4cfb0b8023d871bda34060358a17c2716` | `c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c` | `LOCAL_CONTINUATION` |
| `OA_V_YY` | Y/0 | Y/1 | `42d573a7d8340a1496fec9da3fc7bcd9f73c358083eb39cac6be02a24999ae20` | `d270f4a888136e4a6dc182b15468c3e7dc4c0567b4bb92eee75818638088f356` | `59fb36e54c8c2214e51014009c67452249d030e846366a30dcf367c341be4326` | `2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b` | `LOCAL_CONTINUATION` |
| `OA_V_XY` | X/0 | Y/1 | `a05eb5a15b939ab088ed4d82d866ee120168c11e27e99cb9ea665ccf8e4c1d18` | `d270f4a888136e4a6dc182b15468c3e7dc4c0567b4bb92eee75818638088f356` | `90f2bd6a4fe9cd82d40d950dd1a7288b6b98e064905dfcacb1538e5947aa34f4` | `d9db45ac53bcbddda68555ff398e7ea0f8f45f33979e84a7208d07fca965d1d0` | `LOCAL_SWITCH` |
| `OA_V_YX` | Y/0 | X/1 | `42d573a7d8340a1496fec9da3fc7bcd9f73c358083eb39cac6be02a24999ae20` | `0df023f42e8be41504bbad49fc8c5d89b7d16e25a2904c773f0845a841ffea15` | `19be56470b54b8d074f423cb264fad33024cc17959a89cd7bb5f76f97efd3488` | `68a94dc17f18afb4418e0d79f54f9a148d2c4eb8d9ced0f7607f372d9c2ff63e` | `LOCAL_SWITCH` |

Alle Hexwerte sind kleingeschriebene SHA-256-Digests. Die durch die feste
Fabrik und diese Werte bestimmte kanonische Bytefolge darf nach der
Implementierung nicht angepasst werden.

## Drei gebundene Verlaufsmatrizen

Die Fabrik materialisiert fuer jedes Ordinal einen getrennten Grenzrecord.
Gebunden sind jeweils `boundary_record_digest / input_bytes_digest`:

### H0 `X,Y,X,Y`

```text
0 078d6250bee7a51093bde34f00d4faa33ad329f0c21fd103475d168907710027 / bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228
1 90f2bd6a4fe9cd82d40d950dd1a7288b6b98e064905dfcacb1538e5947aa34f4 / d9db45ac53bcbddda68555ff398e7ea0f8f45f33979e84a7208d07fca965d1d0
2 587271311881f7621bd7db9c393231c93a880303f6fd47dab217917550c7eaf9 / 4bcd1825e7ccd7fda01a345640e6959b9ecabab3ea5442cea6964adb21ae1817
3 6c1da794ec37b88f094fd927e1404f1635163d1f606d253b0603d442a5815263 / cc51ced1142f606d5bd9dd22c743f2bab51828569bb56e8855bd80e3c2654618
```

Erwartung: `NO_PREDECESSOR, LOCAL_SWITCH, LOCAL_SWITCH, LOCAL_SWITCH`.

### H1 `X,X,Y,Y`

```text
0 078d6250bee7a51093bde34f00d4faa33ad329f0c21fd103475d168907710027 / bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228
1 15502f7ba7dedc0046d67cbdd66f0de4cfb0b8023d871bda34060358a17c2716 / c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c
2 040d538164d7f9d405725cc72bda26c86738100534949a6f079e52f03caaa8ff / c438484e53ca01b1d2382a9a9ce57fee743bf41bd8270d62af7cf9bb5af372d9
3 3372d7e9b24bb6cf8a426b2fd08d8418fd2a407bd7eb8788b5b43b90a026118c / 0c0d53a9e47417ad2bca11707612c2977e5f7caced7a5127b496f4a4db1e2b25
```

Erwartung: `NO_PREDECESSOR, LOCAL_CONTINUATION, LOCAL_SWITCH, LOCAL_CONTINUATION`.

### H1M `Y,Y,X,X`

```text
0 1f6cdf067d253d0f8fa300f7074ab4ea6bb5568d4b193e0b274a12b104f6f89c / 3da5f86db0772fb339b25c6e916bf0a13dfde6f5e144a8e48cb7eea62cc43769
1 59fb36e54c8c2214e51014009c67452249d030e846366a30dcf367c341be4326 / 2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b
2 587271311881f7621bd7db9c393231c93a880303f6fd47dab217917550c7eaf9 / 4bcd1825e7ccd7fda01a345640e6959b9ecabab3ea5442cea6964adb21ae1817
3 e5c710170b305b52772188d0cfde78f9bf218315dd1d852094b3cdd8aa88a4bf / a7001cf3bc1044f3e2897e61d9b4973c9922f03758b5068974b059b593482335
```

Erwartung: `NO_PREDECESSOR, LOCAL_CONTINUATION, LOCAL_SWITCH, LOCAL_CONTINUATION`.

## Gebundene Fehlermutationen

Ausgangspunkt ist `OA_V_FIRST_X`, soweit nicht `OA_V_XX` genannt wird.
`reseal` bedeutet: Alle von der semantischen Mutation abhaengigen Kontakt-
und Grenzdigests werden nach der bereits gebundenen kanonischen Regel neu
berechnet. Dies geschieht vor der Validatorimplementierung und verhindert
blosse abgeleitete Digestfehler.

| ID | Mutation | Digestpolitik | Input-Digest | Exakter Fehlercode |
|---|---|---|---|---|
| `OA_I_VERSION` | Version `s1oa.v2` | reseal | `2ef258e62980c27b31f36d271615d2e8c8323aa12e5f4e0d5f0c7254b7d99493` | `OA_UNKNOWN_SCHEMA_OR_VERSION` |
| `OA_I_MISSING` | `candidate_class_id` entfernen | reseal | `47c94ff9586fb10e25a4466d02a181405dd10d1d8a6ee608838fbd3ec9114574` | `OA_MISSING_OR_UNKNOWN_FIELD` |
| `OA_I_EXTRA` | `unknown_field=true` | reseal | `a59245f6ee3f0f296e0dcecfda791c7e4521c6ab216bd43af20f004f12666cb1` | `OA_MISSING_OR_UNKNOWN_FIELD` |
| `OA_I_NONCANONICAL` | eingerueckte Serialisierung | Digests unveraendert | `cc21ccf5b5f1c4250b490924a538e7007b846596e98fd39aa9309be2cf48d0f4` | `OA_NONCANONICAL_SERIALIZATION` |
| `OA_I_CLASS` | Klasse `OTHER` | reseal | `c2e7c0d1058ed6e1cf67bf6a314dc358153a1c84c78ccf6c1c399220b434606c` | `OA_CLASS_ID_MISMATCH` |
| `OA_I_FORBIDDEN` | `raw_data=[]` | reseal | `9cf428b696690525e95c1a9d1b8c2e989c820f110f1eb0faa5839984164a7efb` | `OA_FORBIDDEN_PAYLOAD_PRESENT` |
| `OA_I_CURRENT_DIGEST` | Current-Digest 64 Nullzeichen | nur Grenzrecord reseal | `a07443aae5a5c699367aa620ccd7238104fe28bd42b85c060a623d171aea515b` | `OA_CURRENT_CONTACT_DIGEST_MISMATCH` |
| `OA_I_PRIOR_NULLABILITY` | nur `prior_orientation=X` setzen | Grenzrecord reseal | `a10b5e6270756db626a7510125b4170eaa3f38289ebe8be8f0a4c25de24fed7d` | `OA_PRIOR_NULLABILITY_MISMATCH` |
| `OA_I_PRIOR_DIGEST` | in `OA_V_XX` Prior-Digest 64 Nullzeichen | nur Grenzrecord reseal | `4f5cb94a3f9367773811bfb11e822784c2ca81c0cb8314ac2e06fbbcf0c1a570` | `OA_PRIOR_CONTACT_DIGEST_MISMATCH` |
| `OA_I_D3_SOURCE_INVALID` | gueltige First-X-Grenze plus `D3_I_RECORD_DIGEST` | keine Grenzaenderung | Grenze `bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228`, D3 `1e101961c98475ef1015c85f5eb68de4ef101b977b5db435294a6e822c931a9f` | `OA_D3_SOURCE_RECORD_INVALID` |
| `OA_I_D3_SOURCE_DIGEST` | D3-Quelldigest 64 Nullzeichen | reseal | `6c67dae202f90f05d55dae04b35db15d955d770d547738c37fca1f727e09e335` | `OA_D3_SOURCE_DIGEST_MISMATCH` |
| `OA_I_EDGE` | in `OA_V_XX` Prior-Kante `edge:wrong` | Prior und Grenze reseal | `98c33e6184bb992bd33a2ebef9725a7d745384e65379a037ab5d83732bed81ca` | `OA_EDGE_OR_FIELD_REFERENCE_MISMATCH` |
| `OA_I_ORDINAL` | in `OA_V_XX` Current-Ordinal `2` bei Prior `0` | Current und Grenze reseal | `8f28c49597cf1b09b1a7fd8e419577b9ee04f06a5eb1b4bee700b824e51d93fc` | `OA_INVALID_INTERVAL_ORDINAL` |
| `OA_I_CLOSED` | in `OA_V_XX` Prior-Abschluss `false` | Prior und Grenze reseal | `4421a6cb76c62ba3e6aa3cd888f5ae854a9c5b40254c0c8d469c13b9aac24fa2` | `OA_INTERVAL_NOT_CLOSED` |
| `OA_I_ORIENTATION` | in `OA_V_XX` Current-Orientierung `Z` | Current und Grenze reseal | `895a0b39c83c05b4df3a1383d67e68a05b4bb3510da98fdbba93038f908fdae0` | `OA_UNKNOWN_ORIENTATION` |
| `OA_I_BOUNDARY_DIGEST` | Grenzdigest 64 Nullzeichen | nicht reseal | `b80e5aea4a795ece90c7f7c0589820479114425335472273b76e95eabfef1a0a` | `OA_BOUNDARY_RECORD_DIGEST_MISMATCH` |
| `OA_I_TRANSIENT` | `event_role=LOCAL_CONTINUATION` | reseal | `7a6b422e93f1096f03c2c81b6ee4d07e6dcc574e4dedcb748e77fc925cdbbc85` | `OA_TRANSIENT_PERSISTENCE_FIELD_PRESENT` |

Jede Mutation liefert genau den gebundenen Code. Abhaengige Pruefungen werden
bei fehlender Voraussetzung gesperrt. Weder Fixtures noch Erwartungen duerfen
nach einem Testresultat angepasst werden.

## Fokussierte Testmatrix

| Test-ID | Abnahme |
|---|---|
| `T01` | sechs positive Tabellenfixtures sind byte- und digeststabil |
| `T02` | alle sechs Tabellenfaelle liefern exakt ihre Ereignisrolle |
| `T03` | H0 liefert exakt erster Kontakt plus drei Switches |
| `T04` | H1 und H1M liefern gespiegelt exakt dieselbe Ereignisrollenfolge |
| `T05` | alle 17 Fehlermutationen liefern exakt ihre sicheren Codes |
| `T06` | ungueltige D3-Quelle sperrt jede Ereignisklassifikation |
| `T07` | Kontakt-, Grenz-, D3-, Eingabe-, Vertrags- und Belegdigests bleiben getrennt |
| `T08` | gleiche Bytes und Registries liefern bitgleiche Belege |
| `T09` | Eingabebytes und beide Registries bleiben unveraendert |
| `T10` | falsche API-Typen oder Registries scheitern vor einem Teilbeleg |
| `T11` | Beleg ist passiv und keine API akzeptiert ihn als Folgeeingabe |
| `T12` | Moduloberflaeche erreicht keinen Feld-, Transfer-, O3-, Runner-, I/O-, Medien- oder Netzwerkpfad |

Die Tests verwenden ausschliesslich `unittest` aus der Standardbibliothek.

## Endliches S1-OC-Ausfuehrungsbudget

S1-OC darf genau einmal ausfuehren:

```text
python -m unittest tests.test_g2_d3_s1oc_transient_boundary_validator
```

Innerhalb der Abnahme gelten maximal:

```text
validate_g2_d3_transient_boundary: 48 Aufrufe
validate_g2_d3_anatomy_record:     48 interne Aufrufe
validate_g2_d3_f1_pair:             0 Aufrufe
O3-Auswertungen:                     0
MCM-Feldschritte:                    0
Transfer- oder Umordnungsbuchungen:  0
Runner-/Medien-/Netzwerkaufrufe:     0
Dateischreibzugriffe:                 0
read-only Quelltextzugriffe:     maximal 2
```

Bei einem Fehler werden Vertrag und Implementierung getrennt geprueft. Kein
Fixture, Digest oder erwarteter Fehlercode wird passend gemacht, und der Lauf
wird innerhalb S1-OC nicht wiederholt.

## Aussagegrenze

S1-OB bindet nur eine spaetere Validatorimplementierung. Es gibt noch keinen
Grenzvalidatorbefund, kein klassifiziertes Ereignis, keine Umordnung,
Bildungsgleichung oder Feldwirkung, keine Lernfunktion und keinen Befund zur
hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OC darf ausschliesslich die drei gebundenen Dateien implementieren, den
fokussierten Test genau einmal innerhalb des Budgets ausfuehren und den Befund
dokumentieren. Alle bestehenden Dateien sowie alle Umordnungs-, Feld- und
Runtimepfade bleiben unveraendert.
