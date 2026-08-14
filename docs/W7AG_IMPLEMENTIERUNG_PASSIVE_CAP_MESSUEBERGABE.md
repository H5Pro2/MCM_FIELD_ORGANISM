# W7-AG: Implementierung der passiven CAP-Messuebergabe

## Entscheidung

`PASSIVE_ALIGNED_CAP_MEASUREMENT_HANDOFF_IMPLEMENTED`

W7-AG implementiert den W7-AF-Vertrag als isolierte In-Memory-
Messuebergabe. Es wurde kein Pfad bewertet, kein Report und kein formaler
Forschungslauf erzeugt.

## 1. Private passive Runtimebeobachtung

Der vorhandene kapazitaetsbegrenzte Transientadapter reicht optional den
bereits in der Basis-F3-Runtime vorhandenen privaten Zustandsobserver durch.
Die S/H/M-Arrays werden vor der Uebergabe schreibgeschuetzt. Der Observer
muss `None` zurueckgeben und kann keinen Zustand an die Runtime zurueckgeben.

Ohne Observer bleibt die bisherige Signaturwirkung unveraendert. W7-AEs
interne Segmentfunktion nimmt denselben privaten optionalen Hook an; ihre
Produktions- und Zustandsdigests enthalten keine Observerdaten.

## 2. Implementierter Messadapter

Das Modul
`mcm_field_organism/w7ag_passive_cap_measurement_handoff.py` erzeugt:

- genau 35 CAP-Messresultate fuer sieben Pfade mal fuenf Checkpoints;
- je eine dritte, von Hauptpfad und technischer W7-AE-Probe getrennte
  Messkopie;
- 3.185 S/H/M-Samples an tatsaechlichen Rezeptorabschlussgrenzen;
- 35 W7-P-Feldmessungen;
- 35 CAP-exklusive W7-P-Kapazitaetsmessungen;
- 35 regionale W7-M-M-/Freikapazitaetsledger;
- Messreihenfolge- und Observerpassivitaetsgegenkontrollen;
- einen kanonischen Gesamtmessuebergabedigest.

## 3. Fast-State-Angleichung

Abgeschlossene CAP-Hauptcheckpointzustaende werden tief kopiert und nur in
der Messkopie mit `align_w7m_fast_state` auf S = H = 0 gesetzt. M,
Substratarm, Geometrie, Kapazitaet und Kanteninventar bleiben unveraendert.
Die geaenderte Kopie erhaelt eine neue snapshotgenaue Fortsetzungsbindung.

U/Checkpoint 0 bleibt die Initialausnahme. Diese drei Felder besitzen bereits
S = H = 0 und keine abgeschlossene Distribution. Sie werden tief kopiert,
nicht interveniert und bleiben bis zum Initialadvance bindungslos.

## 4. Messrollen

Aus den geordneten Samples werden ausschliesslich die vorhandenen W7-P-
Feldrollen erzeugt:

- `probe_S_linf`;
- `probe_H_linf`;
- `probe_SH_trajectory_l2`;
- `probe_observation_ticks`.

Die Trajektorien-L2-Norm ist die diskrete Norm ueber alle beobachteten S- und
H-Komponenten. Sie ist kein kontinuierliches Zeitintegral und keine
Feldzeitmessung.

Vor jeder Messprobe liest `measure_w7m_regional_capacity` passiv M und freie
Kapazitaet in `R_A`, `R_B` und `R_0`. Gesamtmasse und gesamte freie
Kapazitaet betragen jeweils `1.0`; der Bilanzrest bleibt innerhalb der
numerischen Toleranz.

## 5. Dreifachtrennung und Gegenkontrollen

Hauptcheckpoint, vorhandene technische W7-AE-Probe und neue Messkopie
besitzen getrennte Feldobjekte. Der Messendzustand kehrt in keinen anderen
Zweig zurueck.

Alle 35 Messungen werden fuer die Reihenfolge-Gegenkontrolle in umgekehrter
Reihenfolge wiederholt. Jeder rollenbezogene Messdigest bleibt gleich. Fuer
AB/Checkpoint 0 wird dieselbe angeglichene Probe zusaetzlich einmal ohne
Observer ausgefuehrt. Produktions- und Endzustandsdigest bleiben gegenueber
der beobachteten Ausfuehrung gleich.

Der W7-AE-Gesamtverbrauchsdigest bleibt unveraendert.

## 6. P0-Grenze

`p0_absolute_comparison_ready` bleibt explizit `false`. Die vorhandenen
W7-AA-Proben sind keine nullgestarteten Messreferenzen und werden nicht
umgedeutet. W7-AG erzeugt deshalb weder CAP/P0-Abstaende noch
Pfadentscheidungen.

## 7. Gebundener Gesamtmessuebergabedigest

```text
898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8
```

Der Digest bindet W7-Y, den unveraenderten W7-AE-Verbrauch, 35 geordnete
Messresultate und beide Gegenkontrollen. Er enthaelt keine Rangfolge,
Kontrastentscheidung oder Interpretation.

## 8. Verifikation

Die neue W7-AG-Suite enthaelt 10 Tests und besteht mit:

```text
Ran 10 tests in 371.453s
OK
```

Zusaetzlich bestehen die 8 direkt betroffenen CAP-Runtimetests und der
bisherige W7-Verbund mit 105 Tests. Zusammen mit W7-AE bestehen damit 126
W7-Pruefungen.

Geprueft wurden vollstaendige Rollenbelegung, S/H-Nullstart, unveraendertes
M, Initialbindungsgrenze, Dreifachtrennung, 3.185 strenge Tick-Samples,
Normdefinitionen, regionale Bilanz, Reihenfolge, Observerpassivitaet,
P0-Sperre, Digestmanipulationsablehnung und fehlende oeffentliche Exporte.

W7-AG wird weder aus dem Paketwurzelmodul noch aus `current_api` exportiert.

## 9. Aussagegrenze

W7-AG erzeugt rollenreine technische Messdaten, wertet sie aber nicht aus.
Es wurden keine Pfade verglichen und keine Interventionen angewendet. Daraus
folgen keine Feldfunktion, kein Memory, keine Feldzeit, Organisation,
Topologie, Semantik, Selbstregulation oder KI.

## 10. Naechster Schritt

W7-AH soll statisch binden, wie fuer jeden Pfad und Checkpoint eine getrennte
P0-Messreferenz mit S = H = 0, identischer Neuronenreihenfolge, identischem
Tick und derselben W7-Y-Probe erzeugt werden darf. Noch keine P0-Ausfuehrung,
kein CAP/P0-Vergleich, keine Pfadauswertung, Intervention, kein Browser,
Report oder Forschungslauf.
