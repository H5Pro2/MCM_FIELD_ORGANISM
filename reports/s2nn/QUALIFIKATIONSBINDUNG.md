# S2-NN: private Halbprofil-Runtime-Anbindung

Qualifikations-ID: `s2nn-half-profile-runtime-qualification-20260907-01`.
Genau ein Aufruf von `tests.test_s2nn_private_half_runtime_binding`, 14
Testkoerper, failfast, maximal 180 Sekunden. Keine Wiederholung der NL-/NM-Suiten.

## Vorab festgelegte neutrale Folge

Nur synthetische reduzierte Ausgangszustaende mit echten Rezeptor-, Zeit-,
Pairing- und Cue-Datentypen. Keine PCM-/RGB-Erzeugung oder Rezeptoranalyse.
Das prueft die Anbindung, nicht reale Quellen oder universelle Numerik.

| Ordinal | Form | Roh-Audio | Visual |
| --- | --- | --- | --- |
| 1 | COMPLETE_AV_PERCEPTION | 48 x 0.5 | 288 x 0.25 |
| 2 | PARTIAL_AUDITORY_CUE | 48 x 0.5 | nicht vorhanden |
| 3 | COMPLETE_AV_PERCEPTION | 48 x 0.5 | 288 x 0.25 |
| 4 | PARTIAL_VISUAL_CUE | nicht vorhanden | 32 x 0.25, 256 x 0.0 |

NJ bildet pro auditivem Ereignis einmal 48 x 0.25. Keine erneute Projektion
je Regelarm. Native Audiofenster `[0,4800]`, `[4800,9600]`, `[9600,14400]`,
Snapshotindizes 0/10/20, Uhr `audio.sample`. Visualfenster `[2,3]`, `[8,9]`,
`[11,12]`, Uhr `video.frame`. Gemeinsame Feldfenster enden bei 100/200/300/400 ms;
jeweils die letzten 10 ms sind gemeinsames Kontaktfenster. Felduhr explizit
`s2nn-neutral-field-clock`. Ereignis 2 bleibt read-only; Ereignis 3 setzt den
bestehenden Zustand fort. Beide Regeln erhalten dieselben Eingabeobjekte,
aber getrennte Runtime-, Feld-, Memory-, Prozessor- und Ereignisownerinstanzen.

Keine Sollrolle im Produktmodul. Im Test erwartet: auditiver A-Kandidat nach
erster Formation, gueltige visuelle Enthaltung bei zwei gleichen B4-Eintraegen
nach zweiter Formation. Keine Rangfolge/Deduplikation im Teilscan.

## Feste 14 Pruefgruppen

1. Halbprofil, Grenzen, Rangumrechnung, feste Regeln und geschlossenes Hauptgate.
2. Drei NJ-Projektionen, gemeinsame neue Werte, Ablehnung bereits projizierter Eingaenge.
3. Ablehnung alter Konfigurationen und gemischter Zustaende in beiden Richtungen.
4. Instanztrennung, Ereignisowner ueber unveraendertes MR, close und Terminalitaet.
5. Formation/Fortsetzung ueber einen read-only Hinweis; beide PPB-Banken atomar erzeugt.
6. Feldkontakte und Feldfortschreibung, nur Vergleich zwischen neuen Regelarmen.
7. Beide Hinweise read-only, Baselines gleich, gueltige Enthaltung technisch akzeptiert.
8. Unveraenderter Visualpfad und identische Slow-Belege beider Regeln.
9. Quellen-, Zeit-, Profil- und Projektionsmanipulationen abweisen.
10. Vollstaendige Scans und unveraenderte Serialisierungs-/Ressourcenlimits.
11. Scanfehler: Praefix 1..2, beide Scans bewusst injiziert fehlerhaft, Feld bleibt gueltig.
12. Atomarer Fehler: Praefix 1..3, realer auditiver PPB-Vorschlag vor injiziertem
    visuellem PPB-Fehler; kein B4-/Fast-/Slow-Teilcommit, Feld bleibt gueltig.
13. Fehlender Abrufbeleg und falsches Profil im Verifikator abweisen.
14. Unveraenderliche Eingaben; Validierung fuehrt keine zweite NJ-Projektion aus.

Fehlerinjektionen ausschliesslich in der neutralen Testfixture und temporaer;
keine Aenderung historischer Dateien/Defaultadapter. Die beiden absichtlich
fehlgeschlagenen Praefixe sind Qualifikationskontrollen, keine Hauptlaeufe
oder Retries der Vierereignisfolge.

## Budgets und Beleggrenze

- 3 gueltige NJ-Projektionen; 2 zusaetzliche, abzuweisende NJ-Aufrufe
  fuer falschen Eingangstyp und falsche Zeit. Keine neuen Zahlenpaare.
- 3 kleine Kompositionen mit 4/2/3 Ereignissen je Regelarm: 18 Runtimeereignisse.
- 10 Formationsversuche, davon 8 erfolgreiche Commitvorgaenge und 2 injizierte
  atomare Fehler. 8 PPB-Aufrufversuche: 6 erfolgreich, 2 injiziert fehlgeschlagen;
  die beiden auditiven Zwischenvorschlaege im Fehlerpfad werden nicht veroeffentlicht.
- 4224 transiente Feldkontakte. Keine Alt-/Neu-Feldgleichheit und kein Feldgain.
- 16 Scanadapterversuche: 12 vollstaendige Abrufbelege, 4 injizierte Fehler.
- Pro auditivem Arm vollstaendig 9/3/8, maximal 528 Wertvergleiche; visuell
  9/3/4, maximal 800. Gesamtobergrenze der erfolgreichen Abrufe: 7424
  Wertvergleiche, Verifikation separat. Formation-L1-Budget maximal 35520.
- Eingangsbindung maximal 65536 Byte. Bestehendes NG-Limit pro Aufzeichnung
  4194304 Byte, Zustand 98304, gepackter Eingang/gepaartes Ereignis je 16384,
  Scan strikt unter 32768 Byte. Drei Aufzeichnungen und drei Pruefbelege;
  keine neue Recorderplattform, keine Budgeterhoehung bei Fehlern.
- Quellhashes, Testinventar und Gates vor dem einzigen Testaufruf binden;
  danach Hashgleichheit und Gates lesend pruefen.

S2-NM bleibt eine akzeptierte **semantische Profilabweichung**, kein Gewinn.
Kein Genauigkeitstrick und keine verlustfreie Migration. Technische
Qualifikation ist keine reale Transfer-/NH-Freigabe. Hauptgates bleiben False.
