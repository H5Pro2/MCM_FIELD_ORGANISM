# S2-C4: r1.a-Fast-State-Angleichung und Probe P

Stand: 2026-08-07

Status: `S2C4_R1_FAST_STATE_EQUALIZATION_AND_PROBE_BOUND`

Gegenbaseline N8: nicht ausgefuehrt

Vollmatrix: gesperrt

Forschungslauf: nein

## Zweck

S2-C4 schliesst den ersten kanonischen technischen Bildung-Probe-Pfad:

```text
r1.a bis 8.0 s
-> externe Angleichung von S und H auf exakt null
-> L unveraendert erhalten
-> identische kanonische Probe P von 8.0 bis 8.4 s
-> getrennte Fortsetzung durch B0 oder B2
```

Der Pfad dient nur der technischen Verdrahtung. Er fuehrt weder N8 noch eine
Forschungsmetrik, Entscheidung oder Interpretation aus.

## Kanonischer Probeplan

`prepare_s2c4_probe_plan` reduziert P mit den vorhandenen neutralen Audio-
und Videorezeptoren bei festem Offset `8.0 s`. Der Plan bindet:

- den kanonischen Probe-Digest;
- getrennte Digests der auditiven und visuellen Rezeptorfolge;
- denselben Organismustakt wie die Bildungsgeschichte;
- genau einen Schritt von `8.0` bis `8.4 s`;
- 31 auditive und 4 visuelle, insgesamt 35 reduzierte Quellenstuetzpunkte.

Alle 35 Stuetzpunkte muessen genau einmal in den Probe-Batch eingehen. Es
werden keine Samples, Frames, Rezeptorfolgen oder Feldtrajektorien
persistiert.

## Externe S/H-Angleichung

`equalize_fast_state_for_probe` akzeptiert sowohl den schnellen B0-Zustand
ohne L als auch den B2-Zustand mit L. Die Operation:

- setzt Aktivierung S und Nachhall H an jedem Feldort exakt auf null;
- erhaelt Feldidentitaet, Docks, letzten Takt und letzte Verteilung;
- erhaelt den gesamten L-Zustand bytegenau, falls er vorhanden ist;
- fuehrt selbst keine Feldentwicklung aus.

Die Angleichung ist eine externe Versuchsoperation und keine Faehigkeit des
Organismus.

## B0/B2-Probe-Fortsetzung

`advance_s2c4_r1_probe` akzeptiert ausschliesslich ein abgeschlossenes
S2-C3-Ergebnis fuer `r1.a`, B0 oder B2 und den kanonischen Probeplan. Der
Probe-Batch wird durch denselben bestehenden transienten Modellpfad
fortgeschrieben wie die Bildungsgeschichte.

Gebundene technische Kontrollen:

- P beginnt exakt am Ende von r1.a bei `8.0 s`;
- B0 besitzt keine L-Kopplung;
- B2 verwendet `rho=8` und regulaer `g=0.25/s`;
- der technische B2-Nullarm `g=0` stimmt nach der Probe in seiner
  Fastprojektion exakt mit B0 ueberein;
- der aktive B2-Pfad ist digestgenau reproduzierbar;
- L ist vor P identisch mit L nach der Bildung und vor der Angleichung.

## Technische Pruefung

`tests/test_s2c4_r1_probe_path.py` prueft Probeplan, Stuetzpunktinventar,
Angleichung, Nullarmgleichheit, L-Erhaltung und Reproduktion.

```text
neue S2-C4-Suite:                  5 passed
gesamter relevanter Testverbund:  93 passed, 13 subtests passed
Python-Kompilation:               bestanden
```

Die bekannte Pytest-Cachewarnung hat keinen Einfluss auf die Ergebnisse.

## Aussagegrenze

S2-C4 zeigt nur, dass ein kontrollierter r1.a-Endzustand nach externer
Fast-State-Angleichung technisch dieselbe Probe P aufnehmen kann. Ohne N8,
paarweise Gegenbaseline und vorregistrierte skalare Auswertung wird keine
Geschichtswirkung beurteilt.

Insbesondere folgen daraus keine Aussagen zu Praegung, Memory, relativer
Feldzeit, innerem Kontext, Wiedererkennung, Semantik, Organisation,
Selbstregulation oder KI.

## Entscheidung

```text
r1.a-Bildung B0/B2:               gebunden
externe S/H-Angleichung:          gebunden
L-Erhaltung:                      bestanden
identische Probe P:               gebunden
vollstaendiger Probe-Handoff:     bestanden
B2-Nullarm gegen B0:              bestanden
aktive B2-Reproduktion:           bestanden
Gegenbaseline N8:                 nein
Forschungsmetrik:                 nein
Vollmatrix:                       gesperrt
Forschungslauf:                   nein
```

## Bester naechster Schritt

S2-C5 bis S2-C8 binden inzwischen N8, Observer, Einpaardistanzen und C1. Als
S2-C9 bis S2-C16 schliessen die A/B-Referenz bis zur kanonischen
End-to-End-Komposition. Der S2-Zwischenentscheid verweist als naechsten
Schritt auf den statischen S1-C-Kandidatenvertrag. Noch keine Vollmatrix,
L-Intervention, Forschungsentscheidung oder Laufnummer.
