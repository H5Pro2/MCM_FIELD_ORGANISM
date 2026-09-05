# S2-MQ: Vorversiegelter Korpusvergleich, Lauf 03

Status: `S2MQ_MIXED_OR_NO_TEMPORAL_ADVANTAGE`

Der Lauf `s2mq-feature-sparse-corpus-comparison-20260905-03` verwendete
unveraendert den unter `s2mq-motion-corpus-preseal-20260905-01`
vorversiegelten Korpus.

## Technischer Abschluss

- Paare: `8/8` verarbeitet;
- terminaler Zustand: `RECORDING_COMPLETE`;
- read-only Verifikation: genau einmal, `OK`;
- Ergebnis-SHA-256 vor/nach Verifikation:
  `b16b85ed71d9572315e0be664545712c9647c14af3648b20abe0f6199733be7a`;
- Ergebnisgroesse: `44.922` Byte;
- Gate nach dem Lauf: `False`;
- Memory-, Kontext- und Feldaufrufe: jeweils `0`;
- Retry oder Parameterwechsel: keiner.

Quellhashes vor und nach dem Lauf waren identisch:

| Rolle | SHA-256 |
| --- | --- |
| S2-MP | `a8d2d6d66aa08b173a3a848ef2b5f5488694ecdabd9d2f78c13a3211ee500955` |
| S2-MQ-Runner | `1ec87e395da89b26449f9ccba4676406c27a382199eeb4b69e44661bd5627ab5` |
| S2-MQ-Vorversiegelung | `c583406f344dfd18dbee45b1dca0dbf76ac2adcca311b765a3604d1b210bc1a1` |

## Paarbefunde

| Fall | Stratum | Kandidaten | gueltige Tracks/Zellen | Status | Zyklusmittel | RGB-Residuenmittel |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| Fortsetzung | strukturreich | 183 | 173/12 | verfuegbar | 48,143987 | 0,048702 |
| Fortsetzung | kantenarm | 4 | 4/4 | unzureichend | - | - |
| Formwechsel | strukturreich | 145 | 99/9 | verfuegbar | 51,916985 | 0,183412 |
| Formwechsel | kantenarm | 4 | 4/4 | unzureichend | - | - |
| Teilverdeckung | strukturreich | 108 | 100/7 | verfuegbar | 102,211908 | 0,126054 |
| Teilverdeckung | kantenarm | 4 | 4/4 | unzureichend | - | - |
| Szenensprung | strukturreich | 185 | 0/0 | unzureichend | - | - |
| Szenensprung | kantenarm | 4 | 0/0 | unzureichend | - | - |

`INSUFFICIENT_MOTION_EVIDENCE` ist hier ein regulaerer Wahrnehmungsbefund.
Insbesondere wurden die zwei Nulltrackfaelle nach der qualifizierten
Digestkorrektur korrekt serialisiert.

## Ordinaler Vergleich

Die vorab gebundenen Beziehungen lauteten je Stratum:
`Fortsetzung < Formwechsel`, `Fortsetzung < Szenensprung` und
`Fortsetzung < Teilverdeckung`.

| Messgruppe | bestanden | anwendbar | gesamt |
| --- | ---: | ---: | ---: |
| S2-MP Zyklus + RGB-Residuum | 4 | 4 | 12 |
| direkte Pixel-L1 | 6 | 6 | 6 |
| Pose | 4 | 6 | 6 |
| Form | 1 | 6 | 6 |

Auf den strukturreichen Fortsetzungs-, Formwechsel- und
Teilverdeckungspaaren erfuellten Zyklus- und RGB-Residuum alle vier
auswertbaren Beziehungen. Fuer den strukturreichen Szenensprung sowie alle
kantenarmen Beziehungen enthielt sich S2-MP mangels ausreichender
Bewegungsevidenz.

Die direkte Pixelbaseline trennte alle sechs ordinalen Beziehungen. Damit
zeigt S2-MQ auf diesem Korpus keinen zusaetzlichen Trennnutzen der zeitlichen
Korrespondenz gegenueber den statischen Baselines. Gleichzeitig zeigt der
Lauf eine fachlich saubere Grenze: S2-MP liefert verwertbare Evidenz auf
strukturreichen Fortsetzungen und Veraenderungen, erfindet aber bei
strukturarmer oder nicht korrespondierender Eingabe keine Bewegung.

Es wird keine Objektidentitaet behauptet. Eine spaetere Bindung dieser
Evidenz an Rezeptor- oder Formationuebergaenge ist durch diesen gemischten
Befund nicht begruendet.
