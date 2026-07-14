# MCM_FIELD_ORGANISM

`MCM_FIELD_ORGANISM` erforscht ein digitales, MCM-basiertes Wahrnehmungs- und
Nervensystem. Der Projektname bezeichnet die Forschungsrichtung. Leben,
Empfinden, Bedeutung, Lernen, Organismus und Feldintelligenz sind keine
vorausgesetzten Eigenschaften, sondern mögliche spätere Forschungsbefunde.

## Grundarchitektur

```text
Kamera       -> visuelle Rezeptoren -> visuelles MCM  --\
Mikrofon     -> auditive Rezeptoren -> auditives MCM  ----> gemeinsamer MCM-Strang
Berührung    -> taktile Rezeptoren  -> taktiles MCM   --/   -> innere Gesamtlage
```

Jede Sinnesmodalität bildet zuerst eine eigene Feldwahrnehmung. Ein visueller
Kontakt kann deshalb eine innere Lage erzeugen, auch wenn kein auditiver oder
taktiler Kontakt vorhanden ist. Der gemeinsame MCM-Strang erhält keine
Rohsensorik, sondern ausschließlich die bereits entstandenen Zustände der
sensorspezifischen MCM-Felder.

Das gesamte innere Muster ist zunächst der tatsächliche Zustand dieses
gekoppelten Feldsystems. Es wird keine zusätzliche Musterkennung und keine
innere Bezeichnung programmiert.

## Forschungsgrenze

Fest vorgegeben werden dürfen nur transparente digitale Naturbedingungen:

- Kausalität und gemeinsame Systemzeit
- atomare Berechnung aus demselben vorherigen Zustand
- lokale Wechselwirkung
- endliche lokale Ressourcen
- numerische Schutzgrenzen
- stabile technische Identitäten
- ein vollständig passiver Observer

Nicht als Runtime-Ziel vorgegeben werden Muster, Syntax, Kontext, Semantik,
Rollen, Emotion, Bedeutung, Reward, Zieltopologie oder gewünschte Intelligenz.
Eine langsamere lokale Organisationsgeschichte bleibt gesperrt, bis ihre
Notwendigkeit, Zustandsrolle, Wirkung, Begrenzung und Lösbarkeit getrennt
nachgewiesen sind.

## Aktueller Stand

Die technische Sensorschnittstelle, unabhängige lokale Träger, eine
kontrollierte Rezeptorfläche und transparente auditive Baselines wurden passiv
geprüft. Zusätzlich ist ein streng endlicher Audioadapter vorhanden. Sein
simulierter Zweig und ein zweisekündiger USB-Mikrofonlauf verarbeiteten Frames
ohne Rohdatenausgabe. Die kontinuierliche Frequenzlage reagierte, während die
synthetischen Ereignis- und Spikeschwellen im realen Lauf stumm blieben.

Eine zusätzliche passive logarithmische Rezeptorfläche deckt unter
synthetischen Kontrollen `50 Hz` bis `18 kHz` mit 24, 48 oder 64 Bändern ab.
Sie nutzt ein explizites 100-ms-Fenster bei 10-ms-Fortschritt. Diese Fläche ist
eine technische Hörschnittstelle, noch kein auditives MCM-Feld.

Kontinuierliche Frequenzlagen, Schwellenereignisse und unabhängige
Integrate-and-Fire-Spikeanzahlen sind technische Referenzen. Sie belegen weder
ein MCM-Neuron noch ein gekoppeltes auditives MCM-Feld. Eine MCM-, Strang-,
Lern-, Kopplungs- oder Beziehungsmechanik ist weiterhin nicht freigegeben.

Vorarbeiten aus MINI_DIO sind externe Forschungsquellen. Sie werden nicht als
Evidenz des neuen Systems übernommen. Alle Komponenten von
`MCM_FIELD_ORGANISM` beginnen bei E0.

## Dokumentation

- [Gründungs- und Architekturvertrag](docs/GRUENDUNGSVERTRAG.md)
- [MINI_DIO-Mechanikabgleich](docs/forschung/001_MINI_DIO_MECHANIKABGLEICH.md)
- [Sensorspezifischer MCM-Schnittstellenvertrag](docs/architektur/001_SENSORSPEZIFISCHER_MCM_SCHNITTSTELLENVERTRAG.md)
- [Vertrag des gemeinsamen MCM-Strangs](docs/architektur/002_GEMEINSAMER_MCM_STRANG_VERTRAG.md)
- [Methodik 001: Passive Sensorschnittstellen-Prüfung](docs/methodik/001_PASSIVE_SENSORSCHNITTSTELLEN_PRUEFUNG.md)
- [Befund 001: Passive Sensorschnittstellen-Prüfung](docs/befunde/001_PASSIVE_SENSORSCHNITTSTELLEN_PRUEFUNG_BEFUND.md)
- [Methodik 002: Minimale lokale Trägerfunktion](docs/methodik/002_MINIMALE_LOKALE_TRAEGERFUNKTION.md)
- [Befund 002: Minimale lokale Trägerfunktion](docs/befunde/002_MINIMALE_LOKALE_TRAEGERFUNKTION_BEFUND.md)
- [Methodik 003: Kontrollierte lokale Rezeptorfläche](docs/methodik/003_KONTROLLIERTE_REZEPTORFLAECHE.md)
- [Befund 003: Kontrollierte lokale Rezeptorfläche](docs/befunde/003_KONTROLLIERTE_REZEPTORFLAECHE_BEFUND.md)
- [Methodik 004: Kontrollierter auditiver Weltkontakt](docs/methodik/004_KONTROLLIERTER_AUDITIVER_WELTKONTAKT.md)
- [Befund 004: Kontrollierter auditiver Weltkontakt](docs/befunde/004_KONTROLLIERTER_AUDITIVER_WELTKONTAKT_BEFUND.md)
- [Methodik 005: Endlicher passiver Mikrofonadapter](docs/methodik/005_ENDLICHER_PASSIVER_MIKROFONADAPTER.md)
- [Befund 005: Endlicher passiver Mikrofonadapter](docs/befunde/005_ENDLICHER_PASSIVER_MIKROFONADAPTER_BEFUND.md)
- [Methodik 006: Passive reale Audiopegelkarte](docs/methodik/006_PASSIVE_REALE_AUDIOPEGELKARTE.md)
- [Befund 006: Audiopegelkarte, Pilot A1](docs/befunde/006_PASSIVE_REALE_AUDIOPEGELKARTE_PILOT_A1.md)
- [Methodik 007: Breite logarithmische Audiorezeptorfläche](docs/methodik/007_BREITE_LOGARITHMISCHE_AUDIOREZEPTORFLAECHE.md)
- [Befund 007: Breite logarithmische Audiorezeptorfläche](docs/befunde/007_BREITE_LOGARITHMISCHE_AUDIOREZEPTORFLAECHE_BEFUND.md)
- [Befund 008: Erster realer Breitband-Audiokontakt](docs/befunde/008_ERSTER_REALER_BREITBAND_AUDIOKONTAKT.md)
- [Offene Forschungsfragen](docs/FORSCHUNGSFRAGEN.md)
- [Dokumentationsübersicht](docs/README.md)

## Nächster methodischer Schritt

Die Datenschutz-, Laufzeit- und Rohdatengrenze ist simuliert und in kurzen
realen Mikrofonläufen geprüft. Ein erster Pilot mit laufendem Audio zeigt eine
breite R0-Pegelverteilung. Zwei spätere Stilleläufe sind bei unverändertem
abgesenktem Aufnahmepegel eng reproduzierbar und von zwei danach gemessenen
Audioabschnitten klar getrennt. Die Audioabschnitte stammen jedoch aus
verschiedenen Positionen des laufenden Programms. Als Nächstes wird derselbe
Ausschnitt zweimal ab demselben Startpunkt geprüft. Ein erster realer
Breitbandlauf zeigt eine ähnliche grobe Spektrallandschaft über 24, 48 und 64
Bänder, aber instabile stärkste Einzelbänder und eine auffällige untere
Randwirkung bei 50 bis 60 Hz. Als nächstes muss dieselbe Breitbandmessung bei
gestopptem externem Audio erfolgen. Die Schwellen werden nicht aus dem
Pilotlauf heraus passend eingestellt. Es entsteht weder ein Hintergrundprozess
noch eine dauerhafte Aufnahme.
