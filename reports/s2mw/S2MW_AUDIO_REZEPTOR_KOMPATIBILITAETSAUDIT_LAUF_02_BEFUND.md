# S2-MW: Audio-Rezeptor-Kompatibilitaetsaudit Lauf 02

## Entscheidung

Der einmalige rezeptor-only Audit im neuen Ergebnisverzeichnis
`s2mw-audio-receptor-compatibility-20260906-02` wurde technisch vollstaendig
ausgefuehrt. Die numerische Entscheidung lautet:

```text
S2MT_AUDIO_RECEPTOR_COMPATIBILITY_MATERIALIZABLE
```

Ein einziger gemeinsam angewendeter, analytisch abgeleiteter
Eingangsskalierungsfaktor bringt alle 13 Rezeptorausgaben in die gebundene
Normalform und erhaelt die vollstaendige auditive S2-MT-Geometrie.

Der unveraenderte Auditcode serialisierte im Ergebnis jedoch weiterhin die
alte interne Audit-ID `s2mw-audio-receptor-compatibility-20260905-01`. Das
Ergebnis liegt zwar ausschliesslich im neu autorisierten Verzeichnis, bindet
dessen neue Identitaet aber nicht kanonisch im Record. Diese formale
ID-Belegluecke wird nicht nachtraeglich umgeschrieben. Der dritte
S2-MT-Transferlauf bleibt gesperrt.

## Vorbindungen

Vor dem Aufruf galten:

- neues Ergebnisziel war nicht vorhanden;
- `main` und `origin/main` standen auf
  `c72540ed2a3be75c01e6f1f79f148d0c629a2c74`;
- Auditwerkzeug:
  `afcbae958173a64742913694dccc3d6279bca25052c167a508e2bf9ccca6ce04`;
- unveraenderter Quellenplan:
  `ae808ad2a9f206bac45210f5f121e232e72da76b22e0b2bf7c599cc57e479f15`;
- unveraenderter Audiorezeptor:
  `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0`.

## Einmalaufruf

Genau ein Aufruf erfolgte aus dem Workspace-Root:

```text
python -m tools._s2mw_private_audio_receptor_compatibility_audit --output reports/s2mw/s2mw-audio-receptor-compatibility-20260906-02/result.json
```

Ergebnis:

- Exit-Code `0`;
- 13 Original-Rezeptoranalysen;
- genau ein abgeleiteter gemeinsamer Faktor;
- 13 skalierte Rezeptoranalysen;
- null Memory-, Feld-, Kontext- und Runtimeaufrufe;
- Record-Digest
  `5ecd4b166c7393a867ae2c52f2460a514e720ed30d20fd790984de82640ff674`;
- Datei-SHA-256
  `b1ca1ad9d11e29c6d5b547d166741f1afbf40fb3e8f240ea6eb07d3f4e7d87ef`.

Es gab keinen Retry, kein Clipping, keine Ausgangsnormierung und keine
Quellen-, Schwellen- oder Rezeptoraenderung.

## Originalausgaben

| Rezept | Frequenz Hz | Maximum | Maximalband | Baender ueber 1 |
|---|---:|---:|---:|---:|
| n00 | 80 | 0.644512459871498 | 4 | - |
| n01 | 180 | 0.754933471607638 | 10 | - |
| n02 | 400 | 0.625272346046791 | 17 | - |
| n03 | 760 | 0.749129854272035 | 22 | - |
| n04 | 920 | 0.789675883499748 | 23 | - |
| n05 | 1100 | 0.696915977960459 | 25 | - |
| n06 | 1300 | 1.01019038918499 | 26 | 26 |
| n07 | 1520 | 0.779411755000434 | 27 | - |
| n08 | 1760 | 0.605209895043258 | 28 | - |
| n09 | 2020 | 0.54110747371757 | 30 | - |
| n10 | 2300 | 0.579229487399018 | 31 | - |
| n11 | 2620 | 0.621386066618894 | 32 | - |
| n12 | 20 | 0.0000184588701012513 | 0 | - |

Nur `n06` verletzt die Kontakt-Normalform. Die Verletzung ist auf Band 26
begrenzt.

## Gemeinsamer Faktor

Der Faktor wurde einmalig und ohne Suche gebildet als:

```text
nextafter(float32(1 / 1.01019038918499), float32(0))
= 0.989912331104279
```

Die kanonischen kleinen-endian Binary32-Bytes lauten `e56a7d3f`. Jedes
urspruengliche Float32-PCM-Sample wurde genau einmal in Float32 mit diesem
Faktor multipliziert. Das globale Rezeptormaximum danach betraegt
`0.999999928438176`; kein skaliertes Rezept ueberschreitet `1`.

## Distanzgeometrie

Alle 78 unterschiedlichen Rezeptpaare wurden vor und nach der gemeinsamen
Skalierung als vollstaendige 48-Werte-L1-Mitteldistanz berechnet. Nach der
Skalierung gilt:

- Minimum: `0.0214866820546912`;
- Maximum: `0.0540575646378831`;
- Paare bei oder unter `0,02`: `0/78`;
- Paare bei oder unter `0,2`: `78/78`.

Die drei fuer die S2-MT-Slow-Trennung besonders gebundenen Paare lauten:

| Paar | Original | Skaliert |
|---|---:|---:|
| n00/n01 | 0.0546084362206944 | 0.0540575646378831 |
| n00/n02 | 0.0521595059989545 | 0.0516333385934270 |
| n01/n02 | 0.0470334490642848 | 0.0465589914763953 |

Auch alle 12 gebundenen 24-Band-Cue-Distanzen wurden neu berechnet:

- Cue `n00` trifft ausschliesslich `n00`;
- Cue `n01` trifft ausschliesslich `n01`;
- Cue `n02` trifft ausschliesslich `n02`;
- Cue `n12` trifft keinen der drei Trainingskandidaten.

Damit bleiben Normalform, auditive Slow-Trennung und die gebundenen
Cue-Treffermengen unter genau diesem einen gemeinsamen Faktor erhalten. Die
vollstaendigen 48-Werte-Ausgaben, 78 Paarbeziehungen und 12 Cue-Distanzen
sind im atomaren JSON-Beleg enthalten.

## Aussagegrenze

Der Befund behandelt ausschliesslich die Kompatibilitaet der versiegelten
PCM-Rezepte mit dem unveraenderten Audiorezeptor. Er ist kein Memory-, Feld-,
Kontext-, Runtime- oder Transferbefund. Wegen der nicht zur neuen
Verzeichnisidentitaet passenden internen Audit-ID ist die vollstaendige
Materialisierungsqualifikation noch nicht als abgeschlossen zu behandeln.
