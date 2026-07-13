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

Das Projekt befindet sich in Phase 0: Architekturvertrag und forensischer
Abgleich mit MINI_DIO. Es gibt noch keinen Runtime-Code und keine freigegebene
Lern-, Kopplungs- oder Beziehungsmechanik.

Vorarbeiten aus MINI_DIO sind externe Forschungsquellen. Sie werden nicht als
Evidenz des neuen Systems übernommen. Alle Komponenten von
`MCM_FIELD_ORGANISM` beginnen bei E0.

## Dokumentation

- [Gründungs- und Architekturvertrag](docs/GRUENDUNGSVERTRAG.md)
- [MINI_DIO-Mechanikabgleich](docs/forschung/001_MINI_DIO_MECHANIKABGLEICH.md)
- [Sensorspezifischer MCM-Schnittstellenvertrag](docs/architektur/001_SENSORSPEZIFISCHER_MCM_SCHNITTSTELLENVERTRAG.md)
- [Vertrag des gemeinsamen MCM-Strangs](docs/architektur/002_GEMEINSAMER_MCM_STRANG_VERTRAG.md)
- [Methodik 001: Passive Sensorschnittstellen-Prüfung](docs/methodik/001_PASSIVE_SENSORSCHNITTSTELLEN_PRUEFUNG.md)
- [Offene Forschungsfragen](docs/FORSCHUNGSFRAGEN.md)
- [Dokumentationsübersicht](docs/README.md)

## Nächster methodischer Schritt

Methodik 001 registriert den ersten mechanikfreien Schnittstellentest vor. Als
Nächstes wird ein minimales unveränderliches Testobjekt implementiert, das nur
Zustandsvalidierung, kanonische Darstellung und passive Invariantentests
enthält. Eine MCM-, Strang-, Lern- oder Beziehungsmechanik bleibt gesperrt.
