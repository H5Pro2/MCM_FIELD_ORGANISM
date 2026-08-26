# Forschung 036: Synthetische Kontaktsequenzen ohne Persistenzannahme

## Auftrag und Grenze

Geprueft wurde, ob der stabile Nullbefund aus Forschung 032 bis 035 bei
kurzen kontrollierten Kontaktsequenzen ueber vorhandene Docks erhalten
bleibt. Verwendet wurden ausschliesslich bestehende synthetische Rezeptor-,
Verteiler-, `SharedMCMField`-, Neuron-Layer- und Projektionsschnittstellen.

Schnellnachhall, Browser, Medienpfade, Download, lokale Medienkopie,
Installation, Transcode und dateibasierte Auswertung blieben ausgeschlossen.
Code, Runtime und Architektur wurden nicht geaendert.

## Kontrollierter Aufbau

Die technischen Kontakte `A`, `B` und `C` lagen auf drei getrennten Docks.
Jeder Kontakt hatte die identische Staerke `0.5`. Jeder Arm belegte exakt drei
Sequenzfenster, damit Organismuszeit und Layer-Tick zwischen den Armen gleich
blieben. Nicht belegte Fenster wurden als kontaktfreie Feldschritte
ausgefuehrt.

Verglichen wurden 14 frisch initialisierte Arme:

- Nullkontakt;
- Einzelkontakt `A`;
- identische Wiederholung `A-A`;
- `A-B-A` und seine drei eindeutigen Permutationen;
- `A-B-C` und seine sechs Permutationen;
- eine getrennte frische Reproduktion von `A-B-A`.

Nach den Sequenzfenstern folgten die neutralen Abstandsstufen `0`, `1`, `2`,
`4` und `8`. Jeder Arm endete mit derselben aktuellen Probe am Dock `A` mit
der Staerke `0.6`.

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
frische A-B-A-Reproduktion:                     gleich
```

Die vollstaendigen Snapshot-Digests unterschieden sich wegen der
arm-spezifischen `snapshot_id` der aktuellen Probe. Diese Metadatenabweichung
war weder in Aktivierung oder `afterimage` noch im Layer-Digest vorhanden.

## Technische Kontrolle der Organismuszeit

Eine Vorpruefung mit unterschiedlich langen Vorgeschichten lieferte gleiche
Aktivierungen und gleiches `afterimage`, aber unterschiedliche Layer-Digests.
Die Ursache war die unterschiedliche Anzahl ausgefuehrter Feldschritte und
damit eine unterschiedliche Layer-Tickzahl. Dieser Vergleich wurde nicht als
Feldbefund gewertet.

Im massgeblichen Lauf wurden deshalb alle Vorgeschichten auf drei
Sequenzfenster gebracht. Bei identischer Organismuszeit verschwanden die
Layer-Digest-Abweichungen vollstaendig. Damit sind Tickzahl und
Sequenzlaenge als technische Nullerklaerung kontrolliert.

## Befund und Stopplinie

Der Nullbefund bleibt fuer Einzelkontakt, identische Wiederholung, `A-B-A`,
`A-B-C`, deren Permutationen und alle geprueften neutralen Abstandsstufen
stabil. Die spaetere lokale Feldaufnahme wird in diesem Projektionspfad
vollstaendig durch die aktuelle Probe erklaert. Kontaktstaerke,
Sequenzreihenfolge, Dock-Auswahl, lokale Ein-Schritt-Wirkung, Snapshotmetadaten
und Numerik hinterlassen keinen zusaetzlichen kausalen Rest im spaeteren
Layerzustand.

Das Ergebnis begruendet keine Programmerweiterung und keine Aussage ueber
Memory, Bedeutung, Reward, Materialrollen, Organisation oder Topologie.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters;
- `docs/forschung/035_SYNTHETISCHE_KONTAKTSTAERKE_NULLBEFUND.md`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/receptor_distributor.py`;
- `mcm_field_organism/shared_mcm_field.py`;
- `mcm_field_organism/mcm_neuron_layer.py`.

Externe Quellen und MINI_DIO wurden nicht verwendet.
