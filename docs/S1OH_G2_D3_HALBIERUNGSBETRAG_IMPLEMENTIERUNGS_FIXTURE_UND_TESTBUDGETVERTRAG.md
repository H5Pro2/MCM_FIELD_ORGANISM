# S1-OH G2/D3 Halbierungsbetrag: Implementierungs-, Fixture- und Testbudgetvertrag

## Status

S1-OH bindet ausschliesslich Dateigrenzen, Abhaengigkeiten, kanonische
Fixtures, Fehlermutationen, erwartete Digests und ein endliches Testbudget
fuer die spaetere isolierte S1-OG-Implementierung. Der Schritt implementiert
und fuehrt den Operator nicht aus.

Entscheidung:

```text
G2_D3_HALVING_AMOUNT_IMPLEMENTATION_FIXTURES_AND_SINGLE_TEST_BUDGET_BOUND
```

## Gebundene Dateigrenze

S1-OI darf genau drei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/g2_d3_halving_amount.py` | reine Halbierungsbetragsermittlung |
| `tests/g2_d3_s1oi_fixtures.py` | kanonische D3-/Grenzfixtures und gebundene Mutationen |
| `tests/test_g2_d3_s1oi_halving_amount.py` | fokussierte technische Abnahme |

Bestehende Produktions-, Fixture- und Testdateien bleiben unveraendert. Der
S1-OC-Grenzvalidator, D3-Validator und O3-Operator duerfen weder erweitert
noch repariert werden.

## Erlaubte Produktionsabhaengigkeiten

Das neue Produktionsmodul darf nur importieren:

- Python-Standardbibliothek fuer unveraenderliche Datentypen, exakte
  rationale Floatinterpretation, endliche Zahlen und reines JSON-Lesen;
- `G2D3ValidationRegistry` aus dem akzeptierten D3-Validator;
- Registrytyp, Receipttyp und reine Validierungsfunktion aus dem akzeptierten
  S1-OC-Grenzvalidator;
- `canonical_json_bytes` und `sha256_hex` aus dem unveraenderten
  KFS-1-Validator.

Feld-, Transfer-, O3-, Runner-, Medien-, Browser-, Netzwerk- und
Dateischreibmodule sind unzulaessig.

## Gebundene oeffentliche API

Das Modul darf genau bereitstellen:

```text
build_g2_d3_halving_amount_registry()
-> G2D3HalvingAmountRegistry

evaluate_g2_d3_continuation_halving_amount(
    boundary_raw_bytes,
    d3_raw_bytes,
    formation_enabled,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3HalvingAmountEvaluationReceipt
```

Zusaetzlich sind nur unveraenderliche Registry- und Belegtypen sowie Schema-,
Phasen-, Fehlercode-, Parameter- und Vertragsdigestkonstanten oeffentlich.
Parsing, Float-/Rationalpruefung, Preview und Belegaufbau bleiben privat.

## Feste Vertragswerte

```text
operator_class_id
= G2_D3_CONTINUATION_RESIDUAL_HALVING_AMOUNT

receipt_schema
= g2_d3_halving_amount_evaluation_receipt/s1og.v1

halving_numerator = 1
halving_denominator = 2

operator_contract_digest
= 396bd7b9fde4b7ee3b268e1d53245fd2a950cf4d8d9464f084d9b498c17de83b

accepted_boundary_validator_contract_digest
= 7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0

accepted_d3_validator_contract_digest
= b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c
```

## Kanonische Fixture-Fabriken

Die testseitige D3-Fabrik startet ausschliesslich von `D3_V_C0`, ersetzt die
fuenf Ressourcenrollen und berechnet danach in dieser Reihenfolge neu:

```text
resource_account_digest
aggregate_projection_digest
anatomy_record_digest
canonical d3_raw_bytes
```

Die Grenzbinder-Fabrik startet von genau einem bestehenden S1-OC-Tabellenfall,
ersetzt nur `source_d3_anatomy_record_digest`, berechnet
`boundary_record_digest` neu und serialisiert kanonisch. Kontaktfelder und
Kontaktdigests bleiben unveraendert.

Die Fabriken enthalten keine erwartete Operatorentscheidung, keinen
Fehlercode und keinen Receiptwert.

## Neun gueltige Kontrollfaelle

Die ersten sieben Standardfaelle verwenden unveraendert `D3_V_C0` mit:

```text
d3_anatomy_record_digest
= 1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f

d3_input_digest
= d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7
```

| Fixture | Grenze | formation_enabled | Boundary-Input-Digest | Erwartetes Ereignis | Erwarteter Betrag |
|---|---|---:|---|---|---:|
| `OG_V_FIRST_X_ON` | first X | true | `bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228` | `NO_PREDECESSOR` | `0.0` |
| `OG_V_FIRST_Y_ON` | first Y | true | `3da5f86db0772fb339b25c6e916bf0a13dfde6f5e144a8e48cb7eea62cc43769` | `NO_PREDECESSOR` | `0.0` |
| `OG_V_XX_ON` | X/X | true | `c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c` | `LOCAL_CONTINUATION` | `0.25` |
| `OG_V_YY_ON` | Y/Y | true | `2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b` | `LOCAL_CONTINUATION` | `0.25` |
| `OG_V_XY_ON` | X/Y | true | `d9db45ac53bcbddda68555ff398e7ea0f8f45f33979e84a7208d07fca965d1d0` | `LOCAL_SWITCH` | `0.0` |
| `OG_V_YX_ON` | Y/X | true | `68a94dc17f18afb4418e0d79f54f9a148d2c4eb8d9ced0f7607f372d9c2ff63e` | `LOCAL_SWITCH` | `0.0` |
| `OG_V_XX_OFF` | X/X | false | `c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c` | `LOCAL_CONTINUATION` | `0.0` |
| `OG_V_C1_XX_ON` | X/X auf D3 C1 | true | `a462d90c805e87d1f64d423260864f476640df12f5ff922c6350653967c61962` | `LOCAL_CONTINUATION` | `0.0` |
| `OG_V_INTEGER_XY_ON` | X/Y auf Integer-D3 | true | `1a2ec59aa7d2b0f50eb1d3727219f37c4c785246cdfe841a43649a1c4d209de7` | `LOCAL_SWITCH` | `0.0` |

Die sieben unveraenderten S1-OC-Grenzen behalten exakt ihre bereits
gebundenen Boundary-Record-Digests:

```text
FIRST_X 078d6250bee7a51093bde34f00d4faa33ad329f0c21fd103475d168907710027
FIRST_Y 1f6cdf067d253d0f8fa300f7074ab4ea6bb5568d4b193e0b274a12b104f6f89c
XX      15502f7ba7dedc0046d67cbdd66f0de4cfb0b8023d871bda34060358a17c2716
YY      59fb36e54c8c2214e51014009c67452249d030e846366a30dcf367c341be4326
XY      90f2bd6a4fe9cd82d40d950dd1a7288b6b98e064905dfcacb1538e5947aa34f4
YX      19be56470b54b8d074f423cb264fad33024cc17959a89cd7bb5f76f97efd3488
XX_OFF  15502f7ba7dedc0046d67cbdd66f0de4cfb0b8023d871bda34060358a17c2716
```

`OG_V_C1_XX_ON` bindet zusaetzlich:

```text
d3_input_digest
= 058ae964682a9750a316d1db1b2e155714c18bc5adab9eb71fbc6e85e3be54b5

d3_anatomy_record_digest
= 3cf515292d1a8591ce1fdecf6f510dfc79cdf72d0fa64dcd965dca41859c3e8c

boundary_record_digest
= 3ce7ab6c42fb9436a361f66b4e59d70e6fd7821c2b607f2288f896ae4551eded
```

## Integer-D3-Fixture

`D3_OG_INTEGER` besitzt exakt:

```text
capacity = 2
free = 1
bound_unconfigured = 1
bound_configured = 0
blocked = 0
```

Gebundene Digests:

```text
resource_account_digest
= 34ed3d365ff94425d9e6a6ab2d3218bb60af869f03f31aa624c460cfcef9e2b5

aggregate_projection_digest
= 604f8408ea3f4b554e60d4cc6fa41ec79154786d8249ffcf55827a2870831846

anatomy_record_digest
= 46ed2673d89583ac6dd4551377e0332bf7be50509b2e9856b37bdb7112b3cde7

d3_input_digest
= 9749ac0c341b85fbe318e6f084261d96da68cf13475cbc6dda51fb0b22e5518e
```

Der X/Y-Nullfall besitzt den oben gebundenen Boundary-Input-Digest und
Boundary-Record-Digest
`b8e3491e30122cfafece4cfadb2c2efe30735e6ddfb2241ecbff5af93b17ff55`.

## Fuenf gebundene Fehlermutationen

Jeder numerische D3-Record und seine neu gebundene X/X-Grenze sind fuer den
unveraenderten D3- und S1-OC-Validator gueltig. Der spaetere Fehler entsteht
erst im S1-OG-Operator.

### `OG_I_SOURCE`

```text
Quelle = OA_I_VERSION plus D3_V_C0
boundary_input_digest
= 2ef258e62980c27b31f36d271615d2e8c8323aa12e5f4e0d5f0c7254b7d99493
boundary_record_digest
= f922f38e140fe584ce35a054f812d2757a943a89b26aa377705528c9f69e720d
d3_input_digest
= d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7
expected = OG_SOURCE_BOUNDARY_VALIDATION_FAILED
```

### `OG_I_NUMERIC_DOMAIN`

```text
Quelle = X/X plus D3_OG_INTEGER
boundary_input_digest
= ce44be3f2eb046307a0012fb4a6a296af177ea93f1362ee314d5d409d667aa6e
boundary_record_digest
= fff4f1614c313f24fdd54cd86095dce3c5f0e63f21b27fff1a743016b0205004
d3_input_digest
= 9749ac0c341b85fbe318e6f084261d96da68cf13475cbc6dda51fb0b22e5518e
expected = OG_NUMERIC_DOMAIN_MISMATCH
```

### `OG_I_HALVING_INVARIANT`

```text
capacity = 1.0
free = 1.0
bound_unconfigured = 5e-324
bound_configured = 0.0
blocked = 0.0

resource_account_digest
= 3e2ad26896c2dd22dfba10273467d97ec900fc4701d58912f079773fa6a4cfb2
aggregate_projection_digest
= 79a66c6105be6f4b059ab1ad25512f7089022a92f25f229b199a5234fb1eb127
anatomy_record_digest
= f923d132b6621181a05936302f8c7541c2cd985ee05a27abfd69a12e5e06b30f
d3_input_digest
= 3dbd6182676d5c65b6e375cab90728a1860daadc318a358d5e1dd45ab023f558
boundary_record_digest
= 60c5ed1b2c94a8bf742ecdd16a730303cb846058535d0a9aea85dd1e596712b6
boundary_input_digest
= 0eb3b2814108033dfbd5e409ce98866fca36f7cea68696bec41101e92c65e680
expected = OG_HALVING_INVARIANT_MISMATCH
```

### `OG_I_TARGET_REPRESENTATION`

```text
capacity = 1.0
free = 0.5
bound_unconfigured = 5.551115123125783e-17
bound_configured = 0.5
blocked = 0.0

resource_account_digest
= dd86ffcb4e5120abfcb68ae24355b588dc5aa11970bc1671b275122ae1b446e2
aggregate_projection_digest
= bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e
anatomy_record_digest
= 5cad22453fccd345fd37a9196db5d7d7c6b587276110623e4a8230021d100ce9
d3_input_digest
= d73b67ce9d9d77b7a3bdce43a4852c892212e048c976b5f1b8b606b08d887d68
boundary_record_digest
= 59706574d9d18ec507cdd3f6cca5e4c3d8f62ec432a4bdc12c4b14a8e981cbda
boundary_input_digest
= 81039d1ddc544751bd014d89c2541e826ac7c17909283ebec3f0f0cdfc846700
expected = OG_TARGET_REPRESENTATION_MISMATCH
```

### `OG_I_EXACT_LEDGER`

```text
capacity = 1.0
free = 1.0
bound_unconfigured = 1.1102230246251565e-16
bound_configured = 0.0
blocked = 0.0

resource_account_digest
= 88c3a8b6fe32da3eb8d1d3fcbcdb92825abb95314f1637cf71aed47559ee2580
aggregate_projection_digest
= 6b6c73ceba827d2e5eee25a886ed2aa38c1726390299623137d52e68b6ef8747
anatomy_record_digest
= 0c7defa65f6e99bf6b959baa2cb6c24b1bdd7a9219f57e894b5d542a0293362c
d3_input_digest
= 2d29818b7dac97a7a20d45ef39134f23170911ea1e3caf3b859d2626c71bd5ab
boundary_record_digest
= dd3e3ccfba2663e182c2c0558d8199ef3d03193a473196898b5387d38030250f
boundary_input_digest
= 59fba0f0361e248b1af1699eaed8a6fedc8c7fdb257f89fac343d5f05306f552
expected = OG_EXACT_LEDGER_IDENTITY_MISMATCH
```

## Fehlergating

Jeder Fehlertest erwartet exakt einen Code:

```text
source invalid
-> keine D3-Projektion und keine Numerik

numeric domain invalid
-> keine Halbierung und keine Preview

halving invariant invalid
-> keine Preview und keine Bilanzpruefung

target representation invalid
-> keine nachgelagerte Bilanzentscheidung

exact ledger invalid
-> kein Betrag trotz vorher exakt darstellbarer Halbierung und Preview
```

Fixtures und erwartete Fehlercodes duerfen nach einem Testresultat nicht
angepasst werden.

## Fokussierte Testmatrix

| Test-ID | Abnahme |
|---|---|
| `T01` | alle Fixturebytes, Record- und Eingabedigests sind exakt gebunden |
| `T02` | neun gueltige Kontrollfaelle liefern exakt Ereignis und Betrag |
| `T03` | X/X und Y/Y liefern bitgleich `0.25` |
| `T04` | Ablation, leere Restressource und Integer-Switch bleiben exakt null |
| `T05` | alle fuenf Fehlermutationen liefern exakt ihren einzelnen Code |
| `T06` | Quellfehler sperrt Ereignis, D3-Werte und Betrag |
| `T07` | Numerikfehler werden nur nach ihren jeweiligen Voraussetzungen erzeugt |
| `T08` | Quell-, Record-, Vertrags- und Belegdigests bleiben getrennt |
| `T09` | gleiche Bytes und Registries liefern bitgleiche Belege |
| `T10` | Eingabebytes und alle Registries bleiben unveraendert |
| `T11` | falsche API-Typen/Registries scheitern vor Beleg; Beleg ist nicht rueckfuehrbar |
| `T12` | Moduloberflaeche erreicht keinen Ziel-, Commit-, O3-, Feld-, Runner-, I/O-, Medien- oder Netzwerkpfad |

Die Tests verwenden ausschliesslich `unittest` und Python-Standardbibliothek.
Receipt-Digests werden unabhaengig aus der vorab gebundenen Payloadregel
rekonstruiert; sie werden nicht aus der Implementierung uebernommen.

## Endliches S1-OI-Ausfuehrungsbudget

S1-OI darf genau einmal ausfuehren:

```text
python -m unittest tests.test_g2_d3_s1oi_halving_amount
```

Innerhalb dieser Abnahme gelten maximal:

```text
evaluate_g2_d3_continuation_halving_amount: 36 Aufrufe
validate_g2_d3_transient_boundary:          36 interne Aufrufe
validate_g2_d3_anatomy_record:              36 interne Aufrufe
validate_g2_d3_f1_pair:                      0 Aufrufe
O3-Auswertungen:                              0
D3-Zielrecord- oder Commitoperationen:         0
MCM-Feldschritte:                              0
Transfer-/Runner-/Medien-/Netzwerkaufrufe:     0
Dateischreibzugriffe des Operators:            0
read-only Quelltextzugriffe:          maximal 2
```

Bei einem Fehler wird innerhalb S1-OI nicht erneut ausgefuehrt. Implementierung
und Vertrag werden getrennt geprueft; Fixtures, Digests und Erwartungen
bleiben unveraendert.

## Aussagegrenze

S1-OH bindet nur die spaetere Implementierung und einmalige Abnahme einer
reinen Betragsermittlung. Es gibt noch keinen implementierten Betrag, keinen
D3-Zielzustand, keinen Commit, keine O3- oder Feldwirkung, keine Lernfunktion
und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OI darf ausschliesslich die drei gebundenen Dateien implementieren, den
fokussierten Test genau einmal innerhalb des Budgets ausfuehren und das
Ergebnis in den bestehenden Statusdokumenten festhalten.

Alle Zielzustands-, Commit-, O3-, Feld-, Transfer-, Runner- und Runtimepfade
bleiben unveraendert und gesperrt.
