# S2-MJ: Vorversiegelung und OpenCV-Flow-Preflight

## Status

`S2MJ_DENSE_FLOW_PATH_AVAILABLE`

Die lokale reproduzierbare Faehigkeit fuer den in S2-MJ gebundenen dichten
Farneback-Fluss ist nachgewiesen. Dieser Befund bestaetigt weder die
Vollbildmessung noch eine fachliche Trennung, Objektidentitaet,
Plattformunabhaengigkeit oder eine Integration in Memory, Kontext oder Feld.

## Reihenfolge

1. Der Acht-Paar-Korpus und die unabhaengige Evaluationswurzel wurden unter
   `s2mj-motion-corpus-preseal-20260905-01` versiegelt.
2. Erst danach lief genau ein isolierter OpenCV-Preflight unter
   `s2mj-opencv-flow-capability-preflight-20260905-01`.
3. Der Preflight oeffnete keine Korpusframes und importierte oder rief keine
   Projektmodule beziehungsweise Projektfunktionen auf.
4. Es gab keine Installation, Aktualisierung, Ersatzbibliothek oder
   Wiederholung.

## Vorversiegelung

- kanonische Framebindungen: `16`;
- neutrale Framepaare: `8`;
- getrennte Evaluationsfaelle: `8`;
- gespeicherte Rohpayloads: `0`;
- Flow-, Rezeptor-, Memory-, Kontext- und Feldaufrufe: jeweils `0`.

| Artefakt | SHA-256 |
| --- | --- |
| `source-plan.json` | `e39fabcd207b45812cac80d9228d45e14740eba8e5329dfe92784e4c14f34b5d` |
| `execution-plan.json` | `eb459bd1ade3b3f7eddd46d28b5354f1ddc5de624de760a608ead03ecace7780` |
| `evaluation-plan.json` | `73ff71915293587113a3ddfac28a7c1dfdbb0453ba05f371cb91f353e90b85fc` |
| `preseal-receipt.json` | `7fafdc7e4d092add3dd78bd2015682e9094f4ba5aa2555ef2fec3bb986548034` |

Der kanonische `preseal_receipt_digest` lautet
`d4f614aef4240babaaa7b1659cc60696f835ad9edb151b225023bc33fdc8fad5`.
Der rollenfreie Ausfuehrungsplan enthaelt weder Evaluationsklasse noch
Generatorparameter. Rollen und ordinale Sollrelationen stehen nur in der
getrennten Evaluationswurzel.

## Lokale Faehigkeitsbindung

| Bindung | Beobachteter Wert |
| --- | --- |
| Python | `CPython 3.14.4` |
| Python-Pfad | `.venv/Scripts/python.exe` |
| OpenCV | `4.13.0` |
| NumPy | `2.5.1` |
| geladenes Binarmodul | `.venv/Lib/site-packages/cv2/cv2.pyd` |
| Binarmodulgroesse | `74.819.072` Byte |
| Binarmodul-SHA-256 | `78db0c836b952d9d5510140677463687c357a7166fddfa6ac7e31abb2d7d9bbd` |
| `cv2.getBuildInformation()`-SHA-256 | `8a55f551e40cf84d0fa7e2509bb9544da66782a8cbc017d7ce27a9de0ef9c1ac` |
| `calcOpticalFlowFarneback` | vorhanden und aufrufbar |
| gesetzte OpenCV-Threadzahl | `1` |
| OpenCL nach Deaktivierung | `False` |

Die neutrale Fixture hatte die Form `64 x 80`, Datentyp `uint8`. Beide
Aufrufe erzeugten ein endliches Flussfeld der Form `64 x 80 x 2` und des
Datentyps `float32`. Beide Little-Endian-Flowbytes waren bitgleich:

```text
d760e8bd49a504f82578decddd90a05cd359144b6f42b7aa3147b2c8a65bdcea
```

Der `capability_digest` lautet
`1bfd6c568e2e55903f15a7234a038160f666d90dc954a4be77f97fc9fdb61eb1`.

## Preflightbelege

| Artefakt | SHA-256 |
| --- | --- |
| `plan.json` | `5d7e58b4c706f3510d76bb573d5d56a3c73338cc17dd9286d4f2550376d1517c` |
| `result.json` | `db8696bc0309468a6cea8038fe735680c473024cde3956f09296244c631d6328` |
| `terminal.json` | `ca053d9182f5fbef0c2bab7265b2e1a2f3f15ae3d0b4a09359e338fd14dff1d5` |

Der Prozess endete mit Exit-Code `0`. Die gebundenen Zaehler lauten:

```text
corpus_frames_opened            = 0
project_modules_imported        = 0
project_function_calls          = 0
install_update_or_fallback_calls = 0
```

## Aussagegrenze

Der Befund erlaubt als naechsten separaten Schritt ausschliesslich die
Vorbereitung einer kleinen privaten Mess- und Vergleichsimplementierung
gegen den versiegelten Acht-Paar-Korpus. Er autorisiert noch keinen
Korpuslauf und keine Memory-, Kontext- oder Feldintegration.
