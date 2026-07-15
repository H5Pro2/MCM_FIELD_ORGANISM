# Befund 010: Endlicher Breitband-Hörpfad

## 1. Bezug

Ausgeführt wurde
[Methodik 008](../methodik/008_ENDLICHER_BREITBAND_HOERPFAD.md) auf Grundlage
der [auditiven Rezeptor-zu-Feld-Grenze](../architektur/003_AUDITIVE_REZEPTOR_ZU_FELD_GRENZE.md).

Es wurden ausschließlich synthetische Quellen verwendet. Das reale Mikrofon
wurde in diesem Versuch nicht geöffnet.

## 2. Implementierter Pfad

```text
endliche Quelle mit 10-ms-Chunks
-> 100-ms-Rollfenster
-> logarithmische Spektralrezeptoren
-> unveränderliche auditive Rezeptorlage
-> passive technische Zusammenfassung
-> [MCM-Feldgrenze bleibt geschlossen]
```

Die Rezeptorlage trägt nur technische Geometrie, Samplezeit, Trägerkennungen,
Bandenergien und exakten Kontaktstatus.

## 3. Ausführung

```text
python -m unittest -v tests.test_broadband_hearing_path
```

Ergebnis:

```text
15 Tests
15 bestanden
0 Fehler
0 Fehlschläge
```

Die anschließende vollständige Projektsuite bestand ebenfalls:

```text
python -m unittest discover

125 Tests
125 bestanden
```

## 4. Zeit- und Fensterbefund

Die ersten neun 10-ms-Chunks erzeugen noch keine Rezeptorlage. Nach dem zehnten
Chunk entsteht exakt:

```text
snapshot_index:       0
window_start_sample:  0
window_end_sample:    4800
```

Der folgende Zustand trägt:

```text
snapshot_index:       1
window_start_sample:  480
window_end_sample:    5280
```

Damit stammt jede Lage aus einem vollständigen kausalen Fenster. Wandzeit wird
nicht als innere Zeit verwendet.

## 5. Kontaktstatus

Exakte synthetische Stille erzeugt:

```text
active_zero
```

Jede numerisch messbare Bandenergie erzeugt:

```text
active_energy
```

Es existiert keine Pegelschwelle. Ein reales stummgeschaltetes Mikrofon kann
daher wegen seines technischen Grundpegels weiterhin `active_energy` tragen.

## 6. Verteilte Hörlage

Ein kontrollierter Mehrklang bei `250`, `4000` und `12000 Hz` blieb als drei
lokale aktive Frequenzregionen erhalten. Der Pfad fügte keine Summenklasse,
Ereigniskennung oder semantische Bezeichnung hinzu.

## 7. Endlichkeit und Fehlergrenze

Gezeigt wurde:

- exakt begrenzte Eingabezahl,
- kein Lesen nach dem Laufende,
- Ablehnung zu kurzer und nicht ausgerichteter Dauer vor dem ersten Lesen,
- Fehler am exakten ungültigen Chunk,
- keine gültige Teilzusammenfassung bei Quellenabbruch,
- kein stilles Wiederverwenden eines nicht zurückgesetzten Pfads,
- exakte Wiederholung nach explizitem Reset.

Ein Lauf mit 20 Chunks erzeugte erwartungsgemäß 11 abgeschlossene
Rezeptorlagen.

## 8. Observer- und Datengrenze

Observer an und aus erzeugten dieselbe Zusammenfassung und denselben Digest.
Rezeptorlagen sind unveränderlich.

Öffentliche Zustände und Zusammenfassungen enthalten insbesondere nicht:

- Rohsamples oder Audioframes,
- Pfade oder Audiodateien,
- Wörter, Sprecher oder Bedeutung,
- `activation`, `afterimage` oder `local_resources`.

Die letzten drei Rollen bleiben dem noch nicht entwickelten MCM-Feld
vorbehalten.

## 9. Geometrieaustausch

24, 48 und 64 Bänder durchliefen denselben Hörpfadvertrag. Geändert wurde nur
die explizite Rezeptorgeometrie. Der Pfad selbst enthält keine Gewinnerregel
und wählt keine Bandzahl aus.

## 10. Evidenz

**E1 für einen endlichen, reproduzierbaren und rohdatensparenden
Breitband-Hörpfad bis zur auditiven Rezeptorlage.**

Weiterhin **E0** für:

- ein auditives MCM-Feld,
- Nachhall jenseits des technischen 100-ms-Fensters,
- MCM-Neuronen und Feldkopplung,
- Hören im erlebenden Sinn,
- organische Entwicklung und Feldintelligenz.

## 11. Architekturentscheidung

Der Hörpfad darf lokal als Vorfeldmechanik bestehen bleiben. Rezeptorenergie
wird nicht direkt in `SensorFieldState.activation` kopiert. Die Feldgrenze ist
im Code und in der Dokumentation sichtbar geschlossen.

## 12. Bester nächster Schritt

Vor einer Feldmechanik muss eine konkrete fehlende Funktion benannt werden,
die weder die gegenwärtige breite Rezeptorlage noch ihr festes 100-ms-Fenster
erfüllt.

Der kleinste nächste technische Schritt wäre ein ausdrücklich freigegebener,
endlicher Lauf des neuen Pfads mit dem stummgeschalteten realen Mikrofon. Er
würde prüfen, ob die reale technische Grundlage sauber als `active_energy`
ankommt. Er würde noch keine Feldmechanik freigeben.
