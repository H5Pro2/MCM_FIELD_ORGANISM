# W7-AE: Implementierung des CAP-Siebenpfad-Verbrauchers

## Entscheidung

`ISOLATED_CAP_SEVEN_PATH_CONSUMER_IMPLEMENTED`

W7-AE implementiert den W7-AD-Vertrag als isolierte In-Memory-Verarbeitung
des vorhandenen W7-M-CAP-Arms. Es wurde kein Report und kein formaler
Forschungslauf erzeugt.

## 1. Implementierter Umfang

Das Modul `mcm_field_organism/w7ae_cap_seven_path_consumer.py` erzeugt:

- sieben getrennte CAP-Hauptketten;
- 32 Hauptproduktionen auf den unveraenderten W7-Y-Segmenten;
- 35 passive Checkpoints;
- 35 tief kopierte, vollstaendige S/H/M-Probezweige;
- snapshot- und konfigurationsgenaue Fortsetzungsbindungen;
- Haupt-/Probereihenfolge- und Pfadreihenfolge-Gegenkontrollen;
- sieben CAP-Pfaddigests und einen Gesamtverbrauchsdigest.

Alle Hauptketten enden bei Tick 8. Probe 4 endet ausschliesslich in ihrem
Probeast bei Tick 9.

## 2. Initial- und Fortsetzungsbindung

Kontaktpfade starten bei Tick 0 aus je einer tiefen Kopie des frischen
W7-M-CAP-Feldes. U-Pfade starten logisch bei Tick 4 aus derselben
unexponierten Anfangsform. Ein frisches Feld besitzt keine abgeschlossene
Distribution und darf deshalb keine Fortsetzungsbindung tragen.

Der Initialfelddigest wird getrennt aus Layer, Dockabbildung, Substratarm,
M-Massen und Kanteninventar gebildet. Nach dem ersten Rezeptorabschluss gilt
ausschliesslich der normale `SharedMCMFieldSnapshot`-Digest. Jede weitere
Fortsetzung konsumiert und erzeugt die exakt dazu passende
`MCMCapacityLimitedContinuationBinding`.

## 3. Direkte CAP-Segmentuebergabe

W7-AE verwendet keinen P0-Zwischenzustand. Die zwei gebundenen
Rezeptorsequenzen eines W7-Y-Segments werden direkt ueber den vorhandenen
Completion-Handoff in transiente Dock- und Neuroneneingaben reduziert und an
`advance_capacity_limited_mcm_f3_shared_field_transient` uebergeben.

Vorhandene W7-M-Quellen bleiben direkt gebunden. Additive W7-W-Quellen
werden erneut gegen Pfad, Intervall und Autorisierungsvertrag geprueft.

## 4. Probeisolation

Jeder Probeast erhaelt eine tiefe Kopie des vollstaendigen Feldes. Layer,
Docks, Substrat und Fortsetzungsbindung besitzen getrennte Objektidentitaet.
Am Kopierpunkt bleiben Feldinhalt und Zustandsdigest gleich.

Eine vorhandene Bindung wird fuer den kopierten Snapshot neu erzeugt. Beim
U-Checkpoint 0 bleiben Haupt- und Probekopie initial und bindungslos. Der
Probeendzustand wird nie als Haupt- oder weiterer Probevorgaenger verwendet.

## 5. Erhaltungskontrollen

Jede Haupt- und Probeproduktion prueft:

- CAP-Arm `w7m.cap` mit unveraenderten Parametern;
- Gesamtmasse M gleich `1.0` innerhalb der vorhandenen Toleranz;
- lokale M-Werte zwischen null und `C_site = 2/84`;
- Kapazitaetsueberschuss gleich null;
- unveraendertes Kanteninventar und unveraenderte Neuronenreihenfolge;
- genaue Snapshot- und Konfigurationsbindung;
- lueckenlose Pfad- und Segmentzeitordnung.

## 6. Gegenbaselines und Gegenkontrollen

W7-AA-P0 und W7-AC-Observer werden nur ueber ihre fertigen
Gesamtverbrauchsdigests gebunden. W7-AE fuehrt sie nicht neu aus und
uebernimmt keine ihrer Zustands- oder Messrollen. Beide Digests sowie das
frische W7-M-Anfangsfeld bleiben nach CAP-Verarbeitung unveraendert.

Die sieben CAP-Pfade werden fuer die Pfadreihenfolge-Gegenkontrolle ein
zweites Mal in umgekehrter Reihenfolge verarbeitet. Jeder rollenbezogene
Pfaddigest bleibt gleich. An AB/Checkpoint 0 bleiben ausserdem Haupt- und
Probeproduktion bei vertauschter Ausfuehrungsreihenfolge digestgleich.

## 7. Gebundener Gesamtverbrauchsdigest

```text
b70a4b4563bb73d50685d1a8475376f0b00377d72369c030027f44f2725af013
```

Der Digest bindet W7-Y, die unveraenderten P0-/Observerdigests, sieben
CAP-Pfaddigests und die Gegenkontrollen. Er enthaelt keine Rangfolge,
Schwellenentscheidung oder Interpretation.

## 8. Verifikation

Die neue W7-AE-Suite enthaelt 11 Tests und besteht mit:

```text
Ran 11 tests in 210.972s
OK
```

Der bisherige W7-Verbund ohne den bereits separat aufgebauten W7-AE-
Verbraucher besteht mit:

```text
Ran 105 tests in 46.791s
OK
```

Damit bestehen insgesamt 116 W7-Pruefungen.

Geprueft wurden Pfad- und Produktionsvollstaendigkeit, Quellen- und
Intervallbindung, Initial- und Fortsetzungsrollen, tiefe Checkpointkopien,
Massenerhaltung, lokale Kapazitaet, Geometrie, Haupt-/Probeisolation,
Gegenkontrollen, unveraenderte Baselines, Digestmanipulationsablehnung und
fehlende oeffentliche Exporte.

Die lange Laufzeit entsteht vor allem durch die echte vollstaendige
Pfadreihenfolge-Gegenkontrolle. W7-AE wird weder aus dem Paketwurzelmodul
noch aus `current_api` exportiert.

## 9. Aussagegrenze

W7-AE weist nur die technische, isolierte Fortsetzbarkeit des vorhandenen
CAP-Modells auf sieben kontrollierten Pfaden nach. Die entstandenen
Zustaende wurden nicht funktional verglichen oder interpretiert. Daraus
folgen keine Feldfunktion, kein Memory, keine Feldzeit, Organisation,
Topologie, Semantik, Selbstregulation oder KI.

## 10. Naechster Schritt

W7-AF soll statisch die passive Messuebergabe der vorhandenen CAP-Haupt- und
Probeproduktionen binden. Zulaessig sind nur vorab definierte Zustands-,
Kapazitaets- und Kontinuitaetsmessrollen sowie P0/Observer als unveraenderte
Gegenbaselines. Noch keine Messausfuehrung, Pfadbewertung, Intervention, kein
Browser, Report oder Forschungslauf.
