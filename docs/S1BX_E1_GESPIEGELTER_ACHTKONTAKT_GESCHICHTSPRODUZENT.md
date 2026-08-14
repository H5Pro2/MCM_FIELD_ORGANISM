# S1-BX: E1 gespiegelter Achtkontakt-Geschichtsproduzent

## Status

Vorregistrierter L/R-Geschichtsproduzent implementiert und fokussiert
abgenommen. Die eingefrorene identische E2-Probe wurde noch nicht mit den
erzeugten Endzustaenden ausgefuehrt. Kein E2-, Memory-, Lern-, Organismus-
oder KI-Befund.

## Implementierte Dateien

```text
mcm_field_organism/e1_mirrored_history.py
tests/test_e1_mirrored_history.py
```

Bestehende Runtime- und API-Dateien wurden nicht veraendert.

## Fester erster Korridor

```text
Geometrie:               Drei-Knoten-Linie, Positionen 0, 1, 2
Intervalle pro Arm:      8
Dauer pro Intervall:     1.0 s
linker Kontakt:          (1.0, 0.0, 0.0)
rechter Kontakt:         (0.0, 0.0, 1.0)
Rueckwirkung:            aktiv
Anfangsbindung:          b_e = 0
```

Die Funktion baut beide Kontaktfolgen intern, erzeugt tiefe objektgetrennte
Kopien von Feld und E1-Anfang und fuehrt beide Geschichten mit der
synchronen S1-BU-Kopplung aus. Eine Probe ist nicht Teil des Ergebnisobjekts.

## Implementierte Ausgabe

```text
E1MirroredHistoryResult
    left_field
    right_field
    left_e1_state
    right_e1_state
    left_contact_energy
    right_contact_energy
    total_binding_difference
    maximum_mirror_binding_error
```

## Fokussierte Abnahme

Ausgefuehrt mit:

```text
python -m unittest -v tests.test_e1_mirrored_history
```

Ergebnis:

```text
8 tests
OK
```

Im ersten Lauf erwartete ein Test faelschlich `layer.tick = 80`. Der Layer
zaehlt abgeschlossene Feldschritte und steht nach acht Intervallen korrekt bei
`8`; die gemeinsame Organismuszeit endet getrennt davon bei Tick `80`. Nur
diese Testannahme wurde korrigiert, die Produktion blieb unveraendert.

## Rohe Endwerte des festen Laufs

Kanonische E1-Kantenreihenfolge:

```text
b_L = (0.1453986710509028,
       0.018561235976152484)

b_R = (0.018561235976152484,
       0.14539867105090284)
```

Kontrollen:

```text
Kontaktenergie links:          8.0
Kontaktenergie rechts:         8.0
Gesamtbindungsdifferenz:       5.551115123125783e-17
maximale Spiegelabweichung:    5.551115123125783e-17
```

Historische Feldendwerte, nur zur Symmetriepruefung:

```text
S_L = (0.6151771581373853,
       0.25600827623408756,
       0.12847910300062543)

S_R = (0.1284791030006255,
       0.2560082762340876,
       0.6151771581373854)

H_L = (0.6152280362086605,
       0.25581920558718146,
       0.1282819454835286)

H_R = (0.12828194548352864,
       0.2558192055871815,
       0.6152280362086605)
```

Diese historischen S/H-Endwerte werden gemaess S1-BV nicht in die spaetere
Probe uebernommen.

## Bestandene Kontrollen

```text
acht gleiche Kontaktintervalle:      bestanden
gleiche Kontaktenergie:              bestanden
tiefe Objekttrennung:                bestanden
unveraenderte Eingaben:              bestanden
verschiedene kanonische Bindungen:   bestanden
gleiche Gesamtbindung:               bestanden
Spiegelsymmetrie der Bindungen:      bestanden
Spiegelsymmetrie der Endfelder:      bestanden
deterministische Wiederholung:       bestanden
neutraler E1-Anfang erzwungen:       bestanden
keine Probe im Ergebnis:             bestanden
API-Isolation:                       bestanden
```

## Gemeinsamer Regressionstest

Der E1-, Probe-, S/H-, Nachhall- und API-Verbund wurde um den
Geschichtsproduzenten erweitert:

```text
78 tests
OK
```

## Technisches Urteil

Die vorregistrierte Geschichtsproduktion ist gueltig. Gleiche Kontaktenergie,
Dauer und Amplitudenmenge erzeugen allein durch gespiegelte geometrische Lage
zwei verschiedene, gleich starke und gespiegelte E1-Kantenverteilungen.

Dies ist ein technischer geschichtsabhaengiger Zustandsbefund. Ob diese
Zustaende bei identischem S/H eine unterschiedliche spaetere Probe verursachen,
wurde in S1-BX absichtlich noch nicht geprueft.

## Aussagegrenze

Die E1-Endzustaende sind Ergebnisse der programmierten adaptiven
Kopplungsmechanik. Ihre Verschiedenheit ist weder Memory noch Emergenz. Die
historischen S/H-Endfelder duerfen nicht als Beleg einer erhaltenen
E1-Wirkung verwendet werden.

## Bester naechster Schritt

S1-BY hat den unveraenderlichen Ergebniscontainer und die exakte Komposition
aus S1-BX-Geschichten, einem frisch neutral vorbereiteten gemeinsamen
Probefeld, S1-BW-Aktiv-/Ablationsarmen, P0 und festen Gain-Gegenbaselines
gebunden. Als naechstes implementiert S1-BZ diese Komposition und fuehrt den
vorregistrierten E2-Lauf genau einmal aus.
