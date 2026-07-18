# Befund 014: Reale endliche auditive Feldkette, Pilot

## 1. Kurzurteil

Die vollständige endliche auditive Kandidatenkette lief erstmals mit realem
Mikrofonkontakt durch:

```text
USB-Mikrofon
-> 48 logarithmische Rezeptorbänder
-> drei parallele B1-Nachhallkandidaten
-> auditiver MCM-Dock
-> unimodale Feldkonstellationen
```

Der Lauf trägt E1 für die technische Durchgängigkeit. Er trägt keinen Befund
über Ruhe, Relaxation oder organische Feldentwicklung, weil die vorgesehene
mittlere Ruhephase messtechnisch nicht ruhiger als die erste Phase war.

## 2. Laufdaten

```text
Datum:                 15. Juli 2026
Gerät:                 Mikrofon (USB PnP Device(Echo-058))
Treiberpfad:           Windows WASAPI, Geräteindex 9
Abtastrate:            48.000 Hz
Rezeptorfenster:       100 ms
Fortschritt:           10 ms
Rezeptorbänder:        48 logarithmische Bänder, 50 Hz bis 18 kHz
Gesamtdauer:           60 Sekunden
Vorgesehene Phasen:    20 s Kontakt / 20 s ruhig / 20 s anderer Kontakt
```

Es wurden keine Rohsamples und keine Audiodatei gespeichert.

## 3. Technischer Durchlauf

```text
gelesene Audio-Chunks:             6.000
vollständige Rezeptorlagen:        5.991
Audioüberläufe:                    0
active_zero:                       0
active_energy:                     5.991
Sequenzdigest:
ddac03b444d196d7d06f3a0928f82fc1b084eaab09f23b03cbb4e11115f1de82
```

Jeder der drei Nachhallkandidaten erzeugte 5.991 Feldfenster und 5.991
unimodale Feldkonstellationen. Kein Zustand wurde vom Verteiler umgeschrieben.

## 4. Beobachtete Phasen

| Phase | Lagen | mittlere gesamte Rezeptorenergie | maximale gesamte Rezeptorenergie |
|---|---:|---:|---:|
| 1 | 1.991 | 0,098432 | 0,758762 |
| 2 | 2.000 | 0,200111 | 0,924006 |
| 3 | 2.000 | 0,265201 | 0,625593 |

Phase 2 war damit nicht die schwächste Phase. Keine Phase erreichte exakte
technische Stille.

Mögliche Erklärungen sind reale Hintergrundwirkung, der abgespielte Inhalt
oder eine zeitlich nicht exakt mit dem Messbeginn getroffene Umschaltung. Ohne
Rohaufnahme kann und soll der konkrete Schallinhalt nicht nachträglich
rekonstruiert werden.

## 5. Parallele Nachhallkandidaten

Mittlere Summe des lokalen Nachhalls je Phase:

| `tau` | Phase 1 | Phase 2 | Phase 3 |
|---:|---:|---:|---:|
| 0,05 s | 0,098430 | 0,199485 | 0,265264 |
| 0,20 s | 0,098425 | 0,196678 | 0,266145 |
| 1,00 s | 0,098399 | 0,184628 | 0,268670 |

Die längere Zeitkonstante reagiert erwartungsgemäß träger auf den Anstieg der
gemessenen Rezeptorwirkung. Alle drei Verläufe bleiben vollständig durch B1
erklärt. Keine Variante wurde ausgewählt oder wirkte auf den Audiokontakt
zurück.

## 6. Tatsächlich gezeigt

- Realer Audio-In kann 60 Sekunden begrenzt und überlauffrei gelesen werden.
- Die breite Rezeptorlage bleibt über 5.991 Zustände vollständig.
- Der sparsame Feldkandidat verarbeitet die reale Lage innerhalb seines
  kontrollierten Wertebereichs.
- Drei passive Nachhallzeitkandidaten können parallel beobachtet werden.
- Jeder Feldzustand kann unverändert eine unimodale Konstellation bilden.
- Rohdatenhaltung ist für diese technische Durchgängigkeitsprüfung nicht
  erforderlich.

## 7. Nicht gezeigt

- kontrollierte Ruhe oder exakte Stille in Phase 2,
- Relaxation nach eindeutig beendetem Weltkontakt,
- Vorteil eines bestimmten `tau`,
- natürliche Auswahl einer Zeitlage,
- Kopplung, Beziehungsgeschichte oder Topologie,
- Reflexion, Offline-Erholung oder Feldintelligenz.

## 8. Evidenz und Status

```text
technische reale End-to-End-Kette: E1
kontrollierter Drei-Phasen-Effekt:  E0
zusätzliche MCM-Feldmechanik:       E0
Runtime-Freigabe:                   nein
```

## 9. Bester nächster Schritt

Der gleiche 60-Sekunden-Lauf wird einmal mit expliziten technischen
Umschaltsignalen bei Sekunde 20 und 40 wiederholt. Erst dann kann sicher geprüft
werden, ob die Feldlagen den beabsichtigten Weltphasen folgen.

Die Nachhallkandidaten bleiben passiv parallel. Es wird weiterhin keine
Variante ausgewählt und keine Rohaufnahme gespeichert.
