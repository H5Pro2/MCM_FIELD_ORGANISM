# S2-MQ: Vorversiegelter Korpusvergleich - Befund

Status: `NOT_EVALUABLE`  
Datum: 2026-09-05

## Vorversiegelung

Die Vorversiegelung `s2mq-motion-corpus-preseal-20260905-01` wurde genau einmal vor jeder Pixelanalyse abgeschlossen.

- Vertrag SHA-256: `b8b000ed91cc8e07619d41552704a09736e7bed9e77598c630befc2acfca2fc0`
- Vorversiegelungsquelle SHA-256: `c583406f344dfd18dbee45b1dca0dbf76ac2adcca311b765a3604d1b210bc1a1`
- Quellenplandigest: `e8daece3fdf9bf57c3ee7bceaff6aede0d23941a21f3843910360cc6eaf4036d`
- Ausfuehrungsplandigest: `9dc6cd13a3003de9b810e13725585568e780c7183e2afa55ee55ae45c2b4a27b`
- Evaluationsplandigest: `9213c4faa1ee5133e25d79483c2b38116c1b3ecbd28d2d8df8b09922daa8274c`
- gebundene Frames/Paare: `16/8`
- Pixelanalyse-, Rezeptor-, Pose-/Form-, S2-MP-, Memory-, Kontext- und Feldaufrufe: jeweils `0`

Quellen-, rollenfreie Ausfuehrungs- und getrennte Evaluationswurzel liegen unter `reports/s2mq/preseal-s2mq-motion-corpus-preseal-20260905-01/`.

## Startabweisung

Der erste Startversuch `s2mq-feature-sparse-corpus-comparison-20260905-01` wurde vor Quellenmaterialisierung und Paarmessung vom vorhandenen S2-MP-Runtime-Gate abgewiesen. Das Shell-`python` lieferte nicht die gebundene NumPy-Version. Das Ausgabeverzeichnis blieb leer. Dieser Versuch ist `START_REJECTED` und besitzt keinen Funktionsbefund.

Danach wurde der bereits projektgebundene Interpreter `.venv/Scripts/python.exe` statisch bestaetigt:

- CPython `3.14.4`
- NumPy `2.5.1`
- OpenCV `4.13.0`

## Technischer Abbruch

Der neue Lauf `s2mq-feature-sparse-corpus-comparison-20260905-02` verwendete den qualifizierten Interpreter und oeffnete den versiegelten Korpus genau einmal. Er brach innerhalb des unveraenderten S2-MP-Pfads ab:

```text
TypeError: memoryview: cannot cast view with zeros in shape or strides
```

Die Abbruchstelle ist `_array_digest(valid_forward, "<f4")` in `tools/_s2mp_private_feature_sparse_correspondence.py`. Mindestens ein Paar erzeugte Kandidatenpunkte, aber null geometrisch gueltige Tracks. Fuer diesen regulaeren Wahrnehmungsfall besitzt `valid_forward` die Form `(0, 2)`. Die bestehende Digestfunktion versucht diese leere mehrdimensionale Sicht dennoch mittels `memoryview(...).cast("B")` zu konvertieren.

S2-MP blieb bytegleich bei SHA-256 `4e0e2b7fb19118a958469ee550d0cd90dc5c557b16529ff5c9fa8efa015dccf9`. Es wurde unter S2-MQ weder korrigiert noch gelockert.

## Abschluss

- atomarer Ergebnisbeleg: nicht entstanden;
- read-only Ergebnisverifikation: nicht aufgerufen;
- fachliche Ordinalauswertung: nicht zulaessig;
- Memory-, Kontext- und Feldaufrufe: `0`;
- Gate nach dem Abbruch: `False`;
- Retry: keiner.

S2-MQ sagt damit nichts darueber aus, ob zeitliche Korrespondenz Fortsetzung, Formwechsel, Verdeckung und Szenensprung besser als die statischen Baselines trennt. Der enge offene Blocker ist die nicht qualifizierte S2-MP-Ausgabeform `candidate_count > 0` bei `valid_track_count == 0`. Eine spaetere Korrektur muss ausschliesslich die kanonische Digestierung leerer gueltiger Komponenten behandeln und neutral qualifizieren, bevor ein neuer Korpuslauf unter neuer ID erwogen wird.
