# W7-BE: CONST-V-AB/R1-Einpfadverbraucher

## Zweck

W7-BE ist die kleinste reale Integrationsgrenze nach W7-BD. Materialisiert
wird ausschliesslich der kanonische W7-Y-Pfad `AB` bei Aufloesung R1. Die
anderen sechs Pfade sowie R2 und R4 bleiben unberuehrt.

## Hauptkette

Die Hauptkette startet mit einem frischen CONST-V-Feld bei Tick null. Sie
verarbeitet den vorhandenen A-Praefix und danach vier vorhandene B-
Fortsetzungen bis Tick 8.000.000. Alle Quellen stammen unveraendert aus dem
digestgebundenen W7-Y-Plan. Der W7-BD-Adapter delegiert jeden Abschnitt an
die bestehende SSPRK33-Runtime mit dem vorhandenen W7-N-CONST-V-Kern.

## Checkpoints und Rohmessung

An den fuenf W7-Y-Checkpoints wird die Hauptlage tief kopiert. Auf der Kopie
werden nur `S` und `H` auf null ausgerichtet. Der technische Skalar bleibt
bitgenau erhalten. Anschliessend laeuft die zugehoerige W7-Y-Probe nur auf
diesem isolierten Zweig.

Der passive Observer erfasst nur lesbare Vektoren an tatsaechlichen
Rezeptorabschluss- und Endgrenzen:

- rohe `S`-Werte;
- rohe `H`-Werte;
- rohe Werte des technischen CONST-V-Skalars.

Die Probe kehrt nicht in die Hauptkette zurueck. Es werden noch keine Linf-
Distanzen, Profile, Schwellen oder CAP-Vergleiche berechnet.

## Evidenzgrenze

Der technische Skalar wird nicht als Kapazitaet, Praegung oder Memory
bezeichnet. W7-BE prueft nur, ob ein einzelner CONST-V-Pfad technisch
durchgaengig, isoliert und roh beobachtbar ist. Ein positiver Feldfunktions-
oder Memorybefund ist ausgeschlossen.

## Technischer Laufbefund

- Ergebnisdigest: `88fd9722420a94f09c15fbce9e4e0b2a283a1a56422ed653e92ef2a7aeaf8708`
- fuenf Hauptproduktionen bis Tick 8.000.000;
- fuenf isolierte Probeproduktionen;
- je Probe 91 rohe S/H/Skalar-Beobachtungsgrenzen;
- 1251 Integrationssubschritte insgesamt;
- maximaler Massenerhaltungsfehler: `6.228351168147128e-14`;
- 8 fokussierte Tests bestanden.

## Naechster Anschluss

W7-BF hat den symmetrischen BA/R1-Gegenpfad und eine exakte AB/R1-
Wiederholung statisch registriert. W7-BG implementiert als naechstes den
privaten Zweirollenexecutor mit Wiederholungsstoppschranke. Weitere Pfade und
hoehere Aufloesungen bleiben gesperrt.
