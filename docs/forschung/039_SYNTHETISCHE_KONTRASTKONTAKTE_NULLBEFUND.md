# Forschung 039: Synthetische Kontrastkontakte ohne Persistenzannahme

## Auftrag und Grenze

Geprueft wurde, ob der stabile Nullbefund aus Forschung 032 bis 038 erhalten
bleibt, wenn synthetische Weltkontakte als kontrollierte Kontrastpaare
eingebracht werden. Verwendet wurden ausschliesslich vorhandene Rezeptor-,
Verteiler-, `SharedMCMField`-, Neuron-Layer- und Projektionsschnittstellen.

Schnellnachhall, Browser, Medienpfade, Download, lokale Medienkopie,
Installation, Transcode und dateibasierte Auswertung blieben ausgeschlossen.
Code, Runtime und Architektur wurden nicht geaendert.

## Technische Kontrastdefinition

Kontrast wurde ausschliesslich numerisch im vorhandenen normierten
Rezeptorbereich definiert:

```text
positive Lage: +0.9
negative Lage: -0.9
```

Diese Vorzeichen tragen keine Bedeutung oder Materialrolle. Sie bilden nur
zwei gegensaetzliche technische Eingabewerte.

## Kontrollierter Aufbau

Die Kontakte lagen auf drei getrennten technischen Docks `A`, `B` und `C`.
Jeder Arm hatte exakt sieben Sequenzfenster. Kontaktimpulse lagen in den
Fenstern `0`, `2`, `4` und `6`; die Zwischenfenster waren neutrale
kontaktfreie Feldschritte.

Verglichen wurden 73 frisch initialisierte Arme:

- ein Nullkontaktarm;
- sechs Einzelkontaktarme fuer beide Kontrastlagen an allen drei Docks;
- sechs identische Wiederholungsarme fuer beide Kontrastlagen an allen Docks;
- zwoelf gegensaetzliche Zweierpaare aus allen geordneten Kombinationen
  verschiedener Docks und beiden Vorzeichenreihenfolgen;
- 24 Permutationen der wechselnden Paarfolge
  `A(+)-B(-)-B(+)-C(-)`;
- 24 Permutationen der inversen wechselnden Paarfolge
  `A(-)-B(+)-B(-)-C(+)`;
- eine getrennte frische Reproduktion der kanonischen wechselnden Paarfolge.

Nach den sieben gleich langen Sequenzfenstern folgten die neutralen
Abstandsstufen `0`, `1`, `2`, `4` und `8`. Alle Arme endeten mit derselben
aktuellen Probe am Dock `A` mit dem Wert `0.6`.

## Ergebnis

In jeder Abstandsstufe und jedem Arm ergab die spaetere Probe:

```text
activation = (0.6, 0.0, 0.0)
afterimage  = (0.0, 0.0, 0.0)
```

Fuer alle 365 Kombinationen aus 73 Armen und 5 Abstandsstufen galt:

```text
maximaler activation-Fehler gegen Nullkontakt: 0.0
maximaler afterimage-Fehler gegen Nullkontakt:  0.0
Layer-Digest gegen Nullkontakt:                 gleich
frische kanonische Reproduktion:                gleich
```

Die vollstaendigen Snapshot-Digests unterschieden sich aufgrund der
arm-spezifischen `snapshot_id` der aktuellen Probe. Diese technische
Metadatenabweichung war nicht in Aktivierung, `afterimage` oder Layer-Digest
vorhanden.

## Technische Laufkontrolle

Ein erster Aufruf wurde vor jeder Feldbewertung durch die bestehende
`snapshot_id`-Validierung beendet, weil Laufmetadaten Grossbuchstaben
enthielten. Die Kennungen wurden auf zulaessige Kleinbuchstaben normalisiert;
Versuchsarme, Kontakte, Werte, Reihenfolgen und Zeitstruktur blieben
unveraendert. Der abgebrochene Aufruf wurde nicht als Forschungsbefund
gewertet.

Im gueltigen Lauf waren Gesamtfensterlaenge, Feldschrittzahl und
Layer-Tickzahl in allen Armen identisch. Kontrastlage, Dock-Auswahl,
Reihenfolge und neutrale Unterbrechungen wurden kontrolliert variiert.

## Befund und Stopplinie

Der Nullbefund bleibt fuer Einzelkontakte, identische Wiederholungen,
gegensaetzliche Paare, wechselnde Kontrastpaare, permutierte Reihenfolgen und
alle geprueften Abstandsstufen stabil. Die spaetere Aktivierung wird
vollstaendig durch die aktuelle Projektion der identischen Probe erklaert.
Es wurde keine veraenderte spaetere lokale Feldaufnahme festgestellt.

Das Ergebnis begruendet keine Programmerweiterung und keine Aussage ueber
Memory, Bedeutung, Reward, Materialrollen, Organisation oder Topologie.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters;
- `docs/forschung/038_SYNTHETISCHE_MEHRDOCK_SEQUENZEN_KONTAKTSTAERKE_UNTERBRECHUNGEN_NULLBEFUND.md`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/receptor_distributor.py`;
- `mcm_field_organism/shared_mcm_field.py`;
- `mcm_field_organism/mcm_neuron_layer.py`.

Externe Quellen und MINI_DIO wurden nicht verwendet.
