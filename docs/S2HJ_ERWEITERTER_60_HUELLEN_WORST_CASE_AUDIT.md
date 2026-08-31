# S2-HJ: erweiterter 60-Huellen-Worst-Case-Audit

Status: `S2HJ_REQUALIFICATION_BLOCKED_CONTRADICTORY_SIZE_AND_CODE_LIMITS`

## Grenze

Der Audit materialisierte die 60 neutralen kompakten Aufzeichnungshüllen
read-only vor einem neuen Qualifikationslauf. Verbindlich verwendet wurden:

- ein echter `ExecutionPlan`;
- eine nach `^[a-z][a-z0-9-]{7,95}$` gueltige Owner-ID mit exakt 96 Zeichen;
- ein typisierter `ValidatedB4ShortSequenceEvidence`-Abwesenheitsbeleg mit
  Status `NOT_REQUESTED`;
- null Sequenzreferenzen;
- die fuer S2-GJ gebundenen Rollenformen nach den Distraktoren:
  `B4_RECENT=ABSENT_VALID`, `TSPM_FAST=ABSENT_VALID`, in drei Geschichten
  stabiler Slow-Befund und in einer Geschichte `TSPM_SLOW=ABSENT_VALID`;
- die bestehenden 52 Formation-, vier S2-GC- und vier S2-GI-Registryzeilen.

Es wurde kein `unittest`-Aufruf gestartet. Es wurden keine Rezeptor-, Speicher-,
Koordinator-, Kontextverbraucher- oder Auswertungsfunktionen ausgefuehrt. Der
Produktions- und Testcode blieb unveraendert.

## Ownerbindung

Die 96-Zeichen-ID wurde vor der Projektion durch
`materialize_execution_plan -> ExecutionPlan.build` abgenommen. Sie erfuellt
die bereits gebundene Zeichen- und Laengenform. Die Projektionen erhielten den
Owner ausschliesslich aus diesem Plan.

## Sequenzbindung

Der verwendete Beleg war eine typisierte gueltige Abwesenheit:

```text
status = NOT_REQUESTED
references = ()
evidence_digest = digest(typisierter Abwesenheitsbeleg)
```

Der Digest ist erforderlich, aber er behauptet weder eine Sequenz noch eine
Referenz. Es wurde keine Sequenzevidenz aus Sollwerten rekonstruiert.

## Materialisierte Huellen

Die kanonische ASCII-JSON-Serialisierung einschliesslich abschliessendem LF
ergab fuer die neutralen, laufplangerechten Formen:

| Rolle | Anzahl | Minimum | Maximum |
| --- | ---: | ---: | ---: |
| Formation | 52 | 2.786 Byte | 2.799 Byte |
| S2-GC | 4 | 2.645 Byte | 3.165 Byte |
| S2-GI | 4 | 2.511 Byte | 2.978 Byte |

Alle 60 Huellen liegen unter der effektiven Registrygrenze von 4.095 Byte.

Die Werte sind neutrale Qualifikationsmaterialisierungen, keine neue
Funktionsausfuehrung und kein Kontextbefund.

## Warum 3.236 Byte nicht die zulaessige S2-GC-Form sind

Die Zahl 3.236 entsteht aus einer anderen, in derselben Freigabe
ausgeschlossenen Form:

```text
gebundene S2-GC-Vollform:               3.174 Byte
eine zusaetzliche 64-stellige Referenz:   +66 Byte
AVAILABLE statt NOT_REQUESTED:              -4 Byte
abweichende Form:                       3.236 Byte
```

Diese Form besitzt eine Sequenzreferenz und den Status `AVAILABLE`. Sie darf
nicht gleichzeitig als `NOT_REQUESTED` ohne Referenzen behandelt werden.
3.236 Byte als tatsaechlich bestaetigtes Maximum der erlaubten Form zu
dokumentieren waere daher sachlich falsch.

Zusaetzlich liegt 3.236 Byte ueber der unveraenderten allgemeinen
Kompaktprojektionsgrenze von 3.200 Byte. Diese Grenze ohne Produktionsaenderung
beizubehalten und gleichzeitig eine gueltige 3.236-Byte-Huelle zu verlangen,
ist technisch widerspruechlich.

## Tatsaechlicher Codeblocker

Die laufplangerechte S2-GI-Maximalhuelle misst in der neutralen
96-Zeichen-Materialisierung 2.978 Byte. Der private Runner und Verifikator
binden derzeit jedoch:

```text
COMPACT_S2GI_MAX_ARTIFACT_BYTES = 2.977
```

Ein neuer Lauf derselben zwoelf Tests wuerde daher bereits im Setup korrekt mit
`E008` stoppen. Eine kuerzere Owner-ID wuerde den Worst-Case-Auftrag umgehen.

## Entscheidung

Ein neuer Testlauf wurde nicht gestartet, weil die Vorbedingungen nicht
widerspruchsfrei erfuellt werden koennen:

1. 3.236 Byte gehoeren zur verbotenen Referenzform, nicht zu
   `NOT_REQUESTED` ohne Referenzen.
2. 3.236 Byte ueberschreiten die unveraenderte allgemeine 3.200-Byte-Grenze.
3. Die zulaessige S2-GI-Worst-Case-Huelle benoetigt 2.978 Byte, der Code erlaubt
   nur 2.977 Byte.
4. Die Freigabe schliesst die dafuer erforderliche enge Codegrenzenkorrektur
   aus.

Status:

`S2HJ_REQUALIFICATION_BLOCKED_CONTRADICTORY_SIZE_AND_CODE_LIMITS`

Der kleinste methodisch saubere naechste Schritt ist eine ausdrueckliche
Freigabe, ausschliesslich die S2-GI-Rollenobergrenze in Runner und Verifikator
von 2.977 auf 2.978 Byte zu korrigieren. S2-GC bleibt fuer die erlaubte Form
unter 3.174 Byte; 3.236 wird nur als Diagnose der ausgeschlossenen
Referenzfixture dokumentiert. Danach koennen die neutrale Fixture und genau ein
neuer Lauf derselben zwoelf Tests unter neuer ID freigegeben werden.
