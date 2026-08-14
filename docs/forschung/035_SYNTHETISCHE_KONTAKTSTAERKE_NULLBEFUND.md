# Forschung 035: Synthetische Kontaktstaerke ohne Persistenzannahme

## Auftrag und Grenze

Geprueft wurde, ob der Nullbefund aus Forschung 032 bis 034 bei kontrolliert
unterschiedlichen Kontaktstaerken und neutralen Abstandsstufen stabil bleibt.
Verwendet wurden ausschliesslich vorhandene synthetische Rezeptor-,
Verteiler-, `SharedMCMField`- und Projektionsschnittstellen.

Schnellnachhall, Browser, Medienpfade, Download, lokale Medienkopie,
Installation, Transcode und dateibasierte Auswertung blieben ausgeschlossen.
Code, Runtime und Architektur wurden nicht geaendert.

## Festgelegter Aufbau

Die Kontaktstaerken wurden vor dem Lauf festgelegt:

```text
schwach: 0.2
mittel:  0.5
stark:   0.9
```

Die neutralen Abstandsstufen waren:

```text
0, 1, 2, 4, 8 kontaktlose Feldschritte
```

Fuer jede der 15 Staerke-Abstands-Kombinationen wurden frisch initialisiert:

- Nullkontakt;
- einmaliger Kontakt der jeweiligen Staerke;
- zweimaliger identischer Kontakt der jeweiligen Staerke;
- frische Reproduktion des Wiederholungsarms;
- Wiederholungsarm mit umgekehrter Dock- und Frame-Reihenfolge.

Nach der jeweiligen Vorgeschichte und dem Abstand folgte in allen Armen die
identische Probe `(0.6, 0.4)`.

## Ergebnis

In allen 15 Kombinationen ergab die spaetere Probe:

```text
activation = (0.6, 0.4)
afterimage  = (0.0, 0.0)
```

Fuer jede Kontaktstaerke und jede Abstandsstufe galt:

```text
Einzelkontakt gegen Nullkontakt, activation max error: 0.0
Wiederholung gegen Einzelkontakt, activation max error: 0.0
Wiederholung gegen Einzelkontakt, afterimage max error:  0.0
Reproduktion, activation/afterimage max error:           0.0
Permutation, activation/afterimage max error:             0.0
Layer-Digest Wiederholung gegen Einzelkontakt:             gleich
Layer-Digest Reproduktion:                                 gleich
Layer-Digest Permutation:                                  gleich
```

Damit besteht weder bei schwacher, mittlerer noch starker Vorgeschichte ein
numerischer oder kausaler Rest in der spaeteren lokalen Feldaufnahme.

## Technische Nullerklaerung

Die spaetere Aktivierung entspricht vollstaendig der aktuellen Projektion der
identischen Probe. Die Variation der vorherigen Kontaktstaerke bleibt nur
waehrend des jeweiligen aktuellen Kontakts wirksam. In der spaeteren Probe
verbleibt auch bei Abstandsstufe `0` kein Unterschied der kausalen
Neuronenschicht. `afterimage` ist in diesem ausgefuehrten Projektionspfad
durchgehend null.

Die vollstaendigen Snapshot-Digests getrennter oder permutierter Arme
unterscheiden sich durch arm-spezifische technische `snapshot_id`-Metadaten
der letzten Rezeptorverteilung. Aktivierung, `afterimage` und Layer-Digest
sind exakt gleich. Ein Cachezustand oder Observer-Writeback wurde nicht
verwendet.

## Befund und Stopplinie

Der Nullbefund bleibt ueber die kontrollierten Kontaktstaerken `0.2`, `0.5`
und `0.9` sowie die Abstandsstufen `0`, `1`, `2`, `4`, `8` stabil. Die
vorhandene Projektionsruntime zeigt keine veraenderte spaetere lokale
Feldaufnahme ausserhalb aktueller Projektion, lokaler Ein-Schritt-Wirkung und
technischer Snapshotmetadaten.

Das Ergebnis begruendet keine Programmerweiterung und keine Aussage ueber
Memory, Bedeutung, Reward, Materialrollen, Organisation oder Topologie.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters;
- `docs/forschung/034_DOCK_UEBERGREIFENDE_SYNTHETISCHE_KONTAKTVARIATION_NULLBEFUND.md`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/receptor_distributor.py`;
- `mcm_field_organism/shared_mcm_field.py`;
- `mcm_field_organism/mcm_neuron_layer.py`.

Externe Quellen und MINI_DIO wurden nicht verwendet.
