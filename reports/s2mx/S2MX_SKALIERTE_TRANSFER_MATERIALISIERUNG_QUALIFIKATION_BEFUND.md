# S2-MX: Skalierte S2-MT-Materialisierungsqualifikation

## Entscheidung

Die Einmalqualifikation unter der ID
`s2mx-scaled-transfer-materialization-20260906-01` ist nicht bestanden.

Der neue prospektive Quellenplan konnte alle 28 Ereignisse vollstaendig
materialisieren. Der anschliessende separate `_geometry`-Aufruf stoppte
jedoch beim ersten Paar an einem ungueltigen Zugriff auf die bestehende
TSPM-Konfigurationsform. Es liefen deshalb keine Testkoerper. Der dritte
S2-MT-Transferlauf bleibt gesperrt.

## Prospektiver Quellenplan

Der neue private V2-Plan bindet:

- den historischen unveraenderten S2-MT-Basisplan;
- den gemeinsamen Dezimalfaktor `0.989912331104279`;
- dessen exakte Binary32-Form `e56a7d3f`;
- fuer alle 13 Rezepte den alten PCM-Payloaddigest und einen neuen
  skalierten PCM-Payloaddigest;
- unveraenderte visuelle Voll- und Teilpayload-Digests;
- den S2-MW-Record-Digest
  `5ecd4b166c7393a867ae2c52f2460a514e720ed30d20fd790984de82640ff674`;
- getrennt die neue S2-MW-Verzeichnis-ID und die dort transparent
  abweichende alte interne Audit-ID.

Die Skalierung erfolgt fuer jedes PCM-Sample genau einmal vor der
Rezeptoranalyse als Binary32-Multiplikation. Es gibt kein Clipping, keine
Ausgangsnormierung und keine rezeptbezogene Anpassung. Der historische
Quellenplan und beide S2-MW-Belege blieben unveraendert.

## Statischer Preflight

Vor dem Testaufruf wurden geprueft:

- alle drei geaenderten beziehungsweise neuen Python-Dateien sind syntaktisch
  gueltig;
- der neue Quellenplan importiert keine Memory-, Feld-, Kontext- oder
  Runtimekomponente;
- die Qualifikation enthaelt keinen Haupt-, Feldschritt-, Memoryformations-
  oder Runtimeaufruf;
- der S2-MT-Runner verwendet den neuen V2-Plan und bindet Skalierungsfaktor,
  Binary32-Form und S2-MW-Evidenz in seinen Plandigest;
- das Hauptgate bleibt im Quellstand `False`.

Vor dem Lauf galten folgende SHA-256-Quellhashes:

- neuer Quellenplan:
  `56ac39b47e9df7cab424943a66636de80200c925035d4328521c90500dd92674`;
- S2-MT-Runner:
  `12443e30aff29a135f75cea5efb1af0a505332172d7610e3d53aa7908cfc54f3`;
- Qualifikation:
  `c4d41338f02f0a4eefe4f269f729cc9e6b58a439bc92d2327bf47f0ed51edcde`;
- historischer Quellenplan:
  `ae808ad2a9f206bac45210f5f121e232e72da76b22e0b2bf7c599cc57e479f15`;
- S2-MW-Ergebnis:
  `b1ca1ad9d11e29c6d5b547d166741f1afbf40fb3e8f240ea6eb07d3f4e7d87ef`.

## Einmalqualifikation

Genau ein Testaufruf wurde ausgefuehrt; es gab keinen Retry:

```text
python -m unittest -v tests.test_s2mx_private_scaled_transfer_materialization
```

Ergebnis:

- Exit-Code `1`;
- `0` Testkoerper ausgefuehrt;
- `_materialize_events` kehrte mit allen 28 Materialisaten zurueck;
- `_geometry` stoppte beim ersten Paar;
- keine Memoryformation, kein Feldschritt und keine Runtimeausfuehrung;
- kein Hauptlauf.

Der konkrete Fehler lautet:

```text
AttributeError: 'TSPM1ConfigBinding' object has no attribute
'auditory_match_threshold'
```

Die private Geometrieprojektion liest aktuell:

```text
config.tspm_config.auditory_match_threshold
config.tspm_config.visual_match_threshold
```

`TSPM1ConfigBinding` bindet diese beiden Fast-Grenzen jedoch ausschliesslich
in seiner unveraenderlichen Unterform `fast_config`. Die vorhandene
Konfigurationsform lautet daher statisch:

```text
config.tspm_config.fast_config.auditory_match_threshold
config.tspm_config.fast_config.visual_match_threshold
```

## Aussagegrenze

Der Lauf belegt, dass die neue gemeinsame PCM-Skalierung den zuvor
blockierten 28-Ereignis-Materialisierungspfad technisch durchlaeuft. Er
qualifiziert wegen des anschliessenden Setupabbruchs weder den
Geometriestatus noch die vier visuellen Cue-Digestbindungen in Testkoerpern.

Die falsche Konfigurationsprojektion wurde nach dem Einmalaufruf nicht
korrigiert. Es erfolgte keine zweite Qualifikation, keine fachliche
Transferauswertung und keine Aenderung an Korpus, Schwellen, Rezeptoren,
Memory, Feld oder Runtime.
