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
- [Verbundene MCM-Feldarchitektur](architektur/013_VERBUNDENE_MCM_FELDARCHITEKTUR.md)
- [Lokale MCM-Neuronenfunktion](architektur/014_LOKALE_MCM_NEURONENFUNKTION.md)
- [Schaltplan der aktuellen Mechanik](architektur/015_SCHALTPLAN_AKTUELLER_MECHANIK.md)
- [Persistenzvertrag verdichteter Feldbeziehungen](architektur/016_PERSISTENZVERTRAG_VERDICHTETER_FELDBEZIEHUNGEN.md)
- [Sensorische Selbstregulation: Grenzvertrag](architektur/017_SENSORISCHE_SELBSTREGULATION_GRENZVERTRAG.md)
- [Minimaler simulierter Effektorvertrag](architektur/018_MINIMALER_SIMULIERTER_EFFEKTORVERTRAG.md)
- [Optionale periodische MCM-Sensoranatomie](architektur/019_OPTIONALE_PERIODISCHE_MCM_SENSORANATOMIE.md)
- [Innere Bezeichnung als verdichtete Feldform](architektur/020_INNERE_BEZEICHNUNG_ALS_VERDICHTETE_FELDFORM.md)
- [Entwicklungsreihenfolge](ENTWICKLUNGSREIHENFOLGE.md)

Die Architekturverträge definieren Zustandsgrenzen und Invarianten. Sie legen
noch keine konkrete MCM-Gleichung, Fusionsfunktion oder Lernregel fest.

## Forschung

- [MINI_DIO-Mechanikabgleich](forschung/001_MINI_DIO_MECHANIKABGLEICH.md):
  Read-only-Rekonstruktion aktiver Mechanik, passiver Diagnose und externer
  Speicherung im Vorgängerprojekt.
- [Sättigungsgrenze des schnellen Feldes](forschung/002_SAETTIGUNGSGRENZE_DES_SCHNELLEN_FELDES.md):
  Begründet den Stopp vor künstlicher Beziehungsspur und leitet als nächste
  funktionale Grenze einen sicheren simulierten Weltkreis ab.

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
- [Methodik 022: Zeitmarkierte visuelle Nullphasen](methodik/022_ZEITMARKIERTE_VISUELLE_NULLPHASEN.md):
  Ordnet Ruhe, kontrollierte Veränderung und erneute Ruhe ausschließlich über
  die gemessene Organismusuhr zu, ohne Detektor oder Feldrückwirkung.
- [Methodik 023: Lokale visuelle Phasenprofile](methodik/023_LOKALE_VISUELLE_PHASENPROFILE.md):
  Bewahrt observerseitig die räumliche Herkunft vorhandener lokaler
  Feldänderungen, ohne Ranking, Bewegungsmaske oder neue Feldmechanik.
- [Methodik 024: Reale visuelle Startphasen-Reichweite](methodik/024_REALE_VISUELLE_STARTPHASEN_REICHWEITE.md):
  Prüft 3, 30 und 90 explizite Startframes gegen technische Einschwingwirkung,
  bevor reale visuelle Feldphasen verglichen werden.
- [Methodik 025: Passive sensorische Belastungs- und Erholungsprüfung](methodik/025_PASSIVE_SENSORISCHE_BELASTUNGS_UND_ERHOLUNGSPRUEFUNG.md):
  Prüft zuerst den erwarteten geschichtslosen Abschluss der vorhandenen festen
  Rezeptoren, bevor eine lokale sensorische Disposition erwogen wird.
- [Methodik 026: Feldfolgen-Gate vor sensorischer Selbstregulation](methodik/026_FELDFOLGEN_GATE_VOR_SENSORISCHER_SELBSTREGULATION.md):
  Schließt Eingangsnachregelung als verfrühten Seitenzweig und verlangt zuerst
  eine kausale, nichtredundante lokale MCM-Feldfolge.
- [Methodik 027: Lokale Feldfolgen-Inertheitsprüfung](methodik/027_LOKALE_FELDFOLGEN_INERTHEITSPRUEFUNG.md):
  Prüft, ob räumlich unterscheidbare Nachhalllagen unter allen vorhandenen
  Neuronenübergängen dennoch exakt denselben Folgezustand erzeugen.
- [Methodik 028: Weltfunktion geschichtsabhängige Wiederaufnahme](methodik/028_WELTFUNKTION_GESCHICHTSABHAENGIGE_WIEDERAUFNAHME.md):
  Definiert aktuell identische Wiederaufnahmen nach verschiedenen lokalen
  Feldgeschichten, ohne Fortsetzung oder Rückkehr als Feldvorgabe einzusetzen.
- [Methodik 029: Passive Wiederaufnahme-Baselineprüfung](methodik/029_PASSIVE_WIEDERAUFNAHME_BASELINEPRUEFUNG.md):
  Fixiert Weltverläufe, Parameter, Gleichungen und Entscheidung vor dem
  passiven Vergleich der Wiederaufnahme gegen B0 bis B5.
- [Methodik 030: Simulierter Effektor-Weltvertrag](methodik/030_SIMULIERTER_EFFEKTOR_WELTVERTRAG.md):
  Registriert Weltzustand, Intervention, Rezeptorfolge, Ursachenablation,
  Reversibilität, Vollumlauf und Reset vor jeder Effektor-Runtime.
- [Methodik 031: Simulierter Weltrezeptor-zu-MCM-Feldpfad](methodik/031_SIMULIERTER_WELTREZEPTOR_ZU_MCM_FELDPFAD.md):
  Prüft den verlustfreien Ursachen-neutralen Transport bis zum Verteiler und
  weist die noch fehlende zyklische MCM-Nachbarschaft ausdrücklich aus.
- [Methodik 032: Offene gegen periodische MCM-Probenadressierung](methodik/032_OFFENE_GEGEN_PERIODISCHE_MCM_PROBENADRESSIERUNG.md):
  Registriert den passiven Randvergleich samt Rotation, Richtungsumkehr,
  Ursachenablation und unveränderten Baseline-Ausgaben.
- [Methodik 033: Optionale periodische Achse der MCM-Neuronenschicht](methodik/033_OPTIONALE_PERIODISCHE_ACHSE_DER_MCM_NEURONENSCHICHT.md):
  Registriert die rückwärtskompatible Runtime-Integration einer expliziten
  periodischen Sensorachse ohne Feldregel oder gespeicherte Kante.
- [Methodik 034: Ringanatomie im simulierten Welt-MCM-Pfad](methodik/034_RINGANATOMIE_IM_SIMULIERTEN_WELT_MCM_PFAD.md):
  Registriert einen kontrafaktischen Zwei-Schritt-Vergleich von offenem und
  periodischem Sensorfeld bei identischen Welt- und Rezeptorfolgen.
- [Methodik 035: Passive Nullprüfung verdichteter Feldform](methodik/035_PASSIVE_NULLPRUEFUNG_VERDICHTETE_FELDFORM.md):
  Registriert identische visuelle Holdout-Proben nach verschiedenen,
  vollständig geleerten Ansichtsgeschichten ohne neue Persistenzmechanik.

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
- [Befund 027: Reale visuelle Ruhe-Nullbasis](befunde/027_REALE_VISUELLE_RUHE_NULLBASIS.md):
  Zwei zeitmarkierte reale Läufe bilden eine enge Referenz aufeinanderfolgender
  Ruhefenster, ohne eine nicht erfolgte Bildintervention zu behaupten.
- [Befund 028: Reale visuelle Startphasen-Grenze](befunde/028_REALE_VISUELLE_STARTPHASEN_GRENZE.md):
  Trennt die technische Einschwingwirkung von 3, 30 und 90 expliziten
  Startframes und trägt 30 Frames für den nächsten realen Phasenlauf.
- [Befund 029: Erster externer audiovisueller Medienkontakt, Pilot](befunde/029_ERSTER_EXTERNER_AUDIOVISUELLER_MEDIENKONTAKT_PILOT.md):
  Ein zeitmarkierter Kamera- und Mikrofonlauf ist technisch vollständig; die
  auditive Trennung bleibt schwach und die globale visuelle Trennung offen.
- [Befund 030: Passive sensorische Belastungs- und Erholungs-Nullprüfung](befunde/030_PASSIVE_SENSORISCHE_BELASTUNGS_UND_ERHOLUNGS_NULLPRUEFUNG.md):
  Drei feste Rezeptorfamilien kollidieren nach verschiedenen Geschichten bei
  identischer Abschlussprobe exakt; sensorische Disposition bleibt E0.
- [Befund 031: Lokale Feldfolgen-Inertheit](befunde/031_LOKALE_FELDFOLGEN_INERTHEIT.md):
  Räumliche Feldasymmetrie erreicht das MCM-Neuron und bleibt als Provenienz
  unterscheidbar, wirkt aber unter den vorhandenen Übergängen nicht weiter.
- [Befund 032: Wiederaufnahme durch unabhängigen Nachhall](befunde/032_WIEDERAUFNAHME_DURCH_UNABHAENGIGEN_NACHHALL.md):
  Alle aktuell identischen Wiederaufnahmepaare werden bereits durch den
  unabhängigen lokalen Nachhall unterschieden; ein Feldrest bleibt nicht.
- [Befund 033: Simulierter Effektor-Weltvertrag](befunde/033_SIMULIERTER_EFFEKTOR_WELTVERTRAG.md):
  Eine reversible Ringtranslation erreicht den Rezeptor kausal und ohne
  Ursachenleck; eine Auslösung durch das MCM-Feld existiert noch nicht.
- [Befund 034: Simulierter Weltrezeptor bis MCM-Verteiler](befunde/034_SIMULIERTER_WELTREZEPTOR_BIS_MCM_VERTEILER.md):
  Der Kontaktwert erreicht den Verteiler vollständig und ursachenneutral; die
  zyklische Weltnachbarschaft ist in der linearen MCM-Schicht noch offen.
- [Befund 035: Offene gegen periodische MCM-Probenadressierung](befunde/035_OFFENE_GEGEN_PERIODISCHE_MCM_PROBENADRESSIERUNG.md):
  Eine isolierte periodische Referenz ergänzt exakt zwei symmetrische
  Randproben, bleibt aber ohne Feldwirkung oder entwickelte Beziehung.
- [Befund 036: Optionale periodische Achse der MCM-Neuronenschicht](befunde/036_OPTIONALE_PERIODISCHE_ACHSE_DER_MCM_NEURONENSCHICHT.md):
  Die Runtime bildet eine explizite Ringachse referenzgleich ab, während alle
  bisherigen offenen Felder unverändert bleiben.
- [Befund 037: Ringanatomie im simulierten Welt-MCM-Pfad](befunde/037_RINGANATOMIE_IM_SIMULIERTEN_WELT_MCM_PFAD.md):
  Die Ringachse trägt eine vorausgehende Randaktivität über zwei getrennte
  Schritte korrekt bis zur lokalen MCM-Wahrnehmung, bleibt dort aber passiv.

## Dokumentationsregel

Dokumentation darf Hypothesen, Zustandsrollen und Prüfbedingungen benennen. Sie
darf keine unbeobachtete Lernregel, Zieltopologie oder kognitive Funktion als
vorhandene Systemeigenschaft ausgeben. Vorarbeiten anderer Projekte bleiben
externe Quellen, bis sie hier reproduziert wurden.
