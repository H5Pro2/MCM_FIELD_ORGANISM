# S2-ND: Einmalige Rezeptormaterialisierung

Lauf-ID: `s2nd-receptor-materialization-20260906-01`.

## Technischer Abschluss

Genau ein Aufruf aus dem Workspace-Root:

```text
python -m tools._s2nd_private_receptor_materialization
```

Exit-Code `0`, Status `RECEPTOR_MATERIALIZATION_COMPLETE`.
Kein Retry, keine Quellen- oder Parameterkorrektur, kein technischer Abbruch.

| Umfang | Ergebnis |
| --- | ---: |
| Regenerierte versiegelte PCM-Quellen | 18/18 |
| Payloadhash vor jeweiliger Analyse bestaetigt | 18/18 |
| Direkte analyze-Aufrufe, versucht / zurueckgekehrt / vollstaendig | 18 / 18 / 18 |
| Rezeptorzustaende / Werte | 18 / 864 |
| Ergebnisdatei | 48.162 Bytes |
| Persistierte PCM-Payloads | 0 |
| Distanzen / Regelvergleiche | 0 / 0 |
| Memory-, Kontext-, Feld-, Runtimeaufrufe | jeweils 0 |

Alle Quellen stammen unveraendert aus der erfolgreichen S2-ND-Vorversiegelung
`s2nd-source-panel-preseal-20260906-02`. Die eigene private Aufrufbindung
verwendet deren gehashten Generator, nicht die historisch korpusspezifischen
S2-NC-Materialisierungshelfer. Diese bleiben unveraendert.

Vor PCM-Erzeugung wurden Siegel, Quellen-/Dokumenthashes, Generator,
Interpreterdatei/-hash und Python-Build geprueft. Die qualifizierte
Built-in-Herkunft von `math` stimmt mit dem Siegel ueberein.
Die getrennte Evaluationswurzel wurde nur als Datei gehasht, nicht geladen
oder zur Materialisierung verwendet.

Je Quelle wurde ein einzelner PCM-Payload erzeugt und vor `analyze` auf
Laenge, SHA-256, Float32-Form und gueltige Samples geprueft. Die NumPy-Sicht
und der Payload wurden nach dem Aufruf freigegeben. Die unveraenderten
internen Arbeitsarrays des Rezeptors sind keine weitere gespeicherte Quelle.
Rohbytes erscheinen nicht im Ergebnis.

## Profil und Wertebindung

Unveraendertes Profil: Mono, 48.000 Hz, Fenster 4.800, Hop 480,
50..18.000 Hz, 48 Baender. Ein Rezeptor wurde initialisiert; anschliessend
erfolgte je Quelle genau ein direkter `LogSpectralReceptor.analyze`-Aufruf.
Keine rollende Audiopipeline und keine erneute Analyse der Exaktkopien zur
Kontrolle ausserhalb ihrer eigenen gebundenen Quellenordinalzahl.

Alle Ausgaben bestehen aus 48 endlichen Binary64-Werten innerhalb der
gebundenen Normalform `0..1`. Das belegt technische Verwendbarkeit, keine
Anwendbarkeit, Selektivitaet oder Erhaltung bekannter Treffer.

Jeder Zustand bindet Quellen-ID und Ordinalzahl, Rezept-/PCM-Digest,
deklarierte Quellenfenster, Ausfuehrungs- und Profildigest, alle Werte,
kanonischen Wertedigest, F64LE-Bytehash und eigenen Zustandsdigest.
Die Quelle traegt `s2nd-source-sample-clock` und Fenster
`[(n-1)*4800, n*4800)`, n=1..18. Diese deklarierte Quellzeit wird nicht
als vom Rezeptor gemessener Zeitstempel ausgegeben.

Aktive Laufzeit: CPython 3.14.4, NumPy 2.4.4. Profilkonfiguration,
48 Kanal-IDs, Filterbandbeschreibungen, Rezeptorquellhash und NumPy-
Modulidentitaet stehen in `result.json`.

## Einmalige unabhaengige Belegpruefung

Nach vollstaendiger Ergebnisablage genau ein separater Prozess:

```text
python -m reports.s2nd.verify_materialization_once
```

Exit-Code `0`, Status `MATERIALIZATION_EVIDENCE_VALID`.
Die Pruefung importiert ausschliesslich Standardbibliothek, weder Generator
noch Rezeptor. Sie prueft Dateihashes, Plan-/Siegelbindung, Profilbeleg,
Quellen- und Zustandsreihenfolge, Werteformen, Zustands-/Wertedigests,
F64LE-Hashes, Zaehler und unveraenderten Ergebnisinhalt.
Keine PCM-Regeneration, Rezeptorwiederholung oder Distanzberechnung.

Alle 13 gebundenen Datei-Vor-/Nachhashes stimmen ueberein. Der Ergebnisbeleg
blieb bei der Pruefung bytegleich. Der Verifikator bestaetigt die technische
Belegintegritaet, nicht eine unabhaengig erneut berechnete Rezeptorfunktion.

## Zentrale Digests und Dateien

Ausfuehrungsplandigest:
`e29682fe7606f533c068b3a57c5f986a18934cea2b7c0ca977c0c538a6052f22`.

Siegeldigest:
`333f15e8ba0a69e50c12481503f089a348a367eec0c8bb2489cc9f184393b61a`.

Aufrufplan-Dateihash:
`5c5332b6ee631fb5b10a0d5b9917730f986d3e9774b24f474447ac5d0a12b756`.

Profildigest einschliesslich Kanal-/Band- und Methodenbindung:
`3d9c7d8ca7a400c8bdfeb35cb8395015a5f48979614d303cd1dbab1972f3a855`.

Ergebnisdigest:
`705f34e547916057e4aefbc52fcf2a7710958b013d4a9501a6ad628194f243d6`.

Ergebnisdatei-SHA-256:
`05981df7575b2833af35f62b8e194a33851ed855fe134fc39fc79a85aa1729f0`.

Verifikationsdigest:
`b794ab2a702ea21515b8d13ebbc9c88de5057eecafadbf95cda0ccecfb0dbcec`.

`../s2nd-receptor-materialization-call-plan.json` bindet beide Kommandos und
Quelldateihashes vor der Ausfuehrung. `call-result.json` und
`verification-call-result.json` erhalten die jeweiligen Originalausgaben
und Exit-Codes. `result.json` enthaelt alle 18 Zustaende, `verification.json`
den einmaligen lesenden Pruefbeleg. Die exklusive Ergebnisverzeichnis-
beziehungsweise Pruefreservierung verhindert Wiederverwendung derselben ID.

## Grenze und Rueckmeldung

Keine Tests, Treffermengen, Regeln, Distanzen oder D/R/L-Erhaltungsbewertung
wurden ausgefuehrt. Keine Normalisierung, Skalierung, Quelle-Hannung,
Clipping, Quellenauswahl oder Systemintegration. Quellen, Vorversiegelung,
historischer Fehlbeleg und S2-NC bleiben unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses
Materialisierungsbefunds und der begrenzten S2-ND-Anbindung an den vorhandenen
Zwei-Regel-Vergleich weiter. Dessen Ausfuehrung bleibt separat freizugeben;
ein Erhaltungs- oder Verlustbefund liegt noch nicht vor.
