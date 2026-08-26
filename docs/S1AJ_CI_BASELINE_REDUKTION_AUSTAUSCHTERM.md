# S1-AJ: Baseline-Reduktion des `C_i`-Austauschmodells

Stand: 2026-08-11

Status: `BASELINE_EQUIVALENT_IN_EINFACHSTER_FORM`

## Ausgangsmodell

S1-AI verwendet:

```text
Delta_i = E_i - C_i
J_i = alpha * (1 - C_i^2) * Delta_i
dC_i/dt = J_i
dS_i/dt = F_MCM_i - beta * J_i
```

## Reduktion

### Externe lokale Feldteilnahme

Wenn `E_i` nur als externe lokale Eingabe behandelt wird, ist `C_i` ein
begrenzter erster Ordnungsspeicher mit Rueckwirkung:

```text
E_i -> C_i -> S_i
```

Das ist eine leaky beziehungsweise begrenzte Integratorstruktur. Die
gemeinsame Verwendung von `J_i` macht die Kopplung konjugiert, erzeugt aber
noch keine neue Substratnatur.

### Wegfall der Rueckwirkung

Bei `beta = 0` bleibt nur die begrenzte Dispositionsentwicklung:

```text
dC_i/dt = alpha * (1 - C_i^2) * (E_i - C_i)
```

Das ist eine begrenzte leaky Spur. Die spaetere Feldwirkung verschwindet.

### Konstante lokale Feldteilnahme

Bei konstantem `E_i` relaxiert `C_i` zu einer begrenzten Gleichgewichtslage.
Es entsteht keine eigenstaendige Wiederverwendung, keine verteilte Bilanz
und keine neue Feldtopologie.

### Mehrere Orte ohne neue Wechselwirkung

Wenn jeder Ort sein eigenes `J_i` unabhaengig berechnet, ist das Gesamtsystem
eine Summe lokaler Austauschspuren. Verteilte kausale Nichtseparierbarkeit
ist damit nicht begruendet.

### Ortsuebergreifender Austausch

Wird `J_i` ueber Nachbarschaften transportiert, wird eine explizite
Transport- oder Ressourcenbaseline eingefuehrt. Das faellt in die bereits
gepruefte konservierte F3-/Transportfamilie, solange keine neue
Materialursache hinzukommt.

## Entscheidung gegen den neuen Naturclaim

Die einfachste `C_i`-Form ist damit nicht als neue MCM-Substratnatur
zugelassen. Sie ist aber als transparente digitale Engineering-Baseline
technisch sinnvoll, weil sie die kleinstmoegliche konjugierte
Substrat-Feld-Kopplung beschreibt.

```text
neue MCM-Natur:              nicht nachgewiesen
technische Materialbaseline: zulaessig
Memory:                      nicht nachgewiesen
Implementierung als Claim:   STOPP
Implementierung als Baseline: moeglich nach separater Freigabe
```

## Technischer Baseline-Anschluss

Die begrenzte lokale Disposition ist nun als isolierte Engineering-Baseline
unter `mcm_field_organism.ci_accommodation_baseline` implementiert. Der
aktuelle API-Pfad stellt dafuer `CIState`, `CIAccommodationConfig`,
`CIAdvanceResult` und `advance_ci_accommodation` bereit.

Die Baseline:

- verarbeitet nur technische lokale Werte in `[-1, 1]`;
- berechnet den Austauschterm und die konjugierte technische Rueckwirkung;
- lehnt unzulaessig grosse Schritte ab, statt Werte zu clippen;
- speichert keine Rohmedien, Labels, Episoden oder Bedeutungen;
- ist kein MCM-Memory und kein Lernmodul.

Die Implementierung bestaetigt nur, dass die digitale Materialbaseline
technisch formulierbar ist. Sie bestaetigt keine neue MCM-Natur.

## Konsequenz fuer das Projekt

Wir haben damit zwei saubere Wege:

1. `C_i` als transparente digitale Baseline implementieren und nur seine
   technische Feldwirkung untersuchen;
2. eine weitere unabhaengige Materialeigenschaft suchen, die ueber diese
   leaky-/Integratorstruktur hinausgeht.

Eine weitere mathematische Verfeinerung von `J_i` ohne neue Ursache waere
keine echte Forschungsfortsetzung, sondern nur Parameter- oder
Funktionsdesign.

## Bester naechster Schritt

Die Entscheidung zwischen technischer Baseline-Implementierung und der Suche
nach einer neuen unabhaengigen Materialeigenschaft treffen. Eine
Implementierung darf nur als Baseline bezeichnet werden.
