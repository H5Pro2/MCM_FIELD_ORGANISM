# S1-SG: Implementierung des kanonischen Vier-Knoten-Expositionsfixtures und Fail-Closed-Validators

## Status und Umfang

S1-SG implementiert den S1-SF-Vertrag als unveraenderliches kanonisches
17-Plan-Fixture mit realen `ReceptorDistribution`- und
`MCMFieldStepTime`-Objekten. Zusaetzlich implementiert der Schritt eine
strikte Validierung gegen die technisch abgenommene S1-SD-
Matrixregistrierung und definiert 13 fokussierte Unit-Tests.

Die Tests wurden nicht ausgefuehrt. Kein Modellkern wurde importiert oder
aufgerufen, kein Alignziel auf ein Feld angewandt, keine Matrixzelle gebaut
und kein Forschungslauf gestartet.

Implementierungsstatus:

```text
CANONICAL_SEVENTEEN_PLAN_EXPOSURE_FIXTURE_IMPLEMENTED
STRICT_REGISTRATION_AND_FIXTURE_VALIDATION_IMPLEMENTED
THIRTEEN_FOCUSED_TESTS_DEFINED_NOT_EXECUTED
NO_ALIGN_APPLICATION_NO_MODEL_INVOCATION_NO_MATRIX_CELL
```

## Neue Produktionsoberflaeche

Datei:

```text
mcm_field_organism/four_node_exposure_fixture.py
```

Oeffentliche Werttypen:

```python
FourNodeExposureInterval
FourNodeAlignTarget
FourNodeExposureEvent
FourNodeExposurePlan
FourNodeExposureFixture
```

Oeffentliche Operationen:

```python
build_four_node_exposure_fixture(registration)
validate_four_node_exposure_fixture(fixture, registration)
```

Der Builder reserialisiert die uebergebene Matrixregistrierung und laesst
sie erneut durch deren strikten Parser pruefen. Ein nur typgleich
konstruiertes Registrierungsobjekt ist keine gueltige Quelle.

## Materialisierte Eingabeformen

Jedes modellwirksame Ereignis enthaelt genau:

- eine `ReceptorDistribution` auf `mcm.s1sf.field`;
- ein wert- und grenzgleiches `MCMFieldStepTime`;
- genau zehn Ticks bei `10.0` Ticks pro Sekunde;
- den S1-SF-Payload `A_CONTACT`, `B_CONTACT`, `C_CONTACT`,
  `PROBE_A_CONTACT`, `PROBE_B_CONTACT` oder `ZERO_CONTACT`;
- einen kanonischen Intervall- und Ereignisdigest.

Nichtnullkontakte tragen einen vollstaendigen Vier-Carrier-Frame am
registrierten technischen Dock. Nullkontakte besitzen exakt `contacts=()`.
Snapshotidentitaeten werden nur aus Payloadrolle und Tickgrenze gebildet.

Align- und Checkpointereignisse enthalten kein Intervall. Das Alignziel
bindet bei seinem Feldtick nur die vier Nullvektoren fuer aktuellen Kontakt,
S und H. Es wendet diese Projektion noch nicht an.

## Planmaterialisierung

Alle 17 S1-SF-Rollen werden in registrierter Reihenfolge gebaut. Die
C-Plaene enthalten `PRE_COMPETITION` und `POST_COMPETITION` zusaetzlich zu
den universellen Checkpoints. Alle anderen Plaene besitzen nur
`ALIGNED_PRE_PROBE` und `POST_PROBE_READOUT`.

Die statische Konstruktion ergibt:

```text
PLANS=17
INTERVALS=127
ALIGNS=17
CHECKPOINTS=40
EVENTS=184
```

Der kanonische Fixturedigest lautet:

```text
ca66f3a673eaca663a0973f7e956a90f4788e6f51963b71de4952801936bac3e
```

Er wird ueber Schema, Quellvertrag, Matrixregistrierungsdigest, geordnete
Plandigests und die drei Vollstaendigkeitszahlen gebildet. Jeder Plandigest
bindet die geordnete Ereignisdigestfolge.

## Fail-Closed-Validierung

`validate_four_node_exposure_fixture` baut aus der erneut validierten
Registrierung die kanonische Erwartung neu auf. Akzeptiert wird nur die
vollstaendige Wertgleichheit. Abweichungen werden ohne Teilfixture mit
stabiler Fehlerklasse verworfen:

```text
FOUR_NODE_EXPOSURE_FIXTURE_REGISTRATION_INVALID
FOUR_NODE_EXPOSURE_FIXTURE_SHAPE_INVALID
FOUR_NODE_EXPOSURE_FIXTURE_PLAN_AXIS_INVALID
FOUR_NODE_EXPOSURE_FIXTURE_CARDINALITY_INVALID
FOUR_NODE_EXPOSURE_FIXTURE_DIGEST_INVALID
FOUR_NODE_EXPOSURE_FIXTURE_EVENT_ORDER_INVALID
FOUR_NODE_EXPOSURE_FIXTURE_INTERVAL_INVALID
```

Eine umsortierte Rolle, ein fehlender Plan, eine alte 16-Repliken-Achse,
ein anderer Tick, Kontakt oder Checkpoint und ein neu berechnetes
Alternativfixture bleiben unzulaessig.

## Definierte Tests

Datei:

```text
tests/test_four_node_exposure_fixture.py
```

13 fokussierte Tests sind definiert fuer:

1. registrierte 17-Plan-Achse und 127/17/40-Zaehler;
2. deterministische Konstruktion, Fixturedigest und Unveraenderlichkeit;
3. exaktes Kontaktalphabet und gemeinsame Feldzeit;
4. echte leere Nullkontaktverteilungen;
5. Snapshotidentitaeten ohne Plan- oder Modelllabels;
6. exakte T-Praefixe und davon verschiedene F-Geschichte;
7. F- sowie lokale/entfernte Last- und Zeitanpassung;
8. nur passive Zusatzcheckpoints der C-Plaene;
9. getrennten I-Gap sowie echten fruehen/spaeten Freigabepraefix;
10. wert- und zeitidentische fruehe und spaete U-B-/Probe-Paare;
11. zeitfreie Align- und Checkpointereignisse;
12. Annahme nur des kanonischen Fixtures und Ablehnung veraenderter Achse;
13. Ablehnung einer ungueltigen Matrixregistrierung.

Die Testdatei importiert keinen Modellaufruf und erzeugt keine
Matrixzelle.

## Statischer Konstruktionsaudit

Ohne Unit-Testlauf wurden nur Python-Syntax, deterministische
Fixturekonstruktion und Zaehler geprueft:

```text
AST_PARSE=OK
FIXTURE_DIGEST=ca66f3a673eaca663a0973f7e956a90f4788e6f51963b71de4952801936bac3e
PLANS=17
INTERVALS=127
ALIGNS=17
CHECKPOINTS=40
EVENTS=184
DEFINED_TESTS=13
```

Diese Konstruktion ruft keinen Feld- oder Modellschritt auf und ist noch
keine technische Testabnahme.

## Aussagegrenze

S1-SG zeigt nur, dass der vorregistrierte Eingabeplan programmatisch
darstellbar ist. Daraus folgt keine ausfuehrbare Gesamtmatrix, kein
Baselineergebnis und keine Faehigkeit einer hypothetischen
MCM-Memory-Entwicklungsrichtung.

## Genau ein naechster Schritt

S1-SH darf ausschliesslich den einmaligen unveraenderten fokussierten Lauf
ausfuehren:

```text
python -m unittest discover -s tests -p "test_four_node_exposure_fixture.py" -v
```

Bei einem Fehler wird nur der Fehlerstand dokumentiert. Keine Korrektur im
selben Schritt, kein allgemeiner Testbestand, keine Alignanwendung, kein
Modellaufruf, keine Matrixzelle und kein Forschungslauf.
