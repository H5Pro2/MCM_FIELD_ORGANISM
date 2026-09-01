# S2-JQ - Codec- und Containerpreflight

## Status

`VIDEO_DECODE_PATH_UNAVAILABLE`

Lauf-ID:

`s2jq-video-pcm-preflight-20260901-01`

Datum: `2026-09-01`

Der einmalige zweistufige Preflight wurde fail-closed in Stufe 1 beendet.
Stufe 2 wurde nicht betreten. Es gab keinen Retry, keinen Ersatzcodec und
keine Toleranz- oder Konvertierungsregel.

## Gebundener Lauf

Implementierungsquelle:

`tools/_s2jq_private_video_pcm_preflight.py`

SHA-256:

`6942b41d8b9667dbda40228d3174e202c39a505d7e2aed5150c94e4be64e800f`

Weitere gebundene Quellen:

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| `docs/S2JP_VIDEO_PCM_QUELLENAUSWAHL_UND_MATERIALISIERUNGSVERTRAG.md` | `43c455d04a117b1c11e13fbc13a33581ca09ed2709cf11889f889d8b811606bd` |

Runtime:

- CPython `3.14.4` auf Windows;
- PyAV `16.1.0`;
- FFmpeg `8.0.1`;
- Little Endian.

## Ergebnis Stufe 1

Die statische Vorbereitung bestaetigte:

- keine Aufrufe von `VideoFrame.to_ndarray`, `VideoFrame.reformat`,
  `AudioFrame.to_ndarray` oder `AudioResampler`;
- keine Rezeptor-, Memory-, Kontext- oder Feldaufrufe;
- direkte Plane-Bytepfade fuer vorgesehenes `rgb24` und `pcm_f32le`;
- ein neues, nicht wiederverwendetes Lauf- und Fixtureverzeichnis.

Der Lauf stoppte danach mit:

```text
S2JQ_CAPABILITY_ABSENT
rawvideo encoder does not advertise rgb24
```

Der konkrete PyAV-Codecbeleg wies `rgb24` nicht als Encoderformat des
gebundenen `rawvideo`-Encoders aus. Nach der vorab gebundenen Stopplogik wurde
deshalb kein direkter Schreib-/Leseversuch begonnen.

Dieser Befund belegt nicht, dass jede FFmpeg-Installation grundsaetzlich kein
RGB24-Rawvideo schreiben kann. Er belegt eng, dass der ausgewaehlte Pfad unter
der gebundenen Faehigkeitsannahme in diesem Preflight nicht freigegeben wurde.
Die fehlende direkte Probe darf nicht nachtraeglich als erfolgreich oder als
Bitgleichheitsnachweis ausgegeben werden.

## Nicht erreichte Stufe 2

Es wurden nicht erzeugt:

- kein NUT-Capabilitycontainer;
- keine vollstaendige etwa 37-MB-S2-JO-Quelldatei;
- kein Container-SHA-256 oder Streaminventar;
- keine sechs dekodierten RGB8-Frames;
- keine 20 dekodierten PCM_F32LE-Hops;
- keine 26 positionsweisen Payloaddigestvergleiche.

Das lokale Fixtureverzeichnis blieb leer. Ein privater Video-/PCM-Adapter ist
damit nicht freigegeben. `JN-B03` bleibt offen.

## Belegdateien

| Datei | Byte | SHA-256 |
| --- | ---: | --- |
| `plan.json` | `1286` | `5b7be601d840a6dbfdc40f8e4494ca533da5a6aa53e1ee7b99c44258dbc43a93` |
| `events.jsonl` | `778` | `fc79ff43aeb0d4ff3bd853ed5cf4508a58fe13ca266e30f20bc02e6afd3e2d2d` |
| `result.json` | `399` | `107acbaf751a0ce054d8fb6585dd10870a2d0ca61b444badfccba51af725f282` |
| `terminal.json` | `363` | `e78517e11e60885477899389b49bde6210501ec75a15b033d5d0679de3ad2183` |
| `UNAVAILABLE` | `65` | `8919870bf8cb786964712882484e5ea97fa06dac175db589e0e00836707afa77` |

Die zwei Journalereignisse bilden eine gueltige SHA-256-Kette. Der
`terminal_event_digest` lautet:

`fc3fc3494d98766f843b3d9ec307d3b75b58161ac7e6836dd45d5fb85fbb9a2d`

Der terminal gebundene Skript-Exit-Code ist `2`. Der aufrufende Host meldete
den nicht erfolgreichen Prozess als Exit-Code `1`; beide Angaben bedeuten
einen technischen Fail-Closed-Abschluss, nicht Erfolg.

## Funktionsgrenze

Zaehler des maschinenlesbaren Ergebnisses:

- Rezeptoraufrufe: `0`;
- Memoryaufrufe: `0`;
- Kontextaufrufe: `0`;
- Feldaufrufe: `0`.

S2-JQ ist kein Wahrnehmungs-, Memory- oder Feldbefund. Der ausgewaehlte
Video-/PCM-Adapter bleibt gesperrt.
