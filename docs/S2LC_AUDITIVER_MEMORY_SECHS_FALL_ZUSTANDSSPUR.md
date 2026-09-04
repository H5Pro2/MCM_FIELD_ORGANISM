# S2-LC - Statische Sechs-Faelle-Zustandsspur

## Status und Grenze

`S2LC_STATIC_SIX_CASE_MEMORY_TRACE_CONFIRMED`

S2-LC leitet vier frische Memorygeschichten und einen frischen Nullzustand
vollstaendig aus den unveraenderten B4-, TSPM-Fast- und auditory-PPB-1-
Regeln her. Die Spur umfasst exakt 30 Formationen und sechs spaetere
auditive Teilhinweisfaelle:

```text
H_A     = L
H_B     = P P P P E1 E2 E3 E4 E5 E6 E7 E8 E9
H_AB    = P P P P E1 E2 E3 E4 E5 E6 E7 E8 E9 L
H_AMBIG = P M
H_NULL  = frischer Nullzustand
```

Es wurden keine Rezeptor-, Memory-, Teilscan-, Kontext- oder Feldfunktionen
ausgefuehrt. Es gibt keine Vollprobe, keine neue PCM-Materialisierung und
keine Schwellen- oder Fixtureaenderung. Die Zustandsspur verwendet nur die
bereits gespeicherten S2-KY- und S2-LB-Rezeptorwerte.

## Quellenbindung

Technischer Ausgangsstand ist Commit
`b6cfe6aa1219db64ea265c25b9eac863ca1cea8c`.

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| S2-LA-Erreichbarkeitsaudit | `docs/S2LA_AUDITIVER_MEMORY_ERREICHBARKEITSAUDIT.md` | `71815b15ad5bdae4c2b03a553da097ccea80b316693f5d1663314fab38c91de4` |
| S2-LB-Plan | `docs/S2LB_D_FAR_PCM_MATERIALISIERUNGSPLAN.json` | `f77f074cb9df6ada1f182c1bdb4abfb5fe233ca923f8a7bd99334c9c13a85d48` |
| S2-LB-Ergebnis | `reports/s2kx/s2lb-d-far-pcm-materialization-20260904-01/materialization.json` | `1fd9ab971acbdb1bcacd6dde7c69a4ba485edd7056697ed240d00d465a9b05d0` |
| TSPM-1 | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| PPB-1 | `mcm_field_organism/_ppb1_reference.py` | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |

## Rollen und feste Distanzen

```text
L  = CUE_LOW              + visueller S2-JV-X-Zustand
P  = CANDIDATE_PLUS       + visueller S2-JV-X-Zustand
M  = CANDIDATE_MINUS      + visueller S2-JV-X-Zustand
Ei = D_FAR                 + visueller S2-JV-Di-Zustand, i=1..9
H  = CANDIDATE_HIGH       als spaeterer auditiver Cue
```

Jede wiederholte Rolle verwendet in einem spaeteren Lauf ein neues,
streng fortgeschriebenes Quellfenster. Die Rollenbezeichnungen sind nur
Auswertungsnotation und kein Memoryinput.

Verbindliche bereits gemessene Teilscanabstaende:

| Beziehung | beobachtete mittlere L1 | relevante Schwelle | Seite |
| --- | ---: | ---: | --- |
| L - P | `7.036867813356767e-11` | Slow `0.02` | Treffer |
| L - M | `1.2327556304197705e-10` | A `0.2` | Treffer |
| H - P | `0.03167999726488322` | Slow `0.02` | Nichttreffer |
| D_FAR - L | `0.22154331317519135` | A `0.2` | Nichttreffer |
| D_FAR - H | `0.23337224934984002` | A `0.2` | Nichttreffer |

Ausserdem gilt fuer die Formation:

```text
d_full(P,M) = 0.00959999972837876 <= 0.2
d_visual(X,Di) >= 13/24 > 0.2
d_visual(Di,Dj) >= 13/24 > 0.2 fuer i != j
```

Damit aktualisiert M den vorhandenen P-Fast-Slot. Jedes E_i ist dagegen
wegen der visuellen Komponente ein gemeinsamer Fast-Nichttreffer, obwohl
sein Audioanteil zu anderen Formationswerten innerhalb der Fast-Schwelle
liegen darf. Beim spaeteren rein auditiven Teilscan ist jedes E_i wegen
des D_FAR-Audioanteils fuer L und H ein A-Nichttreffer.

## Notation der Zustandstabellen

- `F0..F2` sind die drei physischen Fast-Slots.
- `sN` ist der Fast- oder Slow-Support.
- `cN` ist die Anzahl erfolgter Konsolidierungen des Fast-Slots.
- `@N` ist `last_selected_step` im jeweiligen Fast-Zustand.
- B4 wird chronologisch mit Formationindizes gezeigt; ab zehn Formationen
  steht nur das aktuelle FIFO-Fenster von neun Eintraegen dort.
- `S0` bezeichnet den ersten auditory-Slow-Slot.

Fast-Support ist durch `consolidate_after = 2` auf 2 begrenzt. Vier
identische P-Expositionen erzeugen genau drei PPB-Aufrufe und damit
Slow-Support 3.

## H_A: eine Formation

| Schritt | Formation | B4 chronologisch | Fast nach dem Schritt | auditory Slow | LRU/Ersetzung |
| ---: | --- | --- | --- | --- | --- |
| 1 | L | `1:L` | `F0=L/s1/c0@1`, F1/F2 frei | alle 8 frei | freier F0, keine Ersetzung |

Finale physische Anatomie:

```text
B4:   slot0=1:L; slot1..8=frei
Fast: F0=L/s1; F1/F2=frei
Slow: 8 freie Slots
```

Der spaetere Cue L findet je einen identischen B4- und Fast-Kandidaten.
Beide werden intern zu genau einem `A_RECENT`-Kandidaten mit zwei
Herkunftsbelegen projiziert. B ist gueltig abwesend. Der Fall ist
`UNIQUE_A`.

## H_B: dreizehn Formationen

| Schritt | Formation | B4-FIFO nach dem Schritt | Fast nach dem Schritt | auditory Slow | LRU/Ersetzung |
| ---: | --- | --- | --- | --- | --- |
| 1 | P | `1:P` | `F0=P/s1/c0@1` | leer | freier F0 |
| 2 | P | `1:P 2:P` | `F0=P/s2/c1@2` | `S0=P/s1@1` | Fast-Treffer; PPB erstellt S0 |
| 3 | P | `1:P 2:P 3:P` | `F0=P/s2/c2@3` | `S0=P/s2@2` | Fast- und Slow-Treffer |
| 4 | P | `1:P 2:P 3:P 4:P` | `F0=P/s2/c3@4` | `S0=P/s3@3`, stabil | Fast- und Slow-Treffer |
| 5 | E1 | `1:P..4:P 5:E1` | `F0=P@4, F1=E1/s1@5` | unveraendert | freier F1 |
| 6 | E2 | `1:P..4:P 5:E1 6:E2` | `F0=P@4, F1=E1@5, F2=E2/s1@6` | unveraendert | freier F2 |
| 7 | E3 | `1:P..4:P 5:E1 6:E2 7:E3` | `F0=E3/s1@7, F1=E1@5, F2=E2@6` | unveraendert | P aus F0 LRU-ersetzt |
| 8 | E4 | `1:P..4:P 5:E1..8:E4` | `F0=E3@7, F1=E4/s1@8, F2=E2@6` | unveraendert | E1 aus F1 ersetzt |
| 9 | E5 | `1:P..4:P 5:E1..9:E5` | `F0=E3@7, F1=E4@8, F2=E5/s1@9` | unveraendert | E2 aus F2 ersetzt |
| 10 | E6 | `2:P 3:P 4:P 5:E1..10:E6` | `F0=E6/s1@10, F1=E4@8, F2=E5@9` | unveraendert | E3 aus F0 ersetzt |
| 11 | E7 | `3:P 4:P 5:E1..11:E7` | `F0=E6@10, F1=E7/s1@11, F2=E5@9` | unveraendert | E4 aus F1 ersetzt |
| 12 | E8 | `4:P 5:E1..12:E8` | `F0=E6@10, F1=E7@11, F2=E8/s1@12` | unveraendert | E5 aus F2 ersetzt |
| 13 | E9 | `5:E1 6:E2 7:E3 8:E4 9:E5 10:E6 11:E7 12:E8 13:E9` | `F0=E9/s1@13, F1=E7/s1@11, F2=E8/s1@12` | `S0=P/s3@3`, stabil | E6 aus F0 ersetzt |

Kein E_i erreicht Fast-Support 2. Deshalb gibt es in der Druckphase keinen
PPB-Aufruf, keinen neuen Slow-Slot und keine Slow-LRU-Aenderung. Der Abstand
zwischen aufeinanderfolgenden Fast-Auswahlen ist hoechstens 3; es tritt kein
Fast-Ablauf vor der jeweiligen LRU-Ersetzung ein.

Finale physische Anatomie:

```text
B4 slot0=10:E6, slot1=11:E7, slot2=12:E8, slot3=13:E9,
    slot4=5:E1, slot5=6:E2, slot6=7:E3, slot7=8:E4, slot8=9:E5
Fast F0=E9/s1@13, F1=E7/s1@11, F2=E8/s1@12
Slow S0=P/s3@3; S1..S7=frei
```

H_B traegt zwei getrennte Teilhinweisfaelle:

1. Cue L: alle neun B4- und alle drei Fast-Slots sind wegen
   `d_observed(D_FAR,L) > 0.2` Nichttreffer. S0 ist wegen
   `d_observed(P,L) <= 0.02` der einzige stabile Slow-Treffer. Ergebnis:
   `UNIQUE_B`.
2. Cue H: D_FAR ist auch gegen H oberhalb 0.2; P ist gegen H oberhalb der
   Slow-Schwelle 0.02. Beide Bereiche sind belegt, aber nicht anwendbar.
   Ergebnis: `NO_APPLICABLE_CONTEXT`.

## H_AB: vierzehn Formationen

Die Schritte 1 bis 13 sind zustandsgetrennt, aber regel- und wertgleich zu
H_B. Sie werden fuer H_AB neu gebildet und nicht aus H_B uebernommen.

| Schritt | Formation | B4-FIFO nach dem Schritt | Fast nach dem Schritt | auditory Slow | LRU/Ersetzung |
| ---: | --- | --- | --- | --- | --- |
| 1 | P | `1:P` | `F0=P/s1/c0@1` | leer | freier F0 |
| 2 | P | `1:P 2:P` | `F0=P/s2/c1@2` | `S0=P/s1@1` | PPB erstellt S0 |
| 3 | P | `1:P 2:P 3:P` | `F0=P/s2/c2@3` | `S0=P/s2@2` | Trefferupdate |
| 4 | P | `1:P 2:P 3:P 4:P` | `F0=P/s2/c3@4` | `S0=P/s3@3`, stabil | Trefferupdate |
| 5 | E1 | `1:P..4:P 5:E1` | `F0=P@4, F1=E1@5` | unveraendert | freier F1 |
| 6 | E2 | `1:P..4:P 5:E1 6:E2` | `F0=P@4, F1=E1@5, F2=E2@6` | unveraendert | freier F2 |
| 7 | E3 | `1:P..4:P 5:E1..7:E3` | `F0=E3@7, F1=E1@5, F2=E2@6` | unveraendert | P aus F0 ersetzt |
| 8 | E4 | `1:P..4:P 5:E1..8:E4` | `F0=E3@7, F1=E4@8, F2=E2@6` | unveraendert | E1 aus F1 ersetzt |
| 9 | E5 | `1:P..4:P 5:E1..9:E5` | `F0=E3@7, F1=E4@8, F2=E5@9` | unveraendert | E2 aus F2 ersetzt |
| 10 | E6 | `2:P 3:P 4:P 5:E1..10:E6` | `F0=E6@10, F1=E4@8, F2=E5@9` | unveraendert | E3 aus F0 ersetzt |
| 11 | E7 | `3:P 4:P 5:E1..11:E7` | `F0=E6@10, F1=E7@11, F2=E5@9` | unveraendert | E4 aus F1 ersetzt |
| 12 | E8 | `4:P 5:E1..12:E8` | `F0=E6@10, F1=E7@11, F2=E8@12` | unveraendert | E5 aus F2 ersetzt |
| 13 | E9 | `5:E1..13:E9` | `F0=E9@13, F1=E7@11, F2=E8@12` | `S0=P/s3@3` | E6 aus F0 ersetzt |
| 14 | L | `6:E2 7:E3 8:E4 9:E5 10:E6 11:E7 12:E8 13:E9 14:L` | `F0=E9@13, F1=L/s1@14, F2=E8@12` | `S0=P/s3@3` | E7 aus F1 ersetzt |

L trifft keinen E-Fast-Slot gemeinsam: auditiv liegt D_FAR zwar auch voll
innerhalb 0.2, visuell gilt aber X gegen D7-D9 jeweils groesser 0.2. L wird
deshalb als neuer Support-1-Inhalt in den LRU-Slot F1 geschrieben und loest
keine Konsolidierung aus.

Finale physische Anatomie:

```text
B4 slot0=10:E6, slot1=11:E7, slot2=12:E8, slot3=13:E9,
    slot4=14:L, slot5=6:E2, slot6=7:E3, slot7=8:E4, slot8=9:E5
Fast F0=E9/s1@13, F1=L/s1@14, F2=E8/s1@12
Slow S0=P/s3@3; S1..S7=frei
```

Der Cue L findet in B4 genau den Eintrag 14:L und in Fast genau F1=L.
Beide vollen 48-Werte-Kandidaten sind identisch und ergeben einen einzigen
oeffentlichen A-Kandidaten. S0=P ist gleichzeitig der einzige stabile
B-Treffer. Die Kardinalitaet zwischen `A_RECENT` und
`B_STABLE_AUDITORY` ist damit exakt 2. Ergebnis:
`PUBLIC_AMBIGUITY`, also Enthaltung.

## H_AMBIG: zwei Formationen

| Schritt | Formation | B4 chronologisch | Fast nach dem Schritt | auditory Slow | LRU/Ersetzung |
| ---: | --- | --- | --- | --- | --- |
| 1 | P | `1:P` | `F0=P/s1/c0@1` | leer | freier F0 |
| 2 | M | `1:P 2:M` | `F0=(0.5P+0.5M)/s2/c1@2` | `S0=M/s1@1`, instabil | gemeinsamer Fast-Treffer; keine Ersetzung |

M aktualisiert wegen `d_full(P,M) <= 0.2` und identischem X-Begleiter den
vorhandenen Fast-Slot. Der erste PPB-Aufruf erhaelt die aktuelle M-Exposition
und erstellt S0 mit Support 1. Der Slot ist nicht oeffentlich stabil.

Der Cue L trifft in B4 sowohl P als auch M. Der vollstaendige B4-Scan ergibt
daher `BANK_MULTIPLE_OBSERVED_MATCHES` und die A-Aufloesung endet als
`A_RECENT_INTERNAL_AMBIGUITY`. Der zusaetzliche einzelne Fast-Treffer darf
diesen harten internen Befund nicht aufheben. Ergebnis:
`A_BANK_AMBIGUITY`, also Enthaltung.

## H_NULL: frischer Nullzustand

```text
B4:   9 freie Slots, accepted_count=0
Fast: 3 freie Slots, accepted_exposure_count=0
Slow: 8 freie Slots, accepted_step_count=0
```

Ein spaeterer Cue L scannt alle drei Banken vollstaendig. Beide oeffentlichen
Bereiche sind `ABSENT_VALID`; Ergebnis `NO_CONTEXT`. Der Nullzustand ist
kein fuenfter Bildungszustand und traegt null Formationen.

## Sechs Teilhinweisfaelle

| Fall | Zustand | Cue | B4-Treffer | Fast-Treffer | stabile Slow-Treffer | gebundener Ausgang |
| --- | --- | --- | ---: | ---: | ---: | --- |
| LC-01 | H_A | L | 1 | 1, wertgleich | 0 | `ADMIT_SINGLE_CONTEXT:A_RECENT` |
| LC-02 | H_B | L | 0 | 0 | 1 P/s3 | `ADMIT_SINGLE_CONTEXT:B_STABLE_AUDITORY` |
| LC-03 | H_B | H | 0 | 0 | 0, Bank belegt | `ABSTAIN_NO_APPLICABLE_CONTEXT` |
| LC-04 | H_AB | L | 1 L | 1 L, wertgleich | 1 P/s3 | `ABSTAIN_AMBIGUOUS_CONTEXT` |
| LC-05 | H_AMBIG | L | 2 P/M | 1 | 0 stabil | `ABSTAIN_INTERNAL_AMBIGUITY` |
| LC-06 | H_NULL | L | 0, Bank leer | 0, Bank leer | 0, Bank leer | `ABSTAIN_NO_CONTEXT` |

Alle B4-, Fast- und Slow-Scans muessen unabhaengig vom ersten Treffer
vollstaendig abgeschlossen werden. Kein Slotalter, Support, Abstand oder
Listenplatz darf eine Rangfolge erzeugen.

## Umfang und Invarianten

| Ressource | Umfang |
| --- | ---: |
| frische gebildete Memoryzustaende | 4 |
| zusaetzlicher Nullzustand | 1 |
| H_A-Formationen | 1 |
| H_B-Formationen | 13 |
| H_AB-Formationen | 14 |
| H_AMBIG-Formationen | 2 |
| Formationen gesamt | 30 |
| spaetere auditive Teilhinweise | 6 |
| Vollproben | 0 |
| neue PCM-Materialisierungen | 0 |

Fuer einen spaeteren Lauf muessen alle sechs Teilhinweise eigene, strikt
spaetere PCM-Fenster mit nativer Audiouhr erhalten. Verdeckte Baender bleiben
durch den unabhaengigen 24/24-Bandplan maskiert. Zielwerte und Sollstatus
duerfen erst der getrennte Auswerter sehen.

## Fail-Closed- und Falsifikationsgrenze

Die Sechs-Faelle-Spur waere fachlich widerlegt, wenn bei unveraenderten
Regeln:

- ein E_i einen vorhandenen Fast-Slot aktualisiert oder einen PPB-Aufruf
  ausloest;
- P nach H_B oder H_AB noch in B4 oder Fast vorhanden ist;
- P in Slow nicht Support 3 besitzt;
- D_FAR fuer Cue L oder H unter der A-Scanschwelle liegt;
- H_AB mehr oder weniger als einen A- und einen B-Kandidaten liefert;
- H_AMBIG nicht mindestens zwei B4-Treffer liefert.

Quellen-, Zeit-, Dimensions-, Slot-, Digest- oder Read-only-Bruch waere
dagegen `NOT_EVALUABLE` und kein fachlicher Funktionsbefund.

## Abschluss

Die kurze statische Zustandsspur besteht. D_FAR schliesst genau die von
S2-LA identifizierte A-Druckluecke, ohne die Schwellen oder Memorykerne zu
veraendern. Alle sechs fachlich relevanten Faelle sind durch vier frische
Geschichten mit zusammen 30 Formationen plus einen Nullzustand erreichbar.

Reale Fixtures, ein kleiner geschlossener Runner und ein read-only
Verifikator duerfen als naechster begrenzter Schritt vorbereitet werden.
B4/Fast-Konflikt und Slow-Mehrdeutigkeit bleiben ausschliesslich neutrale
S2-KZ-Sicherheitsfaelle. Eine weitere allgemeine Auditstufe ist nicht
begruendet.
