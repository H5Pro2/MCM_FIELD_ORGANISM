# S2-JO - Simulationreferenz und Qualifikation

## Status

`S2JO_SIMULATION_REFERENCE_VALID`

Datum: `2026-09-01`

S2-JO schliesst ausschliesslich `JN-B01` und `JN-B04` fuer die private
Simulationreferenz. `JN-B02` und `JN-B03` bleiben offen.

## Implementierter Umfang

- unveraenderliche `CanonicalVisualFrameV1`-Eingaenge;
- unveraenderliche `CanonicalPCMAudioHopV1`-Eingaenge;
- getrennte `SourceAuditProvenanceV1`;
- quellenneutraler funktionaler AV-Episodendigest;
- quellenneutraler reduzierter Rezeptorsequenzdigest;
- private gestreamte Simulation der gebundenen 200-ms-Episode;
- unveraenderte Default-Live-Rezeptoren mit 288 visuellen und 48 auditiven
  Werten;
- persistente Receipts und Ergebnisse ohne Pixel- oder PCM-Bytes.

Implementierungsquelle:

`tools/_s2jo_private_canonical_av_boundary.py`

SHA-256:

`50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71`

Testquelle:

`tests/test_s2jo_private_canonical_av_boundary.py`

SHA-256:

`c14bd814dfcfa65cfba8e7a54df90cd05ac69f626fa2272280334acb4d005a07`

## Einmalige fokussierte Ausfuehrung

Aufruf:

```text
.venv\Scripts\python.exe -m unittest tests.test_s2jo_private_canonical_av_boundary
```

Ergebnis:

```text
............
----------------------------------------------------------------------
Ran 12 tests in 2.294s

OK
```

Exit-Code: `0`

## Bestaetigte Grenzen

- exakt sechs RGB8-Frames und 20 PCM_F32LE-Hops;
- sechs visuelle und elf auditive reduzierte Zustaende;
- 37.363.200 verarbeitete Rohpayloadbytes je Simulationarm;
- hoechstens ein kanonisches Payloadobjekt gleichzeitig im Reduktionspfad;
- exakt 55 gezaehlte Armoperationen;
- unterschiedliche gueltige Auditprovenienz veraendert weder funktionalen
  Episodendigest noch Rezeptorzustaende oder reduzierten Sequenzdigest;
- ein veraendertes Pixel und ein veraenderter Samplewert bleiben sowohl im
  Payloaddigest als auch im betroffenen Rezeptorzustand unterscheidbar;
- Form-, PCM-, Reihenfolge-, Zeit-, Inventar- und Metadatenkopplungsfehler
  stoppen fail-closed;
- Resultate, Receipts und reduzierte Zustaende enthalten keine Rohpayloads;
- das private Modul importiert ausschliesslich vorhandene visuelle und
  auditive Rezeptorbausteine, keine Memory-, Kontext-, PPB-, TSPM- oder
  Feldfunktion.

## Offene Grenzen

`JN-B02 - DIGITAL_SOURCE_COVERAGE_INCOMPLETE`

Desktopaufnahme und Systemaudio sind nicht implementiert.

`JN-B03 - EXISTING_ADAPTER_PROFILES_OR_TRANSFORMS_DIFFER`

Browser-, Video- und weitere Adapter sind nicht an die kanonische Grenze
angebunden. Synthetische Quellnamen ersetzen diese fehlenden Adapter nicht.

Nicht freigegeben oder behauptet sind Browser-Viewport, Desktop, Video,
Systemaudio, Kamera, Mikrofon, ein Quellenvergleich sowie Memoryskalierung auf
336 Werte. Der naechste Quellenvergleich benoetigt genau eine zweite reale
digitale Quelle unter separater Freigabe.
