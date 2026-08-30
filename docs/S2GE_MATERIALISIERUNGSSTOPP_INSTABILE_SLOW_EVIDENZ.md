# S2-GE: Materialisierungsstopp

## Auftrag

S2-GE war fuer eine private read-only A/B-Schattenprojektion freigegeben.
Die Projektion sollte ausschliesslich ein bereits validiertes S2-GC-Bundle
verarbeiten und dabei unter anderem instabile Slow-Supports als transparente
Pruefevidenz erhalten.

Vor Code und Testanlage wurde geprueft, ob diese Information im erlaubten
Eingang vorhanden ist.

## Festgestellte Luecke

Das qualifizierte `PerceptualContextBundle` besitzt fuer jede der drei Rollen
nur:

- einen verfuegbaren Kandidaten mit Komponenten; oder
- `ABSENT_VALID` mit einem Abwesenheitsgrund.

Fuer `TSPM_SLOW` werden Komponenten nur dann in das Bundle aufgenommen, wenn
der bestehende Slow-Befund funktional erkannt wurde. Liegt kein stabiler
Treffer vor, erzeugt S2-GB ausschliesslich:

```text
status = ABSENT_VALID
absence_reason = NO_STABLE_SLOW_MATCH
candidate = None
```

Der S2-FZ-Befund fuer P2 enthaelt dagegen die relevante Detailinformation:

```text
auditive Slow-Spur: Support 1, instabil
visuelle Slow-Spur: Support 1, instabil
kein stabiler Abruf
```

Support, Slot, Modalitaet, letzter Auswahlschritt und Distanz dieser instabilen
Spuren sind im S2-GC-Bundle nicht enthalten. Sie lagen nur im vorgelagerten
validierten S2-FS-read-only-Befund beziehungsweise in den S2-FZ-Belegen vor.

## Methodische Entscheidung

Eine S2-GE-Projektion mit ausschliesslich dem S2-GC-Bundle koennte deshalb
nur:

1. die instabile Evidenz verlieren; oder
2. sie aus Abwesenheitscode, Fixture, Recorder oder Sollwissen erfinden.

Beides ist durch S2-GD und die S2-GE-Freigabe verboten. Insbesondere ist
`NO_STABLE_SLOW_MATCH` kein Beleg fuer einen konkreten Support `1`; derselbe
Code kann auch fuer andere nicht stabile oder nicht passende Lagen gelten.

S2-GE wird daher vor Implementierung fail-closed gestoppt:

`S2GE_BLOCKED_INPUT_LACKS_UNSTABLE_SLOW_EVIDENCE`

Es wurden kein Projektionsmodul, keine Testdatei und kein `unittest`-Aufruf
erzeugt. S2-GC und das Drei-Rollen-Bundle bleiben unveraendert und weiterhin
gueltig.

## Kleinste fachlich saubere Korrektur

Empfohlen wird keine Aenderung des qualifizierten S2-GC-Bundles. Stattdessen
soll eine spaetere, ausdruecklich korrigierte S2-GE-Grenze einen privaten
quellgebundenen Eingangsbeleg erlauben, der genau zwei bereits vorhandene
Belege atomar zusammenbindet:

```text
ValidatedTwoAreaProjectionInput
- unveraendertes S2-GC PerceptualContextBundle
- genau der validierte S2-FS-read-only-Befund, aus dem es projiziert wurde
- relationale Bundle-/Finding-/Probe-/Zustands-/Quelldigests
```

Der zweite Beleg darf ausschliesslich die im Bundle fehlende interne
Stabilisierungsevidenz liefern. Oeffentliche Kandidaten, A-/B-Zuordnung und
alle bereits im Bundle vorhandenen Werte muessen weiterhin aus dem S2-GC-
Bundle stammen. Abweichungen zwischen Bundle und Finding stoppen vollstaendig
fail-closed.

Diese Korrektur:

- laesst das Drei-Rollen-Bundle und seine S2-GC-Qualifikation unveraendert;
- bewahrt Support und Stabilitaet ohne Rekonstruktion;
- erzeugt keine neue Speicherabfrage;
- fuehrt keine dritte oeffentliche Memory-Ebene ein;
- benoetigt eine ausdrueckliche fachliche Freigabe, weil sie die bisherige
  Eingangsgrenze "ausschliesslich ein Bundle" erweitert.

Ohne diese oder eine gleichwertige explizite Quellenkorrektur darf S2-GE
nicht implementiert werden.
