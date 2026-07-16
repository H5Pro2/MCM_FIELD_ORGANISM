# Befund 027: Reale visuelle Ruhe-Nullbasis

## Kurzurteil

Zwei zeitmarkierte reale Läufe zeigen unter einer weitgehend unveränderten
Raumszene eine enge Ruhe-Nullbasis der bereits vorhandenen lokalen
Feldbeobachtung.

Die ursprünglich vorgesehene kontrollierte Veränderung fand nicht im
Bildbereich statt. Deshalb werden alle drei Zeitabschnitte ausschließlich als
aufeinanderfolgende Ruhefenster behandelt.

Der Befund ist keine Bewegungsprüfung und kein Nachweis visueller
Feldintelligenz.

## Methodische Korrektur vor der Auswertung

Ein erster Pilot zeigte, dass der allererste Kameraframe technisch auf den
leeren Startzustand der Neuronenschicht folgt. Diese Initialisierung würde die
Änderungsgröße der ersten Phase künstlich erhöhen.

Daraufhin wurde der Beobachter vor den hier ausgewerteten Läufen korrigiert:

```text
erster Frame
= sichtbarer Initialisierungsframe
= keine natürliche Feldänderung
= nicht Bestandteil der Phasenmittelwerte
```

Die Korrektur verändert weder Rezeptoren noch MCM-Neuronen und schreibt nichts
in das Feld zurück.

## Reale Läufe

Beide Läufe verwendeten:

- drei aufeinanderfolgende Zeitfenster von jeweils fünf Sekunden,
- dieselbe monotone Organismusuhr für Frameintervalle und Phasenmarken,
- 288 visuelle MCM-Neuronen,
- die unveränderte Rezeptorprojektions-Baseline,
- keine Rohbildspeicherung,
- keine Schwelle, Glättung oder Normalisierung.

### Lauf R1

```text
aufgenommene Frames:       85
auswertbare Frames:        24 / 24 / 24
Grenzframes:                2
Initialisierungsframes:     1
```

| Ruhefenster | mittlere absolute Rezeptoränderung | mittlere absolute lokale Aktivierungsdifferenz |
|---|---:|---:|
| R1 | 0,0004594983 | 0,0815481033 |
| R2 | 0,0004580106 | 0,0814687119 |
| R3 | 0,0004649161 | 0,0814078171 |

### Lauf R2

```text
aufgenommene Frames:       85
auswertbare Frames:        25 / 25 / 25
Grenzframes:                0
Initialisierungsframes:     1
```

| Ruhefenster | mittlere absolute Rezeptoränderung | mittlere absolute lokale Aktivierungsdifferenz |
|---|---:|---:|
| R1 | 0,0004683001 | 0,0819639517 |
| R2 | 0,0004614324 | 0,0818441188 |
| R3 | 0,0004715098 | 0,0818361992 |

## Getragener Befund

- Die gemessene Zeitmarkierung ordnet reale Frames reproduzierbar endlichen
  Fenstern zu.
- Grenzframes bleiben sichtbar und werden nicht passend einer Phase
  zugeschlagen.
- Nach Trennung der Initialisierung bleiben die mittleren absoluten
  Rezeptoränderungen innerhalb beider Läufe eng beieinander.
- Auch die vorhandenen lokalen Aktivierungsdifferenzen zeigen zwischen den
  aufeinanderfolgenden Ruhefenstern nur eine geringe Verschiebung.
- Die Feldbeobachtung läuft über reale Frames, ohne Bilder oder Objekte zu
  speichern.

Damit existiert erstmals eine reale Referenz dafür, wie diese beiden
Beobachtungsgrößen unter einer weitgehend unveränderten Szene aussehen.

## Nicht gezeigt

- Eine kontrollierte Veränderung wurde nicht in den Bildbereich eingebracht.
- Die Ruhefenster sind keine vollständige Rauschcharakterisierung.
- Die Mittelwerte beweisen keine lokale visuelle Invarianz.
- Eine lokale Veränderung könnte durch die Mittelung über alle Neuronen
  verdeckt werden.
- Es ist keine Bewegung, Richtung, Geschwindigkeit oder Objektidentität
  erkannt worden.
- Es ist kein visueller Nachhall und keine Persistenz geprüft worden.

## Evidenzgrenze

```text
reale zeitmarkierte Ruhe-Nullbasis: E1
kontrollierte visuelle Veränderung: E0
visuelle Feldfunktion:              E0
visuelle Persistenz:                E0
```

## Bester nächster Schritt

Als nächstes ist genau ein realer Lauf erforderlich, bei dem während des
mittleren Zeitfensters nachweislich eine fortlaufende Veränderung in den
Bildbereich gelangt. Erst dann dürfen die Ruhefenster dieses Befunds als
Vergleichsbasis dienen.

Falls die globale Mittelung eine sichtbare lokale Intervention trotzdem
verdeckt, muss vor jeder neuen Feldmechanik ausschließlich die räumliche
Verteilung der bereits vorhandenen lokalen Änderungen observerseitig geprüft
werden. Daraus darf kein Bewegungsdetektor entstehen.
