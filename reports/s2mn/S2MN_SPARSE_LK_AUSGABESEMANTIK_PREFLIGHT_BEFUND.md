# S2-MN: Sparse-LK-Ausgabesemantik-Preflight

## Status

`S2MN_SPARSE_LK_PATH_AVAILABLE`

Der neutrale Preflight
`s2mn-sparse-lk-output-semantics-preflight-20260905-01` wurde genau einmal
ausgefuehrt und nicht wiederholt. Er endete mit Exit-Code `0`.

Dies ist ausschliesslich ein lokaler technischer Capability-Befund fuer den
gebundenen CPython-/OpenCV-/NumPy-Build. Es ist kein Bewegungs-,
Fortsetzungs-, Objektidentitaets-, Memory-, Kontext- oder Feldbefund. Kein
S2-MJ-Korpusframe wurde geoeffnet.

## Statischer Semantikbefund

Die OpenCV-`4.13.0`-Quelle initialisiert die vollstaendige Statusmaske, aber
nicht das vollstaendige optionale Fehlerarray. Bei mehreren Abbruchpfaden
wird ein Track ungueltig, ohne unter den gebundenen Flags `0` einen
semantisch verwendbaren Fehlerwert zu erhalten. Massgeblich sind die
Status-/Fehleranlage um Zeilen `1180...1194`, der Eigenwertabbruch um
`452...462` und die nur fuer gueltige Tracks ausgefuehrte Fehlerberechnung um
`642...674` in
[lkpyramid.cpp](https://raw.githubusercontent.com/opencv/opencv/refs/tags/4.13.0/modules/video/src/lkpyramid.cpp).

S2-MN bindet deshalb beide vollstaendigen `uint8`-Statusmasken, projiziert
danach aber Punkte, Fehler und Residuen ausschliesslich auf die streng nach
urspruenglichem Gitterindex geordneten gemeinsam gueltigen Tracks. Werte aus
ungueltigen Punkt- und Fehlerbereichen wurden weder digestiert noch
interpretiert.

Der alte S2-MM-Gesamtvergleich publizierte keine Einzelkomponenten. Deshalb
kann nachtraeglich nicht behauptet werden, welches konkrete ungueltige
Arrayelement damals abwich. Der Quellbefund und die nun bitgleiche gueltige
Projektion bestaetigen jedoch, dass die fruehere Gesamtarraybindung keine
zulaessige Reproduzierbarkeitsdefinition war.

## Einmaliger Aufruf

```text
.venv/Scripts/python.exe tools/_s2mm_private_sparse_lk_preflight.py \
  --output-root C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2mn \
  --contract-file-sha256 9f7fc56272ce7672348fb335f739e79cb7de1e80b79ac217cd12b1b6bd59ad72
```

Gebunden blieben:

- neutrale Vollformatfixture `1920 x 1080 RGB8`;
- festes `12 x 8 x 4 x 4`-Gitter mit `1.536` Punkten;
- Fenster `21 x 21`, Ebenen `0...3`, `30` Iterationen, Epsilon `0,01`;
- Flags `0`, `minEigThreshold=0,0001`;
- OpenCV-Einzelthreadbetrieb und deaktiviertes OpenCL;
- zweimal dieselbe vollstaendige Vorwaerts-/Rueckwaertsauswertung;
- keine Vorwaermung, Installation, Aktualisierung oder Ersatzbibliothek.

## Gueltige Ausgabe

Beide Auswertungen ergaben exakt `1.453` gemeinsam gueltige Tracks, also
`94,5963541667 %` des festen Gitters. Die Mindestgrenze von `1.152` wurde
erfuellt.

Alle zehn getrennt gebundenen Komponenten waren bitgleich:

| Komponente | SHA-256 beider Durchgaenge |
| --- | --- |
| Vorwaertsstatus, vollstaendig | `4fd49f9bdb750657b15e232707d8a60711b26d00a9875aa77faf67a6480fa8ea` |
| Rueckwaertsstatus, vollstaendig | `98be022148bef06fc82cae6f09c3630836f216e339bcd1abd8b373156aafb671` |
| gueltige Gitterindizes | `9a4e151eaca35b351f491dcef358a089971c175f68dbf6366f5870aad1e59687` |
| gueltige Vorwaertspunkte | `cee1afd25f1889c4225755558c2c9661506d0ad74f5a381399a22c3aff749249` |
| gueltige Rueckwaertspunkte | `5343fad31be5a124d19069dc4f4aaa086fea694960dd3ba82aa43b5c2b38ff5f` |
| gueltige Vorwaertsfehler | `eb3293fe04fbd79440c245d10b199917a5f2305244750ff854b38ccb991e7805` |
| gueltige Rueckwaertsfehler | `6682ef27af74f55264e59d703ae63a7a6f8bbb041d783fefdd7988d48b7baadf` |
| Verschiebung | `9bb1b4d867d7b31cff2cc3bf63882cc1fc6ec07e768f6e5c07ac062e2b45b897` |
| Zyklusresiduum | `6c856974db19a98f183fe7717ca85ca97d180ea5b4e11c7399d74fa3f9afe732` |
| RGB-Residuum | `753db924d29fcf47a769723134e0b59284f1ff5501fa98351a6c5162ea9dc270` |

Die komponentengenaue Vergleichsform weist fuer jede Rolle beide Digests und
`bit_identical=true` aus. Es wurde keine Toleranz, Rundung oder
Ergebnisumordnung verwendet.

## Peakmessung

Die unveraenderte Prozessmessbasis ergab:

| Rolle | Byte |
| --- | ---: |
| Working-Set-Anstieg waehrend beider Auswertungen | `55.103.488` |
| gebundene residente RGB-Eingaben | `12.441.600` |
| **gemessener Peak einschliesslich Eingaben** | **`67.545.088`** |
| Grenze | `134.217.728` |
| **Reserve** | **`66.672.640`** |

Die Grenze wurde strikt eingehalten. Anders als in S2-MM wurde die Messung
nach beiden LK-Auswertungen abgeschlossen und waere auch bei einer
Komponentenabweichung erhalten geblieben.

## Artefaktbindungen

| Artefakt | SHA-256 |
| --- | --- |
| S2-MN-Vertrag | `9f7fc56272ce7672348fb335f739e79cb7de1e80b79ac217cd12b1b6bd59ad72` |
| Preflightquelle | `5bdde67336196ccc5abad85a503289339957122f8c9a81e35a3697db20dd2b88` |
| `plan.json` | `ff19b4038347d1113babc7ea2d9b8e8c5a6e4bdf7fa02bddb9bda19bc50fce28` |
| `result.json` | `7c05df7f3d4475c842da1ba4c0e24ba3a2e4d9689cbf99ef5d7a6af1dfa8384a` |
| `terminal.json` | `e0f9aa990405bca2448141c162e3324b10097f454f04f60e994d235446f2c492` |
| Capability-Digest | `2b6092b0d8b4165de60931d3e82747ef014085f6c1c5ee6120425f8b87fc6500` |

Die maschinenlesbaren Belege liegen unter:

`reports/s2mn/s2mn-sparse-lk-output-semantics-preflight-20260905-01/`

## Grenzen und Entscheidung

- Korpusframes geoeffnet: `0`;
- Projektmodule importiert: `0`;
- Projektfunktionen aufgerufen: `0`;
- Memory-, Kontext- und Feldaufrufe: `0`;
- Installations-, Aktualisierungs- oder Fallbackaufrufe: `0`;
- Wiederholungen: `0`.

Sparse-LK ist fuer den exakt gebundenen lokalen Build, die feste
Vollformatfixture und die S2-MM-Parameter technisch reproduzierbar und unter
128 MiB verfuegbar. Erst ein neuer, separat vorversiegelter Korpuslauf darf
untersuchen, ob die Messung fachlich zwischen Fortsetzung, Wechsel,
Verdeckung und Szenensprung unterscheidet.
