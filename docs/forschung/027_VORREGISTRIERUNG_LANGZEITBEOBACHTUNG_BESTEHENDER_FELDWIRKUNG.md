# Forschung 027: Vorregistrierung fuer Langzeitbeobachtung bestehender Feldwirkung

## Status und Ausfuehrungsgrenze

Dieses Dokument konkretisiert Forschung 026 vor einer moeglichen separaten
Freigabe. Es fuehrt keinen Forschungslauf aus, aendert weder Runtime noch
Produktcode und fuehrt keine neue Zustandsrolle ein.

Untersucht werden duerfen ausschliesslich aktuelle Rezeptorprojektion, lokale
Ein-Schritt-Wirkung, schneller Nachhall und additive Ueberlagerung. Dauer ist
nur eine technische Beobachtungsbedingung. Sie ist kein Hinweis auf Memory,
Organisation, reversible Nachwirkung oder entwickelte Topologie.

## Unveraenderte Referenzkonfiguration

Ein moeglicher Lauf muss die bereits in Forschung 023 verwendete Konfiguration
unveraendert uebernehmen:

```text
Substrat-Reaktionszeit:             1.0 Sekunden
Schnelle Nachhall-Zeitkonstante:    0.5 Sekunden
Organismus-Tickrate:                1.0 Tick pro Sekunde
Atomarer Feldschritt:               [k, k + 1)
Geometrie endogener Docks:          (0, 0), (0, 1)
Geometrie externer Dock:            (1, 0)
Lokale Abtastoffsets:               (-1, 0), (0, -1), (0, 1), (1, 0)
Externe Amplitudenskalierung:       1.0
Endogene Amplitudenskalierung:      1.0
```

`CommonFieldTime` und `MCMFieldStepTime` muessen fuer jeden Schritt denselben
Clock-Identifier und dieselben Start- und Endticks tragen. Die bestehende
Referenzprobe verwendet `ticks_per_second = 1.0`; damit entsprechen 5, 15, 30
und 60 Sekunden genau 5, 15, 30 und 60 atomaren Schritten. Ist diese Zuordnung
in der unveraenderten Ausfuehrung nicht belegbar, wird nicht gestartet.

## Vorregistrierte Dauerstufen

| Stufe | Dauer | Atomare Schritte | Zeitfenster |
| --- | ---: | ---: | --- |
| `T0` | 5 s | 5 | `[0, 5)` |
| `T1` | 15 s | 15 | `[0, 15)` |
| `T2` | 30 s | 30 | `[0, 30)` |
| `T3` | 60 s | 60 | `[0, 60)` |

Jede Kombination aus Dauerstufe und Kontrollarm beginnt aus demselben
kanonischen Nullzustand. Ergebnisse kuerzerer Stufen duerfen weder Folgen noch
Messpunkte, Toleranzen oder Fortsetzung laengerer Stufen veraendern.

## Synthetische Kontaktfolgen

Die Folgen sind bedeutungsfrei und werden nur ueber ihren technischen Index
adressiert. Fuer Tick `k` gilt `i = k mod 8`.

Externer Einzelkontakt `X[i]` am Dock `(1, 0)`:

```text
X = (0.60, -0.30, 0.45, -0.15, 0.30, -0.45, 0.15, -0.60)
```

Endogener Einzelkontakt `E[i]` an den Docks `(0, 0)` und `(0, 1)`:

```text
E0 = (0.00, 0.25, 0.50, 0.75, 1.00, 0.75, 0.50, 0.25)
E1 = (0.00, 1.00, 0.00, -1.00, 0.00, 1.00, 0.00, -1.00)
E[i] = (E0[i], E1[i])
```

Die permutierte Folge verwendet fuer jede Dauerstufe dieselben Werte und
dasselbe Kontaktbudget in umgekehrter Zeitordnung: Am Tick `k` wird der Wert
des Ticks `D - 1 - k` aus der jeweiligen nicht permutierten Dauerfolge
angeboten. Es gibt keine Auswahl anhand von Feldwerten.

Alle Werte liegen innerhalb des bestehenden normierten Rezeptorvertrags
`[-1, 1]`. Inaktive Docks bleiben anatomisch vorhanden und erhalten Nullwerte.

## Kontrollarme

Fuer jede Dauerstufe `D` werden folgende unabhaengige Arme aus demselben
Initialzustand ausgefuehrt:

| Arm | Externer Kontakt | Endogener Kontakt | Zweck |
| --- | --- | --- | --- |
| `N` | `0` | `(0, 0)` | Zeit- und Numeriknull |
| `A` | `X[k mod 8]` | `(0, 0)` | externe Einzelwirkung |
| `B` | `0` | `E[k mod 8]` | endogene Einzelwirkung |
| `AB` | `X[k mod 8]` | `E[k mod 8]` | gemeinsame Wirkung |
| `P` | zeitlich umgekehrtes `X` | zeitlich umgekehrtes `E` | Reihenfolgebaseline |
| `R` | identisch zu `AB` | identisch zu `AB` | technische Reproduktion |

Die Ausfuehrungsreihenfolge wird vor dem Lauf fuer alle Dauerstufen fest auf
`N, A, B, AB, P, R` gesetzt. Jeder Arm wird frisch initialisiert; es gibt
keinen Zustandstransfer zwischen Armen.

## Messzeitpunkte

Aktivierung, schneller Nachhall, lokale vorhandene Feldproben und
vollstaendiger Zustandsdigest werden nach jedem abgeschlossenen atomaren
Schritt passiv erfasst. Die vorab hervorgehobenen Vergleichspunkte sind:

```text
M(D) = sort(unique(1, 2, ceil(D/4), ceil(D/2), ceil(3D/4), D))
```

Damit gelten:

| Stufe | Vergleichsticks nach Schrittabschluss |
| --- | --- |
| `T0` | `1, 2, 3, 4, 5` |
| `T1` | `1, 2, 4, 8, 12, 15` |
| `T2` | `1, 2, 8, 15, 23, 30` |
| `T3` | `1, 2, 15, 30, 45, 60` |

Das Erfassen jedes Ticks dient nur der Pruefung von Kontinuitaet und
vorhandener schneller Dynamik. Eine nachtraegliche Auswahl auffaelliger Ticks
als neue Hauptmesspunkte ist ausgeschlossen.

## Vorregistrierte Nullmodelle und Toleranzen

### Aktuelle Feldwirkung

Bei identischem aktuellen Kontakt und identischem bekannten Vorzustand muessen
Aktivierung, Nachhall und lokale Proben komponentenweise bis hoechstens
`1e-12` uebereinstimmen.

### Additivitaet

An jedem Tick und jedem hervorgehobenen Vergleichspunkt gilt getrennt fuer
Aktivierung und schnellen Nachhall:

```text
AB_erwartet = N + (A - N) + (B - N)
```

Ein nicht-additiver Rest ist nur technisch messbar, wenn die maximale absolute
komponentenweise Abweichung strikt groesser als `1e-12` ist und die beiden
isolierten Aktivierungssignaturen `A - N` und `B - N` jeweils eine L2-Norm
strikt groesser als `1e-12` besitzen. Der Schwellenuebertritt begruendet keine
neue Feldrolle, sondern nur eine gesondert zu pruefende Abweichung.

### Reproduktion

`AB` und `R` muessen bei jedem Tick exakt denselben kanonischen Zustandsdigest
und komponentenweise hoechstens `1e-12` Abweichung besitzen. Ein Digestfehler
verwirft die betroffene Dauerstufe als technisch nicht reproduzierbar.

### Reihenfolge und schneller Nachhall

Unterschiede zwischen `AB` und `P` duerfen nur deskriptiv als bekannte
Ein-Schritt- oder schnelle Nachhallwirkung ausgewiesen werden. Sie sind kein
positiver Langzeitbefund. Endet die jeweilige aktuelle Folge mit verschiedenem
Kontakt, ist kein direkter Endzustandsvergleich zulaessig; verglichen werden
nur zeitlich passend kontrollierte Kontaktlagen.

## Pruefbare Zustandsangleichung

Nach dem letzten Dauertick wird fuer jeden Arm ein frischer, kanonisch
identischer Nullzweig aufgebaut. Dies entspricht der vorhandenen exakten
Resetkontrolle durch Neuinitialisierung und setzt keinen mutierenden
Runtime-Reset voraus. Danach folgen zwei identische kontaktfreie atomare
Schritte und eine identische synthetische Holdoutprobe mit externem Wert
`0.60` und endogenen Werten `(0.00, 0.00)`.

Vor der Holdoutprobe muessen exakt gleich sein:

- Rezeptorrahmen und vollstaendige Verteilung;
- Aktivierung und schneller Nachhall;
- lokale Ein-Schritt- und Vorfeldproben;
- vollstaendige Neuronenschicht und feste Anatomie;
- Clock-Identifier, relative Schrittzahl und Intervallbreite;
- Observer-, Snapshot-, Cache- und Serialisierungszustand, soweit vorhanden.

Die Gleichheit wird durch den kanonischen Digest des vollstaendigen bekannten
Zustands sowie komponentenweise Gleichheit belegt. Jede Dauerstufe wird ohne
Holdoutauswertung verworfen, wenn diese Angleichung nicht exakt nachweisbar
ist. Die absolute Ticknummer darf nur durch frisch gestartete, relativ
identische Zweige angeglichen werden; sie darf nicht nachtraeglich manipuliert
werden.

Die Holdoutantwort muss zwischen allen angeglichenen Armen komponentenweise
bis `1e-12` und im kanonischen Digest exakt gleich sein. Dies ist eine
Nullkontrolle, keine Untersuchung reversibler Nachwirkung.

## Abbruch- und Stopplinien

Der Lauf wird vor Beginn oder waehrend der Ausfuehrung abgebrochen, wenn:

- eine Runtime-, Produkt- oder Anatomieaenderung erforderlich wird;
- die Tickrate von `1.0` oder die lueckenlose atomare Schrittteilung nicht mit
  der vorhandenen Organismuszeit ausgefuehrt werden kann;
- eine Kontaktfolge, Dauer, Metrik oder Toleranz nach Einsicht in Ergebnisse
  geaendert werden soll;
- ein Wert den bestehenden Rezeptorvertrag verletzt;
- Initialzustand, Kontaktbudget oder feste Anatomie zwischen Pflichtarmen
  abweichen;
- Observer oder Auswertung in Rezeptor, Feld oder Quellen zurueckschreiben;
- vollstaendige Zustandsangleichung nicht exakt belegt werden kann;
- Labels, Bedeutung, Reward, Zielverhalten, Memory-Mechanik oder Zieltopologie
  in den Kausalpfad gelangen;
- eine Medien-, Download-, Transcode- oder dateibasierte OpenCV-Voraussetzung
  entsteht;
- alle Beobachtungen ausschliesslich die bekannten aktuellen, additiven,
  Ein-Schritt- und schnellen Nachhalleffekte reproduzieren.

Das letzte Kriterium beendet die Untersuchungsreihe als abgeschlossene
Reproduktion. Eine Verlaengerung ueber 60 Sekunden oder Umdeutung des
Nullbefunds ist nicht zulaessig.

## Mediengrenze

Der vorregistrierte Lauf ist vollstaendig synthetisch und medienfrei. Er
verlangt keine Browserwiedergabe. Eine spaetere Browservariante waere ein
anderer, separat freizugebender Auftrag und duerfte ausschliesslich eine
vorhandene Video-, Kamera- oder Rezeptorschnittstelle verwenden. Lokale
Mediendatei, Download, lokale Kopie, Transcode und dateibasierter
OpenCV-Ersatzpfad bleiben ausgeschlossen. Fehlt die geforderte Anschlussstelle,
liegt ein interner Ablauffehler vor.

## Vorab festgelegte Ergebnisentscheidung

Der moegliche Lauf darf nur berichten:

1. ob Zeit- und Kontaktvertraege ueber alle Dauerstufen eingehalten wurden;
2. ob aktuelle Wirkung und schneller Nachhall reproduzierbar blieben;
3. ob `AB` innerhalb `1e-12` additiv rekonstruierbar blieb;
4. ob `AB` und `R` technisch reproduzierbar waren;
5. ob nach exakter Angleichung die identische Holdoutantwort gleich war;
6. an welcher Stopplinie der Lauf gegebenenfalls endete.

Werden nur die bekannten Wirkungen reproduziert, lautet das Ergebnis ein
begrenzter Nullbefund fuer eine weitere aktuelle Feldreaktionsklasse. Weder
dieser Ausgang noch eine numerische Abweichung gibt automatisch Runtime,
Memory, Material, Semantik oder Topologie frei.

## Ergebnis dieser Praeregistrierung

Die fehlenden Ausfuehrungsdetails aus Forschung 026 sind festgelegt: Folgen,
Zeitabbildung, Dauerstufen, Kontrollarme, Messzeitpunkte, Toleranzen,
Zustandsangleichung und Abbruchkriterien. Dieses Paket ist damit zur
fachlichen Freigabepruefung durch den Forschungsleiter bereit. Es startet den
Versuch nicht.

## Projektzielabgleich

Die Praeregistrierung bleibt beim Pfad kontrollierter Weltkontakt,
gemeinsames MCM-Feld und lokale bestehende Feldwirkung. Sie programmiert keine
Bedeutung, Labels, Reward, Memory-Mechanik oder Zieltopologie und behauptet
keine reversible Nachwirkung. Eine Zielabweichung ist nicht erkennbar.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters;
- `docs/forschung/019_VORREGISTRIERUNGSSKIZZE_WELTKONTAKT_BIS_60_SEKUNDEN.md`;
- `docs/forschung/021_AKTUELLE_FELDREAKTIONEN_UNVERAENDERTE_RUNTIME.md`;
- `docs/forschung/022_GLEICHZEITIGE_KONTROLLIERTE_WELTKONTAKTE_NULLBEFUND.md`;
- `docs/forschung/023_VORREGISTRIERUNG_GEOMETRIE_AMPLITUDE_ADDITIVITAET.md`;
- `docs/forschung/026_KONZEPT_LANGZEITBEOBACHTUNG_BESTEHENDER_FELDWIRKUNG.md`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/field_step_time.py`;
- `mcm_field_organism/controlled_endogenous_source.py`;
- `mcm_field_organism/geometry_amplitude_superposition_probe.py`;
- `mcm_field_organism/neutral_local_field_substrate.py`;
- `mcm_field_organism/endogenous_external_overlap_null_probe.py`.

MINI_DIO-Quellen wurden nicht verwendet und keine MINI_DIO-Mechanik wurde
uebernommen.
