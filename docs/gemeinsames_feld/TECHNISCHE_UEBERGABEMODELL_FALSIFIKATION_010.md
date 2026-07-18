# Technische Übergabemodell-Falsifikation 010

## Status

Passive Baselineprüfung vor `GF_001`.

Diese Prüfung vergleicht vier mögliche zeitliche Lesarten kausaler
Rezeptorübergaben. Sie wählt keine davon aus und verändert weder Rezeptoren
noch MCM-Feld, Neuronen, Nachhall oder Memory.

## Kontrollierte Geschichte

Ein konstanter normierter Kontakt von `1,0` besteht genau eine Sekunde. Er
wird technisch auf zwei Arten dargestellt:

- dicht: 100 Übergaben im Abstand von `10 ms`,
- dünn: 20 Übergaben im Abstand von `50 ms`.

Beide Darstellungen beschreiben für diese Nullprüfung denselben konstanten
Kontakt. Ein Modell ist nur rateninvariant, wenn beide Darstellungen dasselbe
zeitliche Gesamtmaß ergeben.

## Baselines

### B0 - Punktübergabe

Jede Übergabe zählt einmal mit ihrem Kontaktwert:

```text
M_point = Summe Kontakt
```

Das Modell benötigt keine Stütze und kein Halten. Es kann dadurch aber die
technische Ereignisanzahl mit Kontaktmenge verwechseln.

### B1 - Halten bis zur nächsten Übergabe

Der letzte Kontaktwert wirkt bis zur nächsten Übergabe desselben Pfades:

```text
M_hold = Summe Kontakt * Zeit bis zur nächsten Übergabe
```

Diese Baseline ist ausdrücklich eine Sample-and-Hold-Annahme, keine
freigegebene Rezeptoreigenschaft.

### B2 - Vollständiges Quellfenster

Jede Übergabe wird mit der gesamten Breite ihres Analysefensters gewichtet:

```text
M_window = Summe Kontakt * Quellfensterbreite
```

Beim Audiofenster von `100 ms` überlappen aufeinanderfolgende Zustände stark.

### B3 - Neuer Quellfortschritt

Jede Übergabe wird nur mit dem seit der vorherigen Ausgabe neu
fortgeschrittenen Quellabschnitt gewichtet:

```text
M_advance = Summe Kontakt * Quellfortschritt
```

Für die auditive Sample-Uhr ist dieser Fortschritt exakt bekannt. Für Video
ist er nach den Audits 007 und 008 nicht belegt.

## Ergebnis

| Baseline | dicht | dünn | Differenz | Grenze |
|---|---:|---:|---:|---|
| B0 Punktübergabe | `100` | `20` | `80` | ratenabhängig |
| B1 Halten | `1,0` | `1,0` | `0` | unbelegte Halteregel |
| B2 Audiofenster | `10,0` | `2,0` | `8,0` | Überlappung zählt mehrfach |
| B3 Audiofortschritt | `1,0` | `1,0` | `0` | nur für Audio belegt |
| B2/B3 Video | unbekannt | unbekannt | unbekannt | keine zeitliche Stütze |

Sieben synthetische Kontrollen sichern die Rechnungen, unbekannte
Videostütze, geordnete Kausalität und das Fehlen einer ausgewählten
Runtime- oder Bedeutungsrolle.

## Befund

Unter der aktuellen Evidenz trägt keines der vier Modelle einen gemeinsamen
Audio-Video-Eingang ohne zusätzliche Annahme:

```text
Punktübergabe       -> technische Rate wird Wirkung
Halten              -> unbelegte Gültigkeitsdauer
volles Quellfenster -> überlappender Kontakt wird mehrfach gezählt
Quellfortschritt    -> für Video nicht bekannt
```

Der positive Audiobefund für B3 ist eng: Samplezählung kann einen vollständig
bekannten auditiven Kontakt rateninvariant bemessen. Das ist keine allgemeine
MCM-Feldzeit und keine Freigabe modalitätsspezifischer Gewichte.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Eine weitere Implementierung derselben vier Varianten würde die offene
Begründung nur in Runtime-Code verschieben. Vor dem nächsten technischen Lauf
muss konzeptionell geklärt werden, was ein Rezeptorzustand zwischen zwei
Übergaben **physisch im Organismus** ist:

- ein abgeschlossenes punktuelles Ereignis,
- ein fortbestehender aktueller Rezeptorzustand,
- oder ein eigener dynamischer Rezeptorprozess.

Diese Rolle muss aus der Rezeptorschicht begründet werden. Sie darf nicht vom
gemeinsamen MCM-Feld nachträglich erfunden werden.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
