# S2-FT: statischer Funktions- und Auswertungsplan fuer den atomaren B4-/TSPM-1-Verbund

Stand: 2026-08-29
Status: `BLOCKED_STATIC_SEQUENCE_DOES_NOT_REACH_SLOW_SUPPORT_3`

## Auftrag und Grenze

S2-FT materialisiert ausschliesslich die freigegebene einzelne Geschichte:

```text
P1, P2, P3, P4, P1, P2, P1, P1,
P5, P6, P7, P8, P9, P10, P11, P3, P4
```

Geprueft werden sollten spaeter eine fruehe B4-Folge, der Verlust von P1 und
P2 aus B4 und TSPM-Fast sowie eine wiederholungsabhaengige Slow-Erhaltung von
P1. Dieser Plan fuehrt keine Zustandsfunktion aus. Es entstehen keine Fixtures,
Implementierung, Tests, Runner oder Ausfuehrung.

Die Materialisierung ergibt einen zwingenden Widerspruch zwischen Geschichte
und Erfolgserwartung: TSPM-1 besitzt drei Fast-Slots. P1 wird bei Schritt 4
durch P4 verdraengt. Die spaeteren P1-Schritte 5, 7 und 8 bilden daher nur
einen neuen Fast-Slot und zwei passende Aktualisierungen. Das erzeugt zwei
PPB-1-Aufrufe und Slow-Support 2, nicht Support 3. S2-FT darf deshalb nicht als
ausfuehrbarer Erfolgsplan freigegeben werden.

## Unveraenderte technische Quellen

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| B4 | `mcm_field_organism/_tspm1_s2dr_private_comparison.py` | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |
| TSPM-1 | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| Inhaltsprobe | `tools/_retention_capacity_read_only.py` | `524a42ae8294a14e58adfda29afa8602f3a799e0caaccae9675dc50bf0109ff7` |
| B4-Folgenprobe | `tools/_visual_sequence_memory_probe.py` | `d5fef4aa9fbbc06502f630e729161274b13c972f9ae2a1f13fb2084bb00593ec` |
| atomarer Koordinator | `tools/_s2fs_b4_tspm1_private_coordinator.py` | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |

Gebunden bleiben B4-Kapazitaet 9, TSPM-Fast-Kapazitaet 3,
`consolidate_after = 2`, `expire_after_exposures = 8`, PPB-1-Stabilitaet ab
Support 3 und die gemeinsame funktionale visuelle Schwelle `44/765`.
TSPM-1 und PPB-1 behalten ihre nativen Matchregeln. Keine Schwelle und kein
Speicherparameter wird fuer S2-FT veraendert.

## Literale Wahrnehmungszustaende

Jeder Zustand ist ein 3-x-2-Bild mit drei Werten 210 und drei Werten 30. Ein
Zellwert wird unveraendert auf seine drei visuellen Kanaele projiziert. Damit
entstehen 18 visuelle Werte `Zellwert/255`. Auditiv gelten immer acht
Nullwerte.

| ID | hohe Zellpositionen | sechs Zellwerte |
| --- | --- | --- |
| P1 | 012 | 210, 210, 210, 30, 30, 30 |
| P2 | 013 | 210, 210, 30, 210, 30, 30 |
| P3 | 014 | 210, 210, 30, 30, 210, 30 |
| P4 | 015 | 210, 210, 30, 30, 30, 210 |
| P5 | 023 | 210, 30, 210, 210, 30, 30 |
| P6 | 024 | 210, 30, 210, 30, 210, 30 |
| P7 | 025 | 210, 30, 210, 30, 30, 210 |
| P8 | 034 | 210, 30, 30, 210, 210, 30 |
| P9 | 035 | 210, 30, 30, 210, 30, 210 |
| P10 | 045 | 210, 30, 30, 30, 210, 210 |
| P11 | 123 | 30, 210, 210, 210, 30, 30 |

Alle Zustaende besitzen dieselbe Gesamthelligkeit 720 und dasselbe Histogramm.
Zwei verschiedene 3-von-6-Masken unterscheiden sich in mindestens zwei
Zellen. Der kleinste visuelle L1-Abstand ist daher exakt `180/765`, liegt ueber
`44/765` und auch ueber der nativen TSPM-Visuellgrenze 0,2. Fremde P-Zustaende
koennen somit keine unbeabsichtigte passende TSPM-Aktualisierung ausloesen.

Die Bezeichnungen P1 bis P11 sind nur Versuchsmetadaten. Speicher- und
Probeoperatoren erhalten ausschliesslich die gebundenen Rezeptorwerte,
Quellenobjekte und Ticks.

## Zeit- und Quellenplan

Die ersten vier Formationen verwenden die Fenster `[0,1)` bis `[3,4)`. Die
vier read-only Vektoren der fruehen Folgenprobe verwenden `[4,5)` bis `[7,8)`.
Die Formationen 5 bis 17 verwenden anschliessend `[8,9)` bis `[20,21)`.
Die finalen P1- und P2-Inhaltsproben verwenden `[21,22)` und `[22,23)`.

Jede Formation wird genau einmal aus einer gemeinsamen validierten auditiven
und visuellen Rezeptorquelle gebunden. Composite, Standalone-B4 und
Standalone-TSPM erhalten bytegleich dieselben Werte und dieselbe Zeitlage.
Probequellen werden ebenfalls einmal gebildet und von den read-only Sichten
wiederverwendet. Kein Arm erhaelt ID, Sollklasse oder erwarteten Befund.

## Vollstaendige Zustandsprognose

| Schritt | Input | B4-Ereignis | TSPM-Fast | Fast-Verlust | PPB-Aufrufe je Modalitaet kumulativ | P1-Slow-Support |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 1 | P1 | `B4_APPENDED` | `FAST_CREATED` | - | 0 | 0 |
| 2 | P2 | `B4_APPENDED` | `FAST_CREATED` | - | 0 | 0 |
| 3 | P3 | `B4_APPENDED` | `FAST_CREATED` | - | 0 | 0 |
| 4 | P4 | `B4_APPENDED` | `FAST_REPLACED` | P1 | 0 | 0 |
| 5 | P1 | `B4_APPENDED` | `FAST_REPLACED` | P2 | 0 | 0 |
| 6 | P2 | `B4_APPENDED` | `FAST_REPLACED` | P3 | 0 | 0 |
| 7 | P1 | `B4_APPENDED` | `FAST_UPDATED` | - | 1 | 1 |
| 8 | P1 | `B4_APPENDED` | `FAST_UPDATED` | - | 2 | 2 |
| 9 | P5 | `B4_APPENDED` | `FAST_REPLACED` | P4 | 2 | 2 |
| 10 | P6 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P2 | 2 | 2 |
| 11 | P7 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P1 | 2 | 2 |
| 12 | P8 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P5 | 2 | 2 |
| 13 | P9 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P6 | 2 | 2 |
| 14 | P10 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P7 | 2 | 2 |
| 15 | P11 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P8 | 2 | 2 |
| 16 | P3 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P9 | 2 | 2 |
| 17 | P4 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P10 | 2 | 2 |

Nach Schritt 4 enthaelt B4 exakt die Bildungsindizes 1 bis 4 und kann
`P1 -> P2 -> P3 -> P4` mit der vorhandenen read-only Folgenprobe
rekonstruieren. TSPM-1 meldet dafuer statisch
`NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE`; kein TSPM-Folgenoperator ist
zulaessig.

Nach Schritt 17 enthaelt B4 exakt die Bildungsindizes 9 bis 17 und damit
`P5, P6, P7, P8, P9, P10, P11, P3, P4`. TSPM-Fast enthaelt P11, P3 und P4.
P1 und P2 sind aus beiden kurzfristigen Sichten verschwunden.

Der visuelle und auditive P1-Slow-Prototyp ist jedoch nur mit Support 2
belegt und nicht stabil. P2 hat keinen Slow-Prototyp. Die finalen Befunde der
unveraenderten Regeln lauten daher:

| Ziel | `B4_RECENT` | `TSPM_FAST` | `TSPM_SLOW` |
| --- | --- | --- | --- |
| P1 | kein Treffer | kein Treffer | Prototyp Support 2, kein stabiler Treffer |
| P2 | kein Treffer | kein Treffer | kein stabiler Treffer |

Damit ist die verlangte Aussage "P1 ausschliesslich stabil in TSPM-Slow"
unter dieser Geschichte nicht materialisierbar.

## Read-only Probe- und Referenzplan

Ein spaeter korrigierter Plan darf genau folgende fachliche Proben verwenden:

1. nach Schritt 4 eine B4-Folgenprobe mit vier Vektoren P1 bis P4; GEORDNET
   muss annehmen, die reihenfolgeblinde Sicht dient nur der Inhaltskontrolle;
2. nach Schritt 17 je eine P1- und P2-Inhaltsprobe gegen den Composite-Zustand;
3. dieselben zwei Probeobjekte je einmal gegen Standalone-B4 und
   Standalone-TSPM.

Das sind sechs einzigartige Rezeptor-Probeinputs, sieben high-level
read-only Aufrufe und keine Zustandsfortschreibung. Die beiden
Standalone-Zustaende muessen nach jedem der 17 Schritte kanonisch exakt den
jeweiligen Composite-Teilzustaenden entsprechen. Abweichung bedeutet
`NOT_EVALUABLE`.

Eine einfache transaktionale Parallelhuelle, die dieselben reinen
Kandidatenzustandsfunktionen lokal berechnet, gemeinsam validiert und nur als
Paar veroeffentlicht, bleibt Engineeringbaseline. Reproduziert sie Zustand,
Abruf und Atomaritaet mit geringerem Aufwand, ist sie zu bevorzugen. Der
Koordinator begruendet keine neue Speicherfunktion.

## Ressourcenledger

Fuer den Composite-Arm gelten die in S2-FS materialisierten Obergrenzen:

| Umfang | Schreib-/Ergebniswoerter | Distanzterme | Kontrollterme |
| --- | ---: | ---: | ---: |
| 17 Formationen | 10489 | 7956 | 918 |
| zwei finale Composite-Inhaltsproben | 28, davon null Zustandswoerter | 936 | 96 |
| eine B4-Folgenprobe | null Zustandswoerter | 416 funktional + 416 validierend | 4 geordnete + 96 blind-pruefende Bits |

Die 17 Formationen enthalten 442 gemeinsame Projektionsterme, 4981
B4-Armwoerter, 4981 TSPM-Armwoerter und 527 Koordinatorwoerter. Native Kosten
bleiben zusaetzlich sichtbar: B4 benoetigt 459 Schreibwoerter; fuer TSPM-1
gilt die Obergrenze 4981.

Die Standalone-Komponentenreferenzen werden nicht dem Verbund kostenlos
zugerechnet. Ihre getrennte Formation besitzt die konservative Obergrenze
9962 Schreibwoerter und 7956 Distanzterme. Vier finale Standalone-Inhaltsproben
zaehlen weitere 936 Distanzterme und null Zustandswoerter. Recorder-,
Sollauswertungs- und Hasharbeit waere spaeter separat auszuweisen.

Der vollstaendige spaetere Operationsumfang waere:

- 23 einzigartige Rezeptoranalysen: 17 Formationen und sechs Probeinputs;
- 17 Composite-, 17 Standalone-B4- und 17 Standalone-TSPM-Formationen;
- 17 kanonische Komponenten-Gleichheitspruefungen;
- eine B4-Folgenprobe;
- zwei Composite- und vier Standalone-Inhaltsproben.

Ein fehlender Teil, ein Teilcommit, eine fremde Quelle oder ein unvollstaendiges
Ledger ergibt `NOT_EVALUABLE`. Fachlich falsche Abrufe bleiben dagegen
auswertbare Ergebnisse.

## Stoppentscheidung und kleinste Korrektur

`BLOCKED_STATIC_SEQUENCE_DOES_NOT_REACH_SLOW_SUPPORT_3`

Die exakt freigegebene 17-Schritt-Geschichte darf nicht implementiert oder
ausgefuehrt werden. Ihre positive Slow-Gegenprognose ist mit dem unveraenderten
TSPM-1-Zustand falsch.

Die kleinste inhaltlich saubere Korrektur ist eine 18-Schritt-Geschichte mit
einem fuenften P1-Auftritt nach dessen Fast-Neuanlage:

```text
P1, P2, P3, P4, P1, P2, P1, P1, P1,
P5, P6, P7, P8, P9, P10, P11, P3, P4
```

Dann erzeugen die P1-Schritte 7, 8 und 9 drei PPB-1-Aufrufe und Support 3;
die letzten neun B4-Eintraege bleiben P5 bis P11, P3 und P4. Alternativ waere
eine Aenderung der Fast-Kapazitaet noetig, die jedoch Kerne und Vergleichsstand
veraendern wuerde und deshalb nicht empfohlen wird.

Eine solche Sequenzaenderung benoetigt eine ausdrueckliche fachliche
Entscheidung. Bis dahin bleiben Fixtures, Implementierung, Tests und Lauf
gesperrt. Auch ein spaeteres Bestehen waere nur ein begrenzter technischer
Verbundbefund, kein Langzeit-Memory-, Semantik-, Kontext- oder Feldnachweis.
