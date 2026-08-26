# S1-BV: E1 eingefrorener identischer E2-Probevertrag

## Status

Statischer Kausal- und Vorregistrierungsvertrag. Noch keine Implementierung,
kein Lauf, keine transiente AV-Kopplung und kein Memory-, Lern-, Organismus-
oder KI-Befund.

## Forschungsfrage

Koennen zwei kontrollierte, energie- und zeitangeglichene Feldgeschichten aus
demselben neutralen E1-Anfangszustand unterschiedliche lokale
Kantenbindungen erzeugen, die bei spaeter exakt identischem S/H-Feld und
identischer Probe eine unterschiedliche Feldfortsetzung verursachen?

## Harte Interpretationsgrenze

Waehrend einer eingefrorenen Probe ist ein E1-Zustand funktional ein fester
raeumlicher Gain. Ein positiver Probeunterschied widerlegt diese Erklaerung
nicht.

Der zulaessige E2-Befund lautet deshalb nur:

```text
kontrollierte unterschiedliche Geschichte
-> unterschiedliche endliche E1-Kantenverteilung
-> kausale unterschiedliche spaetere Feldfortsetzung
```

Nicht zulaessig waeren daraus unmittelbar die Begriffe Memory, Erinnerung,
Semantik, Organisation oder neue MCM-Natur.

## Getrennte Versuchsdatei

Die spaetere Implementierung liegt ausserhalb der Runtime in:

```text
mcm_field_organism/e1_frozen_history_probe.py
tests/test_e1_frozen_history_probe.py
```

Sie wird weder aus `__init__` noch aus `current_api` exportiert und besitzt
keinen Browser-, Audio-, Video- oder Snapshotpfad.

## Gemeinsamer Anfang

Beide Geschichtsarme beginnen objektgetrennt, aber wertidentisch mit:

```text
gleiche Drei-Knoten-Liniengeometrie
gleiches S_0 und H_0
gleicher neutraler E1-Zustand b_e = 0
gleicher E1-Vertrag
gleiche Feld-, Nachhall- und Zeitkonfiguration
gleiche Zahl und Dauer der Kontaktintervalle
```

Zwischen den Armen wird kein veraenderliches Objekt geteilt.

## Kontrolliertes Spiegelpaar der Geschichte

Der erste E2-Korridor verwendet zwei synthetische Spiegelgeschichten auf der
Drei-Knoten-Linie:

```text
Geschichte L je Kontakt: (1.0, 0.0, 0.0)
Geschichte R je Kontakt: (0.0, 0.0, 1.0)
```

Beide besitzen pro Intervall exakt dieselbe:

- Anzahl aktiver Rezeptorwerte;
- Amplitudenmenge;
- quadratische Energie;
- Dauer und gemeinsame Uhr;
- Wiederholungszahl;
- Feld- und E1-Konfiguration.

Nur die gespiegelte geometrische Lage unterscheidet sich. Labels `L` und `R`
sind ausschliesslich Versuchsarmnamen und werden der E1-Mechanik nicht
uebergeben.

## Feste Geschichtsdauer

Vor dem Lauf wird genau eine technische Hauptdauer festgelegt:

```text
n_history = 8 identische Kontaktintervalle pro Arm
```

Die Zahl acht ist eine Versuchsdauer, kein Wiederholungszaehler im
Organismuszustand und keine Speicherregel. Es wird nicht anhand des
Ergebnisses verlaengert.

Beide Geschichten werden mit der aktiven synchronen S1-BU-Kopplung erzeugt.
Danach werden ausschliesslich die beiden E1-Endzustaende `b_L` und `b_R`
weitergegeben. Die unterschiedlichen S/H-Endfelder der Geschichte werden
nicht in die Probe uebernommen.

## Erforderliche Spiegelkontrolle

Vor jeder Probe muss statisch gelten:

```text
Gesamtbindung(b_L) == Gesamtbindung(b_R) innerhalb Numeriktoleranz
b_R == geometrische Spiegelung von b_L innerhalb Numeriktoleranz
b_L != b_R in kanonischer Kantenreihenfolge
```

Scheitert diese Kontrolle, ist der Versuch ungueltig. Ein Probevergleich darf
dann nicht interpretiert werden.

## Exakte S/H-Angleichung

Die Probe verwendet objektgetrennte Kopien genau eines frisch gebauten und
nach S1-BY neutral vorbereiteten kanonischen Feldes `F*`:

```text
S_L* == S_R* elementweise
H_L* == H_R* elementweise
gleiche Neuronen-, Dock- und Geometrieidentitaet
gleicher Tick und gleiche gemeinsame Uhr
gleicher letzter abgeschlossener Kontaktzustand
gleicher Snapshot-Digest vor der Probe
```

`F*` stammt nicht aus einem der beiden Geschichts-Endfelder. Dadurch kann
keine S/H-Restamplitude aus der Geschichte in die Probe gelangen.

Die feste asymmetrische Probe lautet im ersten Korridor:

```text
Probe P: (0.75, -0.25, 0.25)
```

Eine asymmetrische Probe ist erforderlich, weil ein vollstaendig uniformes
oder spiegelsymmetrisches Feld gespiegelte Kantenraten nicht unterscheiden
muss. Die Probe wird vor dem Lauf festgelegt und nicht auf maximale
Armtrennung optimiert.

## Eingefrorener E1-Probeoperator

Die Probe darf die S1-BU-Funktion nicht direkt verwenden, weil diese E1 vor
und nach dem Feldschritt weiterentwickelt. Stattdessen wird ein reiner
Interventionsoperator spezifiziert:

```text
advance_frozen_e1_probe(
    field,
    frozen_e1_state,
    distribution,
    step_time,
    substrate_config,
    afterimage_config,
    dissipation_config=None,
    *,
    backreaction_enabled,
) -> FrozenE1ProbeResult
```

Er:

1. validiert Feld und E1-Geometrie;
2. bildet den Adapter direkt aus dem unveraenderten `frozen_e1_state`;
3. entwickelt nur S/H ueber genau ein Probeintervall;
4. gibt denselben E1-Zustand objekt- und wertidentisch wieder aus;
5. verwendet bei Ablation exakt den bestehenden neutralen Generator;
6. veraendert keine Eingabe und besitzt keine versteckte Zeitquelle.

## Vorregistrierte Arme

Fuer beide Geschichtszustaende werden dieselben Arme gebildet:

```text
L1: b_L, eingefroren, Rueckwirkung an
R1: b_R, eingefroren, Rueckwirkung an

L0: b_L, eingefroren, Rueckwirkung aus
R0: b_R, eingefroren, Rueckwirkung aus

P0: kein E1-Zustand, bestehender neutraler S/H-Pfad
```

Alle fuenf Arme lesen objektgetrennte, wertidentische Kopien von `F*` und
dieselbe Probe P.

## Fester-Gain-Gegenbaseline

Zusaetzlich werden die aus `b_L` und `b_R` berechneten Kantenraten als
eingefrorene feste Gainfelder `G_L` und `G_R` ausgewertet.

Vorhersage:

```text
Feld(L1) == Feld(G_L)
Feld(R1) == Feld(G_R)
```

Diese Gleichheit ist erforderlich. Sie zeigt offen, dass die Probe keine
neue Dynamik jenseits eines festen raeumlichen Gain nachweist. Der
Geschichtsbezug liegt in der vorherigen E1-Entwicklung, nicht im
eingefrorenen Probeoperator.

## Primaere Rohmetriken

Vor und nach der Probe werden ohne Schwellenklassifikation berichtet:

```text
D_pre_S       = Linf(S_L* - S_R*)
D_pre_H       = Linf(H_L* - H_R*)
D_state       = Linf(b_L - b_R)
D_total       = abs(Summe(b_L) - Summe(b_R))
D_active_S    = Linf(S_L1 - S_R1)
D_active_H    = Linf(H_L1 - H_R1)
D_ablate_S    = Linf(S_L0 - S_R0)
D_ablate_H    = Linf(H_L0 - H_R0)
D_p0_a0       = maximale Feldabweichung P0 gegen L0 und R0
D_fixed_gain  = maximale Abweichung L1/G_L und R1/G_R
```

Zusaetzlich werden alle E1-, Adapter- und Felddigests beziehungsweise die
vorhandenen technischen Identitaeten protokolliert, ohne daraus Bedeutung
abzuleiten.

## Vorregistrierte Entscheidung

### Technischer E2-Kausalbefund

Nur zulaessig, wenn gemeinsam gilt:

```text
D_pre_S = 0 exakt
D_pre_H = 0 exakt
D_state > numerischer Verfeinerungsrest
D_total <= vorregistrierte Rundungstoleranz
D_active_S oder D_active_H > zugehoeriger Verfeinerungsrest
D_ablate_S = 0 exakt
D_ablate_H = 0 exakt
D_p0_a0 = 0 exakt
D_fixed_gain <= vorregistrierte Rundungstoleranz
E1-Zustaende bleiben waehrend aller Proben unveraendert
```

Der numerische Verfeinerungsrest wird vor der Entscheidung aus derselben
Probe mit `dt`, `dt/2` und `dt/4` bestimmt. Es wird keine Schwelle nach Sicht
auf das aktive Ergebnis gewaehlt.

### Kein E2-Befund

Liegt keine aktive Differenz oberhalb des Verfeinerungsrests vor, ist E2 im
ersten Korridor nicht nachgewiesen. Der Lauf darf nicht durch nachtraegliche
Probeanpassung, mehr Wiederholungen oder Parameterveraenderung gerettet
werden.

### Ungueltiger Lauf

Der Lauf ist ungueltig bei fehlender Spiegelkontrolle, nichtidentischem
S/H-Vorzustand, nichtneutraler Ablation, veraendertem E1-Zustand waehrend der
Probe oder unvollstaendiger Gegenbaseline.

## Was ein positives Ergebnis bedeuten wuerde

Ein positiver E2-Kausalbefund wuerde zeigen:

- kontrollierte Geschichte veraendert die endliche E1-Verteilung;
- diese Verteilung bleibt nach Entfernung des historischen S/H-Endfeldes als
  technischer Zustand vorhanden;
- sie veraendert kausal eine spaetere identische Feldprobe;
- die Wirkung verschwindet bei Rueckwirkungsablation.

Das waere ein technischer Fortschritt gegenueber S1-BU.

## Was er nicht bedeuten wuerde

Auch ein positives Ergebnis waere weiterhin vereinbar mit einer bekannten
adaptiven Gainmechanik. Es waere kein Nachweis von Rekonstruktion,
Vergessensdynamik, Wiederverwendung, semantischer Zuordnung, organischem
Memory oder feldbasierter KI.

## Bester naechster Schritt

S1-BW hat den eingefrorenen E1-Probeoperator und seine P0-, Ablations- und
Fester-Gain-Identitaetstests implementiert. Als naechstes spezifiziert und
implementiert S1-BX nur den vorregistrierten Achtkontakt-L/R-
Geschichtsproduzenten bis zu den eingefrorenen E1-Endzustaenden. Eine
Probeauswertung folgt noch nicht im selben Schritt.
