# Forschung 023: Vorregistrierung Geometrie- und Amplitudenvariation

## Abgrenzung

Forschung 022 bleibt abgeschlossen. Dieser separate, medienfreie Lauf prueft ausschliesslich die Stabilitaet ihres Additivitaetsbefunds bei unveraenderter Feldruntime. Er fuehrt weder Memory, Material, Semantik, Labels, Reward noch Zieltopologie ein.

## Nullmodell

Fuer jede Parameterkombination werden vier von demselben vollstaendig angeglichenen Initialzustand ausgehende Arme ausgefuehrt: gemeinsamer Kontakt, nur externer Kontakt, nur endogener Kontakt und kontaktfreier Kontrollarm.

Vor der Auswertung gilt getrennt fuer Aktivierung und schnellen Nachhall:

`gemeinsam_erwartet = null + (extern - null) + (endogen - null)`

Ein nicht-additiver Rest gilt nur dann als messbar, wenn die maximale absolute komponentenweise Abweichung groesser als `1e-12` ist und beide isolierten Kontaktwirkungen von Null verschieden sind.

## Vorregistriertes Raster

Die zwei endogenen Dockpositionen bleiben `(0, 0)` und `(0, 1)`. Die einzelne externe Dockposition wird in vier Faellen variiert:

- `near`: `(1, 0)`
- `far`: `(2, 1)`
- `opposite`: `(-1, 0)`
- `transverse`: `(1, 1)`

Je Geometrie werden neun feste Skalierungspaare `(extern, endogen)` geprueft:

`(0.25, 0.25), (1, 0.25), (0.25, 1), (1, 1), (1.5, 0.5), (0.5, 1), (1.5, 1), (-1, 1), (1, -1)`

Damit entstehen 36 Vier-Arm-Vergleiche. Geometrie und Amplitude sind ausschliesslich kontrollierte Eingaben; sie werden nicht adaptiv anhand eines Ergebnisses gewaehlt.

Die zunaechst angesetzten Skalierungen `2` und `4` wurden bei der technischen Vorpruefung vor jeder Feldmessung vom bestehenden normierten Rezeptorvertrag `-1..1` abgewiesen. Das Raster wurde deshalb innerhalb des bestehenden Vertrags festgelegt. Die externe Referenz erreicht bei Skalierung `1.5` maximal den Betrag `0.9`; die endogene Referenz bleibt bis Skalierung `1` innerhalb des Vertrags. Die Abweisung ist kein Feldbefund.

## Stopplinien

- Jeder Arm beginnt aus demselben Initialzustand; eine unvollstaendige Angleichung verwirft den Fall.
- Ein Rest im schnellen Nachhall ist kein Memory-Befund.
- Technische Herkunft, feste Anatomie und Gleitkomma-Rundung duerfen nicht als neue Feldreaktionsklasse gelten.
- Es gibt keine Browser-, Medien-, Download-, Transcode- oder OpenCV-Dateipfad-Anforderung.
- Unabhaengig vom Ausgang entsteht keine automatische Freigabe fuer Runtime- oder Produktentwicklung.

## Ausfuehrung

Ausgefuehrt wurden die neue passive Forschungsprobe und die unveraenderten Kontrollen aus Forschung 022:

`python -m unittest tests.test_geometry_amplitude_superposition_probe tests.test_endogenous_external_overlap_null_probe tests.test_endogenous_receptor tests.test_controlled_endogenous_source`

Ergebnis: 23 Tests bestanden, 0 Fehler. Alle 36 vorregistrierten Vier-Arm-Vergleiche wurden ausgewertet. In jedem Fall waren beide isolierten Ursachen von Null verschieden.

| Auswertung | groesster additiver Rest | vorab gesetzte Grenze |
| --- | ---: | ---: |
| aktuelle Aktivierung | 1.1102230246251565e-16 | 1e-12 |
| schneller Nachhall | 1.1102230246251565e-16 | 1e-12 |

Alle 36 Faelle erfuellen das Nullmodell. Initial- und Quellzustaende blieben erhalten; die Probe fuehrte keinen Beobachter-Writeback und keine Runtimeaenderung aus.

## Befund

Innerhalb des zulaessigen normierten Amplitudenbereichs und der vier geprueften nicht ueberlappenden Dockgeometrien bleibt die Additivitaetsgrenze aus Forschung 022 stabil. Es wurde kein klar messbarer nicht-additiver Rest und damit keine neue gegenwaertige Feldreaktionsklasse gefunden.

Der Befund verallgemeinert nicht auf beliebige Geometrien, Kontaktzahlen, Zeitkonstanten oder Werte ausserhalb des Rezeptorvertrags. Der schnelle Nachhall bleibt eine bekannte schnelle Rolle und ist kein Memory-Nachweis. Die vollstaendige Zustandsangleichung bleibt Stopplinie fuer jede geschichtsbezogene Interpretation.

## Projektzielabgleich

Der Lauf bleibt bei kontrolliertem Weltkontakt, gemeinsamem MCM-Feld und lokaler aktueller Feldwirkung. Er fuehrt keine Bedeutung, kein Zielverhalten und keine vorprogrammierte Organisation ein. Eine Zielabweichung ist nicht erkennbar.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters
- `docs/forschung/022_GLEICHZEITIGE_KONTROLLIERTE_WELTKONTAKTE_NULLBEFUND.md`
- `mcm_field_organism/endogenous_external_overlap_null_probe.py`
- `mcm_field_organism/controlled_endogenous_source.py`
- `mcm_field_organism/shared_mcm_field.py`
- `mcm_field_organism/geometry_amplitude_superposition_probe.py`
- `tests/test_geometry_amplitude_superposition_probe.py`
- `tests/test_endogenous_external_overlap_null_probe.py`
- `tests/test_endogenous_receptor.py`
- `tests/test_controlled_endogenous_source.py`
