# S2-SP: PPB-Lebenszyklus V2 – Runner-Qualifikation 04

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-RUNNER-QUAL-20260919-04`  
Status: `QUALIFIED`

Der einmalige Einzelaufruf der bisher nicht erreichten nativen
Feldbindungskontrolle bestand (`1/1`). Er erzeugt ein natives `oa.Input`,
ersetzt dessen `field_payload` durch eine ungültige Form und erreicht den
Produktadapter. Dieser weist die Eingabe mit
`S2SPOAAdapterError(FIELD_INPUT_TYPE_INVALID)` ab.

Zusammen mit den drei unter unverändertem Produktcode bestandenen Kontrollen
aus `...-03` ergibt dies die vollständige fokussierte Runnerdeckung `4/4`:

| Prüfbereich | Herkunft | Ergebnis |
|---|---|---|
| vollständige neutrale Hülle | `...-03` | bestanden |
| unvollständige Hülle | `...-03` | bestanden |
| falsche Cue-/Formationsart | `...-03` | bestanden |
| nativer ungültiger Feldbeleg | `...-04` | bestanden |

Die frühere `3/4`-Qualifikation bleibt ein historischer Fehlbefund. Dieser
Nachweis wiederholt keine der drei bereits erreichten Kontrollen. Details und
Quellstände stehen in [BINDING.md](BINDING.md).
