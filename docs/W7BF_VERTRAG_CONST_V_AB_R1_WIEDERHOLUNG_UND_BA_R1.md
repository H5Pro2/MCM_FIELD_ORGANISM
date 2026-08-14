# W7-BF: Vertrag fuer CONST-V-AB/R1-Wiederholung und BA/R1

## Zweck

W7-BF registriert die naechste eng begrenzte Ausfuehrungsstufe nach W7-BE.
Zuerst muss der kanonische AB/R1-Lauf exakt wiederholt werden. Nur wenn alle
gebundenen Oberflaechen bytegleich bleiben, darf danach der symmetrische
BA/R1-Gegenpfad materialisiert werden.

## Gebundene Grundlage

- W7-BC-Vertragsdigest: `973ac164...f5f9`
- W7-BD-Adapterdigest: `496a7955...58db`
- kanonischer W7-BE-Ergebnisdigest: `88fd9722...8708`
- W7-Y-Plan: `c771a3c...5b32`
- Modell: `const-v`
- Aufloesung: R1

## Ausfuehrungsreihenfolge

1. `AB/R1-exact-repeat`
2. nur nach bestandener Wiederholung: `BA/R1-primary`

Die AB-Wiederholung muss Anfangszustand, fuenf Hauptproduktionen, fuenf
Checkpointmessungen, alle Rohsamples, alle Runtimediagnosen, Endzustand und
Gesamtdigest exakt reproduzieren. Jede Abweichung stoppt vor BA/R1.

BA/R1 verwendet ausschliesslich den vorhandenen W7-Y-Pfad `ba`: den
autorisierten additiven B-Praefix und die vier autorisierten additiven
A-Fortsetzungen. Pro Rolle bleiben fuenf Hauptproduktionen, fuenf isolierte
Proben und erwartete 91 Rohsamples je Probe gebunden. Vor jeder Probe werden
nur S und H auf der tiefen Kopie nullgesetzt; der technische Skalar bleibt
erhalten.

## Auswertungsgrenze

W7-BF nimmt keine Werte an und startet keine Ausfuehrung. AB und BA werden
spaeter zunaechst nur als rohe S/H/Skalar-Trajektorien bereitgestellt. R1
allein darf weder ein numerisches Epsilon noch einen Effektboden erzeugen.
CAP-, Profil-, Feldfunktions- und Memoryentscheidungen bleiben gesperrt.

## Naechster Anschluss

W7-BG hat den privaten Zweirollenexecutor ausgefuehrt: exakte AB/R1-
Wiederholung mit Stoppschranke und danach BA/R1. W7-BH registriert als
naechstes R2 fuer beide Richtungen. Distanzen und Profile bleiben gesperrt.
