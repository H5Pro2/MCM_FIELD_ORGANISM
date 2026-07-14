# Methodik 007: Breite logarithmische Audiorezeptorfläche

## 1. Ausgangspunkt

Die bisherigen drei Frequenzsonden bei `200`, `400` und `800 Hz` waren
Kontrollinstrumente. Sie tragen keinen vollständigen auditiven Weltkontakt.

Methodik 007 prüft deshalb erstmals eine breite passive Rezeptorfläche. Sie ist
von der noch offenen realen Pegelkarte aus Methodik 006 getrennt.

## 2. Forschungsfrage

Kann eine transparente, logarithmisch angeordnete Rezeptorfläche reale
Audiosamples zwischen `50 Hz` und `18 kHz` als verteilte lokale Energielage
abbilden, ohne Sprache, Musik, Objekte, Bedeutung, Spikegrenzen oder
Feldkopplung vorzugeben?

## 3. Technische Eingangsgrenze

```text
Abtastrate:          48000 Samples pro Sekunde
Weltbereich:         50 Hz bis 18000 Hz
Analysefenster:      4800 Samples / 100 ms
Fortschritt:         480 Samples / 10 ms
Fensterfunktion:     Hann
Spektraltransformation: reelle FFT
Bandform:            überlappende logarithmische Dreiecke
Bandkandidaten:      24 / 48 / 64
```

Das 100-ms-Fenster enthält fünf Perioden bei `50 Hz`. Es ist eine feste
technische Rezeptorreichweite, kein Gedächtnis und kein lernender Zustand.

## 4. Rezeptorgeometrie

Die Stützpunkte der Bänder werden geometrisch zwischen `50` und `18000 Hz`
verteilt. Jeder Kanal erhält ausschließlich:

- eine stabile technische Kennung,
- eine untere Stützfrequenz,
- eine Mittenfrequenz,
- eine obere Stützfrequenz,
- eine nichtnegative lokale Energie.

Benachbarte Bänder überlappen. Ein Ton darf daher mehrere benachbarte Träger
anregen. Eine one-hot-artige Frequenzklasse wird ausdrücklich nicht verlangt.

## 5. Zulässige Berechnung

```text
100-ms-Rohfenster
-> Hann-Gewichtung
-> Amplitudenspektrum
-> lokale dreieckige Bandgewichtung
-> verteilte nichtnegative Energielage
```

Das Rollfenster bewahrt nur die technisch benötigten letzten `100 ms`. Nach
Reset muss es exakt leer sein. Es erzeugt keinen Nachhall über das Fenster
hinaus und schreibt nicht auf den Audioeingang zurück.

## 6. Baselines

- **B0:** Stille muss exakt null bleiben.
- **B1:** Einzelne lineare FFT-Bins als vollständige technische Gegenreferenz.
- **B2-24:** logarithmische Fläche mit 24 Bändern.
- **B2-48:** logarithmische Fläche mit 48 Bändern.
- **B2-64:** logarithmische Fläche mit 64 Bändern.
- **B3:** bisherige drei Einzelsonden nur als historische Minimalreferenz.

Keine B2-Variante wird vor dem Vergleich als richtige Hörgeometrie ausgewählt.

## 7. Pflichtreize

Kontrollierte Einzeltonlagen:

```text
50 / 80 / 125 / 250 / 440 / 1000 / 2000 / 4000 / 8000 / 12000 / 16000 / 18000 Hz
```

Zusätzlich:

- Stille,
- unterschiedliche Phase,
- halbe und volle Amplitude,
- zwei und drei gleichzeitige Frequenzen,
- Frequenzen unterhalb und oberhalb des Weltbereichs,
- identische Wiederholung nach Reset,
- verschobene Chunk- und Berechnungsreihenfolge, soweit kausal zulässig.

## 8. Pflichtmessungen

- dominante Mittenfrequenz je Einzelton,
- Entfernung des dominanten Bandes zur Reizfrequenz auf Log-Skala,
- Aktivitätsbreite über Nachbarbänder,
- Energieverlust an `50 Hz` und `18 kHz`,
- Amplitudenskalierung,
- Phasenempfindlichkeit,
- Trennung gleichzeitiger Frequenzlagen,
- qualitative Stabilität über 24, 48 und 64 Bänder,
- exakte Reset- und Wiederholbarkeit,
- Warm-up-Reichweite des 100-ms-Rollfensters.

## 9. Erfolgskriterien

Die passive Rezeptorfläche trägt nur dann E1, wenn:

1. Stille exakt null bleibt.
2. Alle Pflichtfrequenzen innerhalb ihrer lokalen Bands sichtbar sind.
3. Amplitudenskalierung ohne Sättigung proportional bleibt.
4. Phase die qualitative Bandlage nicht verändert.
5. Mehrklänge mehrere lokale Regionen statt einer Summenklasse erzeugen.
6. Reset dieselbe Folge exakt reproduziert.
7. Kein Zustand länger als die ausgewiesenen `100 ms` trägt.
8. 24, 48 und 64 Bänder denselben groben Frequenzort tragen.

## 10. Scheiter- und Stoppkriterien

Nicht zum Mikrofonlauf übergehen, wenn:

- `50 Hz` im gewählten Fenster nicht stabil sichtbar ist,
- Randfrequenzen systematisch verschwinden,
- Phase den dominanten Frequenzort beliebig verschiebt,
- Bandzahl den qualitativen Ort eines Einzeltons verändert,
- Mehrklänge in eine einzige globale Größe kollabieren,
- das Rollfenster nach Reset technische Geschichte bewahrt,
- für Erfolg eine semantische oder datenabhängig angepasste Grenze nötig wird.

## 11. Evidenzgrenze

Ein positiver synthetischer Lauf kann E1 für eine breite technische auditive
Rezeptorfläche tragen. Er zeigt keine menschliche Cochlea, kein vollständiges
menschliches Hören, kein MCM-Neuron, kein auditives MCM-Feld und keine
Feldintelligenz.

## 12. Architekturfreigabe

Freigegeben ist ausschließlich passive Rezeptor- und Observerlogik. Gesperrt
bleiben:

- adaptive Frequenzbänder,
- gelernte Filter,
- automatische Verstärkung,
- Spike- und Ereignisschwellen,
- Kopplung zwischen Frequenzträgern,
- Nachhall außerhalb des technischen Fensters,
- Muster-, Sprach- oder Musikerkennung.

## 13. Bester nächster Schritt

Nach der synthetischen Prüfung wird genau ein endlicher realer Mikrofonlauf
durch dieselbe breite Rezeptorfläche geführt. Erst dessen vollständige
verteilte R0-Lage darf mit der bisherigen Drei-Sonden-Referenz verglichen
werden.
