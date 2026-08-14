# S1-C: Zulassungsvertrag fuer einen minimalen nichtlinearen lokalen Substratkandidaten

Stand: 2026-08-07

Status: `S1C_CONTRACT_BOUND_CANDIDATE_UNSELECTED`

Implementierung: gesperrt

Forschungslauf: nein

## Zweck

S1-C bindet die kleinste zulaessige Form einer neuen Substrathypothese nach
der technisch geschlossenen linearen B0/B2-Referenz. Der Vertrag waehlt noch
keine konkrete Gleichung. Er verhindert, dass eine bekannte Spur,
Hysteresekurve, Ressourcenregel oder ein adaptiver Leser nur unter neuem
Namen implementiert wird.

Der fehlende konkrete Kandidat ist kein technischer Fehler. Er ist die
gegenwaertige wissenschaftliche Grenze: Die bestehende MCM-Mechanik bestimmt
Ort, Kausalordnung und Testbarkeit einer langsamen Rolle, aber noch nicht ihre
nichtlineare konstitutive Naturform.

## Verbindlicher Bestandsabgleich

S1-C uebernimmt folgende Ergebnisse:

- S0 bindet genau einen ko-lokalisierten Skalar `L_i` je bestehendem Feldort.
- S1-A/S1-B und B2 bilden eine lineare reziproke Referenz, keinen
  eigenstaendigen Entwicklungskandidaten.
- S2-C16 schliesst den kanonischen technischen B0/B2-End-to-End-Pfad.
- Passivitaet und momentane Feldarbeit enthalten keinen verborgenen
  zusaetzlichen Entwicklungszustand.
- Viskoelastik reduziert sich auf feste Leaky-Moden.
- Memristive und Duhem-Formen reduzieren sich auf feste Hysterese oder
  adaptiven Gain.
- Phasen- und Ressourcenmodelle setzen eine Energielandschaft,
  Fliessrichtung oder Freigaberegel voraus.
- Die Deformationsrolle Q wurde als baselineaequivalent geschlossen.

Damit darf S1-C keine dieser Klassen ohne neue unabhaengige Begruendung
wieder oeffnen.

## Kleinster zulaessiger Zustandsraum

Es bleibt bei den vorhandenen Rollen:

```text
S_i = schnelle lokale MCM-Feldlage
H_i = schneller Nachhall, keine Schreibsteuerung fuer L
L_i = genau ein langsamer lokaler konstitutiver Skalar in [-1, 1]
```

S1-C fuehrt weder Q noch eine zweite L-Schicht, neue Kanten, Materialpartikel,
Slots oder gespeicherte Weltbezeichner ein. Eine spaetere Erweiterung des
Zustandsraums benoetigt einen neuen Ressourcenvertrag.

## Allgemeiner Gleichungsrahmen

Eine spaetere konkrete Hypothese muss dieselbe atomare Vorzustandsordnung
verwenden:

```text
dS_i/dt = F0_i(S, Weltkontakt) + X_i(S_i, lokale Nachbarn, L_i)
dL_i/dt = Y_i(S_i, lokale Nachbarn, L_i)
```

Dabei ist `F0` der bestehende schnelle MCM-Pfad. `X` und `Y` sind noch nicht
festgelegt. Beide Vorschlaege lesen denselben abgeschlossenen Vorzustand;
`L_(t+1)` darf nicht im selben Schritt als Ursache von `S_(t+1)` dienen.

Dieser Rahmen ist keine Kandidatengleichung. Insbesondere werden keine
Polynomordnung, Saettigung, Schwelle, Potentialmulde oder Zeitkonstante
vorweggenommen.

## Zulassungsbedingungen fuer X und Y

Eine konkrete Form wird nur zugelassen, wenn gemeinsam gilt:

1. **Unteilbare Mitentwicklung:** Bildung und Rueckwirkung lassen sich nicht
   in eine unabhaengige Spur `L` plus festen nachgeschalteten Leser zerlegen.
2. **Echte gemeinsame Nichtlinearitaet:** Mindestens eine lokale
   Zustandswirkung haengt gemeinsam von `S` und `L` ab. Eine blosse
   Ausgangssaettigung eines linearen Integrals genuegt nicht.
3. **Lokale Gleichheit:** Dieselbe Regel und dieselben inhaltsfreien Parameter
   gelten an allen gleichartigen Feldorten.
4. **Nullpfad:** Ein vor dem Arm fest gebundener Kopplungsnullwert reproduziert
   die bestehende S/H-Runtime exakt.
5. **Begrenzung:** Endlichkeit folgt aus der Gleichung und ihrer Bilanz, nicht
   aus ereignisabhaengigem Reset, Clipping oder globaler Renormierung.
6. **Ein Regelwerk:** Bildung, spaetere Wirkung, funktionaler Verlust und
   erneute Beanspruchung verwenden dieselben Gleichungen und Parameter.
7. **Technische Reversibilitaet:** Die Dynamik darf eine alte Wirkung durch
   weitere lokale Feldgeschichte funktionslos machen. Eine feste Ablaufzeit
   oder Loeschphase gilt nicht.
8. **Atomare Kausalitaet:** `S -> L` und `L -> S` sind getrennt ablatierbar,
   bleiben aber Teile derselben lokalen Transition.
9. **Teilungsinvarianz:** Verlustlose technische Unterteilung derselben
   Welttrajektorie konvergiert gegen dieselbe gekoppelte Zustandsbahn.
10. **Observerfreiheit:** Diagnose, Armname, Probe und spaetere Auswertung
    koennen die Zustandsentwicklung nicht beeinflussen.

## Zwingende unabhaengige Naturannahme

Vor einer Gleichung muss genau eine allgemeine digitale Naturannahme benannt
werden, die auch ohne das gewuenschte Memory-Ergebnis sinnvoll und pruefbar
ist. Sie muss:

- die lokale Ursache fuer `Y` benennen;
- Vorzeichen, Symmetrie und Wertebereich begruenden;
- die Rueckwirkung `X` aus derselben Wechselwirkung ableiten;
- mindestens einen moeglichen Verlauf ausschliessen, statt nur den
  gewuenschten Lebenszyklus zu erlauben;
- erklaeren, warum sie keine bekannte Pflichtbaseline ist.

`L soll Geschichte behalten`, `Wiederholung soll verdichten` oder `das Feld
soll sich erinnern` sind Zielbeschreibungen und keine Naturannahmen.

## Pflichtreduktionen vor Implementierung

Jede vorgeschlagene Form muss statisch gegen mindestens diese Klassen
geprueft werden:

| Kennung | Gegenklasse | Verwerfungsfrage |
| --- | --- | --- |
| B0 | schneller Nullpfad | Veraendert der Kandidat den deaktivierten Pfad? |
| B1 | lineare Leaky-Spur | Ist L nur exponentiell gewichtete S-Geschichte? |
| B2 | lineare reziproke Kopplung | Ist die gemeinsame Wirkung nur linear? |
| B3 | begrenzter Integrator | Ist die Nichtlinearitaet nur Saettigung? |
| B4 | zustandsabhaengiger Gain | Wird L nur als Antwortfaktor gelesen? |
| B5 | Rueckwirkungsablation | Bleibt die Wirkung ohne L-nach-S bestehen? |
| V | viskoelastische Moden | Ist die Dynamik nur eine Bank fester Zeitlagen? |
| M | Hysterese/Memristor | Ist Schreiben und Lesen durch eine feste Kennlinie vorgegeben? |
| F3 | konservierter Traeger | Ist L nur eine zweite Ressourcenverteilung? |
| Q | konstitutive Deformation | Fehlt erneut die unabhaengige MCM-Wirkungsquelle? |

Baselinegleichheit ist kein technisches Scheitern. Sie beendet nur den
Anspruch auf einen neuen Substratkandidaten.

## Statische Falsifikationsbedingungen

Eine vorgeschlagene Gleichung erhaelt vor Implementierung `STOPP`, wenn:

- ihre spaetere Wirkung bereits aus einer fest programmierten Kennlinie,
  Potentiallandschaft oder Attraktorkarte ablesbar ist;
- Wiederholungszahl, Weltzeit, Episode, Quelle oder Probe direkt gelesen
  werden;
- eine feste Schwelle Praegung, Loesung oder Wiederbindung ausloest;
- L nur Rohdaten, Momente, Flussdurchgang oder Aktivitaetsintegrale haelt;
- eine Richtung, Polaritaet oder Ressource nur wegen des erhofften Ergebnisses
  gewaehlt wurde;
- Wirkung und Funktionsverlust verschiedene Regeln benoetigen;
- kein statischer Unterschied zu einer gleich budgetierten Gegenbaseline
  angegeben werden kann;
- keine Gegenprognose existiert, bei der der Kandidat trotz Weltkontakt keine
  bleibende Wirkung entwickeln darf.

## Noch nicht erlaubte Erfolgsentscheidung

S1-C definiert keine Schwelle fuer Praegung oder Memory. Eine spaetere
technische Implementierung duerfte zunaechst nur Nullinvarianz, Endlichkeit,
Lokalitaet, Symmetrie, Teilung, Snapshot und Ablationen pruefen.

Erst danach duerfte eine getrennte Vorregistrierung kontrollierte
Weltgeschichten, S/H-Angleichung, identische Probe, Tausch,
Neutralisierung, funktionalen Verlust und andere Wiederbeanspruchung binden.

## S1-C-Entscheidung

```text
Zustands- und Kausalrahmen:       gebunden
Nichtlinearitaetsgrenze:         gebunden
Pflichtreduktionen:              gebunden
Falsifikationsbedingungen:       gebunden
konkrete Naturannahme:           nicht ausgewaehlt
konkrete Gleichung:              nicht zugelassen
Implementierung:                 gesperrt
Forschungslauf:                  nein
```

Die realistische Entscheidung lautet:

> Ein nichtlinearer lokaler Substratkandidat ist als Forschungsraum sauber
> eingegrenzt, aber aus der vorhandenen MCM-Mechanik noch nicht hergeleitet.
> Eine Gleichung nur zur Erzeugung des gewuenschten Verhaltens waere ein
> programmiertes Ergebnis und wird nicht implementiert.

## Aussagegrenze

S1-C belegt weder Substratwirkung noch Praegung, relative Feldzeit, Memory,
inneren Kontext, Organisation, Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

Der [S1-D-Mobilitaetsaudit](S1D_AUDIT_FELDSPANNUNGSABHAENGIGE_REZIPROKE_MOBILITAET.md)
ist abgeschlossen und reduziert die gepruefte Annahme auf eine
zustandsabhaengige Relaxationsbaseline. Der
[S1-E-Dimensionsaudit](S1E_AUDIT_LOKALE_SKALARDIMENSION_UND_VERTEILTE_NICHTSEPARIERBARKEIT.md)
begruendet keine zweite lokale Variable und bestimmt verteilte kausale
Nichtseparierbarkeit als offene Feldanforderung. Als naechstes folgt ihr
statischer S1-F-Zulassungsvertrag. Die Kandidatenimplementierung bleibt
gesperrt.
