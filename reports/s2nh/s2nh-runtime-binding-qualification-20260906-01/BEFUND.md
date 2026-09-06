# S2-NH: Materialisierungs- und Runtime-Anbindung neutral qualifiziert

Qualifikations-ID: `s2nh-runtime-binding-qualification-20260906-01`.
Status: `S2NH_RUNTIME_BINDING_QUALIFIED`.
Genau ein neutraler Testaufruf: **20/20**, Exit-Code **0**, `OK`.
Kein Retry, keine NH-Payloadmaterialisierung, kein NH-Hauptvergleich.

## Gebundener Aufruf und Belege

Aus dem Workspace:

```text
C:/Python314/python.exe -B -m reports.s2nh.qualify_runtime_once
```

Der Aufrufer startete genau einmal:

```text
C:/Python314/python.exe -B -m unittest tests.test_s2nh_private_runtime_binding -v
```

Testinventar und 104 Datei-/Quellenbindungen wurden vorab in
`preregistration.json` gespeichert. Alle Vor-/Nachhashes stimmen ueberein.
`result.json` bindet Exit-Code, Inventar und unveraenderte Protokolle.

- Ergebnisdigest:
  `6d0df753db461ead1caf664a9da6078ee9f3f409e09b43466e3e5ce6dc619928`.
- Ergebnisdatei SHA-256:
  `bd966c1672127cce85e48c72a7b0c0ca520be1140918bcb8555b85ec49468993`.
- Testprotokoll SHA-256:
  `31305864e23d63932fca7b8e7b386a1c4e829af8a91b0d4e32945c9efcb228fc`.

## Tatsaechlich ausgefuehrter neutraler Umfang

Die sechs neutralen Ereignisse waren AV, Audiohinweis, Videohinweis, AV,
Audiohinweis, Videohinweis. Einmal gemeinsam materialisiert, anschliessend
dasselbe unveraenderliche Ereignistupel in zwei getrennten Runtimearmen:

| Groesse | Beobachtet |
| --- | ---: |
| Audiofenster | 4 |
| Audiohops im fortgefuehrten HearingPath | 40 |
| Rollende Audioabschluesse | 31 |
| Verwendete Audio-Fensterendpunkte | 4 |
| Visuelle Rezeptoranalysen | 4 |
| Runtimeereignisse gesamt | 12 |
| Neutrale Memoryformationen gesamt | 4 |
| Feldkontakte gesamt | 2688 |
| Scanbelege inklusive Direktbaselines | 16 |
| Vergleichswerte der Verifikationsreserve | 2464 |
| Kanonischer neutraler Gesamtbeleg | 330816 Byte |
| Getrennte neutrale Auswertung | 38715 Byte |

Die neutrale Quellenbindung und Materialisierung erzeugten insgesamt fuenf
PCM-Payloads und sieben RGB-Frames, nur aus `neutral-`-Seeds. Die Payloads
wurden nicht gespeichert. Die versiegelten NH-Quellen wurden ausschliesslich
als Planmetadaten und Hashbindungen gelesen. `nh_payloads = main_calls = 0`.

Der reale NH-Umfang bleibt unveraendert auf 24 Audiofenster/240 Hops mit
231 rollenden Audioabschluessen und 24 visuellen Analysen begrenzt. Die
24 ausgewaehlten Audioendpunkte sind nicht mit 24 FFT-Aufrufen gleichzusetzen.
Dieser Umfang wurde hier nicht ausgefuehrt.

## Bestaetigte technische Eigenschaften

- Audiozeit schreitet ueber reine Videoereignisse hinweg ohne Neustart fort.
  Der zweite neutrale AV-Block traegt Samplefenster 9600..14400 und
  Snapshotindex 20. Audio-, Video- und gemeinsame Feldzeit bleiben getrennt.
- Quellen-/Wertedigests der auditiven Hinweise und Quelldigests der bereits
  okkludierten visuellen Hinweise stimmen mit den gemeinsamen Materialisaten
  ueberein. Die explizite NH-Felduhr wird verwendet.
- Die vorhandene NG-Komposition prueft eigene Runtime-/Feld-/Memoryinstanzen
  und armweise gleiche Zustaende. Beide Regelausgaben entsprechen ihren
  Direktbaselines. Beide Runtimes schliessen nach sechs Ereignissen.
- Fruehe Hinweise lassen Memory unveraendert. Die zweite Formation folgt
  auf denselben Zustand und erhoeht dessen Generation auf 2, ohne Neustart.
- Gueltige Enthaltung und ausbleibender Sollsupport bleiben technisch
  verifizierbar. Die bewusst ausbleibende neutrale Hypothese wird getrennt
  als nicht richtiger Abruf ausgewertet, nicht als Infrastrukturfehler.
- N/D/R/L, Gewinne, Verluste und verworfene Zielkandidaten bleiben getrennt.
  Ein auditiver Nullnenner wird nicht mit visuellen Treffern aufgefuellt.
- PPB-Nachverfolgung unterscheidet CREATED, MATCHED, Supportsaettigung,
  gemischte Herkunft, REPLACED und NO_UPDATE. Ersetzung entfernt die alte
  Generationszuordnung in der reinen Auswertung.
- Fehlende/vertauschte Belege, manipulierte Zeiten und Digests, falsche
  Zaehlung, Schreibkonflikt sowie Groessenueberschreitung werden abgewiesen.
  Ein technischer Fehlerbeleg bleibt lesend pruefbar; kein erneuter Aufruf.

## Unveraenderte Quellhashes

| Datei | SHA-256 vor und nach dem einzigen Testaufruf |
| --- | --- |
| `tools/_s2nh_private_runtime_binding.py` | `60150be1ee5bab76105891ece3b47577d49e8b9ee0cd3e1289667529503ab397` |
| `tools/_s2nh_private_runtime_verification.py` | `81c72a321082fa73a36f399d79ae07a10b4b82805977a30ddf6cd6fc68c60084` |
| `tests/test_s2nh_private_runtime_binding.py` | `a23a0f646336a4dd07e87c898c00702eb86f7857b1e7d3de6f4a50e8e3b317a6` |
| `reports/s2nh/qualify_runtime_once.py` | `f7fe88020c96336e5ff445b868eaed1cae0c430bf765df0a1271735861b6f899` |
| `reports/s2nh/RUNTIME_ANBINDUNG.md` | `bf1611b3e3df95a776a19d4829501be0356e96b63a3fd73330bbe3b5b2b81219` |

Die Quellenversiegelung, historische Komponenten, Regeln, Schwellen,
Defaultadapter und Memorykerne wurden nicht geaendert. Hauptgates bleiben
False. Keine Aussage ueber NH-Stabilisierung, Erhaltung, Gewinne oder
Verluste folgt aus dieser neutralen Qualifikation.

RUECKMELDUNG ERFORDERLICH: Der reale 28-Ereignis-NH-Vergleich benoetigt
weiterhin eine separate ausdrueckliche Freigabe.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses
Qualifikationsbefunds und der Entscheidung ueber den einmaligen,
unveraenderten S2-NH-Runtimevergleich weiter.
