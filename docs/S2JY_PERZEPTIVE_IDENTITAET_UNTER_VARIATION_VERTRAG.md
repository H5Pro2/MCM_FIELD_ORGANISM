# S2-JY - Perzeptive Identitaet unter Variation

## Status und Zweck

`S2JY_STATIC_FUNCTION_AND_FALSIFICATION_CONTRACT_COMPLETE`

S2-JY bindet genau eine begrenzte Folgepruefung fuer die Frage:

> Kann derselbe audiovisuelle Wahrnehmungsinhalt trotz kleiner, vorab
> festgelegter sensorischer Veraenderung gemeinsam verdichtet werden, waehrend
> ein klar anderer Inhalt getrennt bleibt?

Dieser Vertrag implementiert und startet nichts. Er fuehrt keine Rezeptor-,
Memory-, Kontext- oder Feldfunktion aus. S2-JX bleibt als feste Referenz
unveraendert; insbesondere werden seine Ergebnisdatei, Schwellen und Befunde
nicht neu ausgewertet.

## Eingefrorene Grundlage

Basis ist Commit `15c14b7` mit dem bestaetigten S2-JX-Befund
`S2JX_FUNCTION_CONFIRMED`.

| Bindung | Wert |
| --- | --- |
| S2-JX-Resultdigest | `d3cc6abd714bcba9c06fec4ff14722fe239394f3cae0979a7c94bdf9d283af35` |
| S2-JX-Dateidigest | `0ed7b62c873603feefde3e5cf4ed949cfc1323ff36e0adc22d58a4ccc8a92547` |
| Default-Live-Quellprofil | `fa6bc21e216068e6d2d02ab016d083d7456819c4505db4db8161b8ec03e5f0f5` |
| PPB-1-Kern | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| TSPM-1-Kern | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| B4-Operator | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |

Unveraendert gelten:

- 48 auditive und 288 visuelle Rezeptorwerte;
- B4-Kapazitaet 9, TSPM-Fast-Kapazitaet 3;
- PPB-Kapazitaeten 8 auditiv und 4 visuell;
- TSPM-Fast-Schwellen `0,2/0,2`, Aktualisierungsfaktor `0,5` und
  Konsolidierung ab Fast-Support 2;
- PPB-Schwellen `0,02` auditiv und `0,01` visuell,
  Aktualisierungsfaktor `0,05` und Stabilitaet ab Support 3.

Diese Schwellen sind mechanische Bestandsparameter. S2-JY kalibriert sie
nicht und behauptet keine allgemeine Wahrnehmungsmetrik fuer 336 Werte.

## Prospektive Rohfixtures

Alle Bilder sind echte `1920 x 1080 x 3`-`uint8`-Frames. Alle Audiofenster
sind echte 4.800-Sample-`PCM_F32LE`-Fenster und werden in zehn geordnete
480-Sample-Hops zerlegt. Die unveraenderten Default-Live-Rezeptoren erzeugen
die funktionalen 48+288-Werte; handgeschriebene Rezeptorvektoren sind
unzulaessig.

### Referenz R0

R0 ist die bestehende S2-JV-X-Fixture:

- visueller Carrier `i`: Byte 255 genau dann, wenn
  `i mod 11 in {1,3,4,5,9}`, sonst Byte 0;
- auditives Fenster: 50-Hz-Rechtecksignal mit Periodenlaenge 960 und den
  exakt darstellbaren Samples `+0,5/-0,5`.

Die bekannten Roh- und Rezeptorwertedigests aus S2-JV bleiben verbindlich.

### Exakte Kontrolle E0

E0 ist bitidentisch zu R0. Nur Quellordinalzahl, Zeitfenster und deren
technische Digests unterscheiden die einzelnen Expositionen. Diese Felder
duerfen keine Matchentscheidung beeinflussen.

### Kleine visuelle Variation V1

V1 behaelt Carrierordnung und Blockgeometrie von R0. Jeder konstante
Nullblock erhaelt Byte 2, jeder konstante 255-Block Byte 253. Der reale
Rezeptor liefert daher je Carrier `2/255` beziehungsweise `253/255`.

Damit gilt vorab exakt:

```text
d_visual(R0,V1) = 2/255 = 0,00784313725490196 < 0,01 < 0,2
d_auditory(R0,V1) = 0
```

V1 ist eine kleine globale Kontrastkompression bei unveraenderter
Ortsanordnung, keine neue Bildklasse.

### Kleine auditive Variation A1

A1 behaelt Frequenz, Phase, Periodenlaenge und Hopgrenzen von R0. Nur die
Amplitude wird auf die einmalig kanonisch als `float32 little-endian`
kodierten Werte `+0,495/-0,495` gesetzt. Der verwendete exakte Samplewert ist
das Ergebnis von `unpack('<f', pack('<f', 0.495))`; eine spaetere
Dezimalrundung ist unzulaessig.

Der Log-Spektralrezeptor ist fuer diese reine Skalierung linear in der
Amplitude. Fuer jeden auditiven Carrier gilt deshalb prospektiv
`A1_i = scale * R0_i`, wobei `scale` aus dem gebundenen Float32-Sample und
`0,5` exakt abgeleitet wird. Da gueltige Rezeptorwerte in `[0,1]` liegen,
gilt:

```text
d_auditory(R0,A1) < 0,01 < 0,02 < 0,2
d_visual(R0,A1) = 0
```

Der konkrete 48er-Abstand wird vor dem ersten Memoryaufruf aus den realen
Rezeptorabschluessen aufgezeichnet; er darf nicht zur Schwellenwahl dienen.

### Kombinierte Variation C1

C1 kombiniert genau das V1-Bild und das A1-Audiofenster. Daher gelten beide
oben gebundenen modalen Grenzen gleichzeitig. Es werden keine weiteren
Veraenderungen addiert.

### Getrennter Distraktor Z1

Z1 ist exakt die vorhandene, reale S2-JV-D1-Fixture mit visueller Ordinalzahl
2 und auditiver Periodenlaenge 400 (120 Hz). Aus der S2-JV-Materialisierung
gelten:

```text
d_visual(R0,Z1) = 13/24 = 0,541666... > 0,2
d_auditory(R0,Z1) >= 0,046051827674693784 > 0,02
```

Die visuelle Distanz erzwingt bereits eine getrennte Fast-Zuordnung. Die
auditive Untergrenze erzwingt auch in der auditiven PPB-Bank eine getrennte
Prototypspur. Z1 ist keine Grenzfixture und darf nicht nachtraeglich ersetzt
werden.

## Receptorischer Vorababschluss

Vor dem ersten Memoryzustand muessen alle fuenf Fixture-Rollen aus ihren
Rohbytes durch die unveraenderten Rezeptoren materialisiert werden. Gebunden
werden je Rolle:

- Rohpayloaddigests, Geometrie, Carrierreihenfolge und Zeitrollen;
- 48er- und 288er-Rezeptorwertedigest;
- getrennte auditive und visuelle mittlere L1-Distanz zu R0;
- Einhaltung der oben festgelegten Intervalle.

Ein Form-, Digest- oder Distanzbruch vor diesem Abschluss ergibt
`START_BLOCKED_FIXTURE_MATERIALIZATION`. Es entsteht dann kein Memorylauf und
kein funktionaler Befund. Nach bestandenem Vorababschluss sind Fixture,
Schwellen, Geschichten und Erfolgsregeln unveraenderlich. Eine spaetere
funktionale Abweichung darf nicht als Fixturefehler umgedeutet werden.

## Fuenf frische Geschichten

Jede Geschichte beginnt mit einem eigenen frischen B4-/TSPM-/PPB-Verbund.
Rollenbezeichnungen und Erwartungen sind Auswertungsmetadaten und werden
weder Rezeptor noch Memory uebergeben.

| Geschichte | Vier Formationen | Read-only Proben |
| --- | --- | --- |
| G0 Exaktkontrolle | `R0, E0, R0, E0` | `R0` |
| G1 visuell | `R0, V1, R0, V1` | `R0, V1` |
| G2 auditiv | `R0, A1, R0, A1` | `R0, A1` |
| G3 kombiniert | `R0, C1, R0, C1` | `R0, C1` |
| G4 Distraktor | `R0, Z1, R0, Z1` | `R0, Z1` |

Das ergibt exakt 20 Formationen und neun Proben. Quellfenster steigen
innerhalb jeder Geschichte strikt an. Geschichten teilen weder Zustand,
Owner, Zeitlinie noch Slotidentitaet.

## Vorab gebundene mechanische Erwartungen

### G0 bis G3: eine gemeinsame Erfahrung

1. Formation 1 erzeugt einen neuen Fast-Slot.
2. Formationen 2 bis 4 aktualisieren denselben Fast-Slot.
3. Jede Aktualisierung loest genau einen auditiven und einen visuellen
   PPB-Schritt aus.
4. Der erste PPB-Schritt erzeugt je Modalitaet einen Prototyp mit Support 1.
5. Die naechsten zwei PPB-Schritte aktualisieren denselben Prototyp auf
   Support 2 und 3.
6. Nach Formation 4 existiert je Modalitaet genau ein zur Geschichte
   gehoerender stabiler Slow-Prototyp.
7. Beide gebundenen Probevarianten werden demselben Fast- und demselben
   stabilen Slow-Inhalt zugeordnet.

Die Konvexitaet der L1-Distanz bindet, dass die vorhandenen Fast- und
PPB-Aktualisierungen zwischen R0 und der jeweiligen kleinen Variation die
vorab festgelegten modalen Maximalabstaende nicht vergroessern.

### G4: zwei getrennte Erfahrungen

1. Formation 1 erzeugt den R0-Fast-Slot, Formation 2 einen anderen Z1-Slot.
2. Formation 3 aktualisiert ausschliesslich R0, Formation 4 ausschliesslich
   Z1.
3. Beide Fast-Slots erreichen Support 2 und loesen je genau einen
   Konsolidierungsschritt aus.
4. In jeder PPB-Bank entstehen zwei verschiedene instabile Slots mit Support
   1; kein Slot ist stabil.
5. Die R0- und Z1-Proben werden verschiedenen Fast-Slots zugeordnet und
   liefern keinen oeffentlichen stabilen Slow-Treffer.

## Vier getrennte Messebenen

Jede Formation protokolliert ohne Rohwerteverdopplung:

1. **Rezeptordistanz:** getrennte auditive und visuelle L1-Distanz zur
   R0-Referenz sowie die Wertedigests.
2. **Fast-Zuordnung:** `FAST_CREATED`, `FAST_UPDATED` oder andere tatsaechliche
   native Ereignisse, Slot-ID, Vor-/Nachslotdigest und native Distanzen.
3. **Slow-Aktualisierung:** ob Konsolidierung ausgeloest wurde; auditive und
   visuelle PPB-Ereignisse, Slots, Support und Stabilitaet getrennt.
4. **Slotneubildung:** neue, aktualisierte oder ersetzte Slots in Fast,
   auditivem Slow und visuellem Slow, ausschliesslich aus validiertem
   Vor-/Nachzustand und nativen Receipts.

Jede Probe protokolliert B4, Fast, Slow auditiv und Slow visuell getrennt,
einschliesslich Distanzen, Support und Stabilitaet. Vor- und
Nachzustandsdigest muessen identisch sein.

## Direkte L1-/Prototypbaseline

Eine unabhaengige read-only Baseline erhaelt dieselben bereits erzeugten
Rezeptorwerte und die tatsaechlich vor der jeweiligen Operation vorhandenen
Prototypwerte. Sie:

- berechnet `normalized_mean_l1_distance` getrennt je Modalitaet;
- wendet nur die eingefrorenen Fast- und PPB-Schwellen an;
- bildet keine Slots, veraendert keinen Support und entscheidet keine
  Memoryrolle;
- kennt keine Geschichte, Sollklasse oder erwartete Entscheidung;
- wird fuer jede Formation und Probe genau einmal ausgewertet.

Baseline und Memory muessen bei Distanz und Schwellenvergleich
uebereinstimmen. Eine Abweichung bei vollstaendigen Belegen ist eine
funktionale beziehungsweise instrumentelle Falsifikation und kein Anlass zur
nachtraeglichen Schwellenanpassung.

## Endlicher Umfang und Budgets

| Rolle | Anzahl beziehungsweise Grenze |
| --- | ---: |
| Geschichten | 5 |
| RGB8-Frames | 29 |
| PCM-Hops | 290 |
| visuelle Rezeptoraufrufe | 29 |
| auditive `push`-Aufrufe | 290 |
| Formationen | 20 |
| read-only Proben | 9 |
| Memory-Top-Level-Operationen, vier je Formation/Probe | 116 |
| direkte Baselineaufrufe | 29 |
| ausgewaehlte reduzierte Rezeptorwerte | 9.744 |
| gestreamte RGB8-Bytes | 180.403.200 |
| gestreamte PCM-Bytes | 556.800 |
| gestreamte Rohbytes gesamt | 180.960.000 |
| maximal gleichzeitig Frame plus Hop | 6.222.720 Bytes |
| maximaler numerischer Memoryzustand je Geschichte | 44.544 Bytes |
| Memory-L1-Obergrenze fuer 20 Formationen | 71.040 Terme |
| Memory-L1-Obergrenze fuer neun Proben | 82.080 Terme |
| Memory-L1-Obergrenze gesamt | 153.120 Terme |
| getrennte Baseline-L1-Obergrenze | 153.120 Terme |

Die L1-Werte sind konservative, profilabgeleitete Obergrenzen, keine
Behauptung tatsaechlich ausgefuehrter Terme. Der spaetere Lauf muss native
Istkosten und Obergrenzen getrennt berichten. Rohframes und PCM-Hops werden
einzeln gestreamt, nach Rezeptorreduktion verworfen und niemals in Memory,
Receipt oder Ergebnisdatei gespeichert.

## Auswertung und Falsifikation

`S2JY_VARIATION_IDENTITY_CONFIRMED` ist nur zulaessig, wenn gemeinsam gilt:

- G0 reproduziert die exakte Wiederholungskontrolle;
- G1, G2 und G3 bilden jeweils einen gemeinsamen Fast-Inhalt und je einen
  stabilen auditiven und visuellen Slow-Prototyp mit Support 3;
- beide Proben jeder Variationsgeschichte werden diesem gemeinsamen Inhalt
  zugeordnet;
- G4 bildet getrennte R0-/Z1-Fast-Slots und keine stabile gemeinsame
  Slow-Identitaet;
- Memory und direkte Baseline stimmen bei allen nativen Distanz- und
  Schwellenentscheidungen ueberein;
- alle neun Probezugriffe sind vollstaendig read-only.

Ein technisch vollstaendiger Lauf, der mindestens eine dieser Regeln
verfehlt, endet als `S2JY_VARIATION_IDENTITY_FALSIFIED`. Er darf weder als
Infrastrukturfehler umgedeutet noch mit geaenderten Schwellen wiederholt
werden.

`NOT_EVALUABLE` ist ausschliesslich fuer Quellen-, Reihenfolge-, Owner-,
Digest-, Receipt-, Ledger-, Zustandsunveraenderlichkeits- oder
Aufzeichnungsbruch zulaessig. Fachlich falsche Zuordnungen bleiben
auswertbare Ergebnisse.

## Unveraenderliche Grenzen

- keine Aenderung an B4, TSPM-1, PPB-1 oder den Default-Live-Rezeptoren;
- keine neue Memoryebene, Kompression, Kontextauswahl oder Feldrueckwirkung;
- kein Feldsnapshot als Memoryeingang;
- keine Browser-, Kamera- oder Mikrofonbehauptung;
- keine Labels, Sollwerte oder Provenienzmetadaten als Matchinput;
- keine nachtraegliche Schwellen-, Fixture- oder Erfolgsregelanpassung;
- keine Wiederholung ohne neuen prospektiven Vertrag und neue Freigabe.

Der naechste konkrete Schritt ist eine kleine private Fixture-/Messadapter-
Implementierung mit neutraler Qualifikation. Erst danach darf genau ein Lauf
der fuenf gebundenen Geschichten separat freigegeben werden.
