# Forschung 037: Synthetische Kontaktsequenzen mit neutralen Unterbrechungen

## Auftrag und Grenze

Geprueft wurde, ob der stabile Nullbefund aus Forschung 032 bis 036 erhalten
bleibt, wenn kurze synthetische Kontaktsequenzen durch neutrale Feldschritte
zwischen ihren Impulsen getrennt werden. Verwendet wurden ausschliesslich
vorhandene synthetische Rezeptor-, Verteiler-, `SharedMCMField`-,
Neuron-Layer- und Projektionsschnittstellen.

Schnellnachhall, Browser, Medienpfade, Download, lokale Medienkopie,
Installation, Transcode und dateibasierte Auswertung blieben ausgeschlossen.
Code, Runtime und Architektur wurden nicht geaendert.

## Kontrollierter Aufbau

Die technischen Kontakte `A`, `B` und `C` lagen auf drei getrennten Docks und
hatten jeweils die Kontaktstaerke `0.5`. Jeder Arm belegte exakt fuenf
Sequenzfenster. Kontakte lagen nur in den Fenstern `0`, `2` und `4`; die
Fenster `1` und `3` waren neutrale kontaktfreie Feldschritte.

Verglichen wurden 14 frisch initialisierte Arme:

- Nullkontakt ueber alle fuenf Fenster;
- Einzelkontakt `A` mit neutraler Auffuellung;
- identische Wiederholung `A-neutral-A` mit neutraler Auffuellung;
- `A-neutral-B-neutral-A` und seine drei eindeutigen Permutationen;
- `A-neutral-B-neutral-C` und seine sechs Permutationen;
- eine getrennte frische Reproduktion von `A-neutral-B-neutral-A`.

Nach den fuenf gleich langen Sequenzfenstern folgten die neutralen
Abstandsstufen `0`, `1`, `2`, `4` und `8`. Alle Arme endeten mit derselben
aktuellen Probe am Dock `A` mit der Staerke `0.6`.

## Ergebnis

In jeder Abstandsstufe und jedem Sequenzarm ergab die spaetere Probe:

```text
activation = (0.6, 0.0, 0.0)
afterimage  = (0.0, 0.0, 0.0)
```

Fuer alle 70 Kombinationen aus 14 Armen und 5 Abstandsstufen galt:

```text
maximaler activation-Fehler gegen Nullkontakt: 0.0
maximaler afterimage-Fehler gegen Nullkontakt:  0.0
Layer-Digest gegen Nullkontakt:                 gleich
frische A-neutral-B-neutral-A-Reproduktion:     gleich
```

Die vollstaendigen Snapshot-Digests unterschieden sich aufgrund der
arm-spezifischen `snapshot_id` der aktuellen Probe. Diese technische
Metadatenabweichung war in Aktivierung, `afterimage` und Layer-Digest nicht
vorhanden.

## Technische Nullerklaerung

Identische Gesamtfensterlaenge, Feldschrittzahl und Layer-Tickzahl schliessen
die in Forschung 036 identifizierte Zeitkonfundierung aus. Die neutralen
Unterbrechungen wurden als regulaere kontaktfreie Verteilungen auf derselben
Organismuszeitachse ausgefuehrt. Sie erzeugten in der spaeteren Probe keinen
zusaetzlichen kausalen Layerrest.

Die spaetere Aktivierung wird vollstaendig durch die aktuelle Projektion der
Probe erklaert. Sequenzreihenfolge, neutrale Unterbrechungen, Kontaktstaerke,
Dock-Auswahl, lokale Ein-Schritt-Wirkung, Snapshotmetadaten und Numerik
erklaeren alle beobachteten technischen Unterschiede.

## Befund und Stopplinie

Der Nullbefund bleibt fuer unterbrochene Einzel-, Wiederholungs-, `A-B-A`-
und `A-B-C`-Sequenzen, deren Permutationen und alle geprueften nachgelagerten
Abstandsstufen stabil. Es wurde keine veraenderte spaetere lokale
Feldaufnahme festgestellt.

Das Ergebnis begruendet keine Programmerweiterung und keine Aussage ueber
Memory, Bedeutung, Reward, Materialrollen, Organisation oder Topologie.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters;
- `docs/forschung/036_SYNTHETISCHE_KONTAKTSEQUENZEN_NULLBEFUND.md`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/receptor_distributor.py`;
- `mcm_field_organism/shared_mcm_field.py`;
- `mcm_field_organism/mcm_neuron_layer.py`.

Externe Quellen und MINI_DIO wurden nicht verwendet.
