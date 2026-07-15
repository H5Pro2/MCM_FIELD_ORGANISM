# Methodik 008: Endlicher Breitband-Hörpfad

## 1. Forschungsfrage

Kann die breite logarithmische Rezeptorfläche als sauber begrenzter
kontinuierlicher Hörpfad betrieben werden, ohne Rohdatenhaltung, impliziten
Feldzustand, Schwellen, Spikes oder Observerrückwirkung?

## 2. Prüfkonfiguration

```text
Abtastrate:       48000 Hz
Chunk:            480 Samples / 10 ms
Fenster:          4800 Samples / 100 ms
Frequenzbereich:  50 Hz bis 18 kHz
Hauptkandidat:    48 logarithmische Bänder
Laufgrenze:       höchstens 10 Sekunden
```

24 und 64 Bänder müssen mit derselben Pfadmechanik austauschbar bleiben.

## 3. Zustandsgrenze

Der Pfad darf pro abgeschlossenem Fenster genau eine unveränderliche auditive
Rezeptorlage erzeugen. Ein fünfsekündiger Lauf besitzt:

```text
500 Eingabe-Chunks
10 Chunks Warm-up
491 abgeschlossene Rezeptorlagen
```

## 4. Pflichtprüfungen

- Stille und exakter `active_zero`-Status,
- kontrollierter Einzelton und `active_energy`-Status,
- Mehrklang als verteilte Lage,
- exakte Samplezeit jedes Fensters,
- Warm-up ohne vorzeitigen Zustand,
- identische Wiederholung nach explizitem Reset,
- Observer an und aus,
- unveränderliche Lage,
- Abwesenheit von Rohsamples in Lage und Zusammenfassung,
- zu kurze Dauer,
- nicht ausgerichtete Dauer,
- zu kurze Quelle,
- ungültiger Chunk,
- exakte Anzahl gelesener Chunks,
- kein stilles Wiederverwenden eines nicht zurückgesetzten Pfads,
- Austauschbarkeit von 24, 48 und 64 Bändern.

## 5. Zusammenfassung

Nach einem Lauf dürfen nur folgende Aggregate zurückgegeben werden:

- Geometrie und Trägerkennungen,
- Eingabe- und Ausgabezahl,
- technische Dauer,
- Minimum, Maximum und Mittel je Band,
- Zahl exakter Null- und Energielagen,
- Überlaufzahl,
- Digest der technischen Zustandsfolge.

## 6. Stoppregeln

Die Mechanik wird nicht an das reale Mikrofon oder ein MCM-Feld übergeben,
wenn:

- Rohsamples in öffentlichen Zuständen auftauchen,
- technische Zeit von Laufzeitreihenfolge abhängt,
- Observer die Ausgabe verändert,
- Reset nicht exakt ist,
- der Pfad über die Laufgrenze hinaus liest,
- eine Schwelle für den Grundvertrag benötigt wird,
- Rezeptorenergie als Nachhall oder Feldaktivierung ausgegeben wird.

## 7. Evidenzgrenze

Ein positiver Lauf kann E1 für einen sauberen endlichen Breitband-Hörpfad
tragen. Er zeigt weiterhin kein auditives MCM-Feld, Hören im erlebenden Sinn,
Lernen oder Feldintelligenz.

## 8. Bester nächster Schritt

Nach den synthetischen Kontrollen wird entschieden, ob der Pfad lokal mit dem
stummgeschalteten Mikrofon geprüft werden soll. Ein Push erfolgt erst nach
ausdrücklicher Freigabe durch den Nutzer.
