# Forschung 022: Gleichzeitige kontrollierte Weltkontakte - Nullbefund

## Status und Abgrenzung

Dieser Forschungslauf ist ein separater Reproduktions- und Auswertungslauf. Forschung 021 bleibt unveraendert abgeschlossen. Untersucht wird ausschliesslich die gegenwaertige lokale Feldreaktion der unveraenderten Runtime auf zwei gleichzeitig anliegende, synthetisch kontrollierte Kontakte.

Der Lauf fuehrt keine Memory-Deutung, Materialhypothese, Zieltopologie, Semantik, Labels oder Reward ein. Er aendert weder Runtime noch Produktcode und verwendet keine Medien-, Download-, Transcode- oder OpenCV-Dateipfade.

## Forschungsfrage

Ist die gemeinsame gegenwaertige Feldwirkung zweier gleichzeitig anliegender Kontakte vollstaendig als Ueberlagerung ihrer einzeln bestimmten schnellen Feldwirkungen erklaerbar, oder bleibt nach den Gegenbaselines ein zusaetzlicher gemeinsamer Reaktionsanteil uebrig?

## Vergleichsdesign

Die vorhandene passive Ursachenueberlagerungs-Nullpruefung verwendet vier Arme mit identischer Feldanatomie, identischer Initialisierung und identischem Auswertungstakt:

- A: externer und endogener Kontakt gemeinsam aktiv
- B: nur externer Kontakt aktiv; endogener Dock bleibt mit Nullwert vorhanden
- C: nur endogener Kontakt aktiv; externer Dock bleibt mit Nullwert vorhanden
- D: beide Docks bleiben mit Nullwert vorhanden

Die Einzelwirkungen werden als `B - D` und `C - D` bestimmt. Fuer den gemeinsamen Arm gilt als Nullmodell:

`A_erwartet = D + (B - D) + (C - D)`

Diese Rekonstruktion wird getrennt fuer aktuelle Aktivierung und schnellen Nachhall geprueft.

## Ausfuehrung

Ausgefuehrt wurden:

`python -m unittest tests.test_endogenous_external_overlap_null_probe tests.test_endogenous_receptor tests.test_controlled_endogenous_source`

Ergebnis: 19 Tests bestanden, 0 Fehler.

Die Probe umfasste drei Feldneuronen. Die beiden isolierten Ursachen hatten von Null verschiedene und voneinander verschiedene Signaturen:

| Groesse | externer Kontakt | endogener Kontakt |
| --- | ---: | ---: |
| Aktivierung, L2 | 0.2868504102354683 | 0.3514704318110997 |
| schneller Nachhall, L2 | 0.18785020239120653 | 0.26086332771306925 |

Maximale Abweichung der gemeinsamen Wirkung vom additiven Nullmodell:

| Auswertung | maximale Abweichung |
| --- | ---: |
| aktuelle Aktivierung | 1.1102230246251565e-16 |
| schneller Nachhall | 5.551115123125783e-17 |

Die Abweichungen liegen im Bereich numerischer Gleitkomma-Rundung. Beide Ursachen wurden als erhalten und unterscheidbar bestaetigt. Die Quellzustaende blieben erhalten; Beobachter-Writeback, Memory-Zustand, Materialbewegung und Runtime-Kandidat blieben ausgeschaltet.

## Gegenbaselines und Grenzen

- **Provenienz:** Die beiden Ursachen werden durch getrennte kontrollierte Quellen und isolierte Arme bestimmt. Aus ihrer technischen Herkunft wird keine Feldbedeutung abgeleitet.
- **Reihenfolge:** Der Hauptbefund betrifft Gleichzeitigkeit. Eine zeitliche Reihenfolge ist kein freier Wirkfaktor dieses Designs und darf aus dem Ergebnis nicht abgeleitet werden.
- **Feste Anatomie:** Alle vier Arme behalten dieselben Docks und dieselbe Feldanatomie; inaktive Kontakte werden genullt und nicht strukturell entfernt.
- **Schneller Nachhall:** Er wird separat rekonstruiert und zeigt ebenfalls keinen zusaetzlichen gemeinsamen Rest. Er ist kein Memory-Indiz.
- **Technische Nebenzustaende:** Gleiche Initialisierung und unveraenderte Quellzustaende begrenzen den Befund auf die Feldreaktion. Beobachtung schreibt nicht in die Runtime zurueck.
- **Vollstaendige Zustandsangleichung:** Sie bleibt die Stopplinie fuer jede spaetere geschichtsbezogene Behauptung. Dieser Lauf untersucht keine Geschichte und hebt den Nullbefund aus Forschung 021 nicht auf.

Das Design prueft nur die vorhandene Kombination eines kontrollierten externen und eines kontrollierten endogenen Kontakts. Es beweist keine allgemeine Linearitaet fuer beliebige Kontaktzahlen, Amplituden, Geometrien oder Laufzeiten.

## Ergebnis

Unter den geprueften Bedingungen ist die gleichzeitige lokale Feldwirkung vollstaendig durch die aktuelle additive Ueberlagerung der beiden bekannten schnellen Rollen erklaerbar. Es bleibt kein zusaetzlicher gemeinsamer Residualanteil, der eine neue gegenwaertige Feldreaktionsklasse begruenden wuerde.

Der Befund ist ein Nullbefund gegen eine neue Reaktionsklasse. Er ist weder ein Memory-Befund noch eine Freigabe fuer Materialmodell, 60-Sekunden-Lauf, Runtime- oder Produktentwicklung.

## Projektzielabgleich

Der Lauf bleibt im freigegebenen Pfad `Weltkontakt -> gemeinsames MCM-Feld -> lokale Feldwirkung`. Eine moegliche spaetere veraenderte Feldaufnahme wird weder behauptet noch vorprogrammiert. Eine Zielabweichung ist nicht erkennbar.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters
- `docs/forschung/021_AKTUELLE_FELDREAKTIONEN_UNVERAENDERTE_RUNTIME.md`
- `docs/architektur/083_PASSIVE_URSACHENUEBERLAGERUNGS_NULLPRUEFUNG.md`
- `mcm_field_organism/endogenous_external_overlap_null_probe.py`
- `tests/test_endogenous_external_overlap_null_probe.py`
- `tests/test_endogenous_receptor.py`
- `tests/test_controlled_endogenous_source.py`
