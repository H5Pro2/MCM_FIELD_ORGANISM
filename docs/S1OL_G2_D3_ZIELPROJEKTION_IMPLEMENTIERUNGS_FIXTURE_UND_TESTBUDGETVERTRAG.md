# S1-OL G2/D3 Zielprojektion: Implementierungs-, Fixture- und Testbudgetvertrag

## Status

S1-OL bindet ausschliesslich Dateigrenzen, kanonische Fixtures,
Fehlermutationen und ein endliches Einmaltestbudget fuer die spaetere reine
S1-OK-Projektionsstufe. Es wird keine Implementierung angelegt und kein Test
ausgefuehrt. Die atomare Commitseite bleibt getrennt gesperrt.

Entscheidung:

```text
G2_D3_PURE_TARGET_PROJECTION_IMPLEMENTATION_FIXTURES_AND_SINGLE_TEST_BUDGET_BOUND
```

## Gebundene Dateigrenze

S1-OM darf genau drei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/g2_d3_target_projection.py` | reine D3-Zielprojektion und gemeinsame statische Registry |
| `tests/g2_d3_s1om_fixtures.py` | kanonische Projektionsfixtures und gebundene Eingabefehler |
| `tests/test_g2_d3_s1om_target_projection.py` | fokussierte technische Abnahme |

Bestehende Produktions-, Fixture- und Testdateien bleiben unveraendert. Der
S1-OI-Betragsoperator, S1-OC-Grenzvalidator und D3-Validator duerfen nicht
erweitert oder repariert werden. Statusdokumente duerfen nach der einmaligen
Abnahme nur um deren tatsaechliches Ergebnis ergaenzt werden.

## Erlaubte Produktionsabhaengigkeiten

Das neue Produktionsmodul darf nur importieren:

- Python-Standardbibliothek fuer unveraenderliche Datentypen, exakte
  rationale Floatpruefung und reines JSON-Lesen;
- Registry, Receipt und reine Auswertung aus
  `g2_d3_halving_amount`;
- Registrytyp und reine Validierungsfunktion aus
  `g2_d3_schema_validator`;
- Registrytyp aus `g2_d3_transient_boundary_validator`;
- `canonical_json_bytes` und `sha256_hex` aus dem unveraenderten
  KFS-1-Validator.

Imports oder Aufrufe von Admissibility-, O3-, Feld-, Transfer-, Runner-,
Medien-, Browser-, Netzwerk- und Dateischreibpfaden sind unzulaessig.

## Gebundene oeffentliche Projektionsoberflaeche

S1-OM darf genau implementieren:

```text
build_g2_d3_target_commit_registry()
-> G2D3TargetCommitRegistry

project_g2_d3_conservative_target(
    boundary_raw_bytes,
    source_d3_raw_bytes,
    formation_enabled,
    target_commit_registry,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3TargetProjectionResult
```

Zusaetzlich sind nur die in S1-OK gebundenen unveraenderlichen Registry-,
Projektionsresultat- und Projektionsbelegtypen sowie zugehoerige Schema-,
Phasen-, Fehlercode- und Vertragsdigestkonstanten oeffentlich. Eine
Commitfunktion oder ein Commitresultat darf S1-OM noch nicht bereitstellen.

Die Projektionsfunktion akzeptiert keinen Betrag oder Beleg als Eingabe. Sie
muss S1-OI mit den originalen Grenz- und D3-Bytes im selben Aufruf verwenden.

## Feste Vertragswerte

```text
projection_receipt_schema
= g2_d3_target_projection_receipt/s1ok.v1

projector_contract_digest
= c761d3f5b2dc486ca6cb9389d305e9b2ec8d847812bac72e40d89995a66f6e2b

commit_contract_digest
= 4cae38e9c7986ff6099cfd8c2c742a2c11465bb61a9885441a403fab9b5859b5

accepted_amount_operator_contract_digest
= 396bd7b9fde4b7ee3b268e1d53245fd2a950cf4d8d9464f084d9b498c17de83b

accepted_boundary_validator_contract_digest
= 7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0

accepted_d3_validator_contract_digest
= b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c
```

Die gemeinsame Registry darf den Commit-Vertragsdigest bereits als statische
Identitaet tragen. Daraus entsteht keine Commit-API und keine Freigabe.

## Fixturegrenze

Die S1-OM-Fixturedatei darf die neun S1-OI-Kontrollen und fuenf
S1-OI-Fehlereingaben importieren. Sie darf deren Bytes, Schalter und Digests
nicht kopieren oder veraendern.

Zusaetzlich konstruiert sie genau:

- die erwarteten ersten positiven Zielbytes aus dem bereits gebundenen
  `D3_V_MIXED`;
- eine X/X-Grenze, deren D3-Quelle exakt `D3_V_MIXED` ist;
- die erwarteten zweiten positiven Zielbytes mit U/C `0.125/0.375`.

Alle Konstruktionen verwenden kanonisches JSON und berechnen nur
Ressourcenaccount-, Aggregatprojektions- und Anatomierecorddigest neu. Die
Fixturefabrik kennt weder Projektionsstatus noch Fehlercode noch Receiptwert.

## Zehn gueltige Kontrollen

Die ersten neun Inputs bleiben exakt die S1-OI-Kontrollen:

| Fixture | Erwarteter Status | Erwartete Zielbytes |
|---|---|---|
| `OL_V_FIRST_X_ON` | `NO_CHANGE` | originales `D3_V_C0`-Objekt |
| `OL_V_FIRST_Y_ON` | `NO_CHANGE` | originales `D3_V_C0`-Objekt |
| `OL_V_XX_ON` | `PROJECTED` | `D3_V_MIXED` |
| `OL_V_YY_ON` | `PROJECTED` | `D3_V_MIXED` |
| `OL_V_XY_ON` | `NO_CHANGE` | originales `D3_V_C0`-Objekt |
| `OL_V_YX_ON` | `NO_CHANGE` | originales `D3_V_C0`-Objekt |
| `OL_V_XX_OFF` | `NO_CHANGE` | originales `D3_V_C0`-Objekt |
| `OL_V_C1_XX_ON` | `NO_CHANGE` | originales `D3_V_C1`-Objekt |
| `OL_V_INTEGER_XY_ON` | `NO_CHANGE` | originales Integer-D3-Objekt |

Ihre Boundary- und D3-Inputdigests bleiben exakt die in S1-OH gebundenen
Werte. Fuer beide ersten positiven Kontrollen gilt:

```text
source D3 input digest
= d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7

target resource_account_digest
= 75bee4f5732ed8c57c942c0e495b910c54097ef72ed1fb457740a4dd7045cd1c

target aggregate_projection_digest
= bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e

target anatomy_record_digest
= d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c

target D3 input digest
= 2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8
```

X/X und Y/Y muessen genau dieselben Zielbytes erzeugen.

## Zehnte Kontrolle: zweite frische Fortsetzung

`OL_V_MIXED_XX_ON` verwendet `D3_V_MIXED` als vollstaendige neue Quelle und
eine daran neu gebundene X/X-Grenze. Es ist kein intern weitergereichter
Zwischenzustand eines vorherigen Projektionsaufrufs.

```text
source D3 input digest
= 2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8

boundary_record_digest
= 62003cc5144577d7c793051c01534348bc8be20e756bc1ab14d50199e17da79b

boundary input digest
= 5b1413f8041cb6d7c9552860affa75f2e74958b30b5bb00a6dfc2cc674f83087

expected amount = 0.125
expected status = PROJECTED
```

Die erwarteten Zielrollen und Digests sind:

```text
capacity = 1.0
free = 0.5
bound_unconfigured = 0.125
bound_configured = 0.375
blocked = 0.0

resource_account_digest
= 95568070519f29b65e34a4c06d681f150e81776b2bae4dfac60b132276df1f52

aggregate_projection_digest
= bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e

anatomy_record_digest
= efba6284b3e56cfe2041465eb8acc76b00de34ee8303f6a2caa20b2a3fc66681

target D3 input digest
= a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab
```

## Fuenf gebundene Fehlereingaben

Die folgenden Inputs werden byteidentisch aus S1-OI uebernommen:

```text
OG_I_SOURCE
OG_I_NUMERIC_DOMAIN
OG_I_HALVING_INVARIANT
OG_I_TARGET_REPRESENTATION
OG_I_EXACT_LEDGER
```

Jeder Fehler muss auf der Projektionsoberflaeche exakt liefern:

```text
evaluation_status = invalid
projection_status = not_computable
target_d3_raw_bytes = not_computable
failure_reasons = (OK_PROJECTION_AMOUNT_EVALUATION_FAILED,)
```

Die Projektion darf keine fachliche Zweitinterpretation der inneren
S1-OI-Fehlercodes vornehmen. Der Digest des tatsaechlichen S1-OI-Belegs wird
im Projektionsbeleg dokumentiert; der Beleg selbst wird nicht gespeichert
oder als Ausgabe verschachtelt.

## Projektionsinvarianten

Jede gueltige positive Ausgabe prueft unabhaengig:

```text
target.U + target.C = source.U + source.C
target.capacity = source.capacity
target.free = source.free
target.blocked = source.blocked
target.aggregate_projection_digest = source.aggregate_projection_digest
```

Nur U, C und ihre abhaengigen Digests duerfen sich aendern. Die Zielbytes
muessen kanonisch und durch den unveraenderten D3-Validator gueltig sein. Ein
Nullpfad muss dasselbe Quellbyteobjekt zurueckgeben und darf keine
Neu-Serialisierung ausfuehren.

## Fokussierte Testmatrix

| Test-ID | Abnahme |
|---|---|
| `T01` | alle Fixture-, Quell-, Grenz- und Zieldigests sind exakt gebunden |
| `T02` | zehn gueltige Kontrollen liefern exakt Status und erwartete Zielbytes |
| `T03` | alle sieben Nullpfade geben exakt ihr jeweiliges Quellbyteobjekt zurueck |
| `T04` | X/X und Y/Y erzeugen bitidentisch `D3_V_MIXED` |
| `T05` | die zweite frische Fortsetzung erzeugt exakt U/C `0.125/0.375` |
| `T06` | positive Ziele erfuellen Erhaltung, Rollensperre und alle Digestregeln |
| `T07` | alle fuenf S1-OI-Fehler liefern nur den gebundenen Projektionsfehler |
| `T08` | Eingabe-, Quell-, Ziel-, Validator-, Vertrags- und Belegdigests bleiben getrennt |
| `T09` | gleiche Originalinputs und Registries liefern bitgleiche Resultate und Belege |
| `T10` | Eingabebytes und alle Registries bleiben unveraendert |
| `T11` | falsche Typen/Registries und Belege als Eingaben scheitern vor Resultat |
| `T12` | Moduloberflaeche erreicht keinen Commit-, O3-, Feld-, Runner-, I/O-, Medien- oder Netzwerkpfad |

Die Tests verwenden ausschliesslich `unittest` und Python-Standardbibliothek.
Ziel- und Receipt-Digests werden unabhaengig aus den gebundenen kanonischen
Payloadregeln rekonstruiert. Fixtures und Erwartungen werden nach einem
Testresultat nicht angepasst.

## Endliches S1-OM-Ausfuehrungsbudget

S1-OM darf genau einmal ausfuehren:

```text
python -m unittest tests.test_g2_d3_s1om_target_projection
```

Innerhalb dieser Abnahme gelten maximal:

```text
project_g2_d3_conservative_target:           40 Aufrufe
evaluate_g2_d3_continuation_halving_amount:  40 interne Aufrufe
validate_g2_d3_transient_boundary:           40 interne Aufrufe
validate_g2_d3_anatomy_record:               80 interne Aufrufe
verify_and_commit-Aufrufe:                     0
O3-Auswertungen:                               0
MCM-Feldschritte:                              0
Transfer-/Runner-/Medien-/Netzwerkaufrufe:     0
Dateischreibzugriffe des Operators:            0
read-only Quelltextzugriffe:          maximal 2
```

Bei einem Fehler wird innerhalb S1-OM nicht erneut ausgefuehrt. Die
Implementierung wird gegen den unveraenderten Vertrag korrigiert, ohne
Fixtures, Digests, Erwartungen oder Budgets nachtraeglich umzudeuten.

## Aussagegrenze

S1-OL bindet nur die spaetere Implementierung und einmalige Abnahme einer
reinen in-memory D3-Zielprojektion. Es gibt noch keinen implementierten
Zieloperator, keinen Commit, keine Sequenzruntime, keine O3- oder Feldwirkung
und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OM darf ausschliesslich die drei gebundenen Dateien implementieren, den
fokussierten Test genau einmal innerhalb des Budgets ausfuehren und das
tatsaechliche Ergebnis in den Statusdokumenten festhalten.

Commit-, O3-, Feld-, Transfer-, Runner- und Runtimepfade bleiben unveraendert
und gesperrt.
