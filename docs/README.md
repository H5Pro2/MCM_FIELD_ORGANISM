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
- [Methodik 002: Minimale lokale Trägerfunktion](methodik/002_MINIMALE_LOKALE_TRAEGERFUNKTION.md):
  Prüft vor jeder Neuronen- oder Nachbarschaftsmechanik, ob unabhängiger
  Leaky-Nachhall die aktuelle Minimalfunktion bereits vollständig erklärt.
- [Methodik 003: Kontrollierte lokale Rezeptorfläche](methodik/003_KONTROLLIERTE_REZEPTORFLAECHE.md):
  Kartiert, welche räumlich-zeitliche Information unabhängige lokale Träger
  bereits ohne Feldkopplung erhalten und wo tatsächliche Kollisionen liegen.
- [Methodik 004: Kontrollierter auditiver Weltkontakt](methodik/004_KONTROLLIERTER_AUDITIVER_WELTKONTAKT.md):
  Vergleicht transparente Frequenzenergie, Schwellenereignisse und unabhängige
  Integrate-and-Fire-Träger vor jeder Live- oder Netzwerkfreigabe.

## Befunde

- [Befund 001: Passive Sensorschnittstellen-Prüfung](befunde/001_PASSIVE_SENSORSCHNITTSTELLEN_PRUEFUNG_BEFUND.md):
  E1 für die technische Schnittstelle; weiterhin E0 für MCM-Dynamik und den
  gemeinsamen MCM-Strang.
- [Befund 002: Minimale lokale Trägerfunktion](befunde/002_MINIMALE_LOKALE_TRAEGERFUNKTION_BEFUND.md):
  Ein unabhängiger Leaky-Zustand erklärt Kontakt, Nachhall und Relaxation
  vollständig; Neuron und Nachbarschaft bleiben unbegründet und gesperrt.
- [Befund 003: Kontrollierte lokale Rezeptorfläche](befunde/003_KONTROLLIERTE_REZEPTORFLAECHE_BEFUND.md):
  Unabhängige Träger erhalten die geprüfte räumlich-zeitliche Information;
  Kopplung bleibt ohne benannte Weltfunktion unbegründet.
- [Befund 004: Kontrollierter auditiver Weltkontakt](befunde/004_KONTROLLIERTER_AUDITIVER_WELTKONTAKT_BEFUND.md):
  Frequenzenergie und lokale Spikes sind reproduzierbar; Spikes tragen
  Zeitereignisse, verlieren aber Information und belegen kein MCM-Neuron.

## Dokumentationsregel

Dokumentation darf Hypothesen, Zustandsrollen und Prüfbedingungen benennen. Sie
darf keine unbeobachtete Lernregel, Zieltopologie oder kognitive Funktion als
vorhandene Systemeigenschaft ausgeben. Vorarbeiten anderer Projekte bleiben
externe Quellen, bis sie hier reproduziert wurden.
