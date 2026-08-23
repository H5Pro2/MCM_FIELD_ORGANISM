# S1-VM: PPB-1 statischer Parameterwahl-, Baseline- und Ausfuehrungsmatrixvertrag

## Auftrag und Grenze

S1-VM bindet vor jeder weiteren Ausfuehrung eine endliche synthetische
Auswahlmatrix fuer die private PPB-1-Engineeringkomponente. Der Vertrag soll
nicht bestaetigen, dass PPB-1 eine besondere Feldfunktion besitzt. Er soll
entscheiden, ob innerhalb der S1-VK-Korridore eine transparente technische
Konfiguration fuer getrennte reduzierte auditive und visuelle Zustaende
gegen einfachere Speicher- und Fortschreibungsformen bestehen kann.

S1-VM enthaelt:

- genau ein vorhandenes synthetisches Rezeptorprofil;
- drei vorab festgelegte Parameterrecords;
- acht labelfreie numerische Verlaufstypen pro Modalitaet;
- sieben faire Vergleichsadapter;
- Messgroessen, Entscheidungsfolge, Budget und Stoppregeln.

S1-VM implementiert und startet keinen Runner. Feldkern, Medienpfade,
`current_api`, Root-Exports, Snapshot und persistente Artefakte bleiben
unveraendert.

## Gebundenes Profil

Die spaetere synthetische Auswahl verwendet ausschliesslich das bereits
vorhandene Profil `controlled`:

```text
auditory.log12.50-1500.w400.h40.v1
visual.grid6x4.channels3.source24x16.v1
```

Damit werden 12 auditive und 72 visuelle Traeger geprueft. Das Profil ist
gross genug fuer getrennte Dimensionspruefungen, ohne einen Browser-,
oeffentlichen oder Live-Medienpfad zu starten. Die in S1-VL bereits
bestandene Skalierungspruefung der anderen drei Profile wird nicht
wiederholt und nicht als Auswahldatensatz verwendet.

## Drei feste Parameterrecords

Alle Werte liegen innerhalb der S1-VK-Korridore. Die Record-IDs bezeichnen
nur technische Konfigurationen und keine Qualitaetsstufen.

### Record P0

| Parameter | auditiv | visuell |
|---|---:|---:|
| Kapazitaet | 8 | 4 |
| Matchschwelle | 0,04 | 0,03 |
| Aktualisierungsrate | 0,10 | 0,10 |
| Stabilisierung nach Supports | 4 | 4 |
| Ablauf nach Bankschritten | 512 | 128 |

### Record P1

| Parameter | auditiv | visuell |
|---|---:|---:|
| Kapazitaet | 16 | 8 |
| Matchschwelle | 0,08 | 0,06 |
| Aktualisierungsrate | 0,20 | 0,20 |
| Stabilisierung nach Supports | 4 | 4 |
| Ablauf nach Bankschritten | 1.024 | 256 |

### Record P2

| Parameter | auditiv | visuell |
|---|---:|---:|
| Kapazitaet | 32 | 16 |
| Matchschwelle | 0,16 | 0,12 |
| Aktualisierungsrate | 0,40 | 0,40 |
| Stabilisierung nach Supports | 8 | 6 |
| Ablauf nach Bankschritten | 2.048 | 512 |

Es ist unzulaessig, nach Sichtung eines Ergebnisses Zwischenwerte zu bilden,
einzelne Parameter auszutauschen oder einen vierten Record hinzuzufuegen.
Die spaetere Entscheidung darf genau P0, P1, P2 oder keinen Record waehlen.

## Labelfreie Vektorkonstruktion

Jeder Verlauf wird direkt in der zum Profil gehoerenden Traegerdimension
erzeugt. Er enthaelt keine Woerter, Klassen, Objektkennungen oder
Medienbedeutung. Technische Fixture-IDs sind nur Provenienzrollen.

Die Konstruktion verwendet ausschliesslich endliche normalisierte Werte im
Bereich null bis eins:

- `v_low`: alle Komponenten 0,20;
- `v_high`: alle Komponenten 0,80;
- `v_near_minus` und `v_near_plus`: symmetrische kleine Abweichungen um
  `v_low`, jeweils innerhalb der kleinsten gebundenen Matchschwelle;
- `v_mid`: komponentenweiser Mittelpunkt von `v_low` und `v_high`;
- `v_fill_i`: deterministisch aus Fixture-Index und Traegerindex erzeugte,
  paarweise getrennte Fuellvektoren;
- `v_drift_i`: neun monotone Zwischenschritte von `v_low` in Richtung
  `v_high`.

Die exakten Vektordigests und Generatorregeln muessen ein spaeterer Runner
vor seinem ersten Kernaufruf materialisieren und im Receipt binden. Kein
Vektor darf aus einem Laufresultat abgeleitet werden.

## Acht gebundene Verlaufstypen

Jeder Typ wird fuer beide Modalitaeten und alle drei Parameterrecords
getrennt aus einem frischen Zustand gestartet.

| ID | Verlauf | Primaere technische Frage |
|---|---|---|
| F01 | acht identische `v_low`, danach identische Probe | entsteht bei exakter Wiederholung genau eine stabile Zuordnung? |
| F02 | `v_low`, vier alternierende Nahvarianten, danach `v_low` | bleiben kleine Abweichungen derselben lokalen Zuordnung zugeordnet? |
| F03 | vier Wechsel `v_low`/`v_high`, danach beide Proben | bleiben zwei deutlich getrennte wiederkehrende Zustaende getrennt? |
| F04 | `v_low`, `v_high`, danach `v_mid` | ist der Konflikt deterministisch und ohne versteckte Reihenfolgeinformation? |
| F05 | neun Driftvektoren, danach Randproben | wie stark verschiebt Aktualisierung einen technischen Prototyp? |
| F06 | Kapazitaet Fuellvektoren, ein weiterer Vektor, erste Probe | sind Vollbelegung und LRU-Ersetzung endlich und nachvollziehbar? |
| F07 | `v_low`, inaktive Fuellschritte bis zur exakten Ablaufgrenze, Probe | wird ein faelliger Slot vor der Zuordnung vollstaendig freigegeben? |
| F08 | `v_low`, inaktive Fuellschritte bis einen Schritt vor Ablauf, Probe | bleibt eine noch nicht faellige Zuordnung erhalten? |

Die Fuellschritte fuer F07 und F08 duerfen den geprueften Slot nicht
auswaehlen. Sollte dies fuer einen Record nicht konstruktiv erreichbar sein,
ist der Fall methodisch ungueltig und der gesamte Record wird nicht
ausgewertet.

## Faire Kausalhistorie

PPB-1 und jeder zustandsbehaftete Vergleichsadapter erhalten pro Matrixfall:

- denselben frischen Start;
- dieselbe Modalitaet und Dimension;
- dieselbe geordnete Vektorfolge;
- dieselben technischen Schrittgrenzen;
- dieselbe Kapazitaetsobergrenze, soweit der Adapter mehrere Eintraege
  besitzt;
- denselben spaeteren Probevektor.

Kein Adapter darf nur die Endprobe erhalten, wenn PPB-1 vorher die
Bildungsgeschichte gesehen hat. Baselinestates werden nie zwischen
Parameterrecords, Modalitaeten oder Verlaufstypen wiederverwendet.

## Sieben Vergleichsadapter

| ID | Baseline | Gebundene Grenze |
|---|---|---|
| B01 | begrenztes Rezeptorvektor-Replay | behaelt hoechstens so viele letzte Vektoren, wie PPB-1 Prototypslots besitzt; keine Rohmedien |
| B02 | ein gleitender Mittelwert | genau eine modalitaetseigene verdichtete Spur mit der jeweiligen Aktualisierungsrate |
| B03 | feste Prototypliste | gleiche Slotkapazitaet und Distanz, aber keine Aktualisierung, Stabilisierung oder Ablaufregel |
| B04 | einzelne exponentiell fortgeschriebene Spur | gleicher Aktualisierungsanteil, genau ein Zustand, naechste-Distanz-Readout |
| B05 | begrenzte Leaky-Spur | eine endliche abklingende Vektorspur ohne Prototypkonkurrenz |
| B06 | begrenzter Integrator | ein geklammerter Vektorakkumulator ohne Prototypkonkurrenz |
| B07 | PPB-OFF | kein privater Zustand und kein spaeterer Zuordnungsreadout |

B05 und B06 sind reine private Vektoradapter fuer den Vergleich derselben
synthetischen Geschichte. Sie duerfen weder das aktive Feld noch historische
Kandidatenruntimes importieren. Ein Vergleich mit schnellem Feldnachhall
oder Feldintegrator wird erst in einem eigenen spaeteren Integrationsvertrag
zulaessig; S1-VM behauptet keine formale Gleichheit dieser Adapter mit dem
aktiven Feld.

## Messgroessen

Jeder Fallrecord muss mindestens enthalten:

- Config-, Fixture-, Eingangsfolgen-, Vorzustands- und Ergebnisdigest;
- Ereignisfolge aus Bildung, Match, Freigabe und Ersetzung;
- belegte Slotzahl und stabilisierte Slotzahl;
- gewaehlte Slot-ID oder explizit keinen Match;
- normalisierte L1-Distanz der Probe zum gewaehlten Zustand;
- Anzahl fehlerhafter Verschmelzungen deutlich getrennter Anker;
- Anzahl fehlerhafter Trennungen der gebundenen Nahvarianten;
- Prototypverschiebung gegen seinen Bildungswert;
- vollstaendige Freigabe an F07 und Erhalt an F08;
- logische gespeicherte Vektorwerte und akzeptierte Adapteraufrufe.

Immer-Match und Nie-Match werden nur auf den diagnostischen Proben F02 bis
F05 beurteilt. F01 ist absichtlich eine exakte Wiederholung; F06 bis F08
pruefen Lebenszyklusgrenzen.

## Matrix und Ausfuehrungsbudget

Die PPB-Matrix besitzt genau:

```text
3 Parameterrecords * 2 Modalitaeten * 8 Verlaufstypen = 48 PPB-Faelle
```

Jeder der sieben Vergleichsadapter erhaelt dieselben 48 Faelle:

```text
48 PPB-Faelle + 336 Baselinefaelle = 384 Fallrecords
```

Aus den festen Verlaufslangen, Kapazitaeten und Ablaufgrenzen folgen
hoechstens:

```text
9.296 akzeptierte PPB-Kernaufrufe
65.072 akzeptierte Baselineadapteraufrufe
74.368 akzeptierte Aufrufe insgesamt
```

Fehlgeschlagene Vorvalidierungen zaehlen nicht als akzeptierter Aufruf und
duerfen nicht automatisch wiederholt werden. Es gibt keine Replikation,
keine Zufallsziehung und keine adaptive Verlaengerung. Laufzeitmessung ist
nicht Teil dieser Matrix.

## Entscheidungsfolge

Die spaetere Auswertung erfolgt strikt in dieser Reihenfolge:

1. Schema, Digests, Fallzahl, Aufrufbudget und Frischstarts muessen bestehen.
2. F01, F07 und F08 muessen die bereits implementierten Lebenszyklusregeln
   exakt bestaetigen.
3. Ein Record mit Immer-Match oder Nie-Match auf F02 bis F05 wird verworfen.
4. Deutlich getrennte Anker duerfen in F03 nicht verschmolzen werden.
5. Gebundene Nahvarianten duerfen in F02 nicht unnoetig vervielfacht werden.
6. F04 bis F06 muessen deterministisch und bei Wiederholung bitgleich sein.
7. Erst danach werden PPB-Records gegen B01 bis B07 verglichen.
8. Unter den verbleibenden technisch gleichwertigen Records gewinnt der mit
   weniger Slots und weniger gespeicherten Vektorwerten.

Die einzige zulaessige Auswahl lautet `P0`, `P1`, `P2` oder
`NO_ADMISSIBLE_CONFIGURATION`. Audio und Video duerfen unterschiedliche
Records erhalten.

## Stopp- und Vereinfachungsregeln

Ein Parameterrecord wird verworfen, wenn mindestens eine der folgenden
Bedingungen eintritt:

- unvollstaendige oder nicht faire Kausalhistorie;
- Ueberschreitung von Fallzahl oder Aufrufbudget;
- nicht deterministisches Ergebnis bei identischem Start und Eingang;
- Immer-Match oder Nie-Match auf den diagnostischen Proben;
- Verletzung von Kapazitaet, Ablauf, Atomaritaet oder Modalitaetstrennung;
- Ergebnisabhaengige Fixture- oder Parameteranpassung.

PPB-1 wird auf die einfachere Baseline reduziert oder entsprechend
vereinfacht, wenn B01, B02, B03, B04, B05 oder B06 alle fuer PPB bestandenen
technischen Fragen mit nicht groesserem Zustands- und Aufrufbudget ebenfalls
beantwortet. B07 prueft nur, ob der private Zustand ueberhaupt einen
technischen Readoutunterschied erzeugt.

Wenn kein Record fuer eine Modalitaet verbleibt, wird fuer diese Modalitaet
keine weitere PPB-Integration freigegeben. Das Ergebnis ist eine
Engineeringentscheidung und kein Befund ueber eine endogene Feldursache.

## Claim- und Integrationsgrenze

Auch ein bestandener Record erlaubt nur die Aussage, dass eine begrenzte
private Prototypbank in den vorregistrierten synthetischen Faellen einen
bestimmten technischen Zuordnungs- und Lebenszyklusumfang erfuellt.

Ausgeschlossen bleiben Aussagen zu Semantik, Objektkenntnis, Verstehen,
Bewusstsein oder biologischer Funktion. Ebenso ausgeschlossen bleiben eine
oeffentliche Memory-Faehigkeitsbehauptung, Feldintegration, Snapshotzustand,
Persistenz und reale Audio-/Video-Ausfuehrung.

## Vertragsentscheidung

```text
S1_VM_CONTROLLED_12_72_PROFILE_ONLY_BOUND
S1_VM_THREE_FIXED_PARAMETER_RECORDS_BOUND
S1_VM_EIGHT_LABEL_FREE_HISTORIES_PER_MODALITY_BOUND
S1_VM_SEVEN_FAIR_BASELINE_ADAPTERS_BOUND
S1_VM_48_PPB_AND_336_BASELINE_CASES_BOUND
S1_VM_74368_ACCEPTED_CALL_TOTAL_LIMIT_BOUND
S1_VM_DETERMINISM_SIMPLICITY_AND_STOP_ORDER_BOUND
S1_VM_NO_RUNNER_NO_EXECUTION_NO_FIELD_OR_MEDIA_CHANGE
S1_VM_STATIC_ENGINEERING_MATRIX_ADMISSIBLE
```

S1-VM bindet eine ausfuehrbare, aber noch nicht ausgefuehrte
Engineeringmatrix. Es liegt kein Parameterergebnis und kein Eignungsbefund
vor.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-VN - private Implementierung der synthetischen Fixturegeneratoren,
        sieben Vergleichsadapter und des gebundenen 384-Fall-Runners
```

S1-VN darf den Runner und seine Vertragstests implementieren, aber die
384-Fall-Matrix noch nicht ausfuehren. Vor einer Ausfuehrung muessen
Fallregister, Digests, exakte Aufrufzaehlung, Frischstarts und
Fail-Closed-Verhalten synthetisch abgenommen sein. Feldkern, Medienruntime,
API und Snapshot bleiben unberuehrt.

## Grundlagen

- [S1-VL privater Rezeptorprofilbinder](S1VL_PPB1_PRIVATER_REZEPTORPROFILBINDER_UND_DIMENSIONSSKALIERTE_SYNTHETISCHE_ABNAHME.md)
- [S1-VK Rezeptorbindungs- und Skalierungsaudit](S1VK_PPB1_STATISCHER_REZEPTORBINDUNGS_SKALIERUNGS_UND_PARAMETERKORRIDORAUDIT.md)
- [S1-VJ privater PPB-1-Referenzkern](S1VJ_PPB1_PRIVATER_REINER_REFERENZKERN_UND_SYNTHETISCHE_VERTRAGSABNAHME.md)
- [S1-VH PPB-1-Engineeringvertrag](S1VH_PPB1_STATISCHER_ENGINEERING_FUNKTIONS_SICHERHEITS_UND_INTEGRATIONSVERTRAG.md)
