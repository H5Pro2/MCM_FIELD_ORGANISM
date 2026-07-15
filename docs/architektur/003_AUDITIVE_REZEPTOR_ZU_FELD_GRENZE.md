# Auditive Rezeptor-zu-Feld-Grenze

## 1. Zweck

Dieser Vertrag trennt die technische Hörschnittstelle vom noch nicht
entwickelten auditiven MCM-Feld:

```text
endliche Audioquelle
-> logarithmische Rezeptorfläche
-> auditive Rezeptorlage
-> [gesperrte Feldgrenze]
-> späteres auditives MCM
```

Eine Rezeptorlage ist noch kein Feldzustand, kein Neuron und kein Erleben.

## 2. Auditive Rezeptorlage

Jede abgeschlossene Lage trägt ausschließlich:

- technische Modalität,
- technische Rezeptorgeometrie,
- fortlaufenden Schnappschussindex,
- Beginn und Ende des kausalen Samplefensters,
- stabile Frequenzträgerkennungen,
- gegenwärtige nichtnegative Bandenergien,
- exakten technischen Kontaktstatus.

Rohsamples, Audioframes, Gerätepfade, Wörter, Sprecher, Musikklassen,
Ereignislabels und Observerdiagnosen sind ausgeschlossen.

## 3. Kontaktstatus ohne Schwelle

Zulässig sind zunächst nur:

```text
active_zero:   alle Bandenergien sind numerisch exakt null
active_energy: mindestens eine Bandenergie ist numerisch ungleich null
```

Ein reales stummgeschaltetes Mikrofon kann wegen Eigenrauschen weiterhin
`active_energy` erzeugen. Es wird keine Pegelschwelle eingeführt, um daraus
„kein Kontakt“ zu machen.

Fehlendes oder technisch ausgefallenes Gerät erzeugt keine gültige
Rezeptorlage, sondern einen expliziten Adapterfehler.

## 4. Technische Zeit

Die erste Lage entsteht erst nach einem vollständigen 100-ms-Fenster. Danach
folgt bei jedem 10-ms-Chunk eine neue Lage.

```text
window_start_sample = window_end_sample - window_size
window_end_sample   = Anzahl kausal gelesener Samples
```

Wandzeit und Betriebssystem-Timing werden nicht als innere Zeit übernommen.

## 5. Geometrie

24, 48 und 64 Bänder bleiben vergleichbare Rezeptorkandidaten. Ein einzelner
Hörpfad besitzt genau eine explizite Geometrie. Mehrere Geometrien dürfen nur
parallel im passiven Observer verglichen werden.

Die zunächst verwendete 48-Band-Geometrie ist eine Forschungskonfiguration,
keine festgeschriebene Anatomie.

## 6. Gesperrte Feldgrenze

Die Rezeptorenergie darf noch nicht automatisch in folgende Rollen umbenannt
werden:

- MCM-Aktivierung,
- Nachhall,
- Erregbarkeit,
- lokale Ressource,
- Verbindung oder Gewicht,
- Muster oder innere Bezeichnung.

Eine spätere Feldmechanik muss zuerst zeigen, welche Funktion über die
gegenwärtige Rezeptorlage und das feste 100-ms-Fenster hinaus fehlt.

Methodik 011 darf diese Grenze ausschließlich als passive B1-exakte
Forschungsprojektion überqueren. Die kontinuierliche Runtime und jede
zusätzliche Feldwirkung bleiben geschlossen.

## 7. Invarianten

1. Exakt dieselben Chunks erzeugen nach Reset dieselben Lagen und Digests.
2. Observer an oder aus verändert die Hörfolge nicht.
3. Jeder Zustand stammt aus einem vollständigen kausalen Fenster.
4. Kein Zustand enthält Rohsamples.
5. Ungültige Chunks erzeugen keine gültige Teilzusammenfassung.
6. Die Quelle wird nur für die vorab festgelegte Dauer gelesen.
7. Nach Laufende wird kein weiterer Chunk angefordert.
8. Reset entfernt die gesamte technische Fensterhistorie.
9. Kontaktstatus folgt nur exakter Nullheit, keiner angepassten Schwelle.
10. Die Feldgrenze bleibt im Code sichtbar und geschlossen.

## 8. Bester nächster Schritt

Methodik 011 bestätigt die verteilte lokale Rezeptor-/Nachhalllage als
B1-exakten passiven Schnellfeld-Kandidaten. Zusätzliche Feldmechanik bleibt
geschlossen.

Als Nächstes wird die vollständige endliche auditive Kette bis zur unimodalen
Feldkonstellation beobachtet. Mehrere Nachhallzeitkandidaten bleiben dabei
parallel und dürfen weder Weltkontakt noch Auswahl beeinflussen.
