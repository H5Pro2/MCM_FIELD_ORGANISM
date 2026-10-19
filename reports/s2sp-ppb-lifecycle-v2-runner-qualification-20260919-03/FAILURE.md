# S2-SP: PPB-Lebenszyklus V2 – Runner-Qualifikation 03

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-RUNNER-QUAL-20260919-03`  
Status: `NOT_QUALIFIED`

## Einmaliger Aufruf

```text
python -B -m unittest tests.test_s2sp_ppb_lifecycle_v2_runner -v
```

Der gebundene Aufruf lief einmal und endete mit `3/4` erfolgreichen
Kontrollen und einem Testaufbaufehler. Es erfolgte kein Retry.

| Kontrolle | Ergebnis |
|---|---|
| vollständige neutrale Runner-Hülle | bestanden |
| unvollständige Hülle vor Memoryfortschreibung | bestanden |
| falsche Art an Cue-Position | bestanden |
| ungültiger nativer Feldbeleg | nicht erreicht |

## Primärfehler

`tests/test_s2sp_ppb_lifecycle_v2_runner.py:79` versucht, aus einem bereits
adaptierten `S2SPOAMaterializedPairV1` ein natives OA-Ereignis über
`item.event` zu erzeugen. Dieser Typ trägt bewusst nur die gebundene
Paarbelegform und kein `event`-Attribut. Die erwartete
`S2SPOAAdapterError(FIELD_INPUT_TYPE_INVALID)` wurde daher nicht erreicht;
der tatsächliche Fehler lautet:

```text
AttributeError: 'S2SPOAMaterializedPairV1' object has no attribute 'event'
```

Der Produktadapter wurde in dieser Kontrolle nicht aufgerufen. Der Befund
belegt weder eine fehlerhafte Feldvalidierung noch einen Fehler der
Memoryfortschreibung. Die reale OA-A–E-Materialisierung und der V2-Hauptlauf
bleiben gesperrt.

## Bereits geprüfte lokale Korrektur

Die neue Adapterbindung liest `field_input` aus dem nativen OA-Eingang, prüft
Typ, beide Framebindungen und die gemeinsame Zeit vor jedem Zugriff auf die
Feldzeit. CPython-Kompilierung und eine AST-Prüfung bestätigten, dass die
lokale Bindung vor dem ersten Zugriff erfolgt. Die exakten Quellstände stehen
in [BINDING.md](BINDING.md).

## Kleinste nächste Korrekturrichtung

Die neutrale Negativfixture muss das native `oa.Input` vor der Adaptierung
manipulieren und erst danach `bind_materialized_input()` aufrufen. Die vier
Kontrollen sind getrennt zu binden; ein weiterer Aufruf darf nur nach einer
neuen, expliziten Qualifikationsfreigabe stattfinden.
