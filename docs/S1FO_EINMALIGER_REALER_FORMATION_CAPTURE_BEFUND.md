# S1-FO: Einmaliger realer Formation-Capture-Befund

Stand: 2026-08-14

Status: `FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY`

## Laufgrenze

Der Besitzer gab genau einen nicht persistenten S1-FK-Formation-Capture-Lauf
mit maximal 14.000 Feldschritten frei. Der Lauf wurde genau einmal gestartet.
Der unmittelbare S1-FI-Preflight bestand vor dem ersten Formation-Arm und der
Autorisierungstoken wurde einmalig verbraucht.

```text
Ausfuehrungsmodus:                real
Fuenf-Arm-Runner-Aufrufe:         3 (r2, r4, r8)
Formationsergebnisse:             15
erfasste E1-Endzustaende:         15
ausgefuehrte Feldschritte:        14.000
atomare Rueckgabe:                ja
Probe:                            nein
Persistenz der Laufzustaende:     nein
Retry:                            nein
Nachparametrierung:               nein
Koordinatorentscheidung:          REAL_FORMATION_CAPTURE_COMPLETED_DIAGNOSTIC_ONLY
Koordinatordigest:                0779ed8e59e38454f477da23caa93b05f80d97b74288ae5ff307a2724fae594b
```

## Messung

Die vorregistrierte S1-FD-Auswertung lieferte:

```text
Kontrollen gueltig:               ja
AB/BA-Zustand unterscheidbar:     ja
alle Komponenten konvergiert:     ja
maximaler Identity-Fehler:        0.0
maximale Ablations-Linf:           0.0
maximaler Ressourcenfehler:       0.0
r8 AB/BA-Ordnungs-Linf:            0.0008568014728262579
Auswertungsentscheidung:          FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY
Auswertungsdigest:                cbd4df8b5218b5454d276e2f2c22cd0f0f21204d1d100eeb6a72be1cc68e5f22
```

Konvergenzkomponenten:

| Komponente | coarse Linf | fine Linf | r8 Linf | fine/r8 | konvergiert |
|---|---:|---:|---:|---:|---|
| active-ab | 3.4885390053043374e-05 | 1.736313599644745e-05 | 0.003700783680910391 | 0.004691745720240565 | ja |
| active-ba | 3.083542419913404e-05 | 1.5348894086337182e-05 | 0.003366784465237944 | 0.004558917936331994 | ja |
| active-order | 7.730995706986977e-06 | 3.857778631230144e-06 | 0.0008568014728262579 | 0.004502535013746906 | ja |

Alle relativen Feinwerte liegen unter der vorregistrierten Grenze `0.01` und
die Feinabweichungen sind kleiner als die Grobabweichungen.

## Technische Interpretation

Unter den gebundenen kontrollierten AV-Eingaben bestimmen AB und BA trotz
angeglichener Bestandteile, Supports, Abschlusszeiten und Kontaktintegrale
unterschiedliche E1-Bildungsendzustaende. Der Ordnungsrest liegt deutlich
ueber der absoluten Kontrolle `1e-12` und bleibt ueber die Verfeinerungen
numerisch stabil. Identity-, Formationsablations- und Ressourcenbaselines
sind exakt null.

Damit ist der bereits in S1-EC13/S1-EC19 beobachtete Ordnungszustand in einer
frischen, nicht persistenten Kette numerisch exakt reproduziert. Neu
geschlossen ist die damalige Captureluecke: Alle 15 lebenden E1-Zustaende
wurden vor Prozessende atomar erfasst und direkt mit der vorregistrierten
S1-FD-Regel ausgewertet. `Substrataehnlich` bezeichnet hier nur einen lokal
gebildeten technischen Zustandstraeger, nicht bereits ein Memory- oder
Gehirnsubstrat.

## Nichtnachweise

Der Lauf pruefte keine spaetere Weltprobe. Deshalb ist nicht nachgewiesen,
dass die gebildeten Zustaende eine spaetere Feldaufnahme unterschiedlich
beeinflussen. Ebenfalls nicht nachgewiesen sind:

- wiederholungsabhaengige lokale Substratveraenderung ueber mehrere Kontakte;
- latente Erhaltung nach einer getrennten Phase;
- begrenzte Hinweisreaktivierung;
- Abschwaechung, Loesung oder Kapazitaetswiederverwendung;
- Feldzeit, innerer Kontext, Reflexion oder Offline-Reorganisation;
- Memory, Organisation, Semantik, Selbstregulation oder KI.

## Offene Annahmen

Der Befund gilt fuer die implementierte E1-Mechanik, die gebundene AV-Welt und
die drei Aufloesungen r2/r4/r8. Eine allgemeine Uebertragbarkeit auf andere
Welten, Lauflaengen oder Substratmechaniken wurde nicht untersucht. Da der
Lauf nicht persistent war, stehen die 15 Zustandsvektoren nach Prozessende
nicht fuer eine nachtraegliche Probe zur Verfuegung.

## Bester naechster Schritt

S1-FP soll statisch einen neuen, getrennt zu autorisierenden
Formation-zu-Gemeinsame-Probe-Vertrag entwerfen. Er muss frisch gebildete
AB/BA-Zustaende innerhalb desselben nicht persistenten Prozesses an exakt
dieselbe neutrale spaetere Feldprobe uebergeben und E1-Ablation, Identity und
einen zustandsneutralen Kontrollpfad binden. Noch keine Ausfuehrung und keine
Wiederverwendung der verbrauchten S1-FK-Autorisierung.
