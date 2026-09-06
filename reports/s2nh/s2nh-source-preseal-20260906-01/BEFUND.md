# S2-NH: einmalige rezeptorfreie Vorversiegelung

Status: **S2NH_SOURCES_PRESEALED**.
Einmalige unabhaengige read-only Bindungspruefung:
**S2NH_PRESEAL_BINDINGS_VERIFIED**.
Lauf-ID: `s2nh-source-preseal-20260906-01`.

Die vorgeschaltete einmalige neutrale Qualifikation bestand 18/18. Erst
danach wurde genau dieser eine neue Vorversiegelungsaufruf ausgefuehrt:

```text
C:/Python314/python.exe -B -m reports.s2nh.preseal_once
```

Arbeitsverzeichnis: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.
Exit-Code `0`. Keine historische Hauptfunktion, kein Retry, keine
Quellenkorrektur oder nachgemessene Parameterauswahl.

## Gebundener Umfang

| Inhalt | Anzahl |
| --- | ---: |
| PCM-Rezepte, jeweils 4800 Samples | 15 |
| Vollstaendige 1920x1080-RGB8-Grundrezepte | 13 |
| Getrennte visuelle Cuequellen | 4 |
| Erzeugte Quellen insgesamt | 32 |
| Literale Ereignisse, noch nicht verarbeitet | 28 |
| Spaetere Formationen / Audiohinweise / Visualhinweise je Arm | 20 / 4 / 4 |

Erzeugt wurden 72.000 PCM-Samples bzw. 288.000 kanonische PCM-Bytes und
105.753.600 RGB-Bytes ueber alle 17 einzeln erzeugten Frames. Dies sind
Gesamtmengen, kein gleichzeitig gehaltener Speicher.

Die Schleife erzeugte und digestierte genau einen Payload je Quellenbindung.
Der einzelne RGB-Frame wird direkt aus dem kleinen 288-Byte-Raster befuellt;
kein voller Zwischenframe. Die Hashbildung verwendet eine kurzlebige
memoryview ohne vollstaendige tobytes-Kopie. View und Payload werden vor
der naechsten Quelle freigegeben. Maximal ein PCM-Fenster von 19.200 Byte
beziehungsweise ein RGB-Frame von 6.220.800 Byte gleichzeitig. Keine
Prozess-Peakmessung behauptet. Rohpayloads wurden nicht gespeichert.

## Plan- und Quellenbindung

`execution-plan.json` enthaelt alle konkreten Frequenzen, Phasen, Seeds,
Rundungsparameter, Quellen-/Rezept-/Payload-Digests, 28 Ereignisse und deren
native sowie gemeinsame Zeitbindungen. Die Quellenfolge einschliesslich
der eingeschobenen Hinweise bleibt exakt beim bestehenden S2-NH-Vertrag.

Faktor und Rechenfolge bleiben fest bei der vereinbarten Binary32-Bindung
von `0.989912331104279`; p13 enthaelt den prospektiven Faktor 0.9, p14 die
festen +7 Hz. Keine weitere Skalierung, Normalisierung oder Clipping.
Die Exaktkopie `nh-vcue-e04` / `nh-vcue-e24` hat denselben Payloadhash,
aber getrennte Quellen-, Ereignis- und Zeitbindungen. Sie wurde zweimal
aus ihrem jeweiligen Rezept erzeugt, nicht dedupliziert. Weitere
identische PCM-/RGB-Payloads wurden nicht festgestellt. Kollisionen wurden
nur dokumentiert, nicht als Auswahlgate benutzt.

Zielrollen, Sollsupport, Variantenkategorien und Erhaltungsbewertung stehen
ausschliesslich in `evaluation-plan.json`. Die Ausfuehrungswurzel enthaelt
keine Solltreffer oder Erfolgsfilter. Die Evaluationswurzel verweist auf den
Ausfuehrungsdigest; `seal.json` bindet beide Wurzeln und deren Dateihashes.

Generator-, Quellen-, Dokument- und Komponentendateien blieben zwischen
Vorbindung und Abschluss unveraendert. Historische NG/NF-Belege und
qualifizierte Komponenten wurden nur gelesen. Die Profilparameter und
vorhandenen Profil-/Konfigurationsdigests wurden aus statischen Bindungen
und dem bestehenden NG-Konfigurationsbeleg uebernommen, ohne dessen
Zustaende auszufuehren oder als neue Wahrnehmungsdaten einzusetzen.

## Lokale technische Identitaet

- CPython 3.14.4, 64 Bit, Build `tags/v3.14.4:23116f9`,
  `Apr 7 2026 14:10:54`, MSC v.1944 AMD64.
- Interpreter `C:/Python314/python.exe`, SHA-256
  `7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a`.
- math: `__spec__.origin == "built-in"` und Built-in-Mitgliedschaft bestaetigt;
  keine erfundene Moduldatei oder deren Hash.
- NumPy 2.4.4; geladene `_multiarray_umath.cp314-win_amd64.pyd` einschliesslich
  absolutem Pfad und SHA-256 in der Ausfuehrungswurzel gebunden.
- Default-Live: 48000 Hz, Fenster 4800, Hop 480, 48 Baender, 50..18000 Hz;
  Video 1920x1080, 12x8 RGB-Zellen, 30 Hz, 288 Werte.
- Unveraenderter Koordinatorkonfigurationsdigest:
  `72c74a8298d98013ef7d1552f764e46c4df1935703f0e4188f11a6eca0479beb`.

## Einmalige lesende Pruefung

Der separate Verifikator pruefte alle Quellenformen, Rezept- und
Payloaddigestbindungen, die vollstaendige Ereignisfolge mit eigenen
Zeitformeln, getrennte Wurzeln, erwartete Exaktkopien, Grenzen,
Interpreter-/Profilbindungen sowie Siegel- und Dateidigests.
Keine erneute Payloadgenerierung, Rezeptoranalyse oder Distanzberechnung.
Vor-/Nachdateihashes der vier gelesenen Artefakte sind identisch.
`verification-reservation.json` bindet genau einen Pruefaufruf.

| Bindung | Digest |
| --- | --- |
| Ausfuehrungswurzel | 47ac97a175e37d45f576479ba82c906e4b36c47ae3708fca7d8e6ced885298a4 |
| Evaluationswurzel | 03bb9a881d5f03935104788f2a98083d2790c8dc0565c5a9664c5d5ba13e8cb2 |
| Siegel | c0acb80b6ab88436ee0daaf007cc2abd46ce4409d9a40ed8fdc2c6635bbb2b2b |
| execution-plan.json Datei-SHA-256 | 776ddf73bcbd9f61ad64612bc7bfb0ddeaebb6c233026e9831a2bfdd5a607826 |
| evaluation-plan.json Datei-SHA-256 | a2b07880702f33bbff6129fdfe11b96897503cef52f7e46f0c9d52b415c9a531 |

Dateigroessen: Ausfuehrungswurzel 47.822 Byte, Evaluationswurzel 1.557 Byte,
Vorbindung 40.023 Byte, Siegel 25.740 Byte, Verifikation 1.226 Byte.
Die gebundenen Grenzen wurden nicht erhoeht. Die spaeteren Runtimebudgets
sind Metadaten, keine bereits ausgefuehrten Operationen.

## Nichtnachweis und Abschluss

Rezeptor-, Distanz-, Regelvergleichs-, Memory-, Feld-, Kontext- und
Runtimeaufrufe: jeweils **0**. Hauptgate durchgehend **False**.
Keine Rezeptornormalform, Stabilisierung, Selektivitaet, Erhaltung oder
Generalisation an den neuen Quellen behauptet. Jede spaetere technisch
gueltige negative Geometrie bleibt ein regulaerer Befund; D=0 bleibt
Erhaltung nicht geprueft. Kein weiterer Seed oder Ersatzkorpus.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser
Vorversiegelung und der getrennten Freigabe der naechsten begrenzten
Materialisierungs-/Runtime-Anbindung auf genau diesen Quellen weiter.
