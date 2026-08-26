# S1-SD: Materialisierung und Implementierung der Vier-Knoten-Frischmatrixregistrierung

## Status und Umfang

S1-SD materialisiert die in S1-SC gebundene versionierte
Frischmatrixregistrierung, implementiert ihren strikten Consumer und
definiert elf fokussierte Unit-Tests.

Die Tests wurden nicht ausgefuehrt. Es wurde kein Frischzustand gebaut,
kein Modellkern aufgerufen, kein Expositionsfixture erzeugt, keine
Matrixzelle materialisiert und kein Forschungslauf gestartet.

Implementierungsstatus:

```text
S1SD_MATRIX_REGISTRATION_MATERIALIZED
STRICT_MATRIX_REGISTRATION_CONSUMER_IMPLEMENTED
ELEVEN_FOCUSED_TESTS_DEFINED_NOT_EXECUTED
S1RK_V1_REPORT_AND_CONSUMER_UNCHANGED
NO_FRESH_BUILD_NO_MATRIX_CELL_NO_FIELD_EXECUTION
```

## Materialisierte Registrierung

Neue Datei:

```text
reports/s1sd_four_node_fresh_matrix_registration.json
```

Gebundene Identitaeten:

| Rolle | Wert |
|---|---|
| Schema | `mcm.s1sc.four-node-fresh-matrix-registration.v1` |
| Quellvertrag | `S1-SC` |
| Kanonisierung | `S1-JN/S1-JT-compact-json-sha256-v1` |
| Registrierungsdigest | `edd3414b3dcc082c0ab7bec66f8dd278cedecd76d11e649ca7aff46a9317a4ba` |
| Basismanifestdigest | `ae7a7356a3e06776a000b6e9fafef75b717944f1d75da62d4418be98cc439c68` |
| Expositionsrepliken | `17` |
| Matrixzellen | `238` |
| passive Pflichtrecords | `560` |

Die Rollenpositionen 16 und 17 sind getrennt als
`U_FRESH_B_EARLY` und `U_FRESH_B_LATE` materialisiert. Die Datei enthaelt
keine Ereignisse, Kontaktwerte, Dauern, Parameter, Modellinputs oder
Erwartungsrichtungen.

Der Registrierungsdigest wird ueber die kanonische Compact-JSON-Praeimage
ohne das eigene Feld `registration_digest` gebildet.

## Implementierter Consumer

Neue Produktionsdatei:

```text
mcm_field_organism/four_node_fresh_matrix_registration.py
```

Die implementierte Oberflaeche umfasst:

```python
class FourNodeFreshMatrixRegistrationError(ValueError): ...

@dataclass(frozen=True, slots=True)
class FourNodeFreshMatrixRegistration: ...

def parse_four_node_fresh_matrix_registration(...): ...
def load_four_node_fresh_matrix_registration(...): ...
def validate_four_node_fresh_matrix_registration_against_manifest(...): ...
```

Der Parser prueft strikt:

- UTF-8, JSON und doppelte Schluessel;
- exakte Root-, Basis-, Achsen-, Zaehler- und Projektionsformen;
- Schema-, Quellvertrags- und Kanonisierungsidentitaet;
- die lueckenlose geordnete 17-Rollen-Achse;
- Integer- und Booltypen ohne Gleichsetzung von `true` und `1`;
- die Ableitungen `14 x 17 = 238`, `34 + 6 = 40` und `14 x 40 = 560`;
- alle unveraenderten v1-Basisdigests;
- den kanonischen Registrierungsdigest;
- eine rekursiv unveraenderliche Ergebnissicht.

Der gemeinsame Validator reserialisiert die uebergebene v1-Manifestansicht
und laesst sie erneut durch den technisch abgenommenen v1-Parser pruefen.
Erst danach vergleicht er alle Basisidentitaeten. Ein nur typgleich
konstruiertes, aber nicht gueltiges Manifestobjekt wird dadurch nicht als
Vertrauensbeleg behandelt.

Es existieren keine Importzeit-Dateioperation, kein Cache, kein Default,
keine Reparatur und kein Teilresultat.

## Definierte Tests

Neue Testdatei:

```text
tests/test_four_node_fresh_matrix_registration.py
```

Elf Tests sind definiert fuer:

1. Annahme der registrierten Datei und die beiden getrennten U-Rollen;
2. rekursive Unveraenderlichkeit;
3. Nicht-Bytes, ungueltiges JSON und doppelte Schluessel;
4. unbekannte, fehlende und abweichende Schemafelder;
5. Registrierungsdigestabweichung;
6. Achsenreihenfolge, Duplikat und falsche Laenge;
7. alte oder inkonsistente 16-/224-/532-Zaehler;
8. abweichende v1-Basisidentitaet;
9. abweichende oeffentliche Frischprojektionsbindung;
10. gemeinsame Validierung mit dem registrierten v1-Manifest;
11. Ablehnung eines nur typgleich konstruierten ungueltigen Manifests.

Die Anzahl liegt unter dem S1-SC-Maximum von 12. Kein Test importiert einen
Modellkern oder erzeugt eine Matrixzelle.

## Statischer Artefaktaudit

Ohne Import oder Testausfuehrung wurden geprueft:

```text
DIGEST_MATCH=True
REPLICAS=17
CELLS=238
CHECKPOINTS=560
AST_PARSE=OK
DEFINED_TESTS=11
```

Die unveraenderten Byte-SHA-256-Werte lauten weiterhin:

```text
reports/s1rk_four_node_fresh_manifest.json
19cc753c110b64d1d48cabe46be190a01247995053da442dd4cefcd344ea8bfc

mcm_field_organism/four_node_fresh_manifest.py
780c7475d2fa52cafa7da988df6f32331b9bbca99f3ca5aa3c6df04875e45220
```

Dieser statische Audit belegt Dateiform und Syntax, aber noch nicht das
Laufzeitverhalten des neuen Consumers.

## Aussagegrenze

S1-SD implementiert nur eine technische Registrierungs- und
Integritaetsgrenze. Daraus folgt noch keine technische Abnahme, keine
ausfuehrbare 238-Zellen-Matrix, kein Baselinebefund und keine Faehigkeit
einer hypothetischen MCM-Memory-Entwicklungsrichtung.

## Genau ein naechster Schritt

S1-SE darf ausschliesslich den einmaligen unveraenderten fokussierten Lauf
ausfuehren:

```text
python -m unittest discover -s tests -p "test_four_node_fresh_matrix_registration.py" -v
```

Bei einem Fehler wird nur der Fehlerstand dokumentiert. Keine Korrektur im
selben Schritt, kein allgemeiner Testbestand, keine Fabrikaenderung, kein
Expositionsfixture, keine Matrixzelle und kein Forschungslauf.
