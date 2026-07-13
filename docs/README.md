# Dokumentationsübersicht

## Verbindliche Grundlage

- [Gründungs- und Architekturvertrag](GRUENDUNGSVERTRAG.md): Ziel, Grenzen,
  Entwicklungsphasen, Evidenzstufen und gesperrte Mechaniken.
- [Offene Forschungsfragen](FORSCHUNGSFRAGEN.md): Ungeklärte Funktionen und
  Trennprüfungen.

## Architektur

- [Sensorspezifischer MCM-Schnittstellenvertrag](architektur/001_SENSORSPEZIFISCHER_MCM_SCHNITTSTELLENVERTRAG.md)
- [Vertrag des gemeinsamen MCM-Strangs](architektur/002_GEMEINSAMER_MCM_STRANG_VERTRAG.md)

Die Architekturverträge definieren Zustandsgrenzen und Invarianten. Sie legen
noch keine konkrete MCM-Gleichung, Fusionsfunktion oder Lernregel fest.

## Forschung

- [MINI_DIO-Mechanikabgleich](forschung/001_MINI_DIO_MECHANIKABGLEICH.md):
  Read-only-Rekonstruktion aktiver Mechanik, passiver Diagnose und externer
  Speicherung im Vorgängerprojekt.

## Methodik

- [Methodik 001: Passive Sensorschnittstellen-Prüfung](methodik/001_PASSIVE_SENSORSCHNITTSTELLEN_PRUEFUNG.md):
  Vorregistrierter Invariantentest für Zustandsunterscheidung, Zeitlage,
  Reihenfolgeneutralität, Reset und passive Baselines. Noch keine Feldmechanik.

## Befunde

- [Befund 001: Passive Sensorschnittstellen-Prüfung](befunde/001_PASSIVE_SENSORSCHNITTSTELLEN_PRUEFUNG_BEFUND.md):
  E1 für die technische Schnittstelle; weiterhin E0 für MCM-Dynamik und den
  gemeinsamen MCM-Strang.

## Dokumentationsregel

Dokumentation darf Hypothesen, Zustandsrollen und Prüfbedingungen benennen. Sie
darf keine unbeobachtete Lernregel, Zieltopologie oder kognitive Funktion als
vorhandene Systemeigenschaft ausgeben. Vorarbeiten anderer Projekte bleiben
externe Quellen, bis sie hier reproduziert wurden.
