# S2-JR - Ein-Frame-Browser-Rasterpreflight

## Status

`NOT_EVALUABLE`

Lauf-ID:

`s2jr-frame0-browser-preflight-20260902-01`

Der einmalig freigegebene Browserlauf stoppte vor der Screenshotaufnahme.
Es liegt deshalb weder `PAYLOADS_DIFFER` noch ein positiver
Pixelgleichheitsbefund vor. Der Lauf wurde nicht wiederholt und nicht mit
einem anderen Browser, Viewport, Flag oder Capturepfad fortgesetzt.

## Gebundener Stand

| Quelle | SHA-256 |
| --- | --- |
| `docs/S2JR_BROWSER_VIEWPORT_SIMULATION_VISUALVERTRAG.md` | `d1da8ba275ff76ef9097ee09a57355e0a39272c7e15654d7caa0da5c49140546` |
| `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| `tools/_s2jr_private_frame0_png_verifier.py` | `421808513d73eb9874907871fe06bb704778cba5fce52410749fefd19398bc63` |

Der PNG-Verifikator war vor dem Lauf statisch syntax- und AST-geprueft. Er
enthaelt keine Rezeptor-, Audio-, Memory-, Kontext- oder Feldaufrufe.

## Browserversuch

Gebunden waren:

- ein neuer Browser-Tab im Codex In-app Browser;
- expliziter Viewport `1920 x 1080`;
- erwarteter Device Scale Factor `1`;
- direkte Erzeugung von Frame 0 mit `ImageData.putImageData`;
- hoechstens ein vollstaendiger Viewport-Screenshot;
- HTML-Digest
  `f87d9d333ed234c5d75b4c5bef5133b31f8c5f924f9b4929f8cb983a959e04e6`;
- Steuergrenze `browser-plugin-26.820.60940/tab.playwright`.

Der Browserpfad meldete vor einem vollstaendigen Geometriebeleg und vor dem
Screenshot:

```text
CAPTURE_FAILED
UNCLASSIFIED_BROWSER_FAILURE
```

Der lokale Browserbeleg weist `screenshot_count = 0` aus. Es wurde keine PNG-
Datei erzeugt. Browser-User-Agent, konkrete Rendereridentitaet und reale
PNG-Decoderidentitaet konnten deshalb nicht vollstaendig abgenommen werden.

Der Fehler ist nicht enger auf Viewportsetzung, Taberzeugung, Navigation oder
Geometrieabfrage lokalisierbar. Eine nachtraegliche Zuordnung waere nicht
belegt.

## Nicht ausgefuehrte Pruefungen

Mangels PNG wurden nicht ausgefuehrt:

- PNG-Signatur-, IHDR-, Dimensions- und Kanalpruefung;
- Alpha-Pruefung oder Alphaentfernung;
- BGR/RGB-Kanalpermutation;
- RGB8-Payloaddigestbildung;
- Bytevergleich mit S2-JO-Frame 0.

Der vorbereitete private PNG-Verifikator wurde nicht aufgerufen. Dadurch
existiert kein synthetisch erzeugter `PAYLOADS_DIFFER`-Befund fuer eine
nicht vorhandene Nutzlast.

## Maschinenlesbare Belege

| Datei | SHA-256 |
| --- | --- |
| `browser-audit.json` | `1f4864fa41c19483b5bc631886ddbf0803acd32baf0264ba204a75949dfd0ccc` |
| `result.json` | `935d69c80b1d536e72d403717409ae6e581eb9ef29971c7a11d325f50d73df7a` |
| `terminal.json` | `7c6aa1fe418559c067975934819a5a0ea3086614400eadd07056e5e3602996c9` |

Der im Repository abgelegte Browserbeleg ist bytegleich mit dem lokalen
Original unter:

`C:/Users/TV/AppData/Local/MCM_FIELD_ORGANISM/s2jr/s2jr-frame0-browser-preflight-20260902-01/browser-audit.json`

## Funktionsgrenze

Maschinenlesbar gebunden sind:

- Screenshots: `0`;
- PNG-Decoderaufrufe: `0`;
- Rezeptoraufrufe: `0`;
- Audioaufrufe: `0`;
- Memoryaufrufe: `0`;
- Kontextaufrufe: `0`;
- Feldaufrufe: `0`.

Die kleine private Sechs-Frame-Adapterimplementierung und jede
Rezeptorqualifikation bleiben gesperrt. Dieser Befund ist ein technischer
Capture-Abbruch und keine Aussage ueber Browser-/Simulationspixel oder die
visuelle Quellenunabhaengigkeit.
