# S2-SP: PPB-Lebenszyklus V2 – konkrete Aufgabenbindung

## Zweck

Dieser private Zweiarmvergleich prüft nur die offene Aussage: Bleibt ein
visuell stabilisiertes Ziel nach tatsächlich eingetretener A-Entfernung
zunächst read-only abrufbar, und endet diese konkrete Zielbindung erst mit
einer später nachgewiesenen visuellen PPB-Ersetzung? Die beiden festen Arme
sind `historical.v1` und `identity-preserving.v1`.

Die unmittelbare Identitätserhaltung und die e07-Formelkontrolle sind bereits
getrennt bestätigt und werden nicht als eigene Experimente wiederholt.

## Quellen- und Regelbezug

Verwendet wird unverändert die bereits dokumentierte OA-Inhaltsfolge A bis E
aus [S2-OA](S2OA_STATISCHER_FUNKTIONSPLAN_FORTGESETZTER_MCM_BETRIEB.md) mit
dem qualifizierten Standardprofil, den bestehenden Fast-/PPB-Regeln, neun
B4-Plätzen, drei Fast-Slots, vier visuellen PPB-Slots, Fast-Ablauf nach acht
Expositionen und PPB-Ablauf nach 64 Schritten. Die Quellen werden nicht nach
Rezeptorwerten oder erwarteten Treffern ausgewählt oder angepasst.

## Gebundene Folge

| Ordinal | Bildung / Hinweis | Rolle |
|---:|---|---|
| 01–04 | A, A, A, A | Zielaufbau und visuelle Stabilisierung |
| 05–08 | B, B, B, B | erster Druckabschnitt |
| 09–12 | C, C, C, C | zweiter Druckabschnitt; A-Fast kann regulär ablaufen |
| 13 | D | B4-Druck: letzter A-B4-Eintrag soll regulär entfallen |
| 14 | A-Cue, read-only | B-Erhaltung nur bei tatsächlich fehlendem A in B4 und Fast |
| 15–17 | D, D, D | D vervollständigen; vier visuelle Slow-Slots belegt |
| 18–19 | E, E | zweites E soll nach der bestehenden LRU-Regel den ältesten visuellen Slow-Slot ersetzen |
| 20 | A-Cue, read-only | Zielersetzung nur bei nativer Ersetzungsbindung auf der vorherigen A-Slotgeneration |

Die Hülle enthält 18 Formationen und zwei Hinweise je Arm. Die Quellen werden
einmal gemeinsam materialisiert; die zwei Memoryzustände und sämtliche
Ownerobjekte bleiben getrennt. Hinweise verändern keinen Zustand.

## Statische Erreichbarkeit

Die Folge übernimmt die ersten 18 Formationen der bereits begründeten
OA-Kette. Dort sind unter den unveränderten Regeln Fast-Ablauf bei f12,
B4-Verdrängung des letzten A-Eintrags bei f13 sowie die visuelle
Slow-Ersetzung des ältesten A-Slots beim zweiten E-Ereignis f18 abgeleitet.
Die hier vorgezogenen Hinweise liegen unmittelbar nach f13 und f18 und
erhöhen die Geschichte nicht.

Die Transitionen sind fachliche Prüfbedingungen, keine Startgates:

- Fehlt bei Hinweis 14 der Nachweis, dass A in B4 und Fast nicht aktuell
  verfügbar ist, lautet das Ergebnis `PRÜFBEDINGUNG_NICHT_ERREICHT`.
- Fehlt der gebundene A-PPB-Slot oder fehlt bei Hinweis 20 ein auf diesen Slot
  bezogenes natives `REPLACED`, lautet auch dort
  `PRÜFBEDINGUNG_NICHT_ERREICHT`.
- Nur nach erfüllter Bedingung werden die A-Cues als B-Erhaltung beziehungsweise
  als Ende derselben Zielbindung bewertet.

Damit ist `FAST_REPLACED` weder nötig noch hinreichend. Regelmäßiger Ablauf
kann Fast entfernen; entscheidend sind die aktuellen B4-/Fast-Scans und die
kontinuierliche visuelle PPB-Slotkette.

## Erweiterte Belegform

Für jede konsolidierte Formation referenziert der neue private Record die
bereits nativ entstehenden visuellen PPB-Readout-Felder: `event`, `slot_id`,
`input_digest`, `prestate_digest`, `poststate_digest`, Support und
Prototypdigest. Für Fast werden `primary_event`, ausgewählter Slot,
abgelaufene Slotdigests und bei einer Ersetzung der verworfene Slotdigest
geführt. Inhaltsdigests bleiben Inhaltsdigests und werden nicht als
Generationen ausgegeben.

Die Verifikation muss die Readout-Kette gegen die atomare Transition und den
jeweiligen Cue-Scan prüfen. Eine Ersetzungsbehauptung ist nur zulässig, wenn
der gebundene Zielslot zuerst im Readout existiert und später dessen
`REPLACED`-Readout mit passendem Vorzustandsdigest vorliegt.

## Budget und Qualifikation

Die 20 Ereignisse, 18 Formationen und zwei Hinweise liegen innerhalb der
bestehenden Obergrenzen von 28 Ereignissen, 20 Formationen sowie zwei
auditiven und sechs visuellen Hinweisen. Der Vergleich benötigt 18 gemeinsam
materialisierte Audio- und 18 visuelle Formationswerte sowie vier read-only
Scans einschließlich unabhängiger Direktbaselines. Feldkontakte bleiben bei
null. Die neue Receipt-Referenzhülle wird vor einer Ausführung gegen das
bestehende private 262.144-Byte-Limit bilanziert.

Die fokussierte Neutralqualifikation deckt die Readout-Auflösung,
Slot-/Vor-/Nachzustandsbindung, regulären Ablauf, `REPLACED`, fehlende
Prüfbedingung, unveränderte Hinweise, getrennte Arme und die
Direktbaseline ab. Erst bei bestandener Qualifikation darf genau ein
gebundener Vergleich stattfinden. Ausbleibende Voraussetzungen führen nicht
zu Quellenwechsel, Verlängerung oder Wiederholung.
