# S1-SB: Statische Korrektur auf 17 Repliken und zwei zeitangepasste U-Frischkontrollen

## Status und Freigabe

S1-SB setzt die nach S1-SA erforderliche ausdrueckliche Richtungsentscheidung
um. Freigegeben sind 17 unabhaengige Expositionsrepliken mit zwei getrennten
zeitangepassten U-Frischkontrollen.

S1-SB korrigiert ausschliesslich die statische Expositionsachse und ihre
abgeleiteten Vollstaendigkeitszahlen. Der Schritt waehlt keine
Kontaktwerte, Dauern, Ticks, Digests, Parameter oder Toleranzen. Er
implementiert kein Fixture, veraendert keinen Modellkern, fuehrt keinen Test
und keinen Feldlauf aus und trifft keine Ergebnisentscheidung.

Verbindliche Entscheidung:

```text
SEVENTEEN_FRESH_EXPOSURE_REPLICAS_BOUND
EARLY_AND_LATE_FRESH_B_CONTROLS_SEPARATED
FOURTEEN_BY_SEVENTEEN_MATRIX_EQUALS_238_CELLS
FORTY_CHECKPOINTS_PER_MODEL_EQUALS_560_TOTAL_RECORDS
NO_VALUES_NO_IMPLEMENTATION_NO_EXECUTION
```

## Korrigierte kanonische Replikachse

Die Positionen 01 bis 15 bleiben gegenueber S1-RA unveraendert. Die
bisherige Position 16 `U_FRESH_B` wird durch zwei unabhaengige
Frischrepliken ersetzt:

| Position | Replikrolle | Aeussere Ereignisstruktur |
|---|---|---|
| 01 | `F_A` | `HISTORY_A -> ALIGN_READOUT_SH -> PROBE_A` |
| 02 | `F_C` | `HISTORY_C_REMOTE -> ALIGN_READOUT_SH -> PROBE_A` |
| 03 | `F_G` | `GAP_ZERO_CONTACT -> ALIGN_READOUT_SH -> PROBE_A` |
| 04 | `T_EARLY` | kurzer `HISTORY_A`-Praefix -> Align -> `PROBE_A` |
| 05 | `T_LATER` | laengerer `HISTORY_A`-Praefix -> Align -> `PROBE_A` |
| 06 | `I_LOCAL` | `HISTORY_A -> HISTORY_B_LOCAL -> Align -> PROBE_A` |
| 07 | `I_REMOTE` | `HISTORY_A -> HISTORY_C_REMOTE -> Align -> PROBE_A` |
| 08 | `I_GAP` | `HISTORY_A -> GAP_ZERO_CONTACT -> Align -> PROBE_A` |
| 09 | `C_LOCAL` | A-Praefix -> Pre -> B lokal -> Post -> Align -> `PROBE_A` |
| 10 | `C_REMOTE` | A-Praefix -> Pre -> C entfernt -> Post -> Align -> `PROBE_A` |
| 11 | `C_GAP` | A-Praefix -> Pre -> Nullkontakt -> Post -> Align -> `PROBE_A` |
| 12 | `R_EARLY` | `HISTORY_A -> GAP_EARLY -> Align -> PROBE_A` |
| 13 | `R_LATE` | `HISTORY_A -> GAP_LATE -> Align -> PROBE_A` |
| 14 | `U_RELEASED` | A -> `GAP_LATE` -> B lokal -> Align -> `PROBE_B` |
| 15 | `U_EARLY` | A -> `GAP_EARLY` -> B lokal -> Align -> `PROBE_B` |
| 16 | `U_FRESH_B_EARLY` | frischer Nullpfad bis zur fruehen B-Zeit -> B lokal -> Align -> `PROBE_B` |
| 17 | `U_FRESH_B_LATE` | frischer Nullpfad bis zur spaeten B-Zeit -> B lokal -> Align -> `PROBE_B` |

Jede Position ist eine eigene Frischreplik. Die beiden neuen
Frischkontrollen duerfen weder Carry noch Checkpoints miteinander teilen.
Die Positionen sind Serialisierungsordnung und keine Ausfuehrungsreihenfolge.

## Verbindliche U-Zeitbeziehungen

Alle vier U-Repliken starten aus derselben registrierten Frischprojektion
und derselben Anfangsfeldzeit `t0`. Fuer die spaeter zu bindenden positiven
Dauern gelten:

```text
a = Dauer der gemeinsamen HISTORY_A
e = Dauer von GAP_EARLY
l = Dauer von GAP_LATE
l > e
```

Die B-Startzeiten werden paarweise kontrolliert:

```text
U_EARLY.B_START
  = U_FRESH_B_EARLY.B_START
  = t0 + a + e

U_RELEASED.B_START
  = U_FRESH_B_LATE.B_START
  = t0 + a + l
```

Damit muessen die Frisch-Nullvorlaeufe spaeter folgende Dauern erhalten:

```text
fresh_early_null_duration = a + e
fresh_late_null_duration  = a + l
```

Diese Identitaeten binden nur die Zeitordnung. S1-SB waehlt noch keine
Zahlenwerte.

## Wertidentitaet innerhalb der U-Familie

`HISTORY_B_LOCAL` und `PROBE_B` muessen in allen vier U-Repliken
wertidentisch sein. Insbesondere muessen spaeter uebereinstimmen:

- Rezeptorkontaktvektor und aktive Dockrolle;
- Intervallanzahl, Segmentgrenzen und Gesamtdauer;
- Geometrie, Knotenordnung und Zeitinterpretation;
- Probeinput und Probeintervallform;
- zeitloses Alignziel unmittelbar vor der Probe.

Nur die kausale Vorgeschichte vor B darf entsprechend der Replikrolle
abweichen. Modellkerne erhalten weder Repliknamen noch Vergleichspaar oder
erwartete Richtung.

## Praefix- und Paarbindungen

Die bisherigen S1-RA-Beziehungen bleiben erhalten, mit folgender
Konkretisierung:

- `GAP_EARLY` ist ein echter zeitlicher Praefix von `GAP_LATE`;
- `U_EARLY` verwendet exakt die A- und Gap-Geschichte von `R_EARLY` vor B;
- `U_RELEASED` verwendet exakt die A- und Gap-Geschichte von `R_LATE` vor B;
- `U_FRESH_B_EARLY` kontrolliert ausschliesslich die B-Startzeit von
  `U_EARLY`;
- `U_FRESH_B_LATE` kontrolliert ausschliesslich die B-Startzeit von
  `U_RELEASED`;
- ein armuebergreifendes Auffuellen, Kuerzen oder Verschieben nach der
  Registrierung ist verboten.

Die beiden Frischkontrollen sind technische Zeitkontrollen. Sie sind kein
Kandidat, kein Ressourcenbeleg und kein Befund einer hypothetischen
MCM-Memory-Entwicklungsrichtung.

## Korrigierte Matrix und Checkpointzahlen

Die Pflichtmatrix lautet nun:

```text
14 Modellrollen
x 17 unabhaengige Expositionsrepliken
= 238 vollstaendige Lebenszykluszellen
```

Jede Replik besitzt weiterhin `ALIGNED_PRE_PROBE` und
`POST_PROBE_READOUT`. Nur die drei C-Repliken besitzen zusaetzlich jeweils
`PRE_COMPETITION` und `POST_COMPETITION`. Daraus folgen:

```text
17 x 2 universelle Checkpoints = 34
 3 x 2 C-Zusatzcheckpoints     =  6
                                  --
pro Modellrolle                = 40

14 Modellrollen x 40           = 560 passive Pflichtrecords
```

Die Zahlen bezeichnen Vollstaendigkeit, kein Ausfuehrungsbudget. Eine
fehlende Zelle oder ein fehlender Pflichtrecord sperrt spaeter das gesamte
Paket fail-closed.

## Auswirkung auf das bestehende Frischmanifest

Das technisch abgenommene Manifest
`mcm.s1rk.four-node-fresh-manifest.v1` enthaelt die digestgebundene Aussage
`public_fresh_shared_by_all_224_cells`. Sie beschreibt den damaligen
16-Repliken-Stand und darf nicht in-place auf 238 geaendert werden.

Unveraendert wiederverwendbar bleiben nach erneuter Queridentitaetspruefung:

- Vier-Knoten-Geometrie und Knotenordnung;
- Rollenabbildung und Dockregistrierung;
- gemeinsame oeffentliche Frischprojektion;
- 14 rollenweise private Frischzustaende beziehungsweise Leermarkierungen;
- bestehende rollenweise Konfigurationsquellen.

Vor einem konkreten Expositionsfixture ist jedoch eine neue versionierte
Manifestregistrierung erforderlich, die 17 Repliken und 238 Zellen
ausdruecklich bindet. Der bestehende v1-Digest bleibt historisch gueltig und
wird nicht uminterpretiert.

## Supersession und Projektgrenze

S1-SB ersetzt ausschliesslich:

- die einzelne S1-PZ/S1-RA-Rolle `U_FRESH_B`;
- die S1-RA-Zahl von 16 Expositionsrepliken;
- die daraus abgeleiteten 224 Matrixzellen und 532 Pflichtrecords.

Alle anderen Rollen-, Carry-, Informations-, Align-, Beobachtungs- und
Atomaritaetsgrenzen aus S1-PZ, S1-QZ und S1-RA bleiben verbindlich.

## Genau ein naechster Schritt

S1-SC ist ausschliesslich als statischer versionierter
Vier-Knoten-Frischmanifest-Migrations-, Queridentitaets- und
Abnahmebudgetvertrag fuer 17 Repliken und 238 Zellen zulaessig.

S1-SC darf noch kein Manifest materialisieren, keinen Consumer aendern,
keinen Test ausfuehren und kein Expositionsfixture binden. Erst muessen
Schemaidentitaet, zu erhaltende v1-Identitaeten, neue Zellzahlsaussage,
Digestgrenzen, Fail-Closed-Regeln und ein fokussiertes spaeteres
Implementierungsbudget statisch feststehen.
