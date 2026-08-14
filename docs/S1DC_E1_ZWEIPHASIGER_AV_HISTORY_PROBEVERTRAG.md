# S1-DC: E1 zweiphasiger AV-History-Probevertrag

## Status

Statische Vorregistrierung. Keine Implementierung, keine Testausfuehrung,
kein Browserstart und kein Forschungsrunner. Der Vertrag oeffnet den in
S1-CY gestoppten Rekonstruktionszweig nicht wieder.

## Forschungsfrage

Erzeugen zwei kontrollierte Audio-/Video-Historien mit exakt demselben
Rezeptorframe-Multiset, denselben technischen Zeitfenstern und nur
vertauschter zeitlicher Ordnung unterschiedliche E1-Kantenverteilungen, die
nach vollstaendiger Entfernung des historischen S/H-Feldes eine spaetere
identische AV-Probe technisch unterschiedlich fortsetzen?

Der zulaessige Befund ist auf eine AV-weite, history-spezifische technische
E1-Wirkung begrenzt. Rekonstruktion und MCM-Memory werden nicht geprueft.

## Warum nicht die vorhandene History-Holdout-Familie

`controlled_history_holdout_world_family()` enthaelt bereits verschiedene
Historien und eine identische Schlussphase. Die Historien unterscheiden
sich jedoch in ihren konkreten Audio-/Videoinhalten und sind auf reduzierter
Rezeptorebene nicht als identisches Payload-Multiset mit reiner
Reihenfolgepermutation gebunden. Sie ist deshalb keine Primaerquelle fuer
S1-DC.

S1-DC darf aus vorhandenen kontrollierten Phasen nur ein einziges
kanonisches reduziertes AV-Sequenzpaar gewinnen. Der zweite Geschichtsarm
wird danach durch eine rein technische Permutation genau dieser bereits
reduzierten Frames gebildet.

## Geschichtsquelle H-AB und H-BA

Als Inhaltsquelle dienen die beiden gleich langen kontrollierten Phasen A
und B, die bereits in `controlled_temporal_order_probe.py` verwendet werden.
Alte Probeausgaben oder Befunde werden nicht uebernommen.

Die neue private S1-DE-Quelle muss:

1. genau einmal die kanonische Reihenfolge A gefolgt von B bis zu
   `ReceptorTimeSequence("auditory")` und
   `ReceptorTimeSequence("visual")` reduzieren;
2. die Frames jeder Modalitaet anhand der beiden gleich langen Zeitsegmente
   in A- und B-Raenge teilen;
3. H-AB unveraendert lassen;
4. fuer H-BA die bereits reduzierten A- und B-Framebloecke vertauschen;
5. nur die organismischen Lesefenster auf die jeweils vorhandenen
   technischen Zeitslots abbilden;
6. Quellframe, Rezeptorwerte, Carrier, Source-Support, Framezahl und
   innerhalb eines Blocks die Reihenfolge unveraendert lassen.

Es werden keine Frames neu erzeugt, interpoliert, skaliert oder geloescht.
Die Armnamen `H-AB` und `H-BA` gelangen nicht in E1 oder das Feld.

## Pflichtidentitaeten der Geschichtsarme

Vor jeder Feldentwicklung muss fuer jede Modalitaet gelten:

```text
Payload-Multiset(H-AB) == Payload-Multiset(H-BA) exakt
Carrierfolge je Payload                           exakt gleich
Framezahl                                         exakt gleich
Source-Support-Multiset                           exakt gleich
Organismus-Zeitslot-Multiset                      exakt gleich
Gesamteingangsmasse und quadratische Energie      exakt gleich
einzige Differenz                                 A->B gegen B->A
```

Die vollstaendigen Sequenz- und Permutationsdigests werden vor einer
Ausfuehrung gebunden. Scheitert eine Identitaet, darf kein E1-Vergleich
gebildet werden.

## Historiensubstrat ohne Rueckwirkung

Beide Geschichtsarme beginnen mit:

```text
objektgetrennten, wertidentischen frischen S/H-Feldern
objektgetrennten, wertidentischen neutralen E1-Zustaenden
dem unveraenderten E1-Vertrag aus S1-DA
identischer Geometrie und identischem Kanteninventardigest
identischer Feld-, Nachhall-, Dissipations- und Zeitkonfiguration
```

H-AB und H-BA werden ausschliesslich mit der in S1-DB bestaetigten
A0-Schaltung erzeugt:

```text
E1 entwickelt sich entlang der neutralen S/H-Geschichte
backreaction_enabled = False
Feld(H-AB) und Feld(H-BA) bleiben jeweils bitgenau ihrem P0-Arm
```

Damit kann die E1-Bildung untersucht werden, ohne dass eine bereits aktive
E1-Rueckwirkung die jeweilige Geschichte veraendert. Eine spaetere aktive
closed-loop-Historie ist nicht Teil dieses ersten AV-Korridors.

## Harte S/H-Trennung vor der Probe

Nach beiden Historien werden nur die E1-Endzustaende `b_AB` und `b_BA`
weitergegeben. Historische Felder, Nachhallwerte und letzte
Rezeptorverteilungen werden verworfen.

Die Probe beginnt in jedem Arm mit einer objektgetrennten Kopie genau eines
frisch aus der unveraenderten Probegeometrie gebauten Feldes `F*`:

```text
S* elementweise identisch
H* elementweise identisch
gleiche Docks, Neuronen, Kanten und Geometriedigests
gleiche Uhr und gleicher Probezeitplan
keine historische S/H-, Snapshot- oder Last-Distribution-Uebernahme
```

`F*` wird nicht aus einem Geschichts-Endfeld restauriert. E1 bleibt ausserhalb
des neutralen Snapshots.

## Identische AV-Probe P

P ist eine dritte, vorab festgelegte kontrollierte AV-Phase aus derselben
Rezeptorkonfiguration. Sie wird einmal reduziert und als wertidentische,
objektgetrennte Sequenzkopie an alle Probearme gegeben.

P darf nach Sicht auf `b_AB`, `b_BA` oder einen Probeausgang nicht veraendert
werden. Audio, Video, gemeinsame Abschlusszeiten und der komplette
Proposal-Plan bleiben identisch.

## Erforderlicher eingefrorener transienter Probeoperator

Der synchrone Operator aus S1-BW kann impulsartige
`TransientNeuronInputSet`-Kontakte nicht verarbeiten. S1-DD darf deshalb
zwei neue private Rollen implementieren:

```text
advance_frozen_e1_fast_shared_field_transient(...)
advance_fixed_e1_adapter_fast_shared_field_transient(...)
```

Beide verwenden denselben transienten Handoff wie P0. Der E1-Zustand und
der daraus vor Probestart gebildete Adapter bleiben ueber die gesamte Probe
unveraendert. Es gibt waehrend P keine E1-Bindung, Freigabe oder
Wiederverwendung.

Die Implementierung darf die vorhandene Punktkontakt-, S/H-, Nachhall- und
Dissipationsrechnung nur mit einem festen internen Kantengenerator
komponieren. Sie darf keine neue Substratgleichung einfuehren und bleibt aus
`__init__.py` und `current_api.py` ausgeschlossen.

## Vorregistrierte Probearme

```text
P0:   F*, Probe P, kein E1, neutraler transienter Feldpfad
N1:   F*, Probe P, neutraler eingefrorener E1-Zustand, Rueckwirkung an

AB0:  F*, Probe P, b_AB eingefroren, Rueckwirkung aus
BA0:  F*, Probe P, b_BA eingefroren, Rueckwirkung aus

AB1:  F*, Probe P, b_AB eingefroren, Rueckwirkung an
BA1:  F*, Probe P, b_BA eingefroren, Rueckwirkung an

ABF:  F*, Probe P, fester Adapter aus b_AB ohne E1-Zustandsrolle
BAF:  F*, Probe P, fester Adapter aus b_BA ohne E1-Zustandsrolle
```

Erwartete harte Identitaeten:

```text
P0 == N1 == AB0 == BA0                 bitgenau
AB1 == ABF                             bitgenau
BA1 == BAF                             bitgenau
b_AB und b_BA bleiben waehrend P       objekt- und wertidentisch
```

Die festen Adapter ABF und BAF sind Kontrollobergrenzen. Sie muessen jeden
aktiven eingefrorenen Probeeffekt vollstaendig erklaeren.

## Primaere Rohmetriken

```text
D_pre_S             Linf aller S*-Vorzustandsdifferenzen
D_pre_H             Linf aller H*-Vorzustandsdifferenzen
D_state             Linf(b_AB - b_BA)
D_total_binding     abs(Summe(b_AB) - Summe(b_BA))
D_active_S          Linf(S_AB1 - S_BA1)
D_active_H          Linf(H_AB1 - H_BA1)
D_ablation          max(P0/N1/AB0/BA0-Feldabweichung)
D_fixed_adapter     max(AB1/ABF- und BA1/BAF-Abweichung)
D_history_p0        max(A0-Historienfeld gegen zugehoerigen P0-Arm)
D_state_refinement  Linf-Rest der E1-Zustaende zwischen dt2 und dt4
D_field_refinement  groesster S/H-Proberest zwischen dt2 und dt4
```

Zusaetzlich werden Geometrie-, Sequenz-, Handoff-, E1- und Adapterdigests
sowie freie und gebundene Ressourcen berichtet. Es gibt keine semantische
Auswertung einzelner Kanten oder Modalitaeten.

## Vorregistrierte Entscheidungen

### `AV_HISTORY_SPECIFIC_E1_CAUSAL_EFFECT`

Nur zulaessig, wenn gemeinsam gilt:

```text
alle Quellen- und Permutationsidentitaeten bestanden
D_history_p0 = 0 exakt
D_pre_S = 0 exakt und D_pre_H = 0 exakt
D_state > D_state_refinement
D_active_S > D_field_refinement oder D_active_H > D_field_refinement
D_ablation = 0 exakt
D_fixed_adapter = 0 exakt
E1-Zustaende waehrend P unveraendert
alle Ressourcen- und Bereichsinvarianten bestanden
```

Diese Entscheidung waere weiterhin vollstaendig mit einer konstruierten
history-abhaengigen festen Gainverteilung vereinbar.

### `NO_AV_HISTORY_SPECIFIC_E1_EFFECT`

Wenn die Kontrollen bestehen, aber weder `D_state` noch die aktive
Probeabweichung den vorregistrierten Numerikrest uebersteigt.

### `TECHNICALLY_UNDECIDABLE`

Bei verletzter Quellenidentitaet, nichtidentischer Probegrenze,
unvollstaendiger Ablation, fehlender Fester-Adapter-Identitaet,
Ressourcenfehlern oder nicht belastbarem Verfeinerungsvergleich.

Ein ungueltiger oder negativer Ausgang darf nicht durch mehr Wiederholungen,
andere E1-Parameter, eine nachtraeglich ausgewaehlte Probe oder weitere
Cue-Amplituden gerettet werden.

## Aussagegrenze

Auch `AV_HISTORY_SPECIFIC_E1_CAUSAL_EFFECT` waere kein Nachweis fuer
MCM-Memory, Rekonstruktion, Bedeutung, inneren Kontext, Organisation,
Topologie, Selbstregulation oder KI. Er wuerde nur den bereits technisch
bekannten E1-Geschichtstraeger sauber auf eine kontrollierte multimodale
Feldgeometrie uebertragen.

## Bester naechster Schritt

S1-DD implementiert nur den eingefrorenen transienten E1-Probeoperator und
seine feste Adapterbaseline. Zuerst werden P0-, Ablations-, Nullgain-,
Fester-Adapter-, Ereigniszeit- und API-Isolationstests mit kleinen
synthetischen In-Memory-Sequenzen ausgefuehrt. Die AB/BA-Historienmatrix und
ein Forschungsrunner bleiben dabei noch gesperrt.

S1-DD ist inzwischen implementiert und mit 92 relevanten `unittest`-Tests
abgenommen. Siehe `S1DD_E1_EINGEFRORENER_TRANSIENTER_PROBEOPERATOR.md`.

S1-DE ist inzwischen als reine reduzierte AB/BA-Quelle implementiert und
abgenommen. S1-DF bindet darauf aufbauend den A0-History-Produzenten
statisch, ohne eine E1-Historie auszufuehren. Siehe
`S1DE_E1_REDUZIERTE_AV_HISTORY_PERMUTATION.md` und
`S1DF_E1_A0_AV_HISTORY_PRODUKTIONSVERTRAG.md`.

S1-DI hat die kanonischen Zustaende genau einmal erzeugt. S1-DJ stellt
danach fest, dass der hier vorregistrierte `D_state_refinement`-Rest fehlt
und keine analytische Ersatzschranke existiert. Der volle
`AV_HISTORY_SPECIFIC_E1_CAUSAL_EFFECT`-Zweig ist deshalb verbindlich
gestoppt. Nur ein neuer, enger benannter Vertrag darf die veroeffentlichten
Zustaende als gegebene feste Inputs technisch pruefen. Siehe
`S1DJ_E1_A0_AV_HISTORY_EVIDENZ_UND_ANSCHLUSSAUDIT.md`.
