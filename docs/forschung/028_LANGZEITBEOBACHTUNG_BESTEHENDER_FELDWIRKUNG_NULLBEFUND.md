# Forschung 028: Langzeitbeobachtung bestehender Feldwirkung - Nullbefund

## Freigegebener Umfang

Ausgefuehrt wurde ausschliesslich die in Forschung 027 vorregistrierte,
synthetische und medienfreie Beobachtung der unveraenderten Feldruntime. Es
wurden keine Runtime-, Produkt- oder Anatomieaenderung und keine neue
Zustandsrolle eingefuehrt.

Die Dauerstufen 5, 15, 30 und 60 Sekunden wurden bei `1.0` Tick pro Sekunde
als 5, 15, 30 und 60 lueckenlose atomare Feldschritte ausgefuehrt. Untersucht
wurden nur aktuelle Feldwirkung, Ein-Schritt-Wirkung, schneller Nachhall,
Additivitaet, Reproduktion und Holdoutgleichheit nach Angleichung.

## Technische Ausfuehrung

Ausgefuehrt wurde:

```text
python -m unittest tests.test_preregistered_long_observation_probe
```

Da `numpy` nicht in der Projektumgebung installiert war, wurde `numpy 2.5.1`
nur in einem temporaeren Verzeichnis ausserhalb des Workspace bereitgestellt.
Projektdateien und Feldruntime blieben unveraendert. Es wurden keine Medien-,
Download-, Transcode- oder OpenCV-Dateipfade verwendet.

Der erste Testaufruf stoppte vor Feldmessung wegen der fehlenden Abhaengigkeit.
Beim ersten vollstaendigen Aufruf zeigte die passive Testauswertung einen
Fehler: Der absichtlich kontaktfreie erste Tick der endogenen Folge wurde
faelschlich als fehlende isolierte Ursache fuer die gesamte Dauerstufe
bewertet. Korrigiert wurde ausschliesslich diese Aggregation von "an jedem
Tick" zu "innerhalb der Dauerstufe beobachtet". Kontaktfolgen, Runtime,
Messwerte, Nullmodell und Toleranz wurden nicht veraendert. Danach wurde der
gesamte Lauf neu ausgefuehrt.

Endergebnis:

```text
Tests:   5
bestanden: 5
Fehler:  0
```

## Vertrags- und Zeitpruefung

Alle vier Dauerstufen wurden mit der vorregistrierten Schrittzahl vollstaendig
erfasst. Die Kontaktwerte blieben innerhalb `[-1, 1]`; feste Docks, Anatomie,
Tickrate, Intervallbreite und Ausfuehrungsreihenfolge blieben ueber die Arme
gleich. Beide isolierten Ursachen waren innerhalb jeder Dauerstufe von Null
verschieden.

## Additivitaet

Das Nullmodell

```text
AB_erwartet = N + (A - N) + (B - N)
```

wurde an jedem Tick getrennt fuer Aktivierung und schnellen Nachhall geprueft.

| Dauer | maximale Aktivierungsabweichung | maximale Nachhallabweichung | Grenze |
| ---: | ---: | ---: | ---: |
| 5 s | `5.551115123125783e-17` | `5.551115123125783e-17` | `1e-12` |
| 15 s | `1.1102230246251565e-16` | `1.1102230246251565e-16` | `1e-12` |
| 30 s | `1.1102230246251565e-16` | `1.1102230246251565e-16` | `1e-12` |
| 60 s | `1.1102230246251565e-16` | `1.1102230246251565e-16` | `1e-12` |

Alle Abweichungen bleiben im Bereich der Gleitkommarundung und deutlich unter
der vorregistrierten Grenze. Es entstand kein messbarer nicht-additiver Rest.

## Reproduktion und Reihenfolge

`AB` und der unabhaengig frisch gestartete Wiederholungsarm `R` hatten an jedem
Tick identische Zustandsdigests. Die maximale komponentenweise Abweichung war
in allen Dauerstufen exakt `0.0`.

Der permutierte Arm `P` erzeugte in jeder Dauerstufe einen vom unpermutierten
Pfad verschiedenen schnellen Verlauf. Dieser Unterschied ist durch die
vorhandene Ein-Schritt-Wirkung und den schnellen Nachhall erwartet und wird
nicht als Langzeitrolle gewertet.

## Zustandsangleichung und Holdout

Fuer jede Dauerstufe wurden sechs frische, kanonisch identische Nullzweige
aufgebaut, zwei kontaktfreie Schritte ausgefuehrt und anschliessend dieselbe
synthetische Holdoutprobe angeboten.

In allen Dauerstufen waren:

- die Holdout-Zustandsdigests exakt gleich;
- die maximale komponentenweise Holdoutabweichung exakt `0.0`;
- Observer-Writeback und Runtimeaenderung nicht vorhanden.

Damit bleibt die vollstaendige Angleichung als Stopplinie bestaetigt.

## Befund und Stopplinie

Bis 60 Sekunden reproduziert die unveraenderte Runtime ausschliesslich die
bereits bekannten aktuellen, lokalen, additiven, Ein-Schritt- und schnellen
Nachhalleffekte. Eine weitere aktuelle Feldreaktionsklasse wurde nicht
beobachtet.

Die vorregistrierte Stopplinie
`known_current_additive_one_step_fast_effects_only` ist erreicht. Die
Untersuchungsreihe wird daher nicht verlaengert und der Nullbefund nicht als
Memory, Organisation, reversible Nachwirkung, Materialrolle oder entwickelte
Topologie interpretiert.

## Projektzielabgleich

Der Lauf blieb auf kontrollierten Weltkontakt, gemeinsames MCM-Feld und lokale
bestehende Feldwirkung begrenzt. Er programmierte keine Bedeutung, Labels,
Reward, Memory-Mechanik oder Zieltopologie. Eine Zielabweichung ist nicht
erkennbar.

## Tatsaechlich verwendete Quellen

- aktuelle Freigabe des MCM-Forschungsleiters;
- `docs/forschung/027_VORREGISTRIERUNG_LANGZEITBEOBACHTUNG_BESTEHENDER_FELDWIRKUNG.md`;
- `mcm_field_organism/endogenous_external_overlap_null_probe.py`;
- `mcm_field_organism/field_step_time.py`;
- `mcm_field_organism/neutral_local_field_substrate.py`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/preregistered_long_observation_probe.py`;
- `tests/test_preregistered_long_observation_probe.py`.

MINI_DIO-Quellen wurden nicht verwendet und keine MINI_DIO-Mechanik wurde
uebernommen.
