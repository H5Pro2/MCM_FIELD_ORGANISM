# Methodik 006: Passive reale Audiopegelkarte

## 1. Status

Diese Methodik entsteht nach dem ersten endlichen Mikrofonkontakt aus Befund
005. Ein bereits unmittelbar vorab angekündigter Fünf-Sekunden-Lauf mit
laufendem externem Audio wird nur als Pilot A1 geführt. Er zählt nicht als
Bestätigung der vollständigen Methodik.

## 2. Forschungsfrage

Welche kontinuierlichen lokalen Frequenzlagen R0 entstehen unter realer Stille
und externem Audio, und tragen feste absolute Pegelgrenzen über unabhängige
Wiederholungen, ohne an eine einzelne Aufnahme angepasst zu werden?

## 3. Unveränderte Eingangsgrenze

```text
Gerät:          Mikrofon (USB PnP Device(Echo-058))
Host-API:       Windows WASAPI
Abtastrate:     48000 Samples pro Sekunde
Fenster:        480 Samples / 0.01 Sekunden
Frequenzsonden: 200 Hz, 400 Hz, 800 Hz
Laufdauer:      5.0 Sekunden je Bedingung
Aufnahmepegel:  über alle verglichenen Bedingungen unverändert
```

Jeder Lauf wird ausdrücklich gestartet. Rohsamples, Audiodateien und
Transkripte werden nicht gespeichert.

Der Windows-Aufnahmepegel ist Teil der technischen Rezeptorgrenze. Wird er
zwischen zwei Bedingungen verändert, dürfen deren absoluten Energien nicht
kausal miteinander verglichen werden.

## 4. Bedingungen

- **A0:** technische Raumstille ohne bewusst abgespieltes Audio,
- **A0R:** unabhängige Wiederholung von A0,
- **A1S1/A1S2:** aufeinanderfolgende Abschnitte eines laufenden externen
  Audiostroms bei unveränderter Geräte- und Lautstärkelage,
- **A1R:** derselbe Audioausschnitt erneut ab demselben bekannten Startpunkt,
- **A2:** dasselbe externe Audio bei kontrolliert verändertem Abstand,
- **A2R:** unabhängige Wiederholung von A2.

Der Pilot A1 darf die späteren Wiederholungen nicht ersetzen. Zwei
aufeinanderfolgende Abschnitte eines fortlaufenden Audios sind keine
Wiederholung desselben Reizes.

## 5. Passive Messgrößen

Je Frequenzkanal werden ausschließlich technische Aggregate gebildet:

- Minimum, Maximum und Mittelwert,
- Quantile `q05`, `q25`, `q50`, `q75`, `q95`, `q99`,
- Anzahl der Fenster oberhalb fester Pegel,
- positive und negative Pegelübergänge,
- Überlaufzahl und technischer Beobachtungsdigest.

Die vor dem Pilotlauf angekündigte feste Pegelfamilie lautet:

```text
0.001 / 0.002 / 0.005 / 0.010 / 0.020
```

Sie bleibt für alle Bedingungen unverändert. Sie ist eine Beobachtungsskala,
keine freigegebene Spike- oder Feldschwelle.

## 6. Pflichtvergleiche

1. A0 gegen A0R: technische Stillevarianz.
2. A1S1 gegen A1S2: natürliche Variation innerhalb des Audiostroms.
3. A1S1 gegen A1R: Wiederholbarkeit desselben Audioausschnitts.
4. A0/A0R gegen A1S1/A1S2: Trennung von Grundpegel und Audio.
5. A1R gegen A2: Abstands- und Pegelabhängigkeit.
6. Alle Kanäle gegen die unveränderte kontinuierliche R0-Referenz.
7. Alle absoluten Grenzen gegen eine reine Rang- oder Quantilbeschreibung.
8. Bestätigung, dass zwischen verglichenen Läufen kein Aufnahmepegel verändert
   wurde.

## 7. Scheiterkriterien

Die feste Pegelfamilie trägt nicht als robuste Ereignisgrenze, wenn:

- A0 und A1 stark überlappen,
- Wiederholungen derselben Bedingung stärker streuen als die Bedingungen,
- kleine Abstandsänderungen alle Übergänge beliebig verschieben,
- nur nachträglich angepasste Grenzen eine Trennung erzeugen,
- ein Kanal allein wegen Gerätecharakteristik dominiert,
- technische Fensterung die Übergänge bestimmt.
- der Aufnahmepegel zwischen den Bedingungen verändert wurde.

## 8. Evidenzgrenze

Ein erfolgreicher Vergleich kann E1 bis E2 für die reale technische
Pegelreichweite der Rezeptorfläche tragen. Er zeigt kein Hören, kein
MCM-Neuron, keine natürliche Schwelle und keine Feldintelligenz.

## 9. Stoppregel

Keine Schwelle wird nach Pilot A1 in die Runtime übernommen. Vor jeder
Ereignis- oder Spikeentscheidung müssen mindestens A0, A0R, A1R, A2 und A2R
vorliegen und gegen die kontinuierliche R0-Referenz ausgewertet sein.

## 10. Bester nächster Schritt

A0, A0R und zwei fortlaufende Audioabschnitte A1S1/A1S2 liegen bei
unverändertem abgesenktem Aufnahmepegel vor. Als nächstes muss derselbe
Audioausschnitt zweimal ab demselben Startpunkt abgespielt werden. Erst das
prüft Reizwiederholung statt bloßer Variation des laufenden Programms.
