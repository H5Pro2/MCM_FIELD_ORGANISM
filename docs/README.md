# Dokumentationsübersicht

## Verbindliche Grundlage

- [Gründungs- und Architekturvertrag](GRUENDUNGSVERTRAG.md): Ziel, Grenzen,
  Entwicklungsphasen, Evidenzstufen und gesperrte Mechaniken.
- [Offene Forschungsfragen](FORSCHUNGSFRAGEN.md): Ungeklärte Funktionen und
  Trennprüfungen.

## Architektur

- [Sensorspezifischer MCM-Schnittstellenvertrag](architektur/001_SENSORSPEZIFISCHER_MCM_SCHNITTSTELLENVERTRAG.md)
- [Vertrag des gemeinsamen MCM-Strangs](architektur/002_GEMEINSAMER_MCM_STRANG_VERTRAG.md)
- [Auditive Rezeptor-zu-Feld-Grenze](architektur/003_AUDITIVE_REZEPTOR_ZU_FELD_GRENZE.md)
- [MCM-Verteiler-Vertrag](architektur/004_MCM_VERTEILER_VERTRAG.md)
- [Vertrag des multimodalen Musterprüfers](architektur/005_MULTIMODALER_MUSTERPRUEFER_VERTRAG.md)
- [Technischer Entwicklungsplan](architektur/006_TECHNISCHER_ENTWICKLUNGSPLAN.md)
- [Reflexions- und Offline-Grenze](architektur/007_REFLEXIONS_UND_OFFLINE_GRENZE.md)
- [Organische Memory-Zeitlagen](architektur/008_ORGANISCHE_MEMORY_ZEITLAGEN.md)
- [Gemeinsamer Energie- und Ressourcenvertrag](architektur/009_GEMEINSAMER_ENERGIE_UND_RESSOURCENVERTRAG.md)
- [Visuelle Rezeptor-zu-Feld-Grenze](architektur/010_VISUELLE_REZEPTOR_ZU_FELD_GRENZE.md)
- [MCM-Neuron mit Feldwahrnehmung](architektur/011_MCM_NEURON_MIT_FELDWAHRNEHMUNG.md)
- [MCM-Neuronenschicht](architektur/012_MCM_NEURONENSCHICHT.md)
- [Entwicklungsreihenfolge](ENTWICKLUNGSREIHENFOLGE.md)

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
- [Methodik 005: Endlicher passiver Mikrofonadapter](methodik/005_ENDLICHER_PASSIVER_MIKROFONADAPTER.md):
  Begrenzt Mikrofonzugriff, Rohdatenhaltung und Observerausgabe; der simulierte
  Zweig wird vor jedem Hardwarezugriff vollständig geprüft.
- [Methodik 006: Passive reale Audiopegelkarte](methodik/006_PASSIVE_REALE_AUDIOPEGELKARTE.md):
  Trennt Stille, externes Audio, Wiederholung und Abstand, bevor reale
  Ereignis- oder Spikeschwellen erwogen werden.
- [Methodik 007: Breite logarithmische Audiorezeptorfläche](methodik/007_BREITE_LOGARITHMISCHE_AUDIOREZEPTORFLAECHE.md):
  Prüft eine passive Spektralfläche von 50 Hz bis 18 kHz über 24, 48 und 64
  logarithmische Bänder, bevor ein breiter realer Hörkontakt erfolgt.
- [Methodik 008: Endlicher Breitband-Hörpfad](methodik/008_ENDLICHER_BREITBAND_HOERPFAD.md):
  Prüft Quelle, Rollfenster, unveränderliche Rezeptorlage und Feldgrenze als
  zusammenhängenden endlichen Pfad ohne implizite MCM-Mechanik.
- [Methodik 009: MCM-Verteiler und multimodale Musterprüfung](methodik/009_MCM_VERTEILER_UND_MULTIMODALE_MUSTERPRUEFUNG.md):
  Prüft offene Docks, verlustfreie Verteilung und passive zeitliche
  Konstellationen synthetischer Sinnes-MCM-Felder.
- [Methodik 010: Auditive Feldfunktions-Kollisionsprüfung](methodik/010_AUDITIVE_FELDFUNKTIONS_KOLLISIONSPRUEFUNG.md):
  Prüft eine relationale auditive Zeitfunktion gegen aktuelle Rezeptorlage,
  unabhängigen Leaky-Nachhall, globale Summe und festen Verzögerungspuffer.
- [Methodik 011: Sparsamer auditiver Schnellfeld-Kandidat](methodik/011_SPARSAMER_AUDITIVER_SCHNELLFELD_KANDIDAT.md):
  Prüft verteilte auditive Gegenwart plus lokalen Nachhall als B1-exakten,
  passiven Feld- und Dockkandidaten ohne Trägerkopplung.
- [Methodik 012: Kontrollierter 20/20/20-Audioregler](methodik/012_KONTROLLIERTER_20_20_20_AUDIOREGLER.md):
  Erzeugt als äußere Testwelt exakt 20 Sekunden Signal, 20 Sekunden Nullkontakt
  und 20 Sekunden dasselbe Signal für die vollständige auditive Feldkette.
- [Methodik 013: Live-Mikrofon-Pass/Mute/Pass-Gate](methodik/013_LIVE_MIKROFON_PASS_MUTE_PASS_GATE.md):
  Lässt den laufenden realen Mikrofonstream 20 Sekunden durch, nullt ihn für
  die MCM 20 Sekunden und öffnet denselben Stream danach erneut.
- [Methodik 014: Endlicher visueller Rezeptorpfad](methodik/014_ENDLICHER_VISUELLER_REZEPTORPFAD.md):
  Prüft endliche technische Frames, ein lokales Drei-Kanal-Raster und die
  geschlossene Grenze zum visuellen MCM ohne Bildspeicherung oder Semantik.

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
- [Befund 005: Endlicher passiver Mikrofonadapter](befunde/005_ENDLICHER_PASSIVER_MIKROFONADAPTER_BEFUND.md):
  Der simulierte Adapter und ein zweisekündiger USB-Mikrofonlauf tragen die
  endliche, observerneutrale Rohdatengrenze. Reale R0-Aktivität blieb unter den
  synthetischen B2/B3-Schwellen.
- [Befund 006: Audiopegelkarte, Pilot A1](befunde/006_PASSIVE_REALE_AUDIOPEGELKARTE_PILOT_A1.md):
  Stille und zwei fortlaufende Audioabschnitte sind bei festem Aufnahmepegel
  klar getrennt; die Wiederholung desselben Ausschnitts bleibt offen.
- [Befund 007: Breite logarithmische Audiorezeptorfläche](befunde/007_BREITE_LOGARITHMISCHE_AUDIOREZEPTORFLAECHE_BEFUND.md):
  24, 48 und 64 passive Bänder tragen synthetisch 50 Hz bis 18 kHz; Fensterzeit,
  Überlappung und Rand-Leckage bleiben ausgewiesene technische Grenzen.
- [Befund 008: Erster realer Breitband-Audiokontakt](befunde/008_ERSTER_REALER_BREITBAND_AUDIOKONTAKT.md):
  Drei Bandgeometrien tragen eine ähnliche grobe reale Spektrallandschaft;
  instabile Einzelbanddominanz und 50-Hz-Randwirkung bleiben offen.
- [Befund 009: Breitband-Stillebasis](befunde/009_BREITBAND_STILLEBASIS_BEI_FESTEM_PEGEL.md):
  Zwei Läufe tragen bei festem abgesenktem Pegel eine hoch reproduzierbare
  technische Stillelandschaft; ihre Quelle bleibt offen.
- [Befund 010: Endlicher Breitband-Hörpfad](befunde/010_ENDLICHER_BREITBAND_HOERPFAD_BEFUND.md):
  Der synthetische Pfad trägt samplegenaue unveränderliche Rezeptorlagen; die
  Grenze zum auditiven MCM-Feld bleibt ausdrücklich geschlossen.
- [Befund 011: MCM-Verteiler und multimodale Musterprüfung](befunde/011_MCM_VERTEILER_UND_MULTIMODALE_MUSTERPRUEFUNG_BEFUND.md):
  E1 für offene MCM-Docks und verlustfreie synthetische Feldkonstellationen;
  gemeinsame Feldwirkung und reale Sinnes-MCMs bleiben offen.
- [Befund 012: Auditive Feldfunktions-Kollisionsprüfung](befunde/012_AUDITIVE_FELDFUNKTIONS_KOLLISIONSPRUEFUNG_BEFUND.md):
  B0, B1 und B2 kollidieren kontrolliert; ein fester Ein-Schritt-Puffer trägt
  die Unterscheidung bereits, daher bleibt zusätzliche Feldmechanik E0.
- [Befund 013: Sparsamer auditiver Schnellfeld-Kandidat](befunde/013_SPARSAMER_AUDITIVER_SCHNELLFELD_KANDIDAT_BEFUND.md):
  Ein B1-exakter verteilter Gegenwarts- und Nachhallzustand erfüllt passiv den
  auditiven Feld- und Dockvertrag; zusätzliche Feldmechanik bleibt E0.
- [Befund 014: Reale endliche auditive Feldkette, Pilot](befunde/014_REALE_ENDLICHE_AUDITIVE_FELDKETTE_PILOT.md):
  60 Sekunden realer Audiokontakt liefen über Rezeptoren, drei passive
  Nachhallkandidaten, Dock und unimodale Feldkonstellation ohne Überlauf durch.
- [Befund 015: Kontrollierte 20/20/20-Feldkette](befunde/015_KONTROLLIERTE_20_20_20_FELDKETTE.md):
  Ein externer Sound-Mute-Sound-Regler trennt Weltphase, Rezeptorfenster und
  B1-Nachhall kausal; zusätzliche Feldmechanik bleibt E0.
- [Befund 016: Reale dauerhafte Umgebungsanregung](befunde/016_REALE_DAUERHAFTE_UMGEBUNGSANREGUNG.md):
  Ein 20-sekündiger realer Umgebungskontakt trägt durchgehend verteilte
  Feldwirkung; eine kausale Zuordnung zu den Ventilatoren bleibt offen.
- [Befund 017: Reales Pass/Mute/Pass-Mikrofon-Gate](befunde/017_REALES_PASS_MUTE_PASS_MIKROFON_GATE.md):
  Ein automatisches Live-Gate unterbricht den realen MCM-Kontakt exakt; nach
  B1-Relaxation kehrt nahezu dieselbe verteilte Umgebungslandschaft zurück.
- [Befund 018: Endlicher synthetischer visueller Rezeptorpfad](befunde/018_ENDLICHER_SYNTHETISCHER_VISUELLER_REZEPTORPFAD.md):
  Eine lokale Drei-Kanal-Fläche bewahrt räumliche Bildverteilung ohne
  Rohpixelspeicherung, Zeitgeschichte, Objekterkennung oder MCM-Feldwirkung.
- [Befund 019: Reales Pass/Mute/Pass bei laufendem Ton](befunde/019_REALES_PASS_MUTE_PASS_BEI_LAUFENDEM_TON.md):
  Stärkerer realer Tonkontakt trägt eine reichere verteilte Frequenzlage,
  wird vom Live-Gate exakt unterbrochen und kehrt danach ähnlich zurück.

## Dokumentationsregel

Dokumentation darf Hypothesen, Zustandsrollen und Prüfbedingungen benennen. Sie
darf keine unbeobachtete Lernregel, Zieltopologie oder kognitive Funktion als
vorhandene Systemeigenschaft ausgeben. Vorarbeiten anderer Projekte bleiben
externe Quellen, bis sie hier reproduziert wurden.
