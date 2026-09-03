# S2-KJ Wiederholungsqualifikationsbefund

## Status

`QUALIFICATION_FAILED_BINDER_CONSTRUCTION_ERROR`

Die ausschliesslich freigegebene neutrale Audiofixture wurde korrigiert. Jede
der zwei vollstaendig unabhaengigen Fixtures verwendet nun genau einen
durchgehenden `BroadbandHearingPath`. Hops, `snapshot_index`, Samplefenster und
gemeinsame AV-Zeit schreiten innerhalb jeder Fixture strikt fort.

Der einzige neue Qualifikationsaufruf passierte diese Zeitgrenze, endete aber
im S2-KJ-Binder, bevor einer der zwoelf Testkoerper lief.

## Einmalaufruf

```text
Qualifikations-ID: s2kj-qualification-20260903-02
python -m unittest tests.test_s2kj_two_area_perceptual_context_336 -v
Exit-Code: 1
Ausgefuehrte Testkoerper: 0/12
Terminal: FAILED (errors=1)
```

## Ursache

`_make_av_candidate` bildet fuer die kanonische Digestserialisierung korrekt
Listen aus den auditiven und visuellen Wertetupeln. Derselbe
Serialisierungspayload wird danach jedoch unveraendert als Konstruktorpayload
fuer `AVContextCandidate336V1` verwendet. Der unveraenderliche Datentyp erhaelt
dadurch Listen statt der vertraglich gebundenen Tupel. Die interne Validierung
stoppt korrekt mit:

```text
S2KJ_DIMENSION_INVALID:
AV auditory candidate must contain exactly 48 values
```

Die enge spaetere Korrektur muss Konstruktion und kanonische Serialisierung
trennen: Der Datentyp erhaelt die urspruenglichen Tupel; nur der Digestpayload
enthaelt Listen. Derselbe Punkt ist fuer den stabilen Modalitaetskandidaten zu
pruefen. In diesem Schritt wurden Produktcode und Validatoren entsprechend der
Freigabe nicht veraendert und der Test nicht wiederholt.

## Gebundene Quellhashes

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2kj_validated_perceptual_finding_336.py` | `9e6a98181d1ccb5a32b8598493c09dd3eb5a67aa2ee355a4d71f1ee295123b85` |
| `tools/_s2kj_two_area_perceptual_context_336.py` | `5e2510eb6dd58ffef27901fc545ad700d1f8a5e4d5b3363d09811fe11c0a1d17` |
| `tests/test_s2kj_two_area_perceptual_context_336.py` | `1261b9524a3c1142ae0be446f84531e6e6df83272485775f693cd14e1d868f23` |

Die beiden Produktdigests sind gegenueber der ersten Qualifikation
unveraendert. Alle drei Hashes waren nach dem Lauf unveraendert.

## Aussagegrenze

Die Audiozeitkorrektur ist belegt. S2-KJ bleibt dennoch unqualifiziert;
`PRIVATE_TWO_AREA_PERCEPTUAL_CONTEXT_336_VALID` wird nicht gesetzt. Es liegt
kein Memory- oder Kontextnutzungsbefund vor. Eine weitere Qualifikation braucht
eine neue ID und eine gesonderte Freigabe fuer die enge
Konstruktor-/Serialisierungskorrektur.
