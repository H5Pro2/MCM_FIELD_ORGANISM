# S2-MO: Vorversiegelter Sparse-LK-Korpuslauf

## Status

`NOT_EVALUABLE`

Der Lauf `s2mo-presealed-sparse-motion-corpus-20260905-01` wurde genau
einmal ausgefuehrt und nicht wiederholt. Der terminal gebundene Exit-Code
lautet `3`.

Es liegt kein fachlicher Bewegungs-, Fortsetzungs-, Formwechsel-,
Verdeckungs-, Szenensprung-, Objektidentitaets-, Memory-, Kontext- oder
Feldbefund vor.

## Unveraenderte Vorbedingungen

Der Lauf verwendete ausschliesslich den bereits vor Sparse-LK versiegelten
S2-MJ-Korpus:

| Bindung | Digest oder SHA-256 |
| --- | --- |
| Source-Plan-Digest | `5a77dab593e7168afc210ccb7eccc4e7c50d3237868385e6d90dda68fa22849c` |
| Source-Plan-Datei | `e39fabcd207b45812cac80d9228d45e14740eba8e5329dfe92784e4c14f34b5d` |
| Execution-Plan-Digest | `561ae5179be4be724356588a5891e1748493b78df141a8a9914917743f61cd69` |
| Execution-Plan-Datei | `eb459bd1ade3b3f7eddd46d28b5354f1ddc5de624de760a608ead03ecace7780` |
| Evaluation-Plan-Digest | `412d128841b87d583e8fb22e35d28e21dcbf195d8c6f06b2b2f31aba181a44db` |
| Evaluation-Plan-Datei | `73ff71915293587113a3ddfac28a7c1dfdbb0453ba05f371cb91f353e90b85fc` |
| Preseal-Receipt-Digest | `d4f614aef4240babaaa7b1659cc60696f835ad9edb151b225023bc33fdc8fad5` |
| S2-MN-Capability-Digest | `2b6092b0d8b4165de60931d3e82747ef014085f6c1c5ee6120425f8b87fc6500` |

Es wurde kein neuer Korpus erzeugt, keine Quelle ersetzt und kein
Messparameter veraendert.

## Einmaliger Aufruf

```text
.venv/Scripts/python.exe tools/_s2mo_private_sparse_motion_corpus_runner.py \
  --workspace-root C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace \
  --output-root C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2mo \
  --contract-file-sha256 4d12ec00d1ae147e15e77c25f88a451c61793f1200940ded3fb75fa1b63c2982
```

## Technischer Abbruch

Der terminale Fehler lautet:

```text
RuntimeError: INSUFFICIENT_VALID_TRACKS
```

Mindestens ein Paar unterschritt damit die prospektiv gebundene Grenze von
`1.152` gemeinsam gueltigen, indexgeordneten Vorwaerts-/Rueckwaertstracks.
Der Vertrag schreibt fuer diesen Fall `NOT_EVALUABLE` vor.

Die Laufhuelle publiziert die neutrale Ausfuehrungsevidenz erst atomar nach
allen acht Paaren. Der Abbruch trat vorher ein. Deshalb existiert kein
`execution-evidence.json`, kein Evaluations-Run-Binding und kein
`evaluation-result.json`. Insbesondere wurden die versiegelten Fallrollen
nicht geoeffnet und keine ordinale Auswertung vorgenommen.

Da keine Teilbelege publiziert wurden, darf aus dem abgeschlossenen Lauf
nicht nachtraeglich abgeleitet werden, welches Paar oder welche konkrete
Trackzahl den Abbruch verursachte. Eine diagnostische Wiederholung ist unter
dieser Lauf-ID ausgeschlossen.

## Terminalbindung

| Artefakt | SHA-256 |
| --- | --- |
| S2-MO-Vertrag | `4d12ec00d1ae147e15e77c25f88a451c61793f1200940ded3fb75fa1b63c2982` |
| Runnerquelle | `046e3f8b2bb2bbf295fd84fbfe07ea1db71ba11224a54690ce8fa538525b2ddc` |
| `terminal.json` | `4a44dc8af12465d0f4b4e784ce817a0a1012d47fa78217621a799e6b187c8fee` |
| Terminal-Digest | `04c20dbde94f979ad725e218d8b1c2aaae929d9cf3de97bdd247c9acdad681db` |

Die maschinenlesbaren Belege liegen unter:

`reports/s2mo/s2mo-presealed-sparse-motion-corpus-20260905-01/`

## Grenzen

- Wiederholungen: `0`;
- Matchschwellen, Toleranzen oder Rundungen: `0`;
- neue oder ersetzte Korpusquellen: `0`;
- fachliche Auswertungen: `0`;
- Rezeptor-, Memory-, Kontext- und Feldaufrufe: `0`;
- persistierte Rohframes oder Trackarrays: `0`.

S2-MN bleibt als neutraler technischer Capability-Befund gueltig. S2-MO
zeigt lediglich, dass die feste Mindestabdeckung von 75 Prozent nicht fuer
jedes Paar des unveraenderten S2-MJ-Korpus erreicht wurde. Sparse-LK ist
damit nicht allgemein widerlegt; der vorliegende Korpuslauf ist jedoch nicht
fachlich auswertbar.
